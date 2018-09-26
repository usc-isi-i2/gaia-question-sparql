from src.utils import *


class ClassQuery(object):
    def __init__(self, xml_file_or_string):
        self.root = ET.Element('classquery_responses')
        self.query_list = xml_loader(xml_file_or_string, CLASS_QUERY)

    def ask_all(self, endpoint, start=0, end=None):
        if not end:
            end = len(self.query_list)
        for i in range(start, end):
            response = self.ans_one(endpoint, self.query_list[i])
            if len(response):
                self.root.append(response)

    def ans_one(self, endpoint, q_dict):
        '''
        :param endpoint: sparql endpoint or rdflib graph
        :param q_dict: {
            '@id': 'CLASS_QUERY_1',
            'enttype': 'PERSON'
        }
        :return: xml Element
        '''
        enttype = q_dict[ENTTYPE]
        sparql_query = self.to_sparql(enttype)
        rows = select_query(endpoint, sparql_query)

        root = ET.Element('classquery_response', attrib={'id':  q_dict['@id']})
        justifications = ET.SubElement(root, 'justifications')
        construct_justifications(justifications, enttype, rows)

        return root

    def dump_responses(self, output_file):
        if len(self.root):
            write_file(self.root, output_file)
            return True
        return False

    @staticmethod
    def to_sparql(enttype):
        return '''
        SELECT DISTINCT ?doceid ?sid ?kfid ?so ?eo ?ulx ?uly ?brx ?bry ?st ?et ?cv
        WHERE {
            ?statement1    a                    rdf:Statement .
            ?statement1    rdf:object           ldcOnt:%s .
            ?statement1    rdf:predicate        rdf:type .
            ?statement1    aida:justifiedBy     ?justification .
            ?justification aida:source          ?doceid .
            ?justification aida:confidence      ?confidence .
            ?confidence    aida:confidenceValue ?cv .
    
            OPTIONAL { 
                ?justification a                           aida:TextJustification .
                ?justification aida:startOffset            ?so .
                ?justification aida:endOffsetInclusive     ?eo 
            }
    
            OPTIONAL { 
                ?justification a                           aida:ImageJustification .
                ?justification aida:boundingBox            ?bb  .
                ?bb            aida:boundingBoxUpperLeftX  ?ulx .
                ?bb            aida:boundingBoxUpperLeftY  ?uly .
                ?bb            aida:boundingBoxLowerRightX ?brx .
                ?bb            aida:boundingBoxLowerRightY ?bry 
            }
    
            OPTIONAL { 
                ?justification a                           aida:KeyFrameVideoJustification .
                ?justification aida:keyFrame               ?kfid .
                ?justification aida:boundingBox            ?bb  .
                ?bb            aida:boundingBoxUpperLeftX  ?ulx .
                ?bb            aida:boundingBoxUpperLeftY  ?uly .
                ?bb            aida:boundingBoxLowerRightX ?brx .
                ?bb            aida:boundingBoxLowerRightY ?bry 
            }
    
            OPTIONAL { 
                ?justification a                           aida:ShotVideoJustification .
                ?justification aida:shot                   ?sid 
            }
    
            OPTIONAL { 
                ?justification a                           aida:AudioJustification .
                ?justification aida:startTimestamp         ?st .
                ?justification aida:endTimestamp           ?et 
            }
        }
        ''' % enttype
