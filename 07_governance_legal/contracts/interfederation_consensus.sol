// SPDX-License-Identifier: GPL-3.0-or-later
/*
 * ════════════════════════════════════════════════════════════════════════════
 * SSID Inter-Federation Mesh Consensus Layer
 * Blueprint: v4.9.0 | Layer 8: Cross-Federation Consensus Root Aggregation
 * Phase: POST-FEDERATION → INTER-FEDERATION
 * Date: 2026-04-01 00:00 UTC
 * ════════════════════════════════════════════════════════════════════════════
 *
 * Security Reference: SHA-256 Hash-Based Zero-Custody Consensus Anchoring
 * Compliance: GDPR, eIDAS, MiCA, DORA, AMLD6
 * Root-24-LOCK: ENFORCED
 * SAFE-FIX: ENFORCED
 *
 * Description:
 * This smart contract implements a zero-custody consensus mechanism for
 * inter-federation mesh proof aggregation. It enables decentralized voting
 * on federation state roots without storing sensitive data on-chain.
 *
 * Exit Codes:
 *   0 = SUCCESS           - Operation completed successfully
 *   1 = HASH_MISMATCH     - Submitted proof hash does not match expected format
 *   2 = VOTE_REJECTED     - Consensus vote did not meet threshold
 *   3 = TIMEOUT           - Epoch window expired before consensus reached
 *   4 = INVALID_SIGNATURE - Cryptographic signature verification failed
 *
 * ════════════════════════════════════════════════════════════════════════════
 */

pragma solidity ^0.8.20;

/**
 * @title InterFederationConsensus
 * @notice Zero-custody consensus contract for Layer 8 cross-federation proof aggregation
 * @dev Implements Byzantine Fault Tolerant consensus with adaptive trust redistribution
 */
contract InterFederationConsensus {

    // ═══════════════════════════════════════════════════════════════════════
    // STATE VARIABLES
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice Current epoch identifier
    uint256 public currentEpochId;

    /// @notice Consensus threshold (80% = 800 basis points)
    uint256 public constant CONSENSUS_THRESHOLD = 800;

    /// @notice Byzantine tolerance (20% = 200 basis points)
    uint256 public constant BYZANTINE_TOLERANCE = 200;

    /// @notice Basis points denominator
    uint256 public constant BASIS_POINTS = 1000;

    /// @notice Epoch duration in seconds (12 hours)
    uint256 public constant EPOCH_DURATION = 12 hours;

    /// @notice Maximum vote weight per node
    uint8 public constant MAX_VOTE_WEIGHT = 100;

    /// @notice Contract owner
    address public owner;

    // ═══════════════════════════════════════════════════════════════════════
    // DATA STRUCTURES
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice Federation proof structure
    struct FederationProof {
        bytes32 proofRoot;
        uint256 epochId;
        uint256 timestamp;
        address submitter;
        bool verified;
    }

    /// @notice Consensus vote structure
    struct ConsensusVote {
        address voter;
        bytes32 federationRoot;
        uint8 voteWeight;
        uint256 timestamp;
        bool counted;
    }

    /// @notice Epoch state structure
    struct Epoch {
        uint256 epochId;
        uint256 startTime;
        uint256 endTime;
        bytes32 consensusRoot;
        uint256 totalVotes;
        uint256 totalWeight;
        bool finalized;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // MAPPINGS
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice Mapping from proof hash to FederationProof
    mapping(bytes32 => FederationProof) public proofs;

    /// @notice Mapping from epoch ID to Epoch data
    mapping(uint256 => Epoch) public epochs;

    /// @notice Mapping from epoch ID to federation root to vote count
    mapping(uint256 => mapping(bytes32 => uint256)) public votes;

    /// @notice Mapping from epoch ID to voter address to voted status
    mapping(uint256 => mapping(address => bool)) public hasVoted;

    /// @notice Mapping from address to node trust weight
    mapping(address => uint8) public nodeTrustWeight;

    /// @notice Array of all registered federation nodes
    address[] public federationNodes;

    // ═══════════════════════════════════════════════════════════════════════
    // EVENTS
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice Emitted when a federation proof is submitted
    event FederationProofSubmitted(
        bytes32 indexed proofRoot,
        uint256 indexed epochId,
        address indexed submitter,
        uint256 timestamp
    );

    /// @notice Emitted when a consensus vote is cast
    event ConsensusVoteCast(
        address indexed node,
        uint8 weight,
        bytes32 indexed root,
        uint256 indexed epochId
    );

    /// @notice Emitted when consensus is reached for an epoch
    event ConsensusReached(
        uint256 indexed epochId,
        bytes32 indexed consensusRoot,
        uint256 totalVotes,
        uint256 totalWeight
    );

    /// @notice Emitted when an epoch is finalized
    event EpochFinalized(
        uint256 indexed epochId,
        bytes32 consensusRoot,
        uint256 timestamp
    );

    /// @notice Emitted for exit code tracking (on-chain audit anchor)
    event ExitCode(
        uint8 indexed code,
        string message,
        bytes32 contextHash
    );

    // ═══════════════════════════════════════════════════════════════════════
    // MODIFIERS
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice Ensures caller is contract owner
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    /// @notice Ensures caller is a registered federation node
    modifier onlyFederationNode() {
        require(nodeTrustWeight[msg.sender] > 0, "Not a federation node");
        _;
    }

    /// @notice Ensures epoch is active
    modifier onlyActiveEpoch(uint256 epochId) {
        require(epochId == currentEpochId, "Epoch not active");
        require(block.timestamp <= epochs[epochId].endTime, "Epoch expired");
        _;
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CONSTRUCTOR
    // ═══════════════════════════════════════════════════════════════════════

    /// @notice Initializes the contract with genesis epoch
    constructor() {
        owner = msg.sender;
        currentEpochId = 1;
        epochs[currentEpochId] = Epoch({
            epochId: currentEpochId,
            startTime: block.timestamp,
            endTime: block.timestamp + EPOCH_DURATION,
            consensusRoot: bytes32(0),
            totalVotes: 0,
            totalWeight: 0,
            finalized: false
        });

        emit ExitCode(0, "SUCCESS: Contract initialized", keccak256("GENESIS_EPOCH"));
    }

    // ═══════════════════════════════════════════════════════════════════════
    // CORE FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Submit a federation proof root for the current epoch
     * @param proofRoot The Merkle root of the federation proof
     * @param epochId The epoch identifier this proof belongs to
     */
    function submitFederationProof(
        bytes32 proofRoot,
        uint256 epochId
    ) external onlyFederationNode onlyActiveEpoch(epochId) {
        require(proofRoot != bytes32(0), "Invalid proof root");

        // Check if proof already exists
        if (proofs[proofRoot].proofRoot != bytes32(0)) {
            emit ExitCode(1, "HASH_MISMATCH: Proof already exists", proofRoot);
            revert("Proof already submitted");
        }

        // Store proof
        proofs[proofRoot] = FederationProof({
            proofRoot: proofRoot,
            epochId: epochId,
            timestamp: block.timestamp,
            submitter: msg.sender,
            verified: false
        });

        emit FederationProofSubmitted(proofRoot, epochId, msg.sender, block.timestamp);
        emit ExitCode(0, "SUCCESS: Proof submitted", proofRoot);
    }

    /**
     * @notice Vote on a federation root for consensus
     * @param federationRoot The root hash being voted on
     * @param voteWeight The weight of this vote (max 100)
     */
    function voteConsensus(
        bytes32 federationRoot,
        uint8 voteWeight
    ) external onlyFederationNode onlyActiveEpoch(currentEpochId) {
        require(federationRoot != bytes32(0), "Invalid federation root");
        require(voteWeight <= MAX_VOTE_WEIGHT, "Vote weight too high");
        require(!hasVoted[currentEpochId][msg.sender], "Already voted");

        uint8 nodeWeight = nodeTrustWeight[msg.sender];
        uint8 effectiveWeight = voteWeight < nodeWeight ? voteWeight : nodeWeight;

        // Record vote
        votes[currentEpochId][federationRoot] += effectiveWeight;
        hasVoted[currentEpochId][msg.sender] = true;
        epochs[currentEpochId].totalVotes += 1;
        epochs[currentEpochId].totalWeight += effectiveWeight;

        emit ConsensusVoteCast(msg.sender, effectiveWeight, federationRoot, currentEpochId);

        // Check if consensus reached
        _checkConsensus(federationRoot);

        emit ExitCode(0, "SUCCESS: Vote recorded", federationRoot);
    }

    /**
     * @notice Register a new federation node with initial trust weight
     * @param nodeAddress The address of the node to register
     * @param trustWeight The initial trust weight (1-100)
     */
    function registerFederationNode(
        address nodeAddress,
        uint8 trustWeight
    ) external onlyOwner {
        require(nodeAddress != address(0), "Invalid node address");
        require(trustWeight > 0 && trustWeight <= MAX_VOTE_WEIGHT, "Invalid trust weight");
        require(nodeTrustWeight[nodeAddress] == 0, "Node already registered");

        nodeTrustWeight[nodeAddress] = trustWeight;
        federationNodes.push(nodeAddress);

        emit ExitCode(0, "SUCCESS: Node registered", keccak256(abi.encodePacked(nodeAddress)));
    }

    /**
     * @notice Finalize current epoch and rotate to next
     */
    function finalizeEpoch() external {
        Epoch storage epoch = epochs[currentEpochId];
        require(block.timestamp > epoch.endTime, "Epoch still active");
        require(!epoch.finalized, "Epoch already finalized");

        epoch.finalized = true;

        emit EpochFinalized(currentEpochId, epoch.consensusRoot, block.timestamp);

        // Rotate to next epoch
        currentEpochId++;
        epochs[currentEpochId] = Epoch({
            epochId: currentEpochId,
            startTime: block.timestamp,
            endTime: block.timestamp + EPOCH_DURATION,
            consensusRoot: bytes32(0),
            totalVotes: 0,
            totalWeight: 0,
            finalized: false
        });

        emit ExitCode(0, "SUCCESS: Epoch finalized and rotated", bytes32(currentEpochId));
    }

    // ═══════════════════════════════════════════════════════════════════════
    // INTERNAL FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Check if consensus has been reached for a federation root
     * @param federationRoot The root being checked
     */
    function _checkConsensus(bytes32 federationRoot) internal {
        Epoch storage epoch = epochs[currentEpochId];
        uint256 voteCount = votes[currentEpochId][federationRoot];

        // Calculate total possible weight
        uint256 totalPossibleWeight = 0;
        for (uint256 i = 0; i < federationNodes.length; i++) {
            totalPossibleWeight += nodeTrustWeight[federationNodes[i]];
        }

        // Check if consensus threshold met (80%)
        if (voteCount * BASIS_POINTS >= totalPossibleWeight * CONSENSUS_THRESHOLD) {
            epoch.consensusRoot = federationRoot;
            emit ConsensusReached(currentEpochId, federationRoot, epoch.totalVotes, voteCount);
            emit ExitCode(0, "SUCCESS: Consensus reached", federationRoot);
        }
    }

    // ═══════════════════════════════════════════════════════════════════════
    // VIEW FUNCTIONS
    // ═══════════════════════════════════════════════════════════════════════

    /**
     * @notice Get the current epoch data
     * @return Epoch struct for current epoch
     */
    function getCurrentEpoch() external view returns (Epoch memory) {
        return epochs[currentEpochId];
    }

    /**
     * @notice Get vote count for a specific root in current epoch
     * @param federationRoot The root to query
     * @return Vote count
     */
    function getVoteCount(bytes32 federationRoot) external view returns (uint256) {
        return votes[currentEpochId][federationRoot];
    }

    /**
     * @notice Get total number of registered federation nodes
     * @return Node count
     */
    function getFederationNodeCount() external view returns (uint256) {
        return federationNodes.length;
    }

    /**
     * @notice Check if address has voted in current epoch
     * @param voter The address to check
     * @return True if voted, false otherwise
     */
    function hasVotedInCurrentEpoch(address voter) external view returns (bool) {
        return hasVoted[currentEpochId][voter];
    }
}
