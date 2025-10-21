#!/usr/bin/env python3
"""
Audit Autologger Executor
==========================

Executes forensic autologging based on audit_autologger.yaml configuration.
Monitors validation results and automatically archives to WORM storage.

Usage:
    python execute_audit_autologger.py [--continuous]

Modes:
    - Single-shot: Process current validation results
    - Continuous: Monitor for new validation results (--continuous flag)
"""

import sys
import json
import yaml
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List

# UTF-8 enforcement for Windows
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

class AuditAutologger:
    """Automated forensic logging for root-write prevention"""

    def __init__(self, repo_root: Path, config_path: Path):
        self.repo_root = repo_root
        self.config = self._load_config(config_path)
        self.log_entries = []

    def _load_config(self, config_path: Path) -> Dict:
        """Load YAML configuration"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def process_sources(self) -> None:
        """Process all configured sources"""
        print("=" * 80)
        print("AUDIT AUTOLOGGER - ROOT-WRITE PREVENTION")
        print("=" * 80)
        print()

        print(f"Configuration: {self.config['name']} v{self.config['version']}")
        print(f"Retention: {self.config['retention']['default_years']} years")
        print()

        processed = 0
        skipped = 0

        for source in self.config['sources']:
            source_path = self.repo_root / source['path']

            if not source_path.exists():
                print(f"⏭️  {source['type']}: File not found")
                skipped += 1
                continue

            print(f"📄 Processing: {source['type']}")
            self._process_source(source_path, source)
            processed += 1

        print()
        print(f"✅ Processed: {processed} sources")
        print(f"⏭️  Skipped: {skipped} sources")
        print()

    def _process_source(self, source_path: Path, source_config: Dict) -> None:
        """Process a single source file"""
        # Read source data
        with open(source_path, 'r', encoding='utf-8') as f:
            if source_path.suffix == '.json':
                data = json.load(f)
            else:
                data = {'content': f.read()}

        # Create audit log entry
        log_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source_type': source_config['type'],
            'source_path': str(source_path),
            'retention_years': source_config['retention_years'],
            'data_hash': self._compute_hash(data),
            'metadata': {
                'tags': self.config['metadata']['tags'],
                'compliance_labels': self.config['metadata']['compliance_labels']
            }
        }

        # Archive to WORM storage
        if self.config['destinations']['worm_storage']['enabled']:
            self._archive_to_worm(source_path, source_config, log_entry)

        # Write to audit log
        if self.config['destinations']['audit_log']['enabled']:
            self._write_audit_log(log_entry)

        self.log_entries.append(log_entry)

    def _archive_to_worm(self, source_path: Path, source_config: Dict, log_entry: Dict) -> None:
        """Archive file to WORM storage"""
        worm_config = self.config['destinations']['worm_storage']
        worm_path = self.repo_root / worm_config['path']
        worm_path.mkdir(parents=True, exist_ok=True)

        # Create timestamped archive filename
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        archive_name = f"{source_config['type']}_{timestamp}{source_path.suffix}"
        archive_path = worm_path / archive_name

        # Copy to WORM storage
        shutil.copy2(source_path, archive_path)

        print(f"   ✅ WORM archived: {archive_path.name}")

        # Mark as immutable (simulation)
        self._mark_immutable(archive_path)

    def _mark_immutable(self, file_path: Path) -> None:
        """Mark file as immutable (WORM simulation)"""
        # In production, this would use actual WORM storage API
        # For simulation, create a .worm metadata file
        metadata_file = file_path.with_suffix(file_path.suffix + '.worm')
        metadata = {
            'created_at': datetime.now(timezone.utc).isoformat(),
            'immutable': True,
            'retention_until': self._calculate_retention_date(20),
            'compliance': ['DSGVO Art. 30', 'eIDAS Art. 24']
        }
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)

    def _calculate_retention_date(self, years: int) -> str:
        """Calculate retention expiry date"""
        from datetime import timedelta
        expiry = datetime.now(timezone.utc) + timedelta(days=years * 365)
        return expiry.isoformat()

    def _write_audit_log(self, log_entry: Dict) -> None:
        """Write entry to audit log (JSONL format)"""
        audit_config = self.config['destinations']['audit_log']
        audit_path = self.repo_root / audit_config['path']
        audit_path.parent.mkdir(parents=True, exist_ok=True)

        # Append to JSONL file
        with open(audit_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

        print(f"   📝 Audit logged: {audit_path.name}")

    def _compute_hash(self, data) -> str:
        """Compute SHA-256 hash of data"""
        import hashlib
        if isinstance(data, dict):
            normalized = json.dumps(data, sort_keys=True, separators=(',', ':'))
        else:
            normalized = str(data)
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    def generate_summary(self) -> Dict:
        """Generate autologger summary"""
        summary = {
            'version': self.config['version'],
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'sources_processed': len(self.log_entries),
            'log_entries': self.log_entries,
            'compliance': {
                'retention_years': self.config['retention']['default_years'],
                'standards': self.config['retention']['compliance_standards'],
                'worm_enabled': self.config['destinations']['worm_storage']['enabled']
            }
        }

        # Save summary
        output_dir = self.repo_root / '02_audit_logging' / 'reports'
        output_file = output_dir / 'audit_autologger_summary.json'

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"📊 Summary: {output_file}")
        return summary

def main():
    """Main execution"""
    repo_root = Path(__file__).resolve().parents[2]
    config_path = repo_root / '23_compliance' / 'automation' / 'audit_autologger.yaml'

    if not config_path.exists():
        print(f"❌ Configuration not found: {config_path}")
        sys.exit(1)

    autologger = AuditAutologger(repo_root, config_path)
    autologger.process_sources()
    summary = autologger.generate_summary()

    print()
    print("=" * 80)
    print("✅ AUDIT AUTOLOGGER COMPLETE")
    print("=" * 80)
    print()
    print(f"Sources Processed: {summary['sources_processed']}")
    print(f"WORM Enabled: {summary['compliance']['worm_enabled']}")
    print(f"Retention: {summary['compliance']['retention_years']} years")
    print()

    sys.exit(0)

if __name__ == "__main__":
    main()
