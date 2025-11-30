"""
Application Entry Point
Runs the Flask development server
"""
import os
from app import create_app, db

# Get configuration from environment variable or use default
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)


@app.shell_context_processor
def make_shell_context():
    """
    Make database and models available in Flask shell
    """
    from app import models
    return {
        'db': db,
        'User': models.User,
        'Company': models.Company,
        'Wallet': models.Wallet,
        'Holdings': models.Holdings,
        'Order': models.Order,
        'Transaction': models.Transaction,
        'Dividend': models.Dividend,
        'DividendPayment': models.DividendPayment,
        'Broker': models.Broker,
        'Notification': models.Notification,
        'SentimentCache': models.SentimentCache,
        'PriceHistory': models.PriceHistory,
        'JobLog': models.JobLog
    }


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized successfully!")


@app.cli.command()
def seed_data():
    """Seed initial data"""
    from scripts.seed_data import seed_companies, seed_admin_user, seed_test_users
    seed_companies()
    seed_admin_user()
    seed_test_users()
    print("Database seeded successfully!")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
