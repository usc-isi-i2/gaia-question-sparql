
from src.basic.utils import *


class Serializer(object):
    def serialize_graph_query(self, nodes, edges, entrypoints):
        select = self.wrap_select(nodes)
        where_clause = self.wrap_where([self.serialize_edges(edges), self.serialize_entrypoints(entrypoints)])
        return select + where_clause

    def serialize_class_query(self, nodes, enttype_triples):
        select = self.wrap_select(nodes)
        where_clause = self.wrap_where([self.serialize_triples(enttype_triples)])
        return select + where_clause

    def serialize_zerohop_query(self, nodes, entrypoints):
        select = self.wrap_select(nodes)
        where_clause = self.wrap_where([self.serialize_entrypoints(entrypoints)])
        return select + where_clause

    def serialize_edges(self, graph_edges: list):
        return self.serialize_list_of_triples(graph_edges)

    def serialize_entrypoints(self, entrypoints: list):
        return '\n'.join([self.serialize_a_node(node)for node in entrypoints])

    def serialize_a_node(self, node_obj: dict):
        top_level = self.serialize_triples(node_obj.get(ENTTYPE))
        union_descriptors = self.serialize_list_of_triples(node_obj.get(DESCRIPTORS))
        return '{\n%s\n%s\n}' % (top_level, union_descriptors)

    def serialize_list_of_triples(self, list_of_triples: list, joiner: str='\n'):
        if not list_of_triples:
            return ''
        return joiner.join([self.serialize_triples(triples) for triples in list_of_triples])

    @staticmethod
    def wrap_select(nodes):
        return '\nSELECT %s \n' % (' '.join(nodes))

    @staticmethod
    def wrap_where(statements):
        return '\nWHERE {\n%s\n}\n' % ('\n'.join(statements))

    @staticmethod
    def serialize_triples(triples: dict):
        '''
        :param triples: {SUBJECT_1 : [(PREDICATE_1_1, OBJECT_1_1), (PREDICATE_1_2, OBJECT_1_2)], SUBJECT_2: [(PREDICATE_2, OBJECT_2)]}
        :return: SPARQL string :
                SUBJECT_1 PREDIACTE_1_1 OBJECT_1_1 ;
                          PREDICATE_1_2 OBJECT_1_2 .
                SUBJECT_2 PREDICATE_1 OBJECT_2 .
        '''
        if not triples:
            return ''
        return '\t' + ('\n\t'.join(['\n'.join(
            [' '.join(('\t\t' if i else k, v[i][0], v[i][1], ';' if i < len(v)-1 else '.')) for i in range(len(v))]
            ) if not k.startswith('@') else v for k, v in triples.items()]))
