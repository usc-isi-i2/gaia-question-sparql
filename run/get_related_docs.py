import sys
sys.path.append('../')
from src.utils import write_file
from src.graph_query import GraphQuery

_, query_file, n2p_txt, output = sys.argv
gq = GraphQuery(query_file, n2p_txt)
write_file(gq.separate_related_docs, output)