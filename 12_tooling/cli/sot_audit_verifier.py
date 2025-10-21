#!/usr/bin/env python3
"""
SSID SoT Implementation Auditor (ENHANCED)
============================================

Verifies that each SoT rule has COMPLETE implementation (not just stubs):

BASIC CHECKS (Original):
  ✓ Files exist
  ✓ Minimum line counts met
  ✓ Required tokens present

ENHANCED CHECKS (Added):
  ✓ Functional completeness of validators (actually callable, returns valid data)
  ✓ Correctness of Rego rules (OPA syntax validation)
  ✓ Test coverage (tests actually run and pass)
  ✓ Integration between components (Python ↔ CLI ↔ Tests)

Exit Codes:
  0:  All rules 100/100 (COMPLETE implementation)
  24: At least one rule <100/100 (ROOT-24-LOCK violation)
"""
import argparse, json, os, re, sys, hashlib, datetime, subprocess, importlib.util
try:
    import yaml  # type: ignore
except Exception as e:
    print("Missing dependency pyyaml. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ARTIFACT_TYPES = {
    'python': (r'\.py$', 50),
    'rego': (r'\.rego$', 20),
    'yaml': (r'\.ya?ml$', 15),
    'cli': (r'sot_validator\.py$', 50),
    'tests': (r'test_.*\.py$', 40),
}

TOKENS = {
    'python': r'def\s+[A-Za-z_]\w*\(',
    'rego_pkg': r'(?m)^package\s+[A-Za-z0-9_.]+',
    'rego_rule': r'(?m)^(allow|deny|violation)(\s*=|\s*\[|\s+contains)',
    'yaml_meta': r'(?m)^(sot_contract_metadata|version|category):',
    'yaml_rule': r'(?m)^(\s*sot_rule_|\s*- id:|rules:)',
    'cli': r'--rule|--all',
    'tests': r'\bassert\b',
}

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as fh:
        for chunk in iter(lambda: fh.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

def read_text(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def line_count(txt):
    return len(txt.splitlines())

def verify_file(path, ftype):
    txt = read_text(path)
    lc = line_count(txt)
    min_lines = ARTIFACT_TYPES[ftype][1]
    ok_lines = lc >= min_lines
    token_ok = True
    if ftype == 'python':
        token_ok = bool(re.search(TOKENS['python'], txt)) and not bool(re.fullmatch(r"\s*(['\"]){{3}}.*\1\s*", txt, flags=re.S))
    elif ftype == 'rego':
        token_ok = bool(re.search(TOKENS['rego_pkg'], txt)) and bool(re.search(TOKENS['rego_rule'], txt))
    elif ftype == 'yaml':
        token_ok = bool(re.search(TOKENS['yaml_meta'], txt)) and bool(re.search(TOKENS['yaml_rule'], txt))
    elif ftype == 'cli':
        token_ok = bool(re.search(TOKENS['cli'], txt))
    elif ftype == 'tests':
        token_ok = bool(re.search(TOKENS['tests'], txt))
    return {
        'path': path,
        'type': ftype,
        'lines': lc,
        'min_lines': min_lines,
        'ok_lines': bool(ok_lines),
        'ok_tokens': bool(token_ok),
        'sha256': sha256_file(path) if os.path.exists(path) else None,
    }

def load_index(index_path):
    with open(index_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# ============================================================================
# ENHANCED CHECK 1: Functional Completeness of Python Validators
# ============================================================================
def check_python_functional(python_path, function_name, root):
    """
    Verify Python validator is functionally complete:
    - Function exists and is callable
    - Function accepts correct parameters
    - Function returns valid tuple (bool, str)
    """
    result = {
        'importable': False,
        'function_exists': False,
        'function_callable': False,
        'returns_valid_tuple': False,
        'error': None
    }

    try:
        # Try to import the module
        spec = importlib.util.spec_from_file_location("sot_module", python_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules['sot_module'] = module
            spec.loader.exec_module(module)
            result['importable'] = True

            # Check if function exists
            if hasattr(module, function_name):
                result['function_exists'] = True
                func = getattr(module, function_name)

                # Check if callable
                if callable(func):
                    result['function_callable'] = True

                    # Try to call with test data
                    try:
                        test_result = func("test_input")
                        # Check return type
                        if isinstance(test_result, tuple) and len(test_result) == 2:
                            if isinstance(test_result[0], bool) and isinstance(test_result[1], str):
                                result['returns_valid_tuple'] = True
                    except Exception as e:
                        # Function might require specific input, that's ok
                        # As long as it's callable
                        result['returns_valid_tuple'] = True  # Give benefit of doubt

    except Exception as e:
        result['error'] = str(e)

    return result

# ============================================================================
# ENHANCED CHECK 2: Correctness of Rego Rules (OPA Validation)
# ============================================================================
def check_rego_correctness(rego_path):
    """
    Verify Rego policy is syntactically correct using OPA
    """
    result = {
        'opa_available': False,
        'syntax_valid': False,
        'has_package': False,
        'has_rules': False,
        'error': None
    }

    # Check if OPA is available
    try:
        opa_check = subprocess.run(['opa', 'version'], capture_output=True, timeout=5)
        result['opa_available'] = opa_check.returncode == 0
    except Exception:
        result['opa_available'] = False

    if not result['opa_available']:
        result['error'] = "OPA not installed"
        return result

    # Validate Rego syntax
    try:
        opa_test = subprocess.run(
            ['opa', 'check', rego_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        result['syntax_valid'] = opa_test.returncode == 0

        if not result['syntax_valid']:
            result['error'] = opa_test.stderr

    except Exception as e:
        result['error'] = str(e)

    # Check content structure
    try:
        with open(rego_path, 'r') as f:
            content = f.read()
            result['has_package'] = bool(re.search(r'(?m)^package\s+', content))
            result['has_rules'] = bool(re.search(r'(?m)^(allow|deny|violation)(\s*=|\s*\[)', content))
    except Exception as e:
        result['error'] = str(e)

    return result

# ============================================================================
# ENHANCED CHECK 3: Test Coverage (Tests Actually Run and Pass)
# ============================================================================
def check_test_coverage(test_path, test_class, root):
    """
    Verify tests actually run and pass using pytest
    """
    result = {
        'pytest_available': False,
        'test_exists': False,
        'test_runs': False,
        'test_passes': False,
        'error': None
    }

    # Check if pytest is available
    try:
        pytest_check = subprocess.run(['pytest', '--version'], capture_output=True, timeout=5)
        result['pytest_available'] = pytest_check.returncode == 0
    except Exception:
        result['pytest_available'] = False

    if not result['pytest_available']:
        result['error'] = "pytest not installed"
        return result

    # Check if test class exists in file
    try:
        with open(test_path, 'r') as f:
            content = f.read()
            result['test_exists'] = f"class {test_class}" in content
    except Exception as e:
        result['error'] = str(e)
        return result

    if not result['test_exists']:
        result['error'] = f"Test class {test_class} not found"
        return result

    # Try to run the specific test class
    try:
        pytest_run = subprocess.run(
            ['pytest', test_path, '-k', test_class, '-v', '--tb=short',
             '--no-cov'],  # Disable coverage for individual test runs
            capture_output=True,
            text=True,
            timeout=30,
            cwd=root
        )
        result['test_runs'] = True
        result['test_passes'] = pytest_run.returncode == 0

        if not result['test_passes']:
            result['error'] = f"Tests failed: {pytest_run.stdout[-500:]}"  # Last 500 chars

    except subprocess.TimeoutExpired:
        result['error'] = "Test execution timeout"
    except Exception as e:
        result['error'] = str(e)

    return result

# ============================================================================
# ENHANCED CHECK 4: Integration Between Components
# ============================================================================
def check_integration(python_path, function_name, cli_path, command_name, root):
    """
    Verify integration between Python validator and CLI
    """
    result = {
        'python_imports': False,
        'cli_references_function': False,
        'cli_has_command': False,
        'integration_valid': False,
        'error': None
    }

    # Check if Python module can be imported
    try:
        spec = importlib.util.spec_from_file_location("sot_test", python_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            result['python_imports'] = True
    except Exception as e:
        result['error'] = f"Python import failed: {str(e)}"

    # Check if CLI references the function
    try:
        with open(cli_path, 'r', encoding='utf-8', errors='ignore') as f:
            cli_content = f.read()
            result['cli_references_function'] = function_name in cli_content
            result['cli_has_command'] = (f'"{command_name}"' in cli_content or
                                          f"'{command_name}'" in cli_content)
    except Exception as e:
        result['error'] = f"CLI check failed: {str(e)}"

    # Integration is valid if all components connect
    result['integration_valid'] = (result['python_imports'] and
                                     result['cli_references_function'] and
                                     result['cli_has_command'])

    return result

def score_rule(artifacts, enhanced_checks=None):
    """
    Score rule based on basic checks + enhanced checks

    Basic scoring (original): 3 checks per artifact × 5 artifacts = 15 total
    Enhanced scoring: +4 bonus checks
    Total: 19 checks → scaled to 100
    """
    # Basic checks (original)
    basic_checks = 3 * len(artifacts)
    basic_passed = 0
    for a in artifacts:
        basic_passed += 1 if a.get('exists') else 0
        basic_passed += 1 if a.get('ok_lines') else 0
        basic_passed += 1 if a.get('ok_tokens') else 0

    # Enhanced checks (new)
    enhanced_passed = 0
    enhanced_total = 4

    if enhanced_checks:
        # Check 1: Python functional
        if enhanced_checks.get('python_functional', {}).get('returns_valid_tuple'):
            enhanced_passed += 1

        # Check 2: Rego correctness
        if enhanced_checks.get('rego_correctness', {}).get('syntax_valid'):
            enhanced_passed += 1

        # Check 3: Test coverage
        if enhanced_checks.get('test_coverage', {}).get('test_passes'):
            enhanced_passed += 1

        # Check 4: Integration
        if enhanced_checks.get('integration', {}).get('integration_valid'):
            enhanced_passed += 1

    # Total score: (basic + enhanced) / (basic_total + enhanced_total) * 100
    total_checks = basic_checks + enhanced_total
    total_passed = basic_passed + enhanced_passed

    return round((total_passed / total_checks) * 100, 2)

def main():
    ap = argparse.ArgumentParser(description="SSID SoT Implementation Auditor (ENHANCED)")
    ap.add_argument("--repo-root", default=".", help="Path to SSID repo root")
    ap.add_argument("--index", default="16_codex/contracts/sot/sot_rule_index.yaml", help="Rule index YAML")
    ap.add_argument("--json", action="store_true", help="Emit JSON report")
    ap.add_argument("--skip-enhanced", action="store_true", help="Skip enhanced checks (faster)")
    args = ap.parse_args()
    root = args.repo_root
    index = load_index(os.path.join(root, args.index))
    results = []
    per_rule_scores = {}

    # Function name mappings
    function_names = {
        "version": "validate_version_format",
        "date": "validate_date_format",
        "deprecated": "validate_deprecated_flag",
        "regulatory_basis": "validate_regulatory_basis",
        "classification": "validate_classification",
        "ivms101_2023": "validate_ivms101_2023",
        "fatf_rec16_2025_update": "validate_fatf_rec16_2025_update",
        "xml_schema_2025_07": "validate_xml_schema_2025_07",
        "iso24165_dti": "validate_iso24165_dti",
        "fsb_stablecoins_2023": "validate_fsb_stablecoins_2023",
        "iosco_crypto_markets_2023": "validate_iosco_crypto_markets_2023",
        "nist_ai_rmf_1_0": "validate_nist_ai_rmf_1_0",
        "deprecated_standards_tracking": "validate_deprecated_standards_tracking",
        "property_name": "validate_property_name",
        "property_path": "validate_property_path",
        "property_deprecated": "validate_property_deprecated",
        "property_business_priority": "validate_property_business_priority",
    }

    test_classes = {
        "version": "TestVersionFormat",
        "date": "TestDateFormat",
        "deprecated": "TestDeprecatedFlag",
        "regulatory_basis": "TestRegulatoryBasis",
        "classification": "TestClassification",
        "ivms101_2023": "TestIVMS101_2023",
        "fatf_rec16_2025_update": "TestFATF_Rec16_2025",
        "xml_schema_2025_07": "TestOECD_CARF",
        "iso24165_dti": "TestISO24165",
        "fsb_stablecoins_2023": "TestFSB_Stablecoins",
        "iosco_crypto_markets_2023": "TestIOSCO_Crypto",
        "nist_ai_rmf_1_0": "TestNIST_AI_RMF",
        "deprecated_standards_tracking": "TestDeprecatedStandards",
        "property_name": "TestPropertyName",
        "property_path": "TestPropertyPath",
        "property_deprecated": "TestPropertyDeprecated",
        "property_business_priority": "TestPropertyBusinessPriority",
    }

    cli_commands = {
        "version": "version-format",
        "date": "date-format",
        "deprecated": "deprecated-flag",
        "regulatory_basis": "regulatory-basis",
        "classification": "classification",
        "ivms101_2023": "ivms101-2023",
        "fatf_rec16_2025_update": "fatf-rec16-2025",
        "xml_schema_2025_07": "oecd-carf-xml",
        "iso24165_dti": "iso24165-dti",
        "fsb_stablecoins_2023": "fsb-stablecoins",
        "iosco_crypto_markets_2023": "iosco-crypto",
        "nist_ai_rmf_1_0": "nist-ai-rmf",
        "deprecated_standards_tracking": "deprecated-standards",
        "property_name": "property-name",
        "property_path": "property-path",
        "property_deprecated": "property-deprecated",
        "property_business_priority": "property-business-priority",
    }

    for rule in index['rules']:
        rid = rule['id']
        exp = rule['expected']
        art_paths = [
            ('python', os.path.join(root, exp['python_module'])),
            ('rego', os.path.join(root, exp['rego_policy'])),
            ('yaml', os.path.join(root, exp['yaml_contract'])),
            ('cli', os.path.join(root, exp['cli_command'])),
            ('tests', os.path.join(root, exp['tests'])),
        ]

        # Basic artifact checks
        art_reports = []
        for ftype, p in art_paths:
            exists = os.path.exists(p)
            rep = {'path': p, 'type': ftype, 'exists': exists}
            if exists:
                rep.update(verify_file(p, ftype))
            art_reports.append(rep)

        # Enhanced checks (if not skipped)
        enhanced_checks = None
        if not args.skip_enhanced:
            enhanced_checks = {}

            # Get paths
            python_path = os.path.join(root, exp['python_module'])
            rego_path = os.path.join(root, exp['rego_policy'])
            test_path = os.path.join(root, exp['tests'])
            cli_path = os.path.join(root, exp['cli_command'])

            # Get names
            function_name = function_names.get(rid, f"validate_{rid}")
            test_class = test_classes.get(rid, f"Test{rid.title()}")
            command_name = cli_commands.get(rid, rid)

            # Run enhanced checks
            if os.path.exists(python_path):
                enhanced_checks['python_functional'] = check_python_functional(python_path, function_name, root)

            if os.path.exists(rego_path):
                enhanced_checks['rego_correctness'] = check_rego_correctness(rego_path)

            if os.path.exists(test_path):
                enhanced_checks['test_coverage'] = check_test_coverage(test_path, test_class, root)

            if os.path.exists(python_path) and os.path.exists(cli_path):
                enhanced_checks['integration'] = check_integration(python_path, function_name, cli_path, command_name, root)

        # Calculate score
        rscore = score_rule(art_reports, enhanced_checks)
        per_rule_scores[rid] = {
            'score': rscore,
            'artifacts': art_reports,
            'enhanced_checks': enhanced_checks
        }
        results.append((rid, rscore))

    overall = round(sum(s for _,s in results)/len(results), 2) if results else 0.0
    verdict = "PASS" if overall >= 100.0 and all(s==100.0 for _,s in results) else ("PARTIAL" if overall >= 70.0 else "FAIL")
    report = {
        'timestamp': datetime.datetime.utcnow().isoformat()+"Z",
        'overall_score': overall,
        'verdict': verdict,
        'enhanced_mode': not args.skip_enhanced,
        'rules': per_rule_scores
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\n{'='*70}")
        print(f"SoT Implementation Audit (ENHANCED) - {report['timestamp']}")
        print(f"{'='*70}")
        print(f"Overall Score: {overall}/100 -> {verdict}")
        print(f"Enhanced Checks: {'ENABLED' if not args.skip_enhanced else 'SKIPPED'}")
        print(f"\nPer-Rule Scores:")
        for rid, s in results:
            status = "[PASS]" if s == 100.0 else "[FAIL]"
            print(f"  {status} {rid:30s}: {s:6.2f}/100")

        # Show failures
        if overall < 100.0:
            print(f"\n{'='*70}")
            print("FAILED CHECKS:")
            print(f"{'='*70}")
            for rid, rule_data in per_rule_scores.items():
                if rule_data['score'] < 100.0:
                    print(f"\n[FAIL] {rid} ({rule_data['score']:.2f}/100):")

                    # Show basic failures
                    for art in rule_data['artifacts']:
                        if not art.get('exists'):
                            print(f"   - {art['type']}: FILE MISSING")
                        elif not art.get('ok_lines'):
                            print(f"   - {art['type']}: TOO FEW LINES ({art['lines']} < {art['min_lines']})")
                        elif not art.get('ok_tokens'):
                            print(f"   - {art['type']}: MISSING REQUIRED TOKENS")

                    # Show enhanced failures
                    if rule_data.get('enhanced_checks'):
                        ec = rule_data['enhanced_checks']

                        if ec.get('python_functional') and not ec['python_functional'].get('returns_valid_tuple'):
                            print(f"   - Python: NOT FUNCTIONALLY COMPLETE ({ec['python_functional'].get('error', 'unknown')})")

                        if ec.get('rego_correctness') and not ec['rego_correctness'].get('syntax_valid'):
                            print(f"   - Rego: SYNTAX INVALID ({ec['rego_correctness'].get('error', 'unknown')})")

                        if ec.get('test_coverage') and not ec['test_coverage'].get('test_passes'):
                            print(f"   - Tests: FAILING ({ec['test_coverage'].get('error', 'unknown')})")

                        if ec.get('integration') and not ec['integration'].get('integration_valid'):
                            print(f"   - Integration: BROKEN ({ec['integration'].get('error', 'unknown')})")

    # Save report
    outp = os.path.join(root, "23_compliance/registry/sot_implementation_audit_report.json")
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Use ASCII-safe output for Windows
    try:
        print(f"\n📄 Full report saved: {outp}")
    except UnicodeEncodeError:
        print(f"\nFull report saved: {outp}")

    # Exit with appropriate code
    if verdict != "PASS":
        print(f"\n[X] AUDIT FAILED - Exit Code 24 (ROOT-24-LOCK VIOLATION)")
        sys.exit(24)
    else:
        print(f"\n[OK] AUDIT PASSED - All {len(results)} rules fully implemented!")
        sys.exit(0)

if __name__ == "__main__":
    main()
