
from src.basic.Serializer import *
from src.advanced.Relaxation import Relaxation
from src.advanced.advanced_utils import *


class AdvancedSerializer(Serializer):
    def __init__(self, question):
        Serializer.__init__(self, question)
        self.rlx = None

    def serialize_select_query(self, relax_strategy: Relaxation=None):
        where_statements = []
        if isinstance(self.question, ClassQuestion):
            # where_statements = [self.serialize_triples(self.question.enttype)]
            return class_query(self.question.ori[ENTTYPE])
        elif isinstance(self.question, ZerohopQuestion):
            where_statements = [self.serialize_entrypoints()]
        elif isinstance(self.question, GraphQuestion):
            self.rlx = relax_strategy
            where_statements = [self.serialize_edges(),
                                self.serialize_entrypoints()]
        return self.select + self.wrap_where(where_statements)

    def serialize_a_node(self, node_obj: dict):
        top_level = self.serialize_triples_with_relaxation(node_obj.get(ENTTYPE), is_enttype=True)
        union_descriptors = self.relax_descriptors(node_obj.get(DESCRIPTORS), node_obj.get(NODE))
        return '{\n%s\n%s\n}' % (top_level, union_descriptors)

    def serialize_edges(self):
        if self.rlx.on_supergraph:
            prototypes = {''}
            for edge in self.question.edges:
                for k, v in edge.items():
                    for sub_or_obj in (v[1][1], v[3][1]):
                        prop_triple = self.serialize_triples({sub_or_obj + '_cluster': [(AIDA_PROTOTYPE, sub_or_obj)]})
                        prototypes.add(prop_triple)
            return self.serialize_list_of_triples(self.question.edges) + '\n'.join(prototypes)
        return super(AdvancedSerializer, self).serialize_edges()

    def relax_descriptors(self, descriptors, node):
        if not self.rlx or not descriptors:
            return self.serialize_list_of_triples(descriptors)

        at_least_n = self.rlx.at_least_n
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

        if is_enttype and self.rlx.ignore_enttype:
            updated_triples = {}
            for k in triples:
                updated_triples[k] = [(RDF_TYPE, AIDA_ENTITY)]
            return self.serialize_triples(updated_triples)

        # relax on a single descriptors - wider_range and larger_bound
        if self.rlx.wider_range or self.rlx.larger_bound:
            # TODO: calc overlap ratio to order results
            ret = []
            filters = []
            for k, pairs in triples.items():
                cur = []
                for i in range(len(pairs)):
                    pred, obj = pairs[i]
                    if (self.rlx.wider_range and pred in {AIDA_STARTOFFSET, AIDA_ENDOFFSETINCLUSIVE}) \
                            or (self.rlx.larger_bound and
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
