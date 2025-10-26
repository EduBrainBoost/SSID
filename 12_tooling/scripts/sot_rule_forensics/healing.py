"""
Layer 20: Error-Tolerance & Self-Healing
========================================

Fallback parsing and self-healing mechanisms
Version: 3.0.0
"""

from typing import List, Tuple, Optional
import subprocess

class ErrorTolerance:
    """Error tolerance and self-healing"""

    def __init__(self):
        self.error_log: List[str] = []
        self.recovery_attempts = 0

    def try_parse_yaml(self, content: str) -> Optional[dict]:
        """Try parsing YAML with fallback"""
        import yaml
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            self.error_log.append(f"YAML parse error: {e}")
            return self._fallback_yaml_parse(content)

    def _fallback_yaml_parse(self, content: str) -> Optional[dict]:
        """Fallback YAML parsing using yq"""
        self.recovery_attempts += 1
        try:
            result = subprocess.run(
                ['yq', 'eval', '-'],
                input=content.encode(),
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                import yaml
                return yaml.safe_load(result.stdout.decode())
        except Exception as e:
            self.error_log.append(f"Fallback parse failed: {e}")

        return None

    def self_heal(self, content: str) -> str:
        """Attempt self-healing of malformed content"""
        # Remove common issues
        healed = content
        healed = healed.replace('\t', '  ')  # Replace tabs with spaces
        healed = healed.strip()
        return healed

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []
        if len(self.error_log) > 100:
            issues.append(f"High error count: {len(self.error_log)}")
        return len(issues) == 0, issues
