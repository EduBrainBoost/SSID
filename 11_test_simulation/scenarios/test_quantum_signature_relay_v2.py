"""
Test Suite: Quantum Signature Relay v2
Coverage Target: ≥95%
Status: Dormant Mode Testing (NIST PQC)
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "03_core" / "interfaces"))

from quantum_signature_relay_v2 import (
    QuantumSignatureRelayV2,
    PQCAlgorithm,
    RelayMode,
    QuantumKeyPair,
    QuantumSignature,
    QuantumEncapsulation
)

class TestQuantumSignatureRelayV2:
    """Test Quantum Signature Relay v2"""

    @pytest.fixture
    def qsr2(self):
        """Initialize QSR2 in simulation mode"""
        return QuantumSignatureRelayV2(
            mode=RelayMode.SIMULATION,
            dormant=True
        )

    def test_initialization(self, qsr2):
        """Test: QSR2 initializes correctly"""
        assert qsr2.mode == RelayMode.SIMULATION
        assert qsr2.dormant is True
        assert qsr2.signature_algorithm == PQCAlgorithm.DILITHIUM3
        assert qsr2.kem_algorithm == PQCAlgorithm.KYBER768

    def test_dormant_enforcement(self):
        """Test: Hardware mode blocked in dormant"""
        with pytest.raises(ValueError):
            QuantumSignatureRelayV2(
                mode=RelayMode.HARDWARE,
                dormant=True
            )

    def test_dilithium_keypair_generation(self, qsr2):
        """Test: Dilithium key pair generation"""
        keypair = qsr2.generate_keypair(PQCAlgorithm.DILITHIUM3)

        assert isinstance(keypair, QuantumKeyPair)
        assert keypair.algorithm == PQCAlgorithm.DILITHIUM3
        assert len(keypair.public_key) == 1952  # Dilithium3 public key size
        assert len(keypair.secret_key) == 4000  # Dilithium3 secret key size
        assert keypair.security_level == 3

    def test_dilithium_signature(self, qsr2):
        """Test: Dilithium signature creation"""
        keypair = qsr2.generate_keypair(PQCAlgorithm.DILITHIUM3)
        message = b"SSID Continuum Test Message"

        signature = qsr2.sign_message(message, keypair)

        assert isinstance(signature, QuantumSignature)
        assert signature.algorithm == PQCAlgorithm.DILITHIUM3
        assert len(signature.signature_bytes) == 3293  # Dilithium3 signature size
        assert signature.key_id == keypair.key_id

    def test_dilithium_verification(self, qsr2):
        """Test: Dilithium signature verification"""
        keypair = qsr2.generate_keypair(PQCAlgorithm.DILITHIUM3)
        message = b"SSID Continuum Test Message"
        signature = qsr2.sign_message(message, keypair)

        # Verify signature
        is_valid = qsr2.verify_signature(message, signature, keypair.public_key)
        assert is_valid is True

        # Verify with wrong message
        wrong_message = b"Wrong Message"
        is_invalid = qsr2.verify_signature(wrong_message, signature, keypair.public_key)
        assert is_invalid is False

    def test_kyber_keypair_generation(self, qsr2):
        """Test: Kyber key pair generation"""
        keypair = qsr2.generate_kem_keypair(PQCAlgorithm.KYBER768)

        assert isinstance(keypair, QuantumKeyPair)
        assert keypair.algorithm == PQCAlgorithm.KYBER768
        assert len(keypair.public_key) == 1184  # Kyber768 public key size
        assert len(keypair.secret_key) == 2400  # Kyber768 secret key size
        assert keypair.security_level == 3

    def test_kyber_encapsulation(self, qsr2):
        """Test: Kyber key encapsulation"""
        keypair = qsr2.generate_kem_keypair(PQCAlgorithm.KYBER768)

        encapsulation = qsr2.encapsulate(keypair.public_key, PQCAlgorithm.KYBER768)

        assert isinstance(encapsulation, QuantumEncapsulation)
        assert encapsulation.algorithm == PQCAlgorithm.KYBER768
        assert len(encapsulation.ciphertext) == 1088  # Kyber768 ciphertext size
        assert len(encapsulation.shared_secret) == 32  # Shared secret size

    def test_kyber_decapsulation(self, qsr2):
        """Test: Kyber key decapsulation"""
        keypair = qsr2.generate_kem_keypair(PQCAlgorithm.KYBER768)
        encapsulation = qsr2.encapsulate(keypair.public_key, PQCAlgorithm.KYBER768)

        shared_secret = qsr2.decapsulate(encapsulation.ciphertext, keypair)

        # Shared secrets should match
        assert shared_secret == encapsulation.shared_secret

    def test_all_dilithium_levels(self, qsr2):
        """Test: All Dilithium security levels"""
        algorithms = [
            (PQCAlgorithm.DILITHIUM2, 1312, 2528, 2420, 2),
            (PQCAlgorithm.DILITHIUM3, 1952, 4000, 3293, 3),
            (PQCAlgorithm.DILITHIUM5, 2592, 4864, 4595, 5)
        ]

        for algo, pub_size, sec_size, sig_size, level in algorithms:
            keypair = qsr2.generate_keypair(algo)
            assert len(keypair.public_key) == pub_size
            assert len(keypair.secret_key) == sec_size
            assert keypair.security_level == level

            message = b"Test"
            signature = qsr2.sign_message(message, keypair)
            assert len(signature.signature_bytes) == sig_size

    def test_all_kyber_levels(self, qsr2):
        """Test: All Kyber security levels"""
        algorithms = [
            (PQCAlgorithm.KYBER512, 800, 1632, 768, 1),
            (PQCAlgorithm.KYBER768, 1184, 2400, 1088, 3),
            (PQCAlgorithm.KYBER1024, 1568, 3168, 1568, 5)
        ]

        for algo, pub_size, sec_size, ct_size, level in algorithms:
            keypair = qsr2.generate_kem_keypair(algo)
            assert len(keypair.public_key) == pub_size
            assert len(keypair.secret_key) == sec_size
            assert keypair.security_level == level

            encap = qsr2.encapsulate(keypair.public_key, algo)
            assert len(encap.ciphertext) == ct_size

    def test_deterministic_generation(self, qsr2):
        """Test: Deterministic key generation in simulation"""
        keypair1 = qsr2.generate_keypair(PQCAlgorithm.DILITHIUM3)
        keypair2 = qsr2.generate_keypair(PQCAlgorithm.DILITHIUM3)

        # Should be deterministic in simulation mode
        assert keypair1.public_key == keypair2.public_key

    def test_test_vectors_export(self, qsr2):
        """Test: Export test vectors"""
        test_vectors = qsr2.export_test_vectors()

        assert test_vectors['version'] == "8.0.0"
        assert test_vectors['mode'] == "simulation"
        assert test_vectors['dormant'] is True
        assert len(test_vectors['dilithium_tests']) == 3
        assert len(test_vectors['kyber_tests']) == 3

        # All tests should pass
        for test in test_vectors['dilithium_tests']:
            assert test['verification'] is True

        for test in test_vectors['kyber_tests']:
            assert test['secrets_match'] is True

    def test_status_report(self, qsr2):
        """Test: Status reporting"""
        status = qsr2.get_status()

        assert status['version'] == "8.0.0"
        assert status['mode'] == "simulation"
        assert status['dormant'] is True
        assert status['hardware_available'] is False
        assert status['cost_usd'] == 0.0

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
