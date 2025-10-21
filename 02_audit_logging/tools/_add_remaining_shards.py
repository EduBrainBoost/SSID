#!/usr/bin/env python3
"""Fügt Shards 07-16 hinzu (Regeln 288-378)"""

shards_data = [
    # Shard 07
    (288, 236, "Shard 07 - Name", "Shard 07 heißt 'Familie & Soziales'", "CRITICAL"),
    (289, 237, "Shard 07 - Capability Geburt", "Shard 07 muss Geburt-Dokumente unterstützen", "HIGH"),
    (290, 237, "Shard 07 - Capability Heirat", "Shard 07 muss Heirat-Dokumente unterstützen", "HIGH"),
    (291, 237, "Shard 07 - Capability Scheidung", "Shard 07 muss Scheidung-Dokumente unterstützen", "MEDIUM"),
    (292, 237, "Shard 07 - Capability Adoption", "Shard 07 muss Adoption-Dokumente unterstützen", "MEDIUM"),
    (293, 237, "Shard 07 - Capability Erbe", "Shard 07 muss Erbe-Verwaltung unterstützen", "MEDIUM"),
    (294, 238, "Shard 07 - Capability Vormundschaft", "Shard 07 muss Vormundschaft unterstützen", "MEDIUM"),
    (295, 238, "Shard 07 - Capability Betreuung", "Shard 07 muss Betreuung unterstützen", "MEDIUM"),
    (296, 238, "Shard 07 - Capability Sozialleistungen", "Shard 07 muss Sozialleistungen unterstützen", "MEDIUM"),
    (297, 239, "Shard 07 - Capability Vereine", "Shard 07 muss Vereine-Verwaltung unterstützen", "LOW"),
    (298, 239, "Shard 07 - Capability Mitgliedschaften", "Shard 07 muss Mitgliedschaften unterstützen", "LOW"),
    (299, 239, "Shard 07 - Capability Ehrenamt", "Shard 07 muss Ehrenamt unterstützen", "LOW"),

    # Shard 08
    (300, 241, "Shard 08 - Name", "Shard 08 heißt 'Mobilität & Fahrzeuge'", "CRITICAL"),
    (301, 242, "Shard 08 - Capability Führerschein", "Shard 08 muss Führerschein-Verwaltung unterstützen", "HIGH"),
    (302, 242, "Shard 08 - Capability KFZ-Zulassung", "Shard 08 muss KFZ-Zulassung unterstützen", "HIGH"),
    (303, 242, "Shard 08 - Capability Fahrzeugpapiere", "Shard 08 muss Fahrzeugpapiere unterstützen", "HIGH"),
    (304, 243, "Shard 08 - Capability TÜV/AU", "Shard 08 muss TÜV/AU-Verwaltung unterstützen", "MEDIUM"),
    (305, 243, "Shard 08 - Capability Fahrzeugkauf/-verkauf", "Shard 08 muss Fahrzeugkauf/-verkauf unterstützen", "MEDIUM"),
    (306, 243, "Shard 08 - Capability Parkausweise", "Shard 08 muss Parkausweise unterstützen", "LOW"),
    (307, 244, "Shard 08 - Capability Maut-Accounts", "Shard 08 muss Maut-Accounts unterstützen", "LOW"),
    (308, 244, "Shard 08 - Capability Kfz-Versicherung", "Shard 08 muss Kfz-Versicherung unterstützen", "HIGH"),
    (309, 244, "Shard 08 - Capability Fahrzeughistorie", "Shard 08 muss Fahrzeughistorie unterstützen", "MEDIUM"),

    # Block 3
    (310, 248, "Shard - Block 3 Definition", "Block 3 heißt 'WIRTSCHAFT & VERMÖGEN' und umfasst Shards 09-12", "CRITICAL"),

    # Shard 09
    (311, 250, "Shard 09 - Name", "Shard 09 heißt 'Arbeit & Karriere'", "CRITICAL"),
    (312, 251, "Shard 09 - Capability Arbeitsverträge", "Shard 09 muss Arbeitsverträge unterstützen", "HIGH"),
    (313, 251, "Shard 09 - Capability Gehalt", "Shard 09 muss Gehalt-Verwaltung unterstützen", "HIGH"),
    (314, 251, "Shard 09 - Capability Bewerbungen", "Shard 09 muss Bewerbungen unterstützen", "MEDIUM"),
    (315, 251, "Shard 09 - Capability Referenzen", "Shard 09 muss Referenzen unterstützen", "MEDIUM"),
    (316, 252, "Shard 09 - Capability Freelancing", "Shard 09 muss Freelancing unterstützen", "MEDIUM"),
    (317, 252, "Shard 09 - Capability Honorare", "Shard 09 muss Honorare unterstützen", "MEDIUM"),
    (318, 252, "Shard 09 - Capability Arbeitszeugnisse", "Shard 09 muss Arbeitszeugnisse unterstützen", "HIGH"),

    # Shard 10
    (319, 254, "Shard 10 - Name", "Shard 10 heißt 'Finanzen & Banking'", "CRITICAL"),
    (320, 255, "Shard 10 - Capability Konten", "Shard 10 muss Konten-Verwaltung unterstützen", "HIGH"),
    (321, 255, "Shard 10 - Capability Zahlungen", "Shard 10 muss Zahlungen unterstützen", "HIGH"),
    (322, 255, "Shard 10 - Capability Überweisungen", "Shard 10 muss Überweisungen unterstützen", "HIGH"),
    (323, 255, "Shard 10 - Capability Kredite", "Shard 10 muss Kredite unterstützen", "MEDIUM"),
    (324, 256, "Shard 10 - Capability Investments", "Shard 10 muss Investments unterstützen", "MEDIUM"),
    (325, 256, "Shard 10 - Capability Portfolios", "Shard 10 muss Portfolio-Verwaltung unterstützen", "MEDIUM"),
    (326, 256, "Shard 10 - Capability DeFi", "Shard 10 muss DeFi (Decentralized Finance) unterstützen", "MEDIUM"),
    (327, 256, "Shard 10 - Capability Krypto", "Shard 10 muss Krypto-Verwaltung unterstützen", "MEDIUM"),
    (328, 257, "Shard 10 - Capability Abonnements", "Shard 10 muss Abonnements unterstützen", "LOW"),
    (329, 257, "Shard 10 - Capability Loyalitäts-Programme", "Shard 10 muss Loyalitäts-Programme unterstützen", "LOW"),

    # Shard 11
    (330, 259, "Shard 11 - Name", "Shard 11 heißt 'Versicherungen & Risiken'", "CRITICAL"),
    (331, 260, "Shard 11 - Capability Versicherungsarten", "Shard 11 muss alle Versicherungsarten unterstützen", "HIGH"),
    (332, 261, "Shard 11 - Capability Schäden", "Shard 11 muss Schäden-Verwaltung unterstützen", "HIGH"),
    (333, 261, "Shard 11 - Capability Claims", "Shard 11 muss Claims-Verwaltung unterstützen", "HIGH"),
    (334, 261, "Shard 11 - Capability Policen", "Shard 11 muss Policen-Verwaltung unterstützen", "HIGH"),
    (335, 261, "Shard 11 - Capability Prämien", "Shard 11 muss Prämien-Verwaltung unterstützen", "MEDIUM"),

    # Shard 12
    (336, 263, "Shard 12 - Name", "Shard 12 heißt 'Immobilien & Grundstücke'", "CRITICAL"),
    (337, 264, "Shard 12 - Capability Eigentum", "Shard 12 muss Eigentums-Verwaltung unterstützen", "HIGH"),
    (338, 264, "Shard 12 - Capability Miete", "Shard 12 muss Miete-Verwaltung unterstützen", "HIGH"),
    (339, 264, "Shard 12 - Capability Pacht", "Shard 12 muss Pacht-Verwaltung unterstützen", "MEDIUM"),
    (340, 264, "Shard 12 - Capability Grundbuch", "Shard 12 muss Grundbuch-Integration unterstützen", "HIGH"),
    (341, 265, "Shard 12 - Capability Hypotheken", "Shard 12 muss Hypotheken unterstützen", "MEDIUM"),
    (342, 265, "Shard 12 - Capability Bewertungen", "Shard 12 muss Immobilien-Bewertungen unterstützen", "MEDIUM"),
    (343, 265, "Shard 12 - Capability Nutzungsrechte", "Shard 12 muss Nutzungsrechte unterstützen", "MEDIUM"),

    # Block 4
    (344, 269, "Shard - Block 4 Definition", "Block 4 heißt 'GESCHÄFT & ÖFFENTLICH' und umfasst Shards 13-16", "CRITICAL"),

    # Shard 13
    (345, 271, "Shard 13 - Name", "Shard 13 heißt 'Unternehmen & Gewerbe'", "CRITICAL"),
    (346, 272, "Shard 13 - Capability Firmendaten", "Shard 13 muss Firmendaten unterstützen", "HIGH"),
    (347, 272, "Shard 13 - Capability Handelsregister", "Shard 13 muss Handelsregister-Integration unterstützen", "HIGH"),
    (348, 272, "Shard 13 - Capability Lizenzen", "Shard 13 muss Lizenzen-Verwaltung unterstützen", "MEDIUM"),
    (349, 272, "Shard 13 - Capability B2B", "Shard 13 muss B2B-Funktionen unterstützen", "HIGH"),
    (350, 273, "Shard 13 - Capability Buchhaltung", "Shard 13 muss Buchhaltung unterstützen", "MEDIUM"),
    (351, 273, "Shard 13 - Capability Bilanzen", "Shard 13 muss Bilanzen unterstützen", "MEDIUM"),
    (352, 273, "Shard 13 - Capability Jahresabschlüsse", "Shard 13 muss Jahresabschlüsse unterstützen", "MEDIUM"),

    # Shard 14
    (353, 275, "Shard 14 - Name", "Shard 14 heißt 'Verträge & Vereinbarungen'", "CRITICAL"),
    (354, 276, "Shard 14 - Capability Smart Contracts", "Shard 14 muss Smart Contracts unterstützen", "CRITICAL"),
    (355, 276, "Shard 14 - Capability Geschäftsverträge", "Shard 14 muss Geschäftsverträge unterstützen", "HIGH"),
    (356, 276, "Shard 14 - Capability AGBs", "Shard 14 muss AGBs-Verwaltung unterstützen", "MEDIUM"),
    (357, 277, "Shard 14 - Capability SLAs", "Shard 14 muss SLAs (Service Level Agreements) unterstützen", "HIGH"),
    (358, 277, "Shard 14 - Capability Lieferantenverträge", "Shard 14 muss Lieferantenverträge unterstützen", "MEDIUM"),
    (359, 277, "Shard 14 - Capability Partnerschaften", "Shard 14 muss Partnerschaften-Verwaltung unterstützen", "MEDIUM"),

    # Shard 15
    (360, 279, "Shard 15 - Name", "Shard 15 heißt 'Handel & Transaktionen'", "CRITICAL"),
    (361, 280, "Shard 15 - Capability Käufe", "Shard 15 muss Käufe unterstützen", "HIGH"),
    (362, 280, "Shard 15 - Capability Verkäufe", "Shard 15 muss Verkäufe unterstützen", "HIGH"),
    (363, 280, "Shard 15 - Capability Rechnungen", "Shard 15 muss Rechnungen unterstützen", "HIGH"),
    (364, 280, "Shard 15 - Capability Garantien", "Shard 15 muss Garantien unterstützen", "MEDIUM"),
    (365, 281, "Shard 15 - Capability Supply Chain", "Shard 15 muss Supply Chain unterstützen", "MEDIUM"),
    (366, 281, "Shard 15 - Capability Logistik", "Shard 15 muss Logistik unterstützen", "MEDIUM"),
    (367, 281, "Shard 15 - Capability Lieferscheine", "Shard 15 muss Lieferscheine unterstützen", "MEDIUM"),
    (368, 282, "Shard 15 - Capability Reisen", "Shard 15 muss Reisen-Buchungen unterstützen", "LOW"),
    (369, 282, "Shard 15 - Capability Events", "Shard 15 muss Events unterstützen", "LOW"),
    (370, 282, "Shard 15 - Capability Tickets", "Shard 15 muss Tickets unterstützen", "LOW"),

    # Shard 16
    (371, 284, "Shard 16 - Name", "Shard 16 heißt 'Behörden & Verwaltung'", "CRITICAL"),
    (372, 285, "Shard 16 - Capability Ämter", "Shard 16 muss Ämter-Integration unterstützen", "HIGH"),
    (373, 285, "Shard 16 - Capability Anträge", "Shard 16 muss Anträge unterstützen", "HIGH"),
    (374, 285, "Shard 16 - Capability Genehmigungen", "Shard 16 muss Genehmigungen unterstützen", "HIGH"),
    (375, 285, "Shard 16 - Capability Steuern", "Shard 16 muss Steuern unterstützen", "HIGH"),
    (376, 286, "Shard 16 - Capability Meldewesen", "Shard 16 muss Meldewesen unterstützen", "MEDIUM"),
    (377, 286, "Shard 16 - Capability Gerichtsurteile", "Shard 16 muss Gerichtsurteile unterstützen", "MEDIUM"),
    (378, 286, "Shard 16 - Capability Ordnungswidrigkeiten", "Shard 16 muss Ordnungswidrigkeiten unterstützen", "MEDIUM"),
]

output = []
for regel_id, zeile, kategorie, beschreibung, priority in shards_data:
    enforcement = "SHOULD" if priority == "LOW" else "MUST"
    artefakte = '["Contract", "Core"]' if "Name" in kategorie or "Block" in kategorie else '["Core"]'

    output.append(f'''  - regel_id: "SOT-MD-COMPLETE-{regel_id}"
    zeile: {zeile}
    kategorie: "{kategorie}"
    beschreibung: "{beschreibung}"
    enforcement: "{enforcement}"
    priority: "{priority}"
    betroffene_artefakte: {artefakte}''')

with open("02_audit_logging/reports/SoT_Master_COMPLETE_Manual_Extraction_20251019.yaml", "a", encoding="utf-8") as f:
    f.write("\n" + "\n".join(output) + "\n")

print(f"OK: Shards 07-16 hinzugefuegt (Regeln 288-378, total {len(shards_data)} Regeln)")
