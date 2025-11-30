# Data Flow Diagram - Level 0 (Context Diagram)
## Stock Market Prediction Web App

```mermaid
graph LR
    subgraph "External Entities"
        USER[User]
        EXTERNAL_APIS[External APIs<br/>Yahoo, Alpha Vantage]
        SOCIAL_MEDIA[Social Media<br/>Twitter]
        DATABASE[Database<br/>MySQL]
    end

    subgraph "Main Process"
        SYSTEM[Stock Prediction System]
    end

    USER -- "Stock Request" --> SYSTEM
    SYSTEM -- "Predictions" --> USER
    EXTERNAL_APIS -- "Stock Data" --> SYSTEM
    SOCIAL_MEDIA -- "Sentiment Data" --> SYSTEM
    DATABASE -- "Store/Retrieve Data" --> SYSTEM
    SYSTEM -- "Store/Retrieve Data" --> DATABASE
```

## Data Flows

### External Entities:
1. **User**: 
   - Provides stock symbol requests
   - Receives prediction results and recommendations

2. **External APIs**:
   - Provides real-time stock market data
   - Provides historical price information
   - Provides company financial data

3. **Social Media**:
   - Provides tweets for sentiment analysis
   - Provides news articles
   - Provides market commentary

4. **Database**:
   - Stores user accounts and preferences
   - Stores prediction history
   - Stores model performance metrics
   - Stores processed data

### Main Process:
**Stock Prediction System** - The core system that:
- Receives stock symbol requests from users
- Retrieves data from external sources
- Processes data through ML models
- Analyzes sentiment from social media
- Generates predictions and recommendations
- Stores results in database
- Returns predictions to users