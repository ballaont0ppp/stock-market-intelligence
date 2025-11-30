# Performance Testing - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Install (1 minute)

```bash
pip install -r performance-testing/requirements.txt
```

### Step 2: Generate Data (2 minutes)

```bash
python performance-testing/test_data_generator.py
```

### Step 3: Run Test (2 minutes)

```bash
python performance-testing/run_tests.py --quick
```

---

## 📊 Common Commands

### Run Specific Test

```bash
# Baseline (10 users, 5 min)
python performance-testing/run_tests.py --scenario baseline

# Normal load (100 users, 10 min)
python performance-testing/run_tests.py --scenario normal

# Stress test (500 users, 10 min)
python performance-testing/run_tests.py --scenario stress
```

### Run All Tests

```bash
python performance-testing/run_tests.py --all
```

### Run with Web UI

```bash
python performance-testing/run_tests.py --scenario normal --ui
# Then open http://localhost:8089
```

---

## 📈 View Results

Reports are saved in `performance-testing/reports/`:

```bash
# Open latest HTML report
open performance-testing/reports/*.html

# View metrics
cat performance-testing/reports/*_metrics.json
```

---

## 🎯 Performance Targets

| Metric | Target |
|--------|--------|
| Page Load | < 3s |
| API Response | < 500ms |
| Order Processing | < 5s |
| Throughput | 50+ req/s |
| Concurrent Users | 200+ |
| Error Rate | < 1% |

---

## 🔧 Troubleshooting

### Locust not found
```bash
pip install locust
```

### Port already in use
```bash
# Kill existing Locust process
pkill -f locust
```

### Application not running
```bash
# Start the application first
python run.py
```

---

## 📚 More Information

- Full documentation: `performance-testing/README.md`
- Configuration: `performance-testing/config.py`
- Implementation summary: `TASK_21_PERFORMANCE_TESTING_SUMMARY.md`
