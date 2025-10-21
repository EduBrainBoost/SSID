# PQC CERT SIGNING GUIDE
Signieren:
python 21_post_quantum_crypto/tools/sign_certificate.py --cert 02_audit_logging/reports/test_hygiene_certificate_v1.md --name test_hygiene_cert_v1 --out-json 02_audit_logging/logs/pqc_sign_report.json
Verifizieren:
python 21_post_quantum_crypto/tools/verify_certificate.py --cert 02_audit_logging/reports/test_hygiene_certificate_v1.md --pubkey 21_post_quantum_crypto/keys/test_hygiene_cert.pub --signature 21_post_quantum_crypto/signatures/test_hygiene_cert_v1.sig --json-out 02_audit_logging/logs/pqc_verification_report.json
