import networkx as nx
from typing import List, Dict
from models import BottleneckNode, RootCauseAnalysis

class GraphAnalyzer:
    def __init__(self):
        pass

    def calculate_risk_score(self, graph: nx.DiGraph) -> float:
        # Enhanced risk scoring algorithm
        total_nodes = graph.number_of_nodes()
        if total_nodes == 0:
            return 0.0
        
        # Get centrality metrics
        try:
            betweenness = nx.betweenness_centrality(graph)
        except:
            betweenness = {n: 0.0 for n in graph.nodes()}
            
        critical_nodes = [n for n, d in graph.nodes(data=True) if d.get('status') == 'critical']
        warning_nodes = [n for n, d in graph.nodes(data=True) if d.get('status') == 'warning']
        
        # Base risk
        base_score = 10.0
        
        # Critical bottlenecks (high centrality + critical status)
        high_centrality_critical = [n for n in critical_nodes 
                                   if betweenness.get(n, 0) > 0.2]
        
        # Service type penalties
        db_critical = [n for n in critical_nodes 
                      if graph.nodes[n].get('type') == 'database']
        external_critical = [n for n in critical_nodes 
                           if graph.nodes[n].get('type') == 'external']
        
        # Calculate weighted score
        score = base_score
        score += len(high_centrality_critical) * 25  # Critical bottleneck nodes
        score += len(db_critical) * 20  # Database failures are severe
        score += len(external_critical) * 15  # External API failures
        score += len(critical_nodes) * 10  # Regular critical nodes
        score += len(warning_nodes) * 3  # Warning nodes
        
        # Network partitioning risk
        try:
            if not nx.is_strongly_connected(graph):
                score += 15
        except:
            pass
            
        return min(100.0, score)

    def find_bottlenecks(self, graph: nx.DiGraph) -> List[BottleneckNode]:
        """Identify primary bottlenecks with detailed analysis"""
        bottlenecks = []
        
        try:
            betweenness = nx.betweenness_centrality(graph)
        except:
            betweenness = {n: 0.0 for n in graph.nodes()}
        
        for node_id, attrs in graph.nodes(data=True):
            if attrs.get('status') in ['critical', 'warning']:
                cpu = attrs.get('cpu_usage', 0)
                memory = attrs.get('memory_usage', 0)
                centrality = betweenness.get(node_id, 0)
                node_type = attrs.get('type', 'service')
                
                # Calculate node-specific risk (only for actual problems)
                risk_score = 0
                reasons = []
                
                # Only flag CPU issues at higher thresholds
                if cpu > 90:
                    risk_score += 30
                    reasons.append(f"CPU overload ({cpu:.1f}%)")
                elif cpu > 75:
                    risk_score += 15
                    reasons.append(f"High CPU usage ({cpu:.1f}%)")
                elif cpu > 60:
                    risk_score += 5
                    reasons.append(f"Elevated CPU usage ({cpu:.1f}%)")
                
                # Only flag memory issues at higher thresholds  
                if memory > 90:
                    risk_score += 25
                    reasons.append(f"Memory critical ({memory:.1f}%)")
                elif memory > 75:
                    risk_score += 10
                    reasons.append(f"High memory usage ({memory:.1f}%)")
                
                if centrality > 0.3:
                    risk_score += 15  # Reduced penalty
                    reasons.append("Critical path bottleneck")
                elif centrality > 0.15:
                    risk_score += 5  # Reduced penalty
                    reasons.append("Important path component")
                
                # Only add database penalty if there are actual issues
                if node_type == "database" and (cpu > 60 or memory > 60):
                    risk_score += 10  # Reduced penalty
                    reasons.append("Database service (elevated)")
                
                conn_pool = attrs.get('connection_pool_usage', 0)
                if conn_pool > 85:
                    risk_score += 20
                    reasons.append(f"Connection pool saturated ({conn_pool:.1f}%)")
                elif conn_pool > 70:
                    risk_score += 5
                    reasons.append(f"Connection pool high ({conn_pool:.1f}%)")
                
                error_rate = attrs.get('error_rate', 0)
                if error_rate > 5:  # Higher threshold
                    risk_score += 15
                    reasons.append(f"High error rate ({error_rate:.1f}%)")
                elif error_rate > 2:
                    risk_score += 5
                    reasons.append(f"Elevated error rate ({error_rate:.1f}%)")
                
                # Only create bottleneck if there's actual risk
                if risk_score > 15:  # Minimum threshold for bottleneck
                    bottlenecks.append(BottleneckNode(
                        id=node_id,
                        name=attrs.get('name', node_id),
                        type=node_type,
                        risk_score=min(100.0, risk_score),
                        centrality=centrality,
                        cpu_usage=cpu,
                        memory_usage=memory,
                        reason="; ".join(reasons) if reasons else "Performance concern"
                    ))
        
        # Sort by risk score
        return sorted(bottlenecks, key=lambda x: x.risk_score, reverse=True)

    def analyze_cascading_failures(self, graph: nx.DiGraph, bottlenecks: List[BottleneckNode]) -> List[str]:
        """Identify potential cascading failure chains"""
        cascading = []
        
        for bottleneck in bottlenecks[:3]:  # Top 3 bottlenecks
            if bottleneck.centrality > 0.2:
                # Find downstream dependencies
                try:
                    descendants = nx.descendants(graph, bottleneck.id)
                    if len(descendants) > 2:
                        cascading.append(
                            f"Failure of {bottleneck.name} could cascade to {len(descendants)} services: "
                            f"{', '.join(list(descendants)[:3])}{'...' if len(descendants) > 3 else ''}"
                        )
                except:
                    continue
        
        return cascading

    def generate_recommendations(self, bottlenecks: List[BottleneckNode], graph: nx.DiGraph) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        for bottleneck in bottlenecks[:5]:  # Top 5 bottlenecks
            if bottleneck.cpu_usage > 85:
                if bottleneck.type == "database":
                    recommendations.append(f"Scale {bottleneck.name}: Add read replicas or optimize queries")
                else:
                    recommendations.append(f"Scale {bottleneck.name}: Add 2-3 more instances behind load balancer")
            
            if bottleneck.type == "database" and hasattr(bottleneck, 'connection_pool_usage'):
                recommendations.append(f"Increase connection pool size for {bottleneck.name}")
            
            if bottleneck.centrality > 0.3:
                recommendations.append(f"Reduce dependency on {bottleneck.name}: implement circuit breakers")
            
            if "error rate" in bottleneck.reason.lower():
                recommendations.append(f"Investigate {bottleneck.name}: check logs for error patterns")
        
        # General recommendations
        if len(bottlenecks) > 3:
            recommendations.append("Consider implementing auto-scaling policies")
            recommendations.append("Set up comprehensive monitoring and alerting")
        
        return recommendations[:8]  # Limit to most important

    def perform_root_cause_analysis(self, graph: nx.DiGraph) -> RootCauseAnalysis:
        """Complete root cause analysis with AI insights placeholder"""
        bottlenecks = self.find_bottlenecks(graph)
        cascading_failures = self.analyze_cascading_failures(graph, bottlenecks)
        recommendations = self.generate_recommendations(bottlenecks, graph)
        risk_score = self.calculate_risk_score(graph)
        
        return RootCauseAnalysis(
            primary_bottlenecks=bottlenecks[:5],
            cascading_failures=cascading_failures,
            recommended_actions=recommendations,
            risk_score=risk_score,
            ai_insights="AI analysis placeholder - will be enhanced with LLM integration"
        )

    def find_shortest_path(self, graph: nx.DiGraph, source: str, target: str):
        try:
            return nx.shortest_path(graph, source, target)
        except nx.NetworkXNoPath:
            return []

graph_analyzer = GraphAnalyzer()
