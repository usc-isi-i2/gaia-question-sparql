
import sys
sys.path.append('../')

from pathlib import Path
from src.ClassQuery import ClassQuery
from src.ZerohopQuery import ZerohopQuery
from src.GraphQuery import GraphQuery
from datetime import datetime
from src.QueryTool import *

ttl_path = Path(sys.argv[1])
# ttl_path = Path('..')
ttls = list(ttl_path.glob('*.ttl'))

class_query_path = '../resources/ta1_batch1_v1/P103_Q002_H001_class_queries.xml'
zerohop_query_path = '../resources/ta1_batch1_v1/P103_Q002_H001_zerohop_queries.xml'
graph_query_path = '../resources/ta1_batch1_v1/P103_Q002_H001_graph_queries.xml'

output_path = sys.argv[2]

# output_path = './'


def wrap_error(_type, _doc, _err):
    return '%s query failed on %s . err: %s \n' % (_type, _doc, str(_err))


def run_on_each_kb():
    print('start - ', str(datetime.now()))

    with open('statics.log', 'a') as ff:

        cnt = 0
        total = len(ttls)
        cq = ClassQuery(class_query_path)
        zq = ZerohopQuery(zerohop_query_path)
        gq = GraphQuery(graph_query_path)

        for KB in ttls:
            if cnt % 100 == 0:
                print('\t run %d of %d - ' % (cnt, total), str(datetime.now()))
            cnt += 1
            qt = QueryTool(str(KB), Mode.SINGLETON)
            # run class query:
            try:
                cq.ask_all(qt)
                cq.dump_responses(output_path + KB.stem + '.batch1.class_responses.xml')
            except Exception as e:
                ff.write(wrap_error('class', KB.stem, e))

            # run zerohop query:
            try:
                zq.ask_all(qt, root_doc=KB.stem)
                zq.dump_responses(output_path + KB.stem + '.batch1.zerohop_responses.xml')
            except Exception as e:
                ff.write(wrap_error('zerohop', KB.stem, e))

            # run graph query:
            try:
                gq.ask_all(qt, root_doc=KB.stem)
                gq.dump_responses(output_path + KB.stem + '.batch1.graph_responses.xml')
            except Exception as e:
                ff.write(wrap_error('graph', KB.stem, e))

    print(' log statistics - ', str(datetime.now()))
    print(' done - ', str(datetime.now()))


run_on_each_kb()


