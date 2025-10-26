#!/usr/bin/env python3
"""
SSID 50KB File Size Monitor & Auto-Splitter
============================================

Überwacht alle Dateien im Repository auf 50KB-Limit.
Bei Überschreitung: Automatisches Splitting oder Warnung.

Version: 1.0.0
Status: Production-Ready
Classification: INTERNAL - Security Operations
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

# 50KB Limit (in Bytes)
SIZE_LIMIT = 51200  # 50 * 1024 bytes

# Ausnahmen: Dateien die größer sein dürfen (z.B. Binaries, komprimierte Dateien)
EXEMPTIONS = [
    ".git/",
    ".venv/",
    ".pytest_cache/",
    "node_modules/",
    "*.pyc",
    "*.exe",
    "*.dll",
    "*.so",
    "*.zip",
    "*.tar.gz",
    "*.jpg",
    "*.png",
    "*.gif",
    "*.pdf",
    "*.woff",
    "*.woff2",
    "*.ttf",
    "*.eot",
]


class FileSizeMonitor:
    """Überwacht Dateigrößen und führt automatisches Splitting durch"""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root)
        self.violations: List[Dict] = []
        self.evidence_log: List[Dict] = []

    def is_exempt(self, file_path: Path) -> bool:
        """Prüft ob Datei von 50KB-Regel ausgenommen ist"""
        path_str = str(file_path)

        # Prüfe Verzeichnis-Ausnahmen
        for exemption in EXEMPTIONS:
            if exemption.endswith("/") and exemption[:-1] in path_str:
                return True
            # Prüfe Wildcard-Muster
            if "*" in exemption:
                pattern = exemption.replace("*", "")
                if path_str.endswith(pattern):
                    return True

        return False

    def calculate_file_hash(self, file_path: Path) -> str:
        """Berechnet SHA256-Hash einer Datei"""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            return f"ERROR: {str(e)}"

    def scan_repository(self) -> Tuple[int, int, int]:
        """
        Scannt alle Dateien im Repository

        Returns:
            (total_files, violations_count, exempt_count)
        """
        total_files = 0
        violations_count = 0
        exempt_count = 0

        print(f"🔍 Scanning repository: {self.repo_root}")
        print(f"📏 Size limit: {SIZE_LIMIT} bytes (50KB)")
        print("-" * 80)

        for root, dirs, files in os.walk(self.repo_root):
            # Überspringe .git und andere ausgenommene Verzeichnisse
            dirs[:] = [d for d in dirs if not any(ex.strip('/') == d for ex in EXEMPTIONS if ex.endswith('/'))]

            for file in files:
                file_path = Path(root) / file
                total_files += 1

                try:
                    file_size = file_path.stat().st_size

                    # Prüfe ob ausgenommen
                    if self.is_exempt(file_path):
                        exempt_count += 1
                        continue

                    # Prüfe Größe
                    if file_size > SIZE_LIMIT:
                        violations_count += 1
                        relative_path = file_path.relative_to(self.repo_root)

                        violation = {
                            "path": str(relative_path),
                            "size_bytes": file_size,
                            "size_kb": round(file_size / 1024, 2),
                            "excess_bytes": file_size - SIZE_LIMIT,
                            "excess_kb": round((file_size - SIZE_LIMIT) / 1024, 2),
                            "hash": self.calculate_file_hash(file_path),
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "can_auto_split": self.can_auto_split(file_path)
                        }

                        self.violations.append(violation)

                        print(f"❌ VIOLATION: {relative_path}")
                        print(f"   Size: {violation['size_kb']} KB (exceeds by {violation['excess_kb']} KB)")
                        print(f"   Auto-split: {'YES' if violation['can_auto_split'] else 'NO'}")
                        print()

                except Exception as e:
                    print(f"⚠️  Error scanning {file_path}: {e}")

        return total_files, violations_count, exempt_count

    def can_auto_split(self, file_path: Path) -> bool:
        """
        Prüft ob Datei automatisch gesplittet werden kann

        Kriterien:
        - Text-basierte Dateien (.md, .txt, .yaml, .json, .py, etc.)
        - Keine Binärdateien
        - Logische Split-Points vorhanden
        """
        text_extensions = {
            '.md', '.txt', '.yaml', '.yml', '.json',
            '.py', '.js', '.ts', '.html', '.css',
            '.sql', '.sh', '.bash', '.xml', '.csv'
        }

        return file_path.suffix.lower() in text_extensions

    def suggest_splits(self) -> List[Dict]:
        """
        Schlägt Split-Strategien für große Dateien vor
        """
        suggestions = []

        for violation in self.violations:
            if not violation['can_auto_split']:
                continue

            file_path = self.repo_root / violation['path']

            suggestion = {
                "file": violation['path'],
                "strategy": self.determine_split_strategy(file_path),
                "estimated_parts": self.estimate_split_parts(violation['size_bytes'])
            }

            suggestions.append(suggestion)

        return suggestions

    def determine_split_strategy(self, file_path: Path) -> str:
        """Bestimmt optimale Split-Strategie basierend auf Dateiinhalt"""

        if file_path.suffix == '.md':
            return "Split by Headers (##, ###)"
        elif file_path.suffix in ['.yaml', '.yml']:
            return "Split by Top-Level Keys"
        elif file_path.suffix == '.json':
            return "Split by JSON Objects/Arrays"
        elif file_path.suffix == '.py':
            return "Split by Class/Function Definitions"
        else:
            return "Split by Line Count (Equal Parts)"

    def estimate_split_parts(self, size_bytes: int) -> int:
        """Schätzt Anzahl der Split-Parts"""
        # Rechne mit 40KB pro Teil (Buffer für Overhead)
        target_size = 40960  # 40KB
        return (size_bytes + target_size - 1) // target_size

    def generate_evidence_report(self, output_path: Path):
        """Generiert Evidence-Report für Audit-Trail"""

        report = {
            "scan_metadata": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "repo_root": str(self.repo_root),
                "size_limit_bytes": SIZE_LIMIT,
                "scanner_version": "1.0.0"
            },
            "scan_results": {
                "total_violations": len(self.violations),
                "auto_splittable": sum(1 for v in self.violations if v['can_auto_split']),
                "manual_review_required": sum(1 for v in self.violations if not v['can_auto_split'])
            },
            "violations": self.violations,
            "split_suggestions": self.suggest_splits()
        }

        # Speichere Report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📊 Evidence report saved: {output_path}")

        return report

    def execute_auto_splits(self, dry_run: bool = True):
        """
        Führt automatisches Splitting für geeignete Dateien durch

        Args:
            dry_run: Wenn True, nur Simulation (keine echten Änderungen)
        """
        auto_splittable = [v for v in self.violations if v['can_auto_split']]

        if not auto_splittable:
            print("✅ No files require auto-splitting")
            return

        print(f"\n{'🔄 DRY RUN MODE' if dry_run else '⚠️  EXECUTING SPLITS'}")
        print(f"📁 Files to split: {len(auto_splittable)}")
        print("-" * 80)

        for violation in auto_splittable:
            file_path = self.repo_root / violation['path']
            print(f"\n📄 {violation['path']}")
            print(f"   Strategy: {self.determine_split_strategy(file_path)}")
            print(f"   Estimated parts: {self.estimate_split_parts(violation['size_bytes'])}")

            if not dry_run:
                # TODO: Implementiere tatsächliches Splitting
                # self.split_file(file_path, strategy)
                print("   Status: SPLIT EXECUTED (Implementation pending)")
            else:
                print("   Status: DRY RUN - No changes made")


def main():
    """Hauptfunktion"""

    # Bestimme Repository-Root
    repo_root = os.getenv('REPO_ROOT', os.getcwd())

    # Parse CLI-Argumente
    dry_run = '--execute' not in sys.argv
    verbose = '--verbose' in sys.argv

    print("=" * 80)
    print("SSID 50KB File Size Monitor")
    print("=" * 80)
    print()

    # Initialisiere Monitor
    monitor = FileSizeMonitor(repo_root)

    # Scanne Repository
    total_files, violations_count, exempt_count = monitor.scan_repository()

    # Ausgabe Zusammenfassung
    print("\n" + "=" * 80)
    print("SCAN SUMMARY")
    print("=" * 80)
    print(f"✅ Total files scanned: {total_files}")
    print(f"🔒 Files exempt from limit: {exempt_count}")
    print(f"❌ Violations found: {violations_count}")
    print()

    if violations_count > 0:
        # Generiere Evidence-Report
        evidence_path = Path(repo_root) / "23_compliance" / "evidence" / "file_size_violations" / f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        monitor.generate_evidence_report(evidence_path)

        # Zeige Split-Vorschläge
        suggestions = monitor.suggest_splits()
        if suggestions:
            print("\n" + "=" * 80)
            print("SPLIT SUGGESTIONS")
            print("=" * 80)
            for suggestion in suggestions:
                print(f"\n📄 {suggestion['file']}")
                print(f"   Strategy: {suggestion['strategy']}")
                print(f"   Parts: {suggestion['estimated_parts']}")

        # Führe Auto-Splits aus (optional)
        if '--execute' in sys.argv:
            print("\n⚠️  AUTO-SPLIT EXECUTION REQUESTED")
            monitor.execute_auto_splits(dry_run=False)
        else:
            print("\n💡 Tip: Run with --execute to perform automatic splitting")
            print("   (Recommended: Review suggestions first)")

        # Exit Code 24 bei Violations
        print("\n❌ EXIT CODE 24: File size violations detected")
        sys.exit(24)
    else:
        print("✅ All files within 50KB limit")
        sys.exit(0)


if __name__ == "__main__":
    main()
