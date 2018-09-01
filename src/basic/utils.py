from SPARQLWrapper import SPARQLWrapper


prefix = {
    "aida": "https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/InterchangeOntology#",
    "ldcOnt": "https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
}

PREFIX = '\n'.join(['PREFIX %s: <%s>' % (k, v) for k, v in prefix.items()])

ENDPOINT = 'http://gaiadev01.isi.edu:3030/latest_rpi_en/query'


def select_query(query_string):
    sw = SPARQLWrapper(ENDPOINT)
    sw.setQuery(PREFIX + query_string)
    sw.setReturnFormat('json')
    return sw.query().convert()['results']['bindings']


SUBJECT = 'subject'
PREDICATE = 'predicate'
OBJECT = 'object'

NODE = 'node'
ENTTYPE = 'enttype'

DESCRIPTORS = 'descriptors'

STRING_DESCRIPTOR = 'string_descriptor'
NAME_STRING = 'name_string'

TEXT_DESCRIPTOR = 'text_descriptor'
DOCEID = 'doceid'
START = 'start'
END = 'end'

VEDIO_DESCRIPTOR = 'video_descriptor'
KEYFRAMEID = 'keyframeid'
TOPLEFT = 'topleft'
BOTTOMRIGHT = 'bottomright'

IMAGE_DESCRIPTOR = 'image_descriptor'

ldcOnt = 'ldcOnt'
RDF_TYPE = 'rdf:type'

RDF_STATEMENT = 'rdf:Statement'
RDF_SUBJECT = 'rdf:subject'
RDF_PREDICATE = 'rdf:predicate'
RDF_OBJECT = 'rdf:object'

AIDA_HASNAME = 'aida:hasName'

AIDA_JUSTIFIEDBY = 'aida:justifiedBy'
AIDA_TEXTJUSTIFICATION = 'aida:TextJustification'
AIDA_IMAGEJUSTIFICATION = 'aida:ImageJustification'
AIDA_VIDEOJUSTIFICATION = 'aida:KeyframeVideoJustification'

AIDA_SOURCE = 'aida:source'
AIDA_STARTOFFSET = 'aida:startOffset'
AIDA_ENDOFFSETINCLUSIVE = 'aida:endOffsetInclusive'
AIDA_KEYFRAME = 'aida:keyFrame'

AIDA_BOUNDINGBOX = 'aida:BoundingBox'
AIDA_BOUNDINGBOXUPPERLEFTX = 'aida:boundingBoxUpperLeftX'
AIDA_BOUNDINGBOXUPPERLEFTY = 'aida:boundingBoxUpperLeftY'
AIDA_BOUNDINGBOXLOWERRIGHTX = 'aida:boundingBoxLowerRightX'
AIDA_BOUNDINGBOXLOWERRIGHTY = 'aida:boundingBoxLowerRightY'
