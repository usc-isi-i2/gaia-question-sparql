from src.basic.XMLLoader import XMLLoader
from src.advanced.AdvancedAnswer import AdvancedAnswer


class AdvancedXMLLoader(XMLLoader):
    @staticmethod
    def answer_one(question, endpoint):
        ans = AdvancedAnswer(question, endpoint).ask_auto_try_relaxation()
        return ans

    @staticmethod
    def answer_one_specify_relaxation(question, endpoint, relaxation):
        ans = AdvancedAnswer(question, endpoint).ask(relaxation)
        return ans


