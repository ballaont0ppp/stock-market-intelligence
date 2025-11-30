# Diagram Generation Summary

Generated on: 2025-11-19

## Successfully Generated Diagrams

### 1. Architecture Diagram (`architecture.md`)
**Status:** ✓ Complete

Shows the complete system architecture with all 60 source files analyzed, including:
- All modules (models, routes, services, forms, jobs, utils)
- Internal dependencies between components
- External library dependencies (Flask, SQLAlchemy, pandas, etc.)
- Clear visualization of the layered architecture

### 2. Package Diagram (`package.md`)
**Status:** ✓ Complete

Shows the high-level package structure:
- `app` - Main application package
- `app/forms` - Form definitions
- `app/jobs` - Background jobs
- `app/models` - Database models
- `app/routes` - HTTP route handlers
- `app/services` - Business logic
- `app/utils` - Utility functions

### 3. Component Diagram (`component.md`)
**Status:** ✓ Generated (minimal)

Basic component structure identified from the codebase.

### 4. Database ER Diagram (`database_er_diagram.md`)
**Status:** ✓ Complete (Manual)

Comprehensive entity-relationship diagram showing:
- All 13 database models (User, Company, Wallet, Holding, Order, Transaction, Dividend, Broker, Notification, PriceHistory, SentimentCache, JobLog, AuditLog)
- Relationships and cardinalities
- Primary and foreign keys
- Column types and constraints
- Business rules and data flow

### 5. Class Diagram - Models (`class_diagram_models.md`)
**Status:** ✓ Complete (Manual)

Detailed class diagram of the data layer:
- All model classes with attributes and methods
- Inheritance from BaseModel
- Relationships between models
- Domain logic and calculated fields
- Validation rules

### 6. Class Diagram - Services (`class_diagram_services.md`)
**Status:** ✓ Complete (Manual)

Business logic layer visualization:
- 11 service classes (AuthService, PortfolioService, TransactionEngine, PredictionService, SentimentEngine, StockRepository, NotificationService, ReportService, DividendManager, AdminService, AuditService)
- Service responsibilities and methods
- Dependencies between services
- External API integrations

### 7. Sequence Diagram - Buy Order (`sequence_buy_order.md`)
**Status:** ✓ Complete (Manual)

Step-by-step flow for stock purchase:
- User interaction through browser
- Form validation (client and server)
- Transaction engine processing
- Wallet and holding updates
- Notification delivery
- Error handling scenarios

### 8. Sequence Diagram - Prediction (`sequence_prediction.md`)
**Status:** ✓ Complete (Manual)

ML prediction workflow:
- Historical data fetching
- Parallel execution of 3 ML models (ARIMA, LSTM, Linear Regression)
- Sentiment analysis with caching
- Prediction combination and confidence intervals
- Chart generation

### 9. Sequence Diagram - Registration (`sequence_user_registration.md`)
**Status:** ✓ Complete (Manual)

User registration process:
- Form validation (CSRF, email, password strength)
- User creation with password hashing
- Automatic wallet initialization
- Audit logging
- Welcome email (async)
- Auto-login and session creation

## Usage

To view the diagrams:
1. Open the `.md` files in any Markdown viewer that supports Mermaid
2. Use GitHub, GitLab, or VS Code with Mermaid extension
3. Copy the Mermaid code blocks to https://mermaid.live for interactive viewing

## Configuration

The diagrams were generated using `config.yaml` with the following settings:
- Source: `app/` directory
- Output: `diagrams/` directory
- Excluded: tests, migrations, templates, static files, virtual environments

## Next Steps

To generate additional diagram types:
1. Fix the remaining type issues in the generators
2. Re-run: `python -m diagram_generator.cli generate --config config.yaml --source app`
3. Or generate specific types only by updating the `enabled_diagrams` in `config.yaml`
