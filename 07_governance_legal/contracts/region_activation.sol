// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.8.20;

/**
 * SSID Region Activation Token (RAT)
 * Non-custodial, utility-only. Enables regional feature flags and compliance mappings.
 * No personal data on-chain. Tokens represent capability flags only.
 */
interface IRATCheck {
    function hasRegion(address owner, bytes32 regionCode) external view returns (bool);
}

contract RegionActivation is IRATCheck {
    mapping(address => mapping(bytes32 => bool)) private _regionEnabled;

    event RegionEnabled(address indexed owner, bytes32 indexed regionCode);
    event RegionDisabled(address indexed owner, bytes32 indexed regionCode);

    function enableRegion(bytes32 regionCode) external {
        _regionEnabled[msg.sender][regionCode] = true;
        emit RegionEnabled(msg.sender, regionCode);
    }

    function disableRegion(bytes32 regionCode) external {
        _regionEnabled[msg.sender][regionCode] = false;
        emit RegionDisabled(msg.sender, regionCode);
    }

    function hasRegion(address owner, bytes32 regionCode) external view override returns (bool) {
        return _regionEnabled[owner][regionCode];
    }
}
