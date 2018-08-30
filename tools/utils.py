from SPARQLWrapper import SPARQLWrapper
import json

ENDPOINT = 'http://gaiadev01.isi.edu:3030/latest_rpi_en/'
PREFIX = '''
PREFIX aida: <https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/InterchangeOntology#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ldcOnt: <https://tac.nist.gov/tracks/SM-KBP/2018/ontologies/SeedlingOntology#>
'''
SUBJECT = 'subject'
PREDICATE = 'predicate'
OBJECT = 'object'
ENTTYPE = 'enttype'
EDGES = 'edges'
ENTRYPOINTS = 'entripoints'
STRING_DESCRIPTOR = 'string_descriptor'
TEXT_DESCRIPTOR = 'text_descriptor'
VEDIO_DESCRIPTOR = 'video_descriptor'
IMAGE_DESCRIPTOR = 'image_descriptor'
NAME_STRING = 'name_string'
START = 'start'
END = 'end'
DOCEID = 'doceid'
KEYFRAMEID = 'keyframeid'
TOPLEFT = 'topleft'
BOTTOMRIGHT = 'bottomright'
NODE = 'node'

query_wrapper = SPARQLWrapper(ENDPOINT+'query')
update_wrapper = SPARQLWrapper(ENDPOINT+'update')


def select_query(q):
    query_wrapper.setQuery(PREFIX + q)
    query_wrapper.setReturnFormat('json')
    res = query_wrapper.query().convert()
    return res.get('results', {}).get('bindings', [])


def get_edges_event(event_uri):
    # event_uri = "http://www.isi.edu/gaia/events/f2ca779a-0b83-4da2-92d4-4c332940949c"
    q = '''
    SELECT DISTINCT ?p ?o
    WHERE {
      ?r a rdf:Statement ;
         rdf:subject <%s> ;
         rdf:predicate ?p ;
         rdf:object ?o .
      ?e a aida:Event .
      FILTER(?p != rdf:type)
    }
    ''' % event_uri
    res = select_query(q)
    # group by predicates:
    ret = {}
    for x in res:
        if x['p']['value'] in ret:
            ret[x['p']['value']].append(x['o']['value'])
        else:
            ret[x['p']['value']] = [x['o']['value']]
    return ret


def filter_exclude(var_name, exclude_list):
    var_name = var_name if var_name[0] == '?' else '?' + var_name
    exclude_vars = ['<%s>' % ex.lstrip('<').rstrip('>') for ex in exclude_list]
    return 'FILTER(%s not in (%s))' % (var_name, ', '.join(exclude_vars)) if exclude_list else ''


def construct_edge(id, sub, pred, obj):
    return {
        '@id': id,
        SUBJECT: sub,
        PREDICATE: pred.rsplit('#', 1)[-1],
        OBJECT: obj
    }


def construct_ep(node, enttype, descriptors):
    ret = {
        NODE: node,
        ENTTYPE: enttype.rsplit('#', 1)[-1],
    }
    ret.update(descriptors)
    return ret


def construct_graph(edges, entrypoints):
    return {
        'graph': {
            EDGES: edges
        },
        ENTRYPOINTS: entrypoints
    }


def get_edges_from_subject(event_or_relation_uri, exclude_predicate=[], exclude_object=[]):
    # event_uri = "http://www.isi.edu/gaia/events/f2ca779a-0b83-4da2-92d4-4c332940949c"
    # relation_uri = "http://www.isi.edu/gaia/assertions/a4172e65-64f0-4dcc-8588-5c66a196e34e"
    q = '''
    SELECT DISTINCT ?p ?o
    WHERE {
      ?r a rdf:Statement ;
         rdf:subject <%s> ;
         rdf:predicate ?p ;
         rdf:object ?o .
      FILTER(?p != rdf:type) .
      %s
      %s
    }
    ''' % (event_or_relation_uri, filter_exclude('?p', exclude_predicate), filter_exclude('?o', exclude_object))
    res = select_query(q)
    # group by predicates:
    ret = {}
    for x in res:
        if x['p']['value'] in ret:
            ret[x['p']['value']].append(x['o']['value'])
        else:
            ret[x['p']['value']] = [x['o']['value']]
    return ret


def get_edges_from_object(entity_uri, exclude_predicate=[], exclude_subject=[]):
    # entity_uri = "http://www.isi.edu/gaia/entities/df905740-b62e-485e-813a-7a14826b31a2"
    q = '''
    SELECT DISTINCT ?s ?p
    WHERE {
      ?r a rdf:Statement ;
         rdf:subject ?s ;
         rdf:predicate ?p ;
         rdf:object <%s> .
      FILTER(?p != rdf:type) .
      %s
      %s
    }
    ''' % (entity_uri, filter_exclude('?p', exclude_predicate), filter_exclude('?o', exclude_subject))
    res = select_query(q)
    # group by predicates:
    ret = {}
    for x in res:
        if x['p']['value'] in ret:
            ret[x['p']['value']].append(x['s']['value'])
        else:
            ret[x['p']['value']] = [x['s']['value']]
    return ret


def get_enttype(entity_uri):
    # entity_uri = "http://www.isi.edu/gaia/entities/df905740-b62e-485e-813a-7a14826b31a2"
    q = '''
    SELECT DISTINCT ?t
    WHERE {
      ?r a rdf:Statement ;
         rdf:subject <%s> ;
         rdf:predicate rdf:type ;
         rdf:object ?t .
    }
    ''' % entity_uri
    return select_query(q)[0]['t']['value']


def get_entrypints(uri):
    descriptors = {
        'string_descriptor': {
            'query': '''
                SELECT DISTINCT ?name_string
                WHERE { <%s> aida:hasName ?name_string }
                ''' % uri,
            'format': lambda x: {
                NAME_STRING: x['name_string']['value']
            }
        },
        'text_descriptor': {
            'query': '''
                SELECT DISTINCT ?doceid ?start ?end
                WHERE {
                  <%s> aida:justifiedBy ?j .
                  ?j a aida:TextJustification ;
                     aida:source ?doceid ;
                     aida:startOffset ?start ;
                     aida:endOffsetInclusive ?end . 
                }    
                ''' % uri,
            'format': lambda x: {
                DOCEID: x['doceid']['value'],
                START: x['start']['value'],
                END: x['end']['value']
            }
        },
        'video_descriptor': {
            'query': '''
                SELECT DISTINCT ?doceid ?keyframeid ?topleftX ?topleftY ?bottomrightX ?bottomrightY
                WHERE {
                  <%s> aida:justifiedBy ?j .
                  ?j a aida:KeyFrameVideoJustification ;
                     aida:source ?doceid ;
                     aida:keyFrame ?keyframeid ;
                     aida:boundingBox ?box .
                  ?box aida:boundingBoxUpperLeftX ?topleftX ;
                       aida:boundingBoxUpperLeftY ?topleftY ;
                       aida:boundingBoxLowerRightX ?bottomrightX ;
                       aida:boundingBoxLowerRightY ?bottomrightY .
                }    
                ''' % uri,
            'format': lambda x: {
                DOCEID: x['doceid']['value'],
                KEYFRAMEID: x['keyframeid']['value'],
                TOPLEFT: "%s,%s" % (x['topleftX']['value'], x['topleftY']['value']),
                BOTTOMRIGHT: "%s,%s" % (x['bottomrightX']['value'], x['bottomrightY']['value'])
            },
        },
        'image_descriptor': {
            'query': '''
                SELECT DISTINCT ?doceid ?topleftX ?topleftY ?bottomrightX ?bottomrightY
                WHERE {
                  <%s> aida:justifiedBy ?j .
                  ?j a aida:ImageJustification ;
                     aida:source ?doceid ;
                     aida:boundingBox ?box .
                  ?box aida:boundingBoxUpperLeftX ?topleftX ;
                       aida:boundingBoxUpperLeftY ?topleftY ;
                       aida:boundingBoxLowerRightX ?bottomrightX ;
                       aida:boundingBoxLowerRightY ?bottomrightY .
                }    
                ''' % uri,
            'format': lambda x: {
                DOCEID: x['doceid']['value'],
                TOPLEFT: "%s,%s" % (x['topleftX']['value'], x['topleftY']['value']),
                BOTTOMRIGHT: "%s,%s" % (x['bottomrightX']['value'], x['bottomrightY']['value'])
            },
        }
    }
    ret = {}
    for k, v in descriptors.items():
        q, f = v['query'], v['format']
        bindings = select_query(q)
        if bindings:
            ret[k] = [f(x) for x in bindings]
    return ret


def pprint(x):
    if not x:
        print('Empty')
    if isinstance(x, dict):
        print(json.dumps(x, indent=2))
    elif isinstance(x, list):
        for ele in x:
            pprint(ele)
    else:
        if isinstance(x, bytes):
            x = x.decode('utf-8')
        try:
            from xml.dom import minidom
            print(minidom.parseString(x).toprettyxml())
        except:
            print(x)
