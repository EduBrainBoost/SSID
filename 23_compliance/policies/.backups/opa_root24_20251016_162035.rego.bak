# OPA Policy-Gate: Root24 Zentralisierungs- und Depth-Check
# Prüft, dass alle Policies nur in 23_compliance liegen und max. Tiefe 2 haben
package root24.compliance

import future.keywords.if
import future.keywords.in

# --- KONFIGURATION ---
compliance_root := "23_compliance"
max_depth := 2
allowed_policy_extensions := {".rego", ".yaml", ".yml", ".json"}

# --- HAUPT-GATE ---
deny[msg] if {
    # Prüfe alle Policy-Dateien im Repository
    policy_file := input.files[_]
    is_policy_file(policy_file.path)
    not is_in_compliance_root(policy_file.path)

    msg := sprintf("❌ POLICY VIOLATION: Policy-Datei '%s' liegt außerhalb von '%s/'", [
        policy_file.path,
        compliance_root
    ])
}

deny[msg] if {
    # Prüfe Tiefe innerhalb 23_compliance
    policy_file := input.files[_]
    is_policy_file(policy_file.path)
    is_in_compliance_root(policy_file.path)
    depth := calculate_depth(policy_file.path)
    depth > max_depth

    msg := sprintf("❌ DEPTH VIOLATION: Policy-Datei '%s' hat Tiefe %d (max: %d)", [
        policy_file.path,
        depth,
        max_depth
    ])
}

# --- HILFSFUNKTIONEN ---

# Prüft, ob Datei eine Policy-Datei ist
is_policy_file(path) if {
    lower_path := lower(path)
    contains(lower_path, "polic")
}

is_policy_file(path) if {
    extension := get_extension(path)
    extension in allowed_policy_extensions
    is_in_compliance_context(path)
}

# Prüft, ob Datei im Compliance-Kontext ist
is_in_compliance_context(path) if {
    lower_path := lower(path)
    contains(lower_path, "compliance")
}

is_in_compliance_context(path) if {
    lower_path := lower(path)
    contains(lower_path, "audit")
}

is_in_compliance_context(path) if {
    lower_path := lower(path)
    contains(lower_path, "regulation")
}

# Prüft, ob Datei im Compliance-Root liegt
is_in_compliance_root(path) if {
    normalized := normalize_path(path)
    startswith(normalized, compliance_root)
}

# Berechnet die Tiefe relativ zum Compliance-Root
calculate_depth(path) := depth if {
    normalized := normalize_path(path)
    relative := trim_prefix(normalized, sprintf("%s/", [compliance_root]))
    parts := split(relative, "/")
    depth := count(parts) - 1  # -1 weil Datei selbst nicht zählt
}

# Normalisiert Pfade (Windows/Unix kompatibel)
normalize_path(path) := normalized if {
    backslash_replaced := replace(path, "\\", "/")
    normalized := trim(backslash_replaced, "/")
}

# Extrahiert Datei-Extension
get_extension(path) := ext if {
    parts := split(path, ".")
    count(parts) > 1
    ext := sprintf(".%s", [parts[count(parts) - 1]])
}

get_extension(path) := "" if {
    parts := split(path, ".")
    count(parts) == 1
}

# --- WARN-REGELN (Soft Checks) ---

warn[msg] if {
    # Warnung bei verdächtigen Dateinamen
    file := input.files[_]
    suspicious_name(file.path)

    msg := sprintf("⚠️  WARNUNG: Verdächtige Datei '%s' könnte Policy-relevante Inhalte enthalten", [
        file.path
    ])
}

suspicious_name(path) if {
    lower_path := lower(path)
    contains(lower_path, "rule")
    not is_in_compliance_root(path)
}

suspicious_name(path) if {
    lower_path := lower(path)
    contains(lower_path, "requirement")
    not is_in_compliance_root(path)
}

# --- ERFOLGS-REGEL ---

allow if {
    count(deny) == 0
}

# --- METADATA ---

metadata := {
    "name": "Root24 Policy Centralization Gate",
    "version": "1.0.0",
    "description": "Stellt sicher, dass alle Policies in 23_compliance/ zentralisiert sind und max. Tiefe 2 haben",
    "compliance_root": compliance_root,
    "max_depth": max_depth,
    "author": "SSID Architecture Team",
    "created": "2025-01-07"
}
