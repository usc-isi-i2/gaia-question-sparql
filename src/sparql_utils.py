from src.utils import *


def serialize_string_descriptor(name_string):
    return '?%s aida:hasName "%s" .' % (NODE, decode_name(name_string.strip('"')))


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
    return '?%s aida:hasName "%s" .' % (NODE, decode_name(name_string.strip('"')))


def serialize_text_descriptor_relax(doceid, start, end, var_suffix=''):
    return '''
    [    a                         aida:TextJustification ;
         aida:source               "{docied}" ;
         aida:startOffset          ?{svar} ;
         aida:endOffsetInclusive   ?{evar} 
    ] 
    FILTER ( (?{evar} >= {start} && ?{svar} <= {end}) || (?{svar} <= {end} && ?{evar} >= {start}) )
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
            ((?{lvar} <= {right} && ?{rvar} >= {left}) || (?{rvar} >= {left} && ?{lvar} <= {right})) &&
            ((?{tvar} <= {bottom} && ?{bvar} >= {top}) || (?{bvar} >= {top} && ?{tvar} <= {bottom}))
        )
    '''.format(justification_type=justification_type, doceid=doceid, keyframe_triple=keyframe_triple,
               lvar=EPULX + var_suffix, tvar=EPULY + var_suffix,
               rvar=EPBRX + var_suffix, bvar=EPBRY + var_suffix,
               left=left, right=right, top=top, bottom=bottom)
