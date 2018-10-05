import sys
from src.utils import *
from src.SingleGraphQuery import SingleGraphQuery


class GraphQuery(object):
    def __init__(self, xml_file_or_string):
        self.query_list = xml_loader(xml_file_or_string, GRAPH_QUERY)
        self.related_docs = []
        for q in self.query_list:
            docs = set([c2p.get(_) for _ in list(find_keys(DOCEID, q[ENTRYPOINTS]))])
            docs = docs.union(*[n2p.get(name, set()) for name in list(find_keys(NAME_STRING, q[ENTRYPOINTS]))])
            self.related_docs.append(docs)

    def ask_all(self, query_tool, start=0, end=None, root_doc=''):
        root = ET.Element('graphqueries_responses')
        errors = []
        diff = []
        failed_on_justi = []
        if not end:
            end = len(self.query_list)
        for i in range(start, end):
            try:
                if root_doc in p2c and root_doc not in self.related_docs[i]:
                    continue
                # ans one:
                single = SingleGraphQuery(query_tool, self.query_list[i], root_doc)
                responses = single.get_responses()
                if len(responses):
                    root.append(responses)
                else:
                    if root_doc:
                        diff.append(self.query_list[i]['@id'])
                    if single.fail_on_justi:
                        failed_on_justi.append(i)
            except Exception:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                errors.append(','.join((root_doc, self.query_list[i]['@id'], str(i),
                                        str(exc_type), str(fname), str(exc_tb.tb_lineno))))
        return root, {'errors': errors, 'diff': diff, 'failed_on_justi': failed_on_justi}

    @property
    def all_related_docs(self):
        return set().union(*self.related_docs)

