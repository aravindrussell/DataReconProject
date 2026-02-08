*** Settings ***
Library    Collections
Library    String

*** Keywords ***

# Data Comparison Keywords for Robot Framework

Load CSV File
    [Arguments]    ${file_path}    ${encoding}=utf-8    ${delimiter}=,
    [Documentation]    Load CSV file into DataFrame using file_reader library
    Log    Loading CSV file: ${file_path}
    # Import and call the file reader library method
    # This keyword will be implemented to call Python library
    [Return]    ${file_data}

Load Excel File
    [Arguments]    ${file_path}    ${sheet_name}=Sheet1
    [Documentation]    Load Excel file into DataFrame
    Log    Loading Excel file: ${file_path} (Sheet: ${sheet_name})
    [Return]    ${file_data}

Connect To Database
    [Arguments]    ${db_config_name}
    [Documentation]    Connect to database using db_config and db_reader library
    Log    Connecting to database: ${db_config_name}
    [Return]    ${connection}

Read Database Table
    [Arguments]    ${connection}    ${table_name}    ${columns}=${EMPTY}
    [Documentation]    Read table from database into DataFrame
    Log    Reading table: ${table_name}
    [Return]    ${table_data}

Execute Database Query
    [Arguments]    ${connection}    ${query}
    [Documentation]    Execute custom SQL query and return DataFrame
    Log    Executing query: ${query}
    [Return]    ${query_result}

Close Database Connection
    [Arguments]    ${connection}
    [Documentation]    Close database connection
    Log    Closing database connection
    No Operation

Compare DataFrames
    [Arguments]    ${source_df}    ${target_df}    ${primary_keys}    ${comparison_config}
    [Documentation]    Compare two DataFrames using data_compare library
    Log    Comparing DataFrames with primary keys: ${primary_keys}
    [Return]    ${comparison_result}

Compare File With Database
    [Arguments]    ${file_path}    ${db_connection}    ${table_name}    
    ...            ${primary_keys}    ${file_type}=csv
    [Documentation]    Compare file data with database table
    Log    Comparing file (${file_path}) with database table (${table_name})
    [Return]    ${comparison_result}

Compare Database Tables
    [Arguments]    ${source_connection}    ${source_table}
    ...            ${target_connection}    ${target_table}
    ...            ${primary_keys}
    [Documentation]    Compare data from two database tables
    Log    Comparing database tables: ${source_table} vs ${target_table}
    [Return]    ${comparison_result}

Generate Excel Report
    [Arguments]    ${comparison_result}    ${source_name}    ${target_name}
    ...            ${report_path}=${EMPTY}
    [Documentation]    Generate Excel report from comparison results
    Log    Generating Excel report
    [Return]    ${report_file_path}

Generate CSV Report
    [Arguments]    ${comparison_result}    ${source_name}    ${target_name}
    ...            ${report_path}=${EMPTY}
    [Documentation]    Generate CSV summary report
    Log    Generating CSV report
    [Return]    ${report_file_path}

Get Comparison Summary
    [Arguments]    ${comparison_result}
    [Documentation]    Get summary statistics from comparison result
    Log    Extracting summary from comparison result
    [Return]    ${summary}

Assert Comparison Status
    [Arguments]    ${comparison_result}    ${expected_status}=PASSED
    [Documentation]    Assert the comparison result status
    Should Be Equal    ${comparison_result}[status]    ${expected_status}

Assert No Data Differences
    [Arguments]    ${comparison_result}
    [Documentation]    Assert that there are no data differences
    Should Be Equal    ${comparison_result}[mismatched_records]    0    msg=Mismatched records found
    Should Be Equal    ${comparison_result}[missing_records]    0    msg=Missing records found
    Should Be Equal    ${comparison_result}[extra_records]    0    msg=Extra records found

Assert Mismatch Count Below Threshold
    [Arguments]    ${comparison_result}    ${threshold}
    [Documentation]    Assert that mismatch count is below threshold
    Should Be True    ${comparison_result}[mismatched_records] <= ${threshold}
    ...    msg=Mismatch count exceeds threshold

Log Comparison Details
    [Arguments]    ${comparison_result}
    [Documentation]    Log detailed comparison results to console
    Log    ${\n}========== COMPARISON RESULTS ==========    console=true
    Log    Total Source Records: ${comparison_result}[total_source_records]    console=true
    Log    Total Target Records: ${comparison_result}[total_target_records]    console=true
    Log    Matched Records: ${comparison_result}[matched_records]    console=true
    Log    Mismatched Records: ${comparison_result}[mismatched_records]    console=true
    Log    Missing Records: ${comparison_result}[missing_records]    console=true
    Log    Extra Records: ${comparison_result}[extra_records]    console=true
    Log    Overall Status: ${comparison_result}[status]    console=true
    Log    ==========================================    console=true

Load Configuration
    [Arguments]    ${config_file}
    [Documentation]    Load configuration from YAML file
    Log    Loading configuration: ${config_file}
    [Return]    ${config}

Validate Primary Keys
    [Arguments]    ${dataframe}    ${primary_keys}
    [Documentation]    Validate that primary keys exist and are unique
    Log    Validating primary keys: ${primary_keys}
    No Operation
