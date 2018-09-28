from src.constants import *


def serialize_get_justi(node_uri, limit=None):
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


def serialize_get_justi_cluster(node_uri, mode, limit=None):
    # now that all nodes will be a cluster rather than an entity/event/relation:
    if isinstance(node_uri, list):
        # justi on bnode assertion
        s, p, o = node_uri
        justi_lines = '''
        ?mem aida:cluster <%s> ;
             aida:clusterMember ?sub .
        ?mem2 aida:cluster <%s> ;
              aida:clusterMember ?obj .
        ?xxx a rdf:Statement ;
             rdf:subject ?sub ;
             rdf:predicate ldcOnt:%s ;
             rdf:object ?obj ;
             aida:justifiedBy ?justification .
        ''' % (s, o, p)
    else:
        justi_lines = '''
        ?mem aida:cluster <%s> ;
             aida:clusterMember ?x .
        ?x aida:justifiedBy ?justification .
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


def serialize_string_descriptor(name_string):
    return '?%s aida:hasName "%s" .' % (NODE, name_string.strip('"').encode('latin1').decode('utf-8'))


def serialize_text_descriptor(doceid, start, end):
    return '''
    [    a                         aida:TextJustification ;
         aida:source               "%s" ;
         aida:startOffset          "%s"^^xsd:int ;
         aida:endOffsetInclusive   "%s"^^xsd:int 
    ] 
    ''' % (doceid, start, end)


def serialize_image_video_descriptor(doceid, topleft, bottomright, keyframeid=''):
    top, left = topleft.split(',')
    bottom, right = bottomright.split(',')
    justification_type = AIDA_VIDEOJUSTIFICATION if keyframeid else AIDA_IMAGEJUSTIFICATION
    keyframe_triple = '    aida:keyFrame    "%s" ;' % keyframeid if keyframeid else ''
    return '''
        [   a                %s   ;
            aida:source      "%s" ;
            %s
            aida:boundingBox [
                    aida:boundingBoxUpperLeftX  "%s"^^xsd:int ;
                    aida:boundingBoxUpperLeftY  "%s"^^xsd:int ;
                    aida:boundingBoxLowerRightX "%s"^^xsd:int ;
                    aida:boundingBoxLowerRightY "%s"^^xsd:int 
            ] 
        ] 
    ''' % (justification_type, doceid, keyframe_triple,
           left, top, right, bottom)


def serialize_string_descriptor_relax(name_string):
    return '?%s aida:hasName "%s" .' % (NODE, name_string.strip('"').encode('latin1').decode('utf-8'))


def serialize_text_descriptor_relax(doceid, start, end, var_suffix=''):
    return '''
    [    a                         aida:TextJustification ;
         aida:source               "{docied}" ;
         aida:startOffset          ?{svar} ;
         aida:endOffsetInclusive   ?{evar} 
    ] 
    FILTER ( (?{evar} >= {end} && ?{svar} <= {end}) || (?{svar} <= {start} && ?{evar} >= {start}) )
    '''.format(docied=doceid, svar=EPSO + var_suffix, evar=EPEO + var_suffix, start=start, end=end)


def serialize_image_video_descriptor_relax(doceid, topleft, bottomright, keyframeid='', var_suffix=''):
    top, left = topleft.split(',')
    bottom, right = bottomright.split(',')
    justification_type = AIDA_VIDEOJUSTIFICATION if keyframeid else AIDA_IMAGEJUSTIFICATION
    keyframe_triple = '    aida:keyFrame    "%s" ;' % keyframeid if keyframeid else ''
    return '''
        [   a                {justification_type}   ;
            aida:source      "{doceid}" ;
            {keyframe_triple}
            aida:boundingBox [
                    aida:boundingBoxUpperLeftX  ?{lvar} ;
                    aida:boundingBoxUpperLeftY  ?{tvar} ;
                    aida:boundingBoxLowerRightX ?{rvar} ;
                    aida:boundingBoxLowerRightY ?{bvar} 
            ] 
        ] 
        FILTER (
            ((?{lvar} <= {left} && ?{rvar} >= {left}) || (?{rvar} >= {right} && ?{lvar} <= {right})) &&
            ((?{tvar} <= {top} && ?{bvar} >= {top}) || (?{bvar} >= {bottom} && ?{tvar} <= {bottom}))
        )
    '''.format(justification_type=justification_type, doceid=doceid, keyframe_triple=keyframe_triple,
               lvar=EPULX + var_suffix, tvar=EPULY + var_suffix,
               rvar=EPBRX + var_suffix, bvar=EPBRY + var_suffix,
               left=left, right=right, top=top, bottom=bottom)
