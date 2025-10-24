#!/usr/bin/env python3
"""
Add 50 Enforcement Layer Rules to all_4_sot_semantic_rules.json
Generated: 2025-10-24
Purpose: Integrate 5-layer enforcement architecture as checkable rules
"""

import json
from datetime import datetime
from pathlib import Path

def main():
    # Read existing rules
    input_file = Path(__file__).parent / 'all_4_sot_semantic_rules.json'
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"[INFO] Current rules: {data['total_rules']}")

    # Define 50 new enforcement layer rules
    rule_templates = [
        # Layer 1: Crypto (9001-9010)
        {'id': 9001, 'category': 'ENFORCEMENT_LAYER_1_CRYPTO', 'severity': 'CRITICAL', 'desc': 'Post-Quantum Crypto Backend (Kyber768/Dilithium3) MUST exist', 'ref': '21_post_quantum_crypto/pqc_backend.py', 'method': 'file_exists'},
        {'id': 9002, 'category': 'ENFORCEMENT_LAYER_1_CRYPTO', 'severity': 'CRITICAL', 'desc': 'SHA-256 Hash-Ledger MUST exist for all SoT rules', 'ref': 'all_4_sot_semantic_rules.json contains reference_hash field', 'method': 'json_field_check'},
        {'id': 9003, 'category': 'ENFORCEMENT_LAYER_1_CRYPTO', 'severity': 'CRITICAL', 'desc': 'Merkle-Root anchoring configuration MUST be defined', 'ref': 'Blueprint specifies Ethereum/Polygon anchoring', 'method': 'spec_compliance'},
        {'id': 9004, 'category': 'ENFORCEMENT_LAYER_1_CRYPTO', 'severity': 'CRITICAL', 'desc': 'WORM storage path MUST exist for audit logs', 'ref': '02_audit_logging/storage/worm/immutable_store/', 'method': 'directory_exists'},
        {'id': 9005, 'category': 'ENFORCEMENT_LAYER_1_CRYPTO', 'severity': 'HIGH', 'desc': 'PQC signature verification MUST be available', 'ref': '21_post_quantum_crypto/ implements signature verification', 'method': 'module_import_check'},
        {'id': 9006, 'category': 'ENFORCEMENT_LAYER_1_CRYPTO', 'severity': 'HIGH', 'desc': 'Hash chain integrity MUST be verifiable', 'ref': '24_meta_orchestration/registry/locks/hash_chain.json', 'method': 'file_exists'},
        {'id': 9007, 'category': 'ENFORCEMENT_LAYER_1_CRYPTO', 'severity': 'MEDIUM', 'desc': 'Blockchain anchoring frequency MUST be documented', 'ref': 'Blueprint: hourly anchoring to Ethereum/Polygon', 'method': 'documentation_check'},
        {'id': 9008, 'category': 'ENFORCEMENT_LAYER_1_CRYPTO', 'severity': 'MEDIUM', 'desc': 'Encryption-at-rest MUST be configured for sensitive data', 'ref': 'Blueprint: AES-256-GCM at-rest', 'method': 'config_check'},
        {'id': 9009, 'category': 'ENFORCEMENT_LAYER_1_CRYPTO', 'severity': 'MEDIUM', 'desc': 'Encryption-in-transit MUST use TLS 1.3', 'ref': 'Blueprint: TLS 1.3 for all connections', 'method': 'config_check'},
        {'id': 9010, 'category': 'ENFORCEMENT_LAYER_1_CRYPTO', 'severity': 'LOW', 'desc': 'Quantum-safe migration plan MUST be documented', 'ref': '21_post_quantum_crypto/migration_roadmap.md', 'method': 'file_exists'},

        # Layer 2: Policy (9011-9020)
        {'id': 9011, 'category': 'ENFORCEMENT_LAYER_2_POLICY', 'severity': 'CRITICAL', 'desc': 'OPA Rego policy MUST contain >= 4723 rules', 'ref': '23_compliance/policies/sot/sot_policy.rego', 'method': 'rule_count >= 4723'},
        {'id': 9012, 'category': 'ENFORCEMENT_LAYER_2_POLICY', 'severity': 'CRITICAL', 'desc': 'CI gates MUST exit with code 24 on structure violations', 'ref': '24_meta_orchestration/triggers/ci/gates/structure_lock_l3.py', 'method': 'exit_code_check'},
        {'id': 9013, 'category': 'ENFORCEMENT_LAYER_2_POLICY', 'severity': 'CRITICAL', 'desc': 'Pre-commit hooks MUST validate structure before commit', 'ref': '12_tooling/hooks/pre_commit/structure_validation.sh', 'method': 'file_exists'},
        {'id': 9014, 'category': 'ENFORCEMENT_LAYER_2_POLICY', 'severity': 'CRITICAL', 'desc': 'Root-24-LOCK enforcer MUST be active', 'ref': '23_compliance/policies/root_24_lock_enforcer.rego', 'method': 'file_exists'},
        {'id': 9015, 'category': 'ENFORCEMENT_LAYER_2_POLICY', 'severity': 'HIGH', 'desc': 'Static analysis hooks MUST scan for PII storage violations', 'ref': 'Blueprint: Semgrep/Bandit for PII detection', 'method': 'tool_config_check'},
        {'id': 9016, 'category': 'ENFORCEMENT_LAYER_2_POLICY', 'severity': 'HIGH', 'desc': 'Runtime PII detector MUST block storage of raw PII', 'ref': 'Blueprint: Runtime PII-Detector blocks violations', 'method': 'runtime_check'},
        {'id': 9017, 'category': 'ENFORCEMENT_LAYER_2_POLICY', 'severity': 'MEDIUM', 'desc': 'Kubernetes Gatekeeper MUST enforce policies at deployment', 'ref': 'Blueprint: OPA Gatekeeper for runtime enforcement', 'method': 'k8s_config_check'},
        {'id': 9018, 'category': 'ENFORCEMENT_LAYER_2_POLICY', 'severity': 'MEDIUM', 'desc': 'All 24 root modules MUST have dedicated OPA policies', 'ref': '23_compliance/policies/*_policy_v6_0.rego (24 files)', 'method': 'file_count == 24'},
        {'id': 9019, 'category': 'ENFORCEMENT_LAYER_2_POLICY', 'severity': 'LOW', 'desc': 'Policy test coverage MUST be >= 90%', 'ref': '23_compliance/policies/tests/', 'method': 'coverage_check'},
        {'id': 9020, 'category': 'ENFORCEMENT_LAYER_2_POLICY', 'severity': 'LOW', 'desc': 'Policy documentation MUST be up-to-date', 'ref': '05_documentation/ contains policy docs', 'method': 'documentation_freshness'},

        # Layer 3: Trust (9021-9030)
        {'id': 9021, 'category': 'ENFORCEMENT_LAYER_3_TRUST', 'severity': 'CRITICAL', 'desc': 'Zero-Time-Auth MUST be implemented in all 16 shards', 'ref': '14_zero_time_auth/shards/*/src/api/auth.py (count == 16)', 'method': 'file_count == 16'},
        {'id': 9022, 'category': 'ENFORCEMENT_LAYER_3_TRUST', 'severity': 'CRITICAL', 'desc': 'Developer registry MUST exist with DID-based identities', 'ref': '09_meta_identity/developer_registry.json', 'method': 'file_exists'},
        {'id': 9023, 'category': 'ENFORCEMENT_LAYER_3_TRUST', 'severity': 'CRITICAL', 'desc': 'W3C DID standard MUST be implemented', 'ref': 'Blueprint: W3C DID Core 1.0 compliance', 'method': 'standard_compliance'},
        {'id': 9024, 'category': 'ENFORCEMENT_LAYER_3_TRUST', 'severity': 'CRITICAL', 'desc': 'Verifiable Credentials MUST be supported', 'ref': 'Blueprint: W3C Verifiable Credentials', 'method': 'standard_compliance'},
        {'id': 9025, 'category': 'ENFORCEMENT_LAYER_3_TRUST', 'severity': 'HIGH', 'desc': 'mTLS MUST be configured for all internal connections', 'ref': 'Blueprint: mTLS for internal APIs', 'method': 'tls_config_check'},
        {'id': 9026, 'category': 'ENFORCEMENT_LAYER_3_TRUST', 'severity': 'HIGH', 'desc': 'Non-custodial proof distribution MUST be peer-to-peer', 'ref': 'Blueprint: P2P proof layer', 'method': 'architecture_check'},
        {'id': 9027, 'category': 'ENFORCEMENT_LAYER_3_TRUST', 'severity': 'MEDIUM', 'desc': 'DID-based commit signatures MUST be verified', 'ref': 'Git commit verification with Developer DIDs', 'method': 'git_signature_check'},
        {'id': 9028, 'category': 'ENFORCEMENT_LAYER_3_TRUST', 'severity': 'MEDIUM', 'desc': 'RBAC policies MUST be defined for all access points', 'ref': 'Blueprint: RBAC for all zugriffe', 'method': 'rbac_config_check'},
        {'id': 9029, 'category': 'ENFORCEMENT_LAYER_3_TRUST', 'severity': 'LOW', 'desc': 'Zero-Trust architecture MUST be documented', 'ref': 'Blueprint: Zero-Trust Security principles', 'method': 'documentation_check'},
        {'id': 9030, 'category': 'ENFORCEMENT_LAYER_3_TRUST', 'severity': 'LOW', 'desc': 'Trust model MUST include threat modeling', 'ref': 'Blueprint: Threat model documentation', 'method': 'documentation_check'},

        # Layer 4: Observability (9031-9040)
        {'id': 9031, 'category': 'ENFORCEMENT_LAYER_4_OBSERVABILITY', 'severity': 'CRITICAL', 'desc': 'SoT Health Monitor MUST be available', 'ref': '17_observability/sot_health_monitor.py', 'method': 'file_exists'},
        {'id': 9032, 'category': 'ENFORCEMENT_LAYER_4_OBSERVABILITY', 'severity': 'CRITICAL', 'desc': 'Metrics collector MUST gather SoT-specific metrics', 'ref': '17_observability/src/metrics_collector.py', 'method': 'file_exists'},
        {'id': 9033, 'category': 'ENFORCEMENT_LAYER_4_OBSERVABILITY', 'severity': 'CRITICAL', 'desc': 'SoT metrics module MUST be implemented', 'ref': '17_observability/sot_metrics.py', 'method': 'file_exists'},
        {'id': 9034, 'category': 'ENFORCEMENT_LAYER_4_OBSERVABILITY', 'severity': 'CRITICAL', 'desc': 'Federation metrics schema MUST be defined', 'ref': '17_observability/metrics/federation_live_metrics_schema.json', 'method': 'file_exists'},
        {'id': 9035, 'category': 'ENFORCEMENT_LAYER_4_OBSERVABILITY', 'severity': 'HIGH', 'desc': 'Prometheus metrics MUST be exported', 'ref': 'Blueprint: Prometheus for metrics collection', 'method': 'prometheus_config_check'},
        {'id': 9036, 'category': 'ENFORCEMENT_LAYER_4_OBSERVABILITY', 'severity': 'HIGH', 'desc': 'Jaeger tracing MUST be configured', 'ref': 'Blueprint: Jaeger for distributed tracing', 'method': 'jaeger_config_check'},
        {'id': 9037, 'category': 'ENFORCEMENT_LAYER_4_OBSERVABILITY', 'severity': 'HIGH', 'desc': 'Loki logging MUST include PII redaction', 'ref': 'Blueprint: Loki with PII-Redaction', 'method': 'logging_config_check'},
        {'id': 9038, 'category': 'ENFORCEMENT_LAYER_4_OBSERVABILITY', 'severity': 'MEDIUM', 'desc': 'Audit pipeline MUST generate scorecard automatically', 'ref': 'CLI generates scorecard.json/md', 'method': 'cli_output_check'},
        {'id': 9039, 'category': 'ENFORCEMENT_LAYER_4_OBSERVABILITY', 'severity': 'MEDIUM', 'desc': 'Alert manager MUST be configured for critical events', 'ref': 'Blueprint: AlertManager for alerts', 'method': 'alertmanager_config_check'},
        {'id': 9040, 'category': 'ENFORCEMENT_LAYER_4_OBSERVABILITY', 'severity': 'LOW', 'desc': 'Observability dashboards MUST visualize SoT status', 'ref': '17_observability/dashboards/', 'method': 'directory_exists'},

        # Layer 5: Governance (9041-9050)
        {'id': 9041, 'category': 'ENFORCEMENT_LAYER_5_GOVERNANCE', 'severity': 'CRITICAL', 'desc': 'Immutable registry MUST exist with logs/locks/manifests', 'ref': '24_meta_orchestration/registry/{logs,locks,manifests}/', 'method': 'directory_structure_check'},
        {'id': 9042, 'category': 'ENFORCEMENT_LAYER_5_GOVERNANCE', 'severity': 'CRITICAL', 'desc': 'Global governance matrix MUST be defined', 'ref': '07_governance_legal/orchestration/global_governance_matrix.yaml', 'method': 'file_exists'},
        {'id': 9043, 'category': 'ENFORCEMENT_LAYER_5_GOVERNANCE', 'severity': 'CRITICAL', 'desc': 'Autonomous governance node MUST be implemented', 'ref': '07_governance_legal/autonomous_governance_node.py', 'method': 'file_exists'},
        {'id': 9044, 'category': 'ENFORCEMENT_LAYER_5_GOVERNANCE', 'severity': 'CRITICAL', 'desc': 'Governance manifest MUST document decision framework', 'ref': '07_governance_legal/governance_manifest.json', 'method': 'file_exists'},
        {'id': 9045, 'category': 'ENFORCEMENT_LAYER_5_GOVERNANCE', 'severity': 'HIGH', 'desc': 'Governance decisions log MUST be maintained', 'ref': '07_governance_legal/governance_decisions.json', 'method': 'file_exists'},
        {'id': 9046, 'category': 'ENFORCEMENT_LAYER_5_GOVERNANCE', 'severity': 'HIGH', 'desc': 'DAO governance framework MUST be ready', 'ref': 'Blueprint: Token-weighted governance, Snapshot + on-chain', 'method': 'spec_compliance'},
        {'id': 9047, 'category': 'ENFORCEMENT_LAYER_5_GOVERNANCE', 'severity': 'MEDIUM', 'desc': 'eIDAS compliance MUST be documented', 'ref': 'Blueprint: eIDAS 2.0 conformance', 'method': 'compliance_documentation_check'},
        {'id': 9048, 'category': 'ENFORCEMENT_LAYER_5_GOVERNANCE', 'severity': 'MEDIUM', 'desc': 'GDPR Article 5 compliance MUST be verifiable', 'ref': 'Blueprint: Audit-Logs erfüllen DSGVO-Artikel 5', 'method': 'compliance_check'},
        {'id': 9049, 'category': 'ENFORCEMENT_LAYER_5_GOVERNANCE', 'severity': 'LOW', 'desc': 'Dual review process MUST be enforced for SoT updates', 'ref': 'Blueprint: Architecture-Review + Compliance-Review', 'method': 'review_process_check'},
        {'id': 9050, 'category': 'ENFORCEMENT_LAYER_5_GOVERNANCE', 'severity': 'LOW', 'desc': 'Legal proof anchoring MUST be available', 'ref': 'Blueprint: Registry-Signaturen sind eIDAS-konform', 'method': 'signature_verification'},
    ]

    enforcement_rules = []
    for tmpl in rule_templates:
        enforcement_rules.append({
            'rule_id': f'ENFORCEMENT-{tmpl["id"]:04d}',
            'source_file': 'ENFORCEMENT_LAYER_INTEGRATION_2025_10_24',
            'source_line': 0,
            'category': tmpl['category'],
            'yaml_file': None,
            'yaml_path': None,
            'field_name': None,
            'expected_value': None,
            'rule_type': 'MUST',
            'severity': tmpl['severity'],
            'description': tmpl['desc'],
            'validation_method': tmpl['method'],
            'evidence_required': 'File/config existence check',
            'reference': tmpl['ref']
        })

    # Append to existing rules
    data['rules'].extend(enforcement_rules)
    data['total_rules'] = len(data['rules'])
    data['enforcement_layer_rules_added'] = 50
    data['generated'] = datetime.now().isoformat()
    data['version'] = '5.0.0'  # Bump version to reflect enforcement layer integration

    # Write updated file
    output_file = Path(__file__).parent / 'all_4_sot_semantic_rules_v2.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f'[OK] Created {output_file.name}')
    print(f'[INFO] Total rules: {data["total_rules"]} (+50 enforcement rules)')
    print(f'[INFO] Version: {data["version"]}')

    # Print summary by layer
    print('\n[SUMMARY] Enforcement Layer Summary:')
    layers = {
        'LAYER_1_CRYPTO': 0,
        'LAYER_2_POLICY': 0,
        'LAYER_3_TRUST': 0,
        'LAYER_4_OBSERVABILITY': 0,
        'LAYER_5_GOVERNANCE': 0
    }
    for rule in enforcement_rules:
        for layer in layers:
            if layer in rule['category']:
                layers[layer] += 1

    for layer, count in layers.items():
        print(f'  {layer}: {count} rules')

if __name__ == '__main__':
    main()
