from pathlib import Path
from src.ClassQuery import ClassQuery
from src.ZerohopQuery import ZerohopQuery
from src.GraphQuery import GraphQuery
from src.utils import *

output_path = './outputs/'

ttl_path = Path('./ttls/')
ttls = list(ttl_path.glob('*.ttl'))

query_path = './queries/'

# import requests
# sparql_endpoint = 'http://localhost:3030/ta1_qa/'
# def refresh(KB):
#     requests.post(sparql_endpoint+'update', data='update=inser')
#     requests.post( )


def run_on_each_kb():
    fail_class = []
    fail_zerohop = []
    fail_graph = []
    cq = ClassQuery(query_path + 'class_query.xml')
    zq = ZerohopQuery(query_path + 'zerohop_query.xml')
    gq = GraphQuery(query_path + 'graph_query.xml')
    for KB in ttls:
        ep = init_graph(str(KB))
        if True:
        # # run class query:
        # try:
        #     cq.ask_all(ep)
        #     cq.dump_responses(output_path + KB.stem + '.batch1.class_responses.xml')
        # except:
        #     fail_class.append(KB.name)

        # run zerohop query:
        # try:
            zq.ask_all(ep, root_doc=KB.stem)
            zq.dump_responses(output_path + KB.stem + '.batch1.zerohop_responses.xml')
        # except:
        #     fail_zerohop.append(KB.name)

        # run graph query:
        # try:
            gq.ask_all(ep, root_doc=KB.stem)
            gq.dump_responses(output_path + KB.stem + '.batch1.graph_responses.xml')
        # except:
        #     fail_graph.append(KB.name)

        print(fail_class)
        print(fail_zerohop)
        print(fail_graph)


run_on_each_kb()


