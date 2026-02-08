"""
Utility functions for Data Comparison Framework
Handles: logging, config parsing, data cleaning, conversions
"""

import os
import logging
import yaml
import json
from datetime import datetime
import pandas as pd
from typing import Any, Dict, List, Optional, Tuple
import traceback


class ConfigManager:
    """Manages configuration loading from YAML files"""
    
    @staticmethod
    def load_yaml(config_path: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config if config else {}
        except FileNotFoundError:
            raise Exception(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise Exception(f"Error parsing YAML file {config_path}: {str(e)}")
    
    @staticmethod
    def load_all_configs(config_dir: str = "./config") -> Dict[str, Any]:
        """Load all configuration files from config directory"""
        configs = {}
        try:
            db_config_path = os.path.join(config_dir, "db_config.yaml")
            file_config_path = os.path.join(config_dir, "file_config.yaml")
            comparison_config_path = os.path.join(config_dir, "comparison_rules.yaml")
            
            if os.path.exists(db_config_path):
                configs['databases'] = ConfigManager.load_yaml(db_config_path)
            if os.path.exists(file_config_path):
                configs['files'] = ConfigManager.load_yaml(file_config_path)
            if os.path.exists(comparison_config_path):
                configs['comparison'] = ConfigManager.load_yaml(comparison_config_path)
            
            return configs
        except Exception as e:
            raise Exception(f"Error loading configurations: {str(e)}")
    
    @staticmethod
    def get_env_variable(var_name: str, default: str = None) -> str:
        """Get environment variable with optional default"""
        return os.getenv(var_name, default)


class LoggerSetup:
    """Configures logging for the framework"""
    
    _loggers = {}
    
    @staticmethod
    def setup_logger(name: str, log_level: str = "INFO", 
                    log_file: Optional[str] = None) -> logging.Logger:
        """Setup and return a logger instance"""
        if name in LoggerSetup._loggers:
            return LoggerSetup._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, log_level.upper()))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_level.upper()))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        LoggerSetup._loggers[name] = logger
        return logger


class DataCleaner:
    """Utility functions for data cleaning and normalization"""
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame, 
                       strip_whitespace: bool = True,
                       treat_empty_as_null: bool = True) -> pd.DataFrame:
        """Clean and normalize DataFrame"""
        df = df.copy()
        
        # Strip whitespace from string columns
        if strip_whitespace:
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].apply(
                    lambda x: x.strip() if isinstance(x, str) else x
                )
        
        # Treat empty strings as NaN
        if treat_empty_as_null:
            df = df.replace('', None)
        
        return df
    
    @staticmethod
    def normalize_string(value: str, case_sensitive: bool = False, 
                        strip: bool = True) -> str:
        """Normalize string for comparison"""
        if not isinstance(value, str):
            return value
        
        if strip:
            value = value.strip()
        
        if not case_sensitive:
            value = value.lower()
        
        return value
    
    @staticmethod
    def compare_values(val1: Any, val2: Any, 
                      numeric_tolerance: float = 0.01,
                      case_sensitive: bool = False,
                      treat_null_equal: bool = True) -> bool:
        """Compare two values with various options"""
        # Handle NULL values
        is_val1_null = pd.isna(val1)
        is_val2_null = pd.isna(val2)
        
        if is_val1_null and is_val2_null:
            return treat_null_equal
        
        if is_val1_null or is_val2_null:
            return False
        
        # Compare numeric values with tolerance
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            return abs(val1 - val2) <= numeric_tolerance
        
        # Compare string values
        if isinstance(val1, str) and isinstance(val2, str):
            val1 = DataCleaner.normalize_string(val1, case_sensitive=case_sensitive)
            val2 = DataCleaner.normalize_string(val2, case_sensitive=case_sensitive)
            return val1 == val2
        
        # Direct comparison for other types
        return val1 == val2


class DataValidator:
    """Validates data structure and consistency"""
    
    @staticmethod
    def validate_primary_keys(df: pd.DataFrame, primary_keys: List[str]) -> bool:
        """Verify primary keys exist and are unique"""
        missing_keys = [key for key in primary_keys if key not in df.columns]
        if missing_keys:
            raise ValueError(f"Primary key columns not found: {missing_keys}")
        
        df_check = df[primary_keys]
        if df_check.isnull().any().any():
            raise ValueError("Primary key columns contain NULL values")
        
        if df_check.duplicated().any():
            raise ValueError("Primary key columns contain duplicate values")
        
        return True
    
    @staticmethod
    def validate_columns_exist(df: pd.DataFrame, columns: List[str], 
                              df_name: str = "DataFrame") -> List[str]:
        """Check if columns exist in DataFrame, return missing columns"""
        missing = [col for col in columns if col not in df.columns]
        if missing:
            logging.warning(f"Missing columns in {df_name}: {missing}")
        return missing
    
    @staticmethod
    def get_column_dtypes(df: pd.DataFrame) -> Dict[str, str]:
        """Get data types of all columns"""
        return df.dtypes.astype(str).to_dict()


class ReportMetadata:
    """Manages metadata for reports"""
    
    @staticmethod
    def generate_metadata(source_name: str, target_name: str,
                         source_record_count: int, target_record_count: int,
                         comparison_type: str) -> Dict[str, Any]:
        """Generate metadata for comparison report"""
        return {
            'execution_timestamp': datetime.now().isoformat(),
            'source_name': source_name,
            'target_name': target_name,
            'source_record_count': source_record_count,
            'target_record_count': target_record_count,
            'comparison_type': comparison_type,
            'framework_version': '1.0.0',
            'python_version': pd.__version__
        }
    
    @staticmethod
    def format_metadata_for_report(metadata: Dict[str, Any]) -> str:
        """Format metadata as readable string"""
        return json.dumps(metadata, indent=2)


class FileUtils:
    """File system utilities"""
    
    @staticmethod
    def ensure_directory_exists(directory: str) -> str:
        """Create directory if it doesn't exist"""
        os.makedirs(directory, exist_ok=True)
        return directory
    
    @staticmethod
    def generate_report_filename(prefix: str, extension: str, 
                                include_timestamp: bool = True) -> str:
        """Generate unique report filename"""
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{prefix}_{timestamp}.{extension}"
        return f"{prefix}.{extension}"
    
    @staticmethod
    def safe_read_file(file_path: str) -> str:
        """Safely read file contents"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Error reading file {file_path}: {str(e)}")


class ExceptionHandler:
    """Centralized exception handling"""
    
    @staticmethod
    def handle_exception(exception: Exception, logger: logging.Logger,
                        raise_error: bool = True) -> Optional[str]:
        """Handle exception with logging"""
        error_message = str(exception)
        stack_trace = traceback.format_exc()
        
        logger.error(f"Exception: {error_message}")
        logger.debug(f"Stack trace:\n{stack_trace}")
        
        if raise_error:
            raise exception
        
        return error_message


# Convenience function to get logger
def get_logger(name: str) -> logging.Logger:
    """Get or create logger"""
    if name not in LoggerSetup._loggers:
        LoggerSetup.setup_logger(name)
    return LoggerSetup._loggers[name]
