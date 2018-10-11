import traceback
from src.utils import *
from src.single_graph_query import SingleGraphQuery
from src.stat import Stat
from datetime import datetime


class GraphQuery(object):
    def __init__(self, xml_file_or_string, n2p_txt=None):
        self.query_list = xml_loader(xml_file_or_string, GRAPH_QUERY)
        self.related_docs = []
        try:
            n2p = generate_n2p_json(n2p_txt)
            for q in self.query_list:
                docs = set([c2p.get(_) for _ in list(find_keys(DOCEID, q[ENTRYPOINTS]))])
                docs = docs.union(*[n2p.get(name, set()) for name in list(find_keys(NAME_STRING, q[ENTRYPOINTS]))])
                self.related_docs.append(docs)
        except Exception as e:
            print(e)
            pass

    def ask_all(self, query_tool, start=0, end=None, root_doc='', prefilter=True):
        root = ET.Element('graphqueries_responses')
        stat = Stat(root_doc)
        errors = []
        if not end:
            end = len(self.query_list)
        for i in range(start, end):
            try:
                if prefilter and self.related_docs and root_doc in p2c and root_doc not in self.related_docs[i]:
                    continue
                # ans one:
                print(root_doc, i, self.query_list[i]['@id'], datetime.now())
                single = SingleGraphQuery(query_tool, self.query_list[i], root_doc, stat)
                responses = single.get_responses()
                if len(responses):
                    root.append(responses)
            except Exception as e:
                errors.append('%s\n%s\n' % (','.join((root_doc, self.query_list[i]['@id'], str(i), str(e))), traceback.format_exc))
        return root, stat, errors

    @property
    def all_related_docs(self):
        return set().union(*self.related_docs)
