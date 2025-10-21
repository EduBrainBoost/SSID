// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title FederationAnchor
 * @notice Federation Node Registry and Trust Score Management for SSID v5.4
 * @dev Manages active federation nodes, trust scores, and triggers audit cycles
 *
 * Features:
 * - Node registration with EdDSA public keys
 * - Dynamic trust score updates (0-1000000 scale)
 * - 24-hour audit cycle triggers
 * - Slashing mechanism for malicious behavior
 * - Emergency pause functionality
 */

contract FederationAnchor {
    /// @notice Contract version
    string public constant VERSION = "5.4.0";

    /// @notice Owner address (DAO multi-sig)
    address public owner;

    /// @notice Audit cycle contract address
    address public auditCycleContract;

    /// @notice Contract paused state
    bool public paused;

    /// @notice Total registered nodes
    uint256 public totalNodes;

    /// @notice Total active nodes
    uint256 public activeNodes;

    /// @notice Last audit cycle timestamp
    uint256 public lastAuditCycle;

    /// @notice Audit cycle interval (24 hours)
    uint256 public constant AUDIT_CYCLE_INTERVAL = 24 hours;

    /// @notice Minimum trust score (0.75 * 1000000)
    uint256 public constant MIN_TRUST_SCORE = 750000;

    /// @notice Node information
    struct Node {
        string nodeId;
        string federationId;
        address nodeAddress;
        bytes32 publicKeyHash;  // Hash of EdDSA public key
        uint256 trustScore;     // 0-1000000 (0.000 - 1.000)
        uint256 stakeAmount;
        uint256 registeredAt;
        uint256 lastUpdated;
        bool active;
        bool slashed;
    }

    /// @notice Node registry (nodeId => Node)
    mapping(string => Node) public nodes;

    /// @notice Node ID list
    string[] public nodeIds;

    /// @notice Trust score history (nodeId => timestamp => score)
    mapping(string => mapping(uint256 => uint256)) public trustScoreHistory;

    /// @notice Events
    event NodeRegistered(
        string indexed nodeId,
        string federationId,
        address nodeAddress,
        uint256 stakeAmount,
        uint256 timestamp
    );

    event TrustScoreUpdated(
        string indexed nodeId,
        uint256 oldScore,
        uint256 newScore,
        uint256 timestamp
    );

    event NodeSlashed(
        string indexed nodeId,
        string reason,
        uint256 slashAmount,
        uint256 timestamp
    );

    event AuditCycleTriggered(
        uint256 cycleNumber,
        uint256 timestamp,
        uint256 totalNodes,
        uint256 activeNodes
    );

    event EmergencyPause(address indexed by, uint256 timestamp);
    event EmergencyUnpause(address indexed by, uint256 timestamp);

    /// @notice Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "FederationAnchor: not owner");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "FederationAnchor: contract paused");
        _;
    }

    modifier onlyAuditContract() {
        require(msg.sender == auditCycleContract, "FederationAnchor: not audit contract");
        _;
    }

    /**
     * @notice Constructor
     * @param _auditCycleContract Address of AuditCycle contract
     */
    constructor(address _auditCycleContract) {
        owner = msg.sender;
        auditCycleContract = _auditCycleContract;
        lastAuditCycle = block.timestamp;
        paused = false;
    }

    /**
     * @notice Register a new federation node
     * @param nodeId Unique node identifier
     * @param federationId Federation identifier
     * @param nodeAddress Node operator address
     * @param publicKeyHash Hash of EdDSA public key
     * @param stakeAmount Stake amount in wei
     */
    function registerNode(
        string memory nodeId,
        string memory federationId,
        address nodeAddress,
        bytes32 publicKeyHash,
        uint256 stakeAmount
    ) external onlyOwner whenNotPaused {
        require(bytes(nodeId).length > 0, "FederationAnchor: invalid nodeId");
        require(bytes(federationId).length > 0, "FederationAnchor: invalid federationId");
        require(nodeAddress != address(0), "FederationAnchor: invalid address");
        require(publicKeyHash != bytes32(0), "FederationAnchor: invalid publicKeyHash");
        require(nodes[nodeId].registeredAt == 0, "FederationAnchor: node already registered");

        nodes[nodeId] = Node({
            nodeId: nodeId,
            federationId: federationId,
            nodeAddress: nodeAddress,
            publicKeyHash: publicKeyHash,
            trustScore: 1000000,  // Start with perfect score
            stakeAmount: stakeAmount,
            registeredAt: block.timestamp,
            lastUpdated: block.timestamp,
            active: true,
            slashed: false
        });

        nodeIds.push(nodeId);
        totalNodes++;
        activeNodes++;

        emit NodeRegistered(nodeId, federationId, nodeAddress, stakeAmount, block.timestamp);
    }

    /**
     * @notice Update trust score for a node
     * @param nodeId Node identifier
     * @param newScore New trust score (0-1000000)
     */
    function updateTrustScore(
        string memory nodeId,
        uint256 newScore
    ) external onlyOwner whenNotPaused {
        require(nodes[nodeId].registeredAt > 0, "FederationAnchor: node not found");
        require(newScore <= 1000000, "FederationAnchor: invalid score");

        uint256 oldScore = nodes[nodeId].trustScore;
        nodes[nodeId].trustScore = newScore;
        nodes[nodeId].lastUpdated = block.timestamp;

        // Store in history
        trustScoreHistory[nodeId][block.timestamp] = newScore;

        // Check if node should be deactivated
        if (newScore < MIN_TRUST_SCORE && nodes[nodeId].active) {
            nodes[nodeId].active = false;
            activeNodes--;
        }

        emit TrustScoreUpdated(nodeId, oldScore, newScore, block.timestamp);
    }

    /**
     * @notice Batch update trust scores
     * @param nodeIdList Array of node IDs
     * @param scores Array of new scores
     */
    function batchUpdateTrustScores(
        string[] memory nodeIdList,
        uint256[] memory scores
    ) external onlyOwner whenNotPaused {
        require(nodeIdList.length == scores.length, "FederationAnchor: length mismatch");
        require(nodeIdList.length > 0, "FederationAnchor: empty array");

        for (uint256 i = 0; i < nodeIdList.length; i++) {
            if (nodes[nodeIdList[i]].registeredAt > 0) {
                uint256 oldScore = nodes[nodeIdList[i]].trustScore;
                nodes[nodeIdList[i]].trustScore = scores[i];
                nodes[nodeIdList[i]].lastUpdated = block.timestamp;

                trustScoreHistory[nodeIdList[i]][block.timestamp] = scores[i];

                emit TrustScoreUpdated(nodeIdList[i], oldScore, scores[i], block.timestamp);
            }
        }
    }

    /**
     * @notice Slash a malicious node
     * @param nodeId Node identifier
     * @param reason Reason for slashing
     * @param slashPercentage Percentage to slash (0-100)
     */
    function slashNode(
        string memory nodeId,
        string memory reason,
        uint256 slashPercentage
    ) external onlyOwner {
        require(nodes[nodeId].registeredAt > 0, "FederationAnchor: node not found");
        require(!nodes[nodeId].slashed, "FederationAnchor: already slashed");
        require(slashPercentage <= 100, "FederationAnchor: invalid percentage");

        uint256 slashAmount = (nodes[nodeId].stakeAmount * slashPercentage) / 100;

        nodes[nodeId].slashed = true;
        nodes[nodeId].active = false;
        nodes[nodeId].stakeAmount -= slashAmount;
        nodes[nodeId].trustScore = 0;

        if (activeNodes > 0) {
            activeNodes--;
        }

        emit NodeSlashed(nodeId, reason, slashAmount, block.timestamp);
    }

    /**
     * @notice Trigger audit cycle (called every 24 hours)
     */
    function triggerAuditCycle() external whenNotPaused {
        require(
            block.timestamp >= lastAuditCycle + AUDIT_CYCLE_INTERVAL,
            "FederationAnchor: audit cycle not due"
        );

        uint256 cycleNumber = (block.timestamp - lastAuditCycle) / AUDIT_CYCLE_INTERVAL;
        lastAuditCycle = block.timestamp;

        emit AuditCycleTriggered(cycleNumber, block.timestamp, totalNodes, activeNodes);

        // Call audit cycle contract if set
        if (auditCycleContract != address(0)) {
            // Interface call to AuditCycle.sol
            // IAuditCycle(auditCycleContract).recordAuditCycle(cycleNumber);
        }
    }

    /**
     * @notice Get node information
     * @param nodeId Node identifier
     * @return Node struct
     */
    function getNode(string memory nodeId) external view returns (Node memory) {
        require(nodes[nodeId].registeredAt > 0, "FederationAnchor: node not found");
        return nodes[nodeId];
    }

    /**
     * @notice Get trust score history
     * @param nodeId Node identifier
     * @param timestamp Timestamp to query
     * @return Trust score at timestamp
     */
    function getTrustScoreAtTime(
        string memory nodeId,
        uint256 timestamp
    ) external view returns (uint256) {
        return trustScoreHistory[nodeId][timestamp];
    }

    /**
     * @notice Get all active nodes
     * @return Array of active node IDs
     */
    function getActiveNodes() external view returns (string[] memory) {
        string[] memory active = new string[](activeNodes);
        uint256 index = 0;

        for (uint256 i = 0; i < nodeIds.length; i++) {
            if (nodes[nodeIds[i]].active && !nodes[nodeIds[i]].slashed) {
                active[index] = nodeIds[i];
                index++;
            }
        }

        return active;
    }

    /**
     * @notice Emergency pause
     */
    function pause() external onlyOwner {
        paused = true;
        emit EmergencyPause(msg.sender, block.timestamp);
    }

    /**
     * @notice Emergency unpause
     */
    function unpause() external onlyOwner {
        paused = false;
        emit EmergencyUnpause(msg.sender, block.timestamp);
    }

    /**
     * @notice Update audit cycle contract address
     * @param _auditCycleContract New audit cycle contract address
     */
    function setAuditCycleContract(address _auditCycleContract) external onlyOwner {
        require(_auditCycleContract != address(0), "FederationAnchor: invalid address");
        auditCycleContract = _auditCycleContract;
    }

    /**
     * @notice Transfer ownership
     * @param newOwner New owner address
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "FederationAnchor: invalid new owner");
        owner = newOwner;
    }

    /**
     * @notice Get contract metadata
     */
    function getMetadata() external view returns (
        string memory version,
        uint256 totalNodesCount,
        uint256 activeNodesCount,
        uint256 lastAudit,
        bool isPaused
    ) {
        return (VERSION, totalNodes, activeNodes, lastAuditCycle, paused);
    }
}
