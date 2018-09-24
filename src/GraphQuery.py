
from src.utils import *
from src.SingleGraphQuery import SingleGraphQuery


class GraphQuery(object):
    def __init__(self, xml_file_or_string, doc_id):
        self.roots = []
        self.doc_id = doc_id
        self.query_list = xml_loader(xml_file_or_string, GRAPH_QUERY)

    def ask_all(self, endpoint, start=0, end=None):
        if not end:
            end = len(self.query_list)
        for i in range(start, end):
            responses, has_responses = self.ans_one(endpoint, self.query_list[i])
            if has_responses:
                self.roots.append(responses)

    def ans_one(self, endpoint, q_dict):
        single = SingleGraphQuery(endpoint, q_dict, self.doc_id)
        responses, has_responses = single.get_responses()
        return responses, has_responses

    def dump_responses(self, output_file):
        write_file(self.roots, output_file)








