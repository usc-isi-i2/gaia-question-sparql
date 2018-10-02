from src.utils import *
from src.QueryTool import QueryTool, Mode


class SingleGraphQuery(object):
    def __init__(self, query_tool: QueryTool, q_dict: dict, doc_id: str):
        '''
        :param endpoint: sparql endpoint or rdflib graph
        :param q_dict: {
            '@id': 'GRAPH_QUERY_1',
            'graph': {
                'edges': {
                    'edge': [ # or a dict when only one edge
                        {
                            '@id': '',
                            'subject': '',
                            'predicate': '',
                            'object': ''
                        }, {
                            ...
                        }
                    ]
                }
            },
            'entrypoints': {
                'entrypoint': [ # or a dict when only one entrypoint
                    {
                        'node': '?attact_target',
                        'typed_descriptor': {
                            'enttype': 'Person',
                            # TODO: multiple or single, now suppose to be a single descriptor as in NIST query v1.3
                            'string_descriptor': {  # list of such objects or an single object
                                'name_string': 'Putin',
                            },
                            'text_descriptor': {  # list of such objects or an single object
                                'docied': 'HC000ZUW7',
                                'start': '308',
                                'end': '310'
                            },
                            'image_descriptor': [  # list of such objects or an single object
                                # TODO: is it possible to have multi descriptors?
                                {
                                    'doceid': 'HC000ZUW7',
                                    'topleft': '10,20',
                                    'bottomright": '50,60'
                                },
                                {
                                    'doceid': 'HC000ZUW8',
                                    'topleft': '20,20',
                                    'bottomright": '60,60'
                                }
                            ]
                        }
                    }
                }
            }
        }
        '''
        self.doc_id = doc_id
        self.query_tool = query_tool
        self.root_responses = ET.Element('graphquery_responses', attrib={'id':  q_dict['@id']})
        self.eps = q_dict[ENTRYPOINTS][ENTRYPOINT]
        if isinstance(self.eps, dict):
            self.eps = [self.eps]
        self.edges = q_dict[GRAPH][EDGES][EDGE]
        if isinstance(self.edges, dict):
            self.edges = [self.edges]

        # find ep nodes:
        self.ep_nodes = self.get_ep_nodes(self.eps)
        # { '?node1': 'http://zxxxzcdsds', '?node2': '', ... }
        # print(self.ep_nodes)

        # TODO: assume need to find all ep nodes
        self.find_all_ep = True
        for v in self.ep_nodes.values():
            if not v:
                self.find_all_ep = False
                break

        self.sopid = {}

        self.justi = {} # {'http://xxx': rows[[doceid, ...], [doceid, , , ...]]}
        self.enttype = {} # {'http://xxx': 'Person'}

    def get_responses(self):
        if self.find_all_ep:
            # parse edges and match edges strictly:
            select_nodes, strict_sparql, self.sopid = self.parse_edges(self.edges)
            # try strict:
            if not self.query_response(select_nodes, strict_sparql):
                # cannot find exact matched graph, try relax
                # 1. try to only match backbone
                select_nodes, sparql_query = self.relax_backbone_one_of(backbone=True, one_of=False)
                if not self.query_response(select_nodes, sparql_query):
                    select_nodes, sparql_query = self.relax_backbone_one_of(backbone=True, one_of=True)
                    if not self.query_response(select_nodes, sparql_query):
                        pass

        return self.root_responses

    def query_response(self, select_nodes, sparql_query):
        rows = self.query_tool.select(sparql_query)
        if rows and rows[0]:
            for row in rows:
                # mapping to select_nodes, and construct response
                non_ep_nodes = {}
                for i in range(len(row)):
                    non_ep_nodes[select_nodes[i]] = row[i]
                # print(non_ep_nodes)
                self.root_responses.append(self.construct_single_response(non_ep_nodes))
            return True
        else:
            return False

    def relax_backbone_one_of(self, backbone=True, one_of=False):
        select_nodes = set()
        states = []
        for s, opid in self.sopid.items():
            # TODO:backbone - prune all leaves, no only object-leaves are prune
            if (not backbone) or len(opid) > 1 or list(opid.keys())[0] in self.ep_nodes or s in self.ep_nodes: # change to ospid ?
                for o, pid in opid.items():
                    if one_of and len(pid) > 1:
                        self.aug_a_statement('', s, list(pid.keys()), o, select_nodes, states)
                    else:
                        for p, _id in pid.items():
                            self.aug_a_statement(_id, s, p, o, select_nodes, states)
        select_nodes = list(select_nodes)
        sparql_query = '''
        SELECT DISTINCT %s WHERE {
        %s
        }
        ''' % (' '.join(select_nodes), '\n'.join(states))
        # if one_of:
        #     print(sparql_query)
        #     exit()
        return select_nodes, sparql_query

    def construct_single_response(self, non_ep_nodes: dict) -> ET.Element:
        '''
        construct a <response>
        :param non_ep_nodes: { '?e001': 'http://xxxx', '?e002': 'http://xxxxx', ... }
        :return:
        <response>
            <edge id="AIDA_M09_TA2_Q2_1">
                <justifications>
                    <justification docid="SOME_DOCID_1">
                        <subject_justification>
                            <system_nodeid> Some_team_internal_ID_1 </system_nodeid>
                            <enttype> ... </enttype>
                            <video_span>
                                <doceid> ... </doceid>
                                <keyframeid> .... </keyframeid>
                                <topleft> x1,y1 </topleft>
                                <bottomright> x2,y2 </bottomright>
                            </video_span>
                            <confidence> 0.8 </confidence>
        '''
        root = ET.Element('response')
        # print('-----construct single query------')
        for e in self.edges:
            _id, s, p, o = e['@id'], e[SUBJECT], e[PREDICATE], e[OBJECT]
            p_var_name = s + '_' + o.lstrip('?')
            assertion = non_ep_nodes.get('?' + _id)
            if not assertion:
                assertion = non_ep_nodes.get(p_var_name, '').endswith(p)
            s = self.ep_nodes.get(s) or non_ep_nodes.get(s)
            o = self.ep_nodes.get(o) or non_ep_nodes.get(o)
            # print(e)
            # print(s, assertion, o)
            if s and o and assertion:
                edge = ET.SubElement(root, EDGE, attrib={'id': _id})
                justifications = ET.SubElement(edge, 'justifications')
                justification = ET.SubElement(justifications, 'justification', attrib={'docid': self.doc_id})
                # insert subject_justification
                subject_justi = ET.SubElement(justification, 'subject_justification')
                update_xml(subject_justi, {'system_nodeid': s, ENTTYPE: self.get_enttype(s)})
                construct_justifications(subject_justi, None, self.get_justi(s, limit=1), '_span', True)
                # insert object_justification
                object_justi = ET.SubElement(justification, 'object_justification')
                update_xml(object_justi, {'system_nodeid': o, ENTTYPE: self.get_enttype(o)})
                construct_justifications(object_justi, None, self.get_justi(o, limit=1), '_span', True)
                # insert edge_justification
                edge_justi = ET.SubElement(justification, 'edge_justification')
                construct_justifications(edge_justi, None, self.get_justi([s, p, o], limit=2), '_span', True)
        return root

    def get_justi(self, node_uri, limit=None):
        cache_key = ' '.join(node_uri) if isinstance(node_uri, list) else node_uri
        if cache_key not in self.justi:
            rows = self.query_tool.get_justi(node_uri, limit=limit)
            self.justi[cache_key] = rows
        return self.justi[cache_key]
        # update_xml(root, {'system_nodeid': node_uri})
        # construct_justifications(root, None, rows)

    def get_enttype(self, node_uri):
        if node_uri not in self.enttype:
            if self.query_tool.mode == Mode.CLUSTER:
                q = '''SELECT ?type WHERE {
                <%s> aida:prototype ?p .
                ?r rdf:subject ?p; rdf:predicate rdf:type; rdf:object ?type .}
                ''' % node_uri
            else:
                q = 'SELECT ?type WHERE {?r rdf:subject <%s>; rdf:predicate rdf:type; rdf:object ?type .}' % node_uri
            rows = self.query_tool.select(q)
            self.enttype[node_uri] = rows[0][0].rsplit('#', 1)[-1]
        return self.enttype[node_uri]

    def parse_edges(self, edges: list) -> (list, str, dict):
        select_nodes = set()
        states = []
        sopid = {}
        for i in range(len(edges)):
            _id, s, p, o = edges[i]['@id'], edges[i][SUBJECT], edges[i][PREDICATE], edges[i][OBJECT]
            self.aug_a_statement(_id, s, p, o, select_nodes, states)
            if s not in sopid:
                sopid[s] = {o: {p: _id}}
            elif o not in sopid[s]:
                sopid[s][o] = {p: _id}
            elif p not in sopid[s][o]:
                sopid[s][o][p] = _id
        select_nodes = list(select_nodes)
        strict_sparql = '''
        SELECT DISTINCT %s WHERE {
        %s
        }
        ''' % (' '.join(select_nodes), '\n'.join(states))
        return select_nodes, strict_sparql, sopid

    def aug_a_statement(self, _id, s, p, o, select_nodes: set, statements: list):
        if s in self.ep_nodes:
            sub = '<%s>' % self.ep_nodes[s]
        else:
            sub = s
            select_nodes.add(s)
        if o in self.ep_nodes:
            obj = '<%s>' % self.ep_nodes[o]
        else:
            obj = o
            select_nodes.add(o)
        extra = ''
        if isinstance(p, list):
            # one of, p is a var name: ?{s}_{o}
            p_var = s + '_' + o.lstrip('?')
            extra = 'VALUES %s { %s }' % (p_var, ' '.join(['ldcOnt:%s' % _ for _ in p]))
            p = p_var
            _id = p.lstrip('?') + '_id'
            # select p var rather than the assertion var
            select_nodes.add(p)
        else:
            select_nodes.add('?'+_id)
            p = 'ldcOnt:' + p
        if self.query_tool.mode == Mode.CLUSTER:
            state = '''
            ?{edge_id}_ss aida:cluster {sub} ;
                   aida:clusterMember ?{edge_id}_s .
            ?{edge_id}_os aida:cluster {obj} ;
                   aida:clusterMember ?{edge_id}_o .
            ?{edge_id} a rdf:Statement ;
                rdf:subject ?{edge_id}_s ;
                rdf:predicate {p} ;
                rdf:object ?{edge_id}_o .
            {extra}
            '''.format(edge_id=_id, sub=sub, obj=obj, p=p, extra=extra)
        else:
            state = '''
            ?{edge_id} a rdf:Statement ;
                rdf:subject {sub} ;
                rdf:predicate {p} ;
                rdf:object {obj} .
            {extra}
            '''.format(edge_id=_id, sub=sub, obj=obj, p=p, extra=extra)
        statements.append(state)

    def get_ep_nodes(self, eps: list):
        group_by_node = {}
        for ep in eps:
            node = ep[NODE]
            if node not in group_by_node:
                group_by_node[node] = []
            # TODO: now assume one descriptor per typed_descriptor -> justi on type_statement
            group_by_node[node].append(ep[TYPED_DESCRIPTOR])
        res = {}
        for node, descriptors in group_by_node.items():
            res[node] = self.query_tool.get_best_node(descriptors)
        return res


