# OPA Policy Deployment Guide

## Files Generated

- `ssid_compliance_policy.rego` - Main compliance policy
- `ssid_compliance_policy_test.json` - Test data and sample queries
- `modules/*.rego` - Per-module policies

## Deployment

### 1. Start OPA Server

```bash
opa run --server --addr :8181
```

### 2. Load Policy

```bash
curl -X PUT http://localhost:8181/v1/policies/ssid-compliance \
  --data-binary @ssid_compliance_policy.rego
```

### 3. Query Examples

**Check overall compliance:**
```bash
curl -X POST http://localhost:8181/v1/data/ssid/compliance/allow
```

**Get audit report:**
```bash
curl -X POST http://localhost:8181/v1/data/ssid/compliance/audit_report
```

**Get risk assessment:**
```bash
curl -X POST http://localhost:8181/v1/data/ssid/compliance/risk_assessment
```

**Query framework controls:**
```bash
curl -X POST http://localhost:8181/v1/data/ssid/compliance/framework_controls \
  -d '{"input": {"framework": "gdpr"}}'
```

**Query module controls:**
```bash
curl -X POST http://localhost:8181/v1/data/ssid/compliance/module_controls \
  -d '{"input": {"module": "09_meta_identity"}}'
```

## Testing

```bash
opa test ssid_compliance_policy.rego ssid_compliance_policy_test.json
```

## Integration

Integrate with external systems via OPA's REST API or SDKs:
- Python: https://github.com/open-policy-agent/opa-python
- Go: https://github.com/open-policy-agent/opa/tree/main/rego
- Java: https://github.com/Bisnode/opa-java-client

Generated: 2025-10-07T11:40:52.067568
