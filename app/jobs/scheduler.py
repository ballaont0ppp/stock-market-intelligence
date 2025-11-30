"""
Background Job Scheduler
APScheduler configuration and job registration
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = None


def init_scheduler(app):
    """
    Initialize and start the background job scheduler
    
    Args:
        app: Flask application instance
    """
    global scheduler
    
    if not app.config.get('JOBS_ENABLED', True):
        app.logger.info('Background jobs are disabled')
        return
    
    # Temporarily disabled - jobs need to be implemented
    app.logger.info('Background jobs are temporarily disabled')
    return
    
    scheduler = BackgroundScheduler()
    
    # Import job functions
    # from app.jobs.dividend_processor import process_dividends
    # from app.jobs.price_updater import update_daily_prices, update_intraday_prices
    
    # Dividend processing job - runs daily at 4:00 PM EST
    scheduler.add_job(
        func=lambda: _run_job_with_app_context(app, process_dividends),
        trigger=CronTrigger(hour=16, minute=0, timezone='US/Eastern'),
        id='dividend_processor',
        name='Dividend Processor',
        replace_existing=True
    )
    
    # Daily price update job - runs at 4:30 PM EST on weekdays (after market close)
    scheduler.add_job(
        func=lambda: _run_job_with_app_context(app, update_daily_prices),
        trigger=CronTrigger(day_of_week='mon-fri', hour=16, minute=30, timezone='US/Eastern'),
        id='daily_price_update',
        name='Daily Price Update',
        replace_existing=True
    )
    
    # Intraday price refresh job - runs every 15 minutes during market hours (9:30 AM - 4:00 PM EST)
    scheduler.add_job(
        func=lambda: _run_job_with_app_context(app, update_intraday_prices),
        trigger=CronTrigger(day_of_week='mon-fri', hour='9-16', minute='*/15', timezone='US/Eastern'),
        id='intraday_price_refresh',
        name='Intraday Price Refresh',
        replace_existing=True
    )
    
    scheduler.start()
    app.logger.info('Background job scheduler started')


def _run_job_with_app_context(app, job_func):
    """
    Run a job function within Flask application context
    
    Args:
        app: Flask application instance
        job_func: Job function to execute
    """
    with app.app_context():
        job_func()
