"""
Locust Performance Testing Suite for Stock Portfolio Management Platform

This file contains load testing scenarios for the platform including:
- User authentication flows
- Portfolio management operations
- Stock trading (buy/sell orders)
- Dashboard and reporting access
- Admin operations

Usage:
    locust -f locustfile.py --host=http://localhost:5000
    locust -f locustfile.py --host=http://localhost:5000 --users 100 --spawn-rate 10
"""

from locust import HttpUser, task, between, SequentialTaskSet
import random
import json
from datetime import datetime, timedelta


class UserAuthenticationFlow(SequentialTaskSet):
    """Sequential task set for user authentication"""
    
    def on_start(self):
        """Setup test data"""
        self.email = f"testuser_{random.randint(1000, 9999)}@example.com"
        self.password = "TestPassword123!"
        self.full_name = f"Test User {random.randint(1000, 9999)}"
    
    @task
    def register(self):
        """Register a new user"""
        with self.client.post("/auth/register", data={
            "email": self.email,
            "password": self.password,
            "confirm_password": self.password,
            "full_name": self.full_name
        }, catch_response=True) as response:
            if response.status_code in [200, 302]:
                response.success()
            else:
                response.failure(f"Registration failed: {response.status_code}")
    
    @task
    def login(self):
        """Login with registered credentials"""
        with self.client.post("/auth/login", data={
            "email": self.email,
            "password": self.password
        }, catch_response=True) as response:
            if response.status_code in [200, 302]:
                response.success()
                # Store session for subsequent requests
                self.user.logged_in = True
            else:
                response.failure(f"Login failed: {response.status_code}")


class TradingFlow(SequentialTaskSet):
    """Sequential task set for trading operations"""
    
    def on_start(self):
        """Ensure user is logged in"""
        if not hasattr(self.user, 'logged_in') or not self.user.logged_in:
            self.login_user()
    
    def login_user(self):
        """Helper to login test user"""
        self.client.post("/auth/login", data={
            "email": "testuser@example.com",
            "password": "TestPassword123!"
        })
        self.user.logged_in = True
    
    @task
    def view_dashboard(self):
        """Access dashboard"""
        with self.client.get("/dashboard", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Dashboard access failed: {response.status_code}")
    
    @task
    def view_portfolio(self):
        """View portfolio holdings"""
        with self.client.get("/portfolio", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Portfolio access failed: {response.status_code}")
    
    @task
    def buy_stock(self):
        """Execute buy order"""
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        symbol = random.choice(symbols)
        quantity = random.randint(1, 10)
        
        with self.client.post("/orders/buy", data={
            "symbol": symbol,
            "quantity": quantity
        }, catch_response=True) as response:
            if response.status_code in [200, 302]:
                response.success()
            else:
                response.failure(f"Buy order failed: {response.status_code}")
    
    @task
    def view_orders(self):
        """View order history"""
        with self.client.get("/orders", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Orders access failed: {response.status_code}")


class PortfolioUser(HttpUser):
    """
    Simulates a regular user performing portfolio management tasks
    
    Weight: 70% of total users
    """
    weight = 70
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    
    @task(3)
    def view_dashboard(self):
        """View dashboard (most common action)"""
        self.client.get("/dashboard")
    
    @task(2)
    def view_portfolio(self):
        """View portfolio"""
        self.client.get("/portfolio")
    
    @task(2)
    def view_orders(self):
        """View order history"""
        self.client.get("/orders")
    
    @task(1)
    def place_buy_order(self):
        """Place a buy order"""
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
        self.client.post("/orders/buy", data={
            "symbol": random.choice(symbols),
            "quantity": random.randint(1, 10)
        })
    
    @task(1)
    def view_reports(self):
        """View reports"""
        self.client.get("/reports")
    
    @task(1)
    def get_stock_price(self):
        """Get current stock price via API"""
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        self.client.get(f"/api/stock/{random.choice(symbols)}/price")


class PredictionUser(HttpUser):
    """
    Simulates users primarily using prediction features
    
    Weight: 20% of total users
    """
    weight = 20
    wait_time = between(2, 8)  # Predictions take longer
    
    @task(3)
    def view_dashboard(self):
        """View dashboard"""
        self.client.get("/dashboard")
    
    @task(2)
    def get_prediction(self):
        """Get stock prediction"""
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        self.client.post("/dashboard/predict", data={
            "symbol": random.choice(symbols)
        })
    
    @task(1)
    def view_portfolio(self):
        """View portfolio"""
        self.client.get("/portfolio")


class AdminUser(HttpUser):
    """
    Simulates admin users performing administrative tasks
    
    Weight: 10% of total users
    """
    weight = 10
    wait_time = between(3, 10)
    
    @task(2)
    def view_admin_dashboard(self):
        """View admin dashboard"""
        self.client.get("/admin")
    
    @task(1)
    def view_users(self):
        """View user management"""
        self.client.get("/admin/users")
    
    @task(1)
    def view_companies(self):
        """View company management"""
        self.client.get("/admin/companies")
    
    @task(1)
    def view_monitoring(self):
        """View system monitoring"""
        self.client.get("/admin/monitoring")
    
    @task(1)
    def view_transactions(self):
        """View transaction monitoring"""
        self.client.get("/admin/monitoring/transactions")


class APIUser(HttpUser):
    """
    Simulates API-only users (mobile apps, integrations)
    
    Weight: 5% of total users
    """
    weight = 5
    wait_time = between(0.5, 2)
    
    @task(3)
    def get_portfolio_api(self):
        """Get portfolio via API"""
        self.client.get("/api/portfolio")
    
    @task(2)
    def get_stock_price_api(self):
        """Get stock price via API"""
        symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
        self.client.get(f"/api/stock/{random.choice(symbols)}/price")
    
    @task(1)
    def search_stocks_api(self):
        """Search stocks via API"""
        queries = ['tech', 'apple', 'microsoft', 'amazon']
        self.client.get(f"/api/search?q={random.choice(queries)}")
