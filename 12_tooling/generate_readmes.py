#!/usr/bin/env python3
"""
Generate comprehensive README.md files for all 24 roots based on chart.yaml definitions.
Uses 23_compliance/README.md as template structure.
"""

import yaml
from pathlib import Path
from datetime import datetime

# Root definitions with descriptions
ROOTS = {
    "01_ai_layer": "AI/ML services for identity verification, risk scoring, and behavioral analytics",
    "02_audit_logging": "Immutable audit logging with WORM storage, blockchain anchoring, and forensic evidence",
    "03_core": "Core service logic including DID management, proof aggregation, and transaction processing",
    "04_deployment": "Deployment configurations, infrastructure as code, and environment management",
    "05_documentation": "Technical documentation, API specs, architecture diagrams, and compliance docs",
    "06_data_pipeline": "Data ingestion, transformation, validation, and ETL workflows with privacy-preserving processing",
    "07_governance_legal": "Legal compliance framework, governance structures, risk management, and regulatory mappings",
    "08_identity_score": "Identity reputation scoring, risk assessment, and trust metrics calculation",
    "09_meta_identity": "DID management, verifiable credentials, identity storage with hash-only PII policy",
    "10_interoperability": "Cross-chain bridges, protocol adapters, and external system integrations",
    "11_test_simulation": "Test suites, simulation scenarios, load testing, and compliance validation",
    "12_tooling": "Development tools, scripts, CLI utilities, and automation helpers",
    "13_ui_layer": "Frontend components, user interfaces, React applications, and WASM policy evaluation",
    "14_zero_time_auth": "Authentication, authorization, KYC/KYB gateway, and zero-knowledge proof verification",
    "15_infra": "Infrastructure services including databases, caching, messaging, and storage",
    "16_codex": "Structure definitions, schemas, registry manifests, and source-of-truth specifications",
    "17_observability": "Monitoring, logging, tracing, alerting, and SLA tracking",
    "18_data_layer": "Data models, ORM mappings, database migrations, and data access layer",
    "19_adapters": "Protocol adapters for external blockchain networks, legacy systems, and third-party APIs",
    "20_foundation": "Tokenomics, utility token framework, governance mechanisms, and economic models",
    "21_post_quantum_crypto": "Post-quantum cryptography implementations, PQC key management, and quantum-resistant signatures",
    "22_datasets": "Dataset management, synthetic data generation, test fixtures, and data cataloging",
    "23_compliance": "Compliance policies, OPA enforcement, regulatory mappings, and audit frameworks",
    "24_meta_orchestration": "Cross-module orchestration, registry management, CI/CD triggers, and meta-level coordination"
}

README_TEMPLATE = """# {root_number}_{root_name} - {title}

**Version:** 0.1.0 (Bootstrap)
**Last Updated:** {date}
**Maintainer:** {maintainer}
**Status:** Bootstrap Phase
**Classification:** {classification}

## Overview

{description}

This module is part of the SSID (Self-Sovereign Identity) system and implements capabilities defined in `chart.yaml` with governance policies ensuring GDPR, DORA, MiCA, and AMLD6 compliance.

## Purpose

{purpose_section}

## Architecture

### Directory Structure

```
{root_number}_{root_name}/
├── README.md           # This file
├── chart.yaml          # Governance definition (SoT)
├── manifest.yaml       # Implementation specification
└── [implementation files - to be added]
```

### Current Status

**Bootstrap Phase:** Governance infrastructure complete, implementation in progress.

| Component | Status | Notes |
|-----------|--------|-------|
| Governance (chart.yaml) | ✅ Complete | Capabilities, interfaces, policies defined |
| Implementation (manifest.yaml) | ✅ Complete | Entry points, dependencies specified |
| README Documentation | ✅ Complete | This file |
| Implementation Code | 🟡 Planned | See roadmap below |
| Tests | 🟡 Planned | Target 80% coverage |
| CI Integration | 🟡 Planned | OPA + pytest workflows |

## Capabilities

As defined in `chart.yaml`:

{capabilities_section}

## Interfaces

{interfaces_section}

## Policies

{policies_section}

## Dependencies

### Internal Dependencies
{internal_deps_section}

### External Dependencies
{external_deps_section}

## Compliance

{compliance_section}

## Development Roadmap

### Phase 1: Foundation (Current)
- ✅ Governance definitions (chart.yaml)
- ✅ Implementation specs (manifest.yaml)
- ✅ Documentation (README.md)

### Phase 2: Implementation (Weeks 1-4)
- 🟡 Core service implementation
- 🟡 Unit tests (target 80% coverage)
- 🟡 Integration tests

### Phase 3: CI/CD (Weeks 5-6)
- 🟡 GitHub Actions workflows
- 🟡 OPA policy enforcement
- 🟡 Automated testing

### Phase 4: Production Hardening (Weeks 7-8)
- 🟡 Load testing
- 🟡 Security audit
- 🟡 Documentation review

## Getting Started

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt  # When available
```

### Configuration

**Environment Variables:** (To be defined in Phase 2)

### Running Services

*Implementation in progress - see roadmap*

## Testing

*Test suite in progress - see roadmap*

## Contributing

- All changes require review as per `chart.yaml` governance
- Approval required: {approval_required}
- Reviewers: {reviewers}

## References

- Governance Chart: `{root_number}_{root_name}/chart.yaml`
- Implementation Manifest: `{root_number}_{root_name}/manifest.yaml`
- Bootstrap Summary: `02_audit_logging/reports/root_24_governance_bootstrap_summary.md`

## Contact

- **Maintainer:** {maintainer}
- **Classification:** {classification}

---

**Document Classification:** {classification}
**Version:** 0.1.0 (Bootstrap Phase)
**Last Updated:** {date}
**Next Review:** 2025-10-20
"""

def load_chart(root_path: Path) -> dict:
    """Load and parse chart.yaml"""
    chart_file = root_path / "chart.yaml"
    if not chart_file.exists():
        return {}

    with open(chart_file) as f:
        return yaml.safe_load(f)

def generate_readme(root_number: str, root_name: str, base_path: Path) -> str:
    """Generate comprehensive README from chart.yaml"""
    root_path = base_path / f"{root_number}_{root_name}"
    chart = load_chart(root_path)

    # Extract chart data
    spec = chart.get('spec', {})
    metadata = chart.get('metadata', {})
    governance = spec.get('governance', {})

    # Build sections
    capabilities = spec.get('capabilities', [])
    capabilities_text = "\\n".join(f"{i+1}. **{cap}**" for i, cap in enumerate(capabilities))

    interfaces = spec.get('interfaces', [])
    interfaces_text = "\\n".join(
        f"### {iface.get('name', 'unnamed')}\\n"
        f"- **Type:** {iface.get('type', 'N/A')}\\n"
        f"- **Authentication:** {iface.get('authentication', 'N/A')}\\n"
        for iface in interfaces
    ) or "*To be defined*"

    policies = spec.get('policies', [])
    policies_text = "\\n".join(
        f"### {pol.get('name', 'unnamed')}\\n"
        f"- **Enforcement:** {pol.get('enforcement', 'N/A')}\\n"
        f"- **Scope:** {pol.get('scope', 'all')}\\n"
        for pol in policies
    ) or "*To be defined*"

    internal_deps = spec.get('dependencies', {}).get('internal', [])
    internal_deps_text = "\\n".join(f"- `{dep}`" for dep in internal_deps) or "*None*"

    external_deps = spec.get('dependencies', {}).get('external', [])
    external_deps_text = "\\n".join(
        f"- {list(dep.keys())[0]}: {list(dep.values())[0]}" if isinstance(dep, dict) else f"- {dep}"
        for dep in external_deps
    ) or "*None*"

    compliance = spec.get('compliance', {})
    compliance_text = "\\n".join(
        f"**{framework.upper()}:** {', '.join(items) if isinstance(items, list) else items}"
        for framework, items in compliance.items()
    ) or "*To be defined*"

    # Generate content
    title = ROOTS.get(f"{root_number}_{root_name}", root_name.replace('_', ' ').title())
    description = metadata.get('description', ROOTS.get(f"{root_number}_{root_name}", ""))

    content = README_TEMPLATE.format(
        root_number=root_number,
        root_name=root_name,
        title=title,
        date=datetime.now().strftime("%Y-%m-%d"),
        maintainer=governance.get('maintainer', 'TBD'),
        classification=governance.get('data_classification', 'internal').upper(),
        description=description,
        purpose_section=f"- Primary purpose: {description}\\n- See `chart.yaml` for detailed capabilities",
        capabilities_section=capabilities_text or "*To be defined*",
        interfaces_section=interfaces_text,
        policies_section=policies_text,
        internal_deps_section=internal_deps_text,
        external_deps_section=external_deps_text,
        compliance_section=compliance_text,
        approval_required=governance.get('approval_required', 'true'),
        reviewers=', '.join(governance.get('reviewers', []))
    )

    return content

def main():
    """Generate all README files"""
    base_path = Path(__file__).parent.parent

    updated_count = 0
    skipped_count = 0

    for root_key, description in ROOTS.items():
        root_number, root_name = root_key.split('_', 1)
        root_path = base_path / root_key
        readme_path = root_path / "README.md"

        
        if readme_path.exists():
            size = readme_path.stat().st_size
            if size > 100:
                print(f"[SKIP] {root_key}/README.md already comprehensive ({size}B)")
                skipped_count += 1
                continue

        # Generate new README
        content = generate_readme(root_number, root_name, base_path)

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[OK] Generated {root_key}/README.md")
        updated_count += 1

    print(f"\\nSummary:")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total: {len(ROOTS)}")

if __name__ == "__main__":
    main()
