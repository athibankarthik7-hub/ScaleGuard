"""
Auto-Remediation System
Automatically fixes common infrastructure issues based on detection and analysis
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

class RemediationStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class RemediationType(Enum):
    SCALE_HORIZONTAL = "scale_horizontal"
    SCALE_VERTICAL = "scale_vertical"
    RESTART_SERVICE = "restart_service"
    CIRCUIT_BREAKER = "circuit_breaker"
    RATE_LIMIT = "rate_limit"
    CACHE_CLEAR = "cache_clear"
    TRAFFIC_REDIRECT = "traffic_redirect"
    ROLLBACK_DEPLOYMENT = "rollback_deployment"

@dataclass
class RemediationAction:
    action_id: str
    service_id: str
    action_type: RemediationType
    reason: str
    triggered_by: str  # "manual", "auto", "prediction"
    status: RemediationStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parameters: Dict[str, Any] = None
    result: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self):
        data = {
            'action_id': self.action_id,
            'service_id': self.service_id,
            'action_type': self.action_type.value,
            'reason': self.reason,
            'triggered_by': self.triggered_by,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'parameters': self.parameters or {},
            'result': self.result,
            'error': self.error
        }
        return data

@dataclass
class RemediationRule:
    rule_id: str
    name: str
    condition: str  # Description of when to trigger
    action_type: RemediationType
    enabled: bool
    auto_approve: bool  # If True, execute without confirmation
    cooldown_minutes: int  # Minimum time between executions
    parameters: Dict[str, Any]
    last_executed: Optional[datetime] = None

class AutoRemediator:
    """Automatically remediate common infrastructure issues"""
    
    def __init__(self):
        self.actions_history: List[RemediationAction] = []
        self.rules: Dict[str, RemediationRule] = self._initialize_default_rules()
        self.enabled = True
        self.dry_run = False  # If True, simulate but don't execute
    
    def _initialize_default_rules(self) -> Dict[str, RemediationRule]:
        """Initialize default auto-remediation rules"""
        rules = {}
        
        # Rule 1: Scale on high CPU
        rules['cpu_scale'] = RemediationRule(
            rule_id='cpu_scale',
            name='Auto-scale on high CPU',
            condition='CPU usage > 85% for 5 minutes',
            action_type=RemediationType.SCALE_HORIZONTAL,
            enabled=True,
            auto_approve=True,
            cooldown_minutes=10,
            parameters={'scale_factor': 2, 'max_instances': 10}
        )
        
        # Rule 2: Restart on memory leak
        rules['memory_restart'] = RemediationRule(
            rule_id='memory_restart',
            name='Restart service on memory leak',
            condition='Memory usage > 95% and trending up',
            action_type=RemediationType.RESTART_SERVICE,
            enabled=True,
            auto_approve=False,  # Requires manual approval
            cooldown_minutes=30,
            parameters={'grace_period_seconds': 30}
        )
        
        # Rule 3: Enable circuit breaker on high errors
        rules['error_circuit_breaker'] = RemediationRule(
            rule_id='error_circuit_breaker',
            name='Enable circuit breaker on high error rate',
            condition='Error rate > 15%',
            action_type=RemediationType.CIRCUIT_BREAKER,
            enabled=True,
            auto_approve=True,
            cooldown_minutes=15,
            parameters={'failure_threshold': 10, 'timeout_seconds': 60}
        )
        
        # Rule 4: Rate limiting on overload
        rules['overload_rate_limit'] = RemediationRule(
            rule_id='overload_rate_limit',
            name='Apply rate limiting on overload',
            condition='Service in critical state with high traffic',
            action_type=RemediationType.RATE_LIMIT,
            enabled=True,
            auto_approve=True,
            cooldown_minutes=20,
            parameters={'max_requests_per_second': 100}
        )
        
        # Rule 5: Clear cache on anomaly
        rules['cache_clear'] = RemediationRule(
            rule_id='cache_clear',
            name='Clear cache on performance anomaly',
            condition='Latency > 1000ms and cache service affected',
            action_type=RemediationType.CACHE_CLEAR,
            enabled=True,
            auto_approve=True,
            cooldown_minutes=30,
            parameters={'cache_keys': ['*']}
        )
        
        return rules
    
    def evaluate_service(self, service_id: str, service_data: Dict, 
                        analysis: Any) -> List[RemediationAction]:
        """Evaluate a service and determine if remediation is needed"""
        if not self.enabled:
            return []
        
        recommended_actions = []
        cpu_usage = service_data.get('cpu_usage', 0)
        memory_usage = service_data.get('memory_usage', 0)
        error_rate = service_data.get('error_rate', 0)
        status = service_data.get('status', 'healthy')
        service_type = service_data.get('type', 'service')
        
        # Check CPU scaling rule
        if cpu_usage > 85 and status in ['critical', 'warning']:
            rule = self.rules.get('cpu_scale')
            if rule and rule.enabled and self._check_cooldown(rule):
                action = self._create_action(
                    service_id, 
                    RemediationType.SCALE_HORIZONTAL,
                    f"CPU usage at {cpu_usage:.1f}% exceeds threshold",
                    "auto",
                    rule.parameters
                )
                recommended_actions.append(action)
        
        # Check memory restart rule
        if memory_usage > 95:
            rule = self.rules.get('memory_restart')
            if rule and rule.enabled and self._check_cooldown(rule):
                action = self._create_action(
                    service_id,
                    RemediationType.RESTART_SERVICE,
                    f"Memory usage at {memory_usage:.1f}% indicates possible leak",
                    "auto",
                    rule.parameters
                )
                action.status = RemediationStatus.PENDING  # Requires approval
                recommended_actions.append(action)
        
        # Check error rate circuit breaker
        if error_rate > 15:
            rule = self.rules.get('error_circuit_breaker')
            if rule and rule.enabled and self._check_cooldown(rule):
                action = self._create_action(
                    service_id,
                    RemediationType.CIRCUIT_BREAKER,
                    f"Error rate at {error_rate:.1f}% requires circuit breaker",
                    "auto",
                    rule.parameters
                )
                recommended_actions.append(action)
        
        # Check rate limiting for overload
        if status == 'critical' and cpu_usage > 90:
            rule = self.rules.get('overload_rate_limit')
            if rule and rule.enabled and self._check_cooldown(rule):
                action = self._create_action(
                    service_id,
                    RemediationType.RATE_LIMIT,
                    f"Service overloaded - applying rate limiting",
                    "auto",
                    rule.parameters
                )
                recommended_actions.append(action)
        
        # Check cache clearing for cache services with high latency
        if service_type == 'cache' and service_data.get('latency', 0) > 1000:
            rule = self.rules.get('cache_clear')
            if rule and rule.enabled and self._check_cooldown(rule):
                action = self._create_action(
                    service_id,
                    RemediationType.CACHE_CLEAR,
                    f"High latency detected - clearing cache",
                    "auto",
                    rule.parameters
                )
                recommended_actions.append(action)
        
        return recommended_actions
    
    def _create_action(self, service_id: str, action_type: RemediationType,
                      reason: str, triggered_by: str, parameters: Dict) -> RemediationAction:
        """Create a new remediation action"""
        action = RemediationAction(
            action_id=f"{service_id}_{action_type.value}_{datetime.now().timestamp()}",
            service_id=service_id,
            action_type=action_type,
            reason=reason,
            triggered_by=triggered_by,
            status=RemediationStatus.PENDING,
            created_at=datetime.now(),
            parameters=parameters
        )
        return action
    
    def _check_cooldown(self, rule: RemediationRule) -> bool:
        """Check if enough time has passed since last execution"""
        if rule.last_executed is None:
            return True
        
        time_since_last = datetime.now() - rule.last_executed
        return time_since_last.total_seconds() >= (rule.cooldown_minutes * 60)
    
    async def execute_action(self, action: RemediationAction) -> RemediationAction:
        """Execute a remediation action (simulated for prototype)"""
        action.status = RemediationStatus.IN_PROGRESS
        action.started_at = datetime.now()
        
        try:
            # Simulate execution time
            await asyncio.sleep(1)
            
            if self.dry_run:
                action.result = f"[DRY RUN] Would execute {action.action_type.value} on {action.service_id}"
            else:
                # Simulate actual remediation
                result = await self._execute_remediation(action)
                action.result = result
            
            action.status = RemediationStatus.COMPLETED
            action.completed_at = datetime.now()
            
            # Update rule's last executed time
            for rule in self.rules.values():
                if rule.action_type == action.action_type:
                    rule.last_executed = datetime.now()
                    break
            
        except Exception as e:
            action.status = RemediationStatus.FAILED
            action.error = str(e)
            action.completed_at = datetime.now()
        
        self.actions_history.append(action)
        return action
    
    async def _execute_remediation(self, action: RemediationAction) -> str:
        """Simulate actual remediation execution"""
        action_type = action.action_type
        service_id = action.service_id
        params = action.parameters or {}
        
        if action_type == RemediationType.SCALE_HORIZONTAL:
            scale_factor = params.get('scale_factor', 2)
            return f"Successfully scaled {service_id} horizontally by {scale_factor}x. Added {scale_factor} new instances."
        
        elif action_type == RemediationType.RESTART_SERVICE:
            grace_period = params.get('grace_period_seconds', 30)
            return f"Successfully restarted {service_id} with {grace_period}s grace period. Service is healthy."
        
        elif action_type == RemediationType.CIRCUIT_BREAKER:
            threshold = params.get('failure_threshold', 10)
            return f"Enabled circuit breaker on {service_id} with failure threshold: {threshold}. Protecting downstream services."
        
        elif action_type == RemediationType.RATE_LIMIT:
            max_rps = params.get('max_requests_per_second', 100)
            return f"Applied rate limiting to {service_id}: {max_rps} req/s. Load reduced by 40%."
        
        elif action_type == RemediationType.CACHE_CLEAR:
            return f"Cleared cache on {service_id}. Cache hit rate will rebuild. Latency improved by 60%."
        
        elif action_type == RemediationType.SCALE_VERTICAL:
            return f"Scaled {service_id} vertically. Increased CPU and memory allocation by 50%."
        
        elif action_type == RemediationType.TRAFFIC_REDIRECT:
            return f"Redirected traffic from {service_id} to healthy replicas. Load balanced across 3 instances."
        
        return f"Executed {action_type.value} on {service_id}"
    
    def get_pending_actions(self) -> List[RemediationAction]:
        """Get all pending actions requiring approval"""
        return [action for action in self.actions_history 
                if action.status == RemediationStatus.PENDING]
    
    def get_active_actions(self) -> List[RemediationAction]:
        """Get all currently executing actions"""
        return [action for action in self.actions_history 
                if action.status == RemediationStatus.IN_PROGRESS]
    
    def get_action_history(self, hours: int = 24) -> List[Dict]:
        """Get remediation history for the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_actions = [action for action in self.actions_history 
                         if action.created_at >= cutoff]
        return [action.to_dict() for action in recent_actions]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get remediation statistics"""
        total_actions = len(self.actions_history)
        completed = len([a for a in self.actions_history if a.status == RemediationStatus.COMPLETED])
        failed = len([a for a in self.actions_history if a.status == RemediationStatus.FAILED])
        pending = len([a for a in self.actions_history if a.status == RemediationStatus.PENDING])
        
        # Group by action type
        actions_by_type = {}
        for action in self.actions_history:
            action_type = action.action_type.value
            actions_by_type[action_type] = actions_by_type.get(action_type, 0) + 1
        
        return {
            'total_actions': total_actions,
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'success_rate': (completed / total_actions * 100) if total_actions > 0 else 0,
            'actions_by_type': actions_by_type,
            'enabled': self.enabled,
            'dry_run_mode': self.dry_run,
            'active_rules': len([r for r in self.rules.values() if r.enabled])
        }
    
    def toggle_rule(self, rule_id: str, enabled: bool) -> bool:
        """Enable or disable a remediation rule"""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = enabled
            return True
        return False
    
    def get_rules(self) -> List[Dict]:
        """Get all remediation rules"""
        return [
            {
                'rule_id': rule.rule_id,
                'name': rule.name,
                'condition': rule.condition,
                'action_type': rule.action_type.value,
                'enabled': rule.enabled,
                'auto_approve': rule.auto_approve,
                'cooldown_minutes': rule.cooldown_minutes,
                'last_executed': rule.last_executed.isoformat() if rule.last_executed else None
            }
            for rule in self.rules.values()
        ]

# Global auto-remediator instance
auto_remediator = AutoRemediator()
