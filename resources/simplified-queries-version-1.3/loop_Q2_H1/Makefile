all: query response

query:
	xmllint --dtdvalid graph_query/graph_query.dtd  --noout graph_query/graph_query.xml
	xmllint --dtdvalid zerohop_query/zerohop_query.dtd --noout zerohop_query/zerohop_query.xml
	xmllint --dtdvalid class_query/class_query.dtd --noout class_query/class_query.xml

response:
	xmllint --dtdvalid graph_query/graph_response.dtd --noout graph_query/graph_response.xml
	xmllint --dtdvalid zerohop_query/zerohop_response.dtd --noout zerohop_query/zerohop_response.xml
	xmllint --dtdvalid class_query/class_response.dtd --noout class_query/class_response.xml
