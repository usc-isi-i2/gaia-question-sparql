from pathlib import Path
from src.ClassQuery import ClassQuery
from src.ZerohopQuery import ZerohopQuery
from src.GraphQuery import GraphQuery
from src.QueryTool import *

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
    # cq = ClassQuery(query_path + 'class_query.xml')
    zq = ZerohopQuery(query_path + 'zerohop_query.xml')
    gq = GraphQuery(query_path + 'graph_query.xml')
    for KB in ttls:
        qt = QueryTool(str(KB), Mode.SINGLETON)

        zq.ask_all(qt, root_doc=KB.stem)
        zq.dump_responses(output_path + KB.stem + '.batch1.zerohop_responses.xml')

        gq.ask_all(qt, root_doc=KB.stem)
        gq.dump_responses(output_path + KB.stem + '.batch1.graph_responses.xml')


run_on_each_kb()


