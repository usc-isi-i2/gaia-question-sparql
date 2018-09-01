# question-sparql
[gaia] convert a xml question to sparql query, get results and format to xml response

## Documentation

#### Installation:
* `git clone` the repo
* run `cd question-sparql`
* run `pip install -r requirements.txt` to install dependencies

#### UPDATE - 20180901
The old version question-answering is under `legacy` folder.
Current version will fit the edge definition as:
```
subject: an Event or a Relation
predicate: the role in the Event/Relation(detailed predicate with '_XXX')
object: an Entity
```

Under the `src/basic` folder is the scripts for strictly parse the query to sparql and format the results as xml.
(NIST-QA)

Under the `src/advanced` folder, there will be scripts for relaxation and super graph query.
(ISI-QA)

The `query_generator` folder contains scripts for automatically generating graph queries in xml, from the sub-graphs of our dataset.
 - run `generate_graph_query.py`




