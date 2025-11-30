# Usability Testing Framework

## Overview

This directory contains a comprehensive usability testing framework for the Stock Portfolio Management Platform. The framework includes tools, scripts, and documentation for conducting, recording, and analyzing usability tests.

## Purpose

The usability testing framework helps us:
- Evaluate user experience and interface design
- Identify usability issues and pain points
- Measure task completion rates and times
- Gather user satisfaction feedback
- Validate design decisions
- Prioritize improvements

## Usability Metrics

We measure the following key metrics:

| Metric | Target | Description |
|--------|--------|-------------|
| Task Success Rate | > 90% | Percentage of tasks completed successfully |
| Time on Task | Varies | Time to complete specific tasks |
| Error Rate | < 5% | Percentage of user actions resulting in errors |
| User Satisfaction | > 4/5 | Average satisfaction score (Likert scale) |
| Learnability | < 10 min | Time for new users to become proficient |

## Test Types

### 1. Exploratory Testing
- Open-ended user exploration
- Identify unexpected issues
- Gather qualitative feedback
- Duration: 30 minutes

### 2. Task-Based Testing
- Specific tasks with time targets
- Measure completion rates
- Identify workflow issues
- Duration: 30-45 minutes

### 3. Learnability Testing
- Complete workflow from start to finish
- Measure time to proficiency
- Assess learning curve
- Duration: 10-15 minutes

## Directory Structure

```
usability-testing/
├── README.md                      # This file
├── SETUP_GUIDE.md                 # Environment setup instructions
├── PARTICIPANT_RECRUITMENT.md     # Recruitment guide
├── CONSENT_FORM.md                # Participant consent form
├── config.py                      # Configuration and metrics
├── test_scenarios.py              # Test scenario definitions
├── data_collector.py              # Data collection and analysis
├── test_runner.py                 # Interactive test runner
├── requirements.txt               # Python dependencies
├── results/                       # Test results (JSON, CSV)
├── recordings/                    # Session recordings
├── notes/                         # Observer notes
├── reports/                       # Generated reports
└── templates/                     # Email and form templates
```

## Quick Start

### 1. Install Dependencies

```bash
cd usability-testing
pip install -r requirements.txt
```

### 2. Set Up Test Environment

Follow the instructions in `SETUP_GUIDE.md`:
- Start the application
- Create test accounts
- Set up recording tools
- Verify everything works

### 3. Recruit Participants

Follow the guide in `PARTICIPANT_RECRUITMENT.md`:
- Create screening survey
- Select 5-10 participants
- Schedule sessions
- Send confirmations

### 4. Conduct Testing

Run the interactive test runner:

```bash
python test_runner.py
```

Or conduct tests manually using the scenarios in `test_scenarios.py`.

### 5. Analyze Results

Generate reports and analyze data:

```bash
# View summary
python test_runner.py
# Select option 2: View results summary

# Generate report
python test_runner.py
# Select option 3: Generate report

# Export to CSV
python test_runner.py
# Select option 4: Export to CSV
```

## Test Scenarios

### Task-Based Scenarios

| Task ID | Task Name | Target Time | Description |
|---------|-----------|-------------|-------------|
| TASK-1 | New User Registration | 3 min | Create a new account |
| TASK-2 | First Stock Purchase | 5 min | Buy first stock |
| TASK-3 | Portfolio Review | 30 sec | View holdings |
| TASK-4 | Sell Stock | 2 min | Sell shares |
| TASK-5 | Report Generation | 1 min | Generate transaction report |
| TASK-6 | View Predictions | 1.5 min | Get ML predictions |
| TASK-7 | Update Profile | 1.5 min | Update user profile |
| TASK-8 | Check Notifications | 30 sec | View notifications |

### Success Criteria

Each task has specific success criteria defined in `test_scenarios.py`. Tasks are considered successful when:
- All steps completed
- Correct outcome achieved
- No critical errors encountered
- Completed within target time (for time-sensitive tasks)

## Data Collection

### Automated Collection

The `data_collector.py` script automatically collects:
- Task completion times
- Success/failure status
- Error counts and descriptions
- User observations
- Satisfaction scores
- Open-ended feedback

### Manual Collection

For manual data collection:
1. Use the data collection sheet template
2. Record observations in real-time
3. Enter data into the system later
4. Backup with written notes

## Analysis and Reporting

### Metrics Calculated

- **Task Success Rate**: Percentage of successfully completed tasks
- **Average Task Times**: Mean time for each task across all participants
- **Error Rate**: Errors per task or per action
- **Satisfaction Scores**: Average Likert scale responses
- **Common Issues**: Most frequently encountered problems

### Report Generation

The framework generates:
- **Summary Report** (`usability_report.md`): Executive summary with key findings
- **CSV Export** (`usability_results.csv`): Raw data for further analysis
- **Session Files** (JSON): Individual session data

### Sample Report Structure

```markdown
# Usability Testing Report

## Executive Summary
- Total Sessions: 10
- Task Success Rate: 92%
- Error Rate: 3%
- Average Satisfaction: 4.2/5

## Task Performance
| Task | Avg Time | Target | Status |
|------|----------|--------|--------|
| TASK-1 | 165s | 180s | ✅ Pass |
| TASK-2 | 285s | 300s | ✅ Pass |
...

## Common Issues
1. Stock search autocomplete not obvious (8 occurrences)
2. Sell button hard to find (6 occurrences)
...

## Recommendations
1. Improve stock search visibility
2. Add sell button to portfolio page
...
```

## Best Practices

### Before Testing

- [ ] Test all equipment and software
- [ ] Prepare test environment
- [ ] Review test scenarios
- [ ] Print consent forms
- [ ] Prepare welcome script
- [ ] Have backup plans ready

### During Testing

- [ ] Make participant comfortable
- [ ] Explain think-aloud protocol
- [ ] Don't help unless necessary
- [ ] Take detailed notes
- [ ] Record everything
- [ ] Stay neutral and encouraging

### After Testing

- [ ] Thank participant
- [ ] Save and backup recordings
- [ ] Enter data immediately
- [ ] Send compensation
- [ ] Prepare for next session
- [ ] Review and improve process

## Think-Aloud Protocol

Encourage participants to:
- Say what they're thinking
- Describe what they're looking for
- Explain their actions
- Share confusion or frustration
- Suggest improvements

**Example prompts:**
- "What are you thinking right now?"
- "What are you looking for?"
- "What do you expect to happen?"
- "Is this what you expected?"

## Common Pitfalls to Avoid

### Don't:
- ❌ Lead the participant
- ❌ Explain how things work
- ❌ Defend design decisions
- ❌ Interrupt during tasks
- ❌ Show frustration
- ❌ Skip the consent form

### Do:
- ✅ Let participants struggle (within reason)
- ✅ Ask open-ended questions
- ✅ Stay neutral
- ✅ Take detailed notes
- ✅ Thank participants
- ✅ Follow ethical guidelines

## Ethical Considerations

- Obtain informed consent
- Protect participant privacy
- Allow withdrawal at any time
- Store data securely
- Anonymize all data
- Delete recordings after analysis
- Follow GDPR/privacy laws

## Troubleshooting

### Technical Issues

**Application not responding:**
- Restart the application
- Check database connection
- Review error logs
- Have backup environment ready

**Recording failed:**
- Use backup recording method
- Take detailed written notes
- Reschedule if necessary

**Participant technical issues:**
- Be patient and helpful
- Switch to backup device
- Reschedule if needed

### Participant Issues

**Participant too nervous:**
- Reassure them
- Start with easy tasks
- Build rapport first
- Take breaks if needed

**Participant too experienced:**
- Still valuable feedback
- Focus on expert insights
- Ask for comparisons
- Gather advanced feature ideas

## Resources

### Documentation
- [Setup Guide](SETUP_GUIDE.md)
- [Recruitment Guide](PARTICIPANT_RECRUITMENT.md)
- [Consent Form](CONSENT_FORM.md)

### Tools
- [OBS Studio](https://obsproject.com/) - Free screen recording
- [Zoom](https://zoom.us/) - Remote testing
- [Google Forms](https://forms.google.com/) - Surveys
- [Hotjar](https://www.hotjar.com/) - Heatmaps and recordings

### Further Reading
- Nielsen Norman Group: https://www.nngroup.com/
- Usability.gov: https://www.usability.gov/
- UX Collective: https://uxdesign.cc/

## Support

For questions or issues:
- Email: [your-email@example.com]
- Slack: #usability-testing
- Documentation: See guides in this directory

## Contributing

To improve this framework:
1. Test the framework yourself
2. Identify gaps or issues
3. Suggest improvements
4. Update documentation
5. Share learnings with team

## Version History

- **v1.0** (2024-01-15): Initial framework
  - Basic test scenarios
  - Data collection tools
  - Analysis scripts
  - Documentation

## License

Internal use only. Do not distribute outside the organization.

---

**Ready to start testing?** Follow the [Setup Guide](SETUP_GUIDE.md) to get started!
