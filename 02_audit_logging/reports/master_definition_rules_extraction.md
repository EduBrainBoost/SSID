# Master Definition Rules Extraction Report
## Version: 1.1.1
## Source: ssid_master_definition_corrected_v1.1.1.md
## Date: 2025-10-20
## Extractor: Claude Code

---

## 🎯 Zweck
Vollständige Extraktion ALLER Regeln aus der Master-Definition v1.1.1 für Coverage-Checking gegen die 5 SoT-Artefakte.

---

## 📊 Regel-Kategorien

### KATEGORIE 1: STRUKTURREGELN (Architektur)

| Rule ID | Description | Source Section | Severity | MUSS/SOLL |
|---------|-------------|----------------|----------|-----------|
| **MD-STRUCT-001** | System MUSS aus exakt 24 Root-Ordnern bestehen | §Die 24 Root-Ordner | CRITICAL | MUSS |
| **MD-STRUCT-002** | Jeder Root MUSS exakt 16 Shards enthalten | §Die 16 Shards | CRITICAL | MUSS |
| **MD-STRUCT-003** | Matrix MUSS 24×16=384 Chart-Dateien bilden | §Matrix-Architektur | CRITICAL | MUSS |
| **MD-STRUCT-004** | Jeder Shard MUSS ein chart.yaml enthalten | §Hybrid-Struktur | CRITICAL | MUSS |
| **MD-STRUCT-005** | Jeder Shard MUSS ein values.yaml enthalten | §Hybrid-Struktur | CRITICAL | MUSS |
| **MD-STRUCT-006** | Jeder Root MUSS eine README.md enthalten | §Ordnerstruktur | CRITICAL | MUSS |
| **MD-STRUCT-007** | Root-Namen MÜSSEN Pattern {NR}_{NAME} folgen (01-24) | §Naming Conventions | CRITICAL | MUSS |
| **MD-STRUCT-008** | Shard-Namen MÜSSEN Pattern Shard_{NR}_{NAME} folgen (01-16) | §Naming Conventions | CRITICAL | MUSS |
| **MD-STRUCT-009** | Pfad MUSS {ROOT}/shards/{SHARD}/chart.yaml sein | §Naming Conventions | CRITICAL | MUSS |
| **MD-STRUCT-010** | Pfad MUSS {ROOT}/shards/{SHARD}/implementations/{IMPL_ID}/manifest.yaml sein | §Naming Conventions | CRITICAL | MUSS |

### KATEGORIE 2: CHART.YAML STRUKTUR (SoT)

| Rule ID | Description | Source Section | Severity | MUSS/SOLL |
|---------|-------------|----------------|----------|-----------|
| **MD-CHART-001** | chart.yaml MUSS metadata.shard_id enthalten | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-002** | chart.yaml MUSS metadata.version enthalten | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-003** | chart.yaml MUSS metadata.status enthalten | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-004** | chart.yaml MUSS governance.owner.team enthalten | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-005** | chart.yaml MUSS governance.owner.lead enthalten | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-006** | chart.yaml MUSS governance.owner.contact enthalten | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-007** | chart.yaml MUSS governance.reviewers definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-008** | chart.yaml MUSS governance.change_process definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-009** | chart.yaml MUSS capabilities.MUST definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-010** | chart.yaml SOLL capabilities.SHOULD definieren | §chart.yaml Struktur | MEDIUM | SOLL |
| **MD-CHART-011** | chart.yaml KANN capabilities.HAVE definieren | §chart.yaml Struktur | LOW | KANN |
| **MD-CHART-012** | chart.yaml MUSS constraints.pii_storage="forbidden" setzen | §chart.yaml Struktur | CRITICAL | MUSS |
| **MD-CHART-013** | chart.yaml MUSS constraints.data_policy="hash_only" setzen | §chart.yaml Struktur | CRITICAL | MUSS |
| **MD-CHART-014** | chart.yaml MUSS constraints.custody="non_custodial_code_only" setzen | §chart.yaml Struktur | CRITICAL | MUSS |
| **MD-CHART-015** | chart.yaml MUSS enforcement.static_analysis definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-016** | chart.yaml MUSS enforcement.runtime_checks definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-017** | chart.yaml MUSS enforcement.audit definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-018** | chart.yaml MUSS interfaces.contracts (OpenAPI) definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-019** | chart.yaml MUSS interfaces.data_schemas (JSON Schema) definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-020** | chart.yaml MUSS interfaces.authentication="mTLS" setzen | §chart.yaml Struktur | CRITICAL | MUSS |
| **MD-CHART-021** | chart.yaml MUSS dependencies.required auflisten | §chart.yaml Struktur | MEDIUM | MUSS |
| **MD-CHART-022** | chart.yaml SOLL dependencies.optional auflisten | §chart.yaml Struktur | LOW | SOLL |
| **MD-CHART-023** | chart.yaml MUSS compatibility.semver definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-024** | chart.yaml MUSS compatibility.core_min_version definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-025** | chart.yaml MUSS implementations.default definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-026** | chart.yaml MUSS implementations.available auflisten | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-027** | chart.yaml MUSS conformance.test_framework definieren | §chart.yaml Struktur | MEDIUM | MUSS |
| **MD-CHART-028** | chart.yaml MUSS conformance.contract_tests definieren | §chart.yaml Struktur | MEDIUM | MUSS |
| **MD-CHART-029** | chart.yaml SOLL orchestration.workflows definieren | §chart.yaml Struktur | LOW | SOLL |
| **MD-CHART-030** | chart.yaml MUSS testing.unit definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-031** | chart.yaml MUSS testing.integration definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-032** | chart.yaml MUSS testing.contract definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-033** | chart.yaml SOLL testing.e2e definieren | §chart.yaml Struktur | MEDIUM | SOLL |
| **MD-CHART-034** | chart.yaml MUSS documentation.auto_generate definieren | §chart.yaml Struktur | MEDIUM | MUSS |
| **MD-CHART-035** | chart.yaml SOLL documentation.manual definieren | §chart.yaml Struktur | LOW | SOLL |
| **MD-CHART-036** | chart.yaml MUSS observability.metrics.prometheus definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-037** | chart.yaml MUSS observability.tracing.jaeger definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-038** | chart.yaml MUSS observability.logging.loki definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-039** | chart.yaml MUSS observability.logging.pii_redaction=true setzen | §chart.yaml Struktur | CRITICAL | MUSS |
| **MD-CHART-040** | chart.yaml SOLL observability.alerting definieren | §chart.yaml Struktur | MEDIUM | SOLL |
| **MD-CHART-041** | chart.yaml MUSS evidence.strategy="hash_ledger_with_anchoring" setzen | §chart.yaml Struktur | CRITICAL | MUSS |
| **MD-CHART-042** | chart.yaml MUSS evidence.anchoring.chains=[ethereum,polygon] definieren | §chart.yaml Struktur | CRITICAL | MUSS |
| **MD-CHART-043** | chart.yaml MUSS security.threat_model referenzieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-044** | chart.yaml MUSS security.secrets_management="15_infra/vault" setzen | §chart.yaml Struktur | CRITICAL | MUSS |
| **MD-CHART-045** | chart.yaml MUSS security.encryption (at_rest, in_transit) definieren | §chart.yaml Struktur | CRITICAL | MUSS |
| **MD-CHART-046** | chart.yaml MUSS deployment.strategy="blue-green" ODER "canary" setzen | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-047** | chart.yaml MUSS deployment.environments=[dev,staging,production] definieren | §chart.yaml Struktur | HIGH | MUSS |
| **MD-CHART-048** | chart.yaml MUSS resources.compute definieren | §chart.yaml Struktur | MEDIUM | MUSS |
| **MD-CHART-049** | chart.yaml MUSS resources.autoscaling definieren | §chart.yaml Struktur | MEDIUM | MUSS |
| **MD-CHART-050** | chart.yaml SOLL roadmap.upcoming definieren | §chart.yaml Struktur | LOW | SOLL |

### KATEGORIE 3: MANIFEST.YAML STRUKTUR (Implementierung)

| Rule ID | Description | Source Section | Severity | MUSS/SOLL |
|---------|-------------|----------------|----------|-----------|
| **MD-MANIFEST-001** | manifest.yaml MUSS metadata.implementation_id enthalten | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-002** | manifest.yaml MUSS metadata.implementation_version enthalten | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-003** | manifest.yaml MUSS metadata.chart_version enthalten | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-004** | manifest.yaml MUSS metadata.maturity enthalten | §manifest.yaml Struktur | MEDIUM | MUSS |
| **MD-MANIFEST-005** | manifest.yaml MUSS technology_stack.language.name enthalten | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-006** | manifest.yaml MUSS technology_stack.language.version enthalten | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-007** | manifest.yaml MUSS technology_stack.frameworks definieren | §manifest.yaml Struktur | MEDIUM | MUSS |
| **MD-MANIFEST-008** | manifest.yaml MUSS technology_stack.testing definieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-009** | manifest.yaml MUSS technology_stack.linting_formatting definieren | §manifest.yaml Struktur | MEDIUM | MUSS |
| **MD-MANIFEST-010** | manifest.yaml MUSS artifacts.source_code.location definieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-011** | manifest.yaml MUSS artifacts.source_code.structure definieren | §manifest.yaml Struktur | MEDIUM | MUSS |
| **MD-MANIFEST-012** | manifest.yaml MUSS artifacts.configuration.location definieren | §manifest.yaml Struktur | MEDIUM | MUSS |
| **MD-MANIFEST-013** | manifest.yaml SOLL artifacts.models.location definieren (wenn AI/ML) | §manifest.yaml Struktur | MEDIUM | SOLL |
| **MD-MANIFEST-014** | manifest.yaml SOLL artifacts.protocols.location definieren (wenn gRPC) | §manifest.yaml Struktur | MEDIUM | SOLL |
| **MD-MANIFEST-015** | manifest.yaml MUSS artifacts.tests.location definieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-016** | manifest.yaml MUSS artifacts.documentation.location definieren | §manifest.yaml Struktur | MEDIUM | MUSS |
| **MD-MANIFEST-017** | manifest.yaml MUSS artifacts.scripts.location definieren | §manifest.yaml Struktur | LOW | MUSS |
| **MD-MANIFEST-018** | manifest.yaml MUSS artifacts.docker.files=[Dockerfile,docker-compose.yml] definieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-019** | manifest.yaml MUSS dependencies.python_packages="requirements.txt" referenzieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-020** | manifest.yaml MUSS dependencies.development_packages referenzieren | §manifest.yaml Struktur | MEDIUM | MUSS |
| **MD-MANIFEST-021** | manifest.yaml SOLL dependencies.system_dependencies auflisten | §manifest.yaml Struktur | LOW | SOLL |
| **MD-MANIFEST-022** | manifest.yaml MUSS dependencies.external_services auflisten | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-023** | manifest.yaml MUSS build.commands definieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-024** | manifest.yaml MUSS build.docker definieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-025** | manifest.yaml MUSS deployment.kubernetes.manifests_location definieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-026** | manifest.yaml SOLL deployment.helm.chart_location definieren | §manifest.yaml Struktur | MEDIUM | SOLL |
| **MD-MANIFEST-027** | manifest.yaml MUSS deployment.environment_variables definieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-028** | manifest.yaml MUSS testing.unit_tests.command definieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-029** | manifest.yaml MUSS testing.unit_tests.coverage_target>=80 setzen | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-030** | manifest.yaml MUSS testing.integration_tests definieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-031** | manifest.yaml MUSS testing.contract_tests definieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-032** | manifest.yaml MUSS testing.security_tests definieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-033** | manifest.yaml SOLL testing.performance_tests definieren | §manifest.yaml Struktur | MEDIUM | SOLL |
| **MD-MANIFEST-034** | manifest.yaml MUSS observability.metrics.exporter="prometheus" setzen | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-035** | manifest.yaml MUSS observability.tracing.exporter="jaeger" setzen | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-036** | manifest.yaml MUSS observability.logging.format="json" setzen | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-037** | manifest.yaml MUSS observability.logging.pii_redaction=true setzen | §manifest.yaml Struktur | CRITICAL | MUSS |
| **MD-MANIFEST-038** | manifest.yaml MUSS observability.health_checks.liveness definieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-039** | manifest.yaml MUSS observability.health_checks.readiness definieren | §manifest.yaml Struktur | HIGH | MUSS |
| **MD-MANIFEST-040** | manifest.yaml MUSS development.setup definieren | §manifest.yaml Struktur | MEDIUM | MUSS |
| **MD-MANIFEST-041** | manifest.yaml MUSS development.local_development definieren | §manifest.yaml Struktur | MEDIUM | MUSS |
| **MD-MANIFEST-042** | manifest.yaml SOLL development.pre_commit_hooks definieren | §manifest.yaml Struktur | LOW | SOLL |
| **MD-MANIFEST-043** | manifest.yaml MUSS compliance.non_custodial_enforcement definieren | §manifest.yaml Struktur | CRITICAL | MUSS |
| **MD-MANIFEST-044** | manifest.yaml MUSS compliance.gdpr_compliance definieren | §manifest.yaml Struktur | CRITICAL | MUSS |
| **MD-MANIFEST-045** | manifest.yaml MUSS compliance.bias_fairness definieren (wenn AI/ML) | §manifest.yaml Struktur | CRITICAL | MUSS |
| **MD-MANIFEST-046** | manifest.yaml MUSS performance.baseline_benchmarks definieren | §manifest.yaml Struktur | MEDIUM | MUSS |
| **MD-MANIFEST-047** | manifest.yaml SOLL performance.optimization_targets definieren | §manifest.yaml Struktur | LOW | SOLL |
| **MD-MANIFEST-048** | manifest.yaml MUSS performance.resource_requirements definieren | §manifest.yaml Struktur | MEDIUM | MUSS |
| **MD-MANIFEST-049** | manifest.yaml MUSS changelog.location="CHANGELOG.md" referenzieren | §manifest.yaml Struktur | MEDIUM | MUSS |
| **MD-MANIFEST-050** | manifest.yaml MUSS support.contacts definieren | §manifest.yaml Struktur | MEDIUM | MUSS |

### KATEGORIE 4: KRITISCHE POLICIES

| Rule ID | Description | Source Section | Severity | MUSS/SOLL |
|---------|-------------|----------------|----------|-----------|
| **MD-POLICY-001** | NIEMALS Rohdaten von PII speichern | §Kritische Policies | CRITICAL | NIEMALS |
| **MD-POLICY-002** | Nur Hash-basierte Speicherung (SHA3-256) erlaubt | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-003** | Tenant-spezifische Peppers MÜSSEN verwendet werden | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-004** | Raw Data Retention MUSS 0 seconds sein | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-005** | Static Analysis (Semgrep) MUSS PII-Storage blockieren | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-006** | Runtime PII-Detector MUSS Verstöße blockieren | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-007** | Hash-Algorithmus MUSS SHA3-256 sein | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-008** | Pepper-Strategie MUSS per_tenant sein | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-009** | Hashing MUSS deterministisch sein | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-010** | Right to Erasure MUSS via Hash-Rotation erfolgen | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-011** | Data Portability MUSS JSON-Export bieten | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-012** | Purpose Limitation MUSS erzwungen werden | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-013** | PII Redaction MUSS automatisch in Logs erfolgen | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-014** | Bias Testing MUSS für alle AI/ML-Modelle durchgeführt werden | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-015** | Fairness-Metrics MÜSSEN Demographic Parity & Equal Opportunity umfassen | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-016** | Quarterly Bias Audits MÜSSEN durchgeführt werden | §Kritische Policies | HIGH | MUSS |
| **MD-POLICY-017** | Model Cards MÜSSEN transparent veröffentlicht werden | §Kritische Policies | HIGH | MUSS |
| **MD-POLICY-018** | Bias-Mitigation-Strategien MÜSSEN verpflichtend sein | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-019** | Evidence-Strategie MUSS Hash-Ledger mit Blockchain-Anchoring sein | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-020** | WORM-Storage MUSS verwendet werden | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-021** | Retention MUSS 10 Jahre betragen | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-022** | Blockchain-Anchoring MUSS Ethereum Mainnet UND Polygon verwenden | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-023** | Anchoring MUSS hourly erfolgen | §Kritische Policies | HIGH | MUSS |
| **MD-POLICY-024** | Secrets Provider MUSS Vault (15_infra/vault) sein | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-025** | Secrets Rotation MUSS alle 90 Tage erfolgen | §Kritische Policies | HIGH | MUSS |
| **MD-POLICY-026** | NIEMALS Secrets in Git committen | §Kritische Policies | CRITICAL | NIEMALS |
| **MD-POLICY-027** | Encryption at-rest MUSS AES-256-GCM verwenden | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-028** | Encryption in-transit MUSS TLS 1.3 verwenden | §Kritische Policies | CRITICAL | MUSS |
| **MD-POLICY-029** | Versioning MUSS Semver (MAJOR.MINOR.PATCH) folgen | §Kritische Policies | HIGH | MUSS |
| **MD-POLICY-030** | Breaking Changes MÜSSEN Migration Guide + Compatibility Layer haben | §Kritische Policies | HIGH | MUSS |
| **MD-POLICY-031** | Deprecations MÜSSEN 180 Tage Notice Period haben | §Kritische Policies | HIGH | MUSS |
| **MD-POLICY-032** | RFC-Prozess MUSS für alle MUST-Capability-Änderungen durchgeführt werden | §Kritische Policies | HIGH | MUSS |

### KATEGORIE 5: GOVERNANCE

| Rule ID | Description | Source Section | Severity | MUSS/SOLL |
|---------|-------------|----------------|----------|-----------|
| **MD-GOV-001** | Jeder Shard MUSS einen Owner haben | §Governance-Modell | HIGH | MUSS |
| **MD-GOV-002** | Owner MUSS für Shard-Entwicklung verantwortlich sein | §Governance-Modell | HIGH | MUSS |
| **MD-GOV-003** | Architecture Board MUSS alle chart.yaml-Änderungen reviewen | §Governance-Modell | HIGH | MUSS |
| **MD-GOV-004** | Architecture Board MUSS Breaking Changes genehmigen | §Governance-Modell | HIGH | MUSS |
| **MD-GOV-005** | Compliance Team MUSS alle Policies prüfen | §Governance-Modell | HIGH | MUSS |
| **MD-GOV-006** | Compliance Team MUSS Constraint-Änderungen genehmigen | §Governance-Modell | HIGH | MUSS |
| **MD-GOV-007** | Security Team MUSS Threat Modeling durchführen | §Governance-Modell | HIGH | MUSS |
| **MD-GOV-008** | Change-Prozess MUSS 7 Schritte durchlaufen (RFC → Tests → Review → Semver → CI/CD → Canary → Monitoring) | §Governance-Modell | HIGH | MUSS |
| **MD-GOV-009** | SHOULD→MUST Promotion MUSS >= 90 Tage Production + >= 99.5% SLA erfüllen | §Governance-Modell | HIGH | MUSS |
| **MD-GOV-010** | SHOULD→MUST Promotion MUSS >= 95% Contract Test Coverage haben | §Governance-Modell | HIGH | MUSS |
| **MD-GOV-011** | HAVE→SHOULD Promotion MUSS Feature complete + Beta-Testing + vollständige Doku haben | §Governance-Modell | MEDIUM | MUSS |
| **MD-GOV-012** | MUST→Deprecated MUSS 180d Notice + Migration Guide + Compatibility Layer haben | §Governance-Modell | HIGH | MUSS |

### KATEGORIE 6: KERNPRINZIPIEN (Details)

| Rule ID | Description | Source Section | Severity | MUSS/SOLL |
|---------|-------------|----------------|----------|-----------|
| **MD-PRINC-001** | API-Contract (OpenAPI/JSON-Schema) MUSS VOR Implementierung existieren | §Kernprinzipien | HIGH | MUSS |
| **MD-PRINC-002** | SoT (chart.yaml) und Implementierung (manifest.yaml) MÜSSEN getrennt sein | §Kernprinzipien | HIGH | MUSS |
| **MD-PRINC-003** | Ein Shard MUSS mehrere Implementierungen unterstützen können | §Kernprinzipien | MEDIUM | MUSS |
| **MD-PRINC-004** | 24×16=384 Chart-Dateien MÜSSEN existieren, keine Ausnahmen | §Kernprinzipien | CRITICAL | MUSS |
| **MD-PRINC-005** | Alles relevante MUSS gehasht, geloggt und geanchort werden | §Kernprinzipien | CRITICAL | MUSS |
| **MD-PRINC-006** | mTLS MUSS für alle internen Verbindungen verwendet werden | §Kernprinzipien | CRITICAL | MUSS |
| **MD-PRINC-007** | RBAC MUSS für alle Zugriffe verwendet werden | §Kernprinzipien | CRITICAL | MUSS |
| **MD-PRINC-008** | PII-Detection MUSS zur Laufzeit erfolgen | §Kernprinzipien | CRITICAL | MUSS |
| **MD-PRINC-009** | Continuous Vulnerability Scanning MUSS durchgeführt werden | §Kernprinzipien | HIGH | MUSS |
| **MD-PRINC-010** | Metrics (Prometheus) MÜSSEN von Anfang an eingebaut sein | §Kernprinzipien | HIGH | MUSS |
| **MD-PRINC-011** | Tracing (Jaeger/OpenTelemetry) MUSS von Anfang an eingebaut sein | §Kernprinzipien | HIGH | MUSS |
| **MD-PRINC-012** | Logging (Loki, JSON-Format, PII-Redaction) MUSS von Anfang an eingebaut sein | §Kernprinzipien | HIGH | MUSS |
| **MD-PRINC-013** | Alerting (AlertManager) MUSS konfiguriert sein | §Kernprinzipien | HIGH | MUSS |
| **MD-PRINC-014** | Fairness-Metrics MÜSSEN Demographic Parity & Equal Opportunity umfassen | §Kernprinzipien | CRITICAL | MUSS |
| **MD-PRINC-015** | Quarterly Bias Audits MÜSSEN durchgeführt werden | §Kernprinzipien | HIGH | MUSS |
| **MD-PRINC-016** | Model Cards MÜSSEN transparent veröffentlicht werden | §Kernprinzipien | HIGH | MUSS |
| **MD-PRINC-017** | Horizontal Pod Autoscaling (HPA) MUSS implementiert sein | §Kernprinzipien | MEDIUM | MUSS |
| **MD-PRINC-018** | Load Balancing MUSS implementiert sein | §Kernprinzipien | HIGH | MUSS |
| **MD-PRINC-019** | Caching-Strategien MÜSSEN definiert sein | §Kernprinzipien | MEDIUM | MUSS |
| **MD-PRINC-020** | Performance-Benchmarks MÜSSEN als Gates fungieren | §Kernprinzipien | MEDIUM | MUSS |
| **MD-PRINC-021** | Dokumentation MUSS aus Contracts/Schemas generiert werden | §Kernprinzipien | MEDIUM | MUSS |
| **MD-PRINC-022** | OpenAPI MUSS zu Swagger UI führen | §Kernprinzipien | MEDIUM | MUSS |
| **MD-PRINC-023** | JSON-Schema MUSS zu json-schema-for-humans führen | §Kernprinzipien | MEDIUM | MUSS |

### KATEGORIE 7: KONSOLIDIERTE ERGÄNZUNGEN v1.1.1

| Rule ID | Description | Source Section | Severity | MUSS/SOLL |
|---------|-------------|----------------|----------|-----------|
| **MD-EXT-001** | UK ICO GDPR MUSS mandatory=true sein | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-002** | UK DPA 2018 alignment MUSS true sein | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-003** | UK DPO contact records MÜSSEN vorhanden sein | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-004** | Singapore MAS PDPA MUSS mandatory=true sein | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-005** | Singapore data_breach_notification MUSS true sein | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-006** | Singapore consent_purposes_documented MUSS true sein | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-007** | Japan JFSA APPI MUSS mandatory=true sein | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-008** | Japan cross_border_transfer_rules MUSS true sein | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-009** | Australia Privacy Act 1988 MUSS mandatory=true sein | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-010** | Australia APP11 security MUSS true sein | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-011** | OPA MUSS has_substr() verwenden (nicht contains()) | §Konsolidierte Ergänzungen | MEDIUM | MUSS |
| **MD-EXT-012** | OPA MUSS string_similarity() für Fuzzy-Matching verwenden | §Konsolidierte Ergänzungen | MEDIUM | MUSS |
| **MD-EXT-013** | CI Workflows MÜSSEN schedule: '15 3 * * *' für daily sanctions haben | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-014** | CI Workflows MÜSSEN schedule: '0 0 1 */3 *' für quarterly audit haben | §Konsolidierte Ergänzungen | MEDIUM | MUSS |
| **MD-EXT-015** | CI MUSS actions/upload-artifact@v4 verwenden | §Konsolidierte Ergänzungen | LOW | MUSS |
| **MD-EXT-016** | Build-Step MUSS entities_to_check.json vor OPA erstellen | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-017** | Sanctions sources.yaml MUSS max_age_hours: 24 definieren | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-018** | Sanctions sources.yaml MUSS sha256 Hash enthalten | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-019** | Jeder Root MUSS docs/incident_response_plan.md haben | §Konsolidierte Ergänzungen | HIGH | MUSS |
| **MD-EXT-020** | NIEMALS .ipynb Dateien committen | §Konsolidierte Ergänzungen | CRITICAL | NIEMALS |
| **MD-EXT-021** | NIEMALS .parquet Dateien committen | §Konsolidierte Ergänzungen | CRITICAL | NIEMALS |
| **MD-EXT-022** | NIEMALS .sqlite Dateien committen | §Konsolidierte Ergänzungen | CRITICAL | NIEMALS |
| **MD-EXT-023** | NIEMALS .db Dateien committen | §Konsolidierte Ergänzungen | CRITICAL | NIEMALS |
| **MD-EXT-024** | OPA MUSS 24_meta_orchestration/registry/generated/repo_scan.json verwenden | §Konsolidierte Ergänzungen | HIGH | MUSS |

---

## 📊 ZUSAMMENFASSUNG

| Kategorie | Anzahl Regeln | Kritische Regeln | Hohe Regeln | Mittlere Regeln | Niedrige Regeln |
|-----------|---------------|------------------|-------------|-----------------|-----------------|
| STRUKTUR | 10 | 10 | 0 | 0 | 0 |
| CHART.YAML | 50 | 8 | 30 | 10 | 2 |
| MANIFEST.YAML | 50 | 3 | 25 | 20 | 2 |
| POLICIES | 32 | 28 | 4 | 0 | 0 |
| GOVERNANCE | 12 | 0 | 10 | 2 | 0 |
| PRINZIPIEN | 23 | 7 | 13 | 3 | 0 |
| EXTENSIONS v1.1.1 | 24 | 4 | 12 | 7 | 1 |
| **GESAMT** | **201** | **60** | **94** | **42** | **5** |

---

## 🎯 KRITISCHER BEFUND

### Vorheriger Bericht vs. Master-Definition

**Vorheriger "Vollständigkeitsbericht" behauptete:**
- 327 Regeln integriert
- 280 ursprüngliche + 47 neue Regeln (CS, MS, KP, CE, TS, DC, MR)

**Tatsächlich aus Master-Definition extrahiert:**
- **201 NEUE granulare Regeln** (MD-* Prefix)
- Diese 201 Regeln sind ZUSÄTZLICH zu den bisherigen 327 Regeln!

**Fehlende Integration:**
- 201 Master-Definition-Regeln wurden **NICHT** in die 5 SoT-Artefakte integriert
- Nur die 47 Regeln aus `ssid_master_rules.txt` wurden integriert
- Die granularen Strukturregeln, Chart/Manifest-Detailregeln, Policy-Details wurden **AUSGELASSEN**

---

## ⚠️ HANDLUNGSBEDARF

1. **Coverage-Check durchführen:** Prüfen, welche der 201 MD-* Regeln bereits implizit in den 5 Artefakten vorhanden sind
2. **Lücken identifizieren:** Welche der 201 Regeln fehlen komplett?
3. **Integration:** ALLE fehlenden Regeln in ALLE 5 SoT-Artefakte integrieren:
   - sot_validator_core.py
   - sot_policy.rego
   - sot_contract.yaml
   - sot_validator.py (CLI)
   - test_sot_validator.py

4. **Verifizierung:** 100% Coverage gegen Master-Definition v1.1.1 erreichen

---

**Status:** INCOMPLETE - Major Coverage-Lücken identifiziert
**Nächster Schritt:** Coverage-Check gegen 5 SoT-Artefakte
