# Incident Response Plan - [ROOT_NAME]

**Version:** 1.0
**Last Updated:** 2025-10-21
**Owner:** Security Team
**Compliance:** DORA, NIS2, ISO 27001, GDPR

---

## 1. Executive Summary

This Incident Response Plan (IRP) defines the procedures for detecting, responding to, and recovering from security incidents affecting the **[ROOT_NAME]** component of the SSID infrastructure.

### Scope
- All systems, services, and data within **[ROOT_NAME]**
- Integration points with other SSID roots
- External dependencies and third-party services

### Objectives
- Minimize incident impact and recovery time
- Preserve evidence for forensic analysis
- Maintain regulatory compliance (DORA, GDPR, NIS2)
- Enable continuous improvement through lessons learned

---

## 2. Incident Classification

### Severity Levels

| Level | Description | Examples | Response Time |
|-------|-------------|----------|---------------|
| **P0 - Critical** | Complete service outage, data breach | Root compromise, ransomware, major data leak | < 15 minutes |
| **P1 - High** | Significant degradation, security vulnerability | DoS attack, unauthorized access attempt, API compromise | < 1 hour |
| **P2 - Medium** | Partial degradation, potential security issue | Failed authentication spike, suspicious activity | < 4 hours |
| **P3 - Low** | Minor issues, no immediate security impact | Configuration drift, non-critical policy violation | < 24 hours |

### Incident Types
- **Security Breach**: Unauthorized access, data exfiltration, account compromise
- **Service Disruption**: DoS/DDoS, infrastructure failure, network outage
- **Data Integrity**: Corruption, unauthorized modification, deletion
- **Compliance Violation**: GDPR breach, policy violation, regulatory non-compliance
- **Supply Chain**: Third-party compromise, dependency vulnerability

---

## 3. Roles and Responsibilities

### Incident Response Team (IRT)

| Role | Responsibilities | Contact |
|------|------------------|---------|
| **Incident Commander** | Overall coordination, decision authority | [TBD] |
| **Security Lead** | Technical investigation, forensics | [TBD] |
| **Communications Lead** | Stakeholder notifications, external comms | [TBD] |
| **Legal/Compliance** | Regulatory notifications, legal guidance | [TBD] |
| **Technical SME** | Root-specific expertise, remediation | [TBD] |

### Escalation Chain
1. On-call Engineer → Team Lead
2. Team Lead → Security Lead
3. Security Lead → Incident Commander
4. Incident Commander → Executive Team (P0/P1 only)

---

## 4. Detection and Alerting

### Monitoring Systems
- **SIEM**: Centralized security event monitoring
- **IDS/IPS**: Network intrusion detection
- **Log Aggregation**: ELK stack, Splunk
- **APM**: Application performance monitoring
- **Blockchain Anchors**: Evidence integrity monitoring

### Alert Sources
- Automated security alerts (SIEM, IDS)
- User reports (security@ssid.eu)
- Third-party notifications (vendors, partners)
- Compliance monitoring (OPA policy violations)
- Threat intelligence feeds

### Alert Triage
1. Validate alert authenticity
2. Classify severity and type
3. Assign to on-call engineer
4. Escalate if P0/P1

---

## 5. Response Procedures

### Phase 1: Detection & Analysis (0-30 minutes)
1. **Confirm Incident**
   - Validate alert/report
   - Gather initial evidence
   - Classify severity and type

2. **Assemble Team**
   - Page Incident Commander (P0/P1)
   - Activate IRT members
   - Establish communication channel (Slack #incident-[ID])

3. **Initial Assessment**
   - Scope: Affected systems, data, users
   - Impact: Business, regulatory, reputational
   - Timeline: First occurrence, detection time

### Phase 2: Containment (30 minutes - 2 hours)
1. **Short-term Containment**
   - Isolate affected systems (network segmentation)
   - Disable compromised accounts
   - Block malicious IPs/domains
   - Preserve evidence (disk images, logs, memory dumps)

2. **Long-term Containment**
   - Apply temporary patches/workarounds
   - Implement compensating controls
   - Monitor for lateral movement

### Phase 3: Eradication (2-24 hours)
1. **Root Cause Analysis**
   - Identify attack vector
   - Determine exploit method
   - Map compromise timeline

2. **Remove Threat**
   - Delete malware/backdoors
   - Close vulnerabilities
   - Revoke compromised credentials
   - Update firewall rules

### Phase 4: Recovery (24-72 hours)
1. **System Restoration**
   - Rebuild from clean backups
   - Apply security patches
   - Restore services incrementally
   - Verify integrity (hash checks, blockchain anchors)

2. **Validation**
   - Security scans (vulnerability, malware)
   - Penetration testing
   - Evidence anchoring
   - Compliance checks (OPA policies)

### Phase 5: Post-Incident (1-2 weeks)
1. **Lessons Learned**
   - Post-mortem meeting (all IRT members)
   - Document timeline and decisions
   - Identify gaps and improvements

2. **Remediation**
   - Implement preventive measures
   - Update policies and procedures
   - Training and awareness

3. **Regulatory Notifications**
   - GDPR: 72 hours to DPA (if applicable)
   - DORA: Notification to competent authority
   - NIS2: Incident reporting requirements
   - Customer notifications (as required)

---

## 6. Communication Plan

### Internal Communications
- **Incident Channel**: Slack #incident-[ID]
- **Status Updates**: Every 30 minutes (P0/P1), every 4 hours (P2/P3)
- **Stakeholders**: Engineering, Security, Legal, Executive

### External Communications
- **Customers**: If data breach or service impact
- **Regulators**: GDPR DPA, DORA authority, NIS2
- **Partners**: If third-party systems affected
- **Public/Media**: Coordinated with PR team

### Templates
- Incident notification email
- Status update (internal)
- Customer notification (external)
- Regulatory report (DORA, GDPR, NIS2)

---

## 7. Evidence Preservation

### Chain of Custody
1. **Collection**
   - Disk images (dd, FTK Imager)
   - Memory dumps (LiME, Volatility)
   - Log files (centralized SIEM)
   - Network captures (tcpdump, Wireshark)

2. **Storage**
   - Write-protected media
   - Encrypted containers
   - Blockchain anchoring (SHA3-256)
   - Access logging

3. **Documentation**
   - Collection timestamp
   - Collector identity
   - Hash values (SHA3-256)
   - Storage location

### Blockchain Anchoring
- All evidence MUST be anchored to blockchain
- Hash: SHA3-256
- Anchor within 1 hour of collection
- Verify integrity before analysis

---

## 8. Regulatory Compliance

### DORA (Digital Operational Resilience Act)
- Incident classification and reporting
- Major incidents: < 24 hours notification
- Significant cyber threats: < 72 hours
- Root cause analysis required

### GDPR (General Data Protection Regulation)
- Personal data breach: < 72 hours to DPA
- High risk to individuals: notify data subjects
- Document all breaches (even if not notified)
- Processor must notify controller

### NIS2 (Network and Information Security Directive)
- Significant incidents: < 24 hours initial notification
- Incident report: < 72 hours
- Final report: within 1 month
- Cross-border coordination

### ISO 27001
- Incident logging and categorization
- Root cause analysis
- Corrective actions
- Management review

---

## 9. Tools and Resources

### Technical Tools
- **SIEM**: Splunk, ELK Stack
- **Forensics**: EnCase, FTK, Volatility
- **Network**: Wireshark, tcpdump, Zeek
- **Malware Analysis**: VirusTotal, Cuckoo Sandbox
- **Blockchain**: Ethereum, Polygon (evidence anchoring)

### Documentation
- [Incident Response Playbooks](../playbooks/)
- [Root Architecture](../architecture/)
- [OPA Policies](../../03_core/opa/)
- [SSID Master Definition](../../16_codex/structure/)

### Contacts
- **Security Team**: security@ssid.eu
- **Legal**: legal@ssid.eu
- **DPO**: dpo@ssid.eu
- **On-call**: +[PHONE]

---

## 10. Testing and Maintenance

### Testing Schedule
- **Tabletop Exercises**: Quarterly
- **Simulations**: Bi-annually
- **Red Team**: Annually
- **Plan Review**: Monthly

### Metrics
- Mean Time to Detect (MTTD)
- Mean Time to Respond (MTTR)
- Mean Time to Recover (MTTR)
- False Positive Rate
- Escalation Time

### Updates
- Review after each incident
- Update when architecture changes
- Annual comprehensive review
- Regulatory changes (DORA, NIS2, GDPR)

---

## 11. Appendices

### A. Emergency Contacts
[List of emergency contacts with roles and phone numbers]

### B. System Dependencies
[Diagram of root dependencies and integration points]

### C. Data Classification
[Matrix of data types and protection requirements]

### D. Incident Report Template
[Standardized format for incident documentation]

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-21 | Security Team | Initial version - DORA compliance |

**Approval**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| CISO | [TBD] | | |
| DPO | [TBD] | | |
| Legal | [TBD] | | |

---

*This template must be customized for each root with specific systems, contacts, and procedures.*
