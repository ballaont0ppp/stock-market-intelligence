"""
Stock Repository Service
Manages company data, price history, and stock information
"""
import logging
import os
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Tuple
import yfinance as yf
import pandas as pd
from sqlalchemy import or_, and_, desc, func
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app

from app import db
from app.models.company import Company
from app.models.price_history import PriceHistory
from app.models.order import Order
from app.utils.exceptions import (
    ValidationError, 
    ExternalAPIError, 
    StockNotFoundError
)
from app.utils.error_handlers import handle_errors

logger = logging.getLogger(__name__)


class StockRepository:
    """Repository for managing stock and company data"""
    
    def __init__(self):
        """Initialize the stock repository"""
        self.price_cache = {}  # Simple in-memory cache
        self.cache_duration = 900  # 15 minutes in seconds
        self._validate_static_mode()
    
    @handle_errors('database')
    def get_company_by_symbol(self, symbol: str) -> Optional[Company]:
        """
        Get company by stock symbol
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Company object or None if not found
        """
        if not symbol:
            raise ValidationError("Stock symbol is required")
        
        symbol = symbol.upper().strip()
        company = Company.query.filter_by(symbol=symbol, is_active=True).first()
        
        if company:
            logger.info(f"Found company: {symbol}")
        else:
            logger.warning(f"Company not found: {symbol}")
        
        return company
    
    @handle_errors('database')
    def create_company(self, symbol: str, data: Optional[Dict] = None) -> Company:
        """
        Create a new company with yfinance integration
        
        Args:
            symbol: Stock symbol
            data: Optional company data dictionary
            
        Returns:
            Created Company object
            
        Raises:
            ValidationError: If symbol is invalid
            ExternalAPIError: If yfinance fetch fails
        """
        if not symbol:
            raise ValidationError("Stock symbol is required")
        
        symbol = symbol.upper().strip()
        
        # Check if company already exists
        existing = Company.query.filter_by(symbol=symbol).first()
        if existing:
            if not existing.is_active:
                existing.is_active = True
                db.session.commit()
                logger.info(f"Reactivated company: {symbol}")
                return existing
            raise ValidationError(f"Company with symbol {symbol} already exists")
        
        # Fetch data from yfinance if not provided
        if not data:
            data = self._fetch_company_info_from_yfinance(symbol)
        
        # Create company record
        company = Company(
            symbol=symbol,
            company_name=data.get('company_name', symbol),
            sector=data.get('sector'),
            industry=data.get('industry'),
            market_cap=data.get('market_cap'),
            description=data.get('description'),
            website=data.get('website'),
            ceo=data.get('ceo'),
            employees=data.get('employees'),
            founded_year=data.get('founded_year'),
            headquarters=data.get('headquarters'),
            is_active=True
        )
        
        db.session.add(company)
        db.session.commit()
        
        logger.info(f"Created company: {symbol}")
        return company
    
    def _fetch_company_info_from_yfinance(self, symbol: str) -> Dict:
        """
        Fetch company information from yfinance
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with company information
            
        Raises:
            ExternalAPIError: If fetch fails
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or 'symbol' not in info:
                raise StockNotFoundError(f"Stock symbol not found: {symbol}")
            
            return {
                'company_name': info.get('longName', info.get('shortName', symbol)),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': info.get('marketCap'),
                'description': info.get('longBusinessSummary'),
                'website': info.get('website'),
                'ceo': info.get('companyOfficers', [{}])[0].get('name') if info.get('companyOfficers') else None,
                'employees': info.get('fullTimeEmployees'),
                'founded_year': None,  # Not available in yfinance
                'headquarters': f"{info.get('city', '')}, {info.get('state', '')}, {info.get('country', '')}".strip(', ')
            }
        except Exception as e:
            logger.error(f"Failed to fetch company info for {symbol}: {str(e)}")
            raise ExternalAPIError(f"Failed to fetch company information: {str(e)}")
    
    @handle_errors('database')
    def update_company(self, company_id: int, data: Dict) -> Company:
        """
        Update company information
        
        Args:
            company_id: Company ID
            data: Dictionary with fields to update
            
        Returns:
            Updated Company object
            
        Raises:
            ValidationError: If company not found
        """
        company = Company.query.get(company_id)
        if not company:
            raise ValidationError(f"Company not found with ID: {company_id}")
        
        # Update allowed fields
        allowed_fields = [
            'company_name', 'sector', 'industry', 'market_cap', 
            'description', 'website', 'ceo', 'employees', 
            'founded_year', 'headquarters', 'is_active'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(company, field, data[field])
        
        company.last_updated = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Updated company: {company.symbol}")
        return company
    
    @handle_errors('database')
    def search_companies(
        self, 
        query: Optional[str] = None, 
        filters: Optional[Dict] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Company], int]:
        """
        Search companies with filters and pagination
        
        Args:
            query: Search query for symbol or company name
            filters: Dictionary with filter criteria (sector, market_cap_min, market_cap_max)
            page: Page number (1-indexed)
            per_page: Items per page
            
        Returns:
            Tuple of (list of companies, total count)
        """
        # Start with base query
        base_query = Company.query.filter_by(is_active=True)
        
        # Apply search query
        if query:
            query = query.strip()
            search_filter = or_(
                Company.symbol.ilike(f'%{query}%'),
                Company.company_name.ilike(f'%{query}%')
            )
            base_query = base_query.filter(search_filter)
        
        # Apply filters
        if filters:
            if 'sector' in filters and filters['sector']:
                base_query = base_query.filter(Company.sector == filters['sector'])
            
            if 'market_cap_min' in filters and filters['market_cap_min']:
                base_query = base_query.filter(Company.market_cap >= filters['market_cap_min'])
            
            if 'market_cap_max' in filters and filters['market_cap_max']:
                base_query = base_query.filter(Company.market_cap <= filters['market_cap_max'])
        
        # Get total count
        total = base_query.count()
        
        # Apply pagination and ordering
        companies = base_query.order_by(Company.symbol).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        ).items
        
        logger.info(f"Search returned {len(companies)} companies (total: {total})")
        return companies, total
    
    @handle_errors('database')
    def get_trending_stocks(self, limit: int = 10) -> List[Dict]:
        """
        Get trending stocks based on recent trades
        
        Args:
            limit: Maximum number of stocks to return
            
        Returns:
            List of dictionaries with stock info and trade count
        """
        # Get stocks with most orders in last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        trending = db.session.query(
            Company.company_id,
            Company.symbol,
            Company.company_name,
            Company.sector,
            func.count(Order.order_id).label('trade_count')
        ).join(
            Order, Company.company_id == Order.company_id
        ).filter(
            Order.created_at >= yesterday,
            Order.order_status == 'COMPLETED'
        ).group_by(
            Company.company_id
        ).order_by(
            desc('trade_count')
        ).limit(limit).all()
        
        result = []
        for item in trending:
            result.append({
                'company_id': item.company_id,
                'symbol': item.symbol,
                'company_name': item.company_name,
                'sector': item.sector,
                'trade_count': item.trade_count
            })
        
        logger.info(f"Retrieved {len(result)} trending stocks")
        return result
    
    def get_all_sectors(self) -> List[str]:
        """
        Get list of all unique sectors
        
        Returns:
            List of sector names
        """
        sectors = db.session.query(Company.sector).filter(
            Company.sector.isnot(None),
            Company.is_active == True
        ).distinct().order_by(Company.sector).all()
        
        return [sector[0] for sector in sectors if sector[0]]
    
    @handle_errors('database')
    def get_current_price(self, symbol: str) -> Decimal:
        """
        Get current price for a stock with caching
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price as Decimal
            
        Raises:
            ValidationError: If symbol is invalid
            ExternalAPIError: If price fetch fails
        """
        if not symbol:
            raise ValidationError("Stock symbol is required")
        
        symbol = symbol.upper().strip()
        
        # Check cache first
        cache_key = f"{symbol}_price"
        if cache_key in self.price_cache:
            cached_data = self.price_cache[cache_key]
            cache_time = cached_data['timestamp']
            
            # Check if cache is still valid (15 minutes)
            if (datetime.utcnow() - cache_time).total_seconds() < self.cache_duration:
                logger.debug(f"Using cached price for {symbol}")
                return cached_data['price']
        
        # Try to get from database first (most recent price)
        company = self.get_company_by_symbol(symbol)
        if company:
            latest_price = PriceHistory.query.filter_by(
                company_id=company.company_id
            ).order_by(desc(PriceHistory.date)).first()
            
            if latest_price and (date.today() - latest_price.date).days == 0:
                # We have today's price in database
                price = latest_price.close
                self._cache_price(symbol, price)
                return price
        
        # Fetch live price from yfinance
        price = self.fetch_live_price(symbol)
        self._cache_price(symbol, price)
        return price
    
    def _cache_price(self, symbol: str, price: Decimal):
        """Cache a price with timestamp"""
        self.price_cache[f"{symbol}_price"] = {
            'price': price,
            'timestamp': datetime.utcnow()
        }
    
    @handle_errors('external_api')
    def fetch_live_price(self, symbol: str) -> Decimal:
        """
        Fetch live price from yfinance
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price as Decimal
            
        Raises:
            ExternalAPIError: If fetch fails
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # Try to get current price from info
            info = ticker.info
            
            # Try different price fields
            price = None
            for field in ['currentPrice', 'regularMarketPrice', 'previousClose']:
                if field in info and info[field]:
                    price = info[field]
                    break
            
            if price is None:
                # Fallback: get latest from history
                hist = ticker.history(period='1d')
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
            
            if price is None:
                raise StockNotFoundError(f"Could not fetch price for {symbol}")
            
            logger.info(f"Fetched live price for {symbol}: ${price}")
            return Decimal(str(price))
            
        except Exception as e:
            logger.error(f"Failed to fetch live price for {symbol}: {str(e)}")
            raise ExternalAPIError(f"Failed to fetch live price: {str(e)}")
    
    @handle_errors('database')
    def get_price_history(
        self, 
        symbol: str, 
        start_date: Optional[date] = None, 
        end_date: Optional[date] = None
    ) -> List[PriceHistory]:
        """
        Get price history for a stock
        
        Args:
            symbol: Stock symbol
            start_date: Start date (default: 1 year ago)
            end_date: End date (default: today)
            
        Returns:
            List of PriceHistory objects
        """
        company = self.get_company_by_symbol(symbol)
        if not company:
            raise ValidationError(f"Company not found: {symbol}")
        
        # Set default dates
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=365)
        
        # Query price history
        history = PriceHistory.query.filter(
            PriceHistory.company_id == company.company_id,
            PriceHistory.date >= start_date,
            PriceHistory.date <= end_date
        ).order_by(PriceHistory.date).all()
        
        logger.info(f"Retrieved {len(history)} price records for {symbol}")
        return history
    
    @handle_errors('database')
    def update_price_history(self, symbol: str, data: pd.DataFrame) -> int:
        """
        Update price history in database from DataFrame
        
        Args:
            symbol: Stock symbol
            data: DataFrame with columns: Date (index), Open, High, Low, Close, Adj Close, Volume
            
        Returns:
            Number of records inserted/updated
            
        Raises:
            ValidationError: If company not found or data is invalid
        """
        company = self.get_company_by_symbol(symbol)
        if not company:
            raise ValidationError(f"Company not found: {symbol}")
        
        if data.empty:
            logger.warning(f"No price data to update for {symbol}")
            return 0
        
        count = 0
        for date_val, row in data.iterrows():
            try:
                # Convert date
                if isinstance(date_val, pd.Timestamp):
                    date_obj = date_val.date()
                else:
                    date_obj = date_val
                
                # Check if record exists
                existing = PriceHistory.query.filter_by(
                    company_id=company.company_id,
                    date=date_obj
                ).first()
                
                if existing:
                    # Update existing record
                    existing.open = Decimal(str(row['Open']))
                    existing.high = Decimal(str(row['High']))
                    existing.low = Decimal(str(row['Low']))
                    existing.close = Decimal(str(row['Close']))
                    existing.adjusted_close = Decimal(str(row.get('Adj Close', row['Close'])))
                    existing.volume = int(row['Volume'])
                else:
                    # Create new record
                    price_record = PriceHistory(
                        company_id=company.company_id,
                        date=date_obj,
                        open=Decimal(str(row['Open'])),
                        high=Decimal(str(row['High'])),
                        low=Decimal(str(row['Low'])),
                        close=Decimal(str(row['Close'])),
                        adjusted_close=Decimal(str(row.get('Adj Close', row['Close']))),
                        volume=int(row['Volume'])
                    )
                    db.session.add(price_record)
                
                count += 1
                
            except Exception as e:
                logger.error(f"Failed to process price record for {symbol} on {date_val}: {str(e)}")
                continue
        
        # Update company last_updated timestamp
        company.last_updated = datetime.utcnow()
        
        db.session.commit()
        logger.info(f"Updated {count} price records for {symbol}")
        return count
    
    def _validate_static_mode(self):
        """Validate static mode configuration on startup"""
        if current_app.config.get('DATA_MODE') == 'STATIC':
            static_dir = current_app.config.get('STATIC_DATA_DIR')
            
            if not os.path.exists(static_dir):
                logger.error(f"Static data directory not found: {static_dir}")
                logger.warning("Switching to LIVE mode")
                current_app.config['DATA_MODE'] = 'LIVE'
                return
            
            # Check if directory has at least one CSV file
            csv_files = [f for f in os.listdir(static_dir) if f.endswith('.csv')]
            if not csv_files:
                logger.error(f"No CSV files found in static data directory: {static_dir}")
                logger.warning("Switching to LIVE mode")
                current_app.config['DATA_MODE'] = 'LIVE'
                return
            
            logger.info(f"Static mode validated. Found {len(csv_files)} CSV files")
            
            # Validate SIMULATION_DATE if provided
            sim_date = current_app.config.get('SIMULATION_DATE')
            if sim_date:
                try:
                    datetime.strptime(sim_date, '%Y-%m-%d')
                    logger.info(f"Simulation date set to: {sim_date}")
                except ValueError:
                    logger.error(f"Invalid SIMULATION_DATE format: {sim_date}. Expected YYYY-MM-DD")
    
    def _get_static_price(self, symbol: str, target_date: Optional[date] = None) -> Decimal:
        """
        Get price from static CSV file
        
        Args:
            symbol: Stock symbol
            target_date: Date to get price for (default: SIMULATION_DATE or today)
            
        Returns:
            Price as Decimal
            
        Raises:
            ValidationError: If CSV file not found or date not in file
        """
        static_dir = current_app.config.get('STATIC_DATA_DIR')
        csv_path = os.path.join(static_dir, f"{symbol}.csv")
        
        if not os.path.exists(csv_path):
            raise ValidationError(f"Static data file not found for {symbol}")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_path, parse_dates=['Date'], index_col='Date')
            
            # Determine target date
            if not target_date:
                sim_date_str = current_app.config.get('SIMULATION_DATE')
                if sim_date_str:
                    target_date = datetime.strptime(sim_date_str, '%Y-%m-%d').date()
                else:
                    target_date = date.today()
            
            # Find the closest date in the CSV (on or before target date)
            df_dates = df.index.date
            valid_dates = [d for d in df_dates if d <= target_date]
            
            if not valid_dates:
                raise ValidationError(f"No data available for {symbol} on or before {target_date}")
            
            closest_date = max(valid_dates)
            price_row = df[df.index.date == closest_date].iloc[0]
            
            price = Decimal(str(price_row['Close']))
            logger.info(f"Retrieved static price for {symbol} on {closest_date}: ${price}")
            return price
            
        except Exception as e:
            logger.error(f"Failed to read static price for {symbol}: {str(e)}")
            raise ValidationError(f"Failed to read static data: {str(e)}")
    
    def get_current_price_with_mode(self, symbol: str) -> Decimal:
        """
        Get current price respecting DATA_MODE configuration
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price as Decimal
        """
        data_mode = current_app.config.get('DATA_MODE', 'LIVE')
        
        if data_mode == 'STATIC':
            return self._get_static_price(symbol)
        else:
            return self.get_current_price(symbol)
    
    def download_and_save_stock_data(
        self, 
        symbol: str, 
        start_date: str, 
        end_date: str, 
        output_dir: Optional[str] = None
    ) -> str:
        """
        Download stock data from yfinance and save as CSV
        Management command for creating static datasets
        
        Args:
            symbol: Stock symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            output_dir: Output directory (default: STATIC_DATA_DIR)
            
        Returns:
            Path to saved CSV file
            
        Raises:
            ExternalAPIError: If download fails
        """
        try:
            # Download data
            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date)
            
            if df.empty:
                raise ExternalAPIError(f"No data available for {symbol}")
            
            # Prepare output directory
            if not output_dir:
                output_dir = current_app.config.get('STATIC_DATA_DIR')
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Save to CSV
            output_path = os.path.join(output_dir, f"{symbol}.csv")
            df.to_csv(output_path)
            
            logger.info(f"Saved {len(df)} records for {symbol} to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to download data for {symbol}: {str(e)}")
            raise ExternalAPIError(f"Failed to download stock data: {str(e)}")

