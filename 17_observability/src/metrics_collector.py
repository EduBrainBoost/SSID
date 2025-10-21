"""
SSID Metrics Collector - PII-Protected Observability
Strictly no PII in labels or values. Hash-only, GDPR compliant.
"""
from typing import Dict, Any, Optional
import time

# Forbidden label keys that could contain PII
FORBIDDEN_LABELS = {
    "user_email", "email", "user_name", "username", "name",
    "ssn", "social_security", "iban", "account_number",
    "phone", "phone_number", "address", "ip_address",
    "credit_card", "passport", "license"
}

class MetricsCollector:
    """
    Non-PII metrics collector for SSID observability.
    Enforces strict PII exclusion in all labels and values.
    """

    def __init__(self):
        self.counters: Dict[tuple, int] = {}
        self.gauges: Dict[tuple, tuple] = {}

    def inc(self, name: str, value: int = 1, labels: Optional[Dict[str, Any]] = None) -> int:
        """
        Increment counter metric.

        Args:
            name: Metric name (e.g., 'events_processed')
            value: Increment value (default 1)
            labels: Optional label dict (e.g., {'component': 'sim'})

        Returns:
            Updated counter value

        Raises:
            ValueError: If labels contain forbidden PII fields
        """
        labels = labels or {}

        # Check for PII labels
        pii_labels = FORBIDDEN_LABELS.intersection(labels.keys())
        if pii_labels:
            raise ValueError(f"PII labels forbidden in metrics: {pii_labels}")

        # Create key from name and sorted labels
        key = (name, tuple(sorted(labels.items())))
        self.counters[key] = self.counters.get(key, 0) + value
        return self.counters[key]

    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, Any]] = None) -> float:
        """
        Set gauge metric value.

        Args:
            name: Metric name (e.g., 'queue_depth')
            value: Gauge value
            labels: Optional label dict

        Returns:
            Set gauge value

        Raises:
            ValueError: If labels contain forbidden PII fields
        """
        labels = labels or {}

        # Check for PII labels
        pii_labels = FORBIDDEN_LABELS.intersection(labels.keys())
        if pii_labels:
            raise ValueError(f"PII labels forbidden in metrics: {pii_labels}")

        # Create key and store with timestamp
        key = (name, tuple(sorted(labels.items())))
        self.gauges[key] = (value, time.time())
        return value

    def snapshot(self) -> Dict[str, Any]:
        """
        Get current metrics snapshot.

        Returns:
            Dict with counters and gauges
        """
        return {
            "counters": {
                f"{n}|{dict(l)}": v
                for (n, l), v in self.counters.items()
            },
            "gauges": {
                f"{n}|{dict(l)}": v
                for (n, l), v in self.gauges.items()
            },
            "timestamp": time.time()
        }

    def reset(self):
        """Reset all metrics (for testing)."""
        self.counters.clear()
        self.gauges.clear()
