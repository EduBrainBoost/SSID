# Post Quantum Crypto

## Zweck
Post-quantum cryptography implementations, PQC key management, and quantum-resistant signatures

## Technische Fähigkeiten
- pqc_key_generation
- quantum_resistant_signatures
- lattice_based_encryption
- hash_based_signatures
- pqc_key_exchange
- hybrid_crypto_schemes

## Governance & Compliance
- **chart.yaml** → Definiert technische Spezifikationen, Abhängigkeiten und Compliance-Anforderungen
- **manifest.yaml** → Implementiert Laufzeitkonfiguration und Deployment-Parameter
- **Policies**: Stub-Status (`ready = false`)
- **Rego-Pfad**: `23_compliance/policies/21_post_quantum_crypto_policy_stub_v6_0.rego`
- **Tests**: `11_test_simulation/tests/test_21_post_quantum_crypto_policy_stub_v6_0.py`

## Abhängigkeiten
**Interne Abhängigkeiten:**
- 09_meta_identity
- 02_audit_logging
- 03_core

**Externe Abhängigkeiten:**
- {'liboqs': '>=0.9'}
- {'pqcrypto': '>=0.18'}

## Regulierung & Frameworks
- EIDAS: regulation_910_2014
- EIDAS: qualified_signatures
- NIST: pqc_standardization_round_3
- ISO: iso_iec_23837

## Fortschrittsstatus
**Compliance Readiness Index:** 70.84 % → 78.89 % (target)
**Epistemic Certainty:** 0.95 → 0.97 (expected)

---

_Diese Datei wurde automatisch im Honest-Compliance-Modus v6.1 generiert._
