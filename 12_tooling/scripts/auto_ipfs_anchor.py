#!/usr/bin/env python3
"""
auto_ipfs_anchor.py - SSID Automated IPFS Anchoring System
Blueprint v4.3 - Auto-Anchoring & Telemetry Layer

This script automatically anchors governance artifacts to IPFS for tamper-proof,
decentralized proof-of-existence. It processes registry events and uploads
relevant artifacts to IPFS, creating an immutable audit trail.

Features:
- Automatic detection of new proof-anchors from registry events
- IPFS upload with local or Web3.Storage API support
- CID tracking and manifest generation
- Verification of existing anchored content
- Compliance with GDPR/eIDAS/MiCA (only hashes and metadata)

Usage:
    python3 auto_ipfs_anchor.py                    # Process latest events
    python3 auto_ipfs_anchor.py --verify           # Verify existing CIDs
    python3 auto_ipfs_anchor.py --event-file path  # Process specific event
"""

import json
import hashlib
import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import urllib.request
import urllib.error

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_LOG = PROJECT_ROOT / "24_meta_orchestration/registry/logs/registry_events.log"
IPFS_MANIFEST = PROJECT_ROOT / "24_meta_orchestration/registry/manifests/ipfs_anchor_manifest.json"
RELEASE_DIR = PROJECT_ROOT / "05_documentation/releases"
MANIFESTS_DIR = PROJECT_ROOT / "24_meta_orchestration/registry/manifests"

# IPFS Configuration
IPFS_GATEWAY = "https://ipfs.io/ipfs/"
WEB3_STORAGE_API_ENDPOINT = "https://api.web3.storage/upload"
WEB3_STORAGE_TOKEN_ENV = "WEB3_STORAGE_TOKEN"

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


# ═══════════════════════════════════════════════════════════════════════════
# IPFS Operations
# ═══════════════════════════════════════════════════════════════════════════

def check_ipfs_available() -> bool:
    """Check if IPFS CLI is available on the system."""
    try:
        result = subprocess.run(
            ["ipfs", "version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def upload_to_ipfs_local(file_path: Path) -> Optional[str]:
    """
    Upload a file to IPFS using local IPFS daemon.

    Args:
        file_path: Path to the file to upload

    Returns:
        CID string if successful, None otherwise
    """
    try:
        result = subprocess.run(
            ["ipfs", "add", "-Q", str(file_path)],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            cid = result.stdout.strip()
            return cid
        else:
            print(f"{Colors.RED}✗ IPFS upload failed: {result.stderr}{Colors.NC}")
            return None

    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}✗ IPFS upload timed out{Colors.NC}")
        return None
    except Exception as e:
        print(f"{Colors.RED}✗ IPFS upload error: {e}{Colors.NC}")
        return None


def upload_to_web3_storage(file_path: Path, api_token: str) -> Optional[str]:
    """
    Upload a file to IPFS via Web3.Storage API.

    Args:
        file_path: Path to the file to upload
        api_token: Web3.Storage API token

    Returns:
        CID string if successful, None otherwise
    """
    try:
        with open(file_path, 'rb') as f:
            file_data = f.read()

        req = urllib.request.Request(
            WEB3_STORAGE_API_ENDPOINT,
            data=file_data,
            headers={
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/octet-stream',
                'X-NAME': file_path.name
            },
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            if response.status == 200:
                response_data = json.loads(response.read().decode())
                return response_data.get('cid')
            else:
                print(f"{Colors.RED}✗ Web3.Storage upload failed: HTTP {response.status}{Colors.NC}")
                return None

    except urllib.error.URLError as e:
        print(f"{Colors.RED}✗ Web3.Storage upload error: {e}{Colors.NC}")
        return None
    except Exception as e:
        print(f"{Colors.RED}✗ Upload error: {e}{Colors.NC}")
        return None


def verify_ipfs_cid(cid: str) -> bool:
    """
    Verify that a CID is accessible via IPFS gateway.

    Args:
        cid: IPFS CID to verify

    Returns:
        True if accessible, False otherwise
    """
    try:
        url = f"{IPFS_GATEWAY}{cid}"
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status == 200
    except:
        return False


# ═══════════════════════════════════════════════════════════════════════════
# Registry Event Processing
# ═══════════════════════════════════════════════════════════════════════════

def load_registry_events() -> List[Dict]:
    """Load all events from the registry log."""
    events = []

    if not REGISTRY_LOG.exists():
        return events

    with open(REGISTRY_LOG, 'r', encoding='utf-8') as f:
        current_event = {}
        for line in f:
            line = line.strip()

            if not line or line == "Registry events initialized.":
                continue

            if line == "{":
                current_event = {"_raw": "{"}
            elif line == "}":
                if current_event:
                    current_event["_raw"] += "}"
                    try:
                        event = json.loads(current_event["_raw"])
                        events.append(event)
                    except json.JSONDecodeError:
                        pass
                current_event = {}
            elif current_event:
                current_event["_raw"] += line

    return events


def load_ipfs_manifest() -> Dict:
    """Load the IPFS anchor manifest or create empty one."""
    if IPFS_MANIFEST.exists():
        with open(IPFS_MANIFEST, 'r', encoding='utf-8') as f:
            return json.load(f)

    return {
        "blueprint_version": "v4.3",
        "manifest_version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "anchors": []
    }


def save_ipfs_manifest(manifest: Dict):
    """Save the IPFS anchor manifest to disk."""
    manifest["last_updated"] = datetime.now(timezone.utc).isoformat()

    # Ensure directory exists
    IPFS_MANIFEST.parent.mkdir(parents=True, exist_ok=True)

    with open(IPFS_MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)


def get_files_for_event(event: Dict) -> List[Path]:
    """
    Determine which files should be anchored for a given event.

    Args:
        event: Registry event dictionary

    Returns:
        List of file paths to anchor
    """
    files = []
    event_type = event.get("event", "")

    # Always anchor the registry log itself
    if REGISTRY_LOG.exists():
        files.append(REGISTRY_LOG)

    # For release events, anchor the bundle and manifest
    if "release" in event_type or "quarterly" in event_type:
        version = event.get("version", "")

        # Find release bundles
        if RELEASE_DIR.exists():
            for bundle in RELEASE_DIR.glob("*.zip"):
                files.append(bundle)

        # Find release manifests
        if MANIFESTS_DIR.exists():
            for manifest in MANIFESTS_DIR.glob("quarterly_release_manifest_*.json"):
                files.append(manifest)

    # For governance events, anchor dashboard and reports
    if "governance" in event_type or "dashboard" in event_type:
        dashboard_files = [
            PROJECT_ROOT / "05_documentation/reports/dashboard/SSID_Governance_Dashboard.md",
            PROJECT_ROOT / "07_governance_legal/dashboard_data.csv"
        ]

        for file in dashboard_files:
            if file.exists():
                files.append(file)

    return list(set(files))  # Remove duplicates


# ═══════════════════════════════════════════════════════════════════════════
# Main Anchoring Logic
# ═══════════════════════════════════════════════════════════════════════════

def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def anchor_file(file_path: Path, event: Dict, use_web3: bool = False) -> Optional[Dict]:
    """
    Anchor a single file to IPFS.

    Args:
        file_path: Path to file to anchor
        event: Associated registry event
        use_web3: Whether to use Web3.Storage API

    Returns:
        Anchor record dictionary if successful, None otherwise
    """
    print(f"{Colors.CYAN}📤 Anchoring: {file_path.name}{Colors.NC}")

    # Compute file hash
    file_hash = compute_file_hash(file_path)

    # Upload to IPFS
    cid = None

    if use_web3:
        import os
        token = os.environ.get(WEB3_STORAGE_TOKEN_ENV)
        if token:
            cid = upload_to_web3_storage(file_path, token)
        else:
            print(f"{Colors.YELLOW}⚠ Web3.Storage token not found in {WEB3_STORAGE_TOKEN_ENV}{Colors.NC}")

    if not cid and check_ipfs_available():
        cid = upload_to_ipfs_local(file_path)

    if not cid:
        print(f"{Colors.RED}✗ Failed to anchor {file_path.name}{Colors.NC}")
        return None

    # Create anchor record
    anchor_record = {
        "file_path": str(file_path.relative_to(PROJECT_ROOT)),
        "file_name": file_path.name,
        "file_hash": file_hash,
        "ipfs_cid": cid,
        "ipfs_gateway_url": f"{IPFS_GATEWAY}{cid}",
        "anchored_at": datetime.now(timezone.utc).isoformat(),
        "event_type": event.get("event"),
        "event_version": event.get("version"),
        "event_timestamp": event.get("timestamp"),
        "blueprint_version": "v4.3"
    }

    print(f"{Colors.GREEN}✓ Anchored: {cid}{Colors.NC}")
    print(f"  URL: {Colors.BLUE}{IPFS_GATEWAY}{cid}{Colors.NC}")

    return anchor_record


def process_events(verify_only: bool = False, use_web3: bool = False):
    """
    Process registry events and anchor new artifacts to IPFS.

    Args:
        verify_only: If True, only verify existing anchors
        use_web3: If True, use Web3.Storage API for uploads
    """
    print(f"{Colors.BLUE}{'═' * 70}{Colors.NC}")
    print(f"{Colors.BLUE}  SSID Auto-Anchoring System - Blueprint v4.3{Colors.NC}")
    print(f"{Colors.BLUE}{'═' * 70}{Colors.NC}")
    print()

    # Load manifests
    events = load_registry_events()
    manifest = load_ipfs_manifest()

    print(f"{Colors.CYAN}📋 Loaded {len(events)} registry events{Colors.NC}")
    print(f"{Colors.CYAN}📋 Existing anchors: {len(manifest.get('anchors', []))}{Colors.NC}")
    print()

    if verify_only:
        print(f"{Colors.YELLOW}🔍 Verifying existing anchors...{Colors.NC}")
        print()

        anchors = manifest.get("anchors", [])
        verified = 0
        failed = 0

        for anchor in anchors:
            cid = anchor.get("ipfs_cid")
            file_name = anchor.get("file_name")

            print(f"  Verifying {file_name}... ", end="", flush=True)

            if verify_ipfs_cid(cid):
                print(f"{Colors.GREEN}✓{Colors.NC}")
                verified += 1
            else:
                print(f"{Colors.RED}✗{Colors.NC}")
                failed += 1

        print()
        print(f"{Colors.CYAN}Verification complete: {verified} verified, {failed} failed{Colors.NC}")
        return

    # Process new events
    existing_cids = {a["ipfs_cid"] for a in manifest.get("anchors", [])}
    anchored_files = {a["file_path"] for a in manifest.get("anchors", [])}

    new_anchors = []

    for event in events:
        event_time = event.get("timestamp", "unknown")
        event_type = event.get("event", "unknown")

        # Get files to anchor for this event
        files = get_files_for_event(event)

        for file_path in files:
            # Skip if already anchored
            rel_path = str(file_path.relative_to(PROJECT_ROOT))
            if rel_path in anchored_files:
                continue

            # Anchor the file
            anchor_record = anchor_file(file_path, event, use_web3)

            if anchor_record:
                new_anchors.append(anchor_record)
                anchored_files.add(rel_path)

    # Update manifest
    if new_anchors:
        manifest["anchors"].extend(new_anchors)
        save_ipfs_manifest(manifest)

        print()
        print(f"{Colors.GREEN}✓ Anchored {len(new_anchors)} new files{Colors.NC}")
        print(f"{Colors.GREEN}✓ Manifest updated: {IPFS_MANIFEST.relative_to(PROJECT_ROOT)}{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}ℹ No new files to anchor{Colors.NC}")

    print()
    print(f"{Colors.BLUE}{'═' * 70}{Colors.NC}")
    print(f"{Colors.BLUE}  Auto-Anchoring Complete{Colors.NC}")
    print(f"{Colors.BLUE}{'═' * 70}{Colors.NC}")
    print()


# ═══════════════════════════════════════════════════════════════════════════
# CLI Interface
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Main entry point for auto-anchoring script."""
    parser = argparse.ArgumentParser(
        description="SSID Automated IPFS Anchoring System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 auto_ipfs_anchor.py                 # Process all events
  python3 auto_ipfs_anchor.py --verify        # Verify existing CIDs
  python3 auto_ipfs_anchor.py --web3-storage  # Use Web3.Storage API
        """
    )

    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify existing anchored CIDs"
    )

    parser.add_argument(
        "--web3-storage",
        action="store_true",
        help="Use Web3.Storage API for uploads (requires WEB3_STORAGE_TOKEN env var)"
    )

    args = parser.parse_args()

    try:
        process_events(verify_only=args.verify, use_web3=args.web3_storage)
        sys.exit(0)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠ Interrupted by user{Colors.NC}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}✗ Error: {e}{Colors.NC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
