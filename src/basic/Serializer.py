from src.basic.Questions.ClassQuestion import ClassQuestion
from src.basic.Questions.ZerohopQuestion import ZerohopQuestion
from src.basic.Questions.GraphQuestion import GraphQuestion
from src.basic.utils import *


class Serializer(object):
    def __init__(self, question):
        self.question = question

    def serialize_select_query(self):
        if isinstance(self.question, ClassQuestion):
            # where_statements = [self.serialize_triples(self.question.enttype)]
            return class_query(self.question.enttype)
        elif isinstance(self.question, ZerohopQuestion):
            # where_statements = [self.serialize_entrypoints()]
            return zerohop_query(self.question.enttype, self.question.descriptor)
        elif isinstance(self.question, GraphQuestion):
            where_statements = [self.serialize_edges(),
                                self.serialize_entrypoints()]
            return self.wrap_select(self.question.nodes) + self.wrap_where(where_statements)

    def serialize_a_node(self, node_obj: dict):
        top_level = self.serialize_triples(node_obj.get(ENTTYPE))
        union_descriptors = self.serialize_list_of_triples(node_obj.get(DESCRIPTORS))
        return '{\n%s\n%s\n}' % (top_level, union_descriptors)

    def serialize_edges(self):
        return self.serialize_list_of_triples(self.question.edges)

    def serialize_entrypoints(self):
        return '\n'.join([self.serialize_a_node(node)for node in self.question.entrypoints])

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
    def serialize_triples(triples: dict) -> str:
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
