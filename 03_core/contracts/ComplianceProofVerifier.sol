// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ComplianceProofVerifier
 * @author edubrainboost ©2025
 * @notice On-chain compliance proof verification for SSID anti-gaming checks
 * @dev This contract records tamper-proof evidence of anti-gaming check results
 *
 * SSID Policy Flags:
 * - hash_only: true
 * - no_pii: true
 * - non_custodial: true
 * - blockchain_anchored: true
 *
 * Compliance Notes:
 * - GDPR Art. 25: Privacy by design (only hashes, no PII on-chain)
 * - eIDAS: Non-repudiation via blockchain immutability
 * - MiCA Art. 76: Operational resilience via decentralized proof storage
 */

contract ComplianceProofVerifier {
    /// @notice Version of the contract
    string public constant VERSION = "1.0.0";

    /// @notice Proof types supported by this contract
    enum ProofType {
        NO_DUPLICATE_IDENTITY,
        HASH_COLLISION_FREE,
        DID_UNIQUENESS_VERIFIED,
        ANTI_GAMING_PASSED
    }

    /// @notice Status of a compliance check
    enum CheckStatus {
        PASS,
        WARN,
        FAIL,
        CRITICAL
    }

    /// @notice Structure representing a compliance proof
    struct ComplianceProof {
        uint256 timestamp;
        ProofType proofType;
        CheckStatus status;
        uint256 collisionCount;
        bytes32 evidenceHash;  // SHA3-256 hash of the full audit log entry
        address submitter;
        string component;  // e.g., "anti_gaming"
        string checkName;  // e.g., "duplicate_identity_hashes"
    }

    /// @notice Mapping from proof ID to ComplianceProof
    mapping(bytes32 => ComplianceProof) public proofs;

    /// @notice Array of all proof IDs (for enumeration)
    bytes32[] public proofIds;

    /// @notice Mapping from component name to latest proof ID
    mapping(string => bytes32) public latestProofByComponent;

    /// @notice Event emitted when a new proof is recorded
    event ProofRecorded(
        bytes32 indexed proofId,
        ProofType indexed proofType,
        CheckStatus status,
        uint256 collisionCount,
        bytes32 evidenceHash,
        address submitter,
        uint256 timestamp
    );

    /// @notice Event emitted when a critical failure is detected
    event CriticalFailureDetected(
        bytes32 indexed proofId,
        ProofType proofType,
        uint256 collisionCount,
        uint256 timestamp
    );

    /// @notice Authorized submitters (can be managed by governance)
    mapping(address => bool) public authorizedSubmitters;

    /// @notice Contract owner (for access control)
    address public owner;

    /// @notice Total number of proofs recorded
    uint256 public totalProofs;

    /// @notice Modifier to restrict function access to authorized submitters
    modifier onlyAuthorized() {
        require(
            authorizedSubmitters[msg.sender] || msg.sender == owner,
            "Not authorized to submit proofs"
        );
        _;
    }

    /// @notice Modifier to restrict function access to contract owner
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    /// @notice Constructor
    constructor() {
        owner = msg.sender;
        authorizedSubmitters[msg.sender] = true;
    }

    /**
     * @notice Record a new anti-gaming compliance proof on-chain
     * @param proofType Type of proof being recorded
     * @param status Status of the check (PASS, WARN, FAIL, CRITICAL)
     * @param collisionCount Number of collisions detected
     * @param evidenceHash SHA3-256 hash of the audit log entry
     * @param component Component name (e.g., "anti_gaming")
     * @param checkName Check name (e.g., "duplicate_identity_hashes")
     * @return proofId Unique identifier for this proof
     */
    function recordAntiGamingProof(
        ProofType proofType,
        CheckStatus status,
        uint256 collisionCount,
        bytes32 evidenceHash,
        string calldata component,
        string calldata checkName
    ) external onlyAuthorized returns (bytes32 proofId) {
        // Generate unique proof ID
        proofId = keccak256(
            abi.encodePacked(
                block.timestamp,
                msg.sender,
                proofType,
                evidenceHash,
                totalProofs
            )
        );

        // Ensure proof ID is unique
        require(proofs[proofId].timestamp == 0, "Proof ID collision");

        // Create proof
        ComplianceProof memory proof = ComplianceProof({
            timestamp: block.timestamp,
            proofType: proofType,
            status: status,
            collisionCount: collisionCount,
            evidenceHash: evidenceHash,
            submitter: msg.sender,
            component: component,
            checkName: checkName
        });

        // Store proof
        proofs[proofId] = proof;
        proofIds.push(proofId);
        latestProofByComponent[component] = proofId;
        totalProofs++;

        // Emit event
        emit ProofRecorded(
            proofId,
            proofType,
            status,
            collisionCount,
            evidenceHash,
            msg.sender,
            block.timestamp
        );

        // Emit critical failure event if applicable
        if (status == CheckStatus.CRITICAL || status == CheckStatus.FAIL) {
            emit CriticalFailureDetected(
                proofId,
                proofType,
                collisionCount,
                block.timestamp
            );
        }

        return proofId;
    }

    /**
     * @notice Verify a proof exists and retrieve its details
     * @param proofId Unique identifier of the proof
     * @return exists Whether the proof exists
     * @return proof The proof details
     */
    function verifyProof(bytes32 proofId)
        external
        view
        returns (bool exists, ComplianceProof memory proof)
    {
        proof = proofs[proofId];
        exists = proof.timestamp > 0;
        return (exists, proof);
    }

    /**
     * @notice Get the latest proof for a given component
     * @param component Component name (e.g., "anti_gaming")
     * @return proofId Latest proof ID for the component
     * @return proof The proof details
     */
    function getLatestProofByComponent(string calldata component)
        external
        view
        returns (bytes32 proofId, ComplianceProof memory proof)
    {
        proofId = latestProofByComponent[component];
        proof = proofs[proofId];
        return (proofId, proof);
    }

    /**
     * @notice Get total number of proofs recorded
     * @return count Total proof count
     */
    function getProofCount() external view returns (uint256 count) {
        return totalProofs;
    }

    /**
     * @notice Get proof ID by index
     * @param index Index in the proofIds array
     * @return proofId Proof ID at the given index
     */
    function getProofIdByIndex(uint256 index)
        external
        view
        returns (bytes32 proofId)
    {
        require(index < proofIds.length, "Index out of bounds");
        return proofIds[index];
    }

    /**
     * @notice Authorize a new submitter
     * @param submitter Address to authorize
     */
    function authorizeSubmitter(address submitter) external onlyOwner {
        authorizedSubmitters[submitter] = true;
    }

    /**
     * @notice Revoke submitter authorization
     * @param submitter Address to revoke
     */
    function revokeSubmitter(address submitter) external onlyOwner {
        authorizedSubmitters[submitter] = false;
    }

    /**
     * @notice Transfer contract ownership
     * @param newOwner Address of the new owner
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid new owner address");
        owner = newOwner;
    }

    /**
     * @notice Get statistics for a given component
     * @param component Component name
     * @return totalChecks Total checks for this component
     * @return passCount Number of PASS results
     * @return failCount Number of FAIL results
     * @return criticalCount Number of CRITICAL results
     */
    function getComponentStats(string calldata component)
        external
        view
        returns (
            uint256 totalChecks,
            uint256 passCount,
            uint256 failCount,
            uint256 criticalCount
        )
    {
        for (uint256 i = 0; i < proofIds.length; i++) {
            ComplianceProof storage proof = proofs[proofIds[i]];
            if (
                keccak256(abi.encodePacked(proof.component)) ==
                keccak256(abi.encodePacked(component))
            ) {
                totalChecks++;
                if (proof.status == CheckStatus.PASS) passCount++;
                if (proof.status == CheckStatus.FAIL) failCount++;
                if (proof.status == CheckStatus.CRITICAL) criticalCount++;
            }
        }
        return (totalChecks, passCount, failCount, criticalCount);
    }
}
