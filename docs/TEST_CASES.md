# Test Cases and Scenarios

## Overview

This document provides detailed test cases and scenarios for the Stock Portfolio Management Platform. Each test case includes preconditions, steps, expected results, and priority.

## Test Case Format

```
TC-XXX: Test Case Title
Priority: High/Medium/Low
Type: Unit/Integration/E2E
Prerequisites: [List of preconditions]
Steps:
  1. Step 1
  2. Step 2
  3. Step 3
Expected Result: [Expected outcome]
Actual Result: [To be filled during execution]
Status: Pass/Fail/Blocked
```

## Authentication Module

### TC-001: User Registration - Valid Data
**Priority**: High  
**Type**: Integration  
**Prerequisites**: None

**Steps**:
1. Navigate to registration page
2. Enter valid email: test@example.com
3. Enter valid password: SecurePass123!
4. Enter full name: John Doe
5. Click Register button

**Expected Result**:
- User account created successfully
- User redirected to login page
- Success message displayed
- Wallet created with $100,000 balance

---

### TC-002: User Registration - Duplicate Email
**Priority**: High  
**Type**: Integration  
**Prerequisites**: User with email test@example.com exists

**Steps**:
1. Navigate to registration page
2. Enter existing email: test@example.com
3. Enter valid password: SecurePass123!
4. Enter full name: Jane Doe
5. Click Register button

**Expected Result**:
- Registration fails
- Error message: "Email already registered"
- User remains on registration page

---

### TC-003: User Login - Valid Credentials
**Priority**: High  
**Type**: Integration  
**Prerequisites**: User account exists

**Steps**:
1. Navigate to login page
2. Enter valid email
3. Enter valid password
4. Click Login button

**Expected Result**:
- User authenticated successfully
- Redirected to dashboard
- Session created
- Last login timestamp updated

---

### TC-004: User Login - Invalid Password
**Priority**: High  
**Type**: Integration  
**Prerequisites**: User account exists

**Steps**:
1. Navigate to login page
2. Enter valid email
3. Enter incorrect password
4. Click Login button

**Expected Result**:
- Login fails
- Error message: "Invalid email or password"
- User remains on login page
- Failed attempt logged

---

### TC-005: Rate Limiting - Multiple Failed Logins
**Priority**: High  
**Type**: Integration  
**Prerequisites**: User account exists

**Steps**:
1. Attempt login with wrong password (5 times)
2. Attempt 6th login with correct password

**Expected Result**:
- First 5 attempts: "Invalid email or password"
- 6th attempt: "Too many failed attempts. Please try again in 15 minutes"
- Account temporarily locked

---

## Portfolio Management Module

### TC-010: View Portfolio - With Holdings
**Priority**: High  
**Type**: Integration  
**Prerequisites**: User logged in, has stock holdings

**Steps**:
1. Navigate to Portfolio page
2. View holdings table

**Expected Result**:
- All holdings displayed
- Columns: Symbol, Company, Quantity, Avg Price, Current Price, Value, Gain/Loss
- Summary metrics shown: Total Value, Total Gain/Loss, Return %
- Current prices fetched from yfinance

---

### TC-011: View Portfolio - Empty Portfolio
**Priority**: Medium  
**Type**: Integration  
**Prerequisites**: User logged in, no holdings

**Steps**:
1. Navigate to Portfolio page

**Expected Result**:
- Message displayed: "Your portfolio is empty. Start investing to build your portfolio."
- Summary shows $0 portfolio value
- Wallet balance displayed

---

### TC-012: Deposit Funds - Valid Amount
**Priority**: High  
**Type**: Integration  
**Prerequisites**: User logged in

**Steps**:
1. Navigate to Wallet page
2. Enter deposit amount: 5000.00
3. Click Deposit button

**Expected Result**:
- Wallet balance increased by $5,000
- Transaction record created (type: DEPOSIT)
- Success message: "Deposited $5,000.00 to your wallet"
- Total deposited updated

---

### TC-013: Deposit Funds - Exceeds Limit
**Priority**: Medium  
**Type**: Integration  
**Prerequisites**: User logged in

**Steps**:
1. Navigate to Wallet page
2. Enter deposit amount: 1500000.00
3. Click Deposit button

**Expected Result**:
- Deposit rejected
- Error message: "Deposit amount cannot exceed $1,000,000"
- Wallet balance unchanged

---

### TC-014: Withdraw Funds - Sufficient Balance
**Priority**: High  
**Type**: Integration  
**Prerequisites**: User logged in, wallet balance >= $1,000

**Steps**:
1. Navigate to Wallet page
2. Enter withdrawal amount: 1000.00
3. Click Withdraw button

**Expected Result**:
- Wallet balance decreased by $1,000
- Transaction record created (type: WITHDRAWAL)
- Success message: "Withdrew $1,000.00 from your wallet"
- Total withdrawn updated

---

### TC-015: Withdraw Funds - Insufficient Balance
**Priority**: High  
**Type**: Integration  
**Prerequisites**: User logged in, wallet balance < requested amount

**Steps**:
1. Navigate to Wallet page
2. Enter withdrawal amount greater than balance
3. Click Withdraw button

**Expected Result**:
- Withdrawal rejected
- Error message: "Insufficient funds"
- Wallet balance unchanged

---

## Trading Module

### TC-020: Buy Stock - Sufficient Funds
**Priority**: High  
**Type**: Integration  
**Prerequisites**: User logged in, wallet balance >= order cost

**Steps**:
1. Navigate to Orders > Buy page
2. Enter stock symbol: AAPL
3. Enter quantity: 10
4. Review order preview (price, commission, total)
5. Click Buy button

**Expected Result**:
- Order created with status COMPLETED
- Wallet balance debited (price * quantity + commission)
- Holding created or updated
- Transaction records created (BUY + FEE)
- Success message with order details
- Processing time < 5 seconds

---

### TC-021: Buy Stock - Insufficient Funds
**Priority**: High  
**Type**: Integration  
**Prerequisites**: User logged in, wallet balance < order cost

**Steps**:
1. Navigate to Orders > Buy page
2. Enter stock symbol: AAPL
3. Enter quantity: 1000
4. Click Buy button

**Expected Result**:
- Order created with status FAILED
- Error message: "Insufficient funds for this purchase. Required: $X, Available: $Y"
- Wallet balance unchanged
- No holding created
- Failure reason logged

---

### TC-022: Buy Stock - Invalid Symbol
**Priority**: Medium  
**Type**: Integration  
**Prerequisites**: User logged in

**Steps**:
1. Navigate to Orders > Buy page
2. Enter invalid stock symbol: INVALID123
3. Enter quantity: 10
4. Click Buy button

**Expected Result**:
- Order rejected
- Error message: "Invalid stock symbol"
- Wallet balance unchanged

---

### TC-023: Sell Stock - Sufficient Shares
**Priority**: High  
**Type**: Integration  
**Prerequisites**: User logged in, owns >= 10 shares of AAPL

**Steps**:
1. Navigate to Orders > Sell page
2. Enter stock symbol: AAPL
3. Enter quantity: 10
4. Click Sell button

**Expected Result**:
- Order created with status COMPLETED
- Wallet balance credited (price * quantity - commission)
- Holding quantity reduced by 10
- If quantity reaches 0, holding deleted
- Transaction records created (SELL + FEE)
- Realized gain/loss calculated and displayed
- Success message with order details

---

### TC-024: Sell Stock - Insufficient Shares
**Priority**: High  
**Type**: Integration  
**Prerequisites**: User logged in, owns < requested quantity

**Steps**:
1. Navigate to Orders > Sell page
2. Enter stock symbol: AAPL
3. Enter quantity greater than owned
4. Click Sell button

**Expected Result**:
- Order created with status FAILED
- Error message: "Insufficient shares to sell. You own X shares, but attempted to sell Y shares"
- Wallet balance unchanged
- Holdings unchanged
- Failure reason logged

---

### TC-025: Sell Stock - Not Owned
**Priority**: Medium  
**Type**: Integration  
**Prerequisites**: User logged in, does not own stock

**Steps**:
1. Navigate to Orders > Sell page
2. Enter stock symbol: GOOGL
3. Enter quantity: 10
4. Click Sell button

**Expected Result**:
- Order rejected
- Error message: "You do not own any shares of GOOGL"
- Wallet balance unchanged

---

## Prediction Module

### TC-030: Stock Prediction - Valid Symbol
**Priority**: High  
**Type**: Integration  
**Prerequisites**: User logged in

**Steps**:
1. Navigate to Dashboard
2. Enter stock symbol: AAPL
3. Click Predict button

**Expected Result**:
- Predictions displayed for all models (ARIMA, LSTM, LR)
- Sentiment analysis shown
- Visualizations generated
- Recommendation provided (BUY/SELL/HOLD)
- Processing time < 30 seconds

---

### TC-031: Stock Prediction - Invalid Symbol
**Priority**: Medium  
**Type**: Integration  
**Prerequisites**: User logged in

**Steps**:
1. Navigate to Dashboard
2. Enter invalid stock symbol: INVALID
3. Click Predict button

**Expected Result**:
- Error message: "Unable to fetch data for symbol INVALID"
- No predictions displayed

---

### TC-032: Sentiment Analysis - Cached Data
**Priority**: Medium  
**Type**: Integration  
**Prerequisites**: Sentiment data cached for AAPL (< 1 hour old)

**Steps**:
1. Request prediction for AAPL
2. Check sentiment data source

**Expected Result**:
- Cached sentiment data used
- No Twitter API call made
- Fast response time
- Cache timestamp displayed

---

## Admin Module

### TC-040: Admin Dashboard - Access Control
**Priority**: High  
**Type**: Integration  
**Prerequisites**: Regular user logged in (not admin)

**Steps**:
1. Navigate to /admin URL

**Expected Result**:
- Access denied
- 403 Forbidden error
- Error message: "Access denied. Admin privileges required."
- Redirected to dashboard

---

### TC-041: Admin Dashboard - Metrics Display
**Priority**: High  
**Type**: Integration  
**Prerequisites**: Admin user logged in

**Steps**:
1. Navigate to Admin Dashboard

**Expected Result**:
- System metrics displayed:
  - Total users
  - Active users
  - Total transactions today
  - Transaction volume
  - Total portfolio value
  - Top 5 traded stocks
  - System health status

---

### TC-042: User Management - Suspend User
**Priority**: High  
**Type**: Integration  
**Prerequisites**: Admin logged in, target user exists

**Steps**:
1. Navigate to Admin > Users
2. Click "Suspend" for target user
3. Enter suspension reason
4. Confirm suspension

**Expected Result**:
- User account status changed to 'suspended'
- Action logged in audit log
- User cannot login
- Success message displayed

---

### TC-043: Company Management - Create Company
**Priority**: Medium  
**Type**: Integration  
**Prerequisites**: Admin logged in

**Steps**:
1. Navigate to Admin > Companies
2. Click "Create Company"
3. Enter symbol: NEWCO
4. Enter company name: New Company Inc.
5. Enter sector, industry
6. Click Save

**Expected Result**:
- Company created in database
- Additional data fetched from yfinance (if available)
- Success message displayed
- Company appears in list

---

### TC-044: Dividend Management - Create Dividend
**Priority**: Medium  
**Type**: Integration  
**Prerequisites**: Admin logged in, company exists

**Steps**:
1. Navigate to Admin > Dividends
2. Click "Create Dividend"
3. Select company: AAPL
4. Enter dividend per share: 0.25
5. Enter payment date (future)
6. Enter record date, ex-dividend date
7. Click Save

**Expected Result**:
- Dividend created
- Dates validated (payment > record > ex-dividend)
- Dividend payment job scheduled
- Success message displayed

---

## Reporting Module

### TC-050: Transaction Report - Date Range
**Priority**: Medium  
**Type**: Integration  
**Prerequisites**: User logged in, has transactions

**Steps**:
1. Navigate to Reports
2. Select "Transaction Report"
3. Select date range: Last 30 days
4. Click Generate

**Expected Result**:
- Report generated with all transactions in range
- Summary statistics displayed
- Export to CSV available
- Generation time < 5 seconds

---

### TC-051: Billing Report - Monthly
**Priority**: Medium  
**Type**: Integration  
**Prerequisites**: User logged in, has transactions

**Steps**:
1. Navigate to Reports
2. Select "Billing Report"
3. Select month and year
4. Click Generate

**Expected Result**:
- Report shows:
  - Transaction count
  - Transaction volume
  - Total commissions paid
  - Breakdown by transaction type
- Export to PDF available

---

### TC-052: Performance Report - Portfolio Analysis
**Priority**: Medium  
**Type**: Integration  
**Prerequisites**: User logged in, has holdings

**Steps**:
1. Navigate to Reports
2. Select "Performance Report"
3. Select period: Last 6 months
4. Click Generate

**Expected Result**:
- Report shows:
  - Portfolio value over time
  - Returns vs benchmarks
  - Best/worst performing stocks
  - Sector allocation
- Charts and visualizations included

---

## Security Tests

### TC-060: SQL Injection Prevention
**Priority**: High  
**Type**: Security  
**Prerequisites**: None

**Steps**:
1. Attempt SQL injection in login form
2. Enter email: admin' OR '1'='1
3. Enter password: anything

**Expected Result**:
- Login fails
- No SQL error displayed
- Parameterized queries prevent injection
- Attempt logged

---

### TC-061: XSS Prevention
**Priority**: High  
**Type**: Security  
**Prerequisites**: User logged in

**Steps**:
1. Attempt XSS in profile update
2. Enter full name: <script>alert('XSS')</script>
3. Save profile

**Expected Result**:
- Script tags escaped
- No JavaScript executed
- Data stored safely
- Display shows escaped text

---

### TC-062: CSRF Protection
**Priority**: High  
**Type**: Security  
**Prerequisites**: User logged in

**Steps**:
1. Submit form without CSRF token
2. Attempt POST request from external site

**Expected Result**:
- Request rejected
- 400 Bad Request error
- CSRF token validation enforced

---

## Performance Tests

### TC-070: Page Load Time - Dashboard
**Priority**: High  
**Type**: Performance  
**Prerequisites**: User logged in

**Steps**:
1. Navigate to Dashboard
2. Measure page load time

**Expected Result**:
- Page loads in < 2 seconds
- All assets loaded
- No JavaScript errors

---

### TC-071: Concurrent Orders - 100 Users
**Priority**: High  
**Type**: Performance  
**Prerequisites**: 100 test users, sufficient test data

**Steps**:
1. Simulate 100 concurrent buy orders
2. Measure response times
3. Check for race conditions

**Expected Result**:
- All orders processed correctly
- No duplicate transactions
- No wallet balance errors
- Average response time < 3 seconds
- No database deadlocks

---

### TC-072: Database Query Performance
**Priority**: Medium  
**Type**: Performance  
**Prerequisites**: Database with 1M+ transactions

**Steps**:
1. Execute complex portfolio query
2. Measure query execution time

**Expected Result**:
- Query completes in < 1 second
- Proper indexes used
- No full table scans

---

## Accessibility Tests

### TC-080: Keyboard Navigation
**Priority**: High  
**Type**: Accessibility  
**Prerequisites**: None

**Steps**:
1. Navigate entire application using only keyboard
2. Tab through all interactive elements
3. Activate buttons with Enter/Space

**Expected Result**:
- All elements reachable via keyboard
- Focus indicators visible
- Logical tab order
- No keyboard traps

---

### TC-081: Screen Reader Compatibility
**Priority**: High  
**Type**: Accessibility  
**Prerequisites**: Screen reader installed (NVDA/JAWS)

**Steps**:
1. Navigate application with screen reader
2. Verify all content announced
3. Check form labels and error messages

**Expected Result**:
- All content accessible
- Proper ARIA labels
- Form fields properly labeled
- Error messages announced

---

### TC-082: Color Contrast
**Priority**: Medium  
**Type**: Accessibility  
**Prerequisites**: None

**Steps**:
1. Check color contrast ratios
2. Use WAVE or axe DevTools

**Expected Result**:
- All text meets 4.5:1 contrast ratio
- Large text meets 3:1 ratio
- WCAG 2.1 Level AA compliant

---

## Test Execution Summary

### Priority Distribution
- **High Priority**: 35 test cases (critical functionality)
- **Medium Priority**: 20 test cases (important features)
- **Low Priority**: 10 test cases (nice-to-have)

### Type Distribution
- **Unit Tests**: 150+ test cases
- **Integration Tests**: 65 test cases
- **E2E Tests**: 15 test cases
- **Security Tests**: 20 test cases
- **Performance Tests**: 10 test cases
- **Accessibility Tests**: 15 test cases

### Execution Schedule
- **Smoke Tests**: After every deployment (5 minutes)
- **Regression Tests**: Before every release (2 hours)
- **Full Suite**: Nightly (3 hours)
- **Performance Tests**: Weekly
- **Security Tests**: Weekly
- **Accessibility Tests**: Monthly

## Test Data Requirements

### User Accounts
- Admin user: admin@example.com
- Regular users: user1@example.com, user2@example.com
- Suspended user: suspended@example.com

### Stock Data
- Active stocks: AAPL, GOOGL, MSFT, AMZN, TSLA
- Invalid symbols: INVALID, FAKE123

### Financial Data
- Wallet balances: $100,000 (default), $50,000, $1,000,000
- Holdings: Various quantities of different stocks
- Transactions: Mix of buys, sells, deposits, withdrawals

## Test Environment Setup

### Prerequisites
- Python 3.9+
- MySQL 8.0+
- Test database: stock_portfolio_test
- Environment variables configured

### Setup Steps
1. Create test database
2. Run migrations
3. Seed test data
4. Configure environment variables
5. Install dependencies

### Teardown
1. Clear test data
2. Reset database
3. Clean up temporary files

## References

- Test execution results: `test_reports/`
- Coverage reports: `htmlcov/`
- Test data: `tests/fixtures/`
- CI/CD pipeline: `.github/workflows/`
