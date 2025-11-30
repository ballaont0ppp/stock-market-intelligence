# Administrator Guide

## Table of Contents

1. [Admin Dashboard Overview](#admin-dashboard-overview)
2. [User Management](#user-management)
3. [Company Management](#company-management)
4. [Broker Management](#broker-management)
5. [Dividend Management](#dividend-management)
6. [System Monitoring](#system-monitoring)
7. [Audit Logs](#audit-logs)
8. [Best Practices](#best-practices)

## Admin Dashboard Overview

### Accessing the Admin Dashboard

1. Log in with an admin account
2. Click "Admin" in the navigation menu
3. You'll see the admin dashboard with system metrics

### Dashboard Metrics

The admin dashboard displays:

**User Metrics**:
- Total registered users
- Active users (traded in last 30 days)
- New users today
- Suspended accounts

**Transaction Metrics**:
- Transactions today
- Transaction volume today (dollar amount)
- Total transaction volume (all-time)
- Average transaction size

**Portfolio Metrics**:
- Total portfolio value across all users
- Total holdings count
- Most traded stocks

**System Health**:
- Database status (green/yellow/red)
- API status (yfinance, Twitter)
- ML model status
- Background job status
- Overall system health

## User Management

### Viewing All Users

1. Go to Admin → Users
2. View user list with:
   - User ID
   - Email
   - Full Name
   - Registration Date
   - Wallet Balance
   - Portfolio Value
   - Total Transactions
   - Last Login
   - Account Status
   - Actions

### Filtering and Searching Users

**Search**:
- Search by email or name
- Use the search box at the top of the user list

**Filters**:
- Filter by account status (Active/Suspended)
- Filter by registration date range
- Filter by activity level
- Sort by any column

### Viewing User Details

1. Click "View Details" next to a user
2. See complete user information:
   - Profile information
   - Wallet balance and transaction history
   - Current holdings with values
   - Order history
   - Performance metrics
   - Activity timeline

### Editing User Information

1. Click "Edit" next to a user
2. Update user information:
   - Full Name
   - Email
   - Risk Tolerance
   - Investment Goals
   - Preferred Sectors
   - Notification Preferences
3. Click "Save Changes"

**Note**: You cannot change user passwords. Users must reset their own passwords.

### Adjusting Wallet Balance

1. View user details
2. Click "Adjust Balance"
3. Enter adjustment amount (positive or negative)
4. Enter reason for adjustment (required)
5. Click "Adjust"

**Important**: This action is logged in the audit log.

### Suspending User Accounts

1. Click "Suspend" next to a user
2. Enter suspension reason (required)
3. Confirm suspension
4. User will be unable to log in
5. Suspension is logged in audit log

**Effects of Suspension**:
- User cannot log in
- All pending orders are cancelled
- Holdings and wallet balance are preserved
- User can be reactivated later

### Reactivating User Accounts

1. Find suspended user
2. Click "Activate"
3. Confirm reactivation
4. User can log in again
5. Reactivation is logged in audit log

### Deleting User Accounts

1. Click "Delete" next to a user
2. Confirm deletion (this is permanent)
3. All user data is removed:
   - User account
   - Wallet
   - Holdings
   - Orders
   - Transactions

**Warning**: This action cannot be undone. Consider suspension instead.

## Company Management

### Viewing All Companies

1. Go to Admin → Companies
2. View company list with:
   - Symbol
   - Company Name
   - Sector
   - Industry
   - Market Cap
   - Last Updated
   - Status (Active/Inactive)
   - Actions

### Adding New Companies

1. Click "Add Company"
2. Enter company information:
   - Stock Symbol (required, 1-10 uppercase characters)
   - Company Name (required)
   - Sector
   - Industry
   - Description
   - Website
3. Click "Create Company"

**Automatic Data Fetching**:
- System automatically fetches additional data from yfinance
- Market cap, CEO, employees, etc. are populated automatically
- Historical price data is downloaded

### Editing Company Information

1. Click "Edit" next to a company
2. Update company details
3. Click "Save Changes"

**Editable Fields**:
- Company Name
- Sector
- Industry
- Description
- Website
- CEO
- Employees
- Founded Year
- Headquarters

**Non-Editable Fields**:
- Stock Symbol (cannot be changed after creation)
- Market Cap (updated automatically)

### Deactivating Companies

1. Click "Deactivate" next to a company
2. Confirm deactivation

**Effects of Deactivation**:
- Company is hidden from user searches
- Users cannot place new orders for this stock
- Existing holdings are preserved
- Price updates stop
- Can be reactivated later

### Reactivating Companies

1. Filter to show inactive companies
2. Click "Activate" next to a company
3. Confirm reactivation
4. Price updates resume

### Bulk Importing Companies

1. Click "Import Companies"
2. Download the CSV template
3. Fill in company data:
   ```csv
   symbol,company_name,sector,industry,description,website
   AAPL,Apple Inc.,Technology,Consumer Electronics,Apple designs and manufactures consumer electronics,https://www.apple.com
   GOOGL,Alphabet Inc.,Technology,Internet Services,Google parent company,https://www.google.com
   ```
4. Upload the CSV file
5. Review import preview
6. Click "Import"
7. System processes each company:
   - Validates data
   - Checks for duplicates
   - Fetches additional data from yfinance
   - Creates company records

**Import Results**:
- Success count
- Failed count
- Error details for failed imports

## Broker Management

### Viewing All Brokers

1. Go to Admin → Brokers
2. View broker list with:
   - Broker Name
   - License Number
   - Email
   - Phone
   - Assigned Users Count
   - Status (Active/Inactive)
   - Actions

### Creating New Brokers

1. Click "Add Broker"
2. Select an admin user account (required)
3. Enter broker information:
   - Broker Name
   - License Number
   - Phone
   - Email
4. Click "Create Broker"

**Requirements**:
- Must be linked to an existing admin user
- Each admin user can only be one broker
- License number should be unique

### Editing Broker Information

1. Click "Edit" next to a broker
2. Update broker details
3. Click "Save Changes"

### Assigning Users to Brokers

1. View broker details
2. Click "Assign Users"
3. Select users from the list
4. Click "Assign"

**Use Cases**:
- Organize users by broker
- Track broker performance
- Generate broker-specific reports

### Deactivating Brokers

1. Click "Deactivate" next to a broker
2. Confirm deactivation

**Effects**:
- Broker cannot access broker-specific features
- Assigned users are unaffected
- Can be reactivated later

## Dividend Management

### Viewing All Dividends

1. Go to Admin → Dividends
2. View dividend list with:
   - Company Symbol
   - Dividend Per Share
   - Payment Date
   - Record Date
   - Ex-Dividend Date
   - Announcement Date
   - Type (Regular/Special)
   - Actions

### Creating Dividend Announcements

1. Click "Add Dividend"
2. Select company
3. Enter dividend information:
   - Dividend Per Share (required, must be positive)
   - Payment Date (required)
   - Record Date (required, must be before payment date)
   - Ex-Dividend Date (required, must be before record date)
   - Announcement Date (optional)
   - Dividend Type (Regular/Special)
4. Click "Create Dividend"

**Validation Rules**:
- Payment Date > Record Date > Ex-Dividend Date
- Dividend Per Share must be positive
- Company must exist and be active

**Automatic Processing**:
- System automatically processes dividend on payment date
- All users holding the stock receive payments
- Payments are added to user wallets
- Transaction records are created
- Notifications are sent to users

### Editing Dividend Information

1. Click "Edit" next to a dividend
2. Update dividend details
3. Click "Save Changes"

**Restrictions**:
- Can only edit future dividends
- Cannot edit dividends with payment date in the past
- Cannot change company after creation

### Deleting Dividends

1. Click "Delete" next to a dividend
2. Confirm deletion

**Restrictions**:
- Can only delete future dividends
- Cannot delete processed dividends
- Deletion is permanent

### Viewing Dividend Payment History

1. Click "View Payments" next to a dividend
2. See all users who received payments:
   - User email
   - Shares owned
   - Amount paid
   - Payment timestamp

## System Monitoring

### Accessing System Monitoring

1. Go to Admin → Monitoring
2. View real-time system metrics

### Transaction Monitoring

**Real-Time Transaction Feed**:
- Auto-refreshes every 30 seconds
- Shows recent transactions across all users
- Displays:
  - Timestamp
  - User email
  - Transaction type
  - Company symbol
  - Amount
  - Status

**Filtering**:
- Filter by date range
- Filter by transaction type
- Filter by user
- Filter by company
- Filter by status

**Use Cases**:
- Monitor suspicious activity
- Track high-value transactions
- Identify system issues
- Generate reports

### API Usage Statistics

**yfinance API**:
- Total calls today
- Average response time
- Failed requests
- Rate limit status

**Twitter API**:
- Total calls today
- Average response time
- Failed requests
- Rate limit status
- Authentication status

**Actions**:
- View detailed API logs
- Reset rate limit counters
- Update API credentials

### Database Performance

**Metrics**:
- Query count
- Average query time
- Slow queries (>1 second)
- Connection pool status
- Database size

**Slow Query Log**:
- View queries taking >1 second
- See query execution plans
- Identify optimization opportunities

**Actions**:
- Run database optimization
- Clear query cache
- Rebuild indexes

### Background Job Status

**Job Monitoring**:
- Price updater status
- Dividend processor status
- Last execution time
- Next scheduled execution
- Execution history

**Job Logs**:
- View execution logs
- See success/failure counts
- Review error messages

**Actions**:
- Manually trigger jobs
- Pause/resume jobs
- View detailed job logs

### System Health Indicators

**Color-Coded Status**:
- **Green**: All systems operational
- **Yellow**: Minor issues, degraded performance
- **Red**: Critical issues, system down

**Components Monitored**:
- Database connectivity
- API availability (yfinance, Twitter)
- ML model service
- Background job scheduler
- Web server

**Alerts**:
- System automatically logs alerts for red status
- Admin receives notifications
- Alerts include timestamp and error details

## Audit Logs

### Viewing Audit Logs

1. Go to Admin → Audit Logs
2. View all admin actions with:
   - Timestamp
   - Admin email
   - Action type
   - Entity type (User/Company/Broker/Dividend)
   - Entity ID
   - Changes made (JSON format)
   - IP address

### Filtering Audit Logs

**Filters**:
- Date range
- Admin user
- Action type (Create/Update/Delete/Suspend/Activate)
- Entity type

**Search**:
- Search by entity ID
- Search by admin email
- Search by IP address

### Audit Log Actions

**Logged Actions**:
- User account modifications
- User suspensions/activations
- User deletions
- Wallet balance adjustments
- Company creations/updates/deactivations
- Broker creations/updates/deactivations
- Dividend creations/updates/deletions
- System configuration changes

**Log Details**:
- Before and after values for updates
- Reason for action (if provided)
- IP address of admin
- Timestamp (UTC)

### Exporting Audit Logs

1. Apply desired filters
2. Click "Export to CSV"
3. Save the file

**Use Cases**:
- Compliance reporting
- Security audits
- Troubleshooting
- Performance reviews

## Best Practices

### User Management

1. **Regular Reviews**: Review user accounts monthly
2. **Suspension vs Deletion**: Prefer suspension over deletion
3. **Document Actions**: Always provide reasons for suspensions
4. **Monitor Activity**: Watch for suspicious trading patterns
5. **Balance Adjustments**: Only adjust balances when necessary and document why

### Company Management

1. **Data Quality**: Verify company data before adding
2. **Regular Updates**: Keep company information current
3. **Deactivation**: Deactivate delisted or bankrupt companies
4. **Bulk Imports**: Use bulk import for adding multiple companies
5. **Price Data**: Ensure price data is updating correctly

### Dividend Management

1. **Advance Notice**: Create dividend announcements well before payment date
2. **Verify Dates**: Double-check all dates before creating
3. **Monitor Processing**: Check dividend processor logs on payment dates
4. **User Communication**: Ensure users receive dividend notifications

### System Monitoring

1. **Daily Checks**: Review system health daily
2. **API Limits**: Monitor API usage to avoid rate limits
3. **Performance**: Watch for slow queries and optimize
4. **Job Monitoring**: Ensure background jobs run successfully
5. **Alerts**: Respond promptly to system alerts

### Security

1. **Strong Passwords**: Use strong admin passwords
2. **Regular Audits**: Review audit logs regularly
3. **Access Control**: Limit admin access to necessary personnel
4. **Session Management**: Log out when not actively using admin features
5. **Suspicious Activity**: Investigate unusual patterns immediately

### Compliance

1. **Audit Trails**: Maintain complete audit logs
2. **Data Retention**: Follow data retention policies
3. **User Privacy**: Respect user data privacy
4. **Documentation**: Document all major actions
5. **Regular Backups**: Ensure database backups are current

## Troubleshooting

### Common Issues

**Users Can't Log In**:
- Check if account is suspended
- Verify email address is correct
- Check for system-wide authentication issues

**Orders Failing**:
- Check user wallet balance
- Verify stock symbol exists
- Check API connectivity
- Review transaction engine logs

**Dividends Not Processing**:
- Verify dividend processor job is running
- Check payment date is correct
- Review job execution logs
- Ensure users have holdings on record date

**Price Data Not Updating**:
- Check price updater job status
- Verify yfinance API connectivity
- Check API rate limits
- Review job execution logs

**System Performance Issues**:
- Check database performance metrics
- Review slow query log
- Monitor API response times
- Check server resources (CPU, memory)

## Emergency Procedures

### System Down

1. Check system health dashboard
2. Review error logs
3. Verify database connectivity
4. Check API status
5. Restart services if necessary
6. Notify users if extended downtime

### Data Corruption

1. Stop all transactions immediately
2. Assess extent of corruption
3. Restore from latest backup
4. Verify data integrity
5. Resume operations
6. Document incident

### Security Breach

1. Immediately suspend affected accounts
2. Change all admin passwords
3. Review audit logs for unauthorized access
4. Assess data exposure
5. Notify affected users
6. Implement additional security measures
7. Document incident and response

## Support and Resources

### Getting Help

- Technical Support: tech-support@example.com
- Security Issues: security@example.com
- Documentation: docs.example.com
- Admin Forum: forum.example.com/admin

### Additional Resources

- System Architecture Documentation
- API Documentation
- Database Schema Documentation
- Security Best Practices Guide
- Compliance Guidelines

---

**Version**: 1.0  
**Last Updated**: 2024  
**For**: Stock Portfolio Management Platform Administrators
