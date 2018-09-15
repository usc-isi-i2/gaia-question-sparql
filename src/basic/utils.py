import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

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


def class_query(enttype):
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


def zerohop_query(enttype, descriptor):
    """

    :param enttype: GeopoliticalEntity
    :param descriptor: {
              "doceid": "HC0000077",
              "keyframeid": "HC0000077_1",
              "topleft": "0,0",
              "bottomright": "480,360"
            }
    :return: sparql query string
    """
    doceid = descriptor[DOCEID]
    start = descriptor.get(START)
    if start:
        end = descriptor.get(END)
        constrain = zerohop_query_text(doceid, start, end)
    else:
        keyframeid = descriptor.get(KEYFRAMEID)
        top, left = descriptor.get(TOPLEFT, ',').split(',')
        bottom, right = descriptor.get(BOTTOMRIGHT, ',').split(',')
        constrain = zerohop_query_image_video(doceid, keyframeid, top, left, bottom, right)
    return '''
    SELECT DISTINCT ?nid_ep ?nid_ot ?doceid ?sid ?kfid ?so ?eo ?ulx ?uly ?brx ?bry ?st ?et ?cm1cv ?cm2cv ?cv
	WHERE {
		?statement1    a                    rdf:Statement .
		?statement1    rdf:object           ldcOnt:%s .
		?statement1    rdf:predicate        rdf:type .
		?statement1    rdf:subject          ?nid_ot .
		?statement1    aida:justifiedBy     ?justification .
		?justification aida:source          ?doceid .
		?justification aida:confidence      ?confidence .
		?confidence    aida:confidenceValue ?cv .

		?cluster        a                    aida:SameAsCluster .
		?statement2     a                    aida:ClusterMembership .
		?statement2     aida:cluster         ?cluster .
		?statement2     aida:clusterMember   ?nid_ep .
		?statement2     aida:confidence      ?cm1_confidence .
		?cm1_confidence aida:confidenceValue ?cm1cv .

		?statement3     a                    aida:ClusterMembership .
		?statement3     aida:cluster         ?cluster .
		?statement3     aida:clusterMember   ?nid_ot .
		?statement3     aida:confidence      ?cm2_confidence .
		?cm2_confidence aida:confidenceValue ?cm2cv .

		?statement4       a                         rdf:Statement .
		?statement4       rdf:object                ldcOnt:%s .
		?statement4       rdf:predicate             rdf:type .
		?statement4       rdf:subject               ?nid_ep .
		?statement4       aida:justifiedBy          ?justification_ep .
		
        %s

		OPTIONAL { ?justification a                  aida:TextJustification .
			?justification aida:startOffset            ?so .
			?justification aida:endOffsetInclusive     ?eo }

		OPTIONAL { ?justification a                  aida:ImageJustification .
			?justification aida:boundingBox            ?bb  .
			?bb            aida:boundingBoxUpperLeftX  ?ulx .
			?bb            aida:boundingBoxUpperLeftY  ?uly .
			?bb            aida:boundingBoxLowerRightX ?brx .
			?bb            aida:boundingBoxLowerRightY ?bry }

		OPTIONAL { ?justification a                  aida:KeyFrameVideoJustification .
			?justification aida:keyFrame               ?kfid .
			?justification aida:boundingBox            ?bb  .
			?bb            aida:boundingBoxUpperLeftX  ?ulx .
			?bb            aida:boundingBoxUpperLeftY  ?uly .
			?bb            aida:boundingBoxLowerRightX ?brx .
			?bb            aida:boundingBoxLowerRightY ?bry }

		OPTIONAL { ?justification a                  aida:ShotVideoJustification .
			?justification aida:shot                   ?sid }

		OPTIONAL { ?justification a                  aida:AudioJustification .
			?justification aida:startTimestamp         ?st .
			?justification aida:endTimestamp           ?et }

	}
    ''' % (enttype, enttype, constrain)


def zerohop_query_text(doceid, start, end):
    return '''
		?justification_ep a                         aida:TextJustification .
		?justification_ep aida:source               "%s" .
		?justification_ep aida:startOffset          ?epso .
		?justification_ep aida:endOffsetInclusive   ?epeo .
		FILTER ( (?epeo >= %s && $epeo <= %s) || (?epso >= %s && ?epso <= %s) ) .
    ''' % (doceid, start, end, start, end)


def zerohop_query_image_video(doceid, keyframeid, top, left, bottom, right):
    justification_type = AIDA_VIDEOJUSTIFICATION if keyframeid else AIDA_IMAGEJUSTIFICATION
    keyframe_triple = '?justification_ep aida:keyFrame             "%s" .' % keyframeid if keyframeid else ''
    return '''
		?justification_ep a                         %s .
		?justification_ep aida:source               "%s" .
		%s
		?justification_ep aida:boundingBox          ?boundingbox_ep .
		?boundingbox_ep aida:boundingBoxUpperLeftX  ?epulx .
		?boundingbox_ep aida:boundingBoxUpperLeftY  ?epuly .
		?boundingbox_ep aida:boundingBoxLowerRightX ?eplrx .
		?boundingbox_ep aida:boundingBoxLowerRightY ?eplry .
		FILTER ((?epulx >= %s && ?epulx <= %s && ?epuly <= %s && ?epuly >= %s) ||
			(?eplrx >= %s && ?eplrx <= %s && ?eplry <= %s && ?eplry >= %s) ||
			(?eplrx >= %s && ?eplrx <= %s && ?epuly <= %s && ?epuly >= %s) ||
			(?epulx >= %s && ?epulx <= %s && ?eplry <= %s && ?eplry >= %s)) .
    ''' % (justification_type, doceid, keyframe_triple, left, right, top, bottom, left, right, top, bottom,
           left, right, top, bottom, left, right, top, bottom, )


def pprint(x):
    if not x:
        print('Empty')
    if isinstance(x, dict):
        print(json.dumps(x, indent=2))
    elif isinstance(x, list):
        for ele in x:
            pprint(ele)
    elif isinstance(x, ET.ElementTree):
        print(minidom.parseString(ET.tostring(x.getroot())).toprettyxml())
    else:
        if isinstance(x, bytes):
            x = x.decode('utf-8')
        try:
            print(minidom.parseString(x).toprettyxml())
        except:
            print(x)


def write_file(x, output):
    if len(output.rsplit('/', 1)) == 2:
        dirpath = output.rsplit('/', 1)[0]
        if dirpath and dirpath != '.':
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
    with open(output, 'w') as f:
        if isinstance(x, dict) or isinstance(x, list):
            json.dump(x, f, indent=2)
        elif isinstance(x, ET.ElementTree):
            str_xml = ET.tostring(x.getroot())
            f.write(minidom.parseString(str_xml).toprettyxml())
        else:
            if isinstance(x, bytes):
                x = x.decode('utf-8')
            try:
                f.write(minidom.parseString(x).toprettyxml())
            except:
                f.write(x)
