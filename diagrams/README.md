# Stock Portfolio Platform - Architecture Documentation

## Overview

This directory contains comprehensive architectural diagrams for the Stock Portfolio Platform, a Flask-based web application for stock trading, portfolio management, and price prediction using machine learning.

## Diagram Index

### System Architecture

#### 📐 [Architecture Diagram](architecture.md)
Complete system architecture showing all 60 source files, their dependencies, and external libraries. Best starting point for understanding the overall system structure.

**Key Insights:**
- Layered architecture (routes → services → models)
- Clear separation of concerns
- External dependencies (Flask, SQLAlchemy, yfinance, pandas, etc.)

#### 📦 [Package Diagram](package.md)
High-level package organization showing the main modules: forms, jobs, models, routes, services, and utils.

### Database Layer

#### 🗄️ [Database ER Diagram](database_er_diagram.md)
Entity-Relationship diagram showing all 13 database tables, their relationships, and constraints.

**Tables:**
- User, Company, Wallet, Holding
- Order, Transaction, Dividend, Broker
- Notification, PriceHistory, SentimentCache
- JobLog, AuditLog

**Key Relationships:**
- User → Wallet (1:1)
- User → Holdings (1:N)
- Company → PriceHistory (1:N)
- Order → Transaction (1:1)

### Application Layer

#### 🏗️ [Class Diagram - Models](class_diagram_models.md)
Detailed view of all database models with their attributes, methods, and relationships.

**Highlights:**
- Active Record pattern
- Domain logic in models
- Calculated fields (unrealized gains, portfolio value)
- Validation rules

#### ⚙️ [Class Diagram - Services](class_diagram_services.md)
Business logic layer showing 11 service classes and their responsibilities.

**Core Services:**
- **AuthService**: User authentication and registration
- **PortfolioService**: Portfolio aggregation and analytics
- **TransactionEngine**: Order execution and trade processing
- **PredictionService**: ML-based price predictions
- **StockRepository**: Stock data management

### User Flows

#### 🔐 [Sequence: User Registration](sequence_user_registration.md)
Complete registration flow from form submission to auto-login.

**Steps:**
1. Form validation (CSRF, email, password)
2. User creation with bcrypt password hashing
3. Automatic wallet initialization
4. Audit logging
5. Welcome email (async)
6. Session creation and redirect

#### 💰 [Sequence: Buy Order](sequence_buy_order.md)
Stock purchase workflow with transaction management.

**Steps:**
1. Form validation
2. Price fetching and cost calculation
3. Wallet balance check
4. Atomic transaction (wallet deduction + holding update)
5. Notification delivery

#### 📈 [Sequence: Price Prediction](sequence_prediction.md)
ML prediction pipeline with multiple models.

**Steps:**
1. Historical data fetching
2. Parallel model execution (ARIMA, LSTM, Linear Regression)
3. Sentiment analysis with caching
4. Prediction combination
5. Chart generation

## Technology Stack

### Backend
- **Flask 3.1.0** - Web framework
- **SQLAlchemy** - ORM
- **Flask-Login** - Authentication
- **Flask-WTF** - Form handling with CSRF
- **APScheduler** - Background jobs

### Data & ML
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **scikit-learn** - Machine learning
- **statsmodels** - ARIMA forecasting
- **yfinance** - Stock data API
- **TextBlob** - Sentiment analysis

### Frontend
- **Bootstrap** - CSS framework
- **jQuery** - JavaScript library
- **Jinja2** - Template engine

## Architecture Patterns

### Layered Architecture
```
Routes (Presentation)
    ↓
Services (Business Logic)
    ↓
Models (Data Access)
    ↓
Database
```

### Design Patterns
- **Active Record**: Models contain both data and behavior
- **Service Layer**: Business logic separated from routes
- **Repository Pattern**: StockRepository abstracts data access
- **Transaction Script**: TransactionEngine for complex operations
- **Observer Pattern**: Notification system for events

### Security Measures
- **CSRF Protection**: All forms protected
- **Password Hashing**: Bcrypt with automatic salting
- **SQL Injection Prevention**: Parameterized queries via ORM
- **XSS Protection**: Output sanitization in templates
- **Session Security**: Secure, HttpOnly cookies
- **Audit Logging**: All critical actions logged

## Key Features

### Portfolio Management
- Real-time portfolio tracking
- Holdings with P&L calculations
- Sector allocation analysis
- Performance metrics

### Trading
- Buy/sell order execution
- Commission tracking
- Transaction history
- Atomic operations with rollback

### Predictions
- 3 ML models (ARIMA, LSTM, Linear Regression)
- Sentiment analysis from Twitter
- 7-day price forecasts
- Confidence intervals

### Administration
- User management
- Company/broker management
- Dividend processing
- System monitoring
- Audit trail

## Data Flow Examples

### Buy Order Flow
```
User → OrderRoute → TransactionEngine → [Wallet, Holding, Transaction] → Database
                                      → NotificationService → User
```

### Prediction Flow
```
User → DashboardRoute → PredictionService → [ARIMA, LSTM, Linear] → Combined Prediction
                                         → SentimentEngine → Twitter API
                                         → StockRepository → yfinance API
```

### Registration Flow
```
User → AuthRoute → AuthService → [User, Wallet, AuditLog] → Database
                              → EmailService (async)
                              → Session → Dashboard
```

## Viewing the Diagrams

### In VS Code
1. Install "Markdown Preview Mermaid Support" extension
2. Open any `.md` file
3. Press `Ctrl+Shift+V` (or `Cmd+Shift+V` on Mac)

### In Browser
1. Visit https://mermaid.live
2. Copy the Mermaid code from any diagram
3. Paste into the editor

### On GitHub/GitLab
Diagrams render automatically when viewing `.md` files

## Diagram Conventions

### Colors (in ER Diagram)
- **Primary Keys**: Bold
- **Foreign Keys**: Italic
- **Required Fields**: No special marking
- **Optional Fields**: Noted in description

### Relationships
- `||--o{` : One-to-Many
- `||--||` : One-to-One
- `}o--o{` : Many-to-Many

### Sequence Diagrams
- **Solid Arrow** (→): Synchronous call
- **Dashed Arrow** (--→): Return value
- **Note**: Additional information
- **Alt/Else**: Conditional logic
- **Par**: Parallel execution

## Contributing

When adding new features:
1. Update relevant diagrams
2. Add sequence diagrams for complex flows
3. Document new services in class diagrams
4. Update ER diagram for schema changes

## Questions?

For questions about the architecture:
- Review the relevant diagram
- Check the source code in `app/`
- Refer to the design documents in `.kiro/specs/`
