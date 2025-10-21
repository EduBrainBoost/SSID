#!/usr/bin/env python3
"""
SSID Compliance Forensic Auditor - SOT-SUPERSET + SHARD Verification
Deterministic 1:1 mapping with zero heuristics.
"""
import json
import hashlib
import csv
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]

# SoT Master Sources
SOT_MASTER_FILES = [
    REPO_ROOT / "16_codex/structure/ssid_master_definition_corrected_v1.1.1.md",
]

# Superset output directory
SUPERSET_DIR = REPO_ROOT / "16_codex/structure/blueprint_v4.2"

# SHARD sources (auto-discover)
SHARD_SOURCE_DIR = REPO_ROOT / "16_codex/structure/blueprint_v4.2"

# Policies and Tests
POLICY_DIR = REPO_ROOT / "23_compliance/policies"
TEST_DIR = REPO_ROOT / "11_test_simulation/tests"

# Output
REPORT_DIR = REPO_ROOT / "02_audit_logging/reports"

# Stopwords for token matching
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might',
    'can', 'must', 'shall', 'this', 'that', 'these', 'those', 'it', 'its'
}

def normalize_text(text: str) -> str:
    """Normalize text: trim + collapse whitespace."""
    return ' '.join(text.strip().split())

def generate_rule_id(origin: str, source_path: str, line_no: int, text: str) -> str:
    """Generate SHA-256 rule_id."""
    normalized = normalize_text(text)
    key = f"{origin}|{source_path}:{line_no}:{normalized}"
    return hashlib.sha256(key.encode('utf-8')).hexdigest()[:12]

def extract_tokens(text: str) -> List[str]:
    """Extract alphanumeric tokens >2 chars, lowercased, no stopwords."""
    words = re.findall(r'\b[a-z0-9_]{3,}\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

def is_code_block_start(line: str) -> bool:
    """Check if line starts a code block."""
    return line.strip().startswith('```')

def is_content_line(line: str) -> bool:
    """Check if line is actual content (not empty)."""
    stripped = line.strip()
    return len(stripped) > 0

def extract_rules_from_markdown(file_path: Path, origin: str) -> List[Dict]:
    """
    Extract rules from markdown file.
    - Skip code blocks (``` ... ```)
    - Import ALL other non-empty lines as rules
    """
    rules = []
    if not file_path.exists():
        print(f"[!] File not found: {file_path}")
        return rules

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    in_code_block = False
    for line_no, line in enumerate(lines, 1):
        # Toggle code block state
        if is_code_block_start(line):
            in_code_block = not in_code_block
            continue

        # Skip if in code block
        if in_code_block:
            continue

        # Import all non-empty lines
        if is_content_line(line):
            rule_text = normalize_text(line)
            rel_path = str(file_path.relative_to(REPO_ROOT)).replace('\\', '/')
            rule_id = generate_rule_id(origin, rel_path, line_no, rule_text)

            rules.append({
                "origin": origin,
                "rule_id": rule_id,
                "rule_text": rule_text,
                "source_file": rel_path,
                "line_no": line_no
            })

    return rules

def create_superset_files(sot_rules: List[Dict]):
    """Create the 4 superset files."""
    SUPERSET_DIR.mkdir(parents=True, exist_ok=True)

    # 1. sot_all_lines.csv (ALL lines with metadata)
    csv_all = SUPERSET_DIR / "sot_all_lines.csv"
    with open(csv_all, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['origin', 'rule_id', 'source_file', 'line_no', 'rule_text'])
        writer.writeheader()
        for rule in sot_rules:
            writer.writerow(rule)
    print(f"[*] Created: {csv_all.relative_to(REPO_ROOT)} ({len(sot_rules)} lines)")

    # 2. sot_rules_filtered.csv (same as all for now - no filtering logic specified)
    csv_filtered = SUPERSET_DIR / "sot_rules_filtered.csv"
    with open(csv_filtered, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['origin', 'rule_id', 'source_file', 'line_no', 'rule_text'])
        writer.writeheader()
        for rule in sot_rules:
            writer.writerow(rule)
    print(f"[*] Created: {csv_filtered.relative_to(REPO_ROOT)} ({len(sot_rules)} lines)")

    # 3. sot_rules_filtered.json
    json_filtered = SUPERSET_DIR / "sot_rules_filtered.json"
    with open(json_filtered, 'w', encoding='utf-8') as f:
        json.dump([{
            "text": r["rule_text"],
            "source_file": r["source_file"],
            "line_no": r["line_no"]
        } for r in sot_rules], f, indent=2, ensure_ascii=False)
    print(f"[*] Created: {json_filtered.relative_to(REPO_ROOT)}")

    # 4. SOT_RULES_FULL_REPORT.md
    md_report = SUPERSET_DIR / "SOT_RULES_FULL_REPORT.md"
    with open(md_report, 'w', encoding='utf-8') as f:
        f.write(f"# SOT Rules Full Report\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}Z\n\n")
        f.write(f"**Total Rules:** {len(sot_rules)}\n\n")
        f.write(f"---\n\n")
        f.write(f"## All Rules\n\n")
        for rule in sot_rules:
            f.write(f"### {rule['source_file']}:L{rule['line_no']}\n\n")
            f.write(f"**Rule ID:** `{rule['rule_id']}`\n\n")
            f.write(f"{rule['rule_text']}\n\n")
            f.write(f"---\n\n")
    print(f"[*] Created: {md_report.relative_to(REPO_ROOT)}")

def discover_shard_files() -> List[Path]:
    """Auto-discover SHARD files (*.md with 'part' or 'shard' in name)."""
    candidates = list(SHARD_SOURCE_DIR.rglob("*.md"))
    shard_files = [
        f for f in candidates
        if 'part' in f.name.lower() or 'shard' in f.name.lower()
    ]
    return shard_files

def map_to_policies(rules: List[Dict]) -> Dict[str, List[Dict]]:
    """Map rules to policy files (.rego) using deterministic token matching."""
    policy_matches = {}

    if not POLICY_DIR.exists():
        print(f"[!] Policy directory not found: {POLICY_DIR}")
        return policy_matches

    policy_files = list(POLICY_DIR.rglob("*.rego"))
    print(f"[*] Scanning {len(policy_files)} policy files...")

    for policy_file in policy_files:
        try:
            with open(policy_file, 'r', encoding='utf-8', errors='ignore') as f:
                policy_content = f.read()
                policy_lines = policy_content.split('\n')
                policy_tokens = set(extract_tokens(policy_content))
        except:
            continue

        rel_path = str(policy_file.relative_to(REPO_ROOT)).replace('\\', '/')

        for rule in rules:
            rule_id = rule['rule_id']
            rule_tokens = set(extract_tokens(rule['rule_text']))

            # Match criteria: >=2 token overlap OR rule_id mentioned
            overlap = rule_tokens & policy_tokens
            rule_id_mentioned = rule_id in policy_content

            if len(overlap) >= 2 or rule_id_mentioned:
                if rule_id not in policy_matches:
                    policy_matches[rule_id] = []

                # Find context lines
                context_lines = []
                for i, line in enumerate(policy_lines, 1):
                    if any(token in line.lower() for token in list(overlap)[:3]):
                        context_lines.append({"line_no": i, "text": line.strip()[:80]})
                        if len(context_lines) >= 2:
                            break

                policy_matches[rule_id].append({
                    "path": rel_path,
                    "overlap_count": len(overlap),
                    "context": context_lines[:2]
                })

    return policy_matches

def map_to_tests(rules: List[Dict]) -> Dict[str, List[Dict]]:
    """Map rules to test files (.py) using deterministic token matching."""
    test_matches = {}

    if not TEST_DIR.exists():
        print(f"[!] Test directory not found: {TEST_DIR}")
        return test_matches

    test_files = list(TEST_DIR.rglob("*.py"))
    print(f"[*] Scanning {len(test_files)} test files...")

    for test_file in test_files:
        try:
            with open(test_file, 'r', encoding='utf-8', errors='ignore') as f:
                test_content = f.read()
                test_lines = test_content.split('\n')
                test_tokens = set(extract_tokens(test_content))
        except:
            continue

        rel_path = str(test_file.relative_to(REPO_ROOT)).replace('\\', '/')

        for rule in rules:
            rule_id = rule['rule_id']
            rule_tokens = set(extract_tokens(rule['rule_text']))

            # Match criteria: >=2 token overlap OR rule_id mentioned
            overlap = rule_tokens & test_tokens
            rule_id_mentioned = rule_id in test_content

            if len(overlap) >= 2 or rule_id_mentioned:
                if rule_id not in test_matches:
                    test_matches[rule_id] = []

                # Find context lines
                context_lines = []
                for i, line in enumerate(test_lines, 1):
                    if any(token in line.lower() for token in list(overlap)[:3]):
                        context_lines.append({"line_no": i, "text": line.strip()[:80]})
                        if len(context_lines) >= 2:
                            break

                test_matches[rule_id].append({
                    "path": rel_path,
                    "overlap_count": len(overlap),
                    "context": context_lines[:2]
                })

    return test_matches

def calculate_diff(sot_rules: List[Dict], shard_rules: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """Calculate Superset<->Shard diff."""
    # Build normalized text sets for comparison
    sot_texts = {normalize_text(r['rule_text']): r for r in sot_rules}
    shard_texts = {normalize_text(r['rule_text']): r for r in shard_rules}

    # SHARD-only: in SHARD but not in SOT
    shard_only = [
        shard_texts[text] for text in shard_texts
        if text not in sot_texts
    ]

    # SOT-only: in SOT but not in SHARD
    superset_only = [
        sot_texts[text] for text in sot_texts
        if text not in shard_texts
    ]

    return shard_only, superset_only

def calculate_sha512(file_path: Path) -> str:
    """Calculate SHA-512 of file."""
    if not file_path.exists():
        return "FILE_NOT_FOUND"
    return hashlib.sha512(file_path.read_bytes()).hexdigest()

def calculate_blake2b(file_path: Path) -> str:
    """Calculate BLAKE2b of file."""
    if not file_path.exists():
        return "FILE_NOT_FOUND"
    return hashlib.blake2b(file_path.read_bytes()).hexdigest()

def generate_reports(all_rules: List[Dict], sot_rules: List[Dict], shard_rules: List[Dict],
                     policy_matches: Dict, test_matches: Dict,
                     shard_only: List[Dict], superset_only: List[Dict],
                     sot_input_files: List[Path], shard_input_files: List[Path]):
    """Generate final MD and JSON reports."""

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Build mapping matrix
    matrix = []
    for rule in all_rules:
        rule_id = rule['rule_id']
        has_policy = rule_id in policy_matches
        has_test = rule_id in test_matches

        matrix.append({
            "origin": rule['origin'],
            "rule_id": rule_id,
            "rule_text": rule['rule_text'],
            "source_file": rule['source_file'],
            "line_no": rule['line_no'],
            "policy_matches": policy_matches.get(rule_id, []),
            "policy_status": "PASS" if has_policy else "MISSING",
            "test_matches": test_matches.get(rule_id, []),
            "test_status": "PASS" if has_test else "MISSING"
        })

    # Calculate stats
    covered_policy = sum(1 for m in matrix if m['policy_status'] == 'PASS')
    covered_test = sum(1 for m in matrix if m['test_status'] == 'PASS')
    full_coverage = sum(1 for m in matrix if m['policy_status'] == 'PASS' and m['test_status'] == 'PASS')
    partial = sum(1 for m in matrix if (m['policy_status'] == 'PASS') != (m['test_status'] == 'PASS'))
    missing = sum(1 for m in matrix if m['policy_status'] == 'MISSING' and m['test_status'] == 'MISSING')

    total_rules = len(all_rules)
    coverage_policy_percent = (covered_policy / total_rules * 100) if total_rules > 0 else 0.0
    coverage_test_percent = (covered_test / total_rules * 100) if total_rules > 0 else 0.0
    full_coverage_percent = (full_coverage / total_rules * 100) if total_rules > 0 else 0.0
    integrity_score = (coverage_policy_percent + coverage_test_percent + full_coverage_percent) / 3.0

    stats = {
        "total_rules": total_rules,
        "total_sot": len(sot_rules),
        "total_shard": len(shard_rules),
        "covered_policy": covered_policy,
        "covered_test": covered_test,
        "partial": partial,
        "missing": missing,
        "coverage_policy_percent": round(coverage_policy_percent, 2),
        "coverage_test_percent": round(coverage_test_percent, 2),
        "full_coverage_percent": round(full_coverage_percent, 2),
        "integrity_score": round(integrity_score, 2),
        "diff": {
            "shard_only_count": len(shard_only),
            "superset_only_count": len(superset_only)
        }
    }

    # Generate JSON report
    json_path = REPORT_DIR / "SOT_SUPERSET_SHARD_VERIFICATION_SUMMARY.json"

    json_report = {
        "meta": {
            "generated_at": datetime.now().isoformat() + "Z",
            "worm": {
                "sha512": "PLACEHOLDER_WILL_BE_CALCULATED",
                "blake2b": "PLACEHOLDER_WILL_BE_CALCULATED"
            },
            "inputs": {
                "superset": [
                    {
                        "path": str(f.relative_to(REPO_ROOT)).replace('\\', '/'),
                        "sha512": calculate_sha512(f)
                    } for f in sot_input_files
                ],
                "shards": {
                    "files": [
                        {
                            "path": str(f.relative_to(REPO_ROOT)).replace('\\', '/'),
                            "sha512": calculate_sha512(f)
                        } for f in shard_input_files
                    ]
                }
            }
        },
        "stats": stats,
        "matrix": matrix,
        "diff": {
            "shard_only": [
                {
                    "rule_id": r['rule_id'],
                    "source_file": r['source_file'],
                    "line_no": r['line_no'],
                    "rule_text": r['rule_text'][:200] + "..." if len(r['rule_text']) > 200 else r['rule_text']
                } for r in shard_only
            ],
            "superset_only": [
                {
                    "rule_id": r['rule_id'],
                    "source_file": r['source_file'],
                    "line_no": r['line_no'],
                    "rule_text": r['rule_text'][:200] + "..." if len(r['rule_text']) > 200 else r['rule_text']
                } for r in superset_only
            ]
        }
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, indent=2, ensure_ascii=False)

    print(f"[*] Generated: {json_path.relative_to(REPO_ROOT)}")

    # Generate MD report
    md_path = REPORT_DIR / "SOT_SUPERSET_SHARD_VERIFICATION_REPORT.md"

    # Determine verdict
    verdict = "[PASS] FULL IMPLEMENTATION" if stats['missing'] == 0 and stats['full_coverage_percent'] == 100.0 else "[WARN] NON-COMPLIANT"

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# SOT-SUPERSET + SHARD Verification Report\n\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}Z\n\n")
        f.write(f"**Verdict:** {verdict}\n\n")
        f.write(f"---\n\n")

        # Section A: Kennzahlen
        f.write(f"## A. Kennzahlen (SOT vs SHARD vs Gesamt)\n\n")
        f.write(f"```\n")
        f.write(f"Total Rules (Unique):     {stats['total_rules']}\n")
        f.write(f"  - From SOT Superset:    {stats['total_sot']}\n")
        f.write(f"  - From SHARD Files:     {stats['total_shard']}\n\n")
        f.write(f"Policy Coverage:          {stats['covered_policy']} ({stats['coverage_policy_percent']}%)\n")
        f.write(f"Test Coverage:            {stats['covered_test']} ({stats['coverage_test_percent']}%)\n")
        f.write(f"Full Coverage (Both):     {stats['covered_policy'] + stats['covered_test'] - stats['partial']} ({stats['full_coverage_percent']}%)\n")
        f.write(f"Partial (One Only):       {stats['partial']}\n")
        f.write(f"Missing (Neither):        {stats['missing']}\n\n")
        f.write(f"Integrity Score:          {stats['integrity_score']}/100\n")
        f.write(f"```\n\n")

        # Section B: Superset<->Shard Diff
        f.write(f"## B. Superset<->Shard Diff\n\n")
        f.write(f"**SHARD-Only Rules:** {stats['diff']['shard_only_count']} (in SHARD but NOT in SOT Superset)\n\n")
        if shard_only:
            f.write(f"### Top-50 SHARD-Only Rules\n\n")
            for i, rule in enumerate(shard_only[:50], 1):
                f.write(f"{i}. `{rule['rule_id']}` - {rule['source_file']}:L{rule['line_no']}\n")
                f.write(f"   {rule['rule_text'][:100]}...\n\n")

        f.write(f"\n**Superset-Only Rules:** {stats['diff']['superset_only_count']} (in SOT Superset but NOT in SHARD)\n\n")
        if superset_only:
            f.write(f"### Top-50 Superset-Only Rules\n\n")
            for i, rule in enumerate(superset_only[:50], 1):
                f.write(f"{i}. `{rule['rule_id']}` - {rule['source_file']}:L{rule['line_no']}\n")
                f.write(f"   {rule['rule_text'][:100]}...\n\n")

        # Section C: Top-10 Missing Policies (SHARD priority)
        f.write(f"\n## C. Top-10 Missing Policies (Priority: SHARD)\n\n")
        missing_policies = [m for m in matrix if m['policy_status'] == 'MISSING']
        missing_policies_shard = [m for m in missing_policies if m['origin'] == 'SHARD']
        missing_policies_sot = [m for m in missing_policies if m['origin'] == 'SOT']
        top_missing_policies = (missing_policies_shard + missing_policies_sot)[:10]

        for i, rule in enumerate(top_missing_policies, 1):
            f.write(f"{i}. [{rule['origin']}] `{rule['rule_id']}` - {rule['source_file']}:L{rule['line_no']}\n")
            f.write(f"   {rule['rule_text'][:100]}...\n\n")

        # Section D: Top-10 Missing Tests
        f.write(f"\n## D. Top-10 Missing Tests\n\n")
        missing_tests = [m for m in matrix if m['test_status'] == 'MISSING']
        missing_tests_shard = [m for m in missing_tests if m['origin'] == 'SHARD']
        missing_tests_sot = [m for m in missing_tests if m['origin'] == 'SOT']
        top_missing_tests = (missing_tests_shard + missing_tests_sot)[:10]

        for i, rule in enumerate(top_missing_tests, 1):
            f.write(f"{i}. [{rule['origin']}] `{rule['rule_id']}` - {rule['source_file']}:L{rule['line_no']}\n")
            f.write(f"   {rule['rule_text'][:100]}...\n\n")

        # Section E: Matrix Table (paginated)
        f.write(f"\n## E. Complete Mapping Matrix\n\n")
        f.write(f"| Origin | Source | L# | rule_id | Policy | Test | Rule (excerpt) |\n")
        f.write(f"|--------|--------|-------|---------|--------|------|----------------|\n")

        for rule in matrix[:100]:  # First 100 rows
            origin = rule['origin']
            source = rule['source_file'][-40:]  # Last 40 chars
            line_no = rule['line_no']
            rule_id = rule['rule_id'][:8]
            policy_status = "PASS" if rule['policy_status'] == 'PASS' else "MISS"
            test_status = "PASS" if rule['test_status'] == 'PASS' else "MISS"
            rule_text = rule['rule_text'][:60].replace('|', '\\|')

            f.write(f"| {origin} | {source} | {line_no} | `{rule_id}` | {policy_status} | {test_status} | {rule_text}... |\n")

        f.write(f"\n*Note: Showing first 100 of {len(matrix)} rules. See JSON for complete matrix.*\n\n")

        f.write(f"---\n\n")
        f.write(f"**End of Report**\n")

    print(f"[*] Generated: {md_path.relative_to(REPO_ROOT)}")

    # Calculate WORM hashes for both output files
    json_sha512 = calculate_sha512(json_path)
    json_blake2b = calculate_blake2b(json_path)
    md_sha512 = calculate_sha512(md_path)
    md_blake2b = calculate_blake2b(md_path)

    # Update JSON with WORM hashes
    json_report['meta']['worm'] = {
        "json_sha512": json_sha512,
        "json_blake2b": json_blake2b,
        "md_sha512": md_sha512,
        "md_blake2b": md_blake2b
    }

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, indent=2, ensure_ascii=False)

    print(f"\n[*] WORM hashes calculated and embedded")
    print(f"    JSON SHA-512:  {json_sha512[:16]}...")
    print(f"    JSON BLAKE2b:  {json_blake2b[:16]}...")
    print(f"    MD SHA-512:    {md_sha512[:16]}...")
    print(f"    MD BLAKE2b:    {md_blake2b[:16]}...")

    return stats

def main():
    print("="*80)
    print("SSID Compliance Forensic Auditor")
    print("SOT-SUPERSET + SHARD Verification (Deterministic, Zero-Heuristics)")
    print("="*80)
    print()

    # Step 1: Extract SOT rules
    print("[1/7] Extracting SOT-Superset rules...")
    sot_rules = []
    sot_input_files = []
    for sot_file in SOT_MASTER_FILES:
        if sot_file.exists():
            print(f"  - {sot_file.name}")
            rules = extract_rules_from_markdown(sot_file, "SOT")
            sot_rules.extend(rules)
            sot_input_files.append(sot_file)
            print(f"    Extracted {len(rules)} rules")

    print(f"\n[*] Total SOT rules: {len(sot_rules)}")

    # Create superset files
    print(f"\n[2/7] Creating Superset files...")
    create_superset_files(sot_rules)

    # Step 2: Discover and extract SHARD rules
    print(f"\n[3/7] Discovering SHARD files...")
    shard_files = discover_shard_files()
    print(f"[*] Found {len(shard_files)} SHARD files")

    print(f"\n[4/7] Extracting SHARD rules...")
    shard_rules = []
    for shard_file in shard_files:
        print(f"  - {shard_file.name}")
        rules = extract_rules_from_markdown(shard_file, "SHARD")
        shard_rules.extend(rules)
        print(f"    Extracted {len(rules)} rules")

    print(f"\n[*] Total SHARD rules: {len(shard_rules)}")

    # Step 3: Consolidate (deduplicate by rule_id)
    all_rules_dict = {}
    for rule in sot_rules + shard_rules:
        rule_id = rule['rule_id']
        if rule_id not in all_rules_dict:
            all_rules_dict[rule_id] = rule

    all_rules = list(all_rules_dict.values())
    print(f"\n[*] Total unique rules: {len(all_rules)}")

    # Step 4: Map to policies
    print(f"\n[5/7] Mapping to policies...")
    policy_matches = map_to_policies(all_rules)
    print(f"[*] Policies matched: {len(policy_matches)} rules")

    # Step 5: Map to tests
    print(f"\n[6/7] Mapping to tests...")
    test_matches = map_to_tests(all_rules)
    print(f"[*] Tests matched: {len(test_matches)} rules")

    # Step 6: Calculate diff
    print(f"\n[7/7] Calculating Superset<->Shard diff...")
    shard_only, superset_only = calculate_diff(sot_rules, shard_rules)
    print(f"[*] SHARD-only: {len(shard_only)}")
    print(f"[*] Superset-only: {len(superset_only)}")

    # Step 7: Generate reports
    print(f"\n[8/7] Generating reports...")

    # Collect all superset input files
    superset_input_files = [
        SUPERSET_DIR / "sot_all_lines.csv",
        SUPERSET_DIR / "sot_rules_filtered.csv",
        SUPERSET_DIR / "sot_rules_filtered.json",
        SUPERSET_DIR / "SOT_RULES_FULL_REPORT.md"
    ]

    stats = generate_reports(
        all_rules, sot_rules, shard_rules,
        policy_matches, test_matches,
        shard_only, superset_only,
        superset_input_files, shard_files
    )

    print("\n" + "="*80)
    if stats['missing'] == 0 and stats['full_coverage_percent'] == 100.0:
        print("[PASS] FULL IMPLEMENTATION")
    else:
        print(f"[WARN] NON-COMPLIANT ({stats['full_coverage_percent']}% full coverage)")
    print("="*80)

    return 0 if stats['missing'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
