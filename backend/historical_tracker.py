"""
Historical Data Tracking System
Stores and analyzes system performance over time
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import deque
import statistics
from dataclasses import dataclass, asdict
import json

@dataclass
class MetricSnapshot:
    timestamp: datetime
    risk_score: float
    cpu_usage: Dict[str, float]  # service_id -> cpu%
    memory_usage: Dict[str, float]  # service_id -> memory%
    error_rates: Dict[str, float]  # service_id -> error%
    latencies: Dict[str, float]  # service_id -> latency ms
    bottleneck_count: int
    critical_services: List[str]
    
    def to_dict(self):
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class TrendAnalysis:
    metric_name: str
    current_value: float
    avg_last_hour: float
    avg_last_day: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    change_rate: float  # percentage change per hour
    severity: str  # "normal", "warning", "critical"

class HistoricalTracker:
    """Track system metrics over time for trend analysis"""
    
    def __init__(self, max_history_hours: int = 48):
        self.max_history_hours = max_history_hours
        self.max_snapshots = max_history_hours * 60  # Store up to 48 hours at 1/min
        self.snapshots: deque = deque(maxlen=self.max_snapshots)
        self.metrics_history: Dict[str, deque] = {
            'risk_score': deque(maxlen=1000),
            'cpu_usage': deque(maxlen=1000),
            'memory_usage': deque(maxlen=1000),
            'error_rate': deque(maxlen=1000),
            'latency': deque(maxlen=1000)
        }
    
    def add_snapshot(self, graph, risk_score: float, bottlenecks: List[Dict]):
        """Add a new system snapshot"""
        cpu_data = {}
        memory_data = {}
        error_data = {}
        latency_data = {}
        critical_services = []
        
        for node_id, node_data in graph.nodes(data=True):
            cpu_data[node_id] = node_data.get('cpu_usage', 0)
            memory_data[node_id] = node_data.get('memory_usage', 0)
            error_data[node_id] = node_data.get('error_rate', 0)
            latency_data[node_id] = node_data.get('latency', 0)
            
            if node_data.get('status') == 'critical':
                critical_services.append(node_id)
        
        snapshot = MetricSnapshot(
            timestamp=datetime.now(),
            risk_score=risk_score,
            cpu_usage=cpu_data,
            memory_usage=memory_data,
            error_rates=error_data,
            latencies=latency_data,
            bottleneck_count=len(bottlenecks),
            critical_services=critical_services
        )
        
        self.snapshots.append(snapshot)
        
        # Update individual metric histories for faster querying
        self.metrics_history['risk_score'].append((datetime.now(), risk_score))
        
        if cpu_data:
            avg_cpu = statistics.mean(cpu_data.values())
            self.metrics_history['cpu_usage'].append((datetime.now(), avg_cpu))
        
        if memory_data:
            avg_memory = statistics.mean(memory_data.values())
            self.metrics_history['memory_usage'].append((datetime.now(), avg_memory))
        
        if error_data:
            avg_error = statistics.mean(error_data.values())
            self.metrics_history['error_rate'].append((datetime.now(), avg_error))
        
        if latency_data:
            avg_latency = statistics.mean(latency_data.values())
            self.metrics_history['latency'].append((datetime.now(), avg_latency))
    
    def get_recent_snapshots(self, minutes: int = 60) -> List[MetricSnapshot]:
        """Get snapshots from the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [s for s in self.snapshots if s.timestamp >= cutoff_time]
    
    def get_metric_trend(self, metric_name: str, time_window_minutes: int = 60) -> Optional[TrendAnalysis]:
        """Analyze trend for a specific metric"""
        if metric_name not in self.metrics_history:
            return None
        
        history = list(self.metrics_history[metric_name])
        if len(history) < 2:
            return None
        
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)
        recent_data = [(t, v) for t, v in history if t >= cutoff_time]
        
        if len(recent_data) < 2:
            return None
        
        current_value = recent_data[-1][1]
        
        # Calculate averages for different time windows
        last_hour = datetime.now() - timedelta(hours=1)
        last_day = datetime.now() - timedelta(days=1)
        
        hour_data = [v for t, v in history if t >= last_hour]
        day_data = [v for t, v in history if t >= last_day]
        
        avg_last_hour = statistics.mean(hour_data) if hour_data else current_value
        avg_last_day = statistics.mean(day_data) if day_data else current_value
        
        # Calculate trend direction and change rate
        if len(recent_data) >= 5:
            # Use linear regression or simple slope calculation
            values = [v for _, v in recent_data[-10:]]
            slope = (values[-1] - values[0]) / len(values)
            change_rate = (slope / values[0] * 100) if values[0] != 0 else 0
            
            if abs(change_rate) < 5:
                trend_direction = "stable"
            elif change_rate > 0:
                trend_direction = "increasing"
            else:
                trend_direction = "decreasing"
        else:
            trend_direction = "stable"
            change_rate = 0
        
        # Determine severity based on metric type and trend
        severity = "normal"
        if metric_name == 'risk_score':
            if current_value > 80:
                severity = "critical"
            elif current_value > 60:
                severity = "warning"
        elif metric_name in ['cpu_usage', 'memory_usage']:
            if current_value > 90:
                severity = "critical"
            elif current_value > 75:
                severity = "warning"
        elif metric_name == 'error_rate':
            if current_value > 10:
                severity = "critical"
            elif current_value > 5:
                severity = "warning"
        
        return TrendAnalysis(
            metric_name=metric_name,
            current_value=current_value,
            avg_last_hour=avg_last_hour,
            avg_last_day=avg_last_day,
            trend_direction=trend_direction,
            change_rate=change_rate,
            severity=severity
        )
    
    def get_all_trends(self, time_window_minutes: int = 60) -> Dict[str, TrendAnalysis]:
        """Get trend analysis for all metrics"""
        trends = {}
        for metric_name in self.metrics_history.keys():
            trend = self.get_metric_trend(metric_name, time_window_minutes)
            if trend:
                trends[metric_name] = trend
        return trends
    
    def get_service_history(self, service_id: str, minutes: int = 60) -> Dict[str, List]:
        """Get historical data for a specific service"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_snapshots = [s for s in self.snapshots if s.timestamp >= cutoff_time]
        
        cpu_history = []
        memory_history = []
        error_history = []
        latency_history = []
        
        for snapshot in recent_snapshots:
            timestamp = snapshot.timestamp.isoformat()
            if service_id in snapshot.cpu_usage:
                cpu_history.append({
                    'timestamp': timestamp,
                    'value': snapshot.cpu_usage[service_id]
                })
            if service_id in snapshot.memory_usage:
                memory_history.append({
                    'timestamp': timestamp,
                    'value': snapshot.memory_usage[service_id]
                })
            if service_id in snapshot.error_rates:
                error_history.append({
                    'timestamp': timestamp,
                    'value': snapshot.error_rates[service_id]
                })
            if service_id in snapshot.latencies:
                latency_history.append({
                    'timestamp': timestamp,
                    'value': snapshot.latencies[service_id]
                })
        
        return {
            'service_id': service_id,
            'cpu_history': cpu_history,
            'memory_history': memory_history,
            'error_history': error_history,
            'latency_history': latency_history
        }
    
    def export_history(self, minutes: int = 60) -> List[Dict]:
        """Export historical data as JSON-serializable format"""
        recent_snapshots = self.get_recent_snapshots(minutes)
        return [snapshot.to_dict() for snapshot in recent_snapshots]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored historical data"""
        return {
            'total_snapshots': len(self.snapshots),
            'oldest_snapshot': self.snapshots[0].timestamp.isoformat() if self.snapshots else None,
            'newest_snapshot': self.snapshots[-1].timestamp.isoformat() if self.snapshots else None,
            'coverage_hours': len(self.snapshots) / 60 if self.snapshots else 0,
            'metrics_tracked': list(self.metrics_history.keys())
        }

# Global historical tracker instance
historical_tracker = HistoricalTracker()
