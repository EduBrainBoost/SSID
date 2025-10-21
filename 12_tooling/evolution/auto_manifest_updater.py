#!/usr/bin/env python3
"""
Auto Manifest Updater
======================

Automatically updates artifact_intent_manifest.yaml with detected changes
from Intent Evolution Guard.

Features:
- Reads intent_evolution_history.json
- Generates YAML entries for new intents
- Updates existing intents with new versions
- Preserves manual edits
- Creates backups before updates

Copyright (c) 2025 SSID Project
"""

import json
import yaml
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List


class AutoManifestUpdater:
    """Automatically updates the intent manifest from evolution history."""

    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.manifest_path = self.repo_root / "24_meta_orchestration/registry/artifact_intent_manifest.yaml"
        self.history_path = self.repo_root / "24_meta_orchestration/registry/intent_evolution_history.json"
        self.backup_dir = self.repo_root / "24_meta_orchestration/registry/backups"

    def load_history(self) -> Dict:
        """Load intent evolution history."""
        if not self.history_path.exists():
            return {}

        with open(self.history_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_manifest(self) -> Dict:
        """Load current manifest."""
        if not self.manifest_path.exists():
            return self._create_empty_manifest()

        with open(self.manifest_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def _create_empty_manifest(self) -> Dict:
        """Create empty manifest structure."""
        return {
            "title": "SSID Artifact Intent Manifest",
            "description": "Auto-managed intent coverage manifest",
            "version": 3,
            "schema": "https://schema.ssid/intents/v3",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "subscriptions": {"required": []},
            "roadmaps": {"required": []},
            "indexes": {"required": []},
            "reports": {"required": []},
            "policies": {"required": []},
            "workflows": {"required": []},
            "tests": {"required": []},
            "intents": [],
            "metadata": {}
        }

    def backup_manifest(self):
        """Create backup of current manifest."""
        if not self.manifest_path.exists():
            return

        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"artifact_intent_manifest_backup_{timestamp}.yaml"

        shutil.copy2(self.manifest_path, backup_path)
        print(f"Backup created: {backup_path}")

    def sync_intents(self):
        """Sync intent history to manifest."""
        history = self.load_history()
        manifest = self.load_manifest()

        if "intents" not in manifest:
            manifest["intents"] = []

        # Build map of existing intents by path
        existing_intents = {
            intent["path"]: intent
            for intent in manifest.get("intents", [])
            if "path" in intent
        }

        updated_count = 0
        added_count = 0

        for path, data in history.items():
            if path in existing_intents:
                # Update existing intent
                intent = existing_intents[path]
                latest_version = data["versions"][-1]

                intent["version"] = latest_version["version"]
                intent["last_updated"] = latest_version["date"]
                intent["hash"] = latest_version["hash"]

                if latest_version.get("deprecated"):
                    intent["required"] = False
                    intent["deprecated"] = True

                updated_count += 1
            else:
                # Add new intent
                latest_version = data["versions"][-1]

                new_intent = {
                    "id": data["intent_id"],
                    "name": self._generate_name(path),
                    "owner": self._determine_owner(data["layer"], data["category"]),
                    "root": data["layer"] or "meta",
                    "path": path,
                    "required": data.get("is_required", False),
                    "version": latest_version["version"],
                    "last_updated": latest_version["date"],
                    "hash": latest_version["hash"],
                    "check": self._generate_check(path, data["category"]),
                    "tags": self._generate_tags(data["layer"], data["category"])
                }

                if latest_version.get("deprecated"):
                    new_intent["deprecated"] = True

                manifest["intents"].append(new_intent)
                added_count += 1

        # Update metadata
        manifest["metadata"]["total_intents"] = len(manifest["intents"])
        manifest["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        manifest["metadata"]["auto_sync_enabled"] = True

        print(f"Updated {updated_count} intents, added {added_count} new intents")

        return manifest

    def _generate_name(self, path: str) -> str:
        """Generate human-readable name from path."""
        filename = Path(path).stem
        # Convert snake_case to Title Case
        return filename.replace("_", " ").title()

    def _determine_owner(self, layer: str, category: str) -> str:
        """Determine owner based on layer and category."""
        owner_map = {
            "01_ai_layer": "ai-team",
            "02_audit_logging": "audit-team",
            "03_core": "platform-team",
            "08_identity_score": "identity-team",
            "09_meta_identity": "identity-team",
            "11_test_simulation": "qa",
            "12_tooling": "dev-tools",
            "14_zero_time_auth": "auth-team",
            "23_compliance": "compliance",
            "24_meta_orchestration": "governance-core"
        }

        return owner_map.get(layer, "platform-team")

    def _generate_check(self, path: str, category: str) -> Dict:
        """Generate check configuration based on file type."""
        ext = Path(path).suffix

        if ext == ".rego":
            return {"type": "rego_presence"}
        elif ext == ".py":
            return {"type": "python_presence"}
        elif ext in [".yaml", ".yml"]:
            return {"type": "yaml_presence", "keys_required": []}
        elif ext == ".json":
            return {"type": "json_presence", "keys_required": []}
        else:
            return {"type": "file_presence"}

    def _generate_tags(self, layer: str, category: str) -> List[str]:
        """Generate tags for an intent."""
        tags = []

        if layer:
            tags.append(f"layer-{layer.split('_')[0]}")

        tags.append(category)
        tags.append("auto-generated")

        return tags

    def save_manifest(self, manifest: Dict):
        """Save updated manifest."""
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

        print(f"Manifest updated: {self.manifest_path}")

    def run(self, create_backup: bool = True):
        """Run full sync process."""
        if create_backup:
            self.backup_manifest()

        manifest = self.sync_intents()
        self.save_manifest(manifest)

        return manifest


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Auto Manifest Updater")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup")
    parser.add_argument("--repo-root", default=".", help="Repository root")

    args = parser.parse_args()

    updater = AutoManifestUpdater(repo_root=args.repo_root)
    updater.run(create_backup=not args.no_backup)


if __name__ == "__main__":
    main()
