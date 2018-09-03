import sys
sys.path.append('..')

from ..basic.Question import Question, Serializer
from ..basic.utils import *


class AdvancedQuestion(Question):
    def test(self):
        # print(self.query_id)
        print(self.serialize_relax_sparql())

    def serialize_relax_sparql(self):
        relax_query = AdvancedSerializer(self).serialize_select_query()
        return relax_query
        pass


class AdvancedSerializer(Serializer):
    def __init__(self, question: Question, relax_strategy=None):
        Serializer.__init__(self, question)
        # self.relax_strategy = relax_strategy
        self.relax_strategy = {
            'wider_range': True,
            'ignore_enttype': True,
            'at_least_n': 1
        }

    def serialize_a_node(self, node_obj: dict):
        top_level = self.serialize_triples_with_relaxation(node_obj.get(ENTTYPE), is_enttype=True)
        union_descriptors = self.relax_descriptors(node_obj.get(DESCRIPTORS))
        return '{\n%s\n%s\n}' % (top_level, union_descriptors)

    def relax_descriptors(self, descriptors):
        if not self.relax_strategy or not descriptors:
            return self.serialize_list_of_triples(descriptors)

        union_descriptors = []

        for descriptor in descriptors:
            union_descriptors.append(self.serialize_triples_with_relaxation(descriptor))

        # TODO: relax on the union of descriptors

        return '\n\n\n'.join(union_descriptors)


    def serialize_triples_with_relaxation(self, triples, is_enttype=False):
        '''
        :param triples: {SUBJECT_1 : [(PREDICATE_1_1, OBJECT_1_1), (PREDICATE_1_2, OBJECT_1_2)], SUBJECT_2: [(PREDICATE_2, OBJECT_2)]}
        :return: SPARQL string :
                SUBJECT_1 PREDIACTE_1_1 OBJECT_1_1 ;
                          PREDICATE_1_2 OBJECT_1_2 .
                SUBJECT_2 PREDICATE_1 OBJECT_2 .
        '''
        if not triples:
            return ''

        if is_enttype and self.relax_strategy.get('ignore_enttype'):
            updated_triples = {}
            for k in triples:
                updated_triples[k] = [('a', 'aida:Entity')]
            return self.serialize_triples(updated_triples)

        # TODO: relax on a single descriptors:
        return '\t' + ('\n\t'.join(['\n'.join(
            [' '.join(('\t\t' if i else k, v[i][0], v[i][1], ';' if i < len(v)-1 else '.')) for i in range(len(v))]
            ) if not k.startswith('@') else v for k, v in triples.items()]))

