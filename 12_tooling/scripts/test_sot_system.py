#!/usr/bin/env python3
"""Complete SOT System Test Suite"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).parent.parent.parent

def test_5_sot_artifacts():
    """Test that all 5 SOT artifacts can be loaded"""
    print("\n=== TEST 4: Loading 5 SOT Artifacts ===")

    artifacts = {
        "sot_contract_expanded_TRUE": "16_codex/structure/level3/sot_contract_expanded_TRUE.yaml",
        "sot_contract_COMPLETE": "16_codex/contracts/sot/sot_contract_COMPLETE.yaml",
        "sot_contract": "16_codex/contracts/sot/sot_contract.yaml",
        "sot_contract_part2": "16_codex/contracts/sot/sot_contract_part2.yaml",
        "sot_contract_part3": "16_codex/contracts/sot/sot_contract_part3.yaml"
    }

    loaded = 0
    total_rules = 0

    for name, path in artifacts.items():
        artifact_path = REPO_ROOT / path

        if not artifact_path.exists():
            print(f"  [ERROR] Missing: {name}")
            continue

        try:
            with open(artifact_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            rules = data.get("rules", []) if isinstance(data, dict) else []
            version = data.get("version", "unknown") if isinstance(data, dict) else "unknown"

            print(f"  [OK] {name}: {len(rules)} rules (v{version})")

            loaded += 1
            total_rules += len(rules)

        except Exception as e:
            print(f"  [ERROR] {name}: {e}")

    print(f"\nLoaded: {loaded}/5 artifacts")
    print(f"Total Rules: {total_rules:,}")

    if loaded == 5:
        print("[OK] All 5 SOT artifacts loaded successfully!")
        return True
    else:
        print(f"[ERROR] Only {loaded}/5 artifacts loaded")
        return False


def test_synchronization_consistency():
    """Test synchronization consistency"""
    print("\n=== TEST 5: Synchronization Consistency ===")

    # Load master index
    master_index_path = REPO_ROOT / "24_meta_orchestration" / "registry" / "sot_master_index.json"

    if not master_index_path.exists():
        print("[ERROR] Master index not found!")
        return False

    try:
        with open(master_index_path, 'r', encoding='utf-8') as f:
            master_index = json.load(f)

        print(f"  Master Index Version: {master_index['version']}")
        print(f"  Source Artifacts: {len(master_index['source_artifacts'])}/5")
        print(f"  Total Rules: {master_index['statistics']['total_rules_across_all_artifacts']:,}")

    except Exception as e:
        print(f"[ERROR] Failed to load master index: {e}")
        return False

    # Check a few random shards
    layers = ["01_ai_layer", "03_core", "16_codex", "24_meta_orchestration"]
    shards = ["01_identitaet_personen", "10_finanzen_banking"]

    consistent = 0
    total_checked = 0

    for layer in layers:
        for shard in shards:
            chart_path = REPO_ROOT / layer / "shards" / shard / "chart.yaml"

            if not chart_path.exists():
                continue

            total_checked += 1

            try:
                with open(chart_path, 'r', encoding='utf-8') as f:
                    chart = yaml.safe_load(f)

                if isinstance(chart, dict) and "sot_master_index" in chart:
                    sot_ref = chart["sot_master_index"]

                    if (sot_ref.get("synchronized") == True and
                        sot_ref.get("version") == master_index["version"] and
                        len(sot_ref.get("source_artifacts", [])) == 5):
                        consistent += 1
                    else:
                        print(f"  [WARN] Inconsistent: {layer}/{shard}")

            except Exception as e:
                print(f"  [ERROR] {layer}/{shard}: {e}")

    print(f"\nConsistency Check:")
    print(f"  Shards Checked: {total_checked}")
    print(f"  Consistent: {consistent}/{total_checked}")

    if consistent == total_checked:
        print("[OK] All checked shards are consistent with master index!")
        return True
    else:
        print(f"[WARN] {total_checked - consistent} shards have inconsistencies")
        return False


def test_complete_system():
    """Test complete system validation"""
    print("\n=== TEST 6: Complete System Validation ===")

    checks = {
        "384 Shards Exist": False,
        "Master Index Valid": False,
        "All Charts Have SOT Ref": False,
        "5 Artifacts Load": False,
        "Synchronization OK": False
    }

    # Check 1: Shards exist
    layers = [
        "01_ai_layer", "02_audit_logging", "03_core", "04_deployment",
        "05_documentation", "06_data_pipeline", "07_governance_legal",
        "08_identity_score", "09_meta_identity", "10_interoperability",
        "11_test_simulation", "12_tooling", "13_ui_layer", "14_zero_time_auth",
        "15_infra", "16_codex", "17_observability", "18_data_layer",
        "19_adapters", "20_foundation", "21_post_quantum_crypto", "22_datasets",
        "23_compliance", "24_meta_orchestration"
    ]

    shard_ids = [
        "01_identitaet_personen", "02_dokumente_nachweise", "03_zugang_berechtigungen",
        "04_kommunikation_daten", "05_gesundheit_medizin", "06_bildung_qualifikationen",
        "07_familie_soziales", "08_mobilitaet_fahrzeuge", "09_arbeit_karriere",
        "10_finanzen_banking", "11_versicherungen_risiken", "12_immobilien_grundstuecke",
        "13_unternehmen_gewerbe", "14_vertraege_vereinbarungen", "15_handel_transaktionen",
        "16_behoerden_verwaltung"
    ]

    shard_count = 0
    for layer in layers:
        for shard_id in shard_ids:
            shard_path = REPO_ROOT / layer / "shards" / shard_id
            if shard_path.exists():
                shard_count += 1

    checks["384 Shards Exist"] = (shard_count == 384)
    print(f"  Shards: {shard_count}/384 {'[OK]' if shard_count == 384 else '[FAIL]'}")

    # Check 2: Master index
    master_index_path = REPO_ROOT / "24_meta_orchestration" / "registry" / "sot_master_index.json"
    checks["Master Index Valid"] = master_index_path.exists()
    print(f"  Master Index: {'[OK]' if checks['Master Index Valid'] else '[FAIL]'}")

    # Check 3: Charts have SOT ref
    chart_count = 0
    sot_ref_count = 0

    for layer in layers:
        for shard_id in shard_ids:
            chart_path = REPO_ROOT / layer / "shards" / shard_id / "chart.yaml"

            if not chart_path.exists():
                continue

            chart_count += 1

            try:
                with open(chart_path, 'r', encoding='utf-8') as f:
                    chart = yaml.safe_load(f)

                if isinstance(chart, dict) and "sot_master_index" in chart:
                    sot_ref_count += 1
            except:
                pass

    checks["All Charts Have SOT Ref"] = (chart_count == sot_ref_count)
    print(f"  Chart SOT Refs: {sot_ref_count}/{chart_count} {'[OK]' if checks['All Charts Have SOT Ref'] else '[FAIL]'}")

    # Summary
    print(f"\nValidation Summary:")
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)

    for check, result in checks.items():
        status = "[OK]" if result else "[FAIL]"
        print(f"  {status} {check}")

    print(f"\nTotal: {passed}/{total} checks passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n[OK] Complete system validation PASSED!")
        return True
    else:
        print(f"\n[WARN] {total - passed} checks failed")
        return False


def generate_test_report(results):
    """Generate test report"""
    print("\n=== Generating Test Report ===")

    report = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "test_results": results,
        "summary": {
            "total_tests": len(results),
            "passed": sum(1 for r in results.values() if r),
            "failed": sum(1 for r in results.values() if not r),
            "success_rate": f"{sum(1 for r in results.values() if r) / len(results) * 100:.1f}%"
        }
    }

    report_path = REPO_ROOT / "02_audit_logging" / "reports" / "sot_system_test_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"  [SAVED] {report_path.relative_to(REPO_ROOT)}")

    # Markdown report
    md_path = REPO_ROOT / "02_audit_logging" / "reports" / "SOT_SYSTEM_TEST_REPORT.md"

    md_content = f"""# SSID SOT System - Test Report

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Version:** 1.0.0

## Test Results

| Test | Result |
|------|--------|
"""

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        md_content += f"| {test_name} | {status} |\n"

    md_content += f"""
## Summary

- **Total Tests:** {report['summary']['total_tests']}
- **Passed:** {report['summary']['passed']}
- **Failed:** {report['summary']['failed']}
- **Success Rate:** {report['summary']['success_rate']}

"""

    if report['summary']['failed'] == 0:
        md_content += "## Conclusion\n\n✅ **ALL TESTS PASSED!** System is 100% functional.\n"
    else:
        md_content += f"## Conclusion\n\n⚠️ **{report['summary']['failed']} test(s) failed.** Review and fix issues.\n"

    md_content += """
---

*Generated by SOT System Test Suite v1.0.0*
"""

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"  [SAVED] {md_path.relative_to(REPO_ROOT)}")

    return report


def main():
    """Run all tests"""

    print("=" * 80)
    print("SSID SOT SYSTEM - COMPLETE TEST SUITE")
    print("=" * 80)

    results = {}

    # Run tests
    results["5 SOT Artifacts Load"] = test_5_sot_artifacts()
    results["Synchronization Consistency"] = test_synchronization_consistency()
    results["Complete System Validation"] = test_complete_system()

    # Generate report
    report = generate_test_report(results)

    # Final summary
    print("\n" + "=" * 80)
    print("TEST SUITE COMPLETE")
    print("=" * 80)
    print(f"\nTotal Tests: {report['summary']['total_tests']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Success Rate: {report['summary']['success_rate']}")

    if report['summary']['failed'] == 0:
        print("\n✅ ALL TESTS PASSED!")
        print("=" * 80)
        return 0
    else:
        print(f"\n⚠️ {report['summary']['failed']} TEST(S) FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
