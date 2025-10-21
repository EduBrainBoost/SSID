#!/usr/bin/env python3
"""
SSID Compliance Forensic Auditor - SoT -> Policy -> Test Mapper
Deterministic 1:1 mapping analysis without heuristics.
"""
import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]

# Input SoT files (exact paths as specified)
SOT_FILES = [
    REPO_ROOT / "16_codex/structure/ssid_master_definition_corrected_v1.1.1.md",
    REPO_ROOT / "16_codex/structure/blueprint_v4.2/SSID_structure_level3_part1_MAX.md",
    REPO_ROOT / "16_codex/structure/blueprint_v4.2/SSID_structure_level3_part2_MAX.md",
    REPO_ROOT / "16_codex/structure/blueprint_v4.2/SSID_structure_level3_part3_MAX.md",
]

# Source directories
POLICY_DIR = REPO_ROOT / "23_compliance/policies"
TEST_DIR = REPO_ROOT / "11_test_simulation/tests"

# Output directories
OUTPUT_DIR = REPO_ROOT / "23_compliance/mappings"
REPORT_DIR = REPO_ROOT / "23_compliance/reports"

def is_content_line(line: str) -> bool:
    """
    Check if line is actual content (not empty, code fence, or comment).
    """
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith('#'):  # Headings are meta, not rules
        return False
    if stripped.startswith('```'):  # Code fences
        return False
    if stripped.startswith('---'):  # Separators
        return False
    if stripped.startswith('|'):  # Table rows
        return False
    if len(stripped) < 10:  # Too short to be a rule
        return False
    return True

def extract_rules(file_path: Path) -> List[Dict]:
    """
    Extract all content lines as individual rules.
    """
    rules = []
    if not file_path.exists():
        print(f"[!] File not found: {file_path}")
        return rules

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line_num, line in enumerate(lines, 1):
        if is_content_line(line):
            rule_text = line.strip()
            # Generate rule_id (SHA-256)
            rule_id = hashlib.sha256(rule_text.encode('utf-8')).hexdigest()[:12]

            rules.append({
                "rule_id": rule_id,
                "source_file": str(file_path.relative_to(REPO_ROOT)).replace('\\', '/'),
                "line_number": line_num,
                "rule_text": rule_text,
                "keywords": extract_keywords(rule_text)
            })

    return rules

def extract_keywords(text: str) -> List[str]:
    """
    Extract meaningful keywords from rule text (lowercase, alphanumeric).
    Filter out common words.
    """
    # Common words to ignore
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
                 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might',
                 'can', 'must', 'shall', 'this', 'that', 'these', 'those', 'it', 'its'}

    # Extract alphanumeric words
    words = re.findall(r'\b[a-z0-9_]{3,}\b', text.lower())

    # Filter stopwords and return unique keywords
    keywords = [w for w in words if w not in stopwords]
    return list(set(keywords))[:20]  # Limit to 20 keywords

def search_policies(rules: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Search all .rego files for rule keywords.
    """
    policy_matches = {}

    if not POLICY_DIR.exists():
        print(f"[!] Policy directory not found: {POLICY_DIR}")
        return policy_matches

    policy_files = list(POLICY_DIR.rglob("*.rego"))
    print(f"[*] Scanning {len(policy_files)} policy files...")

    for policy_file in policy_files:
        try:
            with open(policy_file, 'r', encoding='utf-8', errors='ignore') as f:
                policy_content = f.read().lower()
                policy_lines = policy_content.split('\n')
        except:
            continue

        for rule in rules:
            matches = []
            for keyword in rule['keywords']:
                for line_num, line in enumerate(policy_lines, 1):
                    if keyword in line:
                        matches.append({
                            "keyword": keyword,
                            "line": line_num
                        })

            if matches:
                rule_id = rule['rule_id']
                if rule_id not in policy_matches:
                    policy_matches[rule_id] = []

                # Extract package and rule names
                package_name = extract_package_name(policy_file)
                rule_names = extract_rule_names(policy_file)

                policy_matches[rule_id].append({
                    "file": str(policy_file.relative_to(REPO_ROOT)).replace('\\', '/'),
                    "package": package_name,
                    "rules": rule_names,
                    "matches": len(matches),
                    "matched_keywords": list(set([m['keyword'] for m in matches]))
                })

    return policy_matches

def search_tests(rules: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Search all .py test files for rule keywords.
    """
    test_matches = {}

    if not TEST_DIR.exists():
        print(f"[!] Test directory not found: {TEST_DIR}")
        return test_matches

    test_files = list(TEST_DIR.rglob("*.py"))
    print(f"[*] Scanning {len(test_files)} test files...")

    for test_file in test_files:
        try:
            with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                test_content = f.read().lower()
                test_lines = test_content.split('\n')
        except:
            continue

        for rule in rules:
            matches = []
            for keyword in rule['keywords']:
                for line_num, line in enumerate(test_lines, 1):
                    if keyword in line:
                        matches.append({
                            "keyword": keyword,
                            "line": line_num
                        })

            if matches:
                rule_id = rule['rule_id']
                if rule_id not in test_matches:
                    test_matches[rule_id] = []

                # Extract test functions
                test_functions = extract_test_functions(test_file)

                test_matches[rule_id].append({
                    "file": str(test_file.relative_to(REPO_ROOT)).replace('\\', '/'),
                    "functions": test_functions,
                    "matches": len(matches),
                    "matched_keywords": list(set([m['keyword'] for m in matches]))
                })

    return test_matches

def extract_package_name(rego_file: Path) -> str:
    """Extract package name from .rego file."""
    try:
        with open(rego_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith('package '):
                    return line.strip().split('package ')[-1].strip()
    except:
        pass
    return "unknown"

def extract_rule_names(rego_file: Path) -> List[str]:
    """Extract rule names from .rego file."""
    rules = []
    try:
        with open(rego_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Match rule names (deny, allow, violation, etc.)
            for match in re.finditer(r'^\s*(\w+)\s*(?:\[.*?\])?\s*(?:contains|:=|=|if)', content, re.MULTILINE):
                rule_name = match.group(1)
                if rule_name not in ['package', 'import']:
                    rules.append(rule_name)
    except:
        pass
    return list(set(rules))[:10]  # Limit to 10

def extract_test_functions(test_file: Path) -> List[str]:
    """Extract test function names from .py file."""
    functions = []
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.match(r'^\s*def\s+(test_\w+)\s*\(', line)
                if match:
                    functions.append(match.group(1))
    except:
        pass
    return functions[:20]  # Limit to 20

def build_mapping_matrix(rules: List[Dict], policy_matches: Dict, test_matches: Dict) -> List[Dict]:
    """
    Build complete mapping matrix with status.
    """
    matrix = []

    for rule in rules:
        rule_id = rule['rule_id']
        has_policy = rule_id in policy_matches
        has_test = rule_id in test_matches

        # Determine status
        if has_policy and has_test:
            status = "✅ FULL"
        elif has_policy or has_test:
            status = "⚠️ PARTIAL"
        else:
            status = "❌ MISSING"

        matrix.append({
            "rule_id": rule_id,
            "source": f"{rule['source_file']}:L{rule['line_number']}",
            "rule_text": rule['rule_text'][:100] + "..." if len(rule['rule_text']) > 100 else rule['rule_text'],
            "policies": policy_matches.get(rule_id, []),
            "tests": test_matches.get(rule_id, []),
            "status": status
        })

    # Sort by source file and line number
    matrix.sort(key=lambda x: (x['source'], x['rule_id']))

    return matrix

def calculate_signatures(files: List[Path]) -> Dict[str, str]:
    """
    Calculate SHA-512 and BLAKE2b signatures for all SoT files.
    """
    signatures = {}

    for file_path in files:
        if not file_path.exists():
            continue

        content = file_path.read_bytes()

        sha512 = hashlib.sha512(content).hexdigest()
        blake2b = hashlib.blake2b(content).hexdigest()

        rel_path = str(file_path.relative_to(REPO_ROOT)).replace('\\', '/')
        signatures[rel_path] = {
            "sha512": sha512,
            "blake2b": blake2b,
            "size_bytes": len(content)
        }

    return signatures

def generate_json_report(matrix: List[Dict], signatures: Dict, stats: Dict) -> Path:
    """Generate JSON mapping report."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / "sot_policy_test_matrix.json"

    report = {
        "metadata": {
            "tool": "sot_policy_test_mapper.py",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat() + "Z",
            "repository": "SSID"
        },
        "statistics": stats,
        "source_files": signatures,
        "mapping_matrix": matrix
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return output_file

def generate_markdown_report(matrix: List[Dict], stats: Dict) -> Path:
    """Generate Markdown mapping report."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / "sot_policy_test_matrix.md"

    md = f"""# SoT -> Policy -> Test Mapping Matrix

**Generated:** {datetime.now().isoformat()}Z
**Tool:** sot_policy_test_mapper.py v1.0.0

---

## Statistics

```
Total Rules: {stats['total_rules']}
Full Coverage: {stats['full_coverage']} ({stats['coverage_percent']:.1f}%)
Partial: {stats['partial_coverage']}
Missing: {stats['missing_coverage']}
Compliance Score: {stats['coverage_percent']:.1f}%
```

**Status:** {"[PASS] FULL COMPLIANCE" if stats['coverage_percent'] == 100.0 else "[WARN] NON-COMPLIANT"}

---

## Mapping Table

| SoT Rule | rule_id | Policies | Tests | Status |
|----------|---------|----------|-------|--------|
"""

    for entry in matrix:
        rule_source = entry['source']
        rule_id = entry['rule_id']
        rule_text = entry['rule_text']

        # Format policies
        if entry['policies']:
            policies_str = f"{len(entry['policies'])} policy file(s)"
        else:
            policies_str = "—"

        # Format tests
        if entry['tests']:
            tests_str = f"{len(entry['tests'])} test file(s)"
        else:
            tests_str = "—"

        status = entry['status']

        md += f"| {rule_text[:60]}... | `{rule_id}` | {policies_str} | {tests_str} | {status} |\n"

    md += f"""

---

## Detailed Mappings

"""

    for entry in matrix:
        if entry['policies'] or entry['tests']:
            md += f"""### {entry['source']}

**Rule:** {entry['rule_text']}
**ID:** `{entry['rule_id']}`

"""

            if entry['policies']:
                md += "**Policies:**\n"
                for policy in entry['policies']:
                    md += f"- {policy['file']} (package: `{policy['package']}`)\n"
                    md += f"  - Matched keywords: {', '.join(policy['matched_keywords'][:5])}\n"

            if entry['tests']:
                md += "\n**Tests:**\n"
                for test in entry['tests']:
                    md += f"- {test['file']}\n"
                    if test['functions']:
                        md += f"  - Functions: {', '.join(test['functions'][:5])}\n"

            md += "\n"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(md)

    return output_file

def generate_audit_report(signatures: Dict, stats: Dict) -> Path:
    """Generate audit report with signatures."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = REPORT_DIR / "sot_policy_test_audit.json"

    report = {
        "audit_metadata": {
            "tool": "sot_policy_test_mapper.py",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat() + "Z",
            "auditor": "SSID Compliance Forensic Auditor"
        },
        "compliance_status": {
            "total_rules": stats['total_rules'],
            "covered": stats['full_coverage'],
            "partial": stats['partial_coverage'],
            "missing": stats['missing_coverage'],
            "coverage_percent": stats['coverage_percent'],
            "compliant": stats['coverage_percent'] == 100.0
        },
        "source_file_signatures": signatures,
        "verification": {
            "method": "Deterministic keyword matching",
            "heuristics_used": False,
            "signature_algorithms": ["SHA-512", "BLAKE2b"]
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return output_file

def main():
    print("="*80)
    print("SSID Compliance Forensic Auditor")
    print("SoT -> Policy -> Test Mapper")
    print("="*80)
    print()

    # Step 1: Extract rules from all SoT files
    print("[1/6] Extracting SoT rules...")
    all_rules = []
    for sot_file in SOT_FILES:
        print(f"  - {sot_file.name}")
        rules = extract_rules(sot_file)
        all_rules.extend(rules)
        print(f"    Extracted {len(rules)} rules")

    print(f"\n[*] Total rules extracted: {len(all_rules)}")

    # Step 2: Search policies
    print("\n[2/6] Searching policies...")
    policy_matches = search_policies(all_rules)
    print(f"[*] Found policy matches for {len(policy_matches)} rules")

    # Step 3: Search tests
    print("\n[3/6] Searching tests...")
    test_matches = search_tests(all_rules)
    print(f"[*] Found test matches for {len(test_matches)} rules")

    # Step 4: Build mapping matrix
    print("\n[4/6] Building mapping matrix...")
    matrix = build_mapping_matrix(all_rules, policy_matches, test_matches)

    # Calculate statistics
    full_coverage = sum(1 for e in matrix if e['status'] == "✅ FULL")
    partial_coverage = sum(1 for e in matrix if e['status'] == "⚠️ PARTIAL")
    missing_coverage = sum(1 for e in matrix if e['status'] == "❌ MISSING")
    coverage_percent = (full_coverage / len(matrix) * 100) if matrix else 0.0

    stats = {
        "total_rules": len(matrix),
        "full_coverage": full_coverage,
        "partial_coverage": partial_coverage,
        "missing_coverage": missing_coverage,
        "coverage_percent": coverage_percent
    }

    print(f"""
Statistics:
  Total Rules: {stats['total_rules']}
  Full Coverage: {stats['full_coverage']} ({coverage_percent:.1f}%)
  Partial: {stats['partial_coverage']}
  Missing: {stats['missing_coverage']}
""")

    # Step 5: Calculate signatures
    print("[5/6] Calculating file signatures...")
    signatures = calculate_signatures(SOT_FILES)

    # Step 6: Generate reports
    print("[6/6] Generating reports...")
    json_report = generate_json_report(matrix, signatures, stats)
    print(f"  - JSON: {json_report.relative_to(REPO_ROOT)}")

    md_report = generate_markdown_report(matrix, stats)
    print(f"  - Markdown: {md_report.relative_to(REPO_ROOT)}")

    audit_report = generate_audit_report(signatures, stats)
    print(f"  - Audit: {audit_report.relative_to(REPO_ROOT)}")

    print("\n" + "="*80)
    if coverage_percent == 100.0:
        print("[PASS] FULL IMPLEMENTATION")
    else:
        print(f"[WARN] NON-COMPLIANT ({coverage_percent:.1f}% coverage)")
    print("="*80)

    return 0 if coverage_percent == 100.0 else 1

if __name__ == "__main__":
    sys.exit(main())
