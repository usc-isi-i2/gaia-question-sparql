
prefix = {
    "aida": "https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/InterchangeOntology#",
    "ldcOnt": "https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
}

PREFIX = '\n'.join(['PREFIX %s: <%s>' % (k, v) for k, v in prefix.items()])

SUBJECT = 'subject'
PREDICATE = 'predicate'
OBJECT = 'object'

GRAPH = 'graph'
EDGES = 'edges'
EDGE = 'edge'
ENTRYPOINTS = 'entrypoints'
ENTRYPOINT = 'entrypoint'

NODE = 'node'
ENTTYPE = 'enttype'

DESCRIPTORS = 'descriptors'

TYPED_DESCRIPTOR = 'typed_descriptor'

STRING_DESCRIPTOR = 'string_descriptor'
NAME_STRING = 'name_string'

TEXT_DESCRIPTOR = 'text_descriptor'
DOCEID = 'doceid'
START = 'start'
END = 'end'

VIDEO_DESCRIPTOR = 'video_descriptor'
KEYFRAMEID = 'keyframeid'
TOPLEFT = 'topleft'
BOTTOMRIGHT = 'bottomright'

CONFIDENCE = 'confidence'

IMAGE_DESCRIPTOR = 'image_descriptor'

ldcOnt = 'ldcOnt'
RDF_TYPE = 'rdf:type'

RDF_STATEMENT = 'rdf:Statement'
RDF_SUBJECT = 'rdf:subject'
RDF_PREDICATE = 'rdf:predicate'
RDF_OBJECT = 'rdf:object'

AIDA_ENTITY = 'aida:Entity'

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

TEXT_SPAN = 'text_span'
VIDEO_SPAN = 'video_span'
IMAGE_SPAN = 'image_span'

AIDA_PROTOTYPE = 'aida:prototype'

ENTTYPE_MAPPINT = {
    'Place': ldcOnt + ':' + 'Location'
}

GRAPH_QUERIES = 'graph_queries'
GRAPH_QUERY = 'graph_query'
CLASS_QUERIES = 'class_queries'
CLASS_QUERY = 'class_query'
ZEROHOP_QUERIES = 'zerohop_queries'
ZEROHOP_QUERY = 'zerohop_query'
CLASS = 'class'
ZEROHOP = 'zerohop'


EPSO = 'epso'
EPEO = 'epeo'
EPULX = 'epulx'
EPULY = 'epuly'
EPBRX = 'epbrx'
EPBRY = 'epbry'

BOUND_VARS = ' '.join(['?' + x for x in (EPSO, EPEO, EPULX, EPULY, EPBRX, EPBRY)])
