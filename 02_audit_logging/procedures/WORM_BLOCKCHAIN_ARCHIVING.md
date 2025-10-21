# WORM Storage & Blockchain Anchoring - Procedures

**Version:** 1.0.0
**Datum:** 2025-10-18
**Owner:** SSID Compliance Team
**Status:** DRAFT - Awaiting Implementation

---

## Überblick

Dieses Dokument beschreibt die Prozeduren für:
1. **WORM Storage (Write-Once-Read-Many):** Unveränderliche Speicherung von Audit-Artefakten
2. **Blockchain Anchoring:** Kryptographische Verankerung von Policy-Hashes für Tamper-Proof Audit-Trail

---

## WORM Storage

### Zweck

WORM Storage garantiert, dass einmal geschriebene Audit-Artefakte nicht mehr verändert oder gelöscht werden können. Dies ist essentiell für:
- Regulatorische Compliance (SOC 2, ISO 27001)
- Forensische Analysen
- Tamper-Proof Audit-Trails
- Langzeit-Archivierung (7+ Jahre)

---

### Artefakte für WORM Storage

| Artefakt-Typ | Pfad-Pattern | Retention | Grund |
|--------------|--------------|-----------|-------|
| **Policy-Versionen** | `24_meta_orchestration/registry/qa_corpus_policy.yaml` | 7 Jahre | Compliance-Nachweis |
| **Audit-Reports** | `02_audit_logging/reports/QA_MASTER_SUITE_*.md` | 7 Jahre | Audit-Trails |
| **Migration-Reports** | `02_audit_logging/reports/*_MIGRATION.md` | 7 Jahre | Change-Management |
| **SHA256 Hashes** | `02_audit_logging/archives/qa_master_suite/*_hashes*.json` | 10 Jahre | Integrität |
| **Enforcement-Logs** | `02_audit_logging/logs/qa_policy_enforcement.jsonl` | 5 Jahre | Violation-Tracking |
| **Evidence-Artefakte** | `23_compliance/evidence/**/*.json` | 7 Jahre | Compliance-Evidence |
| **WORM Snapshots** | `02_audit_logging/storage/worm/immutable_store/**` | 10 Jahre | Unveränderliche Kopien |

---

### WORM Storage Optionen

#### Option 1: AWS S3 Object Lock (Empfohlen)

**Vorteile:**
- Native WORM-Funktionalität
- Automatische Retention-Policies
- Compliance-Mode (auch Admin kann nicht löschen)
- Versionierung eingebaut

**Setup:**

```bash
# 1. S3 Bucket mit Object Lock erstellen
aws s3api create-bucket \
  --bucket ssid-worm-storage \
  --region eu-central-1 \
  --object-lock-enabled-for-bucket

# 2. Retention-Policy konfigurieren
aws s3api put-object-lock-configuration \
  --bucket ssid-worm-storage \
  --object-lock-configuration '{
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "COMPLIANCE",
        "Years": 7
      }
    }
  }'

# 3. Artefakte hochladen
aws s3 cp 02_audit_logging/reports/QA_MASTER_SUITE_COMPLIANCE_AUDIT_2025_10_18.md \
  s3://ssid-worm-storage/audit-reports/2025-10-18/ \
  --object-lock-mode COMPLIANCE \
  --object-lock-retain-until-date 2032-10-18T00:00:00Z
```

**Kosten:** ~$0.023/GB/Monat (Standard Storage)

---

#### Option 2: Azure Immutable Blob Storage

**Vorteile:**
- Time-based retention policies
- Legal hold support
- WORM-compliant (SEC 17a-4, FINRA)

**Setup:**

```bash
# 1. Storage Account erstellen
az storage account create \
  --name ssidwormstorage \
  --resource-group ssid-compliance \
  --location westeurope \
  --sku Standard_LRS

# 2. Container mit Immutability Policy
az storage container immutability-policy create \
  --account-name ssidwormstorage \
  --container-name audit-artefacts \
  --period 2555 \
  --allow-protected-append-writes false

# 3. Upload
az storage blob upload \
  --account-name ssidwormstorage \
  --container-name audit-artefacts \
  --name audit-reports/2025-10-18/QA_MASTER_SUITE_COMPLIANCE_AUDIT.md \
  --file 02_audit_logging/reports/QA_MASTER_SUITE_COMPLIANCE_AUDIT_2025_10_18.md
```

---

#### Option 3: Local WORM Filesystem (Budget-Option)

**Vorteile:**
- Keine Cloud-Kosten
- Volle Kontrolle
- Airgap möglich

**Nachteile:**
- Physische Sicherheit erforderlich
- Keine automatische Replikation

**Setup (Linux mit ext4/xfs):**

```bash
# 1. Dediziertes WORM-Verzeichnis
sudo mkdir -p /mnt/worm-storage/ssid-audit
sudo chown compliance:compliance /mnt/worm-storage/ssid-audit

# 2. Immutable-Attribut setzen (nach Upload)
sudo chattr +i /mnt/worm-storage/ssid-audit/audit-reports/2025-10-18/QA_MASTER_SUITE_COMPLIANCE_AUDIT.md

# 3. Verify
lsattr /mnt/worm-storage/ssid-audit/audit-reports/2025-10-18/QA_MASTER_SUITE_COMPLIANCE_AUDIT.md
# Sollte zeigen: ----i--------e---
```

**Hinweis:** Für regulatorische Compliance ist Cloud-basiertes WORM (Option 1 oder 2) empfohlen.

---

### WORM Storage Workflow

```
1. ARTEFAKT ERSTELLEN
   ↓
   QA-Report, Policy-Version, etc.
   ↓
2. SHA256 HASH BERECHNEN
   ↓
   sha256sum <file>
   ↓
3. METADATA ERSTELLEN
   ↓
   {
     "file": "QA_MASTER_SUITE_COMPLIANCE_AUDIT_2025_10_18.md",
     "sha256": "abc123...",
     "timestamp": "2025-10-18T16:30:00Z",
     "retention_until": "2032-10-18T00:00:00Z",
     "compliance_framework": "SOC 2, ISO 27001"
   }
   ↓
4. UPLOAD ZU WORM STORAGE
   ↓
   AWS S3 Object Lock / Azure Immutable Blob
   ↓
5. VERIFY IMMUTABILITY
   ↓
   Versuch zu löschen sollte fehlschlagen
   ↓
6. LOG IN REGISTRY
   ↓
   24_meta_orchestration/registry/worm_storage_index.yaml
```

---

## Blockchain Anchoring

### Zweck

Blockchain Anchoring verankert SHA256-Hashes von kritischen Artefakten in einer öffentlichen Blockchain (z.B. Bitcoin, Ethereum). Dies bietet:
- **Timestamping:** Beweis, dass Artefakt zu bestimmtem Zeitpunkt existierte
- **Tamper-Proof:** Hash in unveränderlicher Blockchain
- **Third-Party Verification:** Jeder kann Hash verifizieren

---

### Artefakte für Blockchain Anchoring

| Artefakt | Hash-Quelle | Frequenz |
|----------|-------------|----------|
| **QA Policy** | `qa_corpus_policy.yaml` SHA256 | Bei jeder Änderung |
| **Audit Reports** | Report-Datei SHA256 | Nach jedem Audit |
| **Evidence Chains** | Merkle Root von Evidence | Monatlich |
| **Registry Snapshots** | Registry-State SHA256 | Quartalsweise |

---

### Blockchain Anchoring Services

#### Option 1: OpenTimestamps (Bitcoin) - Kostenlos

**Vorteile:**
- Bitcoin-basiert (höchste Sicherheit)
- Kostenlos
- Open Source
- Dezentralisiert

**Setup:**

```bash
# 1. Install OpenTimestamps
pip install opentimestamps-client

# 2. Create timestamp
ots stamp 24_meta_orchestration/registry/qa_corpus_policy.yaml

# Erzeugt: qa_corpus_policy.yaml.ots (Timestamp-Proof)

# 3. Upgrade (nach Bitcoin-Bestätigung, ~10 Min - 1 Std)
ots upgrade qa_corpus_policy.yaml.ots

# 4. Verify
ots verify qa_corpus_policy.yaml.ots
# Zeigt: Bitcoin block <block_number> attests data existed as of <timestamp>
```

**Verwendung:**

```bash
# Bei Policy-Änderung
sha256sum 24_meta_orchestration/registry/qa_corpus_policy.yaml
ots stamp 24_meta_orchestration/registry/qa_corpus_policy.yaml
git add 24_meta_orchestration/registry/qa_corpus_policy.yaml.ots
git commit -m "chore: Add blockchain timestamp for policy v2.0.0"
```

---

#### Option 2: Ethereum Smart Contract

**Vorteile:**
- Programmierbare Logik
- Schnellere Bestätigung (~15 Sek)
- Smart Contract kann automatisch prüfen

**Nachteile:**
- Gas Fees (~$1-$10 pro Anchor)
- Komplexer

**Smart Contract Beispiel (Solidity):**

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SSIDAuditAnchoring {
    struct AnchorRecord {
        bytes32 hash;
        uint256 timestamp;
        string artifactType;
    }

    mapping(bytes32 => AnchorRecord) public anchors;

    event HashAnchored(bytes32 indexed hash, uint256 timestamp, string artifactType);

    function anchorHash(bytes32 _hash, string memory _artifactType) public {
        require(anchors[_hash].timestamp == 0, "Hash already anchored");

        anchors[_hash] = AnchorRecord({
            hash: _hash,
            timestamp: block.timestamp,
            artifactType: _artifactType
        });

        emit HashAnchored(_hash, block.timestamp, _artifactType);
    }

    function verifyHash(bytes32 _hash) public view returns (bool, uint256, string memory) {
        AnchorRecord memory record = anchors[_hash];
        if (record.timestamp == 0) {
            return (false, 0, "");
        }
        return (true, record.timestamp, record.artifactType);
    }
}
```

---

#### Option 3: Hybrid (OpenTimestamps + Private Ledger)

**Empfohlen für SSID:**

1. **OpenTimestamps (Bitcoin):** Für externe Verifikation, kostenlos
2. **Private Ledger:** Für interne Audit-Trail, schnell

**Workflow:**

```bash
# 1. Sofortige Aufzeichnung in privater DB
python tools/anchor_to_private_ledger.py \
  --file 24_meta_orchestration/registry/qa_corpus_policy.yaml \
  --type "qa-policy" \
  --version "2.0.0"

# 2. Bitcoin-Anchoring (asynchron, dauert 10-60 Min)
ots stamp 24_meta_orchestration/registry/qa_corpus_policy.yaml &

# 3. Registry aktualisieren
echo "blockchain_anchor_timestamp: 2025-10-18T16:30:00Z" >> registry.yaml
echo "blockchain_anchor_bitcoin_tx: <pending>" >> registry.yaml
```

---

### Blockchain Anchoring Workflow

```
1. ARTEFAKT FINALISIERT
   ↓
   QA Policy v2.0.0 approved
   ↓
2. SHA256 HASH BERECHNEN
   ↓
   sha256sum qa_corpus_policy.yaml
   → 173aedef08b3db974b6d4891aa84269f52970d65b5389697ce7dd1811033602f
   ↓
3. BLOCKCHAIN TIMESTAMP ERSTELLEN
   ↓
   ots stamp qa_corpus_policy.yaml
   ↓
4. WARTEN AUF BITCOIN-BESTÄTIGUNG
   ↓
   ~10 Minuten - 1 Stunde
   ↓
5. UPGRADE TIMESTAMP
   ↓
   ots upgrade qa_corpus_policy.yaml.ots
   ↓
6. VERIFY
   ↓
   ots verify qa_corpus_policy.yaml.ots
   → Verified in Bitcoin block 876543 at 2025-10-18 16:45:23 UTC
   ↓
7. REGISTRY AKTUALISIEREN
   ↓
   blockchain_anchor:
     bitcoin_block: 876543
     timestamp: 2025-10-18T16:45:23Z
     ots_file: qa_corpus_policy.yaml.ots
```

---

## Automation Script

### WORM + Blockchain Anchoring Automation

```bash
#!/bin/bash
# File: tools/worm_blockchain_archive.sh
# Purpose: Automate WORM storage and blockchain anchoring

set -euo pipefail

# Configuration
WORM_BUCKET="s3://ssid-worm-storage"
RETENTION_YEARS=7
OTS_ENABLED=true

function archive_to_worm() {
    local file="$1"
    local retention_date=$(date -d "+${RETENTION_YEARS} years" +%Y-%m-%dT%H:%M:%SZ)

    echo "📦 Archiving to WORM storage: $file"

    # Calculate SHA256
    local sha256=$(sha256sum "$file" | awk '{print $1}')
    echo "   SHA256: $sha256"

    # Upload to S3 with Object Lock
    aws s3 cp "$file" \
        "${WORM_BUCKET}/$(dirname "$file")/" \
        --object-lock-mode COMPLIANCE \
        --object-lock-retain-until-date "$retention_date" \
        --metadata "sha256=$sha256,archived=$(date -u +%Y-%m-%dT%H:%M:%SZ)"

    echo "   ✅ Uploaded with retention until $retention_date"
}

function blockchain_anchor() {
    local file="$1"

    if [ "$OTS_ENABLED" = true ]; then
        echo "⛓️  Creating blockchain timestamp: $file"

        ots stamp "$file"

        echo "   ✅ Timestamp created: ${file}.ots"
        echo "   ⏳ Upgrade will happen automatically in ~10-60 minutes"

        # Background upgrade check
        (sleep 3600; ots upgrade "${file}.ots" 2>/dev/null || true) &
    fi
}

function main() {
    local file="$1"

    if [ ! -f "$file" ]; then
        echo "❌ File not found: $file"
        exit 1
    fi

    echo "🔒 WORM + Blockchain Archiving"
    echo "   File: $file"
    echo ""

    archive_to_worm "$file"
    blockchain_anchor "$file"

    echo ""
    echo "✅ Archiving complete!"
    echo ""
    echo "To verify:"
    echo "  - WORM: aws s3api head-object --bucket ssid-worm-storage --key ..."
    echo "  - Blockchain: ots verify ${file}.ots"
}

# Usage: ./worm_blockchain_archive.sh <file>
main "$@"
```

**Verwendung:**

```bash
# QA Policy archivieren
./tools/worm_blockchain_archive.sh 24_meta_orchestration/registry/qa_corpus_policy.yaml

# Audit Report archivieren
./tools/worm_blockchain_archive.sh 02_audit_logging/reports/QA_MASTER_SUITE_COMPLIANCE_AUDIT_2025_10_18.md
```

---

## Verification Procedures

### WORM Storage Verification

```bash
# AWS S3 Object Lock
aws s3api head-object \
  --bucket ssid-worm-storage \
  --key audit-reports/2025-10-18/QA_MASTER_SUITE_COMPLIANCE_AUDIT.md

# Should show:
#   ObjectLockMode: COMPLIANCE
#   ObjectLockRetainUntilDate: 2032-10-18T00:00:00Z

# Try to delete (should fail)
aws s3 rm s3://ssid-worm-storage/audit-reports/2025-10-18/QA_MASTER_SUITE_COMPLIANCE_AUDIT.md
# Error: Access Denied (Object is locked)
```

### Blockchain Verification

```bash
# Verify OpenTimestamps
ots verify 24_meta_orchestration/registry/qa_corpus_policy.yaml.ots

# Expected output:
# Success! Bitcoin attests data existed as of Wed Oct 18 16:45:23 2025 UTC
# Complete proof:
#  * File sha256 hash: 173aedef08b3db974b6d4891aa84269f52970d65b5389697ce7dd1811033602f
#  * Bitcoin block 876543
```

---

## Next Steps

### Phase 1: Setup (Woche 1-2)

- [ ] AWS S3 Bucket mit Object Lock erstellen
- [ ] IAM Policies für WORM-Zugriff konfigurieren
- [ ] OpenTimestamps Client installieren
- [ ] Automation Script testen

### Phase 2: Initial Archiving (Woche 3)

- [ ] QA Policy v2.0.0 in WORM archivieren
- [ ] Audit Report 2025-10-18 in WORM archivieren
- [ ] Migration Report in WORM archivieren
- [ ] Blockchain-Timestamps erstellen

### Phase 3: Automation (Woche 4)

- [ ] CI/CD Integration (GitHub Actions)
- [ ] Automatische Archivierung bei Policy-Updates
- [ ] Monatliche Evidence-Archivierung
- [ ] Monitoring & Alerting

### Phase 4: Documentation & Training (Woche 5)

- [ ] SOP (Standard Operating Procedure) erstellen
- [ ] Team-Training durchführen
- [ ] Runbooks für Incident Response

---

## Compliance Mapping

| Framework | Requirement | WORM/Blockchain Erfüllung |
|-----------|-------------|---------------------------|
| **SOC 2 (CC6.1)** | Logical Access Controls | ✅ Immutable audit logs |
| **ISO 27001 (A.12.4.1)** | Event Logging | ✅ Tamper-proof logs |
| **NIST CSF (PR.PT-1)** | Audit Records | ✅ Blockchain-verified |
| **SEC 17a-4** | WORM Storage | ✅ S3 Object Lock (compliant) |
| **GDPR (Art. 32)** | Integrity of Processing | ✅ Cryptographic verification |

---

## Kontakt & Support

**WORM/Blockchain Owner:** SSID Compliance Team
**Lead:** bibel
**Email:** compliance@ssid-project.internal
**Emergency:** compliance-emergency@ssid-project.internal

---

**END OF PROCEDURES DOCUMENT**

*Status: DRAFT - Awaiting Implementation*
*Classification: INTERNAL USE ONLY*
