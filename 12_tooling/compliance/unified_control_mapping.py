#!/usr/bin/env python3
"""
Unified Control Mapping Tool - V6.2
Scans all compliance framework mappings (DSGVO, DORA, MiCA) and identifies
equivalent control mechanisms across frameworks using hash-based matching.
Generates unified_control_matrix.json for cross-framework compliance verification.
"""
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

REPORTS_DIR = Path("02_audit_logging/reports")

class UnifiedControlMapper:
    """Map equivalent controls across compliance frameworks"""

    def __init__(self):
        self.dsgvo_data = None
        self.dora_data = None
        self.mica_data = None
        self.control_matrix = []

    def load_framework_mappings(self):
        """Load all framework mapping JSON files"""
        print("=" * 60)
        print("Unified Control Mapping - V6.2")
        print("=" * 60)
        print()

        # Load DSGVO mapping
        dsgvo_file = REPORTS_DIR / "compliance_mapping_dsgvo.json"
        if dsgvo_file.exists():
            with open(dsgvo_file, 'r', encoding='utf-8') as f:
                self.dsgvo_data = json.load(f)
            print(f"[OK] Loaded DSGVO mapping: {len(self.dsgvo_data['mappings'])} articles")
        else:
            print(f"[WARN] DSGVO mapping not found: {dsgvo_file}")
            self.dsgvo_data = {"mappings": []}

        # Load DORA mapping
        dora_file = REPORTS_DIR / "compliance_mapping_dora.json"
        if dora_file.exists():
            with open(dora_file, 'r', encoding='utf-8') as f:
                self.dora_data = json.load(f)
            print(f"[OK] Loaded DORA mapping: {len(self.dora_data['mappings'])} articles")
        else:
            print(f"[WARN] DORA mapping not found: {dora_file}")
            self.dora_data = {"mappings": []}

        # Load MiCA mapping
        mica_file = REPORTS_DIR / "compliance_mapping_mica.json"
        if mica_file.exists():
            with open(mica_file, 'r', encoding='utf-8') as f:
                self.mica_data = json.load(f)
            print(f"[OK] Loaded MiCA mapping: {len(self.mica_data['mappings'])} articles")
        else:
            print(f"[WARN] MiCA mapping not found: {mica_file}")
            self.mica_data = {"mappings": []}

        print()

    def normalize_policy_id(self, policy_string):
        """Extract and normalize policy ID from policy string"""
        # Extract policy identifiers from various formats
        # Examples:
        # "02_audit_logging: WORM storage" -> "02_audit_logging"
        # "policy_audit_worm: Immutable" -> "policy_audit_worm"
        # "23_compliance/policies/structure_policy.yaml" -> "structure_policy"

        if not policy_string:
            return None

        # Split on colon and take first part
        base = policy_string.split(':')[0].strip()

        # If it's a path, extract filename without extension
        if '/' in base:
            base = Path(base).stem

        return base

    def compute_control_hash(self, requirements, policies):
        """Compute hash based on requirements and policy content"""
        # Normalize requirements and policies for comparison
        req_text = " ".join(sorted([r.lower().strip() for r in requirements]))
        policy_ids = sorted([self.normalize_policy_id(p) for p in policies if self.normalize_policy_id(p)])
        policy_text = " ".join(policy_ids)

        # Combine and hash
        combined = f"{req_text}|{policy_text}"
        return hashlib.sha256(combined.encode('utf-8')).hexdigest()[:16]

    def identify_equivalent_controls(self):
        """Identify controls that are equivalent across frameworks"""
        print("Analyzing cross-framework control equivalence...")
        print("-" * 60)

        # Build control database with hashes
        control_db = defaultdict(list)

        # Process DSGVO
        for mapping in self.dsgvo_data.get("mappings", []):
            control_hash = self.compute_control_hash(
                mapping.get("requirements", []),
                mapping.get("ssid_policies", [])
            )
            control_db[control_hash].append({
                "framework": "DSGVO",
                "article": mapping.get("article"),
                "title": mapping.get("title"),
                "policies": mapping.get("ssid_policies", []),
                "compliance_level": mapping.get("compliance_level", "unknown")
            })

        # Process DORA
        for mapping in self.dora_data.get("mappings", []):
            control_hash = self.compute_control_hash(
                mapping.get("requirements", []),
                mapping.get("ssid_policies", [])
            )
            control_db[control_hash].append({
                "framework": "DORA",
                "article": mapping.get("article"),
                "title": mapping.get("title"),
                "policies": mapping.get("ssid_policies", []),
                "compliance_level": mapping.get("compliance_level", "unknown")
            })

        # Process MiCA
        for mapping in self.mica_data.get("mappings", []):
            control_hash = self.compute_control_hash(
                mapping.get("requirements", []),
                mapping.get("ssid_policies", [])
            )
            control_db[control_hash].append({
                "framework": "MiCA",
                "article": mapping.get("article"),
                "title": mapping.get("title"),
                "policies": mapping.get("ssid_policies", []),
                "compliance_level": mapping.get("compliance_level", "unknown")
            })

        # Generate control matrix for equivalent controls
        control_id_counter = 1

        for control_hash, control_instances in control_db.items():
            # Extract unique policy IDs across all instances
            all_policies = []
            for instance in control_instances:
                for policy in instance["policies"]:
                    policy_id = self.normalize_policy_id(policy)
                    if policy_id and policy_id not in all_policies:
                        all_policies.append(policy_id)

            # Determine control category based on policies
            control_category = self._categorize_control(all_policies)

            # Create unified control entry
            if len(control_instances) > 1:
                # This is a cross-framework equivalent control
                control_id = f"{control_category}_{control_id_counter:03d}"
                control_id_counter += 1

                equivalent_articles = [
                    f"{inst['framework']} {inst['article']}"
                    for inst in control_instances
                ]

                # Determine overall status (worst case)
                statuses = [inst["compliance_level"] for inst in control_instances]
                if "partial" in statuses:
                    overall_status = "verified_partial"
                elif all(s == "full" for s in statuses):
                    overall_status = "verified"
                else:
                    overall_status = "unknown"

                self.control_matrix.append({
                    "control_id": control_id,
                    "control_hash": control_hash,
                    "equivalent_articles": equivalent_articles,
                    "mapped_policies": sorted(all_policies),
                    "status": overall_status,
                    "frameworks_count": len(control_instances)
                })

        # Also add single-framework controls
        for control_hash, control_instances in control_db.items():
            if len(control_instances) == 1:
                instance = control_instances[0]
                all_policies = [self.normalize_policy_id(p) for p in instance["policies"] if self.normalize_policy_id(p)]
                control_category = self._categorize_control(all_policies)
                control_id = f"{control_category}_SINGLE_{control_id_counter:03d}"
                control_id_counter += 1

                status = "verified" if instance["compliance_level"] == "full" else "verified_partial"

                self.control_matrix.append({
                    "control_id": control_id,
                    "control_hash": control_hash,
                    "equivalent_articles": [f"{instance['framework']} {instance['article']}"],
                    "mapped_policies": sorted(all_policies),
                    "status": status,
                    "frameworks_count": 1
                })

        print(f"[OK] Identified {len(self.control_matrix)} unified controls")
        print(f"     - Cross-framework equivalents: {sum(1 for c in self.control_matrix if c['frameworks_count'] > 1)}")
        print(f"     - Single-framework controls: {sum(1 for c in self.control_matrix if c['frameworks_count'] == 1)}")
        print()

    def _categorize_control(self, policy_ids):
        """Categorize control based on policy IDs"""
        policy_text = " ".join(policy_ids).lower()

        if any(word in policy_text for word in ["encrypt", "crypto", "pqc", "quantum"]):
            return "SECURITY_ENCRYPTION"
        elif any(word in policy_text for word in ["audit", "logging", "worm"]):
            return "AUDIT_LOGGING"
        elif any(word in policy_text for word in ["identity", "auth", "vc_schema"]):
            return "IDENTITY_AUTH"
        elif any(word in policy_text for word in ["compliance", "policy", "enforcement"]):
            return "COMPLIANCE_GOVERNANCE"
        elif any(word in policy_text for word in ["observability", "metrics", "monitor"]):
            return "MONITORING_OBSERVABILITY"
        elif any(word in policy_text for word in ["pricing", "sla", "legal"]):
            return "LEGAL_PRICING"
        elif any(word in policy_text for word in ["risk", "incident"]):
            return "RISK_MANAGEMENT"
        else:
            return "GENERAL_CONTROL"

    def generate_unified_matrix(self):
        """Generate unified control matrix report"""
        output_file = REPORTS_DIR / "unified_control_matrix.json"

        report_data = {
            "version": "v6.2",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "description": "Unified control mapping across DSGVO, DORA, and MiCA frameworks",
            "frameworks": ["DSGVO", "DORA", "MiCA"],
            "total_controls": len(self.control_matrix),
            "cross_framework_controls": sum(1 for c in self.control_matrix if c['frameworks_count'] > 1),
            "single_framework_controls": sum(1 for c in self.control_matrix if c['frameworks_count'] == 1),
            "controls": sorted(self.control_matrix, key=lambda x: x["control_id"])
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        print(f"[OK] Unified control matrix saved: {output_file}")
        print()
        return output_file

    def print_summary(self):
        """Print summary of unified control mapping"""
        print("=" * 60)
        print("Unified Control Mapping Summary")
        print("=" * 60)
        print()

        # Category breakdown
        categories = defaultdict(int)
        for control in self.control_matrix:
            category = control["control_id"].rsplit("_", 1)[0] if "_SINGLE_" not in control["control_id"] else control["control_id"].rsplit("_", 2)[0]
            categories[category] += 1

        print("Control Categories:")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count} controls")

        print()
        print("Status Breakdown:")
        status_counts = defaultdict(int)
        for control in self.control_matrix:
            status_counts[control["status"]] += 1

        for status, count in sorted(status_counts.items()):
            print(f"  {status}: {count} controls")

        print()

def main():
    """Run unified control mapping"""
    mapper = UnifiedControlMapper()

    # Load framework mappings
    mapper.load_framework_mappings()

    # Identify equivalent controls
    mapper.identify_equivalent_controls()

    # Generate unified matrix
    output_file = mapper.generate_unified_matrix()

    # Print summary
    mapper.print_summary()

    print("=" * 60)
    print("Unified Control Mapping Complete")
    print("=" * 60)
    print()

    return 0

if __name__ == "__main__":
    exit(main())
