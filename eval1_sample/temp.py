from rdflib.graph import Graph
from src.utils import PREFIX

# g = Graph()
# g.parse('./ttls/HC000VS3G.ttl', format='n3')
#
# q = PREFIX + '''
#     SELECT DISTINCT ?node ?epso0 ?epeo0 ?epso1 ?epeo1 WHERE {
#
#         ?state_0 a rdf:Statement ;
#                   rdf:subject ?node ;
#                   rdf:predicate rdf:type ;
#                   rdf:object ldcOnt:Facility ;
#                   aida:justifiedBy
#     [    a                         aida:TextJustification ;
#          aida:source               "HC000ZPT1" ;
#          aida:startOffset          ?epso0 ;
#          aida:endOffsetInclusive   ?epeo0
#     ]
#     FILTER ( (?epeo0 >= 82 && ?epso0 <= 82) || (?epso0 <= 65 && ?epeo0 >= 65) )
#      .
#
#
#         ?state_1 a rdf:Statement ;
#                   rdf:subject ?node ;
#                   rdf:predicate rdf:type ;
#                   rdf:object ldcOnt:Facility ;
#                   aida:justifiedBy
#     [    a                         aida:TextJustification ;
#          aida:source               "HC000ZPT1" ;
#          aida:startOffset          ?epso1 ;
#          aida:endOffsetInclusive   ?epeo1
#     ]
#     FILTER ( (?epeo1 >= 121 && ?epso1 <= 121) || (?epso1 <= 111 && ?epeo1 >= 111) )
#      .
#
#     }
# '''
#
# res = g.query(q)
# for r in res:
#     print(r)

