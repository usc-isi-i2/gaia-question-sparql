import xmltodict
from src.basic.Questions.ClassQuestion import ClassQuestion
from src.basic.Questions.ZerohopQuestion import ZerohopQuestion
from src.basic.Questions.GraphQuestion import GraphQuestion
from src.basic.Answer import Answer
from src.basic.utils import *


class XMLLoader(object):
    def __init__(self, xml_file_or_string):
        if xml_file_or_string.endswith('.xml'):
            with open(xml_file_or_string) as f:
                self.xml = f.read()
        else:
            self.xml = xml_file_or_string

        mappings = {
            CLASS_QUERIES: (CLASS_QUERY, ClassQuestion),
            ZEROHOP_QUERIES: (ZEROHOP_QUERY, ZerohopQuestion),
            GRAPH_QUERIES: (GRAPH_QUERY, GraphQuestion)
        }

        self.question_list = []
        root = xmltodict.parse(self.xml)
        # pprint(root)
        for k, v in root.items():
            content = v[mappings[k][0]]
            initializer = mappings[k][1]
            if isinstance(content, list):
                for single_query in content:
                    self.question_list.append(initializer(single_query))
            else:
                self.question_list.append(initializer(content))

        # for x in self.question_list:
        #     print(x.serialize_sparql())

    def get_question_list(self):
        return self.question_list

    def answer_all(self, endpoint):
        res = []
        # cnt = 1
        for q in self.question_list:
            # print(cnt)
            # cnt += 1
            ans = self.answer_one(q, endpoint)
            res.append(ans)
        return res

    @staticmethod
    def answer_one(question, endpoint):
        return Answer(question, endpoint).ask()

