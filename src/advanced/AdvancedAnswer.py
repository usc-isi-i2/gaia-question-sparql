
from src.basic.Answer import Answer
from src.advanced.AdvancedQuestion import AdvancedQuestion
from src.advanced.Relaxation import Relaxation

class AdvancedAnswer(Answer):
    def __init__(self, question: AdvancedQuestion or str, endpoint: str):
        q = question
        if not isinstance(question, AdvancedQuestion):
            q = AdvancedQuestion(question)
        Answer.__init__(self, q, endpoint)

    def ask_auto_try_relaxation(self):
        pass

    def ask(self, relaxation=None):
        if not relaxation:
            return super(AdvancedAnswer, self).ask()
        try:
            rlx = Relaxation(**relaxation)
            sparql_query = self.question.serialize_relax_sparql(rlx)
            return self.send_query(sparql_query)
        except TypeError as e:
            res = 'Invalid relaxation: %s \n\t TypeError %s \n %s' % (str(relaxation), str(e), Relaxation.help())
            return self.wrap_result('', res)



