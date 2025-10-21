// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract MarketplaceRegistry {
    event OfferListed(bytes32 indexed offerHash, address indexed seller, uint256 priceWei);
    event TradeSettled(bytes32 indexed tradeHash, address indexed seller, address indexed buyer, uint256 priceWei);
    mapping(bytes32 => bool) public offers;
    mapping(bytes32 => bool) public trades;
    function _hash(bytes memory data) internal pure returns (bytes32) { return keccak256(data); }
    function listOffer(bytes memory offerJson, address seller, uint256 priceWei) external {
        bytes32 h = _hash(offerJson); require(!offers[h], "offer_exists"); offers[h] = true; emit OfferListed(h, seller, priceWei);
    }
    function settleTrade(bytes memory tradeJson, address seller, address buyer, uint256 priceWei) external {
        bytes32 h = _hash(tradeJson); require(!trades[h], "trade_exists"); trades[h] = true; emit TradeSettled(h, seller, buyer, priceWei);
    }
}
