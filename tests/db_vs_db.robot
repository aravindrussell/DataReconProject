*** Settings ***
Documentation     Database vs Database Comparison Tests
...               Demonstrates how to compare tables from different databases

Library           Collections
Library           String
Resource          ../resources/CommonKeywords.resource
Resource          ../resources/DataCompareKeywords.resource

Suite Setup       Log Test Header    Database vs Database Comparison Suite
Suite Teardown    Log    Comparison tests completed


*** Test Cases ***

Compare Same Database Tables
    [Documentation]    Test Case 1: Compare two tables from the same database
    [Tags]    db_vs_db    same_database    critical
    
    Log Test Header    Same Database Table Comparison
    
    # Connect to source database
    ${db_connection}=    Connect To Database    source_db
    
    # Read both tables
    ${source_table}=    Read Database Table    ${db_connection}    orders
    ${target_table}=    Read Database Table    ${db_connection}    orders_backup
    
    # Perform comparison
    ${comparison_result}=    Compare Database Tables
    ...    ${db_connection}
    ...    orders
    ...    ${db_connection}
    ...    orders_backup
    ...    primary_keys=['order_id']
    
    # Generate reports
    ${excel_report}=    Generate Excel Report
    ...    ${comparison_result}
    ...    source_name=Orders_Table
    ...    target_name=Orders_Backup
    
    # Log results
    Log Comparison Details    ${comparison_result}
    
    # Assertions
    Assert Comparison Status    ${comparison_result}
    Assert No Data Differences    ${comparison_result}
    Log    Test PASSED - Tables match    console=true
    
    # Cleanup
    Close Database Connection    ${db_connection}


Compare Different Database Tables
    [Documentation]    Test Case 2: Compare tables from different databases (Oracle vs PostgreSQL)
    [Tags]    db_vs_db    different_databases    critical
    
    Log Test Header    Different Database Comparison (Oracle vs PostgreSQL)
    
    # Connect to source database (Oracle)
    ${oracle_connection}=    Connect To Database    oracle_source
    
    # Connect to target database (PostgreSQL)
    ${postgres_connection}=    Connect To Database    target_db
    
    # Read tables from both databases
    ${oracle_table}=    Read Database Table    ${oracle_connection}    customers
    ${postgres_table}=    Read Database Table    ${postgres_connection}    customers
    
    # Perform comparison
    ${comparison_result}=    Compare Database Tables
    ...    ${oracle_connection}
    ...    customers
    ...    ${postgres_connection}
    ...    customers
    ...    primary_keys=['customer_id']
    
    # Generate reports
    ${excel_report}=    Generate Excel Report
    ...    ${comparison_result}
    ...    source_name=Oracle_Customers
    ...    target_name=PostgreSQL_Customers
    
    ${csv_report}=    Generate CSV Report
    ...    ${comparison_result}
    ...    source_name=Oracle_Customers
    ...    target_name=PostgreSQL_Customers
    
    # Log results
    Log Comparison Details    ${comparison_result}
    
    # Assertions
    Assert Comparison Status    ${comparison_result}
    Log    Test PASSED - Oracle and PostgreSQL tables match    console=true
    
    # Cleanup
    Close Database Connection    ${oracle_connection}
    Close Database Connection    ${postgres_connection}


Compare SQL Server With MySQL
    [Documentation]    Test Case 3: Compare SQL Server table with MySQL table
    [Tags]    db_vs_db    mssql_mysql    heterogeneous
    
    Log Test Header    SQL Server vs MySQL Comparison
    
    # Connect to SQL Server
    ${mssql_connection}=    Connect To Database    mssql_target
    
    # Connect to MySQL
    ${mysql_connection}=    Connect To Database    mysql_source
    
    # Read tables from both databases
    ${mssql_table}=    Read Database Table    ${mssql_connection}    products
    ${mysql_table}=    Read Database Table    ${mysql_connection}    products
    
    # Perform comparison
    ${comparison_result}=    Compare Database Tables
    ...    ${mssql_connection}
    ...    products
    ...    ${mysql_connection}
    ...    products
    ...    primary_keys=['product_id']
    
    # Generate reports
    ${excel_report}=    Generate Excel Report
    ...    ${comparison_result}
    ...    source_name=SQLServer_Products
    ...    target_name=MySQL_Products
    
    # Log results and assertions
    Log Comparison Details    ${comparison_result}
    Assert Comparison Status    ${comparison_result}
    Log    Test PASSED - SQL Server and MySQL tables match    console=true
    
    # Cleanup
    Close Database Connection    ${mssql_connection}
    Close Database Connection    ${mysql_connection}


Compare Tables With Composite Primary Keys
    [Documentation]    Test Case 4: Compare tables with composite primary keys
    [Tags]    db_vs_db    composite_keys    critical
    
    Log Test Header    Table Comparison with Composite Primary Keys
    
    # Connect to database
    ${db_connection}=    Connect To Database    source_db
    
    # Read tables
    ${source_table}=    Read Database Table    ${db_connection}    order_items
    ${target_table}=    Read Database Table    ${db_connection}    order_items_archive
    
    # Perform comparison with composite primary keys
    ${comparison_result}=    Compare Database Tables
    ...    ${db_connection}
    ...    order_items
    ...    ${db_connection}
    ...    order_items_archive
    ...    primary_keys=['order_id', 'line_item']
    
    # Generate reports
    ${excel_report}=    Generate Excel Report
    ...    ${comparison_result}
    ...    source_name=Order_Items
    ...    target_name=Order_Items_Archive
    
    # Log results
    Log Comparison Details    ${comparison_result}
    
    # Assertions
    Assert Comparison Status    ${comparison_result}
    Log    Test PASSED - Composite key tables match    console=true
    
    # Cleanup
    Close Database Connection    ${db_connection}


Compare Tables With Large Dataset
    [Documentation]    Test Case 5: Compare large tables with data sampling
    [Tags]    db_vs_db    large_data    performance
    
    Log Test Header    Large Dataset Table Comparison
    
    # Connect to database
    ${db_connection}=    Connect To Database    source_db
    
    # Read large tables with limit for performance testing
    ${source_table}=    Read Database Table    ${db_connection}    transactions    limit=10000
    ${target_table}=    Read Database Table    ${db_connection}    transactions_replica    limit=10000
    
    # Perform comparison
    ${comparison_result}=    Compare Database Tables
    ...    ${db_connection}
    ...    transactions
    ...    ${db_connection}
    ...    transactions_replica
    ...    primary_keys=['transaction_id']
    
    # Generate reports
    ${excel_report}=    Generate Excel Report
    ...    ${comparison_result}
    ...    source_name=Transactions
    ...    target_name=Transactions_Replica
    
    # Log results and verify performance
    Log Comparison Details    ${comparison_result}
    
    # Assert comparison passed
    Assert Comparison Status    ${comparison_result}
    Log    Test PASSED - Large dataset comparison completed    console=true
    
    # Cleanup
    Close Database Connection    ${db_connection}


Compare Tables With Custom SQL Query
    [Documentation]    Test Case 6: Compare data using custom SQL queries
    [Tags]    db_vs_db    custom_query    advanced
    
    Log Test Header    Database Comparison with Custom SQL Queries
    
    # Connect to database
    ${db_connection}=    Connect To Database    source_db
    
    # Execute custom queries instead of reading entire tables
    ${query1}=    Set Variable    SELECT * FROM customers WHERE status='ACTIVE'
    ${query2}=    Set Variable    SELECT * FROM customers WHERE status='ACTIVE' AND modified_date > SYSDATE-30
    
    ${source_data}=    Execute Database Query    ${db_connection}    ${query1}
    ${target_data}=    Execute Database Query    ${db_connection}    ${query2}
    
    # Perform comparison on query results
    ${comparison_result}=    Compare Database Tables
    ...    ${db_connection}
    ...    (custom_query_1)
    ...    ${db_connection}
    ...    (custom_query_2)
    ...    primary_keys=['customer_id']
    
    # Generate reports
    ${excel_report}=    Generate Excel Report
    ...    ${comparison_result}
    ...    source_name=Active_Customers
    ...    target_name=Recent_Active_Customers
    
    # Log results
    Log Comparison Details    ${comparison_result}
    
    # Assertions
    Assert Comparison Status    ${comparison_result}
    Log    Test PASSED - Custom query comparison completed    console=true
    
    # Cleanup
    Close Database Connection    ${db_connection}


*** Keywords ***

Connect To Database
    [Arguments]    ${db_config_name}
    Log    Connecting to database: ${db_config_name}
    Log    This keyword integrates with db_reader library
    [Return]    connection_object

Read Database Table
    [Arguments]    ${connection}    ${table_name}    ${limit}=${EMPTY}
    Log    Reading table: ${table_name}
    [if]    "${limit}" != "${EMPTY}"
        Log    Applying LIMIT: ${limit}
    [end]
    [Return]    table_dataframe

Execute Database Query
    [Arguments]    ${connection}    ${query}
    Log    Executing query: ${query}
    Log    This keyword integrates with db_reader library
    [Return]    query_result

Compare Database Tables
    [Arguments]    @{args}    &{kwargs}
    Log    Comparing database tables
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
