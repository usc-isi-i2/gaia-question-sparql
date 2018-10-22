from src.utils import *
from src.query_tool import QueryTool, Mode
from src.stat import Stat, Failure


class SingleGraphQuery(object):
    def __init__(self, query_tool: QueryTool, q_dict: dict, doc_id: str, stat: Stat):
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
        self.query_id = q_dict['@id']
        self.query_tool = query_tool
        self.stat = stat
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
        for ep_node_uri in self.ep_nodes.values():
            if not ep_node_uri:
                self.find_all_ep = False
                break

        self.sopid = {}
        self.ospid = {}

        self.justi = {} # {'http://xxx': rows[[doceid, ...], [doceid, , , ...]]}
        self.enttype = {} # {'http://xxx': 'Person'}

        self.fail_on_justi = False
        self.found_edge = 0

    def get_responses(self):
        if self.find_all_ep:
            # parse edges and match edges strictly:
            select_nodes, strict_sparql, self.sopid, self.ospid = self.parse_edges(self.edges)
            # try strict:
            if not self.query_response(select_nodes, strict_sparql):
                # if no strict responses, try relax:
                for backbone, one_of in ((True, False), (False, True), (True, True)):
                    select_nodes, sparql_query = self.relax_backbone_one_of(backbone=backbone, one_of=one_of)
                    if select_nodes and self.query_response(select_nodes, sparql_query):
                        break
                # if not work, try search from ep node
                if not len(self.root_responses):
                    self.dfs()
            if self.fail_on_justi:
                self.stat.fail(self.query_id, Failure.NO_JUSTI)
            elif not len(self.root_responses):
                self.stat.fail(self.query_id, Failure.NO_EDGE, self.ep_nodes.values())
            else:
                self.stat.succeed(self.query_id, self.found_edge, len(self.edges))
        else:
            self.stat.fail(self.query_id, Failure.NO_EP)
        return self.root_responses

    def query_response(self, select_nodes, sparql_query):
        rows = self.query_tool.select(sparql_query)
        if rows and rows[0]:
            for row in rows:
                # mapping to select_nodes, and construct response
                non_ep_nodes = {}
                for i in range(len(row)):
                    non_ep_nodes[select_nodes[i]] = row[i]
                self.root_responses.append(self.construct_single_response(non_ep_nodes))
            return True
        else:
            return False

    def relax_backbone_one_of(self, backbone=True, one_of=False):
        select_nodes = set()
        states = []
        for o, spid in self.ospid.items():
            if (not backbone) or len(spid) > 1 or o in self.ep_nodes:
                for s, pid in spid.items():
                    if (not backbone) or len(self.sopid[s]) > 1:
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
        return select_nodes, sparql_query

    def dfs(self):
        to_check = []   # [(node_var_with?, node_uri, node_is_object(entity)) ... ]
        for ep_var, ep_uri in self.ep_nodes.items():
            to_check.append((ep_var, ep_uri, True))
        non_ep_nodes = {}
        while to_check:
            root_var, root_uri, is_obj = to_check.pop()
            select_nodes = set()
            states = []
            if is_obj:
                spid = self.ospid[root_var]  # {'?event1' : {'Conflict.Attack_Attacker': '1'}}
                for s, pid in spid.items():
                    if not non_ep_nodes.get(s):
                        for p, _id in pid.items():
                            self.aug_a_statement(_id, s, p, root_var, select_nodes, states)
            else:
                opid = self.sopid[root_var]  # {'?entity1' : {'Conflict.Attack_Attacker': '1'}}
                for o, pid in opid.items():
                    if not non_ep_nodes.get(o):
                        for p, _id in pid.items():
                            self.aug_a_statement(_id, root_var, p, o, select_nodes, states)
            select_nodes = list(select_nodes)
            sparql_query = '''
            SELECT DISTINCT %s WHERE {
            %s
            }
            ''' % (' '.join(select_nodes), 'OPTIONAL {\n %s }' % '}\nOPTIONAL {\n'.join(states))
            try:
                rows = self.query_tool.select(sparql_query)
                row = self.max_row(rows)
                # TODO: now only take local maximum
                # TODO: should pick global maximum OR global weighted maximum OR multiple responses for each possibility ?
                for i in range(len(row)):
                    if row[i]:
                        non_ep_nodes[select_nodes[i]] = row[i]
                        if (is_obj and row[i] in self.ospid) or (not is_obj and row[i] in self.sopid):
                            # only add nodes, skip edges
                            to_check.append((select_nodes[i], row[i], not is_obj))
            except TimeoutError as e:
                print('inner timeout', e)
        if non_ep_nodes:
            self.root_responses.append(self.construct_single_response(non_ep_nodes))

    @staticmethod
    def max_row(rows):
        if rows:
            _, idx = min([(rows[i].count(''), i) for i in range(len(rows))])
            return rows[idx]
        return []

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
        found_edge = 0
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
                found_edge += 1
                edge = ET.SubElement(root, EDGE, attrib={'id': _id})
                justifications = ET.SubElement(edge, 'justifications')
                self.fail_on_justi = self.add_justi_for_an_edge(justifications, s, p, o)
                if self.fail_on_justi:
                    return ET.Element('response')
        self.found_edge = max(self.found_edge, found_edge)
        return root

    def add_justi_for_an_edge(self, justifications_root, s, p, o):
        # TODO: reconstruct in a better manner
        # limit = 1 if self.doc_id else 0
        # sub_rows = self.get_justi(s, limit)
        # obj_rows = self.get_justi(o, limit)
        # edge_rows = self.get_justi([s, p, o], limit*2)

        if self.doc_id:
            justification = ET.SubElement(justifications_root, 'justification', attrib={'docid': self.doc_id})

            for node_to_just, limit, label in [
                [s, 1, SUBJECT],
                [o, 1, OBJECT],
                [[s, p, o], 2, EDGE]
            ]:
                node_justi = self.get_justi(node_to_just, limit)
                if not (node_justi and node_justi[0]):
                    return True
                self.update_s_o_e_justi(justification, node_to_just, node_justi, label)
        else:
            doc_id = ''
            sub_rows = self.get_justi(s)
            obj_rows = self.get_justi(o)
            edge_rows = self.get_justi([s, p, o])
            if sub_rows and sub_rows[0] and obj_rows and obj_rows[0] and edge_rows and edge_rows[0]:
                sub_docs = set([c2p[line[0]] for line in sub_rows])
                intersect_so = set([c2p[line[0]] for line in obj_rows if c2p[line[0]] in sub_docs])
                for line in edge_rows:
                    if c2p[line[0]] in intersect_so:
                        doc_id = c2p[line[0]]
                        edge_rows = [line]
                        break
                if doc_id:
                    justification = ET.SubElement(justifications_root, 'justification', attrib={'docid': doc_id})
                    sub_rows = [self.get_justi_of_a_doc(sub_rows, doc_id)]
                    obj_rows = [self.get_justi_of_a_doc(obj_rows, doc_id)]
                    for node_to_just, node_justi, label in [
                        [s, sub_rows, SUBJECT],
                        [o, obj_rows, OBJECT],
                        [[s, p, o], edge_rows, EDGE]
                    ]:
                        self.update_s_o_e_justi(justification, node_to_just, node_justi, label)
                    return
            return True

    def update_s_o_e_justi(self, justification, node_to_just, node_justi, label):
        cur_element = ET.SubElement(justification, label + '_justification')
        if label != EDGE:
            update_xml(cur_element, {'system_nodeid': node_to_just,
                                     ENTTYPE: self.get_enttype(node_to_just)})
        construct_justifications(cur_element, None, node_justi, '_span', True)

    @staticmethod
    def get_justi_of_a_doc(rows, doc_id):
        for row in rows:
            if c2p[row[0]] == doc_id:
                return row

    def get_justi(self, node_uri, limit=None):
        cache_key = ' '.join(node_uri) if isinstance(node_uri, list) else node_uri
        if cache_key not in self.justi:
            rows = self.query_tool.get_justi(node_uri, limit=limit)
            self.justi[cache_key] = rows
        return self.justi[cache_key]

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
        ospid = {}
        for i in range(len(edges)):
            _id, s, p, o = edges[i]['@id'], edges[i][SUBJECT], edges[i][PREDICATE], edges[i][OBJECT]
            self.aug_a_statement(_id, s, p, o, select_nodes, states)
            if s not in sopid:
                sopid[s] = {o: {p: _id}}
            elif o not in sopid[s]:
                sopid[s][o] = {p: _id}
            elif p not in sopid[s][o]:
                sopid[s][o][p] = _id
            if o not in ospid:
                ospid[o] = {s: {p: _id}}
            elif s not in ospid[o]:
                ospid[o][s] = {p: _id}
            elif p not in ospid[o][s]:
                ospid[o][s][p] = _id
        select_nodes = list(select_nodes)
        strict_sparql = '''
        SELECT DISTINCT %s WHERE {
        %s
        }
        ''' % (' '.join(select_nodes), '\n'.join(states))
        return select_nodes, strict_sparql, sopid, ospid

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
