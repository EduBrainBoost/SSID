#!/usr/bin/env python3
"""
SSID Policy-as-Code Exporter
Convert compliance_unified_index.yaml to OPA Rego format

Exports YAML compliance policies as executable Rego code for Open Policy Agent,
enabling external systems to enforce the same compliance rules.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class OPARegoExporter:
    """
    Export SSID compliance policies to OPA Rego format

    Converts YAML-based compliance definitions into executable
    Rego policies that can be deployed to OPA servers.
    """

    def __init__(self, unified_index_path: Path):
        self.unified_index_path = Path(unified_index_path)
        self.unified_index = self._load_unified_index()

    def _load_unified_index(self) -> Dict:
        """Load compliance unified index from YAML"""
        with open(self.unified_index_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def export_full_policy(self, output_path: Path) -> bool:
        """
        Export complete compliance policy as Rego

        Creates a comprehensive OPA policy that can enforce
        all compliance rules from the unified index.
        """
        rego_content = self._generate_rego_policy()

        output_path.write_text(rego_content, encoding='utf-8')
        print(f"[OPA Export] OK Exported full policy to {output_path}")

        # Also export test data
        test_data = self._generate_test_data()
        test_path = output_path.parent / f"{output_path.stem}_test.json"
        test_path.write_text(json.dumps(test_data, indent=2), encoding='utf-8')
        print(f"[OPA Export] OK Exported test data to {test_path}")

        return True

    def _generate_rego_policy(self) -> str:
        """Generate complete Rego policy from unified index"""

        header = self._generate_header()
        control_categories = self._generate_control_categories()
        risk_classifications = self._generate_risk_classifications()
        verification_methods = self._generate_verification_methods()
        compliance_rules = self._generate_compliance_rules()
        helper_functions = self._generate_helper_functions()
        audit_decisions = self._generate_audit_decisions()

        return "\n\n".join([
            header,
            control_categories,
            risk_classifications,
            verification_methods,
            compliance_rules,
            helper_functions,
            audit_decisions
        ])

    def _generate_header(self) -> str:
        """Generate Rego policy header"""
        meta = self.unified_index.get("meta", {})

        return f'''# SSID Compliance Policy - OPA Rego Export
# Generated from: {self.unified_index_path.name}
# Framework: {meta.get('framework', 'UNIFIED')}
# Version: {meta.get('version', 'unknown')}
# Generated: {datetime.now().isoformat()}
# Maintainer: {meta.get('maintainer', 'unknown')}
#
# This policy enforces SSID compliance rules across GDPR, DORA, MiCA, and AMLD6.
# Deploy to Open Policy Agent for external system enforcement.

package ssid.compliance

import future.keywords.if
import future.keywords.in
import future.keywords.contains'''

    def _generate_control_categories(self) -> str:
        """Generate control category definitions"""
        categories = self.unified_index.get("ontology", {}).get("control_categories", [])

        rego = '''# =============================================================================
# Control Categories
# =============================================================================

control_categories := {'''

        for cat in categories:
            rego += f'''
    "{cat['id']}": {{
        "name": "{cat['name']}",
        "description": "{cat['description']}",
        "frameworks": {json.dumps(cat['frameworks'])},
        "risk_domain": "{cat['risk_domain']}"
    }},'''

        rego = rego.rstrip(',') + '\n}'

        # Helper rule
        rego += '''

# Check if a control belongs to a category
control_in_category(control_id, category_id) if {
    category := control_categories[category_id]
    control_id
    category
}'''

        return rego

    def _generate_risk_classifications(self) -> str:
        """Generate risk classification rules"""
        risks = self.unified_index.get("ontology", {}).get("risk_classifications", [])

        rego = '''# =============================================================================
# Risk Classifications
# =============================================================================

risk_levels := {'''

        for risk in risks:
            rego += f'''
    "{risk['level']}": {{
        "severity_score": {risk['severity_score']},
        "description": "{risk['description']}",
        "remediation_sla": "{risk['remediation_sla']}",
        "escalation": "{risk['escalation']}"
    }},'''

        rego = rego.rstrip(',') + '\n}'

        # Risk scoring rule
        rego += '''

# Get severity score for risk level
risk_severity(level) := score if {
    risk := risk_levels[level]
    score := risk.severity_score
}

# Check if risk level requires immediate action
requires_immediate_action(level) if {
    risk_severity(level) >= 4
}'''

        return rego

    def _generate_verification_methods(self) -> str:
        """Generate verification method definitions"""
        methods = self.unified_index.get("ontology", {}).get("verification_methods", [])

        rego = '''# =============================================================================
# Verification Methods
# =============================================================================

verification_methods := {'''

        for method in methods:
            rego += f'''
    "{method['method']}": {{
        "description": "{method['description']}",
        "frequency": "{method['frequency']}",
        "tools": {json.dumps(method['tools'])},
        "confidence_level": "{method['confidence_level']}"
    }},'''

        rego = rego.rstrip(',') + '\n}'

        # Verification confidence rule
        rego += '''

# Check if verification method provides high confidence
high_confidence_verification(method) if {
    verification := verification_methods[method]
    verification.confidence_level in ["high", "very-high"]
}'''

        return rego

    def _generate_compliance_rules(self) -> str:
        """Generate compliance validation rules"""
        mappings = self.unified_index.get("cross_framework_mappings", {})

        rego = '''# =============================================================================
# Compliance Rules
# =============================================================================

# All compliance controls indexed by unified ID
compliance_controls := {'''

        # Process each domain's mappings
        for domain_name, controls in mappings.items():
            if isinstance(controls, list):
                for control in controls:
                    rego += f'''
    "{control['unified_id']}": {{
        "category": "{control['category']}",
        "description": "{control['description']}",
        "risk_level": "{control['risk_level']}",
        "frameworks": {json.dumps([m['framework'] for m in control['mappings']])},
        "ssid_modules": {json.dumps(control['ssid_modules'])},
        "verification": "{control['verification']}",
        "implementation_status": "{control['implementation_status']}"
    }},'''

        rego = rego.rstrip(',') + '\n}'

        # Compliance validation rules
        rego += '''

# Check if a control is implemented
control_implemented(control_id) if {
    control := compliance_controls[control_id]
    control.implementation_status == "implemented"
}

# Check if a control is high priority
control_high_priority(control_id) if {
    control := compliance_controls[control_id]
    control.risk_level in ["CRITICAL", "HIGH"]
}

# Get all controls for a specific framework
framework_controls(framework) := controls if {
    controls := [control_id |
        control := compliance_controls[control_id]
        framework in control.frameworks
    ]
}

# Get all controls affecting a specific SSID module
module_controls(module) := controls if {
    controls := [control_id |
        control := compliance_controls[control_id]
        module in control.ssid_modules
    ]
}

# Check if all critical controls are implemented
all_critical_controls_implemented if {
    critical := [c |
        control := compliance_controls[c]
        control.risk_level == "CRITICAL"
    ]
    implemented := [c |
        control := compliance_controls[c]
        control.risk_level == "CRITICAL"
        control.implementation_status == "implemented"
    ]
    count(critical) == count(implemented)
}'''

        return rego

    def _generate_helper_functions(self) -> str:
        """Generate helper functions"""
        metrics = self.unified_index.get("compliance_metrics_unified", {})

        return f'''# =============================================================================
# Helper Functions
# =============================================================================

# Calculate overall compliance score
compliance_score(framework) := score if {{
    coverage := {json.dumps(metrics.get('overall_coverage', {}))}
    score_str := coverage[framework]
    score := to_number(trim_suffix(score_str, "%"))
}}

# Check if framework meets minimum compliance threshold
meets_compliance_threshold(framework, threshold) if {{
    score := compliance_score(framework)
    score >= threshold
}}

# Get all non-compliant controls
non_compliant_controls := controls if {{
    controls := [control_id |
        control := compliance_controls[control_id]
        control.implementation_status != "implemented"
        control_high_priority(control_id)
    ]
}}

# Count controls by risk level
controls_by_risk_level(level) := count if {{
    controls := [c |
        control := compliance_controls[c]
        control.risk_level == level
    ]
    count := count(controls)
}}

# Get remediation SLA for control
remediation_sla(control_id) := sla if {{
    control := compliance_controls[control_id]
    risk := risk_levels[control.risk_level]
    sla := risk.remediation_sla
}}'''

    def _generate_audit_decisions(self) -> str:
        """Generate audit decision rules"""
        return '''# =============================================================================
# Audit Decisions
# =============================================================================

# Main compliance decision
default allow := false

# Allow if all critical controls implemented
allow if {
    all_critical_controls_implemented
    count(non_compliant_controls) == 0
}

# Deny with reasons
deny[msg] if {
    not all_critical_controls_implemented
    msg := "Critical controls not fully implemented"
}

deny[msg] if {
    count(non_compliant_controls) > 0
    msg := sprintf("Non-compliant high-priority controls: %d", [count(non_compliant_controls)])
}

deny[msg] if {
    not meets_compliance_threshold("gdpr", 90)
    msg := "GDPR compliance below 90% threshold"
}

deny[msg] if {
    not meets_compliance_threshold("dora", 90)
    msg := "DORA compliance below 90% threshold"
}

# Audit report generation
audit_report := report if {
    report := {
        "timestamp": time.now_ns(),
        "compliance_status": {
            "gdpr": compliance_score("gdpr"),
            "dora": compliance_score("dora"),
            "mica": compliance_score("mica"),
            "amld6": compliance_score("amld6")
        },
        "critical_controls": {
            "total": controls_by_risk_level("CRITICAL"),
            "implemented": count([c |
                control := compliance_controls[c]
                control.risk_level == "CRITICAL"
                control_implemented(c)
            ])
        },
        "high_priority_gaps": non_compliant_controls,
        "overall_decision": allow
    }
}

# Risk assessment
risk_assessment := assessment if {
    critical_gaps := controls_by_risk_level("CRITICAL") - count([c |
        control := compliance_controls[c]
        control.risk_level == "CRITICAL"
        control_implemented(c)
    ])

    high_gaps := controls_by_risk_level("HIGH") - count([c |
        control := compliance_controls[c]
        control.risk_level == "HIGH"
        control_implemented(c)
    ])

    assessment := {
        "overall_risk": risk_level_assessment(critical_gaps, high_gaps),
        "critical_gaps": critical_gaps,
        "high_priority_gaps": high_gaps,
        "requires_action": critical_gaps > 0 or high_gaps > 3
    }
}

risk_level_assessment(critical, high) := "CRITICAL" if {
    critical > 0
}

risk_level_assessment(critical, high) := "HIGH" if {
    critical == 0
    high > 3
}

risk_level_assessment(critical, high) := "MEDIUM" if {
    critical == 0
    high > 0
    high <= 3
}

risk_level_assessment(critical, high) := "LOW" if {
    critical == 0
    high == 0
}'''

    def _generate_test_data(self) -> Dict:
        """Generate test data for Rego policy"""
        return {
            "test_scenarios": [
                {
                    "name": "Full compliance",
                    "input": {
                        "all_controls_implemented": True,
                        "framework_scores": {
                            "gdpr": 95,
                            "dora": 92,
                            "mica": 88,
                            "amld6": 94
                        }
                    },
                    "expected": {
                        "allow": True,
                        "deny": []
                    }
                },
                {
                    "name": "Critical control missing",
                    "input": {
                        "all_controls_implemented": False,
                        "critical_gaps": 1,
                        "framework_scores": {
                            "gdpr": 95,
                            "dora": 92,
                            "mica": 88,
                            "amld6": 94
                        }
                    },
                    "expected": {
                        "allow": False,
                        "deny": ["Critical controls not fully implemented"]
                    }
                },
                {
                    "name": "GDPR below threshold",
                    "input": {
                        "all_controls_implemented": True,
                        "framework_scores": {
                            "gdpr": 85,
                            "dora": 92,
                            "mica": 88,
                            "amld6": 94
                        }
                    },
                    "expected": {
                        "allow": False,
                        "deny": ["GDPR compliance below 90% threshold"]
                    }
                }
            ],
            "sample_queries": [
                "data.ssid.compliance.allow",
                "data.ssid.compliance.audit_report",
                "data.ssid.compliance.risk_assessment",
                "data.ssid.compliance.framework_controls(\"GDPR\")",
                "data.ssid.compliance.module_controls(\"09_meta_identity\")",
                "data.ssid.compliance.non_compliant_controls"
            ]
        }

    def export_module_policies(self, output_dir: Path) -> bool:
        """
        Export per-module compliance policies

        Creates individual Rego policies for each SSID module
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Collect all modules
        modules = set()
        mappings = self.unified_index.get("cross_framework_mappings", {})
        for domain_name, controls in mappings.items():
            if isinstance(controls, list):
                for control in controls:
                    modules.update(control.get('ssid_modules', []))

        # Generate policy for each module
        for module in sorted(modules):
            policy = self._generate_module_policy(module)
            module_path = output_dir / f"{module}.rego"
            module_path.write_text(policy, encoding='utf-8')
            print(f"[OPA Export] OK Exported module policy: {module}")

        return True

    def _generate_module_policy(self, module: str) -> str:
        """Generate Rego policy for specific module"""
        mappings = self.unified_index.get("cross_framework_mappings", {})

        # Find controls affecting this module
        module_controls = []
        for domain_name, controls in mappings.items():
            if isinstance(controls, list):
                for control in controls:
                    if module in control.get('ssid_modules', []):
                        module_controls.append(control)

        rego = f'''# SSID Module Compliance Policy: {module}
# Generated: {datetime.now().isoformat()}

package ssid.modules.{module.replace('-', '_')}

import future.keywords.if

# Controls affecting this module
module_controls := {{'''

        for control in module_controls:
            rego += f'''
    "{control['unified_id']}": {{
        "category": "{control['category']}",
        "description": "{control['description']}",
        "risk_level": "{control['risk_level']}",
        "implementation_status": "{control['implementation_status']}"
    }},'''

        rego = rego.rstrip(',') + '\n}'

        rego += f'''

# Module compliance check
module_compliant if {{
    implemented := [c |
        control := module_controls[c]
        control.implementation_status == "implemented"
    ]
    count(implemented) == count(module_controls)
}}

# Critical gaps
critical_gaps := gaps if {{
    gaps := [control_id |
        control := module_controls[control_id]
        control.risk_level == "CRITICAL"
        control.implementation_status != "implemented"
    ]
}}

# Module risk level
module_risk := "CRITICAL" if {{
    count(critical_gaps) > 0
}}

module_risk := "OK" if {{
    count(critical_gaps) == 0
}}'''

        return rego


def main():
    """Main CLI entry point"""
    print("=== SSID Policy-as-Code OPA Exporter ===\n")

    # Paths
    unified_index_path = Path("C:/Users/bibel/Documents/Github/SSID/23_compliance/mappings/compliance_unified_index.yaml")
    output_dir = Path("C:/Users/bibel/Documents/Github/SSID/23_compliance/policy_as_code/rego_policies")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize exporter
    exporter = OPARegoExporter(unified_index_path)

    # Export full policy
    print("1. Exporting full compliance policy...")
    full_policy_path = output_dir / "ssid_compliance_policy.rego"
    exporter.export_full_policy(full_policy_path)

    # Export module policies
    print("\n2. Exporting per-module policies...")
    module_dir = output_dir / "modules"
    exporter.export_module_policies(module_dir)

    # Generate deployment guide
    print("\n3. Generating deployment guide...")
    guide = f"""# OPA Policy Deployment Guide

## Files Generated

- `ssid_compliance_policy.rego` - Main compliance policy
- `ssid_compliance_policy_test.json` - Test data and sample queries
- `modules/*.rego` - Per-module policies

## Deployment

### 1. Start OPA Server

```bash
opa run --server --addr :8181
```

### 2. Load Policy

```bash
curl -X PUT http://localhost:8181/v1/policies/ssid-compliance \\
  --data-binary @ssid_compliance_policy.rego
```

### 3. Query Examples

**Check overall compliance:**
```bash
curl -X POST http://localhost:8181/v1/data/ssid/compliance/allow
```

**Get audit report:**
```bash
curl -X POST http://localhost:8181/v1/data/ssid/compliance/audit_report
```

**Get risk assessment:**
```bash
curl -X POST http://localhost:8181/v1/data/ssid/compliance/risk_assessment
```

**Query framework controls:**
```bash
curl -X POST http://localhost:8181/v1/data/ssid/compliance/framework_controls \\
  -d '{{"input": {{"framework": "gdpr"}}}}'
```

**Query module controls:**
```bash
curl -X POST http://localhost:8181/v1/data/ssid/compliance/module_controls \\
  -d '{{"input": {{"module": "09_meta_identity"}}}}'
```

## Testing

```bash
opa test ssid_compliance_policy.rego ssid_compliance_policy_test.json
```

## Integration

Integrate with external systems via OPA's REST API or SDKs:
- Python: https://github.com/open-policy-agent/opa-python
- Go: https://github.com/open-policy-agent/opa/tree/main/rego
- Java: https://github.com/Bisnode/opa-java-client

Generated: {datetime.now().isoformat()}
"""

    guide_path = output_dir / "DEPLOYMENT.md"
    guide_path.write_text(guide, encoding='utf-8')
    print(f"   OK Deployment guide: {guide_path}")

    print("\n=== Export Complete ===")
    print(f"\nPolicies exported to: {output_dir}")
    print(f"Deploy to OPA with: opa run --server {output_dir}")


if __name__ == "__main__":
    main()
