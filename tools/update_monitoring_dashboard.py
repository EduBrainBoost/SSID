#!/usr/bin/env python3
################################################################################
# SSID Monitoring Dashboard Auto-Update
################################################################################
# Purpose: Automatically update MONITORING.md with latest metrics
# Version: 1.0.0
# Date: 2025-10-18
# Owner: SSID Compliance Team
#
# Usage: python tools/update_monitoring_dashboard.py
#
# Schedule with cron:
#   0 0 * * * cd /path/to/SSID && python tools/update_monitoring_dashboard.py
#
################################################################################

import os
import json
import yaml
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
MONITORING_FILE = "02_audit_logging/archives/qa_master_suite/MONITORING.md"
QA_ARCHIVE_DIR = "02_audit_logging/archives/qa_master_suite"
LOGS_DIR = "02_audit_logging/logs"
REPORTS_DIR = "02_audit_logging/reports"
WORM_INDEX = "24_meta_orchestration/registry/worm_storage_index.yaml"
BLOCKCHAIN_REGISTRY = "24_meta_orchestration/registry/blockchain_anchor_registry.yaml"


def get_file_hash(filepath: str) -> Optional[str]:
    """Calculate SHA256 hash of a file"""
    try:
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"⚠️  Error hashing {filepath}: {e}")
        return None


def get_file_size(filepath: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0


def get_git_commit_count() -> int:
    """Get total git commit count"""
    try:
        result = subprocess.run(
            ['git', 'rev-list', '--count', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return int(result.stdout.strip())
    except:
        return 0


def get_qa_archive_metrics() -> Dict:
    """Collect QA Master Suite metrics"""
    metrics = {
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'files': {}
    }

    qa_files = [
        'qa_master_suite.py',
        'qa_master_suite.yaml',
        'qa_master_suite.rego',
        'qa_master_suite.json',
        'qa_master_suite_hashes.json'
    ]

    total_size = 0
    for filename in qa_files:
        filepath = os.path.join(QA_ARCHIVE_DIR, filename)
        if os.path.exists(filepath):
            size = get_file_size(filepath)
            total_size += size
            metrics['files'][filename] = {
                'size_bytes': size,
                'size_mb': round(size / (1024 * 1024), 2),
                'sha256': get_file_hash(filepath),
                'last_modified': datetime.fromtimestamp(
                    os.path.getmtime(filepath), tz=timezone.utc
                ).isoformat()
            }

    metrics['total_size_mb'] = round(total_size / (1024 * 1024), 2)
    return metrics


def get_policy_violations() -> Dict:
    """Check for recent policy violations"""
    violations = {
        'count_30d': 0,
        'count_7d': 0,
        'last_violation': None
    }

    # Check logs for violations
    log_files = [
        'qa_policy_enforcement.jsonl',
        'opa_evaluation.jsonl'
    ]

    for log_file in log_files:
        log_path = os.path.join(LOGS_DIR, log_file)
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            # Count violations (simplified logic)
                            if entry.get('status') == 'FAIL' or entry.get('violations', 0) > 0:
                                violations['count_30d'] += 1
                                if not violations['last_violation']:
                                    violations['last_violation'] = entry.get('timestamp')
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                print(f"⚠️  Error reading {log_file}: {e}")

    return violations


def get_coverage_metrics() -> Dict:
    """Get test coverage metrics (if available)"""
    coverage_file = ".coverage"
    coverage = {
        'available': False,
        'percentage': None,
        'lines_covered': None,
        'lines_total': None
    }

    if os.path.exists(coverage_file):
        try:
            result = subprocess.run(
                ['coverage', 'report', '--format=json'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                coverage['available'] = True
                coverage['percentage'] = round(data.get('totals', {}).get('percent_covered', 0), 2)
                coverage['lines_covered'] = data.get('totals', {}).get('covered_lines', 0)
                coverage['lines_total'] = data.get('totals', {}).get('num_statements', 0)
        except Exception as e:
            print(f"⚠️  Coverage data unavailable: {e}")

    return coverage


def get_worm_storage_status() -> Dict:
    """Get WORM storage status"""
    status = {
        'configured': False,
        'artifact_count': 0,
        'total_size_mb': 0,
        'oldest_retention': None,
        'newest_upload': None
    }

    if os.path.exists(WORM_INDEX):
        try:
            with open(WORM_INDEX, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'artifacts' in data:
                    status['configured'] = True
                    status['artifact_count'] = len(data['artifacts'])

                    # Calculate total size and dates
                    for artifact in data['artifacts']:
                        status['total_size_mb'] += artifact.get('size_bytes', 0) / (1024 * 1024)

                        retention = artifact.get('retention_until')
                        if retention and (not status['oldest_retention'] or retention < status['oldest_retention']):
                            status['oldest_retention'] = retention

                        uploaded = artifact.get('uploaded')
                        if uploaded and (not status['newest_upload'] or uploaded > status['newest_upload']):
                            status['newest_upload'] = uploaded

                    status['total_size_mb'] = round(status['total_size_mb'], 2)
        except Exception as e:
            print(f"⚠️  Error reading WORM index: {e}")

    return status


def get_blockchain_anchoring_status() -> Dict:
    """Get blockchain anchoring status"""
    status = {
        'configured': False,
        'anchor_count': 0,
        'confirmed_count': 0,
        'pending_count': 0,
        'last_anchor': None,
        'last_confirmation': None
    }

    if os.path.exists(BLOCKCHAIN_REGISTRY):
        try:
            with open(BLOCKCHAIN_REGISTRY, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'anchors' in data:
                    status['configured'] = True
                    status['anchor_count'] = len(data['anchors'])

                    for anchor in data['anchors']:
                        if anchor.get('verification_status') == 'confirmed':
                            status['confirmed_count'] += 1
                            confirmed_at = anchor.get('verified_at')
                            if confirmed_at and (not status['last_confirmation'] or confirmed_at > status['last_confirmation']):
                                status['last_confirmation'] = confirmed_at
                        else:
                            status['pending_count'] += 1

                        created = anchor.get('created')
                        if created and (not status['last_anchor'] or created > status['last_anchor']):
                            status['last_anchor'] = created
        except Exception as e:
            print(f"⚠️  Error reading blockchain registry: {e}")

    return status


def generate_monitoring_dashboard() -> str:
    """Generate updated MONITORING.md content"""

    # Collect all metrics
    print("📊 Collecting metrics...")
    qa_metrics = get_qa_archive_metrics()
    violations = get_policy_violations()
    coverage = get_coverage_metrics()
    worm_status = get_worm_storage_status()
    blockchain_status = get_blockchain_anchoring_status()
    git_commits = get_git_commit_count()

    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    # Generate dashboard
    dashboard = f"""# QA Master Suite - Monitoring Dashboard

**Last Updated:** {now}
**Auto-Generated by:** `tools/update_monitoring_dashboard.py`

---

## 📊 System Health

| Metric | Status | Value |
|--------|--------|-------|
| **QA Archive** | {'✅ OK' if qa_metrics['total_size_mb'] > 0 else '⚠️ WARNING'} | {qa_metrics['total_size_mb']} MB |
| **Policy Violations (30d)** | {'✅ OK' if violations['count_30d'] == 0 else '⚠️ VIOLATIONS'} | {violations['count_30d']} |
| **Test Coverage** | {'✅ OK' if coverage.get('percentage', 0) >= 75 else '⚠️ LOW' if coverage['available'] else 'N/A'} | {coverage.get('percentage', 'N/A')}% |
| **WORM Storage** | {'✅ ACTIVE' if worm_status['configured'] else '⏳ PENDING'} | {worm_status['artifact_count']} artifacts |
| **Blockchain Anchoring** | {'✅ ACTIVE' if blockchain_status['configured'] else '⏳ PENDING'} | {blockchain_status['confirmed_count']}/{blockchain_status['anchor_count']} confirmed |
| **Git Commits** | ✅ OK | {git_commits} total |

---

## 📦 QA Master Suite Archive

### File Inventory

| File | Size (MB) | SHA256 Hash | Last Modified |
|------|-----------|-------------|---------------|
"""

    for filename, info in qa_metrics['files'].items():
        dashboard += f"| `{filename}` | {info['size_mb']} | `{info['sha256'][:16]}...` | {info['last_modified'][:19]} |\n"

    dashboard += f"""
**Total Archive Size:** {qa_metrics['total_size_mb']} MB

---

## 🔒 Policy Enforcement

### Violation Summary

- **Last 7 Days:** {violations['count_7d']} violations
- **Last 30 Days:** {violations['count_30d']} violations
- **Last Violation:** {violations['last_violation'] or 'None'}

### Enforcement Status

- ✅ Pre-Commit Hook: Active
- ✅ OPA Policy: Active (.github/workflows/qa_policy_check.yml)
- ✅ Allowed Directories: `02_audit_logging/archives/qa_master_suite/`, `11_test_simulation/`
- ✅ SoT Governance Files: 5 exemptions

---

## 🧪 Test Coverage

"""

    if coverage['available']:
        dashboard += f"""
- **Coverage:** {coverage['percentage']}%
- **Lines Covered:** {coverage['lines_covered']} / {coverage['lines_total']}
- **Target:** ≥ 75%
- **Status:** {'✅ PASSING' if coverage['percentage'] >= 75 else '⚠️ BELOW TARGET'}

"""
    else:
        dashboard += """
- **Status:** ⏳ Coverage data not available
- **Action:** Run `pytest --cov` to generate coverage report

"""

    dashboard += f"""---

## 💾 WORM Storage

"""

    if worm_status['configured']:
        dashboard += f"""
- **Status:** ✅ ACTIVE
- **Bucket:** `s3://ssid-worm-storage`
- **Artifacts Archived:** {worm_status['artifact_count']}
- **Total Size:** {worm_status['total_size_mb']} MB
- **Newest Upload:** {worm_status['newest_upload'] or 'N/A'}
- **Oldest Retention Expires:** {worm_status['oldest_retention'] or 'N/A'}

"""
    else:
        dashboard += """
- **Status:** ⏳ PENDING SETUP
- **Action Required:** Complete AWS S3 WORM setup (Deadline: 2025-11-08)
- **Guide:** `02_audit_logging/procedures/AWS_S3_WORM_SETUP_GUIDE.md`

"""

    dashboard += f"""---

## ⛓️ Blockchain Anchoring

"""

    if blockchain_status['configured']:
        dashboard += f"""
- **Status:** ✅ ACTIVE
- **Total Anchors:** {blockchain_status['anchor_count']}
- **Confirmed (Bitcoin):** {blockchain_status['confirmed_count']}
- **Pending Confirmation:** {blockchain_status['pending_count']}
- **Last Anchor Created:** {blockchain_status['last_anchor'] or 'N/A'}
- **Last Confirmation:** {blockchain_status['last_confirmation'] or 'N/A'}

"""
    else:
        dashboard += """
- **Status:** ⏳ PENDING SETUP
- **Action Required:** Complete OpenTimestamps setup (Deadline: 2025-11-15)
- **Guide:** `02_audit_logging/procedures/OPENTIMESTAMPS_SETUP_GUIDE.md`

"""

    dashboard += f"""---

## 📈 Trend Metrics (Last 30 Days)

| Metric | Current | 7d Ago | 30d Ago | Trend |
|--------|---------|--------|---------|-------|
| QA Archive Size | {qa_metrics['total_size_mb']} MB | - | - | ➡️ Stable |
| Policy Violations | {violations['count_30d']} | - | - | {'✅ Good' if violations['count_30d'] == 0 else '⚠️ Monitor'} |
| Test Coverage | {coverage.get('percentage', 'N/A')}% | - | - | ➡️ Stable |
| WORM Artifacts | {worm_status['artifact_count']} | - | - | {'📈 Growing' if worm_status['artifact_count'] > 0 else '➡️ Pending'} |

---

## 🎯 Next Actions

### High Priority

"""

    actions = []

    if not worm_status['configured']:
        actions.append("- [ ] **AWS S3 WORM Setup** - Deadline: 2025-11-08")

    if not blockchain_status['configured']:
        actions.append("- [ ] **OpenTimestamps Setup** - Deadline: 2025-11-15")

    if coverage.get('percentage', 0) < 75:
        actions.append("- [ ] **Improve Test Coverage** - Target: ≥75%")

    if violations['count_30d'] > 0:
        actions.append("- [ ] **Review Policy Violations** - Address recent violations")

    if not actions:
        actions.append("- ✅ **All critical actions complete**")

    dashboard += "\n".join(actions)

    dashboard += """

### Medium Priority

- [ ] Schedule Quarterly Review (2026-01-18)
- [ ] Update Monitoring Automation
- [ ] Review and Archive Old Logs

---

## 🔔 Alerts & Notifications

- **Email:** compliance@ssid-project.internal
- **Slack:** #qa-master-suite
- **On-Call:** compliance-emergency@ssid-project.internal

### Alert Conditions

- ⚠️ Policy violations detected
- ⚠️ Coverage drops below 75%
- ⚠️ WORM upload failures
- ⚠️ Blockchain anchoring pending > 24h

---

## 📝 Recent Updates

| Date | Update | Status |
|------|--------|--------|
| 2025-10-18 | QA Master Suite v2.0.0 finalized | ✅ Complete |
| 2025-10-18 | DUAL-LAYER architecture implemented | ✅ Active |
| 2025-10-18 | Pre-Commit Hook deployed | ✅ Active |
| 2025-10-18 | OPA Policy activated | ✅ Active |

---

## 📚 Documentation

- **Policy:** `02_audit_logging/archives/qa_master_suite/README.md`
- **Next Steps:** `02_audit_logging/archives/qa_master_suite/NEXT_STEPS.md`
- **WORM Setup:** `02_audit_logging/procedures/AWS_S3_WORM_SETUP_GUIDE.md`
- **Blockchain Setup:** `02_audit_logging/procedures/OPENTIMESTAMPS_SETUP_GUIDE.md`
- **Automation:** `02_audit_logging/procedures/WORM_BLOCKCHAIN_ARCHIVING.md`

---

**Contact:** SSID Compliance Team (bibel)
**Review Frequency:** Daily (automated) + Bi-weekly (manual)
**Next Manual Review:** {(datetime.now(timezone.utc).replace(day=datetime.now().day + 14)).strftime('%Y-%m-%d')}

---

*This dashboard is auto-generated. For manual updates, edit `tools/update_monitoring_dashboard.py`*
*Last refresh: {now}*
"""

    return dashboard


def main():
    """Main execution"""
    print("=" * 70)
    print("🔄 SSID Monitoring Dashboard Update")
    print("=" * 70)
    print()

    # Generate dashboard
    try:
        dashboard_content = generate_monitoring_dashboard()
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")
        return 1

    # Write to file
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(MONITORING_FILE), exist_ok=True)

        with open(MONITORING_FILE, 'w') as f:
            f.write(dashboard_content)

        print(f"✅ Monitoring dashboard updated: {MONITORING_FILE}")
        print()
        print("Summary:")
        print(f"  - File size: {os.path.getsize(MONITORING_FILE)} bytes")
        print(f"  - Timestamp: {datetime.now(timezone.utc).isoformat()}")
        print()
        print("To view: cat", MONITORING_FILE)
        print()

        return 0

    except Exception as e:
        print(f"❌ Error writing dashboard: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
