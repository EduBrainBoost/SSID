#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolidated Health Check Registry
===================================

Single Source of Truth for all shard health check configurations.

This registry consolidates 256 duplicate health.py files into a single
configuration source. Each shard has identical logic across all 16 layers,
only varying by shard name and port number.

Architecture:
- 16 shards (01-16) × 16 layers (07-22) = 256 duplicate files
- Each shard uses port 83XX where XX is shard number
- All reference 03_core health check infrastructure

Generated: 2025-10-17
Author: SSID Core Team
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class ShardHealthConfig:
    """Health check configuration for a single shard"""
    shard_id: str
    shard_name: str
    core_name: str
    port: int
    endpoint: str = "/health"
    timeout: float = 3.0


# Single Source of Truth: All shard health configurations
SHARD_HEALTH_REGISTRY: Dict[str, ShardHealthConfig] = {
    "01_identitaet_personen": ShardHealthConfig(
        shard_id="01",
        shard_name="identitaet_personen",
        core_name="03_core-01_identitaet_personen",
        port=8301
    ),
    "02_dokumente_nachweise": ShardHealthConfig(
        shard_id="02",
        shard_name="dokumente_nachweise",
        core_name="03_core-02_dokumente_nachweise",
        port=8302
    ),
    "03_zugang_berechtigungen": ShardHealthConfig(
        shard_id="03",
        shard_name="zugang_berechtigungen",
        core_name="03_core-03_zugang_berechtigungen",
        port=8303
    ),
    "04_kommunikation_daten": ShardHealthConfig(
        shard_id="04",
        shard_name="kommunikation_daten",
        core_name="03_core-04_kommunikation_daten",
        port=8304
    ),
    "05_gesundheit_medizin": ShardHealthConfig(
        shard_id="05",
        shard_name="gesundheit_medizin",
        core_name="03_core-05_gesundheit_medizin",
        port=8305
    ),
    "06_bildung_qualifikationen": ShardHealthConfig(
        shard_id="06",
        shard_name="bildung_qualifikationen",
        core_name="03_core-06_bildung_qualifikationen",
        port=8306
    ),
    "07_familie_soziales": ShardHealthConfig(
        shard_id="07",
        shard_name="familie_soziales",
        core_name="03_core-07_familie_soziales",
        port=8307
    ),
    "08_mobilitaet_fahrzeuge": ShardHealthConfig(
        shard_id="08",
        shard_name="mobilitaet_fahrzeuge",
        core_name="03_core-08_mobilitaet_fahrzeuge",
        port=8308
    ),
    "09_arbeit_karriere": ShardHealthConfig(
        shard_id="09",
        shard_name="arbeit_karriere",
        core_name="03_core-09_arbeit_karriere",
        port=8309
    ),
    "10_finanzen_banking": ShardHealthConfig(
        shard_id="10",
        shard_name="finanzen_banking",
        core_name="03_core-10_finanzen_banking",
        port=8310
    ),
    "11_versicherungen_risiken": ShardHealthConfig(
        shard_id="11",
        shard_name="versicherungen_risiken",
        core_name="03_core-11_versicherungen_risiken",
        port=8311
    ),
    "12_immobilien_grundstuecke": ShardHealthConfig(
        shard_id="12",
        shard_name="immobilien_grundstuecke",
        core_name="03_core-12_immobilien_grundstuecke",
        port=8312
    ),
    "13_unternehmen_gewerbe": ShardHealthConfig(
        shard_id="13",
        shard_name="unternehmen_gewerbe",
        core_name="03_core-13_unternehmen_gewerbe",
        port=8313
    ),
    "14_vertraege_vereinbarungen": ShardHealthConfig(
        shard_id="14",
        shard_name="vertraege_vereinbarungen",
        core_name="03_core-14_vertraege_vereinbarungen",
        port=8314
    ),
    "15_handel_transaktionen": ShardHealthConfig(
        shard_id="15",
        shard_name="handel_transaktionen",
        core_name="03_core-15_handel_transaktionen",
        port=8315
    ),
    "16_behoerden_verwaltung": ShardHealthConfig(
        shard_id="16",
        shard_name="behoerden_verwaltung",
        core_name="03_core-16_behoerden_verwaltung",
        port=8316
    ),
}


def get_shard_config(shard_name: str) -> ShardHealthConfig:
    """
    Get health check configuration for a shard.

    Args:
        shard_name: Shard identifier (e.g., "01_identitaet_personen")

    Returns:
        ShardHealthConfig for the requested shard

    Raises:
        KeyError: If shard not found in registry
    """
    if shard_name not in SHARD_HEALTH_REGISTRY:
        raise KeyError(f"Shard '{shard_name}' not found in health registry")

    return SHARD_HEALTH_REGISTRY[shard_name]


def get_all_shards() -> List[str]:
    """Get list of all registered shard names"""
    return list(SHARD_HEALTH_REGISTRY.keys())


def get_shard_by_port(port: int) -> ShardHealthConfig:
    """
    Get shard configuration by port number.

    Args:
        port: Port number (e.g., 8301)

    Returns:
        ShardHealthConfig for the shard using that port

    Raises:
        ValueError: If no shard found for that port
    """
    for config in SHARD_HEALTH_REGISTRY.values():
        if config.port == port:
            return config

    raise ValueError(f"No shard found for port {port}")


def validate_registry() -> Tuple[bool, List[str]]:
    """
    Validate registry integrity.

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check for duplicate ports
    ports = [config.port for config in SHARD_HEALTH_REGISTRY.values()]
    if len(ports) != len(set(ports)):
        errors.append("Duplicate port numbers detected")

    # Check port range (should be 8301-8316)
    for config in SHARD_HEALTH_REGISTRY.values():
        if not (8301 <= config.port <= 8316):
            errors.append(f"Port {config.port} out of expected range (8301-8316)")

    # Check shard IDs match port numbers
    for shard_name, config in SHARD_HEALTH_REGISTRY.items():
        expected_port = 8300 + int(config.shard_id)
        if config.port != expected_port:
            errors.append(f"{shard_name}: Port {config.port} != expected {expected_port}")

    return (len(errors) == 0, errors)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    # Self-test
    print("=== Consolidated Health Check Registry ===")
    print(f"Total shards: {len(SHARD_HEALTH_REGISTRY)}")
    print()

    # Validate
    is_valid, errors = validate_registry()
    if is_valid:
        print("OK Registry validation PASSED")
    else:
        print("FAIL Registry validation FAILED:")
        for error in errors:
            print(f"  - {error}")

    print()
    print("=== Registered Shards ===")
    for shard_name, config in SHARD_HEALTH_REGISTRY.items():
        print(f"{config.shard_id}. {shard_name}")
        print(f"   Core: {config.core_name}")
        print(f"   Port: {config.port}")
