"""
Quick Start Example - Data Comparison Framework
Demonstrates a complete comparison workflow
"""

import sys
import os

# Add libraries to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libraries'))

from utils import ConfigManager, LoggerSetup, get_logger
from file_reader import FileReader
from db_reader import DatabaseReader
from data_compare import DataComparator
from report_generator import ReportGenerator


def main():
    """Main execution function"""
    
    # Setup logging
    LoggerSetup.setup_logger('main', log_level='INFO', log_file='./logs/quickstart.log')
    logger = get_logger('main')
    
    logger.info("=" * 60)
    logger.info("Data Comparison Framework - Quick Start Example")
    logger.info("=" * 60)
    
    try:
        # Step 1: Load configurations
        logger.info("\n[Step 1] Loading configurations...")
        config = ConfigManager.load_all_configs('./config')
        logger.info("✓ Configurations loaded successfully")
        
        # Step 2: Read CSV file
        logger.info("\n[Step 2] Reading CSV file...")
        file_reader = FileReader()
        
        # Example CSV configuration
        csv_config = {
            'type': 'csv',
            'path': './data/sample_customers.csv',
            'encoding': 'utf-8',
            'delimiter': ',',
            'has_header': True
        }
        
        # For demo purposes, we'll create sample data
        import pandas as pd
        sample_csv_data = pd.DataFrame({
            'customer_id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 
                     'david@example.com', 'eve@example.com'],
            'amount': [100.0, 200.0, 150.0, 300.0, 250.0]
        })
        logger.info(f"✓ Sample CSV data created ({len(sample_csv_data)} rows)")
        
        # Step 3: Create sample database data
        logger.info("\n[Step 3] Creating sample database data...")
        sample_db_data = pd.DataFrame({
            'customer_id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'email': ['alice@example.com', 'bob@example.com', 'charlie@example.com', 
                     'david@example.com', 'eve@example.com'],
            'amount': [100.0, 200.0, 150.5, 300.0, 250.0]  # Note: row 3 has slightly different amount
        })
        logger.info(f"✓ Sample database data created ({len(sample_db_data)} rows)")
        
        # Step 4: Perform comparison
        logger.info("\n[Step 4] Performing data comparison...")
        comparator = DataComparator(config)
        
        comparison_result = comparator.compare_dataframes(
            source_df=sample_csv_data,
            target_df=sample_db_data,
            primary_keys=['customer_id'],
            exclude_columns=[]
        )
        logger.info(f"✓ Comparison completed: Status = {comparison_result.status}")
        
        # Step 5: Log comparison details
        logger.info("\n[Step 5] Comparison Results:")
        logger.info(f"  - Total Source Records: {comparison_result.total_source_records}")
        logger.info(f"  - Total Target Records: {comparison_result.total_target_records}")
        logger.info(f"  - Matched Records: {comparison_result.matched_records}")
        logger.info(f"  - Mismatched Records: {comparison_result.mismatched_records}")
        logger.info(f"  - Missing Records: {comparison_result.missing_records}")
        logger.info(f"  - Extra Records: {comparison_result.extra_records}")
        
        if comparison_result.mismatch_details:
            logger.info(f"\n  Mismatch Details:")
            for mismatch in comparison_result.mismatch_details:
                logger.info(f"    Key: {mismatch['key']}")
                for col_mismatch in mismatch['column_mismatches']:
                    logger.info(f"      - {col_mismatch['column']}: "
                               f"{col_mismatch['source_value']} != {col_mismatch['target_value']}")
        
        # Step 6: Generate reports
        logger.info("\n[Step 6] Generating reports...")
        generator = ReportGenerator('./reports')
        
        excel_report = generator.generate_excel_report(
            comparison_result=comparison_result,
            source_df=sample_csv_data,
            target_df=sample_db_data,
            source_name='CSV_File',
            target_name='Database_Table',
            primary_keys=['customer_id']
        )
        logger.info(f"✓ Excel report generated: {excel_report}")
        
        csv_report = generator.generate_csv_summary(
            comparison_result=comparison_result,
            source_name='CSV_File',
            target_name='Database_Table'
        )
        logger.info(f"✓ CSV report generated: {csv_report}")
        
        # Step 7: Summary
        logger.info("\n[Step 7] Execution Summary:")
        summary = comparator.generate_comparison_summary(comparison_result)
        logger.info(f"  - Match Percentage: {summary['statistics']['match_percentage']:.2f}%")
        logger.info(f"  - Mismatch Percentage: {summary['statistics']['mismatch_percentage']:.2f}%")
        logger.info(f"  - Overall Status: {comparison_result.status}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Quick Start Example Completed Successfully!")
        logger.info("=" * 60)
        
        return 0
    
    except Exception as e:
        logger.error(f"\n✗ Error occurred: {str(e)}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
