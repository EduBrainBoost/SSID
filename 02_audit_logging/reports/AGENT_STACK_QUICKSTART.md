# SSID Local Agent Stack – Quickstart

**Stack:** Ollama (CPU) + LiteLLM (OpenAI API) + Agent CLI + OPA Policy  
**Ziel:** lokale Agent-Laufzeit mit Zugriff auf Dateien, Shell, Internet – unter Root-24-LOCK & SAFE-FIX

## Start
```bash
cd "C:\Users\bibel\Documents\Github\SSID\04_deployment"
docker compose up -d
ollama pull qwen2.5-coder:7b
```

## Nutzung
```bash
python 12_tooling/agent/agent_cli.py fs-read "C:\Users\bibel\Documents\Github\SSID\16_codex\structure\ssid_master_definition_corrected_v1.1.1.md"
python 12_tooling/agent/agent_cli.py fs-write "C:\Users\bibel\Documents\Github\SSID\02_audit_logging\reports\hello.txt" "hi ssid"
python 12_tooling/agent/agent_cli.py sh "python -V"
python 12_tooling/agent/agent_cli.py http-get "https://docs.python.org/3/"
python 12_tooling/agent/agent_cli.py llm "Erzeuge pytest für validate_all_sot_rules()"
```

## Policies
- OPA Policy: `23_compliance/policies/agent_sandbox.rego` erzwingt Root-24-LOCK & Whitelists.

## CI
```bash
pytest -q
```


## File Hashes (SHA-256)
- `04_deployment/docker-compose.yaml`  
  `600107b2d8736bfb512afd5aa780dc7ec210c82f66d30fe963776b8498296481`
- `16_codex/contracts/agent_tools.yaml`  
  `fa0679db0f13e31c9286fa7ef4676eb5407f87009222a04c2a3fb9d335f81336`
- `23_compliance/policies/agent_sandbox.rego`  
  `3121fdc33f7b8879c06730f190f92ba6a6782c90f4feb174fd8f773cd070a1e7`
- `12_tooling/agent/agent_cli.py`  
  `e9e7edeb2dbc4e676f517324f57c3f19ea11464eb428794913513ee05e29ae19`
- `11_test_simulation/tests_agent/test_agent_tools.py`  
  `48e1c19604b07acf59022d510ae7cc698b7ca27d9c35efaab19a58b946836213`
- `24_meta_orchestration/registry/agent_stack.yaml`  
  `720222d185d6269b2b05cc1f21a93dae61b95bd0c4a57aa85d1807a3570c7387`
- `02_audit_logging/reports/AGENT_STACK_QUICKSTART.md`  
  `8e82a28c5528ec403b5e8b4e68a89879cccdeb9d90f888737ad3d394bb8e0d43`
- `.github/workflows/agent_stack_ci.yaml`  
  `f94bec970dca5cbe3abde29e787bb373cd21a16dfb9b733acbb6faefa6023748`
- `12_tooling/agent/requirements.txt`  
  `7cc4959877dbe6b6c63a8eb1bfe3bfb545fa8fe5b28b1b2c13e4a7c1c0d1c4d4`
- `12_tooling/agent/README.md`  
  `d80440aaab9e81f54f9cf636a199025299bba9c0e4141b718375fabdf1f85631`
- `12_tooling/agent/__init__.py`  
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`