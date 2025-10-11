# SSID Enterprise Community Guidelines

**Version:** 2025-Q4
**Maintainer:** edubrainboost
**Last Updated:** 2025-10-07
**Classification:** PUBLIC - Governance Document
**Gültigkeit:** Enterprise-DAO-Projekte & Sub-Repos (SSID, SSID-OpenCore)

---

## 📜 1. Grundprinzipien

Die SSID-Community basiert auf folgenden unveränderlichen Prinzipien:

### 1.1 Transparenz
- Alle Beiträge, Änderungen und Diskussionen sind öffentlich nachvollziehbar
- Governance-Entscheidungen werden dokumentiert und veröffentlicht
- Code-Reviews sind öffentlich einsehbar (außer sicherheitskritische Inhalte)
- Finanzielle Transaktionen werden quartalsweise offengelegt

### 1.2 Integrität
- Kein Umgang mit rohen personenbezogenen Daten (nur Hash-Proofs)
- Strikte Non-Custodial-Architektur – Nutzer behalten volle Kontrolle
- Keine versteckten Hintertüren oder privilegierten Zugänge
- Open-Source-Prinzip (MIT / Apache 2.0 / EUPL v1.2)

### 1.3 Nachvollziehbarkeit
- Jeder Commit ist mit DID-Signatur verknüpft
- Audit-Logs werden in WORM-Storage unveränderlich gespeichert
- Blockchain-Anchoring für kritische Governance-Entscheidungen
- Vollständige Provenance-Chain für alle Code-Änderungen

### 1.4 Respekt
- Keine Diskriminierung aufgrund von Herkunft, Geschlecht, Religion, etc.
- Konstruktive Kritik ist willkommen, persönliche Angriffe nicht
- Keine Verbreitung von Falschinformationen
- Professionelle Kommunikation auf allen Kanälen

### 1.5 Selbstsouveränität
- Das Projekt dient der digitalen Selbstbestimmung der Nutzer
- Keine Kompromisse zugunsten von Überwachungs- oder Kontrollmechanismen
- Privacy by Design als nicht verhandelbares Kernprinzip

---

## 🔄 2. Contribution-Flow

### 2.1 Pull-Request-Prozess

Alle Änderungen erfolgen ausschließlich über Pull-Requests mit folgenden Schritten:

1. **Fork & Branch:** Erstelle einen Fork und einen feature-branch
2. **Develop & Test:** Implementiere Änderungen + Tests
3. **Submit PR:** Reiche Pull-Request mit detaillierter Beschreibung ein
4. **CI Validation:** Automatische Prüfung durch CI-Pipeline
5. **Code Review:** Mindestens 1 Maintainer-Review erforderlich
6. **Merge:** Nach Approval wird PR gemerged

### 2.2 Erforderliche Checks

Jeder PR benötigt:

✅ **Erfolgreiche CI-Gates:**
- Root-24-LOCK-Überprüfung (`structure_guard.sh`)
- Alle Pytest-Suites (Compliance, Review, Anti-Gaming)
- YAML-Validierung aller geänderten Config-Dateien
- Checksum-Integrität

✅ **Audit-Log-Anhänge:**
- Änderungen müssen in `02_audit_logging/logs/` dokumentiert sein
- Bei strukturellen Änderungen: Eintrag in `registry_lock.yaml`

✅ **Reviewer-Zuweisung:**
- Gemäß `reviewer_assignments.yaml`
- Mindestens 1 Maintainer-Approval für normale PRs
- Mindestens 2 Maintainer-Approvals für kritische Änderungen

### 2.3 Spezielle Anforderungen für SoT-Änderungen

Änderungen an Source-of-Truth-Dateien (`16_codex/structure/...`) erfordern:

- **2 Maintainer-Signaturen** (DID-signiert)
- **Quorum-Abstimmung** nach `maintainers_enterprise.yaml → governance_committee`
- **14-Tage-Kommentierungsfrist** für Community-Feedback
- **Formales RFC** (Request for Comments) im Governance-Repo

---

## 💬 3. Offene Kommunikation

### 3.1 Diskussionskanäle

| Kanal | Zweck | Zugang |
|-------|-------|--------|
| **Matrix/Element** | `#ssid-governance:matrix.org` | Öffentlich |
| **GitHub Discussions** | Langform-Diskussionen, RFCs | Öffentlich |
| **GitHub Issues** | Bug-Reports, Feature-Requests | Öffentlich |
| **E-Mail** | `community@ssid.foundation` | Öffentlich |
| **Signal (Maintainers)** | Vertrauliche Governance | Nur Maintainer |

### 3.2 Reaktionszeiten

- **Security Issues:** < 24 Stunden
- **Bug Reports:** < 7 Tage
- **Feature Requests:** < 14 Tage
- **RFCs:** 14-Tage-Kommentierungsfrist

---

## 🤝 4. Governance-Ethik

### 4.1 Non-Custodial-Mandat

Alle Beteiligten verpflichten sich:

- Keine Implementierung von Custody-Funktionen
- Keine zentrale Kontrolle über Nutzer-Wallets oder Private Keys
- Keine Backdoors für "administrative Zugriffe"
- Strikte Einhaltung der Hash-Only-Datenspeicherung

### 4.2 Interessenkonflikte

**Offenlegungspflicht:**
- Alle finanziellen Beziehungen zu konkurrierenden Projekten
- Consulting-Tätigkeiten für regulatorische Behörden
- Eigentumsanteile an Custody-Service-Providern
- Führungspositionen in kompetitiven Identity-Systemen

**Verbotene Aktivitäten:**
- Direkte Konkurrenz zu SSID
- Custody-Services konfliktär zum Non-Custodial-Ansatz
- Teilnahme an regulatorischer Durchsetzung gegen SSID
- Finanzielles Interesse an Entitäten, die SSID schaden

### 4.3 Open-Source-Lizenzierung

**Hauptprojekt:** MIT License (permissiv für kommerzielle Nutzung)
**Sub-Module:** Apache 2.0 / EUPL v1.2
**Dokumentation:** CC-BY-4.0 (Creative Commons)

---

## ⚖️ 5. Eskalationsprozess

### 5.1 Code-of-Conduct-Verstöße

1. **Meldung an Compliance-Maintainer**
2. **Anerkennung innerhalb 48h**
3. **Interne Untersuchung (14 Tage)**
4. **Entscheidung & Dokumentation**
5. **Ggf. Sanktionen** (Verwarnung → Suspendierung → Ausschluss)

### 5.2 Meldewege

**Öffentliche Verstöße:** GitHub Issue oder `conduct@ssid.foundation`
**Vertrauliche Verstöße:** PGP-verschlüsselt an Lead Auditor

---

## 🛡️ 6. Sicherheits-Richtlinien

### 6.1 Responsible Disclosure

**Sicherheitslücken melden:**
1. **NICHT** öffentlich posten
2. E-Mail an `security@ssid.foundation` (PGP: `9F3E 122B ...`)
3. Erwarte Acknowledgment innerhalb 48h
4. Koordinierte Offenlegung nach Fix (typisch 90 Tage)

### 6.2 Security Best Practices

- 2FA auf GitHub/GitLab
- GPG-signierte Commits
- Regelmäßige Dependency-Updates
- Keine Secrets in Code

---

## 🎓 7. Onboarding & Mentorship

### 7.1 Neue Contributors

**Erste Schritte:**
1. Lies `README.md` und `CONTRIBUTING.md`
2. Setup Dev-Environment (`12_tooling/setup/`)
3. Starte mit "Good First Issues"

### 7.2 Paths to Maintainership

**Kriterien:**
- 6+ Monate aktive Contributions
- Mindestens 50 merged PRs
- Community-Engagement
- Governance-Verständnis

**Bewerbung:** 3/4-Mehrheit im Governance Committee erforderlich

---

## 🔄 8. Änderungshistorie

**Version:** 2025-Q4
**Nächster Review:** 2026-Q1
**Änderungsprozess:** RFC + 2/3-Mehrheit + 30-Tage-Inkrafttreten

---

## 📄 9. Lizenz

Dieses Dokument steht unter **CC-BY-4.0** (Creative Commons Attribution 4.0 International).

---

## 📞 10. Kontakt

**Allgemeine Fragen:** `community@ssid.foundation`
**Governance:** `governance@ssid.foundation`
**Security:** `security@ssid.foundation` (PGP)
**Conduct-Verstöße:** `conduct@ssid.foundation`

**Matrix:** `#ssid-governance:matrix.org`
**GitHub:** `https://github.com/ssid-project/governance`

---

**Dokument-Hash:** `sha256:TO_BE_FILLED_BY_CI`
**Attestation:** Signiert von allen Maintainern gemäß `maintainers_enterprise.yaml`
**Blockchain-Anchor:** `registry_lock.yaml → governance_docs`
