# Data Comparison Framework - Test Execution Guide

## Quick Start

### 1. Run the Python Quick Start Example
```bash
python quickstart_example.py
```

This will:
- Load configurations
- Create sample data
- Perform comparison
- Generate Excel and CSV reports
- Display results

Expected output: Excel and CSV reports in `reports/` folder with comparison results.

---

## Robot Framework Test Execution

### Prerequisites
```bash
# Install Robot Framework
pip install -r requirements.txt

# Verify installation
robot --version
```

### Basic Test Execution

#### Run File vs Database Tests
```bash
robot tests/file_vs_db.robot
```

#### Run Database vs Database Tests
```bash
robot tests/db_vs_db.robot
```

#### Run All Tests
```bash
robot tests/
```

### Advanced Test Execution

#### Run with Specific Tags
```bash
# Run only CSV tests
robot --include csv tests/file_vs_db.robot

# Run only critical tests
robot --include critical tests/

# Exclude tags
robot --exclude performance tests/
```

#### Run with Custom Output Directory
```bash
robot --outputdir ./test_results tests/
```

#### Run with Variables
```bash
robot --variable DB_HOST:prod-server.com --variable DB_PORT:5432 tests/
```

#### Run with Verbosity
```bash
# Verbose output
robot --loglevel DEBUG tests/

# Very verbose
robot --loglevel TRACE tests/
```

#### Generate Documentation
```bash
robot --testdoc ./docs/test_documentation.html tests/
```

---

## Test Case Categories

### File vs Database Tests (`file_vs_db.robot`)
1. **Compare CSV File With Database Table**
   - Compares CSV data with database table
   - Tags: file_vs_db, csv, critical

2. **Compare Excel File With Database Table**
   - Compares Excel sheet with database table
   - Tags: file_vs_db, excel, critical

3. **Compare CSV File With Database - Allow Tolerance**
   - Compares with numeric tolerance
   - Tags: file_vs_db, csv, tolerance

4. **Compare Multiple Sheets From Excel With Database**
   - Compares combined sheets with database
   - Tags: file_vs_db, excel, multi_sheet

### Database vs Database Tests (`db_vs_db.robot`)
1. **Compare Same Database Tables**
   - Compares two tables in same database
   - Tags: db_vs_db, same_database, critical

2. **Compare Different Database Tables**
   - Compares Oracle vs PostgreSQL
   - Tags: db_vs_db, different_databases, critical

3. **Compare SQL Server With MySQL**
   - Heterogeneous database comparison
   - Tags: db_vs_db, mssql_mysql, heterogeneous

4. **Compare Tables With Composite Primary Keys**
   - Multiple key field comparison
   - Tags: db_vs_db, composite_keys, critical

5. **Compare Tables With Large Dataset**
   - Large data comparison with sampling
   - Tags: db_vs_db, large_data, performance

6. **Compare Tables With Custom SQL Query**
   - Custom query comparison
   - Tags: db_vs_db, custom_query, advanced

---

## Configuration Setup

### Database Configuration (`config/db_config.yaml`)

Before running tests, configure your database connections:

```yaml
databases:
  source_db:
    engine: "postgresql"
    host: "localhost"
    port: 5432
    database: "source_db"
    username: "${DB_SOURCE_USER}"
    password: "${DB_SOURCE_PASSWORD}"
    connection_timeout: 30
```

### File Configuration (`config/file_config.yaml`)

Configure your file sources:

```yaml
file_sources:
  csv_file:
    type: "csv"
    path: "./data/source_data.csv"
    encoding: "utf-8"
    delimiter: ","
    skip_rows: 0
    has_header: true
```

### Comparison Rules (`config/comparison_rules.yaml`)

Configure comparison logic and thresholds:

```yaml
comparison_config:
  primary_keys: ["id"]
  exclude_columns: ["created_at", "updated_at"]
  column_comparisons:
    numeric_tolerance: 0.01
    string_options:
      case_sensitive: false
      strip_whitespace: true
  thresholds:
    max_mismatch_percentage: 5.0
    max_missing_records: 10
```

---

## Running Tests with Docker (Optional)

If using Docker for database testing:

```bash
# Start PostgreSQL container
docker run -d --name postgres-test \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:latest

# Run tests against container
robot --variable DB_HOST:localhost tests/

# Cleanup
docker stop postgres-test
docker rm postgres-test
```

---

## Viewing Test Results

### Robot Framework Reports

After test execution, the following files are generated:

- `report.html` - Comprehensive test report
- `log.html` - Detailed execution log
- `output.xml` - Machine-readable results

Open `report.html` in a browser to view results.

### Data Comparison Reports

Excel and CSV reports are generated in:
- `reports/excel/` - Excel reports with color highlighting
- `reports/csv/` - CSV summary reports

### Logs

Detailed logs are available in:
- `logs/data_compare.log` - Main comparison logs
- `logs/db_reader.log` - Database operation logs
- `logs/file_reader.log` - File operation logs

---

## Example Test Execution Scenarios

### Scenario 1: Daily Data Validation
```bash
# Run critical tests daily
robot --include critical --outputdir ./results/daily tests/
```

### Scenario 2: Full Test Suite with Performance Monitoring
```bash
# Run all tests with timing
robot --outputdir ./results/full \
      --log INFO \
      --timings verbose \
      tests/
```

### Scenario 3: Specific Database Testing
```bash
# Test PostgreSQL comparisons only
robot --variable DB_ENGINE:postgresql \
      --outputdir ./results/postgres \
      tests/
```

### Scenario 4: Continuous Integration
```bash
# Generate reports for CI/CD
robot --outputdir ./ci_results \
      --log INFO \
      --report report.html \
      --output output.xml \
      tests/
```

---

## Troubleshooting Test Execution

### Issue: "Database connection failed"
```bash
# Check configuration
cat config/db_config.yaml

# Verify connection
robot --variable DB_HOST:your_host tests/db_vs_db.robot
```

### Issue: "File not found"
```bash
# Check file paths
ls -la data/

# Verify file configuration
cat config/file_config.yaml
```

### Issue: "Primary key validation error"
```bash
# Verify primary keys exist in both files/tables
# Update config/comparison_rules.yaml with correct primary keys
```

### Issue: "Tests not running"
```bash
# Check Robot Framework installation
robot --version

# Verify test file syntax
robot --dryrun tests/

# Check Python path
python -m robot.run tests/
```

---

## Continuous Integration Integration

### GitHub Actions Example
```yaml
name: Data Comparison Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - run: pip install -r requirements.txt
      - run: robot --outputdir ./results tests/
      - uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: results/
```

### Jenkins Pipeline Example
```groovy
pipeline {
    agent any
    stages {
        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        stage('Run Tests') {
            steps {
                sh 'robot --outputdir ./results tests/'
            }
        }
        stage('Publish Results') {
            steps {
                publishHTML([
                    reportDir: 'results',
                    reportFiles: 'report.html',
                    reportName: 'Robot Framework Report'
                ])
            }
        }
    }
}
```

---

## Performance Benchmarking

### Measure Execution Time
```bash
robot --loglevel TRACE --outputdir ./perf_results tests/db_vs_db.robot | tee execution.log
```

### Profile Data Comparison
```python
import cProfile
import pstats
from libraries.data_compare import DataComparator

cProfile.run('comparator.compare_dataframes(...)', 'profile.prof')
stats = pstats.Stats('profile.prof')
stats.sort_stats('cumulative')
stats.print_stats()
```

---

## Best Practices

✅ **Do:**
- Run tests in a non-production environment first
- Validate configurations before large-scale testing
- Monitor resource usage during large comparisons
- Review detailed logs for failures
- Generate reports for documentation
- Implement test result notifications

❌ **Don't:**
- Run tests directly against production databases without approval
- Modify test cases without understanding implications
- Ignore warnings or errors in logs
- Run tests with overly large datasets without sampling
- Forget to clean up test reports and logs

---

## Support and Help

For issues or questions:
1. Check logs in `logs/` directory
2. Review Robot Framework documentation: `robot --help`
3. Check configuration files for syntax errors
4. Verify database connectivity
5. Run with `--loglevel DEBUG` for detailed output
