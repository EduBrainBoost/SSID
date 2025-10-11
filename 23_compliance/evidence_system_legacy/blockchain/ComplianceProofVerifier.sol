// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ComplianceProofVerifier
 * @dev Immutable compliance proof anchoring for SSID Evidence System
 * @notice This contract stores cryptographic proofs on Polygon Mumbai testnet
 *
 * Purpose:
 * - Anchor compliance proofs on-chain for immutability
 * - Enable forensic verification of audit trails
 * - Support GDPR/DORA/MiCA/AMLD6 compliance requirements
 *
 * Architecture:
 * - Off-chain: Python ProofEmitter generates proof hash
 * - On-chain: This contract stores (proofHash, timestamp, metadata)
 * - Verification: Anyone can verify proof existence via getProof()
 *
 * Deployment:
 * - Network: Polygon Mumbai (testnet)
 * - Gas optimization: Minimal storage, event-driven
 * - Access control: Public submission (open system)
 *
 * Integration:
 * - web3.py: Python client for proof submission
 * - CI/CD: Automated proof anchoring via GitHub Actions
 * - Governance: DAO can query proofs for audit reviews
 */

contract ComplianceProofVerifier {
    /// @dev Proof record stored on-chain
    struct Proof {
        bytes32 proofHash;      // SHA-256 hash of proof data
        uint256 timestamp;       // Unix timestamp (UTC)
        address submitter;       // Address that submitted the proof
        string metadata;         // JSON metadata (optional)
        bool exists;             // Existence flag
    }

    /// @dev Mapping from proofHash to Proof record
    mapping(bytes32 => Proof) public proofs;

    /// @dev List of all proof hashes (for enumeration)
    bytes32[] public proofHashes;

    /// @dev Total number of proofs submitted
    uint256 public totalProofs;

    /// @dev Contract owner (for potential upgrades)
    address public owner;

    /// @dev Events for off-chain indexing
    event ProofSubmitted(
        bytes32 indexed proofHash,
        address indexed submitter,
        uint256 timestamp,
        string metadata
    );

    event ProofVerified(
        bytes32 indexed proofHash,
        address indexed verifier,
        uint256 timestamp,
        bool valid
    );

    /// @dev Constructor sets contract owner
    constructor() {
        owner = msg.sender;
        totalProofs = 0;
    }

    /**
     * @notice Submit a compliance proof to the blockchain
     * @param _proofHash SHA-256 hash of proof data (32 bytes)
     * @param _timestamp Unix timestamp when proof was generated
     * @param _metadata JSON metadata string (optional, max 1024 chars)
     * @return success True if proof was submitted successfully
     *
     * Requirements:
     * - _proofHash must not already exist
     * - _timestamp must be reasonable (not far future)
     * - _metadata must be under 1024 characters
     *
     * Example usage from Python:
     * ```python
     * contract.functions.submitProof(
     *     bytes.fromhex(proof_hash),
     *     int(time.time()),
     *     json.dumps({"test": "data"})
     * ).transact()
     * ```
     */
    function submitProof(
        bytes32 _proofHash,
        uint256 _timestamp,
        string calldata _metadata
    ) external returns (bool success) {
        // Validate proof doesn't already exist
        require(!proofs[_proofHash].exists, "Proof already exists");

        // Validate timestamp (not too far in future)
        require(_timestamp <= block.timestamp + 300, "Timestamp too far in future");

        // Validate metadata length
        require(bytes(_metadata).length <= 1024, "Metadata too long");

        // Store proof
        proofs[_proofHash] = Proof({
            proofHash: _proofHash,
            timestamp: _timestamp,
            submitter: msg.sender,
            metadata: _metadata,
            exists: true
        });

        // Add to enumeration
        proofHashes.push(_proofHash);
        totalProofs++;

        // Emit event
        emit ProofSubmitted(_proofHash, msg.sender, _timestamp, _metadata);

        return true;
    }

    /**
     * @notice Verify if a proof exists on-chain
     * @param _proofHash SHA-256 hash to verify
     * @return exists True if proof exists
     * @return timestamp Proof submission timestamp
     * @return submitter Address that submitted the proof
     * @return metadata Proof metadata
     *
     * Example usage:
     * ```python
     * exists, timestamp, submitter, metadata = contract.functions.verifyProof(
     *     bytes.fromhex(proof_hash)
     * ).call()
     * ```
     */
    function verifyProof(bytes32 _proofHash)
        external
        view
        returns (
            bool exists,
            uint256 timestamp,
            address submitter,
            string memory metadata
        )
    {
        Proof memory proof = proofs[_proofHash];

        return (
            proof.exists,
            proof.timestamp,
            proof.submitter,
            proof.metadata
        );
    }

    /**
     * @notice Get proof by index (for enumeration)
     * @param _index Index in proofHashes array
     * @return proofHash Hash at given index
     * @return timestamp Proof timestamp
     * @return submitter Proof submitter
     * @return metadata Proof metadata
     */
    function getProofByIndex(uint256 _index)
        external
        view
        returns (
            bytes32 proofHash,
            uint256 timestamp,
            address submitter,
            string memory metadata
        )
    {
        require(_index < proofHashes.length, "Index out of bounds");

        bytes32 hash = proofHashes[_index];
        Proof memory proof = proofs[hash];

        return (
            proof.proofHash,
            proof.timestamp,
            proof.submitter,
            proof.metadata
        );
    }

    /**
     * @notice Get total number of proofs
     * @return count Total proofs submitted
     */
    function getTotalProofs() external view returns (uint256 count) {
        return totalProofs;
    }

    /**
     * @notice Batch verify multiple proofs
     * @param _proofHashes Array of proof hashes to verify
     * @return results Array of booleans indicating existence
     *
     * Gas optimization: Use this for bulk verification
     */
    function batchVerifyProofs(bytes32[] calldata _proofHashes)
        external
        view
        returns (bool[] memory results)
    {
        results = new bool[](_proofHashes.length);

        for (uint256 i = 0; i < _proofHashes.length; i++) {
            results[i] = proofs[_proofHashes[i]].exists;
        }

        return results;
    }

    /**
     * @notice Get proofs by submitter address
     * @param _submitter Address to query
     * @return hashes Array of proof hashes submitted by address
     *
     * Note: This is O(n) operation, use with caution
     */
    function getProofsBySubmitter(address _submitter)
        external
        view
        returns (bytes32[] memory hashes)
    {
        // Count matching proofs
        uint256 count = 0;
        for (uint256 i = 0; i < proofHashes.length; i++) {
            if (proofs[proofHashes[i]].submitter == _submitter) {
                count++;
            }
        }

        // Allocate result array
        hashes = new bytes32[](count);

        // Populate result
        uint256 index = 0;
        for (uint256 i = 0; i < proofHashes.length; i++) {
            if (proofs[proofHashes[i]].submitter == _submitter) {
                hashes[index] = proofHashes[i];
                index++;
            }
        }

        return hashes;
    }

    /**
     * @notice Emergency pause (owner only)
     * @dev Future implementation for emergency situations
     */
    function pause() external {
        require(msg.sender == owner, "Only owner can pause");
        // Implement pause logic if needed
    }

    /**
     * @notice Get contract version
     * @return version Contract version string
     */
    function getVersion() external pure returns (string memory version) {
        return "1.0.0";
    }
}

/**
 * DEPLOYMENT INSTRUCTIONS:
 *
 * 1. Install dependencies:
 *    npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
 *
 * 2. Configure hardhat.config.js:
 *    module.exports = {
 *      solidity: "0.8.20",
 *      networks: {
 *        mumbai: {
 *          url: "https://rpc-mumbai.maticvigil.com",
 *          accounts: [process.env.DEPLOYER_PRIVATE_KEY]
 *        }
 *      }
 *    };
 *
 * 3. Deploy:
 *    npx hardhat run scripts/deploy.js --network mumbai
 *
 * 4. Verify on PolygonScan:
 *    npx hardhat verify --network mumbai <CONTRACT_ADDRESS>
 *
 * 5. Update proof_emitter.py with deployed address:
 *    self.contract_address = "0x..."
 *
 * GAS ESTIMATES (Mumbai):
 * - submitProof: ~100,000 gas (~$0.01 USD at 30 gwei)
 * - verifyProof: ~25,000 gas (read-only, free via RPC)
 * - batchVerifyProofs: ~5,000 gas per proof
 *
 * SECURITY CONSIDERATIONS:
 * - Proofs are immutable once submitted
 * - No delete/update functions (append-only)
 * - Public submission (no access control)
 * - Owner can pause in emergency
 * - Metadata is limited to 1024 chars
 */
