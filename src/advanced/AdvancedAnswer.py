
from src.basic.Answer import Answer
from src.advanced.AdvancedSerializer import AdvancedSerializer
from src.advanced.Relaxation import Relaxation


class AdvancedAnswer(Answer):

    def ask_auto_try_relaxation(self):
        pass

    def ask(self, relaxation=None):
        if not relaxation:
            return super(AdvancedAnswer, self).ask()
        try:
            rlx = Relaxation(**relaxation)
            sparql_query = AdvancedSerializer(self.question).serialize_select_query(rlx)
            return self.send_query(sparql_query)
        except TypeError as e:
            res = 'Invalid relaxation: %s \n\t TypeError %s \n %s' % (str(relaxation), str(e), Relaxation.help())
            return self.wrap_result('', res)



