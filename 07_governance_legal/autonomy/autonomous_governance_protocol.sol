// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title AutonomousGovernanceProtocol
 * @notice AI-Assisted Governance for SSID v6.0 Planetary Proof Continuum
 * @dev Enables autonomous policy adjustments based on AI oracle recommendations
 *
 * Features:
 * - AI Oracle integration for policy recommendations
 * - Multi-sig approval for autonomous adjustments
 * - Trust threshold auto-adjustment
 * - Epoch duration optimization
 * - Slashing rate calibration
 * - Emergency override mechanisms
 */

contract AutonomousGovernanceProtocol {
    /// @notice Contract version
    string public constant VERSION = "6.0.0";

    /// @notice Owner address (DAO multi-sig)
    address public owner;

    /// @notice AI Oracle address (authorized ML agent)
    address public aiOracle;

    /// @notice Governance paused state
    bool public paused;

    /// @notice Autonomous mode enabled
    bool public autonomousMode;

    /// @notice Current governance parameters
    struct GovernanceParameters {
        uint256 trustThreshold;      // Minimum trust score (0-1000000)
        uint256 epochDuration;        // Epoch duration in seconds
        uint256 slashingRate;         // Slashing percentage (0-100)
        uint256 minValidators;        // Minimum active validators
        uint256 consensusThreshold;   // Consensus percentage (0-100)
        uint256 lastUpdated;          // Last parameter update timestamp
        string updateReason;          // Reason for last update
    }

    /// @notice Current active parameters
    GovernanceParameters public parameters;

    /// @notice Parameter update history
    GovernanceParameters[] public parameterHistory;

    /// @notice AI recommendation struct
    struct AIRecommendation {
        uint256 trustThreshold;
        uint256 epochDuration;
        uint256 slashingRate;
        uint256 confidenceScore;      // 0-1000000 (0.0 - 1.0)
        string reasoning;
        uint256 timestamp;
        bool executed;
        bool approved;
    }

    /// @notice Pending AI recommendations
    mapping(uint256 => AIRecommendation) public recommendations;

    /// @notice Recommendation counter
    uint256 public recommendationCount;

    /// @notice Multi-sig approvers
    mapping(address => bool) public approvers;

    /// @notice Approver count
    uint256 public approverCount;

    /// @notice Required approvals for autonomous changes
    uint256 public requiredApprovals;

    /// @notice Recommendation approvals
    mapping(uint256 => mapping(address => bool)) public recommendationApprovals;

    /// @notice Recommendation approval counts
    mapping(uint256 => uint256) public approvalCounts;

    /// @notice Events
    event ParametersUpdated(
        uint256 trustThreshold,
        uint256 epochDuration,
        uint256 slashingRate,
        string reason,
        uint256 timestamp
    );

    event AIRecommendationReceived(
        uint256 indexed recommendationId,
        uint256 confidenceScore,
        string reasoning,
        uint256 timestamp
    );

    event PolicyAutoAdjusted(
        uint256 indexed recommendationId,
        uint256 oldTrustThreshold,
        uint256 newTrustThreshold,
        uint256 oldEpochDuration,
        uint256 newEpochDuration,
        uint256 timestamp
    );

    event RecommendationApproved(
        uint256 indexed recommendationId,
        address indexed approver,
        uint256 approvalCount,
        uint256 timestamp
    );

    event AutonomousModeToggled(bool enabled, uint256 timestamp);

    event EmergencyOverride(address indexed by, string reason, uint256 timestamp);

    /// @notice Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "AutonomousGovernance: not owner");
        _;
    }

    modifier onlyAIOracle() {
        require(msg.sender == aiOracle, "AutonomousGovernance: not AI oracle");
        _;
    }

    modifier onlyApprover() {
        require(approvers[msg.sender], "AutonomousGovernance: not approver");
        _;
    }

    modifier whenNotPaused() {
        require(!paused, "AutonomousGovernance: paused");
        _;
    }

    modifier whenAutonomous() {
        require(autonomousMode, "AutonomousGovernance: autonomous mode disabled");
        _;
    }

    /**
     * @notice Constructor
     * @param _aiOracle Address of AI oracle
     * @param _requiredApprovals Number of approvals needed for autonomous changes
     */
    constructor(address _aiOracle, uint256 _requiredApprovals) {
        owner = msg.sender;
        aiOracle = _aiOracle;
        requiredApprovals = _requiredApprovals;
        autonomousMode = false;
        paused = false;

        // Initialize default parameters
        parameters = GovernanceParameters({
            trustThreshold: 750000,      // 0.75
            epochDuration: 7 days,       // 1 week epochs
            slashingRate: 10,            // 10% slashing
            minValidators: 3,
            consensusThreshold: 90,      // 90% consensus
            lastUpdated: block.timestamp,
            updateReason: "Initial deployment"
        });

        // Add owner as first approver
        approvers[msg.sender] = true;
        approverCount = 1;
    }

    /**
     * @notice Submit AI recommendation for parameter adjustment
     * @param _trustThreshold New trust threshold
     * @param _epochDuration New epoch duration
     * @param _slashingRate New slashing rate
     * @param _confidenceScore AI confidence (0-1000000)
     * @param _reasoning Explanation for recommendation
     */
    function submitRecommendation(
        uint256 _trustThreshold,
        uint256 _epochDuration,
        uint256 _slashingRate,
        uint256 _confidenceScore,
        string memory _reasoning
    ) external onlyAIOracle whenNotPaused returns (uint256) {
        require(_trustThreshold <= 1000000, "Invalid trust threshold");
        require(_epochDuration >= 1 days && _epochDuration <= 30 days, "Invalid epoch duration");
        require(_slashingRate <= 100, "Invalid slashing rate");
        require(_confidenceScore <= 1000000, "Invalid confidence score");

        recommendationCount++;

        recommendations[recommendationCount] = AIRecommendation({
            trustThreshold: _trustThreshold,
            epochDuration: _epochDuration,
            slashingRate: _slashingRate,
            confidenceScore: _confidenceScore,
            reasoning: _reasoning,
            timestamp: block.timestamp,
            executed: false,
            approved: false
        });

        emit AIRecommendationReceived(
            recommendationCount,
            _confidenceScore,
            _reasoning,
            block.timestamp
        );

        return recommendationCount;
    }

    /**
     * @notice Approve AI recommendation (multi-sig)
     * @param recommendationId ID of recommendation to approve
     */
    function approveRecommendation(uint256 recommendationId)
        external
        onlyApprover
        whenNotPaused
    {
        require(recommendationId > 0 && recommendationId <= recommendationCount, "Invalid recommendation");
        require(!recommendations[recommendationId].executed, "Already executed");
        require(!recommendationApprovals[recommendationId][msg.sender], "Already approved");

        recommendationApprovals[recommendationId][msg.sender] = true;
        approvalCounts[recommendationId]++;

        emit RecommendationApproved(
            recommendationId,
            msg.sender,
            approvalCounts[recommendationId],
            block.timestamp
        );

        // Auto-execute if enough approvals
        if (approvalCounts[recommendationId] >= requiredApprovals) {
            _executeRecommendation(recommendationId);
        }
    }

    /**
     * @notice Execute approved recommendation
     * @param recommendationId ID of recommendation
     */
    function _executeRecommendation(uint256 recommendationId) internal whenAutonomous {
        AIRecommendation storage rec = recommendations[recommendationId];
        require(!rec.executed, "Already executed");
        require(approvalCounts[recommendationId] >= requiredApprovals, "Insufficient approvals");

        // Store old parameters
        uint256 oldTrustThreshold = parameters.trustThreshold;
        uint256 oldEpochDuration = parameters.epochDuration;

        // Save current parameters to history
        parameterHistory.push(parameters);

        // Update parameters
        parameters.trustThreshold = rec.trustThreshold;
        parameters.epochDuration = rec.epochDuration;
        parameters.slashingRate = rec.slashingRate;
        parameters.lastUpdated = block.timestamp;
        parameters.updateReason = rec.reasoning;

        // Mark as executed
        rec.executed = true;
        rec.approved = true;

        emit PolicyAutoAdjusted(
            recommendationId,
            oldTrustThreshold,
            rec.trustThreshold,
            oldEpochDuration,
            rec.epochDuration,
            block.timestamp
        );

        emit ParametersUpdated(
            rec.trustThreshold,
            rec.epochDuration,
            rec.slashingRate,
            rec.reasoning,
            block.timestamp
        );
    }

    /**
     * @notice Manually update parameters (owner override)
     * @param _trustThreshold New trust threshold
     * @param _epochDuration New epoch duration
     * @param _slashingRate New slashing rate
     * @param _reason Reason for manual update
     */
    function manualUpdate(
        uint256 _trustThreshold,
        uint256 _epochDuration,
        uint256 _slashingRate,
        string memory _reason
    ) external onlyOwner {
        require(_trustThreshold <= 1000000, "Invalid trust threshold");
        require(_epochDuration >= 1 days && _epochDuration <= 30 days, "Invalid epoch duration");
        require(_slashingRate <= 100, "Invalid slashing rate");

        // Save to history
        parameterHistory.push(parameters);

        // Update parameters
        parameters.trustThreshold = _trustThreshold;
        parameters.epochDuration = _epochDuration;
        parameters.slashingRate = _slashingRate;
        parameters.lastUpdated = block.timestamp;
        parameters.updateReason = _reason;

        emit ParametersUpdated(
            _trustThreshold,
            _epochDuration,
            _slashingRate,
            _reason,
            block.timestamp
        );
    }

    /**
     * @notice Toggle autonomous mode
     * @param enabled Enable or disable autonomous adjustments
     */
    function setAutonomousMode(bool enabled) external onlyOwner {
        autonomousMode = enabled;
        emit AutonomousModeToggled(enabled, block.timestamp);
    }

    /**
     * @notice Add multi-sig approver
     * @param approver Address to add as approver
     */
    function addApprover(address approver) external onlyOwner {
        require(approver != address(0), "Invalid address");
        require(!approvers[approver], "Already approver");

        approvers[approver] = true;
        approverCount++;
    }

    /**
     * @notice Remove multi-sig approver
     * @param approver Address to remove
     */
    function removeApprover(address approver) external onlyOwner {
        require(approvers[approver], "Not an approver");
        require(approverCount > requiredApprovals, "Cannot reduce below required");

        approvers[approver] = false;
        approverCount--;
    }

    /**
     * @notice Update required approvals
     * @param newRequired New number of required approvals
     */
    function setRequiredApprovals(uint256 newRequired) external onlyOwner {
        require(newRequired > 0 && newRequired <= approverCount, "Invalid required count");
        requiredApprovals = newRequired;
    }

    /**
     * @notice Update AI oracle address
     * @param newOracle New oracle address
     */
    function setAIOracle(address newOracle) external onlyOwner {
        require(newOracle != address(0), "Invalid address");
        aiOracle = newOracle;
    }

    /**
     * @notice Emergency pause
     */
    function pause() external onlyOwner {
        paused = true;
    }

    /**
     * @notice Unpause
     */
    function unpause() external onlyOwner {
        paused = false;
    }

    /**
     * @notice Emergency override (revert to safe defaults)
     * @param reason Reason for override
     */
    function emergencyOverride(string memory reason) external onlyOwner {
        // Revert to conservative defaults
        parameterHistory.push(parameters);

        parameters.trustThreshold = 900000;  // 0.90 (stricter)
        parameters.epochDuration = 1 days;    // Daily audits (more frequent)
        parameters.slashingRate = 50;        // 50% slashing (harsher)
        parameters.lastUpdated = block.timestamp;
        parameters.updateReason = string(abi.encodePacked("EMERGENCY OVERRIDE: ", reason));

        autonomousMode = false;

        emit EmergencyOverride(msg.sender, reason, block.timestamp);
    }

    /**
     * @notice Get current parameters
     * @return GovernanceParameters struct
     */
    function getCurrentParameters() external view returns (GovernanceParameters memory) {
        return parameters;
    }

    /**
     * @notice Get recommendation details
     * @param recommendationId ID of recommendation
     * @return AIRecommendation struct
     */
    function getRecommendation(uint256 recommendationId)
        external
        view
        returns (AIRecommendation memory)
    {
        return recommendations[recommendationId];
    }

    /**
     * @notice Get parameter history count
     * @return Number of historical parameter sets
     */
    function getHistoryCount() external view returns (uint256) {
        return parameterHistory.length;
    }

    /**
     * @notice Get historical parameters
     * @param index History index
     * @return GovernanceParameters struct
     */
    function getHistoricalParameters(uint256 index)
        external
        view
        returns (GovernanceParameters memory)
    {
        require(index < parameterHistory.length, "Invalid index");
        return parameterHistory[index];
    }

    /**
     * @notice Transfer ownership
     * @param newOwner New owner address
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid new owner");
        owner = newOwner;
    }

    /**
     * @notice Get contract metadata
     */
    function getMetadata() external view returns (
        string memory version,
        bool isPaused,
        bool isAutonomous,
        uint256 currentEpochDuration,
        uint256 currentTrustThreshold
    ) {
        return (
            VERSION,
            paused,
            autonomousMode,
            parameters.epochDuration,
            parameters.trustThreshold
        );
    }
}
