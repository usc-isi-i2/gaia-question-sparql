
import sys
sys.path.append('../')
from run.run import run_ta1

_, runN, vN = sys.argv
param = {
    "ttls_folder": "/nas/home/dongyul/ocr_map/ta1brun%s/v%s/" % (runN, vN),
    "query_folder": "/nas/home/dongyul/eval_queries/data/",
    "output_folder": "/nas/home/dongyul/qa_ta1b/run%s/v%s/outputs/" % (runN, vN),
    "log_folder": "/nas/home/dongyul/qa_ta1b/run%s/v%s/logs/" % (runN, vN),
    "batch_num": "1",
    "fuseki": "http://localhost:3030/run%sv%s" % (runN, vN),
    "n2p_txt": "/nas/home/dongyul/ocr_map/ta1brun%s/v%s.txt" % (runN, vN)
}
run_ta1(**param)
