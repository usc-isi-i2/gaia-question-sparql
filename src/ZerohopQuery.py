from src.utils import *
from src.sparql_utils import *
from src.QueryTool import QueryTool


class ZerohopQuery(object):
    def __init__(self, xml_file_or_string: str):
        self.root = ET.Element('zerohopquery_responses')
        self.query_list = xml_loader(xml_file_or_string, ZEROHOP_QUERY)

    def ask_all(self, quert_tool: QueryTool, start=0, end=None, root_doc=''):
        if not end:
            end = len(self.query_list)
        for i in range(start, end):
            if c2p[list(find_keys(DOCEID, self.query_list[i][ENTRYPOINT]))[0]] == root_doc:
                response = self.ans_one(quert_tool, self.query_list[i])
                if len(response):
                    self.root.append(response)

    def ans_one(self, quert_tool, q_dict):
        '''
        :param endpoint: sparql endpoint or rdflib graph
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

        root = ET.Element('zerohopquery_response', attrib={'id':  q_dict['@id']})

        # first get entrypoint node uri
        ep = q_dict[ENTRYPOINT]
        node_uri = quert_tool.get_best_node([ep])
        if not node_uri:
            return root

        # and then find justifications
        # TODO: take cluster member in ta1?? as NIST's sparql sample?
        # TODO: seems CU use clusters for cross doc linkings, RPI has no clusters
        # TODO: now find justi on node_uri, NIST sparql is to find on type_statement uri, mjr said we'll argue on it
        rows = quert_tool.get_justi(node_uri)
        update_xml(root, {'system_nodeid': node_uri})
        construct_justifications(root, None, rows)

        return root

    def dump_responses(self, output_file):
        if len(self.root):
            write_file(self.root, output_file)
            return True
        return False






