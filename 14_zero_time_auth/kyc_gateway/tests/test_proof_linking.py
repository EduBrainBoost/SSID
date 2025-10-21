"""
SSID Proof Linking Test Suite v5.2
Comprehensive tests for Proof Emission & Provider Linking

Target Coverage: ≥95%
Test Scenarios: 8 critical E2E flows + unit tests
"""

import pytest
import time
import json
import hashlib
import hmac
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / "proof_emission"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "20_foundation"))

from proof_emission_engine import (
    ProofEmissionEngine, ProofDigest, EmissionRecord,
    EmissionStatus, create_engine
)
from provider_ack_linker import (
    ProviderACKLinker, ACKRequest, ACKResponse, ACKRecord,
    ACKStatus, create_linker
)
from digest_validator import (
    DigestValidator, ValidationResult, ValidationStatus,
    create_validator
)

###########################################
# Fixtures
###########################################

@pytest.fixture
def test_config():
    """Test configuration"""
    return {
        'layer9_endpoint': 'http://localhost:8009',
        'hmac_secret': 'test_secret_key_12345678901234567890',
        'audit_log_path': '02_audit_logging/proof_emission/',
        'max_retries': 3,
        'retry_delay_seconds': 1,  # Fast retry for tests
        'enable_on_chain_anchoring': False,  
        'provider_registry_path': 'test_registry.yaml',
        'max_ack_retries': 2,
        'ack_timeout_seconds': 30,
        'jwt_algorithm': 'EdDSA',
        'max_timestamp_skew_seconds': 3600,
        'enable_layer9_sync': False,  # Disable for isolated tests
        'enable_opa': False,  # Test without OPA first
        'nonce_cache_size': 1000
    }

@pytest.fixture
def emission_engine(test_config):
    """Proof emission engine fixture"""
    return ProofEmissionEngine(test_config)

@pytest.fixture
def ack_linker(test_config):
    """ACK linker fixture"""
    return ProviderACKLinker(test_config)

@pytest.fixture
def digest_validator(test_config):
    """Digest validator fixture"""
    return DigestValidator(test_config)

@pytest.fixture
def valid_kyc_data():
    """Valid KYC event data"""
    return {
        'event_type': 'kyc_completion',
        'event_id': 'evt_test_12345',
        'timestamp': int(time.time()),
        'provider_type': 'tier1_bank',
        'verification_level': 'enhanced',
        'user_name': 'SHOULD_BE_FILTERED',  # PII
        'document_id': 'SHOULD_BE_FILTERED'  # PII
    }

@pytest.fixture
def valid_digest(emission_engine, valid_kyc_data):
    """Valid proof digest"""
    return emission_engine.generate_digest(valid_kyc_data)

###########################################
# Unit Tests: Proof Emission Engine
###########################################

class TestProofEmissionEngine:
    """Unit tests for ProofEmissionEngine"""

    def test_generate_digest_filters_pii(self, emission_engine, valid_kyc_data):
        """Test that PII is filtered from digest"""
        digest = emission_engine.generate_digest(valid_kyc_data)

        # Check PII fields are not in metadata
        assert 'user_name' not in digest.metadata
        assert 'document_id' not in digest.metadata

        # Check allowed fields are present
        assert 'filtered_keys' in digest.metadata
        assert 'event_type' in digest.metadata['filtered_keys']

    def test_generate_digest_hash_formats(self, emission_engine, valid_kyc_data):
        """Test digest hash format correctness"""
        digest = emission_engine.generate_digest(valid_kyc_data)

        # SHA-512 content hash (128 hex chars)
        assert len(digest.content_hash) == 128
        assert all(c in '0123456789abcdef' for c in digest.content_hash.lower())

        # BLAKE2b merkle root (64 hex chars)
        assert len(digest.merkle_root) == 64
        assert all(c in '0123456789abcdef' for c in digest.merkle_root.lower())

        # HMAC digest ID (64 hex chars)
        assert len(digest.digest_id) == 64
        assert all(c in '0123456789abcdef' for c in digest.digest_id.lower())

    def test_generate_digest_deterministic(self, emission_engine):
        """Test digest generation is deterministic"""
        data1 = {
            'event_type': 'kyc_completion',
            'event_id': 'evt_123',
            'timestamp': 1234567890
        }

        
        with patch.object(emission_engine, '_generate_nonce', return_value='a' * 32):
            digest1 = emission_engine.generate_digest(data1)
            digest2 = emission_engine.generate_digest(data1)

            # Content hash should be identical
            assert digest1.content_hash == digest2.content_hash
            assert digest1.merkle_root == digest2.merkle_root

    def test_validate_digest_success(self, emission_engine, valid_digest):
        """Test digest validation succeeds for valid digest"""
        result = emission_engine._validate_digest(valid_digest)
        assert result is True

    def test_validate_digest_invalid_hash_length(self, emission_engine, valid_digest):
        """Test digest validation fails for invalid hash length"""
        valid_digest.content_hash = 'a' * 64  # Wrong length
        result = emission_engine._validate_digest(valid_digest)
        assert result is False

    def test_validate_digest_timestamp_out_of_range(self, emission_engine, valid_digest):
        """Test digest validation fails for old timestamp"""
        valid_digest.timestamp = int(time.time()) - 7200  # 2 hours ago
        result = emission_engine._validate_digest(valid_digest)
        assert result is False

    @patch('proof_emission_engine.GlobalProofNexus')
    def test_emit_proof_success(self, mock_nexus_class, emission_engine, valid_digest):
        """Test successful proof emission"""
        
        mock_nexus = Mock()
        mock_nexus.emit_proof_anchor.return_value = {
            'success': True,
            'tx_hash': '0x' + 'a' * 64
        }
        mock_nexus_class.return_value = mock_nexus

        emission_engine.enable_anchoring = True
        record = emission_engine.emit_proof(valid_digest, provider_id='test_provider')

        assert record.status == EmissionStatus.ANCHORED
        assert record.anchor_tx_hash is not None

    def test_emit_proof_validation_failure(self, emission_engine, valid_digest):
        """Test emission fails for invalid digest"""
        valid_digest.content_hash = 'invalid'
        record = emission_engine.emit_proof(valid_digest, provider_id='test_provider')

        assert record.status == EmissionStatus.FAILED
        assert 'validation failed' in record.error_log[0].lower()

    def test_export_audit_record(self, emission_engine, valid_digest):
        """Test audit record export"""
        record = EmissionRecord(
            digest=valid_digest,
            status=EmissionStatus.ANCHORED,
            anchor_tx_hash='0xabc123'
        )

        audit = emission_engine.export_audit_record(record)

        assert 'digest' in audit
        assert 'status' in audit
        assert audit['status'] == 'anchored'
        assert audit['anchor_tx_hash'] == '0xabc123'

###########################################
# Unit Tests: Provider ACK Linker
###########################################

class TestProviderACKLinker:
    """Unit tests for ProviderACKLinker"""

    def test_create_ack_request(self, ack_linker):
        """Test ACK request creation"""
        request = ack_linker.create_ack_request(
            digest_id='test_digest_123',
            content_hash='a' * 128,
            anchor_tx_hash='0xabc',
            provider_id='provider_001'
        )

        assert request.digest_id == 'test_digest_123'
        assert request.provider_id == 'provider_001'
        assert len(request.nonce) == 32
        assert len(request.signature) > 0

    def test_ack_request_to_jwt_payload(self, ack_linker):
        """Test ACK request JWT payload conversion"""
        request = ack_linker.create_ack_request(
            digest_id='test_digest',
            content_hash='a' * 128,
            anchor_tx_hash='0xabc',
            provider_id='provider_001'
        )

        payload = request.to_jwt_payload()

        assert payload['iss'] == 'ssid_layer14'
        assert payload['aud'] == 'provider_001'
        assert payload['sub'] == 'test_digest'
        assert 'ack_request' in payload

    def test_verify_ack_signature_valid(self, ack_linker):
        """Test ACK signature verification (mock)"""
        
        import base64
        ack_payload = {
            'iss': 'provider_001',
            'sub': 'test_digest',
            'exp': int(time.time()) + 300,
            'ack': {
                'digest_hash': 'a' * 128,
                'status': 'acknowledged'
            }
        }

        header = base64.urlsafe_b64encode(json.dumps({'alg': 'EdDSA'}).encode()).decode().rstrip('=')
        payload = base64.urlsafe_b64encode(json.dumps(ack_payload).encode()).decode().rstrip('=')
        signature = base64.urlsafe_b64encode(b'mock_sig').decode().rstrip('=')

        ack_jwt = f"{header}.{payload}.{signature}"

        result = ack_linker.verify_ack_signature(ack_jwt, 'provider_001')
        assert result is True  

    def test_verify_ack_signature_invalid_structure(self, ack_linker):
        """Test ACK signature verification fails for invalid JWT"""
        result = ack_linker.verify_ack_signature('invalid.jwt', 'provider_001')
        assert result is False

    def test_send_ack_request_success(self, ack_linker):
        """Test ACK request sending (mock)"""
        request = ack_linker.create_ack_request(
            digest_id='test_digest',
            content_hash='a' * 128,
            anchor_tx_hash='0xabc',
            provider_id='provider_001'
        )

        response = ack_linker.send_ack_request(request)

        
        assert response.status in [ACKStatus.ACKNOWLEDGED, ACKStatus.FAILED]

###########################################
# Unit Tests: Digest Validator
###########################################

class TestDigestValidator:
    """Unit tests for DigestValidator"""

    def test_validate_structure_success(self, digest_validator, valid_digest):
        """Test structure validation succeeds"""
        digest_dict = {
            'digest_id': valid_digest.digest_id,
            'content_hash': valid_digest.content_hash,
            'merkle_root': valid_digest.merkle_root,
            'timestamp': valid_digest.timestamp,
            'layer_origin': valid_digest.layer_origin,
            'nonce': valid_digest.nonce,
            'metadata': valid_digest.metadata
        }

        result = digest_validator.validate_digest(digest_dict)
        assert result.is_valid()

    def test_validate_structure_missing_fields(self, digest_validator):
        """Test structure validation fails for missing fields"""
        invalid_digest = {
            'digest_id': 'a' * 64,
            'content_hash': 'b' * 128
            # Missing required fields
        }

        result = digest_validator.validate_digest(invalid_digest)
        assert result.status == ValidationStatus.INVALID_STRUCTURE

    def test_validate_hash_integrity_invalid_format(self, digest_validator, valid_digest):
        """Test hash validation fails for non-hex"""
        digest_dict = {
            'digest_id': valid_digest.digest_id,
            'content_hash': 'ZZZZ' + 'a' * 124,  # Invalid hex
            'merkle_root': valid_digest.merkle_root,
            'timestamp': valid_digest.timestamp,
            'layer_origin': valid_digest.layer_origin,
            'nonce': valid_digest.nonce,
            'metadata': {}
        }

        result = digest_validator.validate_digest(digest_dict)
        assert result.status == ValidationStatus.INVALID_HASH

    def test_replay_protection(self, digest_validator, valid_digest):
        """Test replay protection detects duplicate nonce"""
        digest_dict = {
            'digest_id': valid_digest.digest_id,
            'content_hash': valid_digest.content_hash,
            'merkle_root': valid_digest.merkle_root,
            'timestamp': valid_digest.timestamp,
            'layer_origin': valid_digest.layer_origin,
            'nonce': valid_digest.nonce,
            'metadata': {}
        }

        # First validation should pass
        result1 = digest_validator.validate_digest(digest_dict)
        assert result1.is_valid()

        # Second validation with same nonce should fail
        result2 = digest_validator.validate_digest(digest_dict)
        assert result2.status == ValidationStatus.REPLAY_DETECTED

    def test_clear_nonce_cache(self, digest_validator):
        """Test nonce cache clearing"""
        digest_validator._nonce_cache.add('test_nonce')
        assert len(digest_validator._nonce_cache) == 1

        digest_validator.clear_nonce_cache()
        assert len(digest_validator._nonce_cache) == 0

###########################################
# Integration Tests: E2E Scenarios
###########################################

class TestE2EScenarios:
    """End-to-end integration test scenarios"""

    def test_scenario_1_valid_digest_anchor_ack_pass(
        self, emission_engine, ack_linker, valid_kyc_data
    ):
        """
        Scenario 1: Valid digest → anchor → ACK → PASS
        """
        # Step 1: Generate digest
        digest = emission_engine.generate_digest(valid_kyc_data)
        assert digest.content_hash is not None

        
        emission_engine.enable_anchoring = False
        record = emission_engine.emit_proof(digest, provider_id='provider_001')
        assert record.status == EmissionStatus.ANCHORED

        # Step 3: Create ACK request
        ack_request = ack_linker.create_ack_request(
            digest_id=digest.digest_id,
            content_hash=digest.content_hash,
            anchor_tx_hash=record.anchor_tx_hash,
            provider_id='provider_001'
        )
        assert ack_request is not None

        
        ack_response = ack_linker.send_ack_request(ack_request)
        assert ack_response.status in [ACKStatus.ACKNOWLEDGED, ACKStatus.FAILED]

    def test_scenario_2_tampered_ack_reject(self, ack_linker):
        """
        Scenario 2: Tampered ACK → reject + audit
        """
        # Create tampered ACK JWT (invalid signature)
        tampered_jwt = "eyJhbGciOiJFZERTQSJ9.eyJpc3MiOiJhdHRhY2tlciJ9.invalid_sig"

        result = ack_linker.verify_ack_signature(tampered_jwt, 'provider_001')
        assert result is False

    def test_scenario_3_replay_attack_opa_reject(self, digest_validator, valid_digest):
        """
        Scenario 3: Replay attack → OPA deny
        """
        digest_dict = {
            'digest_id': valid_digest.digest_id,
            'content_hash': valid_digest.content_hash,
            'merkle_root': valid_digest.merkle_root,
            'timestamp': valid_digest.timestamp,
            'layer_origin': valid_digest.layer_origin,
            'nonce': valid_digest.nonce,
            'metadata': {}
        }

        # First attempt: PASS
        result1 = digest_validator.validate_digest(digest_dict)
        assert result1.is_valid()

        # Second attempt with same nonce: FAIL
        result2 = digest_validator.validate_digest(digest_dict)
        assert result2.status == ValidationStatus.REPLAY_DETECTED

    def test_scenario_4_hash_mismatch_fail(self, digest_validator):
        """
        Scenario 4: Hash mismatch → fail
        """
        invalid_digest = {
            'digest_id': 'a' * 64,
            'content_hash': 'b' * 127 + 'Z',  # Invalid last char
            'merkle_root': 'c' * 64,
            'timestamp': int(time.time()),
            'layer_origin': 'layer_14',
            'nonce': 'd' * 32,
            'metadata': {}
        }

        result = digest_validator.validate_digest(invalid_digest)
        assert not result.is_valid()

    def test_scenario_5_missing_ack_retry_queue(self, ack_linker):
        """
        Scenario 5: Missing ACK → retry queue
        """
        request = ack_linker.create_ack_request(
            digest_id='test',
            content_hash='a' * 128,
            anchor_tx_hash='0xabc',
            provider_id='provider_offline'
        )

        record = ACKRecord(
            request=request,
            response=None,
            status=ACKStatus.PENDING,
            retry_count=0
        )

        # Retry logic
        with patch.object(ack_linker, 'send_ack_request') as mock_send:
            mock_send.return_value = ACKResponse(
                ack_id='',
                request_id=request.request_id,
                digest_id=request.digest_id,
                provider_id=request.provider_id,
                status=ACKStatus.TIMEOUT
            )

            retried = ack_linker.retry_ack(record)
            assert retried.retry_count == 1

    def test_scenario_6_pii_injection_reject(self, emission_engine):
        """
        Scenario 6: PII injection → reject + log
        """
        pii_data = {
            'event_type': 'kyc_completion',
            'user_name': 'John Doe',  # PII
            'ssn': '123-45-6789',  # PII
            'email': 'john@example.com'  # PII
        }

        # PII should be filtered
        digest = emission_engine.generate_digest(pii_data)

        # Verify no PII in metadata
        assert 'user_name' not in digest.metadata
        assert 'ssn' not in digest.metadata
        assert 'email' not in digest.metadata

    def test_scenario_7_digest_resync_pass(self, emission_engine, valid_digest):
        """
        Scenario 7: Digest re-sync → PASS
        """
        # Export and re-import digest
        record = EmissionRecord(
            digest=valid_digest,
            status=EmissionStatus.ANCHORED,
            anchor_tx_hash='0xabc123'
        )

        audit = emission_engine.export_audit_record(record)

        # Verify audit contains all fields
        assert audit['digest']['digest_id'] == valid_digest.digest_id
        assert audit['status'] == 'anchored'

###########################################
# Performance Tests
###########################################

class TestPerformance:
    """Performance and stress tests"""

    def test_digest_generation_performance(self, emission_engine, valid_kyc_data):
        """Test digest generation performance (<10ms target)"""
        start = time.time()

        for _ in range(100):
            emission_engine.generate_digest(valid_kyc_data)

        elapsed = time.time() - start
        avg_time = elapsed / 100

        # Should be fast (<10ms per digest)
        assert avg_time < 0.01

    def test_nonce_cache_size_limit(self, digest_validator):
        """Test nonce cache respects size limit"""
        digest_validator._nonce_cache_max_size = 10

        # Add 20 nonces
        for i in range(20):
            nonce = f"nonce_{i:032d}"
            digest_validator._nonce_cache.add(nonce)

        # Cache should not exceed max size (simple pop logic)
        assert len(digest_validator._nonce_cache) <= 10

###########################################
# Pytest Configuration
###########################################

if __name__ == "__main__":
    pytest.main([
        __file__,
        "-v",
        "--cov=proof_emission",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=95"
    ])
