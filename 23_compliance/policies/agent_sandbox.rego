package ssid.agent.sandbox

default allow = false

# INPUT schema:
# {
#   "tool": "fs_read|fs_write|sh|http_get",
#   "args": {...},
#   "context": {"root": "C:\\Users\\bibel\\Documents\\Github\\SSID"}
# }

root := input.context.root

valid_path(p) {
  startswith(lower(p), lower(sprintf("%s", [root])))
}

deny[msg] {
  input.tool == "fs_read"
  not valid_path(input.args.path)
  msg := "fs_read: path outside SSID root"
}

deny[msg] {
  input.tool == "fs_write"
  not valid_path(input.args.path)
  msg := "fs_write: path outside SSID root"
}

deny[msg] {
  input.tool == "sh"
  not allowed_cmd(input.args.cmd)
  msg := sprintf("sh: command not allowed: %s", [input.args.cmd])
}

allowed_cmd(cmd) {
  cmd == "git status"
} else {
  cmd == "pytest -q"
} else {
  cmd == "python -V"
}

deny[msg] {
  input.tool == "http_get"
  not startswith(lower(input.args.url), "https://schemas.openapis.org/")
  not startswith(lower(input.args.url), "https://raw.githubusercontent.com/")
  not startswith(lower(input.args.url), "https://docs.python.org/")
  msg := sprintf("http_get: domain not allowed: %s", [input.args.url])
}

allow {
  count(deny) == 0
}
