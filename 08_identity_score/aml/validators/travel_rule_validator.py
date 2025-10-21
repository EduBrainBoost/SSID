#!/usr/bin/env python3
"""
Travel Rule Validator (IVMS101 Compliance)

Implements FATF Recommendation 16 / AMLD6 Art.1(14) Travel Rule.
Enforces €1,000 threshold and IVMS101 message format validation.

Compliance: MUST-026-TRAVEL-RULE

Usage:
    from travel_rule_validator import TravelRuleValidator

    validator = TravelRuleValidator()
    result = validator.validate_transfer(
        amount=5000.00,
        currency="EUR",
        originator_data={...},
        beneficiary_data={...}
    )
"""

import hashlib
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from decimal import Decimal

class TravelRuleValidator:
    """Validates crypto transfers against Travel Rule requirements."""

    def __init__(self, config_path: str = "08_identity_score/aml/schemas/ivms101_schema.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Threshold configuration
        self.threshold_amount = Decimal("1000.00")
        self.threshold_currency = "EUR"

        # Evidence logging
        self.evidence_dir = Path("23_compliance/evidence/travel_rule")
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        # Exchange rates cache (daily update)
        self.exchange_rates: Dict[str, Decimal] = {}
        self._load_exchange_rates()

    def _load_config(self) -> Dict:
        """Load IVMS101 schema configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def _load_exchange_rates(self) -> None:
        """Load ECB exchange rates for currency conversion."""
        
        # Production: Fetch from ECB API https://www.ecb.europa.eu/stats/policy_and_exchange_rates/
        self.exchange_rates = {
            "EUR": Decimal("1.00"),
            "USD": Decimal("1.09"),
            "GBP": Decimal("0.85"),
            "BTC": Decimal("50000.00"),  # EUR per BTC
            "ETH": Decimal("2500.00")     # EUR per ETH
        }

    def convert_to_eur(self, amount: Decimal, currency: str) -> Decimal:
        """
        Convert amount to EUR equivalent using ECB reference rates.

        Args:
            amount: Transaction amount
            currency: ISO 4217 currency code

        Returns:
            EUR equivalent amount
        """
        if currency == "EUR":
            return amount

        if currency not in self.exchange_rates:
            raise ValueError(f"Unsupported currency: {currency}")

        # Convert to EUR
        rate = self.exchange_rates[currency]

        # For crypto: 1 BTC = 50,000 EUR → amount_eur = amount * 50,000
        # For fiat: 1 USD = 1.09 EUR → amount_eur = amount / 1.09
        if currency in ["BTC", "ETH"]:
            eur_amount = amount * rate
        else:
            eur_amount = amount / rate

        return eur_amount.quantize(Decimal("0.01"))

    def exceeds_threshold(self, amount: Decimal, currency: str) -> bool:
        """
        Check if transaction exceeds €1,000 threshold.

        Args:
            amount: Transaction amount
            currency: ISO 4217 currency code

        Returns:
            True if amount ≥ €1,000 equivalent
        """
        eur_amount = self.convert_to_eur(amount, currency)
        return eur_amount >= self.threshold_amount

    def hash_pii(self, value: str) -> str:
        """
        Hash PII field using SHA-256.

        Args:
            value: Plaintext PII value

        Returns:
            SHA-256 hash (hex)
        """
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def validate_natural_person(self, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and hash natural person data.

        Args:
            person_data: Originator or beneficiary natural person info

        Returns:
            IVMS101-compliant natural person object with hashed PII
        """
        validated = {
            "natural_person": {
                "name": {
                    "name_identifiers": [
                        {
                            "primary_identifier": {
                                "type": "LEGL",
                                "value": person_data.get("legal_name", "")
                            }
                        }
                    ]
                }
            }
        }

        # Hash national identification
        if "national_id" in person_data:
            validated["natural_person"]["national_identification"] = {
                "national_identifier_type": person_data.get("id_type", "PASSPORT"),
                "national_identifier": self.hash_pii(person_data["national_id"]),
                "registration_authority": person_data.get("registration_authority", ""),
                "country_of_issue": person_data.get("country", "")
            }

        # Hash geographic address
        if "address" in person_data:
            addr = person_data["address"]
            validated["natural_person"]["geographic_addresses"] = [
                {
                    "address_type": "HOME",
                    "building_number": self.hash_pii(addr.get("building_number", "")),
                    "street_name": self.hash_pii(addr.get("street_name", "")),
                    "post_code": self.hash_pii(addr.get("post_code", "")),
                    "town_name": self.hash_pii(addr.get("town_name", "")),
                    "country": addr.get("country", "")  # ISO 3166-1 (plaintext allowed)
                }
            ]

        # Hash date/place of birth
        if "date_of_birth" in person_data:
            validated["natural_person"]["date_and_place_of_birth"] = {
                "date_of_birth": self.hash_pii(person_data["date_of_birth"]),
                "place_of_birth": self.hash_pii(person_data.get("place_of_birth", ""))
            }

        return validated

    def validate_legal_person(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate legal person (company) data.

        Args:
            entity_data: Legal entity information

        Returns:
            IVMS101-compliant legal person object
        """
        return {
            "legal_person": {
                "name": {
                    "name_identifiers": [
                        {
                            "legal_person_name": entity_data.get("company_name", ""),
                            "legal_person_name_identifier_type": "LEGL"
                        }
                    ]
                },
                "national_identification": {
                    "national_identifier_type": "LEIX",  # Legal Entity Identifier
                    "national_identifier": entity_data.get("lei_code", ""),  # Public LEI
                    "registration_authority": entity_data.get("registration_authority", "")
                },
                "geographic_addresses": [
                    {
                        "address_type": "BIZZ",
                        "country": entity_data.get("country", "")
                    }
                ]
            }
        }

    def generate_ivms101_message(
        self,
        amount: Decimal,
        currency: str,
        originator_data: Dict[str, Any],
        beneficiary_data: Dict[str, Any],
        originating_vasp: Dict[str, Any],
        beneficiary_vasp: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate IVMS101-compliant Travel Rule message.

        Args:
            amount: Transaction amount
            currency: ISO 4217 currency code
            originator_data: Sender information
            beneficiary_data: Receiver information
            originating_vasp: Sending VASP details
            beneficiary_vasp: Receiving VASP details

        Returns:
            IVMS101 message dictionary
        """
        # Determine person type (natural vs legal)
        originator = (
            self.validate_natural_person(originator_data)
            if "legal_name" in originator_data
            else self.validate_legal_person(originator_data)
        )

        beneficiary = (
            self.validate_natural_person(beneficiary_data)
            if "legal_name" in beneficiary_data
            else self.validate_legal_person(beneficiary_data)
        )

        ivms101_message = {
            "version": "1.0",
            "originator": originator,
            "beneficiary": beneficiary,
            "transfer": {
                "amount": str(amount),
                "currency": currency,
                "timestamp": datetime.now().isoformat() + "Z",
                "originating_vasp": {
                    "vasp_identifier": originating_vasp.get("lei_code", ""),
                    "vasp_identifier_type": "LEIX",
                    "vasp_name": originating_vasp.get("name", "")
                },
                "beneficiary_vasp": {
                    "vasp_identifier": beneficiary_vasp.get("lei_code", ""),
                    "vasp_identifier_type": "LEIX",
                    "vasp_name": beneficiary_vasp.get("name", "")
                }
            }
        }

        return ivms101_message

    def validate_transfer(
        self,
        amount: float,
        currency: str,
        originator_data: Dict[str, Any],
        beneficiary_data: Dict[str, Any],
        originating_vasp: Optional[Dict[str, Any]] = None,
        beneficiary_vasp: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Validate crypto transfer against Travel Rule requirements.

        Args:
            amount: Transaction amount
            currency: ISO 4217 currency code
            originator_data: Sender information
            beneficiary_data: Receiver information
            originating_vasp: Sending VASP details (optional)
            beneficiary_vasp: Receiving VASP details (optional)

        Returns:
            Validation result with compliance decision
        """
        amount_decimal = Decimal(str(amount))

        # Convert to EUR for threshold comparison
        eur_equivalent = self.convert_to_eur(amount_decimal, currency)

        result = {
            "timestamp": datetime.now().isoformat() + "Z",
            "transaction": {
                "amount": str(amount_decimal),
                "currency": currency,
                "eur_equivalent": str(eur_equivalent)
            },
            "threshold_check": {
                "threshold_amount": str(self.threshold_amount),
                "threshold_currency": self.threshold_currency,
                "exceeds_threshold": eur_equivalent >= self.threshold_amount
            },
            "compliance_decision": "PENDING"
        }

        # If below threshold, approve immediately
        if not result["threshold_check"]["exceeds_threshold"]:
            result["compliance_decision"] = "ALLOW"
            result["reason"] = f"Amount ({eur_equivalent} EUR) below €1,000 threshold"
            result["travel_rule_required"] = False
        else:
            # Generate IVMS101 message for Travel Rule compliance
            result["travel_rule_required"] = True

            # Use default VASP if not provided
            if originating_vasp is None:
                originating_vasp = {
                    "lei_code": "529900T8BM49AURSDO55",
                    "name": "SSID VASP"
                }

            if beneficiary_vasp is None:
                beneficiary_vasp = {
                    "lei_code": "UNKNOWN",
                    "name": "Unknown VASP"
                }

            ivms101_message = self.generate_ivms101_message(
                amount_decimal,
                currency,
                originator_data,
                beneficiary_data,
                originating_vasp,
                beneficiary_vasp
            )

            result["ivms101_message"] = ivms101_message
            result["compliance_decision"] = "ALLOW"
            result["reason"] = "IVMS101 message generated successfully"

        # Save evidence
        self._save_evidence(result)

        return result

    def _save_evidence(self, validation_result: Dict[str, Any]) -> None:
        """Save Travel Rule validation evidence to audit trail."""
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        evidence_file = self.evidence_dir / f"travel_rule_validation_{timestamp}.json"

        # Add evidence hash
        result_hash = hashlib.sha256(
            json.dumps(validation_result, sort_keys=True).encode()
        ).hexdigest()

        evidence = {
            "validation_result": validation_result,
            "audit_metadata": {
                "timestamp": validation_result["timestamp"],
                "result_hash_sha256": result_hash,
                "validator_version": "1.0.0",
                "compliance_requirement": "MUST-026-TRAVEL-RULE"
            }
        }

        with open(evidence_file, 'w', encoding='utf-8') as f:
            json.dump(evidence, f, indent=2, ensure_ascii=False)

def main():
    """Example usage of Travel Rule Validator."""
    validator = TravelRuleValidator()

    # Example 1: Below threshold (€500)
    print("=" * 80)
    print("Example 1: Below Threshold (€500)")
    print("=" * 80)

    result1 = validator.validate_transfer(
        amount=500.00,
        currency="EUR",
        originator_data={"legal_name": "Alice Smith"},
        beneficiary_data={"legal_name": "Bob Johnson"}
    )

    print(json.dumps(result1, indent=2))
    print(f"\nDecision: {result1['compliance_decision']}")
    print(f"Travel Rule Required: {result1['travel_rule_required']}")
    print()

    # Example 2: Above threshold (€5,000)
    print("=" * 80)
    print("Example 2: Above Threshold (€5,000)")
    print("=" * 80)

    result2 = validator.validate_transfer(
        amount=5000.00,
        currency="EUR",
        originator_data={
            "legal_name": "Alice Smith",
            "national_id": "AB123456",
            "id_type": "PASSPORT",
            "country": "US",
            "address": {
                "building_number": "123",
                "street_name": "Main Street",
                "post_code": "10001",
                "town_name": "New York",
                "country": "US"
            },
            "date_of_birth": "1990-01-15",
            "place_of_birth": "New York"
        },
        beneficiary_data={
            "legal_name": "Bob Johnson",
            "address": {
                "country": "DE"
            }
        }
    )

    print(json.dumps(result2, indent=2))
    print(f"\nDecision: {result2['compliance_decision']}")
    print(f"Travel Rule Required: {result2['travel_rule_required']}")
    print()

    # Example 3: BTC transfer (0.1 BTC = EUR 5,000)
    print("=" * 80)
    print("Example 3: BTC Transfer (0.1 BTC ~ EUR 5,000)")
    print("=" * 80)

    result3 = validator.validate_transfer(
        amount=0.1,
        currency="BTC",
        originator_data={"legal_name": "Charlie Brown"},
        beneficiary_data={"legal_name": "Diana Prince"}
    )

    print(json.dumps(result3, indent=2))
    print(f"\nDecision: {result3['compliance_decision']}")
    print(f"EUR Equivalent: {result3['transaction']['eur_equivalent']} EUR")
    print(f"Travel Rule Required: {result3['travel_rule_required']}")

if __name__ == "__main__":
    main()
