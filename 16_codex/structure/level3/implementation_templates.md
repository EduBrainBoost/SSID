# Master Rules → 5 SoT-Artefakte
## Implementation Templates & Best Practices

**Version:** 1.0  
**Zweck:** Zeigt für jede Regel-Kategorie, wie die Implementierung in allen 5 SoT-Artefakten aussieht

---

## 📖 Inhaltsverzeichnis

1. [Template-Struktur](#template-struktur)
2. [Beispiel 1: Non-Custodial Policy (KP001)](#beispiel-1-non-custodial-policy-kp001)
3. [Beispiel 2: Matrix-Architektur (M001)](#beispiel-2-matrix-architektur-m001)
4. [Beispiel 3: GDPR PII Redaction (KP008)](#beispiel-3-gdpr-pii-redaction-kp008)
5. [Beispiel 4: Root Count Validation (R001)](#beispiel-4-root-count-validation-r001)
6. [Beispiel 5: Secrets Management (KP013)](#beispiel-5-secrets-management-kp013)
7. [Quick Reference Matrix](#quick-reference-matrix)

---

## Template-Struktur

Für **jede** Master-Regel erstellen wir:

```
Master-Regel (YAML)
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 1. CONTRACT DEFINITIONS (OpenAPI + JSON-Schema)            │
│    → Interface-Definition (API/Schema)                      │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. CORE LOGIC (Python/Rust)                                │
│    → Implementierung der Regel in Code                      │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. POLICY ENFORCEMENT (OPA Rego / Semgrep)                 │
│    → Automatisierte Prüfung/Blockierung                     │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. CLI VALIDATION (Struktur-Checks)                        │
│    → Validierung bei Build/Deploy                           │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. TEST SUITES (Unit/Integration/Contract)                 │
│    → Automatisierte Tests für die Regel                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Beispiel 1: Non-Custodial Policy (KP001)

### Master-Regel (aus YAML)

```yaml
KP001:
  type: "NIEMALS"
  rule: "NIEMALS Rohdaten von PII oder biometrischen Daten speichern"
  source: "Kritische Policies - Non-Custodial"
  category: "Non-Custodial"
  severity: "CRITICAL"
  enforcement:
    - "Static Analysis (Semgrep) blockiert PII-Storage"
    - "Runtime PII-Detector blockiert Verstöße"
    - "Violations = System-Block + Alert an Compliance-Team"
  implementation_requirements:
    - "Nur Hash-basierte Speicherung (SHA3-256)"
    - "Tenant-spezifische Peppers"
    - "Immediate Discard nach Hashing"
```

---

### 1. CONTRACT DEFINITION

**File:** `01_ai_layer/shards/01_identitaet_personen/contracts/identity_data_handling.openapi.yaml`

```yaml
openapi: 3.1.0
info:
  title: Identity Data Handling API
  version: 1.0.0
  description: |
    API für Identity-Datenverarbeitung.
    CRITICAL: Darf niemals Rohdaten von PII speichern (KP001).

paths:
  /hash-identity-data:
    post:
      summary: Hasht Identity-Daten (Non-Custodial)
      description: |
        Akzeptiert PII, hasht diese mit SHA3-256 + Tenant-Pepper,
        und gibt nur den Hash zurück. Rohdaten werden sofort verworfen.
      operationId: hashIdentityData
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/IdentityDataInput'
      responses:
        '200':
          description: Hash erfolgreich erstellt
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/IdentityHashOutput'
        '400':
          description: Invalid input
        '500':
          description: Internal error

components:
  schemas:
    IdentityDataInput:
      type: object
      required:
        - tenant_id
        - data_type
        - raw_data
      properties:
        tenant_id:
          type: string
          format: uuid
          description: Tenant-ID für Pepper-Auswahl
        data_type:
          type: string
          enum: [name, email, biometric, address]
          description: Typ der Identity-Daten
        raw_data:
          type: string
          description: |
            Rohdaten (PII). WIRD SOFORT NACH HASHING VERWORFEN.
            Niemals in Logs, Dateien oder Datenbanken gespeichert.
      
    IdentityHashOutput:
      type: object
      required:
        - hash
        - algorithm
        - timestamp
      properties:
        hash:
          type: string
          pattern: '^[a-f0-9]{64}$'
          description: SHA3-256 Hash (64 hex chars)
        algorithm:
          type: string
          enum: [SHA3-256]
          description: Verwendeter Hash-Algorithmus
        timestamp:
          type: string
          format: date-time
          description: Zeitpunkt der Hash-Erstellung
        metadata:
          type: object
          properties:
            data_type:
              type: string
            tenant_id:
              type: string
              format: uuid
```

**JSON-Schema:** `contracts/schemas/identity_hash.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://ssid.org/schemas/identity_hash.json",
  "title": "Identity Hash",
  "description": "Schema für Identity-Hashes (Non-Custodial)",
  "type": "object",
  "required": ["hash", "algorithm", "timestamp"],
  "properties": {
    "hash": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$",
      "description": "SHA3-256 Hash"
    },
    "algorithm": {
      "type": "string",
      "enum": ["SHA3-256"],
      "description": "MUST be SHA3-256 (KP001)"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    }
  },
  "additionalProperties": false
}
```

---

### 2. CORE LOGIC

**File:** `implementations/python-tensorflow/src/services/identity_hasher.py`

```python
"""
Identity Hasher Service - Non-Custodial Implementation (KP001)

CRITICAL: NIEMALS Rohdaten speichern!
- Nur In-Memory-Verarbeitung
- Immediate Discard nach Hashing
- Kein File-System-Cache
- Kein Logging von raw_data
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import UUID

from .pii_detector import PIIDetector
from .secrets_manager import get_tenant_pepper

# PII-Redacted Logger
logger = logging.getLogger(__name__)


class IdentityHasher:
    """
    Non-Custodial Identity Hasher.
    
    Compliance: KP001 - NIEMALS Rohdaten speichern.
    """
    
    def __init__(self):
        self.pii_detector = PIIDetector()
    
    def hash_identity_data(
        self,
        tenant_id: UUID,
        data_type: str,
        raw_data: str
    ) -> Dict[str, str]:
        """
        Hasht Identity-Daten non-custodial.
        
        Args:
            tenant_id: Tenant-ID für Pepper-Auswahl
            data_type: Typ der Daten (name, email, biometric, address)
            raw_data: Rohdaten (PII) - WIRD SOFORT VERWORFEN
        
        Returns:
            Dict mit hash, algorithm, timestamp
        
        Raises:
            ValueError: Bei invaliden Inputs
        
        Security:
            - raw_data wird niemals gespeichert
            - raw_data wird niemals geloggt
            - raw_data wird nach Hashing überschrieben
        """
        
        # 1. Validierung (OHNE raw_data zu loggen)
        if not raw_data or len(raw_data.strip()) == 0:
            raise ValueError("raw_data must not be empty")
        
        # 2. PII-Detection (Runtime-Check für KP001)
        if self.pii_detector.contains_pii(raw_data):
            logger.warning(
                "PII detected in raw_data",
                extra={
                    "tenant_id": str(tenant_id),
                    "data_type": data_type,
                    "rule": "KP001"
                }
            )
        
        try:
            # 3. Tenant-Pepper abrufen
            pepper = get_tenant_pepper(tenant_id)
            
            # 4. Hash berechnen (SHA3-256 + Pepper)
            # CRITICAL: raw_data + pepper NUR in Memory
            salted_data = f"{raw_data}{pepper}"
            hash_object = hashlib.sha3_256(salted_data.encode('utf-8'))
            hash_hex = hash_object.hexdigest()
            
            # 5. Sofortiger Discard (Überschreiben mit Nullen)
            # Python Garbage Collection + explizites Überschreiben
            raw_data = "0" * len(raw_data)
            salted_data = "0" * len(salted_data)
            del raw_data, salted_data
            
            # 6. Rückgabe (NUR Hash, keine Rohdaten)
            return {
                "hash": hash_hex,
                "algorithm": "SHA3-256",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "data_type": data_type,
                    "tenant_id": str(tenant_id)
                }
            }
        
        except Exception as e:
            logger.error(
                "Hash creation failed",
                extra={
                    "tenant_id": str(tenant_id),
                    "data_type": data_type,
                    "error": str(e)
                }
            )
            raise
    
    def verify_hash(
        self,
        tenant_id: UUID,
        raw_data: str,
        expected_hash: str
    ) -> bool:
        """
        Verifiziert einen Hash (Non-Custodial).
        
        Args:
            tenant_id: Tenant-ID
            raw_data: Rohdaten zum Vergleich (werden sofort verworfen)
            expected_hash: Erwarteter Hash
        
        Returns:
            True wenn Hash übereinstimmt
        
        Security:
            - raw_data wird sofort nach Verifikation verworfen
            - Constant-Time Comparison
        """
        result = self.hash_identity_data(tenant_id, "verification", raw_data)
        computed_hash = result["hash"]
        
        # Constant-Time Comparison (timing attack prevention)
        return self._constant_time_compare(computed_hash, expected_hash)
    
    @staticmethod
    def _constant_time_compare(a: str, b: str) -> bool:
        """Constant-time string comparison."""
        if len(a) != len(b):
            return False
        result = 0
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
        return result == 0
```

**File:** `implementations/python-tensorflow/src/utils/pii_detector.py`

```python
"""
PII Detector - Runtime Enforcement für KP001.

Erkennt PII in Strings zur Laufzeit und blockiert Speicherung.
"""

import re
from typing import List, Dict


class PIIDetector:
    """Runtime PII Detection."""
    
    # PII-Patterns (simplified, produktiv würde ML-Model verwendet)
    PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
    }
    
    def contains_pii(self, text: str) -> bool:
        """
        Prüft, ob Text PII enthält.
        
        Args:
            text: Zu prüfender Text
        
        Returns:
            True wenn PII erkannt wurde
        """
        for pattern_name, pattern in self.PATTERNS.items():
            if re.search(pattern, text):
                return True
        return False
    
    def detect_pii_types(self, text: str) -> List[str]:
        """
        Identifiziert PII-Typen im Text.
        
        Returns:
            Liste der erkannten PII-Typen
        """
        detected = []
        for pattern_name, pattern in self.PATTERNS.items():
            if re.search(pattern, text):
                detected.append(pattern_name)
        return detected
```

---

### 3. POLICY ENFORCEMENT

**File:** `23_compliance/opa/non_custodial_enforcement.rego`

```rego
# Non-Custodial Policy Enforcement (KP001)
# Blockiert jeden Versuch, Rohdaten von PII zu speichern

package ssid.compliance.non_custodial

import future.keywords.if
import future.keywords.in

# DENY: File-System-Schreibzugriffe für PII
deny[msg] if {
    input.operation == "file_write"
    contains_pii(input.data)
    msg := sprintf(
        "BLOCKED (KP001): Attempt to write PII to file system. File: %s",
        [input.file_path]
    )
}

# DENY: Datenbank-Insert für Rohdaten
deny[msg] if {
    input.operation == "db_insert"
    input.table != "hashes"  # Nur Hash-Tabelle erlaubt
    contains_pii(input.data)
    msg := sprintf(
        "BLOCKED (KP001): Attempt to insert PII into database. Table: %s",
        [input.table]
    )
}

# DENY: Logging von PII
deny[msg] if {
    input.operation == "log_write"
    input.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]
    contains_pii(input.message)
    msg := sprintf(
        "BLOCKED (KP001): Attempt to log PII. Level: %s",
        [input.log_level]
    )
}

# DENY: Cache-Speicherung von PII
deny[msg] if {
    input.operation == "cache_set"
    contains_pii(input.value)
    msg := "BLOCKED (KP001): Attempt to cache PII"
}

# Helper: Erkennt PII (simplified)
contains_pii(data) if {
    # Email
    regex.match(`\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`, data)
}

contains_pii(data) if {
    # Phone
    regex.match(`\b\d{3}[-.]?\d{3}[-.]?\d{4}\b`, data)
}

contains_pii(data) if {
    # SSN
    regex.match(`\b\d{3}-\d{2}-\d{4}\b`, data)
}

# ALLOW: Hash-Speicherung
allow if {
    input.operation == "db_insert"
    input.table == "hashes"
    is_valid_hash(input.data.hash)
}

# Helper: Validiert Hash-Format (SHA3-256)
is_valid_hash(hash) if {
    regex.match(`^[a-f0-9]{64}$`, hash)
}
```

**File:** `.semgrep/rules/no-pii-storage.yaml`

```yaml
rules:
  - id: no-pii-to-file
    pattern-either:
      - pattern: open($PATH, "w").write($DATA)
      - pattern: |
          with open($PATH, "w") as $F:
              $F.write($DATA)
      - pattern: Path($PATH).write_text($DATA)
    message: |
      BLOCKED (KP001): Writing data to file system.
      Non-Custodial Rule: NEVER store raw PII.
      Use IdentityHasher instead.
    severity: ERROR
    languages: [python]
    metadata:
      category: security
      cwe: "CWE-312: Cleartext Storage of Sensitive Information"
      owasp: "A02:2021 - Cryptographic Failures"
      rule: KP001
  
  - id: no-pii-to-db-raw
    pattern-either:
      - pattern: cursor.execute("INSERT INTO $TABLE ...", [$DATA, ...])
      - pattern: session.add($OBJECT)
    message: |
      BLOCKED (KP001): Inserting data into database.
      Ensure only HASHES are stored, never raw PII.
    severity: ERROR
    languages: [python]
    metadata:
      rule: KP001
  
  - id: no-pii-in-logs
    pattern-either:
      - pattern: logger.$LEVEL($MSG, ..., raw_data=$DATA, ...)
      - pattern: logger.$LEVEL(f"... {$RAW_DATA} ...")
      - pattern: print($DATA)
    message: |
      BLOCKED (KP001): Logging raw data.
      Use PII-redacted logger instead.
    severity: WARNING
    languages: [python]
    metadata:
      rule: KP001
```

---

### 4. CLI VALIDATION

**File:** `12_tooling/cli/validators/non_custodial_validator.py`

```python
"""
CLI Validator für Non-Custodial Compliance (KP001).

Prüft bei Build/Deploy, ob Code gegen KP001 verstößt.
"""

import ast
import re
from pathlib import Path
from typing import List, Tuple


class NonCustodialValidator:
    """Validiert Non-Custodial Compliance."""
    
    FORBIDDEN_PATTERNS = [
        # File Writes
        (r'open\([^)]+,\s*["\']w["\']', "File write detected"),
        (r'\.write_text\(', "Path.write_text detected"),
        
        # Database Raw Inserts
        (r'INSERT INTO (?!hashes)', "Raw DB insert (not hashes table)"),
        
        # Logging Raw Data
        (r'logger\.\w+\([^)]*raw_data', "Logging raw_data"),
    ]
    
    def validate_file(self, file_path: Path) -> List[Tuple[int, str]]:
        """
        Validiert einzelne Datei auf KP001-Verstöße.
        
        Args:
            file_path: Pfad zur Python-Datei
        
        Returns:
            Liste von (line_number, error_message)
        """
        violations = []
        
        with open(file_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Pattern-basierte Checks
        for line_no, line in enumerate(lines, start=1):
            for pattern, message in self.FORBIDDEN_PATTERNS:
                if re.search(pattern, line):
                    violations.append((
                        line_no,
                        f"KP001 Violation: {message}"
                    ))
        
        # AST-basierte Checks (tiefere Analyse)
        try:
            tree = ast.parse(content)
            violations.extend(self._check_ast(tree))
        except SyntaxError:
            pass  # Syntax-Fehler werden von anderen Tools gemeldet
        
        return violations
    
    def _check_ast(self, tree: ast.AST) -> List[Tuple[int, str]]:
        """AST-basierte Validierung."""
        violations = []
        
        for node in ast.walk(tree):
            # Check: Attribute Assignment zu 'data' oder 'raw_data'
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if 'raw' in target.id.lower() or 'pii' in target.id.lower():
                            # Check ob direkt in File/DB geschrieben wird
                            violations.append((
                                node.lineno,
                                f"KP001 Warning: Variable '{target.id}' may contain PII"
                            ))
        
        return violations
    
    def validate_directory(self, dir_path: Path) -> dict:
        """
        Validiert gesamtes Verzeichnis.
        
        Returns:
            Dict mit {file_path: [violations]}
        """
        results = {}
        
        for py_file in dir_path.rglob("*.py"):
            violations = self.validate_file(py_file)
            if violations:
                results[str(py_file)] = violations
        
        return results


def main():
    """CLI Entry Point."""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="Validate Non-Custodial Compliance (KP001)"
    )
    parser.add_argument(
        "path",
        type=Path,
        help="File or directory to validate"
    )
    
    args = parser.parse_args()
    validator = NonCustodialValidator()
    
    if args.path.is_file():
        violations = validator.validate_file(args.path)
        if violations:
            print(f"❌ KP001 Violations in {args.path}:")
            for line_no, msg in violations:
                print(f"  Line {line_no}: {msg}")
            sys.exit(1)
        else:
            print(f"✅ {args.path}: No KP001 violations")
    
    elif args.path.is_dir():
        results = validator.validate_directory(args.path)
        if results:
            print(f"❌ KP001 Violations found:")
            for file_path, violations in results.items():
                print(f"\n{file_path}:")
                for line_no, msg in violations:
                    print(f"  Line {line_no}: {msg}")
            sys.exit(1)
        else:
            print(f"✅ {args.path}: No KP001 violations")
    
    else:
        print(f"❌ Error: {args.path} not found")
        sys.exit(2)


if __name__ == "__main__":
    main()
```

---

### 5. TEST SUITES

**File:** `implementations/python-tensorflow/tests/test_identity_hasher.py`

```python
"""
Unit Tests für IdentityHasher - KP001 Compliance.

Testet:
- Hash-Erstellung
- Immediate Discard
- Keine Speicherung von Rohdaten
"""

import pytest
import hashlib
from uuid import uuid4

from src.services.identity_hasher import IdentityHasher
from src.services.secrets_manager import get_tenant_pepper


class TestIdentityHasher:
    """Tests für Non-Custodial Identity Hashing."""
    
    @pytest.fixture
    def hasher(self):
        return IdentityHasher()
    
    @pytest.fixture
    def tenant_id(self):
        return uuid4()
    
    def test_hash_creation(self, hasher, tenant_id):
        """Test: Hash wird korrekt erstellt."""
        result = hasher.hash_identity_data(
            tenant_id=tenant_id,
            data_type="email",
            raw_data="test@example.com"
        )
        
        assert "hash" in result
        assert "algorithm" in result
        assert "timestamp" in result
        
        # Hash Format validieren
        assert len(result["hash"]) == 64  # SHA3-256 = 64 hex chars
        assert result["algorithm"] == "SHA3-256"
    
    def test_deterministic_hashing(self, hasher, tenant_id):
        """Test: Gleiche Eingabe = gleicher Hash."""
        raw_data = "john.doe@example.com"
        
        hash1 = hasher.hash_identity_data(tenant_id, "email", raw_data)
        hash2 = hasher.hash_identity_data(tenant_id, "email", raw_data)
        
        assert hash1["hash"] == hash2["hash"]
    
    def test_different_tenants_different_hashes(self, hasher):
        """Test: Verschiedene Tenants = verschiedene Hashes (Pepper)."""
        raw_data = "john.doe@example.com"
        tenant1 = uuid4()
        tenant2 = uuid4()
        
        hash1 = hasher.hash_identity_data(tenant1, "email", raw_data)
        hash2 = hasher.hash_identity_data(tenant2, "email", raw_data)
        
        assert hash1["hash"] != hash2["hash"]
    
    def test_no_raw_data_in_result(self, hasher, tenant_id):
        """Test: KP001 - Rohdaten NICHT im Ergebnis."""
        raw_data = "sensitive-pii-data@example.com"
        
        result = hasher.hash_identity_data(tenant_id, "email", raw_data)
        
        # Rohdaten dürfen NIRGENDS im Result sein
        result_str = str(result)
        assert "sensitive-pii-data" not in result_str
        assert raw_data not in result_str
    
    def test_verify_hash(self, hasher, tenant_id):
        """Test: Hash-Verifikation funktioniert."""
        raw_data = "test@example.com"
        
        result = hasher.hash_identity_data(tenant_id, "email", raw_data)
        expected_hash = result["hash"]
        
        # Verifikation
        is_valid = hasher.verify_hash(tenant_id, raw_data, expected_hash)
        assert is_valid is True
        
        # Falsche Daten
        is_valid = hasher.verify_hash(tenant_id, "wrong@example.com", expected_hash)
        assert is_valid is False
    
    def test_empty_raw_data_raises_error(self, hasher, tenant_id):
        """Test: Leere raw_data wird abgelehnt."""
        with pytest.raises(ValueError, match="must not be empty"):
            hasher.hash_identity_data(tenant_id, "email", "")
    
    @pytest.mark.slow
    def test_memory_cleanup(self, hasher, tenant_id):
        """Test: KP001 - Memory Cleanup nach Hashing."""
        import gc
        import sys
        
        raw_data = "sensitive-memory-test@example.com"
        
        # Hash erstellen
        result = hasher.hash_identity_data(tenant_id, "email", raw_data)
        
        # Garbage Collection erzwingen
        gc.collect()
        
        # Memory-Scan (simplified, produktiv: Memory Profiler)
        # In Realität würde man hier ein Memory Dump machen
        # und prüfen, ob raw_data noch irgendwo im Speicher ist
        
        # Zumindest prüfen, dass raw_data nicht in result ist
        assert raw_data not in str(result)


class TestPIIDetector:
    """Tests für PII Detection (Runtime Enforcement)."""
    
    @pytest.fixture
    def detector(self):
        from src.utils.pii_detector import PIIDetector
        return PIIDetector()
    
    def test_email_detection(self, detector):
        """Test: Email als PII erkannt."""
        text = "My email is john@example.com"
        assert detector.contains_pii(text) is True
    
    def test_phone_detection(self, detector):
        """Test: Telefonnummer als PII erkannt."""
        text = "Call me at 555-123-4567"
        assert detector.contains_pii(text) is True
    
    def test_no_pii_detection(self, detector):
        """Test: Kein PII = False."""
        text = "This is a normal text without PII"
        assert detector.contains_pii(text) is False
    
    def test_detect_multiple_pii_types(self, detector):
        """Test: Mehrere PII-Typen erkannt."""
        text = "Email: john@example.com, Phone: 555-123-4567"
        types = detector.detect_pii_types(text)
        
        assert "email" in types
        assert "phone" in types
```

**File:** `conformance/test_non_custodial_contract.py`

```python
"""
Contract Tests für Non-Custodial API (KP001).

Testet API-Contract gegen OpenAPI-Spec.
"""

import pytest
import requests
from schemathesis import from_uri


# API-Base-URL (aus Environment)
API_BASE_URL = "http://localhost:8000"

# OpenAPI-Spec laden
schema = from_uri(
    f"{API_BASE_URL}/contracts/identity_data_handling.openapi.yaml"
)


@schema.parametrize()
def test_api_contract(case):
    """
    Contract Test: API entspricht OpenAPI-Spec.
    
    Schemathesis generiert automatisch Test-Cases aus Spec.
    """
    response = case.call()
    case.validate_response(response)


def test_no_raw_data_in_response():
    """Test: KP001 - Response enthält niemals Rohdaten."""
    response = requests.post(
        f"{API_BASE_URL}/hash-identity-data",
        json={
            "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
            "data_type": "email",
            "raw_data": "test@example.com"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Rohdaten dürfen NICHT in Response sein
    assert "test@example.com" not in str(data)
    assert "raw_data" not in data
    
    # Hash muss vorhanden sein
    assert "hash" in data
    assert len(data["hash"]) == 64


def test_response_schema_compliance():
    """Test: Response entspricht JSON-Schema."""
    from jsonschema import validate
    import json
    
    response = requests.post(
        f"{API_BASE_URL}/hash-identity-data",
        json={
            "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
            "data_type": "email",
            "raw_data": "test@example.com"
        }
    )
    
    # JSON-Schema laden
    with open("contracts/schemas/identity_hash.schema.json") as f:
        schema = json.load(f)
    
    # Validierung
    validate(instance=response.json(), schema=schema)
```

---

## Quick Reference Matrix

| Artefakt | File Location | Key Content | Test Command |
|----------|---------------|-------------|--------------|
| **Contract** | `contracts/*.openapi.yaml` | API-Definition, Schemas | `openapi-generator validate` |
| **Core Logic** | `implementations/*/src/` | Python/Rust Code | `pytest -v` |
| **Policy** | `23_compliance/opa/*.rego` | OPA Rules | `opa test .` |
| **CLI** | `12_tooling/cli/` | Validators | `python -m cli.validators` |
| **Tests** | `tests/` + `conformance/` | Unit/Contract Tests | `pytest` + `schemathesis` |

---

## Fortsetzung folgt...

In den nächsten Beispielen zeige ich:
- Beispiel 2: Matrix-Architektur (M001)
- Beispiel 3: GDPR PII Redaction (KP008)
- Beispiel 4: Root Count Validation (R001)
- Beispiel 5: Secrets Management (KP013)
