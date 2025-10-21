package ssid.sot.implementation_audit

default allow = false

min_lines := {"python":50, "rego":20, "yaml":15, "cli":50, "tests":40}

line_ok[file] {
  some i
  file := input.files[i]
  min := min_lines[file.type]
  file.lines >= min
}

python_ok[file] {
  file.type == "python"
  re_match("(?s).*def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(", file.content)
  not re_match("^\s*(['\"]{3}).*\1\s*$", trim(file.content))
}

rego_ok[file] {
  file.type == "rego"
  re_match("(?m)^package\s+[a-zA-Z0-9_.]+", file.content)
  re_match("(?m)^(allow|deny|violation)\s*=", file.content)
}

yaml_ok[file] {
  file.type == "yaml"
  re_match("(?m)^sot_contract_metadata:", file.content)
  re_match("(?m)^\s*sot_rule_", file.content)
}

cli_ok[file] {
  file.type == "cli"
  re_match("--rule|--all", file.content)
}

tests_ok[file] {
  file.type == "tests"
  re_match("(?m)\bassert\b", file.content)
}

file_ok[file] {
  line_ok[file]
  file.type == "python"
  python_ok[file]
} else = true {
  line_ok[file]
  file.type == "rego"
  rego_ok[file]
} else = true {
  line_ok[file]
  file.type == "yaml"
  yaml_ok[file]
} else = true {
  line_ok[file]
  file.type == "cli"
  cli_ok[file]
} else = true {
  line_ok[file]
  file.type == "tests"
  tests_ok[file]
}

allow {
  count({f | file_ok[f]}) == count(input.files)
}
