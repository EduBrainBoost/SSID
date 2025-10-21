# Entry Markers Policy
# SOT-021, SOT-026, SOT-032, SOT-038, SOT-044, SOT-049, SOT-054

package ssid.sot.entry_markers

import rego.v1

# SOT-021: ivms101_2023 Entry
deny contains msg if {
    not input.entry_marker_ivms101_2023
    msg := "[SOT-021] Missing 'entry_marker_ivms101_2023' field"
}

deny contains msg if {
    input.entry_marker_ivms101_2023
    input.entry_marker_ivms101_2023 != "ivms101_2023/:"
    msg := sprintf("[SOT-021] Invalid entry marker: '%v' (expected 'ivms101_2023/:')", [input.entry_marker_ivms101_2023])
}

# SOT-026: fatf_rec16_2025_update Entry
deny contains msg if {
    not input.entry_marker_fatf_rec16_2025
    msg := "[SOT-026] Missing 'entry_marker_fatf_rec16_2025' field"
}

deny contains msg if {
    input.entry_marker_fatf_rec16_2025
    input.entry_marker_fatf_rec16_2025 != "fatf_rec16_2025_update/:"
    msg := sprintf("[SOT-026] Invalid entry marker: '%v' (expected 'fatf_rec16_2025_update/:')", [input.entry_marker_fatf_rec16_2025])
}

# SOT-032: xml_schema_2025_07 Entry
deny contains msg if {
    not input.entry_marker_xml_schema_2025_07
    msg := "[SOT-032] Missing 'entry_marker_xml_schema_2025_07' field"
}

deny contains msg if {
    input.entry_marker_xml_schema_2025_07
    input.entry_marker_xml_schema_2025_07 != "xml_schema_2025_07/:"
    msg := sprintf("[SOT-032] Invalid entry marker: '%v' (expected 'xml_schema_2025_07/:')", [input.entry_marker_xml_schema_2025_07])
}

# SOT-038: iso24165_dti Entry
deny contains msg if {
    not input.entry_marker_iso24165_dti
    msg := "[SOT-038] Missing 'entry_marker_iso24165_dti' field"
}

deny contains msg if {
    input.entry_marker_iso24165_dti
    input.entry_marker_iso24165_dti != "iso24165_dti/:"
    msg := sprintf("[SOT-038] Invalid entry marker: '%v' (expected 'iso24165_dti/:')", [input.entry_marker_iso24165_dti])
}

# SOT-044: fsb_stablecoins_2023 Entry
deny contains msg if {
    not input.entry_marker_fsb_stablecoins_2023
    msg := "[SOT-044] Missing 'entry_marker_fsb_stablecoins_2023' field"
}

deny contains msg if {
    input.entry_marker_fsb_stablecoins_2023
    input.entry_marker_fsb_stablecoins_2023 != "fsb_stablecoins_2023/:"
    msg := sprintf("[SOT-044] Invalid entry marker: '%v' (expected 'fsb_stablecoins_2023/:')", [input.entry_marker_fsb_stablecoins_2023])
}

# SOT-049: iosco_crypto_markets_2023 Entry
deny contains msg if {
    not input.entry_marker_iosco_crypto_markets_2023
    msg := "[SOT-049] Missing 'entry_marker_iosco_crypto_markets_2023' field"
}

deny contains msg if {
    input.entry_marker_iosco_crypto_markets_2023
    input.entry_marker_iosco_crypto_markets_2023 != "iosco_crypto_markets_2023/:"
    msg := sprintf("[SOT-049] Invalid entry marker: '%v' (expected 'iosco_crypto_markets_2023/:')", [input.entry_marker_iosco_crypto_markets_2023])
}

# SOT-054: nist_ai_rmf_1_0 Entry
deny contains msg if {
    not input.entry_marker_nist_ai_rmf_1_0
    msg := "[SOT-054] Missing 'entry_marker_nist_ai_rmf_1_0' field"
}

deny contains msg if {
    input.entry_marker_nist_ai_rmf_1_0
    input.entry_marker_nist_ai_rmf_1_0 != "nist_ai_rmf_1_0/:"
    msg := sprintf("[SOT-054] Invalid entry marker: '%v' (expected 'nist_ai_rmf_1_0/:')", [input.entry_marker_nist_ai_rmf_1_0])
}
