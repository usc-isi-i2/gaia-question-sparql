from pathlib import Path
from datetime import datetime
import sys
sys.path.append('../')
from src.query_tool import *
from run import load_query


def run_ta3(input, output, query_folder, fuseki, run_class=True, run_zerohop=True, run_graph=True):
    def run_query(querier, _type, qt, KB):
        doc_id = KB.stem
        response, stat, errors = querier.ask_all(qt, root_doc=doc_id, verbose=False)
        if len(response):
            write_file(response, output + 'outputs/' + str(KB).rstrip('.ttl').lstrip('/nas/home/dongyul/') + ('.%s_responses.xml' % _type))
        if len(errors):
            # each error: doc_id,query_id,query_idx,error_str
            write_file(errors, output + 'logs/' + str(KB).rstrip('.ttl').lstrip('/nas/home/dongyul/') + ('.%s_errors.csv' % _type))
        if stat:
            stat.dump_report(output + 'logs/' + str(KB).rstrip('.ttl').lstrip('/nas/home/dongyul/') + ('.%s_stat' % _type))

    path = Path(input)
    ttls = list(path.glob('**/*.ttl'))
    cq, zq, gq = load_query(query_folder)
    start_time = datetime.now()
    print('start - ', str(start_time))
    for x in ttls:
      print(str(x))    

    cnt = 0
    total = len(ttls)

    for KB in ttls:
        qt = QueryTool(str(KB), Mode.PROTOTYPE, relax_num_ep=1, use_fuseki=fuseki or '', block_ocrs=False)
        update_res = qt.update('''
        insert {?r aida:justifiedBy ?j} where {
        ?x aida:prototype ?p .
        ?r rdf:subject ?p ;
           rdf:predicate rdf:type ;
           rdf:object ?o .
        ?p aida:justifiedBy ?j .}
        ''')
        print(update_res)
        cnt += 1
        print('\t run query on %s : %d of %d  ' % (KB.stem, cnt, total), str(datetime.now()))
        if run_class:
            run_query(cq, CLASS, qt, KB)
        if run_zerohop:
            run_query(zq, ZEROHOP, qt, KB)
        if run_graph:
            run_query(gq, GRAPH, qt, KB)

    print(' done - ', str(datetime.now()))
    print(' time used: ', datetime.now() - start_time)


_, input_folder, output_folder = sys.argv
query_folder = "/nas/home/dongyul/eval_queries/data/"
fuseki = "http://localhost:3030/run1"

run_ta3(input_folder, output_folder, query_folder, fuseki)



