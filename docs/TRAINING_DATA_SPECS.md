# ScaleGuard AI Training Data Specifications

## Overview

To train your AI model for ScaleGuard, you need training data that maps **system performance inputs** to **expert DevOps analysis outputs**. Here are the complete specifications.

## 📊 Input Data Structure

### 1. **RootCauseAnalysis Object**

```python
{
    "primary_bottlenecks": [
        {
            "id": "primary-db",
            "name": "Primary DB", 
            "type": "database",  # database, api, cache, external, queue, etc.
            "risk_score": 85.0,   # 0-100
            "centrality": 0.25,   # 0-1 (network importance)
            "cpu_usage": 95.0,    # 0-100%
            "memory_usage": 87.5, # 0-100%
            "reason": "CPU overload (95.0%); Memory critical (87.5%); Database service (critical); High error rate (25.0%)"
        }
        # ... more bottlenecks
    ],
    "cascading_failures": [
        "User Authentication Service",
        "Payment Processing API", 
        "Order Management System"
    ],
    "recommended_actions": [],  # Will be populated by AI
    "risk_score": 85.0,  # Overall system risk 0-100
    "ai_insights": null  # Will be populated by AI
}
```

### 2. **System Data Context**

```python
{
    "total_services": 15,
    "critical_count": 3, 
    "service_types": ["api", "database", "cache", "queue", "external"]
}
```

## 🎯 Expected AI Outputs

### 1. **Analysis Insights** (String)

**Format**: Structured markdown with specific sections:

```markdown
**CRITICAL DETECTED** - System health score: 85.0/100

**Root Cause Analysis:**
Primary bottleneck: Primary DB (database)
- CPU overload (95.0%); Memory critical (87.5%)
- Centrality score: 0.25 (critical path component)

**Business Impact:** Immediate business impact

**Immediate Actions Required:**
1. Scale database horizontally (add read replicas)
2. Optimize slow queries and add proper indexing
3. Implement connection pooling optimization

**Architecture Recommendations:**
- Implement observability stack (metrics, logs, traces)
- Consider event-driven architecture for loose coupling
```

### 2. **Recommendations** (List of Strings)

**Format**: 6 specific, actionable recommendations:

```python
[
    "Scale Primary DB: Add 2-3 read replicas immediately",
    "Optimize Primary DB: Enable slow query logging and fix queries >100ms", 
    "Implement Redis cache layer to reduce DB hits by 60-70%",
    "Set up auto-scaling for API services with CPU threshold at 70%",
    "Deploy APM monitoring (New Relic/DataDog) for real-time insights",
    "Review database connection pool settings - increase max connections to 200"
]
```

## 📚 Training Dataset Structure

### Schema for Training Examples

```json
{
    "examples": [
        {
            "input": {
                "system_state": {
                    "risk_score": 85.0,
                    "total_services": 15,
                    "critical_count": 3,
                    "service_types": ["api", "database", "cache"],
                    "time_context": "peak_hours" // peak_hours, maintenance, normal
                },
                "bottlenecks": [
                    {
                        "name": "Primary DB",
                        "type": "database",
                        "cpu_usage": 95.0,
                        "memory_usage": 87.5,
                        "risk_score": 85.0,
                        "reason": "CPU overload; Memory critical; High error rate"
                    }
                ],
                "cascading_failures": ["Auth Service", "Payment API"],
                "business_context": "revenue_impact" // revenue_impact, performance_degradation, capacity_concerns, optimization
            },
            "expected_analysis": "**HIGH RISK DETECTED**...",
            "expected_recommendations": [
                "Scale Primary DB: Add read replicas immediately",
                "Optimize slow queries with proper indexing"
            ]
        }
    ]
}
```

## 🔄 Scenario Categories for Training

### 1. **Database Bottlenecks**
- **High CPU + High Memory**: Query optimization needed
- **High CPU + Normal Memory**: Missing indexes, inefficient queries
- **Normal CPU + High Memory**: Memory leaks, large result sets
- **Connection exhaustion**: Pool sizing issues

### 2. **API Service Issues**
- **High latency**: Network, dependencies, processing time
- **High error rate**: Bug, dependency failure, rate limiting
- **Memory leaks**: Garbage collection, resource cleanup
- **Thread exhaustion**: Concurrency limits

### 3. **Cache Problems**
- **Cache misses**: Poor hit rates, eviction policies
- **Memory pressure**: Cache size vs available RAM
- **Hot key issues**: Uneven data distribution

### 4. **External Dependencies**
- **Third-party failures**: Payment gateways, APIs
- **Network issues**: Timeouts, slow responses
- **Rate limiting**: API quotas exceeded

### 5. **Queue/Message Systems**
- **Message backlog**: Consumer lag, processing delays
- **Dead letter queues**: Failed message handling
- **Throughput issues**: Producer/consumer imbalance

## 📋 Complete Training Examples

### Example 1: Critical Database Overload

**Input:**
```json
{
    "risk_score": 95.0,
    "bottlenecks": [
        {
            "name": "Primary DB",
            "type": "database", 
            "cpu_usage": 98.0,
            "memory_usage": 95.0,
            "risk_score": 95.0,
            "reason": "CPU overload (98.0%); Memory critical (95.0%); Database service (critical)"
        },
        {
            "name": "User DB", 
            "type": "database",
            "cpu_usage": 85.0,
            "memory_usage": 80.0, 
            "risk_score": 82.0,
            "reason": "High CPU usage (85.0%); Memory high (80.0%)"
        }
    ],
    "cascading_failures": ["Authentication Service", "User Profile API", "Payment System"],
    "system_data": {"total_services": 12, "critical_count": 5}
}
```

**Expected Analysis:**
```markdown
🚨 **CRITICAL EMERGENCY** - System health score: 95.0/100

**Root Cause:** Database tier collapse detected. Primary DB experiencing near-total resource exhaustion with 98% CPU and 95% memory utilization. This indicates severe query inefficiency, missing indexes, or insufficient hardware capacity for current load.

**Immediate Business Impact:** REVENUE AT RISK - Payment processing affected, user authentication failing, customer experience severely degraded. Estimated downtime risk: HIGH.

**Cascade Analysis:** 3 critical services failing due to database dependency. Authentication Service cannot validate users, Payment System unable to process transactions.

**EMERGENCY ACTIONS (Execute Immediately):**
1. Scale Primary DB horizontally - deploy read replicas NOW
2. Identify and kill long-running queries causing resource lock
3. Implement emergency rate limiting on user-facing APIs
4. Activate database failover procedures if available

**Prevention Strategy:**
- Implement query performance monitoring
- Add proper indexing for frequent operations  
- Set up auto-scaling triggers at 80% utilization
```

**Expected Recommendations:**
```python
[
    "EMERGENCY: Scale Primary DB - deploy 3 read replicas within 15 minutes",
    "Identify slow queries: Enable pg_stat_statements and find queries >1sec", 
    "Implement connection pooling: PgBouncer with 100 max connections",
    "Add Redis cache: Cache user sessions and frequent queries (80% hit rate target)",
    "Set up monitoring: Deploy DataDog APM with CPU/memory alerts at 80%",
    "Database optimization: Run EXPLAIN ANALYZE on top 10 slowest queries"
]
```

### Example 2: Moderate API Performance Issue

**Input:**
```json
{
    "risk_score": 65.0,
    "bottlenecks": [
        {
            "name": "User API",
            "type": "api",
            "cpu_usage": 75.0, 
            "memory_usage": 45.0,
            "risk_score": 65.0,
            "reason": "High CPU usage (75.0%); Response time increased (350ms avg)"
        }
    ],
    "cascading_failures": [],
    "system_data": {"total_services": 8, "critical_count": 1}
}
```

**Expected Analysis:**
```markdown
⚠️ **MEDIUM RISK** - System health score: 65.0/100

**Root Cause:** User API experiencing elevated CPU usage at 75% with degraded response times (350ms average). Normal memory usage suggests computational bottleneck rather than memory leak. Likely causes: inefficient algorithms, external API calls, or increased user load.

**Business Impact:** User experience degradation - page load times increasing, potential customer frustration. SLA risk if response times exceed 500ms threshold.

**Performance Analysis:** Isolated issue in User API, no cascading failures detected. System remains stable but performance trending downward.

**ACTIONS REQUIRED:**
1. Scale User API horizontally (2-3 additional instances)
2. Investigate response time spikes - check external dependencies
3. Implement caching for frequent user data requests
4. Review API algorithms for optimization opportunities
```

**Expected Recommendations:**
```python
[
    "Scale User API: Deploy 2 additional instances behind load balancer",
    "Add caching layer: Redis for user profile data (30min TTL)",
    "Optimize API calls: Review external service dependencies and add circuit breakers", 
    "Implement monitoring: Track API response times with 500ms alert threshold",
    "Code review: Profile CPU-intensive operations in user data processing",
    "Load testing: Verify performance under 2x current user load"
]
```

### Example 3: Cache Performance Issues

**Input:**
```json
{
    "risk_score": 45.0,
    "bottlenecks": [
        {
            "name": "Redis Cache",
            "type": "cache",
            "cpu_usage": 35.0,
            "memory_usage": 88.0, 
            "risk_score": 45.0,
            "reason": "Memory high (88.0%); Cache hit rate declining (45%)"
        }
    ],
    "cascading_failures": [],
    "system_data": {"total_services": 10, "critical_count": 0}
}
```

**Expected Analysis:**
```markdown
🔧 **OPTIMIZATION NEEDED** - System health score: 45.0/100

**Root Cause:** Redis cache experiencing memory pressure at 88% capacity with declining hit rates (45%). This indicates suboptimal cache configuration - either inadequate memory allocation, poor eviction policies, or inefficient key patterns.

**Business Impact:** Performance degradation - increased database load as cache misses rise, slower response times for cached operations.

**Cache Analysis:** Memory pressure forcing premature evictions, reducing cache effectiveness. CPU usage normal, indicating memory is the limiting factor.

**OPTIMIZATION ACTIONS:**
1. Increase Redis memory allocation or scale to larger instance
2. Review and optimize cache eviction policies (LRU vs LFU)
3. Analyze key patterns for inefficient storage usage
4. Implement cache warming strategies for critical data
```

**Expected Recommendations:**
```python
[
    "Scale Redis memory: Increase from current size to handle 90% of working set",
    "Optimize eviction policy: Switch to allkeys-lru for better hit rates",
    "Key analysis: Review large keys and implement compression for JSON data",
    "Cache warming: Pre-load critical user data during deployment",
    "Monitoring: Set up cache hit rate alerts below 70%",
    "TTL optimization: Review expiration times for different data types"
]
```

## 🎨 Prompt Templates for Different Scenarios

### Analysis Prompt Template
```
You are a Senior DevOps Engineer analyzing a production microservices system {time_context}.

SYSTEM HEALTH OVERVIEW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Risk: {risk_score}/100 ({risk_level} PRIORITY)
System Status: {critical_count}/{total_services} services in critical state
Architecture: {service_types}

ACTIVE BOTTLENECKS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{bottleneck_details}

{cascade_alert}

BUSINESS CONTEXT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{business_impact}

PROVIDE YOUR EXPERT ANALYSIS:
1. Root cause identification (what's really causing this?)
2. Immediate business impact assessment  
3. Critical path to resolution
4. Long-term prevention strategy

Be specific, actionable, and consider the interdependencies.
```

### Recommendations Prompt Template  
```
You are a DevOps architect providing emergency response recommendations.

CRITICAL ISSUES REQUIRING IMMEDIATE ACTION:
{priority_issues}

SYSTEM CONSTRAINTS:
{system_constraints}

RISK LEVEL: {risk_score}/100
DOWNSTREAM IMPACT: {cascade_count} services affected

Provide 6 specific, prioritized recommendations. Format as action-oriented statements.
Consider: scaling, optimization, monitoring, architecture changes, immediate fixes.

Each recommendation should be immediately executable by a DevOps team.
```

## 📈 Performance Metrics to Include

### System Health Indicators
- **Risk Score**: 0-100 (overall system health)
- **Response Times**: Average, P95, P99 latency
- **Error Rates**: 4xx, 5xx error percentages  
- **Throughput**: Requests per second
- **Resource Utilization**: CPU, Memory, Disk, Network

### Service-Level Metrics
- **Availability**: Uptime percentage
- **Dependency Health**: External service response times
- **Queue Depths**: Message backlogs
- **Connection Pools**: Active/idle connections

### Business Context Indicators  
- **Time of Day**: Peak hours, maintenance windows
- **User Impact**: Active sessions affected
- **Revenue Risk**: Transaction volumes at risk
- **SLA Status**: Current vs target performance

## 🔍 Data Collection Strategy

### 1. **Historical Incident Data**
- Past outages and their resolutions
- Performance degradation events
- Successful scaling operations
- Failed deployments and rollbacks

### 2. **Expert Knowledge Capture**
- Senior DevOps engineer decision-making
- Incident response runbooks
- Architecture review findings  
- Capacity planning decisions

### 3. **Simulation Scenarios**
- Load testing results under various conditions
- Failure injection test outcomes
- Scaling behavior patterns
- Recovery time measurements

## 🎯 Training Data Volume Recommendations

- **Minimum**: 500 examples across all scenarios
- **Recommended**: 2,000+ examples for production quality
- **Categories**: 
  - Database issues: 30%
  - API performance: 25% 
  - Infrastructure: 20%
  - Cache/storage: 15%
  - External dependencies: 10%

## 🔧 Implementation Guide

### 1. **Data Generation Script**
```python
def generate_training_example(scenario_type, severity_level):
    """Generate a training example for specific scenario"""
    return {
        "input": create_system_state(scenario_type, severity_level),
        "expected_analysis": generate_expert_analysis(),
        "expected_recommendations": generate_recommendations()
    }
```

### 2. **Validation Metrics**
- **Analysis Quality**: Expert review scores
- **Recommendation Accuracy**: Implementation success rate
- **Response Relevance**: Context appropriateness
- **Action Specificity**: Clarity and executability

### 3. **Continuous Learning**
- **Feedback Loop**: Track recommendation outcomes
- **Model Updates**: Retrain with new incident data
- **Performance Monitoring**: Compare AI vs expert decisions

This specification should give you everything needed to create comprehensive training data for your AI model. The key is diversity across scenarios and consistent output formatting that matches the expected ScaleGuard interface.