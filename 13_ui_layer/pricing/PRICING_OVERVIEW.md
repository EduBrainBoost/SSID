# SSID Preisübersicht (v5.1)

Willkommen zur SSID Enterprise Pricing Übersicht. Die Preise sind **global gültig**, zusätzliche **Regionen** können über **RAT (Region Activation Tokens)** freigeschaltet werden.

## Stufen
- **Core Access** – 29 €/Monat
- **Professional** – 99 €/Monat
- **Enterprise Trust** – 499 €/Monat
- **Global Proof Suite** – 2.000 €/Monat
- **InterFederation Elite** – 10.000 €/Monat
- **Sovereign Infrastructure** – ≥ 25.000 €/Monat

## Regionen (RAT)
- **DACH** (DE/AT/CH) – 0 % Zuschlag
- **EN‑EU** – +5 %
- **US‑CAN** – +10 %
- **LATAM** – +7 %
- **APAC‑EN** – +5 %
- **MENA** – +10 %
- **AFRICA‑EN** – +5 %

## Add‑ons
- Compliance Mesh (+5.000 €/Monat)
- Private PQC Node (+10.000 €/Monat)
- 24/7 SLA (+3.000 €/Monat)
- DAO Seat (+7.000 €/Monat)
- GovChain Bridge (+8.000 €/Monat)

---

### Upsell-Logik (funktional beschrieben)
- Wenn aktive Region ≠ `DACH` → zeige Hinweis auf Region‑Zuschlag (gem. Policy).
- Wenn Tier ≥ `enterprise_trust` und keine Bundles aktiv → zeige EU/Global‑Bundle.
- Bei Laufzeitbindung 12/24/36 Monate → zeige Token‑Rabatt (−5/−10/−15 %).
- Add‑on‑Empfehlungen:
  - **Enterprise Trust** → Compliance Mesh
  - **Global Proof Suite** → PQC Node + 24/7 SLA
  - **Elite/Sovereign** → DAO Seat + GovChain Bridge
