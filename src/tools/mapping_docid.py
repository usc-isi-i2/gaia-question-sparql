'''
catalog_id	version	parent_uid	child_uid	url	child_asset_type	rel_pos	wrapped_md5	unwrapped_md5	download_date	content_date	status_in_corpus
LDC2018E62	V1.0	HC00001DO	HC00002Z8	https://en.wikipedia.org/wiki/Battle_of_Kramatorsk	.ltf.xml	n/a	fe1c267d490d00f87dda75b083282d6c	17da71b481b9cad59de53df0e47f725e	2017-10-31	2014-04-19	present
'''


tab_file = '/Users/dongyuli/isi/parent_children.tab'

with open(tab_file) as f:
    lines = f.readlines()

c2p = {}
p2c = {}

for i in range(1, len(lines)):
    cata, version, pid, cid, others = lines[i].split('\t', 4)
    if pid not in p2c:
        p2c[pid] = []
    p2c[pid].append(cid)
    c2p[cid] = pid

import json
with open('p2c.json', 'w') as f:
    json.dump(p2c, f, indent=2)
with open('c2p.json', 'w') as f:
    json.dump(c2p, f, indent=2)


