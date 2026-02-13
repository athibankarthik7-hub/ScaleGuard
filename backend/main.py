from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import networkx as nx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from models import SystemGraph, SimulationConfig, RootCauseAnalysis
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
    global current_system
    current_system = generate_mock_system()
    simulator.build_graph(current_system.nodes, current_system.edges)
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
