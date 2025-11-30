# Performance Testing Suite

Comprehensive performance testing framework for the Stock Portfolio Management Platform.

## Overview

This suite includes:
- **Load Testing**: Test with expected user loads
- **Stress Testing**: Identify system breaking points
- **Spike Testing**: Test sudden traffic increases
- **Volume Testing**: Test with large datasets
- **Scalability Testing**: Test horizontal and vertical scaling
- **Endurance Testing**: Test system stability over time

## Setup

### 1. Install Dependencies

```bash
pip install -r performance-testing/requirements.txt
```

### 2. Generate Test Data

```bash
python performance-testing/test_data_generator.py
```

This generates:
- 10,000 test users
- 500 test companies
- 5 years of price history
- 1,000,000 test transactions

### 3. Configure Tests

Edit `performance-testing/config.py` to adjust:
- Performance benchmarks
- Load test scenarios
- Monitoring settings

## Running Tests

### Basic Load Test

```bash
locust -f performance-testing/locustfile.py --host=http://localhost:5000
```

Then open http://localhost:8089 in your browser to configure and start the test.

### Command Line Tests

#### Normal Load Test (100 users)
```bash
locust -f performance-testing/locustfile.py \
    --host=http://localhost:5000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 10m \
    --html=performance-testing/reports/load_test_report.html
```

#### Stress Test (500 users)
```bash
locust -f performance-testing/locustfile.py \
    --host=http://localhost:5000 \
    --users 500 \
    --spawn-rate 50 \
    --run-time 10m \
    --html=performance-testing/reports/stress_test_report.html
```

#### Spike Test (1000 users)
```bash
locust -f performance-testing/locustfile.py \
    --host=http://localhost:5000 \
    --users 1000 \
    --spawn-rate 100 \
    --run-time 5m \
    --html=performance-testing/reports/spike_test_report.html
```

### Headless Mode

Run tests without the web UI:

```bash
locust -f performance-testing/locustfile.py \
    --host=http://localhost:5000 \
    --users 100 \
    --spawn-rate 10 \
    --run-time 10m \
    --headless \
    --html=performance-testing/reports/report.html \
    --csv=performance-testing/reports/results
```

## Monitoring

### System Metrics

Monitor system resources during tests:

```bash
python performance-testing/monitoring.py
```

This tracks:
- CPU utilization
- Memory usage
- Disk I/O
- Network I/O

### Real-time Monitoring

While tests are running, monitor in real-time:

```bash
# Terminal 1: Run the test
locust -f performance-testing/locustfile.py --host=http://localhost:5000

# Terminal 2: Monitor system metrics
python performance-testing/monitoring.py
```

## Performance Benchmarks

### Target Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Page Load Time | < 3s | Maximum time for page to fully load |
| API Response Time | < 500ms | Maximum time for API endpoints |
| Order Processing | < 5s | Maximum time to process orders |
| Throughput | 50 req/s | Minimum requests per second |
| Concurrent Users | 200+ | Minimum concurrent users supported |
| Error Rate | < 1% | Maximum acceptable error rate |
| CPU Utilization | < 80% | Maximum CPU usage under load |
| Memory Utilization | < 85% | Maximum memory usage under load |

## Test Scenarios

### 1. Baseline Test
- **Users**: 10
- **Duration**: 5 minutes
- **Purpose**: Establish baseline performance

### 2. Normal Load Test
- **Users**: 100
- **Duration**: 10 minutes
- **Purpose**: Test expected normal load

### 3. Peak Load Test
- **Users**: 200
- **Duration**: 15 minutes
- **Purpose**: Test peak trading hours

### 4. Stress Test
- **Users**: 500
- **Duration**: 10 minutes
- **Purpose**: Identify breaking points

### 5. Spike Test
- **Users**: 1000
- **Duration**: 5 minutes
- **Purpose**: Test sudden traffic spikes

### 6. Endurance Test
- **Users**: 150
- **Duration**: 2 hours
- **Purpose**: Test long-term stability

## User Simulation

The test suite simulates different user types:

### Portfolio User (70% of traffic)
- View dashboard
- Check portfolio
- View orders
- Place buy orders
- View reports

### Prediction User (20% of traffic)
- View dashboard
- Get stock predictions
- View portfolio

### Admin User (10% of traffic)
- View admin dashboard
- Manage users
- View companies
- Monitor system

### API User (5% of traffic)
- API-only requests
- Stock price lookups
- Portfolio queries

## Reports

Test reports are generated in `performance-testing/reports/`:

- **HTML Report**: Visual report with charts
- **CSV Files**: Raw data for analysis
- **Metrics JSON**: System metrics during test

### Analyzing Results

1. **Response Times**: Check 50th, 95th, and 99th percentiles
2. **Error Rate**: Should be < 1%
3. **Throughput**: Should meet 50 req/s target
4. **Resource Usage**: CPU and memory should stay within limits

## Troubleshooting

### High Error Rates

If error rates are high:
1. Check application logs
2. Verify database connections
3. Check for rate limiting
4. Review error types in report

### Slow Response Times

If response times are slow:
1. Check database query performance
2. Review application logs
3. Check system resources
4. Profile slow endpoints

### System Resource Issues

If CPU/memory is high:
1. Check for memory leaks
2. Review database connection pooling
3. Check for inefficient queries
4. Consider scaling resources

## Best Practices

1. **Start Small**: Begin with baseline tests
2. **Incremental Load**: Gradually increase load
3. **Monitor Resources**: Watch CPU, memory, disk, network
4. **Analyze Results**: Review reports after each test
5. **Optimize**: Fix issues before increasing load
6. **Document**: Record findings and optimizations

## Integration with CI/CD

Add performance tests to your CI/CD pipeline:

```yaml
# Example GitHub Actions workflow
performance-test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v2
    - name: Install dependencies
      run: pip install -r performance-testing/requirements.txt
    - name: Run load test
      run: |
        locust -f performance-testing/locustfile.py \
          --host=http://localhost:5000 \
          --users 100 \
          --spawn-rate 10 \
          --run-time 5m \
          --headless \
          --html=report.html
    - name: Upload report
      uses: actions/upload-artifact@v2
      with:
        name: performance-report
        path: report.html
```

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review test logs
3. Consult the main project documentation
