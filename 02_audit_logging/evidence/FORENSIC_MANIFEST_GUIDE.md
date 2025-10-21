# Forensic Evidence Manifest System

**Version**: 1.0.0
**Date**: 2025-10-14
**Status**: ✅ Production Ready

---

## Overview

The Forensic Evidence Manifest System provides deterministic, auditable tracking of all import resolution evidence files through auto-hash injection, merkle root computation, and OPA policy enforcement. This extends the existing audit chain without requiring version or structure changes.

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                  Forensic Manifest System                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────┐      ┌──────────────────┐               │
│  │  Evidence     │─────>│  Manifest        │               │
│  │  Scanner      │      │  Generator       │               │
│  └───────────────┘      └──────────────────┘               │
│         │                        │                           │
│         │                        ▼                           │
│         │               ┌──────────────────┐                │
│         │               │  SHA-256 Hasher  │                │
│         │               └──────────────────┘                │
│         │                        │                           │
│         ▼                        ▼                           │
│  ┌───────────────┐      ┌──────────────────┐               │
│  │  Merkle Root  │<─────│  YAML Manifest   │               │
│  │  Calculator   │      │  Generator       │               │
│  └───────────────┘      └──────────────────┘               │
│         │                        │                           │
│         ▼                        ▼                           │
│  ┌───────────────┐      ┌──────────────────┐               │
│  │  OPA Policy   │      │  Audit Report    │               │
│  │  Validator    │      │  Generator       │               │
│  └───────────────┘      └──────────────────┘               │
│         │                        │                           │
│         ▼                        ▼                           │
│  ┌───────────────────────────────────────┐                 │
│  │  Registry Update & CI Integration     │                 │
│  └───────────────────────────────────────┘                 │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
02_audit_logging/
├── evidence/
│   ├── forensic_manifest_generator.py  # Core generator
│   ├── forensic_manifest.yaml          # Generated manifest
│   └── import_resolution/              # Evidence files
│       ├── canonical_edges_*.json
│       ├── import_resolution_report_*.json
│       └── resolved_edges_*.json

23_compliance/
├── policies/
│   └── opa/
│       └── forensic_manifest_integrity.rego  # OPA policy
└── reports/
    └── forensic_manifest_audit_*.json        # Audit reports

24_meta_orchestration/
└── registry/
    └── forensic_manifest_registry.yaml       # Registry entries

11_test_simulation/
└── tests_compliance/
    └── test_forensic_manifest.py             # Validation tests

.github/
└── workflows/
    └── forensic_manifest_ci.yml              # CI pipeline
```

---

## Manifest Structure

### YAML Schema

```yaml
version: 1
generated_at: "2025-10-14T11:27:54.755769+00:00"
generator: "forensic_manifest_generator.py v1.0.0"
total_files: 3
merkle_root: "5dc0ac561ec9a82e0a6fdd9271f324a3381b67bf61417b23f736b85255bad47e"
evidence_directory: "02_audit_logging/evidence/import_resolution"
evidence:
  - path: "02_audit_logging/evidence/import_resolution/canonical_edges_*.json"
    sha256: "a9297e54e96659cd3a7d08fe014ceca78b204517f7d237805a76ba7ef88746f2"
    size_bytes: 754309
    modified: "2025-10-14T11:12:02.594949+00:00"
  # ... additional entries
integrity:
  algorithm: "SHA-256"
  merkle_algorithm: "SHA-256 concatenated"
  deterministic_ordering: "sorted by path"
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | int | Manifest format version (currently 1) |
| `generated_at` | ISO8601 | Timestamp of manifest generation (UTC) |
| `generator` | string | Tool name and version |
| `total_files` | int | Number of evidence files tracked |
| `merkle_root` | hex string | SHA-256 merkle root of all file hashes |
| `evidence_directory` | path | Base directory for evidence files |
| `evidence[]` | array | List of evidence file entries |
| `evidence[].path` | path | Relative path to evidence file |
| `evidence[].sha256` | hex string | SHA-256 hash of file contents |
| `evidence[].size_bytes` | int | File size in bytes |
| `evidence[].modified` | ISO8601 | Last modification timestamp |
| `integrity` | object | Integrity algorithm metadata |

---

## Merkle Root Computation

### Algorithm

1. **Collect hashes**: Gather SHA-256 hash for each evidence file
2. **Sort deterministically**: Sort by file path (ascending)
3. **Concatenate**: Join all hashes into single string
4. **Hash concatenation**: Compute SHA-256 of concatenated string

### Example

```python
# Evidence files (sorted by path)
files = [
    ("canonical_edges.json", "a9297e54..."),
    ("import_resolution_report.json", "2f91d475..."),
    ("resolved_edges.json", "af6991e4...")
]

# Concatenate hashes
concatenated = "a9297e54..." + "2f91d475..." + "af6991e4..."

# Compute merkle root
merkle_root = sha256(concatenated) = "5dc0ac56..."
```

### Properties

- **Deterministic**: Same files always produce same merkle root
- **Tamper-evident**: Any change to any file changes merkle root
- **Efficient**: O(n) computation, O(1) verification
- **Blockchain-ready**: Suitable for IPFS anchoring

---

## OPA Policy Enforcement

### Policy Rules

The OPA policy (`forensic_manifest_integrity.rego`) enforces:

#### 1. Manifest Exists
```rego
manifest_exists if {
    input.version
    input.generated_at
    input.merkle_root
    input.evidence
}
```

#### 2. Manifest Fresh (< 24 hours)
```rego
manifest_fresh if {
    manifest_time := time.parse_rfc3339_ns(input.generated_at)
    current_time := time.now_ns()
    age_hours := (current_time - manifest_time) / 1000000000 / 3600
    age_hours < 24
}
```

#### 3. Manifest Complete
```rego
manifest_complete if {
    count(input.evidence) > 0
    input.total_files == count(input.evidence)
    all_entries_valid
}
```

#### 4. Hashes Valid
```rego
hashes_valid if {
    every entry in input.evidence {
        entry.sha256 != "ERROR_HASH_FAILED"
        string.length(entry.sha256) == 64
    }
}
```

#### 5. Merkle Root Valid
```rego
merkle_root_valid if {
    input.merkle_root != "EMPTY_NO_EVIDENCE"
    string.length(input.merkle_root) == 64
}
```

### Policy Evaluation

```bash
# Convert YAML to JSON
python -c "import yaml, json; json.dump(yaml.safe_load(open('forensic_manifest.yaml')), open('manifest.json', 'w'))"

# Evaluate policy
opa eval -d forensic_manifest_integrity.rego \
         -i manifest.json \
         --format pretty \
         "data.forensic.allow"

# Get denial reasons (if denied)
opa eval -d forensic_manifest_integrity.rego \
         -i manifest.json \
         --format pretty \
         "data.forensic.deny"
```

---

## CI/CD Integration

### Workflow Triggers

```yaml
on:
  push:
    branches: [ main, develop ]
    paths:
      - '02_audit_logging/evidence/import_resolution/**'
      - '02_audit_logging/evidence/forensic_manifest_generator.py'
      - '23_compliance/policies/opa/forensic_manifest_integrity.rego'
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:
```

### Pipeline Steps

1. **Generate Manifest**
   ```bash
   python 02_audit_logging/evidence/forensic_manifest_generator.py
   ```

2. **Validate with OPA**
   ```bash
   opa eval -d forensic_manifest_integrity.rego \
            -i manifest.json \
            "data.forensic.allow"
   ```

3. **Run Tests**
   ```bash
   pytest 11_test_simulation/tests_compliance/test_forensic_manifest.py -v
   ```

4. **Upload Artifacts**
   - Manifest (retention: 90 days)
   - Audit report (retention: 365 days)
   - Registry (retention: 90 days)

### Success Criteria

✅ Manifest generated successfully
✅ OPA policy evaluation: `allow = true`
✅ All pytest tests passed
✅ Compliance status: `COMPLIANT`

---

## Usage

### Manual Execution

```bash
# Generate manifest
cd /path/to/SSID
python 02_audit_logging/evidence/forensic_manifest_generator.py

# Output:
# ======================================================================
# Forensic Evidence Manifest Generator
# ======================================================================
#
# Scanning evidence files...
# Found 3 evidence files
#
# Computing SHA-256 hashes...
# Hashed 3 files
#
# Generating manifest...
# Merkle root: 5dc0ac561ec9a82e...
#
# Writing manifest...
# Manifest: 02_audit_logging/evidence/forensic_manifest.yaml
#
# Generating audit report...
# Report: 23_compliance/reports/forensic_manifest_audit_20251014_112754.json
# Status: COMPLIANT
#
# Updating registry...
# Registry updated
#
# ======================================================================
# Manifest Generation Complete
# ======================================================================
# Evidence files: 3
# Merkle root: 5dc0ac561ec9a82e0a6fdd9271f324a3381b67bf61417b23f736b85255bad47e
# Compliance: COMPLIANT
```

### Automated (CI)

The manifest is automatically generated and validated on:
- Push to main/develop branches
- Pull requests to main/develop
- Manual workflow dispatch

---

## Testing

### Test Suite Coverage

The test suite (`test_forensic_manifest.py`) includes 18 validation tests:

1. ✅ `test_manifest_exists` - Manifest file exists
2. ✅ `test_manifest_structure` - Required fields present
3. ✅ `test_manifest_version` - Version is valid
4. ✅ `test_manifest_freshness` - Less than 24 hours old
5. ✅ `test_evidence_count` - Count matches array length
6. ✅ `test_evidence_files_exist` - All listed files exist
7. ✅ `test_all_evidence_files_covered` - All files in manifest
8. ✅ `test_hash_validity` - All hashes are valid SHA-256
9. ✅ `test_hash_correctness` - Hashes match actual file contents
10. ✅ `test_merkle_root_validity` - Merkle root is valid
11. ✅ `test_merkle_root_correctness` - Merkle root correctly computed
12. ✅ `test_no_duplicate_hashes` - No hash collisions
13. ✅ `test_evidence_directory_path` - Correct directory path
14. ✅ `test_audit_report_exists` - Audit report generated
15. ✅ `test_audit_report_compliance` - Report shows COMPLIANT
16. ✅ `test_registry_exists` - Registry file exists
17. ✅ `test_registry_entry` - Registry contains current entry
18. ✅ `test_opa_policy_structure` - OPA policy has required rules

### Running Tests

```bash
# Run all tests
pytest 11_test_simulation/tests_compliance/test_forensic_manifest.py -v

# Run specific test
pytest 11_test_simulation/tests_compliance/test_forensic_manifest.py::TestForensicManifest::test_merkle_root_correctness -v

# Generate test report
pytest 11_test_simulation/tests_compliance/test_forensic_manifest.py \
       --json-report \
       --json-report-file=test_report.json
```

---

## Registry Tracking

### Registry Entry Schema

```yaml
registry_version: 1
entries:
  - timestamp: "2025-10-14T11:27:54.755769+00:00"
    merkle_root: "5dc0ac561ec9a82e0a6fdd9271f324a3381b67bf61417b23f736b85255bad47e"
    evidence_count: 3
    manifest_path: "02_audit_logging/evidence/forensic_manifest.yaml"
    audit_report: "23_compliance/reports/forensic_manifest_audit_20251014_112754.json"
    status: "COMPLIANT"
    build_hash: "b32c7573dda144dc"
```

### Registry Functions

- **Historical tracking**: Maintains up to 100 most recent entries
- **Build correlation**: Links manifest to specific build via `build_hash`
- **Compliance auditing**: Tracks compliance status over time
- **Report linkage**: Associates manifest with audit report

---

## Audit Report

### Report Schema

```json
{
  "report_type": "forensic_manifest_audit",
  "generated_at": "2025-10-14T11:27:54.757770+00:00",
  "manifest_version": 1,
  "manifest_merkle_root": "5dc0ac56...",
  "evidence_count": 3,
  "validation": {
    "all_files_hashed": true,
    "merkle_root_valid": true,
    "manifest_complete": true,
    "timestamp_valid": true
  },
  "evidence_files": [...],
  "compliance_status": "COMPLIANT"
}
```

### Compliance Status

- **COMPLIANT**: All validation checks passed
- **NON_COMPLIANT**: One or more validation checks failed

---

## Security Properties

### Tamper Evidence

✅ **File integrity**: Any modification to evidence files changes their SHA-256 hash
✅ **Manifest integrity**: Any change to manifest files list changes merkle root
✅ **Timestamp integrity**: Manifest age tracked and validated (< 24h)
✅ **Completeness**: All evidence files must be listed (no hidden files)

### Auditability

✅ **Deterministic**: Same evidence produces same manifest
✅ **Traceable**: Full chain from evidence → manifest → report → registry
✅ **Verifiable**: Independent verification via hash recomputation
✅ **Policy-enforced**: OPA prevents invalid manifests from passing CI

### Forensic Chain

```
Evidence Files
    ↓ (SHA-256 hash)
File Hashes
    ↓ (Concatenate + sort)
Merkle Root
    ↓ (Include in manifest)
Manifest YAML
    ↓ (Validate with OPA)
Policy Decision
    ↓ (Generate report)
Audit Report
    ↓ (Register entry)
Registry
    ↓ (Optional: Anchor)
Blockchain/IPFS
```

---

## Compliance Impact

### Standards Compliance

| Standard | Requirement | Manifest Support |
|----------|-------------|------------------|
| **GDPR Article 32** | Security of processing | ✅ Tamper-evident evidence |
| **ISO 27001** | Asset inventory | ✅ Complete file tracking |
| **SOC 2 Type II** | Audit trail | ✅ Deterministic manifest |
| **SSID Blueprint 42** | Forensic evidence | ✅ Merkle root anchoring |

### Audit Benefits

- **Zero trust verification**: Evidence integrity verifiable without trusting generator
- **Compliance automation**: OPA policy gates prevent non-compliant builds
- **Forensic readiness**: Manifest serves as legal evidence of system state
- **Supply chain security**: Detects unauthorized evidence file additions/removals

---

## Troubleshooting

### Issue: Manifest generation fails with "No evidence files found"

**Cause**: Evidence directory is empty or not yet created

**Solution**:
```bash
# Generate import resolution evidence first
python 02_audit_logging/anti_gaming/static_import_resolver.py

# Then generate manifest
python 02_audit_logging/evidence/forensic_manifest_generator.py
```

### Issue: OPA policy denies manifest (age > 24 hours)

**Cause**: Manifest is stale and needs regeneration

**Solution**:
```bash
# Regenerate manifest
python 02_audit_logging/evidence/forensic_manifest_generator.py
```

### Issue: Hash mismatch detected in tests

**Cause**: Evidence file was modified after manifest generation

**Solution**:
```bash
# Regenerate manifest to update hashes
python 02_audit_logging/evidence/forensic_manifest_generator.py

# Verify integrity
pytest 11_test_simulation/tests_compliance/test_forensic_manifest.py::TestForensicManifest::test_hash_correctness -v
```

### Issue: Registry entry missing or outdated

**Cause**: Manifest generator did not complete successfully

**Solution**:
```bash
# Check generator exit code
python 02_audit_logging/evidence/forensic_manifest_generator.py
echo $?  # Should be 0 for success

# Verify registry
cat 24_meta_orchestration/registry/forensic_manifest_registry.yaml
```

---

## Future Enhancements

### Phase 2: Blockchain Anchoring

- Automatic IPFS upload of manifest
- Ethereum/Polygon merkle root anchoring
- Timestamping service integration

### Phase 3: Multi-Evidence Support

- Extend to other evidence types (audit logs, test reports)
- Unified manifest for all forensic evidence
- Cross-reference validation

### Phase 4: Real-Time Monitoring

- Continuous evidence file monitoring
- Automatic manifest regeneration on changes
- Alerting for unauthorized modifications

---

## Maintenance

### Regular Tasks

**Daily** (automated via CI):
- Manifest generation on evidence changes
- OPA policy validation
- Test suite execution

**Weekly** (automated):
- Registry cleanup (keep last 100 entries)
- Audit report archival

**Monthly** (manual review):
- OPA policy review and updates
- Test coverage review
- Documentation updates

**Quarterly** (compliance audit):
- Full forensic chain verification
- Registry integrity audit
- Policy effectiveness review

---

## References

- [Forensic Manifest Generator](./forensic_manifest_generator.py)
- [OPA Policy](../../23_compliance/policies/opa/forensic_manifest_integrity.rego)
- [CI Workflow](../../.github/workflows/forensic_manifest_ci.yml)
- [Test Suite](../../11_test_simulation/tests_compliance/test_forensic_manifest.py)
- [Static Import Resolver Guide](./RESOLUTION_SUMMARY.md)

---

**Status**: ✅ Production Ready
**Next Review**: 2025-11-14
**Owner**: Security & Compliance Team
