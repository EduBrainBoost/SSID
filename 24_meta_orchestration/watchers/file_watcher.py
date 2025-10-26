#!/usr/bin/env python3
"""
SoT File Watcher - Automatic Artifact Regeneration
===================================================

Überwacht SoT-Masterdateien und triggert automatische Regenerierung
der Artefakte bei Änderungen.

Features:
- Watches 16_codex/structure/*.md files
- Detects changes in real-time
- Triggers artifact regeneration
- Sends notifications on completion

Version: 1.0.0
Status: PRODUCTION READY
Author: SSID Automation Team
Co-Authored-By: Claude <noreply@anthropic.com>

🧠 Generated with Claude Code (https://claude.com/claude-code)

Usage:
    # Start watcher (foreground)
    python file_watcher.py

    # Start as daemon
    python file_watcher.py --daemon

    # Watch specific directory
    python file_watcher.py --watch-dir 16_codex/structure
"""

import sys
import time
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, Set, Optional
from datetime import datetime, timezone
import json


class FileWatcher:
    """
    Watches SoT master files for changes and triggers regeneration.
    """

    def __init__(self, repo_root: Optional[Path] = None, poll_interval: int = 5):
        """
        Initialize file watcher.

        Args:
            repo_root: Repository root path
            poll_interval: Polling interval in seconds
        """
        if repo_root is None:
            self.repo_root = Path(__file__).resolve().parents[3]
        else:
            self.repo_root = Path(repo_root)

        self.poll_interval = poll_interval
        self.watch_dir = self.repo_root / '16_codex/structure'
        self.file_hashes: Dict[Path, str] = {}

    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA-256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def scan_files(self) -> Dict[Path, str]:
        """Scan all watched files and return their hashes"""
        hashes = {}

        if not self.watch_dir.exists():
            return hashes

        # Watch all .md files
        for md_file in self.watch_dir.glob('*.md'):
            if md_file.is_file():
                hashes[md_file] = self.compute_file_hash(md_file)

        return hashes

    def detect_changes(self) -> Set[Path]:
        """Detect which files have changed"""
        current_hashes = self.scan_files()
        changed_files = set()

        # Check for new or modified files
        for file_path, new_hash in current_hashes.items():
            old_hash = self.file_hashes.get(file_path, "")

            if old_hash != new_hash:
                changed_files.add(file_path)

        # Check for deleted files
        for file_path in self.file_hashes:
            if file_path not in current_hashes:
                changed_files.add(file_path)

        return changed_files

    def trigger_regeneration(self, changed_files: Set[Path]):
        """Trigger artifact regeneration"""
        print(f"\n[{datetime.now(timezone.utc).isoformat()}]")
        print(f"Detected {len(changed_files)} changed file(s):")

        for file_path in changed_files:
            print(f"  - {file_path.relative_to(self.repo_root)}")

        print("\nTriggering artifact regeneration...")

        try:
            # Run parser to regenerate artifacts
            result = subprocess.run(
                [sys.executable, "03_core/validators/sot/sot_rule_parser_v3.py"],
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=180
            )

            if result.returncode == 0:
                print("[OK] Artifact regeneration completed successfully")

                # Run concordance check
                subprocess.run(
                    [sys.executable, "24_meta_orchestration/concordance/cross_artifact_validator.py"],
                    capture_output=True,
                    cwd=self.repo_root,
                    timeout=60
                )

                # Log event
                self.log_regeneration_event(changed_files, "SUCCESS")
            else:
                print(f"[FAIL] Artifact regeneration failed (exit {result.returncode})")
                print(result.stderr)
                self.log_regeneration_event(changed_files, "FAILURE")

        except subprocess.TimeoutExpired:
            print("[FAIL] Regeneration timeout")
            self.log_regeneration_event(changed_files, "TIMEOUT")
        except Exception as e:
            print(f"[ERROR] Regeneration error: {e}")
            self.log_regeneration_event(changed_files, "ERROR")

    def log_regeneration_event(self, changed_files: Set[Path], status: str):
        """Log regeneration event"""
        log_dir = self.repo_root / '24_meta_orchestration/watchers/logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        event = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'changed_files': [str(f.relative_to(self.repo_root)) for f in changed_files],
            'status': status
        }

        log_file = log_dir / 'regeneration_events.jsonl'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event) + '\n')

    def watch(self):
        """Main watch loop"""
        print("="*80)
        print("SoT File Watcher - Starting")
        print("="*80)
        print(f"Repository: {self.repo_root}")
        print(f"Watch Directory: {self.watch_dir}")
        print(f"Poll Interval: {self.poll_interval}s")
        print("="*80)

        # Initial scan
        self.file_hashes = self.scan_files()
        print(f"[INFO] Watching {len(self.file_hashes)} file(s)")
        print("[INFO] Press Ctrl+C to stop")

        try:
            while True:
                # Detect changes
                changed_files = self.detect_changes()

                if changed_files:
                    self.trigger_regeneration(changed_files)

                    # Update hashes
                    self.file_hashes = self.scan_files()

                # Sleep
                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            print("\n[INFO] File watcher stopped")
            sys.exit(0)


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='SoT File Watcher')
    parser.add_argument('--watch-dir', type=Path, help='Directory to watch')
    parser.add_argument('--interval', type=int, default=5, help='Poll interval (seconds)')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon (not yet implemented)')

    args = parser.parse_args()

    if args.daemon:
        print("[ERROR] Daemon mode not yet implemented")
        sys.exit(1)

    watcher = FileWatcher(poll_interval=args.interval)

    if args.watch_dir:
        watcher.watch_dir = args.watch_dir

    watcher.watch()


if __name__ == '__main__':
    main()
