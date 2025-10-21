#!/usr/bin/env python3
"""
Compliance Framework Mapper v2 - Achse 3
Loads compliance mappings from JSON files in 23_compliance/mappings/
Supports: DSGVO, DORA, MiCA, W3C DID, NIST CSF, eIDAS, EU AI Act, ISO 27001, ISO 23837
"""
import json
from pathlib import Path
from datetime import datetime

MAPPINGS_DIR = Path("23_compliance/mappings")
REPORTS_DIR = Path("02_audit_logging/reports")

class ComplianceMapperV2:
    """Load and validate compliance mappings from JSON files"""

    def __init__(self):
        self.frameworks = {}
        self.supported_frameworks = [
            "dsgvo_mapping.json",
            "dora_mapping.yaml",  # YAML exists
            "mica_mapping.yaml",  # YAML exists
            "w3c_mapping.json",
            "nist_mapping.json",
            "eidas_mapping.json",
            "eu_ai_act_mapping.json",
            "iso_27001_mapping.json",
            "iso_23837_mapping.json"
        ]

    def load_json_mapping(self, filepath: Path) -> dict:
        """Load compliance mapping from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"[WARN] Failed to load {filepath}: {e}")
            return None

    def load_yaml_mapping(self, filepath: Path) -> dict:
        """Load compliance mapping from YAML file (legacy)"""
        try:
            import yaml
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            # Convert YAML to JSON-like structure
            return {
                "meta": data.get("meta", {}),
                "mappings": data.get("mappings", []),
                "compliance_metrics": data.get("compliance_metrics", {})
            }
        except ImportError:
            print(f"[WARN] PyYAML not installed, skipping {filepath}")
            return None
        except Exception as e:
            print(f"[WARN] Failed to load {filepath}: {e}")
            return None

    def load_all_frameworks(self):
        """Load all compliance framework mappings"""
        print("=" * 80)
        print("Compliance Framework Mapper v2 - Loading All Frameworks")
        print("=" * 80)
        print()

        for framework_file in MAPPINGS_DIR.glob("*.json"):
            framework_name = framework_file.stem.replace("_mapping", "").upper()
            data = self.load_json_mapping(framework_file)
            if data:
                self.frameworks[framework_name] = {
                    "file": framework_file.name,
                    "data": data,
                    "format": "json"
                }
                print(f"[OK] Loaded {framework_name} from {framework_file.name}")

        # Also load YAML mappings if they exist
        for yaml_file in MAPPINGS_DIR.glob("*.yaml"):
            framework_name = yaml_file.stem.replace("_mapping", "").upper()
            if framework_name not in self.frameworks:  # Don't override JSON
                data = self.load_yaml_mapping(yaml_file)
                if data:
                    self.frameworks[framework_name] = {
                        "file": yaml_file.name,
                        "data": data,
                        "format": "yaml"
                    }
                    print(f"[OK] Loaded {framework_name} from {yaml_file.name}")

        print()
        print(f"Total frameworks loaded: {len(self.frameworks)}")
        print()

    def calculate_framework_score(self, framework_data: dict) -> dict:
        """Calculate compliance score for a framework"""
        mappings = framework_data.get("mappings", [])

        if not mappings:
            return {
                "total_controls": 0,
                "implemented": 0,
                "planned": 0,
                "score": 0.0
            }

        # Filter out non-dict entries (some YAML files have strings)
        valid_mappings = [m for m in mappings if isinstance(m, dict)]

        if not valid_mappings:
            return {
                "total_controls": 0,
                "implemented": 0,
                "planned": 0,
                "score": 0.0
            }

        total = len(valid_mappings)
        implemented = sum(1 for m in valid_mappings if m.get("implementation_status") == "implemented")
        planned = sum(1 for m in valid_mappings if m.get("implementation_status") == "planned")

        # Score: implemented = 100%, planned = 50%
        score = ((implemented * 1.0) + (planned * 0.5)) / total * 100 if total > 0 else 0

        return {
            "total_controls": total,
            "implemented": implemented,
            "planned": planned,
            "score": round(score, 2)
        }

    def generate_compliance_summary(self):
        """Generate summary of all compliance frameworks"""
        print("=" * 80)
        print("Compliance Framework Summary")
        print("=" * 80)
        print()

        scores = {}
        for framework_name, framework_info in self.frameworks.items():
            score_data = self.calculate_framework_score(framework_info["data"])
            scores[framework_name] = score_data

            print(f"{framework_name}:")
            print(f"  Total Controls:      {score_data['total_controls']}")
            print(f"  Implemented:         {score_data['implemented']}")
            print(f"  Planned:             {score_data['planned']}")
            print(f"  Compliance Score:    {score_data['score']:.2f}%")
            print()

        return scores

    def save_compliance_reports(self, scores: dict):
        """Save individual compliance reports"""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        print("=" * 80)
        print("Saving Compliance Reports")
        print("=" * 80)
        print()

        for framework_name, framework_info in self.frameworks.items():
            report_file = REPORTS_DIR / f"compliance_mapping_{framework_name.lower()}.json"

            report_data = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "framework": framework_name,
                "source_file": framework_info["file"],
                "data": framework_info["data"],
                "score": scores.get(framework_name, {})
            }

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2)

            print(f"[OK] {framework_name} report saved: {report_file}")

        print()

    def generate_forensic_compliance_summary(self, scores: dict):
        """Generate summary for forensic validation"""
        # Count frameworks with score >= 80%
        mapped_count = sum(1 for score in scores.values() if score["score"] >= 80.0)
        total_count = len(scores)

        overall_score = (mapped_count / total_count * 100) if total_count > 0 else 0

        summary = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "frameworks_total": total_count,
            "frameworks_mapped": mapped_count,
            "overall_compliance_score": round(overall_score, 2),
            "frameworks": scores
        }

        summary_file = REPORTS_DIR / "compliance_frameworks_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        print(f"[OK] Compliance summary saved: {summary_file}")
        print()

        return summary

def main():
    """Run compliance framework mapping"""
    mapper = ComplianceMapperV2()

    # Load all frameworks
    mapper.load_all_frameworks()

    # Generate compliance summary
    scores = mapper.generate_compliance_summary()

    # Save reports
    mapper.save_compliance_reports(scores)

    # Generate forensic summary
    summary = mapper.generate_forensic_compliance_summary(scores)

    # Final assessment
    print("=" * 80)
    print("Compliance Mapping Complete")
    print("=" * 80)
    print()
    print(f"Frameworks Mapped:       {summary['frameworks_mapped']} / {summary['frameworks_total']}")
    print(f"Overall Compliance:      {summary['overall_compliance_score']:.2f}%")
    print()

    if summary['overall_compliance_score'] >= 90:
        print("[OK] EXCELLENT: Comprehensive compliance coverage")
        return 0
    elif summary['overall_compliance_score'] >= 70:
        print("[OK] GOOD: Strong compliance foundation")
        return 0
    elif summary['overall_compliance_score'] >= 50:
        print("[OK] ACCEPTABLE: Compliance framework in place")
        return 0
    else:
        print("[WARN] NEEDS IMPROVEMENT: Review compliance gaps")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
