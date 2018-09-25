

def serialize_get_justi(node_uri, include_cluster_members=False, limit=None):
    if isinstance(node_uri, list):
        # justi on bnode assertion
        s, p, o = node_uri
        justi_lines = '''
        ?xxx a rdf:Statement ;
             rdf:subject <%s> ;
             rdf:predicate ldcOnt:%s ;
             rdf:object <%s> ;
             aida:justifiedBy ?justification .
        ''' % (s, p, o)
    elif include_cluster_members:
        justi_lines = '''
        {
        ?mem aida:cluster ?c ;
             aida:clusterMember <%s> .
        ?mem2 aida:cluster ?c ;
              aida:clusterMember ?xxx .
        ?xxx aida:justifiedBy ?justification .
        } UNION {
        <%s> aida:justifiedBy ?justification .
        }
        ''' % (node_uri, node_uri)
    else:
        justi_lines = '''
        <%s> aida:justifiedBy ?justification .
        ''' % node_uri
    return '''
        SELECT DISTINCT ?doceid ?sid ?kfid ?so ?eo ?ulx ?uly ?brx ?bry ?st ?et ?cv
        WHERE {
            
            %s
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
        } %s
    ''' % (justi_lines, ' LIMIT %d' % limit if limit else '')
