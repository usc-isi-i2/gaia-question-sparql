import json
import os
import xmltodict
import xml.etree.ElementTree as ET
from xml.dom import minidom
from src.constants import *

c2p = json.load(open(os.path.dirname(__file__) + '/tools/c2p.json'))
p2c = json.load(open(os.path.dirname(__file__) + '/tools/p2c.json'))

ocrs = set(json.load(open(os.path.dirname(__file__) + '/tools/ocrs.json')))
block_ocr_sparql = 'FILTER (?doceid not in ( "%s" ))' % '", "'.join(ocrs)

coredocs = set([_.strip() for _ in open(os.path.dirname(__file__) + '/tools/coredocs.txt').readlines()])


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


def construct_justifications(justi_root, enttype, rows, suffix='_justification', merge_conf=False):
    conf = 0
    for row in rows:
        doceid, sid, kfid, so, eo, ulx, uly, brx, bry, st, et, cv = row
        if merge_conf:
            row_ = {DOCEID: doceid}
            conf += float(cv)
        else:
            row_ = {DOCEID: doceid, CONFIDENCE: cv}
        if enttype:
            row_[ENTTYPE] = enttype
        if so:
            type_ = 'text'
            row_.update({START: so, END: eo})
        elif kfid:
            type_ = 'video'
            row_.update({KEYFRAMEID: kfid,
                         TOPLEFT: '%s,%s' % (uly, ulx),
                         BOTTOMRIGHT: '%s,%s' % (bry, brx),
                         })
        else:
            type_ = 'image'
            row_.update({TOPLEFT: '%s,%s' % (uly, ulx),
                         BOTTOMRIGHT: '%s,%s' % (bry, brx),
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
        justification = ET.SubElement(justi_root, type_ + suffix)
        update_xml(justification, row_)
    if merge_conf and rows:
        update_xml(justi_root, {CONFIDENCE: str(conf/len(rows))})


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
    print(to_string(x))


def write_file(x, output, mode='w'):
    if len(output.rsplit('/', 1)) == 2:
        dirpath = output.rsplit('/', 1)[0]
        if dirpath and dirpath != '.':
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)
    with open(output, mode) as f:
        f.write(to_string(x))


def to_string(x):
    if isinstance(x, list):
        return '\n'.join([to_string(ele) for ele in x])
    if isinstance(x, dict):
        return json.dumps(x, indent=2, ensure_ascii=False)
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


def find_keys(key, dictionary):
    for k, v in dictionary.items():
        if k == key:
            if key == NAME_STRING:
                yield decode_name(v)
            else:
                yield v
        elif isinstance(v, dict):
            for result in find_keys(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find_keys(key, d):
                    yield result


def get_overlap_text(start, end, target_start, target_end):
    # TODO: how to define 'best match'?
    overlap = min(end, target_end) - max(start, target_start) + 1
    if overlap < 2:
        return 0
    return overlap / (target_end - target_start) + 1


def get_overlap_img(left, top, bottom, right, target_left, target_top, target_bottom, target_right):
    # TODO: how to define 'best match'?
    w = min(right, target_right) - max(left, target_left) + 1
    h = min(bottom, target_bottom) - max(top, target_top) + 1
    return w * h / ((target_right - target_left) * (target_bottom - target_top))


def decode_name(x):
    try:
        return x.encode('latin-1').decode('utf-8', errors='ignore')
    except UnicodeEncodeError:
        return x


def generate_n2p_json(txt_file):
    with open(txt_file) as f:
        lines = f.readlines()
        n2p = {}    # hasName: [ttl file names]
        p2n = {}
        for line in lines:
            l = line.strip()
            if l.endswith('.ttl'):
                doc_id = l.rstrip('.ttl').rsplit('/', 1)[-1]
                p2n[doc_id] = set()
            else:
                if l not in n2p:
                    n2p[l] = set()
                n2p[l].add(doc_id)
                p2n[doc_id].add(l)
        return n2p  #, p2n


