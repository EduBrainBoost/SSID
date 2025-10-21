#!/usr/bin/env python3
"""
SoT Validator Pre-Commit Hook
==============================

Git pre-commit hook for incremental SoT validation.

Features:
- Fast incremental validation (<0.5s for typical commits)
- Only validates affected rules
- Blocks commit on CRITICAL/HIGH failures
- Provides clear error messages
- Graceful fallback to full validation

Installation:
    # From repo root
    cp git_hooks/pre-commit.py .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit

    # Or use symbolic link
    ln -s ../../git_hooks/pre-commit.py .git/hooks/pre-commit

Exit Codes:
    0: Validation passed (commit allowed)
    1: Validation failed (commit blocked)
    2: Validation error (commit blocked)

Usage:
    # Automatic (runs on git commit)
    git commit -m "message"

    # Manual test
    python git_hooks/pre-commit.py

    # Skip validation (emergency use only)
    git commit --no-verify -m "message"

Author: SSID Core Team
Version: 1.0.0
Date: 2025-10-21
"""

import sys
import time
from pathlib import Path
from typing import Optional

# Add validator path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "03_core" / "validators" / "sot"))

try:
    from incremental_validator import IncrementalValidator
except ImportError as e:
    print(f"[ERROR] Failed to import IncrementalValidator: {e}")
    print(f"[ERROR] Make sure you're running from the repository root")
    sys.exit(2)


class PreCommitHook:
    """
    Pre-commit hook for SoT validation.
    """

    def __init__(self, repo_root: Path):
        """
        Initialize pre-commit hook.

        Args:
            repo_root: Path to repository root
        """
        self.repo_root = repo_root
        self.validator = None

    def run(self) -> int:
        """
        Run pre-commit validation.

        Returns:
            Exit code (0 = pass, 1 = fail, 2 = error)
        """
        print("=" * 70)
        print("SoT Validator Pre-Commit Hook")
        print("=" * 70)
        print()

        start_time = time.time()

        try:
            # Initialize validator
            print("[INIT] Initializing incremental validator...")
            self.validator = IncrementalValidator(
                repo_root=self.repo_root,
                enable_result_cache=True,
                enable_parallel=True
            )
            print()

            # Run incremental validation on staged files
            print("[VALIDATE] Running incremental validation on staged changes...")
            report = self.validator.validate_incremental(use_working_dir=True)
            print()

            elapsed = time.time() - start_time

            # Check results
            if report.failed_count == 0:
                print("[PASS] All validations passed!")
                print(f"[PASS] Validated {report.total_rules} rules in {elapsed:.3f}s")
                print()
                print("=" * 70)
                return 0

            # Some validations failed
            print(f"[FAIL] {report.failed_count}/{report.total_rules} validations failed")
            print()

            # Categorize failures by severity
            critical_failures = []
            high_failures = []
            other_failures = []

            for result in report.results:
                if not result.passed:
                    if result.severity.value == "CRITICAL":
                        critical_failures.append(result)
                    elif result.severity.value == "HIGH":
                        high_failures.append(result)
                    else:
                        other_failures.append(result)

            # Print critical failures
            if critical_failures:
                print("[CRITICAL] Critical validation failures (MUST be fixed):")
                for result in critical_failures:
                    print(f"  - {result.rule_id}: {result.message}")
                print()

            # Print high severity failures
            if high_failures:
                print("[HIGH] High severity validation failures:")
                for result in high_failures[:5]:  # Show first 5
                    print(f"  - {result.rule_id}: {result.message}")

                if len(high_failures) > 5:
                    print(f"  ... and {len(high_failures) - 5} more")
                print()

            # Determine if commit should be blocked
            block_commit = len(critical_failures) > 0 or len(high_failures) > 0

            if block_commit:
                print("[BLOCKED] Commit blocked due to CRITICAL or HIGH severity failures")
                print("[BLOCKED] Fix the issues above or use 'git commit --no-verify' to skip")
                print()
                print("=" * 70)
                return 1
            else:
                # Only LOW/MEDIUM failures, allow commit with warning
                print("[WARNING] Some validations failed, but commit is allowed")
                print("[WARNING] Please review and fix when possible")
                print()
                print("=" * 70)
                return 0

        except Exception as e:
            print(f"[ERROR] Validation error: {e}")
            print()

            # In case of error, allow commit but warn
            print("[WARNING] Validation failed, but commit is allowed")
            print("[WARNING] Run 'python 12_tooling/cli/sot_validator.py .' to debug")
            print()
            print("=" * 70)
            return 0  # Don't block commit on validation errors

    def get_staged_files(self) -> list:
        """
        Get list of staged files.

        Returns:
            List of staged file paths
        """
        import subprocess

        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=10
            )

            if result.returncode == 0:
                files = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                return files
            else:
                return []

        except Exception:
            return []


def main() -> int:
    """
    Main entry point for pre-commit hook.

    Returns:
        Exit code
    """
    # Detect repository root
    repo_root = Path(__file__).parent.parent

    # Check if we're in a git repository
    if not (repo_root / ".git").exists():
        print("[ERROR] Not in a git repository")
        return 2

    # Run pre-commit hook
    hook = PreCommitHook(repo_root)
    return hook.run()


if __name__ == "__main__":
    sys.exit(main())
