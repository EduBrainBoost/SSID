// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AuditCycle
 * @notice Automated 24-Hour Audit Cycle for SSID Federation v5.4
 * @dev Stores Merkle roots, triggers audit events, verifies digest integrity
 *
 * Features:
 * - 24-hour audit cycle automation
 * - Merkle root storage for all federations
 * - Digest verification against stored roots
 * - Cross-federation audit synchronization
 */

contract AuditCycle {
    /// @notice Contract version
    string public constant VERSION = "5.4.0";

    /// @notice Owner address
    address public owner;

    /// @notice Federation anchor contract
    address public federationAnchorContract;

    /// @notice Total audit cycles completed
    uint256 public totalAuditCycles;

    /// @notice Audit cycle struct
    struct Cycle {
        uint256 cycleNumber;
        uint256 timestamp;
        bytes32 globalMerkleRoot;
        uint256 totalProofs;
        uint256 totalFederations;
        mapping(string => bytes32) federationRoots;  // federationId => merkleRoot
        bool completed;
    }

    /// @notice Audit cycles (cycleNumber => Cycle)
    mapping(uint256 => Cycle) public auditCycles;

    /// @notice Current cycle number
    uint256 public currentCycle;

    /// @notice Digest verification record
    struct DigestVerification {
        bytes32 digestHash;
        string federationId;
        uint256 cycleNumber;
        uint256 timestamp;
        bool verified;
    }

    /// @notice Digest verifications (digestHash => DigestVerification)
    mapping(bytes32 => DigestVerification) public digestVerifications;

    /// @notice Events
    event AuditCycleStarted(
        uint256 indexed cycleNumber,
        uint256 timestamp
    );

    event AuditCycleCompleted(
        uint256 indexed cycleNumber,
        uint256 timestamp,
        bytes32 globalMerkleRoot,
        uint256 totalProofs
    );

    event FederationMerkleRootStored(
        uint256 indexed cycleNumber,
        string indexed federationId,
        bytes32 merkleRoot,
        uint256 timestamp
    );

    event DigestVerified(
        bytes32 indexed digestHash,
        string federationId,
        uint256 cycleNumber,
        bool verified,
        uint256 timestamp
    );

    /// @notice Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "AuditCycle: not owner");
        _;
    }

    modifier onlyFederationAnchor() {
        require(
            msg.sender == federationAnchorContract,
            "AuditCycle: not federation anchor"
        );
        _;
    }

    /**
     * @notice Constructor
     * @param _federationAnchorContract Address of FederationAnchor contract
     */
    constructor(address _federationAnchorContract) {
        owner = msg.sender;
        federationAnchorContract = _federationAnchorContract;
        currentCycle = 0;
    }

    /**
     * @notice Start new audit cycle
     */
    function startAuditCycle() external onlyOwner {
        currentCycle++;
        totalAuditCycles++;

        Cycle storage cycle = auditCycles[currentCycle];
        cycle.cycleNumber = currentCycle;
        cycle.timestamp = block.timestamp;
        cycle.completed = false;

        emit AuditCycleStarted(currentCycle, block.timestamp);
    }

    /**
     * @notice Store federation Merkle root
     * @param cycleNumber Audit cycle number
     * @param federationId Federation identifier
     * @param merkleRoot Merkle root of federation proofs
     */
    function storeFederationMerkleRoot(
        uint256 cycleNumber,
        string memory federationId,
        bytes32 merkleRoot
    ) external onlyOwner {
        require(cycleNumber <= currentCycle, "AuditCycle: invalid cycle");
        require(merkleRoot != bytes32(0), "AuditCycle: invalid merkle root");
        require(!auditCycles[cycleNumber].completed, "AuditCycle: cycle completed");

        auditCycles[cycleNumber].federationRoots[federationId] = merkleRoot;
        auditCycles[cycleNumber].totalFederations++;

        emit FederationMerkleRootStored(
            cycleNumber,
            federationId,
            merkleRoot,
            block.timestamp
        );
    }

    /**
     * @notice Complete audit cycle
     * @param cycleNumber Cycle number
     * @param globalMerkleRoot Global Merkle root (all federations)
     * @param totalProofs Total proofs in cycle
     */
    function completeAuditCycle(
        uint256 cycleNumber,
        bytes32 globalMerkleRoot,
        uint256 totalProofs
    ) external onlyOwner {
        require(cycleNumber <= currentCycle, "AuditCycle: invalid cycle");
        require(!auditCycles[cycleNumber].completed, "AuditCycle: already completed");
        require(globalMerkleRoot != bytes32(0), "AuditCycle: invalid global root");

        auditCycles[cycleNumber].globalMerkleRoot = globalMerkleRoot;
        auditCycles[cycleNumber].totalProofs = totalProofs;
        auditCycles[cycleNumber].completed = true;

        emit AuditCycleCompleted(
            cycleNumber,
            block.timestamp,
            globalMerkleRoot,
            totalProofs
        );
    }

    /**
     * @notice Verify digest against stored Merkle root
     * @param digestHash Hash of digest to verify
     * @param federationId Federation that generated digest
     * @param cycleNumber Audit cycle
     * @param merkleProof Merkle proof path
     * @return bool Verification result
     */
    function verifyDigest(
        bytes32 digestHash,
        string memory federationId,
        uint256 cycleNumber,
        bytes32[] memory merkleProof
    ) external returns (bool) {
        require(cycleNumber <= currentCycle, "AuditCycle: invalid cycle");
        require(auditCycles[cycleNumber].completed, "AuditCycle: cycle not completed");

        bytes32 federationRoot = auditCycles[cycleNumber].federationRoots[federationId];
        require(federationRoot != bytes32(0), "AuditCycle: federation root not found");

        // Verify Merkle proof
        bool verified = _verifyMerkleProof(digestHash, merkleProof, federationRoot);

        // Store verification record
        digestVerifications[digestHash] = DigestVerification({
            digestHash: digestHash,
            federationId: federationId,
            cycleNumber: cycleNumber,
            timestamp: block.timestamp,
            verified: verified
        });

        emit DigestVerified(digestHash, federationId, cycleNumber, verified, block.timestamp);

        return verified;
    }

    /**
     * @notice Verify Merkle proof
     * @param leaf Leaf node (digest hash)
     * @param proof Merkle proof path
     * @param root Merkle root
     * @return bool Verification result
     */
    function _verifyMerkleProof(
        bytes32 leaf,
        bytes32[] memory proof,
        bytes32 root
    ) internal pure returns (bool) {
        bytes32 computedHash = leaf;

        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 proofElement = proof[i];

            if (computedHash < proofElement) {
                computedHash = keccak256(abi.encodePacked(computedHash, proofElement));
            } else {
                computedHash = keccak256(abi.encodePacked(proofElement, computedHash));
            }
        }

        return computedHash == root;
    }

    /**
     * @notice Get federation Merkle root for cycle
     * @param cycleNumber Cycle number
     * @param federationId Federation identifier
     * @return bytes32 Merkle root
     */
    function getFederationMerkleRoot(
        uint256 cycleNumber,
        string memory federationId
    ) external view returns (bytes32) {
        return auditCycles[cycleNumber].federationRoots[federationId];
    }

    /**
     * @notice Get audit cycle info
     * @param cycleNumber Cycle number
     * @return timestamp Cycle timestamp
     * @return globalMerkleRoot Global Merkle root
     * @return totalProofs Total proofs
     * @return completed Completion status
     */
    function getAuditCycle(uint256 cycleNumber) external view returns (
        uint256 timestamp,
        bytes32 globalMerkleRoot,
        uint256 totalProofs,
        bool completed
    ) {
        Cycle storage cycle = auditCycles[cycleNumber];
        return (
            cycle.timestamp,
            cycle.globalMerkleRoot,
            cycle.totalProofs,
            cycle.completed
        );
    }

    /**
     * @notice Get digest verification record
     * @param digestHash Digest hash
     * @return DigestVerification struct
     */
    function getDigestVerification(bytes32 digestHash) external view returns (
        bytes32,
        string memory,
        uint256,
        uint256,
        bool
    ) {
        DigestVerification storage dv = digestVerifications[digestHash];
        return (
            dv.digestHash,
            dv.federationId,
            dv.cycleNumber,
            dv.timestamp,
            dv.verified
        );
    }

    /**
     * @notice Update federation anchor contract address
     * @param _federationAnchorContract New address
     */
    function setFederationAnchorContract(address _federationAnchorContract) external onlyOwner {
        require(_federationAnchorContract != address(0), "AuditCycle: invalid address");
        federationAnchorContract = _federationAnchorContract;
    }

    /**
     * @notice Transfer ownership
     * @param newOwner New owner address
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "AuditCycle: invalid new owner");
        owner = newOwner;
    }

    /**
     * @notice Get contract metadata
     */
    function getMetadata() external view returns (
        string memory version,
        uint256 currentCycleNum,
        uint256 totalCycles
    ) {
        return (VERSION, currentCycle, totalAuditCycles);
    }
}
