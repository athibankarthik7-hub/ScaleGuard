from typing import List, Dict
import random
from models import ServiceNode, DependencyEdge, SystemGraph, SimulationConfig
import networkx as nx

class Simulator:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(self, nodes: List[ServiceNode], edges: List[DependencyEdge]):
        self.graph.clear()
        for node in nodes:
            self.graph.add_node(node.id, **node.dict())
        for edge in edges:
            self.graph.add_edge(edge.source, edge.target, **edge.dict())

    def simulate_traffic(self, config: SimulationConfig) -> SystemGraph:
        # Simple simulation logic: Increase load on root nodes and propagate
        # Identify root nodes (in-degree 0)
        start_nodes = [n for n, d in self.graph.in_degree() if d == 0]
        
        # Propagate traffic
        # This is a simplified BFS propagation for demonstration
        # Real implementation would use more complex queuing theory or flow analysis
        
        bfs_layers = list(nx.bfs_layers(self.graph, start_nodes))
        
        updated_nodes = {}
        
        for layer in bfs_layers:
            for node_id in layer:
                node_data = self.graph.nodes[node_id]
                # Simulate load increase based on growth factor and random variability
                current_rpm = node_data.get('rpm', 100)
                new_rpm = int(current_rpm * config.traffic_growth_factor * random.uniform(0.9, 1.1))
                
                # Check resource limits (mock logic)
                cpu_load = min(100.0, (new_rpm / 1000) * 10) # 1000 RPM = 10% CPU base? Just mock formula
                memory_load = min(100.0, (new_rpm / 1000) * 20)
                
                self.graph.nodes[node_id]['rpm'] = new_rpm
                self.graph.nodes[node_id]['cpu_usage'] = cpu_load
                self.graph.nodes[node_id]['memory_usage'] = memory_load
                
                # Define simple bottleneck condition
                if cpu_load > 80 or memory_load > 80:
                    self.graph.nodes[node_id]['status'] = 'warning'
                if cpu_load > 95 or memory_load > 95:
                    self.graph.nodes[node_id]['status'] = 'critical'
                
                updated_nodes[node_id] = self.graph.nodes[node_id]

        # Reconstruct SystemGraph
        final_nodes = []
        for n_id, attrs in self.graph.nodes(data=True):
            # Create a clean dict for ServiceNode
            node_dict = {
                'id': n_id,
                'name': attrs.get('name', n_id),
                'type': attrs.get('type', 'service'),
                'tier': attrs.get('tier', 'backend'),
                'status': attrs.get('status', 'healthy'),
                'cpu_usage': attrs.get('cpu_usage', 0.0),
                'memory_usage': attrs.get('memory_usage', 0.0),
                'latency': attrs.get('latency', 0.0),
                'rpm': attrs.get('rpm', 0)
            }
            final_nodes.append(ServiceNode(**node_dict))
            
        final_edges = []
        for u, v, attrs in self.graph.edges(data=True):
             edge_dict = {
                 'source': u,
                 'target': v,
                 'type': attrs.get('type', 'http'),
                 'latency': attrs.get('latency', 0.0),
                 'throughput': attrs.get('throughput', 0)
             }
             final_edges.append(DependencyEdge(**edge_dict))
             
        return SystemGraph(nodes=final_nodes, edges=final_edges)

simulation_engine = Simulator()
