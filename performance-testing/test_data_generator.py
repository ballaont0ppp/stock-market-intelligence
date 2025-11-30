"""
Test Data Generator for Performance Testing

Generates large datasets for volume testing
"""

import random
import string
from datetime import datetime, timedelta
from decimal import Decimal
import csv
import os


class TestDataGenerator:
    """Generate test data for performance testing"""
    
    def __init__(self, output_dir='performance-testing/test_data'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_test_users(self, count=10000):
        """Generate test user data"""
        print(f"Generating {count} test users...")
        
        users = []
        for i in range(count):
            user = {
                'email': f'perftest_user_{i}@example.com',
                'password': 'TestPassword123!',
                'full_name': f'Performance Test User {i}',
                'risk_tolerance': random.choice(['conservative', 'moderate', 'aggressive']),
                'is_admin': False
            }
            users.append(user)
        
        # Write to CSV
        filepath = os.path.join(self.output_dir, 'test_users.csv')
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=users[0].keys())
            writer.writeheader()
            writer.writerows(users)
        
        print(f"✓ Generated {count} users -> {filepath}")
        return users
    
    def generate_test_companies(self, count=500):
        """Generate test company data"""
        print(f"Generating {count} test companies...")
        
        sectors = ['Technology', 'Healthcare', 'Finance', 'Energy', 'Consumer', 'Industrial']
        companies = []
        
        for i in range(count):
            symbol = f"TST{i:04d}"
            company = {
                'symbol': symbol,
                'company_name': f'Test Company {i} Inc.',
                'sector': random.choice(sectors),
                'industry': f'Test Industry {random.randint(1, 50)}',
                'market_cap': random.randint(1000000000, 1000000000000),
                'is_active': True
            }
            companies.append(company)
        
        # Write to CSV
        filepath = os.path.join(self.output_dir, 'test_companies.csv')
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=companies[0].keys())
            writer.writeheader()
            writer.writerows(companies)
        
        print(f"✓ Generated {count} companies -> {filepath}")
        return companies
    
    def generate_price_history(self, symbol, years=5):
        """Generate historical price data for a symbol"""
        prices = []
        start_date = datetime.now() - timedelta(days=365 * years)
        current_price = Decimal(str(random.uniform(50, 500)))
        
        for day in range(365 * years):
            date = start_date + timedelta(days=day)
            
            # Skip weekends
            if date.weekday() >= 5:
                continue
            
            # Simulate price movement
            change_percent = Decimal(str(random.uniform(-0.05, 0.05)))
            current_price = current_price * (1 + change_percent)
            
            open_price = current_price * Decimal(str(random.uniform(0.98, 1.02)))
            high_price = max(open_price, current_price) * Decimal(str(random.uniform(1.0, 1.03)))
            low_price = min(open_price, current_price) * Decimal(str(random.uniform(0.97, 1.0)))
            
            price = {
                'symbol': symbol,
                'date': date.strftime('%Y-%m-%d'),
                'open': float(open_price),
                'high': float(high_price),
                'low': float(low_price),
                'close': float(current_price),
                'adjusted_close': float(current_price),
                'volume': random.randint(1000000, 100000000)
            }
            prices.append(price)
        
        return prices
    
    def generate_all_price_history(self, symbols, years=5):
        """Generate price history for multiple symbols"""
        print(f"Generating {years} years of price history for {len(symbols)} symbols...")
        
        all_prices = []
        for i, symbol in enumerate(symbols):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(symbols)} symbols...")
            prices = self.generate_price_history(symbol, years)
            all_prices.extend(prices)
        
        # Write to CSV
        filepath = os.path.join(self.output_dir, 'test_price_history.csv')
        with open(filepath, 'w', newline='') as f:
            if all_prices:
                writer = csv.DictWriter(f, fieldnames=all_prices[0].keys())
                writer.writeheader()
                writer.writerows(all_prices)
        
        print(f"✓ Generated {len(all_prices)} price records -> {filepath}")
        return all_prices
    
    def generate_test_transactions(self, count=1000000):
        """Generate test transaction data"""
        print(f"Generating {count} test transactions...")
        
        transaction_types = ['BUY', 'SELL', 'DIVIDEND', 'DEPOSIT', 'WITHDRAWAL', 'FEE']
        transactions = []
        
        for i in range(count):
            if i % 100000 == 0:
                print(f"  Progress: {i}/{count} transactions...")
            
            transaction = {
                'user_id': random.randint(1, 10000),
                'transaction_type': random.choice(transaction_types),
                'amount': round(random.uniform(10, 10000), 2),
                'balance_before': round(random.uniform(1000, 100000), 2),
                'balance_after': round(random.uniform(1000, 100000), 2),
                'created_at': (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
            }
            transactions.append(transaction)
        
        # Write to CSV
        filepath = os.path.join(self.output_dir, 'test_transactions.csv')
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=transactions[0].keys())
            writer.writeheader()
            writer.writerows(transactions)
        
        print(f"✓ Generated {count} transactions -> {filepath}")
        return transactions
    
    def generate_all_test_data(self):
        """Generate all test data"""
        print("\n=== Generating Performance Test Data ===\n")
        
        # Generate users
        users = self.generate_test_users(count=10000)
        
        # Generate companies
        companies = self.generate_test_companies(count=500)
        
        # Generate price history for first 50 companies
        symbols = [c['symbol'] for c in companies[:50]]
        prices = self.generate_all_price_history(symbols, years=5)
        
        # Generate transactions
        transactions = self.generate_test_transactions(count=1000000)
        
        print("\n=== Test Data Generation Complete ===")
        print(f"Users: {len(users)}")
        print(f"Companies: {len(companies)}")
        print(f"Price Records: {len(prices)}")
        print(f"Transactions: {len(transactions)}")
        print(f"\nData location: {self.output_dir}")


if __name__ == '__main__':
    generator = TestDataGenerator()
    generator.generate_all_test_data()
