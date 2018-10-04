
import sys
sys.path.append('../')
from src.ClassQuery import ClassQuery
from src.ZerohopQuery import ZerohopQuery
from src.GraphQuery import GraphQuery
from src.QueryTool import QueryTool, Mode
from src.utils import *

cq = ClassQuery('./sample_queries/class_queries.xml')
zq = ZerohopQuery('./sample_queries/zerohop_queries.xml')
gq = GraphQuery('./sample_queries/graph_queries.xml')


def test_class_singleton():
    qt = QueryTool('./sample_ttls/doc1.ttl', Mode.SINGLETON)
    responses, errors = cq.ask_all(qt)
    pprint(responses)
    pprint(errors)


def test_class_cluster():
    qt = QueryTool('./sample_ttls/doc1.ttl', Mode.CLUSTER)
    responses, errors = cq.ask_all(qt)
    pprint(responses)
    pprint(errors)


def test_class_prototype():
    qt = QueryTool('./sample_ttls/doc1.ttl', Mode.PROTOTYPE)
    responses, errors = cq.ask_all(qt)
    pprint(responses)
    pprint(errors)


def test_zerohop_singleton():
    qt = QueryTool('./sample_ttls/doc1.ttl', Mode.SINGLETON)
    responses, errors = zq.ask_all(qt)
    pprint(responses)
    pprint(errors)


def test_zerohop_cluster():
    qt = QueryTool('./sample_ttls/doc1.ttl', Mode.CLUSTER)
    responses, errors = zq.ask_all(qt)
    pprint(responses)
    pprint(errors)


def test_zerohop_prototype():
    qt = QueryTool('./sample_ttls/doc1.ttl', Mode.PROTOTYPE)
    responses, errors = zq.ask_all(qt)
    pprint(responses)
    pprint(errors)


def test_graph_singleton():
    qt = QueryTool('./sample_ttls/doc1.ttl', Mode.SINGLETON)
    responses, errors = gq.ask_all(qt)
    pprint(responses)
    pprint(errors)


def test_graph_cluster():
    qt = QueryTool('./sample_ttls/doc1.ttl', Mode.CLUSTER, relax_num_ep=1)
    responses, errors = gq.ask_all(qt)
    pprint(responses)
    pprint(errors)


def test_graph_prototype():
    qt = QueryTool('./sample_ttls/doc1.ttl', Mode.PROTOTYPE)
    responses, errors = gq.ask_all(qt)
    pprint(responses)
    pprint(errors)


test_graph_cluster()
test_zerohop_cluster()
test_graph_prototype()
