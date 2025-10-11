"""
Dynamic Compliance Dashboard Backend

Reads compliance data from registry_anchor.json and dora_operational_metrics.yaml
to provide real-time compliance status visualization (Compliance-Ampel).

Version: 2025-Q4
Last Updated: 2025-10-07
Maintainer: edubrainboost
Classification: PUBLIC - Compliance Dashboard
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class ComplianceDashboard:
    """Dynamic compliance dashboard data provider."""

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize dashboard with repository root path."""
        self.repo_root = repo_root or Path(__file__).parent.parent
        self.registry_anchor_path = self.repo_root / "02_audit_logging/evidence/registry/registry_anchor.json"
        self.registry_lock_path = self.repo_root / "24_meta_orchestration/registry/locks/registry_lock.yaml"
        self.dora_metrics_path = self.repo_root / "23_compliance/mappings/dora_operational_metrics.yaml"
        self.mappings_dir = self.repo_root / "23_compliance/mappings"

    def load_registry_anchor(self) -> Dict[str, Any]:
        """Load registry anchor evidence trail."""
        if not self.registry_anchor_path.exists():
            return {
                "error": "Registry anchor not found",
                "anchors": [],
                "anchor_count": 0
            }

        with open(self.registry_anchor_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_registry_lock(self) -> Dict[str, Any]:
        """Load registry lock state."""
        if not self.registry_lock_path.exists():
            return {"error": "Registry lock not found"}

        with open(self.registry_lock_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_dora_metrics(self) -> Dict[str, Any]:
        """Load DORA operational metrics."""
        if not self.dora_metrics_path.exists():
            return {"error": "DORA metrics not found"}

        with open(self.dora_metrics_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_framework_mapping(self, framework: str) -> Dict[str, Any]:
        """Load specific framework mapping."""
        mapping_path = self.mappings_dir / f"{framework.lower()}_mapping.yaml"

        if not mapping_path.exists():
            return {"error": f"Mapping for {framework} not found"}

        with open(mapping_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def calculate_compliance_status(self, framework_data: Dict[str, Any]) -> Dict[str, str]:
        """Calculate compliance status (traffic light) for a framework."""
        metrics = framework_data.get("compliance_metrics", {})
        coverage_str = metrics.get("overall_coverage", "0%")

        try:
            coverage = int(coverage_str.rstrip("%"))
        except (ValueError, AttributeError):
            coverage = 0

        # Traffic light logic
        if coverage >= 95:
            status = "green"
            label = "COMPLIANT"
        elif coverage >= 80:
            status = "yellow"
            label = "PARTIAL"
        else:
            status = "red"
            label = "NON-COMPLIANT"

        return {
            "status": status,
            "label": label,
            "coverage": coverage_str,
            "coverage_numeric": coverage
        }

    def evaluate_dora_metrics(self) -> Dict[str, Any]:
        """Evaluate DORA operational metrics status."""
        dora_data = self.load_dora_metrics()

        if "error" in dora_data:
            return {"error": dora_data["error"]}

        metrics = dora_data.get("operational_metrics", {})

        # Count metrics by category
        categories = {
            "incident_management": 0,
            "resilience_testing": 0,
            "recovery_objectives": 0,
            "security_monitoring": 0,
            "third_party_risk": 0,
            "change_management": 0,
            "availability_metrics": 0
        }

        for category, metric_list in metrics.items():
            if isinstance(metric_list, list):
                categories[category] = len(metric_list)

        total_metrics = sum(categories.values())

        return {
            "total_metrics": total_metrics,
            "categories": categories,
            "status": "active" if total_metrics > 0 else "inactive"
        }

    def get_latest_anchor(self) -> Optional[Dict[str, Any]]:
        """Get the most recent registry anchor."""
        anchor_data = self.load_registry_anchor()

        if "error" in anchor_data or not anchor_data.get("anchors"):
            raise NotImplementedError("TODO: Implement this function")

        # Return the last anchor (most recent)
        return anchor_data["anchors"][-1]

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system legal awareness status."""
        registry_lock = self.load_registry_lock()

        if "error" in registry_lock:
            return {
                "system_status": "unknown",
                "legally_aware": False,
                "error": registry_lock["error"]
            }

        legal_awareness = registry_lock.get("legal_awareness", {})

        return {
            "system_status": legal_awareness.get("system_status", "unknown"),
            "legally_aware": legal_awareness.get("system_status") == "legally_aware",
            "compliance_framework": legal_awareness.get("compliance_framework", "N/A"),
            "blueprint_version": registry_lock.get("meta", {}).get("version", "N/A")
        }

    def get_framework_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get compliance status for all frameworks."""
        frameworks = ["GDPR", "DORA", "MiCA", "AMLD6"]
        statuses = {}

        for framework in frameworks:
            framework_data = self.load_framework_mapping(framework)

            if "error" in framework_data:
                statuses[framework] = {
                    "status": "red",
                    "label": "NOT FOUND",
                    "coverage": "0%",
                    "error": framework_data["error"]
                }
            else:
                statuses[framework] = self.calculate_compliance_status(framework_data)

                # Add controls info
                metrics = framework_data.get("compliance_metrics", {})
                statuses[framework]["implemented_controls"] = metrics.get("implemented_controls", 0)
                statuses[framework]["pending_controls"] = metrics.get("pending_controls", 0)
                statuses[framework]["planned_controls"] = metrics.get("planned_controls", 0)

        return statuses

    def get_compliance_summary(self) -> Dict[str, Any]:
        """Get complete compliance dashboard summary."""
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "system_status": self.get_system_status(),
            "frameworks": self.get_framework_statuses(),
            "dora_metrics": self.evaluate_dora_metrics(),
            "latest_anchor": self.get_latest_anchor(),
            "dashboard_version": "1.0"
        }

    def get_traffic_light_emoji(self, status: str) -> str:
        """Get emoji representation of traffic light status."""
        emoji_map = {
            "green": "🟢",
            "yellow": "🟡",
            "red": "🔴"
        }
        return emoji_map.get(status, "⚪")

    def generate_text_report(self) -> str:
        """Generate text-based compliance report."""
        summary = self.get_compliance_summary()

        report_lines = [
            "=" * 80,
            "COMPLIANCE DASHBOARD REPORT".center(80),
            "=" * 80,
            "",
            f"Generated: {summary['timestamp']}",
            "",
            "SYSTEM STATUS",
            "-" * 80,
        ]

        system_status = summary["system_status"]
        report_lines.append(f"Legal Awareness: {'✅ LEGALLY AWARE' if system_status['legally_aware'] else '❌ NOT AWARE'}")
        report_lines.append(f"System Status: {system_status['system_status'].upper()}")
        report_lines.append(f"Compliance Framework: {system_status['compliance_framework']}")
        report_lines.append(f"Blueprint Version: {system_status['blueprint_version']}")
        report_lines.append("")

        report_lines.append("FRAMEWORK COMPLIANCE STATUS")
        report_lines.append("-" * 80)

        for framework, status in summary["frameworks"].items():
            emoji = self.get_traffic_light_emoji(status["status"])
            impl = status.get("implemented_controls", 0)
            pending = status.get("pending_controls", 0)
            planned = status.get("planned_controls", 0)
            total = impl + pending + planned

            report_lines.append(f"{emoji} {framework:8s} | {status['label']:15s} | Coverage: {status['coverage']:5s} | Controls: {impl}/{total}")

        report_lines.append("")

        report_lines.append("DORA OPERATIONAL METRICS")
        report_lines.append("-" * 80)

        dora_metrics = summary["dora_metrics"]
        if "error" not in dora_metrics:
            report_lines.append(f"Total Metrics: {dora_metrics['total_metrics']}")
            report_lines.append(f"Status: {dora_metrics['status'].upper()}")
            report_lines.append("")
            report_lines.append("Metrics by Category:")
            for category, count in dora_metrics["categories"].items():
                if count > 0:
                    report_lines.append(f"  - {category.replace('_', ' ').title()}: {count}")
        else:
            report_lines.append(f"❌ {dora_metrics['error']}")

        report_lines.append("")

        latest_anchor = summary["latest_anchor"]
        if latest_anchor:
            report_lines.append("LATEST EVIDENCE ANCHOR")
            report_lines.append("-" * 80)
            report_lines.append(f"Anchor ID: {latest_anchor.get('anchor_id', 'N/A')}")
            report_lines.append(f"Timestamp: {latest_anchor.get('timestamp', 'N/A')}")
            report_lines.append(f"System Status: {latest_anchor.get('system_status', 'N/A')}")

            frameworks_data = latest_anchor.get("frameworks", {})
            if frameworks_data:
                report_lines.append("Framework Checksums:")
                for fw, checksum in frameworks_data.items():
                    report_lines.append(f"  - {fw.upper()}: {checksum[:24]}...")

        report_lines.append("")
        report_lines.append("=" * 80)

        return "\n".join(report_lines)


def main():
    """Main entry point for compliance dashboard."""
    import sys
    import io

    # Fix Windows encoding issues
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    dashboard = ComplianceDashboard()

    print("\n🎯 SSID Compliance Dashboard\n")

    # Generate and print text report
    report = dashboard.generate_text_report()
    print(report)

    # Optionally save JSON summary
    summary = dashboard.get_compliance_summary()
    output_path = Path(__file__).parent / "compliance_dashboard_output.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n📊 JSON summary saved to: {output_path}\n")


if __name__ == "__main__":
    main()
