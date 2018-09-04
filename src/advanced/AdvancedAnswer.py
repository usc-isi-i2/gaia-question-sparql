
from src.basic.Answer import Answer
from src.advanced.AdvancedQuestion import AdvancedQuestion


class AdvancedAnswer(Answer):
    def __init__(self, question: AdvancedQuestion or str, endpoint: str):
        Answer.__init__(self, question if isinstance(question, AdvancedQuestion) else AdvancedQuestion(question), endpoint)

    def ask_auto_try_relaxation(self):
        pass

    def ask_with_specified_relaxation(self, relaxation):
        relax_sparql = self.question.serialize_relax_sparql(relaxation)
        print(relax_sparql)
        self.ask_uri(relax_sparql)
        self.ask_justifications()
        return {
            'sparql': relax_sparql,
            'response': self.construct_xml_response()
        }
