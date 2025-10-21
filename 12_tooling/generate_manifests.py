#!/usr/bin/env python3
"""Generate manifest.yaml files for all 24 roots"""

import os
from pathlib import Path

# Root directory definitions
ROOTS = [
    ("01_ai_layer", "AI Team", "ai_services", ["model_inference.py", "training_pipeline.py"]),
    ("02_audit_logging", "Compliance Team", "audit_logging", ["log_ingestion.py", "blockchain_anchor.py"]),
    ("03_core", "Core Engineering Team", "core_services", ["did_manager.py", "vc_issuer.py", "proof_aggregator.py"]),
    ("04_deployment", "DevOps Team", "deployment", ["deploy.sh", "rollback.sh"]),
    ("05_documentation", "Documentation Team", "docs", ["build_docs.sh"]),
    ("06_data_pipeline", "Data Engineering Team", "data_pipeline", ["ingest.py", "transform.py", "validate.py"]),
    ("07_governance_legal", "Legal Team", "governance", ["compliance_check.py"]),
    ("08_identity_score", "Risk Engineering Team", "scoring", ["risk_engine.py", "reputation_calculator.py"]),
    ("09_meta_identity", "Identity Team", "identity", ["did_service.py", "credential_vault.py"]),
    ("10_interoperability", "Interoperability Team", "interop", ["bridge_service.py", "adapter_registry.py"]),
    ("11_test_simulation", "QA Team", "tests", ["pytest.ini", "run_tests.sh"]),
    ("12_tooling", "DevOps Team", "tools", ["cli.py"]),
    ("13_ui_layer", "Frontend Team", "ui", ["src/index.tsx", "webpack.config.js"]),
    ("14_zero_time_auth", "Security Team", "auth", ["auth_service.py", "kyc_gateway.py", "zkp_verifier.py"]),
    ("15_infra", "Infrastructure Team", "infra", ["database.tf", "cache.tf", "storage.tf"]),
    ("16_codex", "Architecture Team", "codex", ["schema_registry.py", "validator.py"]),
    ("17_observability", "SRE Team", "observability", ["metrics_collector.py", "tracer.py"]),
    ("18_data_layer", "Data Team", "data_layer", ["models.py", "migrations/"]),
    ("19_adapters", "Integration Team", "adapters", ["cosmos_adapter.py", "polkadot_adapter.py"]),
    ("20_foundation", "Tokenomics Team", "foundation", ["token_contract.sol", "governance.sol"]),
    ("21_post_quantum_crypto", "Cryptography Team", "crypto", ["pqc_keygen.py", "signing_service.py"]),
    ("22_datasets", "Data Science Team", "datasets", ["synthetic_generator.py", "catalog.py"]),
    ("23_compliance", "Compliance Team", "compliance", ["policies/", "tests/"]),
    ("24_meta_orchestration", "Platform Team", "orchestration", ["workflow_engine.py", "registry_service.py"]),
]

MANIFEST_TEMPLATE = """apiVersion: ssid/implementation/v1
kind: Manifest
metadata:
  name: {root_name}
  version: "0.1.0"
  description: "Implementation manifest for {root_display}"
  created: "2025-10-13"
  status: bootstrap

spec:
  maintainer: "{maintainer}"

  entry_points:
    primary: "{primary_entry}"
    secondary: {secondary_entries}

  dependencies:
    runtime:
      python: ">=3.11"

    build:
      - setuptools
      - wheel

    test:
      - pytest
      - pytest-cov

  build:
    command: "python -m pip install -e ."
    artifacts:
      - dist/
      - build/

  test:
    command: "pytest tests/ --cov={module_name}"
    coverage_threshold: 80

  deployment:
    environments:
      - dev
      - stage
      - prod

    health_check:
      enabled: true
      endpoint: "/health"
      interval_seconds: 30

  observability:
    metrics:
      enabled: true
      port: 9090

    logging:
      level: INFO
      format: json

    tracing:
      enabled: true
      sample_rate: 0.1

  compliance:
    safe_fix: true
    root_24_lock: enforced
    pii_policy: hash_only
"""

def generate_manifest(root_name, maintainer, module_name, entry_points):
    """Generate manifest.yaml content for a root"""
    primary = entry_points[0] if entry_points else "N/A"
    secondary = entry_points[1:] if len(entry_points) > 1 else []

    # Format secondary entries as YAML list
    if secondary:
        secondary_str = "\\n" + "\\n".join(f"      - {entry}" for entry in secondary)
    else:
      secondary_str = " []"

    root_display = root_name.replace("_", " ").title()

    content = MANIFEST_TEMPLATE.format(
        root_name=root_name.replace("_", "-"),
        root_display=root_display,
        maintainer=maintainer,
        primary_entry=primary,
        secondary_entries=secondary_str,
        module_name=module_name
    )

    return content

def main():
    """Generate all manifest.yaml files"""
    base_path = Path(__file__).parent.parent

    for root_name, maintainer, module_name, entry_points in ROOTS:
        manifest_path = base_path / root_name / "manifest.yaml"

        content = generate_manifest(root_name, maintainer, module_name, entry_points)

        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[OK] Created: {manifest_path}")

    print(f"\\nSuccessfully created {len(ROOTS)} manifest.yaml files!")

if __name__ == "__main__":
    main()
