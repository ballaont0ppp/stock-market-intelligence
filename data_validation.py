#!/usr/bin/env python3
"""
Data Validation Utilities
Common validation functions for stock market data processing
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def validate_stock_data(df, symbol="Unknown", strict=True):
    """
    Comprehensive validation of stock data DataFrame
    
    Args:
        df (pandas.DataFrame): Stock data to validate
        symbol (str): Stock symbol for logging
        strict (bool): If True, raises exceptions on validation failures
        
    Returns:
        tuple: (is_valid, errors_list)
    """
    errors = []
    warnings = []
    
    # Check if DataFrame is empty
    if df.empty:
        errors.append(f"DataFrame for {symbol} is empty")
        return False, errors
    
    # Check expected columns
    expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    missing_columns = set(expected_columns) - set(df.columns)
    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")
    
    # Check for all null data in price columns
    price_columns = ['Open', 'High', 'Low', 'Close']
    for col in price_columns:
        if col in df.columns:
            if df[col].isnull().all():
                errors.append(f"Column '{col}' contains all null values")
            elif df[col].isnull().any():
                warnings.append(f"Column '{col}' contains {df[col].isnull().sum()} null values")
    
    # Check data types
    for col in price_columns + ['Volume']:
        if col in df.columns:
            if not np.issubdtype(df[col].dtype, np.number):
                errors.append(f"Column '{col}' is not numeric (got {df[col].dtype})")
    
    # Check for reasonable price values
    for col in price_columns:
        if col in df.columns:
            if (df[col] <= 0).any():
                warnings.append(f"Column '{col}' contains non-positive values")
            if (df[col] > 10000).any():
                warnings.append(f"Column '{col}' contains unusually high values (>10000)")
    
    # Check volume data
    if 'Volume' in df.columns:
        if (df['Volume'] < 0).any():
            errors.append("Volume column contains negative values")
        if df['Volume'].isnull().all():
            warnings.append("All volume values are null")
    
    # Check DataFrame has sufficient data points
    if len(df) < 10:
        warnings.append(f"DataFrame has only {len(df)} rows (recommend at least 30 for prediction)")
    
    # Check for duplicate dates if Date is the index
    if isinstance(df.index, pd.DatetimeIndex):
        if df.index.duplicated().any():
            errors.append("Date index contains duplicate dates")
    
    # Log results
    if errors:
        logger.error(f"Data validation FAILED for {symbol}: {'; '.join(errors)}")
    if warnings:
        logger.warning(f"Data validation WARNINGS for {symbol}: {'; '.join(warnings)}")
    
    if strict and errors:
        raise ValueError(f"Data validation failed for {symbol}: {'; '.join(errors)}")
    
    return len(errors) == 0, errors + warnings

def clean_stock_data(df):
    """
    Clean stock data by handling common issues
    
    Args:
        df (pandas.DataFrame): Raw stock data
        
    Returns:
        pandas.DataFrame: Cleaned stock data
    """
    df_clean = df.copy()
    
    # Forward fill missing values (common in stock data)
    df_clean = df_clean.fillna(method='ffill')
    
    # Remove any remaining rows with NaN values
    df_clean = df_clean.dropna()
    
    # Ensure numeric columns are actually numeric
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in numeric_columns:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    # Remove rows with negative prices (invalid data)
    price_columns = ['Open', 'High', 'Low', 'Close']
    for col in price_columns:
        if col in df_clean.columns:
            df_clean = df_clean[df_clean[col] > 0]
    
    return df_clean

def print_dataframe_info(df, symbol="Unknown"):
    """
    Print detailed information about a DataFrame
    
    Args:
        df (pandas.DataFrame): DataFrame to analyze
        symbol (str): Stock symbol for context
    """
    print(f"\n=== DATA FRAME INFO FOR {symbol} ===")
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"Index type: {type(df.index)}")
    print(f"Data types:\n{df.dtypes}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum()} bytes")
    print(f"Null values per column:\n{df.isnull().sum()}")
    
    # Show first and last few rows
    print(f"\nFirst 3 rows:\n{df.head(3)}")
    print(f"\nLast 3 rows:\n{df.tail(3)}")
    
    # Show basic statistics
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) > 0:
        print(f"\nBasic statistics for numeric columns:\n{df[numeric_columns].describe()}")
    
    print("=" * 50)