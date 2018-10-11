import unittest
import sys
import os
sys.path.append('../')
from src.class_query import ClassQuery
from src.query_tool import QueryTool, Mode

base_path = os.path.dirname(__file__)
cq = ClassQuery(base_path + '/sample_queries/class_queries.xml')


class TestClassQuery(unittest.TestCase):
    def test_class_cluster(self):
        qt = QueryTool(base_path + '/sample_ttls/doc1.ttl', Mode.CLUSTER)
        responses, stat, errors = cq.ask_all(qt)
        res = [len(x.find('justifications')) for x in responses.getchildren()]
        self.assertFalse(errors)
        self.assertEqual(res, [0, 2, 1])


