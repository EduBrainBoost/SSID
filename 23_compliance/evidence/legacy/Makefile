
.PHONY: validate test scan clean

validate: scan
	@python3 scripts/validators/structure_validator.py
	@opa eval -d 23_compliance/opa/ -i 24_meta_orchestration/registry/generated/repo_scan.json 'data.ssid.structure.depth.allow'

test:
	@pytest 11_test_simulation/ -v --cov

scan:
	@python3 scripts/validators/structure_validator.py

clean:
	@rm -rf 24_meta_orchestration/registry/generated/*.json
	@find . -type d -name __pycache__ -exec rm -rf {} +
