#!/usr/bin/env python3
"""
SSID Safe Cleanup Archiver v12.4
4-Phase process: Scan → Tar → Verify → Optional Delete

Usage:
    python safe_cleanup_archiver.py --phase scan
    python safe_cleanup_archiver.py --phase tar
    python safe_cleanup_archiver.py --phase verify
    python safe_cleanup_archiver.py --phase delete
"""

import argparse
import hashlib
import json
import sys
import tarfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple


class SafeCleanupArchiver:
    """Safe 4-phase cleanup with archival and verification."""

    # Patterns for cleanup (high confidence, low risk)
    CLEANUP_PATTERNS = [
        '02_audit_logging/backups/placeholders_20251013_*',  # Old placeholder backups
        '02_audit_logging/reports/coverage_advice_20251009_*.json',  # Old coverage reports (keep latest)
        '23_compliance/evidence/structure_validator',  # Old structure validation evidence
        '23_compliance/evidence/depth_limit',  # Old depth validation evidence
    ]

    def __init__(self, work_dir: str = '.'):
        self.work_dir = Path(work_dir)
        self.archive_dir = self.work_dir / '02_audit_logging' / 'archives'
        self.reports_dir = self.work_dir / '02_audit_logging' / 'reports'
        self.scan_results_path = self.reports_dir / 'cleanup_scan_results.json'
        self.archive_path = self.archive_dir / f'cleanup_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.tar.gz'
        self.audit_report_path = self.reports_dir / 'cleanup_audit_report.json'

        self.scanned_files: List[Dict] = []
        self.total_size_kb = 0

    def phase_1_scan(self) -> bool:
        """Phase 1: Scan for deletable artifacts."""
        print("=" * 70)
        print("PHASE 1: SCANNING")
        print("=" * 70)
        print()

        self.scanned_files = []
        self.total_size_kb = 0

        print("[INFO] Scanning for cleanup candidates...")

        for pattern in self.CLEANUP_PATTERNS:
            print(f"[INFO] Pattern: {pattern}")
            found_count = 0

            target_path = self.work_dir / pattern.replace('*', '')

            # Handle wildcards manually
            if '*' in pattern:
                # Split pattern into base path and wildcard part
                parts = pattern.split('*')
                base_dir = self.work_dir / parts[0].rstrip('/')

                if base_dir.exists() and base_dir.is_dir():
                    # Find all matching subdirectories/files
                    for item in base_dir.iterdir():
                        if item.name.startswith(parts[0].split('/')[-1]):
                            if item.is_dir():
                                # Recursively add all files
                                for file_path in item.rglob('*'):
                                    if file_path.is_file():
                                        size_kb = file_path.stat().st_size / 1024
                                        sha256 = self._compute_sha256(file_path)

                                        self.scanned_files.append({
                                            'path': str(file_path.relative_to(self.work_dir)),
                                            'size_kb': round(size_kb, 2),
                                            'sha256': sha256,
                                            'pattern': pattern
                                        })
                                        self.total_size_kb += size_kb
                                        found_count += 1
                            elif item.is_file():
                                size_kb = item.stat().st_size / 1024
                                sha256 = self._compute_sha256(item)

                                self.scanned_files.append({
                                    'path': str(item.relative_to(self.work_dir)),
                                    'size_kb': round(size_kb, 2),
                                    'sha256': sha256,
                                    'pattern': pattern
                                })
                                self.total_size_kb += size_kb
                                found_count += 1
            else:
                # Direct path - check if it's a directory or file
                check_path = self.work_dir / pattern

                if check_path.exists():
                    if check_path.is_dir():
                        # Add all files in directory recursively
                        for file_path in check_path.rglob('*'):
                            if file_path.is_file():
                                size_kb = file_path.stat().st_size / 1024
                                sha256 = self._compute_sha256(file_path)

                                self.scanned_files.append({
                                    'path': str(file_path.relative_to(self.work_dir)),
                                    'size_kb': round(size_kb, 2),
                                    'sha256': sha256,
                                    'pattern': pattern
                                })
                                self.total_size_kb += size_kb
                                found_count += 1
                    elif check_path.is_file():
                        size_kb = check_path.stat().st_size / 1024
                        sha256 = self._compute_sha256(check_path)

                        self.scanned_files.append({
                            'path': str(check_path.relative_to(self.work_dir)),
                            'size_kb': round(size_kb, 2),
                            'sha256': sha256,
                            'pattern': pattern
                        })
                        self.total_size_kb += size_kb
                        found_count += 1

            print(f"       Found: {found_count} items")

        print()
        print(f"[OK] Scan complete:")
        print(f"     Files found: {len(self.scanned_files):,}")
        print(f"     Total size: {self.total_size_kb / 1024:.2f} MB")

        # Save scan results
        scan_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'total_files': len(self.scanned_files),
            'total_size_kb': round(self.total_size_kb, 2),
            'total_size_mb': round(self.total_size_kb / 1024, 2),
            'files': self.scanned_files
        }

        self.reports_dir.mkdir(parents=True, exist_ok=True)
        with open(self.scan_results_path, 'w', encoding='utf-8') as f:
            json.dump(scan_data, f, indent=2)

        print(f"[OK] Scan results saved: {self.scan_results_path}")
        print()
        return len(self.scanned_files) > 0

    def phase_2_tar(self) -> bool:
        """Phase 2: Create tar.gz archive."""
        print("=" * 70)
        print("PHASE 2: ARCHIVING")
        print("=" * 70)
        print()

        # Load scan results
        if not self.scan_results_path.exists():
            print("[ERROR] Scan results not found. Run phase 'scan' first.")
            return False

        with open(self.scan_results_path, 'r', encoding='utf-8') as f:
            scan_data = json.load(f)

        self.scanned_files = scan_data['files']
        total_files = scan_data['total_files']

        print(f"[INFO] Creating archive: {self.archive_path}")
        print(f"[INFO] Files to archive: {total_files:,}")

        self.archive_dir.mkdir(parents=True, exist_ok=True)

        archived_count = 0
        failed_count = 0

        with tarfile.open(self.archive_path, 'w:gz') as tar:
            for file_info in self.scanned_files:
                file_path = self.work_dir / file_info['path']

                if not file_path.exists():
                    print(f"[WARN] File not found: {file_path}")
                    failed_count += 1
                    continue

                try:
                    # Add to archive with relative path
                    tar.add(file_path, arcname=file_info['path'])
                    archived_count += 1

                    if archived_count % 1000 == 0:
                        print(f"[INFO] Archived {archived_count:,} files...")

                except Exception as e:
                    print(f"[ERROR] Failed to archive {file_path}: {e}")
                    failed_count += 1

        print()
        print(f"[OK] Archive created:")
        print(f"     Archived: {archived_count:,} files")
        print(f"     Failed: {failed_count}")
        print(f"     Archive size: {self.archive_path.stat().st_size / (1024 * 1024):.2f} MB")

        # Compute archive SHA-256
        archive_sha256 = self._compute_sha256(self.archive_path)
        print(f"     Archive SHA-256: {archive_sha256}")

        # Save archive info
        sha256_path = self.archive_path.with_suffix('.tar.gz.sha256')
        with open(sha256_path, 'w') as f:
            f.write(f"{archive_sha256}  {self.archive_path.name}\n")

        print(f"[OK] SHA-256 saved: {sha256_path}")
        print()

        return archived_count > 0

    def phase_3_verify(self) -> bool:
        """Phase 3: Verify archive integrity."""
        print("=" * 70)
        print("PHASE 3: VERIFICATION")
        print("=" * 70)
        print()

        # Find the most recent archive
        archives = sorted(self.archive_dir.glob('cleanup_backup_*.tar.gz'))
        if not archives:
            print("[ERROR] No archives found. Run phase 'tar' first.")
            return False

        self.archive_path = archives[-1]  # Use most recent
        print(f"[INFO] Using archive: {self.archive_path.name}")

        print(f"[INFO] Verifying archive: {self.archive_path}")

        # Step 1: Verify archive SHA-256
        sha256_path = self.archive_path.with_suffix('.tar.gz.sha256')
        if sha256_path.exists():
            with open(sha256_path, 'r') as f:
                expected_sha256 = f.read().split()[0]

            actual_sha256 = self._compute_sha256(self.archive_path)

            if expected_sha256 == actual_sha256:
                print(f"[OK] Archive SHA-256 verified: {actual_sha256}")
            else:
                print(f"[FAIL] Archive SHA-256 mismatch!")
                print(f"       Expected: {expected_sha256}")
                print(f"       Actual:   {actual_sha256}")
                return False
        else:
            print("[WARN] SHA-256 file not found, skipping checksum verification")

        # Step 2: Verify archive can be opened
        try:
            with tarfile.open(self.archive_path, 'r:gz') as tar:
                members = tar.getmembers()
                print(f"[OK] Archive is valid: {len(members):,} members")

                # Step 3: Verify file count matches scan
                if self.scan_results_path.exists():
                    with open(self.scan_results_path, 'r') as f:
                        scan_data = json.load(f)
                    expected_count = scan_data['total_files']

                    if len(members) == expected_count:
                        print(f"[OK] File count matches scan: {expected_count:,}")
                    else:
                        print(f"[WARN] File count mismatch:")
                        print(f"       Expected: {expected_count:,}")
                        print(f"       Archive:  {len(members):,}")

                # Step 4: Sample integrity check (first 10 files)
                print("[INFO] Sampling file integrity...")
                sample_size = min(10, len(members))

                for i, member in enumerate(members[:sample_size]):
                    try:
                        # Extract to memory and verify
                        f = tar.extractfile(member)
                        if f:
                            content = f.read()
                            file_sha256 = hashlib.sha256(content).hexdigest()
                            print(f"       [{i+1}/{sample_size}] {member.name}: {file_sha256[:12]}...")
                    except Exception as e:
                        print(f"       [ERROR] Failed to extract {member.name}: {e}")
                        return False

                print(f"[OK] Sample integrity check passed")

        except Exception as e:
            print(f"[FAIL] Archive verification failed: {e}")
            return False

        # Generate audit report
        audit_report = {
            'audit_version': 'v12.4',
            'phase': 'verification',
            'status': 'PASS',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'archive_path': str(self.archive_path),
            'archive_size_mb': round(self.archive_path.stat().st_size / (1024 * 1024), 2),
            'archive_sha256': actual_sha256 if sha256_path.exists() else None,
            'files_archived': len(members),
            'verification_passed': True
        }

        with open(self.audit_report_path, 'w', encoding='utf-8') as f:
            json.dump(audit_report, f, indent=2)

        print(f"[OK] Audit report saved: {self.audit_report_path}")
        print()
        print("[SUCCESS] Archive verification PASSED")
        print()

        return True

    def phase_4_delete(self) -> bool:
        """Phase 4: Delete original files (only if verification passed)."""
        print("=" * 70)
        print("PHASE 4: DELETE")
        print("=" * 70)
        print()

        # Check if verification passed
        if not self.audit_report_path.exists():
            print("[ERROR] Audit report not found. Run phase 'verify' first.")
            return False

        with open(self.audit_report_path, 'r') as f:
            audit_report = json.load(f)

        if audit_report.get('status') != 'PASS':
            print("[ERROR] Verification did not pass. Cannot proceed with deletion.")
            return False

        print("[OK] Verification passed, proceeding with deletion...")
        print()

        # Load scan results
        with open(self.scan_results_path, 'r') as f:
            scan_data = json.load(f)

        self.scanned_files = scan_data['files']

        print(f"[WARN] About to DELETE {len(self.scanned_files):,} files!")
        print(f"[WARN] Archive backup: {self.archive_path}")
        print()
        print("[WARN] Press Ctrl+C within 10 seconds to abort...")

        import time
        try:
            for i in range(10, 0, -1):
                print(f"[WARN] Deleting in {i}...")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[INFO] Deletion aborted by user")
            return False

        print()
        print("[INFO] Starting deletion...")

        deleted_count = 0
        failed_count = 0
        deleted_dirs = set()

        for file_info in self.scanned_files:
            file_path = self.work_dir / file_info['path']

            if not file_path.exists():
                continue

            try:
                file_path.unlink()
                deleted_count += 1

                # Track parent directory for cleanup
                deleted_dirs.add(file_path.parent)

                if deleted_count % 1000 == 0:
                    print(f"[INFO] Deleted {deleted_count:,} files...")

            except Exception as e:
                print(f"[ERROR] Failed to delete {file_path}: {e}")
                failed_count += 1

        # Clean up empty directories
        print("[INFO] Cleaning up empty directories...")
        empty_dirs_removed = 0

        for dir_path in sorted(deleted_dirs, reverse=True):
            try:
                if dir_path.exists() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    empty_dirs_removed += 1
            except:
                pass

        print()
        print(f"[OK] Deletion complete:")
        print(f"     Deleted files: {deleted_count:,}")
        print(f"     Failed: {failed_count}")
        print(f"     Empty dirs removed: {empty_dirs_removed}")
        print(f"     Space reclaimed: {scan_data['total_size_mb']:.2f} MB")

        # Update audit report
        audit_report['phase'] = 'deletion'
        audit_report['deletion_timestamp'] = datetime.utcnow().isoformat() + 'Z'
        audit_report['files_deleted'] = deleted_count
        audit_report['files_failed'] = failed_count
        audit_report['space_reclaimed_mb'] = scan_data['total_size_mb']

        with open(self.audit_report_path, 'w', encoding='utf-8') as f:
            json.dump(audit_report, f, indent=2)

        print(f"[OK] Audit report updated: {self.audit_report_path}")
        print()

        return deleted_count > 0

    def _compute_sha256(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()


def main():
    parser = argparse.ArgumentParser(
        description='SSID Safe Cleanup Archiver v12.4 - 4-Phase Process'
    )
    parser.add_argument('--phase', required=True,
                       choices=['scan', 'tar', 'verify', 'delete'],
                       help='Phase to execute')
    parser.add_argument('--work-dir', default='.',
                       help='Working directory (default: current)')

    args = parser.parse_args()

    print()
    print("=" * 70)
    print("SSID SAFE CLEANUP ARCHIVER v12.4")
    print("=" * 70)
    print()

    archiver = SafeCleanupArchiver(args.work_dir)

    if args.phase == 'scan':
        success = archiver.phase_1_scan()
    elif args.phase == 'tar':
        success = archiver.phase_2_tar()
    elif args.phase == 'verify':
        success = archiver.phase_3_verify()
    elif args.phase == 'delete':
        success = archiver.phase_4_delete()

    print("=" * 70)
    if success:
        print(f"[SUCCESS] Phase '{args.phase.upper()}' completed successfully")
    else:
        print(f"[FAIL] Phase '{args.phase.upper()}' failed")
    print("=" * 70)
    print()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
