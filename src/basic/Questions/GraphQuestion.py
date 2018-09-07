
from src.basic.Questions.Question import *


class GraphQuestion(Question):
    def __init__(self, question):
        super(GraphQuestion, self).__init__(question)

        self.parse_an_edge(question['graph'][EDGES][EDGE])
        self.parse_a_entrypoint(question[ENTRYPOINTS][ENTRYPOINT])

        # import json
        # print(json.dumps(self.edges, indent=2))
        # print(json.dumps(self.entrypoints, indent=2))
        # print(self.nodes)

    def parse_an_edge(self, edge: list or dict):
        if isinstance(edge, list):
            for an_edge in edge:
                self.parse_an_edge(an_edge)
        else:
            self.nodes.add(edge[SUBJECT])
            self.nodes.add('?' + edge['@id'])
            self.nodes.add(edge[OBJECT])
            self.edges.append({
                '?' + edge['@id']: [
                    (RDF_TYPE, RDF_STATEMENT),
                    (RDF_SUBJECT, edge[SUBJECT]),
                    (RDF_PREDICATE, ldcOnt + ':' + edge[PREDICATE]),
                    (RDF_OBJECT, edge[OBJECT])
                ]
            })

