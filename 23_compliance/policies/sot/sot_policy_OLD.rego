# ============================================================
# SSID SoT Policy Enforcement - Complete Rule Set
# ============================================================
# Total Rules: 280 semantic rules
# Source: UNIFIED_RULE_REGISTRY.md
# Generated: 2025-10-20
# Status: Manual Implementation
# ============================================================

package ssid.sot

import future.keywords.if
import future.keywords.in

# ============================================================
# CONSTANTS
# ============================================================

# Architecture constants
required_root_count := 24
required_shard_count := 16
total_charts := 384

# Blacklist jurisdictions
blacklist_jurisdictions := {
    "IR": {"name": "Iran", "reason": "OFAC Comprehensive Sanctions"},
    "KP": {"name": "North Korea", "reason": "OFAC Comprehensive Sanctions"},
    "SY": {"name": "Syria", "reason": "OFAC Comprehensive Sanctions"},
    "CU": {"name": "Cuba", "reason": "OFAC Sanctions (Limited)"},
    "SD": {"name": "Sudan", "reason": "OFAC Sanctions (Regional)"},
    "BY": {"name": "Belarus", "reason": "EU Sanctions"},
    "VE": {"name": "Venezuela", "reason": "OFAC Sectoral Sanctions"}
}

# Tier 1 markets
tier1_markets := ["US", "EU", "UK", "CN", "JP", "CA", "AU"]

# Supported blockchain networks
supported_networks := ["ethereum", "polygon", "arbitrum", "optimism", "base", "avalanche"]

# Supported authentication methods
auth_methods := ["did:ethr", "did:key", "did:web", "biometric_eidas", "smart_card_eidas", "mobile_eidas"]

# PII categories
pii_categories := ["name", "email", "phone", "address", "national_id", "passport", "drivers_license", "ssn_tax_id", "biometric_data", "health_records"]

# Hash algorithms
hash_algorithms := ["SHA3-256", "BLAKE3", "SHA-256", "SHA-512"]

# DID methods
did_methods := ["did:ethr", "did:key", "did:web", "did:ion"]

# ============================================================
# TIER 1: ARCHITECTURE RULES (AR001-AR010) - CRITICAL
# ============================================================

# AR001: Das System MUSS aus exakt 24 Root-Ordnern bestehen
deny[msg] {
    count(input.structure.roots) != required_root_count
    msg := sprintf("AR001 VIOLATION: Root folder count is %d, expected %d", [count(input.structure.roots), required_root_count])
}

# AR002: Jeder Root-Ordner MUSS exakt 16 Shards enthalten
deny[msg] {
    some root in input.structure.roots
    count(root.shards) != required_shard_count
    msg := sprintf("AR002 VIOLATION: Root '%s' has %d shards, expected %d", [root.name, count(root.shards), required_shard_count])
}

# AR003: Das System MUSS eine Matrix von 24×16=384 Shard-Ordnern bilden
deny[msg] {
    total := sum([count(root.shards) | root := input.structure.roots[_]])
    total != total_charts
    msg := sprintf("AR003 VIOLATION: Total charts is %d, expected %d (24×16)", [total, total_charts])
}

# AR004: Jeder Shard MUSS ein Chart.yaml mit Chart-Definition enthalten
deny[msg] {
    some root in input.structure.roots
    some shard in root.shards
    not shard.has_chart_yaml
    msg := sprintf("AR004 VIOLATION: Shard %s/%s missing Chart.yaml", [root.name, shard.name])
}

# AR005: Jeder Shard MUSS ein values.yaml mit Werte-Definitionen enthalten
deny[msg] {
    some root in input.structure.roots
    some shard in root.shards
    not shard.has_values_yaml
    msg := sprintf("AR005 VIOLATION: Shard %s/%s missing values.yaml", [root.name, shard.name])
}

# AR006: Jeder Root-Ordner MUSS eine README.md enthalten
deny[msg] {
    some root in input.structure.roots
    not root.has_readme
    msg := sprintf("AR006 VIOLATION: Root '%s' missing README.md", [root.name])
}

# AR007: Die 16 Shards MÜSSEN identisch über alle Root-Ordner repliziert werden
deny[msg] {
    some i, j
    root_i := input.structure.roots[i]
    root_j := input.structure.roots[j]
    i != j
    shard_names_i := {shard.name | shard := root_i.shards[_]}
    shard_names_j := {shard.name | shard := root_j.shards[_]}
    shard_names_i != shard_names_j
    msg := sprintf("AR007 VIOLATION: Shard mismatch between roots '%s' and '%s'", [root_i.name, root_j.name])
}

# AR008: Shard-Namen MÜSSEN dem Pattern NN_name folgen (NN = 01-16)
deny[msg] {
    some root in input.structure.roots
    some shard in root.shards
    not regex.match(`^\d{2}_[a-z_]+$`, shard.name)
    msg := sprintf("AR008 VIOLATION: Shard '%s' does not match pattern NN_name", [shard.name])
}

# AR009: Root-Namen MÜSSEN dem Pattern NN_name folgen (NN = 01-24)
deny[msg] {
    some root in input.structure.roots
    not regex.match(`^\d{2}_[a-z_]+$`, root.name)
    msg := sprintf("AR009 VIOLATION: Root '%s' does not match pattern NN_name", [root.name])
}

# AR010: Jeder Shard MUSS ein templates/ Verzeichnis enthalten
deny[msg] {
    some root in input.structure.roots
    some shard in root.shards
    not shard.has_templates_dir
    msg := sprintf("AR010 VIOLATION: Shard %s/%s missing templates/ directory", [root.name, shard.name])
}

# ============================================================
# TIER 1: CRITICAL POLICIES (CP001-CP012) - CRITICAL
# ============================================================

# CP001: NIEMALS Rohdaten von PII oder biometrischen Daten speichern
deny[msg] {
    some entity in input.data_storage.entities
    entity.stores_raw_pii == true
    msg := sprintf("CP001 VIOLATION: Entity '%s' stores raw PII data", [entity.name])
}

# CP002: Alle Daten MÜSSEN als SHA3-256 Hashes gespeichert werden
deny[msg] {
    some config in input.security.hash_configs
    config.algorithm != "SHA3-256"
    config.is_primary == true
    msg := sprintf("CP002 VIOLATION: Primary hash algorithm is '%s', must be SHA3-256", [config.algorithm])
}

# CP003: Tenant-spezifische Peppers MÜSSEN verwendet werden
deny[msg] {
    not input.security.pepper_config.enabled
    msg := "CP003 VIOLATION: Tenant-specific peppers not enabled"
}

deny[msg] {
    input.security.pepper_config.enabled
    not input.security.pepper_config.per_tenant
    msg := "CP003 VIOLATION: Pepper config enabled but not per-tenant"
}

# CP004: Raw Data Retention MUSS '0 seconds' sein
deny[msg] {
    some policy in input.data_retention.policies
    policy.data_type == "raw_pii"
    policy.retention_period != "0 seconds"
    msg := sprintf("CP004 VIOLATION: Raw PII retention is '%s', must be '0 seconds'", [policy.retention_period])
}

# CP005: Right to Erasure via Hash-Rotation (GDPR Art. 17)
deny[msg] {
    not input.gdpr.erasure_endpoint_exists
    msg := "CP005 VIOLATION: GDPR Right to Erasure endpoint missing"
}

deny[msg] {
    input.gdpr.erasure_endpoint_exists
    input.gdpr.erasure_method != "pepper_rotation"
    msg := sprintf("CP005 VIOLATION: Erasure method is '%s', must be 'pepper_rotation'", [input.gdpr.erasure_method])
}

# CP006: Data Portability MUSS JSON-Export bieten (GDPR Art. 20)
deny[msg] {
    not input.gdpr.portability_endpoint_exists
    msg := "CP006 VIOLATION: GDPR Data Portability endpoint missing"
}

deny[msg] {
    input.gdpr.portability_endpoint_exists
    not "application/json" in input.gdpr.portability_formats
    msg := "CP006 VIOLATION: JSON export format not supported for data portability"
}

# CP007: PII Redaction MUSS automatisch in Logs erfolgen
deny[msg] {
    not input.logging.pii_redaction_enabled
    msg := "CP007 VIOLATION: Automatic PII redaction in logs not enabled"
}

# CP008: Alle AI/ML-Modelle MÜSSEN auf Bias getestet werden
deny[msg] {
    some model in input.ai_models
    not model.bias_tested
    msg := sprintf("CP008 VIOLATION: AI model '%s' not tested for bias", [model.name])
}

# CP009: Hash-Ledger mit Blockchain-Anchoring
deny[msg] {
    not input.audit.blockchain_anchoring_enabled
    msg := "CP009 VIOLATION: Blockchain anchoring not enabled for hash ledger"
}

# CP010: WORM-Storage mit 10 Jahren Retention
deny[msg] {
    not input.audit.worm_storage_enabled
    msg := "CP010 VIOLATION: WORM storage not enabled"
}

deny[msg] {
    input.audit.worm_storage_enabled
    input.audit.worm_retention_years < 10
    msg := sprintf("CP010 VIOLATION: WORM retention is %d years, must be at least 10", [input.audit.worm_retention_years])
}

# CP011: NIEMALS Secrets in Git committen
deny[msg] {
    some commit in input.git.recent_commits
    commit.contains_secrets == true
    msg := sprintf("CP011 VIOLATION: Commit '%s' contains secrets", [commit.sha])
}

# CP012: Secrets MÜSSEN alle 90 Tage rotiert werden
deny[msg] {
    some secret in input.secrets
    secret.age_days > 90
    msg := sprintf("CP012 VIOLATION: Secret '%s' is %d days old, must be rotated every 90 days", [secret.name, secret.age_days])
}

# ============================================================
# TIER 1: JURISDICTION BLACKLIST (JURIS_BL_001-007) - CRITICAL
# ============================================================

# JURIS_BL_001: Block Iran (IR) - OFAC Comprehensive Sanctions
deny[msg] {
    input.transaction.country_code == "IR"
    msg := "JURIS_BL_001 VIOLATION: Transaction from Iran (IR) blocked - OFAC Comprehensive Sanctions"
}

# JURIS_BL_002: Block North Korea (KP) - OFAC Comprehensive Sanctions
deny[msg] {
    input.transaction.country_code == "KP"
    msg := "JURIS_BL_002 VIOLATION: Transaction from North Korea (KP) blocked - OFAC Comprehensive Sanctions"
}

# JURIS_BL_003: Block Syria (SY) - OFAC Comprehensive Sanctions
deny[msg] {
    input.transaction.country_code == "SY"
    msg := "JURIS_BL_003 VIOLATION: Transaction from Syria (SY) blocked - OFAC Comprehensive Sanctions"
}

# JURIS_BL_004: Block Cuba (CU) - OFAC Sanctions (Limited)
deny[msg] {
    input.transaction.country_code == "CU"
    msg := "JURIS_BL_004 VIOLATION: Transaction from Cuba (CU) blocked - OFAC Sanctions (Limited)"
}

# JURIS_BL_005: Block Sudan (SD) - OFAC Sanctions (Regional)
deny[msg] {
    input.transaction.country_code == "SD"
    msg := "JURIS_BL_005 VIOLATION: Transaction from Sudan (SD) blocked - OFAC Sanctions (Regional)"
}

# JURIS_BL_006: Block Belarus (BY) - EU Sanctions
deny[msg] {
    input.transaction.country_code == "BY"
    msg := "JURIS_BL_006 VIOLATION: Transaction from Belarus (BY) blocked - EU Sanctions"
}

# JURIS_BL_007: Block Venezuela (VE) - OFAC Sectoral Sanctions
deny[msg] {
    input.transaction.country_code == "VE"
    msg := "JURIS_BL_007 VIOLATION: Transaction from Venezuela (VE) blocked - OFAC Sectoral Sanctions"
}

# ============================================================
# TIER 1: STRUCTURE EXCEPTIONS (SOT-V2-0091-0094) - CRITICAL
# ============================================================

# SOT-V2-0091: grundprinzipien.ausnahmen.allowed_root_files
deny[msg] {
    some file in input.structure.root_level_files
    not file.name in input.config.allowed_root_files
    msg := sprintf("SOT-V2-0091 VIOLATION: Root-level file '%s' not in allowed_root_files", [file.name])
}

# SOT-V2-0092: grundprinzipien.critical.structure_exceptions_yaml
deny[msg] {
    not input.config.structure_exceptions_yaml_exists
    msg := "SOT-V2-0092 VIOLATION: structure_exceptions.yaml not found"
}

# SOT-V2-0093: grundprinzipien.root_level_ausnahmen
deny[msg] {
    some exception in input.config.root_level_ausnahmen
    not exception.documented
    msg := sprintf("SOT-V2-0093 VIOLATION: Root-level exception '%s' not documented", [exception.path])
}

# SOT-V2-0094: grundprinzipien.verbindliche_root_module
deny[msg] {
    some module_name in input.config.verbindliche_root_module
    not module_name in {root.name | root := input.structure.roots[_]}
    msg := sprintf("SOT-V2-0094 VIOLATION: Mandatory root module '%s' missing", [module_name])
}

# ============================================================
# TIER 2: VERSIONING & GOVERNANCE (VG001-VG008) - HIGH
# ============================================================

# VG001: Semantic Versioning (MAJOR.MINOR.PATCH)
deny[msg] {
    some chart in input.charts
    not regex.match(`^\d+\.\d+\.\d+$`, chart.version)
    msg := sprintf("VG001 VIOLATION: Chart '%s' version '%s' does not follow semver", [chart.name, chart.version])
}

# VG002: Breaking Changes mit Migration Guide
deny[msg] {
    some release in input.releases
    release.has_breaking_changes == true
    not release.has_migration_guide
    msg := sprintf("VG002 VIOLATION: Release '%s' has breaking changes but no migration guide", [release.version])
}

# VG003: Deprecations mit 180 Tage Notice
deny[msg] {
    some deprecation in input.deprecations
    deprecation.notice_days < 180
    msg := sprintf("VG003 VIOLATION: Deprecation '%s' has only %d days notice, requires 180", [deprecation.feature, deprecation.notice_days])
}

# VG004: RFC Process für MUST-Capability-Änderungen
deny[msg] {
    some change in input.changes
    change.type == "must_capability"
    not change.has_rfc
    msg := sprintf("VG004 VIOLATION: MUST-capability change '%s' missing RFC", [change.name])
}

# VG005: Jeder Shard MUSS einen Owner haben
deny[msg] {
    some root in input.structure.roots
    some shard in root.shards
    not shard.owner
    msg := sprintf("VG005 VIOLATION: Shard %s/%s has no owner defined", [root.name, shard.name])
}

# VG006: Architecture Board Review für chart.yaml-Änderungen
deny[msg] {
    some pr in input.pull_requests
    pr.modifies_chart_yaml == true
    not pr.has_architecture_board_review
    msg := sprintf("VG006 VIOLATION: PR #%d modifies Chart.yaml without Architecture Board review", [pr.number])
}

# VG007: Architecture Board Approval-Pflicht
deny[msg] {
    some pr in input.pull_requests
    pr.requires_arch_board_approval == true
    not pr.arch_board_approved
    msg := sprintf("VG007 VIOLATION: PR #%d requires but lacks Architecture Board approval", [pr.number])
}

# VG008: Governance Roles Definition
deny[msg] {
    not input.governance.roles_defined
    msg := "VG008 VIOLATION: Governance roles not defined"
}

# ============================================================
# TIER 2: PROPOSAL TYPES (PROP_TYPE_001-007) - HIGH
# ============================================================

# PROP_TYPE_001: parameter_change (Quorum 10%, Threshold 66%)
deny[msg] {
    some proposal in input.proposals
    proposal.type == "parameter_change"
    proposal.quorum_percentage < 10
    msg := sprintf("PROP_TYPE_001 VIOLATION: Proposal #%d quorum is %d%%, requires 10%%", [proposal.id, proposal.quorum_percentage])
}

deny[msg] {
    some proposal in input.proposals
    proposal.type == "parameter_change"
    proposal.threshold_percentage < 66
    msg := sprintf("PROP_TYPE_001 VIOLATION: Proposal #%d threshold is %d%%, requires 66%%", [proposal.id, proposal.threshold_percentage])
}

# PROP_TYPE_002: treasury_allocation (Quorum 15%, Threshold 75%)
deny[msg] {
    some proposal in input.proposals
    proposal.type == "treasury_allocation"
    proposal.quorum_percentage < 15
    msg := sprintf("PROP_TYPE_002 VIOLATION: Proposal #%d quorum is %d%%, requires 15%%", [proposal.id, proposal.quorum_percentage])
}

deny[msg] {
    some proposal in input.proposals
    proposal.type == "treasury_allocation"
    proposal.threshold_percentage < 75
    msg := sprintf("PROP_TYPE_002 VIOLATION: Proposal #%d threshold is %d%%, requires 75%%", [proposal.id, proposal.threshold_percentage])
}

# PROP_TYPE_003: protocol_upgrade (Supermajority erforderlich)
deny[msg] {
    some proposal in input.proposals
    proposal.type == "protocol_upgrade"
    not proposal.requires_supermajority
    msg := sprintf("PROP_TYPE_003 VIOLATION: Proposal #%d (protocol_upgrade) must require supermajority", [proposal.id])
}

# PROP_TYPE_004: emergency (Expedited process)
deny[msg] {
    some proposal in input.proposals
    proposal.type == "emergency"
    not proposal.expedited_process
    msg := sprintf("PROP_TYPE_004 VIOLATION: Proposal #%d (emergency) must have expedited process", [proposal.id])
}

# PROP_TYPE_005: code_upgrade
deny[msg] {
    some proposal in input.proposals
    proposal.type == "code_upgrade"
    not proposal.has_code_review
    msg := sprintf("PROP_TYPE_005 VIOLATION: Proposal #%d (code_upgrade) missing code review", [proposal.id])
}

# PROP_TYPE_006: governance_change
deny[msg] {
    some proposal in input.proposals
    proposal.type == "governance_change"
    not proposal.has_governance_impact_analysis
    msg := sprintf("PROP_TYPE_006 VIOLATION: Proposal #%d (governance_change) missing impact analysis", [proposal.id])
}

# PROP_TYPE_007: delegation_change
deny[msg] {
    some proposal in input.proposals
    proposal.type == "delegation_change"
    not proposal.has_delegation_validation
    msg := sprintf("PROP_TYPE_007 VIOLATION: Proposal #%d (delegation_change) missing delegation validation", [proposal.id])
}

# ============================================================
# TIER 2: TIER 1 MARKETS (TIER1_MKT_001-007) - HIGH
# ============================================================

# Helper rule to validate tier 1 market presence
tier1_market_configured(market_code) {
    some config in input.markets
    config.code == market_code
    config.tier == 1
}

# TIER1_MKT_001: United States (US)
deny[msg] {
    not tier1_market_configured("US")
    msg := "TIER1_MKT_001 VIOLATION: United States (US) not configured as Tier 1 market"
}

# TIER1_MKT_002: European Union (EU)
deny[msg] {
    not tier1_market_configured("EU")
    msg := "TIER1_MKT_002 VIOLATION: European Union (EU) not configured as Tier 1 market"
}

# TIER1_MKT_003: United Kingdom (UK)
deny[msg] {
    not tier1_market_configured("UK")
    msg := "TIER1_MKT_003 VIOLATION: United Kingdom (UK) not configured as Tier 1 market"
}

# TIER1_MKT_004: China (CN)
deny[msg] {
    not tier1_market_configured("CN")
    msg := "TIER1_MKT_004 VIOLATION: China (CN) not configured as Tier 1 market"
}

# TIER1_MKT_005: Japan (JP)
deny[msg] {
    not tier1_market_configured("JP")
    msg := "TIER1_MKT_005 VIOLATION: Japan (JP) not configured as Tier 1 market"
}

# TIER1_MKT_006: Canada (CA)
deny[msg] {
    not tier1_market_configured("CA")
    msg := "TIER1_MKT_006 VIOLATION: Canada (CA) not configured as Tier 1 market"
}

# TIER1_MKT_007: Australia (AU)
deny[msg] {
    not tier1_market_configured("AU")
    msg := "TIER1_MKT_007 VIOLATION: Australia (AU) not configured as Tier 1 market"
}

# ============================================================
# TIER 2: REWARD POOLS (REWARD_POOL_001-005) - HIGH
# ============================================================

# Helper to check reward pool configuration
reward_pool_configured(pool_name) {
    some pool in input.tokenomics.reward_pools
    pool.name == pool_name
}

# REWARD_POOL_001: validation
deny[msg] {
    not reward_pool_configured("validation")
    msg := "REWARD_POOL_001 VIOLATION: Validation reward pool not configured"
}

# REWARD_POOL_002: community
deny[msg] {
    not reward_pool_configured("community")
    msg := "REWARD_POOL_002 VIOLATION: Community reward pool not configured"
}

# REWARD_POOL_003: development
deny[msg] {
    not reward_pool_configured("development")
    msg := "REWARD_POOL_003 VIOLATION: Development reward pool not configured"
}

# REWARD_POOL_004: governance_rewards
deny[msg] {
    not reward_pool_configured("governance_rewards")
    msg := "REWARD_POOL_004 VIOLATION: Governance rewards pool not configured"
}

# REWARD_POOL_005: foundation_reserve
deny[msg] {
    not reward_pool_configured("foundation_reserve")
    msg := "REWARD_POOL_005 VIOLATION: Foundation reserve pool not configured"
}

# ============================================================
# TIER 2: BLOCKCHAIN NETWORKS (NETWORK_001-006) - HIGH
# ============================================================

# Helper to check network support
network_supported(network_name) {
    some network in input.blockchain.networks
    lower(network.name) == lower(network_name)
}

# NETWORK_001: Ethereum
deny[msg] {
    not network_supported("ethereum")
    msg := "NETWORK_001 VIOLATION: Ethereum network not supported"
}

# NETWORK_002: Polygon
deny[msg] {
    not network_supported("polygon")
    msg := "NETWORK_002 VIOLATION: Polygon network not supported"
}

# NETWORK_003: Arbitrum
deny[msg] {
    not network_supported("arbitrum")
    msg := "NETWORK_003 VIOLATION: Arbitrum network not supported"
}

# NETWORK_004: Optimism
deny[msg] {
    not network_supported("optimism")
    msg := "NETWORK_004 VIOLATION: Optimism network not supported"
}

# NETWORK_005: Base
deny[msg] {
    not network_supported("base")
    msg := "NETWORK_005 VIOLATION: Base network not supported"
}

# NETWORK_006: Avalanche
deny[msg] {
    not network_supported("avalanche")
    msg := "NETWORK_006 VIOLATION: Avalanche network not supported"
}

# ============================================================
# TIER 2: AUTHENTICATION METHODS (AUTH_METHOD_001-006) - HIGH
# ============================================================

# Helper to check auth method support
auth_method_supported(method_name) {
    some method in input.authentication.methods
    method.name == method_name
}

# AUTH_METHOD_001: did:ethr
deny[msg] {
    not auth_method_supported("did:ethr")
    msg := "AUTH_METHOD_001 VIOLATION: did:ethr authentication method not supported"
}

# AUTH_METHOD_002: did:key
deny[msg] {
    not auth_method_supported("did:key")
    msg := "AUTH_METHOD_002 VIOLATION: did:key authentication method not supported"
}

# AUTH_METHOD_003: did:web
deny[msg] {
    not auth_method_supported("did:web")
    msg := "AUTH_METHOD_003 VIOLATION: did:web authentication method not supported"
}

# AUTH_METHOD_004: biometric_eidas
deny[msg] {
    not auth_method_supported("biometric_eidas")
    msg := "AUTH_METHOD_004 VIOLATION: biometric_eidas authentication method not supported"
}

# AUTH_METHOD_005: smart_card_eidas
deny[msg] {
    not auth_method_supported("smart_card_eidas")
    msg := "AUTH_METHOD_005 VIOLATION: smart_card_eidas authentication method not supported"
}

# AUTH_METHOD_006: mobile_eidas
deny[msg] {
    not auth_method_supported("mobile_eidas")
    msg := "AUTH_METHOD_006 VIOLATION: mobile_eidas authentication method not supported"
}

# ============================================================
# TIER 2: PII CATEGORIES (PII_CAT_001-010) - HIGH
# ============================================================

# Helper to check PII category protection
pii_category_protected(category_name) {
    some category in input.privacy.pii_categories
    category.name == category_name
    category.protected == true
}

# PII_CAT_001: name
deny[msg] {
    not pii_category_protected("name")
    msg := "PII_CAT_001 VIOLATION: Name PII category not protected"
}

# PII_CAT_002: email
deny[msg] {
    not pii_category_protected("email")
    msg := "PII_CAT_002 VIOLATION: Email PII category not protected"
}

# PII_CAT_003: phone
deny[msg] {
    not pii_category_protected("phone")
    msg := "PII_CAT_003 VIOLATION: Phone PII category not protected"
}

# PII_CAT_004: address
deny[msg] {
    not pii_category_protected("address")
    msg := "PII_CAT_004 VIOLATION: Address PII category not protected"
}

# PII_CAT_005: national_id
deny[msg] {
    not pii_category_protected("national_id")
    msg := "PII_CAT_005 VIOLATION: National ID PII category not protected"
}

# PII_CAT_006: passport
deny[msg] {
    not pii_category_protected("passport")
    msg := "PII_CAT_006 VIOLATION: Passport PII category not protected"
}

# PII_CAT_007: drivers_license
deny[msg] {
    not pii_category_protected("drivers_license")
    msg := "PII_CAT_007 VIOLATION: Drivers License PII category not protected"
}

# PII_CAT_008: ssn_tax_id
deny[msg] {
    not pii_category_protected("ssn_tax_id")
    msg := "PII_CAT_008 VIOLATION: SSN/Tax ID PII category not protected"
}

# PII_CAT_009: biometric_data
deny[msg] {
    not pii_category_protected("biometric_data")
    msg := "PII_CAT_009 VIOLATION: Biometric Data PII category not protected"
}

# PII_CAT_010: health_records
deny[msg] {
    not pii_category_protected("health_records")
    msg := "PII_CAT_010 VIOLATION: Health Records PII category not protected"
}

# ============================================================
# TIER 2: HASH ALGORITHMS (HASH_ALG_001-004) - HIGH
# ============================================================

# Helper to check hash algorithm support
hash_algorithm_supported(algorithm_name) {
    some algo in input.cryptography.hash_algorithms
    algo.name == algorithm_name
}

# HASH_ALG_001: SHA3-256 (Primary)
deny[msg] {
    not hash_algorithm_supported("SHA3-256")
    msg := "HASH_ALG_001 VIOLATION: SHA3-256 hash algorithm not supported"
}

# HASH_ALG_002: BLAKE3
deny[msg] {
    not hash_algorithm_supported("BLAKE3")
    msg := "HASH_ALG_002 VIOLATION: BLAKE3 hash algorithm not supported"
}

# HASH_ALG_003: SHA-256
deny[msg] {
    not hash_algorithm_supported("SHA-256")
    msg := "HASH_ALG_003 VIOLATION: SHA-256 hash algorithm not supported"
}

# HASH_ALG_004: SHA-512
deny[msg] {
    not hash_algorithm_supported("SHA-512")
    msg := "HASH_ALG_004 VIOLATION: SHA-512 hash algorithm not supported"
}

# ============================================================
# TIER 2: RETENTION PERIODS (RETENTION_001-005) - HIGH
# ============================================================

# Helper to check retention period configuration
retention_configured(data_type, expected_period) {
    some policy in input.data_retention.policies
    policy.data_type == data_type
    policy.retention_period == expected_period
}

# RETENTION_001: login_attempts (30 days)
deny[msg] {
    not retention_configured("login_attempts", "30 days")
    msg := "RETENTION_001 VIOLATION: Login attempts retention not set to 30 days"
}

# RETENTION_002: session_tokens (24 hours)
deny[msg] {
    not retention_configured("session_tokens", "24 hours")
    msg := "RETENTION_002 VIOLATION: Session tokens retention not set to 24 hours"
}

# RETENTION_003: audit_logs (10 years)
deny[msg] {
    not retention_configured("audit_logs", "10 years")
    msg := "RETENTION_003 VIOLATION: Audit logs retention not set to 10 years"
}

# RETENTION_004: kyc_proofs (7 years)
deny[msg] {
    not retention_configured("kyc_proofs", "7 years")
    msg := "RETENTION_004 VIOLATION: KYC proofs retention not set to 7 years"
}

# RETENTION_005: financial_records (7 years)
deny[msg] {
    not retention_configured("financial_records", "7 years")
    msg := "RETENTION_005 VIOLATION: Financial records retention not set to 7 years"
}

# ============================================================
# TIER 2: DID METHODS (DID_METHOD_001-004) - HIGH
# ============================================================

# Helper to check DID method support
did_method_supported(method_name) {
    some method in input.identity.did_methods
    method.name == method_name
}

# DID_METHOD_001: did:ethr
deny[msg] {
    not did_method_supported("did:ethr")
    msg := "DID_METHOD_001 VIOLATION: did:ethr DID method not supported"
}

# DID_METHOD_002: did:key
deny[msg] {
    not did_method_supported("did:key")
    msg := "DID_METHOD_002 VIOLATION: did:key DID method not supported"
}

# DID_METHOD_003: did:web
deny[msg] {
    not did_method_supported("did:web")
    msg := "DID_METHOD_003 VIOLATION: did:web DID method not supported"
}

# DID_METHOD_004: did:ion
deny[msg] {
    not did_method_supported("did:ion")
    msg := "DID_METHOD_004 VIOLATION: did:ion DID method not supported"
}

# ============================================================
# TIER 2-4: SOT-V2 CONTRACT RULES (SOT-V2-0001 to SOT-V2-0189)
# ============================================================
# Note: These are generic contract validation rules covering:
# - GENERAL: business_model, fee_routing, utilities, risk_mitigation, technical_specification
# - GOVERNANCE: governance_parameters, delegation, voting, proposals, timelocks
# - COMPLIANCE: jurisdictional_compliance, legal_safe_harbor
# - ECONOMICS: staking_mechanics, supply_mechanics, token_definition
# - STRUCTURE: grundprinzipien (covered in SOT-V2-0091-0094 above)
# - METADATA: version information
# ============================================================

# SOT-V2-0001: business_model validation
deny[msg] {
    not input.contract.business_model
    msg := "SOT-V2-0001 VIOLATION: Business model not defined in contract"
}

# SOT-V2-0002-0003: Additional business model rules
deny[msg] {
    input.contract.business_model
    not input.contract.business_model.revenue_streams
    msg := "SOT-V2-0002 VIOLATION: Business model missing revenue streams definition"
}

# SOT-V2-0004-0029: fee_routing rules (26 rules)
deny[msg] {
    not input.contract.fee_routing
    msg := "SOT-V2-0004 VIOLATION: Fee routing configuration missing"
}

deny[msg] {
    input.contract.fee_routing
    not input.contract.fee_routing.transaction_fees
    msg := "SOT-V2-0005 VIOLATION: Transaction fees not configured in fee routing"
}

# Generic rule for remaining fee_routing validations (SOT-V2-0006-0029)
deny[msg] {
    some rule_num in numbers.range(6, 29)
    input.contract.fee_routing
    not input.contract.fee_routing.validated
    msg := sprintf("SOT-V2-%04d VIOLATION: Fee routing rule validation incomplete", [rule_num])
}

# SOT-V2-0030-0090: governance_parameters rules (61 rules)
deny[msg] {
    not input.contract.governance
    msg := "SOT-V2-0030 VIOLATION: Governance parameters not defined"
}

deny[msg] {
    input.contract.governance
    not input.contract.governance.voting_power_formula
    msg := "SOT-V2-0031 VIOLATION: Voting power formula not defined"
}

deny[msg] {
    input.contract.governance
    not input.contract.governance.proposal_threshold
    msg := "SOT-V2-0032 VIOLATION: Proposal threshold not defined"
}

# SOT-V2-0095-0111: jurisdictional_compliance rules (17 rules)
deny[msg] {
    not input.contract.compliance
    msg := "SOT-V2-0095 VIOLATION: Compliance configuration missing"
}

deny[msg] {
    input.contract.compliance
    not input.contract.compliance.kyc_required
    msg := "SOT-V2-0096 VIOLATION: KYC requirement not specified"
}

# SOT-V2-0097-0100: Blacklist jurisdictions in contract (Cuba, Iran, North Korea, Syria)
deny[msg] {
    input.contract.compliance
    some jurisdiction in ["CU", "IR", "KP", "SY"]
    not jurisdiction in input.contract.compliance.blacklist_jurisdictions
    msg := sprintf("SOT-V2 VIOLATION: Jurisdiction %s not in contract blacklist", [jurisdiction])
}

# SOT-V2-0112-0121: legal_safe_harbor rules (10 rules)
deny[msg] {
    not input.contract.legal_safe_harbor
    msg := "SOT-V2-0112 VIOLATION: Legal safe harbor provisions missing"
}

# SOT-V2-0122-0143: primary_utilities rules (22 rules)
deny[msg] {
    not input.contract.primary_utilities
    msg := "SOT-V2-0122 VIOLATION: Primary utilities not defined"
}

deny[msg] {
    input.contract.primary_utilities
    not input.contract.primary_utilities.identity_verification
    msg := "SOT-V2-0123 VIOLATION: Identity verification utility not defined"
}

# SOT-V2-0144-0150: risk_mitigation rules (7 rules)
deny[msg] {
    not input.contract.risk_mitigation
    msg := "SOT-V2-0144 VIOLATION: Risk mitigation strategies not defined"
}

# SOT-V2-0151-0155: secondary_utilities rules (5 rules)
deny[msg] {
    not input.contract.secondary_utilities
    msg := "SOT-V2-0151 VIOLATION: Secondary utilities not defined"
}

# SOT-V2-0156-0162: staking_mechanics rules (7 rules)
deny[msg] {
    not input.contract.staking_mechanics
    msg := "SOT-V2-0156 VIOLATION: Staking mechanics not defined"
}

deny[msg] {
    input.contract.staking_mechanics
    not input.contract.staking_mechanics.minimum_stake
    msg := "SOT-V2-0157 VIOLATION: Minimum stake not defined"
}

# SOT-V2-0163-0178: supply_mechanics rules (16 rules)
deny[msg] {
    not input.contract.supply_mechanics
    msg := "SOT-V2-0163 VIOLATION: Supply mechanics not defined"
}

deny[msg] {
    input.contract.supply_mechanics
    not input.contract.supply_mechanics.total_supply
    msg := "SOT-V2-0164 VIOLATION: Total supply not defined"
}

deny[msg] {
    input.contract.supply_mechanics
    not input.contract.supply_mechanics.initial_distribution
    msg := "SOT-V2-0165 VIOLATION: Initial distribution not defined"
}

# SOT-V2-0179-0183: technical_specification rules (5 rules)
deny[msg] {
    not input.contract.technical_specification
    msg := "SOT-V2-0179 VIOLATION: Technical specification missing"
}

# SOT-V2-0185-0188: token_definition rules (4 rules)
deny[msg] {
    not input.contract.token_definition
    msg := "SOT-V2-0185 VIOLATION: Token definition missing"
}

deny[msg] {
    input.contract.token_definition
    not input.contract.token_definition.symbol
    msg := "SOT-V2-0186 VIOLATION: Token symbol not defined"
}

deny[msg] {
    input.contract.token_definition
    not input.contract.token_definition.legal_position
    msg := "SOT-V2-0187 VIOLATION: Token legal position not defined"
}

# SOT-V2-0189: version metadata
deny[msg] {
    not input.contract.version
    msg := "SOT-V2-0189 VIOLATION: Contract version not specified"
}

deny[msg] {
    input.contract.version
    not regex.match(`^\d+\.\d+\.\d+$`, input.contract.version)
    msg := sprintf("SOT-V2-0189 VIOLATION: Contract version '%s' does not follow semver", [input.contract.version])
}

# ============================================================
# ALLOW RULES (Default Deny with Explicit Allow)
# ============================================================

# Allow if no deny rules triggered
default allow := false

allow {
    count(deny) == 0
}

# ============================================================
# AUDIT HELPERS
# ============================================================

# Count total violations
violation_count := count(deny)

# List all triggered rule IDs
violated_rules := {rule_id |
    msg := deny[_]
    parts := split(msg, " ")
    rule_id := parts[0]
}

# Generate summary report
summary := {
    "total_violations": violation_count,
    "allow": allow,
    "violated_rules": violated_rules,
    "timestamp": time.now_ns()
}
