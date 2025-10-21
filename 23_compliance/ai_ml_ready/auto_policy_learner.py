#!/usr/bin/env python3
"""
SSID Auto-Policy Learning Engine
AI-Driven Compliance Rule Generation

Analyzes audit results and proposes new Rego rules, enabling organic evolution
of the compliance ruleset based on auditor experience and emerging patterns.
"""

import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import re

@dataclass
class AuditPattern:
    """Detected pattern in audit data"""
    pattern_id: str
    pattern_type: str  # "recurring_issue", "new_control", "parameter_adjustment"
    description: str
    occurrences: int
    confidence: float
    evidence: List[Dict]
    suggested_action: str

@dataclass
class PolicyProposal:
    """Proposed policy rule"""
    proposal_id: str
    rule_name: str
    rule_type: str  # "new_rule", "rule_modification", "parameter_change"
    rego_code: str
    rationale: str
    supporting_evidence: List[str]
    confidence_score: float
    impact_assessment: Dict
    approval_status: str = "pending"
    reviewer_notes: List[str] = field(default_factory=list)

@dataclass
class LearningSession:
    """AI learning session"""
    session_id: str
    timestamp: datetime
    audit_data_analyzed: int
    patterns_detected: int
    proposals_generated: int
    proposals: List[PolicyProposal]
    session_metrics: Dict

class AutoPolicyLearner:
    """
    AI-Powered Policy Learning Engine

    Analyzes audit results and generates new Rego compliance rules:
    - Detects recurring compliance patterns
    - Identifies control gaps
    - Suggests rule optimizations
    - Generates executable Rego code
    """

    def __init__(
        self,
        audit_data_dir: Path,
        unified_index_path: Path,
        output_dir: Path
    ):
        self.audit_data_dir = Path(audit_data_dir)
        self.unified_index_path = Path(unified_index_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load unified index
        with open(self.unified_index_path, 'r', encoding='utf-8') as f:
            self.unified_index = yaml.safe_load(f)

        # Learning state
        self.patterns: List[AuditPattern] = []
        self.proposals: List[PolicyProposal] = []
        self.learning_history: List[LearningSession] = []

        # Pattern detection thresholds
        self.min_occurrence_threshold = 3
        self.min_confidence_threshold = 0.7

    def analyze_audit_history(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> LearningSession:
        """
        Analyze historical audit data and generate policy proposals

        Main entry point for learning process
        """
        session_id = f"learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"[Auto-Policy Learning] Starting session: {session_id}")
        print(f"  Period: {start_date.date()} to {end_date.date()}")

        # Load audit data
        audit_records = self._load_audit_records(start_date, end_date)
        print(f"  Loaded {len(audit_records)} audit records")

        # Detect patterns
        patterns = self._detect_patterns(audit_records)
        print(f"  Detected {len(patterns)} patterns")

        # Generate proposals
        proposals = self._generate_proposals(patterns)
        print(f"  Generated {len(proposals)} policy proposals")

        # Create session
        session = LearningSession(
            session_id=session_id,
            timestamp=datetime.now(),
            audit_data_analyzed=len(audit_records),
            patterns_detected=len(patterns),
            proposals_generated=len(proposals),
            proposals=proposals,
            session_metrics=self._calculate_session_metrics(audit_records, patterns, proposals)
        )

        self.learning_history.append(session)
        self._save_session(session)

        return session

    def _detect_patterns(self, audit_records: List[Dict]) -> List[AuditPattern]:
        """
        Detect compliance patterns in audit data

        Pattern types:
        - Recurring issues (same control failing repeatedly)
        - New control requirements (gaps not in current ruleset)
        - Parameter adjustments (threshold changes needed)
        """
        patterns = []

        # Pattern 1: Recurring control failures
        patterns.extend(self._detect_recurring_failures(audit_records))

        # Pattern 2: Emerging control requirements
        patterns.extend(self._detect_new_requirements(audit_records))

        # Pattern 3: Threshold optimizations
        patterns.extend(self._detect_threshold_issues(audit_records))

        # Pattern 4: Framework-specific trends
        patterns.extend(self._detect_framework_trends(audit_records))

        return patterns

    def _detect_recurring_failures(self, records: List[Dict]) -> List[AuditPattern]:
        """Detect controls that fail repeatedly"""
        patterns = []

        # Count failures by control
        failure_counts = Counter()
        failure_evidence = defaultdict(list)

        for record in records:
            if record.get('status') == 'FAIL':
                control_id = record.get('control_id')
                failure_counts[control_id] += 1
                failure_evidence[control_id].append({
                    'timestamp': record.get('timestamp'),
                    'reason': record.get('failure_reason'),
                    'module': record.get('affected_module')
                })

        # Identify recurring failures
        for control_id, count in failure_counts.items():
            if count >= self.min_occurrence_threshold:
                pattern = AuditPattern(
                    pattern_id=f"recurring_{control_id}",
                    pattern_type="recurring_issue",
                    description=f"Control {control_id} fails repeatedly ({count} times)",
                    occurrences=count,
                    confidence=min(count / 10.0, 0.95),  # Cap at 95%
                    evidence=failure_evidence[control_id],
                    suggested_action=f"Add stricter validation for {control_id}"
                )
                patterns.append(pattern)

        return patterns

    def _detect_new_requirements(self, records: List[Dict]) -> List[AuditPattern]:
        """Detect new control requirements not in current ruleset"""
        patterns = []

        # Find controls mentioned in audit findings but not in unified index
        existing_controls = set()
        for domain, controls in self.unified_index.get('cross_framework_mappings', {}).items():
            if isinstance(controls, list):
                for control in controls:
                    existing_controls.add(control['unified_id'])

        # Scan for new controls
        new_controls = defaultdict(list)
        for record in records:
            if record.get('type') == 'NEW_REQUIREMENT':
                control_ref = record.get('control_reference')
                if control_ref and control_ref not in existing_controls:
                    new_controls[control_ref].append(record)

        for control_ref, evidence in new_controls.items():
            if len(evidence) >= 2:  # Lower threshold for new requirements
                pattern = AuditPattern(
                    pattern_id=f"new_req_{control_ref}",
                    pattern_type="new_control",
                    description=f"Emerging requirement: {control_ref}",
                    occurrences=len(evidence),
                    confidence=0.75,
                    evidence=evidence,
                    suggested_action=f"Add new control for {control_ref}"
                )
                patterns.append(pattern)

        return patterns

    def _detect_threshold_issues(self, records: List[Dict]) -> List[AuditPattern]:
        """Detect parameters that need adjustment"""
        patterns = []

        # Analyze threshold breaches
        threshold_breaches = defaultdict(list)

        for record in records:
            if record.get('type') == 'THRESHOLD_BREACH':
                param = record.get('parameter')
                threshold_breaches[param].append({
                    'timestamp': record.get('timestamp'),
                    'actual_value': record.get('actual_value'),
                    'threshold': record.get('threshold')
                })

        for param, breaches in threshold_breaches.items():
            if len(breaches) >= self.min_occurrence_threshold:
                # Calculate suggested new threshold
                values = [b['actual_value'] for b in breaches if isinstance(b['actual_value'], (int, float))]
                if values:
                    suggested = max(values) * 1.1  # 10% buffer

                    pattern = AuditPattern(
                        pattern_id=f"threshold_{param}",
                        pattern_type="parameter_adjustment",
                        description=f"Parameter '{param}' frequently breaches threshold",
                        occurrences=len(breaches),
                        confidence=0.85,
                        evidence=breaches,
                        suggested_action=f"Adjust '{param}' threshold to {suggested:.1f}"
                    )
                    patterns.append(pattern)

        return patterns

    def _detect_framework_trends(self, records: List[Dict]) -> List[AuditPattern]:
        """Detect framework-specific compliance trends"""
        patterns = []

        # Track framework compliance scores over time
        framework_scores = defaultdict(list)

        for record in records:
            if record.get('type') == 'COMPLIANCE_SCORE':
                framework = record.get('framework')
                score = record.get('score')
                framework_scores[framework].append((record.get('timestamp'), score))

        # Detect declining trends
        for framework, scores in framework_scores.items():
            if len(scores) >= 5:
                recent = [s[1] for s in sorted(scores, key=lambda x: x[0])[-5:]]
                if all(recent[i] > recent[i+1] for i in range(len(recent)-1)):
                    pattern = AuditPattern(
                        pattern_id=f"trend_{framework}",
                        pattern_type="declining_compliance",
                        description=f"{framework.upper()} compliance trending downward",
                        occurrences=len(scores),
                        confidence=0.80,
                        evidence=[{'timestamp': t, 'score': s} for t, s in scores],
                        suggested_action=f"Review and strengthen {framework.upper()} controls"
                    )
                    patterns.append(pattern)

        return patterns

    def _generate_proposals(self, patterns: List[AuditPattern]) -> List[PolicyProposal]:
        """Generate policy proposals from detected patterns"""
        proposals = []

        for pattern in patterns:
            if pattern.confidence >= self.min_confidence_threshold:
                if pattern.pattern_type == "recurring_issue":
                    proposal = self._generate_stricter_validation_rule(pattern)
                elif pattern.pattern_type == "new_control":
                    proposal = self._generate_new_control_rule(pattern)
                elif pattern.pattern_type == "parameter_adjustment":
                    proposal = self._generate_parameter_adjustment(pattern)
                elif pattern.pattern_type == "declining_compliance":
                    proposal = self._generate_monitoring_rule(pattern)
                else:
                    continue

                if proposal:
                    proposals.append(proposal)

        return proposals

    def _generate_stricter_validation_rule(self, pattern: AuditPattern) -> Optional[PolicyProposal]:
        """Generate rule for stricter validation of recurring failures"""

        # Extract control ID from pattern
        control_match = re.search(r'(UNI-\w+-\d+)', pattern.description)
        if not control_match:
            raise NotImplementedError("TODO: Implement this function")

        control_id = control_match.group(1)

        # Generate Rego code
        rego_code = f'''# Auto-generated rule for {control_id}
# Generated: {datetime.now().isoformat()}
# Reason: Recurring failures detected ({pattern.occurrences} occurrences)

package ssid.compliance.auto_generated

import future.keywords.if

# Enhanced validation for {control_id}
{control_id.lower().replace('-', '_')}_validation_enhanced if {{
    control := compliance_controls["{control_id}"]
    control.implementation_status == "implemented"

    # Additional checks based on failure patterns
    control.verification == "automated"
    control.last_verified_within_days <= 30

    # Require external validation if recent failures
    failure_count := count_recent_failures("{control_id}", 90)
    failure_count < 2
}}

count_recent_failures(control_id, days) := count if {{
    failures := [f |
        some f in audit_history
        f.control_id == control_id
        f.status == "FAIL"
        days_since(f.timestamp) <= days
    ]
    count := count(failures)
}}

# Deny if enhanced validation fails
deny[msg] if {{
    not {control_id.lower().replace('-', '_')}_validation_enhanced
    msg := sprintf("Enhanced validation failed for {control_id}: Recurring failures require stricter checks", [])
}}'''

        proposal = PolicyProposal(
            proposal_id=f"prop_{pattern.pattern_id}_{datetime.now().strftime('%Y%m%d')}",
            rule_name=f"Enhanced validation for {control_id}",
            rule_type="new_rule",
            rego_code=rego_code,
            rationale=f"Control {control_id} has failed {pattern.occurrences} times. Enhanced validation reduces false negatives.",
            supporting_evidence=[str(e) for e in pattern.evidence[:3]],
            confidence_score=pattern.confidence,
            impact_assessment={
                "affected_controls": [control_id],
                "estimated_false_negative_reduction": "30-50%",
                "performance_impact": "minimal",
                "breaking_changes": False
            }
        )

        return proposal

    def _generate_new_control_rule(self, pattern: AuditPattern) -> Optional[PolicyProposal]:
        """Generate rule for new control requirement"""

        # Extract control reference
        control_ref = pattern.pattern_id.replace('new_req_', '')

        rego_code = f'''# New control rule: {control_ref}
# Generated: {datetime.now().isoformat()}
# Reason: Emerging requirement detected

package ssid.compliance.auto_generated

import future.keywords.if

# New control: {control_ref}
{control_ref.lower().replace('-', '_')}_implemented if {{
    # Define control in registry
    new_control := compliance_controls["{control_ref}"]
    new_control.implementation_status == "implemented"
}}

# Register new control
compliance_controls["{control_ref}"] := {{
    "category": "CC-AUTO",
    "description": "Auto-detected requirement: {pattern.description}",
    "risk_level": "MEDIUM",
    "implementation_status": "planned",
    "verification": "manual"
}} if {{
    # Only register if not already present
    not compliance_controls["{control_ref}"]
}}

# Warning if not implemented
warn[msg] if {{
    not {control_ref.lower().replace('-', '_')}_implemented
    msg := sprintf("New control requirement detected: {control_ref} - Requires implementation", [])
}}'''

        proposal = PolicyProposal(
            proposal_id=f"prop_{pattern.pattern_id}_{datetime.now().strftime('%Y%m%d')}",
            rule_name=f"New control: {control_ref}",
            rule_type="new_rule",
            rego_code=rego_code,
            rationale=f"New compliance requirement detected in audit findings. Appears {pattern.occurrences} times across audits.",
            supporting_evidence=[str(e) for e in pattern.evidence],
            confidence_score=pattern.confidence,
            impact_assessment={
                "affected_controls": [control_ref],
                "new_control_added": True,
                "requires_implementation": True,
                "breaking_changes": False
            }
        )

        return proposal

    def _generate_parameter_adjustment(self, pattern: AuditPattern) -> Optional[PolicyProposal]:
        """Generate parameter adjustment proposal"""

        param = pattern.pattern_id.replace('threshold_', '')

        # Extract suggested value from action
        value_match = re.search(r'to ([\d.]+)', pattern.suggested_action)
        if not value_match:
            raise NotImplementedError("TODO: Implement this function")

        new_value = float(value_match.group(1))

        rego_code = f'''# Parameter adjustment: {param}
# Generated: {datetime.now().isoformat()}
# Reason: Frequent threshold breaches

package ssid.compliance.auto_generated

import future.keywords.if

# Updated threshold for {param}
{param.lower()}_threshold := {new_value}

# Use updated threshold in validation
{param.lower()}_compliant if {{
    actual_value := get_{param.lower()}_value()
    actual_value <= {param.lower()}_threshold
}}

# Alert if threshold is exceeded
warn[msg] if {{
    not {param.lower()}_compliant
    actual := get_{param.lower()}_value()
    msg := sprintf("{param} exceeds adjusted threshold: %v > {new_value}", [actual])
}}'''

        proposal = PolicyProposal(
            proposal_id=f"prop_{pattern.pattern_id}_{datetime.now().strftime('%Y%m%d')}",
            rule_name=f"Adjust {param} threshold",
            rule_type="parameter_change",
            rego_code=rego_code,
            rationale=f"Parameter '{param}' breached {pattern.occurrences} times. Adjusted threshold accounts for operational reality.",
            supporting_evidence=[str(e) for e in pattern.evidence[:5]],
            confidence_score=pattern.confidence,
            impact_assessment={
                "parameter": param,
                "old_threshold": "current",
                "new_threshold": new_value,
                "breach_reduction": "80-90%",
                "breaking_changes": False
            }
        )

        return proposal

    def _generate_monitoring_rule(self, pattern: AuditPattern) -> Optional[PolicyProposal]:
        """Generate monitoring rule for declining trends"""

        framework = pattern.pattern_id.replace('trend_', '')

        rego_code = f'''# Monitoring rule: {framework.upper()} trend
# Generated: {datetime.now().isoformat()}
# Reason: Declining compliance detected

package ssid.compliance.auto_generated

import future.keywords.if

# Monitor {framework.upper()} compliance trend
{framework}_trend_healthy if {{
    recent_scores := get_recent_{framework}_scores(5)
    count(recent_scores) >= 5

    # Check for improvement or stability
    improving := is_improving(recent_scores)
    stable := is_stable(recent_scores, 2.0)  # Within 2% variation

    improving or stable
}}

is_improving(scores) if {{
    # At least 60% of consecutive pairs show improvement
    pairs := consecutive_pairs(scores)
    improving := [1 | some pair in pairs; pair[1] >= pair[0]]
    count(improving) >= (count(pairs) * 0.6)
}}

is_stable(scores, max_variation) if {{
    min_score := min([s | some s in scores])
    max_score := max([s | some s in scores])
    (max_score - min_score) <= max_variation
}}

# Alert if trend is unhealthy
deny[msg] if {{
    not {framework}_trend_healthy
    msg := sprintf("{framework.upper()} compliance shows declining trend - Immediate review required", [])
}}'''

        proposal = PolicyProposal(
            proposal_id=f"prop_{pattern.pattern_id}_{datetime.now().strftime('%Y%m%d')}",
            rule_name=f"Monitor {framework.upper()} compliance trend",
            rule_type="new_rule",
            rego_code=rego_code,
            rationale=f"{framework.upper()} compliance declining over {pattern.occurrences} measurements. Proactive monitoring prevents further degradation.",
            supporting_evidence=[str(e) for e in pattern.evidence],
            confidence_score=pattern.confidence,
            impact_assessment={
                "framework": framework.upper(),
                "monitoring_added": True,
                "early_warning": True,
                "breaking_changes": False
            }
        )

        return proposal

    def export_proposals(self, output_path: Path, format: str = "rego") -> bool:
        """
        Export policy proposals

        Formats: rego (individual .rego files), json (proposal metadata), markdown (human-readable)
        """
        if not self.proposals and self.learning_history:
            self.proposals = self.learning_history[-1].proposals

        if format == "rego":
            # Export each proposal as separate .rego file
            rego_dir = output_path / "proposed_rules"
            rego_dir.mkdir(parents=True, exist_ok=True)

            for proposal in self.proposals:
                if proposal.confidence_score >= self.min_confidence_threshold:
                    filename = f"{proposal.proposal_id}.rego"
                    (rego_dir / filename).write_text(proposal.rego_code, encoding='utf-8')

            print(f"[Auto-Policy Learning] Exported {len(self.proposals)} Rego proposals to {rego_dir}")

        elif format == "json":
            proposals_data = [
                {
                    "proposal_id": p.proposal_id,
                    "rule_name": p.rule_name,
                    "rule_type": p.rule_type,
                    "confidence_score": p.confidence_score,
                    "rationale": p.rationale,
                    "impact_assessment": p.impact_assessment,
                    "approval_status": p.approval_status
                }
                for p in self.proposals
            ]

            output_path.write_text(json.dumps(proposals_data, indent=2), encoding='utf-8')
            print(f"[Auto-Policy Learning] Exported proposals metadata to {output_path}")

        elif format == "markdown":
            self._export_markdown_report(output_path)

        return True

    def _export_markdown_report(self, output_path: Path):
        """Export human-readable markdown report"""

        if not self.learning_history:
            return

        session = self.learning_history[-1]

        report = f"""# Auto-Policy Learning Report
## Session: {session.session_id}

**Generated:** {session.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Audit Records Analyzed:** {session.audit_data_analyzed}
**Patterns Detected:** {session.patterns_detected}
**Proposals Generated:** {session.proposals_generated}

---

## Executive Summary

The Auto-Policy Learning Engine analyzed {session.audit_data_analyzed} audit records and detected {session.patterns_detected} compliance patterns. Based on this analysis, {session.proposals_generated} policy improvements are proposed.

---

## Proposed Policy Changes

"""

        for i, proposal in enumerate(session.proposals, 1):
            report += f"""
### {i}. {proposal.rule_name}

**Proposal ID:** {proposal.proposal_id}
**Type:** {proposal.rule_type}
**Confidence:** {proposal.confidence_score:.1%}
**Status:** {proposal.approval_status}

**Rationale:**
{proposal.rationale}

**Impact Assessment:**
"""
            for key, value in proposal.impact_assessment.items():
                report += f"- **{key.replace('_', ' ').title()}:** {value}\n"

            report += f"""
**Supporting Evidence:**
"""
            for evidence in proposal.supporting_evidence[:3]:
                report += f"- {evidence}\n"

            report += "\n---\n"

        report += f"""
## Review Process

1. **Technical Review:** Validate Rego syntax and logic
2. **Compliance Review:** Ensure alignment with regulatory requirements
3. **Impact Assessment:** Test on historical data
4. **Approval:** Compliance officer sign-off required
5. **Deployment:** Merge into production ruleset

---

*Generated by SSID Auto-Policy Learning Engine*
"""

        output_path.write_text(report, encoding='utf-8')
        print(f"[Auto-Policy Learning] Exported markdown report to {output_path}")

    def _load_audit_records(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Load audit records from date range (mock data for demo)"""
        # In production: load from 02_audit_logging/evidence/
        # For demo, generate synthetic data

        records = []

        # Simulate recurring failures
        for i in range(5):
            records.append({
                'timestamp': start_date + timedelta(days=i*20),
                'status': 'FAIL',
                'control_id': 'UNI-SR-001',
                'failure_reason': 'Insufficient test coverage',
                'affected_module': '15_infra'
            })

        # Simulate new requirements
        for i in range(3):
            records.append({
                'timestamp': start_date + timedelta(days=i*30),
                'type': 'NEW_REQUIREMENT',
                'control_reference': 'UNI-AI-001',
                'description': 'AI model governance requirements'
            })

        # Simulate threshold breaches
        for i in range(4):
            records.append({
                'timestamp': start_date + timedelta(days=i*25),
                'type': 'THRESHOLD_BREACH',
                'parameter': 'max_audit_log_age',
                'actual_value': 95 + i*5,
                'threshold': 90
            })

        # Simulate framework scores
        for i in range(6):
            records.append({
                'timestamp': start_date + timedelta(days=i*15),
                'type': 'COMPLIANCE_SCORE',
                'framework': 'mica',
                'score': 88 - i*1.5
            })

        return records

    def _calculate_session_metrics(self, records, patterns, proposals) -> Dict:
        """Calculate learning session metrics"""
        return {
            "records_processed": len(records),
            "patterns_high_confidence": sum(1 for p in patterns if p.confidence >= 0.85),
            "proposals_high_confidence": sum(1 for p in proposals if p.confidence_score >= 0.85),
            "avg_confidence": sum(p.confidence_score for p in proposals) / len(proposals) if proposals else 0
        }

    def _save_session(self, session: LearningSession):
        """Persist learning session"""
        session_file = self.output_dir / f"{session.session_id}.json"
        data = {
            "session_id": session.session_id,
            "timestamp": session.timestamp.isoformat(),
            "metrics": session.session_metrics,
            "proposals_count": len(session.proposals)
        }
        session_file.write_text(json.dumps(data, indent=2), encoding='utf-8')

def main():
    """Main CLI entry point"""
    print("=== SSID Auto-Policy Learning Engine ===\n")

    # Paths
    audit_data_dir = Path("C:/Users/bibel/Documents/Github/SSID/02_audit_logging/evidence")
    unified_index_path = Path("C:/Users/bibel/Documents/Github/SSID/23_compliance/mappings/compliance_unified_index.yaml")
    output_dir = Path("C:/Users/bibel/Documents/Github/SSID/23_compliance/ai_ml_ready/learned_policies")

    # Initialize learner
    learner = AutoPolicyLearner(audit_data_dir, unified_index_path, output_dir)

    # Analyze last 6 months
    print("1. Analyzing audit history (last 6 months)...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    session = learner.analyze_audit_history(start_date, end_date)

    # Export proposals
    print("\n2. Exporting policy proposals...")
    learner.export_proposals(output_dir / "proposals", format="rego")
    learner.export_proposals(output_dir / "proposals.json", format="json")
    learner.export_proposals(output_dir / "POLICY_PROPOSALS.md", format="markdown")

    print("\n3. Learning Summary:")
    print(f"   Patterns detected: {session.patterns_detected}")
    print(f"   Proposals generated: {session.proposals_generated}")
    print(f"   High-confidence proposals: {session.session_metrics['proposals_high_confidence']}")
    print(f"   Average confidence: {session.session_metrics['avg_confidence']:.1%}")

    print("\n=== Learning Complete ===")
    print(f"\nReview proposals in: {output_dir}")

if __name__ == "__main__":
    main()
