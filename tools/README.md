run `generate_graph_query.py` to get 100 randomly generated graph queries under a folder `outputs`

update - 20180831
1. for now the other end node of an edge will be randomly selected from possible node
2. for now the each type of justification of each node will be at most 3
3. filter out existing predicates for more generalized query


20180829
to solve:
1. too many justifications, how to randomly select several justifications
2. need heuristic rules to get meaningful graphs(filter out things like `A locnear B; locnear C; locnear D`)
3. widely cover all subgraphs(different combinations)


