#!/usr/bin/env python3
"""
SSID No Raw Scores Lint (PROMPT 6)
Blocks any raw X/100 or X/400 scores not wrapped in SCORE_REF comments.
Exit 24: ROOT-24-LOCK violation detected
"""
import re
import sys
from pathlib import Path

# Pattern: matches X/100 or X/400 not in SCORE_REF context
RAW_SCORE_PATTERN = re.compile(r'(?:^|[^/\d])(\d{1,3})/(100|400)(?:[^%\d]|$)', re.MULTILINE)
SCORE_REF_PATTERN = re.compile(r'<!--\s*SCORE_REF:[^>]+-->')

def check_file(filepath):
    """Check file for raw scores. Returns (violations, lines)."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        return [], []

    lines = content.splitlines()
    violations = []

    for line_num, line in enumerate(lines, 1):
        # Skip if line contains SCORE_REF
        if SCORE_REF_PATTERN.search(line):
            continue

        # Check for raw scores
        matches = RAW_SCORE_PATTERN.finditer(line)
        for match in matches:
            score_value = match.group(1)
            scale_max = match.group(2)
            violations.append({
                "line": line_num,
                "score": f"{score_value}/{scale_max}",
                "text": line.strip()[:80]
            })

    return violations, lines

def main():
    """Main lint execution."""
    if len(sys.argv) < 2:
        print("[!] Usage: no_raw_scores.py <file1> [file2] ...")
        return 1

    files = [Path(f) for f in sys.argv[1:]]
    total_violations = 0

    for filepath in files:
        if not filepath.exists():
            continue

        # Skip non-text files
        if filepath.suffix not in ['.md', '.yaml', '.yml', '.json', '.txt']:
            continue

        # Skip existing .score.json files
        if ".score.json" in filepath.name:
            continue

        violations, _ = check_file(filepath)

        if violations:
            print(f"\n[FAIL] {filepath}")
            print(f"  Found {len(violations)} raw score(s) without SCORE_REF:")
            for v in violations:
                print(f"    Line {v['line']}: {v['score']} - {v['text']}")
            total_violations += len(violations)

    if total_violations > 0:
        print(f"\n[ROOT-24-LOCK VIOLATION]")
        print(f"  Total raw scores found: {total_violations}")
        print(f"  Action: Run score_manifest_migrator.py to canonize scores")
        return 24  # ROOT-24-LOCK exit code

    print("[OK] No raw scores found - all scores properly referenced")
    return 0

if __name__ == "__main__":
    sys.exit(main())
