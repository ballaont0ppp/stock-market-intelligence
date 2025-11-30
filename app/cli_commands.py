"""
Flask CLI Commands
Custom management commands for the application
"""
import click
from flask import current_app
from flask.cli import with_appcontext
from datetime import datetime

from app.services.stock_repository import StockRepository


@click.command('import-stock-data')
@click.option('--symbol', required=True, help='Stock symbol (e.g., AAPL)')
@click.option('--start', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end', required=True, help='End date (YYYY-MM-DD)')
@click.option('--output', default=None, help='Output directory (default: data/stocks/)')
@with_appcontext
def import_stock_data(symbol, start, end, output):
    """
    Download and save stock data as CSV for offline use
    
    Example:
        flask import-stock-data --symbol AAPL --start 2020-01-01 --end 2023-12-31
    """
    click.echo(f"Downloading data for {symbol} from {start} to {end}...")
    
    try:
        # Validate dates
        datetime.strptime(start, '%Y-%m-%d')
        datetime.strptime(end, '%Y-%m-%d')
        
        # Download and save
        repo = StockRepository()
        output_path = repo.download_and_save_stock_data(symbol, start, end, output)
        
        click.echo(f"✓ Successfully saved data to: {output_path}")
        
    except ValueError as e:
        click.echo(f"✗ Invalid date format: {str(e)}", err=True)
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)


@click.command('refresh-prices')
@click.option('--symbols', default=None, help='Comma-separated list of symbols (e.g., AAPL,GOOGL,MSFT)')
@click.option('--date', default=None, help='Date to fetch prices for (YYYY-MM-DD, default: today)')
@click.option('--force', is_flag=True, help='Force refresh even if data exists')
@with_appcontext
def refresh_prices(symbols, date, force):
    """
    Manually trigger price refresh for stocks
    
    Example:
        flask refresh-prices --symbols AAPL,GOOGL,MSFT
        flask refresh-prices --date 2024-01-15 --force
        flask refresh-prices  # Refresh all active stocks
    """
    from app.models.company import Company
    from app.models.price_history import PriceHistory
    from app.models.holding import Holdings
    from app import db
    from decimal import Decimal
    import yfinance as yf
    
    click.echo("Starting manual price refresh...")
    
    # Determine which symbols to refresh
    if symbols:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        companies = Company.query.filter(Company.symbol.in_(symbol_list), Company.is_active == True).all()
        
        if not companies:
            click.echo(f"✗ No active companies found for symbols: {symbols}", err=True)
            return
    else:
        # Refresh all actively traded stocks (stocks in holdings)
        active_company_ids = db.session.query(Holdings.company_id).distinct().all()
        active_company_ids = [cid[0] for cid in active_company_ids]
        
        if not active_company_ids:
            click.echo("No actively traded stocks found. Refreshing all active companies instead...")
            companies = Company.query.filter_by(is_active=True).limit(50).all()
        else:
            companies = Company.query.filter(
                Company.company_id.in_(active_company_ids),
                Company.is_active == True
            ).all()
    
    if not companies:
        click.echo("No companies found to refresh")
        return
    
    click.echo(f"Refreshing prices for {len(companies)} companies...")
    
    # Parse target date if provided
    target_date = None
    if date:
        try:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()
            click.echo(f"Target date: {target_date}")
        except ValueError:
            click.echo(f"✗ Invalid date format: {date}. Use YYYY-MM-DD", err=True)
            return
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    with click.progressbar(companies, label='Processing') as bar:
        for company in bar:
            try:
                # Check if data already exists (unless force flag is set)
                if not force and target_date:
                    existing = PriceHistory.query.filter_by(
                        company_id=company.company_id,
                        date=target_date
                    ).first()
                    
                    if existing:
                        skipped_count += 1
                        continue
                
                # Fetch latest data from yfinance
                ticker = yf.Ticker(company.symbol)
                df = ticker.history(period='1d')
                
                if df.empty:
                    click.echo(f"\n✗ {company.symbol} - No data available")
                    failed_count += 1
                    continue
                
                # Get the latest row
                latest_data = df.iloc[-1]
                price_date = df.index[-1].date()
                
                # Use target date if specified
                if target_date:
                    price_date = target_date
                
                # Check if record exists
                price_record = PriceHistory.query.filter_by(
                    company_id=company.company_id,
                    date=price_date
                ).first()
                
                if price_record:
                    # Update existing record
                    price_record.open = Decimal(str(latest_data['Open']))
                    price_record.high = Decimal(str(latest_data['High']))
                    price_record.low = Decimal(str(latest_data['Low']))
                    price_record.close = Decimal(str(latest_data['Close']))
                    price_record.volume = int(latest_data['Volume'])
                else:
                    # Create new record
                    price_record = PriceHistory(
                        company_id=company.company_id,
                        date=price_date,
                        open=Decimal(str(latest_data['Open'])),
                        high=Decimal(str(latest_data['High'])),
                        low=Decimal(str(latest_data['Low'])),
                        close=Decimal(str(latest_data['Close'])),
                        adjusted_close=Decimal(str(latest_data['Close'])),
                        volume=int(latest_data['Volume'])
                    )
                    db.session.add(price_record)
                
                # Update company last_updated
                company.last_updated = datetime.utcnow()
                
                db.session.commit()
                success_count += 1
                
            except Exception as e:
                click.echo(f"\n✗ {company.symbol} - {str(e)}")
                failed_count += 1
                db.session.rollback()
    
    click.echo(f"\n{'='*50}")
    click.echo(f"Completed:")
    click.echo(f"  ✓ Successful: {success_count}")
    click.echo(f"  ✗ Failed: {failed_count}")
    if skipped_count > 0:
        click.echo(f"  ⊘ Skipped (already exists): {skipped_count}")
    click.echo(f"{'='*50}")


@click.command('run-daily-price-update')
@with_appcontext
def run_daily_price_update():
    """
    Manually run the daily price update job
    
    Example:
        flask run-daily-price-update
    """
    from app.jobs.price_updater import update_daily_prices
    
    click.echo("Running daily price update job...")
    
    try:
        update_daily_prices()
        click.echo("✓ Daily price update job completed successfully")
    except Exception as e:
        click.echo(f"✗ Daily price update job failed: {str(e)}", err=True)


@click.command('run-intraday-refresh')
@with_appcontext
def run_intraday_refresh():
    """
    Manually run the intraday price refresh job
    
    Example:
        flask run-intraday-refresh
    """
    from app.jobs.price_updater import update_intraday_prices
    
    click.echo("Running intraday price refresh job...")
    
    try:
        update_intraday_prices()
        click.echo("✓ Intraday price refresh job completed successfully")
    except Exception as e:
        click.echo(f"✗ Intraday price refresh job failed: {str(e)}", err=True)


@click.command('run-dividend-processor')
@with_appcontext
def run_dividend_processor():
    """
    Manually run the dividend processor job
    
    Example:
        flask run-dividend-processor
    """
    from app.jobs.dividend_processor import process_dividends
    
    click.echo("Running dividend processor job...")
    
    try:
        process_dividends()
        click.echo("✓ Dividend processor job completed successfully")
    except Exception as e:
        click.echo(f"✗ Dividend processor job failed: {str(e)}", err=True)


@click.command('list-jobs')
@with_appcontext
def list_jobs():
    """
    List all scheduled background jobs
    
    Example:
        flask list-jobs
    """
    from app.jobs.scheduler import scheduler
    
    if not scheduler:
        click.echo("Background jobs are disabled")
        return
    
    jobs = scheduler.get_jobs()
    
    if not jobs:
        click.echo("No scheduled jobs found")
        return
    
    click.echo(f"\nScheduled Background Jobs ({len(jobs)}):")
    click.echo("=" * 80)
    
    for job in jobs:
        click.echo(f"\nJob ID: {job.id}")
        click.echo(f"Name: {job.name}")
        click.echo(f"Next Run: {job.next_run_time}")
        click.echo(f"Trigger: {job.trigger}")
        click.echo("-" * 80)


@click.command('view-job-logs')
@click.option('--job-name', default=None, help='Filter by job name')
@click.option('--limit', default=10, help='Number of recent logs to show')
@with_appcontext
def view_job_logs(job_name, limit):
    """
    View recent job execution logs
    
    Example:
        flask view-job-logs
        flask view-job-logs --job-name daily_price_update --limit 5
    """
    from app.models.job_log import JobLog
    
    query = JobLog.query
    
    if job_name:
        query = query.filter_by(job_name=job_name)
    
    logs = query.order_by(JobLog.started_at.desc()).limit(limit).all()
    
    if not logs:
        click.echo("No job logs found")
        return
    
    click.echo(f"\nRecent Job Logs (showing {len(logs)}):")
    click.echo("=" * 100)
    
    for log in logs:
        status_icon = "✓" if log.status == 'SUCCESS' else "✗" if log.status == 'FAILED' else "⚠"
        
        click.echo(f"\n{status_icon} Job: {log.job_name}")
        click.echo(f"  Status: {log.status}")
        click.echo(f"  Started: {log.started_at}")
        click.echo(f"  Completed: {log.completed_at}")
        
        if log.stocks_processed or log.stocks_failed:
            click.echo(f"  Processed: {log.stocks_processed} | Failed: {log.stocks_failed}")
        
        if log.error_message:
            click.echo(f"  Error: {log.error_message[:100]}...")
        
        click.echo("-" * 100)


def register_commands(app):
    """Register all CLI commands with the Flask app"""
    app.cli.add_command(import_stock_data)
    app.cli.add_command(refresh_prices)
    app.cli.add_command(run_daily_price_update)
    app.cli.add_command(run_intraday_refresh)
    app.cli.add_command(run_dividend_processor)
    app.cli.add_command(list_jobs)
    app.cli.add_command(view_job_logs)

