package ssid.minimal_surface

default allow = false

# Input schema (from CI checker):
# { "changed": ["path1","path2",...],
#   "budget": { "allowed_paths": [...], "forbidden_globs": [...], "max_new_files_per_pr": N } }

import future.keywords.if

path_allowed(p) {
  some ap
  ap := input.budget.allowed_paths[_]
  glob.match(ap, [], p)
}

path_forbidden(p) {
  some fg
  fg := input.budget.forbidden_globs[_]
  glob.match(fg, [], p)
}

deny[msg] {
  p := input.changed[_]
  not path_allowed(p)
  msg := sprintf("Path not allowed by budget: %s", [p])
}

deny[msg] {
  p := input.changed[_]
  path_forbidden(p)
  msg := sprintf("Forbidden path pattern matched: %s", [p])
}

deny[msg] {
  input.stats.new_files > input.budget.max_new_files_per_pr
  msg := sprintf("Too many new files: %d > %d", [input.stats.new_files, input.budget.max_new_files_per_pr])
}

allow {
  count(deny) == 0
}
