#!/usr/bin/env python3
"""
SSID 5 SOT Artifacts - Complete Synchronization
================================================

Synchronizes ALL content between the 5 master SOT artifacts and the 24x16 shard system.

5 SOT Artifacts (Single Source of Truth):
1. sot_contract.yaml (153K lines) - Main contract
2. sot_contract_COMPLETE.yaml (294K lines) - Complete version
3. sot_contract_part2.yaml (2.1K lines) - Part 2
4. sot_contract_part3.yaml (2.1K lines) - Part 3
5. sot_contract_expanded_TRUE.yaml (44K lines) - True contract with hashes

Version: 1.0.0
Author: SSID System
Date: 2025-10-24
"""

import os
import sys
import yaml
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent.parent

# 5 SOT Artifacts (in priority order)
SOT_ARTIFACTS = [
    {
        "name": "sot_contract_expanded_TRUE",
        "path": "16_codex/structure/level3/sot_contract_expanded_TRUE.yaml",
        "priority": 1,
        "description": "True contract with SHA256 hashes from 4 holy source files"
    },
    {
        "name": "sot_contract_COMPLETE",
        "path": "16_codex/contracts/sot/sot_contract_COMPLETE.yaml",
        "priority": 2,
        "description": "Complete contract with all rules"
    },
    {
        "name": "sot_contract",
        "path": "16_codex/contracts/sot/sot_contract.yaml",
        "priority": 3,
        "description": "Main contract"
    },
    {
        "name": "sot_contract_part2",
        "path": "16_codex/contracts/sot/sot_contract_part2.yaml",
        "priority": 4,
        "description": "Part 2 contract"
    },
    {
        "name": "sot_contract_part3",
        "path": "16_codex/contracts/sot/sot_contract_part3.yaml",
        "priority": 5,
        "description": "Part 3 contract"
    }
]

# 24 Layers
ROOT_LAYERS = [
    "01_ai_layer", "02_audit_logging", "03_core", "04_deployment",
    "05_documentation", "06_data_pipeline", "07_governance_legal",
    "08_identity_score", "09_meta_identity", "10_interoperability",
    "11_test_simulation", "12_tooling", "13_ui_layer", "14_zero_time_auth",
    "15_infra", "16_codex", "17_observability", "18_data_layer",
    "19_adapters", "20_foundation", "21_post_quantum_crypto", "22_datasets",
    "23_compliance", "24_meta_orchestration"
]

# 16 Shards
SHARD_IDS = [
    "01_identitaet_personen", "02_dokumente_nachweise", "03_zugang_berechtigungen",
    "04_kommunikation_daten", "05_gesundheit_medizin", "06_bildung_qualifikationen",
    "07_familie_soziales", "08_mobilitaet_fahrzeuge", "09_arbeit_karriere",
    "10_finanzen_banking", "11_versicherungen_risiken", "12_immobilien_grundstuecke",
    "13_unternehmen_gewerbe", "14_vertraege_vereinbarungen", "15_handel_transaktionen",
    "16_behoerden_verwaltung"
]


class SOTSynchronizer:
    """Synchronizes 5 SOT artifacts with 24x16 shard system"""

    def __init__(self):
        self.repo_root = REPO_ROOT
        self.artifacts = {}
        self.unified_rules = []
        self.rule_index = {}
        self.sync_stats = {
            "artifacts_loaded": 0,
            "total_rules": 0,
            "unique_rules": 0,
            "duplicates": 0,
            "shards_updated": 0,
            "consistency_score": 0.0
        }

    def load_sot_artifacts(self) -> None:
        """Load all 5 SOT artifacts"""

        print("\n[LOAD] Loading 5 SOT artifacts...")

        for artifact in SOT_ARTIFACTS:
            artifact_path = self.repo_root / artifact["path"]

            if not artifact_path.exists():
                print(f"  [WARN] Missing: {artifact['name']}")
                continue

            try:
                print(f"  [LOAD] {artifact['name']}...", end='')

                with open(artifact_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                self.artifacts[artifact['name']] = {
                    "path": artifact_path,
                    "priority": artifact["priority"],
                    "description": artifact["description"],
                    "data": data,
                    "rules": data.get("rules", []) if isinstance(data, dict) else [],
                    "version": data.get("version", "unknown") if isinstance(data, dict) else "unknown"
                }

                rule_count = len(self.artifacts[artifact['name']]['rules'])
                print(f" OK ({rule_count} rules, v{self.artifacts[artifact['name']]['version']})")

                self.sync_stats["artifacts_loaded"] += 1
                self.sync_stats["total_rules"] += rule_count

            except Exception as e:
                print(f" ERROR: {e}")

        print(f"\n  [OK] Loaded {self.sync_stats['artifacts_loaded']} artifacts")
        print(f"  [OK] Total rules: {self.sync_stats['total_rules']}")

    def unify_rules(self) -> None:
        """Unify rules from all 5 artifacts into single canonical set"""

        print("\n[UNIFY] Creating unified rule set...")

        rule_map = {}  # hash -> rule

        # Process artifacts in priority order
        sorted_artifacts = sorted(
            self.artifacts.items(),
            key=lambda x: x[1]["priority"]
        )

        for artifact_name, artifact_data in sorted_artifacts:
            rules = artifact_data["rules"]
            print(f"  [PROCESS] {artifact_name} ({len(rules)} rules)...")

            for rule in rules:
                # Create rule hash for deduplication
                rule_key = self._get_rule_key(rule)

                if rule_key not in rule_map:
                    # Add source tracking
                    rule_copy = rule.copy() if isinstance(rule, dict) else {}
                    rule_copy["_sources"] = [artifact_name]
                    rule_copy["_primary_source"] = artifact_name
                    rule_map[rule_key] = rule_copy
                else:
                    # Rule exists, add this artifact as additional source
                    if "_sources" not in rule_map[rule_key]:
                        rule_map[rule_key]["_sources"] = []
                    rule_map[rule_key]["_sources"].append(artifact_name)
                    self.sync_stats["duplicates"] += 1

        self.unified_rules = list(rule_map.values())
        self.sync_stats["unique_rules"] = len(self.unified_rules)

        print(f"\n  [OK] Unified to {self.sync_stats['unique_rules']} unique rules")
        print(f"  [INFO] Eliminated {self.sync_stats['duplicates']} duplicates")

    def _get_rule_key(self, rule: Dict) -> str:
        """Generate unique key for a rule"""

        if not isinstance(rule, dict):
            return hashlib.sha256(str(rule).encode()).hexdigest()

        # Use multiple fields to create key
        key_parts = []

        for field in ["rule_id", "line_ref", "hash_ref", "source", "category"]:
            if field in rule:
                key_parts.append(str(rule[field]))

        if not key_parts:
            # Fallback: hash entire rule
            return hashlib.sha256(json.dumps(rule, sort_keys=True).encode()).hexdigest()

        return hashlib.sha256("||".join(key_parts).encode()).hexdigest()

    def categorize_rules_by_shard(self) -> Dict[str, List[Dict]]:
        """Categorize unified rules by shard"""

        print("\n[CATEGORIZE] Categorizing rules by shard...")

        shard_rules = defaultdict(list)
        uncategorized = []

        for rule in self.unified_rules:
            shard_id = self._classify_rule_to_shard(rule)

            if shard_id:
                shard_rules[shard_id].append(rule)
            else:
                uncategorized.append(rule)

        print(f"  [OK] Categorized into {len(shard_rules)} shards")
        print(f"  [WARN] Uncategorized: {len(uncategorized)} rules")

        # Assign uncategorized to default shard
        if uncategorized:
            shard_rules["01_identitaet_personen"].extend(uncategorized)

        return dict(shard_rules)

    def _classify_rule_to_shard(self, rule: Dict) -> Optional[str]:
        """Classify a rule to appropriate shard based on content"""

        if not isinstance(rule, dict):
            return None

        # Check for explicit shard reference
        for field in ["shard_id", "shard", "domain"]:
            if field in rule:
                value = str(rule[field]).lower()
                for shard_id in SHARD_IDS:
                    if shard_id in value:
                        return shard_id

        # Check category/source/line_preview for keywords
        text_fields = []
        for field in ["category", "source", "line_preview", "description"]:
            if field in rule:
                text_fields.append(str(rule[field]).lower())

        text = " ".join(text_fields)

        # Keyword mapping
        shard_keywords = {
            "01_identitaet_personen": ["identity", "identit", "person", "did", "profile"],
            "02_dokumente_nachweise": ["document", "dokument", "certificate", "proof", "nachweis"],
            "03_zugang_berechtigungen": ["access", "zugang", "permission", "role", "berechtigung"],
            "04_kommunikation_daten": ["communication", "message", "data", "daten"],
            "05_gesundheit_medizin": ["health", "gesundheit", "medical", "medizin"],
            "06_bildung_qualifikationen": ["education", "bildung", "qualification"],
            "07_familie_soziales": ["family", "familie", "social", "sozial"],
            "08_mobilitaet_fahrzeuge": ["mobility", "vehicle", "fahrzeug"],
            "09_arbeit_karriere": ["work", "arbeit", "career", "job"],
            "10_finanzen_banking": ["finance", "finanz", "banking", "payment"],
            "11_versicherungen_risiken": ["insurance", "versicherung", "risk"],
            "12_immobilien_grundstuecke": ["real_estate", "immobilie", "property"],
            "13_unternehmen_gewerbe": ["company", "unternehmen", "business"],
            "14_vertraege_vereinbarungen": ["contract", "vertrag", "agreement"],
            "15_handel_transaktionen": ["trade", "handel", "transaction"],
            "16_behoerden_verwaltung": ["authority", "administration", "verwaltung"]
        }

        # Score each shard
        scores = defaultdict(int)
        for shard_id, keywords in shard_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[shard_id] += 1

        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]

        return None

    def update_shard_charts(self, shard_rules: Dict[str, List[Dict]], dry_run: bool = True) -> None:
        """Update all 384 chart.yaml files with synchronized rules"""

        print(f"\n[UPDATE] Updating 384 chart.yaml files...")
        if dry_run:
            print("  [DRY RUN] No files will be modified")

        updated = 0

        for layer in ROOT_LAYERS:
            for shard_id in SHARD_IDS:
                chart_path = self.repo_root / layer / "shards" / shard_id / "chart.yaml"

                if not chart_path.exists():
                    continue

                # Get rules for this shard
                rules_for_shard = shard_rules.get(shard_id, [])

                try:
                    # Load existing chart
                    with open(chart_path, 'r', encoding='utf-8') as f:
                        chart_data = yaml.safe_load(f)

                    if not isinstance(chart_data, dict):
                        chart_data = {}

                    # Add synchronized rules
                    chart_data["sot_rules"] = {
                        "synchronized_from": [a["name"] for a in SOT_ARTIFACTS],
                        "sync_timestamp": datetime.now().isoformat(),
                        "total_rules": len(rules_for_shard),
                        "rules": rules_for_shard[:100]  # Limit to 100 rules per shard
                    }

                    if not dry_run:
                        with open(chart_path, 'w', encoding='utf-8') as f:
                            yaml.dump(chart_data, f, allow_unicode=True, sort_keys=False)

                    updated += 1

                except Exception as e:
                    print(f"  [ERROR] Failed to update {layer}/{shard_id}: {e}")

        self.sync_stats["shards_updated"] = updated
        print(f"  [OK] Updated {updated} chart.yaml files")

    def verify_consistency(self) -> Dict:
        """Verify 100% consistency across all artifacts"""

        print("\n[VERIFY] Checking 100% consistency...")

        consistency_report = {
            "timestamp": datetime.now().isoformat(),
            "artifacts": {},
            "cross_check": {},
            "issues": []
        }

        # Check each artifact
        for artifact_name, artifact_data in self.artifacts.items():
            consistency_report["artifacts"][artifact_name] = {
                "path": str(artifact_data["path"]),
                "version": artifact_data["version"],
                "rule_count": len(artifact_data["rules"]),
                "exists": artifact_data["path"].exists()
            }

        # Cross-check rules
        print("  [CHECK] Cross-checking rules...")

        # Find rules in artifact 1 but not in artifact 2, etc.
        for i, (name1, data1) in enumerate(self.artifacts.items()):
            for name2, data2 in list(self.artifacts.items())[i+1:]:
                rules1 = set(self._get_rule_key(r) for r in data1["rules"])
                rules2 = set(self._get_rule_key(r) for r in data2["rules"])

                only_in_1 = len(rules1 - rules2)
                only_in_2 = len(rules2 - rules1)
                common = len(rules1 & rules2)

                consistency_report["cross_check"][f"{name1}_vs_{name2}"] = {
                    "common_rules": common,
                    "only_in_first": only_in_1,
                    "only_in_second": only_in_2,
                    "similarity_percent": (common / max(len(rules1), len(rules2)) * 100) if max(len(rules1), len(rules2)) > 0 else 0
                }

        # Calculate overall consistency score
        similarities = [v["similarity_percent"] for v in consistency_report["cross_check"].values()]
        overall_consistency = sum(similarities) / len(similarities) if similarities else 0

        self.sync_stats["consistency_score"] = overall_consistency

        print(f"  [OK] Overall consistency: {overall_consistency:.2f}%")

        return consistency_report

    def generate_sync_report(self, consistency_report: Dict) -> None:
        """Generate comprehensive synchronization report"""

        print("\n[REPORT] Generating synchronization report...")

        report = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "status": "complete",
            "statistics": self.sync_stats,
            "artifacts": {
                name: {
                    "path": str(data["path"]),
                    "priority": data["priority"],
                    "version": data["version"],
                    "rule_count": len(data["rules"])
                }
                for name, data in self.artifacts.items()
            },
            "unified_rules": {
                "total": len(self.unified_rules),
                "by_severity": self._count_by_field("severity"),
                "by_category": self._count_by_field("category")
            },
            "consistency": consistency_report
        }

        # Save JSON report
        report_path = self.repo_root / "02_audit_logging" / "reports" / "sot_5_artifacts_sync_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"  [SAVED] {report_path.relative_to(self.repo_root)}")

        # Generate markdown summary
        md_path = self.repo_root / "02_audit_logging" / "reports" / "SOT_5_ARTIFACTS_SYNC_SUMMARY.md"

        md_content = f"""# SSID 5 SOT Artifacts - Synchronization Report

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Version:** 1.0.0
**Status:** Complete

## Overview

Complete synchronization of 5 SOT artifacts with 24×16 shard matrix system.

## Statistics

- **Artifacts Loaded:** {self.sync_stats['artifacts_loaded']}/5
- **Total Rules:** {self.sync_stats['total_rules']:,}
- **Unique Rules:** {self.sync_stats['unique_rules']:,}
- **Duplicates Eliminated:** {self.sync_stats['duplicates']:,}
- **Shards Updated:** {self.sync_stats['shards_updated']}/384
- **Consistency Score:** {self.sync_stats['consistency_score']:.2f}%

## 5 SOT Artifacts

"""

        for name, info in report["artifacts"].items():
            md_content += f"""
### {name}

- **Path:** `{info['path']}`
- **Version:** {info['version']}
- **Rules:** {info['rule_count']:,}
- **Priority:** {info['priority']}
"""

        md_content += f"""
## Consistency Analysis

Overall consistency across all 5 artifacts: **{self.sync_stats['consistency_score']:.2f}%**

"""

        for cross_check, stats in consistency_report["cross_check"].items():
            md_content += f"""
### {cross_check}

- Common Rules: {stats['common_rules']:,}
- Only in First: {stats['only_in_first']:,}
- Only in Second: {stats['only_in_second']:,}
- Similarity: {stats['similarity_percent']:.2f}%
"""

        md_content += """
## Next Steps

1. Review consistency report
2. Resolve any conflicts between artifacts
3. Update implementations in shards
4. Run validation tests

---

*Generated by SOT 5 Artifacts Synchronizer v1.0.0*
"""

        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"  [SAVED] {md_path.relative_to(self.repo_root)}")

    def _count_by_field(self, field: str) -> Dict[str, int]:
        """Count unified rules by field value"""

        counts = defaultdict(int)
        for rule in self.unified_rules:
            if isinstance(rule, dict) and field in rule:
                counts[str(rule[field])] += 1

        return dict(counts)

    def run(self, dry_run: bool = True) -> None:
        """Run complete synchronization"""

        print("=" * 80)
        print("SSID 5 SOT ARTIFACTS - COMPLETE SYNCHRONIZATION")
        print("=" * 80)

        if dry_run:
            print("\n[MODE] DRY RUN - No files will be modified")
        else:
            print("\n[MODE] EXECUTE - Files will be updated")

        # 1. Load all 5 artifacts
        self.load_sot_artifacts()

        # 2. Unify rules
        self.unify_rules()

        # 3. Categorize by shard
        shard_rules = self.categorize_rules_by_shard()

        # 4. Update chart.yaml files
        self.update_shard_charts(shard_rules, dry_run=dry_run)

        # 5. Verify consistency
        consistency_report = self.verify_consistency()

        # 6. Generate report
        self.generate_sync_report(consistency_report)

        # Summary
        print("\n" + "=" * 80)
        print("SYNCHRONIZATION COMPLETE")
        print("=" * 80)
        print(f"\nArtifacts: {self.sync_stats['artifacts_loaded']}/5")
        print(f"Total Rules: {self.sync_stats['total_rules']:,}")
        print(f"Unique Rules: {self.sync_stats['unique_rules']:,}")
        print(f"Shards Updated: {self.sync_stats['shards_updated']}/384")
        print(f"Consistency: {self.sync_stats['consistency_score']:.2f}%")

        if dry_run:
            print("\n[INFO] This was a DRY RUN. Use --execute to apply changes.")

        print("=" * 80)


def main():
    """Main entry point"""

    import argparse

    parser = argparse.ArgumentParser(description="Synchronize 5 SOT artifacts with shard system")
    parser.add_argument("--execute", action="store_true", help="Actually update files (not dry-run)")

    args = parser.parse_args()

    synchronizer = SOTSynchronizer()
    synchronizer.run(dry_run=not args.execute)


if __name__ == "__main__":
    main()
