"""
SSID Proof Emission & Provider Linking v5.2
Layer 14 → Layer 9 Bidirectional Proof Flow

Exports:
- ProofEmissionEngine: Core emission orchestrator
- ProviderACKLinker: Bidirectional ACK flow manager
- DigestValidator: Cross-layer verification
- EmissionStatus, ACKStatus, ValidationStatus: Status enums
"""

from .proof_emission_engine import (
    ProofEmissionEngine,
    ProofDigest,
    EmissionRecord,
    EmissionStatus,
    create_engine
)

from .provider_ack_linker import (
    ProviderACKLinker,
    ACKRequest,
    ACKResponse,
    ACKRecord,
    ACKStatus,
    create_linker
)

from .digest_validator import (
    DigestValidator,
    ValidationResult,
    ValidationStatus,
    create_validator
)

__version__ = "5.2.0"
__all__ = [
    # Emission Engine
    "ProofEmissionEngine",
    "ProofDigest",
    "EmissionRecord",
    "EmissionStatus",
    "create_engine",
    # ACK Linker
    "ProviderACKLinker",
    "ACKRequest",
    "ACKResponse",
    "ACKRecord",
    "ACKStatus",
    "create_linker",
    # Validator
    "DigestValidator",
    "ValidationResult",
    "ValidationStatus",
    "create_validator",
]
