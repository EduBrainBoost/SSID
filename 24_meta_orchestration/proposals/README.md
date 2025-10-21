# SSID DAO Governance – Proposal-System

Dieser Ordner enthält alle formellen Governance-Vorschläge (Proposals) des SSID-Ökosystems.
Jede Datei beschreibt eine Änderung oder einen Parameter-Lock, die von der DAO abgestimmt und ratifiziert werden kann.

---

## Struktur

```
24_meta_orchestration/
└── proposals/
    ├── lock_fee_params_v5_4_3.yaml
    ├── ballots/
    │   └── lock_fee_params_v5_4_3.json
    ├── registry.yaml
    └── README.md
```

---

## Komponenten

### YAML-Proposal
Enthält alle technischen Parameter (z. B. Fees, Anteile, Governance-Kontrollen).
Definiert exakte mathematische Invarianten und Verifizierungsanforderungen.

**Beispiel:** `lock_fee_params_v5_4_3.yaml`

### JSON-Ballot
Dokumentiert das Abstimmungsergebnis mit Hash-Verifikation.
Enthält:
- Stimmen (yes/no/abstain)
- Quorum-Status
- Approval-Ratio
- Signaturen der Governance-Nodes

**Beispiel:** `ballots/lock_fee_params_v5_4_3.json`

### Registry
Listet aktive und archivierte Proposals.
Verknüpft Proposal-IDs mit Status und Hashes.

**Datei:** `registry.yaml`

### Audit-Pfad
Verknüpft Proposals mit Merkle-Proofs und Signaturen.
Ermöglicht vollständige Rückverfolgbarkeit.

---

## Abstimmungs-Workflow

### 1. Proposal-Erstellung
Proposal wird erstellt und im Ordner `proposals/` abgelegt.

**Erforderliche Felder:**
- `proposal_id`: Eindeutige ID (z.B. LOCK-FEE-V5.4.3)
- `title`: Beschreibender Titel
- `version`: Versionsnummer
- `quorum`: Mindestbeteiligung (Standard: 0.67)
- `approval_threshold`: Zustimmungsschwelle (Standard: 0.67)
- `parameters`: Zu versiegelnde Parameter
- `verification`: Invarianten und Audit-Anforderungen

### 2. Hash-Generierung
SHA-256 Hash des Proposals wird berechnet:

```bash
sha256sum lock_fee_params_v5_4_3.yaml
```

### 3. Review-Phase
DAO-Mitglieder prüfen:
- Inhalt und Mathematik
- Hash-Verifikation
- Compliance mit bestehenden Regeln
- Auswirkungen auf das System

**Dauer:** Mindestens 7 Tage

### 4. Abstimmungs-Phase
**Status:** `vote_open` → `vote_closed`

**Abstimmungsoptionen:**
- **YES:** Zustimmung zum Proposal
- **NO:** Ablehnung des Proposals
- **ABSTAIN:** Enthaltung (zählt zum Quorum, nicht zur Approval)

**Dauer:** 7 Tage

### 5. Quorum-Prüfung
```
Quorum = (yes + no + abstain) / total_voting_power
Quorum_Reached = Quorum >= 0.67
```

### 6. Approval-Prüfung
```
Approval_Ratio = yes / (yes + no)
Approved = Approval_Ratio >= 0.67
```

### 7. Ratifizierung
Wenn beide Bedingungen erfüllt:
- **Quorum ≥ 0.67**
- **Approval ≥ 0.67**

Dann: Proposal **RATIFIZIERT**

### 8. Execution Delay
Nach Ratifizierung wartet das System 24 Stunden (`execution_delay_hours`).

**Zweck:**
- Letzte Sicherheitsprüfung
- Zeit für Einsprüche
- Vorbereitung der Implementierung

### 9. Parameter-Lock
Hash wird in `registry.yaml` festgeschrieben.
Parameter gelten als **immutabel**, bis neues Proposal eingereicht wird.

### 10. Publikation
Ratifiziertes Proposal wird publiziert:
- `23_compliance/certificates/`
- On-chain Anchoring (optional)
- Public documentation

---

## Governance-Regeln

### Änderung versiegelter Parameter

Versiegelte Parameter können **nur** durch ein neues DAO-Proposal geändert werden:

1. **Neues Proposal erstellen** mit höherer Versionsnummer
2. **Begründung** für Änderung bereitstellen
3. **Impact Analysis** durchführen
4. **Abstimmung** nach Standard-Workflow
5. **Quorum ≥ 0.67** und **Approval ≥ 0.67** erforderlich

### Immutability-Flag

Wenn `immutability: true`:
- Parameter können nicht durch Admin-Aktion geändert werden
- Nur DAO-Proposal kann Änderung herbeiführen
- Höchste Sicherheitsstufe

### Adjustable Ranges

Proposals können Bereiche definieren, in denen Anpassungen erlaubt sind:

```yaml
adjustable_ranges:
  dao_treasury_relative: [0.20, 0.35]
  audit_security_absolute_percent_of_amount: [0.0020, 0.0040]
```

**Zweck:**
- Flexibilität innerhalb definierter Grenzen
- Schutz vor extremen Änderungen
- DAO behält Kontrolle

---

## Beispiel: Fee Parameter Lock v5.4.3

### Aktives Proposal
**Datei:** `lock_fee_params_v5_4_3.yaml`
**Status:** RATIFIED
**Ballot:** `ballots/lock_fee_params_v5_4_3.json`

### Versiegelte Parameter

**Transaction Fee:** 3.0% (0.03)
- Developer Share: 1.0% (0.01)
- System Pool: 2.0% (0.02)

**7-Säulen Distribution:**
```
Legal Compliance:       0.35 weight (38.89 bp)
Audit & Security:       0.30 weight (33.33 bp)
Technical Maintenance:  0.30 weight (33.33 bp)
DAO Treasury:           0.25 weight (27.78 bp)
Community Bonus:        0.20 weight (22.22 bp)
Liquidity Reserve:      0.20 weight (22.22 bp)
Marketing & Partnerships: 0.20 weight (22.22 bp)
TOTAL: 1.80 weight (200.00 bp = 2.00%)
```

**Subscription Revenue Split:**
- System Operational: 50%
- DAO Treasury: 30%
- Developer Core: 10%
- Incentive Reserve: 10%

### Mathematische Invarianten

```
1. developer_share + system_pool == transaction_fee_total == 0.03
2. sum(saeulen.decimal_of_amount) == 0.02
3. subscription_revenue_split sum == 1.00
```

**Formel:**
```
share_k = (gewicht_k / 1.80) * 0.02 * A == (gewicht_k / 90) * A
```

### Abstimmungsergebnis

**Stimmen:**
- YES: 128 (94.1%)
- NO: 3 (2.2%)
- ABSTAIN: 5 (3.7%)

**Quorum:** 100% (136/136)
**Approval:** 97.7% (128/131)

**Status:** ✅ RATIFIED AND LOCKED

---

## Verification & Audit

### Hash-Verifikation

```bash
# Proposal-Hash
sha256sum 24_meta_orchestration/proposals/lock_fee_params_v5_4_3.yaml

# Expected:
00499f83b649494e50708dbabf6b92d36189777f46c8cff9c885065c7f71328d
```

### Invarianten-Prüfung

```python
from decimal import Decimal

# Test 1: Total fee
assert Decimal("0.01") + Decimal("0.02") == Decimal("0.03")

# Test 2: System pool sum
saeulen = [
    Decimal("0.0038888888888888889"),
    Decimal("0.0033333333333333333"),
    Decimal("0.0033333333333333333"),
    Decimal("0.0027777777777777778"),
    Decimal("0.0022222222222222222"),
    Decimal("0.0022222222222222222"),
    Decimal("0.0022222222222222222"),
]
assert sum(saeulen) == Decimal("0.02")

# Test 3: Subscription split
subscription = [0.50, 0.30, 0.10, 0.10]
assert sum(subscription) == 1.0
```

### Merkle-Proof

Monatliche Merkle-Proofs aller Ausschüttungen:

```
Root Hash: TBD
Proof Path: 02_audit_logging/merkle_proofs/YYYY-MM.json
```

### SHA-256 Manifest

Quartalsweise Hashes aller Parameterdateien:

```
Manifest: 23_compliance/manifests/fee_distribution_hash_manifest_v5_4_3.json
Period: Q4 2025
```

### Externes Audit

Mindestens 1× pro Jahr:

```
Auditor: [TBD]
Report: 23_compliance/audits/external_audit_2025_Q4.pdf
Status: [Pending]
```

---

## DAO-Governance-Nodes

### Autorisierte Nodes

| Node ID | Wallet | Status |
|---------|--------|--------|
| DAO-GovNode-001 | 0xABCDEF1234567890 | Active |
| DAO-GovNode-002 | 0xFEEFA1DEE55ECA11 | Active |
| DAO-GovNode-003 | 0x... | Active |

### Signing-Prozess

1. **Proposal Review:** Node prüft Proposal
2. **Signature Generation:** Node signiert SHA-256 Hash
3. **Submission:** Signatur wird zu Ballot hinzugefügt
4. **Verification:** Andere Nodes verifizieren Signatur

### Signature-Format

```json
{
  "member": "DAO-GovNode-001",
  "wallet": "0xABCDEF1234567890",
  "signature_sha256": "fb839d2f2c17f6fbc95d5e945b6a3f6728c3290d7aeb2af18b334b1c0edb5c43"
}
```

---

## Snapshot-Periode

**Dauer:** 90 Tage

**Zweck:**
- Regelmäßige Überprüfung der Parameter
- Anpassungen bei Bedarf vorschlagen
- Community-Feedback einholen

**Nächster Snapshot:** 2026-01-12

---

## Change Process

### Schritte für Parameter-Änderung

1. **Vorschlag einreichen**
   - Neues YAML-Proposal erstellen
   - Begründung dokumentieren
   - Impact Analysis durchführen

2. **Community-Diskussion**
   - Forum-Thread erstellen
   - 7 Tage Diskussionsphase
   - Feedback einarbeiten

3. **Formal Proposal**
   - Finales Proposal publizieren
   - SHA-256 Hash berechnen
   - Review-Phase starten

4. **Abstimmung**
   - 7 Tage Voting-Periode
   - Quorum ≥ 0.67
   - Approval ≥ 0.67

5. **Ratifizierung**
   - Bei Erfolg: 24h Execution Delay
   - Parameter-Update
   - Registry-Update

6. **Publikation**
   - Neues Certificate
   - Documentation Update
   - Announcement

---

## Compliance

### GDPR
- ✅ Keine PII in Proposals
- ✅ Pseudonyme Identifier only
- ✅ Privacy by Design

### MiCA
- ✅ Transparente Fee-Struktur
- ✅ Öffentliche Proposals
- ✅ Audit-Trail

### DORA
- ✅ Operational Resilience
- ✅ Change Management
- ✅ Risk Assessment

### AMLD6
- ✅ KYC-ready
- ✅ Governance-Struktur
- ✅ Audit-Anforderungen

---

## Support & Contact

**Maintainer:** SSID DAO Core Team
**Repository:** https://github.com/[organization]/SSID
**Proposals:** 24_meta_orchestration/proposals/
**Registry:** 24_meta_orchestration/proposals/registry.yaml
**Support:** GitHub Issues

---

## References

- [SSID Architecture](../../05_documentation/architecture.md)
- [Fee Distribution System](../../16_codex/fee_distribution_integration_report.md)
- [Production Certificate](../../23_compliance/certificates/fee_fairness_production_certificate_v5_4_3.json)
- [Hash Manifest](../../23_compliance/manifests/fee_distribution_hash_manifest_v5_4_3.json)

---

**Last Updated:** 2025-10-14T23:59:59Z
**Version:** 1.0.0
