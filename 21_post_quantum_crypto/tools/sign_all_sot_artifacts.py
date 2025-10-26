#!/usr/bin/env python3
"""
Batch PQC Signature Application for SoT Artifacts
Signs all critical SoT artifacts with Dilithium3 (FIPS 204)

Version: 1.0.0
Status: PRODUCTION
"""

import subprocess
import json
import hashlib
from pathlib import Path
from datetime import datetime
import sys

# Define all 5 critical artifacts
ARTIFACTS = [
    {
        'name': 'SoT Registry',
        'path': '16_codex/structure/auto_generated/sot_rules_full.json',
        'cert_name': 'SoT_Registry_v3.2.1',
        'signature_file': '02_audit_logging/reports/signatures/registry_signature.json'
    },
    {
        'name': 'SoT Contract',
        'path': '16_codex/contracts/sot/sot_contract.yaml',
        'cert_name': 'SoT_Contract_v3.2.1',
        'signature_file': '02_audit_logging/reports/signatures/contract_signature.json'
    },
    {
        'name': 'SoT Policy',
        'path': '23_compliance/policies/sot/sot_policy.rego',
        'cert_name': 'SoT_Policy_v3.2.1',
        'signature_file': '02_audit_logging/reports/signatures/policy_signature.json'
    },
    {
        'name': 'SoT Validator',
        'path': '03_core/validators/sot/sot_validator_core.py',
        'cert_name': 'SoT_Validator_v3.2.1',
        'signature_file': '02_audit_logging/reports/signatures/validator_signature.json'
    },
    {
        'name': 'SoT Tests',
        'path': '11_test_simulation/tests_compliance/test_sot_validator.py',
        'cert_name': 'SoT_Tests_v3.2.1',
        'signature_file': '02_audit_logging/reports/signatures/tests_signature.json'
    }
]


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of file"""
    sha256 = hashlib.sha256()

    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"  Error computing hash: {e}")
        return "ERROR"


def sign_artifact(artifact: dict, repo_root: Path) -> dict:
    """Sign a single artifact with PQC"""
    cert_path = repo_root / artifact['path']
    sig_path = repo_root / artifact['signature_file']

    # Check if artifact exists
    if not cert_path.exists():
        print(f"  [!] Artifact not found: {cert_path}")
        return {
            'artifact': artifact['name'],
            'status': 'not_found',
            'error': f"File not found: {artifact['path']}"
        }

    # Compute hash
    file_hash = compute_file_hash(cert_path)

    # Create signature directory
    sig_path.parent.mkdir(parents=True, exist_ok=True)

    # Call sign_certificate.py
    signer_script = repo_root / '21_post_quantum_crypto' / 'tools' / 'sign_certificate.py'

    cmd = [
        sys.executable,
        str(signer_script),
        '--cert', artifact['cert_name'],
        '--name', 'AutoAudit_System',
        '--out-json', str(sig_path)
    ]

    print(f"Signing {artifact['name']}...")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)

        # Read signature
        with open(sig_path, encoding='utf-8') as f:
            signature_data = json.load(f)

        # Add file hash
        signature_data['file_hash'] = file_hash
        signature_data['file_path'] = artifact['path']

        # Write back
        with open(sig_path, 'w', encoding='utf-8') as f:
            json.dump(signature_data, f, indent=2)

        print(f"  [OK] Signed: {sig_path.name}")

        return {
            'artifact': artifact['name'],
            'status': 'signed',
            'signature_file': artifact['signature_file'],
            'algorithm': signature_data.get('algorithm', 'Dilithium3'),
            'timestamp': signature_data.get('timestamp'),
            'file_hash': file_hash
        }
    except subprocess.TimeoutExpired:
        print(f"  [!] Timeout signing artifact")
        return {
            'artifact': artifact['name'],
            'status': 'timeout',
            'error': 'Signing operation timed out'
        }
    except subprocess.CalledProcessError as e:
        print(f"  [!] Failed: {e.stderr if e.stderr else str(e)}")
        return {
            'artifact': artifact['name'],
            'status': 'failed',
            'error': e.stderr if e.stderr else str(e)
        }
    except Exception as e:
        print(f"  [!] Error: {e}")
        return {
            'artifact': artifact['name'],
            'status': 'error',
            'error': str(e)
        }


def main():
    repo_root = Path(__file__).resolve().parents[2]

    print("="*60)
    print("PQC SIGNATURE APPLICATION - SoT Artifacts")
    print("="*60)
    print(f"Repository: {repo_root.name}")
    print(f"Algorithm: Dilithium3 (FIPS 204)")
    print(f"Artifacts: {len(ARTIFACTS)}")
    print("="*60)
    print()

    results = []
    for i, artifact in enumerate(ARTIFACTS, 1):
        print(f"[{i}/{len(ARTIFACTS)}] {artifact['name']}")
        result = sign_artifact(artifact, repo_root)
        results.append(result)
        print()

    # Generate manifest
    successful = sum(1 for r in results if r['status'] == 'signed')

    manifest = {
        'version': '3.2.1',
        'timestamp': datetime.now().isoformat(),
        'algorithm': 'Dilithium3 (FIPS 204)',
        'total_artifacts': len(ARTIFACTS),
        'signed_artifacts': successful,
        'artifacts': results,
        'status': 'complete' if successful == len(ARTIFACTS) else 'partial',
        'completeness_percentage': (successful / len(ARTIFACTS) * 100) if ARTIFACTS else 0
    }

    manifest_file = repo_root / '02_audit_logging' / 'reports' / 'signatures' / 'master_signature_manifest.json'
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    print("="*60)
    print("SIGNATURE SUMMARY")
    print("="*60)
    print(f"Total Artifacts: {len(ARTIFACTS)}")
    print(f"Successfully Signed: {successful}")
    print(f"Failed: {len(ARTIFACTS) - successful}")
    print(f"Completeness: {manifest['completeness_percentage']:.1f}%")
    print()

    for result in results:
        status_icon = "[OK]" if result['status'] == 'signed' else "[!]"
        print(f"{status_icon} {result['artifact']:20s}: {result['status'].upper()}")

    print()
    print(f"[OK] Manifest saved: {manifest_file.name}")

    return 0 if manifest['status'] == 'complete' else 1


if __name__ == '__main__':
    sys.exit(main())
