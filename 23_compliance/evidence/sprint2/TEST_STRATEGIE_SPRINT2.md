# Sprint 2 - Test-Strategie für 80% Coverage
**Datum:** 2025-10-09
**Baseline:** 6.80% Coverage
**Ziel:** 80%+ Coverage
**Zeitrahmen:** 18 Arbeitstage (Sprint 2 Week 5-6 + Buffer)

---

## Executive Summary

**Ausgangslage:**
- Aktuelle Coverage: 6.80% (126/1,852 Statements)
- 5 kritische Module unter 80%
- 23 Dateien komplett ungetestet

**Strategie:**
- 4-Phasen Ansatz: Quick Wins → Health System → Anti-Gaming → Infrastructure
- Prioritisierung nach Impact × Complexity
- Gestaffelte CI-Thresholds

**Erwartetes Ergebnis:**
- 80-85% Coverage bis Ende Sprint 2
- Alle kritischen Module >60%
- CI-Enforcement aktiv

---

## 1. Analyse der aktuellen Test-Landschaft

### Was funktioniert bereits (6.80%)

**Validators (86-100% Coverage):**
- `check_hash_chain.py`: 86% (3 fehlende Zeilen)
- `check_log_schema.py`: 100% ✅
- `check_worm_storage.py`: 100% ✅

**Anti-Gaming Detektoren (18-45% Coverage):**
- `detect_circular_dependencies.py`: 45%
- `detect_duplicate_identity_hashes.py`: 30%
- `badge_signature_validator.py`: 31%
- `overfitting_detector.py`: 18%

**Existierende Tests (81 passing):**
- `tests_compliance/`: 75 Tests (Anti-Gaming Suite)
- `tests_audit/`: 6 Tests (Validators)

### Was fehlt komplett (0% Coverage)

**Kritische Systeme:**
- Health Check System (229 Statements)
- Anti-Gaming Suite 02_audit_logging (620 Statements)
- Bridges (141 Statements)
- Policy Engine (42 Statements)
- Meta-Orchestration (113 Statements)

---

## 2. Test-Strategie nach Modul

### 2.1 Validators (02_audit_logging/validators/)

**Status:** 86-100% ✅ FAST FERTIG

**Verbleibende Arbeit:**
```python
# check_hash_chain.py - 3 fehlende Zeilen
def test_hash_chain_empty():
    """Test leere Chain"""
    assert validate_hash_chain([])["valid"] is False

def test_hash_chain_invalid_hash():
    """Test ungültiger Hash"""
    chain = [{"index": 0, "hash": "wrong", ...}]
    assert validate_hash_chain(chain)["valid"] is False
```

**Aufwand:** 0.5h
**Coverage-Gewinn:** +0.2%

---

### 2.2 Identity Score (08_identity_score/)

**Status:** 0% Coverage - EINFACHES TARGET

**Test-Strategie:**
```python
# test_identity_score.py
def test_identity_score_basic():
    """Test basic score calculation"""
    from identity_score_calculator import calculate_score

    data = {
        "verified": True,
        "documents": 3,
        "age_days": 365
    }

    score = calculate_score(data)
    assert 0 <= score <= 100

def test_identity_score_edge_cases():
    """Test edge cases"""
    # Minimum
    assert calculate_score({}) >= 0

    # Maximum
    assert calculate_score({"verified": True, "documents": 10}) <= 100

    # Negative inputs
    with pytest.raises(ValueError):
        calculate_score({"age_days": -1})
```

**Aufwand:** 2h
**Coverage-Gewinn:** +1%

---

### 2.3 Health Check System (03_core/healthcheck/)

**Status:** 0% Coverage - HOHE PRIORITÄT

#### health_check_core.py (85 Statements)

**Test-Ansatz:**
```python
# test_health_check_core.py
import pytest
from unittest.mock import Mock, patch
from health_check_core import HealthChecker

@pytest.fixture
def health_checker():
    return HealthChecker(
        name="test-service",
        port=8080,
        dependencies=["redis", "postgres"]
    )

def test_health_check_all_healthy(health_checker):
    """Test wenn alle Systeme healthy"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200

        result = health_checker.check()

        assert result["status"] == "healthy"
        assert result["checks"]["port"] == "ok"
        assert result["checks"]["dependencies"]["redis"] == "ok"

def test_health_check_degraded(health_checker):
    """Test degraded state"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 503

        result = health_checker.check()

        assert result["status"] == "degraded"

def test_health_check_down(health_checker):
    """Test down state"""
    with patch('socket.socket') as mock_socket:
        mock_socket.side_effect = ConnectionRefusedError

        result = health_checker.check()

        assert result["status"] == "down"

def test_health_check_timeout(health_checker):
    """Test timeout handling"""
    with patch('requests.get', side_effect=TimeoutError):
        result = health_checker.check()

        assert result["status"] == "unknown"
        assert "timeout" in result["error"].lower()
```

**Mocking-Strategie:**
- `requests.get` für HTTP Health Endpoints
- `socket.socket` für Port Checks
- `time.time` für Timeout-Tests

**Aufwand:** 4h
**Coverage-Gewinn:** +5%

#### health_audit_logger.py (43 Statements)

**Test-Ansatz:**
```python
# test_health_audit_logger.py
def test_health_audit_log_entry():
    """Test logging von Health Events"""
    from health_audit_logger import HealthAuditLogger

    logger = HealthAuditLogger()

    event = {
        "service": "test",
        "status": "healthy",
        "timestamp": "2025-01-01T00:00:00Z"
    }

    logger.log(event)

    logs = logger.get_logs()
    assert len(logs) == 1
    assert logs[0]["service"] == "test"
```

**Aufwand:** 2h
**Coverage-Gewinn:** +2%

#### generate_health_wrappers.py (65 Statements)

**Test-Ansatz:**
```python
# test_health_wrapper_generation.py
def test_generate_health_wrapper():
    """Test Health Wrapper Code Generation"""
    from generate_health_wrappers import generate_wrapper

    config = {
        "service": "test-service",
        "port": 8080,
        "endpoints": ["/health", "/ready"]
    }

    code = generate_wrapper(config)

    assert "def check_health" in code
    assert "8080" in code
    assert "/health" in code
```

**Aufwand:** 3h
**Coverage-Gewinn:** +3%

**Health System GESAMT:**
- **Aufwand:** 9h
- **Coverage-Gewinn:** +10%

---

### 2.4 Anti-Gaming Suite (02_audit_logging/anti_gaming/)

**Status:** 0% Coverage - GRÖSSTES MODUL

#### time_skew_analyzer.py (107 Statements)

**Test-Strategie:**
```python
# test_time_skew_analyzer.py
from freezegun import freeze_time
from time_skew_analyzer import TimeSkewAnalyzer

@freeze_time("2025-01-01 12:00:00")
def test_time_skew_detection_normal():
    """Test normale Zeitabstände"""
    analyzer = TimeSkewAnalyzer(max_skew_seconds=60)

    events = [
        {"ts": "2025-01-01T12:00:00Z", "user": "alice"},
        {"ts": "2025-01-01T12:00:30Z", "user": "alice"},
    ]

    result = analyzer.analyze(events)
    assert result["skew_detected"] is False

@freeze_time("2025-01-01 12:00:00")
def test_time_skew_detection_anomaly():
    """Test Zeitmanipulation"""
    analyzer = TimeSkewAnalyzer(max_skew_seconds=60)

    events = [
        {"ts": "2025-01-01T12:00:00Z", "user": "alice"},
        {"ts": "2025-01-01T11:00:00Z", "user": "alice"},  # Zurück in der Zeit!
    ]

    result = analyzer.analyze(events)
    assert result["skew_detected"] is True
    assert "backwards" in result["anomalies"][0]["type"]
```

**Kritische Dependencies:**
- `freezegun` für Zeit-Mocking
- Fixtures für Event-Sequenzen

**Aufwand:** 5h

#### anomaly_rate_guard.py (111 Statements)

**Test-Strategie:**
```python
# test_anomaly_rate_guard.py
def test_anomaly_rate_normal():
    """Test normale Rate"""
    guard = AnomalyRateGuard(
        max_events_per_hour=100,
        window_minutes=60
    )

    events = [{"ts": f"2025-01-01T12:{i:02d}:00Z"} for i in range(50)]

    result = guard.check(events)
    assert result["anomaly"] is False

def test_anomaly_rate_spike():
    """Test Rate-Spike"""
    guard = AnomalyRateGuard(max_events_per_hour=100)

    # 200 Events in 1 Minute = Anomalie
    events = [{"ts": "2025-01-01T12:00:00Z"} for _ in range(200)]

    result = guard.check(events)
    assert result["anomaly"] is True
    assert result["rate"] > 100
```

**Aufwand:** 5h

#### replay_attack_detector.py (96 Statements)

**Test-Strategie:**
```python
# test_replay_attack_detector.py
def test_replay_attack_unique_events():
    """Test eindeutige Events"""
    detector = ReplayAttackDetector()

    events = [
        {"hash": "abc123", "nonce": "1"},
        {"hash": "def456", "nonce": "2"},
    ]

    result = detector.scan(events)
    assert result["replay_detected"] is False

def test_replay_attack_duplicate():
    """Test Replay Attack"""
    detector = ReplayAttackDetector()

    events = [
        {"hash": "abc123", "nonce": "1"},
        {"hash": "abc123", "nonce": "1"},  # Duplicate!
    ]

    result = detector.scan(events)
    assert result["replay_detected"] is True
    assert len(result["duplicates"]) == 1
```

**Aufwand:** 5h

#### overfitting_detector.py (95 Statements)

**Test-Strategie:**
```python
# test_overfitting_detector.py
def test_overfitting_normal_pattern():
    """Test normale Pattern"""
    detector = OverfittingDetector()

    patterns = {
        "test_a": 10,
        "test_b": 12,
        "test_c": 9
    }

    result = detector.detect(patterns)
    assert result["overfitting"] is False

def test_overfitting_detected():
    """Test Overfitting durch repeated patterns"""
    detector = OverfittingDetector()

    patterns = {
        "test_a": 1000,  # Viel zu oft!
        "test_b": 2,
        "test_c": 3
    }

    result = detector.detect(patterns)
    assert result["overfitting"] is True
    assert "test_a" in result["suspicious_patterns"]
```

**Aufwand:** 5h

#### dependency_graph_generator.py (95 Statements)

**Test-Strategie:**
```python
# test_dependency_graph_generator.py
def test_generate_dependency_graph_simple():
    """Test einfacher Graph"""
    generator = DependencyGraphGenerator()

    deps = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": [],
        "D": []
    }

    graph = generator.generate(deps)

    assert len(graph["nodes"]) == 4
    assert len(graph["edges"]) == 3

def test_generate_dependency_graph_cycle_detection():
    """Test Zyklus-Erkennung"""
    generator = DependencyGraphGenerator()

    deps = {
        "A": ["B"],
        "B": ["C"],
        "C": ["A"]  # Cycle!
    }

    graph = generator.generate(deps)

    assert graph["has_cycle"] is True
    assert "A" in graph["cycle_path"]
```

**Aufwand:** 5h

#### circular_dependency_validator.py (116 Statements)

**Test-Strategie:**
```python
# test_circular_dependency_validator.py
def test_circular_dependency_validation_ok():
    """Test valide Dependencies"""
    validator = CircularDependencyValidator()

    deps = {
        "mod_a": ["mod_b"],
        "mod_b": ["mod_c"],
        "mod_c": []
    }

    result = validator.validate(deps)

    assert result["valid"] is True
    assert len(result["cycles"]) == 0

def test_circular_dependency_validation_fail():
    """Test zirkuläre Dependencies"""
    validator = CircularDependencyValidator()

    deps = {
        "mod_a": ["mod_b"],
        "mod_b": ["mod_c"],
        "mod_c": ["mod_a"]  # Cycle!
    }

    result = validator.validate(deps)

    assert result["valid"] is False
    assert len(result["cycles"]) > 0
```

**Aufwand:** 6h

**Anti-Gaming GESAMT (02_audit_logging):**
- **Aufwand:** 31h
- **Coverage-Gewinn:** +34%

---

### 2.5 Bridges (Interconnect)

#### bridge_compliance_push.py (73 Statements)

**Test-Strategie:**
```python
# test_bridge_compliance_push.py
def test_bridge_push_success():
    """Test erfolgreicher Push"""
    from bridge_compliance_push import CompliancePushBridge

    bridge = CompliancePushBridge(target="23_compliance")

    data = {
        "event": "test",
        "payload": {"key": "value"}
    }

    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200

        result = bridge.push(data)

        assert result["success"] is True

def test_bridge_push_failure():
    """Test fehlgeschlagener Push"""
    bridge = CompliancePushBridge(target="23_compliance")

    with patch('requests.post', side_effect=ConnectionError):
        result = bridge.push({"event": "test"})

        assert result["success"] is False
        assert "error" in result
```

**Aufwand:** 4h

#### bridge_23compliance.py (36 Statements)

**Test-Strategie:**
```python
# test_bridge_23compliance.py
def test_bridge_data_transformation():
    """Test Daten-Transformation"""
    from bridge_23compliance import Compliance23Bridge

    bridge = Compliance23Bridge()

    audit_data = {
        "ts": "2025-01-01T00:00:00Z",
        "event": "test"
    }

    compliance_data = bridge.transform(audit_data)

    assert "timestamp" in compliance_data
    assert "compliance_event" in compliance_data
```

**Aufwand:** 2h

#### bridge_foundation.py (32 Statements)

**Test-Strategie:**
```python
# test_bridge_foundation.py
def test_bridge_base_class():
    """Test Bridge Base Class"""
    from bridge_foundation import Bridge

    class TestBridge(Bridge):
        def push(self, data):
            return {"success": True}

    bridge = TestBridge(name="test")
    assert bridge.name == "test"
    assert bridge.push({"key": "value"})["success"]
```

**Aufwand:** 2h

**Bridges GESAMT:**
- **Aufwand:** 8h
- **Coverage-Gewinn:** +7%

---

### 2.6 Policy Engine (23_compliance/policies/)

#### policy_engine.py (42 Statements)

**Test-Strategie:**
```python
# test_policy_engine.py
def test_policy_engine_load():
    """Test Policy Loading"""
    from policy_engine import PolicyEngine

    engine = PolicyEngine()
    engine.load_policy("test_policy", {
        "rules": [
            {"name": "rule1", "condition": "x > 5"}
        ]
    })

    assert "test_policy" in engine.policies

def test_policy_engine_evaluate():
    """Test Policy Evaluation"""
    engine = PolicyEngine()
    engine.load_policy("test", {
        "rules": [{"name": "min_score", "condition": "score >= 80"}]
    })

    result = engine.evaluate("test", {"score": 90})
    assert result["passed"] is True

    result = engine.evaluate("test", {"score": 70})
    assert result["passed"] is False
```

**Aufwand:** 2h
**Coverage-Gewinn:** +2%

---

### 2.7 Anti-Gaming Suite (23_compliance/anti_gaming/)

#### dependency_graph_generator.py (216 Statements)

**Hinweis:** GRÖSSTE DATEI - Komplex!

**Test-Strategie:**
```python
# test_dependency_graph_23compliance.py
def test_generate_compliance_dependency_graph():
    """Test Compliance Dependency Graph"""
    from dependency_graph_generator import ComplianceDependencyGraph

    generator = ComplianceDependencyGraph()

    modules = {
        "23_compliance": ["02_audit_logging", "03_core"],
        "02_audit_logging": ["03_core"],
        "03_core": []
    }

    graph = generator.generate(modules)

    assert len(graph.nodes) == 3
    assert graph.has_edge("23_compliance", "02_audit_logging")

def test_detect_compliance_cycles():
    """Test Cycle Detection im Compliance Graph"""
    generator = ComplianceDependencyGraph()

    modules = {
        "A": ["B"],
        "B": ["C"],
        "C": ["A"]
    }

    cycles = generator.find_cycles(modules)

    assert len(cycles) > 0
    assert ["A", "B", "C", "A"] in cycles
```

**Aufwand:** 8h
**Coverage-Gewinn:** +12%

#### badge_integrity_checker.py (168 Statements)

**Test-Strategie:**
```python
# test_badge_integrity_checker.py
def test_badge_integrity_valid():
    """Test valides Badge"""
    from badge_integrity_checker import BadgeIntegrityChecker

    checker = BadgeIntegrityChecker()

    badge = {
        "id": "badge_123",
        "signature": "abc...",
        "issued_at": "2025-01-01T00:00:00Z",
        "data": {"score": 90}
    }

    result = checker.check(badge)

    assert result["valid"] is True

def test_badge_integrity_tampered():
    """Test manipuliertes Badge"""
    checker = BadgeIntegrityChecker()

    badge = {
        "id": "badge_123",
        "signature": "abc...",
        "data": {"score": 90}  # Data changed but signature not updated!
    }

    result = checker.check(badge)

    assert result["valid"] is False
    assert "signature-mismatch" in result["errors"]
```

**Aufwand:** 6h
**Coverage-Gewinn:** +9%

**23_compliance Anti-Gaming GESAMT:**
- **Aufwand:** 14h
- **Coverage-Gewinn:** +21%

---

### 2.8 Meta-Orchestration (24_meta_orchestration/)

#### compliance_chain_trigger.py (113 Statements)

**Test-Strategie:**
```python
# test_compliance_chain_trigger.py
def test_compliance_chain_trigger_basic():
    """Test Basic Chain Triggering"""
    from compliance_chain_trigger import ComplianceChainTrigger

    trigger = ComplianceChainTrigger()

    event = {
        "type": "compliance_check",
        "module": "23_compliance"
    }

    result = trigger.execute(event)

    assert result["triggered"] is True
    assert len(result["chain"]) > 0

def test_compliance_chain_error_handling():
    """Test Error Propagation in Chain"""
    trigger = ComplianceChainTrigger()

    # Simulate error in chain
    with patch('module.execute', side_effect=Exception("Test error")):
        result = trigger.execute({"type": "test"})

        assert result["success"] is False
        assert "error" in result
```

**Aufwand:** 6h
**Coverage-Gewinn:** +6%

---

## 3. Implementierungs-Roadmap

### Phase 1: Quick Wins (Tage 1-2)

**Ziel:** 6.8% → 10% Coverage

| Tag | Aufgabe | Datei | Aufwand | Coverage |
|-----|---------|-------|---------|----------|
| 1 | Hash Chain Edge Cases | check_hash_chain.py | 0.5h | +0.2% |
| 1-2 | Identity Score Tests | identity_score_calculator.py | 2h | +1% |
| **GESAMT** | **2 Aufgaben** | **2 Dateien** | **2.5h** | **+1.2%** |

**Ergebnis:** 8% Coverage

---

### Phase 2: Health System (Tage 3-5)

**Ziel:** 8% → 18% Coverage

| Tag | Aufgabe | Datei | Aufwand | Coverage |
|-----|---------|-------|---------|----------|
| 3-4 | Health Check Core | health_check_core.py | 4h | +5% |
| 4 | Health Audit Logger | health_audit_logger.py | 2h | +2% |
| 5 | Health Wrappers | generate_health_wrappers.py | 3h | +3% |
| **GESAMT** | **3 Aufgaben** | **3 Dateien** | **9h** | **+10%** |

**Ergebnis:** 18% Coverage

---

### Phase 3: Anti-Gaming Core (Tage 6-15)

**Ziel:** 18% → 73% Coverage

| Tag | Aufgabe | Datei | Aufwand | Coverage |
|-----|---------|-------|---------|----------|
| 6-7 | Time Skew Analyzer | time_skew_analyzer.py | 5h | +6% |
| 7-8 | Anomaly Rate Guard | anomaly_rate_guard.py | 5h | +6% |
| 8-9 | Replay Attack Detector | replay_attack_detector.py | 5h | +5% |
| 9-10 | Overfitting Detector | overfitting_detector.py | 5h | +5% |
| 10-11 | Dep Graph Generator (audit) | dependency_graph_generator.py | 5h | +5% |
| 11-13 | Circular Dep Validator | circular_dependency_validator.py | 6h | +6% |
| 13-15 | Dep Graph Generator (compliance) | dependency_graph_generator.py | 8h | +12% |
| 15 | Badge Integrity Checker | badge_integrity_checker.py | 6h | +9% |
| **GESAMT** | **8 Aufgaben** | **8 Dateien** | **45h** | **+54%** |

**Ergebnis:** 72% Coverage

---

### Phase 4: Infrastructure (Tage 16-18)

**Ziel:** 72% → 85%+ Coverage

| Tag | Aufgabe | Datei | Aufwand | Coverage |
|-----|---------|-------|---------|----------|
| 16 | Bridge Compliance Push | bridge_compliance_push.py | 4h | +4% |
| 16-17 | Bridge 23compliance | bridge_23compliance.py | 2h | +2% |
| 17 | Bridge Foundation | bridge_foundation.py | 2h | +2% |
| 17-18 | Policy Engine | policy_engine.py | 2h | +2% |
| 18 | Compliance Chain Trigger | compliance_chain_trigger.py | 6h | +6% |
| **GESAMT** | **5 Aufgaben** | **5 Dateien** | **16h** | **+16%** |

**Ergebnis:** 88% Coverage

---

## 4. Test-Infrastruktur Setup

### 4.1 Fixtures (conftest.py)

```python
# 11_test_simulation/conftest.py
import pytest
import sys
from pathlib import Path
from datetime import datetime

# Import-Helper für Number-Prefixed Modules
def add_module_path(module_name):
    """Add number-prefixed module to sys.path"""
    root = Path(__file__).parent.parent
    module_path = root / module_name
    if str(module_path) not in sys.path:
        sys.path.insert(0, str(module_path))

# Auto-add bei Import
for module in ["02_audit_logging", "03_core", "08_identity_score",
               "23_compliance", "24_meta_orchestration"]:
    add_module_path(module)

# Shared Fixtures
@pytest.fixture
def sample_audit_log():
    """Sample audit log entries"""
    return [
        {
            "ts": "2025-01-01T00:00:00Z",
            "level": "INFO",
            "message": "test",
            "source": "unit-test",
            "hash": "abc123"
        }
    ]

@pytest.fixture
def sample_hash_chain():
    """Sample hash chain for testing"""
    import hashlib

    def h(i, prev, payload):
        return hashlib.sha256(f"{i}|{prev}|{payload}".encode()).hexdigest()

    chain = [
        {
            "index": 0,
            "payload": "genesis",
            "prev_hash": "GENESIS",
            "hash": h(0, "GENESIS", "genesis")
        }
    ]

    return chain

@pytest.fixture
def mock_health_endpoint(monkeypatch):
    """Mock HTTP health endpoint"""
    def mock_get(*args, **kwargs):
        class MockResponse:
            status_code = 200
            def json(self):
                return {"status": "healthy"}
        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)

@pytest.fixture
def sample_dependency_graph():
    """Sample dependency graph for testing"""
    return {
        "nodes": ["A", "B", "C"],
        "edges": [("A", "B"), ("B", "C")]
    }

@pytest.fixture
def sample_badge_data():
    """Sample badge for testing"""
    return {
        "id": "badge_test_123",
        "signature": "abc123def456",
        "issued_at": "2025-01-01T00:00:00Z",
        "data": {
            "score": 90,
            "level": "gold"
        }
    }

@pytest.fixture
def freeze_time_2025():
    """Freeze time to 2025-01-01"""
    from freezegun import freeze_time
    with freeze_time("2025-01-01 12:00:00"):
        yield
```

### 4.2 Test Templates

#### Template: Validator Test
```python
# templates/test_template_validator.py
"""
Template for Validator Tests

Usage:
1. Copy this file to tests_*/test_your_validator.py
2. Replace VALIDATOR_NAME with actual validator
3. Implement test cases
"""
import pytest
import sys
from pathlib import Path

# Import validator
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02_audit_logging"))
from validators.VALIDATOR_NAME import validate_function

def test_validator_valid_input():
    """Test valid input"""
    data = {...}  # Valid input
    result = validate_function(data)
    assert result["valid"] is True

def test_validator_invalid_input():
    """Test invalid input"""
    data = {...}  # Invalid input
    result = validate_function(data)
    assert result["valid"] is False
    assert len(result["errors"]) > 0

def test_validator_edge_cases():
    """Test edge cases"""
    # Empty
    assert validate_function([])["valid"] is False

    # None
    assert validate_function(None)["valid"] is False
```

#### Template: Anti-Gaming Test
```python
# templates/test_template_anti_gaming.py
"""
Template for Anti-Gaming Tests

Usage:
1. Copy to tests_compliance/test_your_detector.py
2. Replace DETECTOR_NAME
3. Implement scenarios
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02_audit_logging"))
from anti_gaming.DETECTOR_NAME import Detector

@pytest.fixture
def detector():
    return Detector(threshold=100)

def test_detector_normal_activity(detector):
    """Test normal activity - should NOT flag"""
    events = [...]  # Normal events
    result = detector.analyze(events)
    assert result["anomaly_detected"] is False

def test_detector_suspicious_activity(detector):
    """Test suspicious activity - SHOULD flag"""
    events = [...]  # Suspicious events
    result = detector.analyze(events)
    assert result["anomaly_detected"] is True
    assert len(result["anomalies"]) > 0

def test_detector_edge_cases(detector):
    """Test edge cases"""
    # Empty
    assert detector.analyze([])["anomaly_detected"] is False

    # Single event
    result = detector.analyze([{"event": "test"}])
    assert "error" not in result
```

#### Template: Health Check Test
```python
# templates/test_template_health.py
"""
Template for Health Check Tests
"""
import pytest
from unittest.mock import patch, Mock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "03_core"))
from healthcheck.HEALTH_MODULE import HealthChecker

@pytest.fixture
def health_checker():
    return HealthChecker(name="test-service", port=8080)

def test_health_check_healthy(health_checker):
    """Test healthy state"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200

        result = health_checker.check()
        assert result["status"] == "healthy"

def test_health_check_unhealthy(health_checker):
    """Test unhealthy state"""
    with patch('requests.get', side_effect=ConnectionError):
        result = health_checker.check()
        assert result["status"] in ["down", "unhealthy"]

def test_health_check_timeout(health_checker):
    """Test timeout handling"""
    with patch('requests.get', side_effect=TimeoutError):
        result = health_checker.check()
        assert "timeout" in result or result["status"] == "unknown"
```

#### Template: Bridge Test
```python
# templates/test_template_bridge.py
"""
Template for Bridge Tests
"""
import pytest
from unittest.mock import patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "02_audit_logging"))
from interconnect.BRIDGE_NAME import Bridge

@pytest.fixture
def bridge():
    return Bridge(target="23_compliance")

def test_bridge_push_success(bridge):
    """Test successful data push"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200

        result = bridge.push({"data": "test"})
        assert result["success"] is True

def test_bridge_push_failure(bridge):
    """Test failed data push"""
    with patch('requests.post', side_effect=ConnectionError):
        result = bridge.push({"data": "test"})
        assert result["success"] is False

def test_bridge_data_transformation(bridge):
    """Test data transformation"""
    input_data = {...}
    output_data = bridge.transform(input_data)

    # Verify transformation
    assert "expected_field" in output_data
```

---

## 5. Coverage CI Enforcement

### ci_coverage_enforcement.yml

```yaml
name: Coverage Enforcement CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

jobs:
  coverage-check:
    name: Test Coverage Check
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest pytest-cov pytest-mock freezegun requests-mock
          pip install -r requirements.txt

      - name: Run tests with coverage
        run: |
          pytest 11_test_simulation/tests_compliance/ \
                 11_test_simulation/tests_audit/ \
                 --cov=02_audit_logging \
                 --cov=03_core \
                 --cov=08_identity_score \
                 --cov=23_compliance \
                 --cov=24_meta_orchestration \
                 --cov-report=json:coverage.json \
                 --cov-report=html:coverage_html \
                 --cov-report=term-missing \
                 -v

      - name: Check coverage threshold
        run: |
          COVERAGE=$(python -c "import json; print(json.load(open('coverage.json'))['totals']['percent_covered'])")
          echo "Coverage: $COVERAGE%"

          # Gestaffelte Thresholds
          MIN_COVERAGE=75.0  # Wird nach Sprint 2 auf 80.0 erhöht

          if (( $(echo "$COVERAGE < $MIN_COVERAGE" | bc -l) )); then
            echo "ERROR: Coverage $COVERAGE% below minimum $MIN_COVERAGE%"
            exit 1
          fi

          echo "SUCCESS: Coverage $COVERAGE% meets threshold"

      - name: Upload coverage reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-reports
          path: |
            coverage.json
            coverage_html/
          retention-days: 30

      - name: Generate coverage badge
        if: success()
        run: |
          COVERAGE=$(python -c "import json; print(int(json.load(open('coverage.json'))['totals']['percent_covered']))")

          if [ $COVERAGE -ge 80 ]; then
            COLOR="brightgreen"
          elif [ $COVERAGE -ge 60 ]; then
            COLOR="yellow"
          else
            COLOR="red"
          fi

          echo "![Coverage](https://img.shields.io/badge/coverage-${COVERAGE}%25-${COLOR})" > coverage_badge.md

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const coverage = JSON.parse(fs.readFileSync('coverage.json'));
            const pct = coverage.totals.percent_covered.toFixed(2);

            const comment = `## Coverage Report

            **Overall Coverage:** ${pct}%

            **Target:** 80%
            **Status:** ${pct >= 80 ? '✅ PASS' : '⚠️ Below Target'}

            [View Full Report](artifact-link)
            `;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

---

## 6. Erfolgsmetriken & KPIs

### Coverage Metriken
- [ ] Baseline: 6.8% ✅
- [ ] Phase 1: 8%
- [ ] Phase 2: 18%
- [ ] Phase 3: 72%
- [ ] Phase 4: 85%+
- [ ] **ZIEL: 80%** ✅

### Qualitätsmetriken
- [ ] Alle Tests bestehen (0 failures)
- [ ] Keine flaky Tests (<1% flakiness)
- [ ] Test-Ausführung <10 Minuten
- [ ] Coverage-Trend positiv (+5%/Woche)

### CI/CD Metriken
- [ ] CI-Enforcement aktiv
- [ ] PR-Blocking bei <75% Coverage
- [ ] Automatische Coverage-Reports
- [ ] Badge in README aktualisiert

---

## 7. Risiken & Mitigation

### Risiko 1: Zeitüberschreitung
**Wahrscheinlichkeit:** MITTEL
**Impact:** HOCH

**Mitigation:**
- Phase 3 in Sprints aufteilen (2-3 Tage pro Modul)
- Priorisierung: P1 vor P2
- Akzeptiere 75-78% als "good enough" für Sprint 2

### Risiko 2: Komplexe Module (Dep Graph Generator)
**Wahrscheinlichkeit:** HOCH
**Impact:** MITTEL

**Mitigation:**
- Start mit einfachen Tests (Happy Path)
- Edge Cases in Sprint 3 verschieben
- Mocking für komplexe Abhängigkeiten

### Risiko 3: Flaky Tests (Zeit-basiert)
**Wahrscheinlichkeit:** MITTEL
**Impact:** MITTEL

**Mitigation:**
- freezegun für deterministische Zeit-Tests
- Retry-Logic in CI (max 3 retries)
- Isolation zwischen Tests

### Risiko 4: CI Setup-Zeit
**Wahrscheinlichkeit:** NIEDRIG
**Impact:** NIEDRIG

**Mitigation:**
- Dependencies cachen in CI
- Parallele Test-Ausführung
- Optimierte pytest-Konfiguration

---

## 8. Nächste Schritte (SOFORT)

### Heute (Tag 1)

**1. Setup (1h)**
- [ ] conftest.py erstellen
- [ ] 4 Templates erstellen
- [ ] Dependencies installieren (`freezegun`, `requests-mock`)

**2. Phase 1 Start (2h)**
- [ ] Edge Cases für hash_chain.py
- [ ] Identity Score Tests

**3. Verify (15min)**
- [ ] Coverage Run
- [ ] Ziel: 8% erreicht

### Morgen (Tag 2)

**4. Phase 1 Complete (0.5h)**
- [ ] Letzte Edge Cases
- [ ] Alle Tests grün

**5. Phase 2 Start (4h)**
- [ ] Health Check Core Tests beginnen

---

**Status:** ✅ BEREIT FÜR UMSETZUNG
**Nächster Checkpoint:** Tag 2 (8% Coverage)
**Sprint 2 Ziel:** 80% Coverage bis Tag 18

---

**Erstellt:** 2025-10-09
**Version:** 1.0
**Owner:** SSID Compliance Team
