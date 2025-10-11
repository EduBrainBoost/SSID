package ssid.structure.depth
import future.keywords.if

has_substr(haystack, needle) := true if { contains(haystack, needle) }

string_similarity(a, b) := similarity {
    a_lower := lower(a)
    b_lower := lower(b)
    a_tokens := split(a_lower, " ")
    b_tokens := split(b_lower, " ")
    a_set := {x | some x in a_tokens}
    b_set := {x | some x in b_tokens}
    intersection := count(a_set & b_set)
    union := count(a_set | b_set)
    similarity := union > 0 ? intersection / union : 0
}

max_depth := 3
default allow := false

allow if {
    input.summary.invalid_shards == 0
    count(input.forbidden_files) == 0
    all_shards_within_depth
}

all_shards_within_depth if {
    every root in input.roots {
        every shard in root.shards {
            shard_depth_ok(shard)
        }
    }
}

shard_depth_ok(shard) if {
    path := shard.path
    has_substr(path, "/shards/")
    parts := split(path, "/shards/")
    depth := count(split(parts[1], "/")) - 1
    depth <= max_depth
}

violations[msg] {
    some root in input.roots
    some shard in root.shards
    not shard_depth_ok(shard)
    msg := sprintf("Shard %s exceeds max depth %d", [shard.shard_id, max_depth])
}

violations[msg] {
    count(input.forbidden_files) > 0
    msg := sprintf("Found %d forbidden files (.ipynb, .parquet, .sqlite, .db)", [count(input.forbidden_files)])
}
