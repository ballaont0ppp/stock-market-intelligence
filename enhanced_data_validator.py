#!/usr/bin/env python3
"""
Enhanced Data Validator
Comprehensive data validation pipeline with statistical analysis, outlier detection, and quality assessment
"""

import pandas as pd
import numpy as np
import logging
import warnings
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from collections import Counter
import json
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")


class DataQualityMetrics:
    """Container for data quality metrics"""
    
    def __init__(self):
        self.completeness = 0.0
        self.validity = 0.0
        self.uniqueness = 0.0
        self.consistency = 0.0
        self.accuracy = 0.0
        self.timeliness = 0.0
        self.overall_score = 0.0
        self.issues = []
        self.recommendations = []


class OutlierDetection:
    """Advanced outlier detection methods"""
    
    @staticmethod
    def iqr_method(data: np.ndarray, factor: float = 1.5) -> Tuple[np.ndarray, float, float]:
        """
        Detect outliers using Interquartile Range method
        
        Args:
            data: Input data array
            factor: IQR factor for outlier detection
            
        Returns:
            Tuple of (outlier_mask, lower_bound, upper_bound)
        """
        Q1 = np.percentile(data, 25)
        Q3 = np.percentile(data, 75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - factor * IQR
        upper_bound = Q3 + factor * IQR
        
        outlier_mask = (data < lower_bound) | (data > upper_bound)
        
        return outlier_mask, lower_bound, upper_bound
    
    @staticmethod
    def zscore_method(data: np.ndarray, threshold: float = 3.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect outliers using Z-score method
        
        Args:
            data: Input data array
            threshold: Z-score threshold
            
        Returns:
            Tuple of (outlier_mask, z_scores)
        """
        z_scores = np.abs(stats.zscore(data, nan_policy='omit'))
        outlier_mask = z_scores > threshold
        
        return outlier_mask, z_scores
    
    @staticmethod
    def isolation_forest_method(data: np.ndarray, contamination: float = 0.1) -> np.ndarray:
        """
        Detect outliers using Isolation Forest
        
        Args:
            data: Input data array
            contamination: Expected proportion of outliers
            
        Returns:
            Outlier mask
        """
        if len(data) < 10:
            return np.zeros(len(data), dtype=bool)
        
        # Reshape for sklearn
        data_reshaped = data.reshape(-1, 1)
        
        # Fit isolation forest
        iso_forest = IsolationForest(contamination=contamination, random_state=42)
        outlier_labels = iso_forest.fit_predict(data_reshaped)
        
        # Convert to boolean mask (-1 for outliers, 1 for normal)
        return outlier_labels == -1
    
    @staticmethod
    def modified_zscore_method(data: np.ndarray, threshold: float = 3.5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Detect outliers using Modified Z-score method (more robust to outliers)
        
        Args:
            data: Input data array
            threshold: Modified Z-score threshold
            
        Returns:
            Tuple of (outlier_mask, modified_z_scores)
        """
        median = np.median(data)
        mad = np.median(np.abs(data - median))
        
        # Avoid division by zero
        if mad == 0:
            mad = np.std(data)
        
        modified_z_scores = 0.6745 * (data - median) / mad
        outlier_mask = np.abs(modified_z_scores) > threshold
        
        return outlier_mask, modified_z_scores


class TimeSeriesValidator:
    """Time series specific validation"""
    
    @staticmethod
    def check_continuity(df: pd.DataFrame, column: str = 'Close') -> Dict[str, Any]:
        """
        Check time series continuity and identify gaps
        
        Args:
            df: DataFrame with datetime index
            column: Column to analyze
            
        Returns:
            Dictionary with continuity analysis
        """
        if not isinstance(df.index, pd.DatetimeIndex):
            return {'error': 'Index is not datetime'}
        
        # Sort by index
        df_sorted = df.sort_index()
        
        # Calculate time differences
        time_diffs = df_sorted.index.to_series().diff()
        
        # Expected frequency (most common time difference)
        time_diff_counts = Counter(time_diffs.dropna())
        expected_diff = time_diff_counts.most_common(1)[0][0] if time_diff_counts else None
        
        # Find gaps
        gaps = []
        if expected_diff:
            for i in range(1, len(df_sorted)):
                actual_diff = time_diffs.iloc[i]
                if pd.Timedelta(actual_diff) > expected_diff * 1.5:  # Allow some tolerance
                    gaps.append({
                        'from': df_sorted.index[i-1],
                        'to': df_sorted.index[i],
                        'gap_size': actual_diff
                    })
        
        return {
            'total_records': len(df),
            'date_range': {'start': df.index.min(), 'end': df.index.max()},
            'expected_frequency': expected_diff,
            'gaps_count': len(gaps),
            'gaps': gaps,
            'completeness': 1 - (len(gaps) / max(len(df) - 1, 1))
        }
    
    @staticmethod
    def check_stationarity(df: pd.DataFrame, column: str = 'Close') -> Dict[str, Any]:
        """
        Check if time series is stationary using Augmented Dickey-Fuller test
        
        Args:
            df: DataFrame with data
            column: Column to analyze
            
        Returns:
            Dictionary with stationarity analysis
        """
        try:
            from statsmodels.tsa.stattools import adfuller
            
            data = df[column].dropna()
            if len(data) < 10:
                return {'error': 'Insufficient data for stationarity test'}
            
            # Perform ADF test
            result = adfuller(data, autolag='AIC')
            
            is_stationary = result[1] <= 0.05  # p-value <= 0.05
            
            return {
                'is_stationary': is_stationary,
                'p_value': result[1],
                'test_statistic': result[0],
                'critical_values': result[4],
                'used_lags': result[2],
                'n_obs': result[3]
            }
        except ImportError:
            return {'error': 'statsmodels not available for stationarity test'}
        except Exception as e:
            return {'error': f'Stationarity test failed: {str(e)}'}


class EnhancedDataValidator:
    """
    Comprehensive data validation pipeline with advanced statistical analysis
    """
    
    def __init__(self, debug: bool = False):
        """
        Initialize enhanced data validator
        
        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        self.outlier_detector = OutlierDetection()
        self.ts_validator = TimeSeriesValidator()
        
        # Validation thresholds
        self.thresholds = {
            'missing_data_ratio': 0.1,  # 10% missing data threshold
            'outlier_ratio': 0.05,      # 5% outlier ratio threshold
            'negative_values': False,   # No negative values allowed for prices
            'zero_values': False,       # No zero values allowed for prices
            'volume_negative': False,   # No negative volume allowed
            'price_range_min': 0.01,    # Minimum reasonable stock price
            'price_range_max': 10000,   # Maximum reasonable stock price
            'volume_range_max': 1e9     # Maximum reasonable volume
        }
        
        # Required columns for stock data
        self.required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # Data quality metrics
        self.quality_metrics = DataQualityMetrics()
    
    def validate_dataframe(self, df: pd.DataFrame, symbol: str = "Unknown", 
                         strict: bool = False) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Comprehensive data validation with detailed analysis
        
        Args:
            df: DataFrame to validate
            symbol: Stock symbol for context
            strict: If True, raise exceptions on validation failures
            
        Returns:
            Tuple of (is_valid, errors_list, detailed_analysis)
        """
        errors = []
        warnings = []
        detailed_analysis = {
            'basic_validation': {},
            'data_quality': {},
            'statistical_analysis': {},
            'outlier_analysis': {},
            'time_series_analysis': {},
            'data_type_analysis': {},
            'recommendations': []
        }
        
        try:
            # Basic validation
            basic_valid, basic_errors, basic_analysis = self._basic_validation(df, symbol)
            detailed_analysis['basic_validation'] = basic_analysis
            
            if not basic_valid:
                errors.extend(basic_errors)
            
            # Data quality assessment
            quality_analysis = self._assess_data_quality(df)
            detailed_analysis['data_quality'] = quality_analysis
            
            if quality_analysis['overall_score'] < 0.7:
                warnings.append(f"Data quality score is low: {quality_analysis['overall_score']:.2f}")
            
            # Statistical validation
            if basic_valid:
                stats_analysis = self._statistical_validation(df)
                detailed_analysis['statistical_analysis'] = stats_analysis
                
                if stats_analysis['has_issues']:
                    warnings.extend(stats_analysis['issues'])
            
            # Outlier detection
            if basic_valid:
                outlier_analysis = self._outlier_detection(df)
                detailed_analysis['outlier_analysis'] = outlier_analysis
                
                if outlier_analysis['total_outliers'] > len(df) * 0.1:
                    warnings.append(f"High number of outliers detected: {outlier_analysis['total_outliers']}")
            
            # Time series analysis
            if isinstance(df.index, pd.DatetimeIndex) and basic_valid:
                ts_analysis = self._time_series_analysis(df)
                detailed_analysis['time_series_analysis'] = ts_analysis
                
                if ts_analysis.get('continuity', {}).get('gaps_count', 0) > len(df) * 0.05:
                    warnings.append(f"Significant gaps in time series: {ts_analysis['continuity']['gaps_count']}")
            
            # Data type validation
            dtype_analysis = self._data_type_validation(df)
            detailed_analysis['data_type_analysis'] = dtype_analysis
            
            if dtype_analysis['has_conversion_issues']:
                errors.append("Data type conversion issues detected")
            
            # Generate recommendations
            recommendations = self._generate_recommendations(detailed_analysis)
            detailed_analysis['recommendations'] = recommendations
            
            # Overall validation result
            is_valid = len(errors) == 0
            
            # Log results
            if errors:
                self.logger.error(f"Data validation FAILED for {symbol}: {'; '.join(errors)}")
            if warnings:
                self.logger.warning(f"Data validation WARNINGS for {symbol}: {'; '.join(warnings)}")
            
            if strict and errors:
                raise ValueError(f"Data validation failed for {symbol}: {'; '.join(errors)}")
            
            return is_valid, errors + warnings, detailed_analysis
            
        except Exception as e:
            error_msg = f"Unexpected error during validation: {str(e)}"
            self.logger.error(error_msg)
            return False, [error_msg], {'error': error_msg}
    
    def _basic_validation(self, df: pd.DataFrame, symbol: str) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Perform basic data validation"""
        errors = []
        analysis = {}
        
        # Check if DataFrame is empty
        if df.empty:
            errors.append(f"DataFrame for {symbol} is empty")
            return False, errors, analysis
        
        analysis['shape'] = df.shape
        analysis['columns'] = list(df.columns)
        analysis['index_type'] = str(type(df.index).__name__)
        
        # Check required columns
        missing_columns = set(self.required_columns) - set(df.columns)
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
        
        # Check for completely null columns
        null_columns = [col for col in df.columns if df[col].isnull().all()]
        if null_columns:
            errors.append(f"Columns with all null values: {null_columns}")
        
        # Check for reasonable number of rows
        if len(df) < 5:
            errors.append(f"Insufficient data: only {len(df)} rows (minimum 5 required)")
        elif len(df) < 30:
            errors.append(f"Limited data: only {len(df)} rows (minimum 30 recommended)")
        
        # Basic statistics
        if len(df) > 0:
            analysis['null_counts'] = df.isnull().sum().to_dict()
            analysis['memory_usage'] = df.memory_usage(deep=True).sum()
        
        return len(errors) == 0, errors, analysis
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess overall data quality"""
        quality = DataQualityMetrics()
        quality.issues = []
        quality.recommendations = []
        
        # Completeness (percentage of non-null values)
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isnull().sum().sum()
        quality.completeness = 1 - (null_cells / total_cells)
        
        if quality.completeness < 0.9:
            quality.issues.append(f"Low completeness: {quality.completeness:.2%}")
            quality.recommendations.append("Handle missing values using appropriate imputation methods")
        
        # Validity (percentage of values that pass validation rules)
        validity_checks = []
        
        for col in self.required_columns:
            if col in df.columns:
                if col in ['Open', 'High', 'Low', 'Close']:
                    # Price validation
                    valid_prices = (df[col] > 0) & (df[col] < self.thresholds['price_range_max'])
                    validity_checks.append(valid_prices.mean())
                elif col == 'Volume':
                    # Volume validation
                    valid_volume = (df[col] >= 0) & (df[col] <= self.thresholds['volume_range_max'])
                    validity_checks.append(valid_volume.mean())
        
        quality.validity = np.mean(validity_checks) if validity_checks else 1.0
        
        if quality.validity < 0.95:
            quality.issues.append(f"Low validity: {quality.validity:.2%}")
            quality.recommendations.append("Review and clean invalid data values")
        
        # Uniqueness (for index, if applicable)
        if hasattr(df.index, 'duplicated'):
            duplicate_ratio = df.index.duplicated().sum() / len(df)
            quality.uniqueness = 1 - duplicate_ratio
            
            if quality.uniqueness < 0.99:
                quality.issues.append(f"Duplicate index entries: {duplicate_ratio:.2%}")
                quality.recommendations.append("Remove duplicate index entries")
        
        # Calculate overall score
        metrics = [quality.completeness, quality.validity, quality.uniqueness]
        quality.overall_score = np.mean([m for m in metrics if not np.isnan(m)])
        
        return {
            'completeness': quality.completeness,
            'validity': quality.validity,
            'uniqueness': quality.uniqueness,
            'overall_score': quality.overall_score,
            'issues': quality.issues,
            'recommendations': quality.recommendations
        }
    
    def _statistical_validation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform statistical validation"""
        issues = []
        analysis = {}
        has_issues = False
        
        price_columns = ['Open', 'High', 'Low', 'Close']
        available_price_cols = [col for col in price_columns if col in df.columns]
        
        for col in available_price_cols:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue
            
            # Check for negative values
            negative_count = (col_data < 0).sum()
            if negative_count > 0:
                issues.append(f"{col} has {negative_count} negative values")
                has_issues = True
            
            # Check for zero values
            zero_count = (col_data == 0).sum()
            if zero_count > len(col_data) * 0.05:  # More than 5%
                issues.append(f"{col} has {zero_count} zero values ({zero_count/len(col_data):.2%})")
                has_issues = True
            
            # Check price relationships (High >= Low, etc.)
            if all(c in df.columns for c in ['High', 'Low', 'Open', 'Close']):
                invalid_high_low = (df['High'] < df['Low']).sum()
                if invalid_high_low > 0:
                    issues.append(f"High < Low in {invalid_high_low} records")
                    has_issues = True
                
                invalid_open_high = (df['Open'] > df['High']).sum()
                if invalid_open_high > 0:
                    issues.append(f"Open > High in {invalid_open_high} records")
                    has_issues = True
                
                invalid_close_low = (df['Close'] < df['Low']).sum()
                if invalid_close_low > 0:
                    issues.append(f"Close < Low in {invalid_close_low} records")
                    has_issues = True
        
        # Volume validation
        if 'Volume' in df.columns:
            volume_data = df['Volume'].dropna()
            negative_volume = (volume_data < 0).sum()
            if negative_volume > 0:
                issues.append(f"Volume has {negative_volume} negative values")
                has_issues = True
        
        analysis['has_issues'] = has_issues
        analysis['issues'] = issues
        
        return analysis
    
    def _outlier_detection(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform comprehensive outlier detection"""
        outlier_analysis = {
            'methods_used': [],
            'outliers_by_column': {},
            'total_outliers': 0,
            'outlier_details': []
        }
        
        price_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        available_cols = [col for col in price_columns if col in df.columns]
        
        for col in available_cols:
            col_data = df[col].dropna().values
            if len(col_data) < 5:
                continue
            
            column_outliers = {}
            
            # IQR method
            try:
                iqr_outliers, lower, upper = self.outlier_detector.iqr_method(col_data)
                column_outliers['iqr'] = {
                    'count': iqr_outliers.sum(),
                    'indices': np.where(iqr_outliers)[0].tolist(),
                    'bounds': [lower, upper]
                }
                outlier_analysis['methods_used'].append('IQR')
            except Exception as e:
                self.logger.warning(f"IQR method failed for {col}: {e}")
            
            # Z-score method
            try:
                zscore_outliers, z_scores = self.outlier_detector.zscore_method(col_data)
                column_outliers['zscore'] = {
                    'count': zscore_outliers.sum(),
                    'indices': np.where(zscore_outliers)[0].tolist(),
                    'max_zscore': np.max(np.abs(z_scores))
                }
                if 'IQR' not in outlier_analysis['methods_used']:
                    outlier_analysis['methods_used'].append('Z-score')
            except Exception as e:
                self.logger.warning(f"Z-score method failed for {col}: {e}")
            
            # Modified Z-score method (more robust)
            try:
                mod_zscore_outliers, mod_z_scores = self.outlier_detector.modified_zscore_method(col_data)
                column_outliers['modified_zscore'] = {
                    'count': mod_zscore_outliers.sum(),
                    'indices': np.where(mod_zscore_outliers)[0].tolist(),
                    'max_modified_zscore': np.max(np.abs(mod_z_scores))
                }
                if 'Modified Z-score' not in outlier_analysis['methods_used']:
                    outlier_analysis['methods_used'].append('Modified Z-score')
            except Exception as e:
                self.logger.warning(f"Modified Z-score method failed for {col}: {e}")
            
            # Isolation Forest
            if len(col_data) >= 10:
                try:
                    iso_outliers = self.outlier_detector.isolation_forest_method(col_data)
                    column_outliers['isolation_forest'] = {
                        'count': iso_outliers.sum(),
                        'indices': np.where(iso_outliers)[0].tolist()
                    }
                    if 'Isolation Forest' not in outlier_analysis['methods_used']:
                        outlier_analysis['methods_used'].append('Isolation Forest')
                except Exception as e:
                    self.logger.warning(f"Isolation Forest method failed for {col}: {e}")
            
            outlier_analysis['outliers_by_column'][col] = column_outliers
            outlier_analysis['total_outliers'] += sum(
                method.get('count', 0) for method in column_outliers.values()
            )
        
        return outlier_analysis
    
    def _time_series_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform time series specific analysis"""
        analysis = {}
        
        # Continuity check
        if 'Close' in df.columns:
            continuity = self.ts_validator.check_continuity(df, 'Close')
            analysis['continuity'] = continuity
            
            # Stationarity check
            stationarity = self.ts_validator.check_stationarity(df, 'Close')
            analysis['stationarity'] = stationarity
        
        return analysis
    
    def _data_type_validation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate and analyze data types"""
        analysis = {
            'current_types': {},
            'recommended_types': {},
            'has_conversion_issues': False,
            'conversion_recommendations': []
        }
        
        for col in df.columns:
            analysis['current_types'][col] = str(df[col].dtype)
            
            # Recommend appropriate types
            if col in self.required_columns:
                if col == 'Volume':
                    analysis['recommended_types'][col] = 'int64'
                else:
                    analysis['recommended_types'][col] = 'float64'
        
        # Check for object columns that should be numeric
        object_columns = df.select_dtypes(include=['object']).columns
        for col in object_columns:
            if col in self.required_columns:
                analysis['has_conversion_issues'] = True
                analysis['conversion_recommendations'].append(
                    f"Convert {col} from object to numeric type"
                )
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate data quality improvement recommendations"""
        recommendations = []
        
        # From data quality analysis
        quality = analysis.get('data_quality', {})
        if quality.get('completeness', 1) < 0.9:
            recommendations.append("Implement missing value imputation strategies")
        
        if quality.get('validity', 1) < 0.95:
            recommendations.append("Review and clean invalid data values")
        
        # From outlier analysis
        outliers = analysis.get('outlier_analysis', {})
        if outliers.get('total_outliers', 0) > len(analysis.get('basic_validation', {}).get('shape', [0]))[0] * 0.05:
            recommendations.append("Investigate and handle outliers using domain knowledge")
        
        # From time series analysis
        ts_analysis = analysis.get('time_series_analysis', {})
        continuity = ts_analysis.get('continuity', {})
        if continuity.get('gaps_count', 0) > 0:
            recommendations.append("Address time series gaps through interpolation or data sourcing")
        
        stationarity = ts_analysis.get('stationarity', {})
        if not stationarity.get('is_stationary', True):
            recommendations.append("Consider differencing or transformation for non-stationary series")
        
        # From data type analysis
        dtype_analysis = analysis.get('data_type_analysis', {})
        if dtype_analysis.get('has_conversion_issues'):
            recommendations.append("Convert object columns to appropriate numeric types")
        
        return recommendations
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'forward_fill') -> pd.DataFrame:
        """
        Handle missing values using various strategies
        
        Args:
            df: Input DataFrame
            strategy: Missing value handling strategy
            
        Returns:
            DataFrame with missing values handled
        """
        df_clean = df.copy()
        
        if strategy == 'forward_fill':
            # Forward fill for stock data (carry forward last known price)
            df_clean = df_clean.fillna(method='ffill')
            
        elif strategy == 'backward_fill':
            # Backward fill
            df_clean = df_clean.fillna(method='bfill')
            
        elif strategy == 'interpolate':
            # Linear interpolation
            df_clean = df_clean.interpolate(method='linear')
            
        elif strategy == 'drop':
            # Drop rows with any missing values
            df_clean = df_clean.dropna()
            
        elif strategy == 'mean':
            # Fill with mean for numeric columns
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
            
        elif strategy == 'median':
            # Fill with median for numeric columns
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
        
        # Remove any remaining NaN values
        df_clean = df_clean.dropna()
        
        self.logger.info(f"Applied missing value strategy '{strategy}', result shape: {df_clean.shape}")
        
        return df_clean
    
    def handle_outliers(self, df: pd.DataFrame, method: str = 'iqr', 
                       action: str = 'remove') -> pd.DataFrame:
        """
        Handle outliers using various methods
        
        Args:
            df: Input DataFrame
            method: Outlier detection method
            action: Action to take with outliers
            
        Returns:
            DataFrame with outliers handled
        """
        df_clean = df.copy()
        outliers_removed = 0
        
        price_columns = ['Open', 'High', 'Low', 'Close']
        
        for col in price_columns:
            if col not in df_clean.columns:
                continue
            
            col_data = df_clean[col].dropna()
            if len(col_data) < 5:
                continue
            
            # Detect outliers
            if method == 'iqr':
                outlier_mask, lower, upper = self.outlier_detector.iqr_method(col_data)
            elif method == 'zscore':
                outlier_mask, _ = self.outlier_detector.zscore_method(col_data)
            elif method == 'modified_zscore':
                outlier_mask, _ = self.outlier_detector.modified_zscore_method(col_data)
            else:
                continue
            
            outlier_indices = df_clean.index[outlier_mask]
            
            if action == 'remove':
                df_clean = df_clean.drop(outlier_indices)
                outliers_removed += len(outlier_indices)
            elif action == 'cap':
                # Cap outliers at bounds
                df_clean.loc[df_clean[col] < lower, col] = lower
                df_clean.loc[df_clean[col] > upper, col] = upper
        
        self.logger.info(f"Applied outlier handling method '{method}' with action '{action}', removed {outliers_removed} outliers")
        
        return df_clean
    
    def generate_validation_report(self, df: pd.DataFrame, symbol: str, 
                                 output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive validation report
        
        Args:
            df: DataFrame to validate
            symbol: Stock symbol
            output_path: Optional path to save report
            
        Returns:
            Dictionary with validation report
        """
        # Perform full validation
        is_valid, errors_warnings, detailed_analysis = self.validate_dataframe(df, symbol, strict=False)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'validation_summary': {
                'is_valid': is_valid,
                'total_issues': len(errors_warnings),
                'errors': [e for e in errors_warnings if 'WARNING' not in e],
                'warnings': [e for e in errors_warnings if 'WARNING' in e]
            },
            'detailed_analysis': detailed_analysis,
            'data_profile': {
                'shape': df.shape,
                'columns': list(df.columns),
                'dtypes': df.dtypes.to_dict(),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024)
            }
        }
        
        # Save report if path provided
        if output_path:
            try:
                with open(output_path, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                self.logger.info(f"Validation report saved to {output_path}")
            except Exception as e:
                self.logger.error(f"Failed to save validation report: {e}")
        
        return report


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize enhanced validator
    validator = EnhancedDataValidator(debug=True)
    
    # Create sample data with some issues
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    
    # Normal stock data
    base_price = 100
    prices = []
    for i in range(100):
        change = np.random.normal(0, 2)
        base_price = max(base_price + change, 1)  # Ensure positive prices
        prices.append(base_price)
    
    # Create sample DataFrame with some intentional issues
    data = {
        'Open': prices,
        'High': [p + np.random.uniform(0, 5) for p in prices],
        'Low': [p - np.random.uniform(0, 5) for p in prices],
        'Close': prices,
        'Volume': [np.random.randint(1000, 1000000) for _ in range(100)]
    }
    
    # Add some missing values and outliers
    data['Open'][10] = np.nan
    data['High'][20] = 10000  # Outlier
    data['Volume'][30] = -100  # Invalid volume
    
    df = pd.DataFrame(data, index=dates)
    
    # Validate the data
    print("Validating sample data...")
    is_valid, issues, analysis = validator.validate_dataframe(df, "TEST", strict=False)
    
    print(f"Validation result: {'VALID' if is_valid else 'INVALID'}")
    print(f"Issues found: {len(issues)}")
    for issue in issues:
        print(f"  - {issue}")
    
    print(f"Data quality score: {analysis['data_quality']['overall_score']:.2f}")
    print(f"Outliers detected: {analysis['outlier_analysis']['total_outliers']}")
    
    # Generate validation report
    print("\nGenerating validation report...")
    report = validator.generate_validation_report(df, "TEST", "validation_report.json")
    print(f"Report generated with {len(report['detailed_analysis'])} analysis sections")
    
    # Test missing value handling
    print("\nTesting missing value handling...")
    df_filled = validator.handle_missing_values(df, strategy='forward_fill')
    print(f"Data shape after filling: {df_filled.shape}")
    
    # Test outlier handling
    print("\nTesting outlier handling...")
    df_cleaned = validator.handle_outliers(df_filled, method='iqr', action='remove')
    print(f"Data shape after outlier removal: {df_cleaned.shape}")
    
    print("\nValidation testing completed successfully!")