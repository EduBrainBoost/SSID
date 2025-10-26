#!/usr/bin/env python3
"""Generate ALL 9 artefacts from existing 4,723 rules (largest dataset)"""

import json
import sys
from pathlib import Path

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

print("Loading 4,723 rules from all_4_sot_semantic_rules.json...")
rules_file = Path('16_codex/structure/level3/all_4_sot_semantic_rules.json')
data = json.loads(rules_file.read_text(encoding='utf-8'))

# Extract rules from data - convert list to dict
if isinstance(data, list):
    existing_rules_list = data
    existing_rules = {f"RULE-{i:04d}": r for i, r in enumerate(existing_rules_list)}
elif 'rules' in data:
    if isinstance(data['rules'], list):
        existing_rules = {f"RULE-{i:04d}": r for i, r in enumerate(data['rules'])}
    else:
        existing_rules = data['rules']
else:
    existing_rules = data

print(f"Loaded {len(existing_rules)} rules")

# Mock rule class
class MockRule:
    def __init__(self, rule_id, rule_data):
        self.rule_id = rule_id
        if isinstance(rule_data, dict):
            self.text = rule_data.get('rule', rule_data.get('description', str(rule_data)[:100]))
            self.context = rule_data.get('section', rule_data.get('category', 'unknown'))
            level = rule_data.get('severity', rule_data.get('priority', 'MUST'))
        else:
            self.text = str(rule_data)[:100]
            self.context = 'unknown'
            level = 'MUST'

        self.source_path = "all_4_sot_semantic_rules.json"
        self.line_number = 0
        self.content_hash = ""
        self.tags = []

        # Priority
        priority_name = level.upper() if isinstance(level, str) else 'MUST'
        self.priority = type('obj', (object,), {'name': priority_name})()
        self.source_type = type('obj', (object,), {'value': 'yaml_block'})()
        self.reality_level = type('obj', (object,), {'value': 'STRUCTURAL'})()

    def get_evidence_count(self):
        return 1

# Convert rules
mock_rules = {}
for rule_id, rule_data in existing_rules.items():
    mock_rules[rule_id] = MockRule(rule_id, rule_data)

print(f"Converted {len(mock_rules)} rules")
print()

# Generate artefacts
root_dir = Path('.')

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

print("[1/3] Core artefacts (contract, policy, validator_core)...")
generated['contract'] = generators['contract'].generate(mock_rules)
generated['policy'] = generators['policy'].generate(mock_rules)
generated['validator_core'] = generators['validator_core'].generate(mock_rules)

print("[2/3] Tool artefacts (CLI, tests)...")
generated['validator_cli'] = generators['validator_cli'].generate(mock_rules)
generated['validator_test'] = generators['validator_test'].generate(mock_rules)

print("[3/3] Audit & automation...")
generated['audit_report'] = generators['audit_report'].generate(mock_rules, {})
generated['registry'] = generators['registry'].generate(mock_rules)
generated['autopilot'] = generators['autopilot'].generate(mock_rules)
generated['diff_alert'] = generators['diff_alert'].generate(mock_rules)

print()
print("="*70)
print("DONE!")
print("="*70)
print(f"Generated {len(generated)} artefacts from {len(mock_rules)} rules")
for name, path in generated.items():
    print(f"  - {name}: {path}")
