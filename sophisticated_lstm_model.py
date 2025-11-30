#!/usr/bin/env python3
"""
Sophisticated LSTM Model
Advanced LSTM neural network implementation with comprehensive features and validation
"""

import pandas as pd
import numpy as np
import logging
import warnings
import pickle
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split

warnings.filterwarnings("ignore")

# Try to import TensorFlow/Keras
TENSORFLOW_AVAILABLE = False
TENSORFLOW_ERROR = None
KerasModels = None
KerasLayers = None
KerasOptimizers = None
KerasCallbacks = None
KerasLosses = None

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential, Model, load_model
    from tensorflow.keras.layers import Dense, Dropout, LSTM, GRU, Bidirectional, Attention, MultiHeadAttention, LayerNormalization, BatchNormalization
    from tensorflow.keras.optimizers import Adam, RMSprop, SGD
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard
    from tensorflow.keras.losses import MeanSquaredError, MeanAbsoluteError, Huber
    from tensorflow.keras.regularizers import l1, l2, l1_l2
    from tensorflow.keras.constraints import max_norm
    from tensorflow.keras import mixed_precision
    
    TENSORFLOW_AVAILABLE = True
    KerasModels = Sequential
    KerasLayers = {
        'Dense': Dense, 
        'Dropout': Dropout, 
        'LSTM': LSTM, 
        'GRU': GRU,
        'Bidirectional': Bidirectional,
        'LayerNormalization': LayerNormalization,
        'BatchNormalization': BatchNormalization
    }
    KerasOptimizers = {'Adam': Adam, 'RMSprop': RMSprop, 'SGD': SGD}
    KerasCallbacks = {
        'EarlyStopping': EarlyStopping, 
        'ModelCheckpoint': ModelCheckpoint, 
        'ReduceLROnPlateau': ReduceLROnPlateau,
        'TensorBoard': TensorBoard
    }
    KerasLosses = {
        'MSE': MeanSquaredError(), 
        'MAE': MeanAbsoluteError(), 
        'Huber': Huber()
    }
    
    # Enable mixed precision for better performance
    try:
        mixed_precision.set_global_policy('mixed_float16')
    except:
        pass  # Fallback if mixed precision not available
        
except ImportError as e:
    TENSORFLOW_ERROR = str(e)
    logging.warning(f"TensorFlow/Keras not available: {TENSORFLOW_ERROR}")
    logging.warning("LSTM model will return None values")


@dataclass
class ModelConfig:
    """Configuration class for LSTM model parameters"""
    # Architecture parameters
    sequence_length: int = 60
    features: int = 1
    lstm_units: List[int] = None
    dense_units: List[int] = None
    dropout_rate: float = 0.2
    recurrent_dropout: float = 0.2
    l1_reg: float = 0.0
    l2_reg: float = 0.01
    
    # Training parameters
    epochs: int = 100
    batch_size: int = 32
    validation_split: float = 0.2
    early_stopping_patience: int = 15
    learning_rate: float = 0.001
    optimizer: str = 'Adam'
    loss_function: str = 'MSE'
    
    # Model type
    model_type: str = 'LSTM'  # LSTM, GRU, BidirectionalLSTM
    use_attention: bool = False
    use_batch_norm: bool = True
    use_layer_norm: bool = False
    
    # Data preprocessing
    scaler_type: str = 'minmax'  # minmax, standard
    feature_columns: List[str] = None
    
    def __post_init__(self):
        if self.lstm_units is None:
            self.lstm_units = [50, 50, 50]
        if self.dense_units is None:
            self.dense_units = [25]
        if self.feature_columns is None:
            self.feature_columns = ['Close']


@dataclass
class TrainingMetrics:
    """Container for training metrics"""
    train_loss: List[float]
    val_loss: List[float]
    train_mae: List[float]
    val_mae: List[float]
    epochs_trained: int
    training_time: float
    final_train_loss: float
    final_val_loss: float
    final_train_mae: float
    final_val_mae: float
    r2_score: float


class SequencePreprocessor:
    """Advanced sequence preprocessing for time series data"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.scalers = {}
        self.feature_columns = config.feature_columns
        
    def create_sequences(self, data: pd.DataFrame, target_column: str = 'Close') -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM training
        
        Args:
            data: Input DataFrame
            target_column: Column to predict
            
        Returns:
            Tuple of (X_sequences, y_sequences)
        """
        if target_column not in data.columns:
            raise ValueError(f"Target column '{target_column}' not found in data")
        
        # Select features
        if self.feature_columns:
            feature_data = data[self.feature_columns].copy()
        else:
            feature_data = data.select_dtypes(include=[np.number]).copy()
        
        # Scale features
        scaled_data = self._scale_features(feature_data)
        
        # Create sequences
        X, y = [], []
        for i in range(self.config.sequence_length, len(scaled_data)):
            X.append(scaled_data[i-self.config.sequence_length:i].values)
            y.append(scaled_data[i, feature_data.columns.get_loc(target_column)])
        
        return np.array(X), np.array(y)
    
    def _scale_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Scale features using configured scaler"""
        scaled_data = data.copy()
        
        for column in data.columns:
            if column not in self.scalers:
                if self.config.scaler_type == 'minmax':
                    self.scalers[column] = MinMaxScaler()
                elif self.config.scaler_type == 'standard':
                    self.scalers[column] = StandardScaler()
                else:
                    raise ValueError(f"Unknown scaler type: {self.config.scaler_type}")
                
                # Fit scaler and transform data
                scaled_values = self.scalers[column].fit_transform(data[column].values.reshape(-1, 1))
                scaled_data[column] = scaled_values.flatten()
            else:
                # Transform using existing scaler
                scaled_values = self.scalers[column].transform(data[column].values.reshape(-1, 1))
                scaled_data[column] = scaled_values.flatten()
        
        return scaled_data
    
    def inverse_scale_predictions(self, predictions: np.ndarray, target_column: str = 'Close') -> np.ndarray:
        """Inverse scale predictions to original scale"""
        if target_column in self.scalers:
            return self.scalers[target_column].inverse_transform(predictions.reshape(-1, 1)).flatten()
        return predictions
    
    def create_forecast_sequences(self, data: pd.DataFrame, n_predictions: int = 1) -> np.ndarray:
        """Create sequences for forecasting"""
        if len(data) < self.config.sequence_length:
            raise ValueError(f"Insufficient data: need at least {self.config.sequence_length} points")
        
        # Get the last sequence
        last_sequence = data[-self.config.sequence_length:].values
        
        # Reshape for model input
        return last_sequence.reshape(1, self.config.sequence_length, len(data.columns))


class SophisticatedLSTMModel:
    """
    Sophisticated LSTM model with advanced architecture and comprehensive features
    """
    
    def __init__(self, config: Optional[ModelConfig] = None, debug: bool = False):
        """
        Initialize the sophisticated LSTM model
        
        Args:
            config: Model configuration
            debug: Enable debug logging
        """
        self.config = config or ModelConfig()
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        
        # Check TensorFlow availability
        if not TENSORFLOW_AVAILABLE:
            self.logger.error("Sophisticated LSTM Model requires TensorFlow/Keras")
            self.logger.error(f"Import error: {TENSORFLOW_ERROR}")
            return
        
        # Initialize components
        self.preprocessor = SequencePreprocessor(self.config)
        self.model = None
        self.training_history = None
        self.model_metadata = {}
        
        # Model paths
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        self.logger.info("Sophisticated LSTM Model initialized")
        if self.debug:
            self.logger.debug(f"Configuration: {self.config}")
    
    def _build_model(self, input_shape: Tuple[int, int]) -> Model:
        """
        Build sophisticated LSTM model architecture
        
        Args:
            input_shape: Shape of input data (sequence_length, features)
            
        Returns:
            Compiled Keras model
        """
        model = Sequential()
        
        # Add regularization
        kernel_regularizer = l1_l2(l1=self.config.l1_reg, l2=self.config.l2_reg)
        recurrent_regularizer = l1_l2(l1=self.config.l1_reg, l2=self.config.l2_reg)
        
        # Input layer
        model.add(tf.keras.Input(shape=input_shape))
        
        # Build LSTM layers based on configuration
        for i, units in enumerate(self.config.lstm_units):
            return_sequences = i < len(self.config.lstm_units) - 1
            
            # Choose layer type
            if self.config.model_type == 'LSTM':
                layer_class = LSTM
            elif self.config.model_type == 'GRU':
                layer_class = GRU
            elif self.config.model_type == 'BidirectionalLSTM':
                layer_class = lambda **kwargs: Bidirectional(LSTM(**kwargs))
            else:
                raise ValueError(f"Unknown model type: {self.config.model_type}")
            
            # Add layer
            lstm_layer = layer_class(
                units=units,
                return_sequences=return_sequences,
                dropout=self.config.dropout_rate,
                recurrent_dropout=self.config.recurrent_dropout,
                kernel_regularizer=kernel_regularizer,
                recurrent_regularizer=recurrent_regularizer,
                name=f"{self.config.model_type.lower()}_{i+1}"
            )
            
            model.add(lstm_layer)
            
            # Add normalization
            if self.config.use_batch_norm and i < len(self.config.lstm_units) - 1:
                model.add(BatchNormalization(name=f"batch_norm_{i+1}"))
            elif self.config.use_layer_norm:
                model.add(LayerNormalization(name=f"layer_norm_{i+1}"))
        
        # Add attention mechanism if requested
        if self.config.use_attention:
            model.add(MultiHeadAttention(num_heads=8, key_dim=32, name="multihead_attention"))
            model.add(LayerNormalization(name="attention_norm"))
        
        # Add dense layers
        for i, units in enumerate(self.config.dense_units):
            model.add(Dense(
                units=units,
                activation='relu',
                kernel_regularizer=kernel_regularizer,
                name=f"dense_{i+1}"
            ))
            
            # Add dropout between dense layers
            if i < len(self.config.dense_units) - 1:
                model.add(Dropout(self.config.dropout_rate, name=f"dense_dropout_{i+1}"))
        
        # Output layer
        model.add(Dense(1, activation='linear', name="output"))
        
        # Compile model
        optimizer = KerasOptimizers[self.config.optimizer](learning_rate=self.config.learning_rate)
        loss_function = KerasLosses[self.config.loss_function]
        
        model.compile(
            optimizer=optimizer,
            loss=loss_function,
            metrics=['mae', 'mse']
        )
        
        if self.debug:
            model.summary()
        
        self.logger.info(f"Built {self.config.model_type} model with {model.count_params()} parameters")
        
        return model
    
    def validate_input_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data before training
        
        Args:
            df: Input DataFrame
        """
        # Check if DataFrame is empty
        if df.empty:
            raise ValueError("Input DataFrame is empty")
        
        # Check required columns
        missing_columns = set(self.config.feature_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Check sufficient data for sequences
        min_required = self.config.sequence_length + 10  # Need sequence_length + some buffer
        if len(df) < min_required:
            raise ValueError(f"Insufficient data: need at least {min_required} rows, got {len(df)}")
        
        # Check for too many missing values
        for col in self.config.feature_columns:
            null_ratio = df[col].isnull().sum() / len(df)
            if null_ratio > 0.1:  # More than 10% missing
                raise ValueError(f"Too many missing values in {col}: {null_ratio:.2%}")
        
        self.logger.info("Input data validation passed")
    
    def train(self, df: pd.DataFrame, target_column: str = 'Close', 
             validation_data: Optional[pd.DataFrame] = None,
             callbacks: Optional[List] = None) -> TrainingMetrics:
        """
        Train the sophisticated LSTM model
        
        Args:
            df: Training DataFrame
            target_column: Column to predict
            validation_data: Optional validation DataFrame
            callbacks: Optional list of Keras callbacks
            
        Returns:
            TrainingMetrics object with training results
        """
        if not TENSORFLOW_AVAILABLE:
            raise ImportError("TensorFlow/Keras not available for training")
        
        start_time = datetime.now()
        
        try:
            # Validate input data
            self.validate_input_data(df)
            
            # Create sequences
            X, y = self.preprocessor.create_sequences(df, target_column)
            
            # Split data
            if validation_data is not None:
                X_val, y_val = self.preprocessor.create_sequences(validation_data, target_column)
                validation_data_tuple = (X_val, y_val)
            else:
                X_train, X_val, y_train, y_val = train_test_split(
                    X, y, test_size=self.config.validation_split, shuffle=False
                )
                X, y = X_train, y_train
                validation_data_tuple = (X_val, y_val)
            
            # Build model
            input_shape = (self.config.sequence_length, len(self.config.feature_columns))
            self.model = self._build_model(input_shape)
            
            # Setup callbacks
            if callbacks is None:
                callbacks = [
                    KerasCallbacks['EarlyStopping'](
                        monitor='val_loss',
                        patience=self.config.early_stopping_patience,
                        restore_best_weights=True,
                        verbose=1
                    ),
                    KerasCallbacks['ReduceLROnPlateau'](
                        monitor='val_loss',
                        factor=0.5,
                        patience=10,
                        min_lr=1e-7,
                        verbose=1
                    ),
                    KerasCallbacks['ModelCheckpoint'](
                        filepath=str(self.models_dir / "best_model.h5"),
                        monitor='val_loss',
                        save_best_only=True,
                        save_weights_only=False,
                        verbose=1
                    )
                ]
            
            # Train model
            self.logger.info(f"Training {self.config.model_type} model...")
            self.logger.info(f"Training samples: {len(X)}, Validation samples: {len(validation_data_tuple[0])}")
            
            self.training_history = self.model.fit(
                X, y,
                epochs=self.config.epochs,
                batch_size=self.config.batch_size,
                validation_data=validation_data_tuple,
                callbacks=callbacks,
                verbose=1 if self.debug else 2,
                shuffle=False  # Important for time series
            )
            
            # Calculate training time
            training_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate final metrics
            final_train_loss = self.training_history.history['loss'][-1]
            final_val_loss = self.training_history.history['val_loss'][-1]
            final_train_mae = self.training_history.history['mae'][-1]
            final_val_mae = self.training_history.history['val_mae'][-1]
            
            # Calculate R² score on validation set
            val_predictions = self.model.predict(validation_data_tuple[0])
            val_predictions_original = self.preprocessor.inverse_scale_predictions(
                val_predictions.flatten(), target_column
            )
            val_actual_original = self.preprocessor.inverse_scale_predictions(
                validation_data_tuple[1], target_column
            )
            r2 = r2_score(val_actual_original, val_predictions_original)
            
            # Create metrics object
            metrics = TrainingMetrics(
                train_loss=self.training_history.history['loss'],
                val_loss=self.training_history.history['val_loss'],
                train_mae=self.training_history.history['mae'],
                val_mae=self.training_history.history['val_mae'],
                epochs_trained=len(self.training_history.history['loss']),
                training_time=training_time,
                final_train_loss=final_train_loss,
                final_val_loss=final_val_loss,
                final_train_mae=final_train_mae,
                final_val_mae=final_val_mae,
                r2_score=r2
            )
            
            # Store model metadata
            self.model_metadata = {
                'config': self.config.__dict__,
                'training_date': datetime.now().isoformat(),
                'training_time_seconds': training_time,
                'epochs_trained': metrics.epochs_trained,
                'final_metrics': {
                    'train_loss': final_train_loss,
                    'val_loss': final_val_loss,
                    'train_mae': final_train_mae,
                    'val_mae': final_val_mae,
                    'r2_score': r2
                }
            }
            
            self.logger.info(f"Training completed in {training_time:.2f} seconds")
            self.logger.info(f"Final validation loss: {final_val_loss:.4f}, R²: {r2:.4f}")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Training failed: {str(e)}")
            raise
    
    def predict(self, df: pd.DataFrame, target_column: str = 'Close', 
               return_confidence: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray]]:
        """
        Make predictions with the trained model
        
        Args:
            df: DataFrame for prediction
            target_column: Column to predict
            return_confidence: Whether to return confidence intervals
            
        Returns:
            Predictions or tuple of (predictions, confidence_intervals)
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        try:
            # Create prediction sequences
            X, _ = self.preprocessor.create_sequences(df, target_column)
            
            # Make predictions
            predictions_scaled = self.model.predict(X, verbose=0)
            predictions = self.preprocessor.inverse_scale_predictions(
                predictions_scaled.flatten(), target_column
            )
            
            if return_confidence:
                # Calculate confidence intervals using ensemble approach
                confidence_intervals = self._calculate_confidence_intervals(X, target_column)
                return predictions, confidence_intervals
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Prediction failed: {str(e)}")
            raise
    
    def forecast(self, df: pd.DataFrame, n_steps: int = 5, target_column: str = 'Close') -> np.ndarray:
        """
        Forecast future values using the trained model
        
        Args:
            df: Historical data for forecasting
            n_steps: Number of steps to forecast
            target_column: Column to predict
            
        Returns:
            Array of forecasted values
        """
        if self.model is None:
            raise ValueError("Model not trained yet. Call train() first.")
        
        try:
            # Get the last sequence from data
            last_sequence = self.preprocessor.create_forecast_sequences(df)
            
            forecasts = []
            current_sequence = last_sequence.copy()
            
            for _ in range(n_steps):
                # Predict next value
                prediction_scaled = self.model.predict(current_sequence.reshape(1, current_sequence.shape[0], current_sequence.shape[1]), verbose=0)
                
                # Inverse scale prediction
                prediction = self.preprocessor.inverse_scale_predictions(
                    prediction_scaled.flatten(), target_column
                )[0]
                
                forecasts.append(prediction)
                
                # Update sequence for next prediction
                # This is a simplified approach - in practice, you'd want more sophisticated sequence updating
                new_row = current_sequence[-1].copy()
                new_row[-1] = prediction_scaled[0, 0]  # Update target feature
                current_sequence = np.vstack([current_sequence[1:], new_row])
            
            return np.array(forecasts)
            
        except Exception as e:
            self.logger.error(f"Forecasting failed: {str(e)}")
            raise
    
    def _calculate_confidence_intervals(self, X: np.ndarray, target_column: str, 
                                      n_bootstrap: int = 100) -> np.ndarray:
        """
        Calculate prediction confidence intervals using bootstrap
        
        Args:
            X: Input sequences
            target_column: Target column name
            n_bootstrap: Number of bootstrap samples
            
        Returns:
            Confidence intervals array (lower_bound, upper_bound)
        """
        try:
            # Generate multiple predictions with slight variations
            predictions = []
            
            for _ in range(n_bootstrap):
                # Add small noise to input for bootstrap
                X_noisy = X + np.random.normal(0, 0.01, X.shape)
                pred_scaled = self.model.predict(X_noisy, verbose=0)
                pred = self.preprocessor.inverse_scale_predictions(
                    pred_scaled.flatten(), target_column
                )
                predictions.append(pred)
            
            predictions = np.array(predictions)
            
            # Calculate confidence intervals (95% CI)
            lower_bound = np.percentile(predictions, 2.5, axis=0)
            upper_bound = np.percentile(predictions, 97.5, axis=0)
            
            return np.column_stack([lower_bound, upper_bound])
            
        except Exception as e:
            self.logger.warning(f"Confidence interval calculation failed: {e}")
            # Return None if calculation fails
            return np.column_stack([np.full(len(X), np.nan), np.full(len(X), np.nan)])
    
    def save_model(self, filepath: str, include_metadata: bool = True) -> None:
        """
        Save trained model and metadata
        
        Args:
            filepath: Path to save the model
            include_metadata: Whether to include model metadata
        """
        if self.model is None:
            raise ValueError("No model to save. Train the model first.")
        
        try:
            # Save the Keras model
            model_path = f"{filepath}_model.h5"
            self.model.save(model_path)
            
            # Save preprocessing components
            preprocessor_path = f"{filepath}_preprocessor.pkl"
            with open(preprocessor_path, 'wb') as f:
                pickle.dump(self.preprocessor, f)
            
            # Save metadata if requested
            if include_metadata:
                metadata_path = f"{filepath}_metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(self.model_metadata, f, indent=2, default=str)
            
            self.logger.info(f"Model saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save model: {e}")
            raise
    
    def load_model(self, filepath: str, include_metadata: bool = True) -> None:
        """
        Load trained model and metadata
        
        Args:
            filepath: Path to load the model from
            include_metadata: Whether to load model metadata
        """
        try:
            # Load the Keras model
            model_path = f"{filepath}_model.h5"
            self.model = load_model(model_path)
            
            # Load preprocessing components
            preprocessor_path = f"{filepath}_preprocessor.pkl"
            with open(preprocessor_path, 'rb') as f:
                self.preprocessor = pickle.load(f)
            
            # Load metadata if requested
            if include_metadata:
                metadata_path = f"{filepath}_metadata.json"
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        self.model_metadata = json.load(f)
            
            self.logger.info(f"Model loaded from {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            raise
    
    def plot_training_history(self, save_path: Optional[str] = None) -> None:
        """
        Plot training history
        
        Args:
            save_path: Optional path to save the plot
        """
        if self.training_history is None:
            raise ValueError("No training history available. Train the model first.")
        
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # Loss plot
            ax1.plot(self.training_history.history['loss'], label='Training Loss')
            ax1.plot(self.training_history.history['val_loss'], label='Validation Loss')
            ax1.set_title('Model Loss')
            ax1.set_xlabel('Epoch')
            ax1.set_ylabel('Loss')
            ax1.legend()
            ax1.grid(True)
            
            # MAE plot
            ax2.plot(self.training_history.history['mae'], label='Training MAE')
            ax2.plot(self.training_history.history['val_mae'], label='Validation MAE')
            ax2.set_title('Model MAE')
            ax2.set_xlabel('Epoch')
            ax2.set_ylabel('MAE')
            ax2.legend()
            ax2.grid(True)
            
            # Learning rate plot (if available)
            if 'lr' in self.training_history.history:
                ax3.plot(self.training_history.history['lr'])
                ax3.set_title('Learning Rate')
                ax3.set_xlabel('Epoch')
                ax3.set_ylabel('Learning Rate')
                ax3.set_yscale('log')
                ax3.grid(True)
            else:
                ax3.text(0.5, 0.5, 'Learning Rate\nNot Available', ha='center', va='center', transform=ax3.transAxes)
            
            # Summary statistics
            final_metrics = {
                'Final Train Loss': f"{self.training_history.history['loss'][-1]:.4f}",
                'Final Val Loss': f"{self.training_history.history['val_loss'][-1]:.4f}",
                'Final Train MAE': f"{self.training_history.history['mae'][-1]:.4f}",
                'Final Val MAE': f"{self.training_history.history['val_mae'][-1]:.4f}",
                'Total Epochs': str(len(self.training_history.history['loss']))
            }
            
            ax4.axis('off')
            ax4.text(0.1, 0.9, 'Training Summary', fontsize=14, fontweight='bold', transform=ax4.transAxes)
            y_pos = 0.8
            for metric, value in final_metrics.items():
                ax4.text(0.1, y_pos, f'{metric}: {value}', fontsize=10, transform=ax4.transAxes)
                y_pos -= 0.1
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                self.logger.info(f"Training history plot saved to {save_path}")
            
            if self.debug:
                plt.show()
            else:
                plt.close()
                
        except Exception as e:
            self.logger.error(f"Failed to plot training history: {e}")
            raise
    
    def get_model_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive model summary
        
        Returns:
            Dictionary with model summary information
        """
        if self.model is None:
            return {'error': 'No model available'}
        
        summary = {
            'model_type': self.config.model_type,
            'total_parameters': self.model.count_params(),
            'trainable_parameters': sum([tf.keras.backend.count_params(w) for w in self.model.trainable_weights]),
            'non_trainable_parameters': sum([tf.keras.backend.count_params(w) for w in self.model.non_trainable_weights]),
            'architecture': [],
            'training_metadata': self.model_metadata
        }
        
        # Extract architecture details
        for i, layer in enumerate(self.model.layers):
            layer_info = {
                'name': layer.name,
                'type': layer.__class__.__name__,
                'output_shape': str(layer.output_shape),
                'parameters': layer.count_params()
            }
            summary['architecture'].append(layer_info)
        
        return summary
    
    def is_available(self) -> bool:
        """
        Check if LSTM model is available (TensorFlow is installed)
        
        Returns:
            True if model can be used
        """
        return TENSORFLOW_AVAILABLE


# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if not TENSORFLOW_AVAILABLE:
        print("TensorFlow not available. Install with: pip install tensorflow")
        exit(1)
    
    # Create sample data
    print("Creating sample stock data...")
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    
    # Generate realistic stock data
    base_price = 100
    prices = []
    volumes = []
    
    for i in range(500):
        # Add trend and noise
        trend = 0.001 * i  # Slight upward trend
        noise = np.random.normal(0, 2)
        base_price = max(base_price + trend + noise, 10)  # Ensure positive price
        
        prices.append(base_price)
        volumes.append(np.random.randint(100000, 1000000))
    
    # Create OHLC data
    data = {
        'Open': [p * (1 + np.random.uniform(-0.02, 0.02)) for p in prices],
        'High': [p * (1 + np.random.uniform(0, 0.03)) for p in prices],
        'Low': [p * (1 + np.random.uniform(-0.03, 0)) for p in prices],
        'Close': prices,
        'Volume': volumes
    }
    
    df = pd.DataFrame(data, index=dates)
    
    # Initialize sophisticated model
    print("Initializing sophisticated LSTM model...")
    config = ModelConfig(
        sequence_length=60,
        epochs=50,
        batch_size=32,
        lstm_units=[100, 50, 25],
        dense_units=[25, 10],
        dropout_rate=0.3,
        early_stopping_patience=10,
        model_type='LSTM',
        use_batch_norm=True,
        feature_columns=['Close', 'Volume']
    )
    
    model = SophisticatedLSTMModel(config, debug=True)
    
    # Split data for training and validation
    train_size = int(0.8 * len(df))
    train_data = df.iloc[:train_size]
    val_data = df.iloc[train_size:]
    
    print(f"Training data: {len(train_data)} samples")
    print(f"Validation data: {len(val_data)} samples")
    
    # Train the model
    print("Training sophisticated LSTM model...")
    metrics = model.train(train_data, target_column='Close', validation_data=val_data)
    
    print(f"Training completed!")
    print(f"Final validation loss: {metrics.final_val_loss:.4f}")
    print(f"Final validation MAE: {metrics.final_val_mae:.4f}")
    print(f"R² Score: {metrics.r2_score:.4f}")
    print(f"Training time: {metrics.training_time:.2f} seconds")
    
    # Make predictions
    print("Making predictions...")
    predictions = model.predict(val_data, target_column='Close')
    
    # Calculate prediction metrics
    actual = val_data['Close'].values[config.sequence_length:]
    mae = mean_absolute_error(actual, predictions)
    mse = mean_squared_error(actual, predictions)
    rmse = np.sqrt(mse)
    
    print(f"Prediction MAE: {mae:.4f}")
    print(f"Prediction RMSE: {rmse:.4f}")
    
    # Forecast future values
    print("Forecasting future values...")
    forecasts = model.forecast(df, n_steps=5, target_column='Close')
    print(f"Future predictions: {forecasts}")
    
    # Plot training history
    print("Generating training plots...")
    model.plot_training_history(save_path="training_history.png")
    
    # Save model
    print("Saving model...")
    model.save_model("sophisticated_lstm_model")
    
    # Get model summary
    print("Model Summary:")
    summary = model.get_model_summary()
    print(f"Total parameters: {summary['total_parameters']:,}")
    print(f"Trainable parameters: {summary['trainable_parameters']:,}")
    
    print("\nSophisticated LSTM model testing completed successfully!")