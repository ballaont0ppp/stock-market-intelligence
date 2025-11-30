# Test Data Requirements

## Overview

This document specifies the test data requirements for the Stock Portfolio Management Platform. Proper test data is essential for comprehensive testing and ensuring consistent, repeatable test results.

## Test Data Principles

1. **Realistic**: Test data should mirror production data patterns
2. **Comprehensive**: Cover all scenarios including edge cases
3. **Isolated**: Test data should not affect production
4. **Repeatable**: Same data produces same results
5. **Privacy-Compliant**: No real PII or sensitive data

## Test User Accounts

### Admin Users

```json
{
  "email": "admin@testplatform.com",
  "password": "AdminTest123!",
  "full_name": "Test Administrator",
  "is_admin": true,
  "account_status": "active",
  "wallet_balance": 1000000.00
}
`