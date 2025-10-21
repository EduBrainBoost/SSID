#!/usr/bin/env python3
"""
OPA Policy Scaffold Generator (v6.0)
Generates OPA policy stubs from chart.yaml for all roots.

Usage:
    python scaffold_policy_from_chart.py --all
    python scaffold_policy_from_chart.py --roots 01_ai_layer 07_governance_legal
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict

def generate_opa_policy(root_name: str, capabilities: List[str], policies: List[Dict], output_dir: Path):
    """Generate OPA policy stub for a root."""

    package_name = root_name.replace("_", "")

    policy_content = f'''# OPA Policy for {root_name} (v6.0)

#
# Capabilities: {", ".join(capabilities)}

package ssid.{package_name}.v6_0

# Input schema:
# {{
#   "action": string,
#   "resource": {{ "type": string, "id": string, "data": object }},
#   "subject": {{ "id": string, "roles": [string] }},
#   "context": {{ "timestamp": string, "environment": string }}
# }}

default allow = false

'''

    # Generate allow/deny rules for each policy
    for i, policy in enumerate(policies, 1):
        policy_name = policy["name"]
        enforcement = policy["enforcement"]
        scope = policy["scope"]

        policy_content += f'''
# =============================================================================
# POLICY {i}: {policy_name} ({enforcement}, {scope})
# =============================================================================

allow_{policy_name} {{

    # Enforcement: {enforcement}
    # Scope: {scope}

    true  
}}

deny_{policy_name}[msg] {{
    not allow_{policy_name}
    msg := "Policy {policy_name} validation failed (TODO: implement logic)"
}}
'''

    policy_content += '''
# =============================================================================
# Main Policy Decision
# =============================================================================

allow {
'''
    for policy in policies:
        policy_content += f'    allow_{policy["name"]}\n'

    policy_content += '''}

deny[msg] {
'''
    for policy in policies:
        policy_content += f'    deny_{policy["name"]}[msg]\n'

    policy_content += f'''}}

# =============================================================================
# Metadata
# =============================================================================

metadata = {{
    "version": "v6.0",
    "root": "{root_name}",
    "status": "stub",
    "policies_implemented": {json.dumps([p["name"] for p in policies])},
    "capabilities": {json.dumps(capabilities)},
    "todo": ["Implement actual validation logic for all policies"]
}}
'''

    output_file = output_dir / f"{package_name}_policy_v6_0.rego"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(policy_content)

    print(f"[OK] Generated: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate OPA policy stubs")
    parser.add_argument("--roots", nargs='+', help="Specific roots to generate")
    parser.add_argument("--all", action='store_true', help="Generate for all roots")
    parser.add_argument("--map", type=Path, default=Path("02_audit_logging/reports/root_24_governance_map_v6_0.json"))
    parser.add_argument("--output", type=Path, default=Path("23_compliance/policies"))

    args = parser.parse_args()

    # Load governance map
    with open(args.map) as f:
        gov_map = json.load(f)

    roots_to_process = []
    if args.all:
        roots_to_process = [r["root"] for r in gov_map["roots"]]
    elif args.roots:
        roots_to_process = args.roots
    else:
        print("ERROR: Specify --all or --roots", file=sys.stderr)
        sys.exit(1)

    print(f"Generating OPA policies for {len(roots_to_process)} roots...")

    for root_name in roots_to_process:
        # Find root in map
        root_data = None
        for r in gov_map["roots"]:
            if r["root"] == root_name:
                root_data = r
                break

        if not root_data:
            print(f"WARNING: Root {root_name} not found", file=sys.stderr)
            continue

        capabilities = root_data["chart"]["capabilities"]
        policies = root_data["chart"]["policies"]

        generate_opa_policy(root_name, capabilities, policies, args.output)

    print(f"\n[OK] Generated {len(roots_to_process)} OPA policy stubs")

if __name__ == "__main__":
    main()
