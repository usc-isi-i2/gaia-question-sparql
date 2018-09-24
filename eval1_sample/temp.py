from rdflib.graph import Graph
from src.utils import PREFIX

g = Graph()
g.parse('./ttls/HC000VS3G.ttl', format='n3')

q = PREFIX + '''
        SELECT DISTINCT ?doceid ?sid ?kfid ?so ?eo ?ulx ?uly ?brx ?bry ?st ?et ?cv
        WHERE {
            
            
        ?xxx a rdf:Statement ;
             rdf::subject <http://www.isi.edu/gaia/events/207d2f0b-f17c-46a4-b057-61e6100dcdee> ;
             rdf::predicate ldcOnt:Contact.Broadcast_Broadcaster ;
             rdf::object <http://www.isi.edu/gaia/entities/7f9de5c3-14d5-43f2-a603-feee69d2aebe> ;
             aida:justifiedBy ?justification .
        
            ?justification aida:source          ?doceid .
            ?justification aida:confidence      ?confidence .
            ?confidence    aida:confidenceValue ?cv .
    
            OPTIONAL { 
                ?justification a                           aida:TextJustification .
                ?justification aida:startOffset            ?so .
                ?justification aida:endOffsetInclusive     ?eo 
            }
    
            OPTIONAL { 
                ?justification a                           aida:ImageJustification .
                ?justification aida:boundingBox            ?bb  .
                ?bb            aida:boundingBoxUpperLeftX  ?ulx .
                ?bb            aida:boundingBoxUpperLeftY  ?uly .
                ?bb            aida:boundingBoxLowerRightX ?brx .
                ?bb            aida:boundingBoxLowerRightY ?bry 
            }
    
            OPTIONAL { 
                ?justification a                           aida:KeyFrameVideoJustification .
                ?justification aida:keyFrame               ?kfid .
                ?justification aida:boundingBox            ?bb  .
                ?bb            aida:boundingBoxUpperLeftX  ?ulx .
                ?bb            aida:boundingBoxUpperLeftY  ?uly .
                ?bb            aida:boundingBoxLowerRightX ?brx .
                ?bb            aida:boundingBoxLowerRightY ?bry 
            }
    
            # OPTIONAL { 
            #     ?justification a                           aida:ShotVideoJustification .
            #     ?justification aida:shot                   ?sid 
            # }
            # 
            # OPTIONAL { 
            #     ?justification a                           aida:AudioJustification .
            #     ?justification aida:startTimestamp         ?st .
            #     ?justification aida:endTimestamp           ?et 
            # }
        }  LIMIT 2
'''

res = g.query(q)
for r in res:
    print(r)
