"""
Test suite for compliance review templates validation.

Validates structural integrity, required fields, and cross-references
for all review framework YAMLs in 23_compliance/reviews/2025-Q4/.

Classification: PUBLIC - Test Code
"""

from pathlib import Path
import yaml
import pytest


ROOT = Path(__file__).resolve().parents[2]
REVIEWS_DIR = ROOT / "23_compliance" / "reviews" / "2025-Q4"


def load_yaml(filename: str) -> dict:
    """Load and parse a YAML file from the reviews directory."""
    path = REVIEWS_DIR / filename
    assert path.exists(), f"Review file not found: {path}"

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data, f"Empty or invalid YAML in {filename}"
    return data


def test_review_files_exist():
    """Verify all required review files exist."""
    required_files = [
        "review_template.yaml",
        "reviewer_checklist.yaml",
        "reviewer_assignments.yaml",
        "review_findings.yaml",
        "audit_findings.yaml",
        "README.md"
    ]

    for filename in required_files:
        path = REVIEWS_DIR / filename
        assert path.exists(), f"Required file missing: {filename}"


def test_review_template_structure():
    """Validate review_template.yaml has required structure."""
    data = load_yaml("review_template.yaml")

    # Meta validation
    assert "meta" in data
    assert data["meta"]["version"] == "2025-Q4"
    assert data["meta"]["type"] == "review_template"

    # Review sections
    required_sections = [
        "review_information",
        "review_sections",
        "approval"
    ]

    for section in required_sections:
        assert section in data, f"Missing section: {section}"

    # Framework reviews
    assert "review_sections" in data
    sections = data["review_sections"]

    required_framework_reviews = ["gdpr_review", "dora_review", "mica_review", "amld6_review"]
    for framework in required_framework_reviews:
        assert framework in sections, f"Missing framework review: {framework}"

    # Checksum present
    assert "checksum" in data


def test_reviewer_checklist_structure():
    """Validate reviewer_checklist.yaml has required structure."""
    data = load_yaml("reviewer_checklist.yaml")

    # Meta validation
    assert "meta" in data
    assert data["meta"]["version"] == "2025-Q4"
    assert data["meta"]["type"] == "reviewer_checklist"

    # Checklist validation
    assert "checklist" in data
    checklist = data["checklist"]

    # All frameworks present
    required_frameworks = ["gdpr", "dora", "mica", "amld6"]
    for framework in required_frameworks:
        assert framework in checklist, f"Missing framework: {framework}"

        # Each framework has items
        assert "items" in checklist[framework]
        assert len(checklist[framework]["items"]) > 0

        # Each item has required fields
        for item in checklist[framework]["items"]:
            assert "topic" in item
            assert "evidence_path" in item
            assert "verification_method" in item
            assert "status" in item

    # Review progress tracking
    assert "review_progress" in data
    progress = data["review_progress"]
    assert "summary" in progress
    assert "by_framework" in progress

    # Checksum present
    assert "checksum" in data


def test_reviewer_assignments_structure():
    """Validate reviewer_assignments.yaml has required structure."""
    data = load_yaml("reviewer_assignments.yaml")

    # Meta validation
    assert "meta" in data
    assert data["meta"]["version"] == "2025-Q4"
    assert data["meta"]["type"] == "reviewer_assignments"

    # Assignments validation
    assert "assignments" in data
    assignments = data["assignments"]
    assert len(assignments) > 0, "No reviewers assigned"

    # Each reviewer has required fields
    for reviewer in assignments:
        assert "reviewer_id" in reviewer
        assert reviewer["reviewer_id"].startswith("did:ssid:")
        assert "name" in reviewer
        assert "role" in reviewer
        assert "scope" in reviewer
        assert "responsibilities" in reviewer
        assert "status" in reviewer

    # Review schedule
    assert "review_schedule" in data
    schedule = data["review_schedule"]
    assert "start_date" in schedule
    assert "end_date" in schedule
    assert "milestones" in schedule

    # Approval matrix
    assert "approval_matrix" in data
    approval = data["approval_matrix"]
    assert "required_signatures" in approval
    assert len(approval["required_signatures"]) >= 4

    # Checksum present
    assert "checksum" in data


def test_review_findings_structure():
    """Validate review_findings.yaml has required structure."""
    data = load_yaml("review_findings.yaml")

    # Meta validation
    assert "meta" in data
    assert data["meta"]["version"] == "2025-Q4"
    assert data["meta"]["type"] == "review_findings"

    # Findings validation
    assert "findings" in data
    findings = data["findings"]

    # Each finding has required fields
    for finding in findings:
        assert "id" in finding
        assert finding["id"].startswith("FIND-2025Q4-")
        assert "framework" in finding
        assert "severity" in finding
        assert finding["severity"] in ["critical", "high", "medium", "low", "observation"]
        assert "description" in finding
        assert "affected_modules" in finding
        assert "recommendation" in finding
        assert "status" in finding
        assert "target_date" in finding

    # Audit summary
    assert "audit_summary" in data
    summary = data["audit_summary"]
    assert "total_findings" in summary
    assert "by_severity" in summary
    assert "by_status" in summary
    assert "by_framework" in summary
    assert "compliance_score" in summary

    # Checksum present
    assert "checksum" in data


def test_audit_findings_structure():
    """Validate audit_findings.yaml has required structure."""
    data = load_yaml("audit_findings.yaml")

    # Meta validation
    assert "meta" in data
    assert data["meta"]["version"] == "2025-Q4"

    # Audit information
    assert "audit_information" in data
    info = data["audit_information"]
    assert "audit_id" in info
    assert "audit_type" in info

    # Findings
    assert "findings" in data

    # Summary statistics
    assert "summary_statistics" in data

    # Checksum present
    assert "checksum" in data


def test_yaml_structure_integrity():
    """Verify all YAML files are valid and parseable."""
    yaml_files = REVIEWS_DIR.glob("*.yaml")

    for yaml_file in yaml_files:
        data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        assert data, f"Failed to parse {yaml_file.name}"
        assert "meta" in data, f"Missing meta section in {yaml_file.name}"
        assert "version" in data["meta"], f"Missing version in {yaml_file.name}"


def test_framework_coverage():
    """Verify all four frameworks are covered in checklist."""
    checklist = load_yaml("reviewer_checklist.yaml")

    frameworks = checklist["checklist"].keys()
    required = {"gdpr", "dora", "mica", "amld6"}

    assert required.issubset(frameworks), \
        f"Missing frameworks: {required - set(frameworks)}"


def test_reviewer_did_format():
    """Verify all reviewer IDs follow DID format."""
    assignments = load_yaml("reviewer_assignments.yaml")

    did_pattern = r"^did:ssid:[a-z0-9]+$"
    import re

    for reviewer in assignments["assignments"]:
        did = reviewer["reviewer_id"]
        assert re.match(did_pattern, did), \
            f"Invalid DID format: {did}"


def test_finding_severity_valid():
    """Verify all findings have valid severity levels."""
    findings = load_yaml("review_findings.yaml")

    valid_severities = {"critical", "high", "medium", "low", "observation"}

    for finding in findings["findings"]:
        assert finding["severity"] in valid_severities, \
            f"Invalid severity in {finding['id']}: {finding['severity']}"


def test_checksum_placeholder():
    """Verify all YAML files have checksum placeholders for CI."""
    yaml_files = ["review_template.yaml", "reviewer_checklist.yaml",
                  "reviewer_assignments.yaml", "review_findings.yaml",
                  "audit_findings.yaml"]

    for filename in yaml_files:
        data = load_yaml(filename)
        assert "checksum" in data, f"Missing checksum in {filename}"
        # Checksum should either be placeholder or actual hash
        assert data["checksum"], f"Empty checksum in {filename}"


def test_evidence_paths_reference_modules():
    """Verify evidence paths reference valid SSID modules."""
    checklist = load_yaml("reviewer_checklist.yaml")

    valid_module_pattern = r"^\d{2}_[a-z_]+/"
    import re

    for framework_name, framework_data in checklist["checklist"].items():
        if "items" in framework_data:
            for item in framework_data["items"]:
                if "evidence_path" in item:
                    path = item["evidence_path"]
                    # Should reference a module or be in 23_compliance
                    assert (re.match(valid_module_pattern, path) or
                            path.startswith("23_compliance/")), \
                        f"Invalid evidence path: {path}"


def test_target_dates_format():
    """Verify all target dates are in YYYY-MM-DD format."""
    findings = load_yaml("review_findings.yaml")

    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    import re

    for finding in findings["findings"]:
        if "target_date" in finding and finding["target_date"]:
            assert re.match(date_pattern, finding["target_date"]), \
                f"Invalid date format in {finding['id']}: {finding['target_date']}"


def test_remediation_owners_assigned():
    """Verify all findings have remediation owners."""
    findings = load_yaml("review_findings.yaml")

    for finding in findings["findings"]:
        if finding["status"] != "closed":
            assert "remediation_owner" in finding, \
                f"Missing remediation owner for {finding['id']}"
            assert finding["remediation_owner"].startswith("did:ssid:"), \
                f"Invalid remediation owner DID in {finding['id']}"


def test_critical_findings_escalated():
    """Verify critical findings are marked for escalation."""
    findings = load_yaml("review_findings.yaml")

    for finding in findings["findings"]:
        if finding["severity"] == "critical":
            assert finding.get("escalation_required") == True, \
                f"Critical finding {finding['id']} not marked for escalation"


def test_readme_exists_and_has_content():
    """Verify README.md exists and has substantial content."""
    readme_path = REVIEWS_DIR / "README.md"
    assert readme_path.exists()

    content = readme_path.read_text(encoding="utf-8")
    assert len(content) > 1000, "README too short"
    assert "# Quarterly Compliance Review" in content
    assert "GDPR" in content
    assert "DORA" in content
    assert "MiCA" in content
    assert "AMLD6" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
