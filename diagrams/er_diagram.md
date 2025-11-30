# Entity Relationship Diagram
## Stock Market Prediction Web App

```mermaid
erDiagram
    USERS ||--o{ STOCK_DATA : "owns"
    USERS ||--o{ PREDICTIONS : "makes"
    USERS ||--o{ USER_ACTIONS : "performs"
    STOCK_DATA ||--o{ PREDICTIONS : "has"
    STOCK_DATA ||--o{ HISTORICAL_PRICE_DATA : "contains"
    STOCK_DATA ||--o{ SENTIMENT_ANALYSIS : "associated_with"
    PREDICTIONS ||--o{ RESULTS : "generates"
    SENTIMENT_ANALYSIS ||--o{ RESULTS : "contributes_to"
    MODELS ||--o{ RESULTS : "uses"
    USERS ||--o{ MODELS : "configures"

    USERS {
        string user_id PK
        string username
        string email
        string password_hash
        string role
        datetime created_at
        datetime last_login
    }

    STOCK_DATA {
        string stock_id PK
        string symbol
        string company_name
        string exchange
        string sector
        string industry
        float market_cap
        datetime created_at
    }

    PREDICTIONS {
        string pred_id PK
        string stock_id FK
        string user_id FK
        string model_type
        float predicted_price
        float actual_price
        datetime prediction_date
        float accuracy
        float confidence
    }

    HISTORICAL_PRICE_DATA {
        string data_id PK
        string stock_id FK
        date date
        float open_price
        float high_price
        float low_price
        float close_price
        float volume
        float adjusted_close
    }

    SENTIMENT_ANALYSIS {
        string sent_id PK
        string stock_id FK
        string source
        float sentiment_score
        int positive_count
        int negative_count
        int neutral_count
        datetime analyzed_at
    }

    USER_ACTIONS {
        string action_id PK
        string user_id FK
        string action_type
        string action_details
        datetime timestamp
        string ip_address
        string user_agent
        boolean success
        string error_message
    }

    MODELS {
        string model_id PK
        string model_name
        string version
        string algorithm
        datetime training_date
        float accuracy_score
        string parameters
    }

    RESULTS {
        string result_id PK
        string pred_id FK
        string sent_id FK
        float arima_pred
        float lstm_pred
        float lr_pred
        string recommendation
        float confidence_score
        datetime created_at
    }
```

## Entity Descriptions

### Users
- Stores user account information
- Differentiates between admin and regular users
- Tracks login activity and user roles

### Stock Data
- Contains information about stock symbols
- Includes company details and market information
- Links to exchange and sector data

### Predictions
- Stores all prediction results
- Links to users and stock data
- Tracks model performance and accuracy

### Historical Price Data
- Contains actual stock price history
- Used for training models and validating predictions
- Time-series data with OHLCV values

### Sentiment Analysis
- Stores sentiment scores from social media
- Tracks source and analysis timestamps
- Links to specific stocks

### User Actions
- Logs all user interactions with the system
- Tracks successes and errors
- Used for analytics and debugging

### Models
- Contains information about ML models
- Tracks versions and performance metrics
- Stores model parameters

### Results
- Detailed prediction results
- Combines ML predictions with sentiment analysis
- Provides final recommendations