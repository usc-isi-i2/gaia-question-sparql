from SPARQLWrapper import SPARQLWrapper, JSONLD
from src.QuestionParser import QuestionParser
import json, itertools


class Answering(object):
    def __init__(self, endpoint='http://gaiadev01.isi.edu:7200/repositories/dry_en', ont_path='../resources/ontology_mapping.json'):
        self.query_wrapper = SPARQLWrapper(endpoint=endpoint)
        self.question_parser = QuestionParser(ont_path)

    def answer(self, xml_question):
        question = self.question_parser.parse_question(xml_question)

        # answer the question with strict query:
        strict_query = question.to_sparql()
        ans = self.query_db(strict_query)
        strategy_tried = {'strict': strict_query}

        if not self.good_answer(ans):
            strategies = iter(self.auto_strategies(question.STRATEGY_TYPE))
            while not self.good_answer(ans):
                # TODO: different order/priority ?
                strategy = next(strategies, None)
                if not strategy:
                    break
                q = question.to_sparql(relax_strategy=strategy)
                ans = self.query_db(q)
                strategy_tried['+'.join(strategy)] = q

        return {
            'strategies': strategy_tried,
            'json': question.query,
            'graph': ans
        }

    def answer_with_specified_strategy(self, xml_question, strategy=None):
        question = self.question_parser.parse_question(xml_question)
        q = question.to_sparql(relax_strategy=strategy)
        return {
            'strategies': {'+'.join(strategy): q},
            'json': question.query,
            'graph': self.query_db(q)
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

    @staticmethod
    def auto_strategies(S):
        to_try = []
        for m in range(1, len(S)+1):
            for s in itertools.combinations(S, m):
                to_try.append(s)
        return to_try
