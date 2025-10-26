#!/usr/bin/env python3
"""Quick completeness scorer"""
import json
import re
from pathlib import Path

print('='*80)
print('SoT Completeness Scoring')
print('='*80)

# Load registry
print('\n[1/6] Loading registry...')
with open('16_codex/structure/auto_generated/sot_rules_full.json') as f:
    data = json.load(f)

all_rules = data.get('rules', [])
all_rule_ids = set()
for rule in all_rules:
    rid = rule.get('rule_id') or rule.get('id')
    if rid:
        all_rule_ids.add(rid)

print(f'  Total rules in registry: {len(all_rule_ids)}')

# Scan Contract
print('\n[2/6] Scanning Contract...')
contract_rules = set()
try:
    with open('16_codex/contracts/sot/sot_contract.yaml') as f:
        content = f.read()
    patterns = [r'id:\s*[\"\']?([A-Za-z0-9_\-.]+)[\"\']?', r'rule_id:\s*[\"\']?([A-Za-z0-9_\-.]+)[\"\']?']
    for p in patterns:
        contract_rules.update(re.findall(p, content))
except Exception as e:
    print(f'  Error: {e}')
print(f'  Rules found: {len(contract_rules)}')

# Scan Policy
print('\n[3/6] Scanning Policy...')
policy_rules = set()
try:
    for rego_file in Path('23_compliance/policies/sot').glob('*.rego'):
        with open(rego_file) as f:
            content = f.read()
        patterns = [r'# Rule:\s*([A-Za-z0-9_\-.]+)', r'rule_id[\"\']?\s*[:=]\s*[\"\']?([A-Za-z0-9_\-.]+)[\"\']?']
        for p in patterns:
            policy_rules.update(re.findall(p, content))
except Exception as e:
    print(f'  Error: {e}')
print(f'  Rules found: {len(policy_rules)}')

# Scan Validator
print('\n[4/6] Scanning Validator...')
validator_rules = set()
try:
    for py_file in Path('03_core/validators/sot').glob('*.py'):
        with open(py_file) as f:
            content = f.read()
        patterns = [r'def\s+validate_([a-z0-9_]+)\(', r'def\s+validate_r_([A-Za-z0-9_]+)\(']
        for p in patterns:
            validator_rules.update(re.findall(p, content))
except Exception as e:
    print(f'  Error: {e}')
print(f'  Rules found: {len(validator_rules)}')

# Scan Tests
print('\n[5/6] Scanning Tests...')
test_rules = set()
try:
    with open('11_test_simulation/tests_compliance/test_sot_validator.py') as f:
        content = f.read()
    patterns = [r'def\s+test_([a-z0-9_]+)\(', r'def\s+test_r_([A-Za-z0-9_]+)\(']
    for p in patterns:
        test_rules.update(re.findall(p, content))
except Exception as e:
    print(f'  Error: {e}')
print(f'  Rules found: {len(test_rules)}')

# Scan Audit
print('\n[6/6] Scanning Audit...')
audit_rules = set()
try:
    for audit_file in Path('02_audit_logging/reports').glob('*.json'):
        try:
            with open(audit_file) as f:
                content = f.read()
            patterns = [r'\"rule_id\":\s*\"([A-Za-z0-9_\-.]+)\"', r'\"id\":\s*\"([A-Za-z0-9_\-.]+)\"']
            for p in patterns:
                audit_rules.update(re.findall(p, content))
        except:
            pass
except Exception as e:
    print(f'  Error: {e}')
print(f'  Rules found: {len(audit_rules)}')

# Calculate completeness
print('\n[7/7] Calculating completeness...')
score_buckets = {100: 0, 80: 0, 60: 0, 40: 0, 20: 0, 0: 0}
total_score = 0.0

for rule_id in all_rule_ids:
    in_contract = rule_id in contract_rules
    in_policy = rule_id in policy_rules
    in_validator = rule_id in validator_rules
    in_tests = rule_id in test_rules
    in_audit = rule_id in audit_rules

    num_sources = sum([in_contract, in_policy, in_validator, in_tests, in_audit])
    score = num_sources / 5.0
    total_score += score

    if score == 1.0:
        score_buckets[100] += 1
    elif score >= 0.8:
        score_buckets[80] += 1
    elif score >= 0.6:
        score_buckets[60] += 1
    elif score >= 0.4:
        score_buckets[40] += 1
    elif score >= 0.2:
        score_buckets[20] += 1
    else:
        score_buckets[0] += 1

overall_completeness = (total_score / len(all_rule_ids)) * 100 if all_rule_ids else 0.0

print('\n' + '='*80)
print('Completeness Report')
print('='*80)
print(f'Total Rules: {len(all_rule_ids)}')
print(f'\nCompleteness Distribution:')
print(f'  100% (5/5 artifacts): {score_buckets[100]} rules')
print(f'   80% (4/5 artifacts): {score_buckets[80]} rules')
print(f'   60% (3/5 artifacts): {score_buckets[60]} rules')
print(f'   40% (2/5 artifacts): {score_buckets[40]} rules')
print(f'   20% (1/5 artifacts): {score_buckets[20]} rules')
print(f'    0% (0/5 artifacts): {score_buckets[0]} rules')
print(f'\nArtifact Coverage:')
print(f'  Contract:  {len(contract_rules):>6} rules')
print(f'  Policy:    {len(policy_rules):>6} rules')
print(f'  Validator: {len(validator_rules):>6} rules')
print(f'  Tests:     {len(test_rules):>6} rules')
print(f'  Audit:     {len(audit_rules):>6} rules')
print(f'\nOverall Completeness: {overall_completeness:.1f}%')
print('='*80)

# Save report
report = {
    'timestamp': '2025-10-24T16:00:00Z',
    'total_rules': len(all_rule_ids),
    'rules_with_100_percent': score_buckets[100],
    'rules_with_80_percent': score_buckets[80],
    'rules_with_60_percent': score_buckets[60],
    'rules_with_40_percent': score_buckets[40],
    'rules_with_20_percent': score_buckets[20],
    'rules_with_0_percent': score_buckets[0],
    'overall_completeness': overall_completeness,
    'artifact_coverage': {
        'contract': len(contract_rules),
        'policy': len(policy_rules),
        'validator': len(validator_rules),
        'tests': len(test_rules),
        'audit': len(audit_rules)
    }
}

with open('02_audit_logging/reports/completeness_report.json', 'w') as f:
    json.dump(report, f, indent=2)

print('\nReport saved to: 02_audit_logging/reports/completeness_report.json')
