#!/usr/bin/env python3
"""
SSID Structure Audit Tool
==========================
Prüft die 24×16 Matrix-Struktur auf Fehler:
- Doppelte Shards
- Falsche Naming Conventions
- Utility-Roots mit Shards (sollten keine haben)
- Fehlende Shards wo sie sein sollten

Usage:
    python structure_audit.py
"""

from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict


# Define which roots SHOULD have shards
# ALL 24 Roots should have 16 Shards each!
# 24 × 16 = 384 Chart files (24×16 Matrix)
ALL_ROOTS = [
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
    "24_meta_orchestration",
]

# Expected 16 shards (correct naming)
EXPECTED_SHARDS = [
    "Shard_01_Identitaet_Personen",
    "Shard_02_Dokumente_Nachweise",
    "Shard_03_Zugang_Berechtigungen",
    "Shard_04_Kommunikation_Daten",
    "Shard_05_Gesundheit_Medizin",
    "Shard_06_Bildung_Qualifikationen",
    "Shard_07_Familie_Soziales",
    "Shard_08_Mobilitaet_Fahrzeuge",
    "Shard_09_Arbeit_Karriere",
    "Shard_10_Finanzen_Banking",
    "Shard_11_Versicherungen_Risiken",
    "Shard_12_Immobilien_Grundstuecke",
    "Shard_13_Unternehmen_Gewerbe",
    "Shard_14_Vertraege_Vereinbarungen",
    "Shard_15_Handel_Transaktionen",
    "Shard_16_Behoerden_Verwaltung",
]

# Known INCORRECT naming patterns
INCORRECT_SHARD_PATTERNS = [
    "01_identitaet_personen",
    "02_dokumente_nachweise",
    "03_zugang_berechtigungen",
    "04_kommunikation_daten",
    "05_gesundheit_medizin",
    "06_bildung_qualifikationen",
    "07_familie_soziales",
    "08_mobilitaet_fahrzeuge",
    "09_arbeit_karriere",
    "10_finanzen_banking",
    "11_versicherungen_risiken",
    "12_immobilien_grundstuecke",
    "13_unternehmen_gewerbe",
    "14_vertraege_vereinbarungen",
    "15_handel_transaktionen",
    "16_behoerden_verwaltung",
]


def audit_root_structure(repo_path: Path):
    """Audit all 24 root folders for structural issues."""

    issues = []
    stats = {
        "total_roots": 0,
        "roots_with_shards": 0,
        "total_shards_found": 0,
        "correct_shards": 0,
        "incorrect_shards": 0,
        "duplicate_shards": 0,
        "expected_total_shards": 24 * 16,  # 24 roots × 16 shards = 384
    }

    root_details = {}

    print()
    print("=" * 80)
    print("SSID STRUCTURE AUDIT")
    print("=" * 80)
    print()

    for root_name in ALL_ROOTS:
        root_path = repo_path / root_name

        if not root_path.exists():
            issues.append({
                "severity": "HIGH",
                "root": root_name,
                "issue": "Root folder does not exist",
                "path": str(root_path)
            })
            continue

        stats["total_roots"] += 1

        # Check for shards directory
        shards_dir = root_path / "shards"

        root_info = {
            "has_shards_dir": shards_dir.exists(),
            "should_have_shards": True,  # ALL 24 roots should have 16 shards
            "shard_count": 0,
            "correct_shards": [],
            "incorrect_shards": [],
            "duplicate_shards": [],
        }

        if shards_dir.exists():
            stats["roots_with_shards"] += 1

            # List all directories in shards/
            shard_dirs = [d for d in shards_dir.iterdir() if d.is_dir()]
            root_info["shard_count"] = len(shard_dirs)
            stats["total_shards_found"] += len(shard_dirs)

            # Categorize shards
            for shard_dir in shard_dirs:
                shard_name = shard_dir.name

                if shard_name in EXPECTED_SHARDS:
                    root_info["correct_shards"].append(shard_name)
                    stats["correct_shards"] += 1
                elif shard_name in INCORRECT_SHARD_PATTERNS:
                    root_info["incorrect_shards"].append(shard_name)
                    stats["incorrect_shards"] += 1
                    issues.append({
                        "severity": "CRITICAL",
                        "root": root_name,
                        "issue": f"Incorrect shard naming: {shard_name}",
                        "path": str(shard_dir),
                        "fix": f"Should be: {EXPECTED_SHARDS[INCORRECT_SHARD_PATTERNS.index(shard_name)]}"
                    })
                else:
                    issues.append({
                        "severity": "MEDIUM",
                        "root": root_name,
                        "issue": f"Unknown shard: {shard_name}",
                        "path": str(shard_dir)
                    })

            # Check for duplicates (both correct and incorrect versions)
            correct_set = set(root_info["correct_shards"])
            incorrect_set = set(root_info["incorrect_shards"])

            if correct_set and incorrect_set:
                # Check if there are matching pairs
                for incorrect in incorrect_set:
                    idx = INCORRECT_SHARD_PATTERNS.index(incorrect)
                    correct_match = EXPECTED_SHARDS[idx]
                    if correct_match in correct_set:
                        root_info["duplicate_shards"].append(f"{incorrect} + {correct_match}")
                        stats["duplicate_shards"] += 1
                        issues.append({
                            "severity": "CRITICAL",
                            "root": root_name,
                            "issue": f"DUPLICATE: {incorrect} AND {correct_match} both exist!",
                            "path": str(shards_dir),
                            "fix": f"DELETE {incorrect}, KEEP {correct_match}"
                        })

        else:
            # No shards directory - ALL roots should have it!
            issues.append({
                "severity": "HIGH",
                "root": root_name,
                "issue": "Root missing shards directory (all 24 roots need 16 shards)",
                "path": str(shards_dir),
                "fix": "CREATE shards/ directory with 16 Shard_XX_XXX folders"
            })

        root_details[root_name] = root_info

    return {
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
        "issues": issues,
        "root_details": root_details
    }


def print_report(audit_result):
    """Print human-readable audit report."""

    print()
    print("=" * 80)
    print("AUDIT STATISTICS")
    print("=" * 80)
    print()

    stats = audit_result["stats"]
    for key, value in stats.items():
        print(f"  {key:40s} {value}")

    print()
    print("=" * 80)
    print(f"ISSUES FOUND: {len(audit_result['issues'])}")
    print("=" * 80)
    print()

    # Group by severity
    by_severity = defaultdict(list)
    for issue in audit_result["issues"]:
        by_severity[issue["severity"]].append(issue)

    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if severity in by_severity:
            print(f"\n[{severity}] {len(by_severity[severity])} issues")
            print("-" * 80)
            for issue in by_severity[severity]:
                print(f"  Root: {issue['root']}")
                print(f"  Issue: {issue['issue']}")
                if 'fix' in issue:
                    print(f"  Fix: {issue['fix']}")
                print()

    print()
    print("=" * 80)
    print("CLEANUP ACTIONS REQUIRED")
    print("=" * 80)
    print()

    # Count actions
    archive_incorrect = len([i for i in audit_result["issues"]
                          if "Incorrect shard naming" in i["issue"]])
    archive_duplicates = len([i for i in audit_result["issues"]
                            if "DUPLICATE" in i["issue"]])

    print(f"1. ARCHIVE {archive_incorrect} incorrect shard directories (lowercase)")
    print(f"2. RESOLVE {archive_duplicates} duplicate shard pairs (archive incorrect, keep correct)")
    print(f"3. Target: 384 correct Shards (24 roots × 16 shards)")
    print()


def generate_cleanup_script(audit_result, output_path: Path):
    """Generate bash script to ARCHIVE incorrect structures (not delete!)."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_dir = f"_ARCHIVE_FALSCHE_STRUKTUR_{timestamp}"

    script_lines = [
        "#!/bin/bash",
        "# SSID Structure Cleanup Script",
        f"# Generated: {datetime.now().isoformat()}",
        "#",
        "# This script will:",
        "#   1. ARCHIVE (not delete!) all incorrect (lowercase) shard directories",
        "#   2. MARK archived content as FALSCH",
        "#   3. KEEP only correct Shard_XX_XXX directories",
        "#   4. Result: 384 Shards (24 roots × 16 shards)",
        "",
        "set -e  # Exit on error",
        "",
        "echo '==================================================================='",
        "echo 'SSID STRUCTURE CLEANUP - ARCHIVING INCORRECT STRUCTURES'",
        "echo '==================================================================='",
        "echo",
        "",
        f"# Create archive directory",
        f"ARCHIVE_DIR=\"{archive_dir}\"",
        f"mkdir -p \"$ARCHIVE_DIR\"",
        f"echo '[CREATED] Archive directory: $ARCHIVE_DIR'",
        f"echo",
        "",
        f"# Create FALSCH marker file",
        f"cat > \"$ARCHIVE_DIR/README_FALSCH.md\" << 'EOF'",
        f"# FALSCHE STRUKTUR - ARCHIVIERT",
        f"",
        f"**Datum:** {datetime.now().isoformat()}",
        f"**Grund:** Strukturfehler in 24×16 Matrix",
        f"",
        f"## Probleme",
        f"1. Falsche Shard-Naming (lowercase statt Shard_XX_XXX)",
        f"2. Duplikate (sowohl correct als auch incorrect vorhanden)",
        f"3. Sollzustand: 384 Shards (24 roots × 16 shards)",
        f"",
        f"## Inhalt",
        f"Alle archivierten Verzeichnisse mit falscher Struktur.",
        f"",
        f"## Status",
        f"[FALSCH] Nicht verwenden!",
        f"EOF",
        f"echo '[CREATED] FALSCH marker: $ARCHIVE_DIR/README_FALSCH.md'",
        f"echo",
        ""
    ]

    archive_count = 0

    for issue in audit_result["issues"]:
        if "Incorrect shard naming" in issue["issue"]:
            # ARCHIVE incorrect shard (don't delete!)
            path = issue["path"].replace("\\", "/")  # Unix paths
            root = issue["root"]
            shard_name = Path(path).name
            archive_path = f"$ARCHIVE_DIR/{root}__shards__{shard_name}"

            script_lines.append(f"echo '[ARCHIVE] {path}'")
            script_lines.append(f"mv \"{path}\" \"{archive_path}\"")
            script_lines.append(f"echo '  -> {archive_path}'")
            archive_count += 1

    script_lines.append("")
    script_lines.append(f"echo")
    script_lines.append(f"echo '[SUCCESS] Archived {archive_count} incorrect directories'")
    script_lines.append(f"echo '[INFO] Archive location: $ARCHIVE_DIR'")
    script_lines.append(f"echo")

    with open(output_path, 'w') as f:
        f.write('\n'.join(script_lines))

    return archive_count


def main():
    repo_path = Path(".")

    # Run audit
    print("[*] Running structure audit...")
    audit_result = audit_root_structure(repo_path)

    # Print report
    print_report(audit_result)

    # Save JSON report
    report_path = Path("02_audit_logging/reports/structure_audit_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w') as f:
        json.dump(audit_result, f, indent=2)

    print(f"[+] JSON report saved: {report_path}")

    # Generate cleanup script
    cleanup_script = Path("02_audit_logging/tools/structure_cleanup.sh")
    delete_count = generate_cleanup_script(audit_result, cleanup_script)

    print(f"[+] Cleanup script saved: {cleanup_script}")
    print(f"[!] Will delete {delete_count} directories")
    print()
    print("[NEXT STEPS]")
    print(f"  1. Review: {report_path}")
    print(f"  2. Review: {cleanup_script}")
    print(f"  3. Execute: bash {cleanup_script}")
    print()

    return 0


if __name__ == "__main__":
    exit(main())
