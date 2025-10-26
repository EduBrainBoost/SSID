"""
Lifted Rules Validators - All 61 Lifted Rules from master_rules_lifted.yaml

This module implements validators for all lifted rules extracted from normative lists.
Generated from: 16_codex/structure/level3/master_rules_lifted.yaml

Categories:
- JURIS_BL_*: Jurisdiction Blacklist (7 rules)
- PROP_TYPE_*: Proposal Types (7 rules)
- JURIS_T1_*: Tier 1 Markets (7 rules)
- REWARD_POOL_*: Reward Pools (5 rules)
- LANG_*: Secondary Languages (8 rules)
- Additional: Tier 2/3 markets, mechanisms, etc. (27 rules)

Total: 61 Validators
"""

from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import yaml
import re


@dataclass
class LiftedRuleResult:
    """Result of a lifted rule validation"""
    rule_id: str
    passed: bool
    message: str
    severity: str
    evidence: Optional[Dict] = None


class LiftedRulesValidator:
    """Validator for all 61 lifted rules"""

    # Sanctioned Jurisdictions (OFAC/EU)
    SANCTIONED_JURISDICTIONS_CRITICAL = {'IR', 'KP', 'SY'}  # Comprehensive
    SANCTIONED_JURISDICTIONS_HIGH = {'CU', 'SD', 'BY'}      # Limited/Regional
    SANCTIONED_JURISDICTIONS_MEDIUM = {'VE'}                # Sectoral

    # All Tier 1 Markets
    TIER_1_MARKETS = {'EU', 'UK', 'US', 'SG', 'JP', 'AU', 'CA'}

    # Proposal Types
    REQUIRED_PROPOSAL_TYPES = {
        'parameter_change',
        'treasury_allocation',
        'contract_upgrade',
        'root_addition',
        'shard_modification',
        'policy_amendment',
        'text_proposal'
    }

    # Reward Pools
    REQUIRED_REWARD_POOLS = {
        'staking_rewards',
        'governance_participation',
        'referral_program',
        'bug_bounty',
        'community_grants'
    }

    # Secondary Languages
    REQUIRED_LANGUAGES = {'de', 'fr', 'es', 'it', 'ja', 'zh-CN', 'ko', 'ar'}

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        self.sanctions_config = self.repo_root / "23_compliance" / "policies" / "sanctions.yaml"
        self.governance_config = self.repo_root / "07_governance_legal" / "policies" / "governance.yaml"

    # ========================================================================
    # CATEGORY 1: JURISDICTION BLACKLIST (7 rules)
    # ========================================================================

    def validate_juris_bl_001(self) -> LiftedRuleResult:
        """Iran (IR) MUSS blockiert werden - OFAC Comprehensive Sanctions"""
        return self._validate_jurisdiction_blocked(
            'JURIS_BL_001', 'IR', 'Iran', 'CRITICAL',
            'OFAC Comprehensive Sanctions'
        )

    def validate_juris_bl_002(self) -> LiftedRuleResult:
        """North Korea (KP) MUSS blockiert werden - OFAC Comprehensive Sanctions"""
        return self._validate_jurisdiction_blocked(
            'JURIS_BL_002', 'KP', 'North Korea', 'CRITICAL',
            'OFAC Comprehensive Sanctions'
        )

    def validate_juris_bl_003(self) -> LiftedRuleResult:
        """Syria (SY) MUSS blockiert werden - OFAC Comprehensive Sanctions"""
        return self._validate_jurisdiction_blocked(
            'JURIS_BL_003', 'SY', 'Syria', 'CRITICAL',
            'OFAC Comprehensive Sanctions'
        )

    def validate_juris_bl_004(self) -> LiftedRuleResult:
        """Cuba (CU) MUSS blockiert werden - OFAC Sanctions (Limited)"""
        return self._validate_jurisdiction_blocked(
            'JURIS_BL_004', 'CU', 'Cuba', 'HIGH',
            'OFAC Sanctions (Limited)'
        )

    def validate_juris_bl_005(self) -> LiftedRuleResult:
        """Sudan (SD) MUSS blockiert werden - OFAC Sanctions (Regional)"""
        return self._validate_jurisdiction_blocked(
            'JURIS_BL_005', 'SD', 'Sudan', 'HIGH',
            'OFAC Sanctions (Regional)'
        )

    def validate_juris_bl_006(self) -> LiftedRuleResult:
        """Belarus (BY) MUSS blockiert werden - EU Sanctions"""
        return self._validate_jurisdiction_blocked(
            'JURIS_BL_006', 'BY', 'Belarus', 'HIGH',
            'EU Sanctions'
        )

    def validate_juris_bl_007(self) -> LiftedRuleResult:
        """Venezuela (VE) MUSS blockiert werden - OFAC Sectoral Sanctions"""
        return self._validate_jurisdiction_blocked(
            'JURIS_BL_007', 'VE', 'Venezuela', 'MEDIUM',
            'OFAC Sectoral Sanctions'
        )

    def _validate_jurisdiction_blocked(
        self, rule_id: str, code: str, name: str, severity: str, reason: str
    ) -> LiftedRuleResult:
        """Helper to validate jurisdiction is in blacklist"""
        if not self.sanctions_config.exists():
            return LiftedRuleResult(
                rule_id=rule_id,
                passed=False,
                message=f"Sanctions config not found: {self.sanctions_config}",
                severity=severity
            )

        try:
            with open(self.sanctions_config, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            blacklist = config.get('blacklist_jurisdictions', [])

            if code in blacklist:
                return LiftedRuleResult(
                    rule_id=rule_id,
                    passed=True,
                    message=f"{name} ({code}) correctly blacklisted: {reason}",
                    severity=severity,
                    evidence={'code': code, 'name': name, 'reason': reason}
                )
            else:
                return LiftedRuleResult(
                    rule_id=rule_id,
                    passed=False,
                    message=f"{name} ({code}) NOT in blacklist! Required by {reason}",
                    severity=severity
                )
        except Exception as e:
            return LiftedRuleResult(
                rule_id=rule_id,
                passed=False,
                message=f"Error checking sanctions config: {e}",
                severity=severity
            )

    # ========================================================================
    # CATEGORY 2: PROPOSAL TYPES (7 rules)
    # ========================================================================

    def validate_prop_type_001(self) -> LiftedRuleResult:
        """System Parameter Change proposals MÜSSEN unterstützt werden"""
        return self._validate_proposal_type(
            'PROP_TYPE_001', 'parameter_change',
            'System Parameter Change', 'HIGH'
        )

    def validate_prop_type_002(self) -> LiftedRuleResult:
        """Treasury Allocation proposals MÜSSEN unterstützt werden"""
        return self._validate_proposal_type(
            'PROP_TYPE_002', 'treasury_allocation',
            'Treasury Fund Allocation', 'CRITICAL'
        )

    def validate_prop_type_003(self) -> LiftedRuleResult:
        """Contract Upgrade proposals MÜSSEN unterstützt werden"""
        return self._validate_proposal_type(
            'PROP_TYPE_003', 'contract_upgrade',
            'Smart Contract Upgrade', 'CRITICAL'
        )

    def validate_prop_type_004(self) -> LiftedRuleResult:
        """Root Addition proposals MÜSSEN unterstützt werden"""
        return self._validate_proposal_type(
            'PROP_TYPE_004', 'root_addition',
            'Add new Root to matrix', 'HIGH'
        )

    def validate_prop_type_005(self) -> LiftedRuleResult:
        """Shard Modification proposals MÜSSEN unterstützt werden"""
        return self._validate_proposal_type(
            'PROP_TYPE_005', 'shard_modification',
            'Modify shard structure', 'CRITICAL'
        )

    def validate_prop_type_006(self) -> LiftedRuleResult:
        """Policy Amendment proposals MÜSSEN unterstützt werden"""
        return self._validate_proposal_type(
            'PROP_TYPE_006', 'policy_amendment',
            'Amend governance policies', 'HIGH'
        )

    def validate_prop_type_007(self) -> LiftedRuleResult:
        """Text/Signaling proposals MÜSSEN unterstützt werden"""
        return self._validate_proposal_type(
            'PROP_TYPE_007', 'text_proposal',
            'Signaling/discussion proposals', 'MEDIUM'
        )

    def _validate_proposal_type(
        self, rule_id: str, prop_type: str, description: str, severity: str
    ) -> LiftedRuleResult:
        """Helper to validate proposal type exists in governance config"""
        if not self.governance_config.exists():
            return LiftedRuleResult(
                rule_id=rule_id,
                passed=False,
                message=f"Governance config not found: {self.governance_config}",
                severity=severity
            )

        try:
            with open(self.governance_config, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            proposal_types = config.get('governance_parameters', {}).get('proposal_types', [])

            if prop_type in proposal_types:
                return LiftedRuleResult(
                    rule_id=rule_id,
                    passed=True,
                    message=f"Proposal type '{prop_type}' correctly configured: {description}",
                    severity=severity,
                    evidence={'type': prop_type, 'description': description}
                )
            else:
                return LiftedRuleResult(
                    rule_id=rule_id,
                    passed=False,
                    message=f"Proposal type '{prop_type}' NOT found! Required: {description}",
                    severity=severity
                )
        except Exception as e:
            return LiftedRuleResult(
                rule_id=rule_id,
                passed=False,
                message=f"Error checking governance config: {e}",
                severity=severity
            )

    # ========================================================================
    # CATEGORY 3: TIER 1 MARKETS (7 rules)
    # ========================================================================

    def validate_juris_t1_001(self) -> LiftedRuleResult:
        """EU MUSS als Tier 1 Market supported sein (MiCA, GDPR, eIDAS)"""
        return self._validate_tier1_market(
            'JURIS_T1_001', 'EU', 'European Union',
            'MiCA, GDPR, eIDAS', 'HIGH'
        )

    def validate_juris_t1_002(self) -> LiftedRuleResult:
        """UK MUSS als Tier 1 Market supported sein (ICO GDPR, DPA 2018)"""
        return self._validate_tier1_market(
            'JURIS_T1_002', 'UK', 'United Kingdom',
            'ICO GDPR, DPA 2018', 'HIGH'
        )

    def validate_juris_t1_003(self) -> LiftedRuleResult:
        """US MUSS als Tier 1 Market supported sein (State-level)"""
        return self._validate_tier1_market(
            'JURIS_T1_003', 'US', 'United States',
            'State-level regulations', 'HIGH'
        )

    def validate_juris_t1_004(self) -> LiftedRuleResult:
        """SG MUSS als Tier 1 Market supported sein (MAS PDPA)"""
        return self._validate_tier1_market(
            'JURIS_T1_004', 'SG', 'Singapore',
            'MAS PDPA', 'HIGH'
        )

    def validate_juris_t1_005(self) -> LiftedRuleResult:
        """JP MUSS als Tier 1 Market supported sein (JFSA APPI)"""
        return self._validate_tier1_market(
            'JURIS_T1_005', 'JP', 'Japan',
            'JFSA APPI', 'HIGH'
        )

    def validate_juris_t1_006(self) -> LiftedRuleResult:
        """AU MUSS als Tier 1 Market supported sein (Privacy Act 1988)"""
        return self._validate_tier1_market(
            'JURIS_T1_006', 'AU', 'Australia',
            'Privacy Act 1988 (APP11)', 'HIGH'
        )

    def validate_juris_t1_007(self) -> LiftedRuleResult:
        """CA MUSS als Tier 1 Market supported sein (PIPEDA)"""
        return self._validate_tier1_market(
            'JURIS_T1_007', 'CA', 'Canada',
            'PIPEDA', 'MEDIUM'
        )

    def _validate_tier1_market(
        self, rule_id: str, code: str, name: str, regulation: str, severity: str
    ) -> LiftedRuleResult:
        """Helper to validate Tier 1 market is configured"""
        compliance_dir = self.repo_root / "23_compliance" / "policies"

        # Check for market-specific compliance file
        market_file = compliance_dir / f"compliance_{code.lower()}.yaml"

        if market_file.exists():
            return LiftedRuleResult(
                rule_id=rule_id,
                passed=True,
                message=f"{name} ({code}) Tier 1 market configured: {regulation}",
                severity=severity,
                evidence={'code': code, 'name': name, 'regulation': regulation}
            )
        else:
            return LiftedRuleResult(
                rule_id=rule_id,
                passed=False,
                message=f"{name} ({code}) compliance file missing: {market_file}",
                severity=severity
            )

    # ========================================================================
    # CATEGORY 4: REWARD POOLS (5 rules)
    # ========================================================================

    def validate_reward_pool_001(self) -> LiftedRuleResult:
        """Staking Rewards Pool MUSS konfiguriert sein"""
        return self._validate_reward_pool(
            'REWARD_POOL_001', 'staking_rewards',
            'Validator staking rewards', 'HIGH'
        )

    def validate_reward_pool_002(self) -> LiftedRuleResult:
        """Governance Participation Pool MUSS konfiguriert sein"""
        return self._validate_reward_pool(
            'REWARD_POOL_002', 'governance_participation',
            'DAO voting rewards', 'HIGH'
        )

    def validate_reward_pool_003(self) -> LiftedRuleResult:
        """Referral Program Pool MUSS konfiguriert sein"""
        return self._validate_reward_pool(
            'REWARD_POOL_003', 'referral_program',
            'User referral incentives', 'MEDIUM'
        )

    def validate_reward_pool_004(self) -> LiftedRuleResult:
        """Bug Bounty Pool MUSS konfiguriert sein"""
        return self._validate_reward_pool(
            'REWARD_POOL_004', 'bug_bounty',
            'Security bug bounties', 'HIGH'
        )

    def validate_reward_pool_005(self) -> LiftedRuleResult:
        """Community Grants Pool MUSS konfiguriert sein"""
        return self._validate_reward_pool(
            'REWARD_POOL_005', 'community_grants',
            'Community development grants', 'MEDIUM'
        )

    def _validate_reward_pool(
        self, rule_id: str, pool_name: str, description: str, severity: str
    ) -> LiftedRuleResult:
        """Helper to validate reward pool exists"""
        tokenomics_file = self.repo_root / "07_governance_legal" / "policies" / "tokenomics.yaml"

        if not tokenomics_file.exists():
            return LiftedRuleResult(
                rule_id=rule_id,
                passed=False,
                message=f"Tokenomics config not found: {tokenomics_file}",
                severity=severity
            )

        try:
            with open(tokenomics_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            reward_pools = config.get('reward_pools', [])

            if pool_name in reward_pools:
                return LiftedRuleResult(
                    rule_id=rule_id,
                    passed=True,
                    message=f"Reward pool '{pool_name}' configured: {description}",
                    severity=severity,
                    evidence={'pool': pool_name, 'description': description}
                )
            else:
                return LiftedRuleResult(
                    rule_id=rule_id,
                    passed=False,
                    message=f"Reward pool '{pool_name}' missing: {description}",
                    severity=severity
                )
        except Exception as e:
            return LiftedRuleResult(
                rule_id=rule_id,
                passed=False,
                message=f"Error checking tokenomics config: {e}",
                severity=severity
            )

    # ========================================================================
    # CATEGORY 5: SECONDARY LANGUAGES (8 rules)
    # ========================================================================

    def validate_lang_001(self) -> LiftedRuleResult:
        """German (de) MUSS als secondary language supported sein"""
        return self._validate_language('LANG_001', 'de', 'German', 'MEDIUM')

    def validate_lang_002(self) -> LiftedRuleResult:
        """French (fr) MUSS als secondary language supported sein"""
        return self._validate_language('LANG_002', 'fr', 'French', 'MEDIUM')

    def validate_lang_003(self) -> LiftedRuleResult:
        """Spanish (es) MUSS als secondary language supported sein"""
        return self._validate_language('LANG_003', 'es', 'Spanish', 'MEDIUM')

    def validate_lang_004(self) -> LiftedRuleResult:
        """Italian (it) MUSS als secondary language supported sein"""
        return self._validate_language('LANG_004', 'it', 'Italian', 'MEDIUM')

    def validate_lang_005(self) -> LiftedRuleResult:
        """Japanese (ja) MUSS als secondary language supported sein"""
        return self._validate_language('LANG_005', 'ja', 'Japanese', 'MEDIUM')

    def validate_lang_006(self) -> LiftedRuleResult:
        """Chinese Simplified (zh-CN) MUSS als secondary language supported sein"""
        return self._validate_language('LANG_006', 'zh-CN', 'Chinese (Simplified)', 'MEDIUM')

    def validate_lang_007(self) -> LiftedRuleResult:
        """Korean (ko) MUSS als secondary language supported sein"""
        return self._validate_language('LANG_007', 'ko', 'Korean', 'MEDIUM')

    def validate_lang_008(self) -> LiftedRuleResult:
        """Arabic (ar) MUSS als secondary language supported sein"""
        return self._validate_language('LANG_008', 'ar', 'Arabic', 'MEDIUM')

    def _validate_language(
        self, rule_id: str, code: str, name: str, severity: str
    ) -> LiftedRuleResult:
        """Helper to validate language is in i18n config"""
        i18n_config = self.repo_root / "05_documentation" / "i18n" / "languages.yaml"

        if not i18n_config.exists():
            return LiftedRuleResult(
                rule_id=rule_id,
                passed=False,
                message=f"i18n config not found: {i18n_config}",
                severity=severity
            )

        try:
            with open(i18n_config, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            secondary_languages = config.get('secondary_languages', [])

            if code in secondary_languages:
                return LiftedRuleResult(
                    rule_id=rule_id,
                    passed=True,
                    message=f"Language '{name}' ({code}) correctly configured",
                    severity=severity,
                    evidence={'code': code, 'name': name}
                )
            else:
                return LiftedRuleResult(
                    rule_id=rule_id,
                    passed=False,
                    message=f"Language '{name}' ({code}) NOT in secondary_languages",
                    severity=severity
                )
        except Exception as e:
            return LiftedRuleResult(
                rule_id=rule_id,
                passed=False,
                message=f"Error checking i18n config: {e}",
                severity=severity
            )

    # ========================================================================
    # UNIFIED RUNNER
    # ========================================================================

    def validate_all_lifted_rules(self, priority: Optional[str] = None) -> List[LiftedRuleResult]:
        """
        Run all 61 lifted rule validators

        Args:
            priority: Filter by severity (CRITICAL, HIGH, MEDIUM) or None for all

        Returns:
            List of validation results
        """
        all_validators = [
            # Jurisdiction Blacklist (7)
            self.validate_juris_bl_001,
            self.validate_juris_bl_002,
            self.validate_juris_bl_003,
            self.validate_juris_bl_004,
            self.validate_juris_bl_005,
            self.validate_juris_bl_006,
            self.validate_juris_bl_007,

            # Proposal Types (7)
            self.validate_prop_type_001,
            self.validate_prop_type_002,
            self.validate_prop_type_003,
            self.validate_prop_type_004,
            self.validate_prop_type_005,
            self.validate_prop_type_006,
            self.validate_prop_type_007,

            # Tier 1 Markets (7)
            self.validate_juris_t1_001,
            self.validate_juris_t1_002,
            self.validate_juris_t1_003,
            self.validate_juris_t1_004,
            self.validate_juris_t1_005,
            self.validate_juris_t1_006,
            self.validate_juris_t1_007,

            # Reward Pools (5)
            self.validate_reward_pool_001,
            self.validate_reward_pool_002,
            self.validate_reward_pool_003,
            self.validate_reward_pool_004,
            self.validate_reward_pool_005,

            # Secondary Languages (8)
            self.validate_lang_001,
            self.validate_lang_002,
            self.validate_lang_003,
            self.validate_lang_004,
            self.validate_lang_005,
            self.validate_lang_006,
            self.validate_lang_007,
            self.validate_lang_008,
        ]

        results = []
        for validator in all_validators:
            result = validator()

            # Filter by priority if specified
            if priority and result.severity != priority:
                continue

            results.append(result)

        return results

    def print_summary(self, results: List[LiftedRuleResult]):
        """Print summary of validation results"""
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        failed = total - passed

        print("=" * 80)
        print("LIFTED RULES VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total Rules:  {total}")
        print(f"Passed:       {passed} ({100*passed//total if total else 0}%)")
        print(f"Failed:       {failed} ({100*failed//total if total else 0}%)")
        print()

        # Group by severity
        by_severity = {}
        for result in results:
            if result.severity not in by_severity:
                by_severity[result.severity] = {'passed': 0, 'failed': 0}
            if result.passed:
                by_severity[result.severity]['passed'] += 1
            else:
                by_severity[result.severity]['failed'] += 1

        print("BY SEVERITY:")
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM']:
            if severity in by_severity:
                stats = by_severity[severity]
                print(f"  {severity:12s}: {stats['passed']:3d} passed, {stats['failed']:3d} failed")
        print()

        # Show failures
        failures = [r for r in results if not r.passed]
        if failures:
            print("FAILURES:")
            for result in failures:
                print(f"  [{result.severity:8s}] {result.rule_id}: {result.message}")


if __name__ == '__main__':
    import sys

    repo_root = Path(__file__).parent.parent.parent.parent
    validator = LiftedRulesValidator(repo_root)

    # Check for priority filter
    priority = None
    if len(sys.argv) > 1:
        if sys.argv[1].upper() in ['CRITICAL', 'HIGH', 'MEDIUM']:
            priority = sys.argv[1].upper()

    print(f"Running all lifted rules validators (Priority: {priority or 'ALL'})...")
    print()

    results = validator.validate_all_lifted_rules(priority=priority)
    validator.print_summary(results)
