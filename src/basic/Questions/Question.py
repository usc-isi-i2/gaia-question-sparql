
from src.basic.utils import *


class Question(object):
    def __init__(self, question: dict) -> None:
        """
        init a Question with a dict converted from a single xml query by xmltodict module
        :param question: single xml query in dict
        """
        self.query_id = question['@id']
        self.nodes = set()  # to store all the node vars(will be in the sparql select query)
        self.entrypoints = []   # to store the parsed internal representation of entrypoints
        self.edges = []

    def parse_a_entrypoint(self, entrypoint: dict or list) -> None:
        """
        :param entrypoint: a entrypoint is justifications of a node
            e.g. = {  # list of such objects or an single object
                'node': '?attact_target',
                'enttype': 'Person',
                'string_descriptor': {  # list of such objects or an single object
                    'name_string': 'Putin',
                },
                'text_descriptor': {  # list of such objects or an single object
                    'docied': 'HC000ZUW7',
                    'start': '308',
                    'end': '310'
                },
                'image_descriptor': [  # list of such objects or an single object
                    {
                        'doceid': 'HC000ZUW7',
                        'topleft': '10,20',
                        'bottomright": '50,60'
                    },
                    {
                        'doceid': 'HC000ZUW8',
                        'topleft': '20,20',
                        'bottomright": '60,60'
                    }
                ]
            }
        :return: None. just append the parsed result(a dict) to self.entrypoints
            parse an entrypoint to internal dict format for easier serialization to sparql query
            e.g. = {
                      "node": "?attact_target",
                      "enttype": {  # a 'triples' in Serializer, with dict-key is the subject,
                                    # dict-value a list of (predicate, object) tuples
                        "?attact_target_type": [
                          ("rdf:subject", "?attact_target"),
                          ("rdf:predicate", "rdf:type"),
                          ("rdf:object", "ldcOnt:Weapon"
                        ]
                      },
                      "descriptors": [  # a list of "'triples' in Serializer"s
                        {
                          "?crash_target": [
                            [
                              "aida:hasName",
                              "\"MH-17\""
                            ]
                          ]
                        },
                        {
                          "?attact_target": [
                            ("aida:justifiedBy", "?attact_target_text_0")
                          ],
                          "?attact_target_text_0": [
                            ("rdf:type", "aida:TextJustification"   ),
                            ("aida:source", "\"IC0014C4F\""),
                            ("aida:startOffset", "2826"),
                            ("aida:endOffsetInclusive", "2841")
                          ]
                        }
                      ]
                    }
        """
        if isinstance(entrypoint, list):
            for a_entrypoint in entrypoint:
                self.parse_a_entrypoint(a_entrypoint)
        else:
            ep = {NODE: entrypoint[NODE]}
            node = ep[NODE]
            if ENTTYPE in entrypoint:
                ep[ENTTYPE] = self.parse_enttype(node, entrypoint[ENTTYPE])
            ep[DESCRIPTORS] = []
            if STRING_DESCRIPTOR in entrypoint:
                if isinstance(entrypoint[STRING_DESCRIPTOR], dict):
                    ep[DESCRIPTORS].append({node: [(AIDA_HASNAME, self.wrap_data(
                        entrypoint[STRING_DESCRIPTOR][NAME_STRING], 'str'))]})
                else:
                    ep[DESCRIPTORS] += [{node: [(AIDA_HASNAME, self.wrap_data(x[NAME_STRING], 'str'))]}
                                        for x in entrypoint[STRING_DESCRIPTOR]]
            for name_, type_ in ((TEXT_DESCRIPTOR, AIDA_TEXTJUSTIFICATION),
                                 (IMAGE_DESCRIPTOR, AIDA_IMAGEJUSTIFICATION),
                                 (VEDIO_DESCRIPTOR, AIDA_VIDEOJUSTIFICATION)):
                if name_ in entrypoint:
                    self.parse_a_descriptor(node, name_.rstrip('descriptor'), type_, 0, entrypoint[name_], ep[DESCRIPTORS])
            self.entrypoints.append(ep)

    def parse_a_descriptor(self, subject: str, name_: str, type_: str, cnt: int,
                           descriptor_obj: dict or list, descriptor_list: list) -> None:
        """

        :param subject: the subject node of the entrypoint where the descriptor comes from. e.g. "?attact_target"
        :param name_: one of 'text', 'video', 'image'
        :param type_: one of 'aida:TextJustification', 'aida:KeyframeVideoJustification', 'aida:ImageJustification'
        :param cnt: count of justifications, used for generate var name to avoid same var name for different justifications
        :param descriptor_obj: a dict with info of a single justification span
               e.g. {
                        'doceid': 'HC000ZUW8',
                        'topleft': '20,20',
                        'bottomright": '60,60'
                    }
        :param descriptor_list: the list stores results
        :return: None. just append the parsed result(a dict) to "descriptor_list"
               e.g. {
                      "?attact_target": [
                        ("aida:justifiedBy", "?attact_target_text_0")
                      ],
                      "?attact_target_text_0": [
                        ("rdf:type", "aida:TextJustification"   ),
                        ("aida:source", "\"IC0014C4F\""),
                        ("aida:startOffset", "2826"),
                        ("aida:endOffsetInclusive", "2841")
                      ]
                    }

        """
        if isinstance(descriptor_obj, list):
            for i in range(len(descriptor_obj)):
                self.parse_a_descriptor(subject, name_, type_, i, descriptor_obj[i], descriptor_list)
        else:
            justi_var = '%s_%s%d' % (subject, name_, cnt)
            res = {
                subject: [(AIDA_JUSTIFIEDBY, justi_var)],   # ?node aida:justifiedBy ?justi .
                justi_var: [(RDF_TYPE, type_)]              # ?justi a aida:XxxxJustification
            }

            # add predicates directly under ?justi:
            for tag_, ont_, data_type in ((DOCEID, AIDA_SOURCE, 'str'),
                                          (KEYFRAMEID, AIDA_KEYFRAME, 'str'),
                                          (START, AIDA_STARTOFFSET, 'int'),
                                          (END, AIDA_ENDOFFSETINCLUSIVE, 'int')):
                if tag_ in descriptor_obj:
                    res[justi_var].append((ont_, self.wrap_data(descriptor_obj[tag_], data_type)))

            # add predicates under ?bounding_box where ?justi aida:BoundingBox ?bounding_box
            if TOPLEFT in descriptor_obj or BOTTOMRIGHT in descriptor_obj:
                box_var = '%s_%s%d_box' % (subject, name_, cnt)
                res[justi_var].append((AIDA_BOUNDINGBOX, box_var))
                res[box_var] = []
                for tag_, ont_ in ((TOPLEFT, (AIDA_BOUNDINGBOXUPPERLEFTX, AIDA_BOUNDINGBOXUPPERLEFTY)),
                                   (BOTTOMRIGHT, (AIDA_BOUNDINGBOXLOWERRIGHTX, AIDA_BOUNDINGBOXLOWERRIGHTY))):
                    if tag_ in descriptor_obj:
                        values = descriptor_obj[tag_].split(',')
                        res[box_var].append((ont_[0], values[0]))
                        res[box_var].append((ont_[1], values[1]))
            descriptor_list.append(res)

    @staticmethod
    def parse_enttype(sub: str, enttype:str):
        """
        :param sub: subject node var name from xml, e.g. "?attack_target"
        :param enttype: enttype from xml, e.g. "Place", "Person", "Weapon" etc.
        :return: a "triples" object for a rdf:type statement
        """
        return {
            sub + '_type': [
                (RDF_SUBJECT, sub),
                (RDF_PREDICATE, RDF_TYPE),
                (RDF_OBJECT, ENTTYPE_MAPPINT.get(enttype, ldcOnt + ':' + enttype))
        ]}

    @staticmethod
    def wrap_data(x, data_type):
        if data_type == 'str':
            return '"%s"' % x
        elif data_type == 'int':
            return x
        else:
            return x
