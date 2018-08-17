

class Question(object):
    def __init__(self, query: dict, prefix: dict=None):
        self.query = query
        self.sparql_prefix = self.serialize_prefix(prefix)
        self.sparql_edges = self.serialize_triples(self.query.get('edges', {}))

        self.STRATEGY_TYPE = {'wider_range', 'larger_bound', 'ignore_enttype'}
        self.LESS_THAN = {
            'wider_range': {'io:startOffset'},
            'larger_bound': {'io:boundingBoxUpperLeftX', 'io:boundingBoxUpperLeftY'}
        }
        self.GREATER_THAN = {
            'wider_range': {'io:endOffsetInclusive'},
            'larger_bound': {'io:boundingBoxLowerRightX', 'io:boundingBoxLowerRightY'}
        }
        self.SPARQL_TYPE = ['a', 'rdf:type']

    def to_sparql(self, relax_strategy=None) -> str:
        entries = self.relax([relax_strategy] if isinstance(relax_strategy, str) else relax_strategy) if relax_strategy else self.strict()
        query_str = self.serialize_final_query(self.sparql_prefix, self.sparql_edges, self.union(entries))
        return query_str

    def strict(self):
        return [self.serialize_triples(ep) for ep in self.query.get('entrypoints', {}).values()]

    def relax(self, strategies):
        less_than = set.union(*[self.LESS_THAN.get(lt, set()) for lt in strategies])
        greater_than = set.union(*[self.GREATER_THAN.get(gt, set()) for gt in strategies])
        ignore_type = 'ignore_enttype' in strategies
        if less_than or greater_than or ignore_type:
            return self._relax(less_than, greater_than, ignore_type)
        else:
            return self.strict()

    def _relax(self, less_than=set(), greater_than=set(), ignore_type=False):
        entries = []
        for ep in self.query.get('entrypoints', {}).values():
            updated_ep, filters, flag = {}, [], True
            for s, tuples in ep.items():
                updated_ep[s] = []
                for (p, o) in tuples:
                    if ignore_type and flag and p in self.SPARQL_TYPE:
                        continue
                    if p in less_than or p in greater_than:
                        var_name = '?%s' % p.split(':')[-1]
                        filters.append('%s %s= %s' % (var_name, '<' if p in less_than else '>', o))
                        o = var_name
                    updated_ep[s].append((p, o))
                flag = False
            entries.append('%s\n%s' % (self.serialize_triples(updated_ep), self.serialize_filters(filters, '||')))
        return entries

    @staticmethod
    def serialize_final_query(prefix, edges, others):
        return '%s\n\nCONSTRUCT {\n\t%s\n}\nWHERE {\n\t%s\n\n%s\n}' % (prefix, edges, edges, others)

    @staticmethod
    def serialize_filters(filter_statements, joiner):
        if not filter_statements:
            return ''
        return 'FILTER( %s )\n' % ((' %s ' % joiner).join(filter_statements))

    @staticmethod
    def serialize_prefix(prefix: dict) -> str:
        return '\n'.join(['PREFIX %s: <%s>' % (k, v) for k, v in prefix.items()])

    @staticmethod
    def serialize_triples(triples: dict) -> str:
        return '\n\t'.join(['\n'.join([' '.join(('\t\t' if i else k, v[i][0], v[i][1], ';' if i < len(v)-1 else '.'))
                                       for i in range(len(v))]) for k, v in triples.items()])

    @staticmethod
    def union(clauses: list) -> str:
        return '\t{\n\t%s\n\t}' % '\n\t}\n\tUNION\n\t{\n\t'.join(clauses)
