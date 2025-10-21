#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shard_health_base.py – Base Class for Shard Health Checks
Autor: edubrainboost ©2025 MIT License

Consolidates 384 duplicate health modules into single base class with
minimal per-shard subclasses. Maintains compliance while reducing build
overhead by ~38s and ~700KB code size.

Usage:
    class MyShardHealth(ShardHealthCheck):
        def __init__(self):
            super().__init__("MyShard", "01")

Features:
- Standard health check interface
- Automatic timestamp generation
- Shard identification
- Extensible for custom checks
- Flask/FastAPI compatible response format
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
import logging


class ShardHealthCheck:
    """
    Base class for shard health checks.

    Provides standard health check implementation with automatic
    timestamp, shard identification, and extensibility for custom checks.

    Attributes:
        shard_name (str): Human-readable shard name
        shard_id (str): Shard identifier (e.g., "01", "02")
        version (str): Health check version
    """

    VERSION = "1.0.0"

    def __init__(self, shard_name: str, shard_id: str):
        """
        Initialize shard health check.

        Args:
            shard_name: Human-readable shard name (e.g., "Identitaet_Personen")
            shard_id: Two-digit shard identifier (e.g., "01")
        """
        self.shard_name = shard_name
        self.shard_id = shard_id
        self.logger = logging.getLogger(f"health.{shard_name}")

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status for this shard.

        Override this method in subclasses to add custom health checks.

        Returns:
            Dict with health status information:
            {
                "status": "healthy" | "degraded" | "unhealthy",
                "shard": shard_name,
                "shard_id": shard_id,
                "timestamp": ISO8601 timestamp,
                "version": version,
                "checks": {...}  # Optional custom checks
            }
        """
        return {
            "status": "healthy",
            "shard": self.shard_name,
            "shard_id": self.shard_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": self.VERSION
        }

    def check_database(self) -> bool:
        """
        Check database connectivity.

        Override in subclass if shard has database dependency.

        Returns:
            True if database is accessible, False otherwise
        """
        # Default: no database (stateless shard)
        return True

    def check_external_service(self, service_name: str) -> bool:
        """
        Check external service connectivity.

        Override in subclass for custom service checks.

        Args:
            service_name: Name of external service to check

        Returns:
            True if service is accessible, False otherwise
        """
        # Default: no external services
        return True

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get shard-specific metrics.

        Override in subclass to provide custom metrics.

        Returns:
            Dict with metric name -> value
        """
        return {}

    def to_json(self) -> Dict[str, Any]:
        """
        Get JSON-serializable health status.

        Alias for get_health_status() for compatibility.

        Returns:
            Health status dict
        """
        return self.get_health_status()

    def __repr__(self) -> str:
        """String representation."""
        return f"ShardHealthCheck(shard={self.shard_name}, id={self.shard_id})"


# Example subclass (can be used as template)
class ExampleShardHealth(ShardHealthCheck):
    """Example shard health check implementation."""

    def __init__(self):
        super().__init__("ExampleShard", "00")

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status with custom checks."""
        base = super().get_health_status()

        # Add custom checks
        base["checks"] = {
            "database": self.check_database(),
            "external_service": self.check_external_service("example-api")
        }

        # Update overall status based on checks
        if not all(base["checks"].values()):
            base["status"] = "degraded"

        return base

    def check_database(self) -> bool:
        """Check example database."""
        # Implement actual database check
        return True

    def check_external_service(self, service_name: str) -> bool:
        """Check example external service."""
        # Implement actual service check
        return True


# Flask integration helper
def create_flask_health_endpoint(health_check: ShardHealthCheck):
    """
    Create Flask health endpoint from health check instance.

    Args:
        health_check: ShardHealthCheck instance

    Returns:
        Flask route function

    Example:
        from flask import Flask
        app = Flask(__name__)
        health_check = MyShardHealth()
        app.route('/health')(create_flask_health_endpoint(health_check))
    """
    def health():
        from flask import jsonify
        return jsonify(health_check.get_health_status())
    return health


# FastAPI integration helper
def create_fastapi_health_endpoint(health_check: ShardHealthCheck):
    """
    Create FastAPI health endpoint from health check instance.

    Args:
        health_check: ShardHealthCheck instance

    Returns:
        FastAPI route function

    Example:
        from fastapi import FastAPI
        app = FastAPI()
        health_check = MyShardHealth()
        app.get("/health")(create_fastapi_health_endpoint(health_check))
    """
    async def health():
        return health_check.get_health_status()
    return health
