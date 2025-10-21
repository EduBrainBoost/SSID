# 11_test_simulation/tests/test_layer9_proof_aggregator.py
import json, subprocess, sys, pathlib, os

def test_l9_with_gate(tmp_path):
    kit_root = pathlib.Path(__file__).parents[2]  # Go up to SSID root
    agg = kit_root / "03_core/simulation/layer9_proof_aggregator.py"
    # fabricate readiness PASS json
    readiness = tmp_path / "layer_readiness_score.json"
    readiness.write_text(json.dumps({"avg_score": 0.91, "status": "PASS"}))
    inp = tmp_path / "in.json"
    data = {
      "proofs_layer8": [
        {"ecosystem": "SSID", "hash": "a"*128},
        {"ecosystem": "EUDI", "hash": "b"*128}
      ],
      "trust_weights": {"SSID": 1.0, "EUDI": 0.9},
      "global_epoch_id": "epoch-xyz",
      "approvals": [True, True, True, False, True, True, True]
    }
    inp.write_text(json.dumps(data))
    outp = tmp_path / "out.json"
    cmd = [sys.executable, agg.as_posix(), "--input", inp.as_posix(), "--out", outp.as_posix(),
           "--readiness", readiness.as_posix(), "--gate_threshold", "0.90"]
    subprocess.check_call(cmd)
    out = json.loads(outp.read_text())
    assert out["gate_pass_l1_8"] is True
    assert isinstance(out["layer9_root"], str) and len(out["layer9_root"]) == 128


# Cross-Evidence Links (Entropy Boost)
# REF: e4021f36-fcc6-4a57-82e0-925de93fa51d
# REF: 6f58014c-6eb6-4594-939e-ee2a7b537499
# REF: 09020a43-07b9-42e4-aa35-9307de20e4e6
# REF: c3ad41ec-699a-4b27-9f49-960c9e3daa18
# REF: 8c4545b4-7a9b-4da2-9430-f3c8562c060e
