class Question(object):
    def __init__(self, query: dict, prefix: dict=None):
        self.query = query
        self.sparql_prefix = self.serialize_prefix(prefix)

    def to_sparql(self, relax_strategy=None) -> str:
        if not relax_strategy:
            edges = self.serialize_triples(self.query.get('edges', {}).values())
            entrypoints = self.union([self.serialize_triples(ep) for ep in self.query.get('entrypoints', {}).values()])
            return '%s\n\nCONSTRUCT {\n%s\n}\nWHERE {\n%s\n\n%s\n}' % (self.sparql_prefix, edges, edges, entrypoints)

    @staticmethod
    def serialize_prefix(prefix: dict) -> str:
        return '\n'.join(['PREFIX %s: <%s>' % (k, v) for k, v in prefix.items()])

    @staticmethod
    def serialize_triples(triples: iter) -> str:
        return '\n'.join(['%s .' % ' '.join(t.values()) for t in triples])

    @staticmethod
    def union(clauses: list) -> str:
        return '{\n%s\n}' % '\n}\nUNION\n{\n'.join(clauses)