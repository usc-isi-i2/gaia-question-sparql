import json, xmltodict
from src.Question import Question

class QuestionParser(object):
    def __init__(self, ont_path: str) -> None:
        """
        init a question parser with ontology mapping from xml tags to valid sparql uri
        :param ont_path: file path of the ontology mapping json
        """

        self.ont = self.load_ont(ont_path)
        self.ranges = {
            'string': lambda x: '"%s"' % x,
            'uri': lambda x: self.get_path(self.ont, ['class', x, 'path']),
            'number': lambda x: x
        }

        self.JUSTIFIEDBY = 'aida:justifiedBy'
        self.INCLUSTER = 'xij:inCluster'
        self.SUPER_EDGE = lambda s, p, o: [('rdf:subject', s),
                                           ('rdf:predicate', p),
                                           ('rdf:object', o),
                                           ('a', 'aida:SuperEdge')]

    def parse_question(self, xml: str) -> Question:
        """
        parse a xml question to a json representation with valid ontology in sparql
        :param xml: file path of the question in xml, or the xml question text
        :return: a Question instance with json representation of the question
        """
        text = xml
        if xml.endswith('.xml'):
            with open(xml) as f:
                text = f.read()
        ori = xmltodict.parse(text).get('query', {})
        edges = self.parse_edges(self.get_path(ori, ['graph', 'edges', 'edge']))
        entrypoints = self.parse_entrypoints(self.get_path(ori, ['entrypoints']))

        return Question(query={
                '@id': ori.get('@id', ''),
                'edges': edges,
                'entrypoints': entrypoints
            }, prefix=self.ont.get('prefix'))

    def parse_edges(self, edge: list or dict) -> dict:
        ret = {}
        if isinstance(edge, list):
            for e in edge:
                ret.update(self.parse_edges(e))
        else:
            key, s, p, o = edge.values()
            predicate = self.get_path(self.ont, ['predicate', p, 'path'])[0]
            super_edge = '?%s' % key
            ret[super_edge] = self.SUPER_EDGE(s, predicate, o)
        return ret

    def parse_entrypoints(self, entrypoints: dict) -> dict:
        ret = {}
        for k, v in entrypoints.items():
            ret[k] = self.parse_entrypoint(k, v)
        return ret

    def parse_entrypoint(self, ep_type: str, children: dict or list) -> dict:
        triples = {}
        if isinstance(children, list):
            for child in children:
                triples.update(self.parse_entrypoint(ep_type, child))
        else:
            s, exists = '%s_node' % children.get('node'), {}
            self.add_triple(s, self.INCLUSTER, children.get('node'), triples)
            for k, v in children.items():
                predicate = self.get_path(self.ont, ['predicate', k])
                if 'splitter' in predicate:
                    values = v.split(predicate.get('splitter'))
                    predicates = predicate.get('split_to', [])
                    for i in range(len(values)):
                        self.parse_triple(s, predicates[i], values[i], exists, triples)
                elif predicate:
                    self.parse_triple(s, predicate, v, exists, triples)

            justify_type = self.get_path(self.ont, ['class', ep_type, 'path'])
            if justify_type and self.JUSTIFIEDBY in exists:
                self.add_triple(exists[self.JUSTIFIEDBY], 'a', justify_type, triples)

        return triples

    def parse_triple(self, s: str, predicate: dict, value: str, exists: dict, triples: dict) -> None:
        path = predicate.get('path')
        o = self.ranges.get(predicate.get('range'), lambda x: x)(value)
        for i in range(len(path)):
            if i < len(path) - 1:
                if path[i] not in exists:
                    self.add_triple(s, path[i], '?var%d' % i, triples)
                    exists[path[i]] = s = '?var%d' % i
                else:
                    s = exists[path[i]]
            else:
                self.add_triple(s, path[i], o, triples)

    @staticmethod
    def get_path(target: dict, path: list):
        for i in range(len(path)):
            target = target.get(path[i], {})
        return target

    @staticmethod
    def add_triple(s, p, o, triples):
        if s in triples:
            triples[s].append((p, o))
        else:
            triples[s] = [(p, o)]

    @staticmethod
    def load_ont(ont_path: str) -> dict:
        try:
            with open(ont_path) as ont_file:
                return json.load(ont_file)
        except Exception as e:
            print('failed to load ontology, %s' % str(e))
        return {}
