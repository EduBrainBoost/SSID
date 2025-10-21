# YAML Markers Policy
# SOT-018, SOT-019

package ssid.sot.yaml_markers

import rego.v1

# SOT-018: YAML Block Marker
deny contains msg if {
    not input.yaml_block_marker
    msg := "[SOT-018] Missing 'yaml_block_marker' field"
}

deny contains msg if {
    input.yaml_block_marker
    input.yaml_block_marker != "```yaml"
    msg := sprintf("[SOT-018] Invalid YAML block marker: '%v' (expected '```yaml')", [input.yaml_block_marker])
}

# SOT-019: YAML Comment Line
deny contains msg if {
    not input.yaml_comment_line
    msg := "[SOT-019] Missing 'yaml_comment_line' field"
}

deny contains msg if {
    input.yaml_comment_line
    not startswith(input.yaml_comment_line, "#")
    msg := sprintf("[SOT-019] Comment must start with '#': '%v'", [input.yaml_comment_line])
}

deny contains msg if {
    input.yaml_comment_line
    startswith(input.yaml_comment_line, "#")
    comment_path := trim_space(substring(input.yaml_comment_line, 1, -1))
    not contains(comment_path, "/")
    msg := sprintf("[SOT-019] Comment must contain file path with '/': '%v'", [comment_path])
}

deny contains msg if {
    input.yaml_comment_line
    startswith(input.yaml_comment_line, "#")
    comment_path := trim_space(substring(input.yaml_comment_line, 1, -1))
    not endswith(comment_path, ".yaml")
    not endswith(comment_path, ".yml")
    msg := sprintf("[SOT-019] Path must end with .yaml or .yml: '%v'", [comment_path])
}

deny contains msg if {
    input.yaml_comment_line
    startswith(input.yaml_comment_line, "#")
    comment_path := trim_space(substring(input.yaml_comment_line, 1, -1))
    not startswith(comment_path, "23_compliance/")
    msg := sprintf("[SOT-019] Path should start with '23_compliance/': '%v'", [comment_path])
}
