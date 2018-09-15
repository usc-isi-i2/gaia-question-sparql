from src.basic.Questions.Question import Question
from src.basic.QueryWrapper import QueryWrapper
from src.basic.Serializer import Serializer
from src.basic.utils import *


class Answer(object):
    def __init__(self, question: Question, endpoint: str):
        self.question = question
        self.node_uri = []
        # {'?attackt_event': 'http://example.com/event/111'}
        self.node_justification = {}
        self.qw = QueryWrapper(endpoint)

    def ask(self):
        strict_sparql = Serializer(self.question).serialize_select_query()
        print(strict_sparql)
        return self.send_query(strict_sparql)

    def send_query(self, sparql_query):
        self.ask_uri(sparql_query)
        if self.question.query_type == GRAPH_QUERY:
            self.ask_justifications()
        root = self.construct_xml_response()
        xml_response = minidom.parseString(ET.tostring(root)).toprettyxml()
        return self.wrap_result(sparql_query, xml_response)

    def ask_uri(self, strict_sparql):
        # print(strict_sparql)
        bindings = self.qw.select_query(strict_sparql)
        # print(bindings)
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

    # def construct_xml_response(self):
    #     root = None
    #     if isinstance(self.question, ClassQuestion):
    #         root = self.construct_xml_response_class()
    #     elif isinstance(self.question, ZerohopQuestion):
    #         root = self.construct_xml_response_zerohop()
    #     elif isinstance(self.question, GraphQuestion):
    #         root = self.construct_xml_response_graph()
    #     return minidom.parseString(ET.tostring(root)).toprettyxml()

    def construct_xml_response(self):
        qtype = self.question.query_type
        if qtype == GRAPH_QUERY:
            root = self.construct_xml_response_graph()
        elif qtype == CLASS_QUERY:
            root = ET.Element('classquery_response', attrib={'id': self.question.query_id})
            justifications = ET.SubElement(root, 'justifications')
            self.construct_justifications(justifications)
        else:
            # ?nid_ep ?nid_ot ?doceid ?sid ?kfid ?so ?eo ?ulx ?uly ?brx ?bry ?st ?et ?cm1cv ?cm2cv ?cv
            root = ET.Element('zerohopquery_response', attrib={'id': self.question.query_id})
            self.update_xml(root, {'system_nodeid': self.node_uri[0]['?nid_ep']['value']})
            self.construct_justifications(root)
        return root

    def construct_justifications(self, justi_root):
        for row in self.node_uri:
            # ?doceid ?sid ?kfid ?so ?eo ?ulx ?uly ?brx ?bry ?st ?et ?cv
            row_ = {'doceid': row['?doceid'], 'enttype': self.question.ori[ENTTYPE], 'confidence': row['?cv']}
            if '?so' in row:
                type_ = 'text'
                row_.update({'start': row['?so'], 'end': row['?eo']})
            elif '?kfid' in row:
                type_ = 'video'
                row_.update({'keyframeid': row['?kfid'],
                             'topleft': '%s,%s' % (row['?ulx'], row['?uly']),
                             'bottomright': '%s,%s' % (row['?brx'], row['?bry']),
                             })
            elif '?sid' in row:
                type_ = 'shot'
                row_.update({'shotid': row['?sid'],
                             'topleft': '%s,%s' % (row['?ulx'], row['?uly']),
                             'bottomright': '%s,%s' % (row['?brx'], row['?bry']),
                             })
            elif '?st' in row:
                type_ = 'audio'
                row_.update({'start': row['?st'], 'end': row['?et']})
            else:
                type_ = 'image'
                row_.update({'topleft': '%s,%s' % (row['?ulx'], row['?uly']),
                             'bottomright': '%s,%s' % (row['?brx'], row['?bry']),
                             })
            justification = ET.SubElement(justi_root, type_ + '_justification')
            self.update_xml(justification, row_)

    # def flatten_justifications_to_xml(self, root):
    #     justifications = ET.SubElement(root, 'justifications')
    #     for node_key in self.node_justification:
    #         self.update_xml(justifications, {'system_nodeid': self.node_uri[0][node_key]})
    #         for doceid, spans in self.node_justification[node_key].items():
    #             for span_key, list_spans in spans.items():
    #                 for span in list_spans:
    #                     updated_span = {'doceid': doceid, **span}
    #                     self.update_xml(justifications, {span_key: updated_span})

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
