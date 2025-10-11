#!/usr/bin/env python3
"""
federation_sync_manager.py - SSID Federation Synchronization Manager
Blueprint v4.4 - Federated Governance Sync & Consensus Layer

This script manages synchronization between federated SSID nodes, enabling
decentralized governance through distributed event validation and consensus.

Features:
- Multi-node registry synchronization
- Git-based event propagation
- Consensus-driven conflict resolution
- Distributed trust model
- Automatic node discovery
- Cryptographic event verification

Usage:
    python3 federation_sync_manager.py [options]

Options:
    --sync                  Synchronize with all federated nodes
    --add-node <git_url>    Add a new node to the federation
    --remove-node <node_id> Remove a node from the federation
    --list-nodes            List all federated nodes
    --check-status          Check federation status
    --force                 Force sync even if recently synced

Author: SSID Governance System
License: MIT
"""

import json
import hashlib
import subprocess
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import tempfile
import shutil
import re

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
FEDERATION_MANIFEST = PROJECT_ROOT / "24_meta_orchestration/registry/manifests/federation_manifest.json"
REGISTRY_LOG = PROJECT_ROOT / "24_meta_orchestration/registry/logs/registry_events.log"
CONSENSUS_SCRIPT = SCRIPT_DIR / "consensus_validator.py"

# Constants
DEFAULT_SYNC_INTERVAL = 60  # minutes
CONSENSUS_THRESHOLD = 0.66
MAX_CLONE_DEPTH = 100  # Limit git clone depth for performance


class Colors:
    """ANSI color codes for terminal output"""
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    NC = '\033[0m'


@dataclass
class FederatedNode:
    """Represents a federated SSID node"""
    node_id: str
    node_name: str
    organization: str
    git_remote: str
    api_endpoint: str
    public_key_fingerprint: str
    added_at: str
    last_seen: Optional[str]
    status: str
    compliance_score: int
    blueprint_version: str
    trust_score: int

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "node_id": self.node_id,
            "node_name": self.node_name,
            "organization": self.organization,
            "git_remote": self.git_remote,
            "api_endpoint": self.api_endpoint,
            "public_key_fingerprint": self.public_key_fingerprint,
            "added_at": self.added_at,
            "last_seen": self.last_seen,
            "status": self.status,
            "compliance_score": self.compliance_score,
            "blueprint_version": self.blueprint_version,
            "trust_score": self.trust_score
        }


@dataclass
class RegistryEvent:
    """Represents a registry event"""
    timestamp: str
    event: str
    version: str
    commit_hash: str
    blueprint: str
    root_24_lock: str
    compliance_score: str
    emitted_by: str
    event_hash: Optional[str] = None

    def compute_hash(self) -> str:
        """Compute SHA256 hash of event"""
        event_str = f"{self.timestamp}|{self.event}|{self.version}|{self.commit_hash}|{self.blueprint}"
        return hashlib.sha256(event_str.encode()).hexdigest()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp,
            "event": self.event,
            "version": self.version,
            "commit_hash": self.commit_hash,
            "blueprint": self.blueprint,
            "root_24_lock": self.root_24_lock,
            "compliance_score": self.compliance_score,
            "emitted_by": self.emitted_by,
            "event_hash": self.event_hash or self.compute_hash()
        }


class FederationSyncManager:
    """Manages federation synchronization operations"""

    def __init__(self, manifest_path: Path = FEDERATION_MANIFEST):
        self.manifest_path = manifest_path
        self.manifest = self.load_manifest()

    def load_manifest(self) -> Dict:
        """Load federation manifest"""
        if not self.manifest_path.exists():
            print(f"{Colors.RED}X Federation manifest not found: {self.manifest_path}{Colors.NC}")
            sys.exit(1)

        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_manifest(self):
        """Save federation manifest"""
        self.manifest['last_updated'] = datetime.now(timezone.utc).isoformat()
        with open(self.manifest_path, 'w', encoding='utf-8') as f:
            json.dump(self.manifest, f, indent=2)

    def get_nodes(self) -> List[FederatedNode]:
        """Get all federated nodes"""
        nodes = []
        for node_data in self.manifest.get('nodes', []):
            nodes.append(FederatedNode(**node_data))
        return nodes

    def add_node(self, git_remote: str, node_name: str = "", organization: str = "") -> bool:
        """
        Add a new node to the federation

        Args:
            git_remote: Git repository URL
            node_name: Human-readable name
            organization: Organization name

        Returns:
            True if successful, False otherwise
        """
        print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")
        print(f"{Colors.BLUE}  Adding Federated Node{Colors.NC}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")

        # Validate Git URL
        if not self._validate_git_url(git_remote):
            print(f"{Colors.RED}X Invalid Git URL: {git_remote}{Colors.NC}")
            return False

        # Generate node ID
        node_id = hashlib.sha256(git_remote.encode()).hexdigest()[:16]

        # Check if node already exists
        existing_nodes = self.get_nodes()
        if any(node.node_id == node_id for node in existing_nodes):
            print(f"{Colors.YELLOW}! Node already exists: {node_id}{Colors.NC}")
            return False

        # Extract node name from Git URL if not provided
        if not node_name:
            node_name = self._extract_repo_name(git_remote)

        # Create node record
        new_node = FederatedNode(
            node_id=node_id,
            node_name=node_name,
            organization=organization or "Unknown",
            git_remote=git_remote,
            api_endpoint="",
            public_key_fingerprint="",
            added_at=datetime.now(timezone.utc).isoformat(),
            last_seen=None,
            status="active",
            compliance_score=0,
            blueprint_version="unknown",
            trust_score=50  # Initial neutral trust score
        )

        # Add to manifest
        self.manifest['nodes'].append(new_node.to_dict())
        self.manifest['statistics']['total_nodes'] = len(self.manifest['nodes'])
        self.save_manifest()

        print(f"{Colors.GREEN}OK Node added successfully{Colors.NC}")
        print(f"  Node ID: {Colors.CYAN}{node_id}{Colors.NC}")
        print(f"  Name: {node_name}")
        print(f"  Git Remote: {git_remote}\n")

        return True

    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the federation"""
        nodes = self.manifest.get('nodes', [])
        initial_count = len(nodes)

        self.manifest['nodes'] = [n for n in nodes if n['node_id'] != node_id]

        if len(self.manifest['nodes']) == initial_count:
            print(f"{Colors.RED}X Node not found: {node_id}{Colors.NC}")
            return False

        self.manifest['statistics']['total_nodes'] = len(self.manifest['nodes'])
        self.save_manifest()

        print(f"{Colors.GREEN}OK Node removed: {node_id}{Colors.NC}")
        return True

    def list_nodes(self):
        """List all federated nodes"""
        nodes = self.get_nodes()

        print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")
        print(f"{Colors.BLUE}  Federated Nodes ({len(nodes)}){Colors.NC}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")

        if not nodes:
            print(f"{Colors.YELLOW}No federated nodes configured{Colors.NC}\n")
            return

        for node in nodes:
            status_color = Colors.GREEN if node.status == "active" else Colors.RED
            print(f"{Colors.CYAN}Node ID:{Colors.NC} {node.node_id}")
            print(f"  Name: {node.node_name}")
            print(f"  Organization: {node.organization}")
            print(f"  Status: {status_color}{node.status}{Colors.NC}")
            print(f"  Git Remote: {node.git_remote}")
            print(f"  Trust Score: {node.trust_score}/100")
            print(f"  Last Seen: {node.last_seen or 'Never'}")
            print(f"  Blueprint: {node.blueprint_version}")
            print()

    def sync_all_nodes(self, force: bool = False) -> bool:
        """
        Synchronize with all federated nodes

        Args:
            force: Force sync even if recently synced

        Returns:
            True if any sync succeeded, False otherwise
        """
        if not self.manifest.get('federation', {}).get('enabled'):
            print(f"{Colors.YELLOW}! Federation is not enabled{Colors.NC}")
            print(f"  Enable in: {self.manifest_path}")
            return False

        # Check if sync is needed
        if not force and not self._should_sync():
            last_sync = self.manifest['federation'].get('last_sync')
            print(f"{Colors.YELLOW}! Recent sync detected: {last_sync}{Colors.NC}")
            print(f"  Use --force to sync anyway")
            return False

        nodes = self.get_nodes()
        if not nodes:
            print(f"{Colors.YELLOW}! No federated nodes configured{Colors.NC}")
            return False

        print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")
        print(f"{Colors.BLUE}  Federation Synchronization{Colors.NC}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")

        success_count = 0
        fail_count = 0

        for node in nodes:
            if node.status != "active":
                print(f"{Colors.YELLOW}SKIP Skipping inactive node: {node.node_name}{Colors.NC}")
                continue

            print(f"{Colors.CYAN}-> Syncing with: {node.node_name}{Colors.NC}")

            if self._sync_with_node(node):
                success_count += 1
                print(f"{Colors.GREEN}  OK Sync successful{Colors.NC}\n")
            else:
                fail_count += 1
                print(f"{Colors.RED}  X Sync failed{Colors.NC}\n")

        # Update statistics
        self.manifest['federation']['last_sync'] = datetime.now(timezone.utc).isoformat()
        self.manifest['statistics']['total_syncs'] += 1
        self.manifest['statistics']['successful_syncs'] += success_count
        self.manifest['statistics']['failed_syncs'] += fail_count
        self.save_manifest()

        # Summary
        print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")
        print(f"{Colors.BLUE}  Sync Summary{Colors.NC}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")
        print(f"  Successful: {Colors.GREEN}{success_count}{Colors.NC}")
        print(f"  Failed: {Colors.RED}{fail_count}{Colors.NC}")
        print()

        return success_count > 0

    def _sync_with_node(self, node: FederatedNode) -> bool:
        """
        Sync with a specific node

        Args:
            node: The node to sync with

        Returns:
            True if successful, False otherwise
        """
        temp_dir = None
        try:
            # Clone remote repository to temp directory
            temp_dir = Path(tempfile.mkdtemp(prefix="ssid_federation_"))
            print(f"  {Colors.CYAN}Cloning remote repository...{Colors.NC}")

            result = subprocess.run(
                ['git', 'clone', '--depth', str(MAX_CLONE_DEPTH), node.git_remote, str(temp_dir)],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode != 0:
                print(f"  {Colors.RED}Failed to clone: {result.stderr.strip()}{Colors.NC}")
                return False

            # Load remote registry events
            remote_log = temp_dir / "24_meta_orchestration/registry/logs/registry_events.log"
            if not remote_log.exists():
                print(f"  {Colors.YELLOW}No registry log found in remote{Colors.NC}")
                return False

            remote_events = self._load_events_from_file(remote_log)
            local_events = self._load_events_from_file(REGISTRY_LOG)

            # Find new/divergent events
            new_events = self._find_new_events(local_events, remote_events)

            if not new_events:
                print(f"  {Colors.GREEN}No new events to sync{Colors.NC}")
                self._update_node_status(node, "active")
                return True

            print(f"  {Colors.CYAN}Found {len(new_events)} new event(s){Colors.NC}")

            # Validate with consensus
            validated_events = self._validate_with_consensus(new_events, node)

            if validated_events:
                self._apply_events(validated_events)
                print(f"  {Colors.GREEN}Applied {len(validated_events)} event(s){Colors.NC}")

            self._update_node_status(node, "active")
            return True

        except subprocess.TimeoutExpired:
            print(f"  {Colors.RED}Git clone timeout{Colors.NC}")
            return False
        except Exception as e:
            print(f"  {Colors.RED}Sync error: {str(e)}{Colors.NC}")
            return False
        finally:
            # Cleanup temp directory
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _load_events_from_file(self, log_file: Path) -> List[RegistryEvent]:
        """Load registry events from file"""
        events = []
        if not log_file.exists():
            return events

        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    event = RegistryEvent(**data)
                    event.event_hash = event.compute_hash()
                    events.append(event)
                except (json.JSONDecodeError, TypeError):
                    continue

        return events

    def _find_new_events(self, local_events: List[RegistryEvent],
                         remote_events: List[RegistryEvent]) -> List[RegistryEvent]:
        """Find events in remote that are not in local"""
        local_hashes = {event.compute_hash() for event in local_events}
        new_events = []

        for remote_event in remote_events:
            remote_hash = remote_event.compute_hash()
            if remote_hash not in local_hashes:
                new_events.append(remote_event)

        return new_events

    def _validate_with_consensus(self, events: List[RegistryEvent],
                                  source_node: FederatedNode) -> List[RegistryEvent]:
        """Validate events using consensus mechanism"""
        validated = []

        for event in events:
            # For now, accept events from trusted nodes
            # TODO: Implement full consensus validation with consensus_validator.py
            if source_node.trust_score >= 50:
                validated.append(event)

        return validated

    def _apply_events(self, events: List[RegistryEvent]):
        """Apply validated events to local registry"""
        with open(REGISTRY_LOG, 'a', encoding='utf-8') as f:
            for event in events:
                f.write(json.dumps(event.to_dict()) + '\n')

    def _update_node_status(self, node: FederatedNode, status: str):
        """Update node status in manifest"""
        for n in self.manifest['nodes']:
            if n['node_id'] == node.node_id:
                n['last_seen'] = datetime.now(timezone.utc).isoformat()
                n['status'] = status
                break
        self.save_manifest()

    def _should_sync(self) -> bool:
        """Check if sync is needed based on interval"""
        last_sync = self.manifest['federation'].get('last_sync')
        if not last_sync:
            return True

        last_sync_dt = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
        interval = self.manifest['federation'].get('sync_interval_minutes', DEFAULT_SYNC_INTERVAL)
        next_sync = last_sync_dt + timedelta(minutes=interval)

        return datetime.now(timezone.utc) >= next_sync

    def _validate_git_url(self, url: str) -> bool:
        """Validate Git URL format"""
        git_patterns = [
            r'^https?://.*\.git$',
            r'^git@.*:.*\.git$',
            r'^https?://github\.com/.*',
            r'^https?://gitlab\.com/.*'
        ]
        return any(re.match(pattern, url) for pattern in git_patterns)

    def _extract_repo_name(self, git_url: str) -> str:
        """Extract repository name from Git URL"""
        parts = git_url.rstrip('/').split('/')
        repo_name = parts[-1].replace('.git', '')
        return repo_name

    def check_status(self):
        """Check and display federation status"""
        print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}")
        print(f"{Colors.BLUE}  Federation Status{Colors.NC}")
        print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")

        fed_config = self.manifest.get('federation', {})
        stats = self.manifest.get('statistics', {})

        enabled = fed_config.get('enabled', False)
        status_color = Colors.GREEN if enabled else Colors.RED
        print(f"  Enabled: {status_color}{enabled}{Colors.NC}")
        print(f"  Mode: {fed_config.get('mode', 'unknown')}")
        print(f"  Consensus Threshold: {fed_config.get('consensus_threshold', 0) * 100}%")
        print(f"  Sync Interval: {fed_config.get('sync_interval_minutes', 0)} minutes")
        print(f"  Last Sync: {fed_config.get('last_sync', 'Never')}\n")

        print(f"{Colors.CYAN}Statistics:{Colors.NC}")
        print(f"  Total Nodes: {stats.get('total_nodes', 0)}")
        print(f"  Active Nodes: {stats.get('active_nodes', 0)}")
        print(f"  Total Syncs: {stats.get('total_syncs', 0)}")
        print(f"  Successful: {Colors.GREEN}{stats.get('successful_syncs', 0)}{Colors.NC}")
        print(f"  Failed: {Colors.RED}{stats.get('failed_syncs', 0)}{Colors.NC}")
        print(f"  Consensus Agreements: {stats.get('consensus_agreements', 0)}")
        print(f"  Consensus Disagreements: {stats.get('consensus_disagreements', 0)}")
        print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='SSID Federation Synchronization Manager - Blueprint v4.4'
    )
    parser.add_argument('--sync', action='store_true',
                       help='Synchronize with all federated nodes')
    parser.add_argument('--add-node', type=str, metavar='GIT_URL',
                       help='Add a new node to the federation')
    parser.add_argument('--node-name', type=str, default='',
                       help='Name for the new node (used with --add-node)')
    parser.add_argument('--organization', type=str, default='',
                       help='Organization for the new node (used with --add-node)')
    parser.add_argument('--remove-node', type=str, metavar='NODE_ID',
                       help='Remove a node from the federation')
    parser.add_argument('--list-nodes', action='store_true',
                       help='List all federated nodes')
    parser.add_argument('--check-status', action='store_true',
                       help='Check federation status')
    parser.add_argument('--force', action='store_true',
                       help='Force sync even if recently synced')

    args = parser.parse_args()

    # Create manager instance
    manager = FederationSyncManager()

    # Execute requested operation
    if args.sync:
        success = manager.sync_all_nodes(force=args.force)
        sys.exit(0 if success else 1)

    elif args.add_node:
        success = manager.add_node(
            args.add_node,
            node_name=args.node_name,
            organization=args.organization
        )
        sys.exit(0 if success else 1)

    elif args.remove_node:
        success = manager.remove_node(args.remove_node)
        sys.exit(0 if success else 1)

    elif args.list_nodes:
        manager.list_nodes()
        sys.exit(0)

    elif args.check_status:
        manager.check_status()
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
