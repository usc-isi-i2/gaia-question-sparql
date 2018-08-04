from SPARQLWrapper import SPARQLWrapper, JSONLD
from src.QuestionParser import QuestionParser
import json


class Answering(object):
    def __init__(self, endpoint='http://gaiadev01.isi.edu:3030/clusters/sparql', ont_path='../resources/ontology_mapping.json'):
        self.query_wrapper = SPARQLWrapper(endpoint=endpoint)
        self.question_parser = QuestionParser(ont_path)

    def answer(self, xml_question):
        question = self.question_parser.parse_question(xml_question)
        strategies = iter(question.relax.keys())

        # answer the question with strict query:
        strict_query = question.to_sparql()
        ans = self.query_db(strict_query)
        strategy_tried = {'strict': strict_query}
        while not self.good_answer(ans):
            # TODO: define strategies and apply to sparql query, and the try order/priority
            strategy = next(strategies, None)
            if not strategy:
                break
            q = question.to_sparql(relax_strategy=strategy)
            ans = self.query_db(q)
            strategy_tried[strategy] = q

        return {
            'strategies': strategy_tried,
            'json': question.query,
            'graph': ans
        }

    def query_db(self, sparql_query: str):
        self.query_wrapper.setQuery(sparql_query)
        self.query_wrapper.setReturnFormat(JSONLD)
        results = self.query_wrapper.query().convert()

        return json.loads(results.serialize(format='json-ld').decode('utf-8'))

    @staticmethod
    def good_answer(ans):
        if not ans or ans == '[]':
            return False
        return True