import json, os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from flask import Flask, render_template, request, redirect, url_for, jsonify
from src.graph_query import GraphQuery
from src.zerohop_query import ZerohopQuery
from src.class_query import ClassQuery
from src.web_server.constants import *


app = Flask(__name__)

with open('configs.json') as f:
    configs = json.load(f)
    queries = configs.get(QUERIES, {})
    remote_eps = configs.get(ENDPOINTS, {}).get(REMOTE_EPS, {})
    local_folders = configs.get(ENDPOINTS, {}).get(LOCAL_FILES, {})

query_loaders = {
    CLASS: ClassQuery,
    ZEROHOP: ZerohopQuery,
    GRAPH: GraphQuery
}

query_instances = {}


def get_query_instance(file_key) -> GraphQuery or ZerohopQuery or ClassQuery:
    file_path = queries[file_key][FILE_PATH]
    if file_path not in query_instances:
        query_instance = query_loaders[queries[file_key][TYPE]](file_path)
        query_instances[file_path] = query_instance
    return query_instances[file_path]


@app.route('/query_files', methods=['GET'])
def endpoints():
    return jsonify(queries)


@app.route('/query_files', methods=['GET'])
def query_files():
    return jsonify(queries)


@app.route('/query_list/<query_file_key>', methods=['GET'])
def query_list(query_file_key):
    return jsonify(get_query_instance(query_file_key).query_list)


@app.route('/query/<query_file_key>/<int:query_idx>', methods=['GET'])
def query(query_file_key, query_idx):
    # query_instance = get_query_instance(query_file_key)
    # query_instance.ask_all(quert_tool=)


with app.test_request_context():
    print(url_for('query_files'))
    print(url_for('query_list', query_file='aaa'))


if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')