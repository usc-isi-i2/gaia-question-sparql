from SPARQLWrapper import SPARQLWrapper
from .utils import *


class QueryWrapper(object):
    def __init__(self, endpoint):
        self.sw = SPARQLWrapper(endpoint)

    def select_query(self, query_string):
        self.sw.setQuery(PREFIX + query_string)
        self.sw.setReturnFormat('json')
        return self.sw.query().convert()['results']['bindings']

    @staticmethod
    def aug_dict_list(target_dict, key1, key2, value_to_append):
        if key1 in target_dict:
            if key2 in target_dict[key1]:
                target_dict[key1][key2].append(value_to_append)
            else:
                target_dict[key1][key2] = [value_to_append]
        else:
            target_dict[key1] = {key2: [value_to_append]}

    def query_text_justification(self, uri, res):
        # TODO: where to put confidence, in the sample response, confidence is of a node not of a single justification span
        q = '''
        SELECT DISTINCT ?doceid ?start ?end ?confidence 
        WHERE {
            <%s> aida:justifiedBy ?j .
            ?j a aida:TextJustification ;
                aida:source ?doceid ;
                aida:startOffset ?start ;
                aida:endOffsetInclusive ?end ;
                aida:confidence ?conf .
            ?conf aida:confidenceValue ?confidence .
        }
        ''' % uri
        justi = self.select_query(q)
        for j in justi:
            cur = {START: j[START]['value'], END: j[END]['value']}
            doceid = j[DOCEID]['value']
            self.aug_dict_list(res, doceid, TEXT_SPAN, cur)

    def query_video_justification(self, uri, res):
        q = '''
        SELECT DISTINCT ?doceid ?keyframeid ?topleftX ?topleftY ?bottomrightX ?bottomrightY ?confidence 
        WHERE {
            <%s> aida:justifiedBy ?j .
            ?j a aida:KeyframeVideoJustification ;
                aida:keyFrame ?keyframeid ;
                aida:boundingBox ?b;
                aida:confidence ?conf .
            ?conf aida:confidenceValue ?confidence .
            ?b aida:boundingBoxUpperLeftX ?topleftX ;
               aida:boundingBoxUpperLeftX ?topleftY ;
               aida:boundingBoxLowerRightX ?bottomrightX ;
               aida:boundingBoxLowerRightX ?bottomrightY .
        }
        ''' % uri
        justi = self.select_query(q)
        for j in justi:
            cur = {
                KEYFRAMEID: j[KEYFRAMEID]['value'],
                TOPLEFT: '%s,%s' % (j[TOPLEFT+'X']['value'], j[TOPLEFT+'Y']['value']),
                BOTTOMRIGHT: '%s,%s' % (j[BOTTOMRIGHT+'X']['value'], j[BOTTOMRIGHT+'Y']['value'])
            }
            doceid = j[DOCEID]['value']
            self.aug_dict_list(res, doceid, VIDEO_SPAN, cur)

    def query_image_justification(self, uri, res):
        q = '''
        SELECT DISTINCT ?doceid ?topleftX ?topleftY ?bottomrightX ?bottomrightY ?confidence 
        WHERE {
            <%s> aida:justifiedBy ?j .
            ?j a aida:ImageJustification ;
                aida:boundingBox ?b ;
                aida:confidence ?conf .
            ?conf aida:confidenceValue ?confidence .
            ?b aida:boundingBoxUpperLeftX ?topleftX ;
               aida:boundingBoxUpperLeftX ?topleftY ;
               aida:boundingBoxLowerRightX ?bottomrightX ;
               aida:boundingBoxLowerRightX ?bottomrightY .
        }
        ''' % uri
        justi = self.select_query(q)
        for j in justi:
            cur = {
                TOPLEFT: '%s,%s' % (j[TOPLEFT+'X']['value'], j[TOPLEFT+'Y']['value']),
                BOTTOMRIGHT: '%s,%s' % (j[BOTTOMRIGHT+'X']['value'], j[BOTTOMRIGHT+'Y']['value'])
            }
            doceid = j[DOCEID]['value']
            self.aug_dict_list(res, doceid, IMAGE_SPAN, cur)
