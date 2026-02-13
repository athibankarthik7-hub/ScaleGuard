from pydantic import BaseModel
from typing import List, Optional

class ServiceNode(BaseModel):
    id: str
    name: str
    type: str  # service, database, cache, gateway
    tier: str  # frontend, backend, data
    status: str = "healthy"
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    latency: float = 0.0
    rpm: int = 0
    error_rate: float = 0.0  # % of failed requests
    connection_pool_usage: float = 0.0  # for databases
    queue_depth: int = 0  # for async services
    centrality_score: float = 0.0  # betweenness centrality

class DependencyEdge(BaseModel):
    source: str
    target: str
    type: str = "http"
    latency: float = 0.0
    throughput: int = 0

class SystemGraph(BaseModel):
    nodes: List[ServiceNode]
    edges: List[DependencyEdge]

class SimulationConfig(BaseModel):
    traffic_growth_factor: float = 1.0
    duration_seconds: int = 60

class BottleneckNode(BaseModel):
    id: str
    name: str
    type: str
    risk_score: float
    centrality: float
    cpu_usage: float
    memory_usage: float
    reason: str

class RootCauseAnalysis(BaseModel):
    primary_bottlenecks: List[BottleneckNode]
    cascading_failures: List[str]
    recommended_actions: List[str]
    risk_score: float
    ai_insights: Optional[str] = None
