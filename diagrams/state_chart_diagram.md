# State Chart Diagram
## Stock Market Prediction Web App

```mermaid
stateDiagram-v2
    [*] --> Start
    
    Start --> AccessWebsite
    AccessWebsite --> ViewDashboard
    
    ViewDashboard --> EnterStockSymbol
    ViewDashboard --> ViewPredictionHistory
    ViewDashboard --> ViewSentimentAnalysis
    
    EnterStockSymbol --> ValidateSymbol
    ValidateSymbol --> ShowResults: Valid
    ValidateSymbol --> EnterStockSymbol: Invalid
    
    ViewPredictionHistory --> SelectTimeRange
    SelectTimeRange --> GenerateReport
    
    ViewSentimentAnalysis --> FilterBySource
    FilterBySource --> ShowDetails
    
    ShowResults --> GetInvestmentRecommendation
    GenerateReport --> GetInvestmentRecommendation
    ShowDetails --> GetInvestmentRecommendation
    
    GetInvestmentRecommendation --> ExportResults
    ExportResults --> Logout
    Logout --> End
    End --> [*]
    
    state "User Interaction States" as UserStates {
        [*] --> Start
        Start --> AccessWebsite
        AccessWebsite --> ViewDashboard
        ViewDashboard --> EnterStockSymbol
        ViewDashboard --> ViewPredictionHistory
        ViewDashboard --> ViewSentimentAnalysis
        
        EnterStockSymbol --> ValidateSymbol
        ValidateSymbol --> ShowResults: Valid
        ValidateSymbol --> EnterStockSymbol: Invalid
        
        ViewPredictionHistory --> SelectTimeRange
        SelectTimeRange --> GenerateReport
        
        ViewSentimentAnalysis --> FilterBySource
        FilterBySource --> ShowDetails
        
        ShowResults --> GetInvestmentRecommendation
        GenerateReport --> GetInvestmentRecommendation
        ShowDetails --> GetInvestmentRecommendation
        
        GetInvestmentRecommendation --> ExportResults
        ExportResults --> Logout
        Logout --> End
        End --> [*]
    }
    
    state "Prediction Processing States" as PredictionStates {
        [*] --> IdleState
        IdleState --> DataRetrieval
        DataRetrieval --> DataProcessing
        DataProcessing --> ModelProcessing
        
        state ModelProcessing {
            [*] --> ARIMAModel
            [*] --> LSTMModel
            [*] --> LinearRegModel
            
            ARIMAModel --> ARIMAResults
            LSTMModel --> LSTMResults
            LinearRegModel --> LRResults
            
            ARIMAResults --> CombineResults
            LSTMResults --> CombineResults
            LRResults --> CombineResults
        }
        
        CombineResults --> SentimentAnalysis
        SentimentAnalysis --> CombineAllResults
        CombineAllResults --> GenerateRecommendation
        GenerateRecommendation --> StoreResults
        StoreResults --> ReturnResults
        ReturnResults --> [*]
    }
    
    state "System Health States" as SystemStates {
        [*] --> SystemOnline
        SystemOnline --> HighLoad: Performance Degradation
        SystemOnline --> MaintenanceMode: Scheduled Updates
        SystemOnline --> ErrorState: System Issues
        
        HighLoad --> LoadBalancing
        LoadBalancing --> SystemOnline
        
        MaintenanceMode --> MaintenanceOperations
        MaintenanceOperations --> SystemRecovery
        SystemRecovery --> SystemOnline
        
        ErrorState --> ErrorHandling
        ErrorHandling --> SystemRecovery
    }
```

## State Descriptions

### User Interaction States
Represents the user journey through the application:
1. **Start**: Initial access point
2. **Access Website**: Login or registration process
3. **View Dashboard**: Main overview of available features
4. **Enter Stock Symbol**: Input for prediction request
5. **Validate Symbol**: System checks symbol validity
6. **Show Results**: Display prediction outcomes
7. **Get Investment Recommendation**: Receive actionable advice
8. **Export Results**: Save data in various formats
9. **Logout**: End user session
10. **End**: Final state

### Prediction Processing States
Represents the internal processing flow:
1. **Idle State**: Waiting for user requests
2. **Data Retrieval**: Fetching stock information from APIs
3. **Data Processing**: Cleaning and validating data
4. **Model Processing**: Running predictions through all three ML models
5. **Combine Results**: Merging predictions with weighted averages
6. **Sentiment Analysis**: Processing social media sentiment
7. **Generate Recommendation**: Creating investment advice
8. **Store Results**: Saving to database
9. **Return Results**: Sending to user interface

### System Health States
Represents system operational states:
1. **System Online**: Normal operations
2. **High Load**: Performance degradation handling
3. **Maintenance Mode**: Scheduled updates and repairs
4. **Error State**: System issues and failures
5. **Load Balancing**: Distributing requests during high load
6. **Maintenance Operations**: Database backup and restore
7. **Error Handling**: Logging and recovery processes
8. **System Recovery**: Return to normal operations