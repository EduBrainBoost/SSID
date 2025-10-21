# Pricing Token-Lock Widget (G3) – v5.2

**Ziel:** Visualisiert Token-basierte Discounts und Overage-Preise gemäß *Enterprise Subscription Model v5.2*.

## Komponenten
- TokenBalanceBadge: Zeigt verifizierten Token-Lock (on-chain Proof) an.
- DiscountMeter: Berechnet Rabattstufe (BRONZE/SILVER/GOLD) gemäß Partner-Programm (E4).
- OverageEstimator: Schätzt Overage-Kosten je 1k Requests anhand `rate_limit_policy.yaml`.

## Datenquellen
- Pricing SoT: `07_governance_legal/docs/pricing/enterprise_subscription_model_v5_2.yaml`
- SLA: `07_governance_legal/docs/sla/sla_definitions_v5_2.yaml`
- RateLimits: `03_core/services/rate_limit_policy.yaml`

## Compliance
- Non-custodial: Nur Hashes/Proofs on-chain, keine PII.
- SAFE-FIX: UI blockiert, wenn Policy- oder Threshold-Bruch erkannt.

## UI-Verhalten
- Bei überzogener Quote: Zeige Overage-Preis pro 1k Requests (Tier-abhängig).
- Bei Partner-Rabatt: Badge + prozentuale Reduktion der Basisgebühr.
- Bei Inkompatibilität (Eligibility-Fail): Disable CTA + Policy-Hinweis.
