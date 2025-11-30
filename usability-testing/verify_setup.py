"""
Usability Testing Framework Verification Script
Verifies that all components are properly set up
"""

import sys
from pathlib import Path

def verify_files():
    """Verify all required files exist"""
    print("Verifying files...")
    
    required_files = [
        'config.py',
        'test_scenarios.py',
        'data_collector.py',
        'test_runner.py',
        'requirements.txt',
        'README.md',
        'QUICK_START.md',
        'SETUP_GUIDE.md',
        'TESTING_PROCEDURES.md',
        'PARTICIPANT_RECRUITMENT.md',
        'CONSENT_FORM.md',
        'templates/screening_survey.txt',
        'templates/email_templates.txt'
    ]
    
    missing_files = []
    for file in required_files:
        filepath = Path(__file__).parent / file
        if not filepath.exists():
            missing_files.append(file)
            print(f"  ❌ Missing: {file}")
        else:
            print(f"  ✅ Found: {file}")
    
    if missing_files:
        print(f"\n❌ {len(missing_files)} files missing!")
        return False
    else:
        print(f"\n✅ All {len(required_files)} files present!")
        return True

def verify_imports():
    """Verify all modules can be imported"""
    print("\nVerifying imports...")
    
    modules = [
        ('config', 'USABILITY_METRICS'),
        ('test_scenarios', 'TASK_BASED_SCENARIOS'),
        ('data_collector', 'UsabilityDataCollector')
    ]
    
    failed_imports = []
    for module_name, attr_name in modules:
        try:
            module = __import__(module_name)
            if hasattr(module, attr_name):
                print(f"  ✅ {module_name}.{attr_name}")
            else:
                print(f"  ❌ {module_name}.{attr_name} not found")
                failed_imports.append(f"{module_name}.{attr_name}")
        except ImportError as e:
            print(f"  ❌ Failed to import {module_name}: {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n❌ {len(failed_imports)} import failures!")
        return False
    else:
        print(f"\n✅ All imports successful!")
        return True

def verify_data_collector():
    """Verify data collector functionality"""
    print("\nVerifying data collector...")
    
    try:
        from data_collector import UsabilityDataCollector
        
        # Test initialization
        dc = UsabilityDataCollector()
        print("  ✅ Data collector initialized")
        
        # Test session start
        session_id = dc.start_session('TEST_P01', {
            'age': '25-35',
            'experience_level': 'Intermediate',
            'technical_proficiency': 'Medium'
        })
        print(f"  ✅ Session started: {session_id}")
        
        # Test data recording
        dc.record_task({
            'task_id': 'TEST-1',
            'name': 'Test Task',
            'duration': 120,
            'success': True
        })
        print("  ✅ Task recorded")
        
        dc.record_error('Test error', 'TEST-1')
        print("  ✅ Error recorded")
        
        dc.record_observation('Test observation', 'general')
        print("  ✅ Observation recorded")
        
        dc.record_satisfaction('Q1', 5)
        print("  ✅ Satisfaction recorded")
        
        # Test session end
        dc.end_session()
        print("  ✅ Session ended")
        
        # Verify file was created
        results_dir = Path(__file__).parent / 'results'
        if results_dir.exists():
            json_files = list(results_dir.glob('session_*.json'))
            if json_files:
                print(f"  ✅ Session file created: {json_files[-1].name}")
            else:
                print("  ⚠️  No session files found (this is OK for first run)")
        else:
            print("  ⚠️  Results directory will be created on first use")
        
        print("\n✅ Data collector working correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Data collector error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_test_scenarios():
    """Verify test scenarios"""
    print("\nVerifying test scenarios...")
    
    try:
        from test_scenarios import (
            EXPLORATORY_SCENARIOS,
            TASK_BASED_SCENARIOS,
            LEARNABILITY_SCENARIOS,
            get_scenario_by_id,
            get_scenarios_by_type
        )
        
        # Check exploratory scenarios
        exp_count = len(EXPLORATORY_SCENARIOS)
        print(f"  ✅ {exp_count} exploratory scenarios")
        
        # Check task-based scenarios
        task_count = len(TASK_BASED_SCENARIOS)
        print(f"  ✅ {task_count} task-based scenarios")
        
        # Check learnability scenarios
        learn_count = len(LEARNABILITY_SCENARIOS)
        print(f"  ✅ {learn_count} learnability scenarios")
        
        # Test scenario retrieval
        scenario = get_scenario_by_id('TASK-1')
        if scenario:
            print(f"  ✅ Scenario retrieval works: {scenario['name']}")
        else:
            print("  ❌ Scenario retrieval failed")
            return False
        
        # Test scenario filtering
        task_scenarios = get_scenarios_by_type('task_based')
        if len(task_scenarios) == task_count:
            print(f"  ✅ Scenario filtering works")
        else:
            print("  ❌ Scenario filtering failed")
            return False
        
        print(f"\n✅ All {exp_count + task_count + learn_count} scenarios verified!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test scenarios error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_config():
    """Verify configuration"""
    print("\nVerifying configuration...")
    
    try:
        from config import (
            USABILITY_METRICS,
            TEST_SCENARIOS,
            PARTICIPANT_CRITERIA,
            RECORDING_TOOLS,
            TEST_ENVIRONMENT,
            SATISFACTION_SURVEY
        )
        
        # Check metrics
        metrics = list(USABILITY_METRICS.keys())
        print(f"  ✅ {len(metrics)} metrics defined: {', '.join(metrics)}")
        
        # Check test scenarios
        scenarios = list(TEST_SCENARIOS.keys())
        print(f"  ✅ {len(scenarios)} scenario types: {', '.join(scenarios)}")
        
        # Check participant criteria
        if 'count' in PARTICIPANT_CRITERIA:
            print(f"  ✅ Participant criteria defined")
        
        # Check recording tools
        tools = list(RECORDING_TOOLS.keys())
        print(f"  ✅ {len(tools)} recording tool categories")
        
        # Check test environment
        if 'url' in TEST_ENVIRONMENT:
            print(f"  ✅ Test environment configured: {TEST_ENVIRONMENT['url']}")
        
        # Check satisfaction survey
        questions = len(SATISFACTION_SURVEY['questions'])
        print(f"  ✅ {questions} satisfaction survey questions")
        
        print("\n✅ Configuration verified!")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verification checks"""
    print("=" * 60)
    print("USABILITY TESTING FRAMEWORK VERIFICATION")
    print("=" * 60)
    print()
    
    results = []
    
    # Run all checks
    results.append(("Files", verify_files()))
    results.append(("Imports", verify_imports()))
    results.append(("Configuration", verify_config()))
    results.append(("Test Scenarios", verify_test_scenarios()))
    results.append(("Data Collector", verify_data_collector()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    for check_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name:.<40} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL CHECKS PASSED!")
        print("\nThe usability testing framework is ready to use.")
        print("\nNext steps:")
        print("1. Read QUICK_START.md to get started")
        print("2. Run: python test_runner.py")
        print("3. Follow the on-screen prompts")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\nPlease review the errors above and fix any issues.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
