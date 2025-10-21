// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract WorkflowProofAnchor {
    event WorkflowProof(bytes32 indexed hash, string tag, uint256 ts);
    function anchor(bytes32 hash, string calldata tag) external { emit WorkflowProof(hash, tag, block.timestamp); }
}
