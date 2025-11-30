"""
Quick test script for StockRepository functionality
Run with: python test_stock_repository.py
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.services.stock_repository import StockRepository
from app.models.company import Company

def test_stock_repository():
    """Test basic StockRepository functionality"""
    app = create_app('development')
    
    with app.app_context():
        print("Testing StockRepository...")
        print("-" * 50)
        
        repo = StockRepository()
        
        # Test 1: Get company by symbol
        print("\n1. Testing get_company_by_symbol...")
        try:
            company = repo.get_company_by_symbol('AAPL')
            if company:
                print(f"   ✓ Found: {company.symbol} - {company.company_name}")
            else:
                print("   ℹ Company not found (this is OK if not seeded yet)")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
        
        # Test 2: Search companies
        print("\n2. Testing search_companies...")
        try:
            companies, total = repo.search_companies(query='A', page=1, per_page=5)
            print(f"   ✓ Found {total} companies matching 'A'")
            for company in companies[:3]:
                print(f"      - {company.symbol}: {company.company_name}")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
        
        # Test 3: Get all sectors
        print("\n3. Testing get_all_sectors...")
        try:
            sectors = repo.get_all_sectors()
            print(f"   ✓ Found {len(sectors)} sectors")
            if sectors:
                print(f"      Examples: {', '.join(sectors[:5])}")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
        
        # Test 4: Get trending stocks
        print("\n4. Testing get_trending_stocks...")
        try:
            trending = repo.get_trending_stocks(limit=5)
            print(f"   ✓ Found {len(trending)} trending stocks")
            for stock in trending:
                print(f"      - {stock['symbol']}: {stock['trade_count']} trades")
        except Exception as e:
            print(f"   ℹ No trending stocks (this is OK if no orders yet)")
        
        # Test 5: Fetch live price (if in LIVE mode)
        if app.config.get('DATA_MODE') == 'LIVE':
            print("\n5. Testing fetch_live_price...")
            try:
                price = repo.fetch_live_price('AAPL')
                print(f"   ✓ AAPL current price: ${price}")
            except Exception as e:
                print(f"   ✗ Error: {str(e)}")
        else:
            print("\n5. Skipping live price test (STATIC mode)")
        
        # Test 6: Static mode validation
        print("\n6. Testing static mode validation...")
        try:
            repo._validate_static_mode()
            print(f"   ✓ Static mode validation passed")
            print(f"      Current mode: {app.config.get('DATA_MODE')}")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")
        
        print("\n" + "-" * 50)
        print("Testing complete!")

if __name__ == '__main__':
    test_stock_repository()

