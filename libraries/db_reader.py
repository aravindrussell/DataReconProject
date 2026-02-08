"""
Database Reader Module for Data Comparison Framework
Supports: Oracle, SQL Server, MySQL, PostgreSQL
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from utils import get_logger, DataValidator, ExceptionHandler
import os


class DatabaseConnector:
    """Base class for database connections"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.config = db_config
        self.logger = get_logger(self.__class__.__name__)
        self.connection = None
    
    def _resolve_env_var(self, value: str) -> str:
        """Resolve environment variables in configuration"""
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            return os.getenv(env_var, value)
        return value
    
    def connect(self) -> Any:
        """Establish database connection - override in subclasses"""
        raise NotImplementedError
    
    def disconnect(self) -> None:
        """Close database connection"""
        if self.connection:
            try:
                self.connection.close()
                self.logger.info("Database connection closed")
            except Exception as e:
                self.logger.warning(f"Error closing connection: {str(e)}")
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL query and return DataFrame"""
        raise NotImplementedError
    
    def get_table_as_dataframe(self, table_name: str, 
                               columns: Optional[List[str]] = None,
                               limit: Optional[int] = None) -> pd.DataFrame:
        """Read table into DataFrame"""
        raise NotImplementedError


class PostgreSQLConnector(DatabaseConnector):
    """PostgreSQL Database Connector"""
    
    def connect(self) -> Any:
        """Establish PostgreSQL connection"""
        try:
            import psycopg2
            from psycopg2 import pool
            
            # Resolve environment variables
            host = self._resolve_env_var(self.config.get('host', 'localhost'))
            port = self.config.get('port', 5432)
            database = self._resolve_env_var(self.config.get('database'))
            username = self._resolve_env_var(self.config.get('username'))
            password = self._resolve_env_var(self.config.get('password'))
            
            self.connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
                connect_timeout=self.config.get('connection_timeout', 30)
            )
            self.logger.info(f"Connected to PostgreSQL: {host}:{port}/{database}")
            return self.connection
        except Exception as e:
            error_msg = f"Failed to connect to PostgreSQL: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute PostgreSQL query"""
        if not self.connection:
            self.connect()
        
        try:
            df = pd.read_sql_query(query, self.connection)
            self.logger.info(f"Query executed successfully. Rows: {len(df)}")
            return df
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            raise
    
    def get_table_as_dataframe(self, table_name: str, 
                               columns: Optional[List[str]] = None,
                               limit: Optional[int] = None) -> pd.DataFrame:
        """Read PostgreSQL table into DataFrame"""
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table_name}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query)


class MySQLConnector(DatabaseConnector):
    """MySQL Database Connector"""
    
    def connect(self) -> Any:
        """Establish MySQL connection"""
        try:
            from mysql.connector import connect
            
            host = self._resolve_env_var(self.config.get('host', 'localhost'))
            port = self.config.get('port', 3306)
            database = self._resolve_env_var(self.config.get('database'))
            username = self._resolve_env_var(self.config.get('username'))
            password = self._resolve_env_var(self.config.get('password'))
            
            self.connection = connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password,
                connection_timeout=self.config.get('connection_timeout', 30)
            )
            self.logger.info(f"Connected to MySQL: {host}:{port}/{database}")
            return self.connection
        except Exception as e:
            error_msg = f"Failed to connect to MySQL: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute MySQL query"""
        if not self.connection:
            self.connect()
        
        try:
            df = pd.read_sql_query(query, self.connection)
            self.logger.info(f"Query executed successfully. Rows: {len(df)}")
            return df
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            raise
    
    def get_table_as_dataframe(self, table_name: str, 
                               columns: Optional[List[str]] = None,
                               limit: Optional[int] = None) -> pd.DataFrame:
        """Read MySQL table into DataFrame"""
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table_name}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query)


class MSSQLConnector(DatabaseConnector):
    """SQL Server Database Connector"""
    
    def connect(self) -> Any:
        """Establish SQL Server connection"""
        try:
            import pyodbc
            
            host = self._resolve_env_var(self.config.get('host', 'localhost'))
            port = self.config.get('port', 1433)
            database = self._resolve_env_var(self.config.get('database'))
            username = self._resolve_env_var(self.config.get('username'))
            password = self._resolve_env_var(self.config.get('password'))
            
            connection_string = (
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={host},{port};'
                f'DATABASE={database};'
                f'UID={username};'
                f'PWD={password}'
            )
            
            self.connection = pyodbc.connect(connection_string, timeout=30)
            self.logger.info(f"Connected to SQL Server: {host}:{port}/{database}")
            return self.connection
        except Exception as e:
            error_msg = f"Failed to connect to SQL Server: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute SQL Server query"""
        if not self.connection:
            self.connect()
        
        try:
            df = pd.read_sql_query(query, self.connection)
            self.logger.info(f"Query executed successfully. Rows: {len(df)}")
            return df
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            raise
    
    def get_table_as_dataframe(self, table_name: str, 
                               columns: Optional[List[str]] = None,
                               limit: Optional[int] = None) -> pd.DataFrame:
        """Read SQL Server table into DataFrame"""
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table_name}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        return self.execute_query(query)


class OracleConnector(DatabaseConnector):
    """Oracle Database Connector"""
    
    def _resolve_env_var(self, value: str) -> str:
        """Resolve environment variables in configuration"""
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var = value[2:-1]
            return os.getenv(env_var, value)
        return value
    
    def connect(self) -> Any:
        """Establish Oracle connection using compatibility shim.

        This will prefer `cx_Oracle` if present, otherwise falls back to
        `oracledb` via `libraries.oracle_compat`.
        """
        try:
            from .oracle_compat import makedsn, connect as oracle_connect, driver_name

            host = self._resolve_env_var(self.config.get('host', 'localhost'))
            port = self.config.get('port', 1521)
            database = self._resolve_env_var(self.config.get('database'))
            username = self._resolve_env_var(self.config.get('username'))
            password = self._resolve_env_var(self.config.get('password'))

            dsn = makedsn(host, port, service_name=database)
            self.connection = oracle_connect(user=username, password=password, dsn=dsn)
            self.logger.info(f"Connected to Oracle ({driver_name()}): {host}:{port}/{database}")
            return self.connection
        except Exception as e:
            error_msg = f"Failed to connect to Oracle: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute Oracle query"""
        if not self.connection:
            self.connect()
        
        try:
            df = pd.read_sql_query(query, self.connection)
            self.logger.info(f"Query executed successfully. Rows: {len(df)}")
            return df
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            raise
    
    def get_table_as_dataframe(self, table_name: str, 
                               columns: Optional[List[str]] = None,
                               limit: Optional[int] = None) -> pd.DataFrame:
        """Read Oracle table into DataFrame"""
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table_name}"
        
        if limit:
            query += f" ROWNUM <= {limit}"
        
        return self.execute_query(query)


class DatabaseReader:
    """Main class for reading data from databases"""
    
    CONNECTORS = {
        'postgresql': PostgreSQLConnector,
        'mysql': MySQLConnector,
        'mssql': MSSQLConnector,
        'oracle': OracleConnector
    }
    
    def __init__(self, db_config: Dict[str, Any]):
        self.config = db_config
        self.logger = get_logger('DatabaseReader')
        self.connector = None
    
    def connect(self) -> DatabaseConnector:
        """Create and establish database connection"""
        engine = self.config.get('engine', '').lower()
        
        if engine not in self.CONNECTORS:
            raise ValueError(f"Unsupported database engine: {engine}")
        
        connector_class = self.CONNECTORS[engine]
        self.connector = connector_class(self.config)
        self.connector.connect()
        return self.connector
    
    def read_table(self, table_name: str, 
                   columns: Optional[List[str]] = None,
                   limit: Optional[int] = None) -> pd.DataFrame:
        """Read table from database"""
        if not self.connector:
            self.connect()
        
        try:
            df = self.connector.get_table_as_dataframe(table_name, columns, limit)
            self.logger.info(f"Successfully read table '{table_name}': {len(df)} rows")
            return df
        except Exception as e:
            error_msg = f"Failed to read table '{table_name}': {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def read_query(self, query: str) -> pd.DataFrame:
        """Execute custom SQL query"""
        if not self.connector:
            self.connect()
        
        try:
            df = self.connector.execute_query(query)
            self.logger.info(f"Query executed: {len(df)} rows returned")
            return df
        except Exception as e:
            error_msg = f"Query execution failed: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def disconnect(self) -> None:
        """Close database connection"""
        if self.connector:
            self.connector.disconnect()
            self.logger.info("Database connection closed")


# Utility function to create connector from config
def create_db_reader(db_config: Dict[str, Any]) -> DatabaseReader:
    """Factory function to create DatabaseReader"""
    return DatabaseReader(db_config)
