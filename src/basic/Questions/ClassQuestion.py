

from src.basic.Questions.Question import *


class ClassQuestion(Question):
    def __init__(self, question):
        super(ClassQuestion, self).__init__(question)
        self.enttype = question[ENTTYPE]

    def serialize_sparql(self):
        sub = '?x'
        self.nodes.add('?x')
        triples = self.parse_enttype(sub, self.enttype)
        return Serializer().serialize_class_query(self.nodes, triples)
