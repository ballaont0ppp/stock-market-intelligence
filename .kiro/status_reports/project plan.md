# Project Plan

## 1. Project Overview

**Project Title:** Stock Portfolio Management and Prediction Platform  
**Purpose:** Provide an end‑to‑end share‑market management and prediction system that lets users manage virtual portfolios, track funds and dividends, and use machine learning to forecast stock prices.

The system combines:
- Portfolio and fund management
- Simulated buy/sell transactions
- Dividend tracking
- ML‑based price prediction (LSTM and baselines)
- Admin monitoring and reporting

## 2. Objectives

- **O1 &mdash; Portfolio & Fund Management:** Enable users to maintain customer and company profiles, manage holdings, and track cash and dividends.
- **O2 &mdash; Trading Simulation:** Support safe, simulated buy/sell orders with proper validation and transaction history.
- **O3 &mdash; Prediction Engine:** Integrate ML models (LSTM, regression) for future price forecasts integrated into the UI.
- **O4 &mdash; Reporting & Monitoring:** Provide dashboards, billing, and admin tools for monitoring activity and performance.
- **O5 &mdash; Quality & Robustness:** Deliver a secure, tested, and well‑documented application suitable for academic submission and demonstration.

## 3. Scope Summary

**In scope (from draft report):**
- User registration, login, and profile management
- Company and stock data storage and updates
- Fund management and virtual wallet
- Stock buy/sell, portfolio tracking, and dividend payout
- Price prediction using ML models (LSTM + baselines)
- Billing, transaction summaries, and basic reporting
- Broker management and admin monitoring dashboard

**Out of scope:**
- Real‑money trading and integration with live exchanges
- Third‑party broker/trading APIs
- Real‑time web scraping from external financial sites

## 4. Work Breakdown (by Roadmap Tasks)

### 4.1 End‑Semester Work (Tasks 1–15)

**Completed (Tasks 1–6):**
1. Project setup and database foundation  
2. Authentication system implementation  
3. Portfolio management system  
4. Stock repository and data management  
5. Transaction engine for buy/sell orders  
6. ML prediction service integration  

**Remaining (Tasks 7–15):**
7. Sentiment analysis engine  
8. Dividend management system  
9. Admin service and dashboard  
10. Background jobs and scheduling  
11. Notification system  
12. Reporting system  
13. Clean minimalist UI implementation  
14. Error handling and validation  
15. Security implementation  

### 4.2 Final‑Semester Work (Tasks 16–30)

16. Logging and monitoring  
17. Testing implementation  
18. Deployment preparation  
19. Final integration and testing  
20. Documentation and cleanup  
21. Comprehensive performance testing  
22. Comprehensive security testing  
23. Usability testing  
24. Compatibility testing  
25. Accessibility testing  
26. Regression testing suite  
27. Recovery and resilience testing  
28. Acceptance testing  
29. Test automation and CI/CD integration  
30. Testing documentation and knowledge transfer  

## 5. Timeline and Gantt Chart

The roadmap defines a week‑by‑week plan (Weeks 6–21). The Gantt‑style table below summarizes when each task group is planned.

**Legend:** `█` = planned work window

### 5.1 High‑Level Weekly Plan (Weeks 6–21)

| Task Group                                    | W6 | W7 | W8 | W9 | W10 | W11 | W12 | W13 | W14 | W15 | W16 | W17 | W18 | W19 | W20 | W21 |
|----------------------------------------------|:--:|:--:|:--:|:--:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 7–9 Sentiment, Dividend, Admin               | █  | █  |    |    |     |     |     |     |     |     |     |     |     |     |     |     |
| 10–12 Jobs, Notifications, Reports           |    |    | █  | █  |     |     |     |     |     |     |     |     |     |     |     |     |
| 13–15 UI, Error Handling, Security           |    |    |    |    | █   | █   |     |     |     |     |     |     |     |     |     |     |
| 16–18 Logging, Testing, Deployment Prep      |    |    |    |    |     |     | █   | █   |     |     |     |     |     |     |     |     |
| 19–21 Integration, Docs, Performance         |    |    |    |    |     |     |     |     | █   | █   |     |     |     |     |     |     |
| 22–24 Security, Usability, Compatibility     |    |    |    |    |     |     |     |     |     |     | █   | █   |     |     |     |     |
| 25–27 Accessibility, Regression, Recovery    |    |    |    |    |     |     |     |     |     |     |     |     | █   | █   |     |     |
| 28–30 Acceptance, Automation, Documentation  |    |    |    |    |     |     |     |     |     |     |     |     |     |     | █   | █   |

### 5.2 Milestones

- **M1 &mdash; End‑Semester Completion:** 15/30 tasks completed (Tasks 1–15).  
  Target: End of current semester.
- **M2 &mdash; Final Integration:** Tasks 16–21 done; full system integrated and documented.  
  Target: By end of Weeks 14–15.
- **M3 &mdash; Quality & Testing Complete:** Tasks 22–30 done; test suites, automation, and documentation finalized.  
  Target: End of final year (Weeks 20–21 window).

## 6. Risks and Mitigations (Brief)

- **R1 &mdash; Model complexity and training time**  
  *Mitigation:* Keep LSTM architecture lightweight; use pre‑prepared datasets and offline training.

- **R2 &mdash; Scope creep in UI and analytics**  
  *Mitigation:* Prioritize core flows: registration, portfolio, trades, prediction, and basic dashboards.

- **R3 &mdash; Testing and performance backlog**  
  *Mitigation:* Reserve explicit weeks (16–21) for structured testing, regression, and performance work as per roadmap.

## 7. Deliverables

- **D1:** Functional web application (backend, frontend, DB) with user, fund, and portfolio management.
- **D2:** Integrated ML prediction module (LSTM + baselines) with visual outputs.
- **D3:** Admin dashboard for monitoring, broker management, and reporting.
- **D4:** Documentation set: user guide, technical design, and testing documentation.
- **D5:** Final project report and presentation materials.
