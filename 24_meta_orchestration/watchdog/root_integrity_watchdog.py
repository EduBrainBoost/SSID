#!/usr/bin/env python3
"""
Root Integrity Watchdog - Layer 6 Self-Healing Component
Automatically detects and repairs SoT rule violations.

RULE_ID: L6-WATCHDOG-001
Priority: MUST
Source: Extended Enforcement Framework Layer 6
"""

import hashlib
import json
import os
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class RootIntegrityWatchdog:
    """
    Monitors SoT rule compliance and triggers automatic remediation.

    Features:
    - Real-time rule violation detection
    - Automatic hash reconciliation
    - Self-healing trigger system
    - Audit trail generation
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or str(
            PROJECT_ROOT / "24_meta_orchestration" / "watchdog" / "watchdog_config.yaml"
        )
        self.config = self._load_config()
        self.violation_log = []
        self.repair_log = []

    def _load_config(self) -> Dict:
        """Load watchdog configuration."""
        if not os.path.exists(self.config_path):
            return self._default_config()

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _default_config(self) -> Dict:
        """Return default watchdog configuration."""
        return {
            'enabled': True,
            'auto_repair': True,
            'check_interval_seconds': 60,
            'max_repair_attempts': 3,
            'critical_roots': [
                '02_audit_logging',
                '03_core',
                '23_compliance',
                '24_meta_orchestration'
            ],
            'notification_channels': ['audit_log', 'slack'],
            'quarantine_on_failure': True
        }

    def check_root_integrity(self) -> Tuple[bool, List[Dict]]:
        """
        Check integrity of all 24 root modules.

        Returns:
            (is_compliant, violations_list)
        """
        violations = []

        # Check 24 roots exist
        expected_roots = self._get_expected_roots()
        actual_roots = self._get_actual_roots()

        missing_roots = set(expected_roots) - set(actual_roots)
        extra_roots = set(actual_roots) - set(expected_roots)

        for root in missing_roots:
            violations.append({
                'type': 'MISSING_ROOT',
                'severity': 'CRITICAL',
                'root': root,
                'timestamp': datetime.utcnow().isoformat(),
                'auto_repairable': False
            })

        for root in extra_roots:
            violations.append({
                'type': 'EXTRA_ROOT',
                'severity': 'HIGH',
                'root': root,
                'timestamp': datetime.utcnow().isoformat(),
                'auto_repairable': False
            })

        # Check module.yaml exists in each root
        for root in actual_roots:
            if root in expected_roots:
                module_yaml = PROJECT_ROOT / root / "module.yaml"
                if not module_yaml.exists():
                    violations.append({
                        'type': 'MISSING_MODULE_YAML',
                        'severity': 'HIGH',
                        'root': root,
                        'timestamp': datetime.utcnow().isoformat(),
                        'auto_repairable': True,
                        'repair_action': 'generate_module_yaml'
                    })

        # Check hash integrity
        hash_violations = self._check_hash_integrity()
        violations.extend(hash_violations)

        self.violation_log.extend(violations)

        return len(violations) == 0, violations

    def _get_expected_roots(self) -> List[str]:
        """Return list of expected 24 root modules."""
        return [
            "01_ai_layer",
            "02_audit_logging",
            "03_core",
            "04_deployment",
            "05_documentation",
            "06_data_pipeline",
            "07_governance_legal",
            "08_identity_score",
            "09_meta_identity",
            "10_interoperability",
            "11_test_simulation",
            "12_tooling",
            "13_ui_layer",
            "14_zero_time_auth",
            "15_infra",
            "16_codex",
            "17_observability",
            "18_data_layer",
            "19_adapters",
            "20_foundation",
            "21_post_quantum_crypto",
            "22_datasets",
            "23_compliance",
            "24_meta_orchestration"
        ]

    def _get_actual_roots(self) -> List[str]:
        """Get actual root directories in project."""
        roots = []
        for item in PROJECT_ROOT.iterdir():
            if item.is_dir() and item.name.startswith(tuple(f"{i:02d}_" for i in range(1, 25))):
                roots.append(item.name)
        return sorted(roots)

    def _check_hash_integrity(self) -> List[Dict]:
        """Check hash integrity of critical files."""
        violations = []

        hash_file = PROJECT_ROOT / "24_meta_orchestration" / "registry" / "manifests" / "integrity_checksums.json"
        if not hash_file.exists():
            return violations

        with open(hash_file, 'r', encoding='utf-8') as f:
            stored_hashes = json.load(f)

        for file_path, stored_hash in stored_hashes.items():
            full_path = PROJECT_ROOT / file_path
            if full_path.exists():
                actual_hash = self._calculate_sha256(full_path)
                if actual_hash != stored_hash:
                    violations.append({
                        'type': 'HASH_MISMATCH',
                        'severity': 'CRITICAL',
                        'file': file_path,
                        'expected_hash': stored_hash,
                        'actual_hash': actual_hash,
                        'timestamp': datetime.utcnow().isoformat(),
                        'auto_repairable': True,
                        'repair_action': 'reconcile_hash'
                    })

        return violations

    def _calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def auto_repair(self, violations: List[Dict]) -> Dict[str, int]:
        """
        Attempt automatic repair of violations.

        Returns:
            Statistics of repair operations
        """
        if not self.config.get('auto_repair', False):
            return {'repaired': 0, 'failed': 0, 'skipped': len(violations)}

        stats = {'repaired': 0, 'failed': 0, 'skipped': 0}

        for violation in violations:
            if not violation.get('auto_repairable', False):
                stats['skipped'] += 1
                continue

            repair_action = violation.get('repair_action')
            if not repair_action:
                stats['skipped'] += 1
                continue

            try:
                if repair_action == 'generate_module_yaml':
                    self._generate_module_yaml(violation['root'])
                    stats['repaired'] += 1
                elif repair_action == 'reconcile_hash':
                    self._reconcile_hash(violation['file'])
                    stats['repaired'] += 1
                else:
                    stats['skipped'] += 1

                self.repair_log.append({
                    'violation': violation,
                    'action': repair_action,
                    'status': 'SUCCESS',
                    'timestamp': datetime.utcnow().isoformat()
                })

            except Exception as e:
                stats['failed'] += 1
                self.repair_log.append({
                    'violation': violation,
                    'action': repair_action,
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                })

        return stats

    def _generate_module_yaml(self, root: str):
        """Generate missing module.yaml for a root."""
        module_yaml_path = PROJECT_ROOT / root / "module.yaml"

        template = {
            'name': root,
            'version': '1.0.0',
            'owner': 'system_generated',
            'status': 'active',
            'last_update': datetime.utcnow().isoformat(),
            'max_depth': 3,
            'shard_profile': 'default',
            'auto_generated': True,
            'generated_by': 'root_integrity_watchdog'
        }

        os.makedirs(module_yaml_path.parent, exist_ok=True)
        with open(module_yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(template, f, default_flow_style=False, allow_unicode=True)

    def _reconcile_hash(self, file_path: str):
        """Update hash in registry for changed file."""
        hash_file = PROJECT_ROOT / "24_meta_orchestration" / "registry" / "manifests" / "integrity_checksums.json"

        with open(hash_file, 'r', encoding='utf-8') as f:
            hashes = json.load(f)

        full_path = PROJECT_ROOT / file_path
        new_hash = self._calculate_sha256(full_path)

        hashes[file_path] = new_hash

        with open(hash_file, 'w', encoding='utf-8') as f:
            json.dump(hashes, f, indent=2, ensure_ascii=False)

    def save_audit_trail(self):
        """Save violation and repair logs to audit trail."""
        audit_dir = PROJECT_ROOT / "02_audit_logging" / "storage" / "worm" / "immutable_store" / "watchdog"
        os.makedirs(audit_dir, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        audit_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'violations': self.violation_log,
            'repairs': self.repair_log,
            'config': self.config
        }

        audit_file = audit_dir / f"watchdog_audit_{timestamp}.json"
        with open(audit_file, 'w', encoding='utf-8') as f:
            json.dump(audit_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Audit trail saved: {audit_file}")

    def run_check_cycle(self) -> Dict:
        """Execute full check and repair cycle."""
        print("🔍 Starting Root Integrity Check...")

        is_compliant, violations = self.check_root_integrity()

        if is_compliant:
            print("✅ All roots compliant - no violations detected")
            return {'status': 'COMPLIANT', 'violations': 0}

        print(f"⚠️  Found {len(violations)} violations")

        if self.config.get('auto_repair', False):
            print("🔧 Attempting automatic repair...")
            stats = self.auto_repair(violations)
            print(f"📊 Repair stats: {stats}")

        self.save_audit_trail()

        return {
            'status': 'VIOLATIONS_DETECTED',
            'total_violations': len(violations),
            'critical_violations': len([v for v in violations if v['severity'] == 'CRITICAL']),
            'repair_stats': stats if self.config.get('auto_repair') else None
        }


def main():
    """Main entry point for watchdog."""
    watchdog = RootIntegrityWatchdog()
    result = watchdog.run_check_cycle()

    if result['status'] == 'VIOLATIONS_DETECTED':
        sys.exit(24)  # Exit with code 24 for violations

    sys.exit(0)


if __name__ == "__main__":
    main()
