"""
Layer 22: Time-Stamped Run-Proof Logging
========================================

parser_run_YYYYMMDD.log with timestamps
Version: 3.0.0
"""

from typing import List, Tuple
from datetime import datetime
from pathlib import Path

class TimeStampedLogger:
    """Time-stamped run-proof logger"""

    def __init__(self, log_dir: Path = Path('.')):
        self.log_dir = log_dir
        self.log_file = self._create_log_file()
        self.entries: List[str] = []

    def _create_log_file(self) -> Path:
        """Create timestamped log file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return self.log_dir / f"parser_run_{timestamp}.log"

    def log(self, message: str, level: str = 'INFO'):
        """Log message with timestamp"""
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] [{level}] {message}"
        self.entries.append(entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(entry + '\n')

    def log_info(self, message: str):
        """Log info message"""
        self.log(message, 'INFO')

    def log_error(self, message: str):
        """Log error message"""
        self.log(message, 'ERROR')

    def log_warning(self, message: str):
        """Log warning message"""
        self.log(message, 'WARNING')

    def self_verify(self) -> Tuple[bool, List[str]]:
        """Self-verification"""
        issues = []
        if not self.log_file.exists():
            issues.append("Log file not created")
        return len(issues) == 0, issues
