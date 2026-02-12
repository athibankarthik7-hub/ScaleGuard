from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import networkx as nx

from models import SystemGraph, SimulationConfig
from mock_data import generate_mock_system
from simulation import Simulator
from graph import GraphAnalyzer

app = FastAPI(title="ScaleGuard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for demo purposes
current_system = generate_mock_system()
simulator = Simulator()
analyzer = GraphAnalyzer()

# Initialize simulator with initial graph
simulator.build_graph(current_system.nodes, current_system.edges)

@app.get("/")
def read_root():
    return {"message": "ScaleGuard API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/system", response_model=SystemGraph)
def get_system_graph():
    return current_system

@app.post("/api/simulate", response_model=SystemGraph)
def run_simulation(config: SimulationConfig):
    global current_system
    # In a real app, we might not want to permanently mutate the global state
    # but for a prototype, this shows the "live" update effect well.
    
    # 1. Reset to base state to apply growth fresh (optional, but keeps it clean)
    # For now, let's just apply growth on top of current or reset?
    # Let's reset to clean mock to handle "growth from baseline" logic
    base_system = generate_mock_system()
    simulator.build_graph(base_system.nodes, base_system.edges)
    
    # 2. Run simulation
    simulated_graph = simulator.simulate_traffic(config)
    
    # 3. Update global state for other consumers
    current_system = simulated_graph
    
    return current_system

@app.get("/api/risk-score")
def get_risk_score():
    score = analyzer.calculate_risk_score(simulator.graph)
    return {"risk_score": score}

@app.post("/api/reset")
def reset_system():
    global current_system
    current_system = generate_mock_system()
    simulator.build_graph(current_system.nodes, current_system.edges)
    return current_system
