# SSID Health Check Standard

**Version:** 1.0.0
**Status:** ACTIVE
**Compliance:** SHOULD-001-HEALTH-TEMPLATE
**Last Updated:** 2025-10-10

## Overview

This document defines the standardized health check implementation for all SSID modules, ensuring consistent monitoring, alerting, and compliance with DORA Article 10 (Detection and Monitoring) requirements.

## Health Check Endpoints

All SSID modules MUST implement three standard health endpoints:

### 1. Liveness Probe (`/health/live`)

**Purpose:** Determine if the service is running and responsive.

**HTTP Method:** GET
**Expected Status:** 200 OK
**Timeout:** 1000ms

**Response Schema:**
```json
{
  "status": "UP",
  "timestamp": "2025-10-10T13:00:00Z",
  "module": "anti_gaming_validator"
}
```

**Failure Behavior:** If liveness fails, Kubernetes/orchestrator should restart the pod.

---

### 2. Readiness Probe (`/health/ready`)

**Purpose:** Determine if the service is ready to accept traffic.

**HTTP Method:** GET
**Expected Status:** 200 OK
**Timeout:** 2000ms

**Response Schema:**
```json
{
  "status": "READY",
  "timestamp": "2025-10-10T13:00:00Z",
  "module": "anti_gaming_validator",
  "dependencies": [
    {
      "name": "postgresql",
      "status": "UP",
      "latency_ms": 15
    },
    {
      "name": "redis_cache",
      "status": "UP",
      "latency_ms": 3
    }
  ]
}
```

**Failure Behavior:** If readiness fails, remove service from load balancer pool.

---

### 3. Startup Probe (`/health/startup`)

**Purpose:** Determine if the service has completed initialization.

**HTTP Method:** GET
**Expected Status:** 200 OK
**Timeout:** 5000ms

**Response Schema:**
```json
{
  "status": "STARTED",
  "timestamp": "2025-10-10T13:00:00Z",
  "module": "anti_gaming_validator",
  "initialization_duration_ms": 2341
}
```

**Failure Behavior:** If startup fails after threshold, mark service as failed and alert operations.

---

## Health Check Categories

### 1. Dependency Checks

Monitor external dependencies (databases, caches, APIs).

**Example:**
```yaml
database:
  name: "PostgreSQL Connection"
  type: "dependency"
  critical: true
  timeout_ms: 2000
  check_interval_seconds: 30
  failure_threshold: 3
  recovery_threshold: 2
```

### 2. Resource Checks

Monitor system resources (CPU, memory, disk).

**Example:**
```yaml
memory:
  name: "Memory Usage"
  type: "resource"
  critical: true
  threshold_percent: 85
  check_interval_seconds: 60
```

### 3. Business Logic Checks

Validate critical business functionality.

**Example:**
```yaml
fraud_detection:
  name: "Anti-Gaming Pipeline"
  type: "business_logic"
  critical: true
  validation_query: "SELECT COUNT(*) FROM violations WHERE created_at > NOW() - INTERVAL '1 minute'"
  expected_min: 0
  expected_max: 1000
```

---

## Compliance Requirements

### DORA Article 10 (Detection and Monitoring)

- ✅ Continuous monitoring of all critical services
- ✅ Automated alerting on health check failures
- ✅ Audit logging of all health check events
- ✅ 99.9% uptime SLA monitoring

### GDPR Article 32 (Security of Processing)

- ✅ Availability monitoring to ensure data processor reliability
- ✅ Incident detection via health check failures

### ISO 27001:2022

- ✅ A.17.1 - Information security continuity
- ✅ A.17.2 - Redundancies (readiness checks ensure failover readiness)

---

## Implementation Guide

### Step 1: Copy Template

```bash
cp 23_compliance/templates/health_check_template.yaml <your_module>/health/health_config.yaml
```

### Step 2: Customize Configuration

Edit `health_config.yaml` to match your module's dependencies and resources.

### Step 3: Implement Endpoints

**Python Example (Flask):**
```python
from flask import Flask, jsonify
import time

app = Flask(__name__)
startup_time = time.time()

@app.route('/health/live')
def liveness():
    return jsonify({
        "status": "UP",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "module": "anti_gaming_validator"
    }), 200

@app.route('/health/ready')
def readiness():
    # Check dependencies
    db_status = check_database_connection()
    cache_status = check_cache_connection()

    all_ready = db_status["status"] == "UP" and cache_status["status"] == "UP"

    return jsonify({
        "status": "READY" if all_ready else "NOT_READY",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "module": "anti_gaming_validator",
        "dependencies": [db_status, cache_status]
    }), 200 if all_ready else 503

@app.route('/health/startup')
def startup():
    init_duration = int((time.time() - startup_time) * 1000)

    return jsonify({
        "status": "STARTED",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "module": "anti_gaming_validator",
        "initialization_duration_ms": init_duration
    }), 200
```

### Step 4: Configure Kubernetes Probes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: anti-gaming-validator
spec:
  containers:
  - name: validator
    image: ssid/anti-gaming:latest
    livenessProbe:
      httpGet:
        path: /health/live
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 30
      timeoutSeconds: 1
      failureThreshold: 3
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 10
      timeoutSeconds: 2
      failureThreshold: 3
    startupProbe:
      httpGet:
        path: /health/startup
        port: 8080
      initialDelaySeconds: 0
      periodSeconds: 5
      timeoutSeconds: 5
      failureThreshold: 12
```

---

## Monitoring Integration

### Prometheus Metrics

All health checks should expose Prometheus metrics at `/metrics`:

```
# HELP health_check_status Health check status (1 = UP, 0 = DOWN)
# TYPE health_check_status gauge
health_check_status{check="database",module="anti_gaming"} 1
health_check_status{check="cache",module="anti_gaming"} 1

# HELP health_check_duration_seconds Health check duration
# TYPE health_check_duration_seconds histogram
health_check_duration_seconds{check="database",module="anti_gaming"} 0.015
```

### Alerting Rules

```yaml
groups:
  - name: ssid_health_checks
    rules:
      - alert: HealthCheckFailed
        expr: health_check_status == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Health check failed for {{ $labels.module }}"
          description: "{{ $labels.check }} check has been failing for 5 minutes"
```

---

## Testing

### Unit Tests

```python
def test_liveness_endpoint():
    response = client.get('/health/live')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'UP'
    assert 'timestamp' in data
    assert data['module'] == 'anti_gaming_validator'

def test_readiness_when_dependencies_healthy():
    mock_db_connection(healthy=True)
    mock_cache_connection(healthy=True)

    response = client.get('/health/ready')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'READY'

def test_readiness_when_database_unhealthy():
    mock_db_connection(healthy=False)

    response = client.get('/health/ready')
    assert response.status_code == 503
    data = response.get_json()
    assert data['status'] == 'NOT_READY'
```

---

## Audit Logging

All health check failures MUST be logged to the audit trail:

```json
{
  "event_type": "health_check_failure",
  "timestamp": "2025-10-10T13:00:00Z",
  "module": "anti_gaming_validator",
  "check_name": "database",
  "severity": "CRITICAL",
  "details": {
    "error": "Connection timeout after 2000ms",
    "consecutive_failures": 3,
    "last_success": "2025-10-10T12:58:30Z"
  },
  "sha256": "7f8a9e2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f"
}
```

---

## Compliance Validation

To validate compliance with this standard:

```bash
cd 23_compliance/tools
python validate_health_checks.py --module anti_gaming_validator
```

**Expected Output:**
```
✅ Liveness endpoint implemented
✅ Readiness endpoint implemented
✅ Startup endpoint implemented
✅ Prometheus metrics exposed
✅ Audit logging configured
✅ Health check template compliant

Compliance Score: 100%
Status: COMPLIANT
```

---

## References

- **Template:** `23_compliance/templates/health_check_template.yaml`
- **DORA Compliance:** `23_compliance/mappings/dora_mapping.yaml`
- **Kubernetes Probes:** https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
- **Prometheus Best Practices:** https://prometheus.io/docs/practices/naming/

---

**Document Owner:** SSID Compliance Team
**Next Review:** 2026-01-10
**Questions:** compliance@ssid.example.com
