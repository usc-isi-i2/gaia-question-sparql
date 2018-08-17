import json, os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from flask import Flask, render_template, request, redirect
from src.Answering import Answering

app = Flask(__name__, template_folder='./')

ENDPOINT = 'http://gaiadev01.isi.edu:3030/gaiaold/sparql'

qs = []
for qf in os.listdir('../examples/questions/'):
    if qf[0] not in ['1', '2']:
        continue
    with open('../examples/questions/%s' % qf) as f:
        qs.append({'label': qf, 'xml': f.read()})

# var in html:
endpoint = ENDPOINT
xml_question = '<?xml version="1.0"?>\n'
json_question = textarea_strategies = query_result = ''
select_example = len(qs)
check_strategy = 'AUTO'
strategies_list = []
manually = False


def is_select(x):
    return 'selected="selected"' if x == select_example else ''


def is_check(x):
    return 'checked' if x == check_strategy else ''


def option_examples():
    return '\n'.join(['<option value="%d" %s></option>' % (len(qs), is_select(len(qs)))]
                 + ['<option value="%d" %s>%s</option>' % (i, is_select(i), qs[i]['label']) for i in range(len(qs))])


def radio_strategies():
    lines = []
    for s in ['AUTO', 'strict', 'wider_range', 'larger_bound', 'ignore_enttype']:
        lines.append('<input type="radio" name="strategy" value="%s" %s>%s ' % (s, is_check(s), s))
    return '\n'.join(lines)


def tried_strategies(kvs):
    return '\n'.join(['<div><p>%s</p><textarea disabled rows="10">%s</textarea></div>' % (s, q) for s, q in kvs])


def update_forms(forms):
    global endpoint, xml_question
    if 'endpoint' in forms:
        endpoint = forms['endpoint']
    if 'xml_question' in forms:
        xml_question = forms['xml_question']


@app.route('/')
def hello_world():
    strategy_title = ''
    if strategies_list:
        strategy_title = 'Strategies tried: [ MANUALLY ]' if manually else 'Strategies tried: [ AUTO ]'
    return render_template('index.html',
                           option_examples=option_examples(),
                           endpoint=endpoint,
                           xml_question=xml_question,
                           json_question=json_question,
                           query_result=query_result,
                           radio_strategies=radio_strategies(),
                           textarea_strategies=tried_strategies(strategies_list),
                           manually=strategy_title
                           )


@app.route('/query', methods=['POST'])
def query():
    try:
        global json_question, query_result, check_strategy, strategies_list, manually
        check_strategy = request.form['strategy']
        answering = Answering(endpoint=request.form['endpoint'], ont_path='../resources/ontology_mapping.json')
        if check_strategy == 'AUTO':
            ans = answering.answer(request.form['xml_question'])
            strategies_list = list(ans['strategies'].items())
            manually = False
        else:
            ans = answering.answer_with_specified_strategy(request.form['xml_question'], check_strategy)
            strategies_list = strategies_list + list(ans['strategies'].items()) if manually else list(ans['strategies'].items())
            manually = True
        json_question = json.dumps(ans['json'], indent=2)
        query_result = json.dumps(ans['graph'], indent=2)

    except Exception as e:
        query_result = 'Failed, please check your inputs and try again. \n %s' % str(e)
    update_forms(request.form)
    return redirect('/')


@app.route('/example', methods=['POST'])
def examples():
    global xml_question, json_question, textarea_strategies, query_result, select_example, strategies_list
    select_example = int(request.form['example'])
    xml_question = qs[select_example]['xml'] if select_example < len(qs) else '<?xml version="1.0"?>\n'
    json_question = textarea_strategies = query_result = ''
    update_forms(request.form)
    strategies_list = []
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')
