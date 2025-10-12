// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.20;

/**
 * @title ProofAnchor
 * @notice Minimal on-chain proof anchoring for SSID KYC Gateway
 * @dev Hash-only anchoring (no PII, no custody, no payment logic)
 *
 * Architecture: Non-custodial, proof-only, permissionless
 * Use case: Optional on-chain verification of KYC proof digests
 * Privacy: Only SHA-256/BLAKE2b hashes anchored (no personal data)
 * Compliance: GDPR-compatible (hash-only), no KYC role
 *
 * License: GPL-3.0-or-later
 * Version: 1.0.0
 */

contract ProofAnchor {
    /// @notice Proof record structure (hash-only, no PII)
    struct Proof {
        bytes32 digest;         // SHA-256 or BLAKE2b hash
        string providerId;      // Provider identifier (e.g., "didit")
        uint256 timestamp;      // Block timestamp
        address submitter;      // Address that anchored the proof
        bool exists;            // Existence flag
    }

    /// @notice Mapping: proof ID → proof record
    mapping(bytes32 => Proof) public proofs;

    /// @notice Mapping: address → proof count
    mapping(address => uint256) public submitterProofCount;

    /// @notice Total proofs anchored
    uint256 public totalProofs;

    /// @notice Contract version
    string public constant VERSION = "1.0.0";

    /// @notice Events
    event ProofAnchored(
        bytes32 indexed proofId,
        bytes32 indexed digest,
        string providerId,
        address indexed submitter,
        uint256 timestamp
    );

    event ProofVerified(
        bytes32 indexed proofId,
        address indexed verifier,
        uint256 timestamp
    );

    /**
     * @notice Anchor a proof digest on-chain
     * @param proofId Unique proof identifier (keccak256 hash)
     * @param digest SHA-256 or BLAKE2b hash of proof claims
     * @param providerId Provider identifier (e.g., "didit", "yoti")
     */
    function anchorProof(
        bytes32 proofId,
        bytes32 digest,
        string calldata providerId
    ) external {
        require(proofId != bytes32(0), "Invalid proof ID");
        require(digest != bytes32(0), "Invalid digest");
        require(bytes(providerId).length > 0, "Invalid provider ID");
        require(!proofs[proofId].exists, "Proof already anchored");

        proofs[proofId] = Proof({
            digest: digest,
            providerId: providerId,
            timestamp: block.timestamp,
            submitter: msg.sender,
            exists: true
        });

        submitterProofCount[msg.sender]++;
        totalProofs++;

        emit ProofAnchored(proofId, digest, providerId, msg.sender, block.timestamp);
    }

    /**
     * @notice Verify a proof exists on-chain
     * @param proofId Proof identifier
     * @return exists Whether proof exists
     * @return digest Proof digest (if exists)
     * @return providerId Provider ID (if exists)
     * @return timestamp Anchor timestamp (if exists)
     */
    function verifyProof(bytes32 proofId)
        external
        returns (
            bool exists,
            bytes32 digest,
            string memory providerId,
            uint256 timestamp
        )
    {
        Proof memory proof = proofs[proofId];

        if (proof.exists) {
            emit ProofVerified(proofId, msg.sender, block.timestamp);
        }

        return (
            proof.exists,
            proof.digest,
            proof.providerId,
            proof.timestamp
        );
    }

    /**
     * @notice Get proof details (view function)
     * @param proofId Proof identifier
     * @return Proof struct
     */
    function getProof(bytes32 proofId) external view returns (Proof memory) {
        return proofs[proofId];
    }

    /**
     * @notice Check if proof exists (view function)
     * @param proofId Proof identifier
     * @return exists Whether proof exists
     */
    function proofExists(bytes32 proofId) external view returns (bool) {
        return proofs[proofId].exists;
    }

    /**
     * @notice Get submitter's proof count
     * @param submitter Address to query
     * @return count Number of proofs anchored by address
     */
    function getSubmitterProofCount(address submitter) external view returns (uint256) {
        return submitterProofCount[submitter];
    }

    /**
     * @notice Batch verify multiple proofs
     * @param proofIds Array of proof IDs to verify
     * @return results Array of existence flags
     */
    function batchVerifyProofs(bytes32[] calldata proofIds)
        external
        view
        returns (bool[] memory results)
    {
        results = new bool[](proofIds.length);
        for (uint256 i = 0; i < proofIds.length; i++) {
            results[i] = proofs[proofIds[i]].exists;
        }
        return results;
    }
}
