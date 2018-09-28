
from src.utils import *
from src.SingleGraphQuery import SingleGraphQuery


class GraphQuery(object):
    def __init__(self, xml_file_or_string):
        self.root = ET.Element('graphqueries_responses')
        self.query_list = xml_loader(xml_file_or_string, GRAPH_QUERY)

    def ask_all(self, query_tool, start=0, end=None, root_doc=''):
        if not end:
            end = len(self.query_list)
        doc_names = None
        for i in range(start, end):
            if root_doc:
                query_docs = set([c2p[c_id] for c_id in list(find_keys(DOCEID, self.query_list[i][ENTRYPOINTS]))])
                if root_doc not in query_docs:
                    query_names = set(find_keys(NAME_STRING, self.query_list[i][ENTRYPOINTS]))
                    if not doc_names:
                        q = 'select distinct ?n where {?x aida:hasName ?n}'
                        doc_names = set([_[0] for _ in query_tool.select(q)])
                    if not query_names.intersection(doc_names):
                        continue
            # ans one:
            single = SingleGraphQuery(query_tool, self.query_list[i], root_doc)
            responses = single.get_responses()
            if len(responses):
                self.root.append(responses)

    def dump_responses(self, output_file):
        if len(self.root):
            write_file(self.root, output_file)
            return True
        return False








