// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract MarketDAOVote {
    event ProposalCreated(uint256 id, string title);
    event Voted(uint256 id, address voter, bool support, uint256 weight);
    event Finalized(uint256 id, bool passed);
    struct Proposal { string title; uint256 yes; uint256 no; uint256 deadline; bool finalized; }
    mapping(uint256 => Proposal) public proposals; uint256 public nextId;
    function create(string calldata title, uint256 votingPeriod) external returns (uint256) {
        uint256 id = nextId++; proposals[id] = Proposal(title,0,0,block.timestamp+votingPeriod,false); emit ProposalCreated(id, title); return id;
    }
    function vote(uint256 id, bool support, uint256 weight) external {
        Proposal storage p = proposals[id]; require(block.timestamp < p.deadline, "ended");
        if (support) p.yes += weight; else p.no += weight; emit Voted(id, msg.sender, support, weight);
    }
    function finalize(uint256 id) external {
        Proposal storage p = proposals[id]; require(block.timestamp >= p.deadline && !p.finalized, "not_ready");
        p.finalized = true; bool passed = p.yes > p.no; emit Finalized(id, passed);
    }
}
