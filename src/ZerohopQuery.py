from src.utils import *
from src.sparql_utils import *
from src.get_best_node import get_best_node


class ZerohopQuery(object):
    def __init__(self, xml_file_or_string):
        self.root = ET.Element('zerohopquery_responses')
        self.query_list = xml_loader(xml_file_or_string, ZEROHOP_QUERY)

    def ask_all(self, endpoint, start=0, end=None):
        if not end:
            end = len(self.query_list)
        for i in range(start, end):
            response = self.ans_one(endpoint, self.query_list[i])
            self.root.append(response)

    def ans_one(self, endpoint, q_dict):
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
        node_uri = get_best_node([ep], endpoint)
        if not node_uri:
            return root

        # and then find justifications
        # TODO: take cluster member in ta1?? as NIST's sparql sample?
        # TODO: seems CU use clusters for cross doc linkings, RPI has no clusters
        # TODO: now find justi on node_uri, NIST sparql is to find on type_statement uri, mjr said we'll argue on it
        sparql_justi = serialize_get_justi(node_uri, True)
        rows = select_query(endpoint, sparql_justi)
        update_xml(root, {'system_nodeid': node_uri})
        construct_justifications(root, None, rows)

        return root

    def dump_responses(self, output_file):
        write_file(self.root, output_file)





