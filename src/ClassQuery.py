from src.utils import *


class ClassQuery(object):
    def __init__(self, xml_file_or_string):
        self.query_list = xml_loader(xml_file_or_string, CLASS_QUERY)

    def ask_all(self, query_tool, start=0, end=None, root_doc='', prefilter=False):
        root = ET.Element('classquery_responses')
        errors = []
        if not end:
            end = len(self.query_list)
        for i in range(start, end):
            try:
                response = self.ans_one(query_tool, self.query_list[i])
                if len(response):
                    root.append(response)
            except Exception as e:
                errors.append(','.join((root_doc, self.query_list[i]['@id'], str(i), str(e))))
        return root, None, errors

    def ans_one(self, query_tool, q_dict):
        '''
        :param query_tool
        :param q_dict: {
            '@id': 'CLASS_QUERY_1',
            'enttype': 'PERSON'
        }
        :return: xml Element
        '''
        enttype = q_dict[ENTTYPE]
        sparql_query = self.to_sparql(enttype)
        rows = query_tool.select(sparql_query)
        single_root = ET.Element('classquery_response', attrib={'QUERY_ID':  q_dict['@id']})
        justifications = ET.SubElement(single_root, 'justifications')
        construct_justifications(justifications, enttype, rows)
        return single_root

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
