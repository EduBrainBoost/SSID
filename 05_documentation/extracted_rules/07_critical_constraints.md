# Critical Constraints

**Generated:** 2025-10-23T20:12:37.627754
**Total Constraints:** 5

---

## FORBIDDEN: SSID_structure_level3_part2_MAX.md:L20

**VERBOTEN modulnah:** `registry/`, `policies/`, `risk/`, `evidence/`, `exceptions/`, `triggers/`, `ci/`, `cd/`

## FORBIDDEN: SSID_structure_level3_part2_MAX.md:L803

| **Anti-Duplikat** | 10% | Verbotene Items: -10 | Keine modulnahen Policies |

## FORBIDDEN: SSID_structure_level3_part3_MAX.md:L644

**Quarantäne (Singleton):** Der einzige erlaubte Quarantäne-Pfad ist `02_audit_logging/quarantine/singleton/quarantine_store/**`. Evidence-Hashes ausschließlich unter `23_compliance/evidence/malware_quarantine_hashes/`. Alle anderen `*/quarantine/**` sind verboten (FAIL in structure_guard & CI-Gates).

## CRITICAL: SSID_structure_level3_part1_MAX.md:L25

**KRITISCH:** `23_compliance/exceptions/structure_exceptions.yaml` ist die einzige gültige Struktur-Exception. Keine Kopie im Root oder modulnah.

## CRITICAL: SSID_structure_level3_part3_MAX.md:L900

**KRITISCH:** Alle Badge-Claims, Scores und Compliance-Status sind nur für die spezifische interne Compliance-Matrix-Version gültig. Badge-Gültigkeit expiriert bei Matrix-Versionsänderungen außerhalb des Kompatibilitätsbereichs. Business-kritische Entscheidungen basierend auf Compliance-Status müssen Badge-Berechnungsdatum und Matrix-Version verifizieren.

