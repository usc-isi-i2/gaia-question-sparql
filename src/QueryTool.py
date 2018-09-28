
from SPARQLWrapper import SPARQLWrapper, CSV
from rdflib.graph import Graph
import csv
from enum import Enum
from itertools import combinations

from src.utils import *
from src.sparql_utils import *
from src.constants import *


class Selector(object):
    def __init__(self, endpoint: str):
        if endpoint.endswith('.ttl'):
            g = Graph()
            g.parse(endpoint, format='n3')
            self.graph = g
            self.run = self.select_query_rdflib
        else:
            self.sw = SPARQLWrapper(endpoint)
            self.sw.setReturnFormat(CSV)
            if '7200' in endpoint:
                self.run = self.select_query_graphdb
            else:
                self.run = self.select_query_fuseki

    def select_query_rdflib(self, q):
        # print(q)
        csv_res = self.graph.query(PREFIX + q).serialize(format='csv')
        rows = [x.decode('utf-8') for x in csv_res.splitlines()][1:]
        return list(csv.reader(rows))

    def select_query_graphdb(self, q):
        sparql_query = 'query=' + PREFIX + q
        return self.select_query_url(sparql_query)

    def select_query_fuseki(self, q):
        sparql_query = PREFIX + q
        return self.select_query_url(sparql_query)

    def select_query_url(self, full_q):
        self.sw.setQuery(full_q)
        rows = self.sw.query().convert().decode('utf-8').splitlines()[1:]
        return list(csv.reader(rows))


class Mode(Enum):
    SINGLETON = 'singleton'
    CLUSTER = 'cluster'
    PROTOTYPE = 'prototype'


class QueryTool(object):
    def __init__(self, endpoint: str, mode: Mode, relax_num_ep=None):
        """
        :param selector: a Selector instance, for run select query and get results in list(list)
        :param mode:
        :param relax_num_ep:
        """
        self.select = Selector(endpoint).run
        self.mode = mode
        self.at_least = relax_num_ep

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
                # TODO: how much overlapped ?
                if score < 0.3:
                    continue
                cur_score += score
            if cur_score > best_score:
                best_score = cur_score
                best_uri = candidate[0]
        return best_uri

    def get_justi(self, node_uri, limit=None):
        return self.select(self.serialize_get_justi_cluster(node_uri, limit))

    def serialize_get_justi_cluster(self, node_uri, limit):
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
            } %s
        ''' % (justi_lines, ' LIMIT %d' % limit if limit else '')
