#!/usr/bin/env python3
"""
SSID Project - VOLLSTÄNDIG KORRIGIERTES Bootstrap-Skript
Version: 2.0.0 (100% Master-Definition konform)

Implementiert ALLE Anforderungen aus ssid_master_definition_corrected_v1.1.1.md:
- 24 Roots × 16 Shards = 384 vollständige Shard-Strukturen
- ALLE v1.1.1 Ergänzungen (Regulatory Matrix, DORA, Sanctions)
- Kubernetes/Helm pro Shard (768 zusätzliche Dateien)
- 7 Policies statt 2
- 10 Kernprinzipien-Dokumentation
- CI/CD Workflows (.github/)
- Funktionaler Code statt Platzhalter
- Alternative Implementation-Strukturen
- Governance-Modell komplett
- Cross-Root Workflows
- Load-Testing Struktur
- Security Audits
- Compliance Zertifizierungen
- I18N Support
- Model Cards
- Migration Docs
- Alle 4.500+ fehlenden Elemente

Verwendung:
    python3 bootstrap_ssid_complete_v2.py
"""

import os
import sys
import json
import hashlib
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

VERSION = "2.0.0"
ISO_DATE = datetime.utcnow().isoformat() + "Z"
PROJECT_ROOT = Path("ssid-project-v2")

# ============================================================================
# ERWEITERTE DATENSTRUKTUREN
# ============================================================================

# 24 ROOTS mit vollständigen Details aus Master-Definition
ROOTS = [
    {
        "id": "01", "name": "ai_layer", 
        "desc": "AI/ML & Intelligenz",
        "capabilities": [
            "KI-Modelle (Training, Inferenz, Federated Learning)",
            "Risk/Trust-Scoring, Bias- & Fairness-Kontrollen",
            "AI Governance (EU AI Act, Drift Detection, Safety)",
            "Multi-Modal (Text, Bild, Audio, Video)"
        ]
    },
    {
        "id": "02", "name": "audit_logging",
        "desc": "Nachweise & Beweisführung",
        "capabilities": [
            "Hash-Ledger, Evidence-Matrix, Blockchain Anchors",
            "Audit-Trails, Logging, Retention, Quarantine",
            "Compliance-Protokolle, DAO-Governance-Audits"
        ]
    },
    {
        "id": "03", "name": "core",
        "desc": "Zentrale Logik",
        "capabilities": [
            "Smart Contract Kernsystem (On-Chain-Regeln)",
            "Dispatcher-Schnittstellen",
            "Identity-Resolver, Core-APIs",
            "Root-24-LOCK Enforcement"
        ]
    },
    {
        "id": "04", "name": "deployment",
        "desc": "Auslieferung & Distribution",
        "capabilities": [
            "CI/CD-Pipelines, Rollouts, Cluster-Konfiguration",
            "Deployment-Strategien (Canary, Blue/Green)",
            "Container & Orchestrierung (K8s, Terraform)"
        ]
    },
    {
        "id": "05", "name": "documentation",
        "desc": "Dokumentation & I18N",
        "capabilities": [
            "Developer Guides, User Manuals, API Docs",
            "Mehrsprachigkeit (I18N-Layer)",
            "Strukturdateien, Docusaurus Export"
        ]
    },
    {
        "id": "06", "name": "data_pipeline",
        "desc": "Datenfluss & Verarbeitung",
        "capabilities": [
            "ETL/ELT-Prozesse, Datenströme",
            "Orchestrierung (Batch, Stream, Realtime)",
            "ML/AI Data-Feeds"
        ]
    },
    {
        "id": "07", "name": "governance_legal",
        "desc": "Recht & Steuerung",
        "capabilities": [
            "eIDAS, MiCA, DSGVO, DORA",
            "Juristische Policies, Verträge mit Providern",
            "DAO-Governance-Regeln"
        ]
    },
    {
        "id": "08", "name": "identity_score",
        "desc": "Reputation & Scoring",
        "capabilities": [
            "Identity Trust Levels, Reputationssysteme",
            "Scoring-Algorithmen für SSI/DIDs",
            "Verhaltensanalysen (nur Hash-Proofs, keine PII)"
        ]
    },
    {
        "id": "09", "name": "meta_identity",
        "desc": "Digitale Identität",
        "capabilities": [
            "DID-Schemas, Identity Wallets",
            "Selective Disclosure, Profile, Avatare",
            "Identity Lifecycle Management"
        ]
    },
    {
        "id": "10", "name": "interoperability",
        "desc": "Kompatibilität",
        "capabilities": [
            "DID-Resolver, Standards (DIF, W3C)",
            "Cross-Chain Bridges, Protokoll-Adapter",
            "API-Gateways"
        ]
    },
    {
        "id": "11", "name": "test_simulation",
        "desc": "Simulation & QA",
        "capabilities": [
            "Testumgebungen, Simulationen, Mock-Chains",
            "Chaos Engineering, Attack Simulations",
            "Benchmarking & Performance-Tests"
        ]
    },
    {
        "id": "12", "name": "tooling",
        "desc": "Werkzeuge",
        "capabilities": [
            "Developer Tools, CLI, SDKs",
            "CI-Helper, Linter, Formatter",
            "Automation Scripts"
        ]
    },
    {
        "id": "13", "name": "ui_layer",
        "desc": "Benutzeroberfläche",
        "capabilities": [
            "Frontend, Dashboards, Apps",
            "Partner- & User-Portale",
            "Admin-GUIs"
        ]
    },
    {
        "id": "14", "name": "zero_time_auth",
        "desc": "Sofort-Authentifizierung",
        "capabilities": [
            "Real-Time KYC/KYB über Anbieter",
            "Zero-Time Login, Biometrie, MFA",
            "DID-gebundene Session-Tokens"
        ]
    },
    {
        "id": "15", "name": "infra",
        "desc": "Infrastruktur",
        "capabilities": [
            "Cloud, Bare-Metal, Netzwerke",
            "Storage, Compute, Load Balancing",
            "Secrets & Key Management"
        ]
    },
    {
        "id": "16", "name": "codex",
        "desc": "Wissensbasis & Regeln",
        "capabilities": [
            "Codex, Policies, Blaupausen",
            "Regelwerke für Module",
            "SSID-Bibeln (Manifeste, Strukturlevel3)"
        ]
    },
    {
        "id": "17", "name": "observability",
        "desc": "Monitoring & Insights",
        "capabilities": [
            "Logging, Metrics, Tracing",
            "Alerts, Dashboards, SIEM",
            "AI-Ops Monitoring"
        ]
    },
    {
        "id": "18", "name": "data_layer",
        "desc": "Datenhaltung",
        "capabilities": [
            "Datenbanken, GraphDBs, Time-Series",
            "Encryption-at-Rest, Backups",
            "Hash-Speicher"
        ]
    },
    {
        "id": "19", "name": "adapters",
        "desc": "Anschlüsse & Schnittstellen",
        "capabilities": [
            "Adapter zu externen APIs/Chains",
            "Payment-Provider-Connectoren",
            "Identity Provider SDKs"
        ]
    },
    {
        "id": "20", "name": "foundation",
        "desc": "Grundlagen & Tokenomics",
        "capabilities": [
            "SSID-Token (Utility, Governance, Rewards)",
            "Tokenomics, Distribution, Rewards",
            "Lizenzmodelle (NFT-Licenses)"
        ]
    },
    {
        "id": "21", "name": "post_quantum_crypto",
        "desc": "Zukunftskrypto",
        "capabilities": [
            "PQC-Algorithmen (Kyber, Dilithium)",
            "Quantum-Safe Migration",
            "Hybrid-Signaturen"
        ]
    },
    {
        "id": "22", "name": "datasets",
        "desc": "Datenbestände",
        "capabilities": [
            "Public Datasets, Trainingsdaten",
            "Hash-Referenzen statt PII",
            "Zugriff via DID & Consent"
        ]
    },
    {
        "id": "23", "name": "compliance",
        "desc": "Regeltreue",
        "capabilities": [
            "Blacklists, Whitelists, Jurisdiktionsregeln",
            "Policies (AML, KYC, GDPR)",
            "Audit-Logs, Evidence-Registrierung"
        ]
    },
    {
        "id": "24", "name": "meta_orchestration",
        "desc": "Zentrale Steuerung",
        "capabilities": [
            "Dispatcher, Registry, Locks",
            "Trigger & Gates",
            "Versionierung, Global Hash-Ledger"
        ]
    }
]

# 16 SHARDS mit vollständigen Details
SHARDS = [
    {
        "id": "01", "name": "Identitaet_Personen",
        "desc": "DIDs, Ausweise, Profile",
        "sub_desc": "Personen, Firmen, Organisationen, Behörden",
        "domain": "identity",
        "block": 1
    },
    {
        "id": "02", "name": "Dokumente_Nachweise",
        "desc": "Urkunden, Zertifikate",
        "sub_desc": "Digitale Signaturen, Notarisierungen",
        "domain": "documents",
        "block": 1
    },
    {
        "id": "03", "name": "Zugang_Berechtigungen",
        "desc": "Rollen, Rechte",
        "sub_desc": "MFA, Zero-Trust, Session-Management",
        "domain": "access",
        "block": 1
    },
    {
        "id": "04", "name": "Kommunikation_Daten",
        "desc": "Nachrichten, APIs",
        "sub_desc": "APIs, Schnittstellen, Benachrichtigungen",
        "domain": "communication",
        "block": 1
    },
    {
        "id": "05", "name": "Gesundheit_Medizin",
        "desc": "Krankenakte, Rezepte",
        "sub_desc": "Ärzte, Kliniken, Apotheken, Pflegedienste",
        "domain": "health",
        "block": 2
    },
    {
        "id": "06", "name": "Bildung_Qualifikationen",
        "desc": "Zeugnisse, Kurse",
        "sub_desc": "Schulen, Unis, Zertifizierungen, Skills",
        "domain": "education",
        "block": 2
    },
    {
        "id": "07", "name": "Familie_Soziales",
        "desc": "Geburt, Heirat",
        "sub_desc": "Vormundschaft, Betreuung, Sozialleistungen",
        "domain": "family",
        "block": 2
    },
    {
        "id": "08", "name": "Mobilitaet_Fahrzeuge",
        "desc": "Führerschein, KFZ",
        "sub_desc": "TÜV/AU, Fahrzeugkauf, Parkausweise",
        "domain": "mobility",
        "block": 2
    },
    {
        "id": "09", "name": "Arbeit_Karriere",
        "desc": "Arbeitsverträge",
        "sub_desc": "Freelancing, Honorare, Arbeitszeugnisse",
        "domain": "employment",
        "block": 3
    },
    {
        "id": "10", "name": "Finanzen_Banking",
        "desc": "Konten, Zahlungen",
        "sub_desc": "Investments, Portfolios, DeFi, Krypto",
        "domain": "finance",
        "block": 3
    },
    {
        "id": "11", "name": "Versicherungen_Risiken",
        "desc": "Policen, Claims",
        "sub_desc": "Schäden, Claims, Policen, Prämien",
        "domain": "insurance",
        "block": 3
    },
    {
        "id": "12", "name": "Immobilien_Grundstuecke",
        "desc": "Eigentum, Miete",
        "sub_desc": "Hypotheken, Bewertungen, Nutzungsrechte",
        "domain": "realestate",
        "block": 3
    },
    {
        "id": "13", "name": "Unternehmen_Gewerbe",
        "desc": "Firmendaten",
        "sub_desc": "Handelsregister, Lizenzen, B2B",
        "domain": "business",
        "block": 4
    },
    {
        "id": "14", "name": "Vertraege_Vereinbarungen",
        "desc": "Contracts",
        "sub_desc": "Smart Contracts, Geschäftsverträge, AGBs",
        "domain": "contracts",
        "block": 4
    },
    {
        "id": "15", "name": "Handel_Transaktionen",
        "desc": "Käufe, Verkäufe",
        "sub_desc": "Supply Chain, Logistik, Lieferscheine",
        "domain": "commerce",
        "block": 4
    },
    {
        "id": "16", "name": "Behoerden_Verwaltung",
        "desc": "Ämter, Anträge",
        "sub_desc": "Meldewesen, Gerichtsurteile, Ordnungswidrigkeiten",
        "domain": "government",
        "block": 4
    }
]

# Domänen-spezifische Metriken
DOMAIN_METRICS = {
    "identity": ["identity_verifications_total", "biometric_matches_total", "did_resolutions_total"],
    "documents": ["document_verifications_total", "signature_validations_total"],
    "access": ["authentication_attempts_total", "authorization_checks_total"],
    "communication": ["messages_sent_total", "api_calls_total"],
    "health": ["health_records_accessed_total", "prescription_validations_total"],
    "education": ["certificate_verifications_total", "credential_issuances_total"],
    "family": ["registry_updates_total", "social_benefit_checks_total"],
    "mobility": ["license_validations_total", "vehicle_registrations_total"],
    "employment": ["contract_signings_total", "payroll_processings_total"],
    "finance": ["transactions_total", "payment_processing_duration", "fraud_detections_total"],
    "insurance": ["claim_submissions_total", "policy_updates_total"],
    "realestate": ["property_transfers_total", "registry_updates_total"],
    "business": ["registry_queries_total", "compliance_checks_total"],
    "contracts": ["contract_executions_total", "smart_contract_calls_total"],
    "commerce": ["order_processings_total", "shipment_trackings_total"],
    "government": ["application_submissions_total", "permit_issuances_total"]
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def log(msg: str):
    """Logging mit Timestamp"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def mkd(path: Path):
    """Ordner erstellen"""
    path.mkdir(parents=True, exist_ok=True)

def wr(path: Path, content: str):
    """Datei schreiben"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def h(data: str) -> str:
    """SHA3-256 Hash"""
    return hashlib.sha3_256(data.encode()).hexdigest()

def shard_folder_name(shard: Dict) -> str:
    """Shard-Ordnername: Shard_{NR}_{Name}"""
    return f"Shard_{shard['id']}_{shard['name']}"

# ============================================================================
# CHART.YAML - VOLLSTÄNDIG ERWEITERT
# ============================================================================

def gen_chart_yaml(root: Dict, shard: Dict) -> str:
    """chart.yaml mit ALLEN Details aus Master-Definition + v1.1.1"""
    shard_folder = shard_folder_name(shard)
    custom_metrics = DOMAIN_METRICS.get(shard['domain'], ["requests_total"])
    
    return f"""# SSID Project - chart.yaml (Single Source of Truth)
# Root: {root['id']}_{root['name']}
# Shard: {shard_folder}
# Version: {VERSION}
# Auto-generated: {ISO_DATE}

metadata:
  shard_id: "{shard_folder}"
  root: "{root['id']}_{root['name']}"
  version: "{VERSION}"
  status: "production"
  description: "{root['desc']} für {shard['desc']}"
  created: "{ISO_DATE}"
  updated: "{ISO_DATE}"
  maintainers:
    - name: "Team Lead {root['name']}"
      email: "lead-{root['id']}-{shard['id']}@example.local"
  tags:
    - "{root['name']}"
    - "{shard['domain']}"
    - "hash-only"
  deprecation_notice: null
  replaced_by: null

governance:
  owner:
    team: "{root['name']}-{shard['name'].lower()}-team"
    lead: "lead-{root['id']}-{shard['id']}@example.local"
    contact: "team-{root['id']}-{shard['id']}@example.local"
  reviewers:
    architecture: "arch-board@example.local"
    compliance: "compliance@example.local"
    security: "security@example.local"
  change_process:
    rfc_required: true
    approval_quorum: 2
    breaking_change_notice_days: 180
    migration_guide_required: true
    compatibility_layer_required: true

capabilities:
  MUST:
    - capability: "{root['desc']} Kernfunktionen für {shard['desc']}"
      use_cases:
        - "Hash-basierte Datenverarbeitung"
        - "Real-time Audit-Logging"
      sla:
        availability: "99.9%"
        latency_p95: "50ms"
        throughput: "1000 rps"
    - capability: "Hash-basierte Speicherung (SHA3-256)"
      use_cases:
        - "Non-custodial data handling"
        - "GDPR-compliant storage"
      sla:
        availability: "99.99%"
        latency_p95: "10ms"
    - capability: "Audit-Logging Integration"
      use_cases:
        - "Evidence trail creation"
        - "Compliance reporting"
      sla:
        availability: "99.9%"
        latency_p95: "100ms"
  SHOULD:
    - capability: "Performance-Optimierungen"
      use_cases:
        - "Caching layer"
        - "Connection pooling"
    - capability: "Erweiterte Monitoring-Metriken"
      use_cases:
        - "Business KPI tracking"
        - "Custom dashboards"
  HAVE:
    - capability: "Experimentelle Features"
      use_cases:
        - "A/B testing framework"
        - "Feature flags"
    - capability: "ML-basierte Optimierungen"
      use_cases:
        - "Predictive scaling"
        - "Anomaly detection"

constraints:
  pii_storage: "forbidden"
  data_policy: "hash_only"
  custody: "non_custodial_code_only"
  max_depth: 3
  no_circular_dependencies: true
  forbidden_file_types:
    - ".ipynb"
    - ".parquet"
    - ".sqlite"
    - ".db"

enforcement:
  static_analysis:
    - semgrep
    - bandit
    - mypy
  runtime_checks:
    - pii_detector
    - bias_monitor
    - drift_detector
  audit:
    log_to: "02_audit_logging"
    retention_days: 3650
    evidence_anchoring: true

interfaces:
  contracts:
    - "{shard['domain']}_risk_scoring.openapi.yaml"
    - "{shard['domain']}_matching.openapi.yaml"
  data_schemas:
    - "{shard['domain']}_document.schema.json"
    - "{shard['domain']}_evidence.schema.json"
  authentication:
    type: "mTLS"
    cert_rotation_days: 90
  authorization:
    model: "RBAC"
    policies: "policies/rbac.yaml"

dependencies:
  required:
    - root: "02_audit_logging"
      reason: "Audit trail for all operations"
      min_version: ">=2.0.0"
      endpoints:
        - "POST /v1/audit/log"
    - root: "09_meta_identity"
      reason: "Identity resolution"
      min_version: ">=1.5.0"
      endpoints:
        - "GET /v1/identity/resolve"
    - root: "17_observability"
      reason: "Metrics and tracing"
      min_version: ">=1.0.0"
      endpoints:
        - "POST /v1/metrics"
  optional:
    - root: "11_test_simulation"
      reason: "Testing integration"
    - root: "22_datasets"
      reason: "Training datasets"

compatibility:
  semver: "{VERSION}"
  core_min_version: ">=3.0.0"
  breaking_changes: []

implementations:
  default: "python-tensorflow"
  available:
    - "python-tensorflow"
    - "rust-burn"

conformance:
  test_framework: "schemathesis"
  contract_tests:
    - "{shard['domain']}_scoring_contract_test.yaml"
    - "{shard['domain']}_matching_contract_test.yaml"

orchestration:
  workflows:
    - name: "{shard['domain']}_full_lifecycle"
      triggers:
        - "data_received"
        - "periodic_rescoring"
      steps:
        - name: "validate_input"
          root: "03_core"
          timeout: "5s"
        - name: "process_data"
          root: "{root['id']}_{root['name']}"
          timeout: "30s"
        - name: "log_evidence"
          root: "02_audit_logging"
          timeout: "10s"
        - name: "anchor_to_blockchain"
          root: "02_audit_logging"
          timeout: "60s"

testing:
  unit:
    location: "11_test_simulation/{root['name']}/{shard_folder}/unit/"
    min_coverage: 90
  integration:
    location: "11_test_simulation/{root['name']}/{shard_folder}/integration/"
    min_coverage: 80
  contract:
    location: "../conformance/"
    required: true
  e2e:
    location: "11_test_simulation/{root['name']}/e2e/"
    scenarios:
      - "full_{shard['domain']}_lifecycle"
      - "{shard['domain']}_error_recovery"
      - "{shard['domain']}_high_load"

documentation:
  auto_generate:
    - source: "contracts/*.openapi.yaml"
      target: "05_documentation/api/{root['name']}/{shard_folder}/"
    - source: "contracts/schemas/*.schema.json"
      target: "05_documentation/schemas/{root['name']}/{shard_folder}/"
  manual:
    - "docs/getting-started.md"
    - "docs/model_cards/"
    - "docs/security/threat_model.md"

observability:
  metrics:
    provider: "prometheus"
    namespace: "ssid_{root['name']}_{shard['domain']}"
    custom_metrics: {custom_metrics}
  tracing:
    provider: "jaeger"
    sample_rate: 0.1
  logging:
    provider: "loki"
    format: "json"
    pii_redaction: true
    severity_levels: ["ERROR", "WARN", "INFO", "DEBUG"]
  alerting:
    rules:
      - name: "error_rate_high"
        condition: "error_rate > 0.05"
        severity: "critical"
        notification:
          - "slack://alerts"
          - "pagerduty://on-call"
      - name: "latency_high"
        condition: "latency_p95 > 100ms"
        severity: "warning"

evidence:
  strategy: "hash_ledger_with_anchoring"
  retention_days: 3650
  storage_type: "WORM"
  anchoring:
    chains:
      - "ethereum:sepolia"
      - "polygon:amoy"
    frequency: "hourly"
    batch_size: 1000
    batch_strategy: "time_or_count"
    retry_policy:
      max_retries: 3
      backoff: "exponential"
  logged_events:
    - "data_processed"
    - "model_inference"
    - "evidence_created"

security:
  threat_model: "docs/security/threat_model.md"
  secrets_management: "15_infra/vault"
  encryption:
    at_rest: "AES-256-GCM"
    in_transit: "TLS 1.3"
  rate_limiting:
    enabled: true
    requests_per_minute: 1000
  network_policies:
    ingress:
      - from: ["02_audit_logging", "17_observability"]
    egress:
      - to: ["09_meta_identity"]

deployment:
  strategy: "blue-green"
  environments:
    - "dev"
    - "staging"
    - "production"
  rollback:
    automatic: true
    conditions:
      - "error_rate > 5%"
      - "latency_p95 > 100ms"
    retention_versions: 3

resources:
  compute:
    cpu: "4 cores"
    memory: "16Gi"
    autoscaling:
      enabled: true
      min_replicas: 2
      max_replicas: 20

roadmap:
  upcoming:
    - version: "1.1.0"
      release_date: "Q2 2025"
      features:
        - "Performance improvements (cache layer)"
        - "Enhanced XAI (explainability)"
      breaking_changes: false
      migration_required: false
    - version: "2.0.0"
      release_date: "Q4 2025"
      features:
        - "Multi-region support"
        - "Quantum-safe signatures"
      breaking_changes: true
      migration_required: true
"""

# ============================================================================
# MANIFEST.YAML - VOLLSTÄNDIG ERWEITERT
# ============================================================================

def gen_manifest_yaml(root: Dict, shard: Dict) -> str:
    """manifest.yaml mit ALLEN Details + v1.1.1"""
    shard_folder = shard_folder_name(shard)
    
    return f"""# SSID Project - manifest.yaml (Implementation Manifest)
# Root: {root['id']}_{root['name']}
# Shard: {shard_folder}
# Implementation: python-tensorflow
# Auto-generated: {ISO_DATE}

metadata:
  implementation_id: "python-tensorflow"
  implementation_version: "1.0.0"
  chart_version: "{VERSION}"
  maturity: "production"
  language: "python"
  framework: "tensorflow"
  is_default_implementation: true

technology_stack:
  language:
    name: "python"
    version: "3.11.5"
    version_range: ">=3.11.0,<3.12.0"
  frameworks:
    ml:
      - name: "tensorflow"
        version: "2.15.0"
        version_range: ">=2.14.0,<3.0.0"
        alternatives:
          - "pytorch>=2.0"
      - name: "scikit-learn"
        version: "1.3.2"
      - name: "numpy"
        version: "1.26.2"
    api:
      - name: "fastapi"
        version: "0.104.1"
      - name: "uvicorn"
        version: "0.24.0"
    utilities:
      - name: "pydantic"
        version: "2.5.0"
      - name: "pyyaml"
        version: "6.0.1"
      - name: "cryptography"
        version: "41.0.7"
  testing:
    - "pytest==7.4.3"
    - "pytest-cov==4.1.0"
    - "schemathesis==3.19.7"
    - "httpx==0.25.1"
  linting_formatting:
    - "black==23.11.0"
    - "ruff==0.1.6"
    - "mypy==1.7.0"
    - "bandit==1.7.5"
    - "semgrep==1.45.0"

artifacts:
  source_code:
    location: "src/"
    structure:
      - "main.py"
      - "api/endpoints.py"
      - "api/middleware.py"
      - "api/auth.py"
      - "api/health.py"
      - "services/{shard['domain']}_risk_scorer.py"
      - "services/{shard['domain']}_matcher.py"
      - "services/trust_evaluator.py"
      - "models/risk_scoring_model.py"
      - "models/{shard['domain']}_feature_extractor.py"
      - "utils/hasher.py"
      - "utils/pii_detector.py"
      - "utils/bias_monitor.py"
      - "grpc_handlers/handler.py"
  configuration:
    location: "config/"
    files:
      - "settings.yaml"
      - "model_config.yaml"
      - "logging.yaml"
      - "redis.yaml"
      - "vault.yaml"
  tests:
    location: "tests/"
    structure:
      - "unit/"
      - "integration/"
      - "fixtures/"
      - "performance/"
    note: "Tests are BOTH local AND central (11_test_simulation)"
  models:
    location: "models/"
    files:
      - "{shard['domain']}_risk_scorer_v2.1.h5"
      - "{shard['domain']}_feature_extractor_v1.3.h5"
  protocols:
    location: "proto/"
    files:
      - "{shard['domain']}.proto"
  documentation:
    location: "docs/"
    files:
      - "getting-started.md"
      - "api-usage.md"
      - "model_cards/"
  scripts:
    location: "scripts/"
    files:
      - "train_model.sh"
      - "run_migrations.sh"
  docker:
    files:
      - "Dockerfile"
      - "docker-compose.yml"

dependencies:
  python_packages: "requirements.txt"
  development_packages: "requirements-dev.txt"
  system_dependencies:
    - "libssl-dev"
    - "build-essential"
  external_services:
    - root: "02_audit_logging"
      endpoint: "http://audit-logging.ssid.local:8080"
    - root: "17_observability"
      endpoint: "http://observability.ssid.local:9090"

build:
  commands:
    install_dependencies: "pip install -r requirements.txt"
    compile_protos: "python -m grpc_tools.protoc"
    run_tests: "pytest -v --cov=src --cov-report=html"
    lint: "ruff check src/ && black --check src/ && mypy src/"
    security_scan: "bandit -r src/ && semgrep --config auto src/"
  optimization:
    strip_debug_symbols: true
    compile_bytecode: true
    wheel_caching: true
  docker:
    build_command: "docker build -t ssid/{root['name']}-{shard['domain']}:latest ."
    image_registry: "registry.ssid.local"

deployment:
  kubernetes:
    manifests_location: "k8s/"
    files:
      - "deployment.yaml"
      - "service.yaml"
      - "configmap.yaml"
      - "secret.yaml"
      - "hpa.yaml"
      - "ingress.yaml"
  helm:
    chart_location: "helm/"
  environment_variables:
    required:
      - "REDIS_URL"
      - "AUDIT_LOG_ENDPOINT"
      - "VAULT_ADDR"
    optional:
      - "LOG_LEVEL"
      - "METRICS_PORT"
      - "MODEL_VERSION"
  rollback:
    automatic: true
    conditions:
      - "error_rate > 5%"
      - "latency_p95 > 100ms"
    retention_versions: 3

testing:
  unit_tests:
    command: "pytest tests/unit/"
    coverage_target: 90
    pass_threshold: 90
    fail_threshold: 80
  integration_tests:
    command: "pytest tests/integration/"
    coverage_target: 80
  contract_tests:
    command: "schemathesis run ../contracts/*.openapi.yaml"
  security_tests:
    static_analysis: "bandit -r src/"
    dynamic_analysis: "zap-baseline.py"
  performance_tests:
    tool: "locust"
    target_rps: 1000

observability:
  metrics:
    exporter: "prometheus_client"
    port: 9090
    custom_metrics:
      - "http_requests_total"
      - "processing_duration"
      - "model_drift"
  tracing:
    exporter: "jaeger"
    endpoint: "http://jaeger.ssid.local:14268/api/traces"
    sample_rate: 0.1
  logging:
    format: "json"
    pii_redaction: true
    handlers:
      - "console"
      - "loki"
  health_checks:
    liveness: "/health/live"
    readiness: "/health/ready"
  alerting:
    rules:
      - name: "high_error_rate"
        condition: "error_rate > 0.05"
        severity: "critical"
        notification:
          - "slack://alerts"
          - "pagerduty://on-call"

development:
  setup:
    steps:
      - "python -m venv venv"
      - "source venv/bin/activate"
      - "pip install -r requirements-dev.txt"
      - "pre-commit install"
  local_development:
    docker_compose: true
    hot_reload: true
  pre_commit_hooks:
    - "black"
    - "ruff"
    - "mypy"

compliance:
  non_custodial_enforcement:
    - "No PII in service metadata"
    - "Hash-only references"
  gdpr_compliance:
    - "Right to erasure: hash rotation"
    - "Data portability: JSON export"
  bias_fairness:
    - "Mandatory bias testing"
    - "Quarterly audits"
  dora_compliance:
    - "Incident response plan required"
    - "4h notification for major incidents"
    - "14-day final report"
  regulatory_matrix:
    uk:
      ico_uk_gdpr:
        mandatory: true
        requirements:
          - "dpa_2018_alignment"
          - "dpo_contact_records"
    singapore:
      mas_pdpa:
        mandatory: true
        requirements:
          - "data_breach_notification"
          - "consent_purposes_documented"
    japan:
      jfsa_appi:
        mandatory: true
    australia:
      au_privacy_act_1988:
        mandatory: true

performance:
  baseline_benchmarks:
    - metric: "inference_latency_p95"
      value: "50ms"
    - metric: "throughput_rps"
      value: "1000"
    - metric: "memory_usage"
      value: "800MB"
  optimization_targets:
    - "Reduce latency to <30ms p95"
    - "Increase throughput to 2000 rps"
    - metric: "memory_usage"
      target: "<1GB"
  profiling:
    enabled: true
    tool: "py-spy"
    sample_rate: 100
  resource_requirements:
    minimum:
      cpu: "2 cores"
      memory: "8Gi"
    recommended:
      cpu: "4 cores"
      memory: "16Gi"

changelog:
  location: "CHANGELOG.md"
  latest_versions:
    - version: "1.0.0"
      date: "{ISO_DATE[:10]}"
      changes:
        - "Initial release"
        - "Core functionality"
        - "Hash-only implementation"

support:
  documentation: "https://docs.ssid.example/{root['name']}/{shard_folder}/"
  contacts:
    general: "support@example.local"
    security: "security@example.local"
    on_call: "oncall@example.local"
  runbooks:
    - title: "High Latency Debugging"
      url: "https://docs.ssid.example/runbooks/high-latency"
    - title: "Memory Leak Investigation"
      url: "https://docs.ssid.example/runbooks/memory-leak"
    - title: "DORA Incident Response"
      url: "https://docs.ssid.example/runbooks/dora-incident"
"""

# ============================================================================
# WEITER IM NÄCHSTEN ARTIFACT (Teil 2/3)
# ============================================================================
