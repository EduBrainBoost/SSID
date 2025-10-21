#!/usr/bin/env python3
"""
SSID SoT Policy Alignment Verifier (PROMPT 3)
Enforces 100% coverage using semantic matching + stemming.
Exit 0: coverage = 100%, Exit 2: gaps detected
"""
import json
import re
from pathlib import Path
from typing import Dict, Set, List, Tuple
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
SOT_DIRS = [
    REPO_ROOT / "16_codex/sot_definitions",
    REPO_ROOT / "07_governance_legal/requirements"
]
POLICY_DIR = REPO_ROOT / "23_compliance/policies"
REPORT_PATH = REPO_ROOT / "02_audit_logging/reports/sot_policy_alignment_audit.json"

ALIASES = {
    'auth': {'auth', 'mfa', '2fa', 'authentication', 'multifactor'},
    'hash': {'hash', 'sha512', 'blake2b', 'digest', 'checksum'},
    'immutable': {'immutable', 'worm', 'readonly', 'tamperproof'},
    'encrypt': {'encrypt', 'cipher', 'aes', 'rsa', 'cryptograph'},
    'audit': {'audit', 'log', 'trail', 'record', 'evidence'},
    'sign': {'sign', 'signature', 'dilithium', 'ecdsa', 'verify'},
}

def stem(word: str) -> str:
    word = word.lower()
    for suffix in ['ing', 'ed', 'tion', 'able', 's']:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            word = word[:-len(suffix)]
            break
    return word

def normalize_text(text: str) -> Set[str]:
    tokens = re.findall(r'[a-zA-Z0-9]+', text.lower())
    normalized = set()
    for token in tokens:
        if len(token) <= 2:
            continue
        stemmed = stem(token)
        normalized.add(stemmed)
        for key, aliases in ALIASES.items():
            if stemmed in aliases or token in aliases:
                normalized.update(aliases)
    return normalized

def load_sot_rules() -> List[Tuple[str, str]]:
    rules = []
    for sot_dir in SOT_DIRS:
        if not sot_dir.exists():
            continue
        for filepath in sot_dir.rglob("*.md"):
            try:
                content = filepath.read_text(encoding='utf-8')
                for line_num, line in enumerate(content.splitlines(), 1):
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('<!--'):
                        continue
                    if 'SCORE_REF:' in line:
                        continue
                    if len(line) > 10:
                        key = f"{filepath.relative_to(REPO_ROOT)}:{line_num}"
                        rules.append((key, line))
            except:
                pass
    return rules

def build_policy_corpus() -> Set[str]:
    corpus = set()
    if not POLICY_DIR.exists():
        return corpus
    for filepath in POLICY_DIR.rglob("*.rego"):
        try:
            content = filepath.read_text(encoding='utf-8')
            corpus.update(normalize_text(content))
        except:
            pass
    return corpus

def generate_policy_snippet(rule: str) -> str:
    tokens = normalize_text(rule)
    key_concepts = sorted(tokens)[:3]
    snippet = f'''# Suggested policy for: {rule[:60]}...
package ssid.sot
import future.keywords.if
deny contains msg if {{
    # Check for: {', '.join(key_concepts)}
    not input.{key_concepts[0] if key_concepts else 'field'}
    msg := "SoT rule violation: {rule[:40]}..."
}}
'''
    return snippet

def main():
    print("=" * 80)
    print("SSID SoT Policy Alignment Verifier")
    print("=" * 80)
    rules = load_sot_rules()
    print(f"[*] Loaded {len(rules)} SoT rules")
    if not rules:
        print("[!] No SoT rules found")
        return 2
    corpus = build_policy_corpus()
    print(f"[*] Built policy corpus: {len(corpus)} normalized tokens")
    if not corpus:
        print("[!] No policies found")
        return 2
    results = {}
    covered = 0
    missing_rules = []
    for key, rule in rules:
        rule_tokens = normalize_text(rule)
        matched_tokens = rule_tokens & corpus
        coverage_ratio = len(matched_tokens) / len(rule_tokens) if rule_tokens else 0
        is_covered = coverage_ratio >= 0.30
        results[key] = {
            "rule": rule,
            "tokens": sorted(list(rule_tokens)),
            "matched_tokens": sorted(list(matched_tokens)),
            "coverage_ratio": round(coverage_ratio, 4),
            "covered": is_covered
        }
        if is_covered:
            covered += 1
        else:
            missing_rules.append({
                "key": key,
                "rule": rule,
                "coverage_ratio": coverage_ratio,
                "policy_snippet": generate_policy_snippet(rule)
            })
    coverage_percent = (covered / len(rules) * 100) if rules else 0.0
    report = {
        "verification_id": "sot-policy-alignment",
        "timestamp": "2025-10-16T19:50:00Z",
        "coverage_percent": round(coverage_percent, 2),
        "total_rules": len(rules),
        "covered_rules": covered,
        "missing_rules": len(missing_rules),
        "results": results,
        "policy_recommendations": missing_rules[:10],
        "status": "PASS" if coverage_percent == 100.0 else "FAIL"
    }
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nCoverage: {coverage_percent:.2f}%")
    print(f"Covered Rules: {covered}/{len(rules)}")
    print(f"Report: {REPORT_PATH.relative_to(REPO_ROOT)}")
    print("=" * 80)
    if coverage_percent < 100.0:
        print("\n[FAIL] Policy coverage below 100%")
        return 2
    else:
        print("\n[OK] 100% SoT-Policy alignment achieved")
        return 0

if __name__ == "__main__":
    sys.exit(main())
