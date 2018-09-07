

from src.basic.Questions.Question import *


class ClassQuestion(Question):
    def __init__(self, question):
        super(ClassQuestion, self).__init__(question)

        sub = '?x'
        self.nodes.add(sub)
        self.enttype = self.parse_enttype(sub, question[ENTTYPE])

