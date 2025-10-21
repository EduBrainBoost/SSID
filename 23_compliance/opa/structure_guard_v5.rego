package ssid.v5.structure

default allow := false

# Zulässige 24 Roots (Ordner)
allowed_roots := {
  "01_ai_layer","02_audit_logging","03_core","04_deployment","05_documentation","06_data_pipeline",
  "07_governance_legal","08_identity_score","09_meta_identity","10_interoperability","11_test_simulation",
  "12_tooling","13_ui_layer","14_zero_time_auth","15_infra","16_codex","17_observability","18_data_layer",
  "19_adapters","20_foundation","21_post_quantum_crypto","22_datasets","23_compliance","24_meta_orchestration"
}

# 1) Keine neuen Root-Ordner
deny[msg] {
  input.mutation.action == "create_dir"
  not allowed_roots[input.mutation.path.root]
  msg := sprintf("ROOT-24-LOCK violation: '%s' not allowed", [input.mutation.path.root])
}

# 2) SAFE-FIX: Schreiben nur unter SSID-Basis
deny[msg] {
  input.mutation.action == "write_file"
  not startswith(input.mutation.path.full, "C:/Users/bibel/Documents/Github/SSID/")
  msg := "SAFE-FIX violation: write outside SSID path"
}

# 3) NEU: Root-Level-Dateien (Tiefe=0) verbieten — strikte Deny
root_whitelist := {".gitignore",".gitattributes","LICENSE","README.md","pytest.ini",".gitmodules"}
deny[msg] {
  input.mutation.action == "write_file"
  input.mutation.path.depth == 0
  not root_whitelist[input.mutation.path.name]
  msg := sprintf("ROOT-24-LOCK violation: file at repository root '%s' forbidden", [input.mutation.path.name])
}

# 4) NEU: Archiv-Endungen am Root-Level explizit blockieren
deny[msg] {
  input.mutation.action == "write_file"
  input.mutation.path.depth == 0
  endswith(lower(input.mutation.path.name), ".zip")
  msg := sprintf("ROOT-24-LOCK violation: archives at root forbidden ('%s')", [input.mutation.path.name])
}
deny[msg] {
  input.mutation.action == "write_file"
  input.mutation.path.depth == 0
  endswith(lower(input.mutation.path.name), ".tar.gz")
  msg := sprintf("ROOT-24-LOCK violation: archives at root forbidden ('%s')", [input.mutation.path.name])
}

# PASS wenn kein Deny greift
allow { not deny[_] }
