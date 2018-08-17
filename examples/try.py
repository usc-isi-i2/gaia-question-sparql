import os, json, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.Answering import Answering

# endpoint = 'http://gaiadev01.isi.edu:7200/repositories/dry_en'
endpoint = 'http://gaiadev01.isi.edu:3030/gaiaold/sparql'
ont = '../resources/ontology_mapping.json'

answering = Answering(endpoint=endpoint, ont_path=ont)

dir_path = './questions/'
for filename in os.listdir(dir_path):
    if filename != '2_RPI_Data_Q2.xml':
        continue
    print('\n----- %s -----' % filename)
    ans = answering.answer(xml_question=dir_path+filename)
    print('@RESULT:')
    print(json.dumps(ans['graph'], indent=2))

