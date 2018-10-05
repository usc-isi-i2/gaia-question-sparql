with open('tmp.txt') as f:
    lines = f.readlines()
    n2p = {} # hasName: [ttl file names]
    p2n = {}
    for line in lines:
        l = line.strip()
        if l.endswith('.ttl'):
            doc_id = l.rstrip('.ttl').rsplit('/', 1)[-1]
            p2n[doc_id] = set()
        else:
            if l not in n2p:
                n2p[l] = set()
            n2p[l].add(doc_id)
            p2n[doc_id].add(l)
    for k, v in n2p.items():
        n2p[k] = list(v)
    for k, v in p2n.items():
        p2n[k] = list(v)
    import json
    json.dump(n2p, open('n2p.json', 'w'), indent=2, ensure_ascii=False)
    json.dump(p2n, open('p2n.json', 'w'), indent=2, ensure_ascii=False)

