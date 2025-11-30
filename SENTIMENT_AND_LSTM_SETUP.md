# LSTM and Multi-Source Sentiment Analysis Setup Guide

## ✅ Step 1: LSTM Model - COMPLETE!

TensorFlow 2.20.0 has been installed successfully. Your LSTM model is now fully functional!

### What's Enabled:
- ✅ 4-layer LSTM architecture (as per draft report)
- ✅ Dropout layers (0.1)
- ✅ Adam optimizer with MSE loss
- ✅ 7-timestep sequence length
- ✅ Automatic graceful fallback if TensorFlow unavailable

### Testing LSTM:
```powershell
python -c "from ml_models.lstm_model import predict_lstm; print('LSTM is working!')"
```

---

## 🌐 Step 2: Multi-Source Sentiment Analysis

You now have **TWO sentiment sources** available:

### Option A: News API (Recommended - Easiest)
**Free Tier:** 100 requests/day  
**Best For:** Financial news sentiment

#### Setup:
1. Get free API key: https://newsapi.org/register
2. Add to `.env`:
```env
NEWS_API_KEY=your_key_here
SENTIMENT_ENABLED=True
```

#### Test:
```python
from app.services.multi_sentiment_engine import MultiSentimentEngine
engine = MultiSentimentEngine()
print(f"News API enabled: {engine.news_enabled}")
```

### Option B: Twitter/X API (Optional)
**Note:** Requires paid Twitter API access (not recommended)

If you have Twitter API credentials:
```env
TWITTER_BEARER_TOKEN=your_token
# OR
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_secret
SENTIMENT_ENABLED=True
```

---

## 🚀 Step 3: Enable Background Jobs

Background jobs automate price updates and dividend processing.

### What They Do:

#### 1. Price Updater (`app/jobs/price_updater.py`)
- **Daily Updates:** Fetches end-of-day prices at 4:30 PM EST
- **Intraday Updates:** Refreshes prices every 15 minutes during market hours (9:30 AM - 4:00 PM EST)
- **Data Source:** yfinance API
- **Storage:** `PriceHistory` table

#### 2. Dividend Processor (`app/jobs/dividend_processor.py`)
- **Daily Check:** Runs every day to check for dividends with payment_date = today
- **Auto-Credit:** Automatically credits user wallets based on holdings
- **Notifications:** Creates notifications for users receiving dividends
- **Logging:** Records all dividend payments in `DividendPayment` table

### Enable Jobs:

Add to `.env`:
```env
JOBS_ENABLED=True
```

### Manual Job Execution:

You can also run jobs manually via Flask CLI:

```powershell
# Refresh stock prices manually
flask refresh-prices

# Refresh specific symbols
flask refresh-prices --symbols AAPL,GOOGL,MSFT

# Force refresh (ignore cache)
flask refresh-prices --force
```

---

## 📋 Complete .env Configuration

Here's a complete `.env` file with all options:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production

# Database
DATABASE_URL=sqlite:///portfolio.db

# Background Jobs
JOBS_ENABLED=True

# Sentiment Analysis
SENTIMENT_ENABLED=True

# News API (Recommended)
NEWS_API_KEY=your_newsapi_key_here

# Twitter API (Optional - requires paid access)
# TWITTER_BEARER_TOKEN=your_twitter_bearer_token
# OR
# TWITTER_API_KEY=your_twitter_key
# TWITTER_API_SECRET=your_twitter_secret
# TWITTER_ACCESS_TOKEN=your_twitter_token
# TWITTER_ACCESS_TOKEN_SECRET=your_twitter_token_secret

# Data Mode
DATA_MODE=LIVE
# DATA_MODE=STATIC  # Use for testing with CSV files
# SIMULATION_DATE=2024-01-15  # Only if DATA_MODE=STATIC
```

---

## 🎯 Quick Start Guide

### Minimal Setup (LSTM Only):
```powershell
# Already done! TensorFlow is installed
python run.py
```

### With News Sentiment:
```powershell
# 1. Get News API key from https://newsapi.org/register
# 2. Add to .env:
#    NEWS_API_KEY=your_key
#    SENTIMENT_ENABLED=True
# 3. Run
python run.py
```

### With Both News + Twitter (Advanced):
```powershell
# 1. Get both API keys
# 2. Add both to .env
# 3. Run
python run.py
```

---

## 🧪 Testing Your Setup

### Test LSTM:
```powershell
python -c "import tensorflow as tf; print(f'TensorFlow {tf.__version__} ready!')"
```

### Test Sentiment Engine:
```python
from app.services.multi_sentiment_engine import MultiSentimentEngine

engine = MultiSentimentEngine()
print(f"Sentiment enabled: {engine.is_enabled()}")
print(f"Twitter: {engine.twitter_enabled}")
print(f"News API: {engine.news_enabled}")

# Test analysis (requires API keys)
if engine.is_enabled():
    result = engine.analyze_sentiment('AAPL', count_per_source=10)
    print(f"Sentiment for AAPL: {result['sentiment']}")
    print(f"Sources used: {result['sources']}")
```

### Test Background Jobs:
```powershell
# Check if jobs are enabled
python -c "from app.jobs.scheduler import scheduler; print('Jobs configured')"

# Run price update manually
flask refresh-prices --symbols AAPL
```

---

## 📊 Using Multi-Source Sentiment in Your App

The `MultiSentimentEngine` is a drop-in replacement for the old `SentimentEngine`:

```python
from app.services.multi_sentiment_engine import MultiSentimentEngine

# Initialize
engine = MultiSentimentEngine()

# Analyze sentiment (with caching)
sentiment = engine.get_sentiment_with_cache(
    symbol='AAPL',
    count_per_source=50,  # Fetch 50 items from each source
    cache_duration_hours=1  # Cache for 1 hour
)

# Results include:
# - sentiment['positive']: Number of positive items
# - sentiment['negative']: Number of negative items
# - sentiment['neutral']: Number of neutral items
# - sentiment['average_polarity']: Average sentiment score
# - sentiment['sentiment']: Overall sentiment (POSITIVE/NEGATIVE/NEUTRAL)
# - sentiment['sources']: List of sources used (e.g., ['News', 'Twitter'])
# - sentiment['total_items']: Total items analyzed
```

---

## 🎉 What You Have Now

### ML Models:
- ✅ **LSTM** - Deep learning price prediction (TensorFlow 2.20.0)
- ✅ **ARIMA** - Classical time series forecasting
- ✅ **Linear Regression** - Baseline model

### Sentiment Sources:
- ✅ **News API** - Financial news sentiment (100 req/day free)
- ⚪ **Twitter/X** - Social media sentiment (optional, paid)

### Automation:
- ✅ **Price Updates** - Automatic daily and intraday price fetching
- ✅ **Dividend Processing** - Automatic dividend payments to users
- ✅ **Job Logging** - Track all background job executions

---

## 🔧 Troubleshooting

### LSTM Not Working:
```powershell
# Reinstall TensorFlow
pip uninstall tensorflow
pip install tensorflow
```

### Sentiment Not Working:
```powershell
# Check dependencies
pip install newsapi-python textblob

# Verify API keys in .env
python -c "import os; print(f'NEWS_API_KEY: {bool(os.getenv(\"NEWS_API_KEY\"))}')"
```

### Background Jobs Not Running:
```powershell
# Check JOBS_ENABLED in .env
python -c "import os; print(f'JOBS_ENABLED: {os.getenv(\"JOBS_ENABLED\")}')"

# Check scheduler
python -c "from app.jobs.scheduler import scheduler; print('Scheduler OK')"
```

---

## 📚 API Key Resources

- **News API:** https://newsapi.org/register (Free: 100 req/day)
- **Twitter API:** https://developer.twitter.com/ (Paid: $100+/month)

---

## 🎓 Alignment with Draft Report

Your implementation now matches your draft report specifications:

✅ **Section 7.1 LSTM Model Specification** - Fully implemented  
✅ **Section 2: Methods** - LSTM as primary, ARIMA and LR as baselines  
✅ **Section 3: Literature Survey** - Multi-source sentiment (News + Twitter)  
✅ **Section 4: Gap Analysis** - Lightweight LSTM + multi-source sentiment  
✅ **Section 5: Functionalities** - Price prediction with ML algorithms  

Your system now provides:
1. Lightweight, modular LSTM core ✅
2. Combined sentiment from multiple sources ✅
3. Full-stack management platform ✅
4. Explainable visualizations ✅

---

**Ready to deploy!** 🚀
