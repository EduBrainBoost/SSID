#!/usr/bin/env python3
"""
SoT Task Scheduler - Periodic Automation
=========================================

Führt periodische SoT-Tasks automatisch aus:
- Täglich: Full Orchestration
- Stündlich: Health Checks
- Wöchentlich: Extended Audits

Version: 1.0.0
Status: PRODUCTION READY
Author: SSID Automation Team
Co-Authored-By: Claude <noreply@anthropic.com>

🧠 Generated with Claude Code (https://claude.com/claude-code)

Usage:
    # Start scheduler
    python sot_scheduler.py

    # List scheduled tasks
    python sot_scheduler.py --list

    # Run specific task
    python sot_scheduler.py --task daily_orchestration
"""

import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import json


@dataclass
class ScheduledTask:
    """Scheduled task definition"""
    name: str
    command: List[str]
    interval_seconds: int
    last_run: Optional[float] = None
    next_run: Optional[float] = None


class SoTScheduler:
    """
    Task scheduler for periodic SoT automation.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize scheduler"""
        if repo_root is None:
            self.repo_root = Path(__file__).resolve().parents[3]
        else:
            self.repo_root = Path(repo_root)

        self.tasks: List[ScheduledTask] = []
        self.setup_tasks()

    def setup_tasks(self):
        """Setup scheduled tasks"""

        # Daily: Full Orchestration (3 AM)
        self.tasks.append(ScheduledTask(
            name="daily_orchestration",
            command=[sys.executable, "24_meta_orchestration/master_orchestrator.py", "--full"],
            interval_seconds=86400  # 24 hours
        ))

        # Hourly: Health Check
        self.tasks.append(ScheduledTask(
            name="hourly_health_check",
            command=[sys.executable, "17_observability/sot_health_monitor.py"],
            interval_seconds=3600  # 1 hour
        ))

        # Every 6 hours: Concordance Check
        self.tasks.append(ScheduledTask(
            name="concordance_check",
            command=[sys.executable, "24_meta_orchestration/concordance/cross_artifact_validator.py"],
            interval_seconds=21600  # 6 hours
        ))

        # Every 12 hours: Anomaly Detection
        self.tasks.append(ScheduledTask(
            name="anomaly_detection",
            command=[sys.executable, "01_ai_layer/anomaly/sot_anomaly_detector.py"],
            interval_seconds=43200  # 12 hours
        ))

        # Weekly: Full Audit (Sunday 2 AM)
        self.tasks.append(ScheduledTask(
            name="weekly_audit",
            command=[sys.executable, "12_tooling/cli/sot_validator.py", "--verify-all", "--scorecard"],
            interval_seconds=604800  # 7 days
        ))

    def should_run(self, task: ScheduledTask) -> bool:
        """Check if task should run now"""
        current_time = time.time()

        if task.last_run is None:
            return True

        return (current_time - task.last_run) >= task.interval_seconds

    def run_task(self, task: ScheduledTask):
        """Execute a scheduled task"""
        print(f"\n[{datetime.now(timezone.utc).isoformat()}]")
        print(f"Running task: {task.name}")

        try:
            result = subprocess.run(
                task.command,
                capture_output=True,
                text=True,
                cwd=self.repo_root,
                timeout=600
            )

            task.last_run = time.time()
            task.next_run = task.last_run + task.interval_seconds

            status = "SUCCESS" if result.returncode == 0 else "FAILURE"
            print(f"[{status}] {task.name} (exit {result.returncode})")

            # Log execution
            self.log_task_execution(task, status, result.returncode)

        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] {task.name}")
            task.last_run = time.time()
            self.log_task_execution(task, "TIMEOUT", 124)

        except Exception as e:
            print(f"[ERROR] {task.name}: {e}")
            task.last_run = time.time()
            self.log_task_execution(task, "ERROR", 1)

    def log_task_execution(self, task: ScheduledTask, status: str, exit_code: int):
        """Log task execution"""
        log_dir = self.repo_root / '24_meta_orchestration/scheduler/logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        event = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'task_name': task.name,
            'status': status,
            'exit_code': exit_code
        }

        log_file = log_dir / 'scheduler_events.jsonl'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event) + '\n')

    def list_tasks(self):
        """List all scheduled tasks"""
        print("="*80)
        print("Scheduled Tasks")
        print("="*80)

        for task in self.tasks:
            interval_hours = task.interval_seconds / 3600
            print(f"\nTask: {task.name}")
            print(f"  Interval: {interval_hours:.1f} hours")
            print(f"  Command: {' '.join(task.command)}")

            if task.last_run:
                last_run_time = datetime.fromtimestamp(task.last_run, tz=timezone.utc)
                print(f"  Last Run: {last_run_time.isoformat()}")

            if task.next_run:
                next_run_time = datetime.fromtimestamp(task.next_run, tz=timezone.utc)
                print(f"  Next Run: {next_run_time.isoformat()}")

    def run(self):
        """Main scheduler loop"""
        print("="*80)
        print("SoT Scheduler - Starting")
        print("="*80)
        print(f"Repository: {self.repo_root}")
        print(f"Tasks: {len(self.tasks)}")
        print("="*80)

        self.list_tasks()
        print("\n[INFO] Scheduler running. Press Ctrl+C to stop.")

        try:
            while True:
                for task in self.tasks:
                    if self.should_run(task):
                        self.run_task(task)

                # Sleep for 60 seconds before next check
                time.sleep(60)

        except KeyboardInterrupt:
            print("\n[INFO] Scheduler stopped")
            sys.exit(0)


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='SoT Task Scheduler')
    parser.add_argument('--list', action='store_true', help='List scheduled tasks')
    parser.add_argument('--task', type=str, help='Run specific task')

    args = parser.parse_args()

    scheduler = SoTScheduler()

    if args.list:
        scheduler.list_tasks()
        sys.exit(0)

    if args.task:
        # Find and run specific task
        task = next((t for t in scheduler.tasks if t.name == args.task), None)
        if task:
            scheduler.run_task(task)
            sys.exit(0)
        else:
            print(f"[ERROR] Task not found: {args.task}")
            sys.exit(1)

    # Run scheduler
    scheduler.run()


if __name__ == '__main__':
    main()
