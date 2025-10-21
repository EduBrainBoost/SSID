# SSID CI Mini-Bundle – OPA + Playwright (v5.1)

**Zweck:** Policy-Check (OPA) + UI-E2E (Playwright) als GitHub Actions Workflow.

## Enthalten
- `.github/workflows/ci_mini_opa_playwright.yml`
- `playwright.config.ts`, `13_ui_layer/e2e/pricing.spec.ts`
- `package.json` (Node 20, Playwright, http-server)
- Policies: `23_compliance/policies/*.rego`
- Pricing JSON: `07_governance_legal/docs/pricing/enterprise_subscription_model_v5.json`

## Funktionsweise
1. OPA evaluiert `pricing_enforcement.rego` gegen das Pricing-JSON (allow == true erforderlich).
2. OPA evaluiert `rat_enforcement.rego` mit einem Beispiel-Request (Global-Bundle ab Global Proof Suite).
3. Statischer Preview-Server stellt Pricing-JSON & RAT-Registry bereit.
4. Playwright prüft Erreichbarkeit & Basisstruktur.

## Voraussetzungen
- Repo enthält die o. g. Dateien (YAML→JSON-Build kann im Haupt-CI separat erfolgen).
- Keine Secrets notwendig.
