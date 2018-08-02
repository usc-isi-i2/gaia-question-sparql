class Question(object):
    def __init__(self, query: dict, prefix: dict=None):
        self.query = query
        self.sparql_prefix = self.serialize_prefix(prefix)
        self.relax = {
            'wider_range': self._wider_range,
            'ignore_enttype': self._ignore_enttype
        }

    def to_sparql(self, relax_strategy=None) -> str:
        query_str = self.relax.get(relax_strategy, self.strict)()
        print(query_str)
        return query_str

    def strict(self):
        edges = self.serialize_triples(self.query.get('edges', {}).values())
        entrypoints = self.union([self.serialize_triples(ep) for ep in self.query.get('entrypoints', {}).values()])
        return self.serialize_final_query(self.sparql_prefix, edges, entrypoints)

    def _wider_range(self):
        edges = self.serialize_triples(self.query.get('edges', {}).values())
        entries = []
        for ep in self.query.get('entrypoints', {}).values():
            statements = []
            filters = []
            for t in ep:
                s, p, o = t.values()
                if 'startOffset' in p:
                    var_name = '?startOffset'
                    filters.append('%s <= %s' % (var_name, o))
                    o = var_name
                elif 'endOffset' in p:
                    var_name = '?endOffset'
                    filters.append('%s >= %s' % (var_name, o))
                    o = var_name
                statements.append(self.serialize_single_triple(s, p, o))
            statements.append(self.serialize_filters(filters, '||'))
            entries.append(''.join(statements))

        return self.serialize_final_query(self.sparql_prefix, edges, self.union(entries))

    def _ignore_enttype(self):
        ignore_pred = ['a', 'rdf:type']
        edges = self.serialize_triples(self.query.get('edges', {}).values())
        entries = []
        for ep in self.query.get('entrypoints', {}).values():
            main_node = ep[0]['subject']
            statements = []
            for t in ep:
                s, p, o = t.values()
                if s != main_node or p not in ignore_pred:
                    statements.append(self.serialize_single_triple(s, p, o))
            entries.append(''.join(statements))
        return self.serialize_final_query(self.sparql_prefix, edges, self.union(entries))


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
    def serialize_single_triple(s, p, o) -> str:
        return '%s %s %s .\n' % (s, p, o)

    @staticmethod
    def serialize_triples(triples: iter) -> str:
        return '\n'.join(['%s .' % ' '.join(t.values()) for t in triples])

    @staticmethod
    def union(clauses: list) -> str:
        return '{\n%s\n}' % '\n}\nUNION\n{\n'.join(clauses)
