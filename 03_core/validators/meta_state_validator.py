
import json, sys

REQUIRED_KEYS = {"timestamp","boot_duration_s","artifacts","issues","pipelines","global_score"}

def validate_meta_state(path):
    data = json.loads(open(path, "r", encoding="utf-8").read())
    assert REQUIRED_KEYS.issubset(data.keys())
    assert isinstance(data["artifacts"], list)
    assert isinstance(data["pipelines"], dict)
    assert isinstance(data["global_score"], int)
    return True

if __name__ == "__main__":
    ok = validate_meta_state(sys.argv[1])
    print("OK" if ok else "FAIL")
