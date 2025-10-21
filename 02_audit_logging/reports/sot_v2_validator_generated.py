"""
Generated SOT-V2 Validator Methods
===================================
Auto-generated from sot_contract_v2.yaml
Date: 2025-10-20T21:50:49.090402

Usage:
    Replace validate_sot_v2() method in sot_validator_core.py
    Add _validate_field() helper method
"""

from pathlib import Path
import yaml
from typing import Dict, Any


# Helper Method

    def _validate_field(self, field_path: str, rule_id: str, category: str = "GENERAL") -> ValidationResult:
        """
        Helper method to validate field existence in contract YAML.

        Args:
            field_path: Dot-separated path (e.g., "business_model.data_custody")
            rule_id: Rule ID (e.g., "SOT-V2-0002")
            category: Rule category (GENERAL, COMPLIANCE, etc.)

        Returns:
            ValidationResult with field validation status
        """
        # Locate contract YAML files
        contract_files = list(self.repo_root.rglob("**/contracts/**/*.{yaml,yml}"))

        if not contract_files:
            return ValidationResult(
                rule_id=rule_id,
                passed=False,
                severity=self._get_severity(category),
                message=f"{rule_id}: No contract files found in repository",
                evidence={"error": "No contract files", "field_path": field_path}
            )

        # Use first contract file found (or implement multi-contract logic)
        contract_path = contract_files[0]

        try:
            with open(contract_path, 'r', encoding='utf-8') as f:
                contract = yaml.safe_load(f)
        except Exception as e:
            return ValidationResult(
                rule_id=rule_id,
                passed=False,
                severity=self._get_severity(category),
                message=f"{rule_id}: Failed to load contract YAML: {e}",
                evidence={"error": str(e), "file": str(contract_path)}
            )

        # Navigate to field using dot-separated path
        parts = field_path.split('.')
        current = contract

        for i, part in enumerate(parts):
            if not isinstance(current, dict):
                return ValidationResult(
                    rule_id=rule_id,
                    passed=False,
                    severity=self._get_severity(category),
                    message=f"{rule_id}: Path '{'.'.join(parts[:i])}' is not a dict",
                    evidence={
                        "field_path": field_path,
                        "failed_at": '.'.join(parts[:i]),
                        "type": str(type(current))
                    }
                )

            if part not in current:
                return ValidationResult(
                    rule_id=rule_id,
                    passed=False,
                    severity=self._get_severity(category),
                    message=f"{rule_id}: Missing required field '{field_path}'",
                    evidence={
                        "field_path": field_path,
                        "missing_field": part,
                        "available_fields": list(current.keys()) if isinstance(current, dict) else []
                    }
                )

            current = current[part]

        # Field exists!
        return ValidationResult(
            rule_id=rule_id,
            passed=True,
            severity=self._get_severity(category),
            message=f"{rule_id}: Field '{field_path}' exists",
            evidence={
                "field_path": field_path,
                "value_type": str(type(current)),
                "contract_file": str(contract_path)
            }
        )

    def _get_severity(self, category: str) -> Severity:
        """Map category to severity."""
        severity_map = {
            "COMPLIANCE": Severity.HIGH,
            "GOVERNANCE": Severity.HIGH,
            "ECONOMICS": Severity.HIGH,
            "GENERAL": Severity.MEDIUM,
            "METADATA": Severity.INFO,
        }
        return severity_map.get(category, Severity.MEDIUM)


# Main Validator Method

    def validate_sot_v2(self, num: int) -> ValidationResult:
        """
        SOT-V2-0001 to SOT-V2-0189: Contract validation rules.

        Now with SPECIFIC field validation instead of generic file checks!

        Args:
            num: Rule number (1-189)

        Returns:
            ValidationResult with specific field validation
        """
        # Map rule numbers to field paths
        field_map = {
            1: ("business_model", "GENERAL"),
            2: ("business_model.data_custody", "GENERAL"),
            3: ("business_model.kyc_responsibility", "GENERAL"),
            4: ("business_model.not_role", "GENERAL"),
            5: ("business_model.role", "GENERAL"),
            6: ("business_model.user_interactions", "GENERAL"),
            7: ("classification", "METADATA"),
            8: ("compliance_utilities", "COMPLIANCE"),
            9: ("compliance_utilities.audit_payments", "COMPLIANCE"),
            10: ("compliance_utilities.legal_attestations", "COMPLIANCE"),
            11: ("compliance_utilities.regulatory_reporting", "COMPLIANCE"),
            12: ("date", "METADATA"),
            13: ("deprecated", "METADATA"),
            14: ("fee_routing", "ECONOMICS"),
            15: ("fee_routing.system_fees", "ECONOMICS"),
            16: ("fee_routing.system_fees.allocation", "ECONOMICS"),
            17: ("fee_routing.system_fees.allocation.dev_fee", "ECONOMICS"),
            18: ("fee_routing.system_fees.allocation.system_treasury", "ECONOMICS"),
            19: ("fee_routing.system_fees.burn_from_system_fee", "ECONOMICS"),
            20: ("fee_routing.system_fees.burn_from_system_fee.base", "ECONOMICS"),
            21: ("fee_routing.system_fees.burn_from_system_fee.daily_cap_percent_of_circ", "ECONOMICS"),
            22: ("fee_routing.system_fees.burn_from_system_fee.monthly_cap_percent_of_circ", "ECONOMICS"),
            23: ("fee_routing.system_fees.burn_from_system_fee.oracle_source", "ECONOMICS"),
            24: ("fee_routing.system_fees.burn_from_system_fee.policy", "ECONOMICS"),
            25: ("fee_routing.system_fees.burn_from_system_fee.snapshot_time_utc", "ECONOMICS"),
            26: ("fee_routing.system_fees.note", "ECONOMICS"),
            27: ("fee_routing.system_fees.scope", "ECONOMICS"),
            28: ("fee_routing.system_fees.total_fee", "ECONOMICS"),
            29: ("fee_routing.validator_rewards", "ECONOMICS"),
            30: ("fee_routing.validator_rewards.no_per_transaction_split", "ECONOMICS"),
            31: ("fee_routing.validator_rewards.note", "ECONOMICS"),
            32: ("fee_routing.validator_rewards.source", "ECONOMICS"),
            33: ("fee_structure", "ECONOMICS"),
            34: ("fee_structure.allocation", "ECONOMICS"),
            35: ("fee_structure.burn_from_system_fee", "ECONOMICS"),
            36: ("fee_structure.fee_collection", "ECONOMICS"),
            37: ("fee_structure.no_manual_intervention", "ECONOMICS"),
            38: ("fee_structure.scope", "ECONOMICS"),
            39: ("fee_structure.total_fee", "ECONOMICS"),
            40: ("governance_controls", "GOVERNANCE"),
            41: ("governance_controls.authority", "GOVERNANCE"),
            42: ("governance_controls.note", "GOVERNANCE"),
            43: ("governance_controls.reference", "GOVERNANCE"),
            44: ("governance_fees", "GOVERNANCE"),
            45: ("governance_fees.proposal_deposits", "GOVERNANCE"),
            46: ("governance_fees.voting_gas", "GOVERNANCE"),
            47: ("governance_framework", "GOVERNANCE"),
            48: ("governance_framework.dao_ready", "GOVERNANCE"),
            49: ("governance_framework.emergency_procedures", "GOVERNANCE"),
            50: ("governance_framework.proposal_system", "GOVERNANCE"),
            51: ("governance_framework.reference", "GOVERNANCE"),
            52: ("governance_framework.upgrade_authority", "GOVERNANCE"),
            53: ("governance_framework.voting_mechanism", "GOVERNANCE"),
            54: ("governance_parameters", "GOVERNANCE"),
            55: ("governance_parameters.delegation_system", "GOVERNANCE"),
            56: ("governance_parameters.delegation_system.delegation_changes", "GOVERNANCE"),
            57: ("governance_parameters.delegation_system.delegation_enabled", "GOVERNANCE"),
            58: ("governance_parameters.delegation_system.self_delegation_default", "GOVERNANCE"),
            59: ("governance_parameters.delegation_system.vote_weight_calculation", "GOVERNANCE"),
            60: ("governance_parameters.governance_rewards", "GOVERNANCE"),
            61: ("governance_parameters.governance_rewards.delegate_rewards", "GOVERNANCE"),
            62: ("governance_parameters.governance_rewards.minimum_participation", "GOVERNANCE"),
            63: ("governance_parameters.governance_rewards.proposal_creator_rewards", "GOVERNANCE"),
            64: ("governance_parameters.governance_rewards.voter_participation_rewards", "GOVERNANCE"),
            65: ("governance_parameters.proposal_framework", "GOVERNANCE"),
            66: ("governance_parameters.proposal_framework.proposal_deposit", "GOVERNANCE"),
            67: ("governance_parameters.proposal_framework.proposal_threshold", "GOVERNANCE"),
            68: ("governance_parameters.proposal_framework.proposal_types", "GOVERNANCE"),
            69: ("governance_parameters.proposal_framework.proposal_types", "GOVERNANCE"),
            70: ("governance_parameters.proposal_framework.proposal_types", "GOVERNANCE"),
            71: ("governance_parameters.proposal_framework.proposal_types", "GOVERNANCE"),
            72: ("governance_parameters.proposal_framework.proposal_types", "GOVERNANCE"),
            73: ("governance_parameters.timelock_framework", "GOVERNANCE"),
            74: ("governance_parameters.timelock_framework.emergency_proposals", "GOVERNANCE"),
            75: ("governance_parameters.timelock_framework.parameter_changes", "GOVERNANCE"),
            76: ("governance_parameters.timelock_framework.protocol_upgrades", "GOVERNANCE"),
            77: ("governance_parameters.timelock_framework.standard_proposals", "GOVERNANCE"),
            78: ("governance_parameters.timelock_framework.treasury_allocations", "GOVERNANCE"),
            79: ("governance_parameters.voting_periods", "GOVERNANCE"),
            80: ("governance_parameters.voting_periods.emergency_voting", "GOVERNANCE"),
            81: ("governance_parameters.voting_periods.parameter_voting", "GOVERNANCE"),
            82: ("governance_parameters.voting_periods.protocol_upgrade_voting", "GOVERNANCE"),
            83: ("governance_parameters.voting_periods.standard_voting", "GOVERNANCE"),
            84: ("governance_parameters.voting_requirements", "GOVERNANCE"),
            85: ("governance_parameters.voting_requirements.emergency_supermajority", "GOVERNANCE"),
            86: ("governance_parameters.voting_requirements.quorum_emergency", "GOVERNANCE"),
            87: ("governance_parameters.voting_requirements.quorum_protocol_upgrade", "GOVERNANCE"),
            88: ("governance_parameters.voting_requirements.quorum_standard", "GOVERNANCE"),
            89: ("governance_parameters.voting_requirements.simple_majority", "GOVERNANCE"),
            90: ("governance_parameters.voting_requirements.supermajority", "GOVERNANCE"),
            95: ("jurisdictional_compliance", "COMPLIANCE"),
            96: ("jurisdictional_compliance.blacklist_jurisdictions", "COMPLIANCE"),
            97: ("jurisdictional_compliance.blacklist_jurisdictions", "COMPLIANCE"),
            98: ("jurisdictional_compliance.blacklist_jurisdictions", "COMPLIANCE"),
            99: ("jurisdictional_compliance.blacklist_jurisdictions", "COMPLIANCE"),
            100: ("jurisdictional_compliance.blacklist_jurisdictions", "COMPLIANCE"),
            101: ("jurisdictional_compliance.compliance_basis", "COMPLIANCE"),
            102: ("jurisdictional_compliance.excluded_entities", "COMPLIANCE"),
            103: ("jurisdictional_compliance.excluded_entities", "COMPLIANCE"),
            104: ("jurisdictional_compliance.excluded_entities", "COMPLIANCE"),
            105: ("jurisdictional_compliance.excluded_entities", "COMPLIANCE"),
            106: ("jurisdictional_compliance.excluded_markets", "COMPLIANCE"),
            107: ("jurisdictional_compliance.excluded_markets", "COMPLIANCE"),
            108: ("jurisdictional_compliance.excluded_markets", "COMPLIANCE"),
            109: ("jurisdictional_compliance.excluded_markets", "COMPLIANCE"),
            110: ("jurisdictional_compliance.reference", "COMPLIANCE"),
            111: ("jurisdictional_compliance.regulatory_exemptions", "COMPLIANCE"),
            112: ("legal_safe_harbor", "COMPLIANCE"),
            113: ("legal_safe_harbor.admin_controls", "COMPLIANCE"),
            114: ("legal_safe_harbor.e_money_token", "COMPLIANCE"),
            115: ("legal_safe_harbor.investment_contract", "COMPLIANCE"),
            116: ("legal_safe_harbor.passive_income", "COMPLIANCE"),
            117: ("legal_safe_harbor.redemption_rights", "COMPLIANCE"),
            118: ("legal_safe_harbor.security_token", "COMPLIANCE"),
            119: ("legal_safe_harbor.stablecoin", "COMPLIANCE"),
            120: ("legal_safe_harbor.upgrade_mechanism", "COMPLIANCE"),
            121: ("legal_safe_harbor.yield_bearing", "COMPLIANCE"),
            122: ("primary_utilities", "GENERAL"),
            123: ("primary_utilities.ecosystem_rewards", "GENERAL"),
            124: ("primary_utilities.ecosystem_rewards.description", "GENERAL"),
            125: ("primary_utilities.ecosystem_rewards.distribution_method", "GENERAL"),
            126: ("primary_utilities.ecosystem_rewards.reward_pools", "GENERAL"),
            127: ("primary_utilities.ecosystem_rewards.reward_pools", "GENERAL"),
            128: ("primary_utilities.ecosystem_rewards.reward_pools", "GENERAL"),
            129: ("primary_utilities.ecosystem_rewards.reward_pools", "GENERAL"),
            130: ("primary_utilities.governance_participation", "GENERAL"),
            131: ("primary_utilities.governance_participation.description", "GENERAL"),
            132: ("primary_utilities.governance_participation.proposal_threshold", "GOVERNANCE"),
            133: ("primary_utilities.governance_participation.voting_weight", "GOVERNANCE"),
            134: ("primary_utilities.identity_verification", "GENERAL"),
            135: ("primary_utilities.identity_verification.burn_clarification", "GENERAL"),
            136: ("primary_utilities.identity_verification.burn_source_note", "GENERAL"),
            137: ("primary_utilities.identity_verification.description", "GENERAL"),
            138: ("primary_utilities.identity_verification.fee_burn_mechanism", "ECONOMICS"),
            139: ("primary_utilities.identity_verification.smart_contract", "GENERAL"),
            140: ("primary_utilities.staking_utility", "ECONOMICS"),
            141: ("primary_utilities.staking_utility.description", "ECONOMICS"),
            142: ("primary_utilities.staking_utility.slashing_conditions", "ECONOMICS"),
            143: ("primary_utilities.staking_utility.staking_rewards", "ECONOMICS"),
            144: ("risk_mitigation", "GENERAL"),
            145: ("risk_mitigation.clear_utility_purpose", "GENERAL"),
            146: ("risk_mitigation.no_fiat_pegging", "GENERAL"),
            147: ("risk_mitigation.no_marketing_investment", "GENERAL"),
            148: ("risk_mitigation.no_redemption_mechanism", "GENERAL"),
            149: ("risk_mitigation.no_yield_promises", "GENERAL"),
            150: ("risk_mitigation.open_source_license", "GENERAL"),
            151: ("secondary_utilities", "GENERAL"),
            152: ("secondary_utilities.api_access", "GENERAL"),
            153: ("secondary_utilities.data_portability", "GENERAL"),
            154: ("secondary_utilities.marketplace_access", "GENERAL"),
            155: ("secondary_utilities.premium_features", "GENERAL"),
            156: ("staking_mechanics", "ECONOMICS"),
            157: ("staking_mechanics.discount_applies_to", "ECONOMICS"),
            158: ("staking_mechanics.maximum_discount", "ECONOMICS"),
            159: ("staking_mechanics.minimum_stake", "ECONOMICS"),
            160: ("staking_mechanics.slashing_penalty", "ECONOMICS"),
            161: ("staking_mechanics.system_fee_invariance", "ECONOMICS"),
            162: ("staking_mechanics.unstaking_period", "ECONOMICS"),
            163: ("supply_mechanics", "ECONOMICS"),
            164: ("supply_mechanics.circulation_controls", "ECONOMICS"),
            165: ("supply_mechanics.circulation_controls.max_annual_inflation", "ECONOMICS"),
            166: ("supply_mechanics.circulation_controls.partnership_unlock", "ECONOMICS"),
            167: ("supply_mechanics.circulation_controls.reserve_governance", "ECONOMICS"),
            168: ("supply_mechanics.circulation_controls.team_vesting_schedule", "ECONOMICS"),
            169: ("supply_mechanics.deflationary_mechanisms", "ECONOMICS"),
            170: ("supply_mechanics.deflationary_mechanisms.governance_burning", "ECONOMICS"),
            171: ("supply_mechanics.deflationary_mechanisms.staking_slashing", "ECONOMICS"),
            172: ("supply_mechanics.initial_distribution", "ECONOMICS"),
            173: ("supply_mechanics.initial_distribution.community_rewards", "ECONOMICS"),
            174: ("supply_mechanics.initial_distribution.ecosystem_development", "ECONOMICS"),
            175: ("supply_mechanics.initial_distribution.partnerships", "ECONOMICS"),
            176: ("supply_mechanics.initial_distribution.reserve_fund", "ECONOMICS"),
            177: ("supply_mechanics.initial_distribution.team_development", "ECONOMICS"),
            178: ("supply_mechanics.total_supply", "ECONOMICS"),
            179: ("technical_specification", "GENERAL"),
            180: ("technical_specification.blockchain", "GENERAL"),
            181: ("technical_specification.custody_model", "GENERAL"),
            182: ("technical_specification.smart_contract_automation", "GENERAL"),
            183: ("technical_specification.standard", "GENERAL"),
            184: ("technical_specification.supply_model", "ECONOMICS"),
            185: ("token_definition", "GENERAL"),
            186: ("token_definition.explicit_exclusions", "GENERAL"),
            187: ("token_definition.legal_position", "COMPLIANCE"),
            188: ("token_definition.purpose", "GENERAL"),
            189: ("version", "METADATA"),
        }

        if num in field_map:
            field_path, category = field_map[num]
            if field_path:
                return self._validate_field(field_path, f"SOT-V2-{num:04d}", category)
            else:
                # No field path specified - use generic check for now
                return ValidationResult(
                    rule_id=f"SOT-V2-{num:04d}",
                    passed=False,
                    severity=self._get_severity(category),
                    message=f"SOT-V2-{num:04d}: No field path specified - needs manual implementation",
                    evidence={"category": category, "status": "placeholder"}
                )

        # Unknown rule number
        return ValidationResult(
            rule_id=f"SOT-V2-{num:04d}",
            passed=False,
            severity=Severity.MEDIUM,
            message=f"SOT-V2-{num:04d}: Unknown rule number",
            evidence={"error": "Unknown rule", "num": num}
        )
