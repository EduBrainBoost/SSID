#!/usr/bin/env python3
"""
Placeholder Scanner (Gate 0) - SSID Codex Engine v2 + Policy Enforcement

Scans critical SoT areas for placeholder patterns and blocks CI if violations found.
Now integrates placeholder_policy.yaml for whitelist-based compliance management.

Critical Areas (Zero tolerance):
- 23_compliance/anti_gaming/ (fraud detection)
- 02_audit_logging/validators/ (audit validation)
- 08_identity_score/ (trust scoring)

Usage:
    python 12_tooling/placeholder_guard/placeholder_scan_v2.py
    python 12_tooling/placeholder_guard/placeholder_scan_v2.py --critical-only
    python 12_tooling/placeholder_guard/placeholder_scan_v2.py --json
    python 12_tooling/placeholder_guard/placeholder_scan_v2.py --policy 23_compliance/policies/placeholder_policy.yaml

Exit Codes:
    0: No violations found
    1: Violations detected (CI must fail)

Version: Sprint 2 Week 2 - Policy Enforcement
"""

import sys
import re
import json
import os
from pathlib import Path
from typing import List, Dict, Set, Optional
from fnmatch import fnmatch
from datetime import datetime, timezone


# Critical SoT areas - zero tolerance for placeholders
CRITICAL_AREAS = [
    '23_compliance/anti_gaming',
    '02_audit_logging/validators',
    '08_identity_score',
]

# Enhanced placeholder patterns
PATTERNS = [
    (re.compile(r"#\s*(TODO|FIXME|XXX|HACK|PLACEHOLDER)\b", re.IGNORECASE), "TODO-comment"),
    (re.compile(r"^\s*pass\s*$", re.MULTILINE), "pass-line"),
    (re.compile(r"\bassert\s+True\b"), "assert-true"),
    (re.compile(r"^\s*return\s+None\s*$", re.MULTILINE), "return-none-stub"),
    (re.compile(r"\braise\s+NotImplementedError"), "not-implemented"),
    (re.compile(r"def\s+\w+\([^)]*\)\s*:\s*pass\s*$", re.MULTILINE), "empty-function"),
]

# Legitimate exceptions
EXEMPT_INDICATORS = [
    '@abstractmethod',
    '@abc.abstractmethod',
    'class.*Protocol',
    '__init__.py',
    '.pyi',
]


def load_placeholder_policy(policy_path: str) -> Optional[Dict]:
    """
    Load placeholder policy from YAML file.

    Returns policy dict with 'allowed_placeholders' and 'forbidden_placeholders',
    or None if policy file doesn't exist or can't be loaded.
    """
    if not os.path.exists(policy_path):
        return None

    try:
        import yaml
        with open(policy_path, 'r', encoding='utf-8') as f:
            policy = yaml.safe_load(f) or {}
        return policy
    except ImportError:
        print("⚠️  Warning: PyYAML not installed, policy enforcement disabled", file=sys.stderr)
        return None
    except Exception as e:
        print(f"⚠️  Warning: Could not load policy: {e}", file=sys.stderr)
        return None


def load_allowlist(path: str) -> Set[str]:
    """Load allowlist from YAML file (legacy support)."""
    if not os.path.exists(path):
        return set()

    try:
        import yaml
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        return set(data.get('allowed_paths', []))
    except ImportError:
        print("⚠️  Warning: PyYAML not installed, allowlist disabled", file=sys.stderr)
        return set()
    except Exception as e:
        print(f"⚠️  Warning: Could not load allowlist: {e}", file=sys.stderr)
        return set()


def is_exempt(file_path: str, content: str, match_pos: int) -> bool:
    """Check if placeholder is in legitimate context."""
    # Check file patterns
    if '__init__.py' in file_path or file_path.endswith('.pyi'):
        return True

    # Check content context around match
    context_start = max(0, match_pos - 200)
    context_end = min(len(content), match_pos + 200)
    context = content[context_start:context_end]

    for indicator in EXEMPT_INDICATORS:
        if re.search(indicator, context):
            return True

    return False


def check_policy_compliance(file_path: str, snippet: str, policy: Optional[Dict]) -> Dict[str, any]:
    """
    Check if placeholder violates policy (allowed vs forbidden).

    Returns:
        {
            'status': 'ALLOWED' | 'FORBIDDEN' | 'UNKNOWN',
            'reason': str,
            'expires': Optional[str],
            'documented_in': Optional[str]
        }
    """
    if not policy:
        return {'status': 'UNKNOWN', 'reason': 'No policy loaded'}

    # Normalize file path for matching
    normalized_path = str(file_path).replace('\\', '/')

    # Check forbidden patterns first (takes precedence)
    for forbidden in policy.get('forbidden_placeholders', []):
        pattern = forbidden.get('pattern', '')
        forbidden_paths = forbidden.get('forbidden_paths', [])

        # Check if snippet matches forbidden pattern
        if re.search(pattern, snippet):
            # Check if file is in forbidden path
            for forbidden_path in forbidden_paths:
                # Convert glob pattern to match
                forbidden_glob = forbidden_path.replace('*/', '**/').replace('**/', '**')
                if fnmatch(normalized_path, forbidden_glob):
                    return {
                        'status': 'FORBIDDEN',
                        'reason': f"Forbidden in {forbidden_path}",
                        'severity': forbidden.get('severity', 'CRITICAL'),
                        'action': forbidden.get('action', 'BLOCK_COMMIT')
                    }

    # Check allowed patterns
    for allowed in policy.get('allowed_placeholders', []):
        pattern = allowed.get('pattern', '')
        exempt_paths = allowed.get('exempt_paths', [])

        # Check if snippet matches allowed pattern
        if re.search(pattern, snippet):
            # Check if file is in exempt path
            for exempt_path in exempt_paths:
                # Convert glob pattern to match
                exempt_glob = exempt_path.replace('*/', '**/').replace('**/', '**')
                if fnmatch(normalized_path, exempt_glob):
                    # Check expiry
                    expires = allowed.get('expires')
                    if expires:
                        try:
                            expiry_date = datetime.fromisoformat(expires.replace('Z', '+00:00'))
                            if datetime.now(timezone.utc) > expiry_date:
                                return {
                                    'status': 'EXPIRED',
                                    'reason': f"Policy expired on {expires}",
                                    'documented_in': allowed.get('documented_in')
                                }
                        except Exception:
                            pass  # Ignore date parsing errors

                    return {
                        'status': 'ALLOWED',
                        'reason': allowed.get('reason', 'Policy-whitelisted'),
                        'expires': expires,
                        'documented_in': allowed.get('documented_in'),
                        'audit_status': allowed.get('audit_status', 'ACCEPTABLE')
                    }

    # Not in policy
    return {'status': 'UNKNOWN', 'reason': 'Not in policy (requires justification)'}


def scan_file(file_path: str, allowlist: Set[str], policy: Optional[Dict] = None) -> List[Dict[str, any]]:
    """
    Scan single Python file for placeholders with policy enforcement.

    Args:
        file_path: Path to file to scan
        allowlist: Legacy allowlist (set of file paths)
        policy: Placeholder policy dict (if loaded)

    Returns:
        List of violations with policy compliance status
    """
    # Normalize path
    normalized = str(file_path).replace('\\', '/')

    # Check legacy allowlist
    if normalized in allowlist:
        return []

    violations = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [{
            'file': normalized,
            'line': 0,
            'type': 'read-error',
            'snippet': f'Error: {e}',
            'policy_status': 'UNKNOWN'
        }]

    # Scan for each pattern
    for pattern, violation_type in PATTERNS:
        for match in pattern.finditer(content):
            # Check if exempt
            if is_exempt(normalized, content, match.start()):
                continue

            # Calculate line number
            line_num = content[:match.start()].count('\n') + 1

            # Extract snippet (get more context for policy matching)
            # Need enough context to capture full NotImplementedError("...") strings
            snippet_start = max(0, match.start() - 100)
            snippet_end = min(len(content), match.end() + 200)
            full_snippet = content[snippet_start:snippet_end].strip()
            display_snippet = match.group(0).strip()[:80]

            # Check policy compliance
            policy_result = check_policy_compliance(normalized, full_snippet, policy)

            # Only add as violation if FORBIDDEN, EXPIRED, or UNKNOWN
            # ALLOWED placeholders are policy-compliant and not violations
            if policy_result['status'] in ['FORBIDDEN', 'EXPIRED', 'UNKNOWN']:
                violations.append({
                    'file': normalized,
                    'line': line_num,
                    'type': violation_type,
                    'snippet': display_snippet,
                    'policy_status': policy_result['status'],
                    'policy_reason': policy_result.get('reason'),
                    'severity': policy_result.get('severity', 'MEDIUM'),
                    'documented_in': policy_result.get('documented_in')
                })

    return violations


def scan_critical_areas(
    root: str = '.',
    critical_only: bool = True,
    allowlist_path: str = None,
    policy_path: str = None
) -> Dict[str, any]:
    """
    Scan critical SoT areas for placeholder violations with policy enforcement.

    Args:
        root: Repository root directory
        critical_only: If True, scan only critical areas; if False, scan full repo
        allowlist_path: Path to legacy allowlist YAML (optional)
        policy_path: Path to placeholder_policy.yaml (optional)

    Returns:
        Dict with scan results including policy compliance status
    """
    root_path = Path(root)
    allowlist = load_allowlist(allowlist_path) if allowlist_path else set()
    policy = load_placeholder_policy(policy_path) if policy_path else None

    all_violations = []
    files_scanned = 0
    policy_allowed_count = 0

    # Determine scan areas
    if critical_only:
        scan_areas = CRITICAL_AREAS
    else:
        scan_areas = ['.']  # Scan entire repo

    for area in scan_areas:
        area_path = root_path / area

        if not area_path.exists():
            continue

        # Scan all Python files in area
        for py_file in area_path.rglob('*.py'):
            files_scanned += 1
            violations = scan_file(py_file, allowlist, policy)
            all_violations.extend(violations)

    # Count violations by severity
    critical_violations = [v for v in all_violations if v.get('severity') == 'CRITICAL']
    high_violations = [v for v in all_violations if v.get('severity') == 'HIGH']
    medium_violations = [v for v in all_violations if v.get('severity') == 'MEDIUM']

    return {
        'files_scanned': files_scanned,
        'violations': all_violations,
        'violation_count': len(all_violations),
        'critical_violations': len(critical_violations),
        'high_violations': len(high_violations),
        'medium_violations': len(medium_violations),
        'critical_areas': CRITICAL_AREAS,
        'policy_enabled': policy is not None,
        'policy_path': policy_path if policy else None,
        'status': 'PASS' if len(all_violations) == 0 else 'FAIL'
    }


def format_report(results: Dict[str, any], output_format: str = 'text') -> str:
    """Format scan results with policy compliance information."""
    if output_format == 'json':
        return json.dumps(results, indent=2, ensure_ascii=False)

    # Human-readable text
    lines = []
    lines.append("=" * 80)
    lines.append("SSID Codex Engine - Placeholder Guard (Gate 0) - Policy Enforced")
    lines.append("=" * 80)
    lines.append(f"Files Scanned: {results['files_scanned']}")
    lines.append(f"Policy Enabled: {'YES' if results.get('policy_enabled') else 'NO (legacy mode)'}")
    if results.get('policy_path'):
        lines.append(f"Policy File: {results['policy_path']}")
    lines.append("")
    lines.append(f"Total Violations: {results['violation_count']}")
    if results.get('policy_enabled'):
        lines.append(f"  - CRITICAL: {results.get('critical_violations', 0)}")
        lines.append(f"  - HIGH: {results.get('high_violations', 0)}")
        lines.append(f"  - MEDIUM: {results.get('medium_violations', 0)}")
    lines.append(f"Status: {results['status']}")
    lines.append("")

    if results['violations']:
        lines.append("VIOLATIONS DETECTED:")
        lines.append("-" * 80)

        # Group by severity and file
        by_severity = {}
        for v in results['violations']:
            severity = v.get('severity', 'MEDIUM')
            by_severity.setdefault(severity, []).append(v)

        # Show CRITICAL first, then HIGH, then MEDIUM
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM']:
            if severity not in by_severity:
                continue

            lines.append(f"\n[{severity}] - {len(by_severity[severity])} violations")
            lines.append("-" * 40)

            # Group by file within severity
            by_file = {}
            for v in by_severity[severity]:
                by_file.setdefault(v['file'], []).append(v)

            for file_path, viols in sorted(by_file.items()):
                lines.append(f"\n  File: {file_path}")
                for v in viols:
                    lines.append(f"    Line {v['line']}: [{v['type']}]")
                    lines.append(f"      Code: {v['snippet']}")
                    if v.get('policy_status'):
                        lines.append(f"      Policy: {v['policy_status']} - {v.get('policy_reason', 'N/A')}")
                    if v.get('documented_in'):
                        lines.append(f"      Docs: {v['documented_in']}")

        lines.append("")
        lines.append("CI MUST FAIL - Placeholders violate policy")
    else:
        lines.append("No placeholder violations detected")
        lines.append("All critical SoT areas are production-ready")
        if results.get('policy_enabled'):
            lines.append("All placeholders are policy-compliant (whitelisted or eliminated)")

    lines.append("=" * 80)
    return "\n".join(lines)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Scan for placeholder violations in critical SoT areas (Gate 0) with policy enforcement'
    )
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--critical-only', action='store_true', default=True,
                        help='Scan only critical areas (default)')
    parser.add_argument('--full', action='store_true',
                        help='Scan entire repository')
    parser.add_argument('--root', default='.', help='Repository root')
    parser.add_argument('--allowlist',
                        default='12_tooling/placeholder_guard/allowlist_paths.yaml',
                        help='Path to legacy allowlist YAML')
    parser.add_argument('--policy',
                        default='23_compliance/policies/placeholder_policy.yaml',
                        help='Path to placeholder policy YAML')

    args = parser.parse_args()

    try:
        if not args.json:
            # Human-readable mode with headers
            print("Scanning critical SoT areas for placeholders...", file=sys.stderr)
            if os.path.exists(args.policy):
                print(f"Policy enforcement: ENABLED ({args.policy})", file=sys.stderr)
            else:
                print("Policy enforcement: DISABLED (legacy mode)", file=sys.stderr)

        # Scan
        results = scan_critical_areas(
            root=args.root,
            critical_only=not args.full,
            allowlist_path=args.allowlist,
            policy_path=args.policy
        )

        # Output results
        report = format_report(results, 'json' if args.json else 'text')
        print(report)

        # Exit with appropriate code
        if results['status'] == 'PASS':
            if not args.json:
                print("\nGate 0: PASS", file=sys.stderr)
            sys.exit(0)
        else:
            if not args.json:
                print(f"\nGate 0: FAIL - {results['violation_count']} violations", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error during scan: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
