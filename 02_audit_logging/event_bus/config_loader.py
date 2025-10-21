#!/usr/bin/env python3
"""
Event Bus Configuration Loader
===============================

Loads event bus configuration from manifest.yaml and initializes handlers.

Features:
- Handler auto-registration from config
- Factory pattern for handler creation
- Validation of handler configuration

Version: 1.0.0
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
import sys

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent / "interfaces"))
sys.path.insert(0, str(Path(__file__).parent.parent / "handlers"))

from audit_event_emitter import AuditEventHandler
from in_memory_bus import InMemoryAuditBus


def load_manifest(manifest_path: Path) -> Dict[str, Any]:
    """
    Load manifest.yaml configuration.

    Args:
        manifest_path: Path to manifest.yaml

    Returns:
        Configuration dict
    """
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with manifest_path.open('r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_handler(handler_config: Dict[str, Any]) -> AuditEventHandler:
    """
    Create handler instance from configuration.

    Args:
        handler_config: Handler configuration dict

    Returns:
        AuditEventHandler instance
    """
    handler_type = handler_config.get("type")
    handler_name = handler_config.get("name")
    enabled = handler_config.get("enabled", True)
    config = handler_config.get("config", {})

    if not enabled:
        return None

    if handler_type == "worm":
        from worm_handler import create_worm_handler_from_config
        return create_worm_handler_from_config(config)

    elif handler_type == "health_log":
        from health_log_handler import create_health_log_handler_from_config
        return create_health_log_handler_from_config(config)

    elif handler_type == "blockchain":
        # TODO: Implement blockchain handler
        print(f"[WARN] Blockchain handler not yet implemented, skipping {handler_name}", file=sys.stderr)
        return None

    elif handler_type == "compliance_push":
        # TODO: Implement compliance push handler
        print(f"[WARN] Compliance push handler not yet implemented, skipping {handler_name}", file=sys.stderr)
        return None

    elif handler_type == "federation":
        # TODO: Implement federation handler
        print(f"[WARN] Federation handler not yet implemented, skipping {handler_name}", file=sys.stderr)
        return None

    else:
        raise ValueError(f"Unknown handler type: {handler_type}")


def initialize_event_bus_from_manifest(manifest_path: str = None) -> InMemoryAuditBus:
    """
    Initialize event bus with handlers from manifest.yaml.

    Args:
        manifest_path: Path to manifest.yaml (optional)

    Returns:
        Configured InMemoryAuditBus instance
    """
    if manifest_path is None:
        manifest_path = Path(__file__).parent / "manifest.yaml"
    else:
        manifest_path = Path(manifest_path)

    # Load configuration
    config = load_manifest(manifest_path)

    # Create event bus
    bus_config = config.get("in_memory", {})
    bus = InMemoryAuditBus(
        max_queue_size=bus_config.get("max_queue_size", 10000),
        worker_threads=bus_config.get("worker_threads", 4),
        log_dropped_events=bus_config.get("log_dropped_events", True)
    )

    # Register handlers
    handlers_config = config.get("handlers", [])

    for handler_config in handlers_config:
        try:
            handler = create_handler(handler_config)

            if handler is not None:
                bus.register_handler(handler)
                print(f"[INFO] Registered handler: {handler.name()}", file=sys.stderr)

        except Exception as e:
            handler_name = handler_config.get("name", "unknown")
            print(f"[ERROR] Failed to create handler {handler_name}: {e}", file=sys.stderr)

    return bus


# Example usage
if __name__ == "__main__":
    print("Event Bus Configuration Loader")
    print("=" * 70)

    # Load and initialize
    bus = initialize_event_bus_from_manifest()

    # Show health
    health = bus.health_check()

    print(f"Status: {health['status']}")
    print(f"Queue Depth: {health['queue_depth']}")
    print(f"Workers: {health['workers']}")
    print(f"Handlers: {health['handlers']}")
    print()

    print("=" * 70)
    print("[OK] Event Bus Initialized")
