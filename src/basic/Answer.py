from src.basic.Questions.ClassQuestion import ClassQuestion
from src.basic.Questions.ZerohopQuestion import ZerohopQuestion
from src.basic.Questions.GraphQuestion import GraphQuestion
from src.basic.Questions.Question import Question
from src.basic.QueryWrapper import QueryWrapper
from src.basic.utils import *


class Answer(object):
    def __init__(self, question: Question, endpoint: str):
        self.question = question
        self.node_uri = []
        # {'?attackt_event': ['http://example.com/event/111']}
        self.node_justification = {}
        self.qw = QueryWrapper(endpoint)

    def ask(self):
        strict_sparql = self.question.serialize_sparql()
        return self.send_query(strict_sparql)

    def send_query(self, sparql_query):
        try:
            self.ask_uri(sparql_query)
            self.ask_justifications()
            try:
                return self.wrap_result(sparql_query, self.construct_xml_response())
            except Exception as e:
                return self.wrap_result(sparql_query, '%s\nCONSTRUCT XML RESPONSE FAILED: \n%s' % (str(self.node_uri), str(e)))

        except Exception as e:
            return self.wrap_result(sparql_query, 'SPARQL QUERY FAILED: \n%s' % str(e))

    def ask_uri(self, strict_sparql):
        bindings = self.qw.select_query(strict_sparql)
        for raw in bindings:
            cur = {}
            for var_name, cell in raw.items():
                cur['?' + var_name] = cell['value']
            self.node_uri.append(cur)

    def ask_justifications(self):
        # TODO: there can be multiple results, return each as a response?
        # Now only return the first result
        if not self.node_uri:
            return
        for node, uri in self.node_uri[0].items():
            justi = {}
            self.qw.query_text_justification(uri, justi)
            self.qw.query_image_justification(uri, justi)
            self.qw.query_video_justification(uri, justi)
            self.node_justification[node] = justi

    def construct_xml_response(self):
        root = None
        if isinstance(self.question, ClassQuestion):
            root = self.construct_xml_response_class()
        elif isinstance(self.question, ZerohopQuestion):
            root = self.construct_xml_response_zerohop()
        elif isinstance(self.question, GraphQuestion):
            root = self.construct_xml_response_graph()
        return minidom.parseString(ET.tostring(root)).toprettyxml()

    def construct_xml_response_class(self):
        root = ET.Element('classquery_response', attrib={'id': self.question.query_id})
        self.flatten_justifications_to_xml(root)
        return root

    def construct_xml_response_zerohop(self):
        root = ET.Element('zerohopquery_response', attrib={'id': self.question.query_id})
        self.flatten_justifications_to_xml(root)
        return root

    def flatten_justifications_to_xml(self, root):
        justifications = ET.SubElement(root, 'justifications')
        for node_key in self.node_justification:
            self.update_xml(justifications, {'system_nodeid': self.node_uri[0][node_key]})
            for doceid, spans in self.node_justification[node_key].items():
                for span_key, list_spans in spans.items():
                    for span in list_spans:
                        updated_span = {'doceid': doceid, **span}
                        self.update_xml(justifications, {span_key: updated_span})

    def construct_xml_response_graph(self):
        root = ET.Element('graphquery_response', attrib={'id': self.question.query_id})
        for edge in self.question.edges:
            for k, pairs in edge.items():
                justifications = ET.SubElement(ET.SubElement(root, 'edge', id=k.lstrip('?')), 'justifications')
                docs = {}
                for node_key, justi_key in ((pairs[1][1], 'subject_justification'),
                                            (pairs[3][1], 'object_justification'),
                                            (k, 'edge_justification')):
                    if node_key not in self.node_justification:
                        continue
                    for doceid, spans in self.node_justification[node_key].items():
                        if doceid not in docs:
                            docs[doceid] = {}
                        if justi_key not in docs[doceid]:
                            # TODO: what to put in system_nodeid and confidence
                            # TODO: decrease spans ?:
                            # 'Evaluation Plan v0.7':
                            # (7)	The justification for an edge must contain three elements:
                            # a.	subject_justification, containing exactly one span that is a mention of the subject (entity/filler, relation, or event)
                            # b.	object_justification containing exactly one span that is a mention of the object (entity/filler, relation, or event)
                            # c.	edge_justification containing up to two spans, connecting the subject to the object via the predicate
                            docs[doceid][justi_key] = {'system_nodeid': self.node_uri[0][node_key], 'confidence': '1.0'}

                        docs[doceid][justi_key].update(spans)

                for doc, justi in docs.items():
                    self.update_xml(ET.SubElement(justifications, 'justification', docid=doc), justi)
        return root

    def update_xml(self, root, obj):
        if isinstance(obj, str):
            root.text = obj
        elif isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, list):
                    for v_ in v:
                        self.update_xml(ET.SubElement(root, k), v_)
                else:
                    self.update_xml(ET.SubElement(root, k), v)

    @staticmethod
    def wrap_result(sparql, response):
        return {
            'sparql': sparql,
            'response': response
        }
