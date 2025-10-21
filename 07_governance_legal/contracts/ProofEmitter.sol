// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ProofEmitter
 * @notice Minimal on-chain proof anchoring contract for SSID v5.2
 * @dev Emits digest anchors without storing PII (hash-only, GDPR-compliant)
 *
 * Security Features:
 * - No PII storage (digest hashes only)
 * - Immutable proof timestamps
 * - Event-driven architecture (minimal gas)
 * - Access control for authorized emitters
 * - Replay protection via digest uniqueness
 *
 * Integration: Layer 9 Global Proof Nexus → ProofEmitter.sol
 */

contract ProofEmitter {
    /// @notice Contract version
    string public constant VERSION = "5.2.0";

    /// @notice Contract owner (governance address)
    address public owner;

    /// @notice Authorized emitters mapping
    mapping(address => bool) public authorizedEmitters;

    /// @notice Digest registry (digest hash => anchor timestamp)
    mapping(bytes32 => uint256) public digestRegistry;

    /// @notice Total anchors emitted
    uint256 public totalAnchors;

    /// @notice Proof anchored event
    /// @param digestId Unique digest identifier (HMAC-SHA256)
    /// @param contentHash SHA-512 content hash
    /// @param merkleRoot BLAKE2b merkle root
    /// @param timestamp Unix timestamp
    /// @param emitter Address that anchored the proof
    event ProofAnchored(
        bytes32 indexed digestId,
        bytes32 contentHash,
        bytes32 merkleRoot,
        uint256 timestamp,
        address indexed emitter
    );

    /// @notice Emitter authorization changed
    event EmitterAuthorized(address indexed emitter, bool authorized);

    /// @notice Ownership transferred
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    /// @notice Only owner modifier
    modifier onlyOwner() {
        require(msg.sender == owner, "ProofEmitter: caller is not owner");
        _;
    }

    /// @notice Only authorized emitter modifier
    modifier onlyAuthorizedEmitter() {
        require(authorizedEmitters[msg.sender], "ProofEmitter: caller is not authorized emitter");
        _;
    }

    /**
     * @notice Constructor
     * @param _initialEmitter Initial authorized emitter address
     */
    constructor(address _initialEmitter) {
        owner = msg.sender;
        authorizedEmitters[_initialEmitter] = true;
        emit EmitterAuthorized(_initialEmitter, true);
        emit OwnershipTransferred(address(0), msg.sender);
    }

    /**
     * @notice Anchor proof digest to blockchain
     * @param digestId Unique digest identifier (bytes32)
     * @param contentHash SHA-512 content hash (bytes32, truncated or hashed)
     * @param merkleRoot BLAKE2b merkle root (bytes32)
     * @dev Only authorized emitters can anchor proofs
     * @dev Replay protection: digest can only be anchored once
     */
    function anchorProof(
        bytes32 digestId,
        bytes32 contentHash,
        bytes32 merkleRoot
    ) external onlyAuthorizedEmitter {
        require(digestId != bytes32(0), "ProofEmitter: invalid digest ID");
        require(contentHash != bytes32(0), "ProofEmitter: invalid content hash");
        require(merkleRoot != bytes32(0), "ProofEmitter: invalid merkle root");
        require(digestRegistry[digestId] == 0, "ProofEmitter: digest already anchored");

        uint256 timestamp = block.timestamp;

        // Register digest
        digestRegistry[digestId] = timestamp;
        totalAnchors++;

        // Emit event
        emit ProofAnchored(
            digestId,
            contentHash,
            merkleRoot,
            timestamp,
            msg.sender
        );
    }

    /**
     * @notice Batch anchor multiple proofs (gas optimization)
     * @param digestIds Array of digest IDs
     * @param contentHashes Array of content hashes
     * @param merkleRoots Array of merkle roots
     * @dev Arrays must have same length
     */
    function batchAnchorProofs(
        bytes32[] calldata digestIds,
        bytes32[] calldata contentHashes,
        bytes32[] calldata merkleRoots
    ) external onlyAuthorizedEmitter {
        require(
            digestIds.length == contentHashes.length &&
            contentHashes.length == merkleRoots.length,
            "ProofEmitter: array length mismatch"
        );
        require(digestIds.length > 0, "ProofEmitter: empty arrays");
        require(digestIds.length <= 100, "ProofEmitter: batch too large");

        uint256 timestamp = block.timestamp;

        for (uint256 i = 0; i < digestIds.length; i++) {
            bytes32 digestId = digestIds[i];
            bytes32 contentHash = contentHashes[i];
            bytes32 merkleRoot = merkleRoots[i];

            require(digestId != bytes32(0), "ProofEmitter: invalid digest ID");
            require(contentHash != bytes32(0), "ProofEmitter: invalid content hash");
            require(merkleRoot != bytes32(0), "ProofEmitter: invalid merkle root");
            require(digestRegistry[digestId] == 0, "ProofEmitter: digest already anchored");

            digestRegistry[digestId] = timestamp;
            totalAnchors++;

            emit ProofAnchored(
                digestId,
                contentHash,
                merkleRoot,
                timestamp,
                msg.sender
            );
        }
    }

    /**
     * @notice Verify if digest is anchored
     * @param digestId Digest ID to verify
     * @return timestamp Anchor timestamp (0 if not anchored)
     */
    function verifyDigest(bytes32 digestId) external view returns (uint256) {
        return digestRegistry[digestId];
    }

    /**
     * @notice Check if digest is anchored
     * @param digestId Digest ID to check
     * @return bool True if anchored, false otherwise
     */
    function isDigestAnchored(bytes32 digestId) external view returns (bool) {
        return digestRegistry[digestId] != 0;
    }

    /**
     * @notice Authorize emitter
     * @param emitter Emitter address
     * @param authorized Authorization status
     * @dev Only owner can authorize emitters
     */
    function setEmitterAuthorization(address emitter, bool authorized) external onlyOwner {
        require(emitter != address(0), "ProofEmitter: invalid emitter address");
        authorizedEmitters[emitter] = authorized;
        emit EmitterAuthorized(emitter, authorized);
    }

    /**
     * @notice Transfer ownership
     * @param newOwner New owner address
     * @dev Only owner can transfer ownership
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "ProofEmitter: invalid new owner");
        address previousOwner = owner;
        owner = newOwner;
        emit OwnershipTransferred(previousOwner, newOwner);
    }

    /**
     * @notice Get contract metadata
     * @return version Contract version
     * @return totalAnchored Total anchors count
     * @return ownerAddress Contract owner
     */
    function getMetadata() external view returns (
        string memory version,
        uint256 totalAnchored,
        address ownerAddress
    ) {
        return (VERSION, totalAnchors, owner);
    }
}
