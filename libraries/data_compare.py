"""
Data Comparison Module for Data Comparison Framework
Handles: record-level, row-level, and column-level comparisons
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from utils import get_logger, DataCleaner, DataValidator
from dataclasses import dataclass, field
from enum import Enum


class MatchStatus(Enum):
    """Enum for record match status"""
    MATCHED = "MATCHED"
    MISMATCHED = "MISMATCHED"
    MISSING_IN_TARGET = "MISSING_IN_TARGET"
    EXTRA_IN_TARGET = "EXTRA_IN_TARGET"


@dataclass
class ComparisonResult:
    """Data class to hold comparison results"""
    matched_records: int = 0
    mismatched_records: int = 0
    missing_records: int = 0
    extra_records: int = 0
    total_source_records: int = 0
    total_target_records: int = 0
    mismatch_details: List[Dict[str, Any]] = field(default_factory=list)
    missing_record_keys: List[Any] = field(default_factory=list)
    extra_record_keys: List[Any] = field(default_factory=list)
    status: str = "PASSED"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'matched_records': self.matched_records,
            'mismatched_records': self.mismatched_records,
            'missing_records': self.missing_records,
            'extra_records': self.extra_records,
            'total_source_records': self.total_source_records,
            'total_target_records': self.total_target_records,
            'status': self.status,
            'mismatch_count': len(self.mismatch_details),
            'missing_count': len(self.missing_record_keys),
            'extra_count': len(self.extra_record_keys)
        }


class DataComparator:
    """Main class for comparing DataFrames"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = get_logger('DataComparator')
        self.comparison_config = config.get('comparison_config', {})
    
    def compare_dataframes(self, source_df: pd.DataFrame, target_df: pd.DataFrame,
                          primary_keys: List[str],
                          exclude_columns: Optional[List[str]] = None,
                          comparison_options: Optional[Dict[str, Any]] = None) -> ComparisonResult:
        """Main comparison function - compares two DataFrames"""
        
        self.logger.info(
            f"Starting comparison: Source ({len(source_df)} rows) vs "
            f"Target ({len(target_df)} rows)"
        )
        
        # Validate primary keys
        try:
            DataValidator.validate_primary_keys(source_df, primary_keys)
            DataValidator.validate_primary_keys(target_df, primary_keys)
        except ValueError as e:
            self.logger.error(f"Primary key validation failed: {str(e)}")
            raise
        
        result = ComparisonResult(
            total_source_records=len(source_df),
            total_target_records=len(target_df)
        )
        
        options = comparison_options or self.comparison_config.get('column_comparisons', {})
        exclude_cols = exclude_columns or self.comparison_config.get('exclude_columns', [])
        
        # Perform comparisons
        self._compare_record_counts(source_df, target_df, result)
        self._find_missing_records(source_df, target_df, primary_keys, result)
        self._find_extra_records(source_df, target_df, primary_keys, result)
        self._compare_values(source_df, target_df, primary_keys, exclude_cols, 
                           options, result)
        
        # Determine overall status
        thresholds = self.comparison_config.get('thresholds', {})
        result.status = self._determine_status(result, thresholds)
        
        self.logger.info(f"Comparison completed. Status: {result.status}")
        self.logger.info(
            f"Summary - Matched: {result.matched_records}, "
            f"Mismatched: {result.mismatched_records}, "
            f"Missing: {result.missing_records}, Extra: {result.extra_records}"
        )
        
        return result
    
    def _compare_record_counts(self, source_df: pd.DataFrame, target_df: pd.DataFrame,
                               result: ComparisonResult) -> None:
        """Compare record counts between source and target"""
        source_count = len(source_df)
        target_count = len(target_df)
        
        if source_count != target_count:
            self.logger.warning(
                f"Record count mismatch: Source={source_count}, Target={target_count}"
            )
    
    def _find_missing_records(self, source_df: pd.DataFrame, target_df: pd.DataFrame,
                              primary_keys: List[str], result: ComparisonResult) -> None:
        """Find records in source but not in target"""
        source_keys = set(map(tuple, source_df[primary_keys].values))
        target_keys = set(map(tuple, target_df[primary_keys].values))
        
        missing_keys = source_keys - target_keys
        result.missing_records = len(missing_keys)
        result.missing_record_keys = list(missing_keys)
        
        if missing_keys:
            self.logger.warning(f"Found {len(missing_keys)} missing records in target")
    
    def _find_extra_records(self, source_df: pd.DataFrame, target_df: pd.DataFrame,
                           primary_keys: List[str], result: ComparisonResult) -> None:
        """Find records in target but not in source"""
        source_keys = set(map(tuple, source_df[primary_keys].values))
        target_keys = set(map(tuple, target_df[primary_keys].values))
        
        extra_keys = target_keys - source_keys
        result.extra_records = len(extra_keys)
        result.extra_record_keys = list(extra_keys)
        
        if extra_keys:
            self.logger.warning(f"Found {len(extra_keys)} extra records in target")
    
    def _compare_values(self, source_df: pd.DataFrame, target_df: pd.DataFrame,
                       primary_keys: List[str], exclude_columns: List[str],
                       comparison_options: Dict[str, Any],
                       result: ComparisonResult) -> None:
        """Compare values in matching records"""
        
        # Prepare DataFrames for comparison
        source_indexed = source_df.set_index(primary_keys)
        target_indexed = target_df.set_index(primary_keys)
        
        # Find common keys
        common_keys = set(source_indexed.index) & set(target_indexed.index)
        
        # Determine columns to compare
        source_cols = set(source_df.columns) - set(primary_keys)
        target_cols = set(target_df.columns) - set(primary_keys)
        compare_cols = (source_cols & target_cols) - set(exclude_columns)
        
        mismatches = []
        matched = 0
        
        for key in common_keys:
            source_row = source_indexed.loc[key]
            target_row = target_indexed.loc[key]
            
            row_mismatches = []
            
            for col in compare_cols:
                if not DataCleaner.compare_values(
                    source_row[col], target_row[col],
                    numeric_tolerance=comparison_options.get('numeric_tolerance', 0.01),
                    case_sensitive=comparison_options.get('case_sensitive', False),
                    treat_null_equal=True
                ):
                    row_mismatches.append({
                        'column': col,
                        'source_value': source_row[col],
                        'target_value': target_row[col]
                    })
            
            if row_mismatches:
                mismatches.append({
                    'key': key,
                    'column_mismatches': row_mismatches
                })
            else:
                matched += 1
        
        result.matched_records = matched
        result.mismatched_records = len(mismatches)
        result.mismatch_details = mismatches[:100]  # Limit details to first 100
    
    def _determine_status(self, result: ComparisonResult,
                         thresholds: Dict[str, Any]) -> str:
        """Determine overall comparison status based on thresholds"""
        
        # Check missing records
        if result.missing_records > thresholds.get('max_missing_records', 10):
            return "FAILED"
        
        # Check record count difference
        if result.total_source_records > 0:
            count_diff_pct = abs(result.total_source_records - result.total_target_records) / result.total_source_records * 100
            if count_diff_pct > thresholds.get('max_record_diff_percentage', 1.0):
                return "FAILED"
        
        # Check mismatch percentage
        total_compared = result.matched_records + result.mismatched_records
        if total_compared > 0:
            mismatch_pct = result.mismatched_records / total_compared * 100
            if mismatch_pct > thresholds.get('max_mismatch_percentage', 5.0):
                return "FAILED"
        
        return "PASSED"
    
    def compare_single_row(self, source_row: pd.Series, target_row: pd.Series,
                          exclude_columns: Optional[List[str]] = None,
                          comparison_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compare single rows"""
        
        exclude_cols = exclude_columns or []
        options = comparison_options or {}
        
        mismatches = []
        matched_columns = []
        
        for col in source_row.index:
            if col in exclude_cols:
                continue
            
            if col not in target_row.index:
                mismatches.append({
                    'column': col,
                    'source_value': source_row[col],
                    'target_value': 'MISSING',
                    'reason': 'Column not found in target'
                })
            else:
                if DataCleaner.compare_values(
                    source_row[col], target_row[col],
                    numeric_tolerance=options.get('numeric_tolerance', 0.01),
                    case_sensitive=options.get('case_sensitive', False)
                ):
                    matched_columns.append(col)
                else:
                    mismatches.append({
                        'column': col,
                        'source_value': source_row[col],
                        'target_value': target_row[col]
                    })
        
        return {
            'status': 'MATCHED' if not mismatches else 'MISMATCHED',
            'matched_columns': matched_columns,
            'mismatches': mismatches
        }
    
    def generate_comparison_summary(self, result: ComparisonResult) -> Dict[str, Any]:
        """Generate summary of comparison results"""
        total_records = result.total_source_records
        
        return {
            'summary': {
                'total_source_records': result.total_source_records,
                'total_target_records': result.total_target_records,
                'matched_records': result.matched_records,
                'mismatched_records': result.mismatched_records,
                'missing_records': result.missing_records,
                'extra_records': result.extra_records,
                'overall_status': result.status
            },
            'statistics': {
                'match_percentage': (result.matched_records / (result.matched_records + result.mismatched_records) * 100
                                    if (result.matched_records + result.mismatched_records) > 0 else 0),
                'mismatch_percentage': (result.mismatched_records / (result.matched_records + result.mismatched_records) * 100
                                       if (result.matched_records + result.mismatched_records) > 0 else 0),
                'missing_percentage': (result.missing_records / total_records * 100 if total_records > 0 else 0)
            }
        }


# Utility function to create comparator
def create_data_comparator(config: Dict[str, Any] = None) -> DataComparator:
    """Factory function to create DataComparator"""
    return DataComparator(config)
