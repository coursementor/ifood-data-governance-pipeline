"""
Configuration loader with environment variable support and validation.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import logging
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str
    port: int
    database: str
    username: str
    password: str


@dataclass
class StorageConfig:
    """Storage configuration."""
    provider: str
    bucket: str
    bronze_path: str
    silver_path: str
    gold_path: str


@dataclass
class DataQualityConfig:
    """Data quality configuration."""
    store_backend: str
    validation_frequency: str
    alert_channels: list
    thresholds: Dict[str, float]


@dataclass
class SecurityConfig:
    """Security and privacy configuration."""
    pii_fields: list
    masking: Dict[str, str]
    access_control: Dict[str, Any]


class ConfigLoader:
    """Configuration loader with environment variable substitution."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = Path(config_path)
        self._config = None
        
    def load(self) -> Dict[str, Any]:
        """Load configuration from YAML file with environment variable substitution."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
        with open(self.config_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Substitute environment variables
        content = self._substitute_env_vars(content)
        
        try:
            self._config = yaml.safe_load(content)
            logger.info(f"Configuration loaded from {self.config_path}")
            return self._config
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise
            
    def _substitute_env_vars(self, content: str) -> str:
        """Substitute ${VAR_NAME} patterns with environment variables."""
        pattern = r'\$\{([^}]+)\}'
        
        def replace_var(match):
            var_name = match.group(1)
            default_value = None
            
            # Handle default values: ${VAR_NAME:default_value}
            if ':' in var_name:
                var_name, default_value = var_name.split(':', 1)
                
            value = os.getenv(var_name, default_value)
            if value is None:
                logger.warning(f"Environment variable {var_name} not found")
                return match.group(0)  # Return original if not found
                
            return value
            
        return re.sub(pattern, replace_var, content)
        
    def get_database_config(self, db_name: str) -> DatabaseConfig:
        """Get database configuration."""
        if not self._config:
            self.load()
            
        db_config = self._config.get('databases', {}).get(db_name)
        if not db_config:
            raise ValueError(f"Database configuration for '{db_name}' not found")
            
        return DatabaseConfig(**db_config)
        
    def get_storage_config(self) -> StorageConfig:
        """Get storage configuration."""
        if not self._config:
            self.load()
            
        storage_config = self._config.get('storage', {}).get('data_lake')
        if not storage_config:
            raise ValueError("Storage configuration not found")
            
        return StorageConfig(**storage_config)
        
    def get_data_quality_config(self) -> DataQualityConfig:
        """Get data quality configuration."""
        if not self._config:
            self.load()
            
        dq_config = self._config.get('data_quality', {})
        if not dq_config:
            raise ValueError("Data quality configuration not found")
            
        return DataQualityConfig(
            store_backend=dq_config.get('great_expectations', {}).get('store_backend'),
            validation_frequency=dq_config.get('great_expectations', {}).get('validation_frequency'),
            alert_channels=dq_config.get('great_expectations', {}).get('alert_channels', []),
            thresholds=dq_config.get('thresholds', {})
        )
        
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration."""
        if not self._config:
            self.load()
            
        security_config = self._config.get('security', {})
        if not security_config:
            raise ValueError("Security configuration not found")
            
        return SecurityConfig(**security_config)
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        if not self._config:
            self.load()
            
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value


# Global configuration instance
config = ConfigLoader()


def get_config() -> ConfigLoader:
    """Get global configuration instance."""
    return config
