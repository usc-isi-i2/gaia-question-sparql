
from src.basic.Questions.Serializer import *

class Question(object):
    def __init__(self, question):
        self.query_id = question['@id']
        self.entrypoints = []
        self.nodes = set()

    def parse_a_entrypoint(self, entrypoint: list or dict):
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
                    ep[DESCRIPTORS].append({node: [(AIDA_HASNAME, self.quote(entrypoint[STRING_DESCRIPTOR][NAME_STRING]))]})
                else:
                    ep[DESCRIPTORS] += [{node: [(AIDA_HASNAME, self.quote(x[NAME_STRING]))]} for x in entrypoint[STRING_DESCRIPTOR]]
            for name_, type_ in ((TEXT_DESCRIPTOR, AIDA_TEXTJUSTIFICATION),
                                 (IMAGE_DESCRIPTOR, AIDA_IMAGEJUSTIFICATION),
                                 (VEDIO_DESCRIPTOR, AIDA_VIDEOJUSTIFICATION)):
                if name_ in entrypoint:
                    self.parse_a_descriptor(node, name_.rstrip('descriptor'), type_, 0, entrypoint[name_], ep[DESCRIPTORS])
            self.entrypoints.append(ep)

    def parse_a_descriptor(self, subject, name_, type_, cnt, descriptor_obj, descriptor_list):
        if isinstance(descriptor_obj, list):
            for i in range(len(descriptor_obj)):
                self.parse_a_descriptor(subject, name_, type_, i, descriptor_obj[i], descriptor_list)
        else:
            justi_var = '%s_%s%d' % (subject, name_, cnt)
            res = {
                subject: [(AIDA_JUSTIFIEDBY, justi_var)],
                justi_var: [(RDF_TYPE, type_)]
            }

            for tag_, ont_ in ((DOCEID, AIDA_SOURCE),
                               (KEYFRAMEID, AIDA_KEYFRAME)):
                if tag_ in descriptor_obj:
                    res[justi_var].append((ont_, self.quote(descriptor_obj[tag_])))

            for tag_, ont_ in ((START, AIDA_STARTOFFSET),
                               (END, AIDA_ENDOFFSETINCLUSIVE)):
                if tag_ in descriptor_obj:
                    res[justi_var].append((ont_, descriptor_obj[tag_]))

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

    def serialize_sparql(self):
        pass

    @staticmethod
    def parse_enttype(sub, enttype):
        return {
            sub + '_type': [
                (RDF_SUBJECT, sub),
                (RDF_PREDICATE, RDF_TYPE),
                (RDF_OBJECT, ENTTYPE_MAPPINT.get(enttype, ldcOnt + ':' + enttype))
        ]}

    @staticmethod
    def quote(x):
        return '"%s"' % x
