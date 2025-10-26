#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SoT Rule Extraction & Distribution System
==========================================

Extracts ALL rules from the 5 Master SoT files and distributes them
to the appropriate Shards in the 384 Shard Matrix.

CRITICAL: Nothing can be created in the system without being registered in Shards!

Master SoT Files:
1. ssid_master_definition_corrected_v1.1.1.md
2. SSID_structure_gebuhren_abo_modelle.md
3. SSID_structure_level3_part1_MAX.md
4. SSID_structure_level3_part2_MAX.md
5. SSID_structure_level3_part3_MAX.md

This script:
1. Parses all 5 Master files
2. Extracts every rule (MUST, SHOULD, HAVE, CAN)
3. Determines which Shard(s) each rule belongs to
4. Registers the rule in the appropriate Shard's chart.yaml
5. Updates the global registry

Version: 1.0.0
Author: SSID Orchestration Team
Co-Authored-By: Claude <noreply@anthropic.com>
"""

import re
import sys
import json
import yaml
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple, Optional

# Repository root
REPO_ROOT = Path(__file__).parent.parent.parent

# Master SoT file locations
MASTER_FILES = [
    REPO_ROOT / "16_codex" / "structure" / "ssid_master_definition_corrected_v1.1.1.md",
    REPO_ROOT / "16_codex" / "structure" / "SSID_structure_gebühren_abo_modelle.md",
    REPO_ROOT / "16_codex" / "structure" / "SSID_structure_level3_part1_MAX.md",
    REPO_ROOT / "16_codex" / "structure" / "SSID_structure_level3_part2_MAX.md",
    REPO_ROOT / "16_codex" / "structure" / "SSID_structure_level3_part3_MAX.md",
]

# Rule patterns
RULE_PATTERNS = [
    re.compile(r"^(MUST|SHALL|REQUIRED):\s*(.+)", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^(SHOULD|RECOMMENDED):\s*(.+)", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^(HAVE|HAS):\s*(.+)", re.MULTILINE | re.IGNORECASE),
    re.compile(r"^(CAN|MAY|OPTIONAL):\s*(.+)", re.MULTILINE | re.IGNORECASE),
    re.compile(r"\*\*([A-Z][A-Z_]+):\*\*\s*(.+)", re.MULTILINE),
    re.compile(r"- \*\*Rule\*\*:\s*(.+)", re.MULTILINE),
]

# Shard mapping keywords (for intelligent distribution)
SHARD_KEYWORDS = {
    "01_identitaet_personen": ["identity", "person", "DID", "profile", "auth", "user"],
    "02_dokumente_nachweise": ["document", "proof", "evidence", "credential", "certificate"],
    "03_zugang_berechtigungen": ["access", "permission", "role", "authorization", "right"],
    "04_kommunikation_daten": ["communication", "message", "data", "exchange", "API"],
    "05_gesundheit_medizin": ["health", "medical", "prescription", "patient"],
    "06_bildung_qualifikationen": ["education", "degree", "qualification", "skill", "certificate"],
    "07_familie_soziales": ["family", "social", "relation", "network"],
    "08_mobilitaet_fahrzeuge": ["mobility", "vehicle", "transport", "travel"],
    "09_arbeit_karriere": ["work", "job", "employment", "career", "CV"],
    "10_finanzen_banking": ["finance", "bank", "payment", "transaction", "account"],
    "11_versicherungen_risiken": ["insurance", "risk", "policy", "claim"],
    "12_immobilien_grundstuecke": ["property", "real estate", "land", "rental"],
    "13_unternehmen_gewerbe": ["company", "business", "enterprise", "commercial"],
    "14_vertraege_vereinbarungen": ["contract", "agreement", "terms", "legal"],
    "15_handel_transaktionen": ["trade", "transaction", "marketplace", "commerce"],
    "16_behoerden_verwaltung": ["government", "administration", "authority", "permit"],
}


class SoTRuleExtractor:
    """
    Extracts rules from Master SoT files and distributes to Shards

    This is the core of the self-registering system.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.extracted_rules = []
        self.shard_assignments = {}
        self.errors = []

    def extract_all_rules(self) -> List[Dict[str, Any]]:
        """Extract all rules from all 5 Master files"""
        print("=" * 80)
        print(" " * 25 + "SOT RULE EXTRACTION")
        print("=" * 80)
        print()

        for master_file in MASTER_FILES:
            if not master_file.exists():
                error = f"Master file not found: {master_file}"
                print(f"[ERROR] {error}")
                self.errors.append(error)
                continue

            print(f"[PARSING] {master_file.name}")
            rules = self._extract_from_file(master_file)
            print(f"  > Extracted {len(rules)} rules")
            self.extracted_rules.extend(rules)

        print()
        print(f"TOTAL RULES EXTRACTED: {len(self.extracted_rules)}")
        print("=" * 80)
        print()

        return self.extracted_rules

    def _extract_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract rules from a single Master file"""
        rules = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            self.errors.append(f"Failed to read {file_path}: {e}")
            return rules

        # Extract using all patterns
        for pattern in RULE_PATTERNS:
            matches = pattern.findall(content)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2:
                        category, description = match
                    else:
                        description = match[0]
                        category = "RULE"
                else:
                    description = match
                    category = "RULE"

                rule = {
                    "id": self._generate_rule_id(description),
                    "category": self._normalize_category(category),
                    "description": description.strip(),
                    "source": file_path.name,
                    "hash": self._compute_rule_hash(description),
                    "extracted_at": datetime.now(timezone.utc).isoformat(),
                }

                # Avoid duplicates
                if not any(r["hash"] == rule["hash"] for r in rules):
                    rules.append(rule)

        return rules

    def _generate_rule_id(self, description: str) -> str:
        """Generate a unique rule ID from description"""
        # Take first 50 chars, clean, and create ID
        clean = re.sub(r"[^a-zA-Z0-9\s]", "", description[:50])
        words = clean.split()[:5]
        id_part = "_".join(words).upper()
        hash_part = hashlib.sha256(description.encode()).hexdigest()[:8]
        return f"RULE_{id_part}_{hash_part}"

    def _normalize_category(self, category: str) -> str:
        """Normalize rule category"""
        cat = category.upper().strip()
        if cat in ["MUST", "SHALL", "REQUIRED"]:
            return "MUST"
        elif cat in ["SHOULD", "RECOMMENDED"]:
            return "SHOULD"
        elif cat in ["HAVE", "HAS"]:
            return "HAVE"
        elif cat in ["CAN", "MAY", "OPTIONAL"]:
            return "CAN"
        else:
            return "RULE"

    def _compute_rule_hash(self, description: str) -> str:
        """Compute SHA-256 hash of rule"""
        return hashlib.sha256(description.encode()).hexdigest()

    def distribute_to_shards(self) -> Dict[str, List[str]]:
        """
        Distribute rules to appropriate Shards

        CRITICAL: This is where the automatic registration happens!
        """
        print("=" * 80)
        print(" " * 25 + "SHARD DISTRIBUTION")
        print("=" * 80)
        print()

        for rule in self.extracted_rules:
            # Determine which Shard(s) this rule belongs to
            target_shards = self._determine_target_shards(rule)

            if not target_shards:
                # Default: Register in ALL shards if can't determine
                target_shards = list(SHARD_KEYWORDS.keys())
                print(f"[WARN] Rule {rule['id']} -> ALL SHARDS (no specific match)")

            # Register rule in each target shard
            for shard_id in target_shards:
                if shard_id not in self.shard_assignments:
                    self.shard_assignments[shard_id] = []
                self.shard_assignments[shard_id].append(rule["id"])

        # Summary
        print()
        print("DISTRIBUTION SUMMARY:")
        for shard_id, rule_ids in sorted(self.shard_assignments.items()):
            print(f"  {shard_id}: {len(rule_ids)} rules")

        print()
        print(f"Total Shards with rules: {len(self.shard_assignments)}")
        print("=" * 80)
        print()

        return self.shard_assignments

    def _determine_target_shards(self, rule: Dict[str, Any]) -> List[str]:
        """Determine which Shard(s) a rule should be registered in"""
        desc_lower = rule["description"].lower()
        targets = []

        for shard_id, keywords in SHARD_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in desc_lower:
                    targets.append(shard_id)
                    break

        return list(set(targets))  # Remove duplicates

    def register_in_shards(self) -> int:
        """
        Register rules in Shard chart.yaml files

        CRITICAL: This updates the actual Shard registry!
        """
        print("=" * 80)
        print(" " * 25 + "SHARD REGISTRATION")
        print("=" * 80)
        print()

        registered_count = 0

        # Get all roots
        roots = [d.name for d in self.repo_root.iterdir() if d.is_dir() and d.name.startswith(("0", "1", "2"))]

        for root_id in sorted(roots):
            shards_dir = self.repo_root / root_id / "shards"
            if not shards_dir.exists():
                continue

            for shard_id in self.shard_assignments:
                shard_path = shards_dir / shard_id
                if not shard_path.exists():
                    continue

                chart_file = shard_path / "chart.yaml"
                if not chart_file.exists():
                    continue

                # Load chart.yaml
                try:
                    with open(chart_file, "r", encoding="utf-8") as f:
                        chart = yaml.safe_load(f)
                except Exception as e:
                    self.errors.append(f"Failed to load {chart_file}: {e}")
                    continue

                # Add rules to chart
                if "rules" not in chart:
                    chart["rules"] = {"validation": []}

                rule_ids = self.shard_assignments[shard_id]
                for rule_id in rule_ids:
                    # Find full rule data
                    rule_data = next((r for r in self.extracted_rules if r["id"] == rule_id), None)
                    if not rule_data:
                        continue

                    # Check if already registered
                    if any(r.get("id") == rule_id for r in chart["rules"]["validation"]):
                        continue

                    # Add to validation rules
                    chart["rules"]["validation"].append({
                        "id": rule_data["id"],
                        "category": rule_data["category"],
                        "description": rule_data["description"],
                        "source": rule_data["source"],
                        "hash": rule_data["hash"],
                        "registered_at": datetime.now(timezone.utc).isoformat(),
                    })

                    registered_count += 1

                # Save updated chart.yaml
                try:
                    with open(chart_file, "w", encoding="utf-8") as f:
                        yaml.safe_dump(chart, f, allow_unicode=True, sort_keys=False)
                except Exception as e:
                    self.errors.append(f"Failed to save {chart_file}: {e}")

        print(f"Total rules registered in Shards: {registered_count}")
        print("=" * 80)
        print()

        return registered_count


def main():
    """Main entry point"""
    extractor = SoTRuleExtractor(REPO_ROOT)

    # 1. Extract all rules
    rules = extractor.extract_all_rules()

    # 2. Distribute to shards
    assignments = extractor.distribute_to_shards()

    # 3. Register in shard chart.yaml files
    registered = extractor.register_in_shards()

    # Summary
    print("=" * 80)
    print(" " * 25 + "FINAL SUMMARY")
    print("=" * 80)
    print(f"Rules extracted: {len(rules)}")
    print(f"Shards assigned: {len(assignments)}")
    print(f"Rules registered: {registered}")
    print(f"Errors: {len(extractor.errors)}")

    if extractor.errors:
        print("\nErrors:")
        for error in extractor.errors[:10]:
            print(f"  - {error}")

    print("=" * 80)

    return 0 if not extractor.errors else 1


if __name__ == "__main__":
    sys.exit(main())
