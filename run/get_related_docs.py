import sys
sys.path.append('../')
from src.utils import write_file
from src.graph_query import GraphQuery
from src.zerohop_query import ZerohopQuery

# _, query_file, n2p_txt, output_prefix = sys.argv
# gq = GraphQuery(query_file, n2p_txt)
# write_file(gq.related_d2q, output_prefix + '_d2q.json')
# write_file(gq.related_q2d, output_prefix + '_q2d.json')
# write_file(gq.related_img_video, output_prefix + '_d2img_video_doc.json')


zq = ZerohopQuery('/Users/dongyuli/isi/eval_queries/data/zerohop_queries.xml')
print(zq.related_doc)
write_file(zq.related_img_video, './zh_d2img_video_doc.json')