import networkx as nx
from typing import List, Dict

class GraphAnalyzer:
    def __init__(self):
        pass

    def calculate_risk_score(self, graph: nx.DiGraph) -> float:
        # Calculate a system-wide risk score (0-100)
        # Based on:
        # 1. Number of critical nodes
        # 2. Avg CPU/Mem usage
        # 3. Connectivity (centrality of failing nodes)
        
        total_nodes = graph.number_of_nodes()
        if total_nodes == 0:
            return 0.0
            
        critical_nodes = [n for n, d in graph.nodes(data=True) if d.get('status') == 'critical']
        warning_nodes = [n for n, d in graph.nodes(data=True) if d.get('status') == 'warning']
        
        base_score = 10.0 # Base risk
        
        # Weighted penalty
        score = base_score + (len(critical_nodes) * 20) + (len(warning_nodes) * 5)
        
        # Cap at 100
        return min(100.0, score)

    def find_shortest_path(self, graph: nx.DiGraph, source: str, target: str):
        try:
            return nx.shortest_path(graph, source, target)
        except nx.NetworkXNoPath:
            return []

graph_analyzer = GraphAnalyzer()
