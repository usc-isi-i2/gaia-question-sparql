
import sys
sys.path.append('../')
from run.run import run_ta1

mapping = {
    '1': 'r1nl',
    '2': 'r2nl',
    '3': 'r1wl',
    '4': 'r4nl'
}
_, runN = sys.argv
param = {
    "ttls_folder": "/nas/home/dongyul/ocr_map/1003%s/" % mapping[runN],
    "query_folder": "/nas/home/dongyul/eval_queries/data/",
    "output_folder": "/nas/home/dongyul/qa_ta1a/run%s/outputs/" % runN,
    "log_folder": "/nas/home/dongyul/qa_ta1a/run%s/logs/" % runN,
    "batch_num": "1",
    "fuseki": "http://localhost:3030/run%s" % runN,
    "n2p_txt": "/nas/home/dongyul/ocr_map/1003%s.txt" % mapping[runN]
}
run_ta1(**param)

