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
