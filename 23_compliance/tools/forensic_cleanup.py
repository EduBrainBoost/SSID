#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
forensic_cleanup.py - Forensic Artifact Cleanup Manager
Author: edubrainboost ©2025 MIT License

Implements artifact lifecycle management:
- Classifies artifacts by type (living code vs. temporary)
- Consolidates generated reports into monthly snapshots
- Archives temporary artifacts with SHA-256 verification
- Deletes only after successful archiving

Problem:
    - 72% of repository is generated artifacts (Knowledge Layer)
    - Reports, checksums, build artifacts accumulate unbounded
    - No automatic cleanup for temporary files

Solution:
    - Policy-driven artifact classification
    - Monthly snapshot consolidation (AUDIT_SNAPSHOT_YYYYMMDD.tar.gz)
    - Archive-then-delete strategy
    - Living code (28%) never touched

Usage:
    # Dry run (preview what would be cleaned)
    python 23_compliance/tools/forensic_cleanup.py

    # Execute cleanup
    python 23_compliance/tools/forensic_cleanup.py \
      --policy 24_meta_orchestration/registry/artifact_retention_policy.yaml \
      --execute

    # Consolidate reports only
    python 23_compliance/tools/forensic_cleanup.py \
      --consolidate-only \
      --execute
"""

import sys
import json
import hashlib
import tarfile
import fnmatch
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Set, Optional, Tuple
import argparse

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)


class ForensicCleanupManager:
    """Manage artifact lifecycle with forensic integrity."""

    def __init__(self, root_dir: Optional[Path] = None, policy_path: Optional[Path] = None):
        if root_dir is None:
            root_dir = Path(__file__).resolve().parents[2]

        self.root = root_dir
        self.policy = None
        self.snapshot_dir = root_dir / "02_audit_logging" / "archives" / "snapshots"
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

        if policy_path:
            self.policy = self.load_policy(policy_path)

    def load_policy(self, policy_path: Path) -> Dict:
        """Load artifact retention policy from YAML."""
        if not policy_path.exists():
            print(f"ERROR: Policy file not found: {policy_path}")
            sys.exit(1)

        with open(policy_path, 'r', encoding='utf-8') as f:
            policy = yaml.safe_load(f)

        print(f"Loaded policy: {policy_path}")
        print(f"  Version: {policy.get('version', 'unknown')}")
        print(f"  Mode: {policy['retention_strategy']['mode']}")
        print()

        return policy

    def classify_file(self, file_path: Path) -> Optional[str]:
        """
        Classify file by artifact type.

        Args:
            file_path: Path to classify

        Returns:
            Artifact type or None if excluded
        """
        if not self.policy:
            return None

        rel_path = str(file_path.relative_to(self.root)).replace("\\", "/")

        # Check exclusions first
        for exclusion_pattern in self.policy['exclusions']['permanent']:
            if fnmatch.fnmatch(rel_path, exclusion_pattern):
                return None

        # Check each artifact type
        for artifact_type, config in self.policy['artifact_types'].items():
            patterns = config.get('patterns', [])
            exclusions = config.get('exclusions', [])

            # Check if matches pattern
            if any(fnmatch.fnmatch(rel_path, pattern) for pattern in patterns):
                # Check if excluded
                if any(fnmatch.fnmatch(rel_path, excl) for excl in exclusions):
                    continue

                return artifact_type

        return None

    def get_file_age_days(self, file_path: Path) -> float:
        """Get file age in days."""
        mtime = file_path.stat().st_mtime
        file_datetime = datetime.fromtimestamp(mtime, tz=timezone.utc)
        age = datetime.now(timezone.utc) - file_datetime
        return age.total_seconds() / 86400

    def scan_artifacts(self) -> Dict[str, List[Path]]:
        """
        Scan repository and classify all artifacts.

        Returns:
            Dict mapping artifact types to file lists
        """
        print("Scanning repository for artifacts...")
        print()

        artifacts = {
            "living_code": [],
            "generated_reports": [],
            "checksums": [],
            "build_artifacts": [],
            "evidence_trails": [],
            "backup_artifacts": [],
            "shadow_material": [],
            "unclassified": []
        }

        total_files = 0
        classified_files = 0

        for file_path in self.root.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip .git directory
            if ".git" in file_path.parts:
                continue

            total_files += 1

            artifact_type = self.classify_file(file_path)

            if artifact_type:
                artifacts[artifact_type].append(file_path)
                classified_files += 1
            else:
                # Check if in excluded directory
                excluded = any(
                    excluded_dir in file_path.parts
                    for excluded_dir in self.policy['exclusions']['directories']
                )
                if not excluded:
                    artifacts["unclassified"].append(file_path)

        print(f"Total files scanned: {total_files}")
        print(f"Classified files: {classified_files}")
        print()

        return artifacts

    def get_cleanup_candidates(self, artifacts: Dict[str, List[Path]]) -> Dict[str, List[Path]]:
        """
        Identify artifacts eligible for cleanup based on retention policy.

        Args:
            artifacts: Classified artifacts

        Returns:
            Dict of cleanup candidates by type
        """
        candidates = {}

        for artifact_type, files in artifacts.items():
            if not files or artifact_type == "living_code":
                continue

            type_config = self.policy['artifact_types'].get(artifact_type, {})
            retention_days = type_config.get('retention_days')

            # Skip if permanent retention or managed externally
            if type_config.get('retention') == 'permanent':
                continue
            if type_config.get('managed_by'):
                continue

            # Filter by age
            if retention_days:
                candidates[artifact_type] = [
                    f for f in files
                    if self.get_file_age_days(f) > retention_days
                ]

        return candidates

    def consolidate_reports(
        self,
        reports: List[Path],
        snapshot_name: str
    ) -> Tuple[Path, Dict]:
        """
        Consolidate reports into monthly snapshot.

        Args:
            reports: List of report files
            snapshot_name: Name of snapshot archive

        Returns:
            Tuple of (snapshot_path, verification_dict)
        """
        snapshot_path = self.snapshot_dir / f"{snapshot_name}.tar.gz"

        print(f"Creating audit snapshot: {snapshot_path}")

        # Create snapshot archive
        with tarfile.open(snapshot_path, "w:gz") as tar:
            for report_path in reports:
                arcname = report_path.relative_to(self.root)
                tar.add(report_path, arcname=arcname)

        # Generate verification checksums
        checksums = {}
        for report_path in reports:
            with open(report_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                rel_path = str(report_path.relative_to(self.root))
                checksums[rel_path] = file_hash

        # Snapshot checksum
        with open(snapshot_path, 'rb') as f:
            snapshot_hash = hashlib.sha256(f.read()).hexdigest()

        verification = {
            "snapshot_path": str(snapshot_path.relative_to(self.root)),
            "snapshot_sha256": snapshot_hash,
            "snapshot_size_bytes": snapshot_path.stat().st_size,
            "file_count": len(reports),
            "file_checksums": checksums,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "immutable": True
        }

        # Write verification file
        verification_path = snapshot_path.with_suffix('.tar.gz.verify.json')
        with open(verification_path, 'w', encoding='utf-8') as f:
            json.dump(verification, f, indent=2)

        print(f"  Files consolidated: {len(reports)}")
        print(f"  Snapshot size: {snapshot_path.stat().st_size / (1024*1024):.2f} MB")
        print(f"  Verification: {verification_path}")
        print()

        return snapshot_path, verification

    def cleanup_artifacts(
        self,
        dry_run: bool = True,
        consolidate_only: bool = False
    ):
        """
        Execute forensic cleanup.

        Args:
            dry_run: If True, only preview actions
            consolidate_only: If True, only consolidate reports (no deletion)
        """
        print("=" * 70)
        print("Forensic Artifact Cleanup")
        print("=" * 70)
        print()

        if dry_run:
            print("[DRY RUN MODE - No changes will be made]")
            print()

        # Scan artifacts
        artifacts = self.scan_artifacts()

        # Print summary
        print("Artifact Distribution:")
        for artifact_type, files in artifacts.items():
            if files:
                total_size = sum(f.stat().st_size for f in files)
                print(f"  {artifact_type:20s}: {len(files):5d} files ({total_size / (1024*1024):8.2f} MB)")
        print()

        # Get cleanup candidates
        candidates = self.get_cleanup_candidates(artifacts)

        print("Cleanup Candidates:")
        total_candidates = 0
        for artifact_type, files in candidates.items():
            if files:
                total_size = sum(f.stat().st_size for f in files)
                print(f"  {artifact_type:20s}: {len(files):5d} files ({total_size / (1024*1024):8.2f} MB)")
                total_candidates += len(files)
        print()

        if total_candidates == 0:
            print("No artifacts eligible for cleanup (all within retention window)")
            return

        # Consolidate reports
        if not dry_run:
            # Consolidate generated reports
            if 'generated_reports' in candidates and candidates['generated_reports']:
                timestamp = datetime.now().strftime("%Y%m%d")
                snapshot_name = f"AUDIT_SNAPSHOT_{timestamp}"

                snapshot_path, verification = self.consolidate_reports(
                    candidates['generated_reports'],
                    snapshot_name
                )

            # Delete if not consolidate-only
            if not consolidate_only:
                print("Deleting archived artifacts...")
                deleted_count = 0

                for artifact_type, files in candidates.items():
                    type_config = self.policy['artifact_types'].get(artifact_type, {})

                    # Skip if archive_before_delete is False
                    if not type_config.get('archive_before_delete', True):
                        # Safe to delete without archiving (e.g., build artifacts)
                        for file_path in files:
                            file_path.unlink()
                            deleted_count += 1
                        continue

                    # Only delete if we created an archive
                    if artifact_type == 'generated_reports':
                        for file_path in files:
                            file_path.unlink()
                            deleted_count += 1

                print(f"Deleted {deleted_count} files")
                print()

        else:
            # Dry run - preview
            print("Would consolidate into audit snapshot:")
            if 'generated_reports' in candidates and candidates['generated_reports']:
                for file_path in candidates['generated_reports'][:10]:
                    age_days = self.get_file_age_days(file_path)
                    print(f"  {file_path.relative_to(self.root)} (age: {age_days:.1f} days)")

                if len(candidates['generated_reports']) > 10:
                    print(f"  ... and {len(candidates['generated_reports']) - 10} more")
            print()

        # Summary
        print("=" * 70)
        print("Summary")
        print("=" * 70)
        print()
        print(f"Living code:         {len(artifacts['living_code'])} files (never touched)")
        print(f"Generated reports:   {len(artifacts['generated_reports'])} files")
        print(f"Cleanup candidates:  {total_candidates} files")
        print()

        if dry_run:
            print("This was a DRY RUN. No changes were made.")
            print("Run with --execute to perform actual cleanup.")
        elif consolidate_only:
            print("Consolidation complete! (no deletion)")
        else:
            print("Cleanup complete!")

            # Write cleanup report
            self.write_cleanup_report(artifacts, candidates)

    def write_cleanup_report(self, artifacts: Dict, candidates: Dict):
        """Write cleanup report to audit trail."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_file = self.root / "02_audit_logging" / "evidence" / f"forensic_cleanup_{timestamp}.json"

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "policy_version": self.policy.get('version', 1) if self.policy else None,
            "artifact_distribution": {
                artifact_type: len(files)
                for artifact_type, files in artifacts.items()
            },
            "cleanup_candidates": {
                artifact_type: len(files)
                for artifact_type, files in candidates.items()
            },
            "snapshot_location": str(self.snapshot_dir.relative_to(self.root))
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"Cleanup report: {report_file}")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Forensic Artifact Cleanup Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be cleaned (default: dry-run)
  python forensic_cleanup.py

  # Execute cleanup with policy
  python forensic_cleanup.py \
    --policy 24_meta_orchestration/registry/artifact_retention_policy.yaml \
    --execute

  # Consolidate reports only (no deletion)
  python forensic_cleanup.py \
    --policy 24_meta_orchestration/registry/artifact_retention_policy.yaml \
    --consolidate-only \
    --execute
        """
    )

    parser.add_argument(
        "--policy",
        type=Path,
        default=Path("24_meta_orchestration/registry/artifact_retention_policy.yaml"),
        help="Path to artifact retention policy YAML"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview actions without executing (DEFAULT)"
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute cleanup (overrides dry-run)"
    )

    parser.add_argument(
        "--consolidate-only",
        action="store_true",
        help="Only consolidate reports (no deletion)"
    )

    args = parser.parse_args()

    # Determine dry-run mode
    dry_run = not args.execute

    # Execute cleanup
    manager = ForensicCleanupManager(policy_path=args.policy)
    manager.cleanup_artifacts(
        dry_run=dry_run,
        consolidate_only=args.consolidate_only
    )


if __name__ == "__main__":
    main()
