class Question(object):
    def __init__(self, query: dict, prefix: dict=None):
        self.query = query
        self.sparql_prefix = self.serialize_prefix(prefix)
        self.sparql_edges = self.serialize_triples(self.query.get('edges', {}))
        self.relax = {
            'wider_range': lambda: self._relax_range({'aida:startOffset'}, {'aida:endOffsetInclusive'}),
            'larger_bound': lambda: self._relax_range({'aida:boundingBoxUpperLeftX', 'aida:boundingBoxUpperLeftY'},
                                                      {'aida:boundingBoxLowerRightX', 'aida:boundingBoxLowerRightY'}),
            'ignore_enttype': self._ignore_enttype
        }
        self.SPARQL_TYPE = ['a', 'rdf:type']

    def to_sparql(self, relax_strategy=None) -> str:
        entries = self.relax.get(relax_strategy, self.strict)()
        query_str = self.serialize_final_query(self.sparql_prefix, self.sparql_edges, self.union(entries))
        print(query_str)
        return query_str

    def strict(self):
        return [self.serialize_triples(ep) for ep in self.query.get('entrypoints', {}).values()]

    def _relax_range(self, less_than, greater_than):
        entries = []
        for ep in self.query.get('entrypoints', {}).values():
            updated_ep, filters = {}, []
            for s, tuples in ep.items():
                updated_ep[s] = []
                for (p, o) in tuples:
                    if p in less_than or p in greater_than:
                        var_name = '?%s' % p.split(':')[-1]
                        filters.append('%s %s= %s' % (var_name, '<' if p in less_than else '>', o))
                        o = var_name
                    updated_ep[s].append((p, o))
            entries.append('%s\n%s' % (self.serialize_triples(updated_ep), self.serialize_filters(filters, '||')))
        return entries

    def _ignore_enttype(self):
        entries = []
        for ep in self.query.get('entrypoints', {}).values():
            updated_ep, flag = {}, True
            for s, tuples in ep.items():
                updated_ep[s] = [t for t in tuples if t[0] not in self.SPARQL_TYPE] if flag else tuples
                flag = False
            entries.append(self.serialize_triples(updated_ep))
        return entries

    @staticmethod
    def serialize_final_query(prefix, edges, others):
        return '%s\n\nCONSTRUCT {\n%s\n}\nWHERE {\n%s\n\n%s\n}' % (prefix, edges, edges, others)

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
        return '\n'.join(['\n'.join([' '.join((k if i == 0 else '\t', v[i][0], v[i][1], '.' if i == len(v)-1 else ';'))
                                     for i in range(len(v))]) for k, v in triples.items()])

    @staticmethod
    def union(clauses: list) -> str:
        return '{\n%s\n}' % '\n}\nUNION\n{\n'.join(clauses)
