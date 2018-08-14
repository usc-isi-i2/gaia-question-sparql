import os, json, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.Answering import Answering

endpoint = 'http://kg2018a.isi.edu:3030/all_clusters/sparql'
# endpoint = 'http://gaiadev01.isi.edu:3030/clusters/sparql'
ont = '../resources/ontology_mapping.json'

answering = Answering(endpoint=endpoint, ont_path=ont)

dir_path = './questions/'
for filename in os.listdir(dir_path):
    print('\n----- %s -----' % filename)
    ans = answering.answer(xml_question=dir_path+filename)
    print('@RESULT:')
    print(json.dumps(ans['graph'], indent=2))

