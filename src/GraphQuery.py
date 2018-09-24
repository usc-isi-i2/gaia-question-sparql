
from src.utils import *
from src.SingleGraphQuery import SingleGraphQuery


class GraphQuery(object):
    def __init__(self, xml_file_or_string):
        self.roots = []
        self.query_list = xml_loader(xml_file_or_string, GRAPH_QUERY)

    def ask_all(self, endpoint, start=0, end=None, root_doc=''):
        if not end:
            end = len(self.query_list)
        for i in range(start, end):
            target_docs = set([c2p[c_id] for c_id in list(find_keys(DOCEID, self.query_list[i][ENTRYPOINTS]))])
            if root_doc in target_docs:
                responses = self.ans_one(endpoint, self.query_list[i], root_doc)
                self.roots.append(responses)

    def ans_one(self, endpoint, q_dict, root_doc):
        single = SingleGraphQuery(endpoint, q_dict, root_doc)
        responses = single.get_responses()
        return responses

    def dump_responses(self, output_file):
        write_file(self.roots, output_file)








