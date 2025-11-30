"""
Usability Testing Data Collector
Collects and stores usability testing data
"""

import json
import csv
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path


class UsabilityDataCollector:
    """Collects and manages usability testing data"""
    
    def __init__(self, output_dir: str = 'usability-testing/results'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = None
    
    def start_session(self, participant_id: str, demographics: Dict[str, Any]) -> str:
        """Start a new testing session"""
        session_id = f"session_{participant_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = {
            'session_id': session_id,
            'participant_id': participant_id,
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'demographics': demographics,
            'tasks': [],
            'errors': [],
            'observations': [],
            'satisfaction_scores': {},
            'feedback': {}
        }
        
        return session_id
    
    def end_session(self):
        """End the current testing session"""
        if self.current_session:
            self.current_session['end_time'] = datetime.now().isoformat()
            self._save_session()
    
    def record_task(self, task_data: Dict[str, Any]):
        """Record task completion data"""
        if self.current_session:
            self.current_session['tasks'].append(task_data)
    
    def record_error(self, error: str, context: str = ''):
        """Record an error encountered during testing"""
        if self.current_session:
            self.current_session['errors'].append({
                'timestamp': datetime.now().isoformat(),
                'error': error,
                'context': context
            })
    
    def record_observation(self, observation: str, category: str = 'general'):
        """Record an observation during testing"""
        if self.current_session:
            self.current_session['observations'].append({
                'timestamp': datetime.now().isoformat(),
                'observation': observation,
                'category': category
            })
    
    def record_satisfaction(self, question_id: str, score: Any):
        """Record satisfaction survey response"""
        if self.current_session:
            self.current_session['satisfaction_scores'][question_id] = score
    
    def record_feedback(self, question_id: str, response: str):
        """Record open-ended feedback"""
        if self.current_session:
            self.current_session['feedback'][question_id] = response
    
    def _save_session(self):
        """Save session data to file"""
        if self.current_session:
            filename = f"{self.current_session['session_id']}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(self.current_session, f, indent=2)
    
    def load_session(self, session_id: str) -> Dict[str, Any]:
        """Load a saved session"""
        filepath = self.output_dir / f"{session_id}.json"
        
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Load all saved sessions"""
        sessions = []
        for filepath in self.output_dir.glob('session_*.json'):
            with open(filepath, 'r') as f:
                sessions.append(json.load(f))
        return sessions
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate aggregate metrics from all sessions"""
        sessions = self.get_all_sessions()
        
        if not sessions:
            return {}
        
        metrics = {
            'total_sessions': len(sessions),
            'task_success_rate': self._calculate_success_rate(sessions),
            'average_task_times': self._calculate_average_times(sessions),
            'error_rate': self._calculate_error_rate(sessions),
            'average_satisfaction': self._calculate_average_satisfaction(sessions),
            'common_issues': self._identify_common_issues(sessions)
        }
        
        return metrics
    
    def _calculate_success_rate(self, sessions: List[Dict[str, Any]]) -> float:
        """Calculate overall task success rate"""
        total_tasks = 0
        successful_tasks = 0
        
        for session in sessions:
            for task in session.get('tasks', []):
                total_tasks += 1
                if task.get('success', False):
                    successful_tasks += 1
        
        return successful_tasks / total_tasks if total_tasks > 0 else 0
    
    def _calculate_average_times(self, sessions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average time for each task"""
        task_times = {}
        
        for session in sessions:
            for task in session.get('tasks', []):
                task_id = task.get('task_id', 'unknown')
                duration = task.get('duration', 0)
                
                if task_id not in task_times:
                    task_times[task_id] = []
                task_times[task_id].append(duration)
        
        return {
            task_id: sum(times) / len(times)
            for task_id, times in task_times.items()
        }
    
    def _calculate_error_rate(self, sessions: List[Dict[str, Any]]) -> float:
        """Calculate overall error rate"""
        total_actions = 0
        total_errors = 0
        
        for session in sessions:
            total_actions += len(session.get('tasks', []))
            total_errors += len(session.get('errors', []))
        
        return total_errors / total_actions if total_actions > 0 else 0
    
    def _calculate_average_satisfaction(self, sessions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average satisfaction scores"""
        satisfaction_scores = {}
        
        for session in sessions:
            for question_id, score in session.get('satisfaction_scores', {}).items():
                if isinstance(score, (int, float)):
                    if question_id not in satisfaction_scores:
                        satisfaction_scores[question_id] = []
                    satisfaction_scores[question_id].append(score)
        
        return {
            question_id: sum(scores) / len(scores)
            for question_id, scores in satisfaction_scores.items()
        }
    
    def _identify_common_issues(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify common usability issues"""
        issue_counts = {}
        
        for session in sessions:
            for error in session.get('errors', []):
                error_text = error.get('error', '')
                issue_counts[error_text] = issue_counts.get(error_text, 0) + 1
        
        # Sort by frequency
        sorted_issues = sorted(
            issue_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [
            {'issue': issue, 'count': count}
            for issue, count in sorted_issues[:10]  # Top 10 issues
        ]
    
    def export_to_csv(self, filename: str = 'usability_results.csv'):
        """Export results to CSV"""
        sessions = self.get_all_sessions()
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Session ID', 'Participant ID', 'Task ID', 'Task Name',
                'Success', 'Duration (s)', 'Errors', 'Satisfaction'
            ])
            
            # Data
            for session in sessions:
                session_id = session['session_id']
                participant_id = session['participant_id']
                
                for task in session.get('tasks', []):
                    writer.writerow([
                        session_id,
                        participant_id,
                        task.get('task_id', ''),
                        task.get('name', ''),
                        task.get('success', False),
                        task.get('duration', 0),
                        len([e for e in session.get('errors', []) 
                             if e.get('context', '').startswith(task.get('task_id', ''))]),
                        session.get('satisfaction_scores', {}).get('Q5', '')
                    ])
    
    def generate_report(self, output_file: str = 'usability_report.md'):
        """Generate a comprehensive usability testing report"""
        metrics = self.calculate_metrics()
        sessions = self.get_all_sessions()
        filepath = self.output_dir / output_file
        
        with open(filepath, 'w') as f:
            f.write('# Usability Testing Report\n\n')
            f.write(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
            
            # Summary
            f.write('## Executive Summary\n\n')
            f.write(f'- Total Sessions: {metrics.get("total_sessions", 0)}\n')
            f.write(f'- Task Success Rate: {metrics.get("task_success_rate", 0):.1%}\n')
            f.write(f'- Error Rate: {metrics.get("error_rate", 0):.1%}\n')
            f.write(f'- Average Satisfaction: {metrics.get("average_satisfaction", {}).get("Q5", 0):.2f}/5\n\n')
            
            # Task Performance
            f.write('## Task Performance\n\n')
            f.write('| Task ID | Average Time (s) | Target Time (s) | Status |\n')
            f.write('|---------|------------------|-----------------|--------|\n')
            
            task_targets = {
                'TASK-1': 180,
                'TASK-2': 300,
                'TASK-3': 30,
                'TASK-4': 120,
                'TASK-5': 60
            }
            
            for task_id, avg_time in metrics.get('average_task_times', {}).items():
                target = task_targets.get(task_id, 0)
                status = '✅ Pass' if avg_time <= target else '❌ Fail'
                f.write(f'| {task_id} | {avg_time:.1f} | {target} | {status} |\n')
            
            f.write('\n')
            
            # Common Issues
            f.write('## Common Issues\n\n')
            for issue in metrics.get('common_issues', [])[:5]:
                f.write(f'- {issue["issue"]} (occurred {issue["count"]} times)\n')
            
            f.write('\n')
            
            # Satisfaction Scores
            f.write('## Satisfaction Scores\n\n')
            for question_id, score in metrics.get('average_satisfaction', {}).items():
                f.write(f'- {question_id}: {score:.2f}/5\n')
            
            f.write('\n')
            
            # Recommendations
            f.write('## Recommendations\n\n')
            f.write('Based on the usability testing results, we recommend:\n\n')
            
            if metrics.get('task_success_rate', 1) < 0.9:
                f.write('1. Improve task success rate by addressing common failure points\n')
            
            if metrics.get('error_rate', 0) > 0.05:
                f.write('2. Reduce error rate by improving error prevention and recovery\n')
            
            if metrics.get('average_satisfaction', {}).get('Q5', 5) < 4.0:
                f.write('3. Enhance user satisfaction by addressing feedback and pain points\n')
            
            f.write('\n')
