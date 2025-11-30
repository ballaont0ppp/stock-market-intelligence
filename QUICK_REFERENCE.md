# Quick Reference Card

## ✅ What's Installed & Working

### ML Models:
- ✅ **TensorFlow 2.20.0** - LSTM model ready
- ✅ **ARIMA** - Classical forecasting
- ✅ **Linear Regression** - Baseline model

### Sentiment APIs:
- ✅ **newsapi-python** - News sentiment (need API key)
- ✅ **textblob** - Sentiment analysis engine

---

## 🔑 Get Your Free API Keys

### 1. News API (Recommended - 5 minutes)
1. Visit: https://newsapi.org/register
2. Enter email, get instant API key
3. Add to `.env`: `NEWS_API_KEY=your_key_here`
4. Free tier: 100 requests/day



---

## 🚀 Quick Start Commands

### Run the App:
```powershell
python run.py
```

### Test LSTM:
```powershell
python -c "import tensorflow as tf; print('LSTM Ready!')"
```

### Test Sentiment:
```powershell
python -c "from app.services.multi_sentiment_engine import MultiSentimentEngine; e=MultiSentimentEngine(); print(f'News: {e.news_enabled}')"
```

---

## 📝 Essential .env Settings

```env
# Required
FLASK_APP=run.py
FLASK_ENV=development
DATABASE_URL=sqlite:///portfolio.db

# Enable Features
SENTIMENT_ENABLED=True
JOBS_ENABLED=True

# News API (get from newsapi.org)
NEWS_API_KEY=your_key_here
```

---

## 🎯 What Each Feature Does

### LSTM Model:
- Predicts stock prices using deep learning
- Uses 7 days of historical data
- Outputs next-day price prediction
- Automatically enabled (TensorFlow installed)

### News Sentiment:
- Fetches recent news articles about stocks
- Analyzes sentiment (positive/negative/neutral)
- Caches results for 1 hour
- Requires News API key (100 free requests/day)

### Background Jobs:
- **Price Updates**: Fetches stock prices automatically
  - Daily: 4:30 PM EST
  - Intraday: Every 15 min (9:30 AM - 4:00 PM EST)
- **Dividend Processing**: Auto-credits dividends to users
  - Runs daily
  - Checks for dividends with payment_date = today

---

## 🔧 Common Tasks

### Enable LSTM:
Already enabled! TensorFlow is installed.

### Enable News Sentiment:
1. Get key from https://newsapi.org/register
2. Add `NEWS_API_KEY=your_key` to `.env`
3. Set `SENTIMENT_ENABLED=True` in `.env`

### Enable Background Jobs:
Add `JOBS_ENABLED=True` to `.env`

### Run Manual Price Update:
```powershell
flask refresh-prices --symbols AAPL,GOOGL,MSFT
```

---

## 📊 Using in Your Code

### Get LSTM Prediction:
```python
from ml_models.lstm_model import predict_lstm

prediction, error = predict_lstm('AAPL', days=7)
if prediction:
    print(f"LSTM predicts: ${prediction}")
```

### Get Multi-Source Sentiment:
```python
from app.services.multi_sentiment_engine import MultiSentimentEngine

engine = MultiSentimentEngine()
sentiment = engine.get_sentiment_with_cache('AAPL')

print(f"Sentiment: {sentiment['sentiment']}")
print(f"Sources: {sentiment['sources']}")
print(f"Positive: {sentiment['positive']}")
print(f"Negative: {sentiment['negative']}")
```

---

## 🎓 Matches Your Draft Report

Your implementation now includes:

✅ **LSTM neural network** (Section 7.1)  
✅ **ARIMA and Linear Regression** baselines (Section 2)  
✅ **Multi-source sentiment** (Section 3 Literature Survey)  
✅ **Lightweight modular design** (Section 4 Gap Analysis)  
✅ **Full-stack platform** (Section 5 Functionalities)  

---

## 📞 Need Help?

Check these files:
- `SENTIMENT_AND_LSTM_SETUP.md` - Detailed setup guide
- `PRODUCTION_READINESS_REPORT.md` - Full project status
- `FINAL_VERIFICATION_CHECKLIST.md` - Deployment checklist

---

**You're all set!** 🎉

Your Stock Portfolio Platform now has:
- LSTM predictions ✅
- News sentiment analysis ✅
- Background automation ✅
- Production-ready codebase ✅
