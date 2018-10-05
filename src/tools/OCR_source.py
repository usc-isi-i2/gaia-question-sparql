
import json
import re
tab_file = '/Users/dongyuli/isi/masterShotBoundary.msb'

with open(tab_file) as f:
    lines = f.readlines()

ocrs = set()
for l in lines:
    _, source, others = re.compile("[ \t]+").split(l, 2)
    source = source.split('_', 1)[0]
    ocrs.add(source)


with open('ocrs.json', 'w') as f:
    json.dump(list(ocrs), f, indent=2)

