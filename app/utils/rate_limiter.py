"""
Rate Limiter
Implements rate limiting for login attempts to prevent brute force attacks
"""
from datetime import datetime, timedelta
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """
    Simple in-memory rate limiter for login attempts
    Tracks failed login attempts by email address
    """
    
    def __init__(self, max_attempts=5, window_minutes=15):
        """
        Initialize rate limiter
        
        Args:
            max_attempts: Maximum failed attempts allowed
            window_minutes: Time window in minutes
        """
        self.max_attempts = max_attempts
        self.window_minutes = window_minutes
        self.attempts = defaultdict(list)  # email -> list of attempt timestamps
        self.lock = Lock()
    
    def is_rate_limited(self, email):
        """
        Check if email is currently rate limited
        
        Args:
            email: Email address to check
        
        Returns:
            tuple: (is_limited: bool, remaining_time: int in seconds)
        """
        with self.lock:
            email = email.lower().strip()
            now = datetime.utcnow()
            cutoff_time = now - timedelta(minutes=self.window_minutes)
            
            # Remove old attempts outside the window
            self.attempts[email] = [
                attempt_time for attempt_time in self.attempts[email]
                if attempt_time > cutoff_time
            ]
            
            # Check if rate limited
            if len(self.attempts[email]) >= self.max_attempts:
                # Calculate remaining time until oldest attempt expires
                oldest_attempt = min(self.attempts[email])
                unlock_time = oldest_attempt + timedelta(minutes=self.window_minutes)
                remaining_seconds = int((unlock_time - now).total_seconds())
                return True, max(0, remaining_seconds)
            
            return False, 0
    
    def record_failed_attempt(self, email):
        """
        Record a failed login attempt
        
        Args:
            email: Email address
        """
        with self.lock:
            email = email.lower().strip()
            self.attempts[email].append(datetime.utcnow())
    
    def reset_attempts(self, email):
        """
        Reset failed attempts for an email (called on successful login)
        
        Args:
            email: Email address
        """
        with self.lock:
            email = email.lower().strip()
            if email in self.attempts:
                del self.attempts[email]
    
    def get_remaining_attempts(self, email):
        """
        Get number of remaining attempts before rate limit
        
        Args:
            email: Email address
        
        Returns:
            int: Number of remaining attempts
        """
        with self.lock:
            email = email.lower().strip()
            now = datetime.utcnow()
            cutoff_time = now - timedelta(minutes=self.window_minutes)
            
            # Remove old attempts
            self.attempts[email] = [
                attempt_time for attempt_time in self.attempts[email]
                if attempt_time > cutoff_time
            ]
            
            current_attempts = len(self.attempts[email])
            return max(0, self.max_attempts - current_attempts)
    
    def cleanup_old_entries(self):
        """
        Clean up old entries to prevent memory bloat
        Should be called periodically
        """
        with self.lock:
            now = datetime.utcnow()
            cutoff_time = now - timedelta(minutes=self.window_minutes)
            
            # Remove emails with no recent attempts
            emails_to_remove = []
            for email, attempts in self.attempts.items():
                # Filter out old attempts
                recent_attempts = [
                    attempt_time for attempt_time in attempts
                    if attempt_time > cutoff_time
                ]
                
                if not recent_attempts:
                    emails_to_remove.append(email)
                else:
                    self.attempts[email] = recent_attempts
            
            for email in emails_to_remove:
                del self.attempts[email]


# Global rate limiter instance
login_rate_limiter = RateLimiter(max_attempts=5, window_minutes=15)

