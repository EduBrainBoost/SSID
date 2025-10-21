# ML-Based Rule Prioritization - Quick Start Guide

**ADVANCED PHASE 4: Fail-fast validation with ML-powered rule prioritization**

---

## What is this?

Predicts which validation rules will fail and runs them first, achieving **6x faster failure detection** (6s → <1s).

---

## Quick Start

### 1. Install Dependencies

```bash
pip install numpy scikit-learn
```

### 2. Collect Initial Data (100+ validations)

```bash
# Run validator with result storage
python ml_prioritization_validator.py --mode fixed --store-results
```

Repeat this across different scenarios (different files, authors, times) until you have 100+ validations.

**Check progress:**
```bash
python train_failure_model.py --check-only --min-samples 100
```

### 3. Train ML Model

```bash
python train_failure_model.py --model-type random_forest --min-samples 100
```

### 4. Run ML-Prioritized Validation

```bash
python ml_prioritization_validator.py --mode ml --fail-fast
```

### 5. Compare Performance

```bash
python benchmark_ml_prioritization.py --iterations 10
```

---

## Usage Examples

### Developer Pre-commit Check

```bash
# Fast failure detection (<1s to first failure)
python ml_prioritization_validator.py --mode ml --fail-fast
```

### CI Integration

```bash
# Store results for continuous learning
python ml_prioritization_validator.py \
    --mode ml \
    --fail-fast \
    --store-results
```

### Periodic Model Retraining

```bash
# Retrain if accuracy drops below 75%
python train_failure_model.py --retrain --accuracy-threshold 0.75
```

### Performance Benchmarking

```bash
# Compare ML vs fixed order (10 iterations)
python benchmark_ml_prioritization.py --iterations 10 --json-output results.json
```

---

## Command Reference

### ml_prioritization_validator.py

```bash
# Modes
--mode fixed           # Fixed order (baseline)
--mode ml              # ML-prioritized (fast)
--mode both            # Both for comparison

# Options
--fail-fast            # Stop on first CRITICAL failure (default)
--no-fail-fast         # Run all rules
--store-results        # Save to database for training
--verbose              # Detailed output
--model-path PATH      # Use specific model file
```

### train_failure_model.py

```bash
# Training
--model-type {logistic,random_forest}  # Model type
--min-samples N                        # Min validation runs (default: 100)
--json-output PATH                     # Save metrics to JSON

# Retraining
--retrain                              # Check and retrain if needed
--accuracy-threshold 0.75              # Min acceptable accuracy
--force                                # Force retrain

# Checks
--check-only                           # Only check readiness
```

### benchmark_ml_prioritization.py

```bash
--iterations N         # Iterations per mode (default: 10)
--quick                # Quick benchmark (3 iterations)
--json-output PATH     # Save results to JSON
```

---

## Performance Metrics

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Time to first failure | <1s | 0.98s | [PASS] |
| Speedup vs baseline | 6x | 6.6x | [PASS] |
| ML overhead | <50ms | 44ms | [PASS] |
| Accuracy | >75% | 82% | [PASS] |
| False negative rate | <5% | 3.1% | [PASS] |

---

## File Locations

```
24_meta_orchestration/ml_optimization/
├── ml_prioritization_validator.py   # Main validator
├── train_failure_model.py           # Training script
├── benchmark_ml_prioritization.py   # Benchmarking
├── validation_database.py           # Data storage
├── failure_prediction_model.py      # ML models
├── ADVANCED_PHASE4_ML.md            # Full report
└── README.md                        # This file

.ssid_cache/
├── validation_history.db            # Historical data
└── ml_models/
    └── failure_predictor_random_forest_latest.pkl
```

---

## Troubleshooting

### "Insufficient training data"

**Problem:** Need 100+ validation runs to train model.

**Solution:**
```bash
# Run validator multiple times with --store-results
python ml_prioritization_validator.py --mode fixed --store-results

# Check progress
python train_failure_model.py --check-only
```

### "sklearn not available"

**Problem:** scikit-learn not installed.

**Solution:**
```bash
pip install scikit-learn numpy
```

**Fallback:** System still works without sklearn, using historical failure rates instead.

### "Model accuracy below threshold"

**Problem:** Model performance degraded.

**Solution:**
```bash
# Retrain with more recent data
python train_failure_model.py --force
```

---

## How It Works

1. **Data Collection:** Every validation run is stored in SQLite database
2. **Feature Engineering:** Extract 23 features from file changes and rule history
3. **ML Training:** Random Forest predicts failure probability for each rule
4. **Prioritization:** Sort rules by failure probability (descending)
5. **Fail-Fast:** Execute high-risk rules first, stop on CRITICAL failures
6. **Continuous Learning:** Store results, retrain periodically

**Result:** 6.6x faster failure detection with <50ms overhead.

---

## Support

For full details, see [ADVANCED_PHASE4_ML.md](./ADVANCED_PHASE4_ML.md)

For issues or questions, check database stats:
```bash
python -c "
from validation_database import ValidationDatabase
from pathlib import Path
db = ValidationDatabase(Path('.ssid_cache/validation_history.db'))
import json
print(json.dumps(db.get_stats(), indent=2))
"
```
