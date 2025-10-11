"""
Test Structure Policy vs. Markdown Documentation Consistency

Validates that structure lock policies are properly documented in markdown files
and that documentation matches policy definitions.

Version: Sprint 2
"""

import pytest
from pathlib import Path
import yaml


REPO_ROOT = Path(__file__).parent.parent.parent.parent
POLICIES_DIR = REPO_ROOT / "23_compliance" / "policies"
ARCHITECTURE_DIR = REPO_ROOT / "23_compliance" / "architecture"


def test_max_depth_policy_exists():
    """Test that max_depth_policy.yaml exists."""
    policy_file = POLICIES_DIR / "max_depth_policy.yaml"
    assert policy_file.exists(), "max_depth_policy.yaml does not exist"


def test_max_depth_policy_structure():
    """Test that max_depth_policy.yaml has required structure."""
    policy_file = POLICIES_DIR / "max_depth_policy.yaml"

    with open(policy_file, 'r', encoding='utf-8') as f:
        policy = yaml.safe_load(f)

    assert "title" in policy, "Missing title"
    assert "depth_constraints" in policy, "Missing depth_constraints"
    assert "max_depth" in policy["depth_constraints"], "Missing depth_constraints.max_depth"
    assert "enforcement" in policy, "Missing enforcement"


def test_max_depth_constraint_md_exists():
    """Test that max_depth_constraint.md documentation exists."""
    doc_file = ARCHITECTURE_DIR / "max_depth_constraint.md"
    assert doc_file.exists(), "max_depth_constraint.md does not exist"


def test_max_depth_documentation_matches_policy():
    """Test that markdown documentation matches policy definition."""
    policy_file = POLICIES_DIR / "max_depth_policy.yaml"
    doc_file = ARCHITECTURE_DIR / "max_depth_constraint.md"

    with open(policy_file, 'r', encoding='utf-8') as f:
        policy = yaml.safe_load(f)

    with open(doc_file, 'r', encoding='utf-8') as f:
        doc_content = f.read()

    # Check that max_depth value is mentioned in documentation
    max_depth = policy["depth_constraints"]["max_depth"]
    # Check various possible formats in documentation
    doc_lower = doc_content.lower()
    depth_mentioned = (
        f"max_depth: {max_depth}" in doc_content or
        f"max_depth={max_depth}" in doc_content or
        f"max depth: {max_depth}" in doc_lower or
        f"maximum depth of {max_depth}" in doc_lower or
        f"depth limit: {max_depth}" in doc_lower or
        f"depth = {max_depth}" in doc_lower
    )

    assert depth_mentioned, (
        f"Documentation does not clearly mention max_depth={max_depth}"
    )


def test_structure_lock_documentation_exists():
    """Test that structure lock documentation exists."""
    # Check if structure/depth constraint documentation is present
    doc_files = (
        list(ARCHITECTURE_DIR.glob("*structure*.md")) +
        list(ARCHITECTURE_DIR.glob("*lock*.md")) +
        list(ARCHITECTURE_DIR.glob("*depth*.md")) +
        list(ARCHITECTURE_DIR.glob("*constraint*.md"))
    )
    assert len(doc_files) > 0, (
        "No structure lock/depth constraint documentation found in architecture/. "
        f"Searched in: {ARCHITECTURE_DIR}"
    )
