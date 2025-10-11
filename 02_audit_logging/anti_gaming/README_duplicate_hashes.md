# SSID Anti-Gaming Module

## Overview

The `detect_duplicate_identity_hashes.py` module prevents reputation manipulation and gaming through duplicate identity detection in the SSID framework.

## Purpose

Scans all proof files (JSON/YAML/CSV) in `identity_score/` and `audit_logging/evidence/` directories to detect:
- **Hash collisions**: Identical cryptographic hashes (SHA256, SHA3-256, BLAKE2)
- **DID duplicates**: Same Decentralized Identifier used across multiple proofs

## Features

- ✅ **Multi-format support**: JSON, YAML, CSV
- ✅ **Regex-based detection**: Efficient pattern matching for hashes and DIDs
- ✅ **JSONL audit logs**: Append-only, WORM-compatible logging
- ✅ **Exit codes**: 0 = PASS, 2 = FAIL (policy violation)
- ✅ **Non-custodial**: Read-only operations, no PII processing

## Usage

### Command Line

```bash
python 02_audit_logging/anti_gaming/detect_duplicate_identity_hashes.py
```

### Programmatic

```python
from anti_gaming import build_index, detect_collisions, log_findings

# Build index of all identifiers
index = build_index()

# Detect collisions
collisions = detect_collisions(index)

# Log findings
status, results = log_findings(collisions)
```

## Output

### Audit Log Format

Location: `02_audit_logging/logs/anti_gaming_duplicate_hashes.jsonl`

```json
{
  "timestamp": "2025-10-07T10:23:33.229328Z",
  "component": "anti_gaming",
  "check": "duplicate_identity_hashes",
  "status": "PASS",
  "collision_count": 0,
  "collisions": []
}
```

### Console Output

```
[SCAN] Scanning for duplicate identity hashes and DIDs...
       Found 42 unique identifiers
[PASS] 0 duplicate identities detected.
```

When collisions are found:

```
[FAIL] 3 duplicate identities detected.

Collision details:
  - HASH: sha256:abc123def456... (2 files)
  - DID: did:example:user123 (3 files)
  ... and 1 more (see log)
```

## Testing

Test suite: `11_test_simulation/anti_gaming/test_detect_duplicate_identity_hashes.py`

```bash
# Run tests
pytest 11_test_simulation/anti_gaming/test_detect_duplicate_identity_hashes.py -v

# Coverage
pytest 11_test_simulation/anti_gaming/test_detect_duplicate_identity_hashes.py --cov
```

### Test Coverage

- ✅ Script execution and exit codes
- ✅ Log file creation and format validation
- ✅ Module import and function availability
- ✅ Empty directory handling (no false positives)
- ✅ Hash/DID extraction logic
- ✅ Collision detection algorithm
- ✅ Index structure validation
- ✅ File type support verification
- ✅ Regex pattern matching
- ✅ Log entry completeness

## CI Integration

Add to `.github/workflows/compliance_check.yml`:

```yaml
- name: Run Anti-Gaming duplicate identity check
  run: python 02_audit_logging/anti_gaming/detect_duplicate_identity_hashes.py
```

## Supported Patterns

### Hash Formats

- `sha256:[64 hex chars]`
- `sha3-256:[64 hex chars]`
- `sha512:[128 hex chars]`
- `blake2b:[64-128 hex chars]`

### DID Formats

- `did:method:identifier`
- Examples: `did:example:123abc`, `did:web:example.com`, `did:key:z6Mk...`

## Security & Compliance

- **Non-custodial**: Only reads existing files, no data modification
- **Read-only**: No write operations except audit logs
- **WORM-compatible**: Append-only logging for immutability
- **Privacy-preserving**: Processes hashes/DIDs, not PII
- **Defensive only**: Prevents gaming, does not facilitate attacks

## Exit Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 0    | PASS    | No collisions detected |
| 2    | FAIL    | Collisions found (policy violation) |

## License

MIT License ©2025 edubrainboost

## Author

edubrainboost — SSID Codex Engine
