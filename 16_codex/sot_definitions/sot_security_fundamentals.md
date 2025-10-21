# Source of Truth: Security Fundamentals

This document defines the fundamental security rules for the SSID system.
Every rule must be enforced through corresponding OPA policies.

---

## Authentication & Authorization

All user authentication must use multi-factor authentication.
Authorization decisions must be logged in immutable audit trails.
Session tokens must expire after 30 minutes of inactivity.
Role-based access control must be enforced at all API endpoints.

## Data Protection

Personal data must be encrypted at rest using AES-256.
All network communication must use TLS 1.3 or higher.
Data retention policies must comply with GDPR requirements.
User data must never be shared without explicit consent.

## Audit & Compliance

All security events must be logged to WORM storage.
Audit logs must be retained for minimum 12 months.
Compliance checks must run before every deployment.
Policy violations must trigger immediate alerts.

## Structure Enforcement

The 24-layer structure must be validated before commits.
Cross-layer dependencies must follow the approved hierarchy.
No circular dependencies are allowed between layers.
Structure violations must block CI/CD pipeline execution.

## Cryptographic Requirements

All cryptographic hashes must use SHA-512 or BLAKE2b.
Digital signatures must use Ed25519 or stronger algorithms.
Random number generation must use cryptographically secure sources.
Key rotation must occur every 90 days for production systems.

---

*This document represents binding rules for SSID compliance.*
*Every rule must have corresponding enforcement in 23_compliance/policies/*
