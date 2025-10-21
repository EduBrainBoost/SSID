// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract LicenseSplitter {
    address public dao; address public developer; uint256 public constant DEN = 10000; // basis points
    constructor(address _dao, address _developer) { dao = _dao; developer = _developer; }
    event FeeSplit(address indexed payer, uint256 amount, uint256 daoShare, uint256 devShare);
    function split() external payable {
        require(msg.value > 0, "no_value");
        uint256 daoShare = (msg.value * 2000) / DEN; // 2%
        uint256 devShare = (msg.value * 1000) / DEN; // 1%
        (bool s1,) = dao.call{value: daoShare}(""); require(s1, "dao_fail");
        (bool s2,) = developer.call{value: devShare}(""); require(s2, "dev_fail");
        emit FeeSplit(msg.sender, msg.value, daoShare, devShare);
    }
}
