// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.21;

/**
 * SSID Proof Credit Anchor (Hash-only, Non-Custodial)
 * - Anchors Merkle roots for federation batches.
 * - No funds accepted, no balances stored, no custody.
 */
contract ProofCreditAnchor {
    event RootAnchored(
        bytes32 indexed merkleRoot,
        string  indexed federationZone,
        string  batchId,
        uint256 timestamp,
        string  metadataUri // optional off-chain evidence pointer (e.g., IPFS hash of audit pairs)
    );

    function anchorRoot(bytes32 merkleRoot, string calldata federationZone, string calldata batchId, string calldata metadataUri) external {
        // No value transfers, no storage of amounts -> MiCA/PSD neutrality
        emit RootAnchored(merkleRoot, federationZone, batchId, block.timestamp, metadataUri);
    }
}
