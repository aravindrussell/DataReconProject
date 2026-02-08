# Data Comparison Framework

A comprehensive, production-ready framework for validating and comparing data between flat files (CSV/Excel) and databases using Python (pandas) and Robot Framework for test orchestration.

## Features

✅ **Multi-source Support**: Compare data from CSV, Excel, and multiple database engines (Oracle, SQL Server, MySQL, PostgreSQL)

✅ **Comprehensive Comparison Types**:
- Primary key-based record matching
- Row-level comparisons
- Column-level value comparisons
- Detection of missing, extra, and mismatched records

✅ **Advanced Data Handling**:
- NULL vs empty value differentiation (configurable)
- Datatype mismatch detection
- Leading/trailing whitespace handling
- Case-sensitive/insensitive comparisons (configurable)
- Numeric tolerance for float comparisons

✅ **Detailed Reporting**:
- Excel reports with color-coded highlights (Red=mismatches, Yellow=missing, Green=matched)
- CSV summary reports
- Multiple report sheets (Summary, Matched, Mismatched, Missing, Extra)
- Execution metadata and timestamps

✅ **Robot Framework Integration**:
- Keyword-driven test automation
- Reusable test libraries
- Comprehensive logging and reporting
- Test case execution with status tracking

✅ **Configuration-Driven**:
- YAML-based configuration files
- Database connection profiles
- File source definitions
- Comparison rules and thresholds
- No hardcoded values

---

## Framework Structure

```
DataCompareFramework/
├── config/                          # Configuration files
│   ├── db_config.yaml              # Database connection configurations
│   ├── file_config.yaml            # File source configurations
│   └── comparison_rules.yaml        # Comparison rules and thresholds
│
├── libraries/                       # Python libraries (Robot Framework integration)
│   ├── __init__.py                 # Package initializer
│   ├── db_reader.py               # Database reading (supports 4 DB engines)
│   ├── file_reader.py             # CSV/Excel file reading
│   ├── data_compare.py            # Core comparison logic
│   ├── report_generator.py        # Excel/CSV report generation
│   └── utils.py                   # Utility functions (logging, config, validation)
│
├── resources/                      # Robot Framework resources
│   ├── CommonKeywords.resource    # Common test keywords
│   └── DataCompareKeywords.resource # Data comparison specific keywords
│
├── tests/                         # Robot Framework test cases
│   ├── file_vs_db.robot          # File vs Database comparison tests
│   └── db_vs_db.robot            # Database vs Database comparison tests
│
├── reports/                       # Generated reports
│   ├── excel/                     # Excel reports (.xlsx)
│   └── csv/                       # CSV reports (.csv)
│
├── logs/                          # Execution logs
│
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── run_tests.sh/cmd               # Test execution scripts
```

### Folder & File Descriptions

| Folder/File | Purpose |
|---|---|
| `config/db_config.yaml` | Defines database connections for Oracle, SQL Server, MySQL, PostgreSQL with host, port, credentials (environment variable support) |
| `config/file_config.yaml` | Defines file sources (CSV/Excel) with paths, delimiters, sheet names, encoding options |
| `config/comparison_rules.yaml` | Defines comparison logic: primary keys, column exclusions, comparison options, numeric tolerance, case sensitivity, thresholds, reporting settings |
| `libraries/db_reader.py` | Database reader supporting 4 engines; handles connections, query execution, table reading |
| `libraries/file_reader.py` | File reader for CSV and Excel; supports multiple sheets, custom encodings, column selection |
| `libraries/data_compare.py` | Core comparison logic; performs record matching, value comparison, mismatch detection |
| `libraries/report_generator.py` | Generates Excel reports with color highlighting, CSV summary reports, metadata |
| `libraries/utils.py` | Utilities: ConfigManager, LoggerSetup, DataCleaner, DataValidator, ExceptionHandler |
| `resources/CommonKeywords.resource` | Shared Robot keywords: logging, assertions, timestamp generation |
| `resources/DataCompareKeywords.resource` | Comparison-specific Robot keywords: file loading, DB operations, comparisons, reporting |
| `tests/file_vs_db.robot` | 4 test cases demonstrating file vs database comparisons |
| `tests/db_vs_db.robot` | 6 test cases demonstrating database vs database comparisons |

---

## Installation & Setup

### 1. Prerequisites
- Python 3.8+
- pip package manager
- Database clients (optional, based on your database engines)

### 2. Clone/Create Project
```bash
git clone <repository> DataCompareFramework
cd DataCompareFramework
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Database Connections
Edit `config/db_config.yaml`:
```yaml
databases:
  source_db:
    engine: "postgresql"
    host: "localhost"
    port: 5432
    database: "source_db"
    username: "${DB_SOURCE_USER}"    # Use environment variables
    password: "${DB_SOURCE_PASSWORD}"
```

### 5. Configure File Sources
Edit `config/file_config.yaml`:
```yaml
file_sources:
  csv_file:
    type: "csv"
    path: "./data/source_data.csv"
    encoding: "utf-8"
    delimiter: ","
    has_header: true
```

### 6. Set Environment Variables
```bash
# Linux/macOS
export DB_SOURCE_USER=username
export DB_SOURCE_PASSWORD=password

# Windows PowerShell
$env:DB_SOURCE_USER="username"
$env:DB_SOURCE_PASSWORD="password"
```

---

## Usage

### Using Python Libraries Directly

```python
from libraries.file_reader import FileReader
from libraries.db_reader import DatabaseReader
from libraries.data_compare import DataComparator
from libraries.report_generator import ReportGenerator
from utils import ConfigManager

# Load configurations
configs = ConfigManager.load_all_configs("./config")

# Read CSV file
file_reader = FileReader()
csv_data = file_reader.read_csv("./data/customers.csv")

# Read database table
db_reader = DatabaseReader(configs['databases']['source_db'])
db_data = db_reader.read_table("customers")

# Compare data
comparator = DataComparator(configs)
result = comparator.compare_dataframes(
    csv_data, db_data,
    primary_keys=['customer_id']
)

# Generate reports
generator = ReportGenerator("./reports")
excel_report = generator.generate_excel_report(
    result, csv_data, db_data,
    source_name="CSV_File",
    target_name="Database_Table"
)

print(f"Report generated: {excel_report}")
print(f"Status: {result.status}")
```

### Using Robot Framework

```bash
# Run file vs database tests
robot tests/file_vs_db.robot

# Run database vs database tests
robot tests/db_vs_db.robot

# Run with specific tags
robot --include csv tests/file_vs_db.robot

# Run with output directory
robot --outputdir ./results tests/

# Run with variable
robot --variable DB_HOST:prod-server.com tests/
```

---

## Configuration Guide

### Comparison Rules (`comparison_rules.yaml`)

```yaml
comparison_config:
  primary_keys: ["id", "transaction_id"]
  exclude_columns: ["created_at", "updated_at"]
  
  column_comparisons:
    numeric_tolerance: 0.01              # For float comparisons
    string_options:
      case_sensitive: false              # Case-insensitive comparison
      strip_whitespace: true             # Remove leading/trailing spaces
    null_handling:
      treat_empty_as_null: true          # "" treated as NULL
      null_vs_empty_mismatch: false      # NULL == ""
  
  thresholds:
    max_mismatch_percentage: 5.0         # Fail if > 5% mismatches
    max_record_diff_percentage: 1.0      # Fail if record count differs > 1%
    max_missing_records: 10              # Fail if > 10 records missing
```

### Database Configuration

**PostgreSQL:**
```yaml
databases:
  postgres_db:
    engine: "postgresql"
    host: "localhost"
    port: 5432
    database: "mydb"
    username: "${PG_USER}"
    password: "${PG_PASSWORD}"
```

**MySQL:**
```yaml
databases:
  mysql_db:
    engine: "mysql"
    host: "localhost"
    port: 3306
    database: "mydb"
    username: "${MYSQL_USER}"
    password: "${MYSQL_PASSWORD}"
```

**SQL Server:**
```yaml
databases:
  mssql_db:
    engine: "mssql"
    host: "sqlserver.company.com"
    port: 1433
    database: "MyDB"
    username: "${MSSQL_USER}"
    password: "${MSSQL_PASSWORD}"
```

**Oracle:**
```yaml
databases:
  oracle_db:
    engine: "oracle"
    host: "oracle-server.company.com"
    port: 1521
    database: "ORCL"
    username: "${ORACLE_USER}"
    password: "${ORACLE_PASSWORD}"
```

---

## API Reference

### DataComparator

```python
comparator = DataComparator(config)

# Main comparison method
result = comparator.compare_dataframes(
    source_df: pd.DataFrame,
    target_df: pd.DataFrame,
    primary_keys: List[str],
    exclude_columns: List[str] = None,
    comparison_options: Dict = None
) -> ComparisonResult
```

**ComparisonResult attributes:**
- `matched_records`: int - Number of matching records
- `mismatched_records`: int - Number of mismatched records
- `missing_records`: int - Records in source but not in target
- `extra_records`: int - Records in target but not in source
- `status`: str - "PASSED" or "FAILED"
- `mismatch_details`: List[Dict] - Detailed mismatch information

### DatabaseReader

```python
db_reader = DatabaseReader(db_config)

# Connect to database
connection = db_reader.connect()

# Read table
df = db_reader.read_table(table_name, columns, limit)

# Execute query
df = db_reader.read_query(query)

# Disconnect
db_reader.disconnect()
```

### FileReader

```python
file_reader = FileReader()

# Read CSV
df = file_reader.read_csv(file_path, encoding, delimiter, skip_rows)

# Read Excel
df = file_reader.read_excel(file_path, sheet_name, skip_rows)

# Read multiple sheets
df = file_reader.read_multiple_sheets(file_path, sheet_names, combine=True)
```

### ReportGenerator

```python
generator = ReportGenerator(output_dir)

# Generate Excel report
excel_path = generator.generate_excel_report(
    comparison_result, source_df, target_df,
    source_name="Source",
    target_name="Target"
)

# Generate CSV report
csv_path = generator.generate_csv_summary(
    comparison_result,
    source_name="Source",
    target_name="Target"
)
```

---

## Sample Test Execution

### Example 1: Compare CSV with Database

**Python Script:**
```python
from libraries.utils import ConfigManager
from libraries.file_reader import FileReader
from libraries.db_reader import DatabaseReader
from libraries.data_compare import DataComparator
from libraries.report_generator import ReportGenerator

# Load config
config = ConfigManager.load_all_configs("./config")

# Read CSV
file_reader = FileReader()
csv_data = file_reader.read_csv("./data/customers.csv")

# Read Database
db_reader = DatabaseReader(config['databases']['source_db'])
db_data = db_reader.read_table("customers")

# Compare
comparator = DataComparator(config)
result = comparator.compare_dataframes(csv_data, db_data, ['customer_id'])

# Report
generator = ReportGenerator()
excel_file = generator.generate_excel_report(result, csv_data, db_data)

print(f"Comparison Status: {result.status}")
print(f"Matched: {result.matched_records}, Mismatched: {result.mismatched_records}")
```

### Example 2: Compare Two Database Tables

```python
# Read from two databases
oracle_db = DatabaseReader(config['databases']['oracle_source'])
oracle_data = oracle_db.read_table("customers")

pg_db = DatabaseReader(config['databases']['source_db'])
pg_data = pg_db.read_table("customers")

# Compare
result = comparator.compare_dataframes(oracle_data, pg_data, ['customer_id'])

# Generate reports
excel_file = generator.generate_excel_report(
    result, oracle_data, pg_data,
    source_name="Oracle", target_name="PostgreSQL"
)
csv_file = generator.generate_csv_summary(result)
```

---

## Excel Report Format

The generated Excel reports include multiple sheets:

1. **Summary Sheet**
   - Source/Target names
   - Record counts
   - Match statistics
   - Overall status

2. **Matched Records** (Green highlighting)
   - All records that match between source and target

3. **Mismatched Records** (Red highlighting)
   - Records with value differences
   - Shows which columns mismatched
   - Original values from both source and target

4. **Missing in Target** (Yellow highlighting)
   - Records present in source but absent in target

5. **Extra in Target** (Yellow highlighting)
   - Records present in target but absent in source

---

## Logging

Logs are automatically generated in the `logs/` directory:

```
logs/
├── data_compare.log          # Main comparison logs
├── db_reader.log             # Database operations
├── file_reader.log           # File operations
└── report_generator.log      # Report generation
```

Configure logging in `comparison_rules.yaml`:
```yaml
logging:
  log_level: "INFO"            # DEBUG, INFO, WARNING, ERROR
  log_file: "./logs/data_compare.log"
  console_output: true
```

---

## Use Cases

### 1. **Data Migration Testing**
Compare source and target systems during ETL migrations to ensure data integrity.

### 2. **ETL Testing**
Validate ETL processes by comparing file inputs with transformed database outputs.

### 3. **Regression Testing**
Regularly compare production data with backup/archive tables to detect anomalies.

### 4. **Master Data Management**
Ensure master data consistency across multiple systems.

### 5. **Quality Assurance**
Comprehensive data validation in testing environments.

---

## Error Handling

The framework includes comprehensive exception handling:

```python
try:
    result = comparator.compare_dataframes(source_df, target_df, keys)
except ValueError as e:
    logger.error(f"Validation error: {str(e)}")
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
```

---

## Performance Considerations

- **Large Datasets**: Use LIMIT in queries for initial testing
- **Numeric Tolerance**: Set appropriate tolerance for float comparisons
- **Column Exclusion**: Exclude unnecessary columns to improve performance
- **Batch Processing**: Process large comparisons in batches if needed

---

## Troubleshooting

### Issue: Database Connection Failed
- Verify database credentials in config/db_config.yaml
- Check environment variables are set correctly
- Ensure database server is accessible from your network

### Issue: File Not Found
- Verify file paths are correct in config/file_config.yaml
- Check file permissions
- Ensure file encoding is specified correctly

### Issue: Column Mismatch
- Verify primary keys exist in both source and target
- Check column names match (case-sensitive)
- Exclude incompatible columns in comparison_rules.yaml

---

## Best Practices

✅ **Do:**
- Use environment variables for sensitive data (usernames, passwords)
- Validate primary keys before comparison
- Exclude system-generated columns (timestamps, auto-increments)
- Review Excel reports for visual validation
- Set appropriate mismatch thresholds
- Use meaningful test case names
- Document custom comparison rules

❌ **Don't:**
- Hardcode database credentials
- Compare without defining primary keys
- Run comparisons on production databases without testing first
- Ignore warnings in logs
- Use overly strict numeric tolerances for floats
- Forget to close database connections

---

## Contributing

To extend the framework:

1. **New Database Engine**: Extend `DatabaseConnector` class in `db_reader.py`
2. **New File Format**: Extend `FileReader` class in `file_reader.py`
3. **Custom Comparisons**: Extend `DataComparator` class in `data_compare.py`
4. **Custom Reports**: Extend `ReportGenerator` class in `report_generator.py`

---

## License

This framework is provided as-is for testing and data validation purposes.

---

## Support

For issues, questions, or feature requests, refer to the logs and error messages for diagnostics.

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2024 | Initial release with core functionality |

---

## Examples

See `tests/` directory for complete Robot Framework examples demonstrating:
- File vs Database comparisons
- Database vs Database comparisons
- Multi-sheet Excel handling
- Composite primary keys
- Large dataset handling
- Custom SQL queries
