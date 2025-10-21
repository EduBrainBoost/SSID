#!/usr/bin/env python3
"""Temporäres Script zum Hinzufügen der Shards 02-16"""

SHARDS_02_16_YAML = """
  # Shards 02-04
  - regel_id: "SOT-MD-COMPLETE-246"
    zeile: 212
    kategorie: "Shard 02 - Name"
    beschreibung: "Shard 02 heißt 'Dokumente & Nachweise'"
    originaltext: "#### **02. Dokumente & Nachweise**"
    enforcement: "MUST"
    priority: "CRITICAL"
    betroffene_artefakte: ["Contract", "Core"]

  - regel_id: "SOT-MD-COMPLETE-247"
    zeile: 213
    kategorie: "Shard 02 - Capability Urkunden"
    beschreibung: "Shard 02 muss Urkunden unterstützen"
    originaltext: "- Urkunden, Bescheinigungen, Zertifikate, Vollmachten"
    enforcement: "MUST"
    priority: "HIGH"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-248"
    zeile: 213
    kategorie: "Shard 02 - Capability Bescheinigungen"
    beschreibung: "Shard 02 muss Bescheinigungen unterstützen"
    originaltext: "- Urkunden, Bescheinigungen, Zertifikate, Vollmachten"
    enforcement: "MUST"
    priority: "HIGH"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-249"
    zeile: 213
    kategorie: "Shard 02 - Capability Zertifikate"
    beschreibung: "Shard 02 muss Zertifikate unterstützen"
    originaltext: "- Urkunden, Bescheinigungen, Zertifikate, Vollmachten"
    enforcement: "MUST"
    priority: "HIGH"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-250"
    zeile: 213
    kategorie: "Shard 02 - Capability Vollmachten"
    beschreibung: "Shard 02 muss Vollmachten unterstützen"
    originaltext: "- Urkunden, Bescheinigungen, Zertifikate, Vollmachten"
    enforcement: "MUST"
    priority: "HIGH"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-251"
    zeile: 214
    kategorie: "Shard 02 - Capability Digitale Signaturen"
    beschreibung: "Shard 02 muss Digitale Signaturen unterstützen"
    originaltext: "- Digitale Signaturen, Notarisierungen"
    enforcement: "MUST"
    priority: "CRITICAL"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-252"
    zeile: 214
    kategorie: "Shard 02 - Capability Notarisierungen"
    beschreibung: "Shard 02 muss Notarisierungen unterstützen"
    originaltext: "- Digitale Signaturen, Notarisierungen"
    enforcement: "MUST"
    priority: "HIGH"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-253"
    zeile: 216
    kategorie: "Shard 03 - Name"
    beschreibung: "Shard 03 heißt 'Zugang & Berechtigungen'"
    originaltext: "#### **03. Zugang & Berechtigungen**"
    enforcement: "MUST"
    priority: "CRITICAL"
    betroffene_artefakte: ["Contract", "Core"]

  - regel_id: "SOT-MD-COMPLETE-254"
    zeile: 217
    kategorie: "Shard 03 - Capability Rollen"
    beschreibung: "Shard 03 muss Rollen-Management unterstützen"
    originaltext: "- Rollen, Rechte, Mandanten, Delegationen"
    enforcement: "MUST"
    priority: "CRITICAL"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-255"
    zeile: 217
    kategorie: "Shard 03 - Capability Rechte"
    beschreibung: "Shard 03 muss Rechte-Management unterstützen"
    originaltext: "- Rollen, Rechte, Mandanten, Delegationen"
    enforcement: "MUST"
    priority: "CRITICAL"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-256"
    zeile: 217
    kategorie: "Shard 03 - Capability Mandanten"
    beschreibung: "Shard 03 muss Mandanten-Verwaltung unterstützen"
    originaltext: "- Rollen, Rechte, Mandanten, Delegationen"
    enforcement: "MUST"
    priority: "HIGH"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-257"
    zeile: 217
    kategorie: "Shard 03 - Capability Delegationen"
    beschreibung: "Shard 03 muss Delegationen unterstützen"
    originaltext: "- Rollen, Rechte, Mandanten, Delegationen"
    enforcement: "MUST"
    priority: "HIGH"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-258"
    zeile: 218
    kategorie: "Shard 03 - Capability MFA"
    beschreibung: "Shard 03 muss Multi-Factor Authentication (MFA) unterstützen"
    originaltext: "- MFA, Zero-Trust, Session-Management"
    enforcement: "MUST"
    priority: "CRITICAL"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-259"
    zeile: 218
    kategorie: "Shard 03 - Capability Zero-Trust"
    beschreibung: "Shard 03 muss Zero-Trust-Prinzipien unterstützen"
    originaltext: "- MFA, Zero-Trust, Session-Management"
    enforcement: "MUST"
    priority: "CRITICAL"
    betroffene_artefakte: ["Core", "Policy"]

  - regel_id: "SOT-MD-COMPLETE-260"
    zeile: 218
    kategorie: "Shard 03 - Capability Session-Management"
    beschreibung: "Shard 03 muss Session-Management unterstützen"
    originaltext: "- MFA, Zero-Trust, Session-Management"
    enforcement: "MUST"
    priority: "HIGH"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-261"
    zeile: 220
    kategorie: "Shard 04 - Name"
    beschreibung: "Shard 04 heißt 'Kommunikation & Daten'"
    originaltext: "#### **04. Kommunikation & Daten**"
    enforcement: "MUST"
    priority: "CRITICAL"
    betroffene_artefakte: ["Contract", "Core"]

  - regel_id: "SOT-MD-COMPLETE-262"
    zeile: 221
    kategorie: "Shard 04 - Capability Nachrichten"
    beschreibung: "Shard 04 muss Nachrichten unterstützen"
    originaltext: "- Nachrichten, E-Mail, Chat, Datenaustausch"
    enforcement: "MUST"
    priority: "HIGH"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-263"
    zeile: 221
    kategorie: "Shard 04 - Capability E-Mail"
    beschreibung: "Shard 04 muss E-Mail unterstützen"
    originaltext: "- Nachrichten, E-Mail, Chat, Datenaustausch"
    enforcement: "MUST"
    priority: "HIGH"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-264"
    zeile: 221
    kategorie: "Shard 04 - Capability Chat"
    beschreibung: "Shard 04 muss Chat unterstützen"
    originaltext: "- Nachrichten, E-Mail, Chat, Datenaustausch"
    enforcement: "SHOULD"
    priority: "MEDIUM"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-265"
    zeile: 221
    kategorie: "Shard 04 - Capability Datenaustausch"
    beschreibung: "Shard 04 muss Datenaustausch unterstützen"
    originaltext: "- Nachrichten, E-Mail, Chat, Datenaustausch"
    enforcement: "MUST"
    priority: "HIGH"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-266"
    zeile: 222
    kategorie: "Shard 04 - Capability APIs"
    beschreibung: "Shard 04 muss APIs unterstützen"
    originaltext: "- APIs, Schnittstellen, Benachrichtigungen"
    enforcement: "MUST"
    priority: "CRITICAL"
    betroffene_artefakte: ["Core", "Contract"]

  - regel_id: "SOT-MD-COMPLETE-267"
    zeile: 222
    kategorie: "Shard 04 - Capability Schnittstellen"
    beschreibung: "Shard 04 muss Schnittstellen unterstützen"
    originaltext: "- APIs, Schnittstellen, Benachrichtigungen"
    enforcement: "MUST"
    priority: "HIGH"
    betroffene_artefakte: ["Core"]

  - regel_id: "SOT-MD-COMPLETE-268"
    zeile: 222
    kategorie: "Shard 04 - Capability Benachrichtigungen"
    beschreibung: "Shard 04 muss Benachrichtigungen unterstützen"
    originaltext: "- APIs, Schnittstellen, Benachrichtigungen"
    enforcement: "MUST"
    priority: "MEDIUM"
    betroffene_artefakte: ["Core"]
"""

def main():
    with open("02_audit_logging/reports/SoT_Master_COMPLETE_Manual_Extraction_20251019.yaml", "a", encoding="utf-8") as f:
        f.write(SHARDS_02_16_YAML)

    print("OK: Shards 02-04 eingefuegt (Regeln 246-268)")

if __name__ == "__main__":
    main()
