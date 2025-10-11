#!/usr/bin/env python3
"""
mTLS Certificate Manager

Manages X.509 certificates for mutual TLS authentication between SSID modules.
Implements MUST-027-MTLS-AUTH requirement.

Compliance: DORA Art.9, GDPR Art.32, ISO 27001:2022

Usage:
    # Initialize CA
    manager = CertificateManager()
    manager.initialize_ca()

    # Generate server certificate
    manager.generate_server_cert("01_ai_layer", "ai-layer.ssid.internal")

    # Verify mTLS handshake
    is_valid = manager.verify_mtls_handshake(client_cert, server_cert)
"""

import os
import hashlib
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


class CertificateManager:
    """Manages X.509 certificates for mTLS authentication."""

    def __init__(self, config_path: str = "03_core/security/mtls/mtls_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

        # Paths
        self.cert_dir = Path("03_core/security/mtls/certs")
        self.cert_dir.mkdir(parents=True, exist_ok=True)

        self.private_dir = self.cert_dir / "private"
        self.private_dir.mkdir(parents=True, exist_ok=True)

        # Evidence logging
        self.evidence_dir = Path("23_compliance/evidence/mtls")
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        # CA certificate and key
        self.ca_cert: Optional[x509.Certificate] = None
        self.ca_key: Optional[rsa.RSAPrivateKey] = None

    def _load_config(self) -> Dict:
        """Load mTLS configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def initialize_ca(self) -> Tuple[x509.Certificate, rsa.RSAPrivateKey]:
        """
        Initialize Certificate Authority (CA).

        Returns:
            Tuple of (CA certificate, CA private key)
        """
        ca_config = self.config.get('certificate_authority', {})

        # Generate CA private key
        ca_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=ca_config.get('key_size', 4096),
            backend=default_backend()
        )

        # Build CA certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, ca_config.get('country', 'DE')),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, ca_config.get('organization', 'SSID System')),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, ca_config.get('organizational_unit', 'Security')),
            x509.NameAttribute(NameOID.COMMON_NAME, ca_config.get('ca_name', 'SSID Root CA')),
        ])

        ca_cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(ca_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=ca_config.get('validity_days', 3650)))
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    key_encipherment=False,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True
            )
            .sign(ca_key, hashes.SHA256(), backend=default_backend())
        )

        # Save CA certificate and key
        ca_cert_path = self.cert_dir / "ca-cert.pem"
        ca_key_path = self.private_dir / "ca-key.pem"

        with open(ca_cert_path, 'wb') as f:
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

        with open(ca_key_path, 'wb') as f:
            f.write(
                ca_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

        # Set restrictive permissions (Unix)
        if os.name != 'nt':
            os.chmod(ca_cert_path, 0o644)
            os.chmod(ca_key_path, 0o600)

        self.ca_cert = ca_cert
        self.ca_key = ca_key

        self._log_evidence({
            "event": "ca_initialized",
            "ca_cert_path": str(ca_cert_path),
            "ca_cert_fingerprint": self._get_cert_fingerprint(ca_cert),
            "validity_days": ca_config.get('validity_days', 3650)
        })

        return ca_cert, ca_key

    def load_ca(self) -> Tuple[x509.Certificate, rsa.RSAPrivateKey]:
        """Load existing CA certificate and key."""
        ca_cert_path = self.cert_dir / "ca-cert.pem"
        ca_key_path = self.private_dir / "ca-key.pem"

        if not ca_cert_path.exists() or not ca_key_path.exists():
            raise FileNotFoundError("CA certificate or key not found. Run initialize_ca() first.")

        with open(ca_cert_path, 'rb') as f:
            self.ca_cert = x509.load_pem_x509_certificate(f.read(), backend=default_backend())

        with open(ca_key_path, 'rb') as f:
            self.ca_key = serialization.load_pem_private_key(
                f.read(),
                password=None,
                backend=default_backend()
            )

        return self.ca_cert, self.ca_key

    def generate_server_cert(
        self,
        module_id: str,
        common_name: str,
        san_dns: Optional[List[str]] = None,
        validity_days: int = 365
    ) -> Tuple[x509.Certificate, rsa.RSAPrivateKey]:
        """
        Generate server certificate for a module.

        Args:
            module_id: Module identifier (e.g., "01_ai_layer")
            common_name: Certificate CN (e.g., "ai-layer.ssid.internal")
            san_dns: Subject Alternative Names (DNS)
            validity_days: Certificate validity period

        Returns:
            Tuple of (server certificate, server private key)
        """
        if self.ca_cert is None or self.ca_key is None:
            self.load_ca()

        server_config = self.config.get('server_certificates', {}).get('template', {})

        # Generate server private key
        server_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=server_config.get('key_size', 2048),
            backend=default_backend()
        )

        # Build server certificate
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, server_config.get('country', 'DE')),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, server_config.get('organization', 'SSID System')),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, server_config.get('organizational_unit', 'Inter-Module Communication')),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])

        # Subject Alternative Names
        san_list = [x509.DNSName(common_name)]
        if san_dns:
            san_list.extend([x509.DNSName(dns) for dns in san_dns])

        server_cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(self.ca_cert.subject)
            .public_key(server_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=validity_days))
            .add_extension(
                x509.SubjectAlternativeName(san_list),
                critical=False
            )
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None),
                critical=True
            )
            .add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_encipherment=True,
                    key_cert_sign=False,
                    crl_sign=False,
                    content_commitment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    encipher_only=False,
                    decipher_only=False
                ),
                critical=True
            )
            .add_extension(
                x509.ExtendedKeyUsage([
                    ExtendedKeyUsageOID.SERVER_AUTH,
                    ExtendedKeyUsageOID.CLIENT_AUTH
                ]),
                critical=False
            )
            .sign(self.ca_key, hashes.SHA256(), backend=default_backend())
        )

        # Save server certificate and key
        cert_filename = f"{module_id.replace('/', '_')}-cert.pem"
        key_filename = f"{module_id.replace('/', '_')}-key.pem"

        cert_path = self.cert_dir / cert_filename
        key_path = self.private_dir / key_filename

        with open(cert_path, 'wb') as f:
            f.write(server_cert.public_bytes(serialization.Encoding.PEM))

        with open(key_path, 'wb') as f:
            f.write(
                server_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

        # Set restrictive permissions
        if os.name != 'nt':
            os.chmod(cert_path, 0o644)
            os.chmod(key_path, 0o600)

        self._log_evidence({
            "event": "server_cert_generated",
            "module_id": module_id,
            "common_name": common_name,
            "cert_path": str(cert_path),
            "cert_fingerprint": self._get_cert_fingerprint(server_cert),
            "validity_days": validity_days,
            "san_dns": san_dns or []
        })

        return server_cert, server_key

    def verify_certificate(self, cert: x509.Certificate) -> Dict[str, Any]:
        """
        Verify certificate against CA and perform validation checks.

        Args:
            cert: X.509 certificate to verify

        Returns:
            Validation result dictionary
        """
        if self.ca_cert is None:
            self.load_ca()

        result = {
            "timestamp": datetime.now().isoformat() + "Z",
            "certificate_subject": cert.subject.rfc4514_string(),
            "certificate_issuer": cert.issuer.rfc4514_string(),
            "certificate_fingerprint": self._get_cert_fingerprint(cert),
            "checks": {}
        }

        # Check 1: Certificate not expired
        now = datetime.utcnow()
        result["checks"]["not_expired"] = {
            "passed": cert.not_valid_before <= now <= cert.not_valid_after,
            "not_before": cert.not_valid_before.isoformat(),
            "not_after": cert.not_valid_after.isoformat()
        }

        # Check 2: Signed by trusted CA
        try:
            self.ca_cert.public_key().verify(
                cert.signature,
                cert.tbs_certificate_bytes,
                cert.signature_algorithm_parameters
            )
            result["checks"]["signed_by_ca"] = {"passed": True}
        except Exception as e:
            result["checks"]["signed_by_ca"] = {"passed": False, "error": str(e)}

        # Check 3: Issuer matches CA
        result["checks"]["issuer_matches_ca"] = {
            "passed": cert.issuer == self.ca_cert.subject
        }

        # Overall validation
        result["valid"] = all(
            check.get("passed", False)
            for check in result["checks"].values()
        )

        self._log_evidence({
            "event": "certificate_verified",
            "result": result
        })

        return result

    def verify_mtls_handshake(
        self,
        client_cert: x509.Certificate,
        server_cert: x509.Certificate
    ) -> Dict[str, Any]:
        """
        Verify mutual TLS handshake between client and server.

        Args:
            client_cert: Client X.509 certificate
            server_cert: Server X.509 certificate

        Returns:
            mTLS verification result
        """
        result = {
            "timestamp": datetime.now().isoformat() + "Z",
            "client_verification": self.verify_certificate(client_cert),
            "server_verification": self.verify_certificate(server_cert),
            "mtls_handshake_valid": False
        }

        # mTLS is valid if both certificates are valid
        result["mtls_handshake_valid"] = (
            result["client_verification"]["valid"] and
            result["server_verification"]["valid"]
        )

        self._log_evidence({
            "event": "mtls_handshake_verified",
            "result": result
        })

        return result

    def _get_cert_fingerprint(self, cert: x509.Certificate) -> str:
        """Get SHA-256 fingerprint of certificate."""
        return cert.fingerprint(hashes.SHA256()).hex()

    def _log_evidence(self, event_data: Dict[str, Any]) -> None:
        """Log mTLS event to audit trail."""
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        evidence_file = self.evidence_dir / f"mtls_event_{timestamp}.json"

        # Add evidence hash
        event_hash = hashlib.sha256(
            json.dumps(event_data, sort_keys=True).encode()
        ).hexdigest()

        evidence = {
            "event_data": event_data,
            "audit_metadata": {
                "timestamp": event_data.get("timestamp", datetime.now().isoformat() + "Z"),
                "event_hash_sha256": event_hash,
                "compliance_requirement": "MUST-027-MTLS-AUTH"
            }
        }

        with open(evidence_file, 'w', encoding='utf-8') as f:
            json.dump(evidence, f, indent=2, ensure_ascii=False)


def main():
    """Example usage of Certificate Manager."""
    manager = CertificateManager()

    print("=" * 80)
    print("mTLS Certificate Manager - Example Usage")
    print("=" * 80)
    print()

    # Step 1: Initialize CA
    print("[1/3] Initializing Certificate Authority...")
    ca_cert, ca_key = manager.initialize_ca()
    print(f"  CA Certificate: {manager.cert_dir / 'ca-cert.pem'}")
    print(f"  CA Fingerprint: {manager._get_cert_fingerprint(ca_cert)}")
    print()

    # Step 2: Generate server certificates for core modules
    print("[2/3] Generating server certificates...")

    modules = [
        ("01_ai_layer", "ai-layer.ssid.internal", ["localhost"]),
        ("08_identity_score", "identity-score.ssid.internal", ["localhost"]),
        ("09_meta_identity", "meta-identity.ssid.internal", ["localhost"])
    ]

    certs = []
    for module_id, cn, san_dns in modules:
        cert, key = manager.generate_server_cert(module_id, cn, san_dns)
        certs.append((module_id, cert))
        print(f"  {module_id}: {cn}")
        print(f"    Fingerprint: {manager._get_cert_fingerprint(cert)}")

    print()

    # Step 3: Verify mTLS handshake
    print("[3/3] Verifying mTLS handshake...")

    if len(certs) >= 2:
        client_module, client_cert = certs[0]
        server_module, server_cert = certs[1]

        result = manager.verify_mtls_handshake(client_cert, server_cert)

        print(f"  Client: {client_module}")
        print(f"  Server: {server_module}")
        print(f"  mTLS Valid: {result['mtls_handshake_valid']}")
        print()

    print("=" * 80)
    print("Evidence saved to: 23_compliance/evidence/mtls/")
    print("=" * 80)


if __name__ == "__main__":
    main()
