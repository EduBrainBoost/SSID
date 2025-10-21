#!/usr/bin/env python3
"""Quick test of parallel validator - runs single batch"""

import sys
import time
from pathlib import Path

from parallel_validator import ParallelSoTValidator

# Get repo root
repo_root = Path(__file__).parent.parent.parent.parent

print(f"[TEST] Repository: {repo_root}")

# Create validator
validator = ParallelSoTValidator(
    repo_root=repo_root,
    max_workers=4,
    show_progress=False
)

print(f"[TEST] Testing batch 3 (6 rules: AR003, AR004, AR005, AR007, AR008, AR010)")

# Get batch 3 config
batch_config = validator.dependency_graph.get_batch(3)

# Execute batch
start = time.time()
results = validator._execute_batch(batch_config)
elapsed = time.time() - start

# Print results
print(f"\n[RESULTS]")
print(f"  Rules executed: {len(results)}")
print(f"  Passed: {sum(1 for r in results if r.passed)}")
print(f"  Failed: {sum(1 for r in results if not r.passed)}")
print(f"  Time: {elapsed:.3f}s")
print(f"  Throughput: {len(results)/elapsed:.1f} rules/s")

print("\n[OK] Quick test complete")
