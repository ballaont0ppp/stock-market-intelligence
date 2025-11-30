"""
Usability Testing Configuration
Defines metrics, targets, and test scenarios for usability testing
"""

# Usability Metrics and Targets
USABILITY_METRICS = {
    'task_success_rate': {
        'target': 0.90,  # 90% success rate
        'description': 'Percentage of tasks completed successfully',
        'measurement': 'binary (success/failure)'
    },
    'time_on_task': {
        'targets': {
            'registration': 180,  # 3 minutes
            'first_purchase': 300,  # 5 minutes
            'portfolio_review': 30,  # 30 seconds
            'sell_stock': 120,  # 2 minutes
            'report_generation': 60  # 1 minute
        },
        'description': 'Time taken to complete each task (seconds)',
        'measurement': 'seconds'
    },
    'error_rate': {
        'target': 0.05,  # 5% error rate
        'description': 'Percentage of user actions that result in errors',
        'measurement': 'errors per action'
    },
    'user_satisfaction': {
        'target': 4.0,  # 4 out of 5
        'description': 'User satisfaction score',
        'measurement': 'Likert scale (1-5)'
    },
    'learnability': {
        'target': 600,  # 10 minutes
        'description': 'Time for new user to become proficient',
        'measurement': 'seconds'
    }
}

# Test Scenarios
TEST_SCENARIOS = {
    'exploratory': {
        'name': 'Exploratory Usability Testing',
        'description': 'Open-ended exploration to identify usability issues',
        'duration': 30,  # minutes
        'tasks': [
            'Explore the application freely',
            'Try to understand what the platform does',
            'Attempt to complete any task you find interesting',
            'Think aloud while navigating'
        ]
    },
    'task_based': {
        'name': 'Task-Based Usability Testing',
        'description': 'Specific tasks with time targets',
        'tasks': [
            {
                'id': 'T1',
                'name': 'New User Registration',
                'description': 'Create a new account on the platform',
                'target_time': 180,  # 3 minutes
                'steps': [
                    'Navigate to registration page',
                    'Fill in email, password, and full name',
                    'Submit registration form',
                    'Verify account creation'
                ],
                'success_criteria': [
                    'Account created successfully',
                    'User redirected to dashboard',
                    'Welcome message displayed'
                ]
            },
            {
                'id': 'T2',
                'name': 'First Stock Purchase',
                'description': 'Buy your first stock',
                'target_time': 300,  # 5 minutes
                'steps': [
                    'Navigate to orders page',
                    'Search for a stock (e.g., AAPL)',
                    'Enter quantity to purchase',
                    'Review order details',
                    'Confirm purchase'
                ],
                'success_criteria': [
                    'Order placed successfully',
                    'Wallet balance updated',
                    'Stock appears in portfolio',
                    'Confirmation message displayed'
                ]
            },
            {
                'id': 'T3',
                'name': 'Portfolio Review',
                'description': 'View your current portfolio holdings',
                'target_time': 30,  # 30 seconds
                'steps': [
                    'Navigate to portfolio page',
                    'View holdings table',
                    'Check portfolio value',
                    'Review gains/losses'
                ],
                'success_criteria': [
                    'Portfolio page loads quickly',
                    'Holdings displayed clearly',
                    'Values are accurate',
                    'Charts are visible'
                ]
            },
            {
                'id': 'T4',
                'name': 'Sell Stock',
                'description': 'Sell shares from your portfolio',
                'target_time': 120,  # 2 minutes
                'steps': [
                    'Navigate to portfolio or orders page',
                    'Select stock to sell',
                    'Enter quantity to sell',
                    'Review order details',
                    'Confirm sale'
                ],
                'success_criteria': [
                    'Sell order placed successfully',
                    'Wallet balance updated',
                    'Holdings updated',
                    'Confirmation message displayed'
                ]
            },
            {
                'id': 'T5',
                'name': 'Report Generation',
                'description': 'Generate and view a transaction report',
                'target_time': 60,  # 1 minute
                'steps': [
                    'Navigate to reports page',
                    'Select report type',
                    'Choose date range',
                    'Generate report',
                    'View results'
                ],
                'success_criteria': [
                    'Report generated successfully',
                    'Data displayed clearly',
                    'Export option available',
                    'Report is accurate'
                ]
            }
        ]
    }
}

# Participant Criteria
PARTICIPANT_CRITERIA = {
    'count': {
        'min': 5,
        'target': 10,
        'description': 'Number of test participants'
    },
    'demographics': {
        'age_range': '18-65',
        'experience_levels': [
            'Novice (no stock trading experience)',
            'Intermediate (some trading experience)',
            'Expert (regular trader)'
        ],
        'technical_proficiency': [
            'Low (basic computer skills)',
            'Medium (comfortable with web apps)',
            'High (tech-savvy)'
        ]
    },
    'recruitment_sources': [
        'Internal team members',
        'Friends and family',
        'Online recruitment platforms',
        'User testing services'
    ]
}

# Recording and Analysis Tools
RECORDING_TOOLS = {
    'screen_recording': {
        'tools': ['OBS Studio', 'Loom', 'Zoom'],
        'purpose': 'Capture user interactions and navigation'
    },
    'audio_recording': {
        'tools': ['Built-in microphone', 'Zoom audio'],
        'purpose': 'Capture think-aloud protocol'
    },
    'analytics': {
        'tools': ['Google Analytics', 'Hotjar', 'Custom logging'],
        'purpose': 'Track user behavior and metrics'
    },
    'survey_tools': {
        'tools': ['Google Forms', 'SurveyMonkey', 'Typeform'],
        'purpose': 'Collect satisfaction scores and feedback'
    }
}

# Test Environment Setup
TEST_ENVIRONMENT = {
    'url': 'http://localhost:5000',  # Local development
    'test_data': {
        'test_users': [
            {'email': 'testuser1@example.com', 'password': 'TestPass123!'},
            {'email': 'testuser2@example.com', 'password': 'TestPass123!'},
            {'email': 'testuser3@example.com', 'password': 'TestPass123!'},
        ],
        'test_stocks': ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'],
        'initial_wallet_balance': 100000.00
    },
    'browser_requirements': [
        'Chrome (latest)',
        'Firefox (latest)',
        'Safari (latest)',
        'Edge (latest)'
    ]
}

# Satisfaction Survey Questions
SATISFACTION_SURVEY = {
    'questions': [
        {
            'id': 'Q1',
            'question': 'How easy was it to complete the registration process?',
            'type': 'likert',
            'scale': '1-5 (1=Very Difficult, 5=Very Easy)'
        },
        {
            'id': 'Q2',
            'question': 'How intuitive was the navigation?',
            'type': 'likert',
            'scale': '1-5 (1=Very Confusing, 5=Very Intuitive)'
        },
        {
            'id': 'Q3',
            'question': 'How satisfied are you with the overall design?',
            'type': 'likert',
            'scale': '1-5 (1=Very Unsatisfied, 5=Very Satisfied)'
        },
        {
            'id': 'Q4',
            'question': 'How clear were the error messages and feedback?',
            'type': 'likert',
            'scale': '1-5 (1=Very Unclear, 5=Very Clear)'
        },
        {
            'id': 'Q5',
            'question': 'How likely are you to recommend this platform?',
            'type': 'likert',
            'scale': '1-5 (1=Not Likely, 5=Very Likely)'
        },
        {
            'id': 'Q6',
            'question': 'What did you like most about the platform?',
            'type': 'open_ended'
        },
        {
            'id': 'Q7',
            'question': 'What frustrated you the most?',
            'type': 'open_ended'
        },
        {
            'id': 'Q8',
            'question': 'What improvements would you suggest?',
            'type': 'open_ended'
        }
    ]
}

# Data Collection Template
DATA_COLLECTION_TEMPLATE = {
    'participant_id': '',
    'date': '',
    'session_duration': 0,
    'demographics': {
        'age': '',
        'experience_level': '',
        'technical_proficiency': ''
    },
    'task_results': [],
    'errors': [],
    'observations': [],
    'satisfaction_scores': {},
    'feedback': ''
}
