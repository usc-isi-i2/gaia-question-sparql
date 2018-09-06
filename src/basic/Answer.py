
from src.basic.Question import Question
from src.basic.QueryWrapper import QueryWrapper
from src.basic.utils import *


class Answer(object):
    def __init__(self, question: Question or str, endpoint: str):
        if isinstance(question, Question):
            self.question = question
        else:
            self.question = Question(question)
        self.node_uri = []
        # {'?attackt_event': ['http://example.com/event/111']}
        self.node_justification = {}
        self.qw = QueryWrapper(endpoint)

    def ask(self):
        strict_sparql = self.question.serialize_strict_sparql()
        return self.send_query(strict_sparql)

    def send_query(self, sparql_query):
        try:
            self.ask_uri(sparql_query)
            self.ask_justifications()
            return self.wrap_result(sparql_query, self.construct_xml_response())
        except Exception as e:
            return self.wrap_result(sparql_query, str(e))

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
        root = ET.Element('graphquery_responses', attrib={'id': self.question.query_id})
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
        return minidom.parseString(ET.tostring(root)).toprettyxml()

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
