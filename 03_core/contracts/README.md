# Architecture Validation Contracts

Contract Definitions (OpenAPI + JSON Schema) for SSID Architecture Master Rules (AR001-AR010).

**Version:** 1.0.0
**Status:** Production-Ready
**Coverage:** 3/5 SoT Artefacts for AR001-AR010

---

## Overview

This directory contains **Contract Definitions** - one of the 5 mandatory SoT (Source of Truth) Artefacts for Master Rules implementation.

### 5 SoT Artefacts:
1. **Contract Definitions** (this directory) - OpenAPI specs + JSON schemas
2. **Core Logic** - `03_core/validators/architecture_validator.py`
3. **Policy Enforcement** - `23_compliance/opa/architecture_rules.rego`
4. **CLI Validation** - Integration with CLI tools
5. **Test Suites** - `tests/test_architecture_rules.py`

---

## Files

### OpenAPI Specification

**`architecture_validation_api.yaml`**
- Complete REST API specification for Architecture Rule validation
- 12 endpoints covering all AR001-AR010 rules
- Request/response schemas with examples
- Error handling definitions
- Authentication requirements (API key)

**Base URL (Local):** `https://api.ssid.local/v1`
**Base URL (Prod):** `https://api.ssid.prod/v1`

### JSON Schemas

Located in `schemas/` subdirectory:

1. **`architecture_validation_result.schema.json`**
   - Core data structure for validation results
   - Used by all AR001-AR010 endpoints
   - Properties: rule_id, rule_text, passed, evidence, violations, severity

2. **`evidence_ar001_24_root_folders.schema.json`**
   - Evidence structure for AR001 validation
   - Properties: total_root_folders, root_folders, missing_prefixes

3. **`evidence_ar003_384_charts.schema.json`**
   - Evidence structure for AR003 validation
   - Properties: total_charts, sample_charts, expected_count

4. **`evidence_ar006_chart_yaml_exists.schema.json`**
   - Evidence structure for AR006 validation
   - Properties: missing_count, total_shards_scanned, coverage_percent

---

## API Endpoints

### Global Validation

#### `GET /validate/architecture`
Validate all 10 Architecture Rules in one call.

**Parameters:**
- `repo_path` (query, optional): Path to SSID repository (default: ".")

**Response:** `ArchitectureValidationResponse`
```json
{
  "total_rules": 10,
  "passed_count": 8,
  "failed_count": 2,
  "results": [ /* array of ArchitectureValidationResult */ ],
  "timestamp": "2025-10-19T14:30:00Z",
  "repo_path": "/home/user/SSID"
}
```

---

### Individual Rule Validation

All endpoints follow the pattern: `GET /validate/architecture/{ruleId}`

#### AR001: 24 Root Folders
`GET /validate/architecture/ar001`

**Rule:** Das System MUSS aus exakt 24 Root-Ordnern bestehen

**Evidence Schema:** `evidence_ar001_24_root_folders.schema.json`

**Example Response:**
```json
{
  "rule_id": "AR001",
  "rule_text": "Das System MUSS aus exakt 24 Root-Ordnern bestehen",
  "passed": true,
  "evidence": {
    "total_root_folders": 24,
    "root_folders": ["01_ai_layer", "02_audit_logging", ...]
  },
  "violations": [],
  "severity": "CRITICAL"
}
```

#### AR002: 16 Shards per Root
`GET /validate/architecture/ar002`

**Rule:** Jeder Root-Ordner MUSS exakt 16 Shards enthalten

#### AR003: 384 Charts
`GET /validate/architecture/ar003`

**Rule:** Es MUESSEN exakt 384 Chart-Dateien existieren (24x16)

**Evidence Schema:** `evidence_ar003_384_charts.schema.json`

#### AR004: Root Folder Format
`GET /validate/architecture/ar004`

**Rule:** Root-Ordner MUESSEN Format '{NR}_{NAME}' haben

**Format Pattern:** `^\\d{2}_[a-z_]+$`

#### AR005: Shard Format
`GET /validate/architecture/ar005`

**Rule:** Shards MUESSEN Format 'Shard_{NR}_{NAME}' haben

**Format Pattern:** `^Shard_\\d{2}_[A-Za-z_]+$`

#### AR006: chart.yaml Exists
`GET /validate/architecture/ar006`

**Rule:** Jeder Shard MUSS eine chart.yaml (SoT) enthalten

**Evidence Schema:** `evidence_ar006_chart_yaml_exists.schema.json`

#### AR007: manifest.yaml Exists
`GET /validate/architecture/ar007`

**Rule:** Jede Implementierung MUSS eine manifest.yaml enthalten

#### AR008: Path Structure
`GET /validate/architecture/ar008`

**Rule:** Pfadstruktur MUSS sein: {ROOT}/shards/{SHARD}/chart.yaml

#### AR009: Implementations Path
`GET /validate/architecture/ar009`

**Rule:** Implementierungen MUESSEN unter implementations/{IMPL_ID}/ liegen

#### AR010: Contracts Folder
`GET /validate/architecture/ar010`

**Rule:** Contracts MUESSEN in contracts/-Ordner mit OpenAPI/JSON-Schema liegen

---

## Usage Examples

### cURL

**Validate all rules:**
```bash
curl -X GET "https://api.ssid.local/v1/validate/architecture?repo_path=." \
  -H "X-API-Key: your-api-key" \
  -H "Accept: application/json"
```

**Validate specific rule (AR001):**
```bash
curl -X GET "https://api.ssid.local/v1/validate/architecture/ar001?repo_path=/home/user/SSID" \
  -H "X-API-Key: your-api-key" \
  -H "Accept: application/json"
```

### Python

```python
import requests

# Validate all rules
response = requests.get(
    "https://api.ssid.local/v1/validate/architecture",
    params={"repo_path": "."},
    headers={"X-API-Key": "your-api-key"}
)

results = response.json()
print(f"Passed: {results['passed_count']}/{results['total_rules']}")

for result in results['results']:
    status = "PASS" if result['passed'] else "FAIL"
    print(f"[{status}] {result['rule_id']}: {result['rule_text']}")
```

### JavaScript/TypeScript

```typescript
const response = await fetch(
  'https://api.ssid.local/v1/validate/architecture?repo_path=.',
  {
    headers: {
      'X-API-Key': 'your-api-key',
      'Accept': 'application/json'
    }
  }
);

const results = await response.json();
console.log(`Passed: ${results.passed_count}/${results.total_rules}`);
```

---

## JSON Schema Validation

### Validate API Responses

Use JSON Schema validators to verify API responses:

**Python (jsonschema):**
```python
import jsonschema
import yaml
import json

# Load schema
with open('schemas/architecture_validation_result.schema.json') as f:
    schema = json.load(f)

# Validate response
try:
    jsonschema.validate(instance=api_response, schema=schema)
    print("Valid response")
except jsonschema.ValidationError as e:
    print(f"Invalid response: {e.message}")
```

**Node.js (ajv):**
```javascript
const Ajv = require('ajv');
const ajv = new Ajv();

const schema = require('./schemas/architecture_validation_result.schema.json');
const validate = ajv.compile(schema);

if (validate(apiResponse)) {
  console.log('Valid response');
} else {
  console.log('Invalid response:', validate.errors);
}
```

---

## OpenAPI Code Generation

### Generate Client SDKs

**Using openapi-generator-cli:**

```bash
# Python client
openapi-generator-cli generate \
  -i architecture_validation_api.yaml \
  -g python \
  -o ./generated/python-client

# TypeScript/Axios client
openapi-generator-cli generate \
  -i architecture_validation_api.yaml \
  -g typescript-axios \
  -o ./generated/typescript-client

# Java client
openapi-generator-cli generate \
  -i architecture_validation_api.yaml \
  -g java \
  -o ./generated/java-client
```

### Generate Server Stubs

```bash
# FastAPI server (Python)
openapi-generator-cli generate \
  -i architecture_validation_api.yaml \
  -g python-fastapi \
  -o ./generated/fastapi-server

# Express server (Node.js)
openapi-generator-cli generate \
  -i architecture_validation_api.yaml \
  -g nodejs-express-server \
  -o ./generated/express-server
```

---

## Contract-First Development

### Workflow

1. **Define Contract** (OpenAPI + JSON Schema) - THIS FILE
2. **Generate Code** (clients + servers from contract)
3. **Implement Logic** (`03_core/validators/architecture_validator.py`)
4. **Write Tests** (`tests/test_architecture_rules.py`)
5. **Enforce Policies** (`23_compliance/opa/architecture_rules.rego`)
6. **Validate Contract** (ensure API matches spec)

### Benefits

- API specification is source of truth
- Client/server code stays in sync
- Validation is automatic
- Documentation is always up-to-date
- Breaking changes are detected early

---

## Compliance & Audit

### MiCA/eIDAS Requirements

Contract Definitions provide:

1. **Formal API Specification**: OpenAPI standard (CRITICAL for regulatory approval)
2. **Schema Validation**: JSON Schema ensures data integrity
3. **Evidence Structures**: Documented evidence for each rule validation
4. **Audit Trail**: All validations produce structured evidence
5. **Versioning**: Semver versioning of API contract

### Audit Report Generation

```python
from architecture_validator import ArchitectureValidator

validator = ArchitectureValidator(repo_path=".")
results = validator.validate_all()

# Generate audit-ready report
audit_report = {
    "timestamp": datetime.now().isoformat(),
    "validator_version": "1.0.0",
    "contract_version": "1.0.0",
    "results": [r.to_dict() for r in results],
    "compliance_status": "COMPLIANT" if all(r.passed for r in results) else "NON_COMPLIANT"
}

# Save for auditor
with open('audit_report_ar001_ar010.json', 'w') as f:
    json.dump(audit_report, f, indent=2)
```

---

## Testing Contracts

### Contract Testing with Dredd

**Install Dredd:**
```bash
npm install -g dredd
```

**Test API against contract:**
```bash
dredd architecture_validation_api.yaml https://api.ssid.local/v1
```

### Pact Testing (Consumer-Driven Contracts)

```python
from pact import Consumer, Provider

pact = Consumer('ValidationClient').has_pact_with(Provider('ValidationAPI'))

pact.given('Repository with 24 root folders') \
    .upon_receiving('A request to validate AR001') \
    .with_request('GET', '/validate/architecture/ar001') \
    .will_respond_with(200, body={
        'rule_id': 'AR001',
        'passed': True,
        'evidence': {
            'total_root_folders': 24
        }
    })
```

---

## Versioning Strategy

### Semantic Versioning

**Current Version:** 1.0.0

**Version Format:** MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes to API (incompatible)
- **MINOR**: New endpoints/features (backward-compatible)
- **PATCH**: Bug fixes, clarifications (backward-compatible)

### Changelog

**v1.0.0** (2025-10-19)
- Initial release
- 12 endpoints for AR001-AR010 validation
- 4 JSON schemas for evidence structures
- Complete OpenAPI 3.0.3 specification
- Authentication via API key

---

## Integration with Other Artefacts

### Core Logic (`03_core/validators/architecture_validator.py`)
```python
# Contract defines the interface
# Core Logic implements the validation
validator = ArchitectureValidator(repo_path=".")
result = validator.validate_ar001_24_root_folders()

# Result conforms to architecture_validation_result.schema.json
assert result.rule_id == "AR001"
assert isinstance(result.passed, bool)
assert isinstance(result.evidence, dict)
```

### Policy Enforcement (`23_compliance/opa/architecture_rules.rego`)
```rego
# Contract defines evidence structure
# OPA policy enforces rules based on evidence

deny[msg] if {
    input.rule_id == "AR001"
    input.evidence.total_root_folders != 24
    msg := "AR001 violation: Expected 24 root folders"
}
```

### Test Suites (`tests/test_architecture_rules.py`)
```python
# Contract defines expected response
# Tests verify implementation matches contract

def test_ar001_response_conforms_to_schema(validator):
    result = validator.validate_ar001_24_root_folders()

    # Validate against JSON Schema
    with open('03_core/contracts/schemas/architecture_validation_result.schema.json') as f:
        schema = json.load(f)

    jsonschema.validate(instance=result.to_dict(), schema=schema)
```

---

## Error Handling

### Error Response Schema

All API errors follow this structure:

```json
{
  "error": "INVALID_REPOSITORY_PATH",
  "message": "The specified repository path does not exist",
  "details": {
    "provided_path": "/invalid/path",
    "current_directory": "/home/user"
  }
}
```

### Error Codes

- `INVALID_REPOSITORY_PATH`: Repository path does not exist
- `INVALID_RULE_ID`: Rule ID not in range AR001-AR010
- `VALIDATION_ERROR`: Internal validation error
- `SCHEMA_VIOLATION`: Response does not match schema
- `AUTHENTICATION_FAILED`: Invalid or missing API key

---

## Performance Considerations

### Caching

API responses can be cached based on:
- Repository path
- Git commit hash (for immutability)
- Last modified timestamp

**Cache-Control Header:**
```
Cache-Control: public, max-age=3600, stale-while-revalidate=86400
```

### Pagination

For large result sets (violations list), use pagination:

**Request:**
```
GET /validate/architecture/ar006?page=1&per_page=20
```

**Response:**
```json
{
  "violations": [ /* 20 items */ ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_items": 150,
    "total_pages": 8
  }
}
```

---

## Security

### Authentication

**Production:** API Key authentication (X-API-Key header)
**Development:** Optional (can be disabled for local testing)

### Rate Limiting

- 1000 requests/hour per API key
- 100 requests/minute per IP

### HTTPS Only

All API endpoints MUST use HTTPS in production. HTTP requests will be redirected to HTTPS.

---

## References

### Standards
- [OpenAPI 3.0.3 Specification](https://spec.openapis.org/oas/v3.0.3)
- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/schema)
- [REST API Design Best Practices](https://restfulapi.net/)

### Related Files
- Validator Implementation: `03_core/validators/architecture_validator.py`
- Test Suite: `tests/test_architecture_rules.py`
- Master Rules: `16_codex/structure/level3/master_rules.yaml`
- Coverage Checker: `16_codex/structure/level3/coverage_checker.py`

### Tools
- [OpenAPI Generator](https://openapi-generator.tech/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [Dredd](https://dredd.org/)
- [JSON Schema Validator](https://www.jsonschemavalidator.net/)

---

**Status:** Contract Definitions for AR001-AR010 completed (3/5 SoT Artefacts)
**Next:** Phase 1.4 - OPA Policies for AR001-AR010
**Target:** 100% Coverage across all 5 SoT Artefacts

**Version:** 1.0.0
**Last Updated:** 2025-10-19
**Maintained by:** SSID Core Team
