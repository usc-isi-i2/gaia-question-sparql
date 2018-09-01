from .Question import Question
from .utils import *


class Answer(object):
    def __init__(self, question: Question):
        self.question = question
        self.node_uri = {}
        # {'?attackt_event': ['http://example.com/event/111']}
        for node in question.nodes:
            self.node_uri[node] = []
        self.asked_uri = False

    def ask_uri(self):
        bindings = select_query(self.question.serialize_strict_sparql())
        for x in bindings:
            for node in self.question.nodes:
                self.node_uri[node].append(x[node.lstrip('?')]['value'])
        self.asked_uri = True

    def ask_justifications(self):
        if not self.asked_uri:
            self.ask_uri()

        # TODO: get justifications and format xml response
