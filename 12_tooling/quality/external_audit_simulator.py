#!/usr/bin/env python3
"""
External Audit Simulator
Validates governance snapshot against OPA-style audit policies
Simulates external audit committee verification
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

class ExternalAuditSimulator:
    """Simulates external audit committee verification process"""

    def __init__(self, registry_path: Path):
        self.registry_path = registry_path
        self.registry_data = None
        self.audit_results = {}
        self.violations = []

    def load_registry(self) -> bool:
        """Load governance snapshot registry"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self.registry_data = yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"ERROR: Failed to load registry: {e}")
            return False

    def validate_compliance_score(self) -> Tuple[bool, str]:
        """Validate overall compliance score"""
        cert = self.registry_data.get('certification', {})
        score = cert.get('score')
        level = cert.get('certification_level')
        grade = cert.get('grade')

        if score != 100:
            return False, f"Score is {score}, expected 100"
        if level != "FULL_COMPLIANCE":
            return False, f"Certification level is {level}, expected FULL_COMPLIANCE"
        if grade != "A+":
            return False, f"Grade is {grade}, expected A+"

        return True, "Compliance score: 100/100 FULL_COMPLIANCE A+"

    def validate_architecture_constraints(self) -> Tuple[bool, str]:
        """Validate architecture constraints"""
        constraints = self.registry_data.get('architecture_constraints', {})

        # Root-24-LOCK validation
        root_lock = constraints.get('root_24_lock', {})
        if not root_lock.get('enforced'):
            return False, "Root-24-LOCK not enforced"
        if root_lock.get('module_count') != 24:
            return False, f"Module count is {root_lock.get('module_count')}, expected 24"
        if root_lock.get('violations') != 0:
            return False, f"Root-24-LOCK violations: {root_lock.get('violations')}"

        # SAFE-FIX enforcement
        safe_fix = constraints.get('safe_fix_enforcement', {})
        if not safe_fix.get('no_relative_imports'):
            return False, "Relative imports detected"
        if not safe_fix.get('no_external_paths'):
            return False, "External paths detected"
        if not safe_fix.get('no_temporary_variables'):
            return False, "Temporary variables detected"

        return True, "Architecture constraints met: Root-24-LOCK + SAFE-FIX enforced"

    def validate_anti_gaming_controls(self) -> Tuple[bool, str]:
        """Validate anti-gaming controls"""
        controls = self.registry_data.get('anti_gaming_controls', {})

        required_checks = [
            'circular_dependency_check',
            'overfitting_detection',
            'replay_attack_prevention',
            'time_skew_analysis',
            'anomaly_rate_guard'
        ]

        failed = []
        for check in required_checks:
            if controls.get(check) != "PASSED":
                failed.append(check)

        if failed:
            return False, f"Anti-gaming controls failed: {', '.join(failed)}"

        return True, f"All {len(required_checks)} anti-gaming controls PASSED"

    def validate_forensic_evidence(self) -> Tuple[bool, str]:
        """Validate forensic evidence integrity"""
        evidence = self.registry_data.get('forensic_evidence', {})

        if evidence.get('hash_chain_integrity') != "VERIFIED":
            return False, "Hash chain integrity not verified"
        if not evidence.get('worm_storage_enabled'):
            return False, "WORM storage not enabled"
        if not evidence.get('audit_trail_complete'):
            return False, "Audit trail incomplete"

        return True, "Forensic evidence verified: Hash chains + WORM + Audit trail"

    def validate_performance_benchmarks(self) -> Tuple[bool, str]:
        """Validate performance benchmarks"""
        benchmarks = self.registry_data.get('performance_benchmarks', {})

        if not benchmarks.get('all_components_above_target'):
            return False, "Not all components above performance targets"

        multiplier = benchmarks.get('average_performance_multiplier', 0)
        if multiplier < 2.0:
            return False, f"Performance multiplier {multiplier}x below 2.0x threshold"

        return True, f"Performance benchmarks met: {multiplier}x average improvement"

    def validate_compliance_frameworks(self) -> Tuple[bool, str]:
        """Validate all compliance frameworks"""
        frameworks = self.registry_data.get('compliance_frameworks', [])

        required_frameworks = {'GDPR', 'eIDAS 2.0', 'NIS2', 'ISO 27001', 'SOC 2', 'NIST Cybersecurity Framework'}
        found_frameworks = set()

        for framework in frameworks:
            name = framework.get('framework')
            found_frameworks.add(name)

            if framework.get('status') != "COMPLIANT":
                return False, f"{name} status is {framework.get('status')}, expected COMPLIANT"
            if framework.get('score') != 100:
                return False, f"{name} score is {framework.get('score')}, expected 100"

        missing = required_frameworks - found_frameworks
        if missing:
            return False, f"Missing frameworks: {', '.join(missing)}"

        return True, f"All {len(frameworks)} compliance frameworks: 100/100 COMPLIANT"

    def validate_component_scores(self) -> Tuple[bool, str]:
        """Validate all component scores are 100/100"""
        scores = self.registry_data.get('component_scores', {})

        expected_components = 24
        failing_components = []

        for component, score in scores.items():
            if score != 100:
                failing_components.append(f"{component}={score}")

        if failing_components:
            return False, f"Components below 100: {', '.join(failing_components)}"

        if len(scores) != expected_components:
            return False, f"Expected {expected_components} components, found {len(scores)}"

        return True, f"All {expected_components} components: 100/100"

    def validate_ci_gates(self) -> Tuple[bool, str]:
        """Validate CI/CD gates configuration"""
        gates = self.registry_data.get('ci_cd_gates', {})

        if gates.get('threshold') != 100:
            return False, f"CI threshold is {gates.get('threshold')}, expected 100"
        if gates.get('lock_mode') != "strict":
            return False, f"Lock mode is {gates.get('lock_mode')}, expected strict"
        if gates.get('enforcement') != "blocking":
            return False, f"Enforcement is {gates.get('enforcement')}, expected blocking"

        return True, "CI Score-Lock active: threshold=100, mode=strict, enforcement=blocking"

    def validate_placeholder_status(self) -> Tuple[bool, str]:
        """Validate placeholder elimination status"""
        status = self.registry_data.get('placeholder_status', {})

        if not status.get('weekly_validation'):
            return False, "Weekly validation not enabled"
        if not status.get('ci_enforcement'):
            return False, "CI enforcement not enabled"

        total = status.get('total_identified', 0)
        plan = status.get('elimination_plan', '')

        if not plan:
            return False, "No elimination plan found"

        return True, f"Placeholder elimination: {total} identified, weekly validation + CI enforcement active"

    def run_full_audit(self) -> bool:
        """Run complete external audit simulation"""
        print("=" * 80)
        print("EXTERNAL AUDIT COMMITTEE SIMULATION")
        print("Governance Snapshot Verification")
        print("=" * 80)
        print()

        if not self.load_registry():
            return False

        print(f"Registry: {self.registry_path}")
        print(f"Generated: {self.registry_data.get('metadata', {}).get('created', 'UNKNOWN')}")
        print()

        # Run all validation checks
        checks = [
            ("Compliance Score", self.validate_compliance_score),
            ("Architecture Constraints", self.validate_architecture_constraints),
            ("Anti-Gaming Controls", self.validate_anti_gaming_controls),
            ("Forensic Evidence", self.validate_forensic_evidence),
            ("Performance Benchmarks", self.validate_performance_benchmarks),
            ("Compliance Frameworks", self.validate_compliance_frameworks),
            ("Component Scores", self.validate_component_scores),
            ("CI/CD Gates", self.validate_ci_gates),
            ("Placeholder Status", self.validate_placeholder_status),
        ]

        passed = 0
        failed = 0

        print("AUDIT CHECKS:")
        print("-" * 80)

        for check_name, check_func in checks:
            try:
                result, message = check_func()
                self.audit_results[check_name] = result

                status_icon = "PASS" if result else "FAIL"
                status_color = "" if result else "  "

                print(f"[{status_icon}] {check_name}")
                print(f"      {message}")
                print()

                if result:
                    passed += 1
                else:
                    failed += 1
                    self.violations.append(f"{check_name}: {message}")

            except Exception as e:
                print(f"[ERROR] {check_name}")
                print(f"        Exception: {e}")
                print()
                failed += 1
                self.violations.append(f"{check_name}: Exception - {e}")

        # Final summary
        print("=" * 80)
        print("AUDIT SUMMARY")
        print("=" * 80)
        print(f"Total Checks: {len(checks)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print()

        if failed == 0:
            print("CERTIFICATION STATUS: APPROVED")
            print("Grade: A+ (100/100)")
            print("Compliance Level: FULL_COMPLIANCE")
            print()
            print("The governance snapshot meets all external audit requirements.")
            print("All future builds will be validated against this reference state.")
            return True
        else:
            print("CERTIFICATION STATUS: REJECTED")
            print()
            print("VIOLATIONS DETECTED:")
            for violation in self.violations:
                print(f"  - {violation}")
            print()
            print("Remediation required before certification approval.")
            return False

def main():
    """Main entry point"""
    root = Path(__file__).parent.parent.parent
    registry_path = root / "24_meta_orchestration" / "registry" / "final_score_registry.yaml"

    simulator = ExternalAuditSimulator(registry_path)
    success = simulator.run_full_audit()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
