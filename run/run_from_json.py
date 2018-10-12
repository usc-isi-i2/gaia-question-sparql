import json
import sys
sys.path.append('../')


from run.run import run_ta1, run_ta2, run_ta3
_, param = sys.argv
runs = {
    'ta1': run_ta1,
    'ta2': run_ta2,
    'ta3': run_ta3
}
with open(param) as f:
    params = json.load(f)
    for k, v in params.items():
        if v.get('run'):
            runs[k](**v.get('params'))
