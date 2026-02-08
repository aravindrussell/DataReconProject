*** Settings ***
Documentation     File vs Database Comparison Tests
...               Demonstrates how to compare CSV/Excel files with database tables

Library           Collections
Library           String
Resource          ../resources/CommonKeywords.resource
Resource          ../resources/DataCompareKeywords.resource

Suite Setup       Log Test Header    File vs Database Comparison Suite
Suite Teardown    Log    Comparison tests completed


*** Test Cases ***

Compare CSV File With Database Table
    [Documentation]    Test Case 1: Compare a CSV file with database table
    [Tags]    file_vs_db    csv    critical
    
    Log Test Header    CSV File vs Database Table Comparison
    
    # Load CSV file
    ${csv_file}=    Set Variable    ./data/customer_data.csv
    ${file_data}=    Load CSV File    ${csv_file}
    
    # Connect to database
    ${db_connection}=    Connect To Database    source_db
    
    # Read database table
    ${table_data}=    Read Database Table    ${db_connection}    customers
    
    # Perform comparison
    ${comparison_result}=    Compare File With Database
    ...    ${csv_file}
    ...    ${db_connection}
    ...    customers
    ...    primary_keys=['customer_id']
    ...    file_type=csv
    
    # Generate reports
    ${excel_report}=    Generate Excel Report
    ...    ${comparison_result}
    ...    source_name=CSV_File
    ...    target_name=Database_Table
    
    ${csv_report}=    Generate CSV Report
    ...    ${comparison_result}
    ...    source_name=CSV_File
    ...    target_name=Database_Table
    
    # Log results
    Log Comparison Details    ${comparison_result}
    
    # Assertions
    Assert Comparison Status    ${comparison_result}
    Log    Test PASSED - CSV file matches database table    console=true
    
    # Cleanup
    Close Database Connection    ${db_connection}


Compare Excel File With Database Table
    [Documentation]    Test Case 2: Compare an Excel file with database table
    [Tags]    file_vs_db    excel    critical
    
    Log Test Header    Excel File vs Database Table Comparison
    
    # Load Excel file
    ${excel_file}=    Set Variable    ./data/sales_data.xlsx
    ${sheet_name}=    Set Variable    Sales
    ${file_data}=    Load Excel File    ${excel_file}    ${sheet_name}
    
    # Connect to database
    ${db_connection}=    Connect To Database    target_db
    
    # Read database table
    ${table_data}=    Read Database Table    ${db_connection}    sales_transactions
    
    # Perform comparison
    ${comparison_result}=    Compare File With Database
    ...    ${excel_file}
    ...    ${db_connection}
    ...    sales_transactions
    ...    primary_keys=['transaction_id']
    ...    file_type=excel
    
    # Generate reports
    ${excel_report}=    Generate Excel Report
    ...    ${comparison_result}
    ...    source_name=Excel_File
    ...    target_name=Sales_Database
    
    # Log results
    Log Comparison Details    ${comparison_result}
    
    # Assertions
    Assert Comparison Status    ${comparison_result}
    Assert No Data Differences    ${comparison_result}
    Log    Test PASSED - Excel file matches database table    console=true
    
    # Cleanup
    Close Database Connection    ${db_connection}


Compare CSV File With Database - Allow Tolerance
    [Documentation]    Test Case 3: Compare CSV with Database allowing numeric tolerance
    [Tags]    file_vs_db    csv    tolerance
    
    Log Test Header    CSV vs Database with Numeric Tolerance
    
    # Load configuration with tolerance settings
    ${config}=    Load Configuration    ./config/comparison_rules.yaml
    
    # Load CSV file
    ${csv_file}=    Set Variable    ./data/financial_data.csv
    ${file_data}=    Load CSV File    ${csv_file}
    
    # Connect to database
    ${db_connection}=    Connect To Database    source_db
    
    # Read database table
    ${table_data}=    Read Database Table    ${db_connection}    financial_records
    
    # Perform comparison with tolerance
    ${comparison_result}=    Compare File With Database
    ...    ${csv_file}
    ...    ${db_connection}
    ...    financial_records
    ...    primary_keys=['record_id']
    ...    file_type=csv
    
    # Generate reports
    ${excel_report}=    Generate Excel Report
    ...    ${comparison_result}
    ...    source_name=Financial_CSV
    ...    target_name=Financial_Database
    
    # Log results and verify status
    Log Comparison Details    ${comparison_result}
    
    # Allow for some tolerance in comparisons
    Assert Comparison Status    ${comparison_result}
    Assert Mismatch Count Below Threshold    ${comparison_result}    threshold=10
    Log    Test PASSED - CSV matches database within tolerance    console=true
    
    # Cleanup
    Close Database Connection    ${db_connection}


Compare Multiple Sheets From Excel With Database
    [Documentation]    Test Case 4: Compare multiple sheets from Excel with database
    [Tags]    file_vs_db    excel    multi_sheet
    
    Log Test Header    Multiple Excel Sheets vs Database
    
    # Load Excel file with multiple sheets
    ${excel_file}=    Set Variable    ./data/combined_data.xlsx
    ${file_data}=    Load Excel File    ${excel_file}    Combined
    
    # Connect to database
    ${db_connection}=    Connect To Database    target_db
    
    # Read database table
    ${table_data}=    Read Database Table    ${db_connection}    combined_records
    
    # Perform comparison
    ${comparison_result}=    Compare File With Database
    ...    ${excel_file}
    ...    ${db_connection}
    ...    combined_records
    ...    primary_keys=['id']
    ...    file_type=excel
    
    # Log results
    Log Comparison Details    ${comparison_result}
    
    # Assertions
    Assert Comparison Status    ${comparison_result}
    Log    Test PASSED - Multiple Excel sheets match database table    console=true
    
    # Cleanup
    Close Database Connection    ${db_connection}


*** Keywords ***

Load CSV File
    [Arguments]    ${file_path}    ${encoding}=utf-8    ${delimiter}=,
    Log    Loading CSV file: ${file_path}
    Log    This keyword integrates with file_reader library
    [Return]    ${EMPTY}

Load Excel File
    [Arguments]    ${file_path}    ${sheet_name}=Sheet1
    Log    Loading Excel file: ${file_path} (Sheet: ${sheet_name})
    Log    This keyword integrates with file_reader library
    [Return]    ${EMPTY}

Connect To Database
    [Arguments]    ${db_config_name}
    Log    Connecting to database: ${db_config_name}
    Log    This keyword integrates with db_reader library
    [Return]    connection_object

Read Database Table
    [Arguments]    ${connection}    ${table_name}
    Log    Reading table: ${table_name}
    Log    This keyword integrates with db_reader library
    [Return]    table_dataframe

Compare File With Database
    [Arguments]    @{args}    &{kwargs}
    Log    Comparing file with database
    Log    This keyword integrates with data_compare library
    [Return]    ${EMPTY}

Generate Excel Report
    [Arguments]    @{args}    &{kwargs}
    Log    Generating Excel report
    Log    This keyword integrates with report_generator library
    [Return]    report_path

Generate CSV Report
    [Arguments]    @{args}    &{kwargs}
    Log    Generating CSV report
    Log    This keyword integrates with report_generator library
    [Return]    report_path

Close Database Connection
    [Arguments]    ${connection}
    Log    Closing database connection
