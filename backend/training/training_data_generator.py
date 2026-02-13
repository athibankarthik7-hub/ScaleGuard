#!/usr/bin/env python3
"""
Training Data Generator for ScaleGuard AI Model
Generates realistic system performance scenarios and expert DevOps responses
"""

import json
import random
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from enum import Enum

class ServiceType(Enum):
    DATABASE = "database"
    API = "api"
    CACHE = "cache"
    QUEUE = "queue"
    EXTERNAL = "external"
    COMPUTE = "compute"

class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class TimeContext(Enum):
    PEAK_HOURS = "peak_hours"
    MAINTENANCE = "maintenance"
    NORMAL = "normal"

@dataclass
class Bottleneck:
    name: str
    type: str
    cpu_usage: float
    memory_usage: float
    risk_score: float
    reason: str
    centrality: float = 0.0

@dataclass
class SystemState:
    risk_score: float
    total_services: int
    critical_count: int
    service_types: List[str]
    time_context: str
    business_impact: str

@dataclass
class TrainingExample:
    input_data: Dict[str, Any]
    expected_analysis: str
    expected_recommendations: List[str]

class TrainingDataGenerator:
    
    def __init__(self):
        self.service_names = {
            ServiceType.DATABASE: ["Primary DB", "User DB", "Analytics DB", "Cache DB", "Replica DB"],
            ServiceType.API: ["User API", "Payment API", "Auth Service", "Profile API", "Search API"],
            ServiceType.CACHE: ["Redis Cache", "Memcached", "Application Cache", "Session Cache", "CDN Cache"],
            ServiceType.QUEUE: ["Message Queue", "Event Bus", "Task Queue", "Notification Queue", "Log Queue"],
            ServiceType.EXTERNAL: ["Payment Gateway", "Email Service", "SMS Service", "Analytics Service", "CDN"],
            ServiceType.COMPUTE: ["Worker Nodes", "Batch Processor", "ML Pipeline", "Image Processing", "Video Encoder"]
        }
        
        self.cascading_services = [
            "Authentication Service", "User Profile API", "Payment Processing",
            "Order Management", "Inventory System", "Notification Service",
            "Analytics Pipeline", "Recommendation Engine", "Search Index",
            "Session Manager", "File Upload Service", "Email Service"
        ]

    def generate_bottleneck(self, service_type: ServiceType, severity: SeverityLevel) -> Bottleneck:
        """Generate a realistic bottleneck scenario"""
        name = random.choice(self.service_names[service_type])
        
        # Generate CPU and memory based on service type and severity
        if service_type == ServiceType.DATABASE:
            base_cpu = {"low": 50, "medium": 70, "high": 85, "critical": 95}[severity.value]
            base_memory = {"low": 60, "medium": 75, "high": 88, "critical": 95}[severity.value]
        elif service_type == ServiceType.API:
            base_cpu = {"low": 45, "medium": 65, "high": 80, "critical": 90}[severity.value]
            base_memory = {"low": 40, "medium": 60, "high": 75, "critical": 85}[severity.value]
        elif service_type == ServiceType.CACHE:
            base_cpu = {"low": 30, "medium": 45, "high": 65, "critical": 80}[severity.value]
            base_memory = {"low": 70, "medium": 85, "high": 92, "critical": 98}[severity.value]
        else:
            base_cpu = {"low": 40, "medium": 60, "high": 75, "critical": 88}[severity.value]
            base_memory = {"low": 50, "medium": 70, "high": 83, "critical": 90}[severity.value]
        
        # Add some randomness
        cpu_usage = min(100, base_cpu + random.uniform(-10, 15))
        memory_usage = min(100, base_memory + random.uniform(-15, 10))
        
        # Calculate risk score
        risk_score = (cpu_usage + memory_usage) / 2 + random.uniform(-5, 10)
        risk_score = max(0, min(100, risk_score))
        
        # Generate reason string
        reason_parts = []
        if cpu_usage > 80:
            reason_parts.append(f"CPU overload ({cpu_usage:.1f}%)")
        elif cpu_usage > 60:
            reason_parts.append(f"High CPU usage ({cpu_usage:.1f}%)")
            
        if memory_usage > 85:
            reason_parts.append(f"Memory critical ({memory_usage:.1f}%)")
        elif memory_usage > 70:
            reason_parts.append(f"Memory high ({memory_usage:.1f}%)")
            
        # Add service-specific issues
        if service_type == ServiceType.DATABASE:
            issues = ["Slow queries", "Lock contention", "High error rate", "Connection exhaustion"]
        elif service_type == ServiceType.API:
            issues = ["Response time spikes", "High error rate", "Thread exhaustion", "Memory leaks"]
        elif service_type == ServiceType.CACHE:
            issues = ["Cache misses", "Eviction pressure", "Hit rate decline"]
        else:
            issues = ["Performance degradation", "Resource contention", "Scaling issues"]
            
        if random.random() > 0.3:
            reason_parts.append(random.choice(issues))
        
        reason = "; ".join(reason_parts)
        centrality = random.uniform(0.1, 0.8)
        
        return Bottleneck(name, service_type.value, cpu_usage, memory_usage, risk_score, reason, centrality)

    def generate_analysis(self, system_state: SystemState, bottlenecks: List[Bottleneck], 
                         cascading_failures: List[str]) -> str:
        """Generate expert analysis text"""
        primary_bottleneck = bottlenecks[0]
        severity_emoji = {"low": "🔧", "medium": "⚠️", "high": "🚨", "critical": "🔥"}
        
        # Determine severity level from risk score
        if system_state.risk_score >= 90:
            level = "CRITICAL EMERGENCY"
            severity = "critical"
        elif system_state.risk_score >= 75:
            level = "HIGH RISK DETECTED" 
            severity = "high"
        elif system_state.risk_score >= 50:
            level = "MEDIUM RISK"
            severity = "medium"
        else:
            level = "OPTIMIZATION NEEDED"
            severity = "low"
            
        emoji = severity_emoji[severity]
        
        analysis = f"{emoji} **{level}** - System health score: {system_state.risk_score:.1f}/100\n\n"
        
        # Root cause analysis
        analysis += f"**Root Cause Analysis:**\n"
        analysis += f"Primary bottleneck: {primary_bottleneck.name} ({primary_bottleneck.type})\n"
        analysis += f"- {primary_bottleneck.reason}\n"
        analysis += f"- Centrality score: {primary_bottleneck.centrality:.2f} ({'critical path component' if primary_bottleneck.centrality > 0.5 else 'medium impact component'})\n\n"
        
        # Business impact
        analysis += f"**Business Impact:** {system_state.business_impact}\n\n"
        
        # Cascade analysis if applicable
        if cascading_failures:
            analysis += f"**Cascade Analysis:** {len(cascading_failures)} services affected: {', '.join(cascading_failures[:3])}\n\n"
        
        # Immediate actions based on bottleneck type and severity
        analysis += f"**Immediate Actions Required:**\n"
        if primary_bottleneck.type == "database":
            if severity in ["critical", "high"]:
                actions = [
                    "Scale database horizontally (add read replicas)",
                    "Optimize slow queries and add proper indexing", 
                    "Implement connection pooling optimization"
                ]
            else:
                actions = [
                    "Review database performance metrics",
                    "Optimize query patterns and indexing",
                    "Consider read replica for load distribution"
                ]
        elif primary_bottleneck.type == "api":
            if severity in ["critical", "high"]:
                actions = [
                    "Scale API instances horizontally",
                    "Implement circuit breakers for dependencies",
                    "Add caching layer for frequent requests"
                ]
            else:
                actions = [
                    "Review API performance bottlenecks",
                    "Optimize resource-intensive operations",
                    "Add monitoring for response times"
                ]
        else:
            actions = [
                f"Scale {primary_bottleneck.name} capacity immediately",
                f"Investigate {primary_bottleneck.type} service performance",
                "Implement monitoring and alerting"
            ]
        
        for i, action in enumerate(actions, 1):
            analysis += f"{i}. {action}\n"
        
        analysis += f"\n**Architecture Recommendations:**\n"
        analysis += f"- Implement observability stack (metrics, logs, traces)\n"
        if len(cascading_failures) > 2:
            analysis += f"- Consider event-driven architecture for loose coupling\n"
        analysis += f"- Set up automated scaling based on performance thresholds"
        
        return analysis

    def generate_recommendations(self, system_state: SystemState, bottlenecks: List[Bottleneck]) -> List[str]:
        """Generate actionable recommendations"""
        primary_bottleneck = bottlenecks[0]
        recommendations = []
        
        # Scale recommendation
        if primary_bottleneck.type == "database":
            recommendations.append(f"Scale {primary_bottleneck.name}: Add 2-3 read replicas immediately")
            recommendations.append(f"Optimize {primary_bottleneck.name}: Enable slow query logging and fix queries >100ms")
        elif primary_bottleneck.type == "api":
            recommendations.append(f"Scale {primary_bottleneck.name}: Deploy 2-3 additional instances behind load balancer")
            recommendations.append(f"Add caching layer: Redis for {primary_bottleneck.name} data (30min TTL)")
        elif primary_bottleneck.type == "cache":
            recommendations.append(f"Scale {primary_bottleneck.name}: Increase memory allocation by 50%")
            recommendations.append(f"Optimize eviction policy: Review LRU settings for better hit rates")
        else:
            recommendations.append(f"Scale {primary_bottleneck.name}: Increase capacity by 100%")
            recommendations.append(f"Optimize {primary_bottleneck.name}: Review configuration and resource allocation")
        
        # Add monitoring
        recommendations.append("Deploy APM monitoring (New Relic/DataDog) for real-time insights")
        
        # Add specific technical recommendations based on service type
        if primary_bottleneck.type == "database":
            recommendations.append("Implement Redis cache layer to reduce DB hits by 60-70%")
            recommendations.append("Review database connection pool settings - increase max connections to 200")
        elif primary_bottleneck.type == "api":
            recommendations.append("Implement circuit breakers for external service calls")
            recommendations.append("Set up auto-scaling triggers at 70% CPU threshold")
        else:
            recommendations.append(f"Implement health checks and automated recovery for {primary_bottleneck.name}")
            recommendations.append(f"Set up performance alerts for {primary_bottleneck.type} services")
        
        # Ensure exactly 6 recommendations
        while len(recommendations) < 6:
            recommendations.append("Review system architecture for additional optimization opportunities")
        
        return recommendations[:6]

    def generate_cascading_failures(self, primary_type: ServiceType, severity: SeverityLevel) -> List[str]:
        """Generate realistic cascading failure scenarios"""
        failure_count = {
            "low": random.choice([0, 1]), 
            "medium": random.choice([1, 2]),
            "high": random.choice([2, 3, 4]),
            "critical": random.choice([3, 4, 5, 6])
        }[severity.value]
        
        if failure_count == 0:
            return []
        
        # Services most likely to be affected by each type
        if primary_type == ServiceType.DATABASE:
            likely_affected = ["Authentication Service", "User Profile API", "Payment Processing", 
                             "Order Management", "Session Manager"]
        elif primary_type == ServiceType.API:
            likely_affected = ["Frontend Application", "Mobile App", "Analytics Pipeline",
                             "Notification Service", "Search Index"]
        elif primary_type == ServiceType.CACHE:
            likely_affected = ["User API", "Session Manager", "Recommendation Engine",
                             "Search API", "Profile API"]
        else:
            likely_affected = self.cascading_services
        
        return random.sample(likely_affected, min(failure_count, len(likely_affected)))

    def generate_business_impact(self, risk_score: float, time_context: TimeContext, 
                               cascading_count: int) -> str:
        """Generate business impact assessment"""
        if risk_score >= 90:
            if time_context == TimeContext.PEAK_HOURS:
                return "REVENUE AT RISK - Customer transactions failing, immediate escalation required"
            else:
                return "CRITICAL system failure - Major service disruption, customer impact severe"
        elif risk_score >= 75:
            if cascading_count > 3:
                return "HIGH business impact - Multiple services affected, SLA breach imminent"
            else:
                return "Significant performance degradation - Customer experience impacted"
        elif risk_score >= 50:
            return "Moderate business impact - Service quality reduced, proactive action needed"
        else:
            return "Minor performance impact - Optimization opportunity for better efficiency"

    def generate_training_example(self, service_type: ServiceType = None, 
                                severity: SeverityLevel = None) -> TrainingExample:
        """Generate a complete training example"""
        if service_type is None:
            service_type = random.choice(list(ServiceType))
        if severity is None:
            severity = random.choice(list(SeverityLevel))
        
        time_context = random.choice(list(TimeContext))
        
        # Generate primary bottleneck
        primary_bottleneck = self.generate_bottleneck(service_type, severity)
        bottlenecks = [primary_bottleneck]
        
        # Sometimes add secondary bottlenecks for complex scenarios
        if random.random() > 0.7 and severity.value in ["high", "critical"]:
            secondary_type = random.choice([t for t in ServiceType if t != service_type])
            secondary_severity = SeverityLevel.MEDIUM if severity == SeverityLevel.CRITICAL else SeverityLevel.LOW
            secondary_bottleneck = self.generate_bottleneck(secondary_type, secondary_severity) 
            bottlenecks.append(secondary_bottleneck)
        
        # Generate cascading failures
        cascading_failures = self.generate_cascading_failures(service_type, severity)
        
        # Calculate system metrics
        total_services = random.randint(8, 20)
        critical_count = len([b for b in bottlenecks if b.risk_score > 75])
        service_types = list(set([b.type for b in bottlenecks] + 
                                random.sample([t.value for t in ServiceType], 
                                            random.randint(2, 4))))
        
        # Calculate overall risk score
        risk_score = max([b.risk_score for b in bottlenecks])
        if cascading_failures:
            risk_score += len(cascading_failures) * 3  # Increase risk for cascades
        risk_score = min(100, risk_score)
        
        business_impact = self.generate_business_impact(risk_score, time_context, len(cascading_failures))
        
        system_state = SystemState(
            risk_score=risk_score,
            total_services=total_services,
            critical_count=critical_count,
            service_types=service_types,
            time_context=time_context.value,
            business_impact=business_impact
        )
        
        # Generate analysis and recommendations
        analysis = self.generate_analysis(system_state, bottlenecks, cascading_failures)
        recommendations = self.generate_recommendations(system_state, bottlenecks)
        
        # Build input data structure
        input_data = {
            "system_state": asdict(system_state),
            "bottlenecks": [asdict(b) for b in bottlenecks],
            "cascading_failures": cascading_failures
        }
        
        return TrainingExample(input_data, analysis, recommendations)

    def generate_dataset(self, num_examples: int = 100, output_file: str = "training_data.json") -> Dict:
        """Generate a complete training dataset"""
        examples = []
        
        # Ensure good distribution across service types and severities
        service_types = list(ServiceType)
        severities = list(SeverityLevel)
        
        for i in range(num_examples):
            # Cycle through combinations to ensure coverage
            service_type = service_types[i % len(service_types)]
            severity = severities[(i // len(service_types)) % len(severities)]
            
            example = self.generate_training_example(service_type, severity)
            examples.append(asdict(example))
            
            if (i + 1) % 10 == 0:
                print(f"Generated {i + 1}/{num_examples} examples...")
        
        dataset = {
            "metadata": {
                "total_examples": num_examples,
                "service_types": [t.value for t in ServiceType],
                "severities": [s.value for s in SeverityLevel],
                "generated_by": "ScaleGuard Training Data Generator"
            },
            "examples": examples
        }
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"Training dataset saved to {output_file}")
        return dataset

def main():
    """Main function to generate training data"""
    generator = TrainingDataGenerator()
    
    # Generate different dataset sizes
    print("Generating ScaleGuard AI Training Data...")
    
    # Small dataset for testing
    generator.generate_dataset(50, "training_data_small.json")
    
    # Medium dataset for development 
    generator.generate_dataset(500, "training_data_medium.json")
    
    # Large dataset for production training
    generator.generate_dataset(2000, "training_data_large.json")
    
    # Generate example for demonstration
    example = generator.generate_training_example(ServiceType.DATABASE, SeverityLevel.CRITICAL)
    
    print("\n" + "="*80)
    print("EXAMPLE TRAINING DATA")
    print("="*80)
    print("\nINPUT DATA:")
    print(json.dumps(example.input_data, indent=2))
    print("\nEXPECTED ANALYSIS:")
    print(example.expected_analysis)
    print("\nEXPECTED RECOMMENDATIONS:")
    for i, rec in enumerate(example.expected_recommendations, 1):
        print(f"{i}. {rec}")

if __name__ == "__main__":
    main()