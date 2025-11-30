#!/usr/bin/env python3
"""
Configuration Management System
Centralized configuration for enhanced stock market prediction system
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from pathlib import Path
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")


@dataclass
class DataFetcherConfig:
    """Configuration for enhanced data fetcher"""
    # Caching settings
    cache_enabled: bool = True
    cache_dir: str = "data_cache"
    cache_ttl: int = 3600  # 1 hour
    
    # Rate limiting
    rate_limit_calls: int = 60
    rate_limit_window: int = 60  # seconds
    
    # Retry settings
    max_retries: int = 3
    timeout: int = 30
    
    # Data source settings
    primary_source: str = "yfinance"
    fallback_sources: List[str] = field(default_factory=lambda: ["alpha_vantage"])
    
    # API keys (loaded from environment)
    alpha_vantage_key: Optional[str] = field(default_factory=lambda: os.getenv('ALPHA_VANTAGE_API_KEY'))
    iex_cloud_key: Optional[str] = field(default_factory=lambda: os.getenv('IEX_CLOUD_API_KEY'))
    polygon_key: Optional[str] = field(default_factory=lambda: os.getenv('POLYGON_API_KEY'))


@dataclass
class DataValidatorConfig:
    """Configuration for enhanced data validator"""
    # Missing data handling
    missing_data_threshold: float = 0.1  # 10%
    handle_missing_values: bool = True
    missing_value_strategy: str = "forward_fill"  # forward_fill, backward_fill, interpolate, drop, mean, median
    
    # Outlier detection
    outlier_detection_enabled: bool = True
    outlier_methods: List[str] = field(default_factory=lambda: ["iqr", "zscore", "modified_zscore"])
    outlier_threshold_iqr: float = 1.5
    outlier_threshold_zscore: float = 3.0
    outlier_threshold_modified_zscore: float = 3.5
    outlier_action: str = "remove"  # remove, cap
    
    # Data quality thresholds
    min_data_points: int = 30
    max_outlier_ratio: float = 0.05  # 5%
    completeness_threshold: float = 0.9  # 90%
    validity_threshold: float = 0.95  # 95%
    
    # Time series validation
    time_series_validation: bool = True
    check_stationarity: bool = True
    check_continuity: bool = True
    max_gap_ratio: float = 0.05  # 5%
    
    # Statistical validation
    price_range_min: float = 0.01
    price_range_max: float = 10000.0
    volume_range_max: float = 1e9
    allow_negative_prices: bool = False
    allow_zero_prices: bool = False
    allow_negative_volume: bool = False


@dataclass
class LSTMModelConfig:
    """Configuration for sophisticated LSTM model"""
    # Architecture
    sequence_length: int = 60
    model_type: str = "LSTM"  # LSTM, GRU, BidirectionalLSTM
    lstm_units: List[int] = field(default_factory=lambda: [50, 50, 50])
    dense_units: List[int] = field(default_factory=lambda: [25])
    dropout_rate: float = 0.2
    recurrent_dropout: float = 0.2
    l1_reg: float = 0.0
    l2_reg: float = 0.01
    
    # Advanced features
    use_attention: bool = False
    use_batch_norm: bool = True
    use_layer_norm: bool = False
    
    # Training
    epochs: int = 100
    batch_size: int = 32
    validation_split: float = 0.2
    early_stopping_patience: int = 15
    learning_rate: float = 0.001
    optimizer: str = "Adam"
    loss_function: str = "MSE"
    
    # Preprocessing
    scaler_type: str = "minmax"  # minmax, standard
    feature_columns: List[str] = field(default_factory=lambda: ["Close", "Volume"])
    target_column: str = "Close"
    
    # Model persistence
    models_dir: str = "models"
    save_best_only: bool = True
    save_training_history: bool = True
    
    # Prediction settings
    confidence_intervals: bool = True
    n_bootstrap_samples: int = 100
    n_forecast_steps: int = 5


@dataclass
class SystemConfig:
    """Main system configuration"""
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None
    log_max_size: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5
    
    # Output directories
    output_dir: str = "output"
    plots_dir: str = "plots"
    reports_dir: str = "reports"
    
    # Data settings
    default_symbols: List[str] = field(default_factory=lambda: ["AAPL", "GOOGL", "MSFT"])
    default_period: str = "1y"
    default_interval: str = "1d"
    
    # Performance settings
    max_workers: int = 5
    memory_limit_mb: int = 1024
    parallel_processing: bool = True
    
    # Feature flags
    enable_enhanced_features: bool = True
    enable_advanced_lstm: bool = True
    enable_real_time_data: bool = True
    enable_cache_warming: bool = True
    enable_data_validation: bool = True
    
    # Testing
    run_integration_tests: bool = True
    test_data_size: str = "small"  # small, medium, large
    
    # Component configurations
    data_fetcher: DataFetcherConfig = field(default_factory=DataFetcherConfig)
    data_validator: DataValidatorConfig = field(default_factory=DataValidatorConfig)
    lstm_model: LSTMModelConfig = field(default_factory=LSTMModelConfig)


class ConfigManager:
    """Centralized configuration management system"""
    
    def __init__(self, config_path: Optional[str] = None, environment: str = "development"):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
            environment: Environment name (development, testing, production)
        """
        self.environment = environment
        self.config_path = config_path or self._get_default_config_path()
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config()
        
        # Validate configuration
        self._validate_config()
        
        # Setup logging
        self._setup_logging()
        
        # Create output directories
        self._setup_directories()
        
        self.logger.info(f"Configuration loaded for environment: {environment}")
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path based on environment"""
        config_dir = Path("config")
        config_dir.mkdir(exist_ok=True)
        
        env_file = f"config_{self.environment}.yaml"
        return str(config_dir / env_file)
    
    def _load_config(self) -> SystemConfig:
        """Load configuration from file and environment variables"""
        config_data = {}
        
        # Load from file if exists
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                self.logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                self.logger.warning(f"Failed to load config file {self.config_path}: {e}")
        
        # Load from environment variables and apply overrides
        config_data = self._load_from_environment(config_data)
        
        # Create SystemConfig object
        try:
            return self._dict_to_system_config(config_data)
        except Exception as e:
            self.logger.error(f"Failed to create SystemConfig: {e}")
            self.logger.info("Using default configuration")
            return SystemConfig()
    
    def _load_from_environment(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Load configuration overrides from environment variables"""
        env_prefix = "STOCK_APP_"
        
        # Map environment variables to configuration paths
        env_mappings = {
            # System settings
            f"{env_prefix}LOG_LEVEL": ("log_level", str),
            f"{env_prefix}LOG_FILE": ("log_file", str),
            f"{env_prefix}OUTPUT_DIR": ("output_dir", str),
            f"{env_prefix}MAX_WORKERS": ("max_workers", int),
            
            # Data fetcher settings
            f"{env_prefix}CACHE_ENABLED": ("data_fetcher.cache_enabled", lambda x: x.lower() == 'true'),
            f"{env_prefix}CACHE_TTL": ("data_fetcher.cache_ttl", int),
            f"{env_prefix}RATE_LIMIT_CALLS": ("data_fetcher.rate_limit_calls", int),
            f"{env_prefix}TIMEOUT": ("data_fetcher.timeout", int),
            
            # LSTM model settings
            f"{env_prefix}SEQUENCE_LENGTH": ("lstm_model.sequence_length", int),
            f"{env_prefix}EPOCHS": ("lstm_model.epochs", int),
            f"{env_prefix}BATCH_SIZE": ("lstm_model.batch_size", int),
            f"{env_prefix}LEARNING_RATE": ("lstm_model.learning_rate", float),
            
            # API keys
            f"{env_prefix}ALPHA_VANTAGE_KEY": ("data_fetcher.alpha_vantage_key", str),
            f"{env_prefix}IEX_CLOUD_KEY": ("data_fetcher.iex_cloud_key", str),
            f"{env_prefix}POLYGON_KEY": ("data_fetcher.polygon_key", str),
        }
        
        for env_var, (config_path, converter) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    converted_value = converter(value)
                    self._set_nested_value(config_data, config_path, converted_value)
                    self.logger.debug(f"Set {config_path} from environment: {value}")
                except Exception as e:
                    self.logger.warning(f"Failed to convert environment variable {env_var}: {e}")
        
        return config_data
    
    def _set_nested_value(self, data: Dict[str, Any], path: str, value: Any) -> None:
        """Set nested dictionary value using dot notation"""
        keys = path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _dict_to_system_config(self, config_data: Dict[str, Any]) -> SystemConfig:
        """Convert dictionary to SystemConfig object"""
        # Extract nested configurations
        fetcher_config = config_data.get('data_fetcher', {})
        validator_config = config_data.get('data_validator', {})
        lstm_config = config_data.get('lstm_model', {})
        
        # Create configuration objects
        data_fetcher = DataFetcherConfig(**fetcher_config)
        data_validator = DataValidatorConfig(**validator_config)
        lstm_model = LSTMModelConfig(**lstm_config)
        
        # Create main config
        system_config = SystemConfig(
            **{k: v for k, v in config_data.items() 
               if k not in ['data_fetcher', 'data_validator', 'lstm_model']}
        )
        
        # Set nested configs
        system_config.data_fetcher = data_fetcher
        system_config.data_validator = data_validator
        system_config.lstm_model = lstm_model
        
        return system_config
    
    def _validate_config(self) -> None:
        """Validate configuration values"""
        try:
            # Validate data fetcher config
            if not 0 < self.config.data_fetcher.cache_ttl < 86400:  # 24 hours max
                self.logger.warning("Cache TTL should be between 1 second and 24 hours")
                self.config.data_fetcher.cache_ttl = max(300, min(self.config.data_fetcher.cache_ttl, 86400))
            
            if not 1 <= self.config.data_fetcher.max_retries <= 10:
                self.logger.warning("Max retries should be between 1 and 10")
                self.config.data_fetcher.max_retries = max(1, min(self.config.data_fetcher.max_retries, 10))
            
            # Validate LSTM config
            if not 5 <= self.config.lstm_model.sequence_length <= 500:
                self.logger.warning("Sequence length should be between 5 and 500")
                self.config.lstm_model.sequence_length = max(5, min(self.config.lstm_model.sequence_length, 500))
            
            if not 1 <= self.config.lstm_model.epochs <= 1000:
                self.logger.warning("Epochs should be between 1 and 1000")
                self.config.lstm_model.epochs = max(1, min(self.config.lstm_model.epochs, 1000))
            
            # Validate system config
            valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if self.config.log_level.upper() not in valid_log_levels:
                self.logger.warning(f"Invalid log level: {self.config.log_level}, using INFO")
                self.config.log_level = "INFO"
            
            if not 1 <= self.config.max_workers <= 20:
                self.logger.warning("Max workers should be between 1 and 20")
                self.config.max_workers = max(1, min(self.config.max_workers, 20))
            
            self.logger.info("Configuration validation completed")
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            raise
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        try:
            # Create logs directory
            os.makedirs("logs", exist_ok=True)
            
            # Setup logging
            log_level = getattr(logging, self.config.log_level.upper())
            
            handlers = [logging.StreamHandler()]  # Console handler
            
            # Add file handler if log file is specified
            if self.config.log_file:
                from logging.handlers import RotatingFileHandler
                handlers.append(RotatingFileHandler(
                    self.config.log_file,
                    maxBytes=self.config.log_max_size,
                    backupCount=self.config.log_backup_count
                ))
            
            # Configure logging
            logging.basicConfig(
                level=log_level,
                format=self.config.log_format,
                handlers=handlers
            )
            
            # Set matplotlib to use non-interactive backend
            import matplotlib
            matplotlib.use('Agg')
            
            self.logger.info(f"Logging configured: level={self.config.log_level}")
            
        except Exception as e:
            print(f"Warning: Failed to setup logging: {e}")
    
    def _setup_directories(self) -> None:
        """Create necessary directories"""
        directories = [
            self.config.output_dir,
            self.config.plots_dir,
            self.config.reports_dir,
            self.config.data_fetcher.cache_dir,
            self.config.lstm_model.models_dir
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Output directories created")
    
    def save_config(self, filepath: Optional[str] = None) -> None:
        """Save current configuration to file"""
        save_path = filepath or self.config_path
        
        try:
            config_dict = asdict(self.config)
            
            # Convert dataclasses to dictionaries recursively
            config_dict = self._convert_dataclasses_to_dict(config_dict)
            
            # Save to file
            with open(save_path, 'w') as f:
                if save_path.endswith('.yaml') or save_path.endswith('.yml'):
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2)
            
            self.logger.info(f"Configuration saved to {save_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")
            raise
    
    def _convert_dataclasses_to_dict(self, obj: Any) -> Any:
        """Recursively convert dataclass objects to dictionaries"""
        if hasattr(obj, '__dict__'):
            result = {}
            for key, value in obj.__dict__.items():
                result[key] = self._convert_dataclasses_to_dict(value)
            return result
        elif isinstance(obj, list):
            return [self._convert_dataclasses_to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._convert_dataclasses_to_dict(value) for key, value in obj.items()}
        else:
            return obj
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            "environment": self.environment,
            "config_file": self.config_path,
            "components": {
                "data_fetcher": {
                    "cache_enabled": self.config.data_fetcher.cache_enabled,
                    "rate_limit_calls": self.config.data_fetcher.rate_limit_calls,
                    "max_retries": self.config.data_fetcher.max_retries
                },
                "data_validator": {
                    "missing_data_threshold": self.config.data_validator.missing_data_threshold,
                    "outlier_detection_enabled": self.config.data_validator.outlier_detection_enabled,
                    "time_series_validation": self.config.data_validator.time_series_validation
                },
                "lstm_model": {
                    "model_type": self.config.lstm_model.model_type,
                    "sequence_length": self.config.lstm_model.sequence_length,
                    "epochs": self.config.lstm_model.epochs,
                    "dropout_rate": self.config.lstm_model.dropout_rate
                }
            },
            "system": {
                "log_level": self.config.log_level,
                "max_workers": self.config.max_workers,
                "default_symbols": self.config.default_symbols,
                "features": {
                    "enhanced_features": self.config.enable_enhanced_features,
                    "advanced_lstm": self.config.enable_advanced_lstm,
                    "real_time_data": self.config.enable_real_time_data
                }
            }
        }
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration values"""
        try:
            for key, value in updates.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                    self.logger.debug(f"Updated {key} to {value}")
                else:
                    self.logger.warning(f"Unknown configuration key: {key}")
            
            # Re-validate after updates
            self._validate_config()
            
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
            raise


class ConfigurationManager:
    """
    Singleton configuration manager for easy access throughout the application
    """
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigurationManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: Optional[str] = None, environment: str = "development"):
        if not self._initialized:
            self.config_manager = ConfigManager(config_path, environment)
            self._initialized = True
    
    def __getattr__(self, name):
        return getattr(self.config_manager.config, name)
    
    def get_config(self) -> SystemConfig:
        """Get the current system configuration"""
        return self.config_manager.config
    
    def get_config_manager(self) -> ConfigManager:
        """Get the underlying config manager"""
        return self.config_manager


# Create default configuration files
def create_default_config_files():
    """Create default configuration files for different environments"""
    
    # Create config directory
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Development configuration
    dev_config = SystemConfig(
        log_level="DEBUG",
        data_fetcher=DataFetcherConfig(
            cache_enabled=True,
            cache_ttl=1800,  # 30 minutes for development
            rate_limit_calls=30,
            max_retries=2,
            timeout=15
        ),
        data_validator=DataValidatorConfig(
            missing_data_threshold=0.05,  # 5% for development
            outlier_detection_enabled=True,
            time_series_validation=True
        ),
        lstm_model=LSTMModelConfig(
            sequence_length=30,
            epochs=20,
            batch_size=16,
            learning_rate=0.002
        )
    )
    
    # Production configuration
    prod_config = SystemConfig(
        log_level="INFO",
        data_fetcher=DataFetcherConfig(
            cache_enabled=True,
            cache_ttl=7200,  # 2 hours for production
            rate_limit_calls=60,
            max_retries=3,
            timeout=30
        ),
        data_validator=DataValidatorConfig(
            missing_data_threshold=0.02,  # 2% for production
            outlier_detection_enabled=True,
            time_series_validation=True,
            check_stationarity=True
        ),
        lstm_model=LSTMModelConfig(
            sequence_length=60,
            epochs=100,
            batch_size=32,
            learning_rate=0.001,
            use_attention=True,
            use_batch_norm=True
        )
    )
    
    # Save configurations
    for env, config in [("development", dev_config), ("production", prod_config)]:
        config_manager = ConfigManager()
        config_manager.config = config
        config_manager.save_config(f"config/config_{env}.yaml")
    
    print("Default configuration files created:")
    print("  - config/config_development.yaml")
    print("  - config/config_production.yaml")


# Example usage and testing
if __name__ == "__main__":
    # Create default configuration files
    print("Creating default configuration files...")
    create_default_config_files()
    
    # Test configuration loading
    print("\nTesting configuration management...")
    
    # Initialize configuration manager
    config_manager = ConfigurationManager(environment="development")
    
    # Get configuration summary
    summary = config_manager.get_config_summary()
    print("Configuration Summary:")
    print(json.dumps(summary, indent=2))
    
    # Test configuration updates
    print("\nTesting configuration updates...")
    config_manager.update_config({"log_level": "WARNING"})
    
    # Save updated configuration
    config_manager.save_config("config/config_development_updated.yaml")
    print("Updated configuration saved to config/config_development_updated.yaml")
    
    print("\nConfiguration management system testing completed successfully!")