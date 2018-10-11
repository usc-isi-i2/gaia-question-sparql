from pathlib import Path
from datetime import datetime
import sys
sys.path.append('../')
from src.QueryTool import *
from src.ClassQuery import ClassQuery
from src.ZerohopQuery import ZerohopQuery
from src.GraphQuery import GraphQuery


def load_query(query_folder, n2p_txt=''):
    query_path = Path(query_folder)
    cq, zq, gq = None, None, None
    for q in query_path.glob('*.xml'):
        if q.stem.endswith(CLASS_QUERIES):
            cq = ClassQuery(str(q))
        if q.stem.endswith(ZEROHOP_QUERIES):
            zq = ZerohopQuery(str(q))
        if q.stem.endswith(GRAPH_QUERIES):
            gq = GraphQuery(str(q), n2p_txt)
    return cq, zq, gq


def run_ta1(ttls_folder, query_folder, output_folder, log_folder, batch_num, fuseki, n2p_txt='', ta3=False):

    def wrap_output_filename(_doc, _type):
        """
        The responses to queries should be a compressed tarball (.tgz or .zip) of a single directory (named with the run ID),
        with 3 xml response files per document per batch of queries.

        <DocumentID>.<batchNumber>.{class_responses,zerohop_responses,graph_responses}.xml
        (e.g.,  “IC0015PZ4.batch1.class_responses.xml”)
        """
        return '%s%s.%s_responses.xml' % (output_folder, _doc, _type)
    start = datetime.now()
    print('start - ', str(start))
    cq, zq, gq = load_query(query_folder, n2p_txt)
    ttls = list(Path(ttls_folder).glob('*.ttl'))
    err_loggers = {
        CLASS:  open(log_folder + 'class_error.csv', 'w'),
        ZEROHOP:  open(log_folder + 'zerohop_error.csv', 'w'),
        GRAPH:  open(log_folder + 'graph_error.csv', 'w'),
    }

    cnt = 0
    total = len(coredocs)

    for KB in ttls:
        if KB.stem not in coredocs:
            continue
        print('\t run %s %d of %d - ' % (KB.stem, cnt, total), str(datetime.now()))
        cnt += 1
        qt = QueryTool(str(KB), Mode.CLUSTER, relax_num_ep=1, use_fuseki=fuseki or '', block_ocrs=False)

        for query, _type in [
            (cq, CLASS),
            (zq, ZEROHOP),
            (gq, GRAPH)
        ]:
            # print('doc_id: %s, query type: %s' % (KB.stem, _type))
            if ta3:
                response, stat, errors = query.ask_all(qt)
            else:
                response, stat, errors = query.ask_all(qt, root_doc=KB.stem, prefilter=False)
            if len(response):
                write_file(response, wrap_output_filename(KB.stem, _type))
            if len(errors):
                # each error: doc_id,query_id,query_idx,error_str
                write_file(errors, log_folder + _type + '_error.csv')
            if stat:
                stat.dump_report(log_folder)

    for logger in err_loggers.values():
        logger.close()
    print(' done - ', str(datetime.now()))
    print(' time used: ', datetime.now()-start)


def run_ta2(select_endpoint, query_folder, output_folder, log_folder, batch_num):
    def wrap_output_filename(_type):
        """
        The responses to queries should be a compressed tarball (.tgz or .zip) of a single directory (named with the run ID),
        with 3 xml response files per batch of queries.
        Please name your response files TA2.<batchNumber>.
        {class_responses,zerohop_responses,graph_responses}.xml  (e.g.,  “TA2.batch1.class_responses.xml”)
        """
        return '%sTA2.%s_responses.xml' % (output_folder, _type)

    start = datetime.now()
    print('start - ', str(start))
    cq, zq, gq = load_query(query_folder)
    qt = QueryTool(select_endpoint, Mode.PROTOTYPE, relax_num_ep=1, block_ocrs=False)

    for query, _type in [
       # (cq, CLASS),
        (zq, ZEROHOP),
        #(gq, GRAPH)
    ]:
        print('   query type: %s' % _type, str(datetime.now()))
        response, stat, errors = query.ask_all(qt, prefilter=False)
        if len(response):
            write_file(response, wrap_output_filename(_type))
        if len(errors):
            # each error: doc_id,query_id,query_idx,error_str
            write_file(errors, log_folder + _type + '_errors.csv')
        if stat:
            stat.dump_report(log_folder)

    print(' done - ', str(datetime.now()))
    print(' time used: ', datetime.now()-start)


def run_ta3(ttls_folder, query_folder, output_folder, log_folder, batch_num, fuseki):
    """
    The responses to queries should be a compressed tarball (.tgz or .gz) of a single directory (named with the run ID),
    containing one subdirectory for each frame ID for each statement of information need; e
    ach of these subdirectories should be named with the frame ID and should contain 3 xml response files per hypothesis.
    Please name your files <hypothesisID>.{class_responses,zerohop_responses,graph_responses}.xml,
    where hypothesisID is the name of the aida:Hypothesis object in your AIF graph.
    """
    run_ta1(ttls_folder, query_folder, output_folder, log_folder, batch_num, fuseki, ta3=True)


_, param = sys.argv
runs = {
    'ta1': run_ta1,
    'ta2': run_ta2,
    'ta3': run_ta3
}
with open(param) as f:
    params = json.load(f)
    for k, v in params.items():
        if v.get('run'):
            runs[k](**v.get('params'))

