"""
Usability Test Scenarios
Detailed test scenarios for usability testing sessions
"""

from datetime import datetime
from typing import Dict, List, Any


class UsabilityTestScenario:
    """Base class for usability test scenarios"""
    
    def __init__(self, scenario_id: str, name: str, description: str):
        self.scenario_id = scenario_id
        self.name = name
        self.description = description
        self.start_time = None
        self.end_time = None
        self.success = None
        self.errors = []
        self.observations = []
    
    def start(self):
        """Start the scenario timer"""
        self.start_time = datetime.now()
    
    def end(self, success: bool):
        """End the scenario and record success"""
        self.end_time = datetime.now()
        self.success = success
    
    def duration(self) -> float:
        """Calculate duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0
    
    def add_error(self, error: str):
        """Record an error during the scenario"""
        self.errors.append({
            'timestamp': datetime.now(),
            'description': error
        })
    
    def add_observation(self, observation: str):
        """Record an observation during the scenario"""
        self.observations.append({
            'timestamp': datetime.now(),
            'description': observation
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scenario to dictionary"""
        return {
            'scenario_id': self.scenario_id,
            'name': self.name,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration(),
            'success': self.success,
            'errors': self.errors,
            'observations': self.observations
        }


# Exploratory Testing Scenarios
EXPLORATORY_SCENARIOS = [
    {
        'id': 'EXP-1',
        'name': 'First Impressions',
        'description': 'User explores the landing page and forms initial impressions',
        'instructions': [
            'Open the application homepage',
            'Take 2 minutes to explore without clicking anything',
            'Share your first impressions',
            'What do you think this application does?',
            'What catches your attention first?'
        ],
        'duration': 5  # minutes
    },
    {
        'id': 'EXP-2',
        'name': 'Free Navigation',
        'description': 'User navigates freely to understand the application structure',
        'instructions': [
            'Navigate through the application as you wish',
            'Try to understand the main features',
            'Think aloud as you explore',
            'What confuses you?',
            'What makes sense?'
        ],
        'duration': 10  # minutes
    },
    {
        'id': 'EXP-3',
        'name': 'Feature Discovery',
        'description': 'User attempts to discover key features without guidance',
        'instructions': [
            'Try to find where you can buy stocks',
            'Try to find where you can view your portfolio',
            'Try to find where you can see predictions',
            'Try to find where you can generate reports',
            'Share what was easy or difficult to find'
        ],
        'duration': 10  # minutes
    },
    {
        'id': 'EXP-4',
        'name': 'Error Recovery',
        'description': 'User encounters and recovers from errors',
        'instructions': [
            'Try to buy a stock with insufficient funds',
            'Try to sell more shares than you own',
            'Try to access a page without logging in',
            'How clear were the error messages?',
            'Could you recover from errors easily?'
        ],
        'duration': 5  # minutes
    }
]


# Task-Based Testing Scenarios
TASK_BASED_SCENARIOS = [
    {
        'id': 'TASK-1',
        'name': 'New User Registration',
        'description': 'Complete the registration process',
        'target_time': 180,  # 3 minutes
        'instructions': [
            'You want to create an account on this stock trading platform',
            'Find the registration page',
            'Create an account with your email',
            'Complete the registration process'
        ],
        'success_criteria': [
            'Registration form found',
            'All required fields filled',
            'Account created successfully',
            'User redirected to dashboard'
        ],
        'common_issues': [
            'Cannot find registration link',
            'Password requirements unclear',
            'Form validation errors confusing',
            'No confirmation message'
        ]
    },
    {
        'id': 'TASK-2',
        'name': 'First Stock Purchase',
        'description': 'Buy your first stock',
        'target_time': 300,  # 5 minutes
        'instructions': [
            'You have $100,000 in your virtual wallet',
            'You want to buy 10 shares of Apple (AAPL)',
            'Find where to place an order',
            'Complete the purchase'
        ],
        'success_criteria': [
            'Orders page found',
            'Stock symbol entered correctly',
            'Quantity entered',
            'Order preview shown',
            'Order confirmed successfully'
        ],
        'common_issues': [
            'Cannot find orders page',
            'Stock search not working',
            'Price preview not clear',
            'Confirmation unclear'
        ]
    },
    {
        'id': 'TASK-3',
        'name': 'Portfolio Review',
        'description': 'View your current holdings',
        'target_time': 30,  # 30 seconds
        'instructions': [
            'You want to check your current stock holdings',
            'Find your portfolio',
            'View your total portfolio value',
            'Check gains or losses'
        ],
        'success_criteria': [
            'Portfolio page found quickly',
            'Holdings displayed clearly',
            'Values are visible',
            'Gains/losses shown'
        ],
        'common_issues': [
            'Portfolio link not obvious',
            'Information overload',
            'Values not clear',
            'Charts confusing'
        ]
    },
    {
        'id': 'TASK-4',
        'name': 'Sell Stock',
        'description': 'Sell shares from your portfolio',
        'target_time': 120,  # 2 minutes
        'instructions': [
            'You want to sell 5 shares of the stock you own',
            'Find where to sell stocks',
            'Complete the sale'
        ],
        'success_criteria': [
            'Sell option found',
            'Quantity entered',
            'Order preview shown',
            'Sale confirmed'
        ],
        'common_issues': [
            'Sell button not obvious',
            'Process different from buying',
            'Confirmation unclear',
            'No feedback on success'
        ]
    },
    {
        'id': 'TASK-5',
        'name': 'Report Generation',
        'description': 'Generate a transaction report',
        'target_time': 60,  # 1 minute
        'instructions': [
            'You want to see all your transactions from the past month',
            'Find the reports section',
            'Generate a transaction report',
            'View the results'
        ],
        'success_criteria': [
            'Reports page found',
            'Report type selected',
            'Date range set',
            'Report generated',
            'Data displayed clearly'
        ],
        'common_issues': [
            'Reports page hard to find',
            'Date picker confusing',
            'Report takes too long',
            'Export option not clear'
        ]
    },
    {
        'id': 'TASK-6',
        'name': 'View Stock Predictions',
        'description': 'Get ML predictions for a stock',
        'target_time': 90,  # 1.5 minutes
        'instructions': [
            'You want to see price predictions for Microsoft (MSFT)',
            'Find where to get predictions',
            'View the prediction results'
        ],
        'success_criteria': [
            'Prediction feature found',
            'Stock symbol entered',
            'Predictions displayed',
            'Charts visible'
        ],
        'common_issues': [
            'Prediction feature not obvious',
            'Results take too long',
            'Charts not clear',
            'No explanation of models'
        ]
    },
    {
        'id': 'TASK-7',
        'name': 'Update Profile',
        'description': 'Update your user profile',
        'target_time': 90,  # 1.5 minutes
        'instructions': [
            'You want to update your investment goals',
            'Find your profile settings',
            'Update your information',
            'Save the changes'
        ],
        'success_criteria': [
            'Profile page found',
            'Fields editable',
            'Changes saved',
            'Confirmation shown'
        ],
        'common_issues': [
            'Profile link not obvious',
            'Save button not clear',
            'No confirmation',
            'Changes not persisted'
        ]
    },
    {
        'id': 'TASK-8',
        'name': 'Check Notifications',
        'description': 'View your notifications',
        'target_time': 30,  # 30 seconds
        'instructions': [
            'You received a notification about a completed order',
            'Find your notifications',
            'View the notification details'
        ],
        'success_criteria': [
            'Notification icon found',
            'Notifications displayed',
            'Details readable',
            'Mark as read option'
        ],
        'common_issues': [
            'Notification icon not obvious',
            'Badge count confusing',
            'Details not clear',
            'Cannot dismiss'
        ]
    }
]


# Learnability Scenarios
LEARNABILITY_SCENARIOS = [
    {
        'id': 'LEARN-1',
        'name': 'Complete Workflow',
        'description': 'Complete a full trading workflow from start to finish',
        'target_time': 600,  # 10 minutes
        'instructions': [
            'Register a new account',
            'Explore the dashboard',
            'Buy a stock',
            'View your portfolio',
            'Generate a report',
            'Sell the stock'
        ],
        'success_criteria': [
            'All tasks completed',
            'No major confusion',
            'User feels confident',
            'Completed within time limit'
        ]
    }
]


def get_scenario_by_id(scenario_id: str) -> Dict[str, Any]:
    """Get a scenario by its ID"""
    all_scenarios = EXPLORATORY_SCENARIOS + TASK_BASED_SCENARIOS + LEARNABILITY_SCENARIOS
    for scenario in all_scenarios:
        if scenario['id'] == scenario_id:
            return scenario
    return None


def get_scenarios_by_type(scenario_type: str) -> List[Dict[str, Any]]:
    """Get all scenarios of a specific type"""
    if scenario_type == 'exploratory':
        return EXPLORATORY_SCENARIOS
    elif scenario_type == 'task_based':
        return TASK_BASED_SCENARIOS
    elif scenario_type == 'learnability':
        return LEARNABILITY_SCENARIOS
    else:
        return []
