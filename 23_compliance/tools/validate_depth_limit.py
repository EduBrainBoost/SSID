#!/usr/bin/env python3
"""
Maximum Depth Limit Validator (v1.0)

Enforces MUST-010-DEPTH-LIMIT requirement: Directory depth must not exceed 3 levels.

Compliance: DORA Art.6 (ICT Risk Management), GDPR Art.25 (Privacy by Design)

Usage:
    python3 23_compliance/tools/validate_depth_limit.py
    python3 23_compliance/tools/validate_depth_limit.py --max-depth 3
    python3 23_compliance/tools/validate_depth_limit.py --json
    python3 23_compliance/tools/validate_depth_limit.py --fix
"""

import os
import json
import yaml
import sys
import hashlib
import fnmatch
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

class DepthLimitValidator:
    """Validates directory structure against maximum depth policy."""

    def __init__(self, repo_root: str = ".", max_depth: int = 3):
        self.repo_root = Path(repo_root).resolve()
        self.max_depth = max_depth
        self.violations: List[Dict[str, Any]] = []
        self.exceptions: List[Dict[str, Any]] = []
        self.stats = {
            "total_paths": 0,
            "compliant_paths": 0,
            "violation_paths": 0,
            "exempted_paths": 0,
            "max_depth_found": 0
        }

        # Load policy and exceptions
        self.policy = self._load_policy()
        self.exception_patterns = self._load_exceptions()

    def _load_policy(self) -> Dict:
        """Load max depth policy configuration."""
        policy_file = self.repo_root / "23_compliance/policies/max_depth_policy.yaml"
        if policy_file.exists():
            with open(policy_file, 'r', encoding='utf-8') as f:
                policy = yaml.safe_load(f)
                # Override max_depth if specified in policy
                if 'depth_constraints' in policy and 'max_depth' in policy['depth_constraints']:
                    self.max_depth = policy['depth_constraints']['max_depth']
                return policy
        return {}

    def _load_exceptions(self) -> List[str]:
        """Load exception patterns from policy."""
        patterns = []
        if 'exceptions' in self.policy and 'allowed_deep_paths' in self.policy['exceptions']:
            for exc in self.policy['exceptions']['allowed_deep_paths']:
                patterns.append(exc['pattern'])
        return patterns

    def _calculate_depth(self, path: Path) -> int:
        """
        Calculate directory depth relative to repository root.

        Root level = 0
        First numbered directory (01_ai_layer) = 1
        Subdirectories = 2, 3, 4, ...
        """
        try:
            rel_path = path.relative_to(self.repo_root)
            # Count directory separators
            depth = len(rel_path.parts)
            return depth
        except ValueError:
            # Path is not relative to repo_root
            return 0

    def _is_exempted(self, path: Path) -> bool:
        """Check if path matches any exception pattern."""
        rel_path_str = str(path.relative_to(self.repo_root)).replace('\\', '/')

        for pattern in self.exception_patterns:
            # Remove trailing /** for fnmatch
            match_pattern = pattern.replace('/**', '/*')
            if fnmatch.fnmatch(rel_path_str, match_pattern) or rel_path_str.startswith(pattern.replace('/**', '')):
                return True
        return False

    def scan_directory(self) -> None:
        """Scan repository for depth violations."""
        print(f"[INFO] Scanning repository: {self.repo_root}", file=sys.stderr)
        print(f"[INFO] Max depth allowed: {self.max_depth}", file=sys.stderr)

        # Walk directory tree
        for root, dirs, files in os.walk(self.repo_root):
            root_path = Path(root)

            # Skip .git and other hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            # Calculate depth
            depth = self._calculate_depth(root_path)
            self.stats["total_paths"] += 1

            # Track max depth
            if depth > self.stats["max_depth_found"]:
                self.stats["max_depth_found"] = depth

            # Check exemptions
            if self._is_exempted(root_path):
                self.stats["exempted_paths"] += 1
                self.exceptions.append({
                    "path": str(root_path.relative_to(self.repo_root)),
                    "depth": depth,
                    "status": "EXEMPTED"
                })
                continue

            # Check depth violation
            if depth > self.max_depth:
                self.stats["violation_paths"] += 1
                severity = self._calculate_severity(depth)

                violation = {
                    "path": str(root_path.relative_to(self.repo_root)),
                    "depth": depth,
                    "max_allowed": self.max_depth,
                    "excess_depth": depth - self.max_depth,
                    "severity": severity,
                    "violation_type": "depth_limit_exceeded",
                    "recommendation": self._generate_recommendation(root_path, depth)
                }
                self.violations.append(violation)
            else:
                self.stats["compliant_paths"] += 1

    def _calculate_severity(self, depth: int) -> str:
        """Calculate violation severity based on excess depth."""
        excess = depth - self.max_depth

        if excess >= 3:
            return "CRITICAL"
        elif excess == 2:
            return "HIGH"
        elif excess == 1:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_recommendation(self, path: Path, depth: int) -> str:
        """Generate remediation recommendation for violation."""
        excess = depth - self.max_depth

        if excess == 1:
            return f"Flatten by 1 level: Consider consolidating subdirectories"
        elif excess == 2:
            return f"Flatten by 2 levels: Merge nested structures or use flat naming (e.g., module_submodule_file.py)"
        elif excess >= 3:
            return f"Major refactoring required: Move to separate module or archive as legacy"
        else:
            return "No action required"

    def generate_report(self, output_format: str = "human") -> str:
        """Generate validation report."""
        report = {
            "metadata": {
                "generated": datetime.now().replace(microsecond=0).isoformat() + "Z",
                "validator_version": "1.0.0",
                "requirement_id": "MUST-010-DEPTH-LIMIT",
                "repo_root": str(self.repo_root),
                "max_depth_policy": self.max_depth
            },
            "summary": self.stats,
            "violations": self.violations,
            "exemptions": self.exceptions[:10],  # Limit to 10 for readability
            "compliance_status": "PASS" if len(self.violations) == 0 else "FAIL"
        }

        if output_format == "json":
            return json.dumps(report, indent=2, ensure_ascii=False)
        elif output_format == "yaml":
            return yaml.dump(report, default_flow_style=False, allow_unicode=True)
        else:
            return self._format_human_readable(report)

    def _format_human_readable(self, report: Dict) -> str:
        """Format report for human reading."""
        lines = []
        lines.append("=" * 80)
        lines.append("Maximum Depth Limit Validation Report")
        lines.append("=" * 80)
        lines.append(f"Generated: {report['metadata']['generated']}")
        lines.append(f"Requirement: {report['metadata']['requirement_id']}")
        lines.append(f"Max Depth Policy: {report['metadata']['max_depth_policy']} levels")
        lines.append("")

        lines.append("SUMMARY")
        lines.append("-" * 80)
        lines.append(f"Total paths scanned: {report['summary']['total_paths']}")
        lines.append(f"Compliant paths: {report['summary']['compliant_paths']}")
        lines.append(f"Violation paths: {report['summary']['violation_paths']}")
        lines.append(f"Exempted paths: {report['summary']['exempted_paths']}")
        lines.append(f"Max depth found: {report['summary']['max_depth_found']}")
        lines.append(f"Status: {report['compliance_status']}")
        lines.append("")

        if report['violations']:
            # Group violations by severity
            by_severity = {}
            for v in report['violations']:
                sev = v['severity']
                by_severity.setdefault(sev, []).append(v)

            lines.append("VIOLATIONS")
            lines.append("-" * 80)

            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                if severity in by_severity:
                    lines.append(f"\n{severity} ({len(by_severity[severity])} violations):")
                    for v in by_severity[severity][:5]:  # Show top 5 per severity
                        lines.append(f"  Path: {v['path']}")
                        lines.append(f"    Depth: {v['depth']} (max: {v['max_allowed']}, excess: {v['excess_depth']})")
                        lines.append(f"    Recommendation: {v['recommendation']}")
                        lines.append("")

            if len(report['violations']) > 20:
                lines.append(f"... and {len(report['violations']) - 20} more violations")
                lines.append("")

        if report['exemptions']:
            lines.append("EXEMPTIONS (Sample)")
            lines.append("-" * 80)
            for exc in report['exemptions'][:10]:
                lines.append(f"  {exc['path']} (depth: {exc['depth']})")
            lines.append("")

        lines.append("=" * 80)
        if report['compliance_status'] == "PASS":
            lines.append("[PASS] COMPLIANCE STATUS: PASS")
        else:
            lines.append("[FAIL] COMPLIANCE STATUS: FAIL")
            lines.append(f"   {len(report['violations'])} violation(s) must be resolved")
        lines.append("=" * 80)

        return "\n".join(lines)

    def save_evidence(self, report_data: Dict) -> Path:
        """Save validation evidence to audit trail."""
        evidence_dir = self.repo_root / "23_compliance/evidence/depth_limit"
        evidence_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        evidence_file = evidence_dir / f"depth_validation_{timestamp}.json"

        # Add evidence hash
        report_hash = hashlib.sha256(
            json.dumps(report_data, sort_keys=True).encode()
        ).hexdigest()

        evidence = {
            "validation_report": report_data,
            "audit_metadata": {
                "timestamp": report_data['metadata']['generated'],
                "report_hash_sha256": report_hash,
                "validator_version": "1.0.0",
                "compliance_requirement": "MUST-010-DEPTH-LIMIT"
            }
        }

        with open(evidence_file, 'w', encoding='utf-8') as f:
            json.dump(evidence, f, indent=2, ensure_ascii=False)

        print(f"[OK] Evidence saved: {evidence_file}", file=sys.stderr)
        return evidence_file

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Validate directory depth limits')
    parser.add_argument('--max-depth', type=int, default=3, help='Maximum allowed depth (default: 3)')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--yaml', action='store_true', help='Output YAML format')
    parser.add_argument('--save', action='store_true', help='Save evidence to file')
    parser.add_argument('--fail-on-violation', action='store_true', help='Exit with code 1 on violations')

    args = parser.parse_args()

    # Determine output format
    if args.json:
        output_format = 'json'
    elif args.yaml:
        output_format = 'yaml'
    else:
        output_format = 'human'

    try:
        # Create validator
        validator = DepthLimitValidator(max_depth=args.max_depth)

        # Scan directory
        validator.scan_directory()

        # Generate report
        report_str = validator.generate_report(output_format)

        # Parse back for saving evidence
        if output_format == 'json':
            report_data = json.loads(report_str)
        else:
            # Generate JSON version for evidence
            report_data = json.loads(validator.generate_report('json'))

        # Save evidence if requested
        if args.save:
            validator.save_evidence(report_data)

        # Print report
        print(report_str)

        # Exit with appropriate code
        if args.fail_on_violation and len(validator.violations) > 0:
            print(f"\n[FAIL] Found {len(validator.violations)} depth violations", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"\n[OK] Validation complete. Violations: {len(validator.violations)}", file=sys.stderr)
            sys.exit(0)

    except Exception as e:
        print(f"[ERROR] Validation failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
