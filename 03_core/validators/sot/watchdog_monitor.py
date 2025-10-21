#!/usr/bin/env python3
"""
Watchdog Monitor - Real-Time Cache Invalidation
================================================

Optional feature: Real-time cache invalidation using filesystem monitoring.

Monitors repository for file changes and automatically invalidates affected
cache entries. Falls back gracefully if watchdog is not installed.

Features:
- Real-time file change detection
- Automatic cache invalidation
- Background monitoring thread
- Graceful degradation if watchdog unavailable

Installation:
    pip install watchdog

Usage:
    from watchdog_monitor import WatchdogCacheMonitor

    # Create monitor
    monitor = WatchdogCacheMonitor(
        result_cache=cache,
        repo_root=Path("/path/to/ssid")
    )

    # Start monitoring
    monitor.start()

    # ... perform validations ...

    # Stop monitoring
    monitor.stop()

Performance:
- Minimal overhead (<1% CPU)
- Instant cache invalidation on file save
- No polling required
- Falls back to hash-based validation if unavailable
"""

import time
import sys
from pathlib import Path
from typing import Optional, Set, List
import threading

# Try to import watchdog (optional dependency)
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None
    FileSystemEvent = None

# Import result cache
try:
    from result_cache import ResultCache
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from result_cache import ResultCache


# ============================================================
# FILESYSTEM EVENT HANDLER
# ============================================================

if WATCHDOG_AVAILABLE:
    class ValidationCacheInvalidator(FileSystemEventHandler):
        """
        Handles filesystem events and invalidates affected cache entries.

        Monitors:
        - .yaml file modifications
        - .py file modifications
        - File creation/deletion
        - Directory changes

        Invalidation Strategy:
        - Find all rules that track the modified file
        - Invalidate only those specific rules
        - Log invalidations for debugging
        """

        def __init__(self, result_cache: ResultCache, verbose: bool = False):
            """
            Initialize event handler.

            Args:
                result_cache: ResultCache instance to invalidate
                verbose: Print invalidation messages (default: False)
            """
            super().__init__()
            self.result_cache = result_cache
            self.verbose = verbose

            # Track invalidations
            self.invalidation_count = 0
            self.last_invalidation_time = 0

            # Debouncing (avoid duplicate invalidations)
            self._recently_invalidated: Set[str] = set()
            self._debounce_seconds = 1.0

        def on_modified(self, event: FileSystemEvent):
            """Handle file modification events"""
            if event.is_directory:
                return

            self._handle_file_change(event.src_path, "modified")

        def on_created(self, event: FileSystemEvent):
            """Handle file creation events"""
            if event.is_directory:
                return

            self._handle_file_change(event.src_path, "created")

        def on_deleted(self, event: FileSystemEvent):
            """Handle file deletion events"""
            if event.is_directory:
                return

            self._handle_file_change(event.src_path, "deleted")

        def _handle_file_change(self, file_path: str, change_type: str):
            """
            Handle file change and invalidate affected cache entries.

            Args:
                file_path: Path to changed file
                change_type: Type of change (modified, created, deleted)
            """
            file_path_obj = Path(file_path)

            # Only care about relevant files
            if not self._is_relevant_file(file_path_obj):
                return

            # Debounce - avoid duplicate invalidations
            current_time = time.time()
            debounce_key = f"{file_path}:{change_type}"

            if debounce_key in self._recently_invalidated:
                # Check if debounce period has passed
                if current_time - self.last_invalidation_time < self._debounce_seconds:
                    return

            # Find affected rules
            affected_rules = self.result_cache.find_affected_rules(file_path_obj)

            if affected_rules:
                # Invalidate affected rules
                for rule_id in affected_rules:
                    self.result_cache.invalidate(rule_id)
                    self.invalidation_count += 1

                # Add to debounce set
                self._recently_invalidated.add(debounce_key)
                self.last_invalidation_time = current_time

                # Clean debounce set periodically
                if len(self._recently_invalidated) > 100:
                    self._recently_invalidated.clear()

                if self.verbose:
                    print(f"[WATCHDOG] File {change_type}: {file_path_obj.name}")
                    print(f"           Invalidated {len(affected_rules)} rules: {', '.join(affected_rules)}")

        def _is_relevant_file(self, file_path: Path) -> bool:
            """
            Check if file is relevant for cache invalidation.

            Args:
                file_path: Path to file

            Returns:
                True if file should trigger invalidation
            """
            # Ignore cache files
            if '.ssid_cache' in str(file_path):
                return False

            # Ignore hidden files
            if file_path.name.startswith('.'):
                return False

            # Only track specific extensions
            relevant_extensions = {'.yaml', '.yml', '.py', '.json', '.md'}

            return file_path.suffix in relevant_extensions

        def get_stats(self) -> dict:
            """Get invalidation statistics"""
            return {
                'invalidation_count': self.invalidation_count,
                'last_invalidation_time': self.last_invalidation_time
            }


# ============================================================
# WATCHDOG MONITOR
# ============================================================

class WatchdogCacheMonitor:
    """
    Monitors filesystem and invalidates cache in real-time.

    Features:
    - Background monitoring thread
    - Automatic cache invalidation
    - Graceful degradation if watchdog unavailable
    - Start/stop control

    Performance:
    - Minimal CPU overhead (<1%)
    - Instant invalidation (no polling)
    - Debounced to avoid duplicate invalidations
    """

    def __init__(
        self,
        result_cache: ResultCache,
        repo_root: Path,
        verbose: bool = False,
        recursive: bool = True
    ):
        """
        Initialize watchdog monitor.

        Args:
            result_cache: ResultCache instance to monitor
            repo_root: Repository root to monitor
            verbose: Print invalidation messages (default: False)
            recursive: Monitor subdirectories recursively (default: True)
        """
        self.result_cache = result_cache
        self.repo_root = Path(repo_root)
        self.verbose = verbose
        self.recursive = recursive

        # Check if watchdog is available
        if not WATCHDOG_AVAILABLE:
            if verbose:
                print("[WATCHDOG] Warning: watchdog not installed, real-time monitoring disabled")
                print("           Install with: pip install watchdog")
            self.available = False
            return

        self.available = True

        # Create event handler and observer
        self.event_handler = ValidationCacheInvalidator(result_cache, verbose=verbose)
        self.observer = Observer()
        self.observer.schedule(
            self.event_handler,
            str(self.repo_root),
            recursive=recursive
        )

        # Monitoring state
        self.is_running = False

    def start(self):
        """Start filesystem monitoring"""
        if not self.available:
            if self.verbose:
                print("[WATCHDOG] Cannot start: watchdog not available")
            return

        if self.is_running:
            if self.verbose:
                print("[WATCHDOG] Already running")
            return

        try:
            self.observer.start()
            self.is_running = True

            if self.verbose:
                print(f"[WATCHDOG] Started monitoring: {self.repo_root}")
                print(f"           Recursive: {self.recursive}")
        except Exception as e:
            if self.verbose:
                print(f"[WATCHDOG] Failed to start: {e}")

    def stop(self):
        """Stop filesystem monitoring"""
        if not self.available:
            return

        if not self.is_running:
            return

        try:
            self.observer.stop()
            self.observer.join(timeout=5)
            self.is_running = False

            if self.verbose:
                print(f"[WATCHDOG] Stopped monitoring")
        except Exception as e:
            if self.verbose:
                print(f"[WATCHDOG] Error stopping: {e}")

    def get_stats(self) -> dict:
        """Get monitoring statistics"""
        if not self.available:
            return {
                'available': False,
                'running': False,
                'invalidations': 0
            }

        handler_stats = self.event_handler.get_stats()

        return {
            'available': True,
            'running': self.is_running,
            'invalidations': handler_stats['invalidation_count'],
            'last_invalidation': handler_stats['last_invalidation_time']
        }

    def print_stats(self):
        """Print monitoring statistics"""
        stats = self.get_stats()

        print("\n" + "="*60)
        print("WATCHDOG MONITOR STATISTICS")
        print("="*60)

        if not stats['available']:
            print("Status:             NOT AVAILABLE")
            print("Reason:             watchdog package not installed")
            print("Install:            pip install watchdog")
        else:
            print(f"Status:             {'RUNNING' if stats['running'] else 'STOPPED'}")
            print(f"Invalidations:      {stats['invalidations']}")
            if stats['last_invalidation'] > 0:
                import datetime
                last_time = datetime.datetime.fromtimestamp(stats['last_invalidation'])
                print(f"Last Invalidation:  {last_time.isoformat()}")

        print("="*60 + "\n")

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


# ============================================================
# DEMO / TESTING
# ============================================================

def demo_watchdog_monitor():
    """Demonstrate watchdog monitoring"""
    import sys

    if not WATCHDOG_AVAILABLE:
        print("[ERROR] watchdog package not installed")
        print("        Install with: pip install watchdog")
        return

    # Get repo root
    if len(sys.argv) > 1:
        repo_root = Path(sys.argv[1])
    else:
        repo_root = Path(__file__).parent.parent.parent.parent

    cache_dir = repo_root / ".ssid_cache"

    print(f"Repository: {repo_root}")
    print(f"Cache Dir:  {cache_dir}\n")

    # Create result cache
    print("[INIT] Creating ResultCache...")
    from result_cache import ResultCache

    cache = ResultCache(
        cache_dir=cache_dir,
        repo_root=repo_root,
        ttl=3600
    )

    # Create and start monitor
    print("[INIT] Creating WatchdogCacheMonitor...")
    monitor = WatchdogCacheMonitor(
        result_cache=cache,
        repo_root=repo_root,
        verbose=True,
        recursive=True
    )

    print()
    monitor.start()
    print()

    # Monitor for changes
    print("[MONITOR] Watching for file changes...")
    print("          Modify a YAML/Python file to see invalidation")
    print("          Press Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(1)

            # Print stats every 10 seconds
            if int(time.time()) % 10 == 0:
                monitor.print_stats()

    except KeyboardInterrupt:
        print("\n[STOP] Stopping monitor...")

    # Stop monitor
    monitor.stop()
    print()

    # Final stats
    monitor.print_stats()

    print("[OK] Watchdog monitor demo complete!")


if __name__ == "__main__":
    demo_watchdog_monitor()
