#!/usr/bin/env python3
"""
SSID Digest Sync Manager (v5.2)
License: GPL-3.0-or-later

Purpose: Periodic consistency check between off-chain and on-chain proof digests
Security: Hash comparison, audit event on mismatch
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DigestSyncManager:
    """Synchronize digest consistency across layers"""

    def __init__(self, config_path: str, audit_log_path: str = "02_audit_logging/logs/digest_sync.log"):
        self.config_path = config_path
        self.audit_log_path = audit_log_path
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

    def sync_digests(self, off_chain_digests: List[str], on_chain_digests: List[str]) -> Dict[str, Any]:
        """Compare off-chain vs on-chain digests"""
        off_set = set(off_chain_digests)
        on_set = set(on_chain_digests)

        missing_on_chain = off_set - on_set
        extra_on_chain = on_set - off_set

        status = "CONSISTENT" if not missing_on_chain and not extra_on_chain else "INCONSISTENT"

        result = {
            "status": status,
            "off_chain_count": len(off_set),
            "on_chain_count": len(on_set),
            "missing_on_chain": list(missing_on_chain),
            "extra_on_chain": list(extra_on_chain),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self._log_audit("sync_executed", result)
        return result

    def _log_audit(self, event: str, context: Dict[str, Any]) -> None:
        log_entry = {"event": event, "timestamp": datetime.now(timezone.utc).isoformat(), "context": context}
        with open(self.audit_log_path, "a") as f:
            f.write(json.dumps(log_entry, sort_keys=True) + "\n")
        logger.info(json.dumps(log_entry))
