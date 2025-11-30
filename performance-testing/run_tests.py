"""
Performance Test Runner

Automates execution of all performance test scenarios
"""

import subprocess
import sys
import os
from datetime import datetime
from config import LOAD_TEST_SCENARIOS, get_all_scenarios
from monitoring import PerformanceMonitor
import time


class PerformanceTestRunner:
    """Run performance tests and collect results"""
    
    def __init__(self, host='http://localhost:5000'):
        self.host = host
        self.reports_dir = 'performance-testing/reports'
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def run_scenario(self, scenario_name, headless=True):
        """
        Run a specific test scenario
        
        Args:
            scenario_name: Name of the scenario from config
            headless: Run without web UI
        """
        scenario = LOAD_TEST_SCENARIOS.get(scenario_name)
        if not scenario:
            print(f"Error: Scenario '{scenario_name}' not found")
            return False
        
        print(f"\n{'='*60}")
        print(f"Running: {scenario.name}")
        print(f"Description: {scenario.description}")
        print(f"Users: {scenario.users}, Spawn Rate: {scenario.spawn_rate}")
        print(f"Duration: {scenario.duration}")
        print(f"{'='*60}\n")
        
        # Generate report filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_prefix = f"{self.reports_dir}/{scenario_name}_{timestamp}"
        
        # Build locust command
        cmd = [
            'locust',
            '-f', 'performance-testing/locustfile.py',
            '--host', self.host,
            '--users', str(scenario.users),
            '--spawn-rate', str(scenario.spawn_rate),
            '--run-time', scenario.duration,
            '--html', f'{report_prefix}.html',
            '--csv', report_prefix
        ]
        
        if headless:
            cmd.append('--headless')
        
        # Start monitoring
        monitor = PerformanceMonitor(interval=5)
        monitor.start_monitoring()
        
        try:
            # Run the test
            result = subprocess.run(cmd, check=True)
            success = result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"Error running test: {e}")
            success = False
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
            success = False
        finally:
            # Stop monitoring and save metrics
            monitor.stop_monitoring()
            monitor.export_metrics(f'{report_prefix}_metrics.json')
            
            # Print summary
            summary = monitor.get_metrics_summary()
            print("\n=== System Metrics Summary ===")
            print(f"CPU Average: {summary['cpu']['avg']}%")
            print(f"CPU Max: {summary['cpu']['max']}%")
            print(f"Memory Average: {summary['memory']['avg']}%")
            print(f"Memory Max: {summary['memory']['max']}%")
        
        if success:
            print(f"\n✓ Test completed successfully")
            print(f"Report: {report_prefix}.html")
        else:
            print(f"\n✗ Test failed")
        
        return success
    
    def run_all_scenarios(self, headless=True):
        """Run all test scenarios"""
        print("\n" + "="*60)
        print("RUNNING ALL PERFORMANCE TEST SCENARIOS")
        print("="*60)
        
        scenarios = ['baseline', 'normal', 'peak', 'stress']
        results = {}
        
        for scenario_name in scenarios:
            success = self.run_scenario(scenario_name, headless=headless)
            results[scenario_name] = success
            
            # Wait between tests
            if scenario_name != scenarios[-1]:
                print("\nWaiting 30 seconds before next test...")
                time.sleep(30)
        
        # Print final summary
        print("\n" + "="*60)
        print("PERFORMANCE TEST SUMMARY")
        print("="*60)
        for scenario_name, success in results.items():
            status = "✓ PASSED" if success else "✗ FAILED"
            print(f"{scenario_name.upper()}: {status}")
        
        all_passed = all(results.values())
        if all_passed:
            print("\n✓ All performance tests passed!")
        else:
            print("\n✗ Some performance tests failed")
        
        return all_passed
    
    def run_quick_test(self):
        """Run a quick smoke test"""
        print("\nRunning quick performance smoke test...")
        return self.run_scenario('baseline', headless=True)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run performance tests')
    parser.add_argument('--host', default='http://localhost:5000',
                       help='Target host URL')
    parser.add_argument('--scenario', choices=list(LOAD_TEST_SCENARIOS.keys()),
                       help='Run specific scenario')
    parser.add_argument('--all', action='store_true',
                       help='Run all scenarios')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick smoke test')
    parser.add_argument('--ui', action='store_true',
                       help='Run with web UI (not headless)')
    
    args = parser.parse_args()
    
    runner = PerformanceTestRunner(host=args.host)
    headless = not args.ui
    
    if args.quick:
        success = runner.run_quick_test()
    elif args.all:
        success = runner.run_all_scenarios(headless=headless)
    elif args.scenario:
        success = runner.run_scenario(args.scenario, headless=headless)
    else:
        print("Please specify --scenario, --all, or --quick")
        parser.print_help()
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
