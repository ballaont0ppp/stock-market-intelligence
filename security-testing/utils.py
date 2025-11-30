"""
Security Testing Utilities
"""
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import requests
from jinja2 import Template

from config import REPORTS_DIR, RESULTS_DIR


class SecurityTestResult:
    """Container for security test results"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.timestamp = datetime.now()
        self.findings = []
        self.summary = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0,
            'total': 0
        }
        self.status = 'pending'
        self.duration = 0
    
    def add_finding(self, severity: str, title: str, description: str, 
                   recommendation: str = '', evidence: str = '', cwe: str = ''):
        """Add a security finding"""
        finding = {
            'severity': severity.lower(),
            'title': title,
            'description': description,
            'recommendation': recommendation,
            'evidence': evidence,
            'cwe': cwe,
            'timestamp': datetime.now().isoformat()
        }
        self.findings.append(finding)
        self.summary[severity.lower()] += 1
        self.summary['total'] += 1
    
    def set_status(self, status: str):
        """Set test status"""
        self.status = status
    
    def set_duration(self, duration: float):
        """Set test duration in seconds"""
        self.duration = duration
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'test_name': self.test_name,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'duration': self.duration,
            'findings': self.findings,
            'summary': self.summary
        }
    
    def save_json(self, filename: str = None):
        """Save results as JSON"""
        if filename is None:
            filename = f"{self.test_name.replace(' ', '_').lower()}_{int(time.time())}.json"
        
        filepath = RESULTS_DIR / filename
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        return filepath


class ReportGenerator:
    """Generate HTML security reports"""
    
    HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               background: #f5f5f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: white; 
                    border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                 color: white; padding: 30px; border-radius: 8px 8px 0 0; }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .header .meta { opacity: 0.9; font-size: 14px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                  gap: 15px; padding: 30px; border-bottom: 1px solid #e0e0e0; }
        .summary-card { padding: 20px; border-radius: 6px; text-align: center; }
        .summary-card.critical { background: #ffebee; color: #c62828; }
        .summary-card.high { background: #fff3e0; color: #e65100; }
        .summary-card.medium { background: #fffde7; color: #f57f17; }
        .summary-card.low { background: #e8f5e9; color: #2e7d32; }
        .summary-card.info { background: #e3f2fd; color: #1565c0; }
        .summary-card .count { font-size: 36px; font-weight: bold; margin-bottom: 5px; }
        .summary-card .label { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
        .findings { padding: 30px; }
        .finding { margin-bottom: 25px; padding: 20px; border-radius: 6px; 
                  border-left: 4px solid #ccc; background: #fafafa; }
        .finding.critical { border-left-color: #c62828; }
        .finding.high { border-left-color: #e65100; }
        .finding.medium { border-left-color: #f57f17; }
        .finding.low { border-left-color: #2e7d32; }
        .finding.info { border-left-color: #1565c0; }
        .finding-header { display: flex; justify-content: space-between; 
                         align-items: center; margin-bottom: 15px; }
        .finding-title { font-size: 18px; font-weight: 600; }
        .severity-badge { padding: 4px 12px; border-radius: 12px; font-size: 12px; 
                         font-weight: 600; text-transform: uppercase; }
        .severity-badge.critical { background: #c62828; color: white; }
        .severity-badge.high { background: #e65100; color: white; }
        .severity-badge.medium { background: #f57f17; color: white; }
        .severity-badge.low { background: #2e7d32; color: white; }
        .severity-badge.info { background: #1565c0; color: white; }
        .finding-description { margin-bottom: 15px; line-height: 1.6; color: #555; }
        .finding-section { margin-top: 15px; }
        .finding-section-title { font-weight: 600; margin-bottom: 8px; color: #333; }
        .finding-section-content { padding: 12px; background: white; border-radius: 4px; 
                                  font-family: 'Courier New', monospace; font-size: 13px; 
                                  white-space: pre-wrap; word-wrap: break-word; }
        .footer { padding: 20px 30px; background: #f5f5f5; border-radius: 0 0 8px 8px; 
                 text-align: center; color: #666; font-size: 14px; }
        .no-findings { padding: 40px; text-align: center; color: #666; }
        .no-findings-icon { font-size: 48px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ title }}</h1>
            <div class="meta">
                Generated: {{ timestamp }}<br>
                Test Duration: {{ duration }}s<br>
                Status: {{ status }}
            </div>
        </div>
        
        <div class="summary">
            <div class="summary-card critical">
                <div class="count">{{ summary.critical }}</div>
                <div class="label">Critical</div>
            </div>
            <div class="summary-card high">
                <div class="count">{{ summary.high }}</div>
                <div class="label">High</div>
            </div>
            <div class="summary-card medium">
                <div class="count">{{ summary.medium }}</div>
                <div class="label">Medium</div>
            </div>
            <div class="summary-card low">
                <div class="count">{{ summary.low }}</div>
                <div class="label">Low</div>
            </div>
            <div class="summary-card info">
                <div class="count">{{ summary.info }}</div>
                <div class="label">Info</div>
            </div>
        </div>
        
        <div class="findings">
            {% if findings %}
                {% for finding in findings %}
                <div class="finding {{ finding.severity }}">
                    <div class="finding-header">
                        <div class="finding-title">{{ finding.title }}</div>
                        <span class="severity-badge {{ finding.severity }}">{{ finding.severity }}</span>
                    </div>
                    <div class="finding-description">{{ finding.description }}</div>
                    
                    {% if finding.cwe %}
                    <div class="finding-section">
                        <div class="finding-section-title">CWE Reference</div>
                        <div class="finding-section-content">{{ finding.cwe }}</div>
                    </div>
                    {% endif %}
                    
                    {% if finding.evidence %}
                    <div class="finding-section">
                        <div class="finding-section-title">Evidence</div>
                        <div class="finding-section-content">{{ finding.evidence }}</div>
                    </div>
                    {% endif %}
                    
                    {% if finding.recommendation %}
                    <div class="finding-section">
                        <div class="finding-section-title">Recommendation</div>
                        <div class="finding-section-content">{{ finding.recommendation }}</div>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            {% else %}
                <div class="no-findings">
                    <div class="no-findings-icon">✓</div>
                    <div>No security findings detected</div>
                </div>
            {% endif %}
        </div>
        
        <div class="footer">
            Stock Portfolio Management Platform - Security Testing Suite
        </div>
    </div>
</body>
</html>
    """
    
    @staticmethod
    def generate_report(result: SecurityTestResult, filename: str = None) -> Path:
        """Generate HTML report from test result"""
        if filename is None:
            filename = f"{result.test_name.replace(' ', '_').lower()}_report.html"
        
        template = Template(ReportGenerator.HTML_TEMPLATE)
        html = template.render(
            title=result.test_name,
            timestamp=result.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            duration=f"{result.duration:.2f}",
            status=result.status.upper(),
            summary=result.summary,
            findings=result.findings
        )
        
        filepath = REPORTS_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filepath


def check_app_running(url: str, timeout: int = 5) -> bool:
    """Check if application is running"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code < 500
    except requests.exceptions.RequestException:
        return False


def get_session_with_login(base_url: str, email: str, password: str) -> requests.Session:
    """Create authenticated session"""
    session = requests.Session()
    
    # Get CSRF token from login page
    response = session.get(f"{base_url}/auth/login")
    # Extract CSRF token from response (simplified)
    
    # Login
    login_data = {
        'email': email,
        'password': password
    }
    response = session.post(f"{base_url}/auth/login", data=login_data)
    
    return session


def severity_to_priority(severity: str) -> int:
    """Convert severity to numeric priority"""
    severity_map = {
        'critical': 5,
        'high': 4,
        'medium': 3,
        'low': 2,
        'info': 1
    }
    return severity_map.get(severity.lower(), 0)
