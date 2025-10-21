#!/usr/bin/env python3
"""
Coverage Analysis: Master-Definition Rules vs 5 SoT Artefacts
==============================================================
Prüft, welche der 201 MD-* Regeln bereits in den 5 Artefakten vorhanden sind.
"""

import json
from pathlib import Path
from typing import Dict, List, Set

# Basis-Pfade
REPO_ROOT = Path(__file__).parent.parent.parent
ARTEFACTS = {
    "core": REPO_ROOT / "03_core" / "validators" / "sot" / "sot_validator_core.py",
    "rego": REPO_ROOT / "23_compliance" / "policies" / "sot" / "sot_policy.rego",
    "contract": REPO_ROOT / "16_codex" / "contracts" / "sot" / "sot_contract.yaml",
    "cli": REPO_ROOT / "12_tooling" / "cli" / "sot_validator.py",
    "tests": REPO_ROOT / "11_test_simulation" / "tests_compliance" / "test_sot_validator.py",
}

# Alle 201 MD-* Regeln (extrahiert aus Master-Definition)
MD_RULES = {
    # KATEGORIE 1: STRUKTURREGELN (10 Regeln)
    "MD-STRUCT-001": {"desc": "24 Root-Ordner", "maps_to": "AR001"},
    "MD-STRUCT-002": {"desc": "16 Shards pro Root", "maps_to": "AR002"},
    "MD-STRUCT-003": {"desc": "24×16=384 Charts", "maps_to": "AR003"},
    "MD-STRUCT-004": {"desc": "chart.yaml MUSS existieren", "maps_to": "AR004"},
    "MD-STRUCT-005": {"desc": "values.yaml MUSS existieren", "maps_to": "AR005"},
    "MD-STRUCT-006": {"desc": "README.md MUSS existieren", "maps_to": "AR006"},
    "MD-STRUCT-007": {"desc": "Root-Namen Pattern {NR}_{NAME}", "maps_to": "AR009"},
    "MD-STRUCT-008": {"desc": "Shard-Namen Pattern Shard_{NR}_{NAME}", "maps_to": "AR008"},
    "MD-STRUCT-009": {"desc": "Pfad {ROOT}/shards/{SHARD}/chart.yaml", "maps_to": None},
    "MD-STRUCT-010": {"desc": "Pfad .../implementations/{IMPL}/manifest.yaml", "maps_to": None},

    # KATEGORIE 2: CHART.YAML (50 Regeln)
    "MD-CHART-001": {"desc": "chart.yaml metadata.shard_id", "maps_to": "CS001"},
    "MD-CHART-002": {"desc": "chart.yaml metadata.version", "maps_to": "CS001"},
    "MD-CHART-003": {"desc": "chart.yaml metadata.status", "maps_to": "CS001"},
    "MD-CHART-004": {"desc": "chart.yaml governance.owner.team", "maps_to": "CS002"},
    "MD-CHART-005": {"desc": "chart.yaml governance.owner.lead", "maps_to": "CS002"},
    "MD-CHART-006": {"desc": "chart.yaml governance.owner.contact", "maps_to": "CS002"},
    "MD-CHART-007": {"desc": "chart.yaml governance.reviewers", "maps_to": "CS002"},
    "MD-CHART-008": {"desc": "chart.yaml governance.change_process", "maps_to": "CS002"},
    "MD-CHART-009": {"desc": "chart.yaml capabilities.MUST", "maps_to": "CS003"},
    "MD-CHART-010": {"desc": "chart.yaml capabilities.SHOULD", "maps_to": "CS003"},
    "MD-CHART-011": {"desc": "chart.yaml capabilities.HAVE", "maps_to": "CS003"},
    "MD-CHART-012": {"desc": "chart.yaml constraints.pii_storage=forbidden", "maps_to": "CS004"},
    "MD-CHART-013": {"desc": "chart.yaml constraints.data_policy=hash_only", "maps_to": "CS004"},
    "MD-CHART-014": {"desc": "chart.yaml constraints.custody=non_custodial", "maps_to": "CS004"},
    "MD-CHART-015": {"desc": "chart.yaml enforcement.static_analysis", "maps_to": "CS005"},
    "MD-CHART-016": {"desc": "chart.yaml enforcement.runtime_checks", "maps_to": "CS005"},
    "MD-CHART-017": {"desc": "chart.yaml enforcement.audit", "maps_to": "CS005"},
    "MD-CHART-018": {"desc": "chart.yaml interfaces.contracts (OpenAPI)", "maps_to": "CS006"},
    "MD-CHART-019": {"desc": "chart.yaml interfaces.data_schemas (JSON)", "maps_to": "CS006"},
    "MD-CHART-020": {"desc": "chart.yaml interfaces.authentication=mTLS", "maps_to": "KP006"},
    "MD-CHART-021": {"desc": "chart.yaml dependencies.required", "maps_to": "CS007"},
    "MD-CHART-022": {"desc": "chart.yaml dependencies.optional", "maps_to": "CS007"},
    "MD-CHART-023": {"desc": "chart.yaml compatibility.semver", "maps_to": "VG001"},
    "MD-CHART-024": {"desc": "chart.yaml compatibility.core_min_version", "maps_to": None},
    "MD-CHART-025": {"desc": "chart.yaml implementations.default", "maps_to": "CS008"},
    "MD-CHART-026": {"desc": "chart.yaml implementations.available", "maps_to": "CS008"},
    "MD-CHART-027": {"desc": "chart.yaml conformance.test_framework", "maps_to": "CS009"},
    "MD-CHART-028": {"desc": "chart.yaml conformance.contract_tests", "maps_to": "CS009"},
    "MD-CHART-029": {"desc": "chart.yaml orchestration.workflows", "maps_to": None},
    "MD-CHART-030": {"desc": "chart.yaml testing.unit", "maps_to": "CS009"},
    "MD-CHART-031": {"desc": "chart.yaml testing.integration", "maps_to": "CS009"},
    "MD-CHART-032": {"desc": "chart.yaml testing.contract", "maps_to": "CS009"},
    "MD-CHART-033": {"desc": "chart.yaml testing.e2e", "maps_to": "CS009"},
    "MD-CHART-034": {"desc": "chart.yaml documentation.auto_generate", "maps_to": "KP010"},
    "MD-CHART-035": {"desc": "chart.yaml documentation.manual", "maps_to": "KP010"},
    "MD-CHART-036": {"desc": "chart.yaml observability.metrics.prometheus", "maps_to": "CS010"},
    "MD-CHART-037": {"desc": "chart.yaml observability.tracing.jaeger", "maps_to": "CS010"},
    "MD-CHART-038": {"desc": "chart.yaml observability.logging.loki", "maps_to": "CS010"},
    "MD-CHART-039": {"desc": "chart.yaml observability.logging.pii_redaction=true", "maps_to": "MS006"},
    "MD-CHART-040": {"desc": "chart.yaml observability.alerting", "maps_to": "CS010"},
    "MD-CHART-041": {"desc": "chart.yaml evidence.strategy=hash_ledger_with_anchoring", "maps_to": "KP005"},
    "MD-CHART-042": {"desc": "chart.yaml evidence.anchoring.chains=[ethereum,polygon]", "maps_to": "TS001"},
    "MD-CHART-043": {"desc": "chart.yaml security.threat_model", "maps_to": "CS011"},
    "MD-CHART-044": {"desc": "chart.yaml security.secrets_management=15_infra/vault", "maps_to": "CP012"},
    "MD-CHART-045": {"desc": "chart.yaml security.encryption (at_rest, in_transit)", "maps_to": None},
    "MD-CHART-046": {"desc": "chart.yaml deployment.strategy=blue-green|canary", "maps_to": "DC001"},
    "MD-CHART-047": {"desc": "chart.yaml deployment.environments=[dev,staging,production]", "maps_to": "DC002"},
    "MD-CHART-048": {"desc": "chart.yaml resources.compute", "maps_to": None},
    "MD-CHART-049": {"desc": "chart.yaml resources.autoscaling", "maps_to": "KP009"},
    "MD-CHART-050": {"desc": "chart.yaml roadmap.upcoming", "maps_to": None},

    # KATEGORIE 3: MANIFEST.YAML (50 Regeln)
    "MD-MANIFEST-001": {"desc": "manifest.yaml metadata.implementation_id", "maps_to": "MS001"},
    "MD-MANIFEST-002": {"desc": "manifest.yaml metadata.implementation_version", "maps_to": "MS001"},
    "MD-MANIFEST-003": {"desc": "manifest.yaml metadata.chart_version", "maps_to": "MS001"},
    "MD-MANIFEST-004": {"desc": "manifest.yaml metadata.maturity", "maps_to": None},
    "MD-MANIFEST-005": {"desc": "manifest.yaml technology_stack.language.name", "maps_to": "MS002"},
    "MD-MANIFEST-006": {"desc": "manifest.yaml technology_stack.language.version", "maps_to": "MS002"},
    "MD-MANIFEST-007": {"desc": "manifest.yaml technology_stack.frameworks", "maps_to": "MS002"},
    "MD-MANIFEST-008": {"desc": "manifest.yaml technology_stack.testing", "maps_to": "MS002"},
    "MD-MANIFEST-009": {"desc": "manifest.yaml technology_stack.linting_formatting", "maps_to": None},
    "MD-MANIFEST-010": {"desc": "manifest.yaml artifacts.source_code.location", "maps_to": "MS003"},
    "MD-MANIFEST-011": {"desc": "manifest.yaml artifacts.source_code.structure", "maps_to": "MS003"},
    "MD-MANIFEST-012": {"desc": "manifest.yaml artifacts.configuration.location", "maps_to": None},
    "MD-MANIFEST-013": {"desc": "manifest.yaml artifacts.models.location (AI/ML)", "maps_to": None},
    "MD-MANIFEST-014": {"desc": "manifest.yaml artifacts.protocols.location (gRPC)", "maps_to": None},
    "MD-MANIFEST-015": {"desc": "manifest.yaml artifacts.tests.location", "maps_to": None},
    "MD-MANIFEST-016": {"desc": "manifest.yaml artifacts.documentation.location", "maps_to": None},
    "MD-MANIFEST-017": {"desc": "manifest.yaml artifacts.scripts.location", "maps_to": None},
    "MD-MANIFEST-018": {"desc": "manifest.yaml artifacts.docker.files=[Dockerfile,docker-compose.yml]", "maps_to": None},
    "MD-MANIFEST-019": {"desc": "manifest.yaml dependencies.python_packages=requirements.txt", "maps_to": "MS004"},
    "MD-MANIFEST-020": {"desc": "manifest.yaml dependencies.development_packages", "maps_to": "MS004"},
    "MD-MANIFEST-021": {"desc": "manifest.yaml dependencies.system_dependencies", "maps_to": "MS004"},
    "MD-MANIFEST-022": {"desc": "manifest.yaml dependencies.external_services", "maps_to": "MS004"},
    "MD-MANIFEST-023": {"desc": "manifest.yaml build.commands", "maps_to": None},
    "MD-MANIFEST-024": {"desc": "manifest.yaml build.docker", "maps_to": None},
    "MD-MANIFEST-025": {"desc": "manifest.yaml deployment.kubernetes.manifests_location", "maps_to": None},
    "MD-MANIFEST-026": {"desc": "manifest.yaml deployment.helm.chart_location", "maps_to": None},
    "MD-MANIFEST-027": {"desc": "manifest.yaml deployment.environment_variables", "maps_to": None},
    "MD-MANIFEST-028": {"desc": "manifest.yaml testing.unit_tests.command", "maps_to": "MS005"},
    "MD-MANIFEST-029": {"desc": "manifest.yaml testing.unit_tests.coverage_target>=80", "maps_to": None},
    "MD-MANIFEST-030": {"desc": "manifest.yaml testing.integration_tests", "maps_to": "MS005"},
    "MD-MANIFEST-031": {"desc": "manifest.yaml testing.contract_tests", "maps_to": "MS005"},
    "MD-MANIFEST-032": {"desc": "manifest.yaml testing.security_tests", "maps_to": None},
    "MD-MANIFEST-033": {"desc": "manifest.yaml testing.performance_tests", "maps_to": None},
    "MD-MANIFEST-034": {"desc": "manifest.yaml observability.metrics.exporter=prometheus", "maps_to": "KP007"},
    "MD-MANIFEST-035": {"desc": "manifest.yaml observability.tracing.exporter=jaeger", "maps_to": "KP007"},
    "MD-MANIFEST-036": {"desc": "manifest.yaml observability.logging.format=json", "maps_to": None},
    "MD-MANIFEST-037": {"desc": "manifest.yaml observability.logging.pii_redaction=true", "maps_to": "MS006"},
    "MD-MANIFEST-038": {"desc": "manifest.yaml observability.health_checks.liveness", "maps_to": None},
    "MD-MANIFEST-039": {"desc": "manifest.yaml observability.health_checks.readiness", "maps_to": None},
    "MD-MANIFEST-040": {"desc": "manifest.yaml development.setup", "maps_to": None},
    "MD-MANIFEST-041": {"desc": "manifest.yaml development.local_development", "maps_to": None},
    "MD-MANIFEST-042": {"desc": "manifest.yaml development.pre_commit_hooks", "maps_to": None},
    "MD-MANIFEST-043": {"desc": "manifest.yaml compliance.non_custodial_enforcement", "maps_to": "CP001"},
    "MD-MANIFEST-044": {"desc": "manifest.yaml compliance.gdpr_compliance", "maps_to": "CP005"},
    "MD-MANIFEST-045": {"desc": "manifest.yaml compliance.bias_fairness (AI/ML)", "maps_to": "CP008"},
    "MD-MANIFEST-046": {"desc": "manifest.yaml performance.baseline_benchmarks", "maps_to": None},
    "MD-MANIFEST-047": {"desc": "manifest.yaml performance.optimization_targets", "maps_to": None},
    "MD-MANIFEST-048": {"desc": "manifest.yaml performance.resource_requirements", "maps_to": None},
    "MD-MANIFEST-049": {"desc": "manifest.yaml changelog.location=CHANGELOG.md", "maps_to": None},
    "MD-MANIFEST-050": {"desc": "manifest.yaml support.contacts", "maps_to": None},

    # KATEGORIE 4: KRITISCHE POLICIES (32 Regeln)
    "MD-POLICY-001": {"desc": "NIEMALS Rohdaten von PII speichern", "maps_to": "CP001"},
    "MD-POLICY-002": {"desc": "Nur Hash SHA3-256", "maps_to": "CP002"},
    "MD-POLICY-003": {"desc": "Tenant-spezifische Peppers", "maps_to": "CP003"},
    "MD-POLICY-004": {"desc": "Raw Data Retention=0s", "maps_to": "CP004"},
    "MD-POLICY-005": {"desc": "Semgrep blockiert PII-Storage", "maps_to": "CP001"},
    "MD-POLICY-006": {"desc": "Runtime PII-Detector blockiert", "maps_to": "CP007"},
    "MD-POLICY-007": {"desc": "Hash-Algorithmus=SHA3-256", "maps_to": "CP002"},
    "MD-POLICY-008": {"desc": "Pepper-Strategie=per_tenant", "maps_to": "CP003"},
    "MD-POLICY-009": {"desc": "Hashing deterministisch", "maps_to": None},
    "MD-POLICY-010": {"desc": "Right to Erasure via Hash-Rotation", "maps_to": "CP005"},
    "MD-POLICY-011": {"desc": "Data Portability JSON-Export", "maps_to": "CP006"},
    "MD-POLICY-012": {"desc": "Purpose Limitation erzwingen", "maps_to": None},
    "MD-POLICY-013": {"desc": "PII Redaction in Logs", "maps_to": "CP007"},
    "MD-POLICY-014": {"desc": "Bias Testing für AI/ML", "maps_to": "CP008"},
    "MD-POLICY-015": {"desc": "Fairness-Metrics", "maps_to": "CP008"},
    "MD-POLICY-016": {"desc": "Quarterly Bias Audits", "maps_to": "CP008"},
    "MD-POLICY-017": {"desc": "Model Cards transparent", "maps_to": "CP008"},
    "MD-POLICY-018": {"desc": "Bias-Mitigation verpflichtend", "maps_to": "CP008"},
    "MD-POLICY-019": {"desc": "Evidence Hash-Ledger + Blockchain", "maps_to": "CP009"},
    "MD-POLICY-020": {"desc": "WORM-Storage", "maps_to": "CP010"},
    "MD-POLICY-021": {"desc": "Retention 10 Jahre", "maps_to": "CP010"},
    "MD-POLICY-022": {"desc": "Ethereum + Polygon Anchoring", "maps_to": "TS001"},
    "MD-POLICY-023": {"desc": "Hourly Anchoring", "maps_to": None},
    "MD-POLICY-024": {"desc": "Vault für Secrets", "maps_to": "CP012"},
    "MD-POLICY-025": {"desc": "Secrets Rotation 90d", "maps_to": "CP012"},
    "MD-POLICY-026": {"desc": "NIEMALS Secrets in Git", "maps_to": "CP011"},
    "MD-POLICY-027": {"desc": "Encryption AES-256-GCM", "maps_to": None},
    "MD-POLICY-028": {"desc": "TLS 1.3 in-transit", "maps_to": None},
    "MD-POLICY-029": {"desc": "Semver", "maps_to": "VG001"},
    "MD-POLICY-030": {"desc": "Breaking Changes Migration Guide", "maps_to": "VG002"},
    "MD-POLICY-031": {"desc": "Deprecations 180d notice", "maps_to": "VG003"},
    "MD-POLICY-032": {"desc": "RFC für MUST-Changes", "maps_to": "VG004"},

    # KATEGORIE 5: GOVERNANCE (12 Regeln)
    "MD-GOV-001": {"desc": "Jeder Shard Owner", "maps_to": "VG005"},
    "MD-GOV-002": {"desc": "Owner verantwortlich", "maps_to": "VG005"},
    "MD-GOV-003": {"desc": "Architecture Board review chart.yaml", "maps_to": "VG006"},
    "MD-GOV-004": {"desc": "Architecture Board genehmigt Breaking Changes", "maps_to": "VG007"},
    "MD-GOV-005": {"desc": "Compliance Team prüft Policies", "maps_to": None},
    "MD-GOV-006": {"desc": "Compliance Team genehmigt Constraints", "maps_to": None},
    "MD-GOV-007": {"desc": "Security Team Threat Modeling", "maps_to": None},
    "MD-GOV-008": {"desc": "Change-Prozess 7 Schritte", "maps_to": None},
    "MD-GOV-009": {"desc": "SHOULD→MUST 90d + 99.5% SLA", "maps_to": None},
    "MD-GOV-010": {"desc": "SHOULD→MUST 95% Contract Test Coverage", "maps_to": None},
    "MD-GOV-011": {"desc": "HAVE→SHOULD Feature complete + Beta + Doku", "maps_to": None},
    "MD-GOV-012": {"desc": "MUST→Deprecated 180d + Migration + Compat", "maps_to": "VG003"},

    # KATEGORIE 6: KERNPRINZIPIEN (23 Regeln)
    "MD-PRINC-001": {"desc": "Contract-First", "maps_to": "KP001"},
    "MD-PRINC-002": {"desc": "Separation of Concerns (SoT vs Impl)", "maps_to": "KP002"},
    "MD-PRINC-003": {"desc": "Multi-Implementation Support", "maps_to": "KP003"},
    "MD-PRINC-004": {"desc": "384 Charts deterministisch", "maps_to": "KP004"},
    "MD-PRINC-005": {"desc": "Hash, Log, Anchor alles", "maps_to": "KP005"},
    "MD-PRINC-006": {"desc": "mTLS für intern", "maps_to": "KP006"},
    "MD-PRINC-007": {"desc": "RBAC für Zugriffe", "maps_to": None},
    "MD-PRINC-008": {"desc": "PII-Detection Laufzeit", "maps_to": "CP007"},
    "MD-PRINC-009": {"desc": "Continuous Vuln Scanning", "maps_to": None},
    "MD-PRINC-010": {"desc": "Prometheus Metrics", "maps_to": "KP007"},
    "MD-PRINC-011": {"desc": "Jaeger Tracing", "maps_to": "KP007"},
    "MD-PRINC-012": {"desc": "Loki Logging + PII-Redaction", "maps_to": "KP007"},
    "MD-PRINC-013": {"desc": "AlertManager", "maps_to": None},
    "MD-PRINC-014": {"desc": "Fairness-Metrics", "maps_to": "KP008"},
    "MD-PRINC-015": {"desc": "Quarterly Bias Audits", "maps_to": "KP008"},
    "MD-PRINC-016": {"desc": "Model Cards", "maps_to": "KP008"},
    "MD-PRINC-017": {"desc": "HPA", "maps_to": "KP009"},
    "MD-PRINC-018": {"desc": "Load Balancing", "maps_to": None},
    "MD-PRINC-019": {"desc": "Caching-Strategien", "maps_to": None},
    "MD-PRINC-020": {"desc": "Performance-Benchmarks Gates", "maps_to": None},
    "MD-PRINC-021": {"desc": "Doku aus Contracts generiert", "maps_to": "KP010"},
    "MD-PRINC-022": {"desc": "OpenAPI → Swagger UI", "maps_to": "KP010"},
    "MD-PRINC-023": {"desc": "JSON-Schema → json-schema-for-humans", "maps_to": "KP010"},

    # KATEGORIE 7: EXTENSIONS v1.1.1 (24 Regeln)
    "MD-EXT-001": {"desc": "UK ICO GDPR mandatory", "maps_to": "CE001"},
    "MD-EXT-002": {"desc": "UK DPA 2018 alignment", "maps_to": "CE001"},
    "MD-EXT-003": {"desc": "UK DPO contact records", "maps_to": "CE001"},
    "MD-EXT-004": {"desc": "Singapore MAS PDPA mandatory", "maps_to": "CE001"},
    "MD-EXT-005": {"desc": "Singapore data_breach_notification", "maps_to": "CE001"},
    "MD-EXT-006": {"desc": "Singapore consent_purposes_documented", "maps_to": "CE001"},
    "MD-EXT-007": {"desc": "Japan JFSA APPI mandatory", "maps_to": "CE001"},
    "MD-EXT-008": {"desc": "Japan cross_border_transfer_rules", "maps_to": "CE001"},
    "MD-EXT-009": {"desc": "Australia Privacy Act mandatory", "maps_to": "CE001"},
    "MD-EXT-010": {"desc": "Australia APP11 security", "maps_to": "CE001"},
    "MD-EXT-011": {"desc": "OPA has_substr()", "maps_to": "CE002"},
    "MD-EXT-012": {"desc": "OPA string_similarity()", "maps_to": None},
    "MD-EXT-013": {"desc": "CI schedule 15 3 * * * daily sanctions", "maps_to": "CE003"},
    "MD-EXT-014": {"desc": "CI schedule 0 0 1 */3 * quarterly audit", "maps_to": None},
    "MD-EXT-015": {"desc": "CI actions/upload-artifact@v4", "maps_to": None},
    "MD-EXT-016": {"desc": "Build entities_to_check.json vor OPA", "maps_to": "CE004"},
    "MD-EXT-017": {"desc": "Sanctions max_age_hours: 24", "maps_to": "CE005"},
    "MD-EXT-018": {"desc": "Sanctions sha256 Hash", "maps_to": None},
    "MD-EXT-019": {"desc": "incident_response_plan.md pro Root", "maps_to": "CE006"},
    "MD-EXT-020": {"desc": "NIEMALS .ipynb committen", "maps_to": "CE007"},
    "MD-EXT-021": {"desc": "NIEMALS .parquet committen", "maps_to": "CE007"},
    "MD-EXT-022": {"desc": "NIEMALS .sqlite committen", "maps_to": "CE007"},
    "MD-EXT-023": {"desc": "NIEMALS .db committen", "maps_to": "CE007"},
    "MD-EXT-024": {"desc": "OPA repo_scan.json", "maps_to": "CE008"},
}

def analyze_coverage():
    """Analysiert Coverage der MD-* Regeln"""

    # Kategorisieren
    mapped_to_existing = []
    not_mapped = []

    for rule_id, info in MD_RULES.items():
        if info["maps_to"]:
            mapped_to_existing.append((rule_id, info["maps_to"], info["desc"]))
        else:
            not_mapped.append((rule_id, info["desc"]))

    # Statistiken
    print("\n" + "="*80)
    print("COVERAGE ANALYSIS: Master-Definition vs Existing Rules")
    print("="*80)

    print(f"\nTotal MD-* Rules: {len(MD_RULES)}")
    print(f"Mapped to existing rules: {len(mapped_to_existing)}")
    print(f"NOT mapped (truly new/granular): {len(not_mapped)}")

    # Save to JSON first (avoid console encoding issues)
    # JSON Export
    report = {
        "total_md_rules": len(MD_RULES),
        "mapped_to_existing": len(mapped_to_existing),
        "not_mapped": len(not_mapped),
        "coverage_percentage": round(len(mapped_to_existing) / len(MD_RULES) * 100, 2),
        "mapped_rules": [{"md_rule": r[0], "maps_to": r[1], "desc": r[2]} for r in sorted(mapped_to_existing)],
        "unmapped_rules": [{"md_rule": r[0], "desc": r[1]} for r in sorted(not_mapped)],
    }

    output_file = REPO_ROOT / "02_audit_logging" / "reports" / "md_coverage_analysis.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "-"*80)
    print("MAPPED TO EXISTING RULES (already covered):")
    print("-"*80)
    for md_rule, maps_to, desc in sorted(mapped_to_existing):
        # Avoid Unicode in console output
        print(f"{md_rule:20} => {maps_to:10} | {desc}")

    print("\n" + "-"*80)
    print("NOT MAPPED (new/granular rules needing integration):")
    print("-"*80)
    for md_rule, desc in sorted(not_mapped):
        print(f"{md_rule:20} | {desc}")

    print(f"\n[OK] Coverage report saved to: {output_file}")
    print(f"\n[STATS] Coverage: {report['coverage_percentage']}%")
    print(f"   - Existing rules cover: {len(mapped_to_existing)} MD-* rules")
    print(f"   - Need integration: {len(not_mapped)} NEW granular rules")

    return report

if __name__ == "__main__":
    analyze_coverage()
