#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Findings-to-Registry Converter - Governance Integration
SSID Phase 2 Implementation

Purpose:
- Convert CI/CD findings into structured registry format
- Enable governance-ready issue tracking
- Map findings to regulations (GDPR, DORA, MiCA, AMLD6)
- Generate audit-ready evidence chains

Architecture:
CI/CD Findings (JSON) → Converter → Registry Format (YAML/JSON) → Governance System

Flow:
1. Badge violations → Findings
2. Dependency cycles → Findings
3. Test failures → Findings
4. Findings → Issue Registry
5. Issue Registry → Governance Votes

Integration:
- .github/workflows/ci_anti_gaming.yml → generates findings
- 23_compliance/evidence/links/ → stores mappings
- 07_governance_legal/ → consumes findings for policy decisions
"""

import json
import yaml
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum

class FindingSeverity(Enum):
    """Severity levels matching CI/CD outputs"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class FindingStatus(Enum):
    """Finding lifecycle states"""
    OPEN = "open"
    IN_REVIEW = "in_review"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"  # Accepted risk
    WONT_FIX = "wont_fix"

class RegulationMapping(Enum):
    """EU regulatory frameworks"""
    GDPR = "GDPR"
    DORA = "DORA"
    MICA = "MiCA"
    AMLD6 = "AMLD6"
    AIACT = "AI-Act"

@dataclass
class Finding:
    """
    Represents a single finding from CI/CD or audit.

    Fields match governance requirements:
    - finding_id: Unique identifier
    - source: Where finding originated (ci_workflow, manual_audit, etc.)
    - severity: Critical/High/Medium/Low/Info
    - title: Short description
    - description: Detailed explanation
    - affected_entities: List of modules/files/components
    - evidence_refs: References to supporting evidence
    - regulations: Relevant regulatory frameworks
    - remediation: Suggested fix
    - status: Lifecycle state
    - metadata: Additional context
    """
    finding_id: str
    source: str
    severity: str
    title: str
    description: str
    affected_entities: List[str]
    evidence_refs: List[str]
    regulations: List[str]
    remediation: str
    status: str
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_yaml(self) -> str:
        """Export as YAML for human review"""
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)

@dataclass
class IssueRegistry:
    """
    Registry of all findings for governance tracking.

    Fields:
    - registry_id: Unique registry identifier
    - created_at: Registry creation timestamp
    - findings: List of Finding objects
    - statistics: Summary statistics
    """
    registry_id: str
    created_at: str
    findings: List[Finding]
    statistics: Dict[str, int]

    def to_dict(self) -> Dict:
        return {
            "registry_id": self.registry_id,
            "created_at": self.created_at,
            "statistics": self.statistics,
            "findings": [f.to_dict() for f in self.findings]
        }

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)

class FindingsToRegistryConverter:
    """
    Converts CI/CD findings into governance-ready issue registry.

    Responsibilities:
    1. Parse findings from JSON (badge violations, cycle violations, test failures)
    2. Classify by severity and regulation
    3. Generate unique finding IDs
    4. Create evidence chain links
    5. Output registry in YAML/JSON formats
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.findings_dir = repo_root / "23_compliance" / "anti_gaming" / "violations"
        self.registry_dir = repo_root / "23_compliance" / "evidence" / "issue_registry"
        self.registry_dir.mkdir(parents=True, exist_ok=True)

        self.links_dir = repo_root / "23_compliance" / "evidence" / "links"
        self.links_dir.mkdir(parents=True, exist_ok=True)

    def parse_badge_violations(self, violations_file: Path) -> List[Finding]:
        """
        Parse badge integrity violations into Finding objects.

        Args:
            violations_file: Path to badge_violations_*.json file

        Returns:
            List of Finding objects
        """
        findings = []

        with open(violations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        violations = data.get("violations", [])

        for violation in violations:
            finding = Finding(
                finding_id=self._generate_finding_id(violation.get("violation_id", "unknown")),
                source="ci_anti_gaming_badge_integrity",
                severity=violation.get("severity", "medium"),
                title=f"Badge Integrity Violation: {violation.get('violation_type', 'unknown')}",
                description=violation.get("description", ""),
                affected_entities=violation.get("affected_entities", []),
                evidence_refs=[
                    violation.get("violation_id", ""),
                    violation.get("evidence_path", "") if violation.get("evidence_path") else ""
                ],
                regulations=self._map_to_regulations("badge_integrity"),
                remediation=self._suggest_remediation(violation.get("violation_type", "")),
                status=FindingStatus.OPEN.value,
                created_at=violation.get("timestamp", datetime.now(timezone.utc).isoformat()),
                updated_at=datetime.now(timezone.utc).isoformat(),
                metadata={
                    "badge_id": violation.get("badge_id"),
                    "violation_type": violation.get("violation_type")
                }
            )
            findings.append(finding)

        return findings

    def parse_dependency_violations(self, violations_file: Path) -> List[Finding]:
        """
        Parse circular dependency violations into Finding objects.

        Args:
            violations_file: Path to dependency_violations_*.json file

        Returns:
            List of Finding objects
        """
        findings = []

        with open(violations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        violations = data.get("violations", [])

        for violation in violations:
            cycle = violation.get("cycle", [])
            cycle_str = " → ".join(cycle)

            finding = Finding(
                finding_id=self._generate_finding_id(violation.get("violation_id", "unknown")),
                source="ci_anti_gaming_dependency_graph",
                severity=FindingSeverity.CRITICAL.value,  # Always critical
                title=f"Circular Dependency Detected",
                description=f"Circular dependency found: {cycle_str}. {violation.get('description', '')}",
                affected_entities=cycle,
                evidence_refs=[
                    violation.get("violation_id", ""),
                    "graph:dependency_graph.svg"
                ],
                regulations=self._map_to_regulations("circular_dependency"),
                remediation="Break the circular dependency by refactoring module dependencies. Consider introducing an intermediary module or inverting the dependency direction.",
                status=FindingStatus.OPEN.value,
                created_at=violation.get("timestamp", datetime.now(timezone.utc).isoformat()),
                updated_at=datetime.now(timezone.utc).isoformat(),
                metadata={
                    "cycle": cycle,
                    "violation_type": violation.get("violation_type")
                }
            )
            findings.append(finding)

        return findings

    def _generate_finding_id(self, violation_id: str) -> str:
        """
        Generate unique finding ID.

        Format: FIND-{hash[:8]}-{timestamp}
        """
        hash_input = f"{violation_id}_{datetime.now(timezone.utc).isoformat()}"
        hash_val = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()[:8]
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d')
        return f"FIND-{hash_val}-{timestamp}"

    def _map_to_regulations(self, violation_type: str) -> List[str]:
        """
        Map violation types to relevant EU regulations.

        Args:
            violation_type: Type of violation (e.g., "badge_integrity", "circular_dependency")

        Returns:
            List of relevant regulation codes
        """
        mapping = {
            "badge_integrity": [
                RegulationMapping.GDPR.value,  # Art. 5 (Accuracy)
                RegulationMapping.DORA.value,  # ICT risk management
                RegulationMapping.MICA.value   # Fraud prevention
            ],
            "circular_dependency": [
                RegulationMapping.DORA.value,  # System resilience
                RegulationMapping.AIACT.value  # Technical robustness
            ],
            "duplicate_identity": [
                RegulationMapping.GDPR.value,  # Art. 5 (Integrity)
                RegulationMapping.AMLD6.value  # Identity verification
            ],
            "overfitting": [
                RegulationMapping.AIACT.value,  # Model accuracy
                RegulationMapping.GDPR.value   # Art. 22 (Automated decisions)
            ]
        }

        return mapping.get(violation_type, [])

    def _suggest_remediation(self, violation_type: str) -> str:
        """
        Suggest remediation steps for violation types.

        Args:
            violation_type: Type of violation

        Returns:
            Human-readable remediation suggestion
        """
        remediation_map = {
            "missing_registry": "Initialize registry locks in 24_meta_orchestration/registry/locks/. Run `python tools/init_registry.py`.",
            "duplicate_badge_hash": "Investigate badge issuance process. Ensure unique badge identifiers and versioning.",
            "badge_without_implementation": "Add implementation files to shard directory. Follow shard structure guidelines.",
            "deprecated_badge_active": "Remove or update deprecated badge. Update chart.yaml status field.",
            "circular_dependency": "Refactor module dependencies to break cycle. Consider dependency inversion or intermediary modules.",
            "missing_audit_anchor": "Initialize audit registry in 02_audit_logging/evidence/registry/. Run `python tools/init_audit_registry.py`."
        }

        return remediation_map.get(violation_type, "Review violation details and consult compliance documentation.")

    def create_registry(
        self,
        findings: List[Finding],
        registry_name: Optional[str] = None
    ) -> IssueRegistry:
        """
        Create an issue registry from findings.

        Args:
            findings: List of Finding objects
            registry_name: Optional registry name (default: timestamped)

        Returns:
            IssueRegistry object
        """
        if not registry_name:
            registry_name = f"registry_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        registry_id = f"REG-{hashlib.sha256(registry_name.encode()).hexdigest()[:12]}"

        # Calculate statistics
        statistics = {
            "total_findings": len(findings),
            "critical": sum(1 for f in findings if f.severity == FindingSeverity.CRITICAL.value),
            "high": sum(1 for f in findings if f.severity == FindingSeverity.HIGH.value),
            "medium": sum(1 for f in findings if f.severity == FindingSeverity.MEDIUM.value),
            "low": sum(1 for f in findings if f.severity == FindingSeverity.LOW.value),
            "open": sum(1 for f in findings if f.status == FindingStatus.OPEN.value),
            "resolved": sum(1 for f in findings if f.status == FindingStatus.RESOLVED.value)
        }

        return IssueRegistry(
            registry_id=registry_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            findings=findings,
            statistics=statistics
        )

    def export_registry(
        self,
        registry: IssueRegistry,
        output_format: str = "yaml"
    ) -> Path:
        """
        Export registry to file.

        Args:
            registry: IssueRegistry object
            output_format: "yaml" or "json"

        Returns:
            Path to exported file
        """
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        filename = f"issue_registry_{timestamp}.{output_format}"
        output_file = self.registry_dir / filename

        if output_format == "yaml":
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(registry.to_yaml())
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(registry.to_dict(), f, indent=2, sort_keys=True)

        return output_file

    def create_evidence_links(
        self,
        registry: IssueRegistry
    ) -> Path:
        """
        Create evidence link mappings (hash ↔ finding ↔ regulation).

        Args:
            registry: IssueRegistry object

        Returns:
            Path to evidence links file
        """
        links = {}

        for finding in registry.findings:
            link_entry = {
                "finding_id": finding.finding_id,
                "severity": finding.severity,
                "regulations": finding.regulations,
                "evidence_refs": finding.evidence_refs,
                "affected_entities": finding.affected_entities,
                "created_at": finding.created_at
            }

            # Create hash → finding link
            for entity in finding.affected_entities:
                entity_hash = hashlib.sha256(entity.encode()).hexdigest()
                if entity_hash not in links:
                    links[entity_hash] = []
                links[entity_hash].append(link_entry)

            # Create evidence → finding link
            for evidence_ref in finding.evidence_refs:
                if evidence_ref:
                    evidence_hash = hashlib.sha256(evidence_ref.encode()).hexdigest()
                    if evidence_hash not in links:
                        links[evidence_hash] = []
                    links[evidence_hash].append(link_entry)

        # Write links
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        links_file = self.links_dir / f"evidence_links_{timestamp}.json"

        with open(links_file, 'w', encoding='utf-8') as f:
            json.dump(links, f, indent=2, sort_keys=True)

        return links_file

    def process_ci_outputs(self) -> IssueRegistry:
        """
        Process all CI/CD outputs and generate unified issue registry.

        Scans:
        - 23_compliance/anti_gaming/violations/badge_violations_*.json
        - 23_compliance/anti_gaming/violations/dependency_violations_*.json

        Returns:
            IssueRegistry object with all findings
        """
        all_findings = []

        # Parse badge violations
        badge_violation_files = sorted(self.findings_dir.glob("badge_violations_*.json"))
        for file in badge_violation_files:
            findings = self.parse_badge_violations(file)
            all_findings.extend(findings)

        # Parse dependency violations
        dependency_violation_files = sorted(self.findings_dir.glob("dependency_violations_*.json"))
        for file in dependency_violation_files:
            findings = self.parse_dependency_violations(file)
            all_findings.extend(findings)

        # Create registry
        registry = self.create_registry(all_findings)

        # Export registry
        self.export_registry(registry, output_format="yaml")
        self.export_registry(registry, output_format="json")

        # Create evidence links
        self.create_evidence_links(registry)

        return registry

def main():
    """CLI entry point"""
    repo_root = Path(__file__).resolve().parents[2]

    converter = FindingsToRegistryConverter(repo_root)

    print("Processing CI/CD outputs...")
    registry = converter.process_ci_outputs()

    print(json.dumps(registry.statistics, indent=2))
    print(f"\nRegistry created: {registry.registry_id}")
    print(f"Total findings: {registry.statistics['total_findings']}")
    print(f"Critical: {registry.statistics['critical']}")
    print(f"High: {registry.statistics['high']}")
    print(f"Medium: {registry.statistics['medium']}")
    print(f"Low: {registry.statistics['low']}")

if __name__ == "__main__":
    main()
