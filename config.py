"""
Configuration management for Traffic Violation Detection System
"""

import json
import os
from typing import Dict, Any

class Config:
    """Configuration class for managing system settings"""
    
    DEFAULT_CONFIG = {
        # Model paths
        'vehicle_detection_model': 'models/yolov8n.pt',
        'helmet_detection_model': 'models/helmet_detector.pt',
        'anpr_model': 'models/anpr_model.pt',
        
        # Detection thresholds
        'vehicle_detection_threshold': 0.5,
        'helmet_detection_threshold': 0.6,
        'triple_riding_threshold': 0.7,
        'plate_detection_threshold': 0.5,
        
        # Processing settings
        'frame_skip': 5,  # Process every nth frame for videos
        'resize_width': 640,  # Resize frames for faster processing
        'confidence_threshold': 0.5,
        
        # ANPR settings
        'ocr_confidence_threshold': 0.6,
        'plate_char_whitelist': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
        'min_plate_width': 80,
        'min_plate_height': 20,
        
        # Violation settings
        'location': 'Traffic Junction - Main Street',
        'fine_amounts': {
            'no_helmet': 500,
            'triple_riding': 1000,
            'signal_jump': 500,
            'overspeeding': 2000
        },
        
        # Database settings
        'database_path': 'data/violations.db',
        'backup_enabled': True,
        'backup_interval': 3600,  # seconds
        
        # Output settings
        'save_violation_images': True,
        'violation_images_path': 'data/violations/',
        'output_video_fps': 30,
        
        # Logging
        'log_level': 'INFO',
        'log_file': 'logs/system.log'
    }
    
    def __init__(self, config_path: str = None):
        """Initialize configuration
        
        Args:
            config_path: Path to configuration JSON file
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
        
        self._ensure_directories()
    
    def load_config(self, config_path: str):
        """Load configuration from JSON file
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                self.config.update(user_config)
            print(f"Configuration loaded from: {config_path}")
        except Exception as e:
            print(f"Error loading config file: {e}")
            print("Using default configuration")
    
    def save_config(self, config_path: str):
        """Save current configuration to JSON file
        
        Args:
            config_path: Path to save configuration
        """
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"Configuration saved to: {config_path}")
        except Exception as e:
            print(f"Error saving config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        self.config.update(updates)
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        directories = [
            'models',
            'data',
            'data/violations',
            'logs',
            'outputs'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def get_model_path(self, model_type: str) -> str:
        """Get model path for specific type
        
        Args:
            model_type: Type of model ('vehicle', 'helmet', 'anpr')
            
        Returns:
            Path to model file
        """
        model_paths = {
            'vehicle': self.get('vehicle_detection_model'),
            'helmet': self.get('helmet_detection_model'),
            'anpr': self.get('anpr_model')
        }
        
        return model_paths.get(model_type, '')
    
    def get_fine_amount(self, violation_type: str) -> int:
        """Get fine amount for violation type
        
        Args:
            violation_type: Type of violation
            
        Returns:
            Fine amount in local currency
        """
        return self.get('fine_amounts', {}).get(violation_type, 0)
    
    def is_violation(self, confidence: float, threshold_key: str = None) -> bool:
        """Check if detection meets violation threshold
        
        Args:
            confidence: Detection confidence
            threshold_key: Key for threshold in config
            
        Returns:
            True if meets threshold
        """
        if threshold_key:
            threshold = self.get(threshold_key, self.get('confidence_threshold'))
        else:
            threshold = self.get('confidence_threshold')
        
        return confidence >= threshold
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return json.dumps(self.config, indent=2)
