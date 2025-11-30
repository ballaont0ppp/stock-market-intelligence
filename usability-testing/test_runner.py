"""
Usability Test Runner
Interactive script to conduct usability testing sessions
"""

import sys
from datetime import datetime
from typing import Dict, Any
from data_collector import UsabilityDataCollector
from test_scenarios import (
    UsabilityTestScenario,
    get_scenario_by_id,
    get_scenarios_by_type,
    TASK_BASED_SCENARIOS
)
from config import SATISFACTION_SURVEY, USABILITY_METRICS


class UsabilityTestRunner:
    """Runs usability testing sessions"""
    
    def __init__(self):
        self.collector = UsabilityDataCollector()
        self.current_participant = None
    
    def run_session(self):
        """Run a complete usability testing session"""
        print("=" * 60)
        print("USABILITY TESTING SESSION")
        print("=" * 60)
        print()
        
        # Collect participant information
        self.current_participant = self._collect_participant_info()
        
        # Start session
        session_id = self.collector.start_session(
            self.current_participant['id'],
            self.current_participant['demographics']
        )
        
        print(f"\nSession ID: {session_id}")
        print(f"Participant: {self.current_participant['id']}")
        print()
        
        # Choose test type
        test_type = self._choose_test_type()
        
        if test_type == '1':
            self._run_exploratory_testing()
        elif test_type == '2':
            self._run_task_based_testing()
        elif test_type == '3':
            self._run_learnability_testing()
        
        # Collect satisfaction survey
        self._collect_satisfaction_survey()
        
        # End session
        self.collector.end_session()
        
        print("\n" + "=" * 60)
        print("SESSION COMPLETE")
        print("=" * 60)
        print(f"\nResults saved to: usability-testing/results/{session_id}.json")
    
    def _collect_participant_info(self) -> Dict[str, Any]:
        """Collect participant demographic information"""
        print("PARTICIPANT INFORMATION")
        print("-" * 60)
        
        participant_id = input("Participant ID: ").strip()
        age = input("Age: ").strip()
        
        print("\nExperience Level:")
        print("1. Novice (no stock trading experience)")
        print("2. Intermediate (some trading experience)")
        print("3. Expert (regular trader)")
        experience = input("Select (1-3): ").strip()
        
        experience_map = {
            '1': 'Novice',
            '2': 'Intermediate',
            '3': 'Expert'
        }
        
        print("\nTechnical Proficiency:")
        print("1. Low (basic computer skills)")
        print("2. Medium (comfortable with web apps)")
        print("3. High (tech-savvy)")
        proficiency = input("Select (1-3): ").strip()
        
        proficiency_map = {
            '1': 'Low',
            '2': 'Medium',
            '3': 'High'
        }
        
        return {
            'id': participant_id,
            'demographics': {
                'age': age,
                'experience_level': experience_map.get(experience, 'Unknown'),
                'technical_proficiency': proficiency_map.get(proficiency, 'Unknown')
            }
        }
    
    def _choose_test_type(self) -> str:
        """Choose the type of usability test"""
        print("\nTEST TYPE")
        print("-" * 60)
        print("1. Exploratory Testing (open-ended exploration)")
        print("2. Task-Based Testing (specific tasks with time targets)")
        print("3. Learnability Testing (complete workflow)")
        
        choice = input("\nSelect test type (1-3): ").strip()
        return choice
    
    def _run_exploratory_testing(self):
        """Run exploratory usability testing"""
        print("\n" + "=" * 60)
        print("EXPLORATORY TESTING")
        print("=" * 60)
        print("\nInstructions:")
        print("- Allow the participant to explore freely")
        print("- Encourage think-aloud protocol")
        print("- Record observations and pain points")
        print("- Duration: 30 minutes")
        print()
        
        input("Press Enter when ready to start...")
        
        start_time = datetime.now()
        
        print("\nTesting in progress...")
        print("Record observations as they occur.")
        print("Type 'done' when testing is complete.")
        print()
        
        while True:
            observation = input("Observation (or 'done'): ").strip()
            if observation.lower() == 'done':
                break
            if observation:
                self.collector.record_observation(observation, 'exploratory')
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\nExploratory testing completed in {duration:.0f} seconds")
    
    def _run_task_based_testing(self):
        """Run task-based usability testing"""
        print("\n" + "=" * 60)
        print("TASK-BASED TESTING")
        print("=" * 60)
        print()
        
        for scenario in TASK_BASED_SCENARIOS:
            self._run_task(scenario)
    
    def _run_task(self, scenario: Dict[str, Any]):
        """Run a single task scenario"""
        print("\n" + "-" * 60)
        print(f"TASK: {scenario['name']}")
        print("-" * 60)
        print(f"Description: {scenario['description']}")
        print(f"Target Time: {scenario['target_time']} seconds")
        print("\nInstructions:")
        for instruction in scenario['instructions']:
            print(f"  - {instruction}")
        print()
        
        input("Press Enter when participant is ready to start...")
        
        start_time = datetime.now()
        print(f"\nTask started at {start_time.strftime('%H:%M:%S')}")
        print("Timer running... Press Enter when task is complete.")
        
        input()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\nTask completed in {duration:.1f} seconds")
        print(f"Target was {scenario['target_time']} seconds")
        
        # Record success
        success = input("Was the task completed successfully? (y/n): ").strip().lower() == 'y'
        
        # Record errors
        error_count = input("How many errors occurred? (0 if none): ").strip()
        try:
            error_count = int(error_count)
            for i in range(error_count):
                error = input(f"  Error {i+1}: ").strip()
                if error:
                    self.collector.record_error(error, scenario['id'])
        except ValueError:
            pass
        
        # Record observations
        observation = input("Any observations? (press Enter to skip): ").strip()
        if observation:
            self.collector.record_observation(observation, scenario['id'])
        
        # Save task data
        task_data = {
            'task_id': scenario['id'],
            'name': scenario['name'],
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration': duration,
            'target_time': scenario['target_time'],
            'success': success,
            'error_count': error_count if isinstance(error_count, int) else 0
        }
        
        self.collector.record_task(task_data)
        
        # Show status
        status = "✅ PASS" if success and duration <= scenario['target_time'] else "❌ FAIL"
        print(f"\nStatus: {status}")
    
    def _run_learnability_testing(self):
        """Run learnability testing"""
        print("\n" + "=" * 60)
        print("LEARNABILITY TESTING")
        print("=" * 60)
        print("\nInstructions:")
        print("- Participant completes a full workflow")
        print("- Measure time to proficiency")
        print("- Target: < 10 minutes")
        print()
        
        input("Press Enter when ready to start...")
        
        start_time = datetime.now()
        
        print("\nWorkflow:")
        print("1. Register a new account")
        print("2. Explore the dashboard")
        print("3. Buy a stock")
        print("4. View portfolio")
        print("5. Generate a report")
        print("6. Sell the stock")
        print()
        
        input("Press Enter when workflow is complete...")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"\nWorkflow completed in {duration:.0f} seconds ({duration/60:.1f} minutes)")
        print(f"Target was 600 seconds (10 minutes)")
        
        success = input("Was the workflow completed successfully? (y/n): ").strip().lower() == 'y'
        
        task_data = {
            'task_id': 'LEARN-1',
            'name': 'Complete Workflow',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration': duration,
            'target_time': 600,
            'success': success
        }
        
        self.collector.record_task(task_data)
        
        status = "✅ PASS" if success and duration <= 600 else "❌ FAIL"
        print(f"\nStatus: {status}")
    
    def _collect_satisfaction_survey(self):
        """Collect satisfaction survey responses"""
        print("\n" + "=" * 60)
        print("SATISFACTION SURVEY")
        print("=" * 60)
        print()
        
        for question in SATISFACTION_SURVEY['questions']:
            print(f"\n{question['question']}")
            
            if question['type'] == 'likert':
                print(f"Scale: {question['scale']}")
                response = input("Score: ").strip()
                try:
                    score = int(response)
                    self.collector.record_satisfaction(question['id'], score)
                except ValueError:
                    print("Invalid score, skipping...")
            
            elif question['type'] == 'open_ended':
                response = input("Response: ").strip()
                if response:
                    self.collector.record_feedback(question['id'], response)


def main():
    """Main entry point"""
    runner = UsabilityTestRunner()
    
    while True:
        print("\n" + "=" * 60)
        print("USABILITY TESTING MENU")
        print("=" * 60)
        print("1. Run new testing session")
        print("2. View results summary")
        print("3. Generate report")
        print("4. Export to CSV")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            runner.run_session()
        elif choice == '2':
            metrics = runner.collector.calculate_metrics()
            print("\n" + "=" * 60)
            print("RESULTS SUMMARY")
            print("=" * 60)
            print(f"\nTotal Sessions: {metrics.get('total_sessions', 0)}")
            print(f"Task Success Rate: {metrics.get('task_success_rate', 0):.1%}")
            print(f"Error Rate: {metrics.get('error_rate', 0):.1%}")
            print(f"\nAverage Task Times:")
            for task_id, avg_time in metrics.get('average_task_times', {}).items():
                print(f"  {task_id}: {avg_time:.1f}s")
        elif choice == '3':
            runner.collector.generate_report()
            print("\nReport generated: usability-testing/results/usability_report.md")
        elif choice == '4':
            runner.collector.export_to_csv()
            print("\nData exported: usability-testing/results/usability_results.csv")
        elif choice == '5':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid option, please try again.")


if __name__ == '__main__':
    main()
