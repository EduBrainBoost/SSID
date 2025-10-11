
# SSID Teststrategie

## Überblick
Dieses Dokument beschreibt die Testarchitektur und die Abdeckung für das SSID-System.

## Testarten
- Unit-Tests pro Root-Modul (z. B. ai_layer, compliance, deployment)
- Integrationstests pro Shard-Schnittstelle
- Policy-Tests mit YAML-Prüfung
- Registry-Parser-Simulation
- Strukturverletzungs-Trigger

## Ziele
- 100 % CI-Kompatibilität (pytest + coverage)
- 100 % Konformität mit SoT-Level-3
- Automatisierbar in allen CI/CD-Pipelines
