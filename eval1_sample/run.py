from pathlib import Path
from src.ClassQuery import ClassQuery
from src.ZerohopQuery import ZerohopQuery
from src.GraphQuery import GraphQuery
from src.utils import *

output_path = './outputs/'

ttl_path = Path('./ttls/')
ttls = list(ttl_path.glob('*.ttl'))

query_path = './queries/'


def run_on_each_kb():
    fail_class = []
    fail_zerohop = []
    fail_graph = []
    for KB in ttls:
        ep = init_graph(str(KB))
        # run class query:
        try:
            cq = ClassQuery(query_path + 'class_query.xml')
            cq.ask_all(ep)
            cq.dump_responses(output_path + KB.stem + '.batch1.class_responses.xml')
        except:
            fail_class.append(KB.name)

        # run zerohop query:
        try:
            zq = ZerohopQuery(query_path + 'zerohop_query.xml')
            zq.ask_all(ep)
            zq.dump_responses(output_path + KB.stem + '.batch1.zerohop_responses.xml')
        except:
            fail_zerohop.append(KB.name)

        run graph query:
        try:
            gq = GraphQuery(query_path + 'graph_query.xml', KB.stem)
            gq.ask_all(ep)
            gq.dump_responses(output_path + KB.stem + '.batch1.graph_responses.xml')
        except:
            fail_graph.append(KB.name)

        print(fail_class)
        print(fail_zerohop)
        print(fail_graph)


run_on_each_kb()


