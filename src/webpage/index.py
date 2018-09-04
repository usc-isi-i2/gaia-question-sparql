import json, os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from flask import Flask, render_template, request, redirect

from src.advanced.AdvancedAnswer import AdvancedAnswer

app = Flask(__name__, template_folder='./')

ENDPOINT = 'http://gaiadev01.isi.edu:3030/latest_rpi_en/sparql'
STRATEGY = ['wider_range', 'larger_bound', 'ignore_enttype']
# RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
# XIJ = 'http://gaiadev01.isi.edu:5005/cluster/'

qs = []
for qf in os.listdir('../../examples/'):
    if not qf.endswith('.xml') or 'response' in qf:
        continue
    with open('../../examples/%s' % qf) as f:
        qs.append({'label': qf, 'xml': f.read()})

# var in html:
endpoint = ENDPOINT
xml_question = '<?xml version="1.0"?>\n'
textarea_strategies = query_result = ''
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
    global endpoint, xml_question
    if 'endpoint' in forms:
        endpoint = forms['endpoint']
    if 'xml_question' in forms:
        xml_question = forms['xml_question']

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
        answer = AdvancedAnswer(question=request.form['xml_question'], endpoint=request.form['endpoint'])
        if not checked_strategies:
            # TODO: try strategies automatically
            ans = answer.ask()
            strategies_tried = [('strict', ans['sparql'])]
            manually = False
        else:
            relax = {}
            for x in checked_strategies:
                relax[x] = True
            ans = answer.ask_with_specified_relaxation(relax)
            strategies_tried = strategies_tried + [('+'.join(checked_strategies), ans['sparql'])] # if manually else list(ans['strategies'].items())
            manually = True
        query_result = ans['response']
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
