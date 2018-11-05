import json, os, sys
from pathlib import Path
import xmltodict
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from src.graph_query import GraphQuery
from src.zerohop_query import ZerohopQuery
from src.class_query import ClassQuery
from src.query_tool import QueryTool, Mode
from src.utils import to_string
from src.web_server.constants import *

app = Flask(__name__)
CORS(app)

with open('configs.json') as f:
    configs = json.load(f)
    queries = configs.get(QUERIES, {})
    endpoints = configs.get(ENDPOINTS, {})

query_loaders = {
    CLASS: ClassQuery,
    ZEROHOP: ZerohopQuery,
    GRAPH: GraphQuery
}

query_instances = {}
ttl_file_lists = {}

modes = {
    'prototype': Mode.PROTOTYPE,
    'cluster': Mode.CLUSTER,
    'singleton': Mode.SINGLETON
}


def get_query_instance(file_key) -> GraphQuery or ZerohopQuery or ClassQuery:
    file_path = queries[file_key][FILE_PATH]
    n2p = queries[file_key].get('n2p', '')
    if file_path not in query_instances:
        query_instance = query_loaders[queries[file_key][TYPE]](file_path, n2p)
        query_instances[file_path] = query_instance
    return query_instances[file_path]


def get_ep_local_files(ep_key):
    folder_path = endpoints[ep_key].get(FOLDER_PATH)
    print(folder_path)
    if endpoints[ep_key][TYPE] == LOCAL_FILES and folder_path:
        if folder_path not in ttl_file_lists:
            path = Path(folder_path)
            print(folder_path)
            print(len(list(path.glob('*.ttl'))))
            ttl_file_lists[folder_path] = [_.stem for _ in path.glob('*.ttl')]
        return ttl_file_lists[folder_path]
    return []


def sample_queries(query_list):
    res = []
    exist = set()
    for i in range(len(query_list)):
        qid = query_list[i]['@id'].rsplit('_', 1)[0]
        if qid not in exist:
            exist.add(qid)
            res.append({
                'query_idx': i,
                'query_json': query_list[i]
            })
    return res


def apply_query(query, query_idx, endpoint):
    print('----apply query----', ep, query_idx)
    query_instance = get_query_instance(query)
    ep = endpoints[endpoint]
    responses = {}
    if ep[TYPE] == REMOTE_EP:
        qt = QueryTool(endpoint=ep[ENDPOINT], mode=modes[ep[MODE]], relax_num_ep=1)
        response, stat, errors = query_instance.ask_all(query_tool=qt, start=query_idx, end=query_idx+1, prefilter=False)
        if response:
            responses = {'dummy': xmltodict.parse(to_string(response))}
    else:
        if query_instance.related_docs:
            for ttl_file in query_instance.related_docs[query_idx]:
                qt = QueryTool(endpoint=ep[FOLDER_PATH] + ttl_file + '.ttl', mode=modes[ep[MODE]], relax_num_ep=1, use_fuseki=ep[ENDPOINT])
                response, stat, errors = query_instance.ask_all(query_tool=qt, start=query_idx, end=query_idx+1,
                                                                root_doc=ttl_file, prefilter=False)
                responses[ttl_file] = xmltodict.parse(to_string(response))
    return responses


def search_xml(file_path, target_qid, tag):
    root = ET.parse(file_path).getroot()
    for response in root.iter(tag):
        if response.attrib['id'] == target_qid:
            return xmltodict.parse(to_string(response))


def find_response(query, query_idx, endpoint):
    print('----find_response----')
    output = endpoints[endpoint]['outputs'][query]
    q_type = queries[query][TYPE]
    query_id = get_query_instance(query).query_list[query_idx]['@id']
    res = {}
    if output.endswith('.xml'):
        cur_res = search_xml(output, query_id, '%squery_responses' % q_type)
        if cur_res:
            res['dummy'] = cur_res
    else:
        path = Path(output)
        for f in list(path.glob('*%s_responses.xml' % q_type)):
            cur_res = search_xml(str(f), query_id, '%squery_responses' % q_type)
            if cur_res:
                res[f.stem] = cur_res
    return res


@app.route('/configs', methods=['GET'])
def get_configs():
    return json.dumps(configs)


@app.route('/query_instance/<query_key>/<sample>', methods=['GET'])
def get_query_list(query_key, sample):
    query_list = get_query_instance(query_key).query_list
    if sample:
        sample_query_list = sample_queries(query_list)
        return json.dumps(sample_query_list, ensure_ascii=False)
    else:
        converted_query_list = [{'query_idx': i, 'query_json': query_list[i]} for i in range(len(query_list))]
        return json.dumps(converted_query_list, ensure_ascii=False)


@app.route('/ep_local_files/<ep_key>', methods=['GET'])
def get_local_file_list(ep_key):
    return json.dumps(get_ep_local_files(ep_key))


@app.route('/apply/<query_key>/<int:query_idx>/<ep_key>', methods=['GET'])
def apply(query_key, query_idx, ep_key):
    res = apply_query(query_key, query_idx, ep_key)
    return json.dumps(res, ensure_ascii=False) if res else ''


@app.route('/find/<query_key>/<int:query_idx>/<ep_key>', methods=['GET'])
def find(query_key, query_idx, ep_key):
    res = find_response(query_key, query_idx, ep_key)
    return json.dumps(res, ensure_ascii=False) if res else ''


if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')