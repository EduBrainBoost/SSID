# SoT Implementation Audit – Evidence Guide

This directory captures machine-verifiable evidence that each SoT rule
has a complete technical manifestation (Python, Rego, YAML, CLI, Tests)
and that artifacts are substantive (line thresholds + token checks).

- `sot_implementation_audit_report.json`: canonical machine report
- Thresholds: 100/100 overall and per rule
- Exit code on CI failure: 24 (Root-24-LOCK)

Run locally:

```bash
python 12_tooling/cli/sot_audit_verifier.py --json
```
