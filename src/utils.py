import json
import os
import csv
import xmltodict
import xml.etree.ElementTree as ET
from xml.dom import minidom
from rdflib.graph import Graph
from SPARQLWrapper import SPARQLWrapper, CSV
from src.constants import *


def init_graph(ttl_file):
    g = Graph()
    # print(ttl_file)
    g.parse(ttl_file, format='n3')
    return g


def select_query(endpoint, q):
    # print(q)
    sparql_query = PREFIX + q
    if isinstance(endpoint, Graph):
        # print(sparql_query)
        csv_res = endpoint.query(sparql_query).serialize(format='csv')
        rows = [x.decode('utf-8') for x in csv_res.splitlines()][1:]
    else:
        sw = SPARQLWrapper(endpoint)
        sw.setQuery(sparql_query)
        sw.setReturnFormat(CSV)
        rows = sw.query().convert().splitlines()[1:]
    res = list(csv.reader(rows))
    # print(res)
    return res


def update_xml(root, obj):
    if isinstance(obj, str):
        root.text = obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, list):
                for v_ in v:
                    update_xml(ET.SubElement(root, k), v_)
            else:
                update_xml(ET.SubElement(root, k), v)


def construct_justifications(justi_root, enttype, rows):
    for row in rows:
        doceid, sid, kfid, so, eo, ulx, uly, brx, bry, st, et, cv = row
        row_ = {DOCEID: doceid, CONFIDENCE: cv}
        if enttype:
            row_[ENTTYPE] = enttype
        if so:
            type_ = 'text'
            row_.update({START: so, END: eo})
        elif kfid:
            type_ = 'video'
            row_.update({KEYFRAMEID: kfid,
                         TOPLEFT: '%s,%s' % (ulx, uly),
                         BOTTOMRIGHT: '%s,%s' % (brx, bry),
                         })
        else:
            type_ = 'image'
            row_.update({TOPLEFT: '%s,%s' % (ulx, uly),
                         BOTTOMRIGHT: '%s,%s' % (brx, bry),
                         })
        # elif sid:
        #     type_ = 'shot'
        #     row_.update({'shotid': sid,
        #                  TOPLEFT: '%s,%s' % (ulx, uly),
        #                  BOTTOMRIGHT: '%s,%s' % (brx, bry),
        #                  })
        # elif st:
        #     type_ = 'audio'
        #     row_.update({START: st, END: et})
        justification = ET.SubElement(justi_root, type_ + '_justification')
        update_xml(justification, row_)


def xml_loader(xml_file_or_string: str, query_key: str) -> list:
    if xml_file_or_string.endswith('.xml'):
        with open(xml_file_or_string) as f:
            q_dict = xmltodict.parse(f.read())
    else:
        q_dict = xmltodict.parse(xml_file_or_string)
    for k, v in q_dict.items():
        content = v[query_key]
        if isinstance(content, list):
            return content
        else:
            return [content]


def pprint(x):
    if not x:
        print('Empty')
    if isinstance(x, dict):
        print(json.dumps(x, indent=2))
    elif isinstance(x, list):
        for ele in x:
            pprint(ele)
    elif isinstance(x, ET.ElementTree):
        print(minidom.parseString(ET.tostring(x.getroot())).toprettyxml())
    else:
        if isinstance(x, bytes):
            x = x.decode('utf-8')
        try:
            print(minidom.parseString(x).toprettyxml())
        except:
            print(x)


def write_file(x, output):
    if len(output.rsplit('/', 1)) == 2:
        dirpath = output.rsplit('/', 1)[0]
        if dirpath and dirpath != '.':
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
    with open(output, 'w') as f:
        f.write(to_string(x))


def to_string(x):
    if isinstance(x, list):
        return '\n'.join([to_string(ele) for ele in x])
    if isinstance(x, dict):
        return json.dumps(x, indent=2)
    elif isinstance(x, ET.ElementTree):
        str_xml = ET.tostring(x.getroot())
        return minidom.parseString(str_xml).toprettyxml()
    elif isinstance(x, ET.Element):
        return minidom.parseString(ET.tostring(x)).toprettyxml()
    else:
        if isinstance(x, bytes):
            x = x.decode('utf-8')
        try:
            return minidom.parseString(x).toprettyxml()
        except:
            return str(x)
