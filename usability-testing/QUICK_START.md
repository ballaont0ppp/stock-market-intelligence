# Usability Testing Quick Start Guide

## Get Started in 5 Minutes

This guide will help you quickly set up and start conducting usability tests.

## Step 1: Install (1 minute)

```bash
cd usability-testing
pip install -r requirements.txt
```

## Step 2: Start Application (1 minute)

```bash
# From project root
python run.py
```

Verify it's running: http://localhost:5000

## Step 3: Prepare Test Environment (2 minutes)

```bash
# Create test users (if not already done)
python scripts/seed_data.py

# Create results directory
mkdir -p usability-testing/results
```

## Step 4: Run Your First Test (1 minute)

```bash
cd usability-testing
python test_runner.py
```

Select option 1: "Run new testing session"

## That's It!

You're ready to conduct usability testing. Follow the on-screen prompts.

## Quick Reference

### Test Accounts
- testuser1@example.com / TestPass123!
- testuser2@example.com / TestPass123!

### Key URLs
- Home: http://localhost:5000
- Login: http://localhost:5000/login
- Dashboard: http://localhost:5000/dashboard

### Essential Commands

```bash
# Start test session
python test_runner.py

# View results
python test_runner.py
# Select option 2

# Generate report
python test_runner.py
# Select option 3
```

## Need More Help?

- Full documentation: [README.md](README.md)
- Setup guide: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- Testing procedures: [TESTING_PROCEDURES.md](TESTING_PROCEDURES.md)
- Recruitment guide: [PARTICIPANT_RECRUITMENT.md](PARTICIPANT_RECRUITMENT.md)

## Troubleshooting

**Application won't start?**
```bash
# Check if port 5000 is in use
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows
```

**No test users?**
```bash
python scripts/seed_data.py
```

**Recording not working?**
- Use OBS Studio (free): https://obsproject.com/
- Or use Zoom recording

## Next Steps

1. Read [PARTICIPANT_RECRUITMENT.md](PARTICIPANT_RECRUITMENT.md) to recruit participants
2. Review [TESTING_PROCEDURES.md](TESTING_PROCEDURES.md) for detailed procedures
3. Conduct your first test session
4. Analyze results and generate report
5. Implement improvements

## Support

Questions? Check the documentation or contact:
- Email: [your-email@example.com]
- Slack: #usability-testing

---

**Happy Testing! 🎉**
