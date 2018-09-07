

from src.basic.Questions.Question import *

class ZerohopQuestion(Question):
    def __init__(self, question):
        super(ZerohopQuestion, self).__init__(question)

        self.nodes.add(question[ENTRYPOINT][NODE])
        self.parse_a_entrypoint(question[ENTRYPOINT])





