#!/usr/bin/env python3
"""
Generate all 9 SoT artefacts from existing 6,004 extracted rules
================================================================
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add generators to path
sys.path.insert(0, str(Path('03_core/validators/sot')))

from artefact_generators import (
    SotContractYamlGenerator,
    SotPolicyRegoGenerator,
    SotValidatorCorePyGenerator,
    SotValidatorCliGenerator,
    SotValidatorTestGenerator,
    SotAuditReportGenerator,
    SotRegistryJsonGenerator,
    SotAutopilotYmlGenerator,
    SotDiffAlertJsonGenerator
)

# Load existing rules
print("Loading existing 6,004 rules...")
rules_file = Path('12_tooling/scripts/sot_rules_parsed_extended.json')
data = json.loads(rules_file.read_text(encoding='utf-8'))

existing_rules = data['rules']
print(f"✓ Loaded {len(existing_rules)} rules")
print()

# Convert to compatible format for generators
# The generators expect ExtractedRule objects, but we'll use dicts
class MockRule:
    def __init__(self, rule_data):
        self.rule_id = rule_data['rule_id']
        self.text = f"{rule_data['category']}: {rule_data['function']}"
        self.source_path = "sot_validator_core.py"
        self.line_number = 0
        self.context = rule_data['category']
        self.content_hash = ""
        self.tags = [rule_data['level']]

        # Mock priority based on level
        if rule_data['level'] == 'EBENE_2':
            self.priority = type('obj', (object,), {'name': 'MUST'})()
        else:
            self.priority = type('obj', (object,), {'name': 'SHOULD'})()

        self.source_type = type('obj', (object,), {'value': 'yaml_block'})()
        self.reality_level = type('obj', (object,), {'value': 'STRUCTURAL'})()

    def get_evidence_count(self):
        return 1

# Convert to mock rules
mock_rules = {}
for rule_id, rule_data in existing_rules.items():
    mock_rules[rule_id] = MockRule(rule_data)

print(f"Converted {len(mock_rules)} rules to generator format")
print()

# Initialize generators
root_dir = Path('.')

print("=" * 70)
print("GENERATING ALL 9 ARTEFACTS FROM 6,004 EXISTING RULES")
print("=" * 70)
print()

generators = {
    'contract': SotContractYamlGenerator(root_dir),
    'policy': SotPolicyRegoGenerator(root_dir),
    'validator_core': SotValidatorCorePyGenerator(root_dir),
    'validator_cli': SotValidatorCliGenerator(root_dir),
    'validator_test': SotValidatorTestGenerator(root_dir),
    'audit_report': SotAuditReportGenerator(root_dir),
    'registry': SotRegistryJsonGenerator(root_dir),
    'autopilot': SotAutopilotYmlGenerator(root_dir),
    'diff_alert': SotDiffAlertJsonGenerator(root_dir)
}

generated = {}

# Generate all artefacts
print("[1/3] Core artefacts...")
generated['contract'] = generators['contract'].generate(mock_rules)
generated['policy'] = generators['policy'].generate(mock_rules)
generated['validator_core'] = generators['validator_core'].generate(mock_rules)
print()

print("[2/3] Tool artefacts...")
generated['validator_cli'] = generators['validator_cli'].generate(mock_rules)
generated['validator_test'] = generators['validator_test'].generate(mock_rules)
print()

print("[3/3] Audit & automation artefacts...")
stats = data.get('summary', {})
generated['audit_report'] = generators['audit_report'].generate(mock_rules, stats)
generated['registry'] = generators['registry'].generate(mock_rules)
generated['autopilot'] = generators['autopilot'].generate(mock_rules)
generated['diff_alert'] = generators['diff_alert'].generate(mock_rules)
print()

print("=" * 70)
print("GENERATION COMPLETE!")
print("=" * 70)
print(f"Total artefacts generated: {len(generated)}")
print()
for name, path in generated.items():
    print(f"  ✓ {name}: {path}")
print()
