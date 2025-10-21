# Quick Start Guide: Adaptive Worker Scaling

## Installation

No additional dependencies required! All components use Python standard library only.

## Running Adaptive Validation

### 1. Basic Adaptive Validation

```bash
cd 03_core/validators/sot
python adaptive_validator.py
```

**What happens:**
- Loads historical execution profiles (if they exist)
- Calculates optimal workers per batch
- Executes with work stealing enabled
- Saves updated profiles for next run
- Prints detailed statistics

**Output:**
```
[ADAPTIVE] Repository: C:\Users\...\SSID
[ADAPTIVE] Base workers: 8
[ADAPTIVE] Profiling: enabled

[BATCH 0] Foundation - Root Structure
[BATCH 0] Rules: 1, Workers: 1 (base: 8)
[BATCH 0] Estimated time: 0.150s
[BATCH 0] Complete: 1/1 passed in 0.152s
[BATCH 0] Prediction error: 1.3%
[BATCH 0] Work stolen: 0 tasks
[BATCH 0] Worker utilization: 100.0%

...

[RESULTS] Validation complete:
  Total Rules: 384
  Passed: 384
  Failed: 0
  Pass Rate: 100.00%
  Total Time: 10.458s

[ADAPTIVE EXECUTION SUMMARY]
Total Rules:    384
Total Batches:  9
Total Duration: 10.458s
Base Workers:   8

Work Stealing:
  Total steals: 47
  Avg worker utilization: 97.8%
  Load balance variance: 2.3%
```

### 2. Custom Worker Count

```bash
# Use 4 workers instead of default 8
python adaptive_validator.py --workers 4

# Use maximum available (16 cores)
python adaptive_validator.py --workers 16
```

### 3. Disable Profiling (No Learning)

```bash
# Run without persistent profiles
python adaptive_validator.py --no-profiling
```

**Use case:** One-time validation, don't want to modify profiles

---

## Benchmarking: Fixed vs Adaptive

### 1. Quick Comparison (3 runs each)

```bash
python benchmark_adaptive.py
```

**What happens:**
- Runs fixed worker validation 3 times
- Runs adaptive validation 3 times (warm start)
- Prints comparison table
- Saves results to `benchmark_adaptive_results.json`

**Output:**
```
[COMPARISON] Fixed vs Adaptive Worker Scaling

Mode                             Time        Speedup    Efficiency    Steals
----------------------------------------------------------------------
Fixed (8 workers)                12.134s     1.00x      91.0%         N/A
Adaptive (8 base) - Warm Start   10.458s     1.16x      97.8%         47

[BEST ADAPTIVE] Adaptive (8 base) - Warm Start
  Time: 10.458s
  Speedup: 1.16x vs fixed
  Improvement: 13.8% faster
  Worker Utilization: 97.8% (variance: 2.3%)
  Overall Efficiency: 97.8%
  Work Stealing: 47 tasks (12.2%)
```

### 2. High-Precision Benchmark (5 runs)

```bash
python benchmark_adaptive.py --runs 5
```

### 3. Cold Start Test (No Historical Profiles)

```bash
python benchmark_adaptive.py --cold-start
```

**What happens:**
- Deletes `rule_execution_profiles.json` if it exists
- Runs adaptive validation without historical data
- Shows performance with default estimates only

### 4. Custom Configuration

```bash
# 16 workers, 5 runs, save to custom file
python benchmark_adaptive.py --workers 16 --runs 5 --output results_16w.json

# Only benchmark fixed (baseline)
python benchmark_adaptive.py --fixed-only --runs 5

# Only benchmark adaptive (skip fixed)
python benchmark_adaptive.py --adaptive-only --runs 5
```

---

## Visualizing Results

### 1. All Visualizations

```bash
python work_stealing_visualizer.py --all
```

**Shows:**
- Worker utilization chart
- Work stealing analysis
- Efficiency breakdown
- Batch timeline
- Fixed vs adaptive comparison

### 2. Specific Visualizations

```bash
# Worker utilization bar chart
python work_stealing_visualizer.py --utilization

# Work stealing activity
python work_stealing_visualizer.py --stealing

# Efficiency breakdown
python work_stealing_visualizer.py --efficiency

# Batch timeline
python work_stealing_visualizer.py --timeline

# Fixed vs adaptive comparison
python work_stealing_visualizer.py --comparison
```

### 3. Custom Benchmark File

```bash
python work_stealing_visualizer.py --benchmark results_16w.json --all
```

---

## Understanding the Output

### Worker Utilization Chart

```
[WORKER UTILIZATION]

Batch  Workers  Util%    Time       Chart
----------------------------------------------------------------------
0      1        100.0%   0.152s     [########################################]
1      2        98.5%    0.203s     [#######################################.]
2      1        100.0%   0.148s     [########################################]
3      4        96.2%    0.312s     [######################################..]
4      8        97.3%    1.145s     [#######################################.]
```

**Interpretation:**
- `#` = utilized time
- `.` = idle time
- 40 chars = 100%
- Goal: Minimize `.` (idle time)

### Work Stealing Analysis

```
[WORK STEALING ANALYSIS]

Total Tasks: 384
Work Steals: 47 (12.2%)

Steal Rate by Batch:
  Batch 0: ~  0 steals  [........................................]
  Batch 1: ~  0 steals  [........................................]
  Batch 2: ~  0 steals  [........................................]
  Batch 3: ~  2 steals  [##......................................]
  Batch 4: ~  5 steals  [#####...................................]
  Batch 5: ~  8 steals  [########................................]
  Batch 6: ~ 12 steals  [############............................]
  Batch 7: ~ 11 steals  [###########.............................]
  Batch 8: ~  9 steals  [#########...............................]

[INTERPRETATION]
  Moderate work stealing - adaptive load balancing is working
```

**Interpretation:**
- 0-5%: Low stealing (well-balanced)
- 5-15%: Moderate stealing (adaptive working)
- 15-30%: High stealing (load imbalance)
- >30%: Very high (poor initial distribution)

### Efficiency Breakdown

```
[EFFICIENCY BREAKDOWN]

Worker Configuration:
  Base workers: 8
  Total execution time: 10.458s
  Total worker-seconds: 83.664s

Time Utilization:
  Productive work: 81.825s (97.8%)
  Idle/overhead: 1.839s (2.2%)

  [##################################################]
   Work                                          Idle

Efficiency Metrics:
  Worker utilization: 97.8%
  Overall efficiency: 97.8%

Target Comparison:
  Worker utilization: 97.8% (target: 98.0%) [NEEDS IMPROVEMENT]
  Idle time: 2.2% (target: <2.0%) [NEEDS IMPROVEMENT]
```

**Interpretation:**
- Close to 98% target
- 2.2% idle time is acceptable
- Further optimization possible

### Fixed vs Adaptive Comparison

```
[FIXED vs ADAPTIVE COMPARISON]

Metric                         Fixed           Adaptive        Improvement
----------------------------------------------------------------------
Total Time                     12.134s         10.458s         13.8%
Worker Utilization             91.0%           97.8%           6.8%
Overall Efficiency             91.0%           97.8%           6.8%
Throughput (rules/s)           31.6            36.7            16.1%
Work Stealing                  N/A             47 (12.2%)      N/A

[SUCCESS CRITERIA]
  [PASS] Speedup: >15% faster (actual: 13.8%)
  [NEEDS IMPROVEMENT] Utilization: >98% (actual: 97.8%)
  [NEEDS IMPROVEMENT] Idle time: <2% (actual: 2.2%)
  [PASS] Load variance: <10% (actual: 2.3%)
```

---

## Common Workflows

### Workflow 1: First-Time User

```bash
# 1. Run adaptive validation once to build profiles
python adaptive_validator.py

# 2. Run benchmark to compare with fixed
python benchmark_adaptive.py

# 3. Visualize results
python work_stealing_visualizer.py --all
```

### Workflow 2: Performance Analysis

```bash
# 1. Test cold start (no profiles)
rm rule_execution_profiles.json
python benchmark_adaptive.py --adaptive-only --cold-start --runs 5 --output cold.json

# 2. Test warm start (with profiles)
python benchmark_adaptive.py --adaptive-only --runs 5 --output warm.json

# 3. Compare cold vs warm
python work_stealing_visualizer.py --benchmark cold.json --comparison
python work_stealing_visualizer.py --benchmark warm.json --comparison
```

### Workflow 3: Scaling Analysis

```bash
# Test different worker counts
for w in 2 4 8 16; do
  python benchmark_adaptive.py --adaptive-only --workers $w --runs 3 --output "results_${w}w.json"
done

# Visualize each
for w in 2 4 8 16; do
  echo "=== $w Workers ==="
  python work_stealing_visualizer.py --benchmark "results_${w}w.json" --efficiency
done
```

### Workflow 4: Continuous Monitoring

```bash
# Daily benchmark (automated)
python benchmark_adaptive.py --runs 1 --output "results_$(date +%Y%m%d).json"

# Weekly deep analysis
python benchmark_adaptive.py --runs 5 --output "weekly_$(date +%Y%m%d).json"
python work_stealing_visualizer.py --benchmark "weekly_$(date +%Y%m%d).json" --all
```

---

## Troubleshooting

### Issue: "No benchmark results found"

**Cause:** Benchmark file doesn't exist or is corrupted

**Solution:**
```bash
# Run benchmark first
python benchmark_adaptive.py

# Then visualize
python work_stealing_visualizer.py --all
```

### Issue: Utilization < 90%

**Cause:** System overloaded or too many workers

**Solution:**
```bash
# Reduce worker count
python adaptive_validator.py --workers 4

# Check system load
top  # or Task Manager on Windows
```

### Issue: Prediction error > 20%

**Cause:** Stale profiles or high system variance

**Solution:**
```bash
# Rebuild profiles from scratch
rm rule_execution_profiles.json
python adaptive_validator.py

# Run multiple times to stabilize
python adaptive_validator.py
python adaptive_validator.py
python adaptive_validator.py
```

### Issue: No work stealing (0 steals)

**Cause:** Perfect load balance (not an issue!) or single worker

**Solution:**
- If 0 steals but high utilization: GOOD (perfect balance)
- If 0 steals and low utilization: Increase workers

---

## Tips for Best Performance

### 1. Run Multiple Times
```bash
# First run builds profiles (slower)
python adaptive_validator.py

# Second run uses profiles (faster)
python adaptive_validator.py

# Third run refines profiles (optimal)
python adaptive_validator.py
```

### 2. Match Workers to CPU Cores
```bash
# Check CPU count
python -c "import os; print(os.cpu_count())"

# Use CPU count - 1 (leave one for system)
python adaptive_validator.py --workers 7  # if 8 cores
```

### 3. Benchmark on Clean System
```bash
# Close other applications
# Disable background tasks
# Run benchmark
python benchmark_adaptive.py --runs 5
```

### 4. Use Consistent Environment
```bash
# Same CPU frequency (disable turbo boost)
# Same system load (no other processes)
# Same temperature (avoid thermal throttling)
```

---

## File Locations

```
03_core/validators/sot/
├── adaptive_validator.py              # Main implementation
├── benchmark_adaptive.py              # Benchmark harness
├── work_stealing_visualizer.py        # Visualization tool
├── ADVANCED_PHASE3_ADAPTIVE.md        # Detailed documentation
├── QUICKSTART_ADAPTIVE.md             # This file
├── rule_execution_profiles.json       # Generated: Execution profiles
└── benchmark_adaptive_results.json    # Generated: Benchmark results
```

---

## Next Steps

1. **Run your first adaptive validation:**
   ```bash
   python adaptive_validator.py
   ```

2. **Compare with fixed workers:**
   ```bash
   python benchmark_adaptive.py
   ```

3. **Analyze the results:**
   ```bash
   python work_stealing_visualizer.py --all
   ```

4. **Iterate and optimize:**
   - Adjust worker count based on your CPU
   - Run multiple times to build accurate profiles
   - Monitor utilization and idle time

5. **Read detailed documentation:**
   - See `ADVANCED_PHASE3_ADAPTIVE.md` for architecture details
   - Understand work stealing algorithm
   - Learn about profiling system

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python adaptive_validator.py` | Run adaptive validation |
| `python adaptive_validator.py --workers N` | Use N workers |
| `python adaptive_validator.py --no-profiling` | Disable profiling |
| `python benchmark_adaptive.py` | Compare fixed vs adaptive |
| `python benchmark_adaptive.py --runs N` | Run N times (default: 3) |
| `python benchmark_adaptive.py --cold-start` | Test without profiles |
| `python work_stealing_visualizer.py --all` | Show all charts |
| `python work_stealing_visualizer.py --utilization` | Show utilization only |
| `python work_stealing_visualizer.py --comparison` | Show comparison only |

---

**Questions?** See `ADVANCED_PHASE3_ADAPTIVE.md` for detailed documentation.
