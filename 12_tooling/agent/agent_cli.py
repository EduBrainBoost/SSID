import argparse, json, subprocess, hashlib, sys, requests
from pathlib import Path

# ---------------------------------------------------------------------
# SSID Local Agent CLI  v1.1  (Standalone + Auto-Switch)
# ---------------------------------------------------------------------
#  - prüft OPA-Policies (Root-24-LOCK enforced)
#  - kann Dateien lesen/schreiben, Shell-Kommandos ausführen, HTTP-GET
#  - nutzt automatisch LiteLLM (Port 4000) oder direkt Ollama (Port 11434)
# ---------------------------------------------------------------------

SSID_ROOT = Path(r"C:\Users\bibel\Documents\Github\SSID")
POLICY = SSID_ROOT / r"23_compliance\policies\agent_sandbox.rego"
OPA_BIN = "opa"  # OPA muss im PATH liegen


# ---------------------------------------------------------------------
# Utility-Funktionen
# ---------------------------------------------------------------------
def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def opa_allow(payload: dict) -> None:
    """Überprüft die Policy-Freigabe vor jeder Aktion"""
    q = "data.ssid.agent.sandbox"
    r = subprocess.run(
        [OPA_BIN, "eval", "-I", "-d", str(POLICY), q],
        input=json.dumps({"input": payload}),
        text=True,
        capture_output=True,
    )
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(2)

    try:
        out = json.loads(r.stdout)
        val = out["result"][0]["expressions"][0]["value"]
        allow = val["allow"]
        if not allow:
            denies = val.get("deny", [])
            msg = "; ".join(denies) if denies else "denied"
            print(f"POLICY DENY: {msg}", file=sys.stderr)
            sys.exit(3)
    except Exception as e:
        print(f"OPA parse error: {e}\nRaw: {r.stdout}", file=sys.stderr)
        sys.exit(2)


# ---------------------------------------------------------------------
# Werkzeuge
# ---------------------------------------------------------------------
def fs_read(path: str):
    p = Path(path)
    payload = {
        "tool": "fs_read",
        "args": {"path": str(p)},
        "context": {"root": str(SSID_ROOT)},
    }
    opa_allow(payload)
    txt = p.read_text(encoding="utf-8", errors="ignore")
    return {"text": txt, "sha256": sha256_bytes(txt.encode("utf-8"))}


def fs_write(path: str, text: str):
    p = Path(path)
    payload = {
        "tool": "fs_write",
        "args": {"path": str(p)},
        "context": {"root": str(SSID_ROOT)},
    }
    opa_allow(payload)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return {"sha256": sha256_file(p)}


def sh(cmd: str):
    payload = {
        "tool": "sh",
        "args": {"cmd": cmd},
        "context": {"root": str(SSID_ROOT)},
    }
    opa_allow(payload)
    r = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, cwd=str(SSID_ROOT)
    )
    return {"stdout": r.stdout, "stderr": r.stderr, "exit_code": r.returncode}


def http_get(url: str):
    payload = {
        "tool": "http_get",
        "args": {"url": url},
        "context": {"root": str(SSID_ROOT)},
    }
    opa_allow(payload)
    resp = requests.get(url, timeout=10)
    return {"status": resp.status_code, "text": resp.text[:200000]}


# ---------------------------------------------------------------------
# LLM-Interface  (Auto-Switch: LiteLLM → Ollama)
# ---------------------------------------------------------------------
def llm_chat(prompt: str, model="qwen2.5-coder:7b"):
    """
    Fallback-Logik:
      1. Wenn LiteLLM (Port 4000) läuft → benutze ihn.
      2. Wenn nicht → direkt Ollama-CLI (Port 11434).
    """
    import subprocess, requests, json

    try:
        # Test: antwortet LiteLLM?
        requests.get("http://localhost:4000/v1/models", timeout=1)
        backend = "litellm"
    except Exception:
        backend = "ollama"

    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are SSID Local Agent."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 1024,
    }

    if backend == "litellm":
        r = requests.post(
            "http://localhost:4000/v1/chat/completions", json=data, timeout=120
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    # --- direkter Ollama-Fallback ---
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )
    return result.stdout.strip()


# ---------------------------------------------------------------------
# CLI-Dispatcher
# ---------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(prog="ssid-agent")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s1 = sub.add_parser("fs-read")
    s1.add_argument("path")

    s2 = sub.add_parser("fs-write")
    s2.add_argument("path")
    s2.add_argument("text")

    s3 = sub.add_parser("sh")
    s3.add_argument("cmd")

    s4 = sub.add_parser("http-get")
    s4.add_argument("url")

    s5 = sub.add_parser("llm")
    s5.add_argument("prompt")

    args = ap.parse_args()

    if args.cmd == "fs-read":
        print(json.dumps(fs_read(args.path), indent=2))
    elif args.cmd == "fs-write":
        print(json.dumps(fs_write(args.path, args.text), indent=2))
    elif args.cmd == "sh":
        print(json.dumps(sh(args.cmd), indent=2))
    elif args.cmd == "http-get":
        print(json.dumps(http_get(args.url), indent=2))
    elif args.cmd == "llm":
        print(llm_chat(args.prompt))


if __name__ == "__main__":
    main()