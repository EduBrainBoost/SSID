#!/usr/bin/env python3
"""
Adaptive Worker Scaling and Work Stealing Validator
====================================================

Advanced parallel execution optimization with:
1. Adaptive worker scaling based on batch characteristics
2. Work stealing algorithm for dynamic load balancing
3. Rule execution profiling for cost-based scheduling
4. Real-time worker utilization monitoring

Performance Target:
- Fixed workers: ~12.1s with 91% efficiency
- Adaptive + work stealing: ~10.5s with 98% efficiency
- Improvement: 15% speedup, 7% efficiency gain

Architecture:
- WorkStealingQueue: Thread-safe deque for task distribution
- RuleExecutionProfile: Historical timing data for scheduling
- AdaptiveValidator: Main orchestrator with dynamic worker allocation
- WorkerMonitor: Real-time utilization tracking

Usage:
    from adaptive_validator import AdaptiveValidator

    validator = AdaptiveValidator(
        repo_root=Path("/path/to/ssid"),
        base_workers=8,  # Max workers
        enable_profiling=True
    )

    report = validator.validate_all_adaptive()
    validator.print_adaptive_stats()
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
from typing import List, Dict, Set, Optional, Deque, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field
from collections import deque
from statistics import mean, stdev

# Import base classes
try:
    from parallel_validator import ParallelSoTValidator, BatchExecutionStats
    from sot_validator_core import ValidationResult, SoTValidationReport
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from parallel_validator import ParallelSoTValidator, BatchExecutionStats
    from sot_validator_core import ValidationResult, SoTValidationReport


# ============================================================
# RULE EXECUTION PROFILING
# ============================================================

@dataclass
class RuleExecutionProfile:
    """Statistical profile of rule execution time"""
    rule_id: str
    avg_time: float  # Average execution time (seconds)
    std_dev: float   # Standard deviation
    sample_count: int  # Number of samples
    min_time: float = 0.0  # Minimum observed time
    max_time: float = 0.0  # Maximum observed time
    last_updated: float = 0.0  # Timestamp of last update

    def update(self, new_time: float):
        """Update profile with new execution time sample"""
        if self.sample_count == 0:
            # First sample
            self.avg_time = new_time
            self.std_dev = 0.0
            self.min_time = new_time
            self.max_time = new_time
            self.sample_count = 1
        else:
            # Incremental update (Welford's online algorithm)
            n = self.sample_count
            old_avg = self.avg_time
            new_avg = (old_avg * n + new_time) / (n + 1)

            # Update variance (simplified - good enough for our use)
            if n > 1:
                old_var = self.std_dev ** 2
                new_var = ((n - 1) * old_var + (new_time - old_avg) * (new_time - new_avg)) / n
                self.std_dev = new_var ** 0.5

            self.avg_time = new_avg
            self.sample_count = n + 1
            self.min_time = min(self.min_time, new_time)
            self.max_time = max(self.max_time, new_time)

        self.last_updated = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "rule_id": self.rule_id,
            "avg_time": self.avg_time,
            "std_dev": self.std_dev,
            "sample_count": self.sample_count,
            "min_time": self.min_time,
            "max_time": self.max_time,
            "last_updated": self.last_updated
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'RuleExecutionProfile':
        """Create profile from dictionary"""
        return RuleExecutionProfile(
            rule_id=data["rule_id"],
            avg_time=data["avg_time"],
            std_dev=data["std_dev"],
            sample_count=data["sample_count"],
            min_time=data.get("min_time", 0.0),
            max_time=data.get("max_time", 0.0),
            last_updated=data.get("last_updated", 0.0)
        )


class RuleProfileManager:
    """
    Manages persistent storage and retrieval of rule execution profiles.

    Profiles are stored in rule_execution_profiles.json and updated
    incrementally as rules execute.
    """

    def __init__(self, profile_file: Path = None):
        if profile_file is None:
            profile_file = Path(__file__).parent / "rule_execution_profiles.json"

        self.profile_file = profile_file
        self.profiles: Dict[str, RuleExecutionProfile] = {}
        self.lock = threading.Lock()
        self._load_profiles()

    def _load_profiles(self):
        """Load profiles from disk"""
        if self.profile_file.exists():
            try:
                with open(self.profile_file, 'r') as f:
                    data = json.load(f)

                for rule_id, profile_data in data.get("profiles", {}).items():
                    self.profiles[rule_id] = RuleExecutionProfile.from_dict(profile_data)

                print(f"[PROFILER] Loaded {len(self.profiles)} profiles from {self.profile_file.name}")
            except Exception as e:
                print(f"[PROFILER] Failed to load profiles: {e}")
                self.profiles = {}
        else:
            print(f"[PROFILER] No existing profiles found, starting fresh")
            self.profiles = {}

    def save_profiles(self):
        """Save profiles to disk"""
        with self.lock:
            try:
                data = {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "total_profiles": len(self.profiles),
                    "profiles": {
                        rule_id: profile.to_dict()
                        for rule_id, profile in self.profiles.items()
                    }
                }

                with open(self.profile_file, 'w') as f:
                    json.dump(data, f, indent=2)

                print(f"[PROFILER] Saved {len(self.profiles)} profiles to {self.profile_file.name}")
            except Exception as e:
                print(f"[PROFILER] Failed to save profiles: {e}")

    def get_profile(self, rule_id: str) -> Optional[RuleExecutionProfile]:
        """Get profile for rule (None if no profile exists)"""
        with self.lock:
            return self.profiles.get(rule_id)

    def update_profile(self, rule_id: str, execution_time: float):
        """Update profile with new execution time"""
        with self.lock:
            if rule_id not in self.profiles:
                self.profiles[rule_id] = RuleExecutionProfile(
                    rule_id=rule_id,
                    avg_time=execution_time,
                    std_dev=0.0,
                    sample_count=0
                )

            self.profiles[rule_id].update(execution_time)

    def get_estimated_time(self, rule_id: str, default: float = 0.01) -> float:
        """Get estimated execution time for rule"""
        profile = self.get_profile(rule_id)
        if profile and profile.sample_count > 0:
            return profile.avg_time
        return default


# ============================================================
# WORK STEALING QUEUE
# ============================================================

class WorkStealingQueue:
    """
    Thread-safe work stealing queue using deques.

    Each worker has its own deque:
    - Workers pop from their own queue (LIFO - cache locality)
    - Workers steal from other queues (FIFO - load balancing)

    This provides excellent load balancing while maintaining
    cache locality for sequential task execution.
    """

    def __init__(self):
        self.queues: Dict[int, Deque[str]] = {}
        self.lock = threading.Lock()
        self.stats = {
            "pushes": 0,
            "pops": 0,
            "steals": 0,
            "steal_attempts": 0,
            "steal_failures": 0
        }

    def push(self, worker_id: int, task: str):
        """Push task to worker's queue (LIFO for pop)"""
        with self.lock:
            if worker_id not in self.queues:
                self.queues[worker_id] = deque()
            self.queues[worker_id].append(task)
            self.stats["pushes"] += 1

    def pop(self, worker_id: int) -> Optional[str]:
        """Pop task from own queue (LIFO - most recently added)"""
        with self.lock:
            if worker_id in self.queues and self.queues[worker_id]:
                self.stats["pops"] += 1
                return self.queues[worker_id].pop()
        return None

    def steal(self, thief_id: int) -> Optional[str]:
        """Steal task from another worker's queue (FIFO - oldest task)"""
        with self.lock:
            self.stats["steal_attempts"] += 1

            # Find victim with most work
            victim_candidates = [
                (wid, len(q))
                for wid, q in self.queues.items()
                if wid != thief_id and len(q) > 0
            ]

            if not victim_candidates:
                self.stats["steal_failures"] += 1
                return None

            # Choose victim with most work
            victim_id, _ = max(victim_candidates, key=lambda x: x[1])

            # Steal from front (FIFO for stealing - take oldest work)
            if self.queues[victim_id]:
                self.stats["steals"] += 1
                return self.queues[victim_id].popleft()

            self.stats["steal_failures"] += 1
            return None

    def get_queue_sizes(self) -> Dict[int, int]:
        """Get current queue sizes for all workers"""
        with self.lock:
            return {wid: len(q) for wid, q in self.queues.items()}

    def get_stats(self) -> Dict[str, int]:
        """Get work stealing statistics"""
        with self.lock:
            stats = self.stats.copy()
            if stats["steal_attempts"] > 0:
                stats["steal_success_rate"] = (
                    stats["steals"] / stats["steal_attempts"] * 100
                )
            else:
                stats["steal_success_rate"] = 0.0
            return stats


# ============================================================
# WORKER UTILIZATION MONITORING
# ============================================================

@dataclass
class WorkerStats:
    """Statistics for a single worker"""
    worker_id: int
    tasks_executed: int = 0
    tasks_stolen: int = 0
    tasks_donated: int = 0  # Tasks stolen by others
    total_work_time: float = 0.0
    total_idle_time: float = 0.0
    total_steal_time: float = 0.0

    @property
    def utilization(self) -> float:
        """Worker utilization percentage (0-100)"""
        total = self.total_work_time + self.total_idle_time
        if total > 0:
            return (self.total_work_time / total) * 100
        return 0.0


class WorkerMonitor:
    """
    Monitors worker utilization in real-time.

    Tracks:
    - Task execution time per worker
    - Idle time (waiting for work)
    - Work stealing activity
    - Overall worker efficiency
    """

    def __init__(self):
        self.workers: Dict[int, WorkerStats] = {}
        self.lock = threading.Lock()

    def record_task_execution(self, worker_id: int, execution_time: float, was_stolen: bool = False):
        """Record task execution by worker"""
        with self.lock:
            if worker_id not in self.workers:
                self.workers[worker_id] = WorkerStats(worker_id)

            self.workers[worker_id].tasks_executed += 1
            self.workers[worker_id].total_work_time += execution_time

            if was_stolen:
                self.workers[worker_id].tasks_stolen += 1

    def record_idle_time(self, worker_id: int, idle_time: float):
        """Record worker idle time"""
        with self.lock:
            if worker_id not in self.workers:
                self.workers[worker_id] = WorkerStats(worker_id)

            self.workers[worker_id].total_idle_time += idle_time

    def record_steal_attempt(self, worker_id: int, steal_time: float):
        """Record time spent attempting to steal work"""
        with self.lock:
            if worker_id not in self.workers:
                self.workers[worker_id] = WorkerStats(worker_id)

            self.workers[worker_id].total_steal_time += steal_time

    def get_worker_stats(self, worker_id: int) -> Optional[WorkerStats]:
        """Get statistics for specific worker"""
        with self.lock:
            return self.workers.get(worker_id)

    def get_all_stats(self) -> List[WorkerStats]:
        """Get statistics for all workers"""
        with self.lock:
            return list(self.workers.values())

    def get_aggregate_stats(self) -> Dict[str, Any]:
        """Get aggregate statistics across all workers"""
        with self.lock:
            if not self.workers:
                return {}

            total_work = sum(w.total_work_time for w in self.workers.values())
            total_idle = sum(w.total_idle_time for w in self.workers.values())
            total_tasks = sum(w.tasks_executed for w in self.workers.values())
            total_steals = sum(w.tasks_stolen for w in self.workers.values())

            utilizations = [w.utilization for w in self.workers.values()]

            return {
                "total_workers": len(self.workers),
                "total_tasks": total_tasks,
                "total_steals": total_steals,
                "steal_percentage": (total_steals / total_tasks * 100) if total_tasks > 0 else 0.0,
                "total_work_time": total_work,
                "total_idle_time": total_idle,
                "avg_utilization": mean(utilizations) if utilizations else 0.0,
                "min_utilization": min(utilizations) if utilizations else 0.0,
                "max_utilization": max(utilizations) if utilizations else 0.0,
                "utilization_std_dev": stdev(utilizations) if len(utilizations) > 1 else 0.0,
                "overall_efficiency": (total_work / (total_work + total_idle) * 100) if (total_work + total_idle) > 0 else 0.0
            }


# ============================================================
# ADAPTIVE BATCH STATISTICS
# ============================================================

@dataclass
class AdaptiveBatchStats(BatchExecutionStats):
    """Extended batch statistics with adaptive metrics"""
    optimal_workers: int = 0  # Calculated optimal workers
    actual_workers: int = 0   # Actually used workers
    estimated_time: float = 0.0  # Predicted execution time
    actual_time: float = 0.0     # Actual execution time
    prediction_error: float = 0.0  # Percentage error
    worker_utilization: float = 0.0  # Average worker utilization
    work_stolen_count: int = 0  # Number of stolen tasks
    load_balance_variance: float = 0.0  # Variance in worker load


# ============================================================
# ADAPTIVE VALIDATOR
# ============================================================

class AdaptiveValidator(ParallelSoTValidator):
    """
    Advanced parallel validator with adaptive worker scaling and work stealing.

    Key Features:
    1. Adaptive Worker Scaling: Adjusts worker count per batch
    2. Work Stealing: Dynamic load balancing between workers
    3. Cost-Based Scheduling: Orders rules by predicted execution time
    4. Utilization Monitoring: Tracks worker efficiency in real-time
    5. Persistent Profiling: Learns from historical execution data

    Performance Target:
    - Worker efficiency: 91% -> 98%
    - Overall speedup: 12.1s -> 10.5s (15% improvement)
    - Idle time: <2% of total time
    - Load variance: <10% across workers
    """

    def __init__(self,
                 repo_root: Path,
                 base_workers: int = None,
                 enable_profiling: bool = True,
                 show_progress: bool = True,
                 cache_ttl: int = 60):
        """
        Initialize adaptive validator.

        Args:
            repo_root: Path to SSID repository root
            base_workers: Maximum workers (default: CPU count)
            enable_profiling: Enable execution profiling (default: True)
            show_progress: Show progress bars (default: True)
            cache_ttl: Cache TTL in seconds (default: 60)
        """
        # Initialize base class
        super().__init__(repo_root, max_workers=base_workers, show_progress=show_progress, cache_ttl=cache_ttl)

        # Adaptive configuration
        self.base_workers = base_workers or os.cpu_count()
        self.enable_profiling = enable_profiling

        # Profiling system
        self.profiler = RuleProfileManager() if enable_profiling else None

        # Work stealing
        self.work_queue = WorkStealingQueue()
        self.worker_monitor = WorkerMonitor()

        # Adaptive statistics
        self.adaptive_batch_stats: List[AdaptiveBatchStats] = []

        print(f"[ADAPTIVE] Base workers: {self.base_workers}")
        print(f"[ADAPTIVE] Profiling: {'enabled' if enable_profiling else 'disabled'}")

    def _calculate_optimal_workers(self, batch: List[str]) -> int:
        """
        Calculate optimal worker count for batch based on rule count and characteristics.

        Strategy:
        - 1 rule: 1 worker (no overhead)
        - 2-3 rules: 2 workers
        - 4-10 rules: 4 workers
        - 11-50 rules: min(8, base_workers)
        - 50+ rules: base_workers

        Args:
            batch: List of rule IDs in batch

        Returns:
            Optimal worker count (1 to base_workers)
        """
        rule_count = len(batch)

        if rule_count == 1:
            return 1
        elif rule_count <= 3:
            return min(2, self.base_workers)
        elif rule_count <= 10:
            return min(4, self.base_workers)
        elif rule_count <= 50:
            return min(8, self.base_workers)
        else:
            return self.base_workers

    def _estimate_batch_time(self, batch: List[str]) -> float:
        """
        Estimate total execution time for batch based on historical profiles.

        Args:
            batch: List of rule IDs

        Returns:
            Estimated total time in seconds
        """
        if not self.profiler:
            return len(batch) * 0.01  # Default estimate

        total_time = 0.0
        for rule_id in batch:
            total_time += self.profiler.get_estimated_time(rule_id, default=0.01)

        return total_time

    def _sort_by_cost(self, batch: List[str]) -> List[str]:
        """
        Sort rules by estimated cost (largest first for better load balancing).

        Largest-first scheduling minimizes makespan by ensuring expensive
        tasks are started early and distributed evenly.

        Args:
            batch: List of rule IDs

        Returns:
            Sorted list (most expensive first)
        """
        if not self.profiler:
            return batch  # No profiling data, keep original order

        return sorted(
            batch,
            key=lambda rid: self.profiler.get_estimated_time(rid, default=0.01),
            reverse=True
        )

    def validate_all_adaptive(self) -> SoTValidationReport:
        """
        Execute all rules with adaptive worker scaling and work stealing.

        Returns:
            SoTValidationReport with validation results
        """
        print(f"\n[ADAPTIVE] Starting validation with adaptive scaling")
        print(f"[ADAPTIVE] Base workers: {self.base_workers}")
        print(f"[ADAPTIVE] Total batches: {self.dependency_graph.total_batches}")

        self.total_start_time = time.time()
        all_results: List[ValidationResult] = []

        # Execute each batch
        batches = self.dependency_graph.get_all_batches()

        for batch_config in batches:
            batch_id = batch_config['batch_id']

            # Skip batch 8 (SOT-V2) - handle separately
            if batch_id == 8:
                batch_results = self._execute_sot_v2_adaptive(batch_config)
            else:
                batch_results = self._execute_batch_adaptive(batch_config)

            all_results.extend(batch_results)

        self.total_end_time = time.time()

        # Save profiling data
        if self.profiler:
            self.profiler.save_profiles()

        # Calculate summary
        passed_count = sum(1 for r in all_results if r.passed)
        failed_count = len(all_results) - passed_count
        summary = self._generate_summary(all_results)

        # Create report
        report = SoTValidationReport(
            timestamp=self.timestamp,
            repo_root=str(self.repo_root),
            total_rules=len(all_results),
            passed_count=passed_count,
            failed_count=failed_count,
            results=all_results,
            summary=summary
        )

        return report

    def _execute_batch_adaptive(self, batch_config: Dict[str, Any]) -> List[ValidationResult]:
        """
        Execute batch with adaptive worker scaling and work stealing.

        Args:
            batch_config: Batch configuration from dependency graph

        Returns:
            List of validation results
        """
        batch_id = batch_config['batch_id']
        batch_name = batch_config['name']
        batch_rules = batch_config['rules']
        rule_count = len(batch_rules)

        # Create adaptive batch stats
        stats = AdaptiveBatchStats(
            batch_id=batch_id,
            batch_name=batch_name,
            rule_count=rule_count
        )
        stats.start_time = time.time()

        # Calculate optimal workers for this batch
        optimal_workers = self._calculate_optimal_workers(batch_rules)
        stats.optimal_workers = optimal_workers
        stats.actual_workers = optimal_workers
        stats.workers_used = optimal_workers

        # Estimate batch time
        estimated_time = self._estimate_batch_time(batch_rules)
        stats.estimated_time = estimated_time

        # Sort by cost (largest first)
        sorted_rules = self._sort_by_cost(batch_rules)

        print(f"\n[BATCH {batch_id}] {batch_name}")
        print(f"[BATCH {batch_id}] Rules: {rule_count}, Workers: {optimal_workers} (base: {self.base_workers})")
        print(f"[BATCH {batch_id}] Estimated time: {estimated_time:.3f}s")

        # Initialize work stealing queue
        self.work_queue = WorkStealingQueue()
        self.worker_monitor = WorkerMonitor()

        # Distribute work to workers (round-robin)
        for i, rule_id in enumerate(sorted_rules):
            worker_id = i % optimal_workers
            self.work_queue.push(worker_id, rule_id)

        # Execute with work stealing
        results: List[ValidationResult] = []

        if rule_count == 1:
            # Single rule - no parallelism needed
            rule_id = sorted_rules[0]
            start = time.time()
            result = self._execute_rule(rule_id)
            elapsed = time.time() - start

            results.append(result)
            if result.passed:
                stats.passed_count += 1
            else:
                stats.failed_count += 1

            # Update profile
            if self.profiler:
                self.profiler.update_profile(rule_id, elapsed)
        else:
            # Multi-rule batch - use work stealing
            with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
                futures = [
                    executor.submit(self._worker_with_stealing, worker_id)
                    for worker_id in range(optimal_workers)
                ]

                for future in as_completed(futures):
                    worker_results = future.result()
                    results.extend(worker_results)

                    for result in worker_results:
                        if result.passed:
                            stats.passed_count += 1
                        else:
                            stats.failed_count += 1

        stats.end_time = time.time()
        stats.duration = stats.end_time - stats.start_time
        stats.actual_time = stats.duration

        # Calculate prediction error
        if stats.estimated_time > 0:
            stats.prediction_error = abs(stats.actual_time - stats.estimated_time) / stats.estimated_time * 100

        # Get worker utilization
        agg_stats = self.worker_monitor.get_aggregate_stats()
        if agg_stats:
            stats.worker_utilization = agg_stats.get("avg_utilization", 0.0)
            stats.load_balance_variance = agg_stats.get("utilization_std_dev", 0.0)

        # Get work stealing stats
        ws_stats = self.work_queue.get_stats()
        stats.work_stolen_count = ws_stats.get("steals", 0)

        self.adaptive_batch_stats.append(stats)

        print(f"[BATCH {batch_id}] Complete: {stats.passed_count}/{rule_count} passed in {stats.duration:.3f}s")
        print(f"[BATCH {batch_id}] Prediction error: {stats.prediction_error:.1f}%")
        print(f"[BATCH {batch_id}] Work stolen: {stats.work_stolen_count} tasks")
        print(f"[BATCH {batch_id}] Worker utilization: {stats.worker_utilization:.1f}%")

        return results

    def _execute_sot_v2_adaptive(self, batch_config: Dict[str, Any]) -> List[ValidationResult]:
        """
        Execute SOT-V2 batch with adaptive workers.

        Args:
            batch_config: Batch configuration

        Returns:
            List of validation results
        """
        batch_id = batch_config['batch_id']
        batch_name = batch_config['name']
        rule_count = batch_config['rule_count']  # 185 rules

        # Always use full workers for large SOT-V2 batch
        optimal_workers = self.base_workers

        stats = AdaptiveBatchStats(
            batch_id=batch_id,
            batch_name=batch_name,
            rule_count=rule_count,
            optimal_workers=optimal_workers,
            actual_workers=optimal_workers,
            workers_used=optimal_workers
        )
        stats.start_time = time.time()

        print(f"\n[BATCH {batch_id}] {batch_name}")
        print(f"[BATCH {batch_id}] Rules: {rule_count}, Workers: {optimal_workers}")

        # Initialize work stealing
        self.work_queue = WorkStealingQueue()
        self.worker_monitor = WorkerMonitor()

        # Generate rule numbers
        rule_numbers = [i for i in range(1, 190) if i not in [91, 92, 93, 94]]

        # Distribute work
        for i, num in enumerate(rule_numbers):
            worker_id = i % optimal_workers
            self.work_queue.push(worker_id, f"SOT-V2-{num:04d}")

        results: List[ValidationResult] = []

        with ThreadPoolExecutor(max_workers=optimal_workers) as executor:
            futures = [
                executor.submit(self._worker_sot_v2_stealing, worker_id)
                for worker_id in range(optimal_workers)
            ]

            for future in as_completed(futures):
                worker_results = future.result()
                results.extend(worker_results)

                for result in worker_results:
                    if result.passed:
                        stats.passed_count += 1
                    else:
                        stats.failed_count += 1

        stats.end_time = time.time()
        stats.duration = stats.end_time - stats.start_time
        stats.actual_time = stats.duration

        # Get stats
        agg_stats = self.worker_monitor.get_aggregate_stats()
        if agg_stats:
            stats.worker_utilization = agg_stats.get("avg_utilization", 0.0)
            stats.load_balance_variance = agg_stats.get("utilization_std_dev", 0.0)

        ws_stats = self.work_queue.get_stats()
        stats.work_stolen_count = ws_stats.get("steals", 0)

        self.adaptive_batch_stats.append(stats)

        print(f"[BATCH {batch_id}] Complete: {stats.passed_count}/{rule_count} passed in {stats.duration:.3f}s")
        print(f"[BATCH {batch_id}] Work stolen: {stats.work_stolen_count} tasks")
        print(f"[BATCH {batch_id}] Worker utilization: {stats.worker_utilization:.1f}%")

        return results

    def _worker_with_stealing(self, worker_id: int) -> List[ValidationResult]:
        """
        Worker function with work stealing support.

        Args:
            worker_id: Unique worker identifier

        Returns:
            List of validation results from this worker
        """
        results = []

        while True:
            # Try to get work from own queue (LIFO)
            task_id = self.work_queue.pop(worker_id)
            was_stolen = False

            if task_id is None:
                # No work in own queue, try to steal (FIFO)
                steal_start = time.time()
                task_id = self.work_queue.steal(worker_id)
                steal_time = time.time() - steal_start

                self.worker_monitor.record_steal_attempt(worker_id, steal_time)

                if task_id is not None:
                    was_stolen = True

            # If still no work, we're done
            if task_id is None:
                # Record final idle time
                break

            # Execute task
            start = time.time()
            try:
                result = self._execute_rule(task_id)
            except Exception as e:
                result = ValidationResult(
                    rule_id=task_id,
                    passed=False,
                    severity="HIGH",
                    message=f"Execution error: {str(e)}",
                    evidence={"error": str(e)}
                )

            elapsed = time.time() - start

            # Update profile
            if self.profiler:
                self.profiler.update_profile(task_id, elapsed)

            # Record execution
            self.worker_monitor.record_task_execution(worker_id, elapsed, was_stolen)

            results.append(result)

        return results

    def _worker_sot_v2_stealing(self, worker_id: int) -> List[ValidationResult]:
        """
        Worker function for SOT-V2 rules with work stealing.

        Args:
            worker_id: Unique worker identifier

        Returns:
            List of validation results
        """
        results = []

        while True:
            # Try to get work
            task_id = self.work_queue.pop(worker_id)
            was_stolen = False

            if task_id is None:
                # Try to steal
                steal_start = time.time()
                task_id = self.work_queue.steal(worker_id)
                steal_time = time.time() - steal_start

                self.worker_monitor.record_steal_attempt(worker_id, steal_time)

                if task_id is not None:
                    was_stolen = True

            if task_id is None:
                break

            # Extract rule number from task_id (SOT-V2-0001 -> 1)
            rule_num = int(task_id.split('-')[-1])

            # Execute task
            start = time.time()
            try:
                result = self.validate_sot_v2(rule_num)
            except Exception as e:
                result = ValidationResult(
                    rule_id=task_id,
                    passed=False,
                    severity="MEDIUM",
                    message=f"Execution error: {str(e)}",
                    evidence={"error": str(e)}
                )

            elapsed = time.time() - start

            # Update profile
            if self.profiler:
                self.profiler.update_profile(task_id, elapsed)

            # Record execution
            self.worker_monitor.record_task_execution(worker_id, elapsed, was_stolen)

            results.append(result)

        return results

    def print_adaptive_stats(self):
        """Print detailed adaptive execution statistics"""
        print("\n" + "="*70)
        print("[ADAPTIVE EXECUTION SUMMARY]")
        print("="*70)

        total_duration = self.total_end_time - self.total_start_time
        total_rules = sum(stat.rule_count for stat in self.adaptive_batch_stats)

        print(f"Total Rules:    {total_rules}")
        print(f"Total Batches:  {len(self.adaptive_batch_stats)}")
        print(f"Total Duration: {total_duration:.3f}s")
        print(f"Base Workers:   {self.base_workers}")

        # Aggregate statistics
        total_steals = sum(stat.work_stolen_count for stat in self.adaptive_batch_stats)
        avg_utilization = mean([stat.worker_utilization for stat in self.adaptive_batch_stats if stat.worker_utilization > 0])
        avg_variance = mean([stat.load_balance_variance for stat in self.adaptive_batch_stats if stat.load_balance_variance > 0])

        print(f"\nWork Stealing:")
        print(f"  Total steals: {total_steals}")
        print(f"  Avg worker utilization: {avg_utilization:.1f}%")
        print(f"  Load balance variance: {avg_variance:.1f}%")

        print("\nBatch Breakdown:")
        print("-"*70)
        print(f"{'Batch':<6} {'Name':<25} {'Rules':<6} {'Workers':<8} {'Time':<10} {'Util%':<8} {'Steals':<8}")
        print("-"*70)

        for stat in self.adaptive_batch_stats:
            print(f"{stat.batch_id:<6} {stat.batch_name[:23]:<25} {stat.rule_count:<6} "
                  f"{stat.actual_workers:<8} {stat.duration:>7.3f}s  "
                  f"{stat.worker_utilization:>5.1f}%  {stat.work_stolen_count:<8}")

        print("="*70)

        # Print cache stats
        print("\n[CACHE STATISTICS]")
        self.print_cache_stats()


# ============================================================
# DEMO / TESTING
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Adaptive Worker Scaling Validator")
    parser.add_argument('--repo-root', type=str, help='Path to SSID repository root')
    parser.add_argument('--workers', type=int, help='Base worker count')
    parser.add_argument('--no-profiling', action='store_true', help='Disable profiling')
    parser.add_argument('--no-progress', action='store_true', help='Disable progress bars')

    args = parser.parse_args()

    # Get repo root
    if args.repo_root:
        repo_root = Path(args.repo_root)
    else:
        repo_root = Path(__file__).parent.parent.parent.parent

    print(f"[ADAPTIVE] Repository: {repo_root}")

    # Create validator
    validator = AdaptiveValidator(
        repo_root=repo_root,
        base_workers=args.workers,
        enable_profiling=not args.no_profiling,
        show_progress=not args.no_progress
    )

    # Execute validation
    print("\n[ADAPTIVE] Running adaptive validation...\n")

    start = time.time()
    report = validator.validate_all_adaptive()
    elapsed = time.time() - start

    # Print results
    print(f"\n[RESULTS] Validation complete:")
    print(f"  Total Rules: {report.total_rules}")
    print(f"  Passed: {report.passed_count}")
    print(f"  Failed: {report.failed_count}")
    print(f"  Pass Rate: {(report.passed_count/report.total_rules*100):.2f}%")
    print(f"  Total Time: {elapsed:.3f}s")

    # Print adaptive stats
    validator.print_adaptive_stats()

    print("\n[OK] Adaptive validation complete!")
