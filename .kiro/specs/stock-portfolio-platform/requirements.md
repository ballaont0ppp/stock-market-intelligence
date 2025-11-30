# Requirements Document

## Introduction

This document specifies the requirements for transforming the Stock Market Prediction application into a comprehensive stock portfolio management platform. The system will integrate user authentication, database persistence, virtual portfolio management, transaction tracking, dividend management, broker administration, and enhanced sentiment analysis capabilities. This builds upon the existing ML prediction models (LSTM, Linear Regression, ARIMA) and adds the business logic layer needed for a production-ready stock trading simulation platform.

## Glossary

- **Portfolio System**: The component managing user stock holdings, purchases, sales, and valuations
- **Virtual Wallet**: A simulated cash account for each user to fund stock purchases
- **Transaction Engine**: The component processing buy/sell orders and recording transaction history (also called Trade Engine)
- **Order**: A user request to buy or sell a specific quantity of stock at market price
- **Holdings**: The collection of stocks currently owned by a user with quantities and purchase details
- **Dividend Manager**: The component tracking and distributing dividend payments to portfolio holdings
- **Broker Dashboard**: Administrative interface for managing users, monitoring transactions, and system oversight
- **Broker**: An administrative entity that can manage companies, users, and system configuration
- **Sentiment Engine**: Enhanced sentiment analysis system integrating Twitter API via tweepy with proper authentication
- **Stock Repository**: Database layer storing company information, historical prices, and market data
- **Company**: A publicly traded entity with stock symbol, name, sector, and associated price history
- **Price History**: Time-series data of stock prices (open, high, low, close, volume) stored in database
- **Background Job**: Scheduled task that runs periodically to refresh stock prices from yfinance to database
- **Authentication System**: User identity verification and session management (from existing spec)
- **Database Layer**: MySQL persistence layer using SQLAlchemy ORM (from existing spec)
- **Prediction Engine**: Existing ML models (LSTM, ARIMA, Linear Regression) for price forecasting
- **Regular User**: Standard user with portfolio and trading capabilities
- **Admin User**: User with elevated privileges for broker dashboard and system management
- **Transaction Report**: Detailed record of user trading activity over a specified period
- **Billing Report**: Summary of fees, charges, and account activity for a user (also called Receipt)
- **Static Dataset Mode**: Configuration option to use local CSV files instead of live yfinance API calls
- **Navigation Menu**: UI component providing links to Dashboard, Portfolio, Orders, Reports, and Admin sections

## Requirements

### Requirement 1: Virtual Wallet Management

**User Story:** As a registered user, I want to manage a virtual wallet with simulated funds, so that I can practice stock trading without real financial risk

#### Acceptance Criteria

1. WHEN a new user account is created, THE Portfolio System SHALL automatically create a Wallets record with: user_id (foreign key), balance = 100000.00, currency = 'USD', total_deposited = 100000.00, total_withdrawn = 0.00, created_at = current_timestamp

2. THE Portfolio System SHALL provide a wallet service class with methods: get_balance(user_id), debit(user_id, amount, description), credit(user_id, amount, description), get_transaction_history(user_id, limit, offset)

3. WHEN a user views their dashboard, THE Portfolio System SHALL display: current wallet balance (formatted as $XXX,XXX.XX), total portfolio value (sum of all holdings at current prices), combined net worth (wallet + portfolio), and percentage allocation (wallet vs portfolio)

4. WHEN a user deposits simulated funds via the wallet page, THE Portfolio System SHALL: (a) validate amount is positive number with max 2 decimals, (b) validate amount does not exceed $1,000,000 per deposit, (c) add amount to Wallets.balance, (d) update Wallets.total_deposited, (e) create Transaction record with type 'DEPOSIT', (f) display success message "Deposited $X,XXX.XX to your wallet"

5. WHEN a user withdraws simulated funds via the wallet page, THE Portfolio System SHALL: (a) validate amount is positive, (b) validate amount <= current balance, (c) deduct amount from Wallets.balance, (d) update Wallets.total_withdrawn, (e) create Transaction record with type 'WITHDRAWAL', (f) display success message "Withdrew $X,XXX.XX from your wallet"

6. THE Portfolio System SHALL prevent wallet balance from becoming negative by: (a) using database CHECK constraint (balance >= 0), (b) validating sufficient funds before any debit operation, (c) using row-level locking during transactions

7. WHEN any wallet operation fails, THE Portfolio System SHALL rollback all changes, log the error with user_id and operation details, and display user-friendly error message

8. THE Portfolio System SHALL display wallet transaction history on the wallet page with columns: date, type (DEPOSIT/WITHDRAWAL/BUY/SELL/DIVIDEND/FEE), description, amount (positive for credits, negative for debits), balance after transaction, with pagination (20 per page)

### Requirement 2: Stock Purchase Simulation (Trade Engine - Buy Orders)

**User Story:** As a user, I want to buy stocks using my virtual wallet funds, so that I can build a simulated investment portfolio

#### Acceptance Criteria

1. WHEN a user submits a buy order with stock symbol and quantity, THE Transaction Engine SHALL validate: (a) stock symbol exists in Companies table or can be fetched from yfinance, (b) quantity is a positive integer greater than 0, (c) quantity does not exceed 1,000,000 shares per order

2. WHEN a buy order is submitted, THE Transaction Engine SHALL create an Order record with status 'PENDING', fetch the current market price from PriceHistory table (latest date) or yfinance if not cached, and calculate: total_cost = (price_per_share * quantity) + commission_fee where commission_fee = (price_per_share * quantity * 0.001)

3. WHEN validating a buy order, THE Transaction Engine SHALL lock the user's Wallet record using database row-level locking (SELECT FOR UPDATE) to prevent race conditions

4. IF the user's wallet balance is insufficient (balance < total_cost), THEN THE Transaction Engine SHALL update Order status to 'FAILED' with failure_reason "Insufficient funds", rollback the transaction, and display error message "Insufficient funds for this purchase. Required: $X,XXX.XX, Available: $X,XXX.XX"

5. WHEN a buy order is validated and approved, THE Transaction Engine SHALL execute the following atomic transaction: (a) deduct total_cost from Wallets.balance, (b) update Order status to 'COMPLETED' with executed_at timestamp, (c) INSERT or UPDATE Holdings record (if user already owns the stock, recalculate average_purchase_price = ((existing_quantity * average_purchase_price) + (new_quantity * price_per_share)) / (existing_quantity + new_quantity)), (d) create Transaction record with type 'BUY', (e) create Transaction record with type 'FEE' for commission, (f) commit all changes or rollback on any error

6. WHEN a buy order fails due to system error, THE Transaction Engine SHALL update Order status to 'FAILED', log the full error stack trace, rollback all database changes, and display user-friendly message "Order failed due to system error. Please try again."

7. WHEN a buy order is completed, THE Transaction Engine SHALL display confirmation message with details: "Order completed successfully! Purchased X shares of SYMBOL at $XX.XX per share. Total cost: $X,XXX.XX (including $X.XX commission)"

8. THE Transaction Engine SHALL complete buy order processing within 5 seconds under normal conditions (excluding external API delays)

### Requirement 3: Stock Sale Simulation (Trade Engine - Sell Orders)

**User Story:** As a user, I want to sell stocks from my portfolio, so that I can realize gains or cut losses in my simulated trading

#### Acceptance Criteria

1. WHEN a user submits a sell order with stock symbol and quantity, THE Transaction Engine SHALL validate: (a) user has a Holdings record for that company_id, (b) Holdings.quantity >= requested quantity, (c) quantity is a positive integer greater than 0

2. IF the user does not own enough shares (Holdings.quantity < requested quantity), THEN THE Transaction Engine SHALL reject the order, create Order record with status 'FAILED' and failure_reason "Insufficient shares", and display error message "Insufficient shares to sell. You own X shares of SYMBOL, but attempted to sell Y shares"

3. WHEN a sell order is submitted, THE Transaction Engine SHALL create an Order record with status 'PENDING', fetch current market price from PriceHistory or yfinance, and calculate: gross_proceeds = price_per_share * quantity, commission_fee = gross_proceeds * 0.001, net_proceeds = gross_proceeds - commission_fee

4. WHEN validating a sell order, THE Transaction Engine SHALL lock both the user's Wallet and Holdings records using database row-level locking (SELECT FOR UPDATE) to prevent race conditions

5. WHEN a sell order is validated and approved, THE Transaction Engine SHALL execute the following atomic transaction: (a) add net_proceeds to Wallets.balance, (b) update Order status to 'COMPLETED' with executed_at timestamp, (c) reduce Holdings.quantity by sold quantity, (d) IF Holdings.quantity reaches 0, DELETE the Holdings record, (e) create Transaction record with type 'SELL' for gross_proceeds, (f) create Transaction record with type 'FEE' for commission (negative amount), (g) commit all changes or rollback on any error

6. WHEN a sell order is completed, THE Transaction Engine SHALL calculate realized gain/loss as: realized_gain_loss = (price_per_share - Holdings.average_purchase_price) * quantity, and store this value in the Order record

7. WHEN a sell order is completed, THE Transaction Engine SHALL display confirmation message with details: "Order completed successfully! Sold X shares of SYMBOL at $XX.XX per share. Total proceeds: $X,XXX.XX (after $X.XX commission). Realized gain/loss: $XXX.XX (XX.X%)"

8. THE Transaction Engine SHALL complete sell order processing within 5 seconds under normal conditions (excluding external API delays)

### Requirement 4: Portfolio Holdings Management

**User Story:** As a user, I want to view my current stock holdings with real-time valuations, so that I can track my investment performance

#### Acceptance Criteria

1. WHEN a user accesses the portfolio page, THE Portfolio System SHALL display all current holdings with columns: stock symbol, company name, quantity, average purchase price, current market price, total value, unrealized gain/loss, and percentage change

2. THE Portfolio System SHALL fetch current market prices for all holdings using yfinance when the portfolio page loads

3. THE Portfolio System SHALL calculate unrealized gain/loss as: (current_price - average_purchase_price) * quantity for each holding

4. THE Portfolio System SHALL display portfolio summary metrics: total invested amount, current portfolio value, total unrealized gain/loss, and overall return percentage

5. WHEN a user has no holdings, THE Portfolio System SHALL display a message "Your portfolio is empty. Start investing to build your portfolio."

### Requirement 5: Transaction History and Reporting

**User Story:** As a user, I want to view my complete transaction history with filtering options, so that I can review my trading activity and performance

#### Acceptance Criteria

1. WHEN a user accesses the transaction history page, THE Transaction Engine SHALL display all transactions in reverse chronological order with columns: date, stock symbol, type (BUY/SELL), quantity, price, commission, total amount, and status

2. THE Transaction Engine SHALL provide filter options for: date range, transaction type (BUY/SELL/ALL), stock symbol, and status

3. WHEN a user applies filters, THE Transaction Engine SHALL update the displayed transactions to match the filter criteria within 2 seconds

4. THE Transaction Engine SHALL provide an export function to download transaction history as CSV format with all transaction details

5. THE Transaction Engine SHALL display summary statistics for the filtered period: total transactions, total buy amount, total sell amount, total commissions paid, and net profit/loss

### Requirement 6: Dividend Tracking and Distribution

**User Story:** As a user, I want to automatically receive dividend payments for stocks I own, so that my portfolio reflects realistic investment returns

#### Acceptance Criteria

1. THE Dividend Manager SHALL run a daily scheduled job at market close (4:00 PM EST) to check for dividend announcements for all stocks in user portfolios

2. WHEN a dividend payment date occurs for a stock, THE Dividend Manager SHALL calculate the dividend amount as: dividend_per_share * quantity_owned for each user holding that stock

3. WHEN dividend payments are calculated, THE Dividend Manager SHALL add the dividend amount to the user's wallet balance and create a transaction record with type 'DIVIDEND'

4. THE Dividend Manager SHALL store dividend records with fields: dividend_id, stock_id, dividend_per_share, payment_date, record_date, ex_dividend_date, announcement_date

5. WHEN a user views their transaction history, THE Dividend Manager SHALL display dividend payments with the stock symbol, payment date, shares owned, dividend per share, and total amount received

### Requirement 7: Database Models and Schema

**User Story:** As a developer, I want comprehensive database models for all entities, so that the system can persist and manage all application data

#### Acceptance Criteria

1. THE Database Layer SHALL define a Users table with fields: user_id (primary key, auto-increment), email (unique, varchar 255), password_hash (varchar 255), full_name (varchar 255), risk_tolerance (enum: conservative/moderate/aggressive), investment_goals (text), preferred_sectors (JSON array), notification_preferences (JSON object), is_admin (boolean, default false), created_at (timestamp), last_login (timestamp), account_status (enum: active/suspended, default active)

2. THE Database Layer SHALL define a Companies table with fields: company_id (primary key, auto-increment), symbol (unique, varchar 10), company_name (varchar 255), sector (varchar 100), industry (varchar 100), market_cap (bigint), description (text), website (varchar 255), ceo (varchar 255), employees (int), founded_year (int), headquarters (varchar 255), last_updated (timestamp), is_active (boolean, default true)

3. THE Database Layer SHALL define a PriceHistory table with fields: price_id (primary key, auto-increment), company_id (foreign key to Companies), date (date), open (decimal 10,2), high (decimal 10,2), low (decimal 10,2), close (decimal 10,2), adjusted_close (decimal 10,2), volume (bigint), created_at (timestamp), with composite unique index on (company_id, date)

4. THE Database Layer SHALL define a Wallets table with fields: wallet_id (primary key, auto-increment), user_id (foreign key to Users, unique), balance (decimal 15,2, default 100000.00), currency (varchar 3, default 'USD'), total_deposited (decimal 15,2, default 100000.00), total_withdrawn (decimal 15,2, default 0.00), created_at (timestamp), last_updated (timestamp)

5. THE Database Layer SHALL define a Holdings table with fields: holding_id (primary key, auto-increment), user_id (foreign key to Users), company_id (foreign key to Companies), quantity (int), average_purchase_price (decimal 10,2), total_invested (decimal 15,2), first_purchase_date (timestamp), last_updated (timestamp), with composite unique index on (user_id, company_id)

6. THE Database Layer SHALL define an Orders table with fields: order_id (primary key, auto-increment), user_id (foreign key to Users), company_id (foreign key to Companies), order_type (enum: BUY/SELL), quantity (int), price_per_share (decimal 10,2), commission_fee (decimal 10,2), total_amount (decimal 15,2), order_status (enum: PENDING/COMPLETED/FAILED/CANCELLED), created_at (timestamp), executed_at (timestamp), failure_reason (text)

7. THE Database Layer SHALL define a Transactions table with fields: transaction_id (primary key, auto-increment), user_id (foreign key to Users), transaction_type (enum: BUY/SELL/DIVIDEND/DEPOSIT/WITHDRAWAL/FEE), order_id (foreign key to Orders, nullable), company_id (foreign key to Companies, nullable), amount (decimal 15,2), balance_before (decimal 15,2), balance_after (decimal 15,2), description (text), created_at (timestamp), with index on (user_id, created_at)

8. THE Database Layer SHALL define a Dividends table with fields: dividend_id (primary key, auto-increment), company_id (foreign key to Companies), dividend_per_share (decimal 10,4), payment_date (date), record_date (date), ex_dividend_date (date), announcement_date (date), dividend_type (enum: REGULAR/SPECIAL), created_at (timestamp), with index on (company_id, payment_date)

9. THE Database Layer SHALL define a DividendPayments table with fields: payment_id (primary key, auto-increment), dividend_id (foreign key to Dividends), user_id (foreign key to Users), holding_id (foreign key to Holdings), shares_owned (int), amount_paid (decimal 15,2), transaction_id (foreign key to Transactions), paid_at (timestamp)

10. THE Database Layer SHALL define a Brokers table with fields: broker_id (primary key, auto-increment), user_id (foreign key to Users, unique), broker_name (varchar 255), license_number (varchar 100), phone (varchar 20), email (varchar 255), assigned_users_count (int, default 0), created_at (timestamp), is_active (boolean, default true)

11. THE Database Layer SHALL define a Notifications table with fields: notification_id (primary key, auto-increment), user_id (foreign key to Users), notification_type (enum: TRANSACTION/DIVIDEND/PRICE_ALERT/SYSTEM), title (varchar 255), message (text), is_read (boolean, default false), created_at (timestamp), read_at (timestamp), with index on (user_id, is_read, created_at)

12. THE Database Layer SHALL define a SentimentCache table with fields: cache_id (primary key, auto-increment), company_id (foreign key to Companies), source (enum: TWITTER/NEWS/REDDIT), polarity_score (decimal 3,2), positive_count (int), negative_count (int), neutral_count (int), sample_texts (JSON array), fetched_at (timestamp), expires_at (timestamp), with index on (company_id, source, expires_at)

13. THE Database Layer SHALL enforce foreign key constraints with ON DELETE CASCADE for dependent records and ON DELETE RESTRICT for referenced records to maintain referential integrity

14. THE Database Layer SHALL create indexes on frequently queried columns: Users.email, Companies.symbol, Orders.user_id, Orders.created_at, Transactions.user_id, Transactions.created_at, Holdings.user_id, PriceHistory.company_id, PriceHistory.date

15. THE Database Layer SHALL use InnoDB storage engine for all tables to support transactions and foreign key constraints

### Requirement 8: Broker Administration Dashboard with CRUD Operations

**User Story:** As an administrator, I want to access a comprehensive broker dashboard with full CRUD capabilities, so that I can monitor platform activity and manage all system entities

#### Acceptance Criteria

1. WHEN an admin user logs in, THE Broker Dashboard SHALL display key metrics on the overview page: total registered users, active users (traded in last 30 days), total transactions today, total transaction volume (dollar amount), total portfolio value across all users, top 5 most traded stocks, and system health status (green/yellow/red)

2. THE Broker Dashboard SHALL provide a "User Management" section with table displaying all users: user_id, email, full_name, registration date, wallet balance, portfolio value, total transactions, last login, account status, with actions: View Details, Edit Profile, Suspend/Activate, Delete Account

3. WHEN an admin clicks "View Details" for a user, THE Broker Dashboard SHALL display: complete profile information, transaction history (last 50), current holdings with values, performance metrics (total return, win rate), and activity timeline

4. WHEN an admin clicks "Edit Profile" for a user, THE Broker Dashboard SHALL display a form to update: full_name, email, risk_tolerance, investment_goals, preferred_sectors, notification_preferences, and allow manual wallet balance adjustment with reason field

5. WHEN an admin suspends a user account, THE Broker Dashboard SHALL update Users.account_status to 'suspended', log the action with admin_id and reason, and prevent that user from logging in with message "Your account has been suspended. Please contact support."

6. THE Broker Dashboard SHALL provide a "Company Management" section with CRUD operations: (a) List all companies with columns: symbol, company_name, sector, market_cap, last_updated, is_active, actions, (b) Create new company with form fields: symbol (required, unique), company_name, sector, industry, description, website, (c) Edit existing company details, (d) Deactivate company (soft delete by setting is_active=false), (e) Bulk import companies from CSV file

7. WHEN an admin creates a new company, THE Broker Dashboard SHALL validate: symbol is 1-10 uppercase characters, symbol is unique, company_name is not empty, and automatically fetch additional company details from yfinance if available

8. THE Broker Dashboard SHALL provide a "Broker Management" section with CRUD operations: (a) List all brokers with columns: broker_name, license_number, email, assigned_users_count, is_active, actions, (b) Create new broker linked to an admin user_id, (c) Edit broker details, (d) Deactivate broker, (e) Assign/unassign users to brokers

9. THE Broker Dashboard SHALL provide a "Transaction Monitoring" section displaying recent transactions across all users in real-time (auto-refresh every 30 seconds) with columns: transaction_id, timestamp, user_email, type, company_symbol, amount, status, with filters: date range, transaction type, user, company, status

10. THE Broker Dashboard SHALL provide a "Dividend Management" section with CRUD operations: (a) List all dividends with columns: company_symbol, dividend_per_share, payment_date, record_date, announcement_date, actions, (b) Create new dividend announcement, (c) Edit upcoming dividend details, (d) Delete dividend (only if payment_date is in future), (e) View dividend payment history showing which users received payments

11. WHEN an admin creates a new dividend, THE Broker Dashboard SHALL validate: company_id exists, dividend_per_share > 0, payment_date > record_date > ex_dividend_date, and automatically schedule the dividend payment job for payment_date

12. THE Broker Dashboard SHALL provide an "Audit Log" section displaying all admin actions with columns: timestamp, admin_email, action_type, entity_type, entity_id, changes_made (JSON), ip_address, with search and filter capabilities

13. THE Broker Dashboard SHALL restrict all admin routes with @admin_required decorator that checks Users.is_admin=true, and return 403 Forbidden with message "Access denied. Admin privileges required." for non-admin users

### Requirement 9: System Monitoring Dashboard

**User Story:** As an administrator, I want to monitor system performance and API usage, so that I can ensure platform reliability and optimize resource usage

#### Acceptance Criteria

1. THE Monitoring Dashboard SHALL display API usage statistics: total yfinance API calls today, average response time, failed requests, and rate limit status

2. THE Monitoring Dashboard SHALL track and display database performance metrics: query count, average query time, slow queries (>1 second), and connection pool status

3. THE Monitoring Dashboard SHALL show prediction model performance: total predictions today, average processing time per model (LSTM/ARIMA/LR), and error rates

4. THE Monitoring Dashboard SHALL provide system health indicators with color-coded status (green/yellow/red) for: database connectivity, API availability, model service status, and overall system health

5. WHEN any system health indicator turns red, THE Monitoring Dashboard SHALL log an alert with timestamp, component name, and error details

### Requirement 10: Enhanced Sentiment Analysis with Twitter API Integration

**User Story:** As a user, I want to see sentiment analysis from Twitter and other sources, so that I can make more informed trading decisions based on market sentiment

#### Acceptance Criteria

1. THE Sentiment Engine SHALL integrate with Twitter API v2 using tweepy library with authentication credentials stored in environment variables: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET

2. WHEN a user requests stock predictions for a symbol, THE Sentiment Engine SHALL first check SentimentCache table for cached results where company_id matches, source='TWITTER', and expires_at > current_time

3. IF cached sentiment data exists and is not expired, THEN THE Sentiment Engine SHALL return cached results without making API calls

4. IF cached sentiment data does not exist or is expired, THEN THE Sentiment Engine SHALL: (a) fetch company name from Companies table, (b) search Twitter for tweets containing stock symbol OR company name (first 12 characters) using tweepy.Cursor with parameters: q=search_term, tweet_mode='extended', lang='en', exclude_replies=True, count=100, (c) process and analyze tweets, (d) cache results in SentimentCache with expires_at = current_time + 1 hour

5. WHEN processing tweets, THE Sentiment Engine SHALL clean each tweet text by: (a) using preprocessor library to remove URLs, mentions, hashtags, (b) replacing '&amp;' with '&', (c) removing colons and emojis, (d) encoding to ASCII to remove non-English characters

6. WHEN analyzing cleaned tweets, THE Sentiment Engine SHALL use TextBlob to calculate polarity for each tweet, classify as: positive (polarity > 0.05), negative (polarity < -0.05), neutral (-0.05 <= polarity <= 0.05), and calculate global_polarity = sum(all_polarities) / tweet_count

7. THE Sentiment Engine SHALL store sentiment results in SentimentCache with: polarity_score = global_polarity, positive_count, negative_count, neutral_count, sample_texts = JSON array of up to 10 representative tweets (5 positive, 5 negative)

8. THE Sentiment Engine SHALL display sentiment visualization as a pie chart showing distribution of positive/negative/neutral tweets, saved as static/SA_{symbol}.png

9. THE Sentiment Engine SHALL display sentiment summary with: overall polarity label (Overall Positive if global_polarity > 0, Overall Negative if <= 0), polarity score (rounded to 2 decimals), tweet counts (positive/negative/neutral), and list of up to 10 sample tweets

10. IF Twitter API authentication fails (invalid credentials), THE Sentiment Engine SHALL log error "Twitter API authentication failed. Check credentials in environment variables.", set polarity to 0, and display message "Sentiment analysis unavailable. Twitter API credentials not configured."

11. IF Twitter API rate limit is exceeded, THE Sentiment Engine SHALL log error "Twitter API rate limit exceeded.", use cached data if available (even if expired), or set polarity to 0 and display message "Sentiment analysis temporarily unavailable due to API rate limits. Please try again later."

12. THE Sentiment Engine SHALL provide configuration in config.py for: SENTIMENT_ENABLED (boolean, default True), SENTIMENT_CACHE_DURATION (int seconds, default 3600), SENTIMENT_TWEET_COUNT (int, default 100), SENTIMENT_SOURCES (list, default ['TWITTER'])

13. WHEN SENTIMENT_ENABLED=False in config, THE Sentiment Engine SHALL skip all sentiment analysis, set polarity to 0, and display message "Sentiment analysis is currently disabled."

### Requirement 11: Billing and Fee Management

**User Story:** As a user, I want to view a detailed breakdown of all fees and charges, so that I understand the costs of my trading activity

#### Acceptance Criteria

1. THE Transaction Engine SHALL calculate and store commission fees for each transaction: 0.1% of transaction value for both buy and sell orders

2. WHEN a user accesses the billing page, THE Transaction Engine SHALL display a summary of fees: total commissions paid (all-time), commissions this month, commissions this year, and average commission per trade

3. THE Transaction Engine SHALL provide a monthly billing report showing: transaction count, total transaction volume, total commissions, and a breakdown by transaction type (buy/sell)

4. THE Transaction Engine SHALL allow users to download billing reports as PDF format with detailed transaction listings and fee calculations

5. THE Transaction Engine SHALL display fee information prominently during order preview before execution: "Commission fee: $X.XX (0.1% of $X,XXX.XX)"

### Requirement 12: User Profile Enhancement

**User Story:** As a user, I want to customize my profile with trading preferences and risk settings, so that the platform can provide personalized recommendations

#### Acceptance Criteria

1. THE Authentication System SHALL extend user profiles with fields: risk_tolerance (conservative/moderate/aggressive), investment_goals (text), preferred_sectors (array), notification_preferences (boolean flags)

2. WHEN a user updates their risk tolerance, THE Authentication System SHALL validate the value is one of the allowed options and save the preference

3. WHEN a user sets preferred sectors, THE Authentication System SHALL allow selection of multiple sectors from a predefined list: Technology, Healthcare, Finance, Energy, Consumer, Industrial, Real Estate, Utilities

4. THE Portfolio System SHALL use risk tolerance settings to provide personalized warnings: IF risk_tolerance='conservative' AND user attempts to buy a volatile stock (beta > 1.5), THEN display a warning message

5. THE Authentication System SHALL allow users to enable/disable email notifications for: dividend payments, large price movements in holdings (>5% change), and weekly portfolio summaries

### Requirement 13: Stock Search and Discovery

**User Story:** As a user, I want to search and discover stocks by various criteria, so that I can find investment opportunities matching my interests

#### Acceptance Criteria

1. THE Stock Repository SHALL provide a search interface accepting: stock symbol, company name (partial match), sector, and market cap range

2. WHEN a user enters a search query, THE Stock Repository SHALL return matching stocks within 2 seconds with columns: symbol, company name, sector, current price, day change percentage, and market cap

3. THE Stock Repository SHALL provide filtering options for: sector (dropdown), market cap (small/mid/large), price range, and day performance (gainers/losers)

4. WHEN a user clicks on a stock from search results, THE Stock Repository SHALL display a detailed stock page with: company information, current price, historical chart (1 year), ML predictions, sentiment analysis, and buy/sell buttons

5. THE Stock Repository SHALL display a "Trending Stocks" section on the dashboard showing the top 10 most-traded stocks on the platform in the last 24 hours

### Requirement 14: Performance Analytics

**User Story:** As a user, I want to view detailed analytics of my portfolio performance, so that I can evaluate my investment strategy

#### Acceptance Criteria

1. THE Portfolio System SHALL calculate and display performance metrics: total return (percentage and dollar amount), annualized return, best performing stock, worst performing stock, and win rate (profitable trades / total trades)

2. THE Portfolio System SHALL provide a performance chart showing portfolio value over time with options to view: 1 week, 1 month, 3 months, 6 months, 1 year, and all-time

3. THE Portfolio System SHALL display sector allocation as a pie chart showing the percentage of portfolio value in each sector

4. THE Portfolio System SHALL compare user performance against benchmark indices: S&P 500, NASDAQ, and DOW JONES with side-by-side return comparison

5. THE Portfolio System SHALL provide a trade analysis section showing: average holding period, most traded stocks, trading frequency, and profit/loss distribution histogram

### Requirement 15: Background Jobs for Price Refresh

**User Story:** As a system administrator, I want automated background jobs to refresh stock prices, so that the database stays current without manual intervention

#### Acceptance Criteria

1. THE Stock Repository SHALL implement a background job scheduler using APScheduler or Celery to run periodic tasks

2. THE Stock Repository SHALL run a "Daily Price Update" job every weekday at 4:30 PM EST (after market close) that: (a) fetches list of all unique company_ids from Holdings table, (b) calls yfinance to get latest daily data for each symbol, (c) inserts new PriceHistory records for today's date, (d) updates Companies.last_updated timestamp

3. THE Stock Repository SHALL run an "Intraday Price Refresh" job every 15 minutes during market hours (9:30 AM - 4:00 PM EST, Monday-Friday) that updates the most recent PriceHistory record for actively traded stocks (stocks with orders in last 24 hours)

4. WHEN a background job encounters an API error (rate limit, network timeout, invalid symbol), THE Stock Repository SHALL log the error with company_id and symbol, skip that stock, continue processing remaining stocks, and retry failed stocks after 5 minutes

5. THE Stock Repository SHALL provide a management command to manually trigger price refresh: flask refresh-prices --symbols AAPL,GOOGL,MSFT --date 2024-01-15

6. THE Stock Repository SHALL track job execution history in a JobLog table with fields: job_id, job_name, started_at, completed_at, status (SUCCESS/FAILED/PARTIAL), stocks_processed, stocks_failed, error_message

7. WHEN a background job completes, THE Stock Repository SHALL send a summary notification to admin users if any errors occurred: "Price refresh completed. Processed: X stocks, Failed: Y stocks. View details in job log."

### Requirement 15A: Static Dataset Support

**User Story:** As a developer, I want to support both live and static dataset modes, so that I can test the system without API dependencies and demonstrate historical scenarios

#### Acceptance Criteria

1. THE Stock Repository SHALL provide a configuration setting 'DATA_MODE' in config.py with values: 'LIVE' (default, uses yfinance) or 'STATIC' (uses local CSV files from data/stocks/ directory)

2. WHEN DATA_MODE='STATIC', THE Stock Repository SHALL load historical price data from CSV files with naming convention: data/stocks/{SYMBOL}.csv with columns: Date,Open,High,Low,Close,Adj Close,Volume

3. THE Stock Repository SHALL support a 'SIMULATION_DATE' setting in config.py that, when DATA_MODE='STATIC', treats that date as "today" for all price lookups, predictions, and order executions

4. WHEN DATA_MODE='STATIC', THE Transaction Engine SHALL use prices from the static CSV file at the SIMULATION_DATE for all buy/sell transactions, and SHALL reject orders if SIMULATION_DATE is not found in the CSV

5. THE Stock Repository SHALL provide a management command to download and save stock data as CSV files for offline use: flask import-stock-data --symbol AAPL --start 2020-01-01 --end 2023-12-31 --output data/stocks/

6. WHEN DATA_MODE='STATIC', THE Stock Repository SHALL disable all background price refresh jobs and display a warning banner on admin dashboard: "Running in STATIC mode - prices will not update automatically"

7. THE Stock Repository SHALL validate on startup that if DATA_MODE='STATIC', the data/stocks/ directory exists and contains at least one valid CSV file, otherwise log error and switch to LIVE mode

### Requirement 16: Database Migration and Setup

**User Story:** As a developer, I want automated database setup and migration tools, so that I can easily deploy and update the database schema

#### Acceptance Criteria

1. THE Database Layer SHALL provide a database initialization script that creates all required tables with proper indexes and foreign key constraints

2. THE Database Layer SHALL use Flask-Migrate (Alembic) for database migrations to track schema changes over time

3. WHEN the application starts for the first time, THE Database Layer SHALL automatically run migrations to create the initial schema

4. THE Database Layer SHALL provide management commands: 'flask db init' (initialize migrations), 'flask db migrate' (generate migration), 'flask db upgrade' (apply migrations)

5. THE Database Layer SHALL include seed data scripts to populate initial data: sample stocks, admin user account, and test user accounts for development

### Requirement 17: Error Handling and Validation

**User Story:** As a user, I want clear error messages and validation feedback, so that I understand what went wrong and how to fix it

#### Acceptance Criteria

1. WHEN any database operation fails, THE Database Layer SHALL log the error with full stack trace and display a user-friendly message "An error occurred. Please try again later."

2. WHEN API calls to yfinance fail, THE Stock Repository SHALL retry up to 3 times with exponential backoff before displaying an error message "Unable to fetch stock data. Please try again."

3. WHEN a user submits invalid form data, THE Authentication System SHALL display field-specific error messages next to the invalid fields with clear instructions

4. THE Transaction Engine SHALL validate all monetary amounts are positive numbers with maximum 2 decimal places before processing

5. WHEN a user attempts an action requiring authentication while logged out, THE Authentication System SHALL redirect to the login page with a message "Please log in to continue" and return to the intended page after successful login

### Requirement 18: Security and Data Protection

**User Story:** As a user, I want my account and data to be secure, so that I can trust the platform with my information

#### Acceptance Criteria

1. THE Authentication System SHALL hash all passwords using bcrypt with a work factor of at least 12 before storing in the database

2. THE Authentication System SHALL implement CSRF protection on all forms using Flask-WTF CSRF tokens

3. THE Database Layer SHALL use parameterized queries for all database operations to prevent SQL injection attacks

4. THE Authentication System SHALL implement rate limiting on login attempts: maximum 5 failed attempts per email address within 15 minutes, then require a 15-minute cooldown

5. THE Authentication System SHALL set secure session cookies with flags: HttpOnly=true, Secure=true (in production), SameSite=Lax

### Requirement 19: UI Navigation and Page Structure

**User Story:** As a user, I want intuitive navigation between different sections of the platform, so that I can easily access all features

#### Acceptance Criteria

1. THE Portfolio System SHALL provide a navigation menu (navbar) displayed on all pages with links: Home, Dashboard, Portfolio, Orders, Reports, Profile, Logout, and Admin (visible only to admin users)

2. WHEN a user is not logged in, THE Portfolio System SHALL display a public navigation menu with links: Home, About, Login, Register

3. THE Portfolio System SHALL implement the following page routes: (a) / (home/landing page), (b) /login (login form), (c) /register (registration form), (d) /dashboard (user dashboard with predictions), (e) /portfolio (holdings and valuations), (f) /orders (order history and new order form), (g) /reports (transaction and billing reports), (h) /profile (user profile and settings), (i) /admin (admin dashboard, requires admin role), (j) /admin/users (user management), (k) /admin/companies (company CRUD), (l) /admin/brokers (broker management), (m) /admin/dividends (dividend management), (n) /admin/monitoring (system monitoring)

4. THE Portfolio System SHALL highlight the active page in the navigation menu by adding an 'active' CSS class to the current page's nav link

5. WHEN a user accesses the Dashboard page (/dashboard), THE Portfolio System SHALL display: welcome message with user's name, wallet balance card, portfolio value card, top holdings (top 3 by value), quick stock prediction form (symbol input + predict button), recent transactions (last 5), and links to "View Full Portfolio" and "Place Order"

6. WHEN a user accesses the Portfolio page (/portfolio), THE Portfolio System SHALL display: portfolio summary (total invested, current value, unrealized gain/loss, return %), holdings table (symbol, company name, quantity, avg price, current price, total value, gain/loss, % change, actions: Sell), sector allocation pie chart, performance chart (portfolio value over time), and "Add to Portfolio" button

7. WHEN a user accesses the Orders page (/orders), THE Portfolio System SHALL display: new order form (symbol input with autocomplete, order type radio: BUY/SELL, quantity input, price preview, submit button), order history table (date, symbol, type, quantity, price, commission, total, status, actions: View Details), and filter controls (date range, type, status)

8. WHEN a user accesses the Reports page (/reports), THE Portfolio System SHALL display: report type selector (Transaction Report / Billing Report / Performance Report), date range picker, generate button, and report display area with export options (PDF, CSV)

9. WHEN a user accesses the Profile page (/profile), THE Portfolio System SHALL display: profile information form (email, full name, risk tolerance, investment goals, preferred sectors), password change form (current password, new password, confirm password), notification preferences checkboxes, and save button

10. WHEN an admin accesses the Admin Dashboard (/admin), THE Portfolio System SHALL display: system metrics cards (users, transactions, volume, health), quick links to management sections (Users, Companies, Brokers, Dividends, Monitoring), recent activity feed (last 20 admin actions), and system alerts panel

11. THE Portfolio System SHALL use a consistent layout template (base.html) with: header (navbar), main content area, footer (copyright, links), and flash message display area for success/error/info messages

12. THE Portfolio System SHALL display flash messages using Flask's flash() function with categories: 'success' (green), 'error' (red), 'warning' (yellow), 'info' (blue), and auto-dismiss after 5 seconds

13. THE Portfolio System SHALL implement breadcrumb navigation on all pages showing the current page hierarchy: Home > Dashboard > Portfolio

### Requirement 19A: Responsive Design and User Experience

**User Story:** As a user, I want the platform to work well on mobile devices, so that I can manage my portfolio on the go

#### Acceptance Criteria

1. THE Portfolio System SHALL render all pages with responsive CSS using Bootstrap 5 grid system that adapts to screen sizes: mobile (<768px), tablet (768-1024px), and desktop (>1024px)

2. WHEN viewed on mobile devices (width < 768px), THE Portfolio System SHALL display a hamburger menu icon for navigation, collapse the navbar into a dropdown menu, and stack portfolio holdings vertically with full-width cards

3. THE Portfolio System SHALL ensure all interactive elements (buttons, links, form inputs) have minimum touch target size of 44x44 pixels on mobile devices

4. THE Portfolio System SHALL optimize page load times to under 3 seconds on 3G connections by: (a) minifying CSS and JavaScript, (b) using lazy loading for images, (c) caching static assets with appropriate headers, (d) loading charts only when visible

5. THE Portfolio System SHALL provide a mobile-friendly stock search with autocomplete suggestions appearing below the search input, limited to 5 suggestions on mobile and 10 on desktop

### Requirement 20: Notification System

**User Story:** As a user, I want to receive notifications about important portfolio events, so that I can stay informed about my investments

#### Acceptance Criteria

1. THE Portfolio System SHALL display in-app notifications for: completed transactions, dividend payments, and significant price movements (>5% change) in holdings

2. WHEN a notification is generated, THE Portfolio System SHALL store it with fields: notification_id, user_id, type, title, message, is_read (boolean), created_at

3. WHEN a user logs in, THE Portfolio System SHALL display unread notification count in the navigation bar with a badge indicator

4. WHEN a user clicks the notification icon, THE Portfolio System SHALL display a dropdown list of recent notifications (last 10) with options to mark as read or view all

5. WHERE a user has enabled email notifications in preferences, THE Portfolio System SHALL send email summaries for: weekly portfolio performance, monthly transaction summary, and immediate alerts for dividends received
