from utils import *

import json

test_event = 'http://www.isi.edu/gaia/events/22ebc69d-7cb5-4326-bf72-c5ae79e71698'
# should have:
# ldcOnt:Conflict.Attack_Place * 4
# ldcOnt:Conflict.Attack_Target * 3
# ldcOnt:Conflict.Attack_Attacker * 2
# ldcOnt:Conflict.Attack_Instrument * 1


def expand_from_subject(subject, num_edges):
    edges, entrypoints, objects = [], [], []
    sub = '?' + subject.rsplit('/', 2)[-2][:-1] + '_' + subject.rsplit('/', 2)[-1][:5]
    possible_edges = get_edges_from_subject(subject)
    i = 0
    for pred, obj_list in possible_edges.items():
        if i == num_edges:
            break
        i += 1
        obj = '?' + pred.rsplit('.', 1)[-1].lower()
        edges.append(construct_edge('edge_%s_%d' % (subject[-5:], i), sub, pred, obj))
        entrypoints.append(construct_ep(obj, get_enttype(obj_list[0]), get_entrypints(obj_list[0])))
        objects.append((obj_list[0], obj))
    return edges, entrypoints, objects


def augment_from_object(object_uri, object_var_name, num_edges, edges):
    exclude_pred = [edge[PREDICATE] for edge in edges]
    possible_edges = get_edges_from_object(object_uri, exclude_pred)
    i = 0
    for pred, sub_list in possible_edges.items():
        if i == num_edges:
            break
        i += 1
        sub = '?subject_' + pred.rsplit('.', 1)[-1].lower()
        edges.append(construct_edge('edge_%s_%d' % (object_uri[-5:], i), sub, pred, object_var_name))
    return i


def generate_two_layer_graph(root, max_edges_per_layer):
    edges, entrypoints, objects = expand_from_subject(root, max_edges_per_layer)
    second_layer_edges = 0
    for obj_uri, obj_var_name in objects:
        second_layer_edges += augment_from_object(obj_uri, obj_var_name, max_edges_per_layer, edges)
        if second_layer_edges >= max_edges_per_layer:
            break
    return construct_graph(edges, entrypoints)



all_events = get_all_event_uri()
for i in range(min(len(all_events), 5)):
    output_file = './sample_question_%d.xml' % i

    test_query_json = generate_two_layer_graph(test_event, 3)
    # pprint(test_query_json)

    from dicttoxml import dicttoxml
    test_query_xml = dicttoxml(test_query_json, attr_type=False, item_func=lambda x: x.rstrip('s'))
    # pprint(test_query_xml)

    write_file(test_query_xml, output_file)





# import xmltodict
# from dicttoxml import dicttoxml
#
# with open('graph_query/graph_query.xml') as f_q:
#     sample_q = xmltodict.parse(f_q.read())
#     pprint(sample_q)
#     back = dicttoxml(sample_q, attr_type=False, item_func=lambda x: x)
#     pprint(back)

# def generate_question_from_an_event()



