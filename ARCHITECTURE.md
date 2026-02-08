# Data Comparison Framework - Architecture & Design Document

## Executive Summary

The Data Comparison Framework is a production-ready, enterprise-grade solution for automated data validation and comparison across heterogeneous data sources. It combines Python's data processing capabilities (pandas) with Robot Framework's test orchestration to provide comprehensive data testing functionality.

**Key Capabilities:**
- Compare CSV/Excel files with database tables
- Compare tables across different database engines
- Detect missing, extra, and mismatched records
- Generate detailed HTML and Excel reports with color highlighting
- Configuration-driven, no hardcoded values
- Enterprise-grade logging and error handling

---

## Architecture Overview

### 3-Tier Architecture

```
┌─────────────────────────────────────┐
│   Test Orchestration Layer (Robot)  │
│  - Test execution                   │
│  - Keyword-driven scenarios         │
│  - Reporting & logging              │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│   Integration Layer (Python)        │
│  - Robot Framework Library Wrapper  │
│  - Configuration Management         │
│  - Exception Handling               │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│   Core Libraries (Python)           │
│  - FileReader (CSV/Excel)           │
│  - DatabaseReader (4 DB engines)    │
│  - DataComparator (comparison logic)│
│  - ReportGenerator (Excel/CSV)      │
│  - Utilities (logging, validation)  │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│   Data Sources                      │
│  - CSV Files                        │
│  - Excel Files                      │
│  - PostgreSQL                       │
│  - MySQL                            │
│  - SQL Server                       │
│  - Oracle                           │
└─────────────────────────────────────┘
```

### Module Breakdown

```
DataCompareFramework/
│
├── Entry Points
│   ├── quickstart_example.py      (Python-based execution)
│   ├── tests/file_vs_db.robot     (Robot-based test cases)
│   └── tests/db_vs_db.robot       (Robot-based test cases)
│
├── Configuration Layer
│   └── config/
│       ├── db_config.yaml         (Database profiles)
│       ├── file_config.yaml       (File profiles)
│       └── comparison_rules.yaml   (Comparison rules & thresholds)
│
├── Core Libraries
│   └── libraries/
│       ├── utils.py               (ConfigManager, LoggerSetup, etc.)
│       ├── db_reader.py           (Database abstraction layer)
│       ├── file_reader.py         (File abstraction layer)
│       ├── data_compare.py        (Comparison engine)
│       ├── report_generator.py    (Report generation)
│       └── robot_library.py       (Robot Framework bridge)
│
├── Robot Framework Layer
│   └── resources/
│       ├── CommonKeywords.resource     (Shared keywords)
│       └── DataCompareKeywords.resource (Comparison keywords)
│
└── Output
    ├── reports/
    │   ├── excel/                  (Excel reports)
    │   └── csv/                    (CSV reports)
    └── logs/
        └── *.log                   (Execution logs)
```

---

## Detailed Component Design

### 1. Configuration Manager (utils.py)

**Responsibility:** Load and manage YAML configurations

**Key Methods:**
```python
ConfigManager.load_yaml(config_path)           # Load single YAML file
ConfigManager.load_all_configs(config_dir)    # Load all configs
ConfigManager.get_env_variable(var_name)      # Environment variable resolution
```

**Features:**
- Environment variable substitution (${VAR_NAME})
- Error handling for missing/invalid files
- YAML parsing with PyYAML

---

### 2. Logger Setup (utils.py)

**Responsibility:** Centralized logging configuration

**Key Methods:**
```python
LoggerSetup.setup_logger(name, log_level, log_file)
get_logger(name)  # Get existing logger
```

**Features:**
- Console and file output
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Formatted timestamps
- Singleton pattern for logger instances

---

### 3. Database Reader (db_reader.py)

**Responsibility:** Abstract database access across multiple engines

**Architecture:**

```
DatabaseConnector (Abstract Base)
    ├── PostgreSQLConnector
    ├── MySQLConnector
    ├── MSSQLConnector
    └── OracleConnector

DatabaseReader (Factory)
    └── Manages connector lifecycle
```

**Supported Databases:**
- PostgreSQL (psycopg2)
- MySQL (mysql-connector-python)
- SQL Server (pyodbc)
- Oracle (cx_Oracle)

**Key Methods:**
```python
db_reader = DatabaseReader(config)
connection = db_reader.connect()
df = db_reader.read_table(table_name, columns, limit)
df = db_reader.read_query(query)
db_reader.disconnect()
```

**Features:**
- Connection pooling/management
- Query timeout configuration
- Environment variable support for credentials
- Automatic DataFrame conversion

---

### 4. File Reader (file_reader.py)

**Responsibility:** Abstract file reading for various formats

**Supported Formats:**
- CSV (with encoding, delimiter, skip rows options)
- Excel (single and multiple sheets)

**Key Methods:**
```python
file_reader = FileReader()
df = file_reader.read_csv(path, encoding, delimiter, skip_rows, has_header)
df = file_reader.read_excel(path, sheet_name, skip_rows, has_header)
df = file_reader.read_multiple_sheets(path, sheet_names, combine=True)
df = file_reader.read_file(config)  # Config-driven
```

**Features:**
- Flexible encoding support
- Custom delimiters
- Row skipping
- Column selection
- Multi-sheet combining

---

### 5. Data Comparator (data_compare.py)

**Responsibility:** Core comparison engine

**Architecture:**

```
ComparisonResult (Data Class)
    ├── matched_records
    ├── mismatched_records
    ├── missing_records
    ├── extra_records
    ├── mismatch_details
    └── status

DataComparator (Main Engine)
    ├── compare_dataframes()
    ├── _compare_record_counts()
    ├── _find_missing_records()
    ├── _find_extra_records()
    ├── _compare_values()
    └── _determine_status()
```

**Comparison Logic:**

1. **Record Count Comparison**
   - Verifies total record counts match
   - Identifies discrepancies

2. **Missing Records Detection**
   - Uses primary keys to identify records in source but not target
   - Returns list of missing primary keys

3. **Extra Records Detection**
   - Identifies records in target but not in source
   - Returns list of extra primary keys

4. **Value Comparison**
   - Matches records by primary key
   - Compares column values with configurable options:
     - Numeric tolerance (for float comparisons)
     - Case sensitivity (string comparison)
     - NULL handling (NULL vs empty)
     - Whitespace stripping

5. **Status Determination**
   - Applies thresholds to determine PASSED/FAILED
   - Configurable thresholds for:
     - Maximum mismatch percentage
     - Maximum record count difference
     - Maximum missing records

**Key Methods:**
```python
comparator = DataComparator(config)
result = comparator.compare_dataframes(
    source_df, target_df, primary_keys,
    exclude_columns, comparison_options
)
summary = comparator.generate_comparison_summary(result)
```

---

### 6. Report Generator (report_generator.py)

**Responsibility:** Generate detailed comparison reports

**Report Types:**

1. **Excel Report (.xlsx)**
   - Summary sheet with metadata
   - Matched records sheet (green highlighting)
   - Mismatched records sheet (red highlighting)
   - Missing records sheet (yellow highlighting)
   - Extra records sheet (yellow highlighting)

2. **CSV Summary Report (.csv)**
   - One-line summary with key metrics
   - Execution timestamp
   - Source/target names
   - Record counts

**Color Scheme:**
```
Green (#00B050)   = Matched records
Red (#FF0000)     = Mismatched values
Yellow (#FFFF00)  = Missing/Extra records
```

**Key Methods:**
```python
generator = ReportGenerator(output_dir)
excel_path = generator.generate_excel_report(
    result, source_df, target_df, source_name, target_name
)
csv_path = generator.generate_csv_summary(result, source_name, target_name)
```

---

### 7. Robot Framework Library (robot_library.py)

**Responsibility:** Bridge between Robot Framework and Python libraries

**Exposed Keywords:**

**File Operations:**
- `Read CSV File` - Load CSV with options
- `Read Excel File` - Load Excel sheet
- `Read File By Config` - Config-driven file reading

**Database Operations:**
- `Connect To Database` - Establish connection
- `Read Database Table` - Query table into DataFrame
- `Execute Database Query` - Run custom SQL
- `Close Database Connection` - Cleanup

**Comparison:**
- `Compare DataFrames` - Main comparison
- `Get Comparison Summary` - Extract results

**Reporting:**
- `Generate Excel Report` - Create Excel report
- `Generate CSV Report` - Create CSV report

**Assertions:**
- `Assert Comparison Passed` - Verify status
- `Assert No Mismatches` - Check for differences
- `Assert No Missing Records` - Verify completeness
- `Assert Record Counts Match` - Verify totals

**Cleanup:**
- `Close All Connections` - Close all DB connections
- `Cleanup Framework` - Full cleanup

---

## Data Flow Diagrams

### File vs Database Comparison Flow

```
User initiates test
        │
        ▼
Load Configuration ─────────────────┐
        │                           │
        ▼                           │
Read CSV File                       │
        │                           │
        ▼                           │
Clean & Prepare Data                │
        │                           │
        ▼                           │
Connect to Database ◄───────────────┘
        │
        ▼
Read Database Table
        │
        ▼
Clean & Prepare Data
        │
        ▼
Compare DataFrames
    ├─ Match by Primary Key
    ├─ Find Missing Records
    ├─ Find Extra Records
    └─ Compare Values
        │
        ▼
Generate Report (Excel + CSV)
        │
        ▼
Return Results
        │
        ▼
Robot Framework Assertions
```

### Database vs Database Comparison Flow

```
Connect to Source DB ────┐
                         │
Connect to Target DB     │
                         │
                    ┌────▼────┐
                    │ Read     │
                    │ Tables   │
                    └────┬────┘
                         │
                    ┌────▼──────────┐
                    │ Clean & Merge │
                    │   DataFrames  │
                    └────┬──────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
   Record Count              Value Comparison
   Validation                with Tolerance
        │                                 │
        └────────────────┬────────────────┘
                         │
                    ┌────▼─────┐
                    │ Determine│
                    │  Status  │
                    └────┬─────┘
                         │
                    ┌────▼──────────┐
                    │ Generate      │
                    │ Reports       │
                    └────┬──────────┘
                         │
                ┌────────▼────────┐
                │ Return to Robot │
                │   Framework     │
                └─────────────────┘
```

---

## Configuration Design

### Configuration Hierarchy

```
1. Code Defaults (Built-in)
        ↓
2. YAML Configuration Files
        ├── db_config.yaml
        ├── file_config.yaml
        └── comparison_rules.yaml
        ↓
3. Environment Variables (Credentials)
        ↓
4. Runtime Parameters (Override)
```

### Configuration Structure

**db_config.yaml**: Database connection profiles
```yaml
databases:
  <profile_name>:
    engine: postgresql|mysql|mssql|oracle
    host: hostname
    port: port_number
    database: db_name
    username: ${ENV_VAR}        # Environment variable
    password: ${ENV_VAR}
    connection_timeout: 30
```

**file_config.yaml**: File source definitions
```yaml
file_sources:
  <source_name>:
    type: csv|excel
    path: file_path
    [csv_specific]:
      encoding: utf-8
      delimiter: ,
    [excel_specific]:
      sheet_name: Sheet1
```

**comparison_rules.yaml**: Comparison logic
```yaml
comparison_config:
  primary_keys: [key1, key2]
  exclude_columns: [col1, col2]
  column_comparisons:
    numeric_tolerance: 0.01
    string_options:
      case_sensitive: false
  thresholds:
    max_mismatch_percentage: 5.0
```

---

## Error Handling Strategy

### Layered Error Handling

```
Level 1: Input Validation
    ├─ Primary key validation
    ├─ Column existence checks
    └─ Data type validation
           ↓
Level 2: Component Error Handling
    ├─ Database connection errors
    ├─ File reading errors
    └─ Comparison logic errors
           ↓
Level 3: Framework Error Handling
    ├─ Robot Framework assertions
    ├─ Test result reporting
    └─ Log aggregation
```

### Exception Types

```
ValueError              - Invalid input/configuration
FileNotFoundError       - Missing files
ConnectionError         - Database connectivity issues
Exception (Generic)     - Unexpected errors
```

---

## Performance Characteristics

### Time Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Primary Key Matching | O(n + m) | Using set operations |
| Value Comparison | O(n × c) | n records, c columns |
| Excel Report Generation | O(n) | Linear with record count |
| CSV Report Generation | O(1) | Constant time |

### Space Complexity

| Component | Space | Notes |
|-----------|-------|-------|
| DataFrames | O(n × c) | n records, c columns |
| Mismatch Details | O(m × c) | m mismatches, c columns |
| Report Generation | O(n) | Output size |

### Optimization Tips

1. **Use LIMIT in queries** for large datasets
2. **Exclude unnecessary columns** from comparison
3. **Set appropriate primary keys** for efficient matching
4. **Use numeric tolerance** wisely for float comparisons
5. **Process in batches** for very large datasets (>1M records)

---

## Extensibility Points

### Adding New Database Engine

1. Create new connector class inheriting from `DatabaseConnector`
2. Implement `connect()` and `execute_query()` methods
3. Register in `DatabaseReader.CONNECTORS` dictionary
4. Add connection profile to `db_config.yaml`

### Adding New File Format

1. Extend `FileReader` with new read method
2. Add file type handling in `read_file()` method
3. Add configuration support in `file_config.yaml`

### Adding Custom Comparison Logic

1. Extend `DataComparator` with new comparison method
2. Call from `compare_dataframes()` workflow
3. Document comparison options in `comparison_rules.yaml`

### Adding Custom Reports

1. Extend `ReportGenerator` with new generate method
2. Implement formatting/styling as needed
3. Add report configuration to `comparison_rules.yaml`

---

## Security Considerations

### Credential Management

✅ **Do:**
- Use environment variables for sensitive data
- Store credentials in environment, not code
- Use `.env` files locally (never commit to repo)
- Implement access controls on configuration files

❌ **Don't:**
- Hardcode usernames/passwords
- Store credentials in YAML files
- Commit sensitive data to version control
- Log sensitive information

### Data Privacy

- Sanitize logs of sensitive values
- Implement field-level encryption if needed
- Audit comparison access and reports
- Implement retention policies for reports

---

## Testing Strategy

### Unit Tests (Recommended)

```python
# Test DataCleaner
test_normalize_string()
test_compare_values()

# Test DataValidator
test_validate_primary_keys()
test_get_column_dtypes()

# Test DataComparator
test_missing_records_detection()
test_extra_records_detection()
test_mismatch_detection()
```

### Integration Tests

```
test_csv_to_db_comparison()
test_db_to_db_comparison()
test_multi_sheet_comparison()
```

### Robot Framework Tests

```
file_vs_db.robot    - 4 test cases
db_vs_db.robot      - 6 test cases
```

---

## Deployment Checklist

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Configure databases in `config/db_config.yaml`
- [ ] Configure files in `config/file_config.yaml`
- [ ] Set environment variables for credentials
- [ ] Create test data/tables in source/target systems
- [ ] Run quickstart example: `python quickstart_example.py`
- [ ] Run Robot tests: `robot tests/`
- [ ] Review reports in `reports/` directory
- [ ] Validate log output in `logs/` directory
- [ ] Set up continuous integration
- [ ] Document custom configurations
- [ ] Train team on framework usage

---

## Maintenance & Support

### Regular Maintenance

- Monitor log files for errors
- Review report trends for anomalies
- Update dependencies quarterly
- Archive old reports per retention policy
- Test database connectivity periodically

### Troubleshooting Guide

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection refused | DB not running | Start database server |
| File not found | Invalid path | Check file path in config |
| Primary key error | Missing/duplicate keys | Validate data in source/target |
| Mismatch detected | Data differences | Review detailed report |
| Performance slow | Large dataset | Use LIMIT, exclude columns |

### Support Resources

- Configuration: See `README.md` for detailed settings
- Testing: See `TEST_EXECUTION_GUIDE.md` for test options
- Architecture: See this document for design details
- Logs: Check `logs/` directory for execution details
- Reports: Review `reports/` directory for comparison results

---

## Version History

| Version | Date | Key Changes |
|---------|------|------------|
| 1.0.0   | 2024 | Initial release |

---

## Conclusion

The Data Comparison Framework provides a robust, scalable solution for data validation testing. Its modular architecture enables easy extension and customization while maintaining clean separation of concerns and production-grade reliability.

For additional information, refer to:
- README.md - Installation and usage guide
- TEST_EXECUTION_GUIDE.md - Test execution options
- config/ - Configuration examples
- quickstart_example.py - Working example
