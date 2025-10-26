
# SSID Meta Orchestrator (MAOS)

Dieses Modul fährt beim Start alle relevanten Subsysteme hoch (validieren, compliance prüfen, testen, registrieren, auditieren) und erzeugt eine einheitliche State-Matrix sowie Scorecards. Es ist deterministisch, CI-fähig und Root-24-LOCK-konform.

## CLI
```bash
export SSID_REPO_ROOT=./
python 12_tooling/cli/meta_cli.py --boot
python 12_tooling/cli/meta_cli.py --status
```

## Artefakte
- `24_meta_orchestration/meta_orchestrator.py`
- `16_codex/contracts/meta/meta_pipeline.yaml`
- `23_compliance/policies/orchestrator/orchestrator_policy.rego`
- `03_core/validators/meta_state_validator.py`
- `11_test_simulation/tests_meta/test_meta_orchestrator.py`
- Reports unter `02_audit_logging/reports/*`
