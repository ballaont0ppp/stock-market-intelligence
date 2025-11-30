# Data Flow Diagram - Level 1
## Stock Market Prediction Web App

```mermaid
graph TD
    USER[User]
    APIS[External APIs<br/>Yahoo Finance]
    TWITTER[Twitter API]
    DB[(Database)]
    
    USER -->|Stock Symbol| VALIDATE[1.0 Validate Input]
    VALIDATE -->|Valid Request| FETCH[2.0 Fetch Stock Data]
    FETCH -->|Historical Data| PREDICT[3.0 Generate Predictions]
    TWITTER -->|Tweets| SENTIMENT[4.0 Analyze Sentiment]
    SENTIMENT -->|Sentiment Score| PREDICT
    PREDICT -->|Predictions| STORE[5.0 Store Results]
    STORE -->|Save| DB
    STORE -->|Results| FORMAT[6.0 Format Output]
    FORMAT -->|Display| USER
    DB -->|Retrieve| FETCH
    RETRIEVE_DATA --> FETCH_REALTIME_DATA
    RETRIEVE_DATA --> STORE_DATA
    RETRIEVE_DATA --> RETRIEVE_PROCESSED_DATA
    
    FETCH_STOCK_DATA --> EXTERNAL_APIS
    FETCH_REALTIME_DATA --> EXTERNAL_APIS
    STORE_DATA --> DB
    RETRIEVE_PROCESSED_DATA --> DB
    
    EXTERNAL_APIS -- "Stock Data" --> FETCH_STOCK_DATA
    EXTERNAL_APIS -- "Real-time Data" --> FETCH_REALTIME_DATA
    DB -- "Stored Data" --> STORE_DATA
    DB -- "Processed Data" --> RETRIEVE_PROCESSED_DATA
    
    RETRIEVE_PROCESSED_DATA --> PROCESS_PREDICTIONS
    PROCESS_PREDICTIONS --> ARIMA_MODEL
    PROCESS_PREDICTIONS --> LSTM_MODEL
    PROCESS_PREDICTIONS --> LINEAR_REGRESSION
    PROCESS_PREDICTIONS --> COMBINE_RESULTS
    
    ARIMA_MODEL --> DB
    LSTM_MODEL --> DB
    LINEAR_REGRESSION --> DB
    COMBINE_RESULTS --> DB
    
    DB -- "Historical Data" --> ARIMA_MODEL
    DB -- "Sequential Data" --> LSTM_MODEL
    DB -- "Feature Data" --> LINEAR_REGRESSION
    DB -- "Model Results" --> COMBINE_RESULTS
    
    ARIMA_MODEL --> PROCESS_PREDICTIONS
    LSTM_MODEL --> PROCESS_PREDICTIONS
    LINEAR_REGRESSION --> PROCESS_PREDICTIONS
    COMBINE_RESULTS --> PROCESS_PREDICTIONS
    
    PROCESS_PREDICTIONS --> ANALYZE_SENTIMENT
    ANALYZE_SENTIMENT --> COLLECT_TWEETS
    ANALYZE_SENTIMENT --> PROCESS_SENTIMENT
    ANALYZE_SENTIMENT --> STORE_SENTIMENT
    
    COLLECT_TWEETS --> SOCIAL_MEDIA
    PROCESS_SENTIMENT --> COLLECT_TWEETS
    STORE_SENTIMENT --> DB
    
    SOCIAL_MEDIA -- "Tweets" --> COLLECT_TWEETS
    COLLECT_TWEETS -- "Tweet Data" --> PROCESS_SENTIMENT
    PROCESS_SENTIMENT -- "Cleaned Text" --> STORE_SENTIMENT
    DB -- "Stored Scores" --> STORE_SENTIMENT
    
    STORE_SENTIMENT --> ANALYZE_SENTIMENT
    ANALYZE_SENTIMENT --> GENERATE_RECOMMENDATION
    GENERATE_RECOMMENDATION --> STORE_FINAL_RESULTS
    STORE_FINAL_RESULTS --> DB
    DB -- "Storage Confirmation" --> STORE_FINAL_RESULTS
    
    GENERATE_RECOMMENDATION --> FORMAT_OUTPUT
    FORMAT_OUTPUT --> FORMAT_RESULTS
    FORMAT_OUTPUT --> SEND_RESULTS
    
    FORMAT_RESULTS --> DB
    SEND_RESULTS --> USER
    
    DB -- "Processed Data" --> FORMAT_RESULTS
    FORMAT_RESULTS -- "Formatted Results" --> SEND_RESULTS
    SEND_RESULTS -- "6.0 View Results" --> USER
```

## Process Descriptions

### Process 1.0 - Receive Request
- **1.1 Validate Input**: Check if stock symbol is valid
- **1.2 Log Request**: Record user request for analytics

### Process 2.0 - Retrieve Data
- **2.1 Fetch Stock Data**: Get historical data from APIs
- **2.2 Fetch Real-time Data**: Get current market data
- **2.3 Store Data**: Save retrieved data for processing
- **2.4 Retrieve Data**: Get processed data for models

### Process 3.0 - Process Predictions
- **3.1 ARIMA Model**: Run time series forecasting
- **3.2 LSTM Model**: Run deep learning prediction
- **3.3 Linear Regression**: Run statistical modeling
- **3.4 Combine Results**: Merge predictions from all models

### Process 4.0 - Analyze Sentiment
- **4.1 Collect Tweets**: Gather social media data
- **4.2 Process Sentiment**: Analyze text for sentiment
- **4.3 Store Results**: Save sentiment analysis

### Process 5.0 - Generate Recommendation
- **5.1 Store Results**: Save final predictions

### Process 6.0 - Format Output
- **6.1 Format Output**: Prepare results for display
- **6.2 Send Results**: Return formatted results to user