import traceback
from src.utils import *
from src.single_graph_query import SingleGraphQuery
from src.stat import Stat
from datetime import datetime


class GraphQuery(object):
    def __init__(self, xml_file_or_string, n2p_txt=None):
        self.query_list = xml_loader(xml_file_or_string, GRAPH_QUERY)
        self.all_queries_id = [_['@id'] for _ in self.query_list]
        self.query_ep_types = [[x for x in [NAME_STRING, TEXT_DESCRIPTOR, IMAGE_DESCRIPTOR, VIDEO_DESCRIPTOR]
                          if list(find_keys(x, q[ENTRYPOINTS]))] for q in self.query_list]
        self.related_docs = []
        self.n2p = {}
        try:
            self.n2p = generate_n2p_json(n2p_txt)
            for q in self.query_list:
                docs = set([c2p.get(_) for _ in list(find_keys(DOCEID, q[ENTRYPOINTS]))])
                docs = docs.union(*[self.n2p.get(name, set()) for name in list(find_keys(NAME_STRING, q[ENTRYPOINTS]))])
                self.related_docs.append(docs)
        except Exception as e:
            print(e)
            pass

    def ask_all(self, query_tool, start=0, end=None, root_doc='', prefilter=True, verbose=True):
        root = ET.Element('graphqueries_responses')
        stat = Stat(root_doc)
        errors = []
        if not end or end < start or end > len(self.query_list):
            end = len(self.query_list)
        for i in range(start, end):
            try:
                if prefilter and self.related_docs and root_doc in p2c and root_doc not in self.related_docs[i]:
                    continue
                # ans one:
                if verbose:
                    print(root_doc, i, self.query_list[i]['@id'], datetime.now())
                single = SingleGraphQuery(query_tool, self.query_list[i], root_doc, stat)
                responses = single.get_responses()
                if len(responses):
                    root.append(responses)
            except Exception as e:
                errors.append('%s\n%s\n' % (','.join((root_doc, self.query_list[i]['@id'], str(i), str(e))), traceback.format_exc))
        return root, stat, errors

    def get_query_by_idx(self, idx):
        return self.query_list[idx]

    @property
    def all_related_docs(self):
        return set().union(*self.related_docs)

    @property
    def related_q2d(self):
        res = {}
        for i in range(len(self.related_docs)):
            res[self.query_list[i]['@id']] = (list(self.related_docs[i]), ','.join(self.query_ep_types[i]))
        return res

    @property
    def related_d2q(self):
        res = {}
        for i in range(len(self.related_docs)):
            q_tuple = (self.query_list[i]['@id'], ','.join(self.query_ep_types[i]))
            for doc in self.related_docs[i]:
                if doc not in res:
                    res[doc] = []
                res[doc].append(q_tuple)
        return res

    @property
    def related_img_video(self):
        res = {}
        if self.n2p and c2p:
            for i in range(len(self.related_docs)):
                q = self.query_list[i]
                q_id = q['@id']
                eps = q[ENTRYPOINTS][ENTRYPOINT]
                parents = {}
                if isinstance(eps, dict):
                    eps = [eps]
                for ep in eps:
                    source1 = ep['typed_descriptor'].get(IMAGE_DESCRIPTOR, {}).get(DOCEID)
                    source = source1 or ep['typed_descriptor'].get(VIDEO_DESCRIPTOR, {}).get(DOCEID)
                    if c2p.get(source):
                        if c2p.get(source) not in parents:
                            parents[c2p.get(source)] = []
                        parents[c2p.get(source)].append(source)
                if parents:
                    for doc in self.related_docs[i]:
                        if doc in parents:
                            if doc not in res:
                                res[doc] = {}
                            res[doc][q_id] = parents[doc]
        return res





