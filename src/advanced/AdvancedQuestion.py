
from src.basic.Question import Question, Serializer
from src.advanced.advanced_utils import *


class AdvancedQuestion(Question):
    def test(self):
        # print(self.query_id)
        print(self.serialize_relax_sparql())

        # TODO: now no relax on graph, only relax entrypoints.
        # In 'Evaluation Plan v0.7' 7.3 note(4):
        # "(4)	A response may or may not contain all edges."
        # may need to relax on graph in the future

        # TODO: query on super graph

        # TODO: auto try relaxation strategies

    def serialize_relax_sparql(self, relaxation):
        relax_query = AdvancedSerializer(self, relaxation).serialize_select_query()
        return relax_query


class AdvancedSerializer(Serializer):
    def __init__(self, question: Question, relax_strategy=None):
        Serializer.__init__(self, question)
        self.relax_strategy = relax_strategy
        # self.relax_strategy = {
        #     WIDER_RANGE: True,
        #     IGNORE_ENTTYPE: True,
        #     LARGER_BOUND: True,
        #     AT_LEAST_N: 1
        # }

    def serialize_a_node(self, node_obj: dict):
        top_level = self.serialize_triples_with_relaxation(node_obj.get(ENTTYPE), is_enttype=True)
        union_descriptors = self.relax_descriptors(node_obj.get(DESCRIPTORS), node_obj.get(NODE))
        return '{\n%s\n%s\n}' % (top_level, union_descriptors)

    def relax_descriptors(self, descriptors, node):
        if not self.relax_strategy or not descriptors:
            return self.serialize_list_of_triples(descriptors)

        at_least_n = self.relax_strategy.get(AT_LEAST_N)
        if not at_least_n or at_least_n >= len(descriptors):
            return '\n'.join([self.serialize_triples_with_relaxation(descriptor) for descriptor in descriptors])

        # no need to satisfy all descriptors, returns results satisfy at_least_n descriptors:
        ret = []
        to_count = []
        for descriptor in descriptors:
            if descriptor[node][0][0] == AIDA_HASNAME:
                # string descriptor, change to filter:
                cnt_var = '%s_hasName_%s' % (node, len(to_count))
                triples = self.serialize_triples({node: [(AIDA_HASNAME, cnt_var)]})
                filters = 'FILTER(%s = %s)' % (cnt_var, descriptor[node][0][1])
                ret.append('%s\n\t%s' % (triples, filters))
                to_count.append(cnt_var)
            else:
                ret.append(self.serialize_triples_with_relaxation(descriptor))
                to_count.append(descriptor[node][0][1])

        count_optional = self.seiralize_cnt_optional(to_count, '>=', at_least_n, node + '_descr_cnt')
        return '\nOPTIONAL {\n%s\n} %s' % ('\n} \nOPTIONAL {\n'.join(ret), count_optional)

    @staticmethod
    def seiralize_cnt_optional(var_list, operator, threshold, cnt_var):
        add_up = ' +\n\t\t'.join(['xsd:integer(BOUND(%s))' % var_name for var_name in var_list])
        filters = 'FILTER (%s %s %d)' % (cnt_var, operator, threshold)
        return '\n\tBIND(%s \n\t\tAS %s) \n\t%s' % (add_up, cnt_var, filters)

    def serialize_triples_with_relaxation(self, triples, is_enttype=False):
        if not triples:
            return ''

        if is_enttype and self.relax_strategy.get(IGNORE_ENTTYPE):
            updated_triples = {}
            for k in triples:
                updated_triples[k] = [(RDF_TYPE, AIDA_ENTITY)]
            return self.serialize_triples(updated_triples)

        # relax on a single descriptors - wider_range and larger_bound
        if self.relax_strategy.get(WIDER_RANGE) or self.relax_strategy.get(LARGER_BOUND):
            # TODO: calc overlap ratio to order results
            ret = []
            filters = []
            for k, pairs in triples.items():
                cur = []
                for i in range(len(pairs)):
                    pred, obj = pairs[i]
                    if (self.relax_strategy.get(WIDER_RANGE) and pred in {AIDA_STARTOFFSET, AIDA_ENDOFFSETINCLUSIVE}) \
                            or (self.relax_strategy.get(LARGER_BOUND) and
                                pred in {AIDA_BOUNDINGBOXUPPERLEFTX, AIDA_BOUNDINGBOXUPPERLEFTY,
                                         AIDA_BOUNDINGBOXLOWERRIGHTX, AIDA_BOUNDINGBOXLOWERRIGHTY}):
                        obj = '%s_%s' % (k, pred[-5:])
                        operator = FILTER_OPERATOR[pred]
                        filters.append('%s %s %s' % (obj, operator, pairs[i][1]))
                    cur.append(' '.join(('\t\t' if i else k, pred, obj, ';' if i < len(pairs)-1 else '.')))
                ret.append('\n'.join(cur))
            return '\t%s\n\tFILTER(%s)' % ('\n\t'.join(ret), ' && '.join(filters)) if filters else '\t' + '\n\t'.join(ret)

        # TODO: other relaxations:

        return '\t' + ('\n\t'.join(['\n'.join(
            [' '.join(('\t\t' if i else k, v[i][0], v[i][1], ';' if i < len(v)-1 else '.')) for i in range(len(v))]
            ) if not k.startswith('@') else v for k, v in triples.items()]))

