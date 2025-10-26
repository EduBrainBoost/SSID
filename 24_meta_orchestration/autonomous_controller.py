#!/usr/bin/env python3
"""
SSID Autonomous Controller
==========================

Self-sufficient system that monitors, heals, and improves itself continuously.

Components:
- Continuous monitoring and health checks
- Automatic self-healing and problem resolution
- ML-based self-improvement and optimization
- Continuous testing and validation
- Comprehensive logging and reporting

Author: SSID Autonomous System
Version: 1.0.0
License: ROOT-LOCKED
"""

import asyncio
import json
import logging
import signal
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:/Users/bibel/Documents/Github/SSID/02_audit_logging/autopilot/autonomous_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AutonomousController')


class SystemStatus(Enum):
    """System health status levels"""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    HEALING = "HEALING"
    IMPROVING = "IMPROVING"
    TESTING = "TESTING"


class IssueType(Enum):
    """Types of issues the system can encounter"""
    MISSING_FILE = "missing_file"
    TEST_FAILURE = "test_failure"
    VALIDATION_ERROR = "validation_error"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    CONFIGURATION_DRIFT = "configuration_drift"
    SECURITY_VIOLATION = "security_violation"
    DEPENDENCY_ISSUE = "dependency_issue"


@dataclass
class Issue:
    """Represents a system issue"""
    type: IssueType
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    component: str
    timestamp: str
    metadata: Dict[str, Any]
    auto_fixable: bool = True


@dataclass
class HealthReport:
    """System health report"""
    status: SystemStatus
    timestamp: str
    issues: List[Issue]
    metrics: Dict[str, Any]
    recommendations: List[str]


@dataclass
class HealingAction:
    """Healing action taken by the system"""
    issue: Issue
    action: str
    success: bool
    timestamp: str
    details: str


@dataclass
class Improvement:
    """System improvement suggestion"""
    category: str
    description: str
    confidence: float
    impact: str  # LOW, MEDIUM, HIGH
    risk: str  # LOW, MEDIUM, HIGH
    auto_apply: bool


class AutonomousController:
    """
    Main autonomous controller orchestrating all self-* capabilities
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "C:/Users/bibel/Documents/Github/SSID/24_meta_orchestration/autonomous_config.json"
        self.state_path = "C:/Users/bibel/Documents/Github/SSID/24_meta_orchestration/autonomous_state.json"
        self.base_dir = Path("C:/Users/bibel/Documents/Github/SSID")

        # Load configuration
        self.config = self._load_config()

        # Initialize state
        self.state = {
            "started_at": datetime.now().isoformat(),
            "cycle_count": 0,
            "total_issues_detected": 0,
            "total_issues_healed": 0,
            "total_improvements_applied": 0,
            "last_health_check": None,
            "current_status": SystemStatus.HEALTHY.value,
            "uptime_seconds": 0
        }

        # Control flags
        self.running = False
        self.shutdown_requested = False

        # Initialize components (lazy loading)
        self._monitor = None
        self._healer = None
        self._improver = None
        self._tester = None

        # Statistics
        self.stats = {
            "cycles_completed": 0,
            "issues_fixed": 0,
            "improvements_applied": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "uptime_start": time.time()
        }

        logger.info("Autonomous Controller initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "cycle_interval_seconds": 300,  # 5 minutes
            "enable_auto_healing": True,
            "enable_auto_improvement": True,
            "enable_continuous_testing": True,
            "max_auto_improvements_per_cycle": 3,
            "improvement_risk_threshold": "MEDIUM",  # Don't auto-apply HIGH risk
            "alert_on_critical_issues": True,
            "full_test_suite_interval_hours": 24,
            "health_check_components": [
                "validators",
                "contracts",
                "policies",
                "tests",
                "documentation",
                "audit_logs"
            ],
            "healing_strategies": {
                "missing_file": "regenerate",
                "test_failure": "analyze_and_fix",
                "validation_error": "auto_correct",
                "performance_degradation": "optimize",
                "configuration_drift": "sync",
                "security_violation": "quarantine_and_alert"
            }
        }

        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
                    logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.warning(f"Could not load config, using defaults: {e}")

        return default_config

    def _save_state(self):
        """Persist current state to disk"""
        try:
            self.state["uptime_seconds"] = int(time.time() - self.stats["uptime_start"])
            with open(self.state_path, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    @property
    def monitor(self):
        """Lazy load continuous monitor"""
        if self._monitor is None:
            from continuous_monitor import ContinuousMonitor
            self._monitor = ContinuousMonitor(self.base_dir)
        return self._monitor

    @property
    def healer(self):
        """Lazy load self-healer"""
        if self._healer is None:
            from self_healer import SelfHealer
            self._healer = SelfHealer(self.base_dir)
        return self._healer

    @property
    def improver(self):
        """Lazy load self-improver"""
        if self._improver is None:
            from self_improver import SelfImprover
            self._improver = SelfImprover(self.base_dir)
        return self._improver

    @property
    def tester(self):
        """Lazy load continuous tester"""
        if self._tester is None:
            from continuous_tester import ContinuousTester
            self._tester = ContinuousTester(self.base_dir)
        return self._tester

    def run_forever(self):
        """Main autonomous operation loop"""
        logger.info("=" * 80)
        logger.info("SSID AUTONOMOUS SYSTEM STARTING")
        logger.info("=" * 80)
        logger.info(f"Cycle interval: {self.config['cycle_interval_seconds']}s")
        logger.info(f"Auto-healing: {self.config['enable_auto_healing']}")
        logger.info(f"Auto-improvement: {self.config['enable_auto_improvement']}")
        logger.info(f"Continuous testing: {self.config['enable_continuous_testing']}")

        self.running = True

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            while self.running and not self.shutdown_requested:
                cycle_start = time.time()

                logger.info(f"\n{'=' * 80}")
                logger.info(f"CYCLE {self.state['cycle_count'] + 1} - {datetime.now().isoformat()}")
                logger.info(f"{'=' * 80}")

                try:
                    # 1. MONITOR: Check system health
                    logger.info("[1/5] Running health checks...")
                    health = self._run_health_checks()
                    self.state["last_health_check"] = health.timestamp
                    self.state["current_status"] = health.status.value

                    # 2. HEAL: Fix detected issues
                    if self.config["enable_auto_healing"] and health.issues:
                        logger.info(f"[2/5] Healing {len(health.issues)} detected issues...")
                        healing_results = self._heal_issues(health.issues)
                        self.state["total_issues_healed"] += sum(1 for r in healing_results if r.success)
                    else:
                        logger.info("[2/5] No issues to heal")

                    # 3. IMPROVE: Apply safe improvements
                    if self.config["enable_auto_improvement"]:
                        logger.info("[3/5] Analyzing improvement opportunities...")
                        improvements = self._analyze_improvements()
                        applied = self._apply_safe_improvements(improvements)
                        self.state["total_improvements_applied"] += applied
                    else:
                        logger.info("[3/5] Auto-improvement disabled")

                    # 4. TEST: Run continuous validation
                    if self.config["enable_continuous_testing"]:
                        logger.info("[4/5] Running continuous tests...")
                        test_results = self._run_continuous_tests()
                        self.stats["tests_passed"] += test_results.get("passed", 0)
                        self.stats["tests_failed"] += test_results.get("failed", 0)
                    else:
                        logger.info("[4/5] Continuous testing disabled")

                    # 5. REPORT: Generate cycle report
                    logger.info("[5/5] Generating cycle report...")
                    self._generate_cycle_report(health)

                    # Update state
                    self.state["cycle_count"] += 1
                    self.stats["cycles_completed"] += 1
                    self._save_state()

                    # Log cycle summary
                    cycle_duration = time.time() - cycle_start
                    logger.info(f"\nCycle completed in {cycle_duration:.2f}s")
                    logger.info(f"Status: {health.status.value}")
                    logger.info(f"Issues detected: {len(health.issues)}")
                    logger.info(f"Total cycles: {self.state['cycle_count']}")

                except Exception as e:
                    logger.error(f"Error in autonomous cycle: {e}", exc_info=True)
                    self.state["current_status"] = SystemStatus.CRITICAL.value

                # Sleep until next cycle
                cycle_duration = time.time() - cycle_start
                sleep_time = max(0, self.config["cycle_interval_seconds"] - cycle_duration)

                if sleep_time > 0:
                    logger.info(f"Sleeping for {sleep_time:.0f}s until next cycle...")
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("\nShutdown requested by user")
        finally:
            self._shutdown()

    def _run_health_checks(self) -> HealthReport:
        """Execute comprehensive health checks"""
        try:
            health = self.monitor.check_health()

            logger.info(f"Health Status: {health.status.value}")
            if health.issues:
                logger.warning(f"Detected {len(health.issues)} issues:")
                for issue in health.issues[:5]:  # Log first 5
                    logger.warning(f"  - [{issue.severity}] {issue.description}")
            else:
                logger.info("All systems healthy")

            self.state["total_issues_detected"] += len(health.issues)

            return health
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthReport(
                status=SystemStatus.CRITICAL,
                timestamp=datetime.now().isoformat(),
                issues=[Issue(
                    type=IssueType.DEPENDENCY_ISSUE,
                    severity="CRITICAL",
                    description=f"Health check system failure: {str(e)}",
                    component="monitor",
                    timestamp=datetime.now().isoformat(),
                    metadata={"error": str(e)},
                    auto_fixable=False
                )],
                metrics={},
                recommendations=["Investigate health check system failure"]
            )

    def _heal_issues(self, issues: List[Issue]) -> List[HealingAction]:
        """Attempt to heal detected issues"""
        results = []

        for issue in issues:
            if not issue.auto_fixable:
                logger.warning(f"Issue not auto-fixable: {issue.description}")
                continue

            try:
                logger.info(f"Healing: {issue.description}")
                action = self.healer.heal(issue)
                results.append(action)

                if action.success:
                    logger.info(f"  Success: {action.details}")
                    self.stats["issues_fixed"] += 1
                else:
                    logger.warning(f"  Failed: {action.details}")

            except Exception as e:
                logger.error(f"Healing failed for {issue.description}: {e}")
                results.append(HealingAction(
                    issue=issue,
                    action="heal_failed",
                    success=False,
                    timestamp=datetime.now().isoformat(),
                    details=str(e)
                ))

        return results

    def _analyze_improvements(self) -> List[Improvement]:
        """Analyze system for improvement opportunities"""
        try:
            improvements = self.improver.suggest_improvements()

            if improvements:
                logger.info(f"Found {len(improvements)} improvement opportunities")
                for imp in improvements[:3]:  # Log top 3
                    logger.info(f"  - [{imp.confidence:.0%}] {imp.description}")
            else:
                logger.info("No improvements suggested")

            return improvements
        except Exception as e:
            logger.error(f"Improvement analysis failed: {e}")
            return []

    def _apply_safe_improvements(self, improvements: List[Improvement]) -> int:
        """Apply improvements that meet safety criteria"""
        applied = 0
        max_improvements = self.config["max_auto_improvements_per_cycle"]
        risk_threshold = self.config["improvement_risk_threshold"]

        # Filter to auto-applicable improvements
        safe_improvements = [
            imp for imp in improvements
            if imp.auto_apply and self._is_risk_acceptable(imp.risk, risk_threshold)
        ]

        # Apply up to max per cycle
        for improvement in safe_improvements[:max_improvements]:
            try:
                logger.info(f"Applying improvement: {improvement.description}")
                success = self.improver.apply_improvement(improvement)

                if success:
                    logger.info(f"  Applied successfully")
                    applied += 1
                    self.stats["improvements_applied"] += 1
                else:
                    logger.warning(f"  Application failed")

            except Exception as e:
                logger.error(f"Failed to apply improvement: {e}")

        return applied

    def _is_risk_acceptable(self, risk: str, threshold: str) -> bool:
        """Check if improvement risk is acceptable"""
        risk_levels = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        return risk_levels.get(risk, 2) <= risk_levels.get(threshold, 1)

    def _run_continuous_tests(self) -> Dict[str, int]:
        """Run continuous validation tests"""
        try:
            results = self.tester.run_continuous_tests()

            passed = results.get("passed", 0)
            failed = results.get("failed", 0)

            logger.info(f"Tests: {passed} passed, {failed} failed")

            if failed > 0:
                logger.warning(f"Test failures detected, triggering healing...")
                # Convert test failures to issues for healing
                for failure in results.get("failures", []):
                    issue = Issue(
                        type=IssueType.TEST_FAILURE,
                        severity="HIGH",
                        description=f"Test failed: {failure}",
                        component="tests",
                        timestamp=datetime.now().isoformat(),
                        metadata={"test": failure},
                        auto_fixable=True
                    )
                    self._heal_issues([issue])

            return results
        except Exception as e:
            logger.error(f"Continuous testing failed: {e}")
            return {"passed": 0, "failed": 0}

    def _generate_cycle_report(self, health: HealthReport):
        """Generate comprehensive cycle report"""
        report_dir = self.base_dir / "02_audit_logging" / "autopilot"
        report_dir.mkdir(parents=True, exist_ok=True)

        report = {
            "cycle": self.state["cycle_count"] + 1,
            "timestamp": datetime.now().isoformat(),
            "health_status": health.status.value,
            "issues_detected": len(health.issues),
            "issues_healed": self.state["total_issues_healed"],
            "improvements_applied": self.state["total_improvements_applied"],
            "tests_passed": self.stats["tests_passed"],
            "tests_failed": self.stats["tests_failed"],
            "uptime_seconds": int(time.time() - self.stats["uptime_start"]),
            "metrics": health.metrics,
            "recommendations": health.recommendations
        }

        # Save cycle report
        report_path = report_dir / f"cycle_{report['cycle']:04d}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Update latest report
        latest_path = report_dir / "latest_cycle.json"
        with open(latest_path, 'w') as f:
            json.dump(report, f, indent=2)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"\nReceived signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
        self.running = False

    def _shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down autonomous system...")

        # Save final state
        self._save_state()

        # Generate final report
        self._generate_final_report()

        logger.info("Autonomous system stopped")
        logger.info(f"Total cycles: {self.stats['cycles_completed']}")
        logger.info(f"Total issues fixed: {self.stats['issues_fixed']}")
        logger.info(f"Total improvements: {self.stats['improvements_applied']}")
        logger.info(f"Total uptime: {int(time.time() - self.stats['uptime_start'])}s")

    def _generate_final_report(self):
        """Generate comprehensive final report"""
        report_dir = self.base_dir / "02_audit_logging" / "autopilot"

        final_report = {
            "autonomous_system_session": {
                "started_at": self.state["started_at"],
                "ended_at": datetime.now().isoformat(),
                "total_cycles": self.stats["cycles_completed"],
                "uptime_seconds": int(time.time() - self.stats["uptime_start"])
            },
            "performance": {
                "total_issues_detected": self.state["total_issues_detected"],
                "total_issues_healed": self.state["total_issues_healed"],
                "healing_success_rate": (
                    self.state["total_issues_healed"] / max(1, self.state["total_issues_detected"])
                ),
                "total_improvements_applied": self.state["total_improvements_applied"],
                "tests_passed": self.stats["tests_passed"],
                "tests_failed": self.stats["tests_failed"]
            },
            "configuration": self.config,
            "final_state": self.state
        }

        report_path = report_dir / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(final_report, f, indent=2)

        logger.info(f"Final report saved to {report_path}")

    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "running": self.running,
            "current_status": self.state.get("current_status"),
            "cycle_count": self.state.get("cycle_count"),
            "uptime_seconds": int(time.time() - self.stats["uptime_start"]) if self.running else 0,
            "issues_healed": self.state.get("total_issues_healed"),
            "improvements_applied": self.state.get("total_improvements_applied"),
            "last_health_check": self.state.get("last_health_check")
        }


def main():
    """Main entry point for autonomous controller"""
    import argparse

    parser = argparse.ArgumentParser(description="SSID Autonomous Controller")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--single-cycle", action="store_true", help="Run single cycle and exit")

    args = parser.parse_args()

    controller = AutonomousController(config_path=args.config)

    if args.status:
        status = controller.get_status()
        print(json.dumps(status, indent=2))
        return

    if args.single_cycle:
        # Run one cycle for testing
        logger.info("Running single autonomous cycle...")
        health = controller._run_health_checks()
        if health.issues and controller.config["enable_auto_healing"]:
            controller._heal_issues(health.issues)
        logger.info("Single cycle complete")
        return

    # Run continuously
    controller.run_forever()


if __name__ == "__main__":
    main()
