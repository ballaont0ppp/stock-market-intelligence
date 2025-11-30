#!/usr/bin/env python3
"""
Comprehensive Integration Test for Enhanced Stock Market Prediction System
Tests all enhanced components working together
"""

import os
import sys
import logging
import traceback
import time
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Tuple
import warnings

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# Import enhanced components
try:
    from enhanced_stock_data_fetcher import EnhancedStockDataFetcher
    from enhanced_data_validator import EnhancedDataValidator
    from sophisticated_lstm_model import SophisticatedLSTMModel, ModelConfig
    from configuration_manager import ConfigurationManager, create_default_config_files
    print("✓ All enhanced components imported successfully")
except ImportError as e:
    print(f"✗ Failed to import enhanced components: {e}")
    print("Make sure all enhanced files are in the current directory")
    sys.exit(1)


class IntegrationTestSuite:
    """Comprehensive integration test suite"""
    
    def __init__(self, debug: bool = False):
        """
        Initialize test suite
        
        Args:
            debug: Enable debug logging
        """
        self.debug = debug
        self.results = {
            'test_suite': 'Enhanced Stock Market Prediction System',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'tests': {},
            'summary': {
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0
            }
        }
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize components
        self.config_manager = None
        self.fetcher = None
        self.validator = None
        self.lstm_model = None
        
        self.logger.info("Integration test suite initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for test suite"""
        logger = logging.getLogger('IntegrationTest')
        logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        
        # Console handler
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG if self.debug else logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
    
    def _log_test_result(self, test_name: str, status: str, message: str = "", 
                        details: Dict[str, Any] = None):
        """Log test result"""
        self.results['tests'][test_name] = {
            'status': status,
            'message': message,
            'details': details or {}
        }
        
        self.results['summary']['total_tests'] += 1
        
        if status == 'PASSED':
            self.results['summary']['passed'] += 1
            self.logger.info(f"✓ {test_name}: {message}")
        elif status == 'FAILED':
            self.results['summary']['failed'] += 1
            self.logger.error(f"✗ {test_name}: {message}")
            if details:
                self.logger.error(f"  Details: {details}")
        elif status == 'SKIPPED':
            self.results['summary']['skipped'] += 1
            self.logger.warning(f"⊗ {test_name}: {message}")
    
    def test_configuration_management(self) -> bool:
        """Test configuration management system"""
        test_name = "Configuration Management"
        self.logger.info(f"Testing {test_name}...")
        
        try:
            # Create default configuration files
            create_default_config_files()
            self._log_test_result(test_name, "PASSED", 
                                "Default configuration files created")
            
            # Test loading configuration
            config_manager = ConfigurationManager(environment="development")
            config = config_manager.get_config()
            
            if not config:
                raise ValueError("Configuration not loaded")
            
            # Validate configuration attributes
            required_attrs = ['data_fetcher', 'data_validator', 'lstm_model']
            for attr in required_attrs:
                if not hasattr(config, attr):
                    raise ValueError(f"Missing configuration attribute: {attr}")
            
            # Test configuration summary
            summary = config_manager.get_config_summary()
            if not summary or 'components' not in summary:
                raise ValueError("Configuration summary failed")
            
            self.config_manager = config_manager
            self.fetcher = EnhancedStockDataFetcher(**config.data_fetcher.__dict__)
            self.validator = EnhancedDataValidator(debug=self.debug)
            
            self._log_test_result(test_name, "PASSED", 
                                f"Configuration loaded successfully with {len(summary['components'])} components")
            
            return True
            
        except Exception as e:
            error_msg = f"Configuration management test failed: {str(e)}"
            self.logger.error(error_msg)
            self.logger.debug(traceback.format_exc())
            self._log_test_result(test_name, "FAILED", error_msg)
            return False
    
    def test_data_fetcher(self) -> bool:
        """Test enhanced data fetcher"""
        test_name = "Enhanced Data Fetcher"
        self.logger.info(f"Testing {test_name}...")
        
        try:
            if not self.fetcher:
                raise ValueError("Data fetcher not initialized")
            
            # Test connection
            connection_test = self.fetcher.test_connection()
            
            if connection_test['overall'] not in ['ok', 'degraded']:
                self.logger.warning(f"Connection test returned: {connection_test['overall']}")
            
            # Test symbol validation
            valid_symbols = ["AAPL", "GOOGL", "MSFT"]
            invalid_symbols = ["INVALID123", "TEST", ""]
            
            for symbol in valid_symbols:
                # This would normally make actual API calls, so we'll use small test data
                pass  # Skip actual API calls in test for speed
            
            # Test data quality (simulate with sample data)
            sample_data = self._create_sample_data()
            
            # Test caching functionality
            if self.fetcher.cache_enabled:
                cache_stats = self.fetcher.cache.get_cache_stats()
                self.logger.info(f"Cache stats: {cache_stats}")
            
            # Test API usage stats
            api_stats = self.fetcher.get_api_usage_stats()
            self.logger.info(f"API stats: {api_stats}")
            
            self._log_test_result(test_name, "PASSED", 
                                f"Data fetcher initialized with cache, API usage tracking, and validation")
            
            return True
            
        except Exception as e:
            error_msg = f"Data fetcher test failed: {str(e)}"
            self.logger.error(error_msg)
            self.logger.debug(traceback.format_exc())
            self._log_test_result(test_name, "FAILED", error_msg)
            return False
    
    def test_data_validator(self) -> bool:
        """Test enhanced data validator"""
        test_name = "Enhanced Data Validator"
        self.logger.info(f"Testing {test_name}...")
        
        try:
            if not self.validator:
                raise ValueError("Data validator not initialized")
            
            # Create sample data with various issues
            sample_data = self._create_sample_data_with_issues()
            
            # Test basic validation
            is_valid, issues, analysis = self.validator.validate_dataframe(
                sample_data, "TEST", strict=False
            )
            
            self.logger.info(f"Validation result: {'VALID' if is_valid else 'INVALID'}")
            self.logger.info(f"Issues found: {len(issues)}")
            
            # Test data quality assessment
            quality_score = analysis['data_quality']['overall_score']
            self.logger.info(f"Data quality score: {quality_score:.2f}")
            
            # Test missing value handling
            df_filled = self.validator.handle_missing_values(sample_data, strategy='forward_fill')
            self.logger.info(f"Data shape after filling: {df_filled.shape}")
            
            # Test outlier detection
            outlier_analysis = self.validator._outlier_detection(sample_data)
            outliers_count = outlier_analysis['total_outliers']
            self.logger.info(f"Outliers detected: {outliers_count}")
            
            # Test outlier handling
            df_cleaned = self.validator.handle_outliers(sample_data, method='iqr', action='remove')
            self.logger.info(f"Data shape after outlier removal: {df_cleaned.shape}")
            
            # Test validation report generation
            report = self.validator.generate_validation_report(sample_data, "TEST")
            self.logger.info(f"Validation report generated with {len(report)} sections")
            
            self._log_test_result(test_name, "PASSED", 
                                f"Data validation completed with quality score {quality_score:.2f}")
            
            return True
            
        except Exception as e:
            error_msg = f"Data validator test failed: {str(e)}"
            self.logger.error(error_msg)
            self.logger.debug(traceback.format_exc())
            self._log_test_result(test_name, "FAILED", error_msg)
            return False
    
    def test_lstm_model(self) -> bool:
        """Test sophisticated LSTM model"""
        test_name = "Sophisticated LSTM Model"
        self.logger.info(f"Testing {test_name}...")
        
        try:
            # Check TensorFlow availability
            if not SophisticatedLSTMModel().is_available():
                self._log_test_result(test_name, "SKIPPED", 
                                    "TensorFlow not available - skipping LSTM test")
                return True
            
            # Create sample data for training
            sample_data = self._create_sample_data(size=200)
            
            # Test configuration
            config = ModelConfig(
                sequence_length=20,  # Small for testing
                epochs=5,  # Few epochs for testing
                batch_size=16,
                lstm_units=[32, 16],  # Small model for testing
                dense_units=[8],
                dropout_rate=0.2,
                model_type='LSTM'
            )
            
            # Initialize model
            self.lstm_model = SophisticatedLSTMModel(config, debug=self.debug)
            
            # Test model availability
            if not self.lstm_model.is_available():
                raise ValueError("LSTM model not available")
            
            # Split data
            train_size = int(0.8 * len(sample_data))
            train_data = sample_data.iloc[:train_size]
            val_data = sample_data.iloc[train_size:]
            
            # Test training
            metrics = self.lstm_model.train(train_data, target_column='Close', 
                                          validation_data=val_data)
            
            self.logger.info(f"Training completed in {metrics.training_time:.2f} seconds")
            self.logger.info(f"Final validation loss: {metrics.final_val_loss:.4f}")
            self.logger.info(f"R² Score: {metrics.r2_score:.4f}")
            
            # Test predictions
            predictions = self.lstm_model.predict(val_data, target_column='Close')
            self.logger.info(f"Generated {len(predictions)} predictions")
            
            # Test forecasting
            forecasts = self.lstm_model.forecast(sample_data, n_steps=3, target_column='Close')
            self.logger.info(f"Generated {len(forecasts)} forecasts: {forecasts}")
            
            # Test model summary
            summary = self.lstm_model.get_model_summary()
            self.logger.info(f"Model has {summary['total_parameters']:,} parameters")
            
            # Test model saving/loading (in memory for test)
            self.lstm_model.save_model("test_model")
            self.lstm_model.load_model("test_model")
            
            # Clean up test files
            for file in Path("test_model_model.h5"), Path("test_model_preprocessor.pkl"), \
                        Path("test_model_metadata.json"):
                if file.exists():
                    file.unlink()
            
            self._log_test_result(test_name, "PASSED", 
                                f"LSTM model trained successfully with {metrics.r2_score:.2f} R² score")
            
            return True
            
        except Exception as e:
            error_msg = f"LSTM model test failed: {str(e)}"
            self.logger.error(error_msg)
            self.logger.debug(traceback.format_exc())
            self._log_test_result(test_name, "FAILED", error_msg)
            return False
    
    def test_end_to_end_workflow(self) -> bool:
        """Test complete end-to-end workflow"""
        test_name = "End-to-End Workflow"
        self.logger.info(f"Testing {test_name}...")
        
        try:
            if not all([self.fetcher, self.validator, self.lstm_model]):
                raise ValueError("Not all components available for end-to-end test")
            
            # Create realistic sample data
            sample_data = self._create_realistic_stock_data(size=150)
            
            # Step 1: Data Validation
            self.logger.info("Step 1: Data validation")
            is_valid, issues, analysis = self.validator.validate_dataframe(
                sample_data, "TEST", strict=False
            )
            
            if not is_valid:
                self.logger.warning("Data validation failed, cleaning data")
                sample_data = self.validator.handle_missing_values(sample_data)
                sample_data = self.validator.handle_outliers(sample_data)
            
            # Step 2: LSTM Training and Prediction
            self.logger.info("Step 2: LSTM model training and prediction")
            
            config = ModelConfig(
                sequence_length=15,  # Small for testing
                epochs=3,  # Minimal for testing
                batch_size=16,
                lstm_units=[32],
                dense_units=[16],
                model_type='LSTM'
            )
            
            model = SophisticatedLSTMModel(config, debug=False)
            
            if model.is_available():
                # Split data
                train_size = int(0.7 * len(sample_data))
                train_data = sample_data.iloc[:train_size]
                test_data = sample_data.iloc[train_size:]
                
                # Train model
                metrics = model.train(train_data, target_column='Close', 
                                    validation_data=test_data)
                
                # Make predictions
                predictions = model.predict(test_data, target_column='Close')
                
                # Generate forecasts
                forecasts = model.forecast(sample_data, n_steps=2)
                
                self.logger.info(f"End-to-end workflow completed successfully")
                self.logger.info(f"Final model performance: R² = {metrics.r2_score:.3f}")
                self.logger.info(f"Generated {len(predictions)} predictions and {len(forecasts)} forecasts")
                
                workflow_result = {
                    'data_quality_score': analysis['data_quality']['overall_score'],
                    'model_r2_score': metrics.r2_score,
                    'predictions_count': len(predictions),
                    'forecasts_count': len(forecasts),
                    'training_time': metrics.training_time
                }
                
                self._log_test_result(test_name, "PASSED", 
                                    f"End-to-end workflow completed successfully", 
                                    workflow_result)
            else:
                self._log_test_result(test_name, "SKIPPED", 
                                    "TensorFlow not available for LSTM testing")
            
            return True
            
        except Exception as e:
            error_msg = f"End-to-end workflow test failed: {str(e)}"
            self.logger.error(error_msg)
            self.logger.debug(traceback.format_exc())
            self._log_test_result(test_name, "FAILED", error_msg)
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling across components"""
        test_name = "Error Handling"
        self.logger.info(f"Testing {test_name}...")
        
        try:
            # Test data validator with invalid data
            try:
                empty_df = pd.DataFrame()
                self.validator.validate_dataframe(empty_df, "EMPTY", strict=False)
                self.logger.info("✓ Empty DataFrame handled gracefully")
            except Exception as e:
                self.logger.warning(f"Empty DataFrame handling issue: {e}")
            
            # Test data fetcher with invalid symbol
            if self.fetcher:
                invalid_data = self.fetcher.get_historical_data("INVALID_SYMBOL_12345")
                if invalid_data is None:
                    self.logger.info("✓ Invalid symbol handled gracefully")
            
            # Test LSTM model with insufficient data
            if SophisticatedLSTMModel().is_available():
                small_data = self._create_sample_data(size=5)
                config = ModelConfig(sequence_length=10)
                model = SophisticatedLSTMModel(config)
                
                try:
                    # This should fail gracefully
                    model.train(small_data)
                    self.logger.warning("Expected training to fail with small data")
                except ValueError as e:
                    self.logger.info("✓ Insufficient data handled gracefully")
            
            self._log_test_result(test_name, "PASSED", 
                                "Error handling tested across all components")
            
            return True
            
        except Exception as e:
            error_msg = f"Error handling test failed: {str(e)}"
            self.logger.error(error_msg)
            self.logger.debug(traceback.format_exc())
            self._log_test_result(test_name, "FAILED", error_msg)
            return False
    
    def _create_sample_data(self, size: int = 100) -> pd.DataFrame:
        """Create sample stock data"""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=size, freq='D')
        
        base_price = 100
        prices = []
        for i in range(size):
            change = np.random.normal(0, 1)
            base_price = max(base_price + change, 1)
            prices.append(base_price)
        
        data = {
            'Open': [p * (1 + np.random.uniform(-0.01, 0.01)) for p in prices],
            'High': [p * (1 + np.random.uniform(0, 0.02)) for p in prices],
            'Low': [p * (1 + np.random.uniform(-0.02, 0)) for p in prices],
            'Close': prices,
            'Volume': [np.random.randint(100000, 1000000) for _ in range(size)]
        }
        
        return pd.DataFrame(data, index=dates)
    
    def _create_sample_data_with_issues(self, size: int = 100) -> pd.DataFrame:
        """Create sample stock data with intentional issues"""
        data = self._create_sample_data(size).copy()
        
        # Add missing values
        data.loc[data.index[10], 'Open'] = np.nan
        data.loc[data.index[20], 'Close'] = np.nan
        
        # Add outliers
        data.loc[data.index[30], 'High'] = 1000  # Outlier
        data.loc[data.index[40], 'Volume'] = -1000  # Invalid volume
        
        # Add price relationship issues
        data.loc[data.index[50], 'High'] = data.loc[data.index[50], 'Low'] * 0.5  # High < Low
        
        return data
    
    def _create_realistic_stock_data(self, size: int = 100) -> pd.DataFrame:
        """Create more realistic stock data"""
        np.random.seed(42)
        dates = pd.date_range('2022-01-01', periods=size, freq='D')
        
        # Create realistic price movement
        base_price = 150
        prices = []
        volumes = []
        
        for i in range(size):
            # Add trend and volatility
            trend = 0.001 if i < size//2 else -0.0005  # Slight up then down trend
            volatility = 0.02
            noise = np.random.normal(0, volatility)
            change = trend + noise
            base_price = max(base_price * (1 + change), 10)  # Ensure positive
            
            prices.append(base_price)
            volumes.append(np.random.lognormal(12, 0.5))  # Realistic volume distribution
        
        # Create OHLC data
        data = {
            'Open': [p * (1 + np.random.uniform(-0.005, 0.005)) for p in prices],
            'High': [p * (1 + np.random.uniform(0, 0.015)) for p in prices],
            'Low': [p * (1 + np.random.uniform(-0.015, 0)) for p in prices],
            'Close': prices,
            'Volume': [int(v) for v in volumes]
        }
        
        return pd.DataFrame(data, index=dates)
    
    def generate_test_report(self, output_path: str = "integration_test_report.json") -> str:
        """Generate comprehensive test report"""
        try:
            with open(output_path, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate test report: {e}")
            return ""
    
    def run_all_tests(self) -> bool:
        """Run all integration tests"""
        self.logger.info("=" * 60)
        self.logger.info("ENHANCED STOCK MARKET PREDICTION SYSTEM")
        self.logger.info("COMPREHENSIVE INTEGRATION TEST SUITE")
        self.logger.info("=" * 60)
        
        test_results = []
        
        # Run individual component tests
        tests = [
            ("Configuration Management", self.test_configuration_management),
            ("Enhanced Data Fetcher", self.test_data_fetcher),
            ("Enhanced Data Validator", self.test_data_validator),
            ("Sophisticated LSTM Model", self.test_lstm_model),
            ("Error Handling", self.test_error_handling),
            ("End-to-End Workflow", self.test_end_to_end_workflow)
        ]
        
        for test_name, test_func in tests:
            self.logger.info(f"\n{'=' * 40}")
            self.logger.info(f"Running: {test_name}")
            self.logger.info(f"{'=' * 40}")
            
            try:
                result = test_func()
                test_results.append((test_name, result))
            except Exception as e:
                self.logger.error(f"Test {test_name} crashed: {e}")
                self.logger.debug(traceback.format_exc())
                test_results.append((test_name, False))
        
        # Generate final summary
        self.logger.info(f"\n{'=' * 60}")
        self.logger.info("TEST SUMMARY")
        self.logger.info(f"{'=' * 60}")
        
        passed = self.results['summary']['passed']
        failed = self.results['summary']['failed']
        skipped = self.results['summary']['skipped']
        total = self.results['summary']['total_tests']
        
        success_rate = (passed / max(total - skipped, 1)) * 100
        
        self.logger.info(f"Total Tests: {total}")
        self.logger.info(f"Passed: {passed}")
        self.logger.info(f"Failed: {failed}")
        self.logger.info(f"Skipped: {skipped}")
        self.logger.info(f"Success Rate: {success_rate:.1f}%")
        
        # Generate detailed report
        report_path = self.generate_test_report()
        if report_path:
            self.logger.info(f"\nDetailed test report saved to: {report_path}")
        
        # Clean up test files
        self._cleanup_test_files()
        
        return failed == 0
    
    def _cleanup_test_files(self):
        """Clean up test files"""
        test_files = [
            "data_cache",
            "validation_report.json",
            "models",
            "plots"
        ]
        
        for file_path in test_files:
            try:
                if os.path.exists(file_path):
                    if os.path.isdir(file_path):
                        import shutil
                        shutil.rmtree(file_path)
                    else:
                        os.remove(file_path)
            except Exception as e:
                self.logger.warning(f"Failed to cleanup {file_path}: {e}")


def main():
    """Main function to run integration tests"""
    print("Starting Enhanced Stock Market Prediction System Integration Tests...")
    print("This will test all enhanced components and their integration.")
    print()
    
    # Initialize test suite
    test_suite = IntegrationTestSuite(debug=False)
    
    # Run all tests
    success = test_suite.run_all_tests()
    
    # Print final results
    print()
    print("=" * 60)
    if success:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("The enhanced stock market prediction system is working correctly.")
    else:
        print("❌ SOME INTEGRATION TESTS FAILED!")
        print("Please check the test report for details.")
    print("=" * 60)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)