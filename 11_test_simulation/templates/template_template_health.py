"""
Test Template: Health Check Tests

Usage:
1. Copy to tests_core/test_your_health_checker.py
2. Replace HEALTH_MODULE and HEALTH_CLASS
3. Implement health check scenarios
4. Mock external dependencies

Example:
    # From: templates/test_template_health.py
    # To: tests_core/test_health_check_core.py

    from healthcheck.health_check_core import HealthChecker as HEALTH_CLASS
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
import sys
from pathlib import Path

# Import health checker
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "03_core"))
from healthcheck.HEALTH_MODULE import HEALTH_CLASS

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def health_checker():
    """
    Create health checker instance with default config.

    TODO: Adjust parameters based on actual health checker
    """
    return HEALTH_CLASS(
        name="test-service",
        port=8080,
        dependencies=["redis", "postgres", "api"]
    )

@pytest.fixture
def health_checker_minimal():
    """Create health checker with minimal dependencies"""
    return HEALTH_CLASS(
        name="minimal-service",
        port=8000,
        dependencies=[]
    )

# ============================================================================
# Healthy State Tests
# ============================================================================

def test_health_check_all_healthy(health_checker):
    """Test when all systems are healthy"""
    
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"status": "ok"}

        result = health_checker.check()

        assert result["status"] == "healthy", "All systems healthy should return 'healthy'"
        assert "checks" in result

        # All dependency checks should be ok
        for dep in health_checker.dependencies:
            assert result["checks"].get(dep, {}).get("status") == "ok"

def test_health_check_port_accessible(health_checker):
    """Test port accessibility check"""
    with patch('socket.socket') as mock_socket:
        mock_socket_instance = Mock()
        mock_socket_instance.connect_ex.return_value = 0  # Success
        mock_socket.return_value.__enter__.return_value = mock_socket_instance

        result = health_checker.check()

        # Port should be accessible
        assert "port" in result["checks"]
        assert result["checks"]["port"]["status"] in ["ok", "healthy"]

# ============================================================================
# Degraded State Tests
# ============================================================================

def test_health_check_degraded_dependency(health_checker):
    """Test degraded state when one dependency is slow"""
    with patch('requests.get') as mock_get:
        def mock_response(*args, **kwargs):
            # Main service: ok
            # Redis: degraded (slow response)
            if "redis" in str(args):
                response = Mock()
                response.status_code = 200
                response.elapsed.total_seconds.return_value = 5.0  # Slow!
                return response
            else:
                response = Mock()
                response.status_code = 200
                response.elapsed.total_seconds.return_value = 0.1
                return response

        mock_get.side_effect = mock_response

        result = health_checker.check()

        # Overall status should be degraded (not healthy, not down)
        assert result["status"] in ["degraded", "warning"]

def test_health_check_one_dependency_down(health_checker):
    """Test when one non-critical dependency is down"""
    with patch('requests.get') as mock_get:
        def mock_response(*args, **kwargs):
            if "redis" in str(args):
                # Redis down
                raise ConnectionError("Redis unavailable")
            else:
                response = Mock()
                response.status_code = 200
                return response

        mock_get.side_effect = mock_response

        result = health_checker.check()

        # Should be degraded (not completely down)
        assert result["status"] in ["degraded", "unhealthy"]
        assert result["checks"]["redis"]["status"] in ["down", "error"]

# ============================================================================
# Down State Tests
# ============================================================================

def test_health_check_service_down(health_checker):
    """Test when main service is down"""
    with patch('socket.socket') as mock_socket:
        mock_socket_instance = Mock()
        mock_socket_instance.connect_ex.return_value = 1  # Connection refused
        mock_socket.return_value.__enter__.return_value = mock_socket_instance

        result = health_checker.check()

        # Service should be down
        assert result["status"] in ["down", "unhealthy"]

def test_health_check_all_dependencies_down(health_checker):
    """Test when all dependencies are down"""
    with patch('requests.get', side_effect=ConnectionError("All services down")):
        result = health_checker.check()

        assert result["status"] == "down"

        # All dependency checks should show error
        for dep in health_checker.dependencies:
            assert result["checks"][dep]["status"] in ["down", "error"]

# ============================================================================
# Timeout Tests
# ============================================================================

def test_health_check_timeout(health_checker):
    """Test timeout handling"""
    with patch('requests.get', side_effect=TimeoutError("Request timeout")):
        result = health_checker.check()

        assert result["status"] in ["down", "unknown", "timeout"]
        assert "timeout" in str(result).lower() or "error" in result

def test_health_check_slow_response(health_checker):
    """Test slow response (near timeout)"""
    import time

    with patch('requests.get') as mock_get:
        def slow_response(*args, **kwargs):
            time.sleep(0.5)  # Simulate slow response
            response = Mock()
            response.status_code = 200
            return response

        mock_get.side_effect = slow_response

        start = time.time()
        result = health_checker.check()
        elapsed = time.time() - start

        # Should complete (not timeout) but may be flagged
        assert "status" in result
        # May be degraded due to latency

# ============================================================================
# Edge Cases
# ============================================================================

def test_health_check_no_dependencies(health_checker_minimal):
    """Test health check with no dependencies"""
    result = health_checker_minimal.check()

    assert "status" in result
    # With no dependencies, should just check self
    assert result["status"] in ["healthy", "ok"]

def test_health_check_invalid_port():
    """Test health check with invalid port"""
    checker = HEALTH_CLASS(
        name="invalid-port-service",
        port=-1,  # Invalid port
        dependencies=[]
    )

    result = checker.check()

    # Should handle gracefully (not crash)
    assert "status" in result or "error" in result

def test_health_check_malformed_dependency_response(health_checker):
    """Test handling of malformed dependency responses"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.side_effect = ValueError("Invalid JSON")

        result = health_checker.check()

        # Should handle gracefully
        assert "status" in result

# ============================================================================
# Response Structure Tests
# ============================================================================

def test_health_check_response_structure(health_checker):
    """Test that health check response has correct structure"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200

        result = health_checker.check()

        # Required fields
        assert "status" in result
        assert "checks" in result
        assert isinstance(result["checks"], dict)

        # Optional but common fields
        # assert "timestamp" in result
        # assert "uptime" in result

def test_health_check_includes_latency(health_checker):
    """Test that health check includes latency/response time"""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.123
        mock_get.return_value = mock_response

        result = health_checker.check()

        # Should include latency information
        # (adjust based on actual implementation)
        # assert any("latency" in str(check).lower() for check in result["checks"].values())

# ============================================================================
# Integration Tests
# ============================================================================

def test_health_check_with_real_health_data(sample_health_data):
    """Test health checker with realistic health data from fixtures"""
    # Uses conftest.py fixture
    checker = HEALTH_CLASS(name="test", port=8080, dependencies=[])

    # Simulate health data
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = sample_health_data

        result = checker.check()

        assert "status" in result

def test_health_check_endpoint_integration():
    """Test health check with actual HTTP endpoint (if available)"""
    # This test assumes a real endpoint is available
    # Skip if not in integration test environment
    pytest.skip("Integration test - requires real endpoint")

    checker = HEALTH_CLASS(
        name="integration-test",
        port=8080,
        dependencies=["http://localhost:8080/health"]
    )

    result = checker.check()
    assert "status" in result

# ============================================================================

# ============================================================================

def test_health_check_with_mock_endpoint(mock_health_endpoint):
    """Test with mocked health endpoint from fixtures"""
    # Uses conftest.py fixture that mocks requests.get
    checker = HEALTH_CLASS(name="test", port=8080, dependencies=[])

    result = checker.check()

    
    # (adjust based on fixture implementation)

# ============================================================================
# Error Handling Tests
# ============================================================================

def test_health_check_exception_handling(health_checker):
    """Test that exceptions are handled gracefully"""
    with patch('requests.get', side_effect=Exception("Unexpected error")):
        result = health_checker.check()

        # Should not crash, should return error status
        assert "status" in result
        assert result["status"] in ["error", "down", "unknown"]

def test_health_check_network_error(health_checker):
    """Test handling of network errors"""
    with patch('requests.get', side_effect=OSError("Network unreachable")):
        result = health_checker.check()

        assert "status" in result
        assert result["status"] in ["down", "error"]

# ============================================================================
# Performance Tests (Optional)
# ============================================================================

@pytest.mark.performance
def test_health_check_performance():
    """Test health check completes quickly"""
    import time

    checker = HEALTH_CLASS(
        name="perf-test",
        port=8080,
        dependencies=["dep1", "dep2", "dep3"]
    )

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200

        start = time.time()
        result = checker.check()
        elapsed = time.time() - start

        # Health check should complete in <1 second
        assert elapsed < 1.0, f"Health check too slow: {elapsed}s"
        assert "status" in result
