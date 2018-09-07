

from src.basic.Questions.Question import *

class ZerohopQuestion(Question):
    def __init__(self, question):
        super(ZerohopQuestion, self).__init__(question)
        self.nodes.add(question['entrypoint']['node'])

        self.parse_a_entrypoint(question['entrypoint'])

    def serialize_sparql(self):
        return Serializer().serialize_zerohop_query(self.nodes, self.entrypoints)



