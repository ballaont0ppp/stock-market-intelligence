"""
Reports Routes
Transaction reports, billing, and performance analytics
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_login import login_required, current_user
from datetime import datetime
import csv
import io

from app.services.report_service import ReportService
from app.forms.report_forms import TransactionReportForm, BillingReportForm, PerformanceReportForm

bp = Blueprint('reports', __name__, url_prefix='/reports')
report_service = None

def get_report_service():
    """Lazy load report service"""
    global report_service
    if report_service is None:
        report_service = ReportService()
    return report_service


@bp.route('/')
@login_required
def index():
    """Reports dashboard with report type selector"""
    transaction_form = TransactionReportForm()
    billing_form = BillingReportForm()
    performance_form = PerformanceReportForm()
    
    # Set default values
    transaction_form.end_date.data = datetime.utcnow().date()
    billing_form.month.data = str(datetime.utcnow().month)
    billing_form.year.data = datetime.utcnow().year
    
    return render_template(
        'reports/index.html',
        transaction_form=transaction_form,
        billing_form=billing_form,
        performance_form=performance_form
    )


@bp.route('/transaction', methods=['GET', 'POST'])
@login_required
def transaction_report():
    """Generate transaction report"""
    form = TransactionReportForm()
    report_data = None
    
    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data
        
        # Convert dates to datetime if provided
        if start_date:
            start_date = datetime.combine(start_date, datetime.min.time())
        if end_date:
            end_date = datetime.combine(end_date, datetime.max.time())
        
        try:
            report_data = get_report_service().generate_transaction_report(
                current_user.user_id,
                start_date,
                end_date
            )
            flash('Transaction report generated successfully', 'success')
        except Exception as e:
            flash(f'Error generating report: {str(e)}', 'error')
    
    return render_template(
        'reports/transaction.html',
        form=form,
        report=report_data
    )


@bp.route('/billing', methods=['GET', 'POST'])
@login_required
def billing_report():
    """Generate billing report"""
    form = BillingReportForm()
    report_data = None
    
    if form.validate_on_submit():
        month = int(form.month.data)
        year = form.year.data
        
        try:
            report_data = get_report_service().generate_billing_report(
                current_user.user_id,
                month,
                year
            )
            flash('Billing report generated successfully', 'success')
        except Exception as e:
            flash(f'Error generating report: {str(e)}', 'error')
    
    return render_template(
        'reports/billing.html',
        form=form,
        report=report_data
    )


@bp.route('/performance', methods=['GET', 'POST'])
@login_required
def performance_report():
    """Generate performance report"""
    form = PerformanceReportForm()
    report_data = None
    
    if form.validate_on_submit():
        period = form.period.data
        
        try:
            report_data = get_report_service().generate_performance_report(
                current_user.user_id,
                period
            )
            flash('Performance report generated successfully', 'success')
        except Exception as e:
            flash(f'Error generating report: {str(e)}', 'error')
    
    return render_template(
        'reports/performance.html',
        form=form,
        report=report_data
    )


@bp.route('/export/transaction/csv')
@login_required
def export_transaction_csv():
    """Export transaction report as CSV"""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Parse dates
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end_date = datetime.utcnow()
    
    try:
        report_data = get_report_service().generate_transaction_report(
            current_user.user_id,
            start_date,
            end_date
        )
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Date', 'Type', 'Symbol', 'Company', 'Amount',
            'Balance Before', 'Balance After', 'Description'
        ])
        
        # Write data
        for txn in report_data['transactions']:
            writer.writerow([
                txn['date'].strftime('%Y-%m-%d %H:%M:%S'),
                txn['type'],
                txn['company_symbol'] or '',
                txn['company_name'] or '',
                f"${txn['amount']:.2f}",
                f"${txn['balance_before']:.2f}",
                f"${txn['balance_after']:.2f}",
                txn['description'] or ''
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=transaction_report_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        
        return response
    
    except Exception as e:
        flash(f'Error exporting report: {str(e)}', 'error')
        return redirect(url_for('reports.transaction_report'))


@bp.route('/export/billing/csv')
@login_required
def export_billing_csv():
    """Export billing report as CSV"""
    month = int(request.args.get('month', datetime.utcnow().month))
    year = int(request.args.get('year', datetime.utcnow().year))
    
    try:
        report_data = get_report_service().generate_billing_report(
            current_user.user_id,
            month,
            year
        )
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Billing Report', report_data['period']])
        writer.writerow([])
        
        # Transaction counts
        writer.writerow(['Transaction Counts'])
        for key, value in report_data['transaction_counts'].items():
            writer.writerow([key.replace('_', ' ').title(), value])
        writer.writerow([])
        
        # Transaction volumes
        writer.writerow(['Transaction Volumes'])
        for key, value in report_data['transaction_volumes'].items():
            writer.writerow([key.replace('_', ' ').title(), f"${value:.2f}"])
        writer.writerow([])
        
        # Fee breakdown
        writer.writerow(['Fee Breakdown'])
        for key, value in report_data['fee_breakdown'].items():
            writer.writerow([key.replace('_', ' ').title(), f"${value:.2f}"])
        writer.writerow([])
        
        # Summary
        writer.writerow(['Summary'])
        for key, value in report_data['summary'].items():
            if isinstance(value, (int, float)):
                writer.writerow([key.replace('_', ' ').title(), f"${value:.2f}" if 'fee' in key else value])
            else:
                writer.writerow([key.replace('_', ' ').title(), value])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=billing_report_{year}_{month:02d}.csv'
        
        return response
    
    except Exception as e:
        flash(f'Error exporting report: {str(e)}', 'error')
        return redirect(url_for('reports.billing_report'))


@bp.route('/export/performance/csv')
@login_required
def export_performance_csv():
    """Export performance report as CSV"""
    period = request.args.get('period', '1m')
    
    try:
        report_data = get_report_service().generate_performance_report(
            current_user.user_id,
            period
        )
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Performance Report', f"Period: {period}"])
        writer.writerow([])
        
        # Summary metrics
        writer.writerow(['Summary Metrics'])
        writer.writerow(['Current Portfolio Value', f"${report_data['current_portfolio_value']:.2f}"])
        writer.writerow(['Total Invested', f"${report_data['total_invested']:.2f}"])
        writer.writerow(['Total Gain/Loss', f"${report_data['total_gain_loss']:.2f}"])
        writer.writerow(['Total Return %', f"{report_data['total_return_pct']:.2f}%"])
        writer.writerow(['Annualized Return', f"{report_data['annualized_return']:.2f}%"])
        writer.writerow(['Win Rate', f"{report_data['win_rate']:.2f}%"])
        writer.writerow(['Profitable Trades', report_data['profitable_trades']])
        writer.writerow(['Total Trades', report_data['total_trades']])
        writer.writerow([])
        
        # Holdings
        writer.writerow(['Holdings'])
        writer.writerow([
            'Symbol', 'Company', 'Quantity', 'Avg Price', 'Current Price',
            'Invested', 'Current Value', 'Gain/Loss', 'Gain/Loss %'
        ])
        
        for holding in report_data['holdings']:
            writer.writerow([
                holding['symbol'],
                holding['company_name'],
                holding['quantity'],
                f"${holding['average_price']:.2f}",
                f"${holding['current_price']:.2f}",
                f"${holding['invested']:.2f}",
                f"${holding['current_value']:.2f}",
                f"${holding['gain_loss']:.2f}",
                f"{holding['gain_loss_pct']:.2f}%"
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=performance_report_{period}_{datetime.utcnow().strftime("%Y%m%d")}.csv'
        
        return response
    
    except Exception as e:
        flash(f'Error exporting report: {str(e)}', 'error')
        return redirect(url_for('reports.performance_report'))
