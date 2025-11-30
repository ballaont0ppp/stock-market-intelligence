# Usability Testing Procedures

## Overview

This document provides detailed procedures for conducting usability testing sessions (Tasks 23.2-23.5).

## Task 23.2: Conduct Exploratory Usability Testing

### Purpose
Open-ended user exploration to identify usability issues and gather qualitative feedback.

### Duration
30 minutes per participant

### Procedure

#### 1. Welcome and Setup (5 minutes)
- Welcome participant
- Explain study purpose
- Review and sign consent form
- Start recording
- Make participant comfortable

#### 2. Introduction Script
```
"Thank you for participating today. We're testing a stock portfolio management 
platform and want to understand how people interact with it.

There are no right or wrong answers - we're testing the system, not you. 
Please think aloud as you explore, sharing what you're thinking, what you're 
looking for, and any confusion you experience.

Feel free to explore the application however you'd like. I'll be taking notes 
but won't be able to help you navigate. This helps us understand what's 
intuitive and what needs improvement.

Do you have any questions before we begin?"
```

#### 3. Exploratory Session (20 minutes)
- Give participant the URL: http://localhost:5000
- Ask them to explore freely
- Encourage think-aloud protocol
- Take detailed notes on:
  - First impressions
  - Navigation patterns
  - Confusion points
  - Positive reactions
  - Suggestions
  - Pain points

#### 4. Probing Questions (During exploration)
- "What are you thinking right now?"
- "What are you looking for?"
- "What do you expect to happen when you click that?"
- "Is this what you expected?"
- "How would you describe this to a friend?"

#### 5. Wrap-up Questions (5 minutes)
- "What was your overall impression?"
- "What did you like most?"
- "What frustrated you the most?"
- "What would you change?"
- "Would you use this platform? Why or why not?"

### Data to Collect
- [ ] First impressions (written notes)
- [ ] Navigation patterns (screen recording)
- [ ] Confusion points (timestamps and descriptions)
- [ ] Positive feedback (quotes)
- [ ] Pain points (specific issues)
- [ ] Suggestions (improvement ideas)
- [ ] Overall sentiment (positive/neutral/negative)

### Success Criteria
- Participant explores for full 20 minutes
- Think-aloud protocol maintained
- At least 5 observations recorded
- Both positive and negative feedback gathered

---

## Task 23.3: Conduct Task-Based Usability Testing

### Purpose
Test specific tasks with time targets to measure usability metrics.

### Duration
30-45 minutes per participant

### Procedure

#### 1. Welcome and Setup (5 minutes)
- Same as exploratory testing
- Explain task-based approach

#### 2. Introduction Script
```
"Today you'll complete specific tasks on the platform. I'll give you a scenario 
and ask you to complete it. Please think aloud as you work.

I'll be timing each task, but don't rush - work at your natural pace. If you 
get stuck, that's valuable feedback for us.

Remember, we're testing the system, not you. There are no wrong answers."
```

#### 3. Task Execution

For each task (TASK-1 through TASK-8):

**Before Task:**
- Read scenario aloud
- Ensure participant understands
- Answer clarifying questions
- Start timer

**During Task:**
- Observe silently
- Take notes on:
  - Hesitations
  - Wrong paths taken
  - Errors encountered
  - Recovery attempts
  - Expressions of confusion
- Only intervene if completely stuck (>2 minutes)

**After Task:**
- Stop timer
- Record completion time
- Ask: "Was the task completed successfully?"
- Ask: "How many errors did you encounter?"
- Ask: "Any observations or feedback?"
- Record data in test runner

**Debrief Questions:**
- "How difficult was that task?" (1-5 scale)
- "What made it easy or difficult?"
- "What would have helped?"

#### 4. Task List

Execute these tasks in order:

1. **TASK-1: New User Registration** (Target: 3 min)
   - Scenario: "Create a new account on this platform"
   - Success: Account created, user logged in

2. **TASK-2: First Stock Purchase** (Target: 5 min)
   - Scenario: "Buy 10 shares of Apple (AAPL)"
   - Success: Order placed, wallet updated

3. **TASK-3: Portfolio Review** (Target: 30 sec)
   - Scenario: "Check your current holdings and portfolio value"
   - Success: Portfolio page viewed, values understood

4. **TASK-4: Sell Stock** (Target: 2 min)
   - Scenario: "Sell 5 shares of the stock you just bought"
   - Success: Sell order placed, holdings updated

5. **TASK-5: Report Generation** (Target: 1 min)
   - Scenario: "Generate a transaction report for the past month"
   - Success: Report generated and displayed

6. **TASK-6: View Predictions** (Target: 1.5 min)
   - Scenario: "Get price predictions for Microsoft (MSFT)"
   - Success: Predictions displayed with charts

7. **TASK-7: Update Profile** (Target: 1.5 min)
   - Scenario: "Update your investment goals in your profile"
   - Success: Profile updated and saved

8. **TASK-8: Check Notifications** (Target: 30 sec)
   - Scenario: "View your notifications"
   - Success: Notifications viewed

### Data to Collect
For each task:
- [ ] Start time
- [ ] End time
- [ ] Duration (seconds)
- [ ] Success (yes/no)
- [ ] Error count
- [ ] Error descriptions
- [ ] Observations
- [ ] Difficulty rating (1-5)

### Success Criteria
- All 8 tasks attempted
- At least 90% success rate
- Average times within targets
- Detailed notes for each task

---

## Task 23.4: Measure Usability Metrics

### Purpose
Calculate and analyze usability metrics from collected data.

### Procedure

#### 1. Data Aggregation

After completing all testing sessions, aggregate data:

```bash
cd usability-testing
python test_runner.py
# Select option 2: View results summary
```

#### 2. Calculate Metrics

**Task Success Rate:**
```
Success Rate = (Successful Tasks / Total Tasks) × 100%
Target: > 90%
```

**Average Time on Task:**
```
For each task:
  Average Time = Sum of all times / Number of participants
  
Compare to targets:
  TASK-1: 180s
  TASK-2: 300s
  TASK-3: 30s
  TASK-4: 120s
  TASK-5: 60s
```

**Error Rate:**
```
Error Rate = (Total Errors / Total Actions) × 100%
Target: < 5%
```

**User Satisfaction:**
```
Average Satisfaction = Sum of all Q5 scores / Number of participants
Target: > 4.0 / 5.0
```

**Learnability:**
```
Learnability = Average time for complete workflow (LEARN-1)
Target: < 600s (10 minutes)
```

#### 3. Statistical Analysis

For each metric:
- Calculate mean
- Calculate median
- Calculate standard deviation
- Identify outliers
- Compare to targets

#### 4. Generate Report

```bash
python test_runner.py
# Select option 3: Generate report
```

Review the generated report at:
`usability-testing/results/usability_report.md`

#### 5. Identify Patterns

Analyze the data to identify:
- **Common failure points**: Tasks with low success rates
- **Time bottlenecks**: Tasks taking longer than target
- **Frequent errors**: Most common error types
- **User segments**: Differences by experience level
- **Correlation**: Relationship between metrics

### Data to Collect
- [ ] Task success rates (per task and overall)
- [ ] Average task times (per task)
- [ ] Error rates (per task and overall)
- [ ] Satisfaction scores (per question)
- [ ] Learnability metrics
- [ ] Statistical analysis (mean, median, std dev)
- [ ] Comparison to targets (pass/fail)

### Success Criteria
- All metrics calculated
- Statistical analysis complete
- Report generated
- Targets compared
- Patterns identified

---

## Task 23.5: Implement Usability Improvements

### Purpose
Fix identified usability issues and improve user experience based on testing results.

### Procedure

#### 1. Prioritize Issues

Review the usability report and prioritize issues by:
- **Severity**: How much it impacts users
- **Frequency**: How often it occurs
- **Impact**: Effect on task success
- **Effort**: Time to fix

Use this matrix:

| Priority | Severity | Frequency | Action |
|----------|----------|-----------|--------|
| P0 - Critical | High | High | Fix immediately |
| P1 - High | High | Medium | Fix in current sprint |
| P2 - Medium | Medium | High | Fix in next sprint |
| P3 - Low | Low | Low | Backlog |

#### 2. Create Improvement Plan

For each high-priority issue:

**Issue Template:**
```
Issue ID: UI-001
Title: Stock search autocomplete not obvious
Severity: High
Frequency: 8/10 participants
Impact: Delays task completion by 30s average
Current Behavior: Search box has no placeholder or icon
Desired Behavior: Clear search icon and placeholder text
Proposed Solution: Add magnifying glass icon and "Search stocks..." placeholder
Effort: 1 hour
Priority: P1
```

#### 3. Implement Improvements

Common improvement categories:

**A. Navigation Improvements**
- Make menu items more descriptive
- Add breadcrumbs
- Improve link visibility
- Add shortcuts

**B. Form Improvements**
- Add clear labels
- Improve placeholder text
- Add inline validation
- Show password requirements
- Add helpful tooltips

**C. Feedback Improvements**
- Enhance success messages
- Improve error messages
- Add loading indicators
- Show progress feedback

**D. Visual Improvements**
- Increase button contrast
- Improve color coding
- Add icons for clarity
- Improve spacing

**E. Help Documentation**
- Add contextual help
- Create tooltips
- Add FAQ section
- Improve error recovery guidance

#### 4. Implementation Examples

**Example 1: Improve Stock Search**
```html
<!-- Before -->
<input type="text" name="symbol">

<!-- After -->
<div class="search-container">
  <i class="icon-search"></i>
  <input type="text" 
         name="symbol" 
         placeholder="Search stocks (e.g., AAPL, GOOGL)..."
         autocomplete="off"
         aria-label="Search for stocks">
  <div class="search-suggestions" id="suggestions"></div>
</div>
```

**Example 2: Improve Error Messages**
```python
# Before
flash('Error', 'error')

# After
flash('Insufficient funds. You need $1,250.00 but only have $1,000.00 in your wallet. Please deposit more funds or reduce your order quantity.', 'error')
```

**Example 3: Add Sell Button to Portfolio**
```html
<!-- Add to portfolio holdings table -->
<td>
  <button class="btn btn-sm btn-danger" 
          onclick="sellStock('{{ holding.company.symbol }}', {{ holding.quantity }})">
    <i class="icon-sell"></i> Sell
  </button>
</td>
```

#### 5. Test Improvements

After implementing:
- [ ] Test each improvement manually
- [ ] Verify it solves the issue
- [ ] Check for new issues introduced
- [ ] Test on different browsers
- [ ] Test on mobile devices

#### 6. Validate with Users

Conduct follow-up testing:
- Test with 2-3 participants
- Focus on improved areas
- Measure improvement in metrics
- Gather feedback on changes

#### 7. Document Changes

Create a summary document:

```markdown
# Usability Improvements Summary

## Issues Fixed

### UI-001: Stock Search Visibility
- **Issue**: Search not obvious (8/10 participants)
- **Solution**: Added search icon and placeholder
- **Result**: 100% found search in follow-up testing
- **Files Changed**: templates/orders/buy.html, static/css/components.css

### UI-002: Sell Button Location
- **Issue**: Sell button hard to find (6/10 participants)
- **Solution**: Added sell button to portfolio table
- **Result**: Average time reduced from 120s to 45s
- **Files Changed**: templates/portfolio/index.html

[Continue for all issues...]

## Metrics Improvement

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Task Success Rate | 88% | 95% | +7% |
| Average Task Time | 165s | 142s | -14% |
| Error Rate | 6% | 3% | -50% |
| Satisfaction | 3.8/5 | 4.3/5 | +13% |
```

### Data to Collect
- [ ] List of all issues identified
- [ ] Priority ranking
- [ ] Implementation plan
- [ ] Code changes made
- [ ] Test results
- [ ] Follow-up testing results
- [ ] Metrics improvement
- [ ] Documentation

### Success Criteria
- All P0 and P1 issues fixed
- Improvements tested and validated
- Metrics show improvement
- Documentation complete
- Follow-up testing confirms fixes

---

## General Best Practices

### During All Testing

**Do:**
- ✅ Stay neutral and encouraging
- ✅ Take detailed notes
- ✅ Record everything
- ✅ Thank participants
- ✅ Follow ethical guidelines
- ✅ Be patient

**Don't:**
- ❌ Lead participants
- ❌ Explain how things work
- ❌ Defend design decisions
- ❌ Interrupt during tasks
- ❌ Show frustration
- ❌ Skip consent

### Think-Aloud Prompts

Use these prompts to encourage thinking aloud:
- "What are you thinking?"
- "What are you looking for?"
- "What do you expect to happen?"
- "Why did you click that?"
- "Is this what you expected?"

### Handling Difficult Situations

**Participant is stuck:**
- Wait 1-2 minutes
- Ask: "What are you trying to do?"
- If still stuck: "Would you like a hint?"
- Last resort: "Let's move to the next task"

**Participant is frustrated:**
- Acknowledge: "I can see this is frustrating"
- Reassure: "This is valuable feedback"
- Offer break: "Would you like to take a short break?"

**Technical issues:**
- Have backup device ready
- Use backup recording method
- Reschedule if necessary

### Data Quality

Ensure high-quality data by:
- Recording all sessions
- Taking detailed notes
- Entering data immediately
- Backing up files
- Reviewing for completeness

---

## Timeline

### Recommended Schedule

**Week 1: Exploratory Testing**
- Day 1-2: Sessions 1-5
- Day 3: Analyze results
- Day 4-5: Sessions 6-10

**Week 2: Task-Based Testing**
- Day 1-2: Sessions 1-5
- Day 3: Analyze results
- Day 4-5: Sessions 6-10

**Week 3: Analysis and Improvements**
- Day 1: Calculate metrics
- Day 2: Generate reports
- Day 3: Prioritize issues
- Day 4-5: Implement improvements

**Week 4: Validation**
- Day 1-2: Follow-up testing
- Day 3: Final analysis
- Day 4: Documentation
- Day 5: Present findings

---

## Deliverables

### Required Deliverables

1. **Session Recordings** (all sessions)
2. **Session Data** (JSON files for each session)
3. **Usability Report** (usability_report.md)
4. **CSV Export** (usability_results.csv)
5. **Improvement Plan** (prioritized list of issues)
6. **Implementation Summary** (changes made)
7. **Final Presentation** (key findings and recommendations)

### Optional Deliverables

1. **Video Highlights** (compilation of key moments)
2. **User Personas** (based on participant demographics)
3. **Journey Maps** (user flows through the application)
4. **Heatmaps** (if using Hotjar or similar)
5. **Comparison Report** (before/after metrics)

---

## Resources

- Test Runner: `python test_runner.py`
- Data Collector: `data_collector.py`
- Test Scenarios: `test_scenarios.py`
- Configuration: `config.py`
- Setup Guide: `SETUP_GUIDE.md`
- Recruitment Guide: `PARTICIPANT_RECRUITMENT.md`

---

**Ready to conduct testing?** Start with Task 23.2 (Exploratory Testing) and follow the procedures above!
