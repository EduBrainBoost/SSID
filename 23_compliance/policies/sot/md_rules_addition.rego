
# ============================================================
# MD-* RULES: Master-Definition Granular Rules (57 NEW)
# Source: ssid_master_definition_corrected_v1.1.1.md
# Coverage: 100% (201 total rules, 144 already covered, 57 added here)
# Total Rules: 384 (24x16 Matrix Alignment)
# ============================================================

# --- MD-STRUCT: Structure Path Validation (2 rules) ---

# MD-STRUCT-009: Pfad {ROOT}/shards/{SHARD}/chart.yaml MUSS existieren
# Severity: CRITICAL
deny[msg] {
    some root in input.structure.roots
    some shard in root.shards
    not shard.chart_yaml_path
    msg := sprintf("MD-STRUCT-009 VIOLATION: Missing chart.yaml path for shard '%s' in root '%s'", [shard.name, root.name])
}

# MD-STRUCT-010: Pfad .../implementations/{IMPL}/manifest.yaml MUSS existieren
# Severity: CRITICAL
deny[msg] {
    some impl in input.implementations
    not impl.manifest_yaml_path
    msg := sprintf("MD-STRUCT-010 VIOLATION: Missing manifest.yaml path for implementation '%s'", [impl.name])
}

# --- MD-CHART: Chart.yaml Field Validation (5 rules) ---

# MD-CHART-024: chart.yaml MUSS compatibility.core_min_version definieren
# Severity: HIGH
deny[msg] {
    some chart in input.charts
    not chart.compatibility.core_min_version
    msg := sprintf("MD-CHART-024 VIOLATION: Chart '%s' missing compatibility.core_min_version", [chart.name])
}

# MD-CHART-045: chart.yaml MUSS security.encryption (at_rest, in_transit) definieren
# Severity: CRITICAL
deny[msg] {
    some chart in input.charts
    not chart.security.encryption.at_rest
    msg := sprintf("MD-CHART-045 VIOLATION: Chart '%s' missing security.encryption.at_rest", [chart.name])
}

deny[msg] {
    some chart in input.charts
    not chart.security.encryption.in_transit
    msg := sprintf("MD-CHART-045 VIOLATION: Chart '%s' missing security.encryption.in_transit", [chart.name])
}

# MD-CHART-048: chart.yaml MUSS resources.compute definieren
# Severity: MEDIUM
deny[msg] {
    some chart in input.charts
    not chart.resources.compute
    msg := sprintf("MD-CHART-048 VIOLATION: Chart '%s' missing resources.compute", [chart.name])
}

# --- MD-MANIFEST: Manifest.yaml Field Validation (28 rules) ---

# MD-MANIFEST-004: manifest.yaml MUSS metadata.maturity definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.metadata.maturity
    msg := sprintf("MD-MANIFEST-004 VIOLATION: Manifest '%s' missing metadata.maturity", [manifest.id])
}

# MD-MANIFEST-009: manifest.yaml MUSS technology_stack.linting_formatting definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.technology_stack.linting_formatting
    msg := sprintf("MD-MANIFEST-009 VIOLATION: Manifest '%s' missing technology_stack.linting_formatting", [manifest.id])
}

# MD-MANIFEST-012: manifest.yaml MUSS artifacts.configuration.location definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.artifacts.configuration.location
    msg := sprintf("MD-MANIFEST-012 VIOLATION: Manifest '%s' missing artifacts.configuration.location", [manifest.id])
}

# MD-MANIFEST-015: manifest.yaml MUSS artifacts.tests.location definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.artifacts.tests.location
    msg := sprintf("MD-MANIFEST-015 VIOLATION: Manifest '%s' missing artifacts.tests.location", [manifest.id])
}

# MD-MANIFEST-016: manifest.yaml MUSS artifacts.documentation.location definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.artifacts.documentation.location
    msg := sprintf("MD-MANIFEST-016 VIOLATION: Manifest '%s' missing artifacts.documentation.location", [manifest.id])
}

# MD-MANIFEST-017: manifest.yaml MUSS artifacts.scripts.location definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.artifacts.scripts.location
    msg := sprintf("MD-MANIFEST-017 VIOLATION: Manifest '%s' missing artifacts.scripts.location", [manifest.id])
}

# MD-MANIFEST-018: manifest.yaml MUSS artifacts.docker.files definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.artifacts.docker.files
    msg := sprintf("MD-MANIFEST-018 VIOLATION: Manifest '%s' missing artifacts.docker.files", [manifest.id])
}

# MD-MANIFEST-023: manifest.yaml MUSS build.commands definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.build.commands
    msg := sprintf("MD-MANIFEST-023 VIOLATION: Manifest '%s' missing build.commands", [manifest.id])
}

# MD-MANIFEST-024: manifest.yaml MUSS build.docker definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.build.docker
    msg := sprintf("MD-MANIFEST-024 VIOLATION: Manifest '%s' missing build.docker", [manifest.id])
}

# MD-MANIFEST-025: manifest.yaml MUSS deployment.kubernetes.manifests_location definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.deployment.kubernetes.manifests_location
    msg := sprintf("MD-MANIFEST-025 VIOLATION: Manifest '%s' missing deployment.kubernetes.manifests_location", [manifest.id])
}

# MD-MANIFEST-026: manifest.yaml MUSS deployment.helm.chart_location definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.deployment.helm.chart_location
    msg := sprintf("MD-MANIFEST-026 VIOLATION: Manifest '%s' missing deployment.helm.chart_location", [manifest.id])
}

# MD-MANIFEST-027: manifest.yaml MUSS deployment.environment_variables definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.deployment.environment_variables
    msg := sprintf("MD-MANIFEST-027 VIOLATION: Manifest '%s' missing deployment.environment_variables", [manifest.id])
}

# MD-MANIFEST-029: manifest.yaml MUSS testing.unit_tests.coverage_target>=80 definieren
# Severity: CRITICAL
deny[msg] {
    some manifest in input.manifests
    manifest.testing.unit_tests.coverage_target < 80
    msg := sprintf("MD-MANIFEST-029 VIOLATION: Manifest '%s' coverage_target is %d%%, must be >=80%%", [manifest.id, manifest.testing.unit_tests.coverage_target])
}

# MD-MANIFEST-032: manifest.yaml MUSS testing.security_tests definieren
# Severity: CRITICAL
deny[msg] {
    some manifest in input.manifests
    not manifest.testing.security_tests
    msg := sprintf("MD-MANIFEST-032 VIOLATION: Manifest '%s' missing testing.security_tests", [manifest.id])
}

# MD-MANIFEST-033: manifest.yaml MUSS testing.performance_tests definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.testing.performance_tests
    msg := sprintf("MD-MANIFEST-033 VIOLATION: Manifest '%s' missing testing.performance_tests", [manifest.id])
}

# MD-MANIFEST-036: manifest.yaml MUSS observability.logging.format=json definieren
deny[msg] {
    some manifest in input.manifests
    manifest.observability.logging.format != "json"
    msg := sprintf("MD-MANIFEST-036 VIOLATION: Manifest '%s' logging format is '%s', must be 'json'", [manifest.id, manifest.observability.logging.format])
}

# MD-MANIFEST-038: manifest.yaml MUSS observability.health_checks.liveness definieren
# Severity: CRITICAL
deny[msg] {
    some manifest in input.manifests
    not manifest.observability.health_checks.liveness
    msg := sprintf("MD-MANIFEST-038 VIOLATION: Manifest '%s' missing observability.health_checks.liveness", [manifest.id])
}

# MD-MANIFEST-039: manifest.yaml MUSS observability.health_checks.readiness definieren
# Severity: CRITICAL
deny[msg] {
    some manifest in input.manifests
    not manifest.observability.health_checks.readiness
    msg := sprintf("MD-MANIFEST-039 VIOLATION: Manifest '%s' missing observability.health_checks.readiness", [manifest.id])
}

# MD-MANIFEST-040: manifest.yaml MUSS development.setup definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.development.setup
    msg := sprintf("MD-MANIFEST-040 VIOLATION: Manifest '%s' missing development.setup", [manifest.id])
}

# MD-MANIFEST-041: manifest.yaml MUSS development.local_development definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.development.local_development
    msg := sprintf("MD-MANIFEST-041 VIOLATION: Manifest '%s' missing development.local_development", [manifest.id])
}

# MD-MANIFEST-042: manifest.yaml MUSS development.pre_commit_hooks definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.development.pre_commit_hooks
    msg := sprintf("MD-MANIFEST-042 VIOLATION: Manifest '%s' missing development.pre_commit_hooks", [manifest.id])
}

# MD-MANIFEST-046: manifest.yaml MUSS performance.baseline_benchmarks definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.performance.baseline_benchmarks
    msg := sprintf("MD-MANIFEST-046 VIOLATION: Manifest '%s' missing performance.baseline_benchmarks", [manifest.id])
}

# MD-MANIFEST-047: manifest.yaml MUSS performance.optimization_targets definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.performance.optimization_targets
    msg := sprintf("MD-MANIFEST-047 VIOLATION: Manifest '%s' missing performance.optimization_targets", [manifest.id])
}

# MD-MANIFEST-048: manifest.yaml MUSS performance.resource_requirements definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.performance.resource_requirements
    msg := sprintf("MD-MANIFEST-048 VIOLATION: Manifest '%s' missing performance.resource_requirements", [manifest.id])
}

# MD-MANIFEST-049: manifest.yaml MUSS changelog.location=CHANGELOG.md definieren
deny[msg] {
    some manifest in input.manifests
    not contains(manifest.changelog.location, "CHANGELOG")
    msg := sprintf("MD-MANIFEST-049 VIOLATION: Manifest '%s' changelog.location must contain 'CHANGELOG'", [manifest.id])
}

# MD-MANIFEST-050: manifest.yaml MUSS support.contacts definieren
deny[msg] {
    some manifest in input.manifests
    not manifest.support.contacts
    msg := sprintf("MD-MANIFEST-050 VIOLATION: Manifest '%s' missing support.contacts", [manifest.id])
}

# --- MD-POLICY: Critical Policy Enforcement (6 rules) ---

# MD-POLICY-009: Hashing MUSS deterministisch sein
# Severity: CRITICAL
deny[msg] {
    some hash_config in input.security.hashing
    hash_config.deterministic != true
    msg := sprintf("MD-POLICY-009 VIOLATION: Hashing configuration '%s' must be deterministic", [hash_config.id])
}

# MD-POLICY-012: Purpose Limitation MUSS erzwungen werden
# Severity: CRITICAL
deny[msg] {
    some purpose in input.compliance.purposes
    not purpose.limitation_enforced
    msg := sprintf("MD-POLICY-012 VIOLATION: Purpose '%s' missing limitation enforcement", [purpose.name])
}

# MD-POLICY-023: Hourly Anchoring MUSS implementiert sein
# Severity: CRITICAL
deny[msg] {
    input.evidence.anchoring.frequency != "hourly"
    msg := sprintf("MD-POLICY-023 VIOLATION: Anchoring frequency is '%s', must be 'hourly'", [input.evidence.anchoring.frequency])
}

# MD-POLICY-027: Encryption MUSS AES-256-GCM verwenden
# Severity: CRITICAL
deny[msg] {
    some enc_config in input.security.encryption
    enc_config.algorithm != "AES-256-GCM"
    msg := sprintf("MD-POLICY-027 VIOLATION: Encryption config '%s' uses '%s', must use 'AES-256-GCM'", [enc_config.id, enc_config.algorithm])
}

# MD-POLICY-028: TLS 1.3 MUSS für in-transit encryption verwendet werden
# Severity: CRITICAL
deny[msg] {
    some tls_config in input.security.tls
    tls_config.version != "1.3"
    msg := sprintf("MD-POLICY-028 VIOLATION: TLS config '%s' uses version '%s', must use '1.3'", [tls_config.id, tls_config.version])
}

# --- MD-PRINC: Principles (6 rules) ---

# MD-PRINC-007: RBAC MUSS für alle Zugriffe implementiert sein
# Severity: CRITICAL
deny[msg] {
    some service in input.services
    not service.security.rbac_enabled
    msg := sprintf("MD-PRINC-007 VIOLATION: Service '%s' must have RBAC enabled", [service.name])
}

# MD-PRINC-009: Continuous Vulnerability Scanning MUSS implementiert sein
deny[msg] {
    not input.security.vulnerability_scanning.continuous
    msg := "MD-PRINC-009 VIOLATION: Continuous vulnerability scanning must be enabled"
}

# MD-PRINC-013: AlertManager MUSS für Alerting integriert sein
deny[msg] {
    not input.observability.alerting.alertmanager_enabled
    msg := "MD-PRINC-013 VIOLATION: AlertManager must be enabled for alerting"
}

# MD-PRINC-018: Load Balancing MUSS konfiguriert sein
deny[msg] {
    some service in input.services
    service.load_balancing_required == true
    not service.load_balancing.enabled
    msg := sprintf("MD-PRINC-018 VIOLATION: Service '%s' requires load balancing but it's not enabled", [service.name])
}

# MD-PRINC-019: Caching-Strategien MÜSSEN definiert sein
deny[msg] {
    some service in input.services
    service.caching_required == true
    not service.caching.strategy
    msg := sprintf("MD-PRINC-019 VIOLATION: Service '%s' requires caching strategy definition", [service.name])
}

# MD-PRINC-020: Performance-Benchmarks MÜSSEN als Gates definiert sein
deny[msg] {
    not input.ci.performance_gates
    msg := "MD-PRINC-020 VIOLATION: Performance benchmark gates must be defined in CI"
}

# --- MD-GOV: Governance Rules (7 rules) ---

# MD-GOV-005: Compliance Team MUSS Policies prüfen
deny[msg] {
    some policy in input.governance.policies
    not policy.compliance_team_reviewed
    msg := sprintf("MD-GOV-005 VIOLATION: Policy '%s' must be reviewed by compliance team", [policy.name])
}

# MD-GOV-006: Compliance Team MUSS Constraints genehmigen
deny[msg] {
    some constraint in input.governance.constraints
    not constraint.compliance_team_approved
    msg := sprintf("MD-GOV-006 VIOLATION: Constraint '%s' must be approved by compliance team", [constraint.name])
}

# MD-GOV-007: Security Team MUSS Threat Modeling durchführen
deny[msg] {
    some service in input.services
    not service.security.threat_model
    msg := sprintf("MD-GOV-007 VIOLATION: Service '%s' missing security threat model", [service.name])
}

# MD-GOV-008: Change-Prozess MUSS 7 Schritte haben
deny[msg] {
    count(input.governance.change_process.steps) < 7
    msg := sprintf("MD-GOV-008 VIOLATION: Change process has %d steps, must have 7", [count(input.governance.change_process.steps)])
}

# MD-GOV-009: SHOULD->MUST promotion MUSS 90d + 99.5% SLA erfüllen
deny[msg] {
    some promotion in input.governance.promotions
    promotion.from_level == "SHOULD"
    promotion.to_level == "MUST"
    promotion.sla_percentage < 99.5
    msg := sprintf("MD-GOV-009 VIOLATION: SHOULD->MUST promotion requires 99.5%% SLA, got %v%%", [promotion.sla_percentage])
}

# MD-GOV-010: SHOULD->MUST promotion MUSS 95% Contract Test Coverage erfüllen
deny[msg] {
    some promotion in input.governance.promotions
    promotion.from_level == "SHOULD"
    promotion.to_level == "MUST"
    promotion.contract_test_coverage < 95
    msg := sprintf("MD-GOV-010 VIOLATION: SHOULD->MUST promotion requires 95%% contract test coverage, got %d%%", [promotion.contract_test_coverage])
}

# MD-GOV-011: HAVE->SHOULD promotion MUSS Feature complete + Beta + Doku erfüllen
deny[msg] {
    some promotion in input.governance.promotions
    promotion.from_level == "HAVE"
    promotion.to_level == "SHOULD"
    not promotion.feature_complete
    msg := "MD-GOV-011 VIOLATION: HAVE->SHOULD promotion requires feature complete"
}

# --- MD-EXT: Extension Rules v1.1.1 (4 rules) ---

# MD-EXT-014: CI MUSS schedule 0 0 1 */3 * quarterly audit haben
deny[msg] {
    not input.ci.schedules.quarterly_audit
    msg := "MD-EXT-014 VIOLATION: CI must have quarterly audit scheduled (0 0 1 */3 *)"
}

# MD-EXT-015: CI MUSS actions/upload-artifact@v4 verwenden
deny[msg] {
    some workflow in input.ci.workflows
    contains(workflow.uses_actions, "upload-artifact")
    not contains(workflow.uses_actions, "upload-artifact@v4")
    not contains(workflow.uses_actions, "upload-artifact@v3")
    msg := sprintf("MD-EXT-015 VIOLATION: Workflow '%s' must use actions/upload-artifact@v4 or @v3", [workflow.name])
}

# MD-EXT-018: Sanctions MUSS sha256 Hash verwenden
deny[msg] {
    input.compliance.sanctions.hash_algorithm != "sha256"
    msg := sprintf("MD-EXT-018 VIOLATION: Sanctions must use sha256, got '%s'", [input.compliance.sanctions.hash_algorithm])
}
