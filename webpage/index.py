import json, os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from flask import Flask, render_template, request, redirect
from src.Answering import Answering

app = Flask(__name__, template_folder='./')

ENDPOINT = 'http://gaiadev01.isi.edu:3030/gaiaold/sparql'

qs = []
for qf in os.listdir('../examples/questions/'):
    with open('../examples/questions/%s' % qf) as f:
        qs.append({'label': qf, 'xml': f.read()})

# var in html:
option_examples = '\n'.join(['<option value="%d">%s</option>' % (i, qs[i]['label']) for i in range(len(qs))])
endpoint = ENDPOINT
xml_question = '<?xml version="1.0"?>\n'
json_question = textarea_strategies = query_result = ''


def update_forms(forms):
    global endpoint, xml_question
    if 'endpoint' in forms:
        endpoint = forms['endpoint']
    if 'xml_question' in forms:
        xml_question = forms['xml_question']


@app.route('/')
def hello_world():
    return render_template('index.html',
                           option_examples=option_examples,
                           endpoint=endpoint,
                           xml_question=xml_question,
                           json_question=json_question,
                           textarea_strategies=textarea_strategies,
                           query_result=query_result
                           )


@app.route('/query', methods=['POST'])
def query():
    try:
        global json_question, textarea_strategies, query_result
        answering = Answering(endpoint=request.form['endpoint'], ont_path='../resources/ontology_mapping.json')
        ans = answering.answer(request.form['xml_question'])
        json_question = json.dumps(ans['json'], indent=2)
        textarea_strategies = '\n'.join(['<div><p>%s</p><textarea disabled rows="10">%s</textarea></div>' % (s, q)
                                         for s, q in ans['strategies'].items()])
        query_result = json.dumps(ans['graph'], indent=2)
    except Exception as e:
        query_result = 'Failed, please check your inputs and try again. \n %s' % str(e)
    update_forms(request.form)
    return redirect('/')


@app.route('/example', methods=['POST'])
def examples():
    global xml_question, json_question, textarea_strategies, query_result
    xml_question = qs[int(request.form['example'])]['xml']
    json_question = textarea_strategies = query_result = ''
    update_forms(request.form)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')
