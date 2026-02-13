from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import networkx as nx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from models import SystemGraph, SimulationConfig, RootCauseAnalysis, ServiceNode, DependencyEdge
from mock_data import generate_mock_system
from simulation import Simulator
from graph import GraphAnalyzer
from ai_integration import ai_manager
from historical_tracker import historical_tracker
from predictive_analytics import predictive_analyzer
from auto_remediation import auto_remediator, RemediationStatus

app = FastAPI(title="ScaleGuard API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state - Start with empty system (user must input data)
# Use POST /api/reset to load sample mock data
current_system = SystemGraph(nodes=[], edges=[])
simulator = Simulator()
analyzer = GraphAnalyzer()

# Initialize simulator with empty graph
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
    """Run traffic simulation on the current user-provided system"""
    global current_system
    
    if len(current_system.nodes) == 0:
        raise HTTPException(
            status_code=400, 
            detail="No system data to simulate. Please add nodes and edges first."
        )
    
    # Rebuild graph with current system before simulating
    simulator.build_graph(current_system.nodes, current_system.edges)
    
    # Run simulation with given traffic growth factor
    simulated_graph = simulator.simulate_traffic(config)
    
    # Update global state with simulated results
    current_system = simulated_graph
    
    return current_system

@app.get("/api/risk-score")
def get_risk_score():
    score = analyzer.calculate_risk_score(simulator.graph)
    return {"risk_score": score}

@app.get("/api/analysis", response_model=RootCauseAnalysis)
async def get_root_cause_analysis():
    """Get comprehensive root cause analysis with AI insights"""
    try:
        analysis = analyzer.perform_root_cause_analysis(simulator.graph)
        
        # Track this snapshot in historical data
        bottlenecks = analyzer.find_bottlenecks(simulator.graph)
        risk_score = analyzer.calculate_risk_score(simulator.graph)
        historical_tracker.add_snapshot(simulator.graph, risk_score, bottlenecks)
        
        # Get system overview data for AI context
        system_data = {
            "total_services": simulator.graph.number_of_nodes(),
            "critical_count": len([n for n, d in simulator.graph.nodes(data=True) 
                                 if d.get('status') == 'critical']),
            "service_types": list(set(d.get('type', 'unknown') 
                                    for _, d in simulator.graph.nodes(data=True)))
        }
        
        # Get AI insights and recommendations (with error handling)
        try:
            ai_insights = await ai_manager.get_ai_insights(analysis, system_data)
            analysis.ai_insights = ai_insights
            
            ai_recommendations = await ai_manager.get_ai_recommendations(analysis, system_data)
            if ai_recommendations:
                analysis.recommended_actions = ai_recommendations
        except Exception as e:
            print(f"AI processing error: {e}")
            # Continue without AI insights
        
        # Evaluate for auto-remediation (with error handling)
        if auto_remediator.enabled:
            for node_id, node_data in simulator.graph.nodes(data=True):
                try:
                    remediation_actions = auto_remediator.evaluate_service(
                        node_id, node_data, analysis
                    )
                    # Auto-execute enabled actions
                    for action in remediation_actions:
                        if action.status == RemediationStatus.PENDING:
                            # Check if rule allows auto-approval
                            rule = next((r for r in auto_remediator.rules.values() 
                                       if r.action_type == action.action_type), None)
                            if rule and rule.auto_approve:
                                await auto_remediator.execute_action(action)
                except Exception as e:
                    print(f"Auto-remediation error for {node_id}: {e}")
                    # Continue with other services
        
        return analysis
    except Exception as e:
        import traceback
        print(f"ERROR in /api/analysis: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bottlenecks")
def get_bottlenecks():
    """Get detailed bottleneck analysis"""
    bottlenecks = analyzer.find_bottlenecks(simulator.graph)
    return {"bottlenecks": bottlenecks[:10]}  # Top 10

@app.post("/api/ai/switch-provider")
def switch_ai_provider(provider: str):
    """Switch AI provider (openai, gemini, claude, mock)"""
    success = ai_manager.switch_provider(provider)
    if success:
        return {"message": f"Switched to {provider} provider", "provider": provider}
    else:
        available = ai_manager.get_available_providers()
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid provider. Available: {available}"
        )

@app.get("/api/ai/providers")
def get_ai_providers():
    """Get available AI providers"""
    return {
        "providers": ai_manager.get_available_providers(),
        "current": ai_manager.current_provider.provider_name
    }

@app.post("/api/reset")
def reset_system():
    """Reset system to sample mock data (for demo/testing purposes)"""
    global current_system
    current_system = generate_mock_system()
    simulator.build_graph(current_system.nodes, current_system.edges)
    return current_system

@app.post("/api/clear")
def clear_system():
    """Clear all nodes and edges (start fresh)"""
    global current_system
    current_system = SystemGraph(nodes=[], edges=[])
    simulator.build_graph(current_system.nodes, current_system.edges)
    return {"message": "System cleared", "nodes": 0, "edges": 0}

# ============================================================================
# USER INPUT / CUSTOM SYSTEM GRAPH ENDPOINTS
# ============================================================================

@app.post("/api/system/custom", response_model=SystemGraph)
def upload_custom_system(system: SystemGraph):
    """Upload a complete custom system graph to analyze"""
    global current_system
    
    # Validate that all edges reference existing nodes
    node_ids = {node.id for node in system.nodes}
    for edge in system.edges:
        if edge.source not in node_ids:
            raise HTTPException(
                status_code=400, 
                detail=f"Edge source '{edge.source}' not found in nodes"
            )
        if edge.target not in node_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Edge target '{edge.target}' not found in nodes"
            )
    
    # Update the global system state
    current_system = system
    simulator.build_graph(current_system.nodes, current_system.edges)
    
    return current_system

@app.post("/api/system/nodes", response_model=ServiceNode)
def add_node(node: ServiceNode):
    """Add a new node to the current system"""
    global current_system
    
    # Check if node already exists
    if any(n.id == node.id for n in current_system.nodes):
        raise HTTPException(
            status_code=400,
            detail=f"Node with id '{node.id}' already exists"
        )
    
    current_system.nodes.append(node)
    simulator.build_graph(current_system.nodes, current_system.edges)
    
    return node

@app.put("/api/system/nodes/{node_id}", response_model=ServiceNode)
def update_node(node_id: str, updated_node: ServiceNode):
    """Update an existing node in the system"""
    global current_system
    
    # Find and update the node
    for i, node in enumerate(current_system.nodes):
        if node.id == node_id:
            # Preserve the node_id even if the update tries to change it
            updated_node.id = node_id
            current_system.nodes[i] = updated_node
            simulator.build_graph(current_system.nodes, current_system.edges)
            return updated_node
    
    raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")

@app.delete("/api/system/nodes/{node_id}")
def delete_node(node_id: str):
    """Delete a node and all its associated edges from the system"""
    global current_system
    
    # Find and remove the node
    initial_count = len(current_system.nodes)
    current_system.nodes = [n for n in current_system.nodes if n.id != node_id]
    
    if len(current_system.nodes) == initial_count:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    
    # Remove all edges connected to this node
    current_system.edges = [
        e for e in current_system.edges 
        if e.source != node_id and e.target != node_id
    ]
    
    simulator.build_graph(current_system.nodes, current_system.edges)
    
    return {"message": f"Node '{node_id}' deleted successfully"}

@app.post("/api/system/edges", response_model=DependencyEdge)
def add_edge(edge: DependencyEdge):
    """Add a new edge (dependency) to the current system"""
    global current_system
    
    # Validate that both nodes exist
    node_ids = {node.id for node in current_system.nodes}
    if edge.source not in node_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Source node '{edge.source}' not found"
        )
    if edge.target not in node_ids:
        raise HTTPException(
            status_code=404,
            detail=f"Target node '{edge.target}' not found"
        )
    
    # Check if edge already exists
    if any(e.source == edge.source and e.target == edge.target 
           for e in current_system.edges):
        raise HTTPException(
            status_code=400,
            detail=f"Edge from '{edge.source}' to '{edge.target}' already exists"
        )
    
    current_system.edges.append(edge)
    simulator.build_graph(current_system.nodes, current_system.edges)
    
    return edge

@app.delete("/api/system/edges")
def delete_edge(source: str, target: str):
    """Delete an edge (dependency) from the system"""
    global current_system
    
    # Find and remove the edge
    initial_count = len(current_system.edges)
    current_system.edges = [
        e for e in current_system.edges 
        if not (e.source == source and e.target == target)
    ]
    
    if len(current_system.edges) == initial_count:
        raise HTTPException(
            status_code=404,
            detail=f"Edge from '{source}' to '{target}' not found"
        )
    
    simulator.build_graph(current_system.nodes, current_system.edges)
    
    return {"message": f"Edge from '{source}' to '{target}' deleted successfully"}

@app.get("/api/system/export", response_model=SystemGraph)
def export_system():
    """Export the current system graph as JSON (for saving/backup)"""
    return current_system

# ============================================================================
# HISTORICAL TRACKING ENDPOINTS
# ============================================================================

@app.get("/api/historical/trends")
def get_system_trends(time_window_minutes: int = 60):
    """Get trend analysis for all system metrics"""
    trends = historical_tracker.get_all_trends(time_window_minutes)
    return {
        "trends": {name: {
            "metric_name": trend.metric_name,
            "current_value": trend.current_value,
            "avg_last_hour": trend.avg_last_hour,
            "avg_last_day": trend.avg_last_day,
            "trend_direction": trend.trend_direction,
            "change_rate": trend.change_rate,
            "severity": trend.severity
        } for name, trend in trends.items()},
        "time_window_minutes": time_window_minutes
    }

@app.get("/api/historical/service/{service_id}")
def get_service_history(service_id: str, minutes: int = 60):
    """Get historical performance data for a specific service"""
    history = historical_tracker.get_service_history(service_id, minutes)
    return history

@app.get("/api/historical/snapshots")
def get_historical_snapshots(minutes: int = 60):
    """Get system snapshots from the last N minutes"""
    snapshots = historical_tracker.export_history(minutes)
    return {
        "snapshots": snapshots,
        "count": len(snapshots),
        "time_range_minutes": minutes
    }

@app.get("/api/historical/statistics")
def get_historical_statistics():
    """Get statistics about stored historical data"""
    return historical_tracker.get_statistics()

# ============================================================================
# PREDICTIVE ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/predictions/all")
def get_all_predictions():
    """Get comprehensive predictions for all services"""
    predictions = predictive_analyzer.get_all_predictions(
        simulator.graph, 
        historical_tracker
    )
    return predictions

@app.get("/api/predictions/failures")
def get_failure_predictions():
    """Get predictions of potential service failures"""
    predictions = predictive_analyzer.get_all_predictions(
        simulator.graph,
        historical_tracker
    )
    return {
        "failure_predictions": predictions.get('failure_predictions', []),
        "total_at_risk": predictions.get('total_at_risk_services', 0)
    }

@app.get("/api/predictions/cascades")
def get_cascade_predictions():
    """Get predictions of potential cascade failures"""
    predictions = predictive_analyzer.get_all_predictions(
        simulator.graph,
        historical_tracker
    )
    return {
        "cascade_predictions": predictions.get('cascade_predictions', []),
        "prediction_timestamp": predictions.get('prediction_timestamp')
    }

# ============================================================================
# AUTO-REMEDIATION ENDPOINTS
# ============================================================================

@app.get("/api/remediation/actions")
def get_remediation_actions(hours: int = 24):
    """Get remediation action history"""
    history = auto_remediator.get_action_history(hours)
    return {
        "actions": history,
        "count": len(history)
    }

@app.get("/api/remediation/pending")
def get_pending_remediations():
    """Get pending remediation actions requiring approval"""
    pending = auto_remediator.get_pending_actions()
    return {
        "pending_actions": [action.to_dict() for action in pending],
        "count": len(pending)
    }

@app.get("/api/remediation/active")
def get_active_remediations():
    """Get currently executing remediation actions"""
    active = auto_remediator.get_active_actions()
    return {
        "active_actions": [action.to_dict() for action in active],
        "count": len(active)
    }

@app.post("/api/remediation/execute/{action_id}")
async def approve_and_execute_remediation(action_id: str):
    """Approve and execute a pending remediation action"""
    # Find the action
    action = next((a for a in auto_remediator.actions_history 
                    if a.action_id == action_id), None)
    
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    if action.status != RemediationStatus.PENDING:
        raise HTTPException(
            status_code=400, 
            detail=f"Action is already {action.status.value}"
        )
    
    # Execute the action
    result = await auto_remediator.execute_action(action)
    return result.to_dict()

@app.get("/api/remediation/rules")
def get_remediation_rules():
    """Get all auto-remediation rules"""
    rules = auto_remediator.get_rules()
    return {
        "rules": rules,
        "count": len(rules)
    }

@app.post("/api/remediation/rules/{rule_id}/toggle")
def toggle_remediation_rule(rule_id: str, enabled: bool):
    """Enable or disable a remediation rule"""
    success = auto_remediator.toggle_rule(rule_id, enabled)
    if success:
        return {"message": f"Rule {rule_id} {'enabled' if enabled else 'disabled'}"}
    else:
        raise HTTPException(status_code=404, detail="Rule not found")

@app.get("/api/remediation/statistics")
def get_remediation_statistics():
    """Get remediation system statistics"""
    stats = auto_remediator.get_statistics()
    return stats

@app.post("/api/remediation/toggle")
def toggle_auto_remediation(enabled: bool):
    """Enable or disable the entire auto-remediation system"""
    auto_remediator.enabled = enabled
    return {
        "enabled": auto_remediator.enabled,
        "message": f"Auto-remediation {'enabled' if enabled else 'disabled'}"
    }

@app.post("/api/remediation/dry-run")
def toggle_dry_run_mode(dry_run: bool):
    """Enable or disable dry-run mode (simulate without executing)"""
    auto_remediator.dry_run = dry_run
    return {
        "dry_run": auto_remediator.dry_run,
        "message": f"Dry-run mode {'enabled' if dry_run else 'disabled'}"
    }
