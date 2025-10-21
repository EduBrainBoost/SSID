#!/usr/bin/env python3
"""
ROOT-IMMUNITY ENGINE v1.0
Persistent guard enforcing ROOT-24-LOCK at file system level
Blocks violations before they can be committed

Author: SSID Compliance System
License: MIT
"""

import sys
import os
import hashlib
import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime, timezone
import argparse

# Fix Windows console encoding
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

class RootImmunityDaemon:
    """
    Persistent guard enforcing ROOT-24-LOCK
    Prevents violations before they can be committed
    """

    def __init__(self, root_dir: Path, strict_mode: bool = False):
        self.root = root_dir
        self.strict_mode = strict_mode
        self.violations = []
        self.allowed_roots_cache = set()
        self.exception_paths = {}
        self.hash_cache = {}

        # Load configuration
        self._load_root_structure()
        self._load_exception_policy()
        self._build_hash_cache()

    def _load_root_structure(self) -> None:
        """Load root structure manifest (Single Source of Truth)"""
        manifest_path = self.root / '24_meta_orchestration' / 'registry' / 'root_structure_manifest.yaml'

        if not manifest_path.exists():
            # Generate default manifest
            self._generate_default_manifest(manifest_path)

        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)

        # Extract allowed roots
        if 'allowed_roots' in manifest:
            self.allowed_roots_cache = set(manifest['allowed_roots'])
        else:
            # Fallback: scan for 24 root directories
            self.allowed_roots_cache = self._scan_root_directories()

        print(f"[ROOT-IMMUNITY] Loaded {len(self.allowed_roots_cache)} allowed roots")

    def _generate_default_manifest(self, manifest_path: Path) -> None:
        """Generate default root structure manifest"""
        manifest_path.parent.mkdir(parents=True, exist_ok=True)

        # Scan for 24 root directories
        roots = self._scan_root_directories()

        manifest = {
            'version': '1.0',
            'generated': datetime.now(timezone.utc).isoformat(),
            'root_lock': 'ROOT-24-LOCK',
            'allowed_roots': sorted(list(roots)),
            'count': len(roots),
            'description': 'Single Source of Truth for ROOT-24-LOCK enforcement'
        }

        with open(manifest_path, 'w', encoding='utf-8') as f:
            yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True)

        print(f"[ROOT-IMMUNITY] Generated default manifest: {len(roots)} roots")

    def _scan_root_directories(self) -> Set[str]:
        """Scan repository for root directories"""
        roots = set()

        for item in self.root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Check if it matches XX_name pattern
                if re.match(r'^\d{2}_\w+$', item.name):
                    roots.add(item.name)

        return roots

    def _load_exception_policy(self) -> None:
        """Load exception policy for special paths like .claude"""
        policy_path = self.root / '24_meta_orchestration' / 'registry' / 'root_exception_policy.yaml'

        if not policy_path.exists():
            # Generate default policy
            self._generate_default_exception_policy(policy_path)

        with open(policy_path, 'r', encoding='utf-8') as f:
            policy = yaml.safe_load(f)

        # Parse exceptions
        if 'exceptions' in policy:
            for exception in policy['exceptions']:
                path = exception['path']
                allow_in_roots = exception.get('allow_in_roots', [])
                self.exception_paths[path] = {
                    'reason': exception.get('reason', ''),
                    'allow_in_roots': set(allow_in_roots)
                }

        print(f"[ROOT-IMMUNITY] Loaded {len(self.exception_paths)} exception paths")

    def _generate_default_exception_policy(self, policy_path: Path) -> None:
        """Generate default exception policy"""
        policy_path.parent.mkdir(parents=True, exist_ok=True)

        policy = {
            'version': '1.0',
            'generated': datetime.now(timezone.utc).isoformat(),
            'description': 'Exception policy for special paths',
            'exceptions': [
                {
                    'path': '.claude/',
                    'reason': 'AI context store (non-deployable)',
                    'allow_in_roots': ['16_codex', '20_foundation']
                },
                {
                    'path': '.git/',
                    'reason': 'Version control system',
                    'allow_in_roots': []  # Root level only
                },
                {
                    'path': '.github/',
                    'reason': 'GitHub Actions workflows',
                    'allow_in_roots': []  # Root level only
                },
                {
                    'path': '.gitignore',
                    'reason': 'Git ignore rules',
                    'allow_in_roots': []  # Root level only
                },
                {
                    'path': '.pre-commit-config.yaml',
                    'reason': 'Pre-commit hooks configuration',
                    'allow_in_roots': []  # Root level only
                },
                {
                    'path': 'README.md',
                    'reason': 'Repository documentation',
                    'allow_in_roots': []  # Root level only
                }
            ]
        }

        with open(policy_path, 'w', encoding='utf-8') as f:
            yaml.dump(policy, f, default_flow_style=False, allow_unicode=True)

        print(f"[ROOT-IMMUNITY] Generated default exception policy")

    def _build_hash_cache(self) -> None:
        """Build SHA-256 hash cache of allowed root paths"""
        for root in self.allowed_roots_cache:
            root_hash = hashlib.sha256(root.encode()).hexdigest()
            self.hash_cache[root_hash] = root

        print(f"[ROOT-IMMUNITY] Built hash cache: {len(self.hash_cache)} entries")

    def _normalize_path(self, path: Path) -> str:
        """
        Normalize path to OS-agnostic, lowercase format
        Returns: normalized relative path string
        """
        try:
            # Get relative path
            rel_path = path.relative_to(self.root)
        except ValueError:
            # Path outside root - try to make relative anyway
            try:
                resolved = path.resolve()
                root_resolved = self.root.resolve()
                rel_path = resolved.relative_to(root_resolved)
            except (ValueError, OSError):
                return str(path).replace("\\", "/").casefold()

        # Convert to forward slashes and lowercase
        return str(rel_path).replace("\\", "/").casefold()

    def check_path(self, path: Path) -> Tuple[bool, Optional[str]]:
        """
        Check if path violates ROOT-24-LOCK
        Returns: (is_allowed, violation_reason)
        """
        # Normalize path
        norm_path = self._normalize_path(path)

        # Convert to relative path
        try:
            rel_path = path.relative_to(self.root)
        except ValueError:
            return False, f"Path outside repository: {path}"

        # Get first component (root directory)
        parts = rel_path.parts
        if len(parts) == 0:
            return True, None  # Root directory itself

        first_part = parts[0].casefold()

        # Check for .claude/ directories with strict scoping
        if re.search(r'/\.claude(/|$)', norm_path, re.I):
            # .claude must be in an allowed root
            if len(parts) >= 2:
                parent_root = parts[0]
                # Check if .claude is allowed in this root
                claude_exception = self.exception_paths.get('.claude/', {})
                allowed_roots = claude_exception.get('allow_in_roots', set())
                if parent_root in allowed_roots:
                    return True, None
                else:
                    return False, f".claude/ not allowed in '{parent_root}' (only in: {allowed_roots})"
            else:
                return False, ".claude/ not allowed at root level"

        # Check if it's an exception path
        for exception_path, exception_config in self.exception_paths.items():
            norm_exception = exception_path.casefold()
            if norm_path.startswith(norm_exception) or first_part == norm_exception.rstrip('/'):
                # Check if exception is allowed at root level
                if len(exception_config['allow_in_roots']) == 0:
                    # Root level exception (like .git, .github)
                    if len(parts) == 1 or parts[0].casefold() == norm_exception.rstrip('/'):
                        return True, None
                    else:
                        return False, f"Exception path '{exception_path}' only allowed at root level"

                # Check if within allowed roots
                if len(parts) >= 2:
                    parent_root = parts[0]
                    if parent_root in exception_config['allow_in_roots']:
                        return True, None
                    else:
                        return False, f"Exception path '{exception_path}' not allowed in '{parent_root}'"

        # Check if first part is an allowed root (case-insensitive)
        for allowed_root in self.allowed_roots_cache:
            if first_part == allowed_root.casefold():
                return True, None

        # Check if it's a hidden file/directory at root
        if first_part.startswith('.'):
            # Check exception policy (case-insensitive)
            for exc_path in self.exception_paths.keys():
                norm_exc = exc_path.casefold()
                if first_part == norm_exc.rstrip('/') or (first_part + '/') == norm_exc:
                    return True, None
            return False, f"Hidden path '{first_part}' not in exception policy"

        # Violation detected
        return False, f"Path '{first_part}' not in allowed roots (ROOT-24-LOCK violation)"

    def scan_repository(self) -> List[Dict]:
        """Scan entire repository for ROOT-24-LOCK violations"""
        print("[ROOT-IMMUNITY] Scanning repository for violations...")

        violations = []

        for item in self.root.iterdir():
            if item.name == '.git':
                continue  # Skip .git directory

            is_allowed, reason = self.check_path(item)

            if not is_allowed:
                violations.append({
                    'type': 'ROOT-24-LOCK-VIOLATION',
                    'path': str(item.relative_to(self.root)),
                    'reason': reason,
                    'severity': 'CRITICAL',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })

        return violations

    def check_file_operation(self, operation: str, path: Path) -> bool:
        """
        Check if file operation is allowed
        Returns: True if allowed, False if blocked
        """
        is_allowed, reason = self.check_path(path)

        if not is_allowed:
            violation = {
                'type': 'ROOT-24-LOCK-VIOLATION',
                'operation': operation,
                'path': str(path.relative_to(self.root)),
                'reason': reason,
                'severity': 'CRITICAL',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'actor': os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
            }

            self.violations.append(violation)
            self._log_violation(violation)

            if self.strict_mode:
                print(f"❌ ROOT-LOCK VIOLATION: {operation} denied for {path.name}")
                print(f"   Reason: {reason}")
                raise SystemExit(f"ROOT-LOCK VIOLATION: Write denied for {path}")

            return False

        return True

    def _log_violation(self, violation: Dict) -> None:
        """Log violation to JSONL event log"""
        log_dir = self.root / '02_audit_logging' / 'reports'
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / 'root_immunity_events.jsonl'

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(violation, ensure_ascii=False) + '\n')

    def precommit_check(self) -> bool:
        """
        Pre-commit hook check
        Returns: True if all files pass, False if violations detected
        """
        print("=" * 80)
        print("ROOT-IMMUNITY ENGINE - Pre-Commit Check")
        print("=" * 80)
        print()

        # Scan repository
        violations = self.scan_repository()

        if violations:
            print(f"❌ {len(violations)} ROOT-24-LOCK VIOLATION(S) DETECTED")
            print()

            for v in violations:
                print(f"  - {v['path']}")
                print(f"    Reason: {v['reason']}")
                print()

            print("=" * 80)
            print("COMMIT ABORTED")
            print("=" * 80)
            print()
            print("Fix violations before committing:")
            print("  1. Move files to appropriate root directories")
            print("  2. Or add to exception policy if legitimate")
            print()

            # Log all violations
            for v in violations:
                self._log_violation(v)

            return False

        print("✅ All files comply with ROOT-24-LOCK")
        print()
        return True

    def ci_check(self) -> bool:
        """
        CI check mode
        Returns: True if compliant, False if violations
        """
        print("=" * 80)
        print("ROOT-IMMUNITY ENGINE - CI Check")
        print("=" * 80)
        print()

        # Scan repository
        violations = self.scan_repository()

        # Print summary
        print(f"Allowed Roots: {len(self.allowed_roots_cache)}")
        print(f"Exception Paths: {len(self.exception_paths)}")
        print(f"Violations: {len(violations)}")
        print()

        if violations:
            print("❌ ROOT-24-LOCK VIOLATIONS DETECTED")
            print()

            for v in violations:
                print(f"  [{v['severity']}] {v['path']}")
                print(f"    {v['reason']}")
                print()

            # Log violations
            for v in violations:
                self._log_violation(v)

            return False

        print("✅ ROOT-24-LOCK COMPLIANCE VERIFIED")
        return True

    def generate_report(self) -> Dict:
        """Generate compliance report"""
        violations = self.scan_repository()

        report = {
            'version': '1.0',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'root_lock': 'ROOT-24-LOCK',
            'allowed_roots': sorted(list(self.allowed_roots_cache)),
            'allowed_roots_count': len(self.allowed_roots_cache),
            'exception_paths': {
                path: {
                    'reason': config['reason'],
                    'allowed_in': list(config['allow_in_roots']) if config['allow_in_roots'] else ['root_level']
                }
                for path, config in self.exception_paths.items()
            },
            'violations': violations,
            'violation_count': len(violations),
            'compliant': len(violations) == 0,
            'hash_cache_entries': len(self.hash_cache)
        }

        return report

    def export_baseline(self) -> Dict:
        """Export current allowed root entries from policy"""
        print("=" * 80)
        print("ROOT-IMMUNITY ENGINE - Export Baseline")
        print("=" * 80)
        print()

        # Extract core 4-FILE-LOCK entries
        core_entries = []
        temp_entries = []
        scoped_entries = []

        for path, config in self.exception_paths.items():
            if len(config['allow_in_roots']) == 0:
                # Root-level exceptions
                if path in ['LICENSE', 'README.md', '.gitignore', '.github/']:
                    core_entries.append(path)
                else:
                    temp_entries.append(path)
            else:
                # Scoped exceptions
                scoped_entries.append({
                    'path': path,
                    'allowed_in': list(config['allow_in_roots'])
                })

        baseline = {
            'version': '1.0',
            'generated': datetime.now(timezone.utc).isoformat(),
            'policy_source': '24_meta_orchestration/registry/root_exception_policy.yaml',
            'core_4_file_lock': sorted(core_entries),
            'temporary_exceptions': sorted(temp_entries),
            'scoped_exceptions': scoped_entries,
            'allowed_root_directories': sorted(list(self.allowed_roots_cache))
        }

        print("Core 4-FILE-LOCK entries:")
        for entry in baseline['core_4_file_lock']:
            print(f"  ✅ {entry}")
        print()

        print("Temporary exceptions:")
        for entry in baseline['temporary_exceptions']:
            print(f"  ⚠️ {entry}")
        print()

        print("Scoped exceptions:")
        for entry in baseline['scoped_exceptions']:
            print(f"  🔒 {entry['path']} (only in: {', '.join(entry['allowed_in'])})")
        print()

        print(f"Total allowed ROOT-24-LOCK directories: {len(baseline['allowed_root_directories'])}")
        print()

        return baseline

    def clean_root(self, auto_mode: bool = False, policy_path: Optional[Path] = None) -> Dict:
        """
        Clean root directory by moving/removing violations

        Args:
            auto_mode: If True, execute cleanup automatically
            policy_path: Path to exception policy (default: use loaded policy)

        Returns:
            Cleanup report dict
        """
        print("=" * 80)
        print("ROOT-IMMUNITY ENGINE - Root Cleanup")
        print("=" * 80)
        print()

        if not auto_mode:
            print("⚠️ DRY-RUN MODE (use --auto to execute)")
            print()

        # Scan for violations
        violations = self.scan_repository()

        if len(violations) == 0:
            print("✅ No violations detected - root is clean")
            return {
                'status': 'CLEAN',
                'violations_found': 0,
                'actions_taken': []
            }

        print(f"Found {len(violations)} violations")
        print()

        actions = []
        moved = []
        deleted = []
        skipped = []

        for v in violations:
            path_str = v['path']
            path = self.root / path_str

            if not path.exists():
                skipped.append({
                    'path': path_str,
                    'reason': 'File no longer exists',
                    'action': 'SKIP'
                })
                continue

            # Determine action based on file type
            action = self._determine_cleanup_action(path)

            print(f"{'[DRY-RUN]' if not auto_mode else '[EXECUTE]'} {action['action']}: {path.name}")
            print(f"  → {action['destination'] if action['destination'] else 'DELETE'}")
            print()

            if auto_mode:
                success, message = self._execute_cleanup_action(path, action)
                action['success'] = success
                action['message'] = message

                if success:
                    if action['action'] == 'MOVE':
                        moved.append(action)
                    elif action['action'] == 'DELETE':
                        deleted.append(action)
                else:
                    skipped.append(action)

            actions.append(action)

        # Generate cleanup report
        report = {
            'status': 'EXECUTED' if auto_mode else 'DRY_RUN',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'violations_found': len(violations),
            'actions_planned': len(actions),
            'actions': actions,
            'moved': len(moved),
            'deleted': len(deleted),
            'skipped': len(skipped)
        }

        # Write report
        if auto_mode:
            report_file = self.root / '02_audit_logging' / 'reports' / 'root_cleanup_report.json'
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"✅ Cleanup report written: {report_file}")
            print()

        # Summary
        print("=" * 80)
        print("CLEANUP SUMMARY")
        print("=" * 80)
        print(f"Violations found: {len(violations)}")
        print(f"Moved: {len(moved)}")
        print(f"Deleted: {len(deleted)}")
        print(f"Skipped: {len(skipped)}")
        print()

        if auto_mode:
            # Re-scan to verify
            print("Re-scanning repository...")
            violations_after = self.scan_repository()
            print(f"✅ Violations after cleanup: {len(violations_after)}")
            report['violations_after_cleanup'] = len(violations_after)

        return report

    def _determine_cleanup_action(self, path: Path) -> Dict:
        """Determine cleanup action for a path"""
        name = path.name.lower()

        # Test artifacts → DELETE
        if name in ['.coverage', 'test_results.log', '.pytest_cache'] or name.endswith('.pyc'):
            return {
                'path': str(path.relative_to(self.root)),
                'action': 'DELETE',
                'destination': None,
                'reason': 'Test artifact'
            }

        # Archives → artifacts/
        if name.endswith('.zip') or name.endswith('.tar.gz'):
            dest = self.root / '24_meta_orchestration' / 'artifacts' / path.name
            return {
                'path': str(path.relative_to(self.root)),
                'action': 'MOVE',
                'destination': str(dest.relative_to(self.root)),
                'reason': 'Archive file'
            }

        # Documentation → docs/
        if name.endswith('.md') and name not in ['readme.md', 'license']:
            dest = self.root / '24_meta_orchestration' / 'docs' / path.name
            return {
                'path': str(path.relative_to(self.root)),
                'action': 'MOVE',
                'destination': str(dest.relative_to(self.root)),
                'reason': 'Documentation file'
            }

        # Health reports → audit reports/
        if 'health' in name or 'report' in name:
            dest = self.root / '02_audit_logging' / 'reports' / path.name
            return {
                'path': str(path.relative_to(self.root)),
                'action': 'MOVE',
                'destination': str(dest.relative_to(self.root)),
                'reason': 'Report file'
            }

        # Hidden files → requires manual decision
        if name.startswith('.'):
            return {
                'path': str(path.relative_to(self.root)),
                'action': 'SKIP',
                'destination': None,
                'reason': 'Hidden file - requires manual decision (whitelist or delete)'
            }

        # Default → move to 24_meta_orchestration/docs/
        dest = self.root / '24_meta_orchestration' / 'docs' / path.name
        return {
            'path': str(path.relative_to(self.root)),
            'action': 'MOVE',
            'destination': str(dest.relative_to(self.root)),
            'reason': 'Unclassified - moving to docs'
        }

    def _execute_cleanup_action(self, path: Path, action: Dict) -> Tuple[bool, str]:
        """Execute cleanup action"""
        try:
            if action['action'] == 'DELETE':
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.unlink()
                return True, f"Deleted {path.name}"

            elif action['action'] == 'MOVE':
                dest = self.root / action['destination']
                dest.parent.mkdir(parents=True, exist_ok=True)

                # Check if destination exists
                if dest.exists():
                    # Add timestamp to avoid collision
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    stem = dest.stem
                    suffix = dest.suffix
                    dest = dest.parent / f"{stem}_{timestamp}{suffix}"

                path.rename(dest)
                return True, f"Moved to {dest.relative_to(self.root)}"

            elif action['action'] == 'SKIP':
                return False, action['reason']

            return False, "Unknown action"

        except Exception as e:
            return False, f"Error: {str(e)}"

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='ROOT-IMMUNITY ENGINE v1.0')
    parser.add_argument('--precommit', action='store_true',
                       help='Pre-commit hook mode (exit 1 on violations)')
    parser.add_argument('--check', action='store_true',
                       help='CI check mode (exit 1 on violations)')
    parser.add_argument('--report', action='store_true',
                       help='Generate compliance report')
    parser.add_argument('--export-baseline', action='store_true',
                       help='Export allowed root entries from policy')
    parser.add_argument('--clean', action='store_true',
                       help='Clean root directory (dry-run by default)')
    parser.add_argument('--auto', action='store_true',
                       help='Execute cleanup automatically (use with --clean)')
    parser.add_argument('--policy', type=str,
                       help='Path to exception policy YAML')
    parser.add_argument('--strict', action='store_true',
                       help='Strict mode (block operations on violations)')
    args = parser.parse_args()

    root = Path(__file__).parent.parent.parent

    daemon = RootImmunityDaemon(root, strict_mode=args.strict)

    if args.precommit:
        success = daemon.precommit_check()
        sys.exit(0 if success else 1)

    elif args.check:
        success = daemon.ci_check()
        sys.exit(0 if success else 1)

    elif args.report:
        report = daemon.generate_report()

        # Write report to file
        report_file = root / '02_audit_logging' / 'reports' / 'root_immunity_scan.json'
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"✅ Report written: {report_file}")
        print(json.dumps(report, indent=2, ensure_ascii=False))

        sys.exit(0 if report['compliant'] else 1)

    elif args.export_baseline:
        baseline = daemon.export_baseline()

        # Write baseline to file
        baseline_file = root / '02_audit_logging' / 'reports' / 'root_baseline_export.json'
        baseline_file.parent.mkdir(parents=True, exist_ok=True)

        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)

        print(f"✅ Baseline exported: {baseline_file}")
        sys.exit(0)

    elif args.clean:
        policy_path = Path(args.policy) if args.policy else None
        report = daemon.clean_root(auto_mode=args.auto, policy_path=policy_path)

        if args.auto:
            # After cleanup, verify
            final_violations = report.get('violations_after_cleanup', 0)
            if final_violations == 0:
                print("✅ ROOT-24-LOCK: 100% COMPLIANT")
                sys.exit(0)
            else:
                print(f"⚠️ {final_violations} violations remaining")
                sys.exit(1)
        else:
            print("💡 Run with --auto to execute cleanup")
            sys.exit(0)

    else:
        # Default: scan and report
        print("=" * 80)
        print("ROOT-IMMUNITY ENGINE v1.0")
        print("=" * 80)
        print()

        violations = daemon.scan_repository()

        print(f"Allowed Roots: {len(daemon.allowed_roots_cache)}")
        print(f"Exception Paths: {len(daemon.exception_paths)}")
        print(f"Violations: {len(violations)}")
        print()

        if violations:
            print("Violations detected:")
            for v in violations:
                print(f"  - {v['path']}: {v['reason']}")
        else:
            print("✅ No violations detected")

        sys.exit(0 if len(violations) == 0 else 1)

if __name__ == "__main__":
    main()
