"""
Performance Testing Configuration

Defines test scenarios, benchmarks, and SLAs for the Stock Portfolio Platform
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PerformanceBenchmark:
    """Performance benchmark definition"""
    name: str
    target_value: float
    unit: str
    description: str


@dataclass
class LoadTestScenario:
    """Load test scenario configuration"""
    name: str
    users: int
    spawn_rate: int
    duration: str  # e.g., "10m", "1h"
    description: str


# Performance Benchmarks and SLAs
BENCHMARKS = {
    'page_load_time': PerformanceBenchmark(
        name='Page Load Time',
        target_value=3.0,
        unit='seconds',
        description='Maximum time for page to fully load'
    ),
    'api_response_time': PerformanceBenchmark(
        name='API Response Time',
        target_value=0.5,
        unit='seconds',
        description='Maximum time for API endpoints to respond'
    ),
    'order_processing_time': PerformanceBenchmark(
        name='Order Processing Time',
        target_value=5.0,
        unit='seconds',
        description='Maximum time to process buy/sell orders'
    ),
    'throughput': PerformanceBenchmark(
        name='Throughput',
        target_value=50.0,
        unit='requests/second',
        description='Minimum requests per second the system should handle'
    ),
    'concurrent_users': PerformanceBenchmark(
        name='Concurrent Users',
        target_value=200.0,
        unit='users',
        description='Minimum concurrent users the system should support'
    ),
    'error_rate': PerformanceBenchmark(
        name='Error Rate',
        target_value=1.0,
        unit='percentage',
        description='Maximum acceptable error rate'
    ),
    'cpu_utilization': PerformanceBenchmark(
        name='CPU Utilization',
        target_value=80.0,
        unit='percentage',
        description='Maximum CPU utilization under load'
    ),
    'memory_utilization': PerformanceBenchmark(
        name='Memory Utilization',
        target_value=85.0,
        unit='percentage',
        description='Maximum memory utilization under load'
    )
}


# Load Test Scenarios
LOAD_TEST_SCENARIOS = {
    'baseline': LoadTestScenario(
        name='Baseline Test',
        users=10,
        spawn_rate=2,
        duration='5m',
        description='Baseline performance with minimal load'
    ),
    'normal': LoadTestScenario(
        name='Normal Load Test',
        users=100,
        spawn_rate=10,
        duration='10m',
        description='Expected normal operating load'
    ),
    'peak': LoadTestScenario(
        name='Peak Load Test',
        users=200,
        spawn_rate=20,
        duration='15m',
        description='Peak trading hours load'
    ),
    'stress': LoadTestScenario(
        name='Stress Test',
        users=500,
        spawn_rate=50,
        duration='10m',
        description='Stress test to identify breaking points'
    ),
    'spike': LoadTestScenario(
        name='Spike Test',
        users=1000,
        spawn_rate=100,
        duration='5m',
        description='Sudden traffic spike simulation'
    ),
    'endurance': LoadTestScenario(
        name='Endurance Test',
        users=150,
        spawn_rate=15,
        duration='2h',
        description='Extended duration test for stability'
    )
}


# Test Data Configuration
TEST_DATA_CONFIG = {
    'num_test_users': 10000,
    'num_test_companies': 500,
    'num_test_transactions': 1000000,
    'historical_data_years': 5,
    'test_symbols': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
}


# Monitoring Configuration
MONITORING_CONFIG = {
    'prometheus_port': 9090,
    'metrics_interval': 5,  # seconds
    'enable_profiling': True,
    'enable_memory_tracking': True,
    'enable_cpu_tracking': True,
    'log_level': 'INFO'
}


# Report Configuration
REPORT_CONFIG = {
    'output_dir': 'performance-testing/reports',
    'generate_html': True,
    'generate_csv': True,
    'generate_charts': True,
    'chart_format': 'png'
}


def get_scenario(scenario_name: str) -> LoadTestScenario:
    """Get load test scenario by name"""
    return LOAD_TEST_SCENARIOS.get(scenario_name)


def get_benchmark(benchmark_name: str) -> PerformanceBenchmark:
    """Get performance benchmark by name"""
    return BENCHMARKS.get(benchmark_name)


def get_all_scenarios() -> List[LoadTestScenario]:
    """Get all load test scenarios"""
    return list(LOAD_TEST_SCENARIOS.values())


def get_all_benchmarks() -> Dict[str, PerformanceBenchmark]:
    """Get all performance benchmarks"""
    return BENCHMARKS
