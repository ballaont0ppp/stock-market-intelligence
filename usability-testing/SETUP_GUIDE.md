# Usability Testing Environment Setup Guide

## Overview

This guide explains how to set up the testing environment for conducting usability tests on the Stock Portfolio Management Platform.

## Prerequisites

- Python 3.8+
- MySQL 8.0+
- Web browser (Chrome, Firefox, Safari, or Edge)
- Internet connection
- Microphone for recording
- Screen recording software (optional)

## Environment Setup

### 1. Application Setup

#### Start the Application

```bash
# Navigate to project root
cd /path/to/stock-portfolio-platform

# Activate virtual environment
source stock_market_venv/bin/activate  # Linux/Mac
# OR
stock_market_venv\Scripts\activate  # Windows

# Start the application
python run.py
```

The application should be running at: `http://localhost:5000`

#### Verify Application is Running

Open a browser and navigate to:
- Homepage: `http://localhost:5000`
- Login: `http://localhost:5000/login`
- Register: `http://localhost:5000/register`

### 2. Test Data Setup

#### Create Test Users

Run the seed data script to create test users:

```bash
python scripts/seed_data.py
```

This creates:
- Admin user: `admin@example.com` / `Admin123!`
- Test users: `testuser1@example.com` through `testuser5@example.com` / `TestPass123!`

#### Verify Test Data

```bash
# Connect to MySQL
mysql -u root -p

# Use the database
USE stock_portfolio_db;

# Check users
SELECT user_id, email, full_name, is_admin FROM users;

# Check wallets
SELECT user_id, balance FROM wallets;

# Check companies
SELECT company_id, symbol, company_name FROM companies LIMIT 10;
```

### 3. Recording Tools Setup

#### Option 1: OBS Studio (Free)

1. Download from: https://obsproject.com/
2. Install and launch OBS
3. Add "Display Capture" source
4. Add "Audio Input Capture" for microphone
5. Click "Start Recording" when ready
6. Recordings saved to: `~/Videos/` (default)

#### Option 2: Zoom Recording

1. Start a Zoom meeting
2. Share your screen
3. Click "Record" button
4. Choose "Record on this Computer"
5. Recordings saved to: `~/Documents/Zoom/`

#### Option 3: Built-in Screen Recording

**Mac:**
- Press `Cmd + Shift + 5`
- Select recording area
- Click "Record"

**Windows 10/11:**
- Press `Win + G` (Game Bar)
- Click "Record" button
- Recordings saved to: `~/Videos/Captures/`

### 4. Browser Setup

#### Recommended: Chrome

1. Open Chrome
2. Install extensions (optional):
   - Screen recorder
   - Note-taking tool
3. Clear cache and cookies
4. Disable autofill for forms
5. Set zoom to 100%

#### Browser Console (for debugging)

- Press `F12` to open Developer Tools
- Monitor console for errors
- Check Network tab for API calls

### 5. Data Collection Setup

#### Install Python Dependencies

```bash
cd usability-testing
pip install -r requirements.txt
```

#### Create Results Directory

```bash
mkdir -p usability-testing/results
```

#### Test Data Collector

```python
# Test the data collector
python -c "from data_collector import UsabilityDataCollector; dc = UsabilityDataCollector(); print('Data collector ready!')"
```

## Testing Session Setup

### Pre-Session Checklist

**30 Minutes Before:**
- [ ] Start the application
- [ ] Verify all pages load correctly
- [ ] Test login with test account
- [ ] Clear browser cache
- [ ] Test recording software
- [ ] Prepare consent form
- [ ] Print task scenarios
- [ ] Prepare note-taking materials

**10 Minutes Before:**
- [ ] Open application in browser
- [ ] Start recording software (but don't record yet)
- [ ] Open data collection script
- [ ] Review test scenarios
- [ ] Prepare welcome script
- [ ] Test microphone levels

**When Participant Arrives:**
- [ ] Welcome participant
- [ ] Explain study purpose
- [ ] Obtain consent
- [ ] Start recording
- [ ] Begin session

### Session Environment

#### Physical Setup (In-Person)

- Quiet room with minimal distractions
- Comfortable seating
- Desk with computer
- Water/coffee available
- Clock visible (for timing)
- Notepad and pen for observer

#### Remote Setup (Zoom/Teams)

- Stable internet connection
- Zoom/Teams meeting link ready
- Screen sharing enabled
- Recording enabled
- Backup recording method
- Chat for communication

### Test Accounts

Use these accounts for testing:

| Email | Password | Wallet Balance | Holdings |
|-------|----------|----------------|----------|
| testuser1@example.com | TestPass123! | $100,000 | None |
| testuser2@example.com | TestPass123! | $50,000 | AAPL (10 shares) |
| testuser3@example.com | TestPass123! | $75,000 | GOOGL (5 shares) |
| testuser4@example.com | TestPass123! | $100,000 | None |
| testuser5@example.com | TestPass123! | $25,000 | Multiple holdings |

**Note:** For registration tasks, participants should create new accounts.

## Running Tests

### Start Test Runner

```bash
cd usability-testing
python test_runner.py
```

This launches an interactive menu:
1. Run new testing session
2. View results summary
3. Generate report
4. Export to CSV
5. Exit

### Manual Testing (Without Script)

If you prefer manual data collection:

1. Open `usability-testing/templates/data_collection_sheet.xlsx`
2. Print or use digitally
3. Record observations manually
4. Enter data later

## Troubleshooting

### Application Won't Start

**Issue:** `Address already in use`
```bash
# Find process using port 5000
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows
```

**Issue:** Database connection error
```bash
# Check MySQL is running
sudo systemctl status mysql  # Linux
brew services list  # Mac
net start MySQL  # Windows

# Verify credentials in .env file
cat .env | grep DB_
```

### Recording Issues

**Issue:** No audio in recording
- Check microphone permissions
- Test microphone in system settings
- Restart recording software

**Issue:** Screen not recording
- Check screen recording permissions
- Try different recording software
- Use Zoom as backup

### Browser Issues

**Issue:** Page not loading
- Clear cache: `Ctrl+Shift+Delete`
- Try incognito mode
- Try different browser
- Check console for errors

**Issue:** Forms not submitting
- Check browser console
- Verify CSRF token
- Check network tab
- Try different browser

### Participant Issues

**Issue:** Participant can't hear you
- Check audio settings
- Restart Zoom/Teams
- Use phone as backup

**Issue:** Participant's screen frozen
- Ask them to refresh
- Check their internet
- Reschedule if needed

## Data Management

### During Session

- Save recordings immediately
- Backup to cloud storage
- Name files consistently: `session_P01_20240115.mp4`
- Take written notes as backup

### After Session

- Transfer recordings to secure storage
- Run data collector to save results
- Backup JSON files
- Delete local recordings after backup

### File Organization

```
usability-testing/
├── results/
│   ├── session_P01_20240115.json
│   ├── session_P02_20240115.json
│   └── ...
├── recordings/
│   ├── session_P01_20240115.mp4
│   ├── session_P02_20240115.mp4
│   └── ...
├── notes/
│   ├── session_P01_notes.txt
│   ├── session_P02_notes.txt
│   └── ...
└── reports/
    ├── usability_report.md
    └── usability_results.csv
```

## Security and Privacy

### Data Protection

- Use participant IDs, not names
- Encrypt recordings
- Secure storage location
- Delete after analysis (6 months)
- No personal information in filenames

### Access Control

- Limit access to research team only
- Use password-protected folders
- Don't share recordings publicly
- Anonymize all data in reports

## Post-Session Cleanup

### After Each Session

- [ ] Stop recording
- [ ] Save and backup files
- [ ] Reset test environment
- [ ] Clear browser data
- [ ] Reset test accounts (if needed)
- [ ] Prepare for next session

### After All Sessions

- [ ] Analyze all data
- [ ] Generate final report
- [ ] Archive recordings
- [ ] Delete temporary files
- [ ] Send thank you emails
- [ ] Process compensation

## Resources

### Documentation
- Test scenarios: `test_scenarios.py`
- Data collector: `data_collector.py`
- Configuration: `config.py`

### Templates
- Consent form: `CONSENT_FORM.md`
- Recruitment guide: `PARTICIPANT_RECRUITMENT.md`
- Data collection sheet: `templates/data_collection_sheet.xlsx`

### Tools
- OBS Studio: https://obsproject.com/
- Zoom: https://zoom.us/
- Google Forms: https://forms.google.com/

## Support

For technical issues during testing:
- Email: [support@example.com]
- Phone: [support-phone]
- Slack: #usability-testing

## Quick Reference

### Essential Commands

```bash
# Start application
python run.py

# Start test runner
python usability-testing/test_runner.py

# Generate report
python -c "from data_collector import UsabilityDataCollector; dc = UsabilityDataCollector(); dc.generate_report()"

# Export to CSV
python -c "from data_collector import UsabilityDataCollector; dc = UsabilityDataCollector(); dc.export_to_csv()"
```

### Essential URLs

- Application: http://localhost:5000
- Login: http://localhost:5000/login
- Dashboard: http://localhost:5000/dashboard
- Portfolio: http://localhost:5000/portfolio
- Orders: http://localhost:5000/orders

### Test Credentials

- Test User: testuser1@example.com / TestPass123!
- Admin: admin@example.com / Admin123!
