from src.ClassQuery import ClassQuery
from src.ZerohopQuery import ZerohopQuery
from src.GraphQuery import GraphQuery
import sys

ep = sys.argv[1]

if ep.endswith('query') or ep.endswith('sparql'):
    data_name = ep.rsplit('/', 2)[-2]
else:
    data_name = ep.rsplit('/', 1)[-1]

query_path = sys.argv[2]

class_query_path = query_path + 'P103_Q002_H001_class_queries.xml'
zerohop_query_path = query_path + 'P103_Q002_H001_zerohop_queries.xml'
graph_query_path = query_path + 'P103_Q002_H001_graph_queries.xml'

output_path = sys.argv[3]

cq = ClassQuery(class_query_path)
zq = ZerohopQuery(zerohop_query_path)
gq = GraphQuery(graph_query_path)

# cq.ask_all(ep)
# cq.dump_responses(output_path + data_name + '.batch1.class_responses.xml')

zq.ask_all(ep)
zq.dump_responses(output_path + data_name + '.batch1.zerohop_responses.xml')

gq.ask_all(ep)
gq.dump_responses(output_path + data_name + '.batch1.graph_responses.xml')

