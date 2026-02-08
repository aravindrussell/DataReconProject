"""
Robot Framework Library Wrapper for Data Comparison Framework
Exposes Python libraries as Robot Framework keywords

This library integrates with Robot Framework to provide keyword-driven
interface to the data comparison functionality.

Usage in Robot Framework:
    Library    robot_library.py
    
    Test Case
        ${result}=    Compare DataFrames    ${source}    ${target}    customer_id
"""

import os
import sys
from typing import Dict, List, Any, Optional
from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.Collections import Collections
import pandas as pd

# Add libraries path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libraries'))

from utils import ConfigManager, LoggerSetup, get_logger
from file_reader import FileReader, create_file_reader
from db_reader import DatabaseReader, create_db_reader
from data_compare import DataComparator, create_data_comparator
from report_generator import ReportGenerator, create_report_generator


class DataComparisonLibrary:
    """Robot Framework Library for Data Comparison Framework"""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def __init__(self):
        """Initialize the library"""
        self.builtin = BuiltIn()
        self.collections = Collections()
        
        # Initialize components
        self.config = {}
        self.logger = LoggerSetup.setup_logger('RobotDataComparison')
        self.file_reader = create_file_reader()
        self.comparator = None
        self.report_generator = create_report_generator()
        self.connections = {}  # Store active database connections
        
        self.logger.info("DataComparisonLibrary initialized")
    
    # ==================== Configuration Keywords ====================
    
    @keyword
    def load_configuration(self, config_dir: str = './config') -> Dict[str, Any]:
        """Load configuration from directory"""
        try:
            self.config = ConfigManager.load_all_configs(config_dir)
            self.comparator = create_data_comparator(self.config)
            self.builtin.log('Configuration loaded successfully', 'INFO')
            return self.config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            raise
    
    # ==================== File Reading Keywords ====================
    
    @keyword
    def read_csv_file(self, file_path: str, encoding: str = 'utf-8',
                     delimiter: str = ',', has_header: bool = True) -> pd.DataFrame:
        """Read CSV file and return as DataFrame"""
        try:
            df = self.file_reader.read_csv(file_path, encoding, delimiter, has_header=has_header)
            self.builtin.log(f"CSV file loaded: {len(df)} rows, {len(df.columns)} columns", 'INFO')
            return df
        except Exception as e:
            self.logger.error(f"Failed to read CSV: {str(e)}")
            raise
    
    @keyword
    def read_excel_file(self, file_path: str, sheet_name: str = 'Sheet1',
                       has_header: bool = True) -> pd.DataFrame:
        """Read Excel file and return as DataFrame"""
        try:
            df = self.file_reader.read_excel(file_path, sheet_name, has_header=has_header)
            self.builtin.log(f"Excel file loaded: {len(df)} rows, {len(df.columns)} columns", 'INFO')
            return df
        except Exception as e:
            self.logger.error(f"Failed to read Excel: {str(e)}")
            raise
    
    @keyword
    def read_file_by_config(self, config_key: str) -> pd.DataFrame:
        """Read file using configuration key"""
        try:
            if config_key not in self.config.get('files', {}).get('file_sources', {}):
                raise ValueError(f"File configuration '{config_key}' not found")
            
            file_config = self.config['files']['file_sources'][config_key]
            df = self.file_reader.read_file(file_config)
            self.builtin.log(f"File loaded: {len(df)} rows", 'INFO')
            return df
        except Exception as e:
            self.logger.error(f"Failed to read file: {str(e)}")
            raise
    
    # ==================== Database Keywords ====================
    
    @keyword
    def connect_to_database(self, database_config_key: str, connection_name: str = 'default') -> str:
        """Connect to database and store connection"""
        try:
            if database_config_key not in self.config.get('databases', {}).get('databases', {}):
                raise ValueError(f"Database configuration '{database_config_key}' not found")
            
            db_config = self.config['databases']['databases'][database_config_key]
            reader = create_db_reader(db_config)
            reader.connect()
            
            self.connections[connection_name] = reader
            self.builtin.log(f"Connected to database: {connection_name}", 'INFO')
            return connection_name
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    @keyword
    def read_database_table(self, connection_name: str, table_name: str,
                           columns: Optional[List[str]] = None,
                           limit: Optional[int] = None) -> pd.DataFrame:
        """Read table from database"""
        try:
            if connection_name not in self.connections:
                raise ValueError(f"Connection '{connection_name}' not found")
            
            reader = self.connections[connection_name]
            df = reader.read_table(table_name, columns, limit)
            self.builtin.log(f"Table loaded: {len(df)} rows", 'INFO')
            return df
        except Exception as e:
            self.logger.error(f"Failed to read table: {str(e)}")
            raise
    
    @keyword
    def execute_database_query(self, connection_name: str, query: str) -> pd.DataFrame:
        """Execute SQL query"""
        try:
            if connection_name not in self.connections:
                raise ValueError(f"Connection '{connection_name}' not found")
            
            reader = self.connections[connection_name]
            df = reader.read_query(query)
            self.builtin.log(f"Query executed: {len(df)} rows returned", 'INFO')
            return df
        except Exception as e:
            self.logger.error(f"Failed to execute query: {str(e)}")
            raise
    
    @keyword
    def close_database_connection(self, connection_name: str = 'default') -> None:
        """Close database connection"""
        try:
            if connection_name in self.connections:
                self.connections[connection_name].disconnect()
                del self.connections[connection_name]
                self.builtin.log(f"Connection closed: {connection_name}", 'INFO')
        except Exception as e:
            self.logger.error(f"Failed to close connection: {str(e)}")
    
    # ==================== Comparison Keywords ====================
    
    @keyword
    def compare_dataframes(self, source_df: pd.DataFrame, target_df: pd.DataFrame,
                          primary_keys: List[str],
                          exclude_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Compare two DataFrames"""
        try:
            if not self.comparator:
                self.comparator = create_data_comparator(self.config)
            
            result = self.comparator.compare_dataframes(
                source_df, target_df, primary_keys, exclude_columns
            )
            
            # Convert result to dictionary for Robot Framework
            result_dict = result.to_dict()
            result_dict['status'] = result.status
            result_dict['mismatch_details'] = result.mismatch_details
            
            self.builtin.log(f"Comparison completed: Status={result.status}", 'INFO')
            return result_dict
        except Exception as e:
            self.logger.error(f"Comparison failed: {str(e)}")
            raise
    
    @keyword
    def get_comparison_summary(self, comparison_result: Dict[str, Any]) -> Dict[str, Any]:
        """Get comparison summary"""
        return comparison_result
    
    # ==================== Reporting Keywords ====================
    
    @keyword
    def generate_excel_report(self, comparison_result: Dict[str, Any],
                             source_df: pd.DataFrame, target_df: pd.DataFrame,
                             source_name: str = 'Source',
                             target_name: str = 'Target',
                             filename: Optional[str] = None) -> str:
        """Generate Excel report"""
        try:
            from data_compare import ComparisonResult
            
            # Reconstruct ComparisonResult object
            result = ComparisonResult(
                matched_records=comparison_result.get('matched_records', 0),
                mismatched_records=comparison_result.get('mismatched_records', 0),
                missing_records=comparison_result.get('missing_records', 0),
                extra_records=comparison_result.get('extra_records', 0),
                total_source_records=comparison_result.get('total_source_records', 0),
                total_target_records=comparison_result.get('total_target_records', 0),
                status=comparison_result.get('status', 'UNKNOWN')
            )
            
            report_path = self.report_generator.generate_excel_report(
                result, source_df, target_df, source_name, target_name, filename
            )
            self.builtin.log(f"Excel report generated: {report_path}", 'INFO')
            return report_path
        except Exception as e:
            self.logger.error(f"Failed to generate Excel report: {str(e)}")
            raise
    
    @keyword
    def generate_csv_report(self, comparison_result: Dict[str, Any],
                           source_name: str = 'Source',
                           target_name: str = 'Target',
                           filename: Optional[str] = None) -> str:
        """Generate CSV report"""
        try:
            from data_compare import ComparisonResult
            
            # Reconstruct ComparisonResult object
            result = ComparisonResult(
                matched_records=comparison_result.get('matched_records', 0),
                mismatched_records=comparison_result.get('mismatched_records', 0),
                missing_records=comparison_result.get('missing_records', 0),
                extra_records=comparison_result.get('extra_records', 0),
                total_source_records=comparison_result.get('total_source_records', 0),
                total_target_records=comparison_result.get('total_target_records', 0),
                status=comparison_result.get('status', 'UNKNOWN')
            )
            
            report_path = self.report_generator.generate_csv_summary(
                result, source_name, target_name, filename=filename
            )
            self.builtin.log(f"CSV report generated: {report_path}", 'INFO')
            return report_path
        except Exception as e:
            self.logger.error(f"Failed to generate CSV report: {str(e)}")
            raise
    
    # ==================== Assertion Keywords ====================
    
    @keyword
    def assert_comparison_passed(self, comparison_result: Dict[str, Any]) -> None:
        """Assert comparison status is PASSED"""
        status = comparison_result.get('status', 'UNKNOWN')
        self.builtin.should_be_equal(status, 'PASSED', 
                                    msg='Comparison did not pass')
    
    @keyword
    def assert_no_mismatches(self, comparison_result: Dict[str, Any]) -> None:
        """Assert no mismatched records"""
        mismatches = comparison_result.get('mismatched_records', -1)
        self.builtin.should_be_equal(mismatches, 0, 
                                    msg='Mismatched records found')
    
    @keyword
    def assert_no_missing_records(self, comparison_result: Dict[str, Any]) -> None:
        """Assert no missing records"""
        missing = comparison_result.get('missing_records', -1)
        self.builtin.should_be_equal(missing, 0, 
                                    msg='Missing records found')
    
    @keyword
    def assert_record_counts_match(self, comparison_result: Dict[str, Any]) -> None:
        """Assert source and target record counts match"""
        source_count = comparison_result.get('total_source_records', -1)
        target_count = comparison_result.get('total_target_records', -1)
        self.builtin.should_be_equal(source_count, target_count,
                                    msg='Record counts do not match')
    
    # ==================== Cleanup Keywords ====================
    
    @keyword
    def close_all_connections(self) -> None:
        """Close all database connections"""
        for conn_name in list(self.connections.keys()):
            self.close_database_connection(conn_name)
        self.builtin.log('All connections closed', 'INFO')
    
    @keyword
    def cleanup_framework(self) -> None:
        """Cleanup all resources"""
        self.close_all_connections()
        self.logger.info("Framework cleanup completed")
