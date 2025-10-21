"""
Test suite for governance documents validation.

Validates structural integrity and required content for all governance
documents in 23_compliance/governance/.

Classification: PUBLIC - Test Code
"""

from pathlib import Path
import yaml
import re
import pytest

ROOT = Path(__file__).resolve().parents[2]
GOV_DIR = ROOT / "23_compliance" / "governance"

def test_governance_files_exist():
    """Verify all required governance files exist."""
    required_files = [
        "maintainers_enterprise.yaml",
        "community_guidelines_enterprise.md",
        "audit_committee_policy.md"
    ]

    for filename in required_files:
        path = GOV_DIR / filename
        assert path.exists(), f"Required governance file missing: {filename}"

def test_maintainers_yaml_valid():
    """Validate maintainers_enterprise.yaml structure."""
    path = GOV_DIR / "maintainers_enterprise.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Meta validation
    assert "meta" in data
    assert data["meta"]["document"] == "Enterprise Maintainers Registry"
    assert data["meta"]["version"] == "2025-Q4"

    # Maintainers validation
    assert "maintainers" in data
    assert len(data["maintainers"]) >= 1, "At least one maintainer required"

    # Each maintainer has required fields
    for maintainer in data["maintainers"]:
        assert "id" in maintainer
        assert maintainer["id"].startswith("did:ssid:")
        assert "name" in maintainer
        assert "role" in maintainer
        assert "jurisdiction" in maintainer
        assert "roots_responsible" in maintainer
        assert "pgp_fingerprint" in maintainer
        assert "status" in maintainer
        assert "voting_weight" in maintainer

    # Governance committee validation
    assert "governance_committee" in data
    committee = data["governance_committee"]
    assert "total_members" in committee
    assert "quorum_required" in committee
    assert "voting_method" in committee
    assert "decision_policies" in committee

    # Checksum present
    assert "checksum" in data

def test_maintainer_did_format():
    """Verify all maintainer DIDs follow correct format."""
    path = GOV_DIR / "maintainers_enterprise.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    did_pattern = r"^did:ssid:maintainer\d{3}$"

    for maintainer in data["maintainers"]:
        did = maintainer["id"]
        assert re.match(did_pattern, did), \
            f"Invalid DID format: {did}"

def test_maintainer_jurisdictions_valid():
    """Verify maintainer jurisdictions are valid ISO country codes."""
    path = GOV_DIR / "maintainers_enterprise.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Common EU jurisdictions
    valid_jurisdictions = {"DE", "FR", "LU", "UK", "NL", "BE", "AT", "CH", "ES", "IT"}

    for maintainer in data["maintainers"]:
        jurisdiction = maintainer["jurisdiction"]
        assert jurisdiction in valid_jurisdictions, \
            f"Invalid jurisdiction: {jurisdiction}"

def test_roots_responsible_valid():
    """Verify roots_responsible references valid module names."""
    path = GOV_DIR / "maintainers_enterprise.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    valid_module_pattern = r"^\d{2}_[a-z_]+$"

    for maintainer in data["maintainers"]:
        for root in maintainer["roots_responsible"]:
            assert re.match(valid_module_pattern, root), \
                f"Invalid root module reference: {root}"

def test_community_guidelines_format():
    """Validate community_guidelines_enterprise.md structure."""
    path = GOV_DIR / "community_guidelines_enterprise.md"
    content = path.read_text(encoding="utf-8")

    # Check required sections
    required_sections = [
        "# SSID Enterprise Community Guidelines",
        "## 1. Grundprinzipien",
        "## 2. Contribution-Flow",
        "## 3. Offene Kommunikation",
        "## 4. Governance-Ethik",
        "## 5. Eskalationsprozess",
        "## 6. Sicherheits-Richtlinien"
    ]

    for section in required_sections:
        assert section in content, f"Missing section: {section}"

    # Check for key content
    assert "Non-Custodial" in content
    assert "DID-Signatur" in content or "DID-signiert" in content
    assert "Pull-Request" in content or "PR" in content
    assert "CC-BY-4.0" in content

    # Check document length (should be substantial)
    assert len(content) > 2000, "Community guidelines too short"

def test_audit_committee_policy_format():
    """Validate audit_committee_policy.md structure."""
    path = GOV_DIR / "audit_committee_policy.md"
    content = path.read_text(encoding="utf-8")

    # Check required sections
    required_sections = [
        "# SSID Audit Committee Policy",
        "## 1. Mandat",
        "## 2. Zusammensetzung",
        "## 3. Verantwortlichkeiten",
        "## 4. Berichterstattung",
        "## 5. Transparenzregeln"
    ]

    for section in required_sections:
        assert section in content, f"Missing section: {section}"

    # Check for key content
    assert "Lead Auditor" in content
    assert "Compliance Officer" in content
    assert "External Auditor" in content
    assert "Quorum" in content
    assert "ISO 27001" in content or "ISO 19011" in content

    # Check document length (should be substantial)
    assert len(content) > 3000, "Audit committee policy too short"

def test_governance_docs_have_version():
    """Verify all governance docs specify version 2025-Q4."""
    for doc in GOV_DIR.glob("*.md"):
        content = doc.read_text(encoding="utf-8")
        assert "2025-Q4" in content, f"{doc.name} missing version"

    # Check YAML too
    for doc in GOV_DIR.glob("*.yaml"):
        with open(doc, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "meta" in data
        assert data["meta"]["version"] == "2025-Q4"

def test_governance_docs_have_checksums():
    """Verify all governance docs have checksum placeholders."""
    # YAML files
    for doc in GOV_DIR.glob("*.yaml"):
        with open(doc, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "checksum" in data
        assert data["checksum"], f"Empty checksum in {doc.name}"

    # Markdown files
    for doc in GOV_DIR.glob("*.md"):
        content = doc.read_text(encoding="utf-8")
        assert "sha256:TO_BE_FILLED_BY_CI" in content or \
               "Dokument-Hash" in content, \
               f"Missing checksum in {doc.name}"

def test_contact_emails_present():
    """Verify governance docs contain contact information."""
    contact_pattern = r"[\w\.-]+@ssid\.foundation"

    for doc in GOV_DIR.glob("*.md"):
        content = doc.read_text(encoding="utf-8")
        assert re.search(contact_pattern, content), \
            f"{doc.name} missing contact email"

def test_governance_cross_references():
    """Verify governance docs reference each other correctly."""
    # Community guidelines should reference maintainers
    guidelines = (GOV_DIR / "community_guidelines_enterprise.md").read_text(encoding="utf-8")
    assert "maintainers_enterprise.yaml" in guidelines

    # Audit policy should reference both
    audit_policy = (GOV_DIR / "audit_committee_policy.md").read_text(encoding="utf-8")
    assert "maintainers_enterprise.yaml" in audit_policy
    assert "community_guidelines_enterprise.md" in audit_policy

def test_governance_committee_quorum_valid():
    """Verify governance committee quorum is sensible."""
    path = GOV_DIR / "maintainers_enterprise.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    committee = data["governance_committee"]
    total = committee["total_members"]
    quorum = committee["quorum_required"]

    # Quorum should be majority but not all
    assert quorum > total / 2, "Quorum too low"
    assert quorum <= total, "Quorum cannot exceed total members"

def test_decision_policies_exist():
    """Verify governance committee has decision policies defined."""
    path = GOV_DIR / "maintainers_enterprise.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    policies = data["governance_committee"]["decision_policies"]

    required_policies = [
        "sot_changes",
        "root_structure_changes",
        "compliance_framework_changes"
    ]

    for policy in required_policies:
        assert policy in policies, f"Missing decision policy: {policy}"
        assert "description" in policies[policy]
        assert "approval_required" in policies[policy]

def test_pgp_fingerprints_valid_format():
    """Verify PGP fingerprints follow correct format."""
    path = GOV_DIR / "maintainers_enterprise.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # PGP fingerprint: 40 hex chars with spaces every 4 chars
    # Example: "9F3E 122B D671 1CFE 48DA 1C41 77D3 22A9 48D2 B1AF"
    fingerprint_pattern = r"^[0-9A-F]{4}( [0-9A-F]{4}){9}$"

    for maintainer in data["maintainers"]:
        fingerprint = maintainer["pgp_fingerprint"]
        assert re.match(fingerprint_pattern, fingerprint), \
            f"Invalid PGP fingerprint format: {fingerprint}"

def test_markdown_files_not_empty():
    """Verify markdown governance docs have substantial content."""
    for doc in GOV_DIR.glob("*.md"):
        content = doc.read_text(encoding="utf-8")
        # Should have multiple sections (## headers)
        section_count = content.count("## ")
        assert section_count >= 5, f"{doc.name} has too few sections ({section_count})"

def test_license_information_present():
    """Verify governance docs specify licensing."""
    for doc in GOV_DIR.glob("*.md"):
        content = doc.read_text(encoding="utf-8")
        assert "CC-BY-4.0" in content or "Creative Commons" in content, \
            f"{doc.name} missing license information"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
