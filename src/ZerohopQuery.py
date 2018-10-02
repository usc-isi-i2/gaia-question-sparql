
from src.sparql_utils import *
from src.QueryTool import QueryTool


class ZerohopQuery(object):
    def __init__(self, xml_file_or_string: str):
        self.query_list = xml_loader(xml_file_or_string, ZEROHOP_QUERY)
        self.query_docs = [c2p.get(list(find_keys(DOCEID, q[ENTRYPOINT]))[0]) for q in self.query_list]

    def ask_all(self, quert_tool: QueryTool, start=0, end=None, root_doc=''):
        root = ET.Element('zerohopquery_responses')
        errors = []
        related = ['0' for _ in range(len(self.query_list))]
        has_res = ['0' for _ in range(len(self.query_list))]
        if not end:
            end = len(self.query_list)
        for i in range(start, end):
            try:
                if root_doc and self.query_docs[i] != root_doc:
                    continue
                related[i] = '1'
                response = self.ans_one(quert_tool, self.query_list[i])
                if len(response):
                    has_res[i] = '1'
                    root.append(response)
            except Exception as e:
                errors.append(','.join((root_doc, self.query_list[i]['@id'], str(i), str(e))))
        return root, {'errors': errors, 'related': related, 'has_res': has_res}

    def ans_one(self, quert_tool, q_dict):
        '''
        :param quert_tool
        :param q_dict: {
            '@id': 'ZEROHOP_QUERY_1',
            'entrypoint': {
                'node': '?node',
                'enttype': 'PERSON',
                'xxx_descriptor': {
                    'doceid': 'xxx',
                    ...
                }
            }
        }
        :return: xml Element
        '''

        single_root = ET.Element('zerohopquery_response', attrib={'id':  q_dict['@id']})

        # first get entrypoint node uri
        ep = q_dict[ENTRYPOINT]
        node_uri = quert_tool.get_best_node([ep])
        if not node_uri:
            return single_root

        # and then find justifications
        # TODO: now find justi on node_uri, NIST sparql is to find on type_statement uri, mjr said we'll argue on it
        rows = quert_tool.get_justi(node_uri)
        update_xml(single_root, {'system_nodeid': node_uri})
        construct_justifications(single_root, None, rows)
        return single_root
