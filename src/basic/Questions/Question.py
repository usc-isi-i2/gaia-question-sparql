from src.basic.utils import *


class Question(object):
    def __init__(self, question: dict) -> None:
        """
        init a Question with a dict converted from a single xml query by xmltodict module
        :param question: single xml query in dict
        """
        self.ori = question
        self.query_id = question['@id']
        self.query_type = None

