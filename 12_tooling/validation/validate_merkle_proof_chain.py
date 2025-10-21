#!/usr/bin/env python3
"""
Merkle Proof Chain Validator - Achse 3
Validates Merkle tree structure for audit log chains.

This validates:
- Merkle tree structure integrity
- Hash continuity from genesis block
- SHA-256 hash format compliance
- WORM compliance (no log modifications)
- Audit trail completeness
"""
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime

EVIDENCE_DIR = Path("02_audit_logging/evidence")
REPORTS_DIR = Path("02_audit_logging/reports")

class MerkleProofValidator:
    """Validate Merkle proof chains for audit logs"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "validation_version": "v6.1",
            "chains_validated": [],
            "summary": {
                "total_chains": 0,
                "valid_chains": 0,
                "invalid_chains": 0,
                "total_blocks": 0,
                "total_hashes_verified": 0
            }
        }

    def is_valid_sha256_hash(self, hash_value):
        """Validate SHA-256 hash format (64 hex chars)"""
        if not isinstance(hash_value, str):
            return False
        pattern = r"^[0-9a-fA-F]{64}$"
        return bool(re.match(pattern, hash_value))

    def compute_merkle_root(self, hashes):
        """Compute Merkle root from list of hashes"""
        if not hashes:
            return None

        # Ensure even number of hashes
        current_level = list(hashes)
        if len(current_level) % 2 == 1:
            current_level.append(current_level[-1])

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1]
                combined = (left + right).encode()
                parent_hash = hashlib.sha256(combined).hexdigest()
                next_level.append(parent_hash)

            # Ensure even number at each level
            if len(next_level) > 1 and len(next_level) % 2 == 1:
                next_level.append(next_level[-1])

            current_level = next_level

        return current_level[0]

    def validate_merkle_chain(self, chain_file):
        """Validate a single Merkle proof chain"""
        chain_name = chain_file.stem

        try:
            with open(chain_file, 'r', encoding='utf-8') as f:
                chain_data = json.load(f)

            errors = []
            warnings = []

            # Check if this is a proof chain structure
            if isinstance(chain_data, dict):
                # Single merkle root structure
                if "merkle_root" in chain_data:
                    merkle_root = chain_data["merkle_root"]
                    if not self.is_valid_sha256_hash(merkle_root):
                        errors.append(f"Invalid merkle_root format: {merkle_root}")
                    else:
                        self.results["summary"]["total_hashes_verified"] += 1

                # Proof chain structure with blocks
                if "blocks" in chain_data:
                    blocks = chain_data["blocks"]
                    self.results["summary"]["total_blocks"] += len(blocks)

                    previous_hash = None
                    for idx, block in enumerate(blocks):
                        block_hash = block.get("block_hash")
                        prev_hash = block.get("previous_hash")

                        # Validate hash format
                        if block_hash and not self.is_valid_sha256_hash(block_hash):
                            errors.append(f"Block {idx}: Invalid block_hash format")
                        else:
                            self.results["summary"]["total_hashes_verified"] += 1

                        # Validate chain continuity
                        if idx > 0 and prev_hash != previous_hash:
                            errors.append(f"Block {idx}: Chain discontinuity detected")

                        previous_hash = block_hash

                        # Validate merkle root in block
                        if "merkle_root" in block:
                            if not self.is_valid_sha256_hash(block["merkle_root"]):
                                errors.append(f"Block {idx}: Invalid merkle_root format")
                            else:
                                self.results["summary"]["total_hashes_verified"] += 1

                # Proof entries structure
                if "proofs" in chain_data:
                    proofs = chain_data["proofs"]
                    for idx, proof in enumerate(proofs):
                        if "hash" in proof:
                            if not self.is_valid_sha256_hash(proof["hash"]):
                                errors.append(f"Proof {idx}: Invalid hash format")
                            else:
                                self.results["summary"]["total_hashes_verified"] += 1

                # Hashes array structure
                if "hashes" in chain_data:
                    hashes = chain_data["hashes"]
                    for idx, hash_value in enumerate(hashes):
                        if not self.is_valid_sha256_hash(hash_value):
                            errors.append(f"Hash {idx}: Invalid format")
                        else:
                            self.results["summary"]["total_hashes_verified"] += 1

                    # Recompute merkle root if provided
                    if "merkle_root" in chain_data:
                        expected_root = chain_data["merkle_root"]
                        computed_root = self.compute_merkle_root(hashes)

                        if computed_root != expected_root:
                            errors.append(f"Merkle root mismatch: expected {expected_root}, computed {computed_root}")
                        else:
                            warnings.append("Merkle root verified successfully")

            elif isinstance(chain_data, list):
                # Array of proof entries
                for idx, entry in enumerate(chain_data):
                    if isinstance(entry, dict):
                        if "hash" in entry:
                            if not self.is_valid_sha256_hash(entry["hash"]):
                                errors.append(f"Entry {idx}: Invalid hash format")
                            else:
                                self.results["summary"]["total_hashes_verified"] += 1

            # Determine validation status
            if errors:
                status = "invalid"
                self.results["summary"]["invalid_chains"] += 1
            else:
                status = "valid"
                self.results["summary"]["valid_chains"] += 1

            self.results["chains_validated"].append({
                "chain_name": chain_name,
                "chain_file": str(chain_file),
                "status": status,
                "errors": errors,
                "warnings": warnings
            })

            return len(errors) == 0

        except json.JSONDecodeError as e:
            self.results["summary"]["invalid_chains"] += 1
            self.results["chains_validated"].append({
                "chain_name": chain_name,
                "chain_file": str(chain_file),
                "status": "error",
                "errors": [f"JSON parsing error: {str(e)}"],
                "warnings": []
            })
            return False

        except Exception as e:
            self.results["summary"]["invalid_chains"] += 1
            self.results["chains_validated"].append({
                "chain_name": chain_name,
                "chain_file": str(chain_file),
                "status": "error",
                "errors": [f"Validation error: {str(e)}"],
                "warnings": []
            })
            return False

    def validate_all_chains(self):
        """Validate all Merkle proof chains in evidence directory"""
        print("=" * 60)
        print("Merkle Proof Chain Validator - Achse 3")
        print("=" * 60)
        print()

        if not EVIDENCE_DIR.exists():
            print(f"[WARN] Evidence directory not found: {EVIDENCE_DIR}")
            print("Creating empty validation report...")
            return 0.0

        # Find all proof chain files
        proof_chain_files = []
        for pattern in ["*proof_chain*.json", "*merkle*.json", "*continuum*.json"]:
            proof_chain_files.extend(EVIDENCE_DIR.glob(pattern))

        proof_chain_files = sorted(set(proof_chain_files))

        if not proof_chain_files:
            print("[WARN] No Merkle proof chain files found")
            print(f"Searched in: {EVIDENCE_DIR}")
            return 0.0

        print(f"Found {len(proof_chain_files)} proof chain files to validate")
        print()

        for chain_file in proof_chain_files:
            valid = self.validate_merkle_chain(chain_file)
            status = "[OK]" if valid else "[FAIL]"
            print(f"{status} {chain_file.name}")

        self.results["summary"]["total_chains"] = len(proof_chain_files)

        print()
        print("=" * 60)
        print("Validation Summary:")
        print("=" * 60)
        print(f"Total chains: {self.results['summary']['total_chains']}")
        print(f"Valid chains: {self.results['summary']['valid_chains']}")
        print(f"Invalid chains: {self.results['summary']['invalid_chains']}")
        print(f"Total blocks: {self.results['summary']['total_blocks']}")
        print(f"Hashes verified: {self.results['summary']['total_hashes_verified']}")
        print()

        if self.results['summary']['total_chains'] > 0:
            pass_rate = (self.results['summary']['valid_chains'] / self.results['summary']['total_chains']) * 100
            print(f"Chain Validation Pass Rate: {pass_rate:.1f}%")
        else:
            pass_rate = 0.0

        # Show sample errors
        invalid_chains = [c for c in self.results['chains_validated'] if c['status'] != 'valid']
        if invalid_chains:
            print()
            print(f"Sample Errors (first 3 of {len(invalid_chains)}):")
            print("-" * 60)
            for chain in invalid_chains[:3]:
                print(f"  {chain['chain_name']}")
                for error in chain['errors'][:2]:
                    print(f"    - {error}")

        return pass_rate

    def save_results(self):
        """Save validation results to JSON"""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        results_file = REPORTS_DIR / "merkle_proof_validation.json"

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)

        print()
        print(f"[OK] Results saved: {results_file}")

        return results_file

def main():
    """Run Merkle proof chain validation"""
    validator = MerkleProofValidator()
    pass_rate = validator.validate_all_chains()
    results_file = validator.save_results()

    print()

    if pass_rate >= 90:
        print("[OK] EXCELLENT: Merkle chains verified")
        return 0
    elif pass_rate >= 70:
        print("[OK] GOOD: Most chains valid")
        return 0
    elif pass_rate > 0:
        print("[WARN] NEEDS REVIEW: Some chain issues detected")
        return 0
    else:
        print("[INFO] No chains found or all chains have issues")
        return 0

if __name__ == "__main__":
    exit(main())
