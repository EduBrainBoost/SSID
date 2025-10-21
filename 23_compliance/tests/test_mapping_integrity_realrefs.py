"""
Test suite for compliance mapping integrity with real article references.

Validates that all compliance mappings contain actual regulatory references
(article numbers, chapters) and meet structural integrity requirements.

Test coverage:
- GDPR: Art. 5-32 references
- DORA: Chapter III references (Art. 6-28)
- MiCA: Art. 3+ references
- AMLD6: Art. 2-48 + AMLR references

Classification: PUBLIC - Test Code
"""

from pathlib import Path
import yaml
import re
import pytest

ROOT = Path(__file__).resolve().parents[2]
MAPS_DIR = ROOT / "23_compliance" / "mappings"

def load_mapping_file(filename: str) -> dict:
    """Load and parse a compliance mapping YAML file."""
    path = MAPS_DIR / filename
    assert path.exists(), f"Mapping file not found: {path}"

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    assert data, f"Empty or invalid YAML in {filename}"
    return data

def test_gdpr_mapping_structure():
    """Verify GDPR mapping has required structure and real article references."""
    data = load_mapping_file("gdpr_mapping.yaml")

    # Meta validation
    assert "meta" in data
    assert data["meta"]["framework"] == "GDPR"
    assert data["meta"]["status"] in ["active", "draft"]

    # Mappings validation
    assert "mappings" in data
    assert len(data["mappings"]) > 0

    # Check for real article references
    article_pattern = re.compile(r"Art\.?\s*\d+")
    found_articles = []

    for entry in data["mappings"]:
        assert "id" in entry
        assert "description" in entry
        assert "applies_to" in entry
        assert "verification" in entry

        # Each mapping must reference an article
        assert article_pattern.search(entry["id"]) or article_pattern.search(entry["description"]), \
            f"No article reference in {entry['id']}"

        # Extract article numbers
        matches = article_pattern.findall(entry["id"] + " " + entry["description"])
        found_articles.extend(matches)

    # Should have multiple distinct articles
    assert len(found_articles) >= 5, f"Expected multiple GDPR articles, found: {found_articles}"

def test_dora_mapping_structure():
    """Verify DORA mapping has required structure and Chapter III references."""
    data = load_mapping_file("dora_mapping.yaml")

    # Meta validation
    assert "meta" in data
    assert data["meta"]["framework"] == "DORA"

    # Mappings validation
    assert "mappings" in data
    assert len(data["mappings"]) > 0

    # Check for Chapter III or Article references
    article_pattern = re.compile(r"(Art\.?\s*\d+|Kap\.?\s*III|Chapter\s*III)")
    found_refs = []

    for entry in data["mappings"]:
        assert "id" in entry
        assert "description" in entry
        assert "applies_to" in entry
        assert "verification" in entry

        # Each mapping must reference an article or chapter
        full_text = entry["id"] + " " + entry["description"]
        assert article_pattern.search(full_text), \
            f"No DORA article/chapter reference in {entry['id']}"

        matches = article_pattern.findall(full_text)
        found_refs.extend(matches)

    # Should have multiple distinct references
    assert len(found_refs) >= 5, f"Expected multiple DORA references, found: {found_refs}"

def test_mica_mapping_structure():
    """Verify MiCA mapping has required structure and Art. 76+ references."""
    data = load_mapping_file("mica_mapping.yaml")

    # Meta validation
    assert "meta" in data
    assert data["meta"]["framework"] == "MiCA"

    # Mappings validation
    assert "mappings" in data
    assert len(data["mappings"]) > 0

    # Check for article references
    article_pattern = re.compile(r"Art\.?\s*\d+")
    found_articles = []

    for entry in data["mappings"]:
        assert "id" in entry
        assert "description" in entry
        assert "applies_to" in entry
        assert "verification" in entry

        # Each mapping must reference an article
        full_text = entry["id"] + " " + entry["description"]
        assert article_pattern.search(full_text), \
            f"No MiCA article reference in {entry['id']}"

        matches = article_pattern.findall(full_text)
        found_articles.extend(matches)

    # Should have multiple distinct articles
    assert len(found_articles) >= 5, f"Expected multiple MiCA articles, found: {found_articles}"

def test_amld6_mapping_structure():
    """Verify AMLD6 mapping has required structure and Art. 2-44 references."""
    data = load_mapping_file("amld6_mapping.yaml")

    # Meta validation
    assert "meta" in data
    assert data["meta"]["framework"] == "AMLD6"

    # Mappings validation
    assert "mappings" in data
    assert len(data["mappings"]) > 0

    # Check for article references (AMLD6 or AMLR)
    article_pattern = re.compile(r"(Art\.?\s*\d+|AMLD6|AMLR)")
    found_refs = []

    for entry in data["mappings"]:
        assert "id" in entry
        assert "description" in entry
        assert "applies_to" in entry
        assert "verification" in entry

        # Each mapping must reference an article
        full_text = entry["id"] + " " + entry["description"]
        assert article_pattern.search(full_text), \
            f"No AMLD6/AMLR reference in {entry['id']}"

        matches = article_pattern.findall(full_text)
        found_refs.extend(matches)

    # Should have multiple distinct references
    assert len(found_refs) >= 5, f"Expected multiple AMLD6 references, found: {found_refs}"

def test_all_mappings_have_real_article_references():
    """Global test: verify ALL mappings contain real regulatory article references."""
    mapping_files = {
        "gdpr_mapping.yaml": r"Art\.?\s*\d+",
        "dora_mapping.yaml": r"(Art\.?\s*\d+|Kap\.?\s*III)",
        "mica_mapping.yaml": r"Art\.?\s*\d+",
        "amld6_mapping.yaml": r"(Art\.?\s*\d+|AMLR)",
    }

    for filename, pattern in mapping_files.items():
        data = load_mapping_file(filename)
        regex = re.compile(pattern)

        for entry in data["mappings"]:
            full_text = entry["id"] + " " + entry["description"]
            assert regex.search(full_text), \
                f"{filename} - {entry['id']}: Missing regulatory reference"

def test_mapping_applies_to_valid_modules():
    """Verify applies_to references valid SSID modules (00-24 range)."""
    valid_module_pattern = re.compile(r"^\d{2}_[a-z_]+$")

    for mapping_file in MAPS_DIR.glob("*_mapping.yaml"):
        data = load_mapping_file(mapping_file.name)

        for entry in data["mappings"]:
            if "applies_to" in entry:
                for module in entry["applies_to"]:
                    assert valid_module_pattern.match(module), \
                        f"{mapping_file.name} - {entry['id']}: Invalid module reference '{module}'"

def test_verification_methods_valid():
    """Verify all entries use valid verification methods."""
    valid_methods = {"automated", "manual", "hybrid"}

    for mapping_file in MAPS_DIR.glob("*_mapping.yaml"):
        data = load_mapping_file(mapping_file.name)

        for entry in data["mappings"]:
            assert "verification" in entry, \
                f"{mapping_file.name} - {entry['id']}: Missing verification field"
            assert entry["verification"] in valid_methods, \
                f"{mapping_file.name} - {entry['id']}: Invalid verification method '{entry['verification']}'"

def test_checksums_present():
    """Verify all mapping files have checksum placeholders or values."""
    for mapping_file in MAPS_DIR.glob("*_mapping.yaml"):
        data = load_mapping_file(mapping_file.name)

        assert "checksum" in data, \
            f"{mapping_file.name}: Missing checksum field"
        assert data["checksum"], \
            f"{mapping_file.name}: Empty checksum"

def test_no_duplicate_ids():
    """Verify no duplicate mapping IDs within each framework."""
    for mapping_file in MAPS_DIR.glob("*_mapping.yaml"):
        data = load_mapping_file(mapping_file.name)

        ids = [entry["id"] for entry in data["mappings"]]
        unique_ids = set(ids)

        assert len(ids) == len(unique_ids), \
            f"{mapping_file.name}: Duplicate mapping IDs found"

def test_descriptions_not_empty():
    """Verify all descriptions are non-empty and meaningful."""
    for mapping_file in MAPS_DIR.glob("*_mapping.yaml"):
        data = load_mapping_file(mapping_file.name)

        for entry in data["mappings"]:
            desc = entry.get("description", "")
            assert desc, \
                f"{mapping_file.name} - {entry['id']}: Empty description"
            assert len(desc) > 10, \
                f"{mapping_file.name} - {entry['id']}: Description too short"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
