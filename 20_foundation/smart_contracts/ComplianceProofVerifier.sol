// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ComplianceProofVerifier
 * @notice Verifies and stores compliance proof hashes with auditor signatures
 * @dev Part of SSID decentralized compliance framework
 *
 * Version: 2025-Q4
 * Last Updated: 2025-10-07
 * Maintainer: edubrainboost
 * Classification: CRITICAL - Blockchain Verification
 */

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract ComplianceProofVerifier is AccessControl, Pausable {
    // Role definitions
    bytes32 public constant AUDITOR_ROLE = keccak256("AUDITOR_ROLE");
    bytes32 public constant SYSTEM_ROLE = keccak256("SYSTEM_ROLE");

    // Proof structure
    struct ComplianceProof {
        bytes32 proofHash;
        uint256 timestamp;
        address submittedBy;
        ProofStatus status;
        string framework; // "GDPR", "DORA", "MiCA", "AMLD6", or "UNIFIED"
        string complianceVersion; // e.g., "2025-Q4"
    }

    // Auditor signature structure
    struct AuditorSignature {
        address auditor;
        uint256 signedAt;
        bool isVerified;
        string comment;
    }

    enum ProofStatus {
        Submitted,
        UnderReview,
        Verified,
        Rejected,
        Expired
    }

    // State variables
    mapping(bytes32 => ComplianceProof) public proofs;
    mapping(bytes32 => AuditorSignature[]) public proofSignatures;
    mapping(address => bool) public approvedAuditors;

    bytes32[] public proofHashes;
    uint256 public proofCount;

    // Events
    event ProofSubmitted(
        bytes32 indexed proofHash,
        address indexed submitter,
        string framework,
        string complianceVersion,
        uint256 timestamp
    );

    event ProofSigned(
        bytes32 indexed proofHash,
        address indexed auditor,
        bool isVerified,
        string comment,
        uint256 timestamp
    );

    event ProofStatusChanged(
        bytes32 indexed proofHash,
        ProofStatus oldStatus,
        ProofStatus newStatus,
        uint256 timestamp
    );

    event AuditorApproved(
        address indexed auditor,
        address indexed approvedBy,
        uint256 timestamp
    );

    event AuditorRevoked(
        address indexed auditor,
        address indexed revokedBy,
        uint256 timestamp
    );

    // Constructor
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(SYSTEM_ROLE, msg.sender);
    }

    // ========================================================================
    // Proof Submission Functions
    // ========================================================================

    /**
     * @notice Submit a new compliance proof hash
     * @param _proofHash SHA256 hash of the compliance proof
     * @param _framework Framework name (GDPR, DORA, MiCA, AMLD6, UNIFIED)
     * @param _complianceVersion Compliance version (e.g., "2025-Q4")
     */
    function submitProof(
        bytes32 _proofHash,
        string memory _framework,
        string memory _complianceVersion
    ) external onlyRole(SYSTEM_ROLE) whenNotPaused {
        require(_proofHash != bytes32(0), "Invalid proof hash");
        require(proofs[_proofHash].timestamp == 0, "Proof already exists");

        proofs[_proofHash] = ComplianceProof({
            proofHash: _proofHash,
            timestamp: block.timestamp,
            submittedBy: msg.sender,
            status: ProofStatus.Submitted,
            framework: _framework,
            complianceVersion: _complianceVersion
        });

        proofHashes.push(_proofHash);
        proofCount++;

        emit ProofSubmitted(
            _proofHash,
            msg.sender,
            _framework,
            _complianceVersion,
            block.timestamp
        );
    }

    /**
     * @notice Submit multiple proofs in batch
     * @param _proofHashes Array of proof hashes
     * @param _frameworks Array of framework names
     * @param _complianceVersions Array of compliance versions
     */
    function submitProofBatch(
        bytes32[] memory _proofHashes,
        string[] memory _frameworks,
        string[] memory _complianceVersions
    ) external onlyRole(SYSTEM_ROLE) whenNotPaused {
        require(
            _proofHashes.length == _frameworks.length &&
            _proofHashes.length == _complianceVersions.length,
            "Array length mismatch"
        );

        for (uint256 i = 0; i < _proofHashes.length; i++) {
            if (_proofHashes[i] != bytes32(0) && proofs[_proofHashes[i]].timestamp == 0) {
                proofs[_proofHashes[i]] = ComplianceProof({
                    proofHash: _proofHashes[i],
                    timestamp: block.timestamp,
                    submittedBy: msg.sender,
                    status: ProofStatus.Submitted,
                    framework: _frameworks[i],
                    complianceVersion: _complianceVersions[i]
                });

                proofHashes.push(_proofHashes[i]);
                proofCount++;

                emit ProofSubmitted(
                    _proofHashes[i],
                    msg.sender,
                    _frameworks[i],
                    _complianceVersions[i],
                    block.timestamp
                );
            }
        }
    }

    // ========================================================================
    // Auditor Signature Functions
    // ========================================================================

    /**
     * @notice Sign a proof as an approved auditor
     * @param _proofHash Hash of the proof to sign
     * @param _isVerified Whether the auditor verifies the proof
     * @param _comment Auditor's comment
     */
    function signProof(
        bytes32 _proofHash,
        bool _isVerified,
        string memory _comment
    ) external whenNotPaused {
        require(proofs[_proofHash].timestamp != 0, "Proof does not exist");
        require(approvedAuditors[msg.sender] || hasRole(AUDITOR_ROLE, msg.sender), "Not an approved auditor");
        require(proofs[_proofHash].status != ProofStatus.Expired, "Proof expired");

        AuditorSignature memory signature = AuditorSignature({
            auditor: msg.sender,
            signedAt: block.timestamp,
            isVerified: _isVerified,
            comment: _comment
        });

        proofSignatures[_proofHash].push(signature);

        // Update proof status based on verification
        if (_isVerified) {
            _updateProofStatus(_proofHash, ProofStatus.Verified);
        } else {
            _updateProofStatus(_proofHash, ProofStatus.UnderReview);
        }

        emit ProofSigned(
            _proofHash,
            msg.sender,
            _isVerified,
            _comment,
            block.timestamp
        );
    }

    /**
     * @notice Update proof status
     * @param _proofHash Hash of the proof
     * @param _newStatus New status
     */
    function _updateProofStatus(bytes32 _proofHash, ProofStatus _newStatus) internal {
        ProofStatus oldStatus = proofs[_proofHash].status;
        proofs[_proofHash].status = _newStatus;

        emit ProofStatusChanged(_proofHash, oldStatus, _newStatus, block.timestamp);
    }

    /**
     * @notice Manually update proof status (admin only)
     * @param _proofHash Hash of the proof
     * @param _newStatus New status
     */
    function updateProofStatus(
        bytes32 _proofHash,
        ProofStatus _newStatus
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(proofs[_proofHash].timestamp != 0, "Proof does not exist");
        _updateProofStatus(_proofHash, _newStatus);
    }

    // ========================================================================
    // Auditor Management Functions
    // ========================================================================

    /**
     * @notice Approve an auditor
     * @param _auditor Address of the auditor to approve
     */
    function approveAuditor(address _auditor) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_auditor != address(0), "Invalid auditor address");
        require(!approvedAuditors[_auditor], "Auditor already approved");

        approvedAuditors[_auditor] = true;
        _grantRole(AUDITOR_ROLE, _auditor);

        emit AuditorApproved(_auditor, msg.sender, block.timestamp);
    }

    /**
     * @notice Revoke an auditor
     * @param _auditor Address of the auditor to revoke
     */
    function revokeAuditor(address _auditor) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(approvedAuditors[_auditor], "Auditor not approved");

        approvedAuditors[_auditor] = false;
        _revokeRole(AUDITOR_ROLE, _auditor);

        emit AuditorRevoked(_auditor, msg.sender, block.timestamp);
    }

    // ========================================================================
    // View Functions
    // ========================================================================

    /**
     * @notice Get proof details
     * @param _proofHash Hash of the proof
     */
    function getProof(bytes32 _proofHash)
        external
        view
        returns (
            bytes32 proofHash,
            uint256 timestamp,
            address submittedBy,
            ProofStatus status,
            string memory framework,
            string memory complianceVersion,
            uint256 signatureCount
        )
    {
        ComplianceProof memory proof = proofs[_proofHash];
        return (
            proof.proofHash,
            proof.timestamp,
            proof.submittedBy,
            proof.status,
            proof.framework,
            proof.complianceVersion,
            proofSignatures[_proofHash].length
        );
    }

    /**
     * @notice Get all signatures for a proof
     * @param _proofHash Hash of the proof
     */
    function getProofSignatures(bytes32 _proofHash)
        external
        view
        returns (AuditorSignature[] memory)
    {
        return proofSignatures[_proofHash];
    }

    /**
     * @notice Verify if a proof exists and is verified
     * @param _proofHash Hash of the proof
     */
    function isProofVerified(bytes32 _proofHash) external view returns (bool) {
        return proofs[_proofHash].status == ProofStatus.Verified;
    }

    /**
     * @notice Get total number of proofs
     */
    function getTotalProofs() external view returns (uint256) {
        return proofCount;
    }

    /**
     * @notice Get proof hash by index
     * @param _index Index in the proofHashes array
     */
    function getProofHashByIndex(uint256 _index) external view returns (bytes32) {
        require(_index < proofHashes.length, "Index out of bounds");
        return proofHashes[_index];
    }

    // ========================================================================
    // Admin Functions
    // ========================================================================

    /**
     * @notice Pause the contract
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    /**
     * @notice Unpause the contract
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }
}
