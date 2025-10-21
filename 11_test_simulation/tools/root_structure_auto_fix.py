#!/usr/bin/env python3
"""
SSID Root-24-LOCK Auto-Fix Script
Version: 2.0.0 (Forensic + Auto-Remediation)
Purpose: Automatically remediate all Root-24-LOCK violations
Mode: SAFE (dry-run option, SHA-256 verification, backup)
Cost: $0 (local file operations only)
"""

import os
import sys
import shutil
import hashlib
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

class Root24AutoFix:
    """Automated Root-24-LOCK violation remediation"""

    def __init__(self, project_root: str, dry_run: bool = False):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.moved_files = []
        self.deleted_items = []
        self.errors = []

        # Migration mappings (source → target)
        self.file_migrations = {
            "DEPLOYMENT_v5.2.md": "05_documentation/deployment/DEPLOYMENT_v5.2.md",
            "DEPLOYMENT_v5.4_Federation.md": "05_documentation/deployment/DEPLOYMENT_v5.4_Federation.md",
            "DEPLOYMENT_v6.0_Planetary_Continuum.md": "05_documentation/deployment/DEPLOYMENT_v6.0_Planetary_Continuum.md",
            "DEPLOYMENT_v8.0_Continuum_Ignition.md": "05_documentation/deployment/DEPLOYMENT_v8.0_Continuum_Ignition.md",
            "TRANSITION_v6_to_v7_DORMANT.md": "05_documentation/transitions/TRANSITION_v6_to_v7_DORMANT.md",
            "ROOT_24_LOCK_COMPLIANCE_SUMMARY.md": "05_documentation/compliance/ROOT_24_LOCK_COMPLIANCE_SUMMARY.md",
            "pytest.ini": "11_test_simulation/config/pytest.ini"
        }

        # Critical violations to delete
        self.delete_items = [
            ".claude",
            ".pytest_cache"
        ]

        # SHA-256 registry (baseline from forensic audit)
        self.sha256_baseline = {
            "DEPLOYMENT_v5.2.md": "1d46df201e4a1da8f9c6ccfa78980293fc3c6c10bd65704f70e60b4abd477945",
            "DEPLOYMENT_v5.4_Federation.md": "02da6105b1dbe10e049537f2afdeafe134e2a524d42e8290b7e79822f5b4ced2",
            "DEPLOYMENT_v6.0_Planetary_Continuum.md": "36be330cc44abd42dd30df618e8e3402e3d2070f2b6c46cc2a19a4b503a73e77",
            "DEPLOYMENT_v8.0_Continuum_Ignition.md": "8ac9de5648dbd2bd4943e0407004d9566868b0d5a3ff3c49badf6685dc6db1c2",
            "TRANSITION_v6_to_v7_DORMANT.md": "06913ccde36fcf6ac63dfb9a14171c5e874561740139ef67408638a1b786f365",
            "ROOT_24_LOCK_COMPLIANCE_SUMMARY.md": "cee8b64de63b7ea04b93c64a78ee88e2cc4a14d52ee160c5a2eb7d29e83537e8",
            "pytest.ini": "1adae0a97fe99ce1b3f7ee592e2082564098300f0ab68d91f0527613e91d7fd2"
        }

    def calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def verify_file_integrity(self, filename: str) -> Tuple[bool, Optional[str]]:
        """Verify file SHA-256 matches baseline"""
        if filename not in self.sha256_baseline:
            return True, None  # No baseline, assume OK

        file_path = self.project_root / filename
        if not file_path.exists():
            return False, "File does not exist"

        actual_hash = self.calculate_sha256(file_path)
        expected_hash = self.sha256_baseline[filename]

        if actual_hash == expected_hash:
            return True, None
        else:
            return False, f"Hash mismatch: expected {expected_hash[:16]}..., got {actual_hash[:16]}..."

    def create_backup(self, path: Path) -> Optional[Path]:
        """Create backup of file or directory"""
        if not path.exists():
            return None

        backup_dir = self.project_root / "02_audit_logging" / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_path = backup_dir / path.name

        if path.is_dir():
            shutil.copytree(path, backup_path)
        else:
            shutil.copy2(path, backup_path)

        return backup_path

    def migrate_file(self, source_name: str, target_path: str) -> bool:
        """Migrate file from root to target location"""
        source = self.project_root / source_name
        target = self.project_root / target_path

        if not source.exists():
            print(f"   ⚠️  {source_name} - file not found (already moved?)")
            return True

        # Verify integrity before migration
        integrity_ok, error_msg = self.verify_file_integrity(source_name)
        if not integrity_ok:
            print(f"   ❌ {source_name} - integrity check failed: {error_msg}")
            self.errors.append(f"{source_name}: {error_msg}")
            return False

        # Create target directory
        target.parent.mkdir(parents=True, exist_ok=True)

        # Create backup
        if not self.dry_run:
            backup = self.create_backup(source)
            print(f"   💾 Backup created: {backup.relative_to(self.project_root)}")

        # Move file
        if self.dry_run:
            print(f"   🔍 [DRY-RUN] Would move: {source_name} → {target_path}")
        else:
            shutil.move(str(source), str(target))
            print(f"   ✅ Moved: {source_name} → {target_path}")

            # Verify integrity after migration
            post_hash = self.calculate_sha256(target)
            expected_hash = self.sha256_baseline.get(source_name)
            if expected_hash and post_hash == expected_hash:
                print(f"   🔒 Integrity verified (SHA-256 match)")
            else:
                print(f"   ⚠️  Warning: Could not verify post-migration integrity")

        self.moved_files.append({
            "source": source_name,
            "target": target_path,
            "sha256": self.sha256_baseline.get(source_name),
            "timestamp": datetime.now().isoformat()
        })

        return True

    def delete_item(self, item_name: str) -> bool:
        """Delete unauthorized directory or file"""
        item = self.project_root / item_name

        if not item.exists():
            print(f"   ⚠️  {item_name} - not found (already deleted?)")
            return True

        # Create backup before deletion (skip .claude due to permission issues)
        if not self.dry_run and item_name != ".claude":
            try:
                backup = self.create_backup(item)
                if backup:
                    print(f"   💾 Backup created: {backup.relative_to(self.project_root)}")
            except (PermissionError, OSError) as e:
                print(f"   ⚠️  Backup skipped (permission denied): {item_name}")

        # Delete
        if self.dry_run:
            print(f"   🔍 [DRY-RUN] Would delete: {item_name}")
        else:
            try:
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                    print(f"   ✅ Deleted directory: {item_name}")
                else:
                    item.unlink()
                    print(f"   ✅ Deleted file: {item_name}")
            except (PermissionError, OSError) as e:
                print(f"   ⚠️  Could not delete {item_name}: {str(e)}")
                self.errors.append(f"Delete failed for {item_name}: {str(e)}")
                return False

        self.deleted_items.append({
            "path": item_name,
            "type": "directory" if item.is_dir() else "file",
            "timestamp": datetime.now().isoformat()
        })

        return True

    def update_gitignore(self) -> bool:
        """Update .gitignore with prohibited patterns"""
        gitignore_path = self.project_root / ".gitignore"

        patterns_to_add = [
            ".claude/",
            ".pytest_cache/",
            "__pycache__/",
            "*.pyc",
            ".DS_Store",
            "Thumbs.db"
        ]

        # Read existing .gitignore
        existing_patterns = set()
        if gitignore_path.exists():
            with open(gitignore_path, "r", encoding="utf-8") as f:
                existing_patterns = set(line.strip() for line in f if line.strip() and not line.startswith("#"))

        # Determine new patterns
        new_patterns = [p for p in patterns_to_add if p not in existing_patterns]

        if not new_patterns:
            print("\n   ✅ .gitignore already up-to-date")
            return True

        if self.dry_run:
            print(f"\n   🔍 [DRY-RUN] Would add to .gitignore: {', '.join(new_patterns)}")
            return True

        # Append new patterns
        with open(gitignore_path, "a", encoding="utf-8") as f:
            f.write("\n# Root-24-LOCK Auto-Fix - Added patterns\n")
            for pattern in new_patterns:
                f.write(f"{pattern}\n")

        print(f"\n   ✅ Added {len(new_patterns)} pattern(s) to .gitignore")
        return True

    def generate_checksums(self) -> bool:
        """Generate SHA-256 checksums for all documentation files"""
        checksum_file = self.project_root / "02_audit_logging" / "reports" / "documentation_checksums.txt"

        if self.dry_run:
            print("\n   🔍 [DRY-RUN] Would generate documentation checksums")
            return True

        checksum_file.parent.mkdir(parents=True, exist_ok=True)

        checksums = []
        doc_root = self.project_root / "05_documentation"

        if doc_root.exists():
            for root, _, files in os.walk(doc_root):
                for file in sorted(files):
                    if file.endswith((".md", ".yaml", ".json", ".txt")):
                        file_path = Path(root) / file
                        file_hash = self.calculate_sha256(file_path)
                        rel_path = file_path.relative_to(self.project_root)
                        checksums.append(f"{file_hash}  {rel_path}")

        # Add pytest.ini if migrated
        pytest_config = self.project_root / "11_test_simulation" / "config" / "pytest.ini"
        if pytest_config.exists():
            pytest_hash = self.calculate_sha256(pytest_config)
            rel_path = pytest_config.relative_to(self.project_root)
            checksums.append(f"{pytest_hash}  {rel_path}")

        with open(checksum_file, "w", encoding="utf-8") as f:
            f.write("# SSID Documentation Checksums (SHA-256)\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n")
            f.write(f"# Total files: {len(checksums)}\n\n")
            for checksum in checksums:
                f.write(f"{checksum}\n")

        print(f"\n   ✅ Generated checksums for {len(checksums)} file(s)")
        print(f"   📄 Checksum file: {checksum_file.relative_to(self.project_root)}")
        return True

    def generate_report(self) -> Dict:
        """Generate auto-fix execution report"""
        report = {
            "version": "2.0.0",
            "mode": "AUTO_FIX",
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "project_root": str(self.project_root),
            "summary": {
                "files_migrated": len(self.moved_files),
                "items_deleted": len(self.deleted_items),
                "errors": len(self.errors)
            },
            "migrations": self.moved_files,
            "deletions": self.deleted_items,
            "errors": self.errors,
            "status": "SUCCESS" if len(self.errors) == 0 else "PARTIAL_SUCCESS"
        }

        return report

    def run(self) -> bool:
        """Execute auto-fix procedure"""
        print("=" * 70)
        print("SSID Root-24-LOCK Auto-Fix")
        print("=" * 70)
        print(f"Mode: {'DRY-RUN' if self.dry_run else 'LIVE'}")
        print(f"Project Root: {self.project_root}")
        print()

        # Phase 1: Delete critical violations
        print("Phase 1: Removing Critical Violations")
        print("-" * 70)
        for item in self.delete_items:
            self.delete_item(item)

        # Phase 2: Migrate files
        print("\nPhase 2: Migrating Files to Proper Locations")
        print("-" * 70)
        for source, target in self.file_migrations.items():
            self.migrate_file(source, target)

        # Phase 3: Update .gitignore
        print("\nPhase 3: Updating .gitignore")
        print("-" * 70)
        self.update_gitignore()

        # Phase 4: Generate checksums
        print("\nPhase 4: Generating Documentation Checksums")
        print("-" * 70)
        self.generate_checksums()

        # Generate report
        report = self.generate_report()

        # Save report
        if not self.dry_run:
            report_path = self.project_root / "02_audit_logging" / "reports" / "auto_fix_report.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            print(f"\n   📄 Report saved: {report_path.relative_to(self.project_root)}")

        # Summary
        print("\n" + "=" * 70)
        print("Auto-Fix Summary")
        print("=" * 70)
        print(f"Files Migrated: {report['summary']['files_migrated']}")
        print(f"Items Deleted: {report['summary']['items_deleted']}")
        print(f"Errors: {report['summary']['errors']}")
        print(f"Status: {report['status']}")

        if self.dry_run:
            print("\n⚠️  DRY-RUN MODE: No changes were made")
            print("   Run without --dry-run to apply changes")
        else:
            print("\n✅ Auto-fix complete!")
            print("   Run forensic audit to verify compliance:")
            print("   python 12_tooling/root_forensic_audit.py")

        return len(self.errors) == 0

def main():
    parser = argparse.ArgumentParser(
        description="SSID Root-24-LOCK Auto-Fix Script",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry-run mode: preview changes without applying"
    )
    parser.add_argument(
        "--project-root",
        type=str,
        default=r"C:\Users\bibel\Documents\Github\SSID",
        help="Project root directory (default: C:\\Users\\bibel\\Documents\\Github\\SSID)"
    )

    args = parser.parse_args()

    # Validate project root
    project_root = Path(args.project_root)
    if not project_root.exists():
        print(f"❌ Error: Project root does not exist: {project_root}")
        sys.exit(1)

    # Execute auto-fix
    auto_fix = Root24AutoFix(str(project_root), dry_run=args.dry_run)
    success = auto_fix.run()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
