"""
File Reader Module for Data Comparison Framework
Supports: CSV and Excel files
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from utils import get_logger
import os


class FileReader:
    """Reads data from CSV and Excel files"""
    
    def __init__(self):
        self.logger = get_logger('FileReader')
    
    def read_csv(self, file_path: str, 
                 encoding: str = 'utf-8',
                 delimiter: str = ',',
                 skip_rows: int = 0,
                 usecols: Optional[List[str]] = None,
                 has_header: bool = True) -> pd.DataFrame:
        """Read CSV file into DataFrame"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            header = 0 if has_header else None
            
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                delimiter=delimiter,
                skiprows=skip_rows,
                usecols=usecols,
                header=header
            )
            
            self.logger.info(
                f"Successfully read CSV file: {file_path} "
                f"({len(df)} rows, {len(df.columns)} columns)"
            )
            return df
        except Exception as e:
            error_msg = f"Failed to read CSV file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def read_excel(self, file_path: str,
                   sheet_name: str = 'Sheet1',
                   skip_rows: int = 0,
                   usecols: Optional[List[str]] = None,
                   has_header: bool = True) -> pd.DataFrame:
        """Read Excel file into DataFrame"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            header = 0 if has_header else None
            
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                skiprows=skip_rows,
                usecols=usecols,
                header=header
            )
            
            self.logger.info(
                f"Successfully read Excel file: {file_path} (Sheet: {sheet_name}) "
                f"({len(df)} rows, {len(df.columns)} columns)"
            )
            return df
        except Exception as e:
            error_msg = f"Failed to read Excel file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def read_multiple_sheets(self, file_path: str,
                            sheet_names: List[str],
                            skip_rows: int = 0,
                            usecols: Optional[List[str]] = None,
                            has_header: bool = True,
                            combine: bool = True) -> pd.DataFrame:
        """Read multiple sheets from Excel and optionally combine"""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            header = 0 if has_header else None
            dfs = []
            
            for sheet_name in sheet_names:
                df = pd.read_excel(
                    file_path,
                    sheet_name=sheet_name,
                    skiprows=skip_rows,
                    usecols=usecols,
                    header=header
                )
                dfs.append(df)
                self.logger.info(f"Read sheet '{sheet_name}': {len(df)} rows")
            
            if combine:
                combined_df = pd.concat(dfs, ignore_index=True)
                self.logger.info(
                    f"Combined {len(sheet_names)} sheets: {len(combined_df)} total rows"
                )
                return combined_df
            else:
                return dfs
        except Exception as e:
            error_msg = f"Failed to read Excel file {file_path}: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def read_file(self, file_config: Dict[str, Any]) -> pd.DataFrame:
        """Read file based on configuration"""
        file_type = file_config.get('type', 'csv').lower()
        file_path = file_config.get('path')
        
        if not file_path:
            raise ValueError("File path not specified in configuration")
        
        try:
            if file_type == 'csv':
                return self.read_csv(
                    file_path=file_path,
                    encoding=file_config.get('encoding', 'utf-8'),
                    delimiter=file_config.get('delimiter', ','),
                    skip_rows=file_config.get('skip_rows', 0),
                    usecols=file_config.get('usecols'),
                    has_header=file_config.get('has_header', True)
                )
            
            elif file_type == 'excel':
                sheet_name = file_config.get('sheet_name', 'Sheet1')
                sheet_names = file_config.get('sheet_names')
                
                if sheet_names:  # Multiple sheets
                    return self.read_multiple_sheets(
                        file_path=file_path,
                        sheet_names=sheet_names,
                        skip_rows=file_config.get('skip_rows', 0),
                        usecols=file_config.get('usecols'),
                        has_header=file_config.get('has_header', True),
                        combine=True
                    )
                else:  # Single sheet
                    return self.read_excel(
                        file_path=file_path,
                        sheet_name=sheet_name,
                        skip_rows=file_config.get('skip_rows', 0),
                        usecols=file_config.get('usecols'),
                        has_header=file_config.get('has_header', True)
                    )
            
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        
        except Exception as e:
            self.logger.error(f"Error reading file: {str(e)}")
            raise


# Utility function to create reader
def create_file_reader() -> FileReader:
    """Factory function to create FileReader"""
    return FileReader()
