#!/usr/bin/env python3
"""
SSID Legal Summary Generator
Human-Readable Compliance Reports for Non-Technical Auditors

Automatically generates clear-text compliance summaries from YAML metrics,
making technical compliance data accessible to legal and regulatory professionals.
"""

import yaml
import json
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ComplianceSummary:
    """Human-readable compliance summary"""
    title: str
    executive_summary: str
    period: str
    overall_status: str
    frameworks: List[Dict[str, Any]]
    key_findings: List[str]
    critical_issues: List[Dict[str, Any]]
    high_priority_gaps: List[Dict[str, Any]]
    remediation_plan: List[Dict[str, Any]]
    recommendations: List[str]
    sign_off: Dict[str, str]

class LegalSummaryGenerator:
    """
    Generate human-readable compliance summaries

    Converts technical YAML compliance metrics into clear-text reports
    suitable for legal teams, auditors, and regulatory authorities.
    """

    def __init__(self, unified_index_path: Path):
        self.unified_index_path = Path(unified_index_path)
        self.unified_index = self._load_unified_index()

    def _load_unified_index(self) -> Dict:
        """Load compliance unified index"""
        with open(self.unified_index_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def generate_executive_summary(self, output_path: Path, report_period: str = None) -> bool:
        """
        Generate executive compliance summary

        High-level overview for C-level executives and board members
        """
        if not report_period:
            report_period = f"Q{(datetime.now().month-1)//3 + 1} {datetime.now().year}"

        meta = self.unified_index.get("meta", {})
        metrics = self.unified_index.get("compliance_metrics_unified", {})
        overall = metrics.get("overall_coverage", {})
        by_category = metrics.get("by_category", {})
        by_risk = metrics.get("by_risk_level", {})

        # Determine overall status
        overall_avg = self._parse_percentage(metrics.get("unified_average", "0%"))
        status = self._get_status_label(overall_avg)

        # Generate summary
        report = f"""
# EXECUTIVE COMPLIANCE SUMMARY
## {report_period}

**Report Date:** {datetime.now().strftime("%B %d, %Y")}
**Framework Version:** {meta.get('version', 'N/A')}
**Overall Status:** **{status}**

---

## EXECUTIVE OVERVIEW

The organization's compliance framework demonstrates **{overall_avg:.0f}% overall compliance** across four major regulatory frameworks: GDPR (data protection), DORA (operational resilience), MiCA (crypto-assets), and AMLD6 (anti-money laundering).

### Key Compliance Metrics

| Framework | Coverage | Status |
|-----------|----------|--------|
| **GDPR** (Data Protection) | {overall.get('gdpr', 'N/A')} | {self._get_status_emoji(self._parse_percentage(overall.get('gdpr', '0%')))} {self._get_status_label(self._parse_percentage(overall.get('gdpr', '0%')))} |
| **DORA** (ICT Resilience) | {overall.get('dora', 'N/A')} | {self._get_status_emoji(self._parse_percentage(overall.get('dora', '0%')))} {self._get_status_label(self._parse_percentage(overall.get('dora', '0%')))} |
| **MiCA** (Crypto Assets) | {overall.get('mica', 'N/A')} | {self._get_status_emoji(self._parse_percentage(overall.get('mica', '0%')))} {self._get_status_label(self._parse_percentage(overall.get('mica', '0%')))} |
| **AMLD6** (AML/CFT) | {overall.get('amld6', 'N/A')} | {self._get_status_emoji(self._parse_percentage(overall.get('amld6', '0%')))} {self._get_status_label(self._parse_percentage(overall.get('amld6', '0%')))} |
| **Overall Average** | **{metrics.get('unified_average', 'N/A')}** | {self._get_status_emoji(overall_avg)} **{status}** |

### Compliance by Control Category

| Category | Coverage | Priority |
|----------|----------|----------|
| Data Protection & Privacy | {by_category.get('data_protection', 'N/A')} | High |
| Security & Resilience | {by_category.get('security_resilience', 'N/A')} | Critical |
| Financial Crime Prevention | {by_category.get('financial_crime', 'N/A')} | High |
| Governance & Accountability | {by_category.get('governance', 'N/A')} | Medium |
| Third-Party Risk Management | {by_category.get('third_party', 'N/A')} | High |
| Cryptographic Controls | {by_category.get('cryptography', 'N/A')} | Critical |
| Audit & Monitoring | {by_category.get('audit_logging', 'N/A')} | High |

---

## KEY FINDINGS

{self._generate_key_findings(metrics)}

---

## CRITICAL CONTROL STATUS

{self._generate_critical_control_status()}

---

## RISK ASSESSMENT

**By Risk Level:**

- **Critical Controls:** {by_risk.get('critical', 'N/A')} implemented
- **High Priority Controls:** {by_risk.get('high', 'N/A')} implemented
- **Medium Priority Controls:** {by_risk.get('medium', 'N/A')} implemented
- **Low Priority Controls:** {by_risk.get('low', 'N/A')} implemented

{self._generate_risk_narrative(by_risk)}

---

## RECOMMENDATIONS

{self._generate_recommendations(metrics)}

---

## NEXT STEPS

1. **Immediate Actions** (Within 7 days)
   - Review and address any CRITICAL control gaps
   - Ensure incident response procedures are tested

2. **Short-term Actions** (Within 30 days)
   - Complete implementation of HIGH priority controls
   - Conduct third-party vendor risk assessments

3. **Long-term Actions** (Within 90 days)
   - Enhance automation of compliance monitoring
   - Prepare for external audit

---

## SIGN-OFF

**Prepared by:** Compliance Office
**Reviewed by:** Chief Compliance Officer
**Date:** {datetime.now().strftime("%B %d, %Y")}

**Note:** This report is based on automated compliance monitoring and internal assessments. External audit validation recommended annually.

---

*Generated by SSID Compliance Framework v{meta.get('version', 'N/A')}*
"""

        output_path.write_text(report, encoding='utf-8')
        print(f"[Legal Summary] Generated executive summary: {output_path}")
        return True

    def generate_detailed_report(self, output_path: Path, include_technical: bool = False) -> bool:
        """
        Generate detailed compliance report

        Comprehensive report for auditors and compliance officers
        """
        meta = self.unified_index.get("meta", {})
        metrics = self.unified_index.get("compliance_metrics_unified", {})
        mappings = self.unified_index.get("cross_framework_mappings", {})

        report = f"""
# DETAILED COMPLIANCE REPORT
## SSID Framework Compliance Analysis

**Report Date:** {datetime.now().strftime("%B %d, %Y")}
**Framework:** {meta.get('framework', 'UNIFIED')}
**Version:** {meta.get('version', 'N/A')}
**Classification:** {meta.get('classification', 'N/A')}

---

## 1. REGULATORY LANDSCAPE

This organization operates under multiple regulatory frameworks that govern different aspects of operations:

### 1.1 General Data Protection Regulation (GDPR)
- **Scope:** Processing of personal data of EU residents
- **Key Requirements:** Data protection principles, individual rights, security measures
- **Current Coverage:** {metrics.get('overall_coverage', {}).get('gdpr', 'N/A')}

### 1.2 Digital Operational Resilience Act (DORA)
- **Scope:** ICT risk management for financial entities
- **Key Requirements:** ICT governance, incident reporting, third-party oversight
- **Current Coverage:** {metrics.get('overall_coverage', {}).get('dora', 'N/A')}

### 1.3 Markets in Crypto-Assets (MiCA)
- **Scope:** Regulation of crypto-asset services and issuers
- **Key Requirements:** Authorization, custody, operational resilience
- **Current Coverage:** {metrics.get('overall_coverage', {}).get('mica', 'N/A')}

### 1.4 Anti-Money Laundering Directive 6 (AMLD6)
- **Scope:** Prevention of money laundering and terrorist financing
- **Key Requirements:** Customer due diligence, transaction monitoring, reporting
- **Current Coverage:** {metrics.get('overall_coverage', {}).get('amld6', 'N/A')}

---

## 2. CONTROL FRAMEWORK

{self._generate_control_framework_section(mappings)}

---

## 3. COMPLIANCE GAPS ANALYSIS

{self._generate_gaps_analysis(mappings)}

---

## 4. REMEDIATION ROADMAP

{self._generate_remediation_roadmap(mappings)}

---

## 5. VERIFICATION METHODOLOGY

The compliance assessment uses a multi-tiered verification approach:

| Method | Frequency | Confidence | Usage |
|--------|-----------|------------|-------|
| Automated Testing | Real-time | High | {metrics.get('verification_status', {}).get('automated', 0)} controls |
| Semi-Automated | Daily/Weekly | Medium-High | {metrics.get('verification_status', {}).get('semi_automated', 0)} controls |
| Manual Review | Quarterly | Medium | {metrics.get('verification_status', {}).get('manual', 0)} controls |
| External Audit | Annual | Very High | {metrics.get('verification_status', {}).get('external_audit', 0)} controls |

**Total Controls Under Management:** {metrics.get('verification_status', {}).get('total_controls', 0)}

---

## 6. EVIDENCE TRAIL

All compliance assertions are backed by:

- **Immutable Audit Logs:** WORM storage with cryptographic anchoring
- **Blockchain Proofs:** On-chain evidence validation
- **Automated Testing:** Continuous CI/CD integration
- **Manual Documentation:** Quarterly compliance reviews

Evidence repository location: `02_audit_logging/evidence/`

---

## 7. MULTI-JURISDICTIONAL CONSIDERATIONS

{self._generate_jurisdictional_section()}

---

## 8. CONTINUOUS MONITORING

The compliance framework includes:

- Real-time policy enforcement
- Automated control testing in CI/CD pipeline
- Quarterly management reviews
- Annual external audits

---

## APPENDIX A: GLOSSARY

**Control:** A safeguard or countermeasure to manage risk
**Framework:** A structured set of regulatory requirements
**Unified ID:** Cross-framework control identifier
**Risk Level:** Classification of control criticality (CRITICAL, HIGH, MEDIUM, LOW)
**Implementation Status:** Current state (implemented, planned, partial)

---

## APPENDIX B: REGULATORY REFERENCES

{self._generate_regulatory_references()}

---

**Report Generated:** {datetime.now().isoformat()}
**Generated by:** SSID Compliance Framework v{meta.get('version', 'N/A')}

"""

        output_path.write_text(report, encoding='utf-8')
        print(f"[Legal Summary] Generated detailed report: {output_path}")
        return True

    def generate_framework_specific_report(self, framework: str, output_path: Path) -> bool:
        """
        Generate framework-specific compliance report

        Focused report for single regulatory framework (GDPR, DORA, MiCA, AMLD6)
        """
        framework_upper = framework.upper()
        mappings = self.unified_index.get("cross_framework_mappings", {})

        # Collect controls for this framework
        framework_controls = []
        for domain_name, controls in mappings.items():
            if isinstance(controls, list):
                for control in controls:
                    frameworks = [m['framework'] for m in control.get('mappings', [])]
                    if framework_upper in frameworks:
                        framework_controls.append(control)

        implemented = sum(1 for c in framework_controls if c['implementation_status'] == 'implemented')
        total = len(framework_controls)
        percentage = (implemented / total * 100) if total > 0 else 0

        report = f"""
# {framework_upper} COMPLIANCE REPORT

**Report Date:** {datetime.now().strftime("%B %d, %Y")}
**Framework:** {framework_upper}
**Overall Compliance:** {percentage:.1f}% ({implemented}/{total} controls)

---

## EXECUTIVE SUMMARY

This report assesses compliance with {framework_upper} requirements. The organization has implemented **{implemented} of {total}** applicable controls, achieving **{percentage:.1f}% compliance**.

{self._get_framework_description(framework_upper)}

---

## CONTROL ASSESSMENT

| Control ID | Description | Risk Level | Status |
|------------|-------------|------------|--------|
"""

        for control in framework_controls:
            status_icon = "OK" if control['implementation_status'] == 'implemented' else "PENDING"
            report += f"| {control['unified_id']} | {control['description'][:50]}... | {control['risk_level']} | {status_icon} |\n"

        report += f"""

---

## GAPS AND REMEDIATION

### Outstanding Items

"""

        gaps = [c for c in framework_controls if c['implementation_status'] != 'implemented']
        if gaps:
            for gap in gaps:
                report += f"""
**{gap['unified_id']}: {gap['description']}**
- Risk Level: {gap['risk_level']}
- Target Remediation: {self._get_remediation_sla(gap['risk_level'])}
- Affected Modules: {', '.join(gap['ssid_modules'])}
"""
        else:
            report += "\nNo outstanding compliance gaps identified.\n"

        report += f"""

---

## RECOMMENDATIONS

{self._get_framework_recommendations(framework_upper, percentage)}

---

**Report Generated:** {datetime.now().isoformat()}

"""

        output_path.write_text(report, encoding='utf-8')
        print(f"[Legal Summary] Generated {framework_upper} report: {output_path}")
        return True

    # Helper methods

    def _parse_percentage(self, value: str) -> float:
        """Parse percentage string to float"""
        if isinstance(value, str):
            return float(value.strip('%'))
        return float(value)

    def _get_status_label(self, percentage: float) -> str:
        """Get status label from percentage"""
        if percentage >= 95:
            return "EXCELLENT"
        elif percentage >= 90:
            return "GOOD"
        elif percentage >= 80:
            return "ACCEPTABLE"
        elif percentage >= 70:
            return "NEEDS IMPROVEMENT"
        else:
            return "CRITICAL"

    def _get_status_emoji(self, percentage: float) -> str:
        """Get status emoji"""
        if percentage >= 95:
            return "✓✓"
        elif percentage >= 90:
            return "✓"
        elif percentage >= 80:
            return "~"
        else:
            return "✗"

    def _generate_key_findings(self, metrics: Dict) -> str:
        """Generate key findings section"""
        overall = metrics.get("overall_coverage", {})
        by_risk = metrics.get("by_risk_level", {})

        findings = []

        # Overall compliance
        avg = self._parse_percentage(metrics.get("unified_average", "0%"))
        if avg >= 90:
            findings.append(f"- **Strong Overall Compliance:** The organization maintains {avg:.0f}% average compliance across all frameworks, indicating robust regulatory adherence.")
        else:
            findings.append(f"- **Compliance Improvement Needed:** Current {avg:.0f}% average requires attention to meet regulatory expectations.")

        # Critical controls
        critical = self._parse_percentage(by_risk.get("critical", "0%"))
        if critical == 100:
            findings.append("- **All Critical Controls Implemented:** 100% of critical risk controls are operational, providing strong foundation for regulatory compliance.")
        else:
            findings.append(f"- **Critical Control Gap:** {100-critical:.0f}% of critical controls remain outstanding - immediate action required.")

        # Framework-specific
        for framework, coverage in overall.items():
            pct = self._parse_percentage(coverage)
            if pct < 90:
                findings.append(f"- **{framework.upper()} Below Target:** At {pct:.0f}%, requires focused remediation effort.")

        return "\n".join(findings)

    def _generate_critical_control_status(self) -> str:
        """Generate critical control status"""
        mappings = self.unified_index.get("cross_framework_mappings", {})

        critical_controls = []
        for domain_name, controls in mappings.items():
            if isinstance(controls, list):
                for control in controls:
                    if control['risk_level'] == 'CRITICAL':
                        critical_controls.append(control)

        if not critical_controls:
            return "No critical controls defined."

        status_text = "| Control | Description | Status |\n|---------|-------------|--------|\n"
        for control in critical_controls:
            status = "IMPLEMENTED" if control['implementation_status'] == 'implemented' else "PENDING"
            icon = "✓" if status == "IMPLEMENTED" else "✗"
            status_text += f"| {control['unified_id']} | {control['description'][:40]}... | {icon} {status} |\n"

        return status_text

    def _generate_risk_narrative(self, by_risk: Dict) -> str:
        """Generate risk narrative"""
        critical = self._parse_percentage(by_risk.get("critical", "0%"))
        high = self._parse_percentage(by_risk.get("high", "0%"))

        if critical == 100 and high >= 95:
            return "**Risk Assessment: LOW** - All critical controls and nearly all high-priority controls are implemented. Residual risk is minimal and well-managed."
        elif critical == 100 and high >= 90:
            return "**Risk Assessment: MEDIUM** - Critical controls are complete, but some high-priority gaps exist. Continued focus on remediation recommended."
        elif critical < 100:
            return "**Risk Assessment: HIGH** - Critical control gaps present significant regulatory and operational risk. Immediate remediation required."
        else:
            return "**Risk Assessment: MEDIUM** - Generally acceptable control posture with targeted improvement areas."

    def _generate_recommendations(self, metrics: Dict) -> str:
        """Generate recommendations"""
        recommendations = []
        overall = metrics.get("overall_coverage", {})

        for framework, coverage in overall.items():
            pct = self._parse_percentage(coverage)
            if pct < 90:
                recommendations.append(f"1. **Prioritize {framework.upper()} Remediation:** Increase coverage from {pct:.0f}% to minimum 90% through targeted control implementation.")

        if not recommendations:
            recommendations.append("1. **Maintain Current Posture:** Continue quarterly reviews and automated monitoring.")
            recommendations.append("2. **External Validation:** Schedule annual third-party audit to validate compliance assertions.")

        recommendations.append("3. **Enhance Automation:** Expand automated verification coverage to reduce manual review burden.")
        recommendations.append("4. **Staff Training:** Ensure all staff complete annual compliance awareness training.")

        return "\n".join(recommendations)

    def _generate_control_framework_section(self, mappings: Dict) -> str:
        """Generate control framework section"""
        section = "The organization implements a unified control framework mapping requirements across all regulatory frameworks:\n\n"

        for domain_name, controls in mappings.items():
            if isinstance(controls, list) and len(controls) > 0:
                section += f"### 2.{list(mappings.keys()).index(domain_name) + 1} {domain_name.replace('_', ' ').title()}\n\n"
                for control in controls[:2]:  # Limit to first 2 for brevity
                    section += f"**{control['unified_id']}: {control['description']}**\n"
                    section += f"- Risk Level: {control['risk_level']}\n"
                    section += f"- Implementation: {control['implementation_status'].title()}\n"
                    section += f"- Verification: {control['verification'].replace('_', ' ').title()}\n\n"

        return section

    def _generate_gaps_analysis(self, mappings: Dict) -> str:
        """Generate gaps analysis"""
        gaps = []
        for domain_name, controls in mappings.items():
            if isinstance(controls, list):
                for control in controls:
                    if control['implementation_status'] != 'implemented':
                        gaps.append(control)

        if not gaps:
            return "No significant compliance gaps identified. All high-priority controls are implemented.\n"

        section = f"**Total Outstanding Items:** {len(gaps)}\n\n"

        # Group by risk level
        critical = [g for g in gaps if g['risk_level'] == 'CRITICAL']
        high = [g for g in gaps if g['risk_level'] == 'HIGH']

        if critical:
            section += f"### 3.1 Critical Gaps ({len(critical)} items)\n\n"
            for gap in critical:
                section += f"- **{gap['unified_id']}:** {gap['description']}\n"

        if high:
            section += f"\n### 3.2 High Priority Gaps ({len(high)} items)\n\n"
            for gap in high:
                section += f"- **{gap['unified_id']}:** {gap['description']}\n"

        return section

    def _generate_remediation_roadmap(self, mappings: Dict) -> str:
        """Generate remediation roadmap"""
        return """
The organization follows a risk-based remediation approach:

**Phase 1 (0-30 days): Critical Controls**
- Address all CRITICAL risk level controls
- Deploy emergency fixes if necessary
- Validate with automated testing

**Phase 2 (30-90 days): High Priority Controls**
- Implement HIGH risk level controls
- Conduct user acceptance testing
- Update documentation

**Phase 3 (90-180 days): Medium & Low Priority**
- Complete remaining controls
- Optimize automation
- Prepare for external audit

**Ongoing: Continuous Improvement**
- Quarterly compliance reviews
- Annual external audits
- Continuous monitoring and alerting
"""

    def _generate_jurisdictional_section(self) -> str:
        """Generate jurisdictional considerations"""
        return """
The unified compliance framework addresses multi-jurisdictional requirements:

- **EU/EEA:** GDPR, DORA, MiCA, AMLD6 fully applicable
- **Global Operations:** Framework design supports multi-jurisdiction deployment
- **Data Localization:** Architecture supports jurisdiction-specific data residency
- **Cross-Border:** Transfer mechanisms compliant with GDPR Chapter V
"""

    def _generate_regulatory_references(self) -> str:
        """Generate regulatory references"""
        refs = self.unified_index.get("references", [])
        if not refs:
            return "No references available.\n"

        text = ""
        for ref in refs:
            text += f"- **{ref.get('title', 'N/A')}:** `{ref.get('location', 'N/A')}`\n"

        return text

    def _get_remediation_sla(self, risk_level: str) -> str:
        """Get remediation SLA for risk level"""
        slas = {
            "CRITICAL": "24 hours",
            "HIGH": "7 days",
            "MEDIUM": "30 days",
            "LOW": "90 days"
        }
        return slas.get(risk_level, "To be determined")

    def _get_framework_description(self, framework: str) -> str:
        """Get framework description"""
        descriptions = {
            "GDPR": "The General Data Protection Regulation governs the processing of personal data of individuals in the European Union. It establishes comprehensive requirements for data protection, individual rights, and organizational accountability.",
            "DORA": "The Digital Operational Resilience Act establishes a regulatory framework for ICT risk management in the financial sector. It requires financial entities to ensure operational continuity through robust ICT governance, incident management, and third-party oversight.",
            "MICA": "The Markets in Crypto-Assets Regulation creates a comprehensive regulatory framework for crypto-asset services and issuers in the EU. It covers authorization, custody, operational requirements, and consumer protection.",
            "AMLD6": "The Sixth Anti-Money Laundering Directive strengthens the EU's framework for preventing money laundering and terrorist financing. It extends criminal liability, harmonizes penalties, and enhances cooperation between member states."
        }
        return descriptions.get(framework, "Regulatory framework description not available.")

    def _get_framework_recommendations(self, framework: str, percentage: float) -> str:
        """Get framework-specific recommendations"""
        if percentage >= 95:
            return f"""
- **Maintain Excellence:** Continue current compliance posture
- **Document Best Practices:** Capture processes for organizational knowledge
- **Prepare for Audit:** Excellent position for external validation
"""
        elif percentage >= 90:
            return f"""
- **Close Remaining Gaps:** Focus on outstanding controls
- **Enhance Documentation:** Ensure all controls are fully documented
- **Schedule External Review:** Prepare for third-party assessment
"""
        else:
            return f"""
- **Urgent Remediation Required:** Develop detailed action plan for {framework}
- **Allocate Resources:** Assign dedicated personnel to gap closure
- **Weekly Reviews:** Implement weekly progress monitoring
- **Consider External Expertise:** Engage consultants if needed
"""

def main():
    """Main CLI entry point"""
    print("=== SSID Legal Summary Generator ===\n")

    # Paths
    unified_index_path = Path("C:/Users/bibel/Documents/Github/SSID/23_compliance/mappings/compliance_unified_index.yaml")
    output_dir = Path("C:/Users/bibel/Documents/Github/SSID/13_ui_layer/legal_summaries")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize generator
    generator = LegalSummaryGenerator(unified_index_path)

    # Generate reports
    print("1. Generating executive summary...")
    exec_path = output_dir / f"Executive_Summary_{datetime.now().strftime('%Y%m%d')}.md"
    generator.generate_executive_summary(exec_path)

    print("\n2. Generating detailed compliance report...")
    detailed_path = output_dir / f"Detailed_Compliance_Report_{datetime.now().strftime('%Y%m%d')}.md"
    generator.generate_detailed_report(detailed_path)

    print("\n3. Generating framework-specific reports...")
    for framework in ['gdpr', 'dora', 'mica', 'amld6']:
        fw_path = output_dir / f"{framework.upper()}_Report_{datetime.now().strftime('%Y%m%d')}.md"
        generator.generate_framework_specific_report(framework, fw_path)

    print("\n=== Generation Complete ===")
    print(f"\nReports generated in: {output_dir}")
    print("\nAvailable reports:")
    print("- Executive Summary (for C-level/Board)")
    print("- Detailed Compliance Report (for auditors)")
    print("- Framework-Specific Reports (GDPR, DORA, MiCA, AMLD6)")

if __name__ == "__main__":
    main()
