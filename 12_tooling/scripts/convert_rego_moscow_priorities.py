#!/usr/bin/env python3
"""
Convert Rego Policy to MoSCoW Priority Model
=============================================

Converts deny rules to warn/info based on RULE_PRIORITIES from sot_validator_core.py

Version: 1.0.0
Date: 2025-10-17
Author: SSID Core Team
"""

import sys
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "03_core"))

from validators.sot.sot_validator_core import RULE_PRIORITIES

# File paths
REGO_PATH = Path(__file__).parent.parent.parent / "23_compliance" / "policies" / "sot" / "sot_policy.rego"


def convert_rule_to_priority(content: str, rule_id: str, priority: str) -> str:
    """
    Convert a specific rule from deny to warn/info based on priority

    Args:
        content: Full rego file content
        rule_id: Rule ID (e.g., "SOT-025")
        priority: Priority (must/should/have)

    Returns:
        Updated content
    """
    if priority == "must":
        # MUST rules stay as deny
        return content

    # Find all deny statements for this rule_id
    # Pattern: deny contains msg if { ... msg := "[rule_id] ..."

    # Pattern to match deny blocks with this rule_id
    pattern = rf'(deny contains msg if \{{[^}}]*?"\[{rule_id}\][^"]*"[^}}]*?\}})'

    replacement_type = "warn" if priority == "should" else "info"

    def replace_func(match):
        block = match.group(0)
        # Replace deny with warn or info
        updated_block = block.replace("deny contains", f"{replacement_type} contains")
        # Add priority label to message if not already present
        if f"[{rule_id}]" in updated_block and priority.upper() not in updated_block:
            updated_block = updated_block.replace(
                f'"[{rule_id}]',
                f'"[{rule_id}] {priority.upper()}:'
            )
        return updated_block

    return re.sub(pattern, replace_func, content, flags=re.DOTALL)


def main():
    """Convert all rules based on RULE_PRIORITIES"""

    print(f"Reading Rego policy: {REGO_PATH}")

    with open(REGO_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Convert each rule based on priority
    for rule_id, priority in RULE_PRIORITIES.items():
        if priority in ["should", "have"]:
            print(f"Converting {rule_id} to {priority.upper()} ({['warn', 'info'][priority == 'have']})")
            content = convert_rule_to_priority(content, rule_id, priority)

    # Check if changes were made
    if content == original_content:
        print("No changes made - rules may already be converted")
    else:
        # Write updated content
        with open(REGO_PATH, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Successfully converted Rego policy to MoSCoW priorities")
        print(f"Updated: {REGO_PATH}")

    # Count deny/warn/info statements
    deny_count = len(re.findall(r'deny contains msg', content))
    warn_count = len(re.findall(r'warn contains msg', content))
    info_count = len(re.findall(r'info contains msg', content))

    print(f"\nRule distribution:")
    print(f"  MUST (deny):   {deny_count} rules")
    print(f"  SHOULD (warn): {warn_count} rules")
    print(f"  HAVE (info):   {info_count} rules")


if __name__ == "__main__":
    main()
