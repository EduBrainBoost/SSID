#!/usr/bin/env python3
"""
Compliance Rule Generator
=========================

Automatically generates the 4 mandatory SoT manifestations for compliance rules:
1. Python Module
2. Rego Policy
3. YAML Contract
4. CLI Command

This generator ensures every rule has a scientific basis + technical manifestation.

Usage:
    python generate_compliance_rules.py --config rules_config.yaml

Author: SSID Compliance Team
Version: 1.0.0
Date: 2025-10-17
"""

import sys
import argparse
import yaml
from pathlib import Path
from typing import Dict, List
from datetime import datetime


# Rule definitions for SOC2, Gaia-X, ETSI EN 319 421
RULES_CONFIG = {
    "soc2": [
        {
            "id": "CC2.1",
            "name": "Monitoring Activities",
            "description": "The entity selects, develops, and performs ongoing and/or separate evaluations to ascertain whether the components of internal control are present and functioning.",
            "coso_principle": "Principle 16 - Conducts Ongoing Evaluations",
            "evidence_paths": ["07_governance_legal/monitoring/", "02_audit_logging/monitoring/"],
            "key_requirements": ["Continuous monitoring program", "Management review cycles", "Control self-assessments"]
        },
        {
            "id": "CC3.1",
            "name": "Risk Assessment Process",
            "description": "The entity specifies objectives with sufficient clarity to enable the identification and assessment of risks relating to objectives.",
            "coso_principle": "Principle 6 - Specifies Suitable Objectives",
            "evidence_paths": ["07_governance_legal/risk/", "02_audit_logging/risk_assessments/"],
            "key_requirements": ["Risk assessment methodology", "Risk register", "Risk treatment plans"]
        },
        {
            "id": "CC4.1",
            "name": "Information and Communication",
            "description": "The entity obtains or generates and uses relevant, quality information to support the functioning of internal control.",
            "coso_principle": "Principle 13 - Uses Relevant Information",
            "evidence_paths": ["13_ui_layer/dashboards/", "17_observability/"],
            "key_requirements": ["Information quality controls", "Communication channels", "Reporting mechanisms"]
        },
        {
            "id": "CC5.1",
            "name": "Control Activities",
            "description": "The entity selects and develops control activities that contribute to the mitigation of risks to the achievement of objectives to acceptable levels.",
            "coso_principle": "Principle 10 - Selects and Develops Control Activities",
            "evidence_paths": ["23_compliance/controls/", "03_core/security/"],
            "key_requirements": ["Control design", "Control implementation", "Control testing"]
        },
        {
            "id": "CC6.1",
            "name": "Logical Access Controls",
            "description": "The entity implements logical access security software, infrastructure, and architectures over protected information assets to protect them from security events.",
            "coso_principle": "Principle 11 - Selects and Develops General Controls over Technology",
            "evidence_paths": ["14_zero_time_auth/", "03_core/security/access_control/"],
            "key_requirements": ["Authentication mechanisms", "Authorization controls", "Access reviews"]
        },
        {
            "id": "CC7.1",
            "name": "System Operations",
            "description": "The entity identifies, selects, and develops risk mitigation activities for risks arising from potential disruptions to internal control.",
            "coso_principle": "Principle 17 - Evaluates and Communicates Deficiencies",
            "evidence_paths": ["15_infra/operations/", "17_observability/"],
            "key_requirements": ["Change management", "Incident response", "Business continuity"]
        }
    ],

    "gaia_x": [
        {
            "id": "GAIA-X-01",
            "name": "Data Sovereignty",
            "description": "Ensure data sovereignty through transparent control mechanisms and legal frameworks",
            "framework": "Gaia-X Trust Framework",
            "evidence_paths": ["23_compliance/mappings/gaia_x/data_sovereignty/", "06_data_pipeline/sovereignty/"],
            "key_requirements": ["Data location transparency", "Legal jurisdiction mapping", "Data portability"]
        },
        {
            "id": "GAIA-X-02",
            "name": "Transparency and Trust",
            "description": "Provide verifiable claims about service characteristics and compliance",
            "framework": "Gaia-X Self-Description",
            "evidence_paths": ["10_interoperability/gaia_x/", "23_compliance/self_descriptions/"],
            "key_requirements": ["Self-description format", "Verifiable credentials", "Trust anchors"]
        },
        {
            "id": "GAIA-X-03",
            "name": "Interoperability",
            "description": "Enable seamless service composition and data exchange across federated infrastructure",
            "framework": "Gaia-X Federation Services",
            "evidence_paths": ["10_interoperability/", "18_data_layer/"],
            "key_requirements": ["Standard APIs", "Data formats", "Service discovery"]
        },
        {
            "id": "GAIA-X-04",
            "name": "Portability",
            "description": "Ensure applications and data can move between service providers",
            "framework": "Gaia-X Portability & Interoperability",
            "evidence_paths": ["06_data_pipeline/portability/", "18_data_layer/export/"],
            "key_requirements": ["Data export capabilities", "Application containerization", "Minimal lock-in"]
        },
        {
            "id": "GAIA-X-05",
            "name": "Security by Design",
            "description": "Implement security controls aligned with European regulatory requirements",
            "framework": "Gaia-X Security Framework",
            "evidence_paths": ["03_core/security/", "21_post_quantum_crypto/"],
            "key_requirements": ["Encryption standards", "Access controls", "Audit logging"]
        },
        {
            "id": "GAIA-X-06",
            "name": "Federated Services",
            "description": "Support participation in federated service ecosystems with clear governance",
            "framework": "Gaia-X Federation",
            "evidence_paths": ["10_interoperability/federation/", "24_meta_orchestration/federation/"],
            "key_requirements": ["Federation agreements", "Service catalogs", "Compliance validation"]
        }
    ],

    "etsi_en_319_421": [
        {
            "id": "ETSI-421-01",
            "name": "Certificate Policy Requirements",
            "description": "Establish and maintain certificate policies compliant with eIDAS requirements",
            "framework": "ETSI EN 319 421 - Policy Requirements for Trust Service Providers",
            "evidence_paths": ["21_post_quantum_crypto/policies/", "03_core/security/pki/"],
            "key_requirements": ["Certificate policy document", "Certificate practice statement", "Policy approval"]
        },
        {
            "id": "ETSI-421-02",
            "name": "Certificate Lifecycle Management",
            "description": "Implement secure certificate issuance, renewal, and revocation processes",
            "framework": "ETSI EN 319 421",
            "evidence_paths": ["03_core/security/pki/lifecycle/", "02_audit_logging/pki/"],
            "key_requirements": ["Issuance procedures", "Revocation checking", "CRL/OCSP services"]
        },
        {
            "id": "ETSI-421-03",
            "name": "Qualified Trust Service Provider Requirements",
            "description": "Meet QTSP requirements for organizational and technical controls",
            "framework": "eIDAS Regulation + ETSI EN 319 421",
            "evidence_paths": ["23_compliance/eidas/", "07_governance_legal/qtsp/"],
            "key_requirements": ["QTSP status evidence", "Supervisory body notifications", "Annual audits"]
        },
        {
            "id": "ETSI-421-04",
            "name": "Cryptographic Controls",
            "description": "Implement cryptographic controls meeting ETSI and eIDAS standards",
            "framework": "ETSI EN 319 421 + SOGIS Agreed Cryptographic Mechanisms",
            "evidence_paths": ["21_post_quantum_crypto/", "03_core/security/crypto/"],
            "key_requirements": ["Approved algorithms", "Key management", "HSM usage"]
        },
        {
            "id": "ETSI-421-05",
            "name": "Time-Stamping Services",
            "description": "Provide trusted time-stamping compliant with ETSI EN 319 422",
            "framework": "ETSI EN 319 421 (cross-ref 319 422)",
            "evidence_paths": ["02_audit_logging/timestamping/", "10_interoperability/rfc3161/"],
            "key_requirements": ["TSA operations", "Time source accuracy", "Timestamp validation"]
        },
        {
            "id": "ETSI-421-06",
            "name": "Trust Service Status List",
            "description": "Maintain and publish trust service status lists per ETSI EN 319 412",
            "framework": "ETSI EN 319 421 + 319 412 (TSL)",
            "evidence_paths": ["10_interoperability/tsl/", "23_compliance/eidas/tsl/"],
            "key_requirements": ["TSL publication", "TSL signing", "TSL updates"]
        }
    ]
}


def generate_python_module(rule: Dict, standard: str, output_dir: Path):
    """Generate Python validation module"""
    rule_id_safe = rule["id"].replace(".", "_").replace("-", "_").lower()
    module_name = f"{rule_id_safe}_{rule['name'].replace(' ', '_').replace('&', 'and').lower()}.py"

    content = f'''#!/usr/bin/env python3
"""
{standard.upper()} {rule["id"]} - {rule["name"]}
{'='*80}

Scientific Basis:
-----------------
{rule.get("framework", rule.get("coso_principle", "Industry Standard"))}

Description:
{rule["description"]}

Technical Manifestation:
------------------------
Validates compliance with {rule["id"]} requirements through automated checks

Evidence Paths:
{chr(10).join(f"- {path}" for path in rule["evidence_paths"])}

Key Requirements:
{chr(10).join(f"- {req}" for req in rule["key_requirements"])}

Author: SSID Compliance Team
Version: 1.0.0
Date: {datetime.now().strftime("%Y-%m-%d")}
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class {rule_id_safe.upper()}Validator:
    """
    Validates {standard.upper()} {rule["id"]} - {rule["name"]}
    """

    EVIDENCE_PATHS = {chr(123)}
        {', '.join(f'"{path.split("/")[-2] if "/" in path else "evidence"}": "{path}"' for path in rule["evidence_paths"])}
    {chr(125)}

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize validator"""
        self.repo_root = repo_root or Path.cwd()
        self.findings: List[Dict] = []
        self.is_compliant = False

    def validate(self) -> Tuple[bool, List[Dict]]:
        """Execute validation"""
        self.findings = []

        # Validate evidence paths exist
        all_valid = self._validate_evidence_paths()

        self.is_compliant = all_valid
        return self.is_compliant, self.findings

    def _validate_evidence_paths(self) -> bool:
        """Validate required evidence paths exist"""
        all_valid = True

        for evidence_type, path in self.EVIDENCE_PATHS.items():
            full_path = self.repo_root / path

            if not full_path.exists():
                self.findings.append({chr(123)}
                    "rule": "{rule["id"]}",
                    "severity": "HIGH",
                    "finding": f"Missing evidence path: {chr(123)}evidence_type{chr(125)}",
                    "path": path,
                    "remediation": f"Create evidence directory at {chr(123)}path{chr(125)}"
                {chr(125)})
                all_valid = False
            else:
                self.findings.append({chr(123)}
                    "rule": "{rule["id"]}",
                    "severity": "INFO",
                    "finding": f"Evidence path exists: {chr(123)}evidence_type{chr(125)}",
                    "path": path,
                    "status": "PASS"
                {chr(125)})

        return all_valid

    def generate_evidence_hash(self) -> str:
        """Generate evidence hash for audit trail"""
        evidence_data = {chr(123)}
            "timestamp": datetime.now().isoformat(),
            "rule": "{standard.upper()}_{rule["id"]}",
            "findings": self.findings,
            "is_compliant": self.is_compliant
        {chr(125)}

        evidence_json = json.dumps(evidence_data, sort_keys=True)
        return hashlib.sha256(evidence_json.encode()).hexdigest()


def cli_check() -> int:
    """CLI entry point"""
    validator = {rule_id_safe.upper()}Validator()
    is_compliant, findings = validator.validate()

    print(f"\\n{'='*80}")
    print(f"{standard.upper()} {rule["id"]} - {rule["name"]} Validation")
    print(f"{'='*80}\\n")

    for finding in findings:
        severity = finding.get("severity", "INFO")
        icon = "✓" if finding.get("status") == "PASS" else "✗"
        print(f"{chr(123)}icon{chr(125)} [{chr(123)}severity{chr(125)}] {chr(123)}finding.get('finding'){chr(125)}")
        print()

    print(f"{'='*80}")
    print(f"Compliance: {'PASS' if is_compliant else 'FAIL'}")
    print(f"Evidence Hash: {chr(123)}validator.generate_evidence_hash(){chr(125)}")
    print(f"{'='*80}\\n")

    return 0 if is_compliant else 1


if __name__ == "__main__":
    exit(cli_check())
'''

    output_path = output_dir / module_name
    output_path.write_text(content, encoding='utf-8')
    print(f"✓ Generated Python module: {output_path}")


def generate_rego_policy(rule: Dict, standard: str, output_dir: Path):
    """Generate OPA Rego policy"""
    rule_id_safe = rule["id"].replace(".", "_").replace("-", "_").lower()
    policy_name = f"{standard}_{rule_id_safe}.rego"

    content = f'''# {standard.upper()} {rule["id"]} - {rule["name"]}
# {'='*80}
#
# Scientific Basis:
# {rule.get("framework", rule.get("coso_principle", "Industry Standard"))}
#
# Description:
# {rule["description"]}
#
# Enforcement: Evidence paths must exist
#
# Author: SSID Compliance Team
# Version: 1.0.0
# Date: {datetime.now().strftime("%Y-%m-%d")}

package ssid.compliance.{standard}.{rule_id_safe}

import future.keywords.if

default allow = false

evidence_paths := [{", ".join(f'"{path}"' for path in rule["evidence_paths"])}]

# All evidence paths must exist
allow if {{
    input.file_system
    count(missing_paths) == 0
}}

missing_paths[path] {{
    some path in evidence_paths
    not path_exists(path)
}}

path_exists(path) if {{
    some entry in input.file_system.paths
    entry.path == path
    entry.exists == true
}}

violations[violation] {{
    some path in missing_paths
    violation := {{
        "rule": "{rule["id"]}",
        "severity": "HIGH",
        "finding": sprintf("Missing evidence path: %s", [path]),
        "remediation": sprintf("Create evidence directory: %s", [path])
    }}
}}
'''

    output_path = output_dir / policy_name
    output_path.write_text(content, encoding='utf-8')
    print(f"✓ Generated Rego policy: {output_path}")


def generate_yaml_contract(rule: Dict, standard: str, output_dir: Path):
    """Generate YAML contract"""
    rule_id_safe = rule["id"].replace(".", "_").replace("-", "_").lower()
    contract_name = f"{rule_id_safe}.yaml"

    content = f'''# {standard.upper()} {rule["id"]} - {rule["name"]} Contract
# {'='*80}
#
# Scientific Basis: {rule.get("framework", rule.get("coso_principle"))}
# Description: {rule["description"]}
#
# Author: SSID Compliance Team
# Version: 1.0.0
# Date: {datetime.now().strftime("%Y-%m-%d")}

version: "1.0.0"
contract_id: "{standard.upper()}_{rule["id"]}"
contract_name: "{rule["name"]}"
standard: "{standard.upper()}"
effective_date: "{datetime.now().strftime("%Y-%m-%d")}"
review_cycle: "annual"
classification: "CONFIDENTIAL"

scientific_basis:
  framework: "{rule.get("framework", rule.get("coso_principle"))}"
  description: |
    {rule["description"]}

compliance_requirements:
{chr(10).join(f'''  - requirement_id: "{rule["id"]}-R{i+1}"
    description: "{req}"
    evidence_required: true''' for i, req in enumerate(rule["key_requirements"]))}

evidence_paths:
{chr(10).join(f'  - "{path}"' for path in rule["evidence_paths"])}

enforcement:
  python_module: "23_compliance/mappings/{standard}/src/{rule_id_safe}_{rule["name"].replace(" ", "_").lower()}.py"
  rego_policy: "23_compliance/policies/{standard}_{rule_id_safe}.rego"
  cli_command: "python 12_tooling/scripts/compliance/check_{standard}_{rule_id_safe}.py"
  ci_gate_enabled: true

validation_schedule:
  ci_pipeline: true
  nightly_scan: true
  monthly_audit: true

metadata:
  created_by: "SSID Compliance Team"
  created_date: "{datetime.now().strftime("%Y-%m-%d")}"
  tags:
    - "{standard}"
    - "{rule["id"].lower()}"
'''

    output_path = output_dir / contract_name
    output_path.write_text(content, encoding='utf-8')
    print(f"✓ Generated YAML contract: {output_path}")


def generate_cli_command(rule: Dict, standard: str, output_dir: Path):
    """Generate CLI command wrapper"""
    rule_id_safe = rule["id"].replace(".", "_").replace("-", "_").lower()
    cli_name = f"check_{standard}_{rule_id_safe}.py"

    content = f'''#!/usr/bin/env python3
"""
CLI Command: check_{standard}_{rule_id_safe}
{'='*80}

{standard.upper()} {rule["id"]} - {rule["name"]} Compliance Check

Usage:
    python check_{standard}_{rule_id_safe}.py [--json] [--verbose]

Author: SSID Compliance Team
Version: 1.0.0
Date: {datetime.now().strftime("%Y-%m-%d")}
"""

import sys
import argparse
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "23_compliance" / "mappings" / "{standard}" / "src"))

from {rule_id_safe}_{rule["name"].replace(" ", "_").replace("&", "and").lower()} import {rule_id_safe.upper()}Validator


def main():
    parser = argparse.ArgumentParser(description="{standard.upper()} {rule["id"]} Compliance Check")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    validator = {rule_id_safe.upper()}Validator()
    is_compliant, findings = validator.validate()

    if args.json:
        print(json.dumps({{
            "rule": "{rule["id"]}",
            "is_compliant": is_compliant,
            "findings": findings,
            "evidence_hash": validator.generate_evidence_hash()
        }}, indent=2))
    else:
        print(f"\\n{standard.upper()} {rule["id"]} - {rule["name"]}")
        print(f"{'='*80}")
        for f in findings:
            icon = "✓" if f.get("status") == "PASS" else "✗"
            print(f"{chr(123)}icon{chr(125)} {chr(123)}f['finding']{chr(125)}")
        print(f"\\nCompliance: {'PASS' if is_compliant else 'FAIL'}")

    return 0 if is_compliant else 1


if __name__ == "__main__":
    sys.exit(main())
'''

    output_path = output_dir / cli_name
    output_path.write_text(content, encoding='utf-8')
    output_path.chmod(0o755)
    print(f"✓ Generated CLI command: {output_path}")


def main():
    """Main generator"""
    parser = argparse.ArgumentParser(description="Generate compliance rule manifestations")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--standards", nargs="+", choices=["soc2", "gaia_x", "etsi_en_319_421", "all"],
                        default=["all"], help="Standards to generate")
    args = parser.parse_args()

    repo_root = args.repo_root
    standards = ["soc2", "gaia_x", "etsi_en_319_421"] if "all" in args.standards else args.standards

    print(f"\n{'='*80}")
    print("Compliance Rule Generator - SoT Manifestation Creator")
    print(f"{'='*80}\n")

    total_generated = 0

    for standard in standards:
        print(f"\n[{standard.upper()}] Generating rules...")
        rules = RULES_CONFIG[standard]

        # Create directories
        python_dir = repo_root / "23_compliance" / "mappings" / standard / "src"
        rego_dir = repo_root / "23_compliance" / "policies"
        yaml_dir = repo_root / "16_codex" / "contracts" / standard
        cli_dir = repo_root / "12_tooling" / "scripts" / "compliance"

        for d in [python_dir, rego_dir, yaml_dir, cli_dir]:
            d.mkdir(parents=True, exist_ok=True)

        # Generate manifestations for each rule
        for rule in rules:
            print(f"\n  Generating {rule['id']} - {rule['name']}...")
            generate_python_module(rule, standard, python_dir)
            generate_rego_policy(rule, standard, rego_dir)
            generate_yaml_contract(rule, standard, yaml_dir)
            generate_cli_command(rule, standard, cli_dir)
            total_generated += 4  # 4 manifestations per rule

    print(f"\n{'='*80}")
    print(f"✓ Generated {total_generated} manifestation files")
    print(f"{'='*80}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
