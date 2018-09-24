from pathlib import Path
from src.ClassQuery import ClassQuery
from src.ZerohopQuery import ZerohopQuery
from src.GraphQuery import GraphQuery
from src.utils import *
from datetime import datetime

import sys
ttl_path = Path(sys.argv[0])
ttls = list(ttl_path.glob('*.ttl'))

class_query_path = '../resources/ta1_batch1_v1/P103_Q002_H001_class_queries.xml'
zerohop_query_path = '../resources/ta1_batch1_v1/P103_Q002_H001_zerohop_queries.xml'
graph_query_path = '../resources/ta1_batch1_v1/P103_Q002_H001_graph_queries.xml'

output_path = sys.argv[1]


def run_on_each_kb():
    print('start - ', str(datetime.now()))
    fail_class = []
    fail_zerohop = []
    fail_graph = []
    graph_has_response = []
    cnt = 0
    total = len(ttls)
    for KB in ttls:
        if cnt % 100 == 0:
            print('\t run %d of %d - ' % (cnt, total), str(datetime.now()))
        cnt += 1
        ep = init_graph(str(KB))
        # run class query:
        try:
            cq = ClassQuery(class_query_path)
            cq.ask_all(ep)
            cq.dump_responses(output_path + KB.stem + '.batch1.class_responses.xml')
        except:
            fail_class.append(KB.stem)

        # run zerohop query:
        try:
            zq = ZerohopQuery(zerohop_query_path)
            zq.ask_all(ep)
            zq.dump_responses(output_path + KB.stem + '.batch1.zerohop_responses.xml')
        except:
            fail_zerohop.append(KB.stem)

        # run graph query:
        try:
            gq = GraphQuery(graph_query_path, KB.stem)
            gq.ask_all(ep)
            if gq.roots:
                graph_has_response.append(KB.stem)
            gq.dump_responses(output_path + KB.stem + '.batch1.graph_responses.xml')
        except:
            fail_graph.append(KB.stem)

    print(' log statistics - ', str(datetime.now()))
    with open('statics.log', 'w') as ff:
        ff.write('fails: \n')
        ff.write(','.join(fail_class))
        ff.write('\n')
        ff.write(','.join(fail_zerohop))
        ff.write('\n')
        ff.write(','.join(fail_graph))
        ff.write('\n')
        ff.write('has graph response: \n')
        ff.write(','.join(graph_has_response))
    print(' done - ', str(datetime.now()))


run_on_each_kb()


