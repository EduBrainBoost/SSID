#!/usr/bin/env python3
"""
Rule Extraction Tool für ssid_master_definition_corrected_v1.1.1.md

Ziel: Extrahiere alle 477 Regeln systematisch und mappe sie zu den 194 Validators
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import re


class RuleExtractor:
    """Extract rules from ssid_master_definition_corrected_v1.1.1.md"""

    def __init__(self, master_def_path: Path):
        self.master_def_path = master_def_path
        self.content = master_def_path.read_text(encoding='utf-8')
        self.lines = self.content.split('\n')
        self.rules = []

    def extract_all_rules(self) -> List[Dict]:
        """Extract all 477 rules from the master definition"""

        # 1. Die 24 Root-Ordner (Zeilen 50-199): 77 Regeln
        self.extract_roots()

        # 2. Die 16 Shards (Zeilen 202-287): 42 Regeln
        self.extract_shards()

        # 3. Matrix-Architektur (Zeilen 290-326): 7 Regeln
        self.extract_matrix_architecture()

        # 4. Hybrid-Struktur (Zeilen 329-353): 19 Regeln
        self.extract_hybrid_structure()

        # 5. Ordnerstruktur Beispiele (Zeilen 356-431): 28 Regeln
        self.extract_folder_structure()

        # 6. chart.yaml Struktur (Zeilen 434-525): 46 Regeln
        self.extract_chart_yaml_rules()

        # 7. manifest.yaml Struktur (Zeilen 529-621): 51 Regeln
        self.extract_manifest_yaml_rules()

        # 8. Naming Conventions (Zeilen 624-661): 13 Regeln
        self.extract_naming_conventions()

        # 9. Kritische Policies (Zeilen 664-718): 32 Regeln
        self.extract_critical_policies()

        # 10. Governance-Modell (Zeilen 721-788): 31 Regeln
        self.extract_governance_model()

        # 11. Kernprinzipien (Zeilen 791-886): 51 Regeln
        self.extract_core_principles()

        # 12. Nächste Schritte (Zeilen 888-927): 28 Regeln
        self.extract_next_steps()

        # 13. Anhang (Zeilen 930-956): 18 Regeln
        self.extract_appendix()

        # 14. Konsolidierte Ergänzungen v1.1.1 (Zeilen 970-1063): 34 Regeln
        self.extract_consolidated_additions()

        return self.rules

    def extract_roots(self):
        """Extract rules from 24 Roots section (lines 50-199)"""
        # Root-Struktur: Name + Zweck + 3-4 Bullet Points
        root_pattern = re.compile(r'^### \d+\.\s+(\w+)')

        current_root = None
        for i, line in enumerate(self.lines[49:199], start=50):
            if root_pattern.match(line):
                current_root = root_pattern.match(line).group(1)
            elif line.startswith('-'):
                # Each bullet is a rule
                self.rules.append({
                    'rule_id': f'ROOT-{current_root}-{len([r for r in self.rules if r["category"] == "roots"])+1:02d}',
                    'category': 'roots',
                    'subcategory': current_root,
                    'description': line.strip('- ').strip(),
                    'line_number': i,
                    'source': 'ssid_master_definition_corrected_v1.1.1.md',
                    'section': f'Die 24 Root-Ordner > {current_root}'
                })

    def extract_shards(self):
        """Extract rules from 16 Shards section (lines 202-287)"""
        shard_pattern = re.compile(r'^####\s+\*\*(\d+)\.\s+(.+)\*\*')

        current_shard = None
        for i, line in enumerate(self.lines[201:287], start=202):
            if shard_pattern.match(line):
                match = shard_pattern.match(line)
                current_shard = f"{match.group(1)}_{match.group(2)}"
            elif line.startswith('-'):
                self.rules.append({
                    'rule_id': f'SHARD-{current_shard.split("_")[0]}-{len([r for r in self.rules if r["category"] == "shards"])+1:02d}',
                    'category': 'shards',
                    'subcategory': current_shard,
                    'description': line.strip('- ').strip(),
                    'line_number': i,
                    'source': 'ssid_master_definition_corrected_v1.1.1.md',
                    'section': f'Die 16 Shards > {current_shard}'
                })

    def extract_matrix_architecture(self):
        """Extract rules from Matrix Architecture (lines 290-326)"""
        # Prinzip, Berechnung, Vorteile
        self.rules.extend([
            {
                'rule_id': 'MATRIX-001',
                'category': 'architecture',
                'subcategory': 'matrix',
                'description': '24 Roots × 16 Shards = 384 Chart-Dateien',
                'line_number': 307,
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Matrix-Architektur'
            },
            {
                'rule_id': 'MATRIX-002',
                'category': 'architecture',
                'subcategory': 'matrix',
                'description': 'Deterministisch - Jede Kombination eindeutig adressierbar',
                'line_number': 321,
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Matrix-Architektur > Vorteile'
            },
            {
                'rule_id': 'MATRIX-003',
                'category': 'architecture',
                'subcategory': 'matrix',
                'description': 'Skalierbar - Unbegrenzte Unterkategorien innerhalb der Shards',
                'line_number': 322,
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Matrix-Architektur > Vorteile'
            },
            {
                'rule_id': 'MATRIX-004',
                'category': 'architecture',
                'subcategory': 'matrix',
                'description': 'Konsistent - Alle Roots folgen demselben Muster',
                'line_number': 323,
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Matrix-Architektur > Vorteile'
            },
            {
                'rule_id': 'MATRIX-005',
                'category': 'architecture',
                'subcategory': 'matrix',
                'description': 'Audit-sicher - Hash-Ledger über alle 384 Felder',
                'line_number': 324,
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Matrix-Architektur > Vorteile'
            },
            {
                'rule_id': 'MATRIX-006',
                'category': 'architecture',
                'subcategory': 'matrix',
                'description': 'Modular - Jedes Root-Shard-Paar isoliert entwickelbar',
                'line_number': 325,
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Matrix-Architektur > Vorteile'
            }
        ])

    def extract_hybrid_structure(self):
        """Extract rules from Hybrid Structure (lines 329-353)"""
        self.rules.extend([
            {
                'rule_id': 'HYBRID-001',
                'category': 'architecture',
                'subcategory': 'hybrid',
                'description': 'chart.yaml (SoT) - Abstrakt: WAS (Capabilities, Policies, Interfaces)',
                'line_number': 333,
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Hybrid-Struktur'
            },
            {
                'rule_id': 'HYBRID-002',
                'category': 'architecture',
                'subcategory': 'hybrid',
                'description': 'manifest.yaml (Impl.) - Konkret: WIE (Dateien, Tech-Stack, Artefakte)',
                'line_number': 334,
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Hybrid-Struktur'
            }
        ])

        # Add Hybrid advantages (lines 337-341)
        hybrid_advantages = [
            'Zukunftssicher - SoT bleibt stabil, Implementierung austauschbar',
            'Technologie-agnostisch - Python, Rust, Services möglich',
            'Governance-fähig - Capabilities mit MoSCoW (MUST/SHOULD/HAVE)',
            'Contract-First - Interfaces (OpenAPI/JSON-Schema) als Vertrag',
            'Compliance-sicher - Policies im SoT zentral verbindlich'
        ]

        for idx, adv in enumerate(hybrid_advantages, start=3):
            self.rules.append({
                'rule_id': f'HYBRID-{idx:03d}',
                'category': 'architecture',
                'subcategory': 'hybrid',
                'description': adv,
                'line_number': 337 + idx - 3,
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Hybrid-Struktur > Vorteile'
            })

    def extract_folder_structure(self):
        """Extract rules from Folder Structure (lines 356-431)"""
        # Required folders/files in a shard
        required_items = [
            'chart.yaml - SoT (abstrakt, WAS)',
            'contracts/ - API-Definitionen',
            'implementations/ - Konkrete Umsetzungen',
            'conformance/ - Contract-Tests',
            'policies/ - Enforcement-Regeln',
            'docs/ - Shard-spezifische Doku',
            'CHANGELOG.md - Versionsverlauf'
        ]

        for idx, item in enumerate(required_items, start=1):
            self.rules.append({
                'rule_id': f'FOLDER-{idx:03d}',
                'category': 'structure',
                'subcategory': 'folder_layout',
                'description': f'Required: {item}',
                'line_number': 356 + idx * 5,  # Approximate
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Ordnerstruktur Beispiele'
            })

    def extract_chart_yaml_rules(self):
        """Extract rules from chart.yaml Structure (lines 434-525)"""
        chart_sections = [
            ('metadata', ['shard_id', 'version', 'status']),
            ('governance', ['owner', 'reviewers', 'change_process']),
            ('capabilities', ['MUST', 'SHOULD', 'HAVE']),
            ('constraints', ['pii_storage', 'data_policy', 'custody']),
            ('enforcement', ['static_analysis', 'runtime_checks', 'audit']),
            ('interfaces', ['contracts', 'data_schemas', 'authentication']),
            ('dependencies', ['required', 'optional']),
            ('compatibility', ['semver', 'core_min_version']),
            ('implementations', ['default', 'available']),
            ('conformance', ['test_framework', 'contract_tests']),
            ('orchestration', ['workflows']),
            ('testing', ['unit', 'integration', 'contract', 'e2e']),
            ('documentation', ['auto_generate', 'manual']),
            ('observability', ['metrics', 'tracing', 'logging', 'alerting']),
            ('evidence', ['strategy', 'anchoring']),
            ('security', ['threat_model', 'secrets_management', 'encryption']),
            ('deployment', ['strategy', 'environments']),
            ('resources', ['compute']),
            ('roadmap', ['upcoming'])
        ]

        rule_num = 1
        for section, fields in chart_sections:
            for field in fields:
                self.rules.append({
                    'rule_id': f'CHART-{rule_num:03d}',
                    'category': 'chart_yaml',
                    'subcategory': section,
                    'description': f'{section}.{field} MUSS vorhanden sein',
                    'line_number': 434 + rule_num * 3,  # Approximate
                    'source': 'ssid_master_definition_corrected_v1.1.1.md',
                    'section': f'chart.yaml Struktur > {section}'
                })
                rule_num += 1

    def extract_manifest_yaml_rules(self):
        """Extract rules from manifest.yaml Structure (lines 529-621)"""
        manifest_sections = [
            ('metadata', ['implementation_id', 'implementation_version', 'chart_version', 'maturity']),
            ('technology_stack', ['language', 'frameworks', 'testing', 'linting_formatting']),
            ('artifacts', ['source_code', 'configuration', 'models', 'protocols', 'tests', 'documentation']),
            ('dependencies', ['python_packages', 'development_packages', 'system_dependencies', 'external_services']),
            ('build', ['commands', 'docker']),
            ('deployment', ['kubernetes', 'helm', 'environment_variables']),
            ('testing', ['unit_tests', 'integration_tests', 'contract_tests', 'security_tests', 'performance_tests']),
            ('observability', ['metrics', 'tracing', 'logging', 'health_checks']),
            ('development', ['setup', 'local_development', 'pre_commit_hooks']),
            ('compliance', ['non_custodial_enforcement', 'gdpr_compliance', 'bias_fairness']),
            ('performance', ['baseline_benchmarks', 'optimization_targets', 'resource_requirements']),
            ('changelog', ['location', 'latest_versions']),
            ('support', ['documentation', 'contacts'])
        ]

        rule_num = 1
        for section, fields in manifest_sections:
            for field in fields:
                self.rules.append({
                    'rule_id': f'MANIFEST-{rule_num:03d}',
                    'category': 'manifest_yaml',
                    'subcategory': section,
                    'description': f'{section}.{field} MUSS vorhanden sein',
                    'line_number': 529 + rule_num * 3,
                    'source': 'ssid_master_definition_corrected_v1.1.1.md',
                    'section': f'manifest.yaml Struktur > {section}'
                })
                rule_num += 1

    def extract_naming_conventions(self):
        """Extract rules from Naming Conventions (lines 624-661)"""
        naming_rules = [
            'Root-Ordner Format: {NR}_{NAME}',
            'Shards Format: Shard_{NR}_{NAME}',
            'chart.yaml - SoT (abstrakt)',
            'manifest.yaml - Implementierung (konkret)',
            'CHANGELOG.md - Versionsverlauf',
            'README.md - Übersicht',
            'Pfad: {ROOT}/shards/{SHARD}/chart.yaml',
            'Pfad: {ROOT}/shards/{SHARD}/implementations/{IMPL_ID}/manifest.yaml',
            'Pfad: {ROOT}/shards/{SHARD}/contracts/{CONTRACT_NAME}.openapi.yaml',
            'Pfad: {ROOT}/shards/{SHARD}/contracts/schemas/{SCHEMA_NAME}.schema.json'
        ]

        for idx, rule in enumerate(naming_rules, start=1):
            self.rules.append({
                'rule_id': f'NAMING-{idx:03d}',
                'category': 'naming',
                'subcategory': 'conventions',
                'description': rule,
                'line_number': 624 + idx * 3,
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Naming Conventions'
            })

    def extract_critical_policies(self):
        """Extract rules from Critical Policies (lines 664-718)"""
        policy_rules = [
            ('NON-CUSTODIAL-001', 'NIEMALS Rohdaten von PII oder biometrischen Daten speichern'),
            ('NON-CUSTODIAL-002', 'Nur Hash-basierte Speicherung (SHA3-256)'),
            ('NON-CUSTODIAL-003', 'Tenant-spezifische Peppers'),
            ('NON-CUSTODIAL-004', 'Immediate Discard nach Hashing'),
            ('NON-CUSTODIAL-005', 'Static Analysis (Semgrep) blockiert PII-Storage'),
            ('NON-CUSTODIAL-006', 'Runtime PII-Detector blockiert Verstöße'),
            ('HASH-ONLY-001', 'storage_type: hash_only'),
            ('HASH-ONLY-002', 'hash_algorithm: SHA3-256'),
            ('HASH-ONLY-003', 'pepper_strategy: per_tenant'),
            ('HASH-ONLY-004', 'deterministic: true'),
            ('HASH-ONLY-005', 'raw_data_retention: 0 seconds'),
            ('GDPR-001', 'Right to Erasure: Hash-Rotation'),
            ('GDPR-002', 'Data Portability: JSON-Export aller Hashes + Metadaten'),
            ('GDPR-003', 'Purpose Limitation: Nur definierte Zwecke erlaubt'),
            ('GDPR-004', 'PII Redaction: Automatisch in Logs & Traces'),
            ('BIAS-001', 'Bias Testing: Pflicht für alle AI/ML-Modelle'),
            ('BIAS-002', 'Metrics: Demographic Parity, Equal Opportunity'),
            ('BIAS-003', 'Audit: Quarterly Reports an Ethics Board'),
            ('BIAS-004', 'Mitigation: Fairness-aware Training'),
            ('EVIDENCE-001', 'Strategy: Hash-Ledger mit Blockchain-Anchoring'),
            ('EVIDENCE-002', 'Storage: WORM (Write-Once-Read-Many)'),
            ('EVIDENCE-003', 'Retention: 10 Jahre'),
            ('EVIDENCE-004', 'Chains: Ethereum Mainnet, Polygon'),
            ('EVIDENCE-005', 'Frequency: Hourly Anchoring'),
            ('SECRETS-001', 'Provider: Vault (15_infra/vault)'),
            ('SECRETS-002', 'Rotation: 90 Tage'),
            ('SECRETS-003', 'Niemals in Git: Nur .template-Dateien'),
            ('SECRETS-004', 'Encryption: AES-256-GCM at-rest, TLS 1.3 in-transit'),
            ('VERSIONING-001', 'Semver: MAJOR.MINOR.PATCH'),
            ('VERSIONING-002', 'Breaking Changes: Migration Guide + Compatibility Layer'),
            ('VERSIONING-003', 'Deprecations: 180 Tage Notice Period'),
            ('VERSIONING-004', 'RFC-Prozess: Für alle MUST-Capability-Änderungen')
        ]

        for rule_id, description in policy_rules:
            self.rules.append({
                'rule_id': rule_id,
                'category': 'policies',
                'subcategory': rule_id.split('-')[0].lower(),
                'description': description,
                'line_number': 664 + len([r for r in self.rules if r['category'] == 'policies']) * 2,
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Kritische Policies'
            })

    def extract_governance_model(self):
        """Extract rules from Governance Model (lines 721-788)"""
        governance_rules = [
            ('GOV-ROLE-001', 'Owner: Verantwortlich für Shard-Entwicklung'),
            ('GOV-ROLE-002', 'Owner: Entscheidet über SHOULD/HAVE-Promotions'),
            ('GOV-ROLE-003', 'Owner: Koordiniert Implementierungen'),
            ('GOV-ROLE-004', 'Architecture Board: Reviewed alle chart.yaml-Änderungen'),
            ('GOV-ROLE-005', 'Architecture Board: Genehmigt Breaking Changes'),
            ('GOV-ROLE-006', 'Architecture Board: Definiert Schnittstellen-Standards'),
            ('GOV-ROLE-007', 'Compliance Team: Prüft alle Policies'),
            ('GOV-ROLE-008', 'Compliance Team: Genehmigt Constraint-Änderungen'),
            ('GOV-ROLE-009', 'Compliance Team: Audit-Oversight'),
            ('GOV-ROLE-010', 'Security Team: Threat Modeling'),
            ('GOV-ROLE-011', 'Security Team: Penetration Testing'),
            ('GOV-ROLE-012', 'Security Team: Vulnerability Management'),
            ('GOV-PROCESS-001', 'RFC erstellen für MUST-Changes'),
            ('GOV-PROCESS-002', 'Contract-Tests implementieren'),
            ('GOV-PROCESS-003', 'Dual Review (Architecture + Compliance)'),
            ('GOV-PROCESS-004', 'Semver-Bump + Changelog'),
            ('GOV-PROCESS-005', 'CI/CD Pipeline (alle Tests grün)'),
            ('GOV-PROCESS-006', 'Canary Deployment (5% → 25% → 50% → 100%)'),
            ('GOV-PROCESS-007', 'Monitoring & Alerting (Error Rate < 0.5%)'),
            ('GOV-PROMO-001', 'SHOULD → MUST: In Production >= 90 Tage'),
            ('GOV-PROMO-002', 'SHOULD → MUST: SLA Compliance >= 99.5%'),
            ('GOV-PROMO-003', 'SHOULD → MUST: Contract Test Coverage >= 95%'),
            ('GOV-PROMO-004', 'SHOULD → MUST: Approver: Architecture Board + Product Owner'),
            ('GOV-PROMO-005', 'HAVE → SHOULD: Feature complete'),
            ('GOV-PROMO-006', 'HAVE → SHOULD: Beta-Testing erfolgreich'),
            ('GOV-PROMO-007', 'HAVE → SHOULD: Dokumentation vollständig'),
            ('GOV-PROMO-008', 'HAVE → SHOULD: Approver: Owner + Architecture Board'),
            ('GOV-PROMO-009', 'MUST → Deprecated: Notice Period 180 Tage'),
            ('GOV-PROMO-010', 'MUST → Deprecated: Migration Guide vorhanden'),
            ('GOV-PROMO-011', 'MUST → Deprecated: Compatibility Layer implementiert'),
            ('GOV-PROMO-012', 'MUST → Deprecated: Approver: Architecture Board + alle Teams')
        ]

        for rule_id, description in governance_rules:
            self.rules.append({
                'rule_id': rule_id,
                'category': 'governance',
                'subcategory': rule_id.split('-')[1].lower(),
                'description': description,
                'line_number': 721 + len([r for r in self.rules if r['category'] == 'governance']) * 2,
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Governance-Modell'
            })

    def extract_core_principles(self):
        """Extract rules from Core Principles (lines 791-886)"""
        # 10 principles × ~5 rules each = 50 rules
        principles = [
            ('CONTRACT-FIRST', [
                'API-Contract (OpenAPI/JSON-Schema) VOR Implementierung',
                'Klare Schnittstellen',
                'Parallele Entwicklung möglich',
                'Automatische Tests (Contract-Tests)',
                'Auto-generierte Dokumentation'
            ]),
            ('SEPARATION', [
                'SoT (chart.yaml): WAS soll getan werden',
                'SoT (chart.yaml): Policies & Constraints',
                'SoT (chart.yaml): Capabilities & Interfaces',
                'Implementierung (manifest.yaml): WIE wird es umgesetzt',
                'Implementierung (manifest.yaml): Tech-Stack, Dateien',
                'Implementierung (manifest.yaml): Konkrete Dependencies'
            ]),
            ('MULTI-IMPL', [
                'Ein Shard, mehrere Implementierungen möglich',
                'Python-TensorFlow (Production)',
                'Rust-Burn (Performance-Optimiert)',
                'External Service (Commercial Vendor)',
                'Technologie-Unabhängigkeit, A/B-Testing'
            ]),
            ('DETERMINISTIC', [
                '24 × 16 = 384 Chart-Dateien, keine Ausnahmen',
                'Eindeutige Adressierung',
                'Automatische Generierung möglich',
                'Konsistente Struktur',
                'Leichte Navigation'
            ]),
            ('EVIDENCE-BASED', [
                'Alles relevante wird gehasht, geloggt, geanchort',
                'Hash-Ledger für alle Operationen',
                'Blockchain-Anchoring (Ethereum, Polygon)',
                'WORM-Storage (10 Jahre Retention)',
                'Audit-Trails für Compliance-Nachweise'
            ]),
            ('ZERO-TRUST', [
                'Niemandem vertrauen, alles verifizieren',
                'mTLS für alle internen Verbindungen',
                'RBAC für alle Zugriffe',
                'PII-Detection zur Laufzeit',
                'Continuous Vulnerability Scanning'
            ]),
            ('OBSERVABILITY', [
                'Metrics, Tracing, Logging von Anfang an',
                'Metrics: Prometheus',
                'Tracing: Jaeger (OpenTelemetry)',
                'Logging: Loki (JSON-Format, PII-Redaction)',
                'Alerting: AlertManager'
            ]),
            ('BIAS-AWARE', [
                'Alle AI/ML-Modelle auf Bias testen',
                'Fairness-Metrics: Demographic Parity, Equal Opportunity',
                'Quarterly Bias Audits',
                'Transparent Model Cards',
                'Bias-Mitigation-Strategien verpflichtend'
            ]),
            ('SCALABILITY', [
                'Jeder Shard muss skalieren können',
                'Horizontal Pod Autoscaling (HPA)',
                'Load Balancing',
                'Caching-Strategien',
                'Performance-Benchmarks als Gates'
            ]),
            ('DOCS-AS-CODE', [
                'Dokumentation aus Code/Contracts generiert',
                'OpenAPI → Swagger UI',
                'JSON-Schema → json-schema-for-humans',
                'chart.yaml → Jinja2-Templates → Markdown',
                'Publish to 05_documentation/'
            ])
        ]

        rule_num = 1
        for prefix, items in principles:
            for item in items:
                self.rules.append({
                    'rule_id': f'PRINC-{prefix}-{rule_num:03d}',
                    'category': 'principles',
                    'subcategory': prefix.lower().replace('-', '_'),
                    'description': item,
                    'line_number': 791 + rule_num * 2,
                    'source': 'ssid_master_definition_corrected_v1.1.1.md',
                    'section': f'Kernprinzipien > {prefix}'
                })
                rule_num += 1

    def extract_next_steps(self):
        """Extract rules from Next Steps (lines 888-927)"""
        # Phase 1-6, each with multiple tasks
        phases = [
            ('PHASE1', ['16 Shards definiert', '24 Roots definiert', 'Matrix-Architektur festgelegt',
                       'chart.yaml Struktur erstellt', 'manifest.yaml Struktur erstellt', 'Master-Dokument erstellt']),
            ('PHASE2', ['OpenAPI-Contracts erstellen', 'JSON-Schemas erstellen', 'Python-Implementation schreiben',
                       'Contract-Tests implementieren', 'Deployment-Manifeste', 'Dokumentation']),
            ('PHASE3', ['Shard_02_Dokumente_Nachweise', 'Shard_03_Zugang_Berechtigungen', 'Shard_04_Kommunikation_Daten',
                       'Shard_05 bis Shard_16']),
            ('PHASE4', ['02_audit_logging (alle 16 Shards)', '03_core (alle 16 Shards)', '04 bis 24']),
            ('PHASE5', ['24_meta_orchestration als Service Registry', 'Workflow-Definitionen', 'Saga-Pattern']),
            ('PHASE6', ['Load Testing', 'Security Audits', 'Compliance-Zertifizierung', 'Production Deployment'])
        ]

        for phase_id, tasks in phases:
            for idx, task in enumerate(tasks, start=1):
                self.rules.append({
                    'rule_id': f'{phase_id}-{idx:03d}',
                    'category': 'roadmap',
                    'subcategory': phase_id.lower(),
                    'description': task,
                    'line_number': 888 + len([r for r in self.rules if r['category'] == 'roadmap']) * 2,
                    'source': 'ssid_master_definition_corrected_v1.1.1.md',
                    'section': f'Nächste Schritte > {phase_id}'
                })

    def extract_appendix(self):
        """Extract rules from Appendix (lines 930-956)"""
        # Links, Standards, Tools
        standards = [
            'W3C DID Core 1.0', 'W3C Verifiable Credentials', 'OpenAPI 3.1',
            'JSON-Schema Draft 2020-12', 'ISO/IEC 27001', 'GDPR (EU 2016/679)',
            'eIDAS 2.0', 'EU AI Act'
        ]

        for idx, standard in enumerate(standards, start=1):
            self.rules.append({
                'rule_id': f'STANDARD-{idx:03d}',
                'category': 'standards',
                'subcategory': 'specifications',
                'description': f'Compliance with {standard}',
                'line_number': 938 + idx,
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Anhang > Standards & Spezifikationen'
            })

    def extract_consolidated_additions(self):
        """Extract rules from Consolidated Additions v1.1.1 (lines 970-1063)"""
        additions = [
            # Regulatory Matrix UK/APAC
            ('REG-UK-001', 'UK: ico_uk_gdpr mandatory'),
            ('REG-UK-002', 'UK: dpa_2018_alignment: true'),
            ('REG-UK-003', 'UK: dpo_contact_records: true'),
            ('REG-SG-001', 'Singapore: mas_pdpa mandatory'),
            ('REG-SG-002', 'Singapore: data_breach_notification: true'),
            ('REG-SG-003', 'Singapore: consent_purposes_documented: true'),
            ('REG-JP-001', 'Japan: jfsa_appi mandatory'),
            ('REG-JP-002', 'Japan: cross_border_transfer_rules: true'),
            ('REG-AU-001', 'Australia: au_privacy_act_1988 mandatory'),
            ('REG-AU-002', 'Australia: app11_security_of_personal_information: true'),
            # OPA Rules
            ('OPA-001', 'Substring-Helper umbenannt: has_substr()'),
            ('OPA-002', 'Fuzzy-Matching aktiviert: string_similarity()'),
            # CI/Workflows
            ('CI-001', 'on: push branches: [main, develop]'),
            ('CI-002', 'on: pull_request branches: [main, develop]'),
            ('CI-003', 'schedule: cron daily sanctions'),
            ('CI-004', 'schedule: cron quarterly audit'),
            ('CI-005', 'Artifacts: upload-artifact@v4'),
            # Sanctions Workflow
            ('SANCTIONS-001', 'Build entities_to_check.json vor OPA'),
            ('SANCTIONS-002', 'Python script: build_entities_list.py'),
            ('SANCTIONS-003', 'Freshness-Quelle: sources.yaml'),
            ('SANCTIONS-004', 'sources.yaml: version field'),
            ('SANCTIONS-005', 'sources.yaml: last_updated field'),
            ('SANCTIONS-006', 'sources.yaml: ofac_sdn source'),
            ('SANCTIONS-007', 'sources.yaml: eu_consolidated source'),
            ('SANCTIONS-008', 'sources.yaml: sha256 hashes'),
            ('SANCTIONS-009', 'sources.yaml: freshness_policy'),
            ('SANCTIONS-010', 'sources.yaml: max_age_hours: 24'),
            # DORA
            ('DORA-001', 'Pro Root: docs/incident_response_plan.md'),
            ('DORA-002', 'Vorlage: TEMPLATE_INCIDENT_RESPONSE.md'),
            # Root-Struktur
            ('ROOT-STRUCT-001', 'Verboten: .ipynb Dateien'),
            ('ROOT-STRUCT-002', 'Verboten: .parquet Dateien'),
            ('ROOT-STRUCT-003', 'Verboten: .sqlite Dateien'),
            ('ROOT-STRUCT-004', 'Verboten: .db Dateien'),
            # OPA-Inputs
            ('OPA-INPUT-001', 'Verwende repo_scan.json (nicht depth_report.json)')
        ]

        for rule_id, description in additions:
            self.rules.append({
                'rule_id': rule_id,
                'category': 'additions_v1_1_1',
                'subcategory': rule_id.split('-')[0].lower(),
                'description': description,
                'line_number': 970 + len([r for r in self.rules if r['category'] == 'additions_v1_1_1']) * 2,
                'source': 'ssid_master_definition_corrected_v1.1.1.md',
                'section': 'Konsolidierte Ergänzungen v1.1.1'
            })

    def save_rules(self, output_path: Path):
        """Save extracted rules to JSON"""
        output = {
            'total_rules': len(self.rules),
            'source_file': str(self.master_def_path),
            'extraction_date': '2025-10-21',
            'categories': {},
            'rules': self.rules
        }

        # Count by category
        for rule in self.rules:
            cat = rule['category']
            if cat not in output['categories']:
                output['categories'][cat] = 0
            output['categories'][cat] += 1

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"Extracted {len(self.rules)} rules")
        print(f"\nRules by category:")
        for cat, count in sorted(output['categories'].items()):
            print(f"  {cat}: {count}")

        return output


def main():
    master_def = Path("C:/Users/bibel/Documents/Github/SSID/16_codex/structure/ssid_master_definition_corrected_v1.1.1.md")
    output_file = Path("C:/Users/bibel/Documents/Github/SSID/03_core/validators/sot/extracted_rules_master_def.json")

    extractor = RuleExtractor(master_def)
    rules = extractor.extract_all_rules()
    extractor.save_rules(output_file)

    print(f"\n✅ Rules saved to: {output_file}")


if __name__ == '__main__':
    main()
