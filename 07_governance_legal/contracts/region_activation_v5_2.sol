// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title SSID Region Activation Token (RAT) v5.2
 * @notice ROOT-24-LOCK compliant | SAFE-FIX enforced
 * @dev Extends RAT framework with expiry timestamps and tier binding
 *
 * Key Features:
 * - Region activation with expiry timestamps
 * - Tier-based region eligibility enforcement
 * - Immutable vs. mutable region distinction
 * - Multi-region bundle support
 * - On-chain proof generation for OPA validation
 */

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

contract RegionActivationToken is AccessControl, ReentrancyGuard, Pausable {

    // ============ Constants & Roles ============

    bytes32 public constant ACTIVATOR_ROLE = keccak256("ACTIVATOR_ROLE");
    bytes32 public constant AUDITOR_ROLE = keccak256("AUDITOR_ROLE");

    uint256 public constant EXPIRY_24H = 24 hours;
    uint256 public constant EXPIRY_30D = 30 days;
    uint256 public constant EXPIRY_1Y = 365 days;

    // ============ Enums ============

    enum TierLevel { S1, S2, S3, E2, E3, E5, E6 }

    enum RegionCode {
        DACH,       // Germany, Austria, Switzerland
        EN_EU,      // Ireland, Netherlands, Malta
        UK,         // United Kingdom
        US_CAN,     // United States & Canada
        LATAM,      // Latin America
        APAC_EN,    // Singapore, Australia, New Zealand
        APAC_EXT,   // Japan, Korea, SEA
        MENA,       // Middle East & North Africa
        AFRICA_EN,  // South Africa, Nigeria, Kenya
        SOVEREIGN,  // China, Russia, India
        GLOBAL      // Multi-region bundle
    }

    // ============ Structs ============

    struct RATToken {
        RegionCode region;
        uint256 expiryTimestamp;
        uint256 proofTimestamp;
        bytes32 blockchainProof;
        bool immutable_;
        bool active;
        TierLevel tierBinding;
    }

    struct Subscription {
        address owner;
        TierLevel tier;
        bool tierVerified;
        bool gdprCompliant;
        uint256 subscriptionStart;
        uint256 subscriptionEnd;
        bool perpetualLicense;
    }

    // ============ State Variables ============

    // Mapping: user address => region => RAT token
    mapping(address => mapping(RegionCode => RATToken)) public ratTokens;

    // Mapping: user address => subscription details
    mapping(address => Subscription) public subscriptions;

    // Mapping: region => minimum tier requirement
    mapping(RegionCode => TierLevel) public regionMinTiers;

    // Counter for total activations (audit trail)
    uint256 public totalActivations;

    // ============ Events ============

    event RegionActivated(
        address indexed user,
        RegionCode indexed region,
        TierLevel tier,
        uint256 expiryTimestamp,
        bytes32 proofHash
    );

    event RegionDeactivated(
        address indexed user,
        RegionCode indexed region,
        string reason
    );

    event RegionExpired(
        address indexed user,
        RegionCode indexed region,
        uint256 expiryTimestamp
    );

    event SubscriptionCreated(
        address indexed user,
        TierLevel tier,
        uint256 subscriptionEnd
    );

    event TierUpgraded(
        address indexed user,
        TierLevel oldTier,
        TierLevel newTier
    );

    // ============ Constructor ============

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ACTIVATOR_ROLE, msg.sender);
        _grantRole(AUDITOR_ROLE, msg.sender);

        // Initialize region minimum tiers
        regionMinTiers[RegionCode.DACH] = TierLevel.S1;
        regionMinTiers[RegionCode.EN_EU] = TierLevel.S1;
        regionMinTiers[RegionCode.UK] = TierLevel.S2;
        regionMinTiers[RegionCode.US_CAN] = TierLevel.S2;
        regionMinTiers[RegionCode.LATAM] = TierLevel.S2;
        regionMinTiers[RegionCode.APAC_EN] = TierLevel.S3;
        regionMinTiers[RegionCode.APAC_EXT] = TierLevel.E2;
        regionMinTiers[RegionCode.MENA] = TierLevel.E2;
        regionMinTiers[RegionCode.AFRICA_EN] = TierLevel.E3;
        regionMinTiers[RegionCode.SOVEREIGN] = TierLevel.E5;
        regionMinTiers[RegionCode.GLOBAL] = TierLevel.E3;
    }

    // ============ Modifiers ============

    modifier onlySubscribed() {
        require(subscriptions[msg.sender].owner == msg.sender, "No active subscription");
        require(subscriptions[msg.sender].tierVerified, "Tier not verified");
        _;
    }

    modifier validRegion(RegionCode region) {
        require(uint8(region) <= uint8(RegionCode.GLOBAL), "Invalid region");
        _;
    }

    // ============ Subscription Management ============

    /**
     * @notice Create new subscription for user
     * @param user User address
     * @param tier Subscription tier
     * @param durationDays Subscription duration in days (0 for perpetual)
     */
    function createSubscription(
        address user,
        TierLevel tier,
        uint256 durationDays
    ) external onlyRole(ACTIVATOR_ROLE) {
        require(user != address(0), "Invalid user address");

        uint256 subscriptionEnd = durationDays == 0
            ? type(uint256).max
            : block.timestamp + (durationDays * 1 days);

        subscriptions[user] = Subscription({
            owner: user,
            tier: tier,
            tierVerified: true,
            gdprCompliant: false,  // Must be set separately
            subscriptionStart: block.timestamp,
            subscriptionEnd: subscriptionEnd,
            perpetualLicense: durationDays == 0
        });

        emit SubscriptionCreated(user, tier, subscriptionEnd);
    }

    /**
     * @notice Upgrade user tier
     * @param user User address
     * @param newTier New tier level
     */
    function upgradeTier(address user, TierLevel newTier)
        external
        onlyRole(ACTIVATOR_ROLE)
    {
        require(subscriptions[user].owner == user, "No subscription");
        require(newTier > subscriptions[user].tier, "Cannot downgrade");

        TierLevel oldTier = subscriptions[user].tier;
        subscriptions[user].tier = newTier;

        emit TierUpgraded(user, oldTier, newTier);
    }

    // ============ Region Activation ============

    /**
     * @notice Activate region for user
     * @param user User address
     * @param region Region to activate
     * @param expiryDays Days until expiry (0 for subscription-based)
     * @param immutable_ Whether region activation is immutable (longer proof validity)
     */
    function activateRegion(
        address user,
        RegionCode region,
        uint256 expiryDays,
        bool immutable_
    ) external onlyRole(ACTIVATOR_ROLE) nonReentrant validRegion(region) {
        Subscription memory sub = subscriptions[user];
        require(sub.owner == user, "No subscription");
        require(sub.tierVerified, "Tier not verified");

        // Check tier eligibility
        require(
            sub.tier >= regionMinTiers[region],
            "Tier insufficient for region"
        );

        // Calculate expiry
        uint256 expiry = expiryDays == 0
            ? sub.subscriptionEnd
            : block.timestamp + (expiryDays * 1 days);

        // Generate blockchain proof
        bytes32 proof = keccak256(abi.encodePacked(
            user,
            region,
            sub.tier,
            block.timestamp,
            block.number
        ));

        // Store RAT token
        ratTokens[user][region] = RATToken({
            region: region,
            expiryTimestamp: expiry,
            proofTimestamp: block.timestamp,
            blockchainProof: proof,
            immutable_: immutable_,
            active: true,
            tierBinding: sub.tier
        });

        totalActivations++;

        emit RegionActivated(user, region, sub.tier, expiry, proof);
    }

    /**
     * @notice Deactivate region for user
     * @param user User address
     * @param region Region to deactivate
     * @param reason Deactivation reason
     */
    function deactivateRegion(
        address user,
        RegionCode region,
        string calldata reason
    ) external onlyRole(ACTIVATOR_ROLE) validRegion(region) {
        require(ratTokens[user][region].active, "Region not active");

        ratTokens[user][region].active = false;

        emit RegionDeactivated(user, region, reason);
    }

    // ============ Validation & Queries ============

    /**
     * @notice Check if region is active and valid for user
     * @param user User address
     * @param region Region to check
     * @return isValid Whether region is valid
     * @return token RAT token details
     */
    function isRegionValid(address user, RegionCode region)
        external
        view
        validRegion(region)
        returns (bool isValid, RATToken memory token)
    {
        token = ratTokens[user][region];

        if (!token.active) {
            return (false, token);
        }

        if (block.timestamp > token.expiryTimestamp) {
            return (false, token);
        }

        // Check tier binding (user tier must still meet region requirement)
        Subscription memory sub = subscriptions[user];
        if (sub.tier < regionMinTiers[region]) {
            return (false, token);
        }

        return (true, token);
    }

    /**
     * @notice Get all active regions for user
     * @param user User address
     * @return regions Array of active region codes
     */
    function getActiveRegions(address user)
        external
        view
        returns (RegionCode[] memory regions)
    {
        uint256 count = 0;

        // Count active regions
        for (uint8 i = 0; i <= uint8(RegionCode.GLOBAL); i++) {
            RegionCode region = RegionCode(i);
            if (ratTokens[user][region].active && block.timestamp <= ratTokens[user][region].expiryTimestamp) {
                count++;
            }
        }

        // Build array
        regions = new RegionCode[](count);
        uint256 index = 0;
        for (uint8 i = 0; i <= uint8(RegionCode.GLOBAL); i++) {
            RegionCode region = RegionCode(i);
            if (ratTokens[user][region].active && block.timestamp <= ratTokens[user][region].expiryTimestamp) {
                regions[index] = region;
                index++;
            }
        }

        return regions;
    }

    /**
     * @notice Get blockchain proof for region (for OPA validation)
     * @param user User address
     * @param region Region code
     * @return proof Blockchain proof hash
     * @return proofTimestamp Timestamp of proof generation
     * @return immutable_ Whether proof is immutable
     */
    function getBlockchainProof(address user, RegionCode region)
        external
        view
        validRegion(region)
        returns (bytes32 proof, uint256 proofTimestamp, bool immutable_)
    {
        RATToken memory token = ratTokens[user][region];
        return (token.blockchainProof, token.proofTimestamp, token.immutable_);
    }

    // ============ Admin Functions ============

    /**
     * @notice Update minimum tier for region (emergency only)
     * @param region Region code
     * @param minTier New minimum tier
     */
    function updateRegionMinTier(RegionCode region, TierLevel minTier)
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
        validRegion(region)
    {
        regionMinTiers[region] = minTier;
    }

    /**
     * @notice Pause contract (emergency)
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    /**
     * @notice Unpause contract
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    // ============ Audit Trail ============

    /**
     * @notice Get audit data for region activation
     * @param user User address
     * @param region Region code
     * @return Audit data in JSON-compatible format
     */
    function getAuditData(address user, RegionCode region)
        external
        view
        validRegion(region)
        onlyRole(AUDITOR_ROLE)
        returns (
            address owner,
            TierLevel tier,
            uint256 activationTimestamp,
            uint256 expiryTimestamp,
            bytes32 proof,
            bool active,
            bool immutable_
        )
    {
        RATToken memory token = ratTokens[user][region];
        Subscription memory sub = subscriptions[user];

        return (
            user,
            sub.tier,
            token.proofTimestamp,
            token.expiryTimestamp,
            token.blockchainProof,
            token.active,
            token.immutable_
        );
    }
}
