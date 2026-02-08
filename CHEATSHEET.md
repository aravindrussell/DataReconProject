# Data Comparison Framework - Quick Reference Cheat Sheet

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
robot --version
```

---

## Running Tests

### Quick Start (Python)
```bash
python quickstart_example.py
```

### Robot Framework
```bash
# Run all tests
robot tests/

# Run specific file
robot tests/file_vs_db.robot
robot tests/db_vs_db.robot

# Run with tags
robot --include critical tests/
robot --include csv tests/file_vs_db.robot

# Custom output directory
robot --outputdir ./my_results tests/
```

---

## Configuration Examples

### Database Connection (db_config.yaml)

```yaml
databases:
  pg_db:
    engine: "postgresql"
    host: "localhost"
    port: 5432
    database: "mydb"
    username: "${DB_USER}"
    password: "${DB_PASS}"

  mysql_db:
    engine: "mysql"
    host: "localhost"
    port: 3306
    database: "mydb"
    username: "${MYSQL_USER}"
    password: "${MYSQL_PASS}"

  mssql_db:
    engine: "mssql"
    host: "sqlserver.com"
    port: 1433
    database: "MyDB"
    username: "${MSSQL_USER}"
    password: "${MSSQL_PASS}"

  oracle_db:
    engine: "oracle"
    host: "oracle.com"
    port: 1521
    database: "ORCL"
    username: "${ORACLE_USER}"
    password: "${ORACLE_PASS}"
```

### File Configuration (file_config.yaml)

```yaml
file_sources:
  csv_source:
    type: "csv"
    path: "./data/source.csv"
    encoding: "utf-8"
    delimiter: ","
    skip_rows: 0
    has_header: true

  excel_source:
    type: "excel"
    path: "./data/data.xlsx"
    sheet_name: "Sheet1"
    has_header: true

  excel_multi:
    type: "excel"
    path: "./data/combined.xlsx"
    sheet_names: ["Sheet1", "Sheet2"]
```

### Comparison Rules (comparison_rules.yaml)

```yaml
comparison_config:
  primary_keys: ["id", "customer_id"]
  exclude_columns: ["created_at", "updated_at"]
  
  column_comparisons:
    numeric_tolerance: 0.01
    string_options:
      case_sensitive: false
      strip_whitespace: true
    null_handling:
      treat_empty_as_null: true
  
  thresholds:
    max_mismatch_percentage: 5.0
    max_record_diff_percentage: 1.0
    max_missing_records: 10
```

---

## Environment Variables

```bash
# Linux/macOS
export DB_USER=username
export DB_PASS=password
export ORACLE_USER=ouser
export ORACLE_PASS=opass

# Windows (PowerShell)
$env:DB_USER="username"
$env:DB_PASS="password"

# Windows (CMD)
set DB_USER=username
set DB_PASS=password
```

---

## Python API Quick Reference

### Load Configuration

```python
from libraries.utils import ConfigManager
config = ConfigManager.load_all_configs('./config')
```

### Read Files

```python
from libraries.file_reader import FileReader
reader = FileReader()

# CSV
df = reader.read_csv("./data/file.csv", encoding='utf-8', delimiter=',')

# Excel
df = reader.read_excel("./data/file.xlsx", sheet_name='Sheet1')

# By config
df = reader.read_file(config['files']['file_sources']['csv_file'])
```

### Database Operations

```python
from libraries.db_reader import DatabaseReader
db_reader = DatabaseReader(config['databases']['databases']['source_db'])
db_reader.connect()

# Read table
df = db_reader.read_table('customers', columns=['id', 'name'], limit=100)

# Query
df = db_reader.read_query('SELECT * FROM customers WHERE status="ACTIVE"')

db_reader.disconnect()
```

### Compare Data

```python
from libraries.data_compare import DataComparator
comparator = DataComparator(config)

result = comparator.compare_dataframes(
    source_df,
    target_df,
    primary_keys=['id'],
    exclude_columns=['timestamp']
)

# Access results
print(f"Matched: {result.matched_records}")
print(f"Mismatched: {result.mismatched_records}")
print(f"Status: {result.status}")
```

### Generate Reports

```python
from libraries.report_generator import ReportGenerator
generator = ReportGenerator('./reports')

# Excel
excel_path = generator.generate_excel_report(
    result, source_df, target_df,
    source_name='Source', target_name='Target'
)

# CSV
csv_path = generator.generate_csv_summary(
    result,
    source_name='Source', target_name='Target'
)
```

---

## Robot Framework Keywords

### File Operations

```robot
${df}=    Read CSV File    ./data/file.csv    encoding=utf-8    delimiter=,
${df}=    Read Excel File    ./data/file.xlsx    sheet_name=Sheet1
${df}=    Read File By Config    csv_file
```

### Database Operations

```robot
${conn}=    Connect To Database    source_db    connection_name=db1
${df}=    Read Database Table    db1    customers    columns=id,name,email
${df}=    Execute Database Query    db1    SELECT * FROM active_customers
Close Database Connection    db1
```

### Comparisons

```robot
${result}=    Compare DataFrames    ${source_df}    ${target_df}    ['id']
${summary}=    Get Comparison Summary    ${result}
```

### Reporting

```robot
${report}=    Generate Excel Report    ${result}    ${src_df}    ${tgt_df}
...    source_name=Source    target_name=Target
${csv_report}=    Generate CSV Report    ${result}
...    source_name=Source    target_name=Target
```

### Assertions

```robot
Assert Comparison Passed    ${result}
Assert No Mismatches    ${result}
Assert No Missing Records    ${result}
Assert Record Counts Match    ${result}
```

---

## Common Use Cases

### 1. Compare CSV with Database

```robot
*** Test Cases ***
Test CSV vs Database
    ${config}=    Load Configuration    ./config
    ${csv_data}=    Read CSV File    ./data/customers.csv
    ${db_conn}=    Connect To Database    source_db
    ${db_data}=    Read Database Table    db_conn    customers
    ${result}=    Compare DataFrames    ${csv_data}    ${db_data}    ['id']
    ${report}=    Generate Excel Report    ${result}    ${csv_data}    ${db_data}
    Assert Comparison Passed    ${result}
    Close Database Connection    db_conn
```

### 2. Compare Two Database Tables

```robot
*** Test Cases ***
Test Database vs Database
    ${src_conn}=    Connect To Database    source_db
    ${tgt_conn}=    Connect To Database    target_db
    ${src_data}=    Read Database Table    src_conn    customers
    ${tgt_data}=    Read Database Table    tgt_conn    customers
    ${result}=    Compare DataFrames    ${src_data}    ${tgt_data}    ['id']
    ${report}=    Generate Excel Report    ${result}    ${src_data}    ${tgt_data}
    Assert Comparison Passed    ${result}
    Close All Connections
```

### 3. Compare with Mismatch Tolerance

```python
# Python
result = comparator.compare_dataframes(
    source_df, target_df,
    primary_keys=['id'],
    comparison_options={
        'numeric_tolerance': 0.05,  # Allow 5% difference
        'case_sensitive': False,     # Ignore case
        'strip_whitespace': True     # Trim spaces
    }
)

summary = comparator.generate_comparison_summary(result)
if summary['statistics']['mismatch_percentage'] < 10:
    print("PASSED: Mismatch within tolerance")
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -h localhost -U username -d dbname

# Test MySQL connection
mysql -h localhost -u username -p dbname

# Check SQL Server connectivity
sqlcmd -S localhost -U username -P password -d dbname

# Check Oracle connectivity
sqlplus username/password@hostname:1521/ORCL
```

### File Issues

```bash
# Verify file exists
ls -la ./data/filename.csv

# Check file encoding
file -i ./data/filename.csv

# Preview file
head -20 ./data/filename.csv
```

### Framework Issues

```bash
# Verify Python installation
python --version
pip list

# Check Robot Framework
robot --version

# Run with debug
robot --loglevel DEBUG tests/file_vs_db.robot

# Test configuration
python -c "from libraries.utils import ConfigManager; print(ConfigManager.load_all_configs())"
```

---

## File Structure Reference

```
DataReconProject/
├── config/
│   ├── db_config.yaml              ◄─ Edit database configs
│   ├── file_config.yaml            ◄─ Edit file configs
│   └── comparison_rules.yaml        ◄─ Edit comparison rules
│
├── libraries/
│   ├── db_reader.py                (Database abstraction)
│   ├── file_reader.py              (File reading)
│   ├── data_compare.py             (Comparison logic)
│   ├── report_generator.py         (Report generation)
│   ├── utils.py                    (Utilities)
│   └── robot_library.py            (Robot Framework bridge)
│
├── resources/
│   ├── CommonKeywords.resource     (Shared keywords)
│   └── DataCompareKeywords.resource (Comparison keywords)
│
├── tests/
│   ├── file_vs_db.robot            ◄─ Run: robot tests/file_vs_db.robot
│   └── db_vs_db.robot              ◄─ Run: robot tests/db_vs_db.robot
│
├── data/
│   ├── sample_customers.csv
│   └── sample_orders.csv
│
├── reports/
│   ├── excel/                      ◄─ Excel reports generated here
│   └── csv/                        ◄─ CSV reports generated here
│
├── logs/
│   ├── data_compare.log            ◄─ Check for errors
│   ├── db_reader.log
│   └── file_reader.log
│
├── quickstart_example.py           ◄─ Run: python quickstart_example.py
├── requirements.txt                ◄─ Install: pip install -r requirements.txt
├── README.md                       (Installation & usage)
├── ARCHITECTURE.md                 (Design & architecture)
└── TEST_EXECUTION_GUIDE.md         (Detailed testing guide)
```

---

## Key Classes & Methods

### ComparisonResult

```python
result.matched_records        # Number of matching records
result.mismatched_records     # Number of mismatched records
result.missing_records        # Records in source but not target
result.extra_records          # Records in target but not source
result.status                 # 'PASSED' or 'FAILED'
result.mismatch_details       # List of mismatch details
result.to_dict()              # Convert to dictionary
```

### DataComparator

```python
comparator.compare_dataframes()      # Main method
comparator.generate_comparison_summary()  # Get summary stats
comparator.compare_single_row()      # Compare two rows
```

### FileReader

```python
reader.read_csv()              # CSV file
reader.read_excel()            # Excel file
reader.read_multiple_sheets()  # Multiple sheets
```

### DatabaseReader

```python
db.connect()                   # Establish connection
db.read_table()                # Read entire table
db.read_query()                # Execute custom query
db.disconnect()                # Close connection
```

---

## Exit Codes

```
0   = Success
1   = Failure
-1  = Configuration error
-2  = Database error
-3  = File error
```

---

## Tips & Tricks

### Performance Optimization

```python
# Use LIMIT for large tables
df = db_reader.read_table('large_table', limit=10000)

# Exclude unnecessary columns
result = comparator.compare_dataframes(..., exclude_columns=['audit_cols'])

# Set appropriate tolerance
comparison_options = {'numeric_tolerance': 0.01}
```

### Better Logging

```python
# Enable debug logging
from libraries.utils import LoggerSetup
LoggerSetup.setup_logger('main', log_level='DEBUG', log_file='./logs/debug.log')

# Check logs
tail -f ./logs/data_compare.log
```

### Sample Mismatches

```python
# Review first N mismatches
for mismatch in result.mismatch_details[:10]:
    print(f"Record: {mismatch['key']}")
    for col_mismatch in mismatch['column_mismatches']:
        print(f"  {col_mismatch['column']}: {col_mismatch['source_value']} != {col_mismatch['target_value']}")
```

---

## Useful Commands

```bash
# Install framework
pip install -r requirements.txt

# Run quick start
python quickstart_example.py

# Run all tests
robot tests/

# Generate test docs
robot --testdoc ./docs/tests.html tests/

# List all tags
robot --list tests/

# Run with parallel execution
robot --processes 4 tests/

# Create test report
robot --outputdir ./reports tests/

# View log
tail -f logs/data_compare.log

# Check Python packages
pip show pandas robotframework

# Export config as JSON (Python)
python -c "import json; from libraries.utils import ConfigManager; print(json.dumps(ConfigManager.load_all_configs(), indent=2))"
```

---

## Default Values

```
Connection Timeout: 30 seconds
Query Timeout: 300 seconds
Numeric Tolerance: 0.01
Max Mismatch Percentage: 5%
Max Record Diff Percentage: 1%
Max Missing Records: 10
Default Encoding: UTF-8
Default CSV Delimiter: ,
Case Sensitive: False
Strip Whitespace: True
Treat Empty as NULL: True
```

---

## Resources

- **README.md** - Full documentation
- **ARCHITECTURE.md** - Design patterns
- **TEST_EXECUTION_GUIDE.md** - Testing options
- **config/** - Configuration examples
- **data/** - Sample data
- **quickstart_example.py** - Working example
- **logs/** - Execution logs
- **reports/** - Generated reports

---

**Last Updated:** 2024
**Framework Version:** 1.0.0
