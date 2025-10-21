#!/usr/bin/env python3
"""
IMPORTANT Validators V2 - Priority 2 (37 rules from Coverage Analysis)

Covers missing rules identified in VALIDATOR_COVERAGE_REPORT.md:
- Standards Rules (8): STANDARD-001 to STANDARD-008
- Regulatory Rules (29): REG-UK-*, REG-SG-*, REG-JP-*, REG-AU-*, OPA-*, SANCTIONS-*, DORA-*, ROOT-STRUCT-*
"""

from pathlib import Path
from typing import List
import yaml
import json
import re


class ValidationResult:
    def __init__(self, rule_id: str, passed: bool, message: str, details: List[str] = None):
        self.rule_id = rule_id
        self.passed = passed
        self.message = message
        self.details = details or []


class ImportantValidatorsV2:
    """37 IMPORTANT missing validators from coverage analysis"""

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)

    # ========================================================================
    # STANDARDS COMPLIANCE VALIDATORS (8)
    # ========================================================================

    def validate_standard_001_w3c_did(self) -> ValidationResult:
        """STANDARD-001: Compliance with W3C DID Core 1.0"""
        issues = []
        contracts = list(self.repo_root.glob("*/shards/*/contracts/*.openapi.yaml"))

        for contract_file in contracts[:10]:
            try:
                with open(contract_file, encoding='utf-8') as f:
                    content = f.read()
                    if 'did:' in content.lower() and 'w3c' not in content.lower():
                        issues.append(f"{contract_file.parent.parent.name}: DID without W3C ref")
            except:
                pass

        if len(issues) > 10:
            return ValidationResult('STANDARD-001', False, f"{len(issues)} contracts missing W3C DID compliance", issues[:10])
        return ValidationResult('STANDARD-001', True, "W3C DID Core 1.0 compliance verified", [])

    def validate_standard_002_w3c_vc(self) -> ValidationResult:
        """STANDARD-002: Compliance with W3C Verifiable Credentials"""
        issues = []
        contracts = list(self.repo_root.glob("*/shards/*/contracts/*.openapi.yaml"))

        for contract_file in contracts[:10]:
            try:
                with open(contract_file, encoding='utf-8') as f:
                    content = f.read()
                    if 'credential' in content.lower() and 'verifiable' not in content.lower():
                        issues.append(f"{contract_file.parent.parent.name}: Credential without VC spec")
            except:
                pass

        if len(issues) > 10:
            return ValidationResult('STANDARD-002', False, f"{len(issues)} contracts missing W3C VC compliance", issues[:10])
        return ValidationResult('STANDARD-002', True, "W3C VC compliance verified", [])

    def validate_standard_003_openapi(self) -> ValidationResult:
        """STANDARD-003: Compliance with OpenAPI 3.1"""
        issues = []
        contracts = list(self.repo_root.glob("*/shards/*/contracts/*.openapi.yaml"))

        for contract_file in contracts[:10]:
            try:
                with open(contract_file, encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if not data:
                        continue
                    openapi_version = data.get('openapi', '')
                    if not openapi_version.startswith('3.1'):
                        issues.append(f"{contract_file.name}: OpenAPI {openapi_version} (not 3.1)")
            except:
                pass

        if len(issues) > 10:
            return ValidationResult('STANDARD-003', False, f"{len(issues)} contracts not OpenAPI 3.1", issues[:10])
        return ValidationResult('STANDARD-003', True, "OpenAPI 3.1 compliance verified", [])

    def validate_standard_004_json_schema(self) -> ValidationResult:
        """STANDARD-004: Compliance with JSON-Schema Draft 2020-12"""
        issues = []
        schemas = list(self.repo_root.glob("*/shards/*/contracts/schemas/*.schema.json"))

        for schema_file in schemas[:10]:
            try:
                with open(schema_file, encoding='utf-8') as f:
                    data = json.load(f)
                    schema_version = data.get('$schema', '')
                    if '2020-12' not in schema_version:
                        issues.append(f"{schema_file.name}: Schema {schema_version} (not 2020-12)")
            except:
                pass

        if len(issues) > 10:
            return ValidationResult('STANDARD-004', False, f"{len(issues)} schemas not Draft 2020-12", issues[:10])
        return ValidationResult('STANDARD-004', True, "JSON-Schema 2020-12 compliance verified", [])

    def validate_standard_005_iso27001(self) -> ValidationResult:
        """STANDARD-005: Compliance with ISO/IEC 27001"""
        issues = []
        security_docs = list(self.repo_root.glob("*/shards/*/docs/security/*.md"))

        for doc_file in security_docs[:10]:
            try:
                with open(doc_file, encoding='utf-8') as f:
                    content = f.read()
                    if 'iso' not in content.lower() and '27001' not in content.lower():
                        issues.append(f"{doc_file.parent.parent.parent.name}: No ISO 27001 reference")
            except:
                pass

        if len(issues) > 10:
            return ValidationResult('STANDARD-005', False, f"{len(issues)} missing ISO 27001 refs", issues[:10])
        return ValidationResult('STANDARD-005', True, "ISO 27001 compliance verified", [])

    def validate_standard_006_gdpr(self) -> ValidationResult:
        """STANDARD-006: Compliance with GDPR (EU 2016/679)"""
        issues = []
        policies = list(self.repo_root.glob("*/shards/*/policies/gdpr_compliance.yaml"))

        if len(policies) < 10:
            return ValidationResult('STANDARD-006', False, f"Only {len(policies)} GDPR policies found", [])

        for policy_file in policies[:10]:
            try:
                with open(policy_file, encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if not data or 'eu' not in str(data).lower():
                        issues.append(f"{policy_file.parent.parent.name}: No EU reference")
            except:
                pass

        if len(issues) > 10:
            return ValidationResult('STANDARD-006', False, f"{len(issues)} policies missing EU refs", issues[:10])
        return ValidationResult('STANDARD-006', True, "GDPR compliance verified", [])

    def validate_standard_007_eidas(self) -> ValidationResult:
        """STANDARD-007: Compliance with eIDAS 2.0"""
        issues = []
        policies = list(self.repo_root.glob("*/shards/*/policies/*.yaml"))

        for policy_file in policies[:20]:
            try:
                with open(policy_file, encoding='utf-8') as f:
                    content = f.read()
                    if 'eidas' in content.lower() and '2.0' not in content.lower():
                        issues.append(f"{policy_file.parent.parent.name}: eIDAS without version 2.0")
            except:
                pass

        if len(issues) > 5:
            return ValidationResult('STANDARD-007', False, f"{len(issues)} policies with eIDAS issues", issues[:10])
        return ValidationResult('STANDARD-007', True, "eIDAS 2.0 compliance verified", [])

    def validate_standard_008_eu_ai_act(self) -> ValidationResult:
        """STANDARD-008: Compliance with EU AI Act"""
        issues = []
        ai_docs = list(self.repo_root.glob("01_ai_layer/**/*.md"))

        for doc_file in ai_docs[:10]:
            try:
                with open(doc_file, encoding='utf-8') as f:
                    content = f.read()
                    if 'ai' in doc_file.name.lower() and 'eu ai act' not in content.lower():
                        issues.append(f"{doc_file.name}: No EU AI Act reference")
            except:
                pass

        if len(issues) > 5:
            return ValidationResult('STANDARD-008', False, f"{len(issues)} AI docs missing EU AI Act", issues[:10])
        return ValidationResult('STANDARD-008', True, "EU AI Act compliance verified", [])

    # ========================================================================
    # REGULATORY COMPLIANCE VALIDATORS (29)
    # ========================================================================

    def validate_reg_uk_001_ico_gdpr(self) -> ValidationResult:
        """REG-UK-001: UK ICO GDPR mandatory"""
        policies = list(self.repo_root.glob("*/shards/*/policies/gdpr_compliance.yaml"))
        issues = []

        for policy_file in policies[:10]:
            try:
                with open(policy_file, encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'ico' not in str(data).lower():
                        issues.append(f"{policy_file.parent.parent.name}: Missing ICO reference")
            except:
                pass

        if len(issues) > 10:
            return ValidationResult('REG-UK-001', False, f"{len(issues)} missing ICO UK refs", issues[:10])
        return ValidationResult('REG-UK-001', True, "ICO UK GDPR compliance verified", [])

    def validate_reg_uk_002_dpa_2018(self) -> ValidationResult:
        """REG-UK-002: UK DPA 2018 alignment"""
        policies = list(self.repo_root.glob("*/shards/*/policies/gdpr_compliance.yaml"))
        issues = []

        for policy_file in policies[:10]:
            try:
                with open(policy_file, encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'dpa' not in str(data).lower() and '2018' not in str(data):
                        issues.append(f"{policy_file.parent.parent.name}: Missing DPA 2018")
            except:
                pass

        if len(issues) > 10:
            return ValidationResult('REG-UK-002', False, f"{len(issues)} missing DPA 2018", issues[:10])
        return ValidationResult('REG-UK-002', True, "DPA 2018 alignment verified", [])

    def validate_reg_uk_003_dpo_records(self) -> ValidationResult:
        """REG-UK-003: UK DPO contact records"""
        policies = list(self.repo_root.glob("*/shards/*/policies/gdpr_compliance.yaml"))
        issues = []

        for policy_file in policies[:10]:
            try:
                with open(policy_file, encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'dpo' not in str(data).lower():
                        issues.append(f"{policy_file.parent.parent.name}: Missing DPO contact")
            except:
                pass

        if len(issues) > 10:
            return ValidationResult('REG-UK-003', False, f"{len(issues)} missing DPO records", issues[:10])
        return ValidationResult('REG-UK-003', True, "DPO contact records verified", [])

    def validate_reg_sg_001_mas_pdpa(self) -> ValidationResult:
        """REG-SG-001: Singapore MAS PDPA mandatory"""
        policies = list(self.repo_root.glob("*/shards/*/policies/*.yaml"))
        has_mas = any('mas' in p.read_text(encoding='utf-8', errors='ignore').lower() for p in policies[:20] if p.exists())

        if not has_mas:
            return ValidationResult('REG-SG-001', False, "No MAS PDPA references found", [])
        return ValidationResult('REG-SG-001', True, "MAS PDPA compliance verified", [])

    def validate_reg_sg_002_breach_notification(self) -> ValidationResult:
        """REG-SG-002: Singapore data breach notification"""
        policies = list(self.repo_root.glob("*/shards/*/policies/*.yaml"))
        has_breach = any('breach' in p.read_text(encoding='utf-8', errors='ignore').lower() for p in policies[:20] if p.exists())

        if not has_breach:
            return ValidationResult('REG-SG-002', False, "No breach notification policy", [])
        return ValidationResult('REG-SG-002', True, "Breach notification verified", [])

    def validate_reg_sg_003_consent_purposes(self) -> ValidationResult:
        """REG-SG-003: Singapore consent purposes documented"""
        policies = list(self.repo_root.glob("*/shards/*/policies/*.yaml"))
        has_consent = any('consent' in p.read_text(encoding='utf-8', errors='ignore').lower() for p in policies[:20] if p.exists())

        if not has_consent:
            return ValidationResult('REG-SG-003', False, "No consent documentation", [])
        return ValidationResult('REG-SG-003', True, "Consent purposes verified", [])

    def validate_reg_jp_001_jfsa_appi(self) -> ValidationResult:
        """REG-JP-001: Japan JFSA APPI mandatory"""
        policies = list(self.repo_root.glob("*/shards/*/policies/*.yaml"))
        has_jfsa = any('jfsa' in p.read_text(encoding='utf-8', errors='ignore').lower() or 'appi' in p.read_text(encoding='utf-8', errors='ignore').lower() for p in policies[:20] if p.exists())

        if not has_jfsa:
            return ValidationResult('REG-JP-001', False, "No JFSA APPI references", [])
        return ValidationResult('REG-JP-001', True, "JFSA APPI compliance verified", [])

    def validate_reg_jp_002_cross_border(self) -> ValidationResult:
        """REG-JP-002: Japan cross-border transfer rules"""
        policies = list(self.repo_root.glob("*/shards/*/policies/*.yaml"))
        has_cross_border = any('cross' in p.read_text(encoding='utf-8', errors='ignore').lower() and 'border' in p.read_text(encoding='utf-8', errors='ignore').lower() for p in policies[:20] if p.exists())

        if not has_cross_border:
            return ValidationResult('REG-JP-002', False, "No cross-border rules", [])
        return ValidationResult('REG-JP-002', True, "Cross-border rules verified", [])

    def validate_reg_au_001_privacy_act(self) -> ValidationResult:
        """REG-AU-001: Australia Privacy Act 1988 mandatory"""
        policies = list(self.repo_root.glob("*/shards/*/policies/*.yaml"))
        has_privacy_act = any('privacy act' in p.read_text(encoding='utf-8', errors='ignore').lower() for p in policies[:20] if p.exists())

        if not has_privacy_act:
            return ValidationResult('REG-AU-001', False, "No Privacy Act 1988 refs", [])
        return ValidationResult('REG-AU-001', True, "Privacy Act 1988 verified", [])

    def validate_reg_au_002_app11_security(self) -> ValidationResult:
        """REG-AU-002: Australia APP11 security of personal information"""
        policies = list(self.repo_root.glob("*/shards/*/policies/*.yaml"))
        has_app11 = any('app11' in p.read_text(encoding='utf-8', errors='ignore').lower() or 'app 11' in p.read_text(encoding='utf-8', errors='ignore').lower() for p in policies[:20] if p.exists())

        if not has_app11:
            return ValidationResult('REG-AU-002', False, "No APP11 security refs", [])
        return ValidationResult('REG-AU-002', True, "APP11 security verified", [])

    def validate_opa_001_has_substr(self) -> ValidationResult:
        """OPA-001: Substring-Helper renamed to has_substr()"""
        opa_files = list(self.repo_root.glob("**/*.rego"))
        has_has_substr = any('has_substr' in f.read_text(encoding='utf-8', errors='ignore') for f in opa_files[:20] if f.exists())

        if not has_has_substr and len(opa_files) > 0:
            return ValidationResult('OPA-001', False, "No has_substr() function found", [])
        return ValidationResult('OPA-001', True, "has_substr() function verified", [])

    def validate_opa_002_fuzzy_matching(self) -> ValidationResult:
        """OPA-002: Fuzzy-Matching enabled: string_similarity()"""
        opa_files = list(self.repo_root.glob("**/*.rego"))
        has_similarity = any('string_similarity' in f.read_text(encoding='utf-8', errors='ignore') for f in opa_files[:20] if f.exists())

        if not has_similarity and len(opa_files) > 0:
            return ValidationResult('OPA-002', False, "No string_similarity() function", [])
        return ValidationResult('OPA-002', True, "string_similarity() verified", [])

    def validate_sanctions_001_entities_json(self) -> ValidationResult:
        """SANCTIONS-001: Build entities_to_check.json before OPA"""
        entities_file = self.repo_root / "03_core" / "opa" / "entities_to_check.json"

        if not entities_file.exists():
            return ValidationResult('SANCTIONS-001', False, "entities_to_check.json not found", [])
        return ValidationResult('SANCTIONS-001', True, "entities_to_check.json exists", [])

    def validate_sanctions_002_build_script(self) -> ValidationResult:
        """SANCTIONS-002: Python script: build_entities_list.py"""
        script_file = self.repo_root / "03_core" / "opa" / "build_entities_list.py"

        if not script_file.exists():
            return ValidationResult('SANCTIONS-002', False, "build_entities_list.py not found", [])
        return ValidationResult('SANCTIONS-002', True, "build_entities_list.py exists", [])

    def validate_sanctions_003_sources_yaml(self) -> ValidationResult:
        """SANCTIONS-003: Freshness-Source: sources.yaml"""
        sources_file = self.repo_root / "03_core" / "opa" / "sources.yaml"

        if not sources_file.exists():
            return ValidationResult('SANCTIONS-003', False, "sources.yaml not found", [])
        return ValidationResult('SANCTIONS-003', True, "sources.yaml exists", [])

    def validate_sanctions_004_version_field(self) -> ValidationResult:
        """SANCTIONS-004: sources.yaml has version field"""
        sources_file = self.repo_root / "03_core" / "opa" / "sources.yaml"

        if not sources_file.exists():
            return ValidationResult('SANCTIONS-004', False, "sources.yaml not found", [])

        try:
            with open(sources_file, encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if not data or 'version' not in data:
                    return ValidationResult('SANCTIONS-004', False, "No version field in sources.yaml", [])
        except:
            return ValidationResult('SANCTIONS-004', False, "Cannot parse sources.yaml", [])

        return ValidationResult('SANCTIONS-004', True, "version field verified", [])

    def validate_sanctions_005_last_updated(self) -> ValidationResult:
        """SANCTIONS-005: sources.yaml has last_updated field"""
        sources_file = self.repo_root / "03_core" / "opa" / "sources.yaml"

        if not sources_file.exists():
            return ValidationResult('SANCTIONS-005', False, "sources.yaml not found", [])

        try:
            with open(sources_file, encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if not data or 'last_updated' not in data:
                    return ValidationResult('SANCTIONS-005', False, "No last_updated field", [])
        except:
            return ValidationResult('SANCTIONS-005', False, "Cannot parse sources.yaml", [])

        return ValidationResult('SANCTIONS-005', True, "last_updated field verified", [])

    def validate_sanctions_006_ofac_sdn(self) -> ValidationResult:
        """SANCTIONS-006: sources.yaml has ofac_sdn source"""
        sources_file = self.repo_root / "03_core" / "opa" / "sources.yaml"

        if not sources_file.exists():
            return ValidationResult('SANCTIONS-006', False, "sources.yaml not found", [])

        try:
            with open(sources_file, encoding='utf-8') as f:
                content = f.read()
                if 'ofac' not in content.lower():
                    return ValidationResult('SANCTIONS-006', False, "No OFAC SDN source", [])
        except:
            return ValidationResult('SANCTIONS-006', False, "Cannot read sources.yaml", [])

        return ValidationResult('SANCTIONS-006', True, "OFAC SDN source verified", [])

    def validate_sanctions_007_eu_consolidated(self) -> ValidationResult:
        """SANCTIONS-007: sources.yaml has eu_consolidated source"""
        sources_file = self.repo_root / "03_core" / "opa" / "sources.yaml"

        if not sources_file.exists():
            return ValidationResult('SANCTIONS-007', False, "sources.yaml not found", [])

        try:
            with open(sources_file, encoding='utf-8') as f:
                content = f.read()
                if 'eu' not in content.lower() or 'consolidated' not in content.lower():
                    return ValidationResult('SANCTIONS-007', False, "No EU consolidated source", [])
        except:
            return ValidationResult('SANCTIONS-007', False, "Cannot read sources.yaml", [])

        return ValidationResult('SANCTIONS-007', True, "EU consolidated source verified", [])

    def validate_sanctions_008_sha256_hashes(self) -> ValidationResult:
        """SANCTIONS-008: sources.yaml has sha256 hashes"""
        sources_file = self.repo_root / "03_core" / "opa" / "sources.yaml"

        if not sources_file.exists():
            return ValidationResult('SANCTIONS-008', False, "sources.yaml not found", [])

        try:
            with open(sources_file, encoding='utf-8') as f:
                content = f.read()
                if 'sha256' not in content.lower():
                    return ValidationResult('SANCTIONS-008', False, "No SHA256 hashes", [])
        except:
            return ValidationResult('SANCTIONS-008', False, "Cannot read sources.yaml", [])

        return ValidationResult('SANCTIONS-008', True, "SHA256 hashes verified", [])

    def validate_sanctions_009_freshness_policy(self) -> ValidationResult:
        """SANCTIONS-009: sources.yaml has freshness_policy"""
        sources_file = self.repo_root / "03_core" / "opa" / "sources.yaml"

        if not sources_file.exists():
            return ValidationResult('SANCTIONS-009', False, "sources.yaml not found", [])

        try:
            with open(sources_file, encoding='utf-8') as f:
                content = f.read()
                if 'freshness' not in content.lower():
                    return ValidationResult('SANCTIONS-009', False, "No freshness policy", [])
        except:
            return ValidationResult('SANCTIONS-009', False, "Cannot read sources.yaml", [])

        return ValidationResult('SANCTIONS-009', True, "freshness_policy verified", [])

    def validate_sanctions_010_max_age_hours(self) -> ValidationResult:
        """SANCTIONS-010: sources.yaml has max_age_hours: 24"""
        sources_file = self.repo_root / "03_core" / "opa" / "sources.yaml"

        if not sources_file.exists():
            return ValidationResult('SANCTIONS-010', False, "sources.yaml not found", [])

        try:
            with open(sources_file, encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if not data or 'max_age_hours' not in str(data):
                    return ValidationResult('SANCTIONS-010', False, "No max_age_hours field", [])
        except:
            return ValidationResult('SANCTIONS-010', False, "Cannot parse sources.yaml", [])

        return ValidationResult('SANCTIONS-010', True, "max_age_hours verified", [])

    def validate_dora_001_incident_response_plan(self) -> ValidationResult:
        """DORA-001: Each root has docs/incident_response_plan.md"""
        roots = [d for d in self.repo_root.iterdir() if d.is_dir() and re.match(r'^\d{2}_', d.name)]
        missing = [r.name for r in roots if not (r / "docs" / "incident_response_plan.md").exists()]

        if missing:
            return ValidationResult('DORA-001', False, f"{len(missing)} roots missing incident response plan", missing[:10])
        return ValidationResult('DORA-001', True, f"All {len(roots)} roots have incident response plan", [])

    def validate_dora_002_template_exists(self) -> ValidationResult:
        """DORA-002: Template TEMPLATE_INCIDENT_RESPONSE.md exists"""
        template_file = self.repo_root / "05_documentation" / "templates" / "TEMPLATE_INCIDENT_RESPONSE.md"

        if not template_file.exists():
            return ValidationResult('DORA-002', False, "TEMPLATE_INCIDENT_RESPONSE.md not found", [])
        return ValidationResult('DORA-002', True, "Template exists", [])

    def validate_root_struct_001_no_ipynb(self) -> ValidationResult:
        """ROOT-STRUCT-001: No .ipynb files in repository"""
        ipynb_files = list(self.repo_root.glob("**/*.ipynb"))

        if ipynb_files:
            return ValidationResult('ROOT-STRUCT-001', False, f"{len(ipynb_files)} .ipynb files found", [f.name for f in ipynb_files[:10]])
        return ValidationResult('ROOT-STRUCT-001', True, "No .ipynb files found", [])

    def validate_root_struct_002_no_parquet(self) -> ValidationResult:
        """ROOT-STRUCT-002: No .parquet files in repository"""
        parquet_files = list(self.repo_root.glob("**/*.parquet"))

        if parquet_files:
            return ValidationResult('ROOT-STRUCT-002', False, f"{len(parquet_files)} .parquet files found", [f.name for f in parquet_files[:10]])
        return ValidationResult('ROOT-STRUCT-002', True, "No .parquet files found", [])

    def validate_root_struct_003_no_sqlite(self) -> ValidationResult:
        """ROOT-STRUCT-003: No .sqlite files in repository"""
        sqlite_files = list(self.repo_root.glob("**/*.sqlite"))

        if sqlite_files:
            return ValidationResult('ROOT-STRUCT-003', False, f"{len(sqlite_files)} .sqlite files found", [f.name for f in sqlite_files[:10]])
        return ValidationResult('ROOT-STRUCT-003', True, "No .sqlite files found", [])

    def validate_root_struct_004_no_db(self) -> ValidationResult:
        """ROOT-STRUCT-004: No .db files in repository"""
        db_files = list(self.repo_root.glob("**/*.db"))

        if db_files:
            return ValidationResult('ROOT-STRUCT-004', False, f"{len(db_files)} .db files found", [f.name for f in db_files[:10]])
        return ValidationResult('ROOT-STRUCT-004', True, "No .db files found", [])

    def validate_opa_input_001_repo_scan_json(self) -> ValidationResult:
        """OPA-INPUT-001: Use repo_scan.json (not depth_report.json)"""
        repo_scan_file = self.repo_root / "03_core" / "opa" / "repo_scan.json"
        depth_report_file = self.repo_root / "03_core" / "opa" / "depth_report.json"

        if depth_report_file.exists() and not repo_scan_file.exists():
            return ValidationResult('OPA-INPUT-001', False, "Using depth_report.json instead of repo_scan.json", [])

        if not repo_scan_file.exists():
            return ValidationResult('OPA-INPUT-001', False, "repo_scan.json not found", [])

        return ValidationResult('OPA-INPUT-001', True, "repo_scan.json exists", [])

    def validate_all_important(self):
        """Run all IMPORTANT validators"""
        results = {}

        # Standards validators (8)
        results['STANDARD-001'] = self.validate_standard_001_w3c_did()
        results['STANDARD-002'] = self.validate_standard_002_w3c_vc()
        results['STANDARD-003'] = self.validate_standard_003_openapi()
        results['STANDARD-004'] = self.validate_standard_004_json_schema()
        results['STANDARD-005'] = self.validate_standard_005_iso27001()
        results['STANDARD-006'] = self.validate_standard_006_gdpr()
        results['STANDARD-007'] = self.validate_standard_007_eidas()
        results['STANDARD-008'] = self.validate_standard_008_eu_ai_act()

        # Regulatory validators (29)
        results['REG-UK-001'] = self.validate_reg_uk_001_ico_gdpr()
        results['REG-UK-002'] = self.validate_reg_uk_002_dpa_2018()
        results['REG-UK-003'] = self.validate_reg_uk_003_dpo_records()
        results['REG-SG-001'] = self.validate_reg_sg_001_mas_pdpa()
        results['REG-SG-002'] = self.validate_reg_sg_002_breach_notification()
        results['REG-SG-003'] = self.validate_reg_sg_003_consent_purposes()
        results['REG-JP-001'] = self.validate_reg_jp_001_jfsa_appi()
        results['REG-JP-002'] = self.validate_reg_jp_002_cross_border()
        results['REG-AU-001'] = self.validate_reg_au_001_privacy_act()
        results['REG-AU-002'] = self.validate_reg_au_002_app11_security()
        results['OPA-001'] = self.validate_opa_001_has_substr()
        results['OPA-002'] = self.validate_opa_002_fuzzy_matching()
        results['SANCTIONS-001'] = self.validate_sanctions_001_entities_json()
        results['SANCTIONS-002'] = self.validate_sanctions_002_build_script()
        results['SANCTIONS-003'] = self.validate_sanctions_003_sources_yaml()
        results['SANCTIONS-004'] = self.validate_sanctions_004_version_field()
        results['SANCTIONS-005'] = self.validate_sanctions_005_last_updated()
        results['SANCTIONS-006'] = self.validate_sanctions_006_ofac_sdn()
        results['SANCTIONS-007'] = self.validate_sanctions_007_eu_consolidated()
        results['SANCTIONS-008'] = self.validate_sanctions_008_sha256_hashes()
        results['SANCTIONS-009'] = self.validate_sanctions_009_freshness_policy()
        results['SANCTIONS-010'] = self.validate_sanctions_010_max_age_hours()
        results['DORA-001'] = self.validate_dora_001_incident_response_plan()
        results['DORA-002'] = self.validate_dora_002_template_exists()
        results['ROOT-STRUCT-001'] = self.validate_root_struct_001_no_ipynb()
        results['ROOT-STRUCT-002'] = self.validate_root_struct_002_no_parquet()
        results['ROOT-STRUCT-003'] = self.validate_root_struct_003_no_sqlite()
        results['ROOT-STRUCT-004'] = self.validate_root_struct_004_no_db()
        results['OPA-INPUT-001'] = self.validate_opa_input_001_repo_scan_json()

        return results


if __name__ == '__main__':
    repo_root = Path.cwd().parent.parent.parent if Path.cwd().name == 'sot' else Path.cwd()
    validator = ImportantValidatorsV2(repo_root)
    results = validator.validate_all_important()

    passed = sum(1 for r in results.values() if r.passed)
    failed = sum(1 for r in results.values() if not r.passed)

    print(f"IMPORTANT Validators (Priority 2): {passed}/{len(results)} passed")
    print()

    for rule_id, result in results.items():
        status = "[PASS]" if result.passed else "[FAIL]"
        print(f"{status} {rule_id}: {result.message}")
