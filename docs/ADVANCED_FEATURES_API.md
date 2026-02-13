# ScaleGuard Advanced Features API Documentation

## 🎯 Overview

Three new advanced features have been implemented:
1. **Historical Tracking** - Track system metrics over time (up to 48 hours)
2. **Predictive Analytics** - Forecast potential failures before they occur
3. **Auto-Remediation** - Automatically execute fixes for common issues

---

## 📊 Historical Tracking Endpoints

### GET `/api/historical/trends`

Get trend analysis for all system metrics.

**Query Parameters:**
- `time_window_minutes` (optional, default: 60) - Time window for trend calculation

**Response:**
```json
{
  "trends": {
    "risk_score": {
      "metric_name": "risk_score",
      "current_value": 100.0,
      "avg_last_hour": 100.0,
      "avg_last_day": 100.0,
      "trend_direction": "stable",
      "change_rate": 0.0,
      "severity": "critical"
    },
    "cpu_usage": { ... },
    "memory_usage": { ... },
    "error_rate": { ... },
    "latency": { ... }
  },
  "time_window_minutes": 60
}
```

**Trend Directions:**
- `increasing` - Metric is going up
- `decreasing` - Metric is going down
- `stable` - Metric is relatively unchanged
- `volatile` - Metric is fluctuating

---

### GET `/api/historical/service/{service_id}`

Get historical performance data for a specific service.

**Path Parameters:**
- `service_id` (required) - The service identifier

**Query Parameters:**
- `minutes` (optional, default: 60) - How many minutes of history to retrieve

**Example:**
```bash
GET /api/historical/service/payment-api?minutes=30
```

---

### GET `/api/historical/snapshots`

Get system snapshots from the last N minutes.

**Query Parameters:**
- `minutes` (optional, default: 60) - Time range in minutes

**Response:**
```json
{
  "snapshots": [
    {
      "timestamp": "2026-02-13T15:00:00",
      "risk_score": 95.5,
      "cpu_usage": 85.3,
      "memory_usage": 72.1,
      "error_rate": 12.5,
      "latency": 450.2
    }
  ],
  "count": 30,
  "time_range_minutes": 60
}
```

---

### GET `/api/historical/statistics`

Get statistics about stored historical data.

**Response:**
```json
{
  "total_snapshots": 30,
  "oldest_snapshot": "2026-02-13T14:30:00",
  "newest_snapshot": "2026-02-13T15:00:00",
  "coverage_hours": 0.5,
  "metrics_tracked": ["risk_score", "cpu_usage", "memory_usage", "error_rate", "latency"]
}
```

---

## 🔮 Predictive Analytics Endpoints

### GET `/api/predictions/all`

Get comprehensive predictions for all services.

**Response:**
```json
{
  "failure_predictions": [
    {
      "service_id": "payment-db",
      "failure_probability": 95,
      "estimated_time_minutes": 15,
      "failure_type": "error_cascade",
      "contributing_factors": "Critical CPU at 97.6%, Critical memory at 100%, High error rate",
      "preventive_actions": "Implement circuit breaker, Review error logs, Add retry logic",
      "severity": "critical"
    }
  ],
  "cascade_predictions": [],
  "prediction_timestamp": "2026-02-13T15:00:00",
  "total_at_risk_services": 5
}
```

**Failure Types:**
- `error_cascade` - Cascading failure from errors
- `resource_exhaustion` - Running out of CPU/memory
- `performance_degradation` - Slow response times

**Severity Levels:**
- `critical` - 75%+ failure probability
- `high` - 50-75% failure probability
- `medium` - 25-50% failure probability
- `low` - <25% failure probability

---

### GET `/api/predictions/failures`

Get predictions of potential service failures only.

**Response:**
```json
{
  "failure_predictions": [...],
  "total_at_risk": 5
}
```

---

### GET `/api/predictions/cascades`

Get predictions of potential cascade failures.

**Response:**
```json
{
  "cascade_predictions": [
    {
      "trigger_service": "api-gateway",
      "affected_services": ["auth-service", "payment-api"],
      "cascade_probability": 80,
      "estimated_time_minutes": 20
    }
  ],
  "prediction_timestamp": "2026-02-13T15:00:00"
}
```

---

## 🔧 Auto-Remediation Endpoints

### GET `/api/remediation/rules`

Get all auto-remediation rules.

**Response:**
```json
{
  "rules": [
    {
      "rule_id": "cpu_scale",
      "name": "Auto-scale on high CPU",
      "condition": "CPU usage > 85% for 5 minutes",
      "action_type": "scale_horizontal",
      "enabled": true,
      "auto_approve": true,
      "cooldown_minutes": 10,
      "last_executed": "2026-02-13T14:52:59"
    }
  ],
  "count": 5
}
```

**Default Rules:**
1. **cpu_scale** - Auto-scale when CPU > 85% (auto-approved, 10min cooldown)
2. **memory_restart** - Restart service when memory > 95% (requires approval, 30min cooldown)
3. **error_circuit_breaker** - Enable circuit breaker when error rate > 15% (auto-approved, 15min cooldown)
4. **overload_rate_limit** - Apply rate limiting on critical overload (auto-approved, 20min cooldown)
5. **cache_clear** - Clear cache when latency > 1000ms (auto-approved, 30min cooldown)

---

### GET `/api/remediation/actions`

Get remediation action history.

**Query Parameters:**
- `hours` (optional, default: 24) - How many hours of history to retrieve

**Response:**
```json
{
  "actions": [
    {
      "action_id": "rem-abc123",
      "service_id": "payment-api",
      "action_type": "scale_horizontal",
      "reason": "High CPU usage detected",
      "status": "completed",
      "timestamp": "2026-02-13T14:55:00",
      "execution_time": "2026-02-13T14:55:05",
      "details": "Scaled from 3 to 5 instances"
    }
  ],
  "count": 3
}
```

**Action Statuses:**
- `pending` - Awaiting approval
- `executing` - Currently running
- `completed` - Successfully executed
- `failed` - Execution failed
- `cancelled` - Action was cancelled

---

### GET `/api/remediation/pending`

Get pending remediation actions requiring approval.

**Response:**
```json
{
  "pending_actions": [
    {
      "action_id": "rem-xyz789",
      "service_id": "auth-service",
      "action_type": "restart_service",
      "reason": "Memory leak detected",
      "status": "pending"
    }
  ],
  "count": 1
}
```

---

### GET `/api/remediation/active`

Get currently executing remediation actions.

**Response:**
```json
{
  "active_actions": [],
  "count": 0
}
```

---

### POST `/api/remediation/execute/{action_id}`

Approve and execute a pending remediation action.

**Path Parameters:**
- `action_id` (required) - The action ID to execute

**Example:**
```bash
POST /api/remediation/execute/rem-xyz789
```

**Response:**
```json
{
  "action_id": "rem-xyz789",
  "status": "completed",
  "message": "Service restarted successfully"
}
```

---

### POST `/api/remediation/rules/{rule_id}/toggle`

Enable or disable a specific remediation rule.

**Path Parameters:**
- `rule_id` (required) - The rule ID

**Query Parameters:**
- `enabled` (required) - Boolean, true to enable, false to disable

**Example:**
```bash
POST /api/remediation/rules/memory_restart/toggle?enabled=false
```

**Response:**
```json
{
  "message": "Rule memory_restart disabled"
}
```

---

### GET `/api/remediation/statistics`

Get remediation system statistics.

**Response:**
```json
{
  "total_actions": 3,
  "completed": 3,
  "failed": 0,
  "pending": 0,
  "success_rate": 100.0,
  "actions_by_type": {
    "scale_horizontal": 1,
    "circuit_breaker": 1,
    "rate_limit": 1
  },
  "enabled": true,
  "dry_run_mode": false,
  "active_rules": 5
}
```

---

### POST `/api/remediation/toggle`

Enable or disable the entire auto-remediation system.

**Query Parameters:**
- `enabled` (required) - Boolean

**Example:**
```bash
POST /api/remediation/toggle?enabled=false
```

**Response:**
```json
{
  "enabled": false,
  "message": "Auto-remediation disabled"
}
```

---

### POST `/api/remediation/dry-run`

Enable or disable dry-run mode (simulate without executing).

**Query Parameters:**
- `dry_run` (required) - Boolean

**Example:**
```bash
POST /api/remediation/dry-run?dry_run=true
```

**Response:**
```json
{
  "dry_run": true,
  "message": "Dry-run mode enabled"
}
```

---

## 🧪 Testing Examples

### PowerShell Examples

```powershell
# Get historical trends
Invoke-RestMethod -Uri "http://localhost:8000/api/historical/trends?time_window_minutes=30" -Method GET

# Get failure predictions
Invoke-RestMethod -Uri "http://localhost:8000/api/predictions/failures" -Method GET

# Get remediation statistics
Invoke-RestMethod -Uri "http://localhost:8000/api/remediation/statistics" -Method GET

# Get all remediation rules
Invoke-RestMethod -Uri "http://localhost:8000/api/remediation/rules" -Method GET

# Disable a specific rule
Invoke-RestMethod -Uri "http://localhost:8000/api/remediation/rules/memory_restart/toggle?enabled=false" -Method POST

# Enable dry-run mode
Invoke-RestMethod -Uri "http://localhost:8000/api/remediation/dry-run?dry_run=true" -Method POST
```

---

## 📈 Integration with Existing Endpoints

### Modified `/api/analysis` Endpoint

The analysis endpoint now automatically:
1. **Records historical snapshot** after each analysis
2. **Evaluates auto-remediation rules** for all services
3. **Executes auto-approved actions** immediately
4. **Logs all remediation attempts** for audit trail

**Example Flow:**
```
1. User requests /api/analysis
2. System analyzes current state
3. Historical snapshot saved automatically
4. Auto-remediation evaluates all services
5. Auto-approved actions executed immediately
6. Analysis response includes AI recommendations
```

---

## 🎨 Current System Status

**Live Test Results (from current system):**

### Historical Tracking
- ✅ 30 snapshots collected (0.5 hours of data)
- ✅ Tracking 5 metrics: risk_score, cpu_usage, memory_usage, error_rate, latency
- ✅ All trends calculated correctly

### Predictive Analytics
- ✅ 5 services identified as at-risk
- ✅ Critical alerts: payment-db (95% failure probability in 15 min)
- ✅ Preventive actions generated for each prediction

### Auto-Remediation
- ✅ 3 actions executed automatically
- ✅ 100% success rate
- ✅ 5 rules active (4 auto-approved, 1 manual)
- ✅ Actions: scale_horizontal (1), circuit_breaker (1), rate_limit (1)

---

## 🚀 Next Steps

### Frontend Integration
Create React components for:
1. **Historical Dashboard** - Line charts showing metric trends over time
2. **Predictions Panel** - Display at-risk services with time-to-failure countdowns
3. **Remediation Control Center** - Manage rules, approve actions, view statistics

### Suggested Pages
- `/dashboard/trends` - Historical metrics visualization
- `/dashboard/predictions` - Failure forecasts and preventive actions
- `/dashboard/remediation` - Auto-remediation management console

---

## 📝 Notes

- Historical data is stored in memory and limited to 48 hours (2880 snapshots)
- Predictions use linear extrapolation and multi-factor analysis
- Auto-remediation has cooldown periods to prevent rapid repeated actions
- All actions are logged and can be audited via the history endpoint
- Dry-run mode allows testing without making actual changes
