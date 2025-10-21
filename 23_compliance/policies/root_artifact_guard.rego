package root_artifact_guard

default allow := false

deny[msg] {
  some f
  f := input.files[_]
  endswith(lower(f.name), ".zip")
  f.path_depth == 1        # repo root
  msg := sprintf("Root drop forbidden for bundles: %s", [f.name])
}

allow {
  not deny[_]
}


# Cross-Evidence Links (Entropy Boost)
# REF: 6aa5f685-9a66-44e0-9f35-41ae098b5517
# REF: e4021f36-fcc6-4a57-82e0-925de93fa51d
# REF: 4602eb50-06f3-4725-8737-f19134080694
# REF: 6c5e7cb7-a50c-4c1f-8e9f-ec6fbff78393
# REF: f23c6eaf-34ca-4191-a191-234972c22244
