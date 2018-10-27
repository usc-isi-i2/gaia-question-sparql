from requests import put
from SPARQLWrapper import SPARQLWrapper, CSV, POST
from rdflib.graph import Graph
import csv
from enum import Enum
from itertools import combinations

from src.sparql_utils import *
from src.constants import *
from src.timeout import timeout


class Selector(object):
    def __init__(self, endpoint: str, use_fuseki=''):
        sparql_ep = ''
        update_ep = ''
        if endpoint.endswith('.ttl'):
            if use_fuseki:
                put(use_fuseki + '/data', data=open(endpoint).read().encode('utf-8'), headers={'Content-Type': 'text/turtle'})
                sparql_ep = use_fuseki + '/sparql'
                update_ep = use_fuseki + '/update'
            else:
                g = Graph()
                g.parse(endpoint, format='n3')
                self.graph = g
                self.run = self.select_query_rdflib
        else:
            sparql_ep = endpoint
        if sparql_ep:
            self.sw = SPARQLWrapper(sparql_ep)
            self.sw.setReturnFormat(CSV)
            self.sw.setMethod(POST)
            self.run = self.select_query_url
            if update_ep:
                self.sw_update = SPARQLWrapper(update_ep)
                self.sw_update.setMethod(POST)
                self.update = self.update_query_url

    @timeout(600, 'select rdflib timeout: 10 min')
    def select_query_rdflib(self, q):
        # print(q)
        csv_res = self.graph.query(PREFIX + q).serialize(format='csv')
        rows = [x.decode('utf-8') for x in csv_res.splitlines()][1:]
        res = list(csv.reader(rows))
        return res

    @timeout(1200, 'select url timeout: 20 min')
    def select_query_url(self, q):
        # print(q)
        sparql_query = PREFIX + q
        self.sw.setQuery(sparql_query)
        rows = self.sw.query().convert().decode('utf-8').splitlines()[1:]
        res = list(csv.reader(rows))
        # print(res)
        return res

    @timeout(1200, 'update url timeout: 20 min')
    def update_query_url(self, q):
        # print(q)
        sparql_query = PREFIX + q
        self.sw_update.setQuery(sparql_query)
        res = self.sw_update.query()
        return res


class Mode(Enum):
    SINGLETON = 'singleton'
    CLUSTER = 'cluster'
    PROTOTYPE = 'prototype'


class QueryTool(object):
    def __init__(self, endpoint: str, mode: Mode, relax_num_ep=None, use_fuseki='', block_ocrs=False):
        """
        :param selector: a Selector instance, for run select query and get results in list(list)
        :param mode:
        :param relax_num_ep:
        """
        selector = Selector(endpoint, use_fuseki)
        self.select = selector.run
        self.update = selector.update
        self.mode = mode
        self.at_least = relax_num_ep
        self.block_ocrs = block_ocrs

    def get_best_node(self, descriptors) -> str:
        '''
        :param descriptors: a list of typed descriptors: [
            {
                'enttype': 'Person',
                'string_descriptor': {
                    'name_string': ''
                }
            },
            {
                'enttype': 'Organization',
                'text_descriptors': {
                    'doceid': '',
                    'start': '',
                    'end'
                }
            }
        ]
        :return: str: the best node uri
        '''

        # try strict match:
        states = []
        for i in range(len(descriptors)):
            descriptor = descriptors[i]
            enttype = descriptor[ENTTYPE]

            if STRING_DESCRIPTOR in descriptor:
                justi = serialize_string_descriptor(descriptor[STRING_DESCRIPTOR][NAME_STRING])
            elif TEXT_DESCRIPTOR in descriptor:
                justi = serialize_text_descriptor(**descriptor[TEXT_DESCRIPTOR])
            else:
                des = descriptor.get(IMAGE_DESCRIPTOR) or descriptor.get(VIDEO_DESCRIPTOR)
                justi = serialize_image_video_descriptor(**des)

            states.append(self.serialize_a_types_descriptor(NODE, enttype, justi, str(i)))
        sparql_query_strict = '''
        SELECT DISTINCT ?node WHERE {
        %s
        }
        ''' % '\n'.join(states)
        # print(sparql_query_strict)
        nodes = self.select(sparql_query_strict)
        if nodes and nodes[0]:
            # TODO: is it possible that multiple nodes match the target -> maybe something went wrong during extraction
            return nodes[0][0]

        # try relax match and get the best one:
        states = []
        var_list = [NODE]
        to_compare = [] # [(1, 3), (3, 7) ... ] for the (start, end) index in var list for each descriptor
        for i in range(len(descriptors)):
            descriptor = descriptors[i]
            enttype = descriptor[ENTTYPE]

            if STRING_DESCRIPTOR in descriptor:
                justi = serialize_string_descriptor_relax(descriptor[STRING_DESCRIPTOR][NAME_STRING])
            elif TEXT_DESCRIPTOR in descriptor:
                justi = serialize_text_descriptor_relax(**descriptor[TEXT_DESCRIPTOR], var_suffix=str(i))
                to_compare.append((len(var_list), len(var_list) + 2))
                var_list.append(EPSO + str(i))
                var_list.append(EPEO + str(i))
            else:
                des = descriptor.get(IMAGE_DESCRIPTOR) or descriptor.get(VIDEO_DESCRIPTOR)
                justi = serialize_image_video_descriptor_relax(**des, var_suffix=str(i))
                to_compare.append((len(var_list), len(var_list) + 4))
                var_list.append(EPULX + str(i))
                var_list.append(EPULY + str(i))
                var_list.append(EPBRX + str(i))
                var_list.append(EPBRY + str(i))

            states.append(self.serialize_a_types_descriptor(NODE, enttype, justi, str(i)))

        sparql_query_relax = '''
        SELECT DISTINCT %s WHERE {
        %s
        }
        ''' % (' '.join(['?' + x for x in var_list]), '\n'.join(states))
        candidates = self.select(sparql_query_relax)
        best_uri = self.get_best_candidate(candidates, to_compare, descriptors)
        if best_uri:
            return best_uri

        # try match some of the descriptors:
        if self.at_least and 0 < self.at_least < len(descriptors):
            for idx_list in combinations(range(len(descriptors)), self.at_least):
                # TODO: check from len-1 to relax_num_ep
                best_uri = self.get_best_node([descriptors[i] for i in idx_list])
                if best_uri:
                    return best_uri

        return ''

    def serialize_a_types_descriptor(self, node_var, enttype, justi_sparql, suffix=''):
        if justi_sparql[-1] == '.':
            # string descriptor
            justi_sparql = '''.
            %s ''' % justi_sparql
        else:
            justi_sparql = ''';
                    aida:justifiedBy %s .''' % justi_sparql
        if self.mode == Mode.CLUSTER:
            return '''
            ?mem_state_{suffix} aida:cluster ?{node_var} ;
                        aida:clusterMember ?mem_{suffix} .
            ?state_{suffix} a rdf:Statement ;
                      rdf:subject ?mem_{suffix} ;
                      rdf:predicate rdf:type ;
                      rdf:object ldcOnt:{enttype} {justi_sparql} 
            '''.format(suffix=suffix, node_var=node_var, enttype=enttype, justi_sparql=justi_sparql)
        elif self.mode == Mode.PROTOTYPE:
            return '''
            ?{node_var}_cluster aida:prototype ?{node_var} .
            ?{node_var}_state a rdf:Statement ;
                      rdf:subject ?{node_var} ;
                      rdf:predicate rdf:type ;
                      rdf:object ldcOnt:{enttype} {justi_sparql} 
            '''.format(node_var=node_var, enttype=enttype, justi_sparql=justi_sparql)
        else:
            return '''
            ?{node_var}_state a rdf:Statement ;
                      rdf:subject ?{node_var} ;
                      rdf:predicate rdf:type ;
                      rdf:object ldcOnt:{enttype} {justi_sparql} 
            '''.format(node_var=node_var, enttype=enttype, justi_sparql=justi_sparql)

    @staticmethod
    def get_best_candidate(candidates, to_compare, descriptors):
        # TODO: group by ?node and compare, one ?node may have multiple combination satisfy the descriptors
        best_uri = ''
        best_score = 0
        for candidate in candidates:
            cur_score = 0
            for i in range(len(to_compare)):
                start, end = to_compare[i]
                descriptor = descriptors[i]
                cand_bound = candidate[start:end]
                if TEXT_DESCRIPTOR in descriptor:
                    target_start = descriptor[TEXT_DESCRIPTOR][START]
                    target_end = descriptor[TEXT_DESCRIPTOR][END]
                    score = get_overlap_text(int(cand_bound[0]), int(cand_bound[1]), int(target_start), int(target_end))
                else:
                    des = descriptor.get(IMAGE_DESCRIPTOR) or descriptor.get(VIDEO_DESCRIPTOR)
                    target_ulx, target_uly = des[TOPLEFT].split(',')
                    target_brx, target_bry = des[BOTTOMRIGHT].split(',')
                    score = get_overlap_img(*[int(x) for x in cand_bound],
                                            int(target_ulx), int(target_uly), int(target_brx), int(target_bry))
                # TODO: how much overlapped? consider FP? consider centroid distance?
                # if score <= 0:
                #     continue
                cur_score += score
            if cur_score > best_score:
                best_score = cur_score
                best_uri = candidate[0]
        return best_uri

    def get_justi(self, node_uri, limit=None):
        sparql = self.serialize_get_justi(node_uri, limit)
        return self.select(sparql)

    def serialize_get_justi(self, node_uri, limit=None):
        if self.mode == Mode.CLUSTER:
            # now that all nodes will be a cluster rather than an entity/event/relation:
            if isinstance(node_uri, list):
                # justi on bnode assertion
                s, p, o = node_uri
                justi_lines = '''
                ?mem aida:cluster <%s> ;
                     aida:clusterMember ?sub .
                ?mem2 aida:cluster <%s> ;
                      aida:clusterMember ?obj .
                ?xxx a rdf:Statement ;
                     rdf:subject ?sub ;
                     rdf:predicate ldcOnt:%s ;
                     rdf:object ?obj ;
                     aida:justifiedBy ?justification .
                ''' % (s, o, p)
            else:
                justi_lines = '''
                ?mem aida:cluster <%s> ;
                     aida:clusterMember ?x .
                ?x aida:justifiedBy ?justification .
                ''' % node_uri
        else:
            if isinstance(node_uri, list):
                # justi on bnode assertion
                s, p, o = node_uri
                justi_lines = '''
                ?xxx a rdf:Statement ;
                     rdf:subject <%s> ;
                     rdf:predicate ldcOnt:%s ;
                     rdf:object <%s> ;
                     aida:justifiedBy ?justification .
                ''' % (s, p, o)
            else:
                justi_lines = '''
                <%s> aida:justifiedBy ?justification .
                ''' % node_uri

        return '''
            SELECT DISTINCT ?doceid ?sid ?kfid ?so ?eo ?ulx ?uly ?brx ?bry ?st ?et ?cv
            WHERE {
                
                %s
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
        
                # OPTIONAL { 
                #     ?justification a                           aida:ShotVideoJustification .
                #     ?justification aida:shot                   ?sid 
                # }
                # 
                # OPTIONAL { 
                #     ?justification a                           aida:AudioJustification .
                #     ?justification aida:startTimestamp         ?st .
                #     ?justification aida:endTimestamp           ?et 
                # }
                
                %s
                
            } %s
        ''' % (justi_lines,
               block_ocr_sparql if self.block_ocrs else '',
               ' LIMIT %d' % limit if limit else '')
