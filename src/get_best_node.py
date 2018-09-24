from src.utils import *
from itertools import combinations


def get_best_node(descriptors: list, endpoint: str, relax_num_ep=None) -> str:
    '''
    This method is to find a node that best match a list of typed descriptors
    TODO: now only return max(sum(overlap/target for each descriptor)), not ignore type
    :param descriptors: list of typed descriptors: [
        {
            'enttype': 'Person',
            'string_descriptor': {
                'name_string': ''
            }
        },
        {
            'enttype': 'Organization',
            'text_descriptors': {
                'doceid': '',
                'start': '',
                'end'
            }
        }
    ]
    :param endpoint: sparql ep or rdflib graph
    :param relax: int, at least how many eps have to match
         BIND(
            xsd:integer(bound(?opt1)) +
            xsd:integer(bound(?opt2))
            AS ?cnt)
         FILTER(?cnt > relax)
    :return: str: the best node uri
    '''

    # try strict match:
    states = []
    for i in range(len(descriptors)):
        descriptor = descriptors[i]
        enttype = descriptor[ENTTYPE]

        if STRING_DESCRIPTOR in descriptor:
            justi = '?%s aida:hasName "%s" .' % (NODE, descriptor[STRING_DESCRIPTOR][NAME_STRING].strip('"'))
        elif TEXT_DESCRIPTOR in descriptor:
            justi = serialize_text_justification(**descriptor[TEXT_DESCRIPTOR])
        else:
            des = descriptor.get(IMAGE_DESCRIPTOR) or descriptor.get(VIDEO_DESCRIPTOR)
            justi = serialize_image_video_justification(**des)

        states.append(serialize_a_types_descriptor(NODE, enttype, justi, str(i)))
    sparql_query_strict = '''
    SELECT DISTINCT ?node WHERE {
    %s
    }
    ''' % '\n'.join(states)
    # print(sparql_query_strict)
    nodes = select_query(endpoint, sparql_query_strict)
    if nodes and nodes[0]:
        # TODO: is it possible that multiple nodes match the target -> maybe something went wrong during extraction
        return nodes[0][0]

    # try relax match and get the best one:
    states = []
    var_list = [NODE]
    to_compare = [] # [(1, 3), (3, 7) ... ] for the (start, end) index in var list for each descriptor
    for i in range(len(descriptors)):
        descriptor = descriptors[i]
        enttype = descriptor[ENTTYPE]

        if STRING_DESCRIPTOR in descriptor:
            justi = '?%s aida:hasName "%s" .' % (NODE, descriptor[STRING_DESCRIPTOR][NAME_STRING].strip('"'))
        elif TEXT_DESCRIPTOR in descriptor:
            justi = serialize_text_justification_relax(**descriptor[TEXT_DESCRIPTOR], var_suffix=str(i))
            to_compare.append((len(var_list), len(var_list) + 2))
            var_list.append(EPSO + str(i))
            var_list.append(EPEO + str(i))
        else:
            des = descriptor.get(IMAGE_DESCRIPTOR) or descriptor.get(VIDEO_DESCRIPTOR)
            justi = serialize_image_video_justification_relax(**des, var_suffix=str(i))
            to_compare.append((len(var_list), len(var_list) + 4))
            var_list.append(EPULX + str(i))
            var_list.append(EPULY + str(i))
            var_list.append(EPBRX + str(i))
            var_list.append(EPBRY + str(i))

        states.append(serialize_a_types_descriptor(NODE, enttype, justi, str(i)))

    sparql_query_relax = '''
    SELECT DISTINCT %s WHERE {
    %s
    }
    ''' % (' '.join(['?' + x for x in var_list]), '\n'.join(states))
    candidates = select_query(endpoint, sparql_query_relax)
    best_uri = get_best_candidate(candidates, to_compare, descriptors)
    if best_uri:
        return best_uri

    # try match some of the descriptors:
    if relax_num_ep and 0 < relax_num_ep < len(descriptors):
        for idx_list in combinations(range(len(descriptors)), relax_num_ep):
            # TODO: check from len-1 to relax_num_ep
            best_uri = get_best_node([descriptors[i] for i in idx_list], endpoint)
            if best_uri:
                return best_uri

    return ''


def get_best_candidate(candidates, to_compare, descriptors):
    best_uri = ''
    best_score = 0
    for candidate in candidates:
        cur_score = 0
        for i in range(len(to_compare)):
            start, end = to_compare[i]
            descriptor = descriptors[i]
            cand_bound = candidate[start:end]
            if TEXT_DESCRIPTOR in descriptor:
                target_start = descriptor[TEXT_DESCRIPTOR][START]
                target_end = descriptor[TEXT_DESCRIPTOR][END]
                score = get_overlap_text(int(cand_bound[0]), int(cand_bound[1]), int(target_start), int(target_end))
            else:
                des = descriptor.get(IMAGE_DESCRIPTOR) or descriptor.get(VIDEO_DESCRIPTOR)
                target_ulx, target_uly = des[TOPLEFT].split(',')
                target_brx, target_bry = des[BOTTOMRIGHT].split(',')
                score = get_overlap_img(*[int(x) for x in cand_bound],
                                        int(target_ulx), int(target_uly), int(target_brx), int(target_bry))
            # TODO: how much overlapped ?
            if score < 0.4:
                return ''
            cur_score += score
        if cur_score > best_score:
            best_score = cur_score
            best_uri = candidate[0]
    return best_uri


def get_overlap_text(start, end, target_start, target_end):
    # TODO: how to define 'best match'?
    return (min(end, target_end) - max(start, target_start)) / (target_end - target_start)


def get_overlap_img(left, top, bottom, right, target_left, target_top, target_bottom, target_right):
    # TODO: how to define 'best match'?
    w = min(right, target_right) - max(left, target_left)
    h = min(bottom, target_bottom) - max(top, target_top)
    return w * h / ((target_right - target_left) * (target_bottom - target_top))


def serialize_a_types_descriptor(node_var, enttype, justi_sparql, suffix=''):
    if justi_sparql[-1] == '.':
        # string descriptor
        return '''
        ?state_%s a rdf:Statement ;
                  rdf:subject ?%s ;
                  rdf:predicate rdf:type ;
                  rdf:object ldcOnt:%s .
        %s
        ''' % (suffix, node_var, enttype, justi_sparql)
    else:
        return '''
        ?state_%s a rdf:Statement ;
                  rdf:subject ?%s ;
                  rdf:predicate rdf:type ;
                  rdf:object ldcOnt:%s ;
                  aida:justifiedBy %s .
        ''' % (suffix, node_var, enttype, justi_sparql)


def serialize_text_justification(doceid, start, end):
    return '''
    [    a                         aida:TextJustification ;
         aida:source               "%s" ;
         aida:startOffset          "%s"^^xsd:int ;
         aida:endOffsetInclusive   "%s"^^xsd:int 
    ] 
    ''' % (doceid, start, end)


def serialize_image_video_justification(doceid, topleft, bottomright, keyframeid=''):
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


def serialize_text_justification_relax(doceid, start, end, var_suffix=''):
    return '''
    [    a                         aida:TextJustification ;
         aida:source               "{docied}" ;
         aida:startOffset          ?{svar} ;
         aida:endOffsetInclusive   ?{evar} 
    ] 
    FILTER ( (?{evar} >= {end} && ?{svar} <= {end}) || (?{svar} <= {start} && ?{evar} >= {start}) )
    '''.format(docied=doceid, svar=EPSO + var_suffix, evar=EPEO + var_suffix, start=start, end=end)


def serialize_image_video_justification_relax(doceid, topleft, bottomright, keyframeid='', var_suffix=''):
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
