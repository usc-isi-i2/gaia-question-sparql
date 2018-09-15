

from src.basic.Questions.Question import *


class ZerohopQuestion(Question):
    def __init__(self, question):
        super(ZerohopQuestion, self).__init__(question)
        """
        {
          "@id": "AIDA_ZH_2018_1",
          "entrypoint": {
            "node": "?node",
            "enttype": "GeopoliticalEntity",
            "video_descriptor": {
              "doceid": "HC0000077",
              "keyframeid": "HC0000077_1",
              "topleft": "0,0",
              "bottomright": "480,360"
            }
          },
          "sparql": "SELECT ?nid_ep ?nid_ot ?doceid ?sid ?kfid ?so ?eo ?ulx ?uly ?brx ?bry ?st ?et ?cm1cv ?cm2cv ?cv\n\tWHERE {\n\t\t?statement1    a                    rdf:Statement .\n\t\t?statement1    rdf:object           ldcOnt:GeopoliticalEntity .\n\t\t?statement1    rdf:predicate        rdf:type .\n\t\t?statement1    rdf:subject          ?nid_ot .\n\t\t?statement1    aida:justifiedBy     ?justification .\n\t\t?justification aida:source          ?doceid .\n\t\t?justification aida:confidence      ?confidence .\n\t\t?confidence    aida:confidenceValue ?cv .\n\n\t\t?cluster        a                    aida:SameAsCluster .\n\t\t?statement2     a                    aida:ClusterMembership .\n\t\t?statement2     aida:cluster         ?cluster .\n\t\t?statement2     aida:clusterMember   ?nid_ep .\n\t\t?statement2     aida:confidence      ?cm1_confidence .\n\t\t?cm1_confidence aida:confidenceValue ?cm1cv .\n\n\t\t?statement3     a                    aida:ClusterMembership .\n\t\t?statement3     aida:cluster         ?cluster .\n\t\t?statement3     aida:clusterMember   ?nid_ot .\n\t\t?statement3     aida:confidence      ?cm2_confidence .\n\t\t?cm2_confidence aida:confidenceValue ?cm2cv .\n\n\t\t?statement4       a                         rdf:Statement .\n\t\t?statement4       rdf:object                ldcOnt:GeopoliticalEntity .\n\t\t?statement4       rdf:predicate             rdf:type .\n\t\t?statement4       rdf:subject               ?nid_ep .\n\t\t?statement4       aida:justifiedBy          ?justification_ep .\n\t\t?justification_ep a                         aida:KeyFrameVideoJustification .\n\t\t?justification_ep aida:source               \"HC0000077\" .\n\t\t?justification_ep aida:keyFrame             \"HC0000077_1\" .\n\t\t?justification_ep aida:boundingBox          ?boundingbox_ep .\n\t\t?boundingbox_ep aida:boundingBoxUpperLeftX  ?epulx .\n\t\t?boundingbox_ep aida:boundingBoxUpperLeftY  ?epuly .\n\t\t?boundingbox_ep aida:boundingBoxLowerRightX ?eplrx .\n\t\t?boundingbox_ep aida:boundingBoxLowerRightY ?eplry .\n\t\tFILTER ((?epulx >= 0 && ?epulx <= 480 && ?epuly <= 360 && ?epuly >= 0) ||\n\t\t\t(?eplrx >= 0 && ?eplrx <= 480 && ?eplry <= 360 && ?eplry >= 0) ||\n\t\t\t(?eplrx >= 0 && ?eplrx <= 480 && ?epuly <= 360 && ?epuly >= 0) ||\n\t\t\t(?epulx >= 0 && ?epulx <= 480 && ?eplry <= 360 && ?eplry >= 0)) .\n\n\n\t\tOPTIONAL { ?justification a                  aida:TextJustification .\n\t\t\t?justification aida:startOffset            ?so .\n\t\t\t?justification aida:endOffsetInclusive     ?eo }\n\n\t\tOPTIONAL { ?justification a                  aida:ImageJustification .\n\t\t\t?justification aida:boundingBox            ?bb  .\n\t\t\t?bb            aida:boundingBoxUpperLeftX  ?ulx .\n\t\t\t?bb            aida:boundingBoxUpperLeftY  ?uly .\n\t\t\t?bb            aida:boundingBoxLowerRightX ?brx .\n\t\t\t?bb            aida:boundingBoxLowerRightY ?bry }\n\n\t\tOPTIONAL { ?justification a                  aida:KeyFrameVideoJustification .\n\t\t\t?justification aida:keyFrame               ?kfid .\n\t\t\t?justification aida:boundingBox            ?bb  .\n\t\t\t?bb            aida:boundingBoxUpperLeftX  ?ulx .\n\t\t\t?bb            aida:boundingBoxUpperLeftY  ?uly .\n\t\t\t?bb            aida:boundingBoxLowerRightX ?brx .\n\t\t\t?bb            aida:boundingBoxLowerRightY ?bry }\n\n\t\tOPTIONAL { ?justification a                  aida:ShotVideoJustification .\n\t\t\t?justification aida:shot                   ?sid }\n\n\t\tOPTIONAL { ?justification a                  aida:AudioJustification .\n\t\t\t?justification aida:startTimestamp         ?st .\n\t\t\t?justification aida:endTimestamp           ?et }\n\n\t}"
        }
        """

        self.query_type = ZEROHOP_QUERY
        ep = question[ENTRYPOINT]
        self.enttype = ep[ENTTYPE]
        self.descriptor_type = [k for k in (TEXT_DESCRIPTOR, IMAGE_DESCRIPTOR, VIDEO_DESCRIPTOR) if k in ep][0]
        self.descriptor = ep[self.descriptor_type]





