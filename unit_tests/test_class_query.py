import unittest
import sys
import os
sys.path.append('../')
from src.ClassQuery import ClassQuery
from src.QueryTool import QueryTool, Mode

base_path = os.path.dirname(__file__)
cq = ClassQuery(base_path + '/sample_queries/class_queries.xml')


class TestClassQuery(unittest.TestCase):
    def test_class_cluster(self):
        qt = QueryTool(base_path + '/sample_ttls/doc1.ttl', Mode.CLUSTER)
        responses, errors = cq.ask_all(qt)
        res = [len(x.find('justifications')) for x in responses.getchildren()]
        self.assertFalse(errors.get('errors'))
        self.assertEqual(res, [0, 2, 1])


