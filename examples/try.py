from src.Answering import Answering
import os

endpoint = 'http://gaiadev01.isi.edu:3030/clusters/sparql'
ont = '../resources/ontology_mapping.json'

answering = Answering(endpoint=endpoint, ont_path=ont)

dir_path = '../examples/questions/'
for filename in os.listdir(dir_path):
    print('\n----- %s -----' % filename)
    ans = answering.answer(xml_question_file=dir_path+filename)
    print('@RESULT:')
    print(ans)

