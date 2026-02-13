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

    def calculate_load(self, node_type: str, rpm: int, current_cpu: float = 0) -> tuple:
        """Calculate CPU and memory load based on service type with realistic degradation"""
        if node_type == "database":
            # Databases degrade exponentially under load
            cpu = min(100.0, (rpm / 500) ** 1.5 * 10)
            memory = min(100.0, (rpm / 400) ** 1.3 * 15)
            # Connection pool saturation
            conn_pool = min(100.0, (rpm / 300) * 100 / 50)  # 50 max connections
        elif node_type == "cache":
            # Caches handle more load but memory grows
            cpu = min(100.0, (rpm / 2000) ** 1.2 * 5)
            memory = min(100.0, (rpm / 1500) ** 1.4 * 20)
            conn_pool = 0.0
        elif node_type == "external":
            # External services can fail suddenly
            cpu = min(100.0, (rpm / 200) ** 1.8 * 15)
            memory = min(100.0, (rpm / 200) * 10)
            conn_pool = 0.0
        else:
            # Regular services - standard load
            cpu = min(100.0, (rpm / 1000) ** 1.3 * 10)
            memory = min(100.0, (rpm / 800) * 20)
            conn_pool = 0.0
        
        # Error rate increases with overload
        error_rate = 0.0
        if cpu > 80:
            error_rate = min(50.0, (cpu - 80) * 2)
        
        return cpu, memory, conn_pool, error_rate

    def simulate_traffic(self, config: SimulationConfig) -> SystemGraph:
        # Simple simulation logic: Increase load on root nodes and propagate
        # Identify root nodes (in-degree 0)
        start_nodes = [n for n, d in self.graph.in_degree() if d == 0]
        
        # Calculate betweenness centrality for all nodes
        try:
            betweenness = nx.betweenness_centrality(self.graph)
        except:
            betweenness = {n: 0.0 for n in self.graph.nodes()}
        
        # Propagate traffic using BFS
        bfs_layers = list(nx.bfs_layers(self.graph, start_nodes))
        
        updated_nodes = {}
        
        for layer in bfs_layers:
            for node_id in layer:
                node_data = self.graph.nodes[node_id]
                node_type = node_data.get('type', 'service')
                
                # Simulate load increase based on growth factor
                current_rpm = node_data.get('rpm', 100)
                new_rpm = int(current_rpm * config.traffic_growth_factor * random.uniform(0.9, 1.1))
                
                # Calculate realistic resource usage
                cpu_load, memory_load, conn_pool, error_rate = self.calculate_load(
                    node_type, new_rpm, node_data.get('cpu_usage', 0)
                )
                
                # Update metrics
                self.graph.nodes[node_id]['rpm'] = new_rpm
                self.graph.nodes[node_id]['cpu_usage'] = cpu_load
                self.graph.nodes[node_id]['memory_usage'] = memory_load
                self.graph.nodes[node_id]['connection_pool_usage'] = conn_pool
                self.graph.nodes[node_id]['error_rate'] = error_rate
                self.graph.nodes[node_id]['centrality_score'] = betweenness.get(node_id, 0.0)
                
                # Enhanced bottleneck detection
                if node_type == "database":
                    # Databases are critical - stricter thresholds
                    if cpu_load > 70 or memory_load > 75 or conn_pool > 80:
                        self.graph.nodes[node_id]['status'] = 'warning'
                    if cpu_load > 85 or memory_load > 90 or conn_pool > 95:
                        self.graph.nodes[node_id]['status'] = 'critical'
                elif node_type == "external":
                    # External services can fail, causing cascading issues
                    if cpu_load > 75 or error_rate > 5:
                        self.graph.nodes[node_id]['status'] = 'warning'
                    if cpu_load > 90 or error_rate > 15:
                        self.graph.nodes[node_id]['status'] = 'critical'
                else:
                    # Standard services
                    if cpu_load > 80 or memory_load > 80:
                        self.graph.nodes[node_id]['status'] = 'warning'
                    if cpu_load > 95 or memory_load > 95:
                        self.graph.nodes[node_id]['status'] = 'critical'
                
                # Cascading failure: if critical and high centrality, degrade dependents
                if self.graph.nodes[node_id]['status'] == 'critical' and betweenness.get(node_id, 0) > 0.2:
                    for successor in self.graph.successors(node_id):
                        if self.graph.nodes[successor]['status'] == 'healthy':
                            self.graph.nodes[successor]['status'] = 'warning'
                            self.graph.nodes[successor]['error_rate'] = min(
                                self.graph.nodes[successor].get('error_rate', 0) + 10, 50
                            )
                
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
                'rpm': attrs.get('rpm', 0),
                'error_rate': attrs.get('error_rate', 0.0),
                'connection_pool_usage': attrs.get('connection_pool_usage', 0.0),
                'queue_depth': attrs.get('queue_depth', 0),
                'centrality_score': attrs.get('centrality_score', 0.0)
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
