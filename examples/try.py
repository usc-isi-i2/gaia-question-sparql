from src.QuestionParser import QuestionParser

qp = QuestionParser('../resources/ontology_mapping.json')
q = qp.parse_question('question.xml')

print(q.to_sparql())

# import json
# print(json.dumps(ori, indent=2))