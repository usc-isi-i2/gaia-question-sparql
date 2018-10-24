import sys
sys.path.append('../')
from src.utils import write_file
from src.graph_query import GraphQuery

_, query_file, n2p_txt, output_prefix = sys.argv
gq = GraphQuery(query_file, n2p_txt)
write_file(gq.related_d2q, output_prefix + '_d2q.json')
write_file(gq.related_q2d, output_prefix + '_q2d.json')