import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.query_generator.generate_graph_query import run_from_events

run_from_events(5, './outputs')
