#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
evidence_rolling_window.py - Rolling Evidence Window Manager
Author: edubrainboost ©2025 MIT License

Implements rolling evidence window with WORM archiving:
- Active window: Last 14 days OR last 10 builds
- Archive window: 12 months in WORM storage
- Permanent evidence: Never deleted (merkle roots, proof chains)

Problem:
    - 37,933 files in 02_audit_logging (unbounded growth)
    - Evidence accumulates from every CI run
    - No automatic cleanup mechanism

Solution:
    - Rolling window: Keep recent evidence active
    - WORM archive: Immutable historical storage
    - Selective retention: Permanent vs. temporary evidence

Usage:
    # Dry run (preview what would be archived/deleted)
    python 12_tooling/scripts/evidence_rolling_window.py --dry-run

    # Execute with policy
    python 12_tooling/scripts/evidence_rolling_window.py \
      --policy 24_meta_orchestration/registry/evidence_retention_policy.yaml \
      --execute
"""

import sys
import json
import hashlib
import tarfile
import fnmatch
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Tuple, Optional
import argparse

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required. Install with: pip install pyyaml")
    sys.exit(1)


class EvidenceRollingWindowManager:
    """Manage rolling evidence window with WORM archiving."""

    def __init__(self, root_dir: Optional[Path] = None, policy_path: Optional[Path] = None):
        if root_dir is None:
            root_dir = Path(__file__).resolve().parents[2]

        self.root = root_dir
        self.evidence_dir = root_dir / "02_audit_logging" / "evidence"
        self.archive_dir = root_dir / "02_audit_logging" / "archives" / "evidence"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Load policy
        self.policy = None
        if policy_path:
            self.policy = self.load_policy(policy_path)

    def load_policy(self, policy_path: Path) -> Dict:
        """Load evidence retention policy from YAML."""
        if not policy_path.exists():
            print(f"ERROR: Policy file not found: {policy_path}")
            sys.exit(1)

        with open(policy_path, 'r', encoding='utf-8') as f:
            policy = yaml.safe_load(f)

        print(f"Loaded policy: {policy_path}")
        print(f"  Version: {policy.get('version', 'unknown')}")
        print(f"  Active window: {policy['rolling_window']['active_retention_days']} days")
        print()

        return policy

    def is_permanent_evidence(self, file_path: Path) -> bool:
        """
        Check if file matches permanent evidence patterns.

        Args:
            file_path: Path to check

        Returns:
            True if file should be kept permanently
        """
        if not self.policy:
            return False

        rel_path = str(file_path.relative_to(self.evidence_dir)).replace("\\", "/")

        permanent_patterns = self.policy['rolling_window']['permanent_patterns']

        return any(fnmatch.fnmatch(rel_path, pattern) for pattern in permanent_patterns)

    def get_file_age_days(self, file_path: Path) -> float:
        """
        Get file age in days based on modification time.

        Args:
            file_path: Path to file

        Returns:
            Age in days
        """
        mtime = file_path.stat().st_mtime
        file_datetime = datetime.fromtimestamp(mtime, tz=timezone.utc)
        age = datetime.now(timezone.utc) - file_datetime

        return age.total_seconds() / 86400  # Convert to days

    def categorize_evidence(self) -> Dict[str, List[Path]]:
        """
        Categorize evidence files by retention status.

        Returns:
            Dict with categories: permanent, active, archive_candidate, delete_candidate
        """
        if not self.evidence_dir.exists():
            return {
                "permanent": [],
                "active": [],
                "archive_candidate": [],
                "delete_candidate": []
            }

        active_days = self.policy['rolling_window']['active_retention_days'] if self.policy else 14

        categories = {
            "permanent": [],
            "active": [],
            "archive_candidate": [],
            "delete_candidate": []
        }

        # Scan all files
        for file_path in self.evidence_dir.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip .gitkeep and .gitignore
            if file_path.name in [".gitkeep", ".gitignore"]:
                continue

            # Check if permanent
            if self.is_permanent_evidence(file_path):
                categories["permanent"].append(file_path)
                continue

            # Check age
            age_days = self.get_file_age_days(file_path)

            if age_days <= active_days:
                categories["active"].append(file_path)
            else:
                categories["archive_candidate"].append(file_path)

        return categories

    def create_worm_archive(
        self,
        files: List[Path],
        archive_name: str
    ) -> Tuple[Path, Dict]:
        """
        Create WORM (Write Once, Read Many) archive.

        Args:
            files: List of files to archive
            archive_name: Name of archive file

        Returns:
            Tuple of (archive_path, verification_dict)
        """
        archive_path = self.archive_dir / f"{archive_name}.tar.gz"

        # Create archive
        print(f"Creating WORM archive: {archive_path}")

        with tarfile.open(archive_path, "w:gz") as tar:
            for file_path in files:
                arcname = file_path.relative_to(self.evidence_dir)
                tar.add(file_path, arcname=arcname)

        # Generate verification checksums
        checksums = {}
        for file_path in files:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                rel_path = str(file_path.relative_to(self.evidence_dir))
                checksums[rel_path] = file_hash

        # Archive checksum
        with open(archive_path, 'rb') as f:
            archive_hash = hashlib.sha256(f.read()).hexdigest()

        verification = {
            "archive_path": str(archive_path.relative_to(self.root)),
            "archive_sha256": archive_hash,
            "archive_size_bytes": archive_path.stat().st_size,
            "file_count": len(files),
            "file_checksums": checksums,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "immutable": True
        }

        # Write verification file
        verification_path = archive_path.with_suffix('.tar.gz.verify.json')
        with open(verification_path, 'w', encoding='utf-8') as f:
            json.dump(verification, f, indent=2)

        print(f"  Files archived: {len(files)}")
        print(f"  Archive size: {archive_path.stat().st_size / 1024:.2f} KB")
        print(f"  Verification: {verification_path}")

        return archive_path, verification

    def generate_archive_index(self, archive_path: Path, verification: Dict) -> Path:
        """
        Generate searchable index for archive.

        Args:
            archive_path: Path to archive file
            verification: Verification dict

        Returns:
            Path to index file
        """
        index_path = archive_path.with_suffix('.tar.gz.index.json')

        index = {
            "archive": str(archive_path.name),
            "archive_sha256": verification["archive_sha256"],
            "created_at": verification["created_at"],
            "file_count": verification["file_count"],
            "files": list(verification["file_checksums"].keys())
        }

        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)

        return index_path

    def cleanup_evidence(
        self,
        dry_run: bool = True
    ):
        """
        Execute rolling window cleanup.

        Args:
            dry_run: If True, only preview actions
        """
        print("=" * 70)
        print("Evidence Rolling Window Cleanup")
        print("=" * 70)
        print()

        if dry_run:
            print("[DRY RUN MODE - No changes will be made]")
            print()

        # Categorize evidence
        print("Categorizing evidence files...")
        categories = self.categorize_evidence()

        print(f"  Permanent:         {len(categories['permanent'])} files")
        print(f"  Active (recent):   {len(categories['active'])} files")
        print(f"  Archive candidate: {len(categories['archive_candidate'])} files")
        print()

        if not categories['archive_candidate']:
            print("No files to archive (all within active window)")
            return

        # Create archive
        if not dry_run:
            timestamp = datetime.now().strftime("%Y%m%d")
            oldest_age = max(self.get_file_age_days(f) for f in categories['archive_candidate'])
            archive_name = f"evidence_archive_{timestamp}_last{int(oldest_age)}d"

            archive_path, verification = self.create_worm_archive(
                categories['archive_candidate'],
                archive_name
            )

            # Generate index
            index_path = self.generate_archive_index(archive_path, verification)
            print(f"  Index: {index_path}")
            print()

            # Delete archived files
            if self.policy and self.policy['cleanup_strategy'].get('require_worm_success', True):
                print("Deleting archived files...")
                for file_path in categories['archive_candidate']:
                    file_path.unlink()
                    print(f"  Deleted: {file_path.relative_to(self.evidence_dir)}")

                print()
                print(f"Deleted {len(categories['archive_candidate'])} files")
        else:
            print("Would archive and delete:")
            for file_path in categories['archive_candidate'][:10]:
                age_days = self.get_file_age_days(file_path)
                print(f"  {file_path.relative_to(self.evidence_dir)} (age: {age_days:.1f} days)")

            if len(categories['archive_candidate']) > 10:
                print(f"  ... and {len(categories['archive_candidate']) - 10} more")

            print()

        # Summary
        print("=" * 70)
        print("Summary")
        print("=" * 70)
        print()
        print(f"Permanent evidence:  {len(categories['permanent'])} files (never deleted)")
        print(f"Active evidence:     {len(categories['active'])} files (recent)")
        print(f"Archived:            {len(categories['archive_candidate'])} files")
        print()

        if dry_run:
            print("This was a DRY RUN. No changes were made.")
            print("Run with --execute to perform actual cleanup.")
        else:
            print("Cleanup complete!")

            # Write cleanup report
            self.write_cleanup_report(categories, archive_name if not dry_run else None)

    def write_cleanup_report(self, categories: Dict, archive_name: Optional[str]):
        """Write cleanup report to evidence directory."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_file = self.evidence_dir / f"evidence_cleanup_{timestamp}.json"

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "policy_version": self.policy.get('version', 1) if self.policy else None,
            "categories": {
                "permanent_count": len(categories['permanent']),
                "active_count": len(categories['active']),
                "archived_count": len(categories['archive_candidate'])
            },
            "archive_name": archive_name,
            "archive_location": str(self.archive_dir.relative_to(self.root)) if archive_name else None
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"Cleanup report: {report_file}")

    def generate_vital_signs(self):
        """Generate Evidence Vital Signs as cleanup byproduct."""
        try:
            # Import generator (avoid dependency if not installed)
            sys.path.insert(0, str(self.root / "12_tooling" / "quality"))
            from evidence_vital_signs_generator import EvidenceVitalSignsGenerator

            print()
            print("=" * 70)
            print("Evidence Vital Signs (Monthly Health Check)")
            print("=" * 70)
            print()

            generator = EvidenceVitalSignsGenerator(root_dir=self.root)
            vital_signs = generator.generate_vital_signs()

            md_path = generator.write_markdown_snapshot(vital_signs)
            json_path = generator.write_json_report(vital_signs)

            print(f"Overall Health: {vital_signs['overall_health']}")
            print(f"Markdown: {md_path}")
            print(f"JSON:     {json_path}")
            print()

        except ImportError:
            print("Evidence Vital Signs generator not available (optional)")
        except Exception as e:
            print(f"Warning: Could not generate vital signs: {e}")


def main():
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Evidence Rolling Window Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be archived (default: dry-run)
  python evidence_rolling_window.py

  # Execute cleanup with policy
  python evidence_rolling_window.py \
    --policy 24_meta_orchestration/registry/evidence_retention_policy.yaml \
    --execute

  # Execute without policy (14-day default)
  python evidence_rolling_window.py --execute
        """
    )

    parser.add_argument(
        "--policy",
        type=Path,
        help="Path to evidence retention policy YAML"
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

    args = parser.parse_args()

    # Determine dry-run mode
    dry_run = not args.execute

    # Execute cleanup
    manager = EvidenceRollingWindowManager(policy_path=args.policy)
    manager.cleanup_evidence(dry_run=dry_run)

    # Generate vital signs (monthly health check)
    if not dry_run:
        manager.generate_vital_signs()


if __name__ == "__main__":
    main()
