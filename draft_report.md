**1. Problem Statement**

The financial market generates a massive volume of data every second, making it difficult for individual investors to analyze and make timely decisions. Existing systems often focus on either market tracking or basic trading but lack intelligent forecasting and integrated portfolio management features.

The proposed system aims to provide a Share Market Management and Prediction System that integrates customer profiles, stock data, and predictive analytics to help users make informed investment decisions.

The system will simplify buy/sell transactions, track funds and dividends, and use machine learning algorithms to predict future stock trends.

**2. Scope**

**In Scope:**

· User registration, login, and customer profile management.

· Company and stock data storage and updates.

· Fund tracking and virtual wallet for simulated trading.

· Stock buy/sell and portfolio management.

· Dividend management for invested stocks.

· Price prediction using regression-based models.
  
**Methods:**
We use an LSTM neural network as the primary predictive model. For baseline comparison, we optionally include a classical ARIMA model and a linear regression model.

· Billing and transaction report generation.

· Broker management and monitoring dashboard for admin.

**Out of Scope:**

· Real-time trading on live exchanges.

· Integration with third-party trading APIs.

· Real-money transactions.

· External data scraping from financial websites.

**Intended Users:**

· Students or researchers are studying stock prediction.

· Amateur investors learning market behavior.

· Administrators managing datasets and users.

**3. Literature Survey**

| No. | Author(s) / Year | Method / Algorithm | Key Findings | Limitations |
| --- | --- | --- | --- | --- |
| 1   | Ko & Chang (2021) | BERT \+ LSTM; price history \+ forum sentiment | Technical \+ textual data raise forecast accuracy | Taiwan-only stocks; forum noise |
| 2   | Shimaa Ouf et al. (2024) | LSTM vs. XGBoost \+ Twitter sentiment | Twitter sentiment lifts AAPL, GOOGL, TSLA forecasts; XGBoost \> LSTM here | Short horizon; three stocks only |
| 3   | Darapaneni et al. (2022) | LSTM \+ sentiment \+ macro (oil, gold, USD) | Macro features \+ sentiment help Indian market prediction | Single country; small universe |
| 4   | Gupta et al. (2022) | HiSA-SMFM: LSTM with historical & sentiment fusion | Clear gain from hybrid historical-sentiment signals | Reduced dataset; generalisability open |
| 5   | Shahbandari et al. (2024) | CNN+LSTM \+ social-media sentiment \+ candlestick | Multi-modal data (sentiment \+ tech) cut error | Social signal noisy; heavy architecture |
| 6   | Journal of Big Data (2025) | VMD–TMFG–LSTM (feature decomposition) | Signal decomposition \+ LSTM sharply↓ RMSE/MAE | Complex pipeline; no sentiment used |

**4. Gap Analysis & Motivation**

| Observed Gap | Evidence from the Six Papers | Implication |
| --- | --- | --- |
| **Narrow prediction focus** | Ko & Chang (2021) & Ouf et al. (2024) improve price forecasts with sentiment but stop at prediction only. | No end‑to‑end workflow for portfolio or fund management. |
| **Sparse real‑time context** | Darapaneni et al. (2022) add static macro variables; Gupta et al. (2022) fuse sentiment & history but ignore regime shifts or asset inter‑dependencies. | Models miss dynamic market conditions that affect co‑movements. |
| **Heavy computational demand** | Shahbandari et al. (2024) (CNN‑LSTM) and Journal of Big Data (2025) (VMD‑TMFG‑LSTM) achieve high accuracy but need large datasets & intensive training. | Infeasible for small‑scale investors or rapid prototyping. |
| **Low interpretability & user support** | All six studies present black‑box models with little explanation or visual feedback for users. | Limits adoption by non‑experts and hampers decision‑making. |

**Motivation**

To close these gaps, the proposed Share‑Market Management & Prediction System will:

1. **Offer a lightweight, modular LSTM core** that retains strong accuracy while remaining computationally affordable.
2. **Combine sentiment, technical, and fundamental indicators** (including real‑time macro data) to capture both short‑term moves and broader market regimes.
3. **Embed the predictor in a full‑stack management platform** featuring user profiles, fund allocation, buy/sell simulation, dividend tracking, and dashboards.
4. **Provide explainable visualizations** (feature importance, prediction confidence, portfolio impact) to make the system accessible to students, small investors, and prototype developers.

By integrating prediction with actionable management tools and transparent interfaces, the system advances beyond isolated forecasting models toward a practical, research‑ready market‑decision support solution.

**5. Functionalities**

The system will include the following major components as discussed with the mentor:

1. Customer Profile – Maintain user details, portfolio, and investment behavior.
2. Company Profile – Store and update listed companies and stock performance.
3. Fund Management – Track available balance and investment allocation.
4. Stock Buy/Sell – Enable simulated trading functions.
5. Dividend Payout – Record dividend earnings per share.
6. Price Prediction – Forecast future prices using ML algorithms.
7. Billing – Generate invoices or summaries for each transaction.
8. Broker Management – Manage brokers and commission details.
9. Monitoring and Control – Admin panel for data visualization and oversight.

**6. Assumptions**

1. Users will operate on simulated data, not real-time market feeds.

2. The stock dataset will be static for initial testing.

3. Internet connection will be stable during transactions.

4. Predictive models will be trained offline before integration.

5. Each transaction is assumed to be error-free for prototype evaluation.

**7. Solution Approach**

The project will follow the Waterfall model for development, moving through analysis, design, implementation, testing, and deployment in phases.

Frontend: HTML, CSS, JavaScript (React or Vite-based interface)

Backend: Python Flask / Node.js

Database: MySQL

Machine Learning Models: Linear Regression, LSTM (for prediction module)

Visualization: Matplotlib / Chart.js for displaying trends

**7.1 LSTM Model Specification**

- **Architecture**
  - 4 stacked layers: `LSTM(50, return_sequences=True) × 3` + `LSTM(50)`
  - Dropout `0.1` after each LSTM layer
  - Dense output layer `Dense(1)` for next‑step price
  - Optimizer: `Adam`, Loss: `Mean Squared Error`

- **Data preprocessing**
  - Input feature: `Close` price (required column)
  - Scaling: `MinMaxScaler(0, 1)` on Close series
  - Sequence length: `7` timesteps per training sample
  - Train/Test split: ~`80/20` on time order

- **Training & evaluation**
  - Default epochs: `5`, batch size: `32`
  - Metric: test `RMSE` on predicted vs. actual Close
  - Forecast: single‑step ahead using the last sequence window

- **Integration**
  - Implemented in `ml_models/lstm_model.py`; orchestrated by `PredictionService`
  - The dashboard “Predict” view can include LSTM alongside ARIMA and Linear Regression
  - If TensorFlow/Keras is unavailable, the app skips LSTM gracefully (other models still run)

- **Enabling LSTM (no X/Twitter required)**
  - Install optional deps locally: `pip install tensorflow` (Keras is bundled)
  - Keep sentiment/X features disabled; they are unrelated to LSTM

**Flow Summary:**

1. Users register and log in.
2. They can view company profiles and live/simulated stock data.
3. They perform buy/sell actions, view their portfolio, and receive dividends.
4. Admin can manage brokers, view transaction logs, and monitor performance.
5. Prediction models update stock trends periodically.

---

**8. Conclusion**

This draft report outlines the foundation of the Share Market Management and Prediction System. It defines the problem, research direction, and the planned functionalities for the system. In the next stage, the team will focus on refining the design models and initiating the implementation process.