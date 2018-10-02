
from src.utils import *
from src.SingleGraphQuery import SingleGraphQuery


class GraphQuery(object):
    def __init__(self, xml_file_or_string):
        self.query_list = xml_loader(xml_file_or_string, GRAPH_QUERY)
        self.query_names = [set(find_keys(NAME_STRING, q[ENTRYPOINTS])) for q in self.query_list]
        self.query_docs = [set([c2p.get(_) for _ in list(find_keys(DOCEID, q[ENTRYPOINTS]))]) for q in self.query_list]

    def ask_all(self, query_tool, start=0, end=None, root_doc=''):
        root = ET.Element('graphqueries_responses')
        errors = []
        diff = []
        if not end:
            end = len(self.query_list)
        for i in range(start, end):
            try:
                if root_doc and root_doc not in self.query_docs[i]:
                    q = 'select distinct ?n where {?x aida:hasName ?n}'
                    doc_names = set([_[0] for _ in query_tool.select(q)])
                    if not self.query_names[i].intersection(doc_names):
                        continue
                # ans one:

                single = SingleGraphQuery(query_tool, self.query_list[i], root_doc)
                responses = single.get_responses()
                if len(responses):
                    root.append(responses)
                elif root_doc:
                    diff.append(self.query_list[i])
            except Exception as e:
                errors.append(','.join((root_doc, self.query_list[i]['@id'], str(i), str(e))))
        return root, {'errors': errors, 'diff': diff}

    def summarize(self, output_file):
        # TODO: get names of each ttl, the related docs are not enough
        res = []
        edge_counts = {}
        for i in range(len(self.query_list)):
            q = self.query_list[i]
            eps = q[ENTRYPOINTS][ENTRYPOINT]
            if isinstance(eps, dict):
                eps = [eps]
            edge_cnt = len(q[GRAPH][EDGES][EDGE]) if isinstance(q[GRAPH][EDGES][EDGE], list) else 1
            edge_counts[edge_cnt] = edge_counts.get(edge_cnt, 0) + 1
            cur = {
                'index': i,
                'query_id': q['@id'],
                'edge_cnt': edge_cnt,
                'ep': [self.summarize_ep(ep.get(TYPED_DESCRIPTOR) or ep) for ep in eps]
            }
            res.append(cur)
        summary = {
            'summary': {
                'source_parent_id': list(set.union(*self.query_docs)),
                'edge_count_distribution': edge_counts
            },
            'eps': res
        }
        write_file(summary, output_file)

    @staticmethod
    def summarize_ep(ep):
        descriptors = [STRING_DESCRIPTOR, TEXT_DESCRIPTOR, IMAGE_DESCRIPTOR, VIDEO_DESCRIPTOR]
        desp = [ep.get(ENTTYPE)]
        for d in descriptors:
            if d in ep:
                for k, v in ep[d].items():
                    if k == NAME_STRING:
                        desp.append(decode_name(v))
                    else:
                        if k == DOCEID:
                            desp.append(c2p[v])
                        desp.append(v)
                break
        return ', '.join(desp)
