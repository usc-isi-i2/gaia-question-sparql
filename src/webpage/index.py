import json, os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from flask import Flask, render_template, request, redirect
from src.advanced.AdvancedXMLLoader import AdvancedXMLLoader

app = Flask(__name__, template_folder='./')

ENDPOINT = 'http://gaiadev01.isi.edu:3030/rpi0901aif80d2/sparql'
STRATEGY = ['wider_range', 'larger_bound', 'ignore_enttype', 'on_supergraph']
# RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
# XIJ = 'http://gaiadev01.isi.edu:5005/cluster/'

qs = []
for qf in os.listdir('../../examples/xml_queries/'):
    if not qf.endswith('.xml') or 'response' in qf:
        continue
    with open('../../examples/xml_queries/%s' % qf) as f:
        qs.append({'label': qf, 'xml': f.read()})

# var in html:
endpoint = ENDPOINT
xml_question = '<?xml version="1.0"?>\n'
textarea_strategies = query_result = at_least_n = ''
select_example = len(qs)
strategies_tried = []
manually = False
checked_strategies = set()


def is_select(x):
    return 'selected="selected"' if x == select_example else ''


def is_check(x):
    return 'checked' if x in checked_strategies else ''


def option_examples():
    return '\n'.join(['<option value="%d" %s></option>' % (len(qs), is_select(len(qs)))]
                 + ['<option value="%d" %s>%s</option>' % (i, is_select(i), qs[i]['label']) for i in range(len(qs))])


def check_strategies():
    lines = []
    for s in STRATEGY:
        lines.append('<input type="checkbox" name="strategy_%s" value="%s" %s>%s ' % (s, s, is_check(s), s))
    return '\n'.join(lines)


def tried_strategies(kvs):
    return '\n'.join(['<li><span>%s</span><textarea disabled>%s</textarea></li>' % (s, q) for s, q in kvs])


def update_forms(forms):
    global endpoint, xml_question, at_least_n, checked_strategies
    checked_strategies = set([x for x in STRATEGY if 'strategy_%s' % x in forms])

    if 'endpoint' in forms:
        endpoint = forms['endpoint']
    if 'xml_question' in forms:
        xml_question = forms['xml_question']
    if 'at_least_n' in forms:
        at_least_n = forms['at_least_n']


#
# def wrap_td(k, uri):
#     if k == 'predicate':
#         return '<td>%s</td>' % uri.split('#')[-1]
#     return '<td><a href="%s">%s</a></td>' % (XIJ+'/'.join(uri.split('/')[-2:]), uri)
#
#
# def pretty_result(result):
#     keys = ['subject', 'predicate', 'object']
#     ret = ['<tr>%s</tr>' % ''.join(['<th>%s</th>' % k for k in keys])]
#     for se in result:
#         ret.append('<tr>%s</tr>' % ''.join([wrap_td(k, se[RDF+k][0]['@id']) for k in keys]))
#     return '\n'.join(ret)


@app.route('/')
def hello_world():
    strategy_title = ''
    if strategies_tried:
        strategy_title = 'Strategies tried: [ MANUALLY ]' if manually else 'Strategies tried: [ AUTO ]'
    return render_template('index.html',
                           option_examples=option_examples(),
                           endpoint=endpoint,
                           xml_question=xml_question,
                           query_result=query_result,
                           check_strategies=check_strategies(),
                           textarea_strategies=tried_strategies(strategies_tried),
                           manually=strategy_title
                           )


@app.route('/query', methods=['POST'])
def query():
    try:
        global query_result, strategies_tried, manually, checked_strategies
        checked_strategies = set([x for x in STRATEGY if 'strategy_%s' % x in request.form])
        at_least_n = request.form['at_least_n']
        answer = AdvancedXMLLoader(request.form['xml_question'])
        if not checked_strategies and not at_least_n:
            # TODO: try strategies automatically
            ans = answer.answer_all(endpoint=request.form['endpoint'])
            strategies_tried = [('strict', x['sparql']) for x in ans]
            manually = False
        else:
            relax = {}
            if at_least_n.isdigit() and int(at_least_n) > 0:
                relax['at_least_n'] = int(at_least_n)
            for x in checked_strategies:
                relax[x] = True
            ans = answer.answer_one_specify_relaxation(answer.get_question_list()[0], request.form['endpoint'], relax)
            strategies_tried = strategies_tried + [('+'.join(checked_strategies), ans['sparql'])] # if manually else list(ans['strategies'].items())
            manually = True
        query_result = '\n'.join([x['response'] for x in ans])
    except Exception as e:
        query_result = 'Failed, please check your inputs and try again. \n %s' % str(e)
    update_forms(request.form)
    return redirect('/')


@app.route('/example', methods=['POST'])
def examples():
    global xml_question, textarea_strategies, query_result, select_example, strategies_tried
    select_example = int(request.form['example'])
    xml_question = qs[select_example]['xml'] if select_example < len(qs) else '<?xml version="1.0"?>\n'
    textarea_strategies = query_result = ''
    update_forms(request.form)
    strategies_tried = []
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, port=5001, host='0.0.0.0')
