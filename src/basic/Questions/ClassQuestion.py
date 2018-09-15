

from src.basic.Questions.Question import *
from src.basic.utils import *


class ClassQuestion(Question):
    def __init__(self, question):
        super(ClassQuestion, self).__init__(question)

        self.query_type = CLASS_QUERY
        self.enttype = question[ENTTYPE]

