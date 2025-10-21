#!/usr/bin/env python3
"""
Self-Healing Suggestion Engine
===============================

Generates AI-powered remediation suggestions for failed SoT validation rules.

Features:
- LLM-powered suggestions (Claude/GPT-4)
- JSON Patch generation (RFC 6902)
- CLI command generation (yq/jq/sed)
- Fallback to rule-based suggestions
- Confidence scoring

Version: 1.0.0
Date: 2025-10-17
Author: SSID AI/ML Team
"""

import json
import os
import sys
import hashlib
from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml

# Try to import requests for LLM API calls
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: 'requests' library not available. LLM features will be limited.")


class SelfHealingEngine:
    """Generate AI-powered or rule-based remediation suggestions for failed rules"""

    def __init__(
        self,
        llm_provider: str = "claude",
        api_key: Optional[str] = None,
        use_fallback: bool = True
    ):
        """
        Initialize Self-Healing Engine

        Args:
            llm_provider: "claude" or "gpt4"
            api_key: API key for LLM provider (or use env var)
            use_fallback: Use rule-based fallback if LLM unavailable
        """
        self.llm_provider = llm_provider
        self.use_fallback = use_fallback

        # Load API key
        if llm_provider == "claude":
            self.api_key = api_key or os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        elif llm_provider == "gpt4":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        else:
            self.api_key = None

        # Load prompt template
        self.prompt_template = self._load_prompt_template()

        # Cache for suggestions (avoid redundant LLM calls)
        self.suggestion_cache: Dict[str, Dict[str, Any]] = {}

    def _load_prompt_template(self) -> Dict[str, Any]:
        """Load prompt template from YAML"""
        prompt_path = Path(__file__).parent.parent.parent / "16_codex" / "prompts" / "ai_remediation_suggestion_example.yaml"

        if not prompt_path.exists():
            print(f"Warning: Prompt template not found at {prompt_path}")
            return {}

        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Failed to load prompt template: {e}")
            return {}

    def generate_suggestion(
        self,
        rule_id: str,
        rule_name: str,
        priority: str,
        scientific_foundation: str,
        current_data: Dict[str, Any],
        failure_message: str,
        expected_behavior: str,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Generate remediation suggestion using LLM or fallback

        Args:
            rule_id: Rule ID (e.g., "SOT-018")
            rule_name: Human-readable rule name
            priority: "must", "should", or "have"
            scientific_foundation: Regulatory/standard reference
            current_data: Current configuration data
            failure_message: Error message from validator
            expected_behavior: What the rule expects

        Returns:
            {
                "patch": [...],  # JSON Patch operations
                "cli_command": "yq -i ...",
                "explanation": "...",
                "effort": "30 seconds",
                "confidence": 0.95,
                "method": "llm" or "fallback"
            }
        """

        # Check cache
        cache_key = self._generate_cache_key(rule_id, current_data)
        if use_cache and cache_key in self.suggestion_cache:
            return self.suggestion_cache[cache_key]

        # Try LLM first
        if self.api_key and REQUESTS_AVAILABLE:
            try:
                suggestion = self._generate_llm_suggestion(
                    rule_id, rule_name, priority, scientific_foundation,
                    current_data, failure_message, expected_behavior
                )
                suggestion["method"] = "llm"

                # Cache result
                self.suggestion_cache[cache_key] = suggestion
                return suggestion

            except Exception as e:
                print(f"Warning: LLM suggestion failed: {e}")
                if not self.use_fallback:
                    raise

        # Fallback to rule-based suggestions
        if self.use_fallback:
            suggestion = self._generate_fallback_suggestion(
                rule_id, rule_name, priority, current_data,
                failure_message, expected_behavior
            )
            suggestion["method"] = "fallback"

            # Cache result
            self.suggestion_cache[cache_key] = suggestion
            return suggestion

        raise Exception("LLM unavailable and fallback disabled")

    def _generate_cache_key(self, rule_id: str, current_data: Dict[str, Any]) -> str:
        """Generate cache key from rule_id and data hash"""
        data_str = json.dumps(current_data, sort_keys=True)
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()[:8]
        return f"{rule_id}_{data_hash}"

    def _generate_llm_suggestion(
        self,
        rule_id: str,
        rule_name: str,
        priority: str,
        scientific_foundation: str,
        current_data: Dict[str, Any],
        failure_message: str,
        expected_behavior: str
    ) -> Dict[str, Any]:
        """Generate suggestion using LLM API"""

        if not self.prompt_template:
            raise Exception("Prompt template not loaded")

        # Construct prompt
        user_prompt = self.prompt_template["user_prompt_template"].format(
            rule_id=rule_id,
            rule_name=rule_name,
            priority=priority,
            scientific_foundation=scientific_foundation,
            current_data=yaml.dump(current_data, default_flow_style=False),
            failure_message=failure_message,
            expected_behavior=expected_behavior
        )

        # Call LLM API
        if self.llm_provider == "claude":
            return self._call_claude_api(user_prompt)
        elif self.llm_provider == "gpt4":
            return self._call_openai_api(user_prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

    def _call_claude_api(self, user_prompt: str) -> Dict[str, Any]:
        """Call Claude API for structured output"""

        if not REQUESTS_AVAILABLE:
            raise Exception("'requests' library not available")

        system_prompt = self.prompt_template.get("system_prompt", "")
        llm_config = self.prompt_template.get("llm_config", {})

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": llm_config.get("model", "claude-3-5-sonnet-20241022"),
                "max_tokens": llm_config.get("max_tokens", 1024),
                "temperature": llm_config.get("temperature", 0.1),
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            },
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"Claude API error: {response.status_code} - {response.text}")

        result = response.json()
        content = result["content"][0]["text"]

        # Parse JSON from response (strip markdown if present)
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        return json.loads(content)

    def _call_openai_api(self, user_prompt: str) -> Dict[str, Any]:
        """Call OpenAI GPT-4 API for structured output"""

        if not REQUESTS_AVAILABLE:
            raise Exception("'requests' library not available")

        system_prompt = self.prompt_template.get("system_prompt", "")
        llm_config = self.prompt_template.get("llm_config", {})

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": llm_config.get("fallback_model", "gpt-4"),
                "max_tokens": llm_config.get("max_tokens", 1024),
                "temperature": llm_config.get("temperature", 0.1),
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "response_format": {"type": "json_object"}
            },
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        return json.loads(content)

    def _generate_fallback_suggestion(
        self,
        rule_id: str,
        rule_name: str,
        priority: str,
        current_data: Dict[str, Any],
        failure_message: str,
        expected_behavior: str
    ) -> Dict[str, Any]:
        """Generate rule-based suggestion (no LLM)"""

        # Hardcoded suggestions for common rules
        FALLBACK_SUGGESTIONS = {
            "SOT-018": {
                "patch": [{"op": "replace", "path": "/yaml_block_marker", "value": "```yaml"}],
                "cli_command": 'yq -i \'.yaml_block_marker = "```yaml"\' config.yaml',
                "explanation": "YAML block markers should use '```yaml' not '```yml' for consistency per SOT-018 specification.",
                "effort": "10 seconds",
                "confidence": 0.95
            },
            "SOT-019": {
                "patch": [{"op": "replace", "path": "/version_badge", "value": "![Version](https://img.shields.io/badge/version-3.2.0-blue)"}],
                "cli_command": 'yq -i \'.version_badge = "![Version](https://img.shields.io/badge/version-3.2.0-blue)"\' config.yaml',
                "explanation": "Version badges should follow shields.io format for consistency per SOT-019 specification.",
                "effort": "30 seconds",
                "confidence": 0.90
            },
            "SOT-025": {
                "patch": [{"op": "add", "path": "/instances/0/business_priority", "value": "medium"}],
                "cli_command": 'yq -i \'.instances[0].business_priority = "medium"\' config.yaml',
                "explanation": "Adding business_priority field with default 'medium' value. Adjust to 'high' or 'low' based on business criticality.",
                "effort": "30 seconds",
                "confidence": 0.85
            },
            "SOT-030": {
                "patch": [{"op": "add", "path": "/deprecated_list/0/business_priority", "value": "low"}],
                "cli_command": 'yq -i \'.deprecated_list[0].business_priority = "low"\' config.yaml',
                "explanation": "Deprecated items typically have low business priority. Adjust if needed.",
                "effort": "30 seconds",
                "confidence": 0.80
            }
        }

        # Check if we have a hardcoded suggestion
        if rule_id in FALLBACK_SUGGESTIONS:
            return FALLBACK_SUGGESTIONS[rule_id]

        # Generic suggestion based on priority
        if priority == "should":
            return {
                "patch": [],
                "cli_command": f"# Manual fix required for {rule_id}",
                "explanation": f"Review {rule_name} documentation and apply fix manually. Expected: {expected_behavior}",
                "effort": "5 minutes",
                "confidence": 0.50
            }
        else:  # have
            return {
                "patch": [],
                "cli_command": f"# Optional: {rule_id}",
                "explanation": f"{rule_name} is optional (HAVE priority). Consider implementing if needed: {expected_behavior}",
                "effort": "5 minutes",
                "confidence": 0.30
            }

    def apply_patch(
        self,
        file_path: str,
        patch: List[Dict[str, Any]],
        dry_run: bool = False
    ) -> bool:
        """
        Apply JSON Patch to YAML file

        Args:
            file_path: Path to YAML file
            patch: JSON Patch operations
            dry_run: If True, don't write changes

        Returns:
            True if successful
        """
        try:
            import jsonpatch
        except ImportError:
            print("Error: 'jsonpatch' library not available. Install with: pip install jsonpatch")
            return False

        # Load file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # Apply patch
        try:
            patched_data = jsonpatch.apply_patch(data, patch)
        except jsonpatch.JsonPatchException as e:
            print(f"Error applying patch: {e}")
            return False

        if dry_run:
            print("Dry run - changes not written")
            return True

        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(patched_data, f, default_flow_style=False, sort_keys=False)

        return True


def main():
    """CLI test for Self-Healing Engine"""
    import argparse

    parser = argparse.ArgumentParser(description="Self-Healing Suggestion Engine Test")
    parser.add_argument("--rule-id", required=True, help="Rule ID (e.g., SOT-018)")
    parser.add_argument("--provider", default="claude", choices=["claude", "gpt4"], help="LLM provider")
    parser.add_argument("--api-key", help="API key (or use env var)")
    parser.add_argument("--fallback-only", action="store_true", help="Use fallback only (no LLM)")

    args = parser.parse_args()

    # Initialize engine
    if args.fallback_only:
        engine = SelfHealingEngine(use_fallback=True)
        engine.api_key = None  # Force fallback
    else:
        engine = SelfHealingEngine(llm_provider=args.provider, api_key=args.api_key)

    # Test data
    test_data = {
        "version": "3.2.0",
        "yaml_block_marker": "```yml",  # Wrong - should be ```yaml
        "instances": [
            {"name": "test", "path": "/test", "deprecated": False}
        ]
    }

    # Generate suggestion
    suggestion = engine.generate_suggestion(
        rule_id=args.rule_id,
        rule_name="YAML Block Marker Validation",
        priority="should",
        scientific_foundation="IEEE 829-2008 Documentation Standards",
        current_data=test_data,
        failure_message=f"[{args.rule_id}] FAIL: Invalid YAML marker",
        expected_behavior="Use ```yaml not ```yml"
    )

    # Print result
    print("\n" + "="*70)
    print(f"Self-Healing Suggestion for {args.rule_id}")
    print("="*70)
    print(f"\nMethod: {suggestion.get('method', 'unknown').upper()}")
    print(f"Confidence: {suggestion.get('confidence', 0):.0%}")
    print(f"Effort: {suggestion.get('effort', 'unknown')}")
    print(f"\nExplanation:")
    print(f"  {suggestion.get('explanation', 'N/A')}")
    print(f"\nCLI Command:")
    print(f"  {suggestion.get('cli_command', 'N/A')}")
    print(f"\nJSON Patch:")
    print(f"  {json.dumps(suggestion.get('patch', []), indent=2)}")
    print("="*70)


if __name__ == "__main__":
    main()
