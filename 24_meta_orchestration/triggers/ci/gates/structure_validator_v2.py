#!/usr/bin/env python3
"""Structure Validator v2.0 - Audit-Ready bis 2045
Compliance: Blueprint v4.1, Exit-Code-Standard, Evidence-Logging, Hash-Ledger
"""
import json, yaml, sys, hashlib
from pathlib import Path
from datetime import datetime

PROJECT = Path(".")
OUT = PROJECT / "24_meta_orchestration/registry/generated/repo_scan.json"

# Compliance Integration
POLICY_FILE = PROJECT / "23_compliance/policies/structure_policy.yaml"
EXCEPTIONS_FILE = PROJECT / "23_compliance/exceptions/structure_exceptions.yaml"

# Evidence Logging
EVIDENCE_DIR = PROJECT / "02_audit_logging/evidence/structure_validator"

# Exit Codes (CI-Gate-Standard)
EXIT_SUCCESS = 0
EXIT_SHARD_INVALID = 1
EXIT_FORBIDDEN_FILES = 8
EXIT_POLICY_VIOLATION = 16
EXIT_ROOT_VIOLATION = 24

ROOTS = ["01_ai_layer", "02_audit_logging", "03_core", "04_deployment",
         "05_documentation", "06_data_pipeline", "07_governance_legal", "08_identity_score",
         "09_meta_identity", "10_interoperability", "11_test_simulation", "12_tooling",
         "13_ui_layer", "14_zero_time_auth", "15_infra", "16_codex",
         "17_observability", "18_data_layer", "19_adapters", "20_foundation",
         "21_post_quantum_crypto", "22_datasets", "23_compliance", "24_meta_orchestration"]

FORBIDDEN_EXTENSIONS = [".ipynb", ".parquet", ".sqlite", ".db"]

def load_policy():
    """Load structure policy (optional)"""
    if POLICY_FILE.exists():
        with open(POLICY_FILE) as f:
            return yaml.safe_load(f)
    return {"max_depth": 3, "require_chart": True}

def load_exceptions():
    """Load structure exceptions (optional)"""
    if EXCEPTIONS_FILE.exists():
        with open(EXCEPTIONS_FILE) as f:
            data = yaml.safe_load(f)
            return data.get("allowed_forbidden_files", [])
    return []

def check_forbidden_files(exceptions):
    """Check for forbidden file types with exception handling"""
    violations = []
    for root in PROJECT.rglob("*"):
        if root.is_file() and root.suffix in FORBIDDEN_EXTENSIONS:
            rel_path = str(root.relative_to(PROJECT))
            if rel_path not in exceptions:
                violations.append(rel_path)
    return violations

def check_root_structure():
    """Verify all 24 roots exist"""
    missing_roots = []
    for r in ROOTS:
        rp = PROJECT / r
        if not rp.exists():
            missing_roots.append(r)
    return missing_roots

def compute_sha256(data):
    """Compute SHA-256 hash for audit trail"""
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def save_evidence(result, exit_code):
    """Save evidence to audit log with hash-ledger entry"""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    evidence_path = EVIDENCE_DIR / today
    evidence_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    evidence_file = evidence_path / f"scan_{timestamp}.json"
    
    # Add hash and audit metadata
    evidence = {
        "scan_result": result,
        "exit_code": exit_code,
        "audit_metadata": {
            "validator_version": "2.0",
            "blueprint_version": "4.1",
            "timestamp": result["scan_timestamp"],
            "result_hash_sha256": compute_sha256(result)
        }
    }
    
    # Sign with additional hash (hash-ledger entry)
    evidence["audit_metadata"]["evidence_hash_sha256"] = compute_sha256(evidence)
    
    evidence_file.write_text(json.dumps(evidence, indent=2))
    return evidence_file, evidence["audit_metadata"]["evidence_hash_sha256"]

def scan():
    """Main scanning function with full compliance"""
    policy = load_policy()
    exceptions = load_exceptions()
    
    result = {
        "scan_timestamp": datetime.utcnow().isoformat() + "Z",
        "policy_ref": str(POLICY_FILE.relative_to(PROJECT)) if POLICY_FILE.exists() else None,
        "exceptions_ref": str(EXCEPTIONS_FILE.relative_to(PROJECT)) if EXCEPTIONS_FILE.exists() else None,
        "roots": [],
        "summary": {
            "scanned_roots": 0, 
            "total_shards": 0, 
            "valid_shards": 0, 
            "invalid_shards": 0,
            "missing_roots": 0
        },
        "violations": {
            "forbidden_files": [],
            "missing_roots": [],
            "policy_violations": []
        }
    }
    
    # Check root structure
    missing_roots = check_root_structure()
    result["violations"]["missing_roots"] = missing_roots
    result["summary"]["missing_roots"] = len(missing_roots)
    
    # Check forbidden files
    forbidden = check_forbidden_files(exceptions)
    result["violations"]["forbidden_files"] = forbidden
    
    # Scan shards
    for r in ROOTS:
        rp = PROJECT / r / "shards"
        if not rp.exists(): 
            continue
        root_data = {"root_id": r, "shards": []}
        for sp in sorted(rp.iterdir()):
            if sp.is_dir() and sp.name.startswith(("Shard_", "shard_")):
                chart_exists = (sp / "chart.yaml").exists()
                valid = chart_exists if policy.get("require_chart", True) else True
                
                shard_info = {
                    "shard_id": sp.name,
                    "valid": valid,
                    "path": str(sp.relative_to(PROJECT))
                }
                
                if not valid:
                    result["violations"]["policy_violations"].append({
                        "shard": sp.name,
                        "reason": "missing_chart_yaml"
                    })
                
                root_data["shards"].append(shard_info)
                result["summary"]["total_shards"] += 1
                if valid:
                    result["summary"]["valid_shards"] += 1
                else:
                    result["summary"]["invalid_shards"] += 1
        
        result["roots"].append(root_data)
        result["summary"]["scanned_roots"] += 1
    
    # Save main result
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2))
    
    # Determine exit code (priority-based)
    exit_code = EXIT_SUCCESS
    if result["violations"]["missing_roots"]:
        exit_code = EXIT_ROOT_VIOLATION
    elif result["violations"]["forbidden_files"]:
        exit_code = EXIT_FORBIDDEN_FILES
    elif result["violations"]["policy_violations"]:
        exit_code = EXIT_POLICY_VIOLATION
    elif result["summary"]["invalid_shards"] > 0:
        exit_code = EXIT_SHARD_INVALID
    
    # Save evidence (audit trail)
    evidence_file, evidence_hash = save_evidence(result, exit_code)
    
    # Console output
    print(f"✅ Scan completed: {OUT}")
    print(f"📊 Statistics:")
    print(f"   Roots: {result['summary']['scanned_roots']}/{len(ROOTS)}")
    print(f"   Shards: {result['summary']['total_shards']} (valid: {result['summary']['valid_shards']}, invalid: {result['summary']['invalid_shards']})")
    print(f"🔒 Evidence: {evidence_file}")
    print(f"🔐 Hash (SHA-256): {evidence_hash}")
    
    if result["violations"]["missing_roots"]:
        print(f"\n❌ Missing Roots: {len(result['violations']['missing_roots'])}")
        for r in result["violations"]["missing_roots"][:5]:
            print(f"   - {r}")
        print(f"EXIT CODE: {exit_code} (ROOT_VIOLATION)")
    
    if result["violations"]["forbidden_files"]:
        print(f"\n⚠️  Forbidden files: {len(result['violations']['forbidden_files'])}")
        for f in result["violations"]["forbidden_files"][:10]:
            print(f"   - {f}")
        if exit_code == EXIT_FORBIDDEN_FILES:
            print(f"EXIT CODE: {exit_code} (FORBIDDEN_FILES)")
    
    if result["violations"]["policy_violations"]:
        print(f"\n⚠️  Policy violations: {len(result['violations']['policy_violations'])}")
        for v in result["violations"]["policy_violations"][:5]:
            print(f"   - {v['shard']}: {v['reason']}")
        if exit_code == EXIT_POLICY_VIOLATION:
            print(f"EXIT CODE: {exit_code} (POLICY_VIOLATION)")
    
    if exit_code == EXIT_SUCCESS:
        print("\n✅ All checks passed")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(scan())