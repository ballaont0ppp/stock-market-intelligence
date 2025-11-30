# Model Tests

This directory contains tests for the machine learning models used in the Stock Market Prediction application.

## Files

- `test_lstm_model.py` - Test for the LSTM model (skipped if TensorFlow not available)
- `test_arima_model.py` - Test for the ARIMA model
- `test_linear_regression_model.py` - Test for the Linear Regression model
- `test_with_real_data.py` - Tests all models with real Apple stock data
- `compare_models.py` - Compares all models side-by-side
- `check_model_status.py` - Checks the status of all models
- `run_all_tests.py` - Script to run all tests
- `requirements.txt` - Python dependencies needed for tests

## Model Status

The application currently includes three machine learning models:

1. **ARIMA Model** - ✅ Available and working
2. **Linear Regression Model** - ✅ Available and working
3. **LSTM Model** - ⚠️ Requires TensorFlow to be installed

You can check the status of all models by running:
```bash
python check_model_status.py
```

## Running the Tests

To run all tests:

```bash
python run_all_tests.py
```

To run individual tests:

```bash
python test_lstm_model.py
python test_arima_model.py
python test_linear_regression_model.py
python test_with_real_data.py
python compare_models.py
```

To check model status:

```bash
python check_model_status.py
```

## Requirements

The tests require the same dependencies as the main application:

- pandas
- numpy
- scikit-learn
- statsmodels
- matplotlib

For the LSTM model, you also need:
- tensorflow (optional)

These should already be installed if you've set up the main application. If you want to use the LSTM model, install TensorFlow:

```bash
pip install tensorflow
```

## Test Results

See [TEST_RESULTS.md](TEST_RESULTS.md) for detailed test results.