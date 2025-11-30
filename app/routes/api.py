"""
API Routes Blueprint
Provides API endpoints for stock search, discovery, and data access
"""
import logging
import time
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from decimal import Decimal

from app.services.stock_repository import StockRepository
from app.utils.error_handlers import ValidationError, ExternalAPIError

bp = Blueprint('api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)


def log_api_call(f):
    """Decorator to log API calls with response times"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        endpoint = request.endpoint
        method = request.method
        user_id = current_user.user_id if current_user.is_authenticated else None
        
        try:
            response = f(*args, **kwargs)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Get status code from response
            if isinstance(response, tuple):
                status_code = response[1] if len(response) > 1 else 200
            else:
                status_code = 200
            
            logger.info(
                f"API call: {method} {endpoint} | user_id={user_id} | "
                f"status={status_code} | response_time={response_time:.2f}ms"
            )
            
            return response
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(
                f"API call failed: {method} {endpoint} | user_id={user_id} | "
                f"error={str(e)} | response_time={response_time:.2f}ms",
                exc_info=True
            )
            raise
    
    return decorated_function


@bp.route('/stocks/search', methods=['GET'])
@login_required
@log_api_call
def search_stocks():
    """
    Search for stocks by symbol or company name
    
    Query Parameters:
        q: Search query (symbol or company name)
        sector: Filter by sector
        market_cap_min: Minimum market cap
        market_cap_max: Maximum market cap
        page: Page number (default: 1)
        per_page: Items per page (default: 20)
    
    Returns:
        JSON response with search results
    """
    try:
        # Get query parameters
        query = request.args.get('q', '').strip()
        sector = request.args.get('sector', '').strip()
        market_cap_min = request.args.get('market_cap_min', type=int)
        market_cap_max = request.args.get('market_cap_max', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build filters
        filters = {}
        if sector:
            filters['sector'] = sector
        if market_cap_min:
            filters['market_cap_min'] = market_cap_min
        if market_cap_max:
            filters['market_cap_max'] = market_cap_max
        
        # Search companies
        repo = StockRepository()
        companies, total = repo.search_companies(
            query=query if query else None,
            filters=filters,
            page=page,
            per_page=per_page
        )
        
        # Format results
        results = []
        for company in companies:
            # Get current price
            try:
                current_price = repo.get_current_price_with_mode(company.symbol)
                
                # Get day change (compare with yesterday's close)
                price_history = repo.get_price_history(company.symbol, end_date=None)
                day_change_pct = None
                if len(price_history) >= 2:
                    yesterday_close = price_history[-2].close
                    if yesterday_close > 0:
                        day_change_pct = float((current_price - yesterday_close) / yesterday_close * 100)
                
            except Exception:
                current_price = None
                day_change_pct = None
            
            results.append({
                'company_id': company.company_id,
                'symbol': company.symbol,
                'company_name': company.company_name,
                'sector': company.sector,
                'industry': company.industry,
                'market_cap': company.market_cap,
                'current_price': float(current_price) if current_price else None,
                'day_change_pct': round(day_change_pct, 2) if day_change_pct else None
            })
        
        return jsonify({
            'success': True,
            'data': {
                'results': results,
                'total': total,
                'page': page,
                'per_page': per_page,
                'total_pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Stock search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/stocks/autocomplete', methods=['GET'])
@login_required
@log_api_call
def autocomplete_stocks():
    """
    Autocomplete endpoint for stock symbol search
    
    Query Parameters:
        q: Search query (partial symbol or company name)
        limit: Maximum results (default: 10)
    
    Returns:
        JSON response with matching stocks
    """
    try:
        query = request.args.get('q', '').strip()
        limit = request.args.get('limit', 10, type=int)
        
        if not query or len(query) < 1:
            return jsonify({
                'success': True,
                'data': []
            })
        
        # Search companies
        repo = StockRepository()
        companies, _ = repo.search_companies(
            query=query,
            page=1,
            per_page=limit
        )
        
        # Format results for autocomplete
        results = []
        for company in companies:
            results.append({
                'symbol': company.symbol,
                'company_name': company.company_name,
                'label': f"{company.symbol} - {company.company_name}"
            })
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        current_app.logger.error(f"Autocomplete error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/stocks/trending', methods=['GET'])
@login_required
@log_api_call
def trending_stocks():
    """
    Get trending stocks based on recent trading activity
    
    Query Parameters:
        limit: Maximum results (default: 10)
    
    Returns:
        JSON response with trending stocks
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        repo = StockRepository()
        trending = repo.get_trending_stocks(limit=limit)
        
        # Enrich with current prices
        for stock in trending:
            try:
                current_price = repo.get_current_price_with_mode(stock['symbol'])
                stock['current_price'] = float(current_price)
            except Exception:
                stock['current_price'] = None
        
        return jsonify({
            'success': True,
            'data': trending
        })
        
    except Exception as e:
        current_app.logger.error(f"Trending stocks error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/stocks/<symbol>', methods=['GET'])
@login_required
@log_api_call
def get_stock_details(symbol):
    """
    Get detailed information about a stock
    
    Args:
        symbol: Stock symbol
    
    Returns:
        JSON response with stock details
    """
    try:
        repo = StockRepository()
        company = repo.get_company_by_symbol(symbol)
        
        if not company:
            return jsonify({
                'success': False,
                'error': f'Stock not found: {symbol}'
            }), 404
        
        # Get current price
        try:
            current_price = repo.get_current_price_with_mode(symbol)
        except Exception:
            current_price = None
        
        # Get price history (last year)
        try:
            price_history = repo.get_price_history(symbol)
            history_data = [
                {
                    'date': ph.date.isoformat(),
                    'open': float(ph.open),
                    'high': float(ph.high),
                    'low': float(ph.low),
                    'close': float(ph.close),
                    'volume': ph.volume
                }
                for ph in price_history[-365:]  # Last year
            ]
        except Exception:
            history_data = []
        
        return jsonify({
            'success': True,
            'data': {
                'company_id': company.company_id,
                'symbol': company.symbol,
                'company_name': company.company_name,
                'sector': company.sector,
                'industry': company.industry,
                'market_cap': company.market_cap,
                'description': company.description,
                'website': company.website,
                'ceo': company.ceo,
                'employees': company.employees,
                'headquarters': company.headquarters,
                'current_price': float(current_price) if current_price else None,
                'price_history': history_data
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Get stock details error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/stocks/<symbol>/price', methods=['GET'])
@login_required
@log_api_call
def get_stock_price(symbol):
    """
    Get current price for a stock
    
    Args:
        symbol: Stock symbol
    
    Returns:
        JSON response with current price
    """
    try:
        repo = StockRepository()
        price = repo.get_current_price_with_mode(symbol)
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol.upper(),
                'price': float(price),
                'timestamp': current_app.config.get('SIMULATION_DATE') or 'live'
            }
        })
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except ExternalAPIError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 503
    except Exception as e:
        current_app.logger.error(f"Get stock price error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch stock price'
        }), 500


@bp.route('/stocks/sectors', methods=['GET'])
@login_required
def get_sectors():
    """
    Get list of all available sectors
    
    Returns:
        JSON response with sector list
    """
    try:
        repo = StockRepository()
        sectors = repo.get_all_sectors()
        
        return jsonify({
            'success': True,
            'data': sectors
        })
        
    except Exception as e:
        current_app.logger.error(f"Get sectors error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



# Notification API Endpoints

@bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """
    Get notifications for the current user
    
    Query Parameters:
        limit: Maximum number of notifications (default: 10)
        unread_only: Only return unread notifications (default: false)
    
    Returns:
        JSON response with notifications and unread count
    """
    try:
        from app.services.notification_service import NotificationService
        
        limit = request.args.get('limit', 10, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        notification_service = NotificationService()
        
        # Get notifications
        notifications = notification_service.get_user_notifications(
            user_id=current_user.user_id,
            unread_only=unread_only,
            limit=limit
        )
        
        # Get unread count
        unread_count = notification_service.get_unread_count(current_user.user_id)
        
        # Format notifications
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'notification_id': notification.notification_id,
                'notification_type': notification.notification_type,
                'title': notification.title,
                'message': notification.message,
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat(),
                'read_at': notification.read_at.isoformat() if notification.read_at else None
            })
        
        return jsonify({
            'success': True,
            'notifications': notifications_data,
            'unread_count': unread_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Get notifications error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """
    Mark a notification as read
    
    Args:
        notification_id: ID of the notification
    
    Returns:
        JSON response with success status
    """
    try:
        from app.services.notification_service import NotificationService
        from app.models.notification import Notification
        
        # Verify notification belongs to current user
        notification = Notification.query.get(notification_id)
        if not notification:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
        if notification.user_id != current_user.user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        notification_service = NotificationService()
        success = notification_service.mark_as_read(notification_id)
        
        return jsonify({
            'success': success
        })
        
    except Exception as e:
        current_app.logger.error(f"Mark notification read error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """
    Mark all notifications as read for the current user
    
    Returns:
        JSON response with count of notifications marked as read
    """
    try:
        from app.services.notification_service import NotificationService
        
        notification_service = NotificationService()
        count = notification_service.mark_all_as_read(current_user.user_id)
        
        return jsonify({
            'success': True,
            'count': count
        })
        
    except Exception as e:
        current_app.logger.error(f"Mark all notifications read error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    """
    Delete a notification
    
    Args:
        notification_id: ID of the notification
    
    Returns:
        JSON response with success status
    """
    try:
        from app.services.notification_service import NotificationService
        from app.models.notification import Notification
        
        # Verify notification belongs to current user
        notification = Notification.query.get(notification_id)
        if not notification:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
        if notification.user_id != current_user.user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        notification_service = NotificationService()
        success = notification_service.delete_notification(notification_id)
        
        return jsonify({
            'success': success
        })
        
    except Exception as e:
        current_app.logger.error(f"Delete notification error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
