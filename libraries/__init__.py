"""
Data Comparison Framework Package
Version 1.0.0
"""

from .utils import (
    ConfigManager,
    LoggerSetup,
    DataCleaner,
    DataValidator,
    get_logger
)
from .db_reader import DatabaseReader, create_db_reader
from .file_reader import FileReader, create_file_reader
from .data_compare import DataComparator, ComparisonResult, create_data_comparator
from .report_generator import ReportGenerator, create_report_generator

__all__ = [
    'ConfigManager',
    'LoggerSetup',
    'DataCleaner',
    'DataValidator',
    'get_logger',
    'DatabaseReader',
    'create_db_reader',
    'FileReader',
    'create_file_reader',
    'DataComparator',
    'ComparisonResult',
    'create_data_comparator',
    'ReportGenerator',
    'create_report_generator'
]

__version__ = '1.0.0'
__author__ = 'Data Testing Team'
