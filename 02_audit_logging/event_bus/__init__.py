#!/usr/bin/env python3
"""
Audit Event Bus - Initialization Module
========================================

Auto-initialization of event bus from configuration.
Supports multiple backends: in_memory, redis, rabbitmq, nats.

Usage:
    from 02_audit_logging.event_bus import get_audit_bus

    bus = get_audit_bus()
    bus.emit(AuditEvent(...))

Version: 1.0.0
"""

from pathlib import Path
from typing import Optional
import yaml

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "interfaces"))

from audit_event_emitter import (
    AuditEventEmitter,
    set_audit_emitter,
    get_audit_emitter,
    reset_audit_emitter
)

from in_memory_bus import InMemoryAuditBus, create_audit_bus_from_config


# Configuration loader
def load_config(config_path: Optional[str] = None) -> dict:
    """
    Load event bus configuration from manifest.yaml.

    Args:
        config_path: Custom config path (optional)

    Returns:
        Configuration dict
    """
    if config_path is None:
        config_path = Path(__file__).parent / "manifest.yaml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        # Return default config
        return {
            "bus_mode": "in_memory",
            "in_memory": {
                "max_queue_size": 10000,
                "worker_threads": 4,
                "log_dropped_events": True
            }
        }

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_event_bus(config: Optional[dict] = None) -> AuditEventEmitter:
    """
    Create event bus from configuration.

    Args:
        config: Configuration dict (loads from manifest.yaml if None)

    Returns:
        AuditEventEmitter implementation
    """
    if config is None:
        config = load_config()

    bus_mode = config.get("bus_mode", "in_memory")

    if bus_mode == "in_memory":
        bus_config = config.get("in_memory", {})
        return create_audit_bus_from_config(bus_config)

    elif bus_mode == "redis":
        # TODO: Implement Redis backend
        raise NotImplementedError("Redis backend not yet implemented")

    elif bus_mode == "rabbitmq":
        # TODO: Implement RabbitMQ backend
        raise NotImplementedError("RabbitMQ backend not yet implemented")

    elif bus_mode == "nats":
        # TODO: Implement NATS backend
        raise NotImplementedError("NATS backend not yet implemented")

    else:
        raise ValueError(f"Unknown bus_mode: {bus_mode}")


def initialize_global_bus(config_path: Optional[str] = None) -> AuditEventEmitter:
    """
    Initialize global singleton event bus with handlers.

    Args:
        config_path: Custom config path (optional)

    Returns:
        Initialized event bus with registered handlers
    """
    # Use config_loader for full initialization with handlers
    try:
        from config_loader import initialize_event_bus_from_manifest
        bus = initialize_event_bus_from_manifest(config_path)
        set_audit_emitter(bus)
        return bus
    except ImportError:
        # Fallback to simple initialization
        config = load_config(config_path)
        bus = create_event_bus(config)
        set_audit_emitter(bus)
        return bus


def get_audit_bus() -> AuditEventEmitter:
    """
    Get global audit event bus (singleton).

    Auto-initializes if not yet configured.

    Returns:
        AuditEventEmitter instance
    """
    try:
        return get_audit_emitter()
    except RuntimeError:
        # Not initialized yet, auto-initialize
        return initialize_global_bus()


# Export public API
__all__ = [
    "get_audit_bus",
    "initialize_global_bus",
    "create_event_bus",
    "load_config",
    "reset_audit_emitter"
]
