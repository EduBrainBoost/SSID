"""
SSID Pricing Validator v5.1
Root-24-LOCK Compliance Enforced
Generated: 2025-10-13

Pricing validation engine with updated thresholds:
- S2 ≥ €3.0M (raised from €2.5M)
- S3 ≥ €6.5M (raised from €5.0M)
- Sovereign floor: €40,000 (raised from €25,000)
- Business Plus tier validation
- Region surcharge validation (10 regions)
"""

from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from enum import Enum
import hashlib
import json

class TierID(str, Enum):
    """Subscription tier identifiers"""
    STARTER = "T1_STARTER"
    PROFESSIONAL = "T2_PROFESSIONAL"
    BUSINESS_PLUS = "T3_BUSINESS_PLUS"
    ENTERPRISE = "T4_ENTERPRISE"
    SOVEREIGN = "T5_SOVEREIGN"

class AddOnID(str, Enum):
    """Add-on identifiers"""
    WHITE_LABEL = "AO_WHITE_LABEL"
    PREMIUM_API = "AO_PREMIUM_API"
    AUDIT_EXPORT = "AO_AUDIT_EXPORT"
    FIVE_NINES = "AO_FIVE_NINES"
    ENTERPRISE_BUNDLE = "AO_ENTERPRISE_BUNDLE"

class RegionID(str, Enum):
    """Region identifiers"""
    EU_CENTRAL = "R1_EU_CENTRAL"
    EU_WEST = "R2_EU_WEST"
    US_EAST = "R3_US_EAST"
    US_WEST = "R4_US_WEST"
    APAC = "R5_APAC"
    ME_UAE = "R6_ME_UAE"
    UK = "R7_UK"
    APAC_EXT = "R8_APAC_EXT"
    LATAM_BR = "R9_LATAM_BR"
    EU_EAST = "R10_EU_EAST"

class ValidationError(Exception):
    """Pricing validation error"""
    pass

class PricingValidatorV5_1:
    """
    Pricing validator with v5.1 thresholds and rules
    """

    VERSION = "5.1.0"
    EFFECTIVE_DATE = "2025-10-13"
    ROOT_COMPLIANCE = "ROOT_24_LOCK_ENFORCED"

    # Tier pricing (EUR)
    TIER_PRICES = {
        TierID.STARTER: Decimal("99"),
        TierID.PROFESSIONAL: Decimal("499"),
        TierID.BUSINESS_PLUS: Decimal("249"),
        TierID.ENTERPRISE: Decimal("2499"),
        TierID.SOVEREIGN: Decimal("40000"),
    }

    # Add-on pricing (EUR)
    ADDON_PRICES = {
        AddOnID.WHITE_LABEL: Decimal("299"),
        AddOnID.PREMIUM_API: Decimal("199"),
        AddOnID.AUDIT_EXPORT: Decimal("149"),
        AddOnID.FIVE_NINES: Decimal("999"),
        AddOnID.ENTERPRISE_BUNDLE: Decimal("1499"),
    }

    # Add-on tier eligibility
    ADDON_TIER_ELIGIBILITY = {
        AddOnID.WHITE_LABEL: [TierID.PROFESSIONAL, TierID.BUSINESS_PLUS, TierID.ENTERPRISE],
        AddOnID.PREMIUM_API: [TierID.PROFESSIONAL, TierID.BUSINESS_PLUS, TierID.ENTERPRISE],
        AddOnID.AUDIT_EXPORT: [TierID.PROFESSIONAL, TierID.BUSINESS_PLUS, TierID.ENTERPRISE],
        AddOnID.FIVE_NINES: [TierID.ENTERPRISE],
        AddOnID.ENTERPRISE_BUNDLE: [TierID.ENTERPRISE],
    }

    # Region surcharges (percentage)
    REGION_SURCHARGES = {
        RegionID.EU_CENTRAL: Decimal("0"),
        RegionID.EU_WEST: Decimal("0"),
        RegionID.US_EAST: Decimal("0"),
        RegionID.US_WEST: Decimal("0"),
        RegionID.APAC: Decimal("8"),
        RegionID.ME_UAE: Decimal("15"),
        RegionID.UK: Decimal("3"),
        RegionID.APAC_EXT: Decimal("12"),
        RegionID.LATAM_BR: Decimal("10"),
        RegionID.EU_EAST: Decimal("5"),
    }

    # Thresholds (v5.1 updates)
    SEGMENT_2_MIN_REVENUE_EUR = Decimal("3000000")  # Raised from 2.5M
    SEGMENT_3_MIN_REVENUE_EUR = Decimal("6500000")  # Raised from 5.0M
    ADD_ON_ADOPTION_CAP_PERCENTAGE = Decimal("70")
    SOVEREIGN_FLOOR_EUR = Decimal("40000")  # Raised from 25,000

    # Business Plus delegate constraints
    BUSINESS_PLUS_MIN_DELEGATES = 10
    BUSINESS_PLUS_MAX_DELEGATES = 100

    def __init__(self):
        """Initialize validator"""
        self.validation_log: List[Dict] = []

    def validate_business_plus_eligibility(
        self, tier_id: TierID, delegate_count: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate Business Plus tier eligibility based on delegate count

        Args:
            tier_id: Tier identifier
            delegate_count: Number of delegates

        Returns:
            Tuple of (is_valid, error_message)
        """
        if tier_id != TierID.BUSINESS_PLUS:
            return (True, None)

        if delegate_count < self.BUSINESS_PLUS_MIN_DELEGATES:
            return (
                False,
                f"Business Plus tier requires at least {self.BUSINESS_PLUS_MIN_DELEGATES} delegates (provided: {delegate_count})"
            )

        if delegate_count > self.BUSINESS_PLUS_MAX_DELEGATES:
            return (
                False,
                f"Business Plus tier allows maximum {self.BUSINESS_PLUS_MAX_DELEGATES} delegates (provided: {delegate_count})"
            )

        return (True, None)

    def validate_sovereign_floor(
        self, tier_id: TierID, price_eur: Decimal
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate Sovereign tier minimum price floor

        Args:
            tier_id: Tier identifier
            price_eur: Proposed price in EUR

        Returns:
            Tuple of (is_valid, error_message)
        """
        if tier_id != TierID.SOVEREIGN:
            return (True, None)

        if price_eur < self.SOVEREIGN_FLOOR_EUR:
            return (
                False,
                f"Sovereign tier requires minimum €{self.SOVEREIGN_FLOOR_EUR} (provided: €{price_eur})"
            )

        return (True, None)

    def validate_addon_adoption_cap(
        self, tier_id: TierID, addon_ids: List[AddOnID]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate add-on adoption does not exceed 70% of base tier price

        Args:
            tier_id: Tier identifier
            addon_ids: List of add-on identifiers

        Returns:
            Tuple of (is_valid, error_message)
        """
        base_price = self.TIER_PRICES[tier_id]
        total_addon_cost = sum(self.ADDON_PRICES[addon_id] for addon_id in addon_ids)

        if base_price == 0:
            return (True, None)

        adoption_percentage = (total_addon_cost / base_price) * 100

        if adoption_percentage > self.ADD_ON_ADOPTION_CAP_PERCENTAGE:
            return (
                False,
                f"Add-on adoption exceeds {self.ADD_ON_ADOPTION_CAP_PERCENTAGE}% cap (current: {adoption_percentage:.2f}%)"
            )

        return (True, None)

    def validate_region_surcharge(
        self, region_id: RegionID, base_price_eur: Decimal, total_price_eur: Decimal
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate region surcharge is correctly applied

        Args:
            region_id: Region identifier
            base_price_eur: Base price before surcharge
            total_price_eur: Total price after surcharge

        Returns:
            Tuple of (is_valid, error_message)
        """
        surcharge_percentage = self.REGION_SURCHARGES[region_id]
        expected_surcharge = base_price_eur * (surcharge_percentage / 100)
        expected_total = base_price_eur + expected_surcharge

        # Allow small floating point differences
        if abs(total_price_eur - expected_total) >= Decimal("0.01"):
            return (
                False,
                f"Region surcharge mismatch: expected €{expected_total:.2f}, got €{total_price_eur:.2f} "
                f"(region: {region_id.value}, surcharge: {surcharge_percentage}%)"
            )

        return (True, None)

    def validate_addon_tier_eligibility(
        self, tier_id: TierID, addon_ids: List[AddOnID]
    ) -> Tuple[bool, List[str]]:
        """
        Validate all add-ons are eligible for the tier

        Args:
            tier_id: Tier identifier
            addon_ids: List of add-on identifiers

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        for addon_id in addon_ids:
            eligible_tiers = self.ADDON_TIER_ELIGIBILITY[addon_id]
            if tier_id not in eligible_tiers:
                errors.append(
                    f"Add-on {addon_id.value} not available for tier {tier_id.value} "
                    f"(allowed: {[t.value for t in eligible_tiers]})"
                )

        return (len(errors) == 0, errors)

    def validate_segment_revenue_threshold(
        self, segment: str, annual_revenue_eur: Decimal
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate segment revenue thresholds (S2 ≥ €3.0M, S3 ≥ €6.5M)

        Args:
            segment: Segment identifier (S1, S2, S3)
            annual_revenue_eur: Annual revenue in EUR

        Returns:
            Tuple of (is_valid, error_message)
        """
        if segment == "S2":
            if annual_revenue_eur < self.SEGMENT_2_MIN_REVENUE_EUR:
                return (
                    False,
                    f"Segment 2 requires minimum €{self.SEGMENT_2_MIN_REVENUE_EUR} annual revenue "
                    f"(provided: €{annual_revenue_eur})"
                )

        elif segment == "S3":
            if annual_revenue_eur < self.SEGMENT_3_MIN_REVENUE_EUR:
                return (
                    False,
                    f"Segment 3 requires minimum €{self.SEGMENT_3_MIN_REVENUE_EUR} annual revenue "
                    f"(provided: €{annual_revenue_eur})"
                )

        return (True, None)

    def calculate_total_price(
        self, tier_id: TierID, addon_ids: List[AddOnID], region_id: RegionID
    ) -> Decimal:
        """
        Calculate total price with add-ons and region surcharge

        Args:
            tier_id: Tier identifier
            addon_ids: List of add-on identifiers
            region_id: Region identifier

        Returns:
            Total price in EUR
        """
        base_price = self.TIER_PRICES[tier_id]
        addon_cost = sum(self.ADDON_PRICES[addon_id] for addon_id in addon_ids)
        subtotal = base_price + addon_cost

        surcharge_percentage = self.REGION_SURCHARGES[region_id]
        surcharge = subtotal * (surcharge_percentage / 100)

        total = subtotal + surcharge
        return total

    def validate_subscription(
        self,
        tier_id: TierID,
        addon_ids: List[AddOnID],
        region_id: RegionID,
        delegate_count: int,
        segment: Optional[str] = None,
        annual_revenue_eur: Optional[Decimal] = None,
    ) -> Tuple[bool, List[str], Dict]:
        """
        Comprehensive subscription validation

        Args:
            tier_id: Tier identifier
            addon_ids: List of add-on identifiers
            region_id: Region identifier
            delegate_count: Number of delegates
            segment: Optional segment identifier (S1, S2, S3)
            annual_revenue_eur: Optional annual revenue in EUR

        Returns:
            Tuple of (is_valid, error_messages, validation_result)
        """
        errors = []

        # Validate Business Plus eligibility
        is_valid, error_msg = self.validate_business_plus_eligibility(tier_id, delegate_count)
        if not is_valid:
            errors.append(error_msg)

        # Calculate total price
        total_price = self.calculate_total_price(tier_id, addon_ids, region_id)

        # Validate Sovereign floor
        is_valid, error_msg = self.validate_sovereign_floor(tier_id, total_price)
        if not is_valid:
            errors.append(error_msg)

        # Validate add-on adoption cap
        is_valid, error_msg = self.validate_addon_adoption_cap(tier_id, addon_ids)
        if not is_valid:
            errors.append(error_msg)

        # Validate add-on tier eligibility
        is_valid, error_msgs = self.validate_addon_tier_eligibility(tier_id, addon_ids)
        if not is_valid:
            errors.extend(error_msgs)

        # Validate region surcharge
        base_price = self.TIER_PRICES[tier_id] + sum(self.ADDON_PRICES[a] for a in addon_ids)
        is_valid, error_msg = self.validate_region_surcharge(region_id, base_price, total_price)
        if not is_valid:
            errors.append(error_msg)

        # Validate segment revenue thresholds (if provided)
        if segment and annual_revenue_eur:
            is_valid, error_msg = self.validate_segment_revenue_threshold(segment, annual_revenue_eur)
            if not is_valid:
                errors.append(error_msg)

        # Build result
        result = {
            "version": self.VERSION,
            "tier_id": tier_id.value,
            "addon_ids": [a.value for a in addon_ids],
            "region_id": region_id.value,
            "delegate_count": delegate_count,
            "base_price_eur": float(self.TIER_PRICES[tier_id]),
            "total_price_eur": float(total_price),
            "is_valid": len(errors) == 0,
            "errors": errors,
            "root_compliance": self.ROOT_COMPLIANCE,
        }

        # Log validation
        self.validation_log.append(result)

        return (len(errors) == 0, errors, result)

    def get_validation_hash(self, result: Dict) -> str:
        """
        Generate SHA-256 hash of validation result

        Args:
            result: Validation result dictionary

        Returns:
            SHA-256 hash string
        """
        result_json = json.dumps(result, sort_keys=True)
        return hashlib.sha256(result_json.encode()).hexdigest()

    def export_validation_log(self) -> List[Dict]:
        """
        Export validation log with hashes

        Returns:
            List of validation results with hashes
        """
        return [
            {**result, "sha256": self.get_validation_hash(result)}
            for result in self.validation_log
        ]

# Example usage
if __name__ == "__main__":
    validator = PricingValidatorV5_1()

    # Example 1: Valid Business Plus subscription
    is_valid, errors, result = validator.validate_subscription(
        tier_id=TierID.BUSINESS_PLUS,
        addon_ids=[AddOnID.WHITE_LABEL],
        region_id=RegionID.EU_CENTRAL,
        delegate_count=50,
    )
    print(f"Business Plus validation: {'PASS' if is_valid else 'FAIL'}")
    if errors:
        for error in errors:
            print(f"  - {error}")

    # Example 2: Invalid Sovereign floor
    is_valid, errors, result = validator.validate_subscription(
        tier_id=TierID.SOVEREIGN,
        addon_ids=[],
        region_id=RegionID.EU_CENTRAL,
        delegate_count=100,
    )
    print(f"\nSovereign validation: {'PASS' if is_valid else 'FAIL'}")
    if errors:
        for error in errors:
            print(f"  - {error}")

    # Example 3: Valid Enterprise with region surcharge
    is_valid, errors, result = validator.validate_subscription(
        tier_id=TierID.ENTERPRISE,
        addon_ids=[AddOnID.FIVE_NINES, AddOnID.AUDIT_EXPORT],
        region_id=RegionID.APAC,
        delegate_count=500,
        segment="S2",
        annual_revenue_eur=Decimal("3500000"),
    )
    print(f"\nEnterprise validation: {'PASS' if is_valid else 'FAIL'}")
    print(f"Total price: €{result['total_price_eur']:.2f}")
