# 📓 Supply Chain ETL Pipeline — Guide

## Architecture
```
[CSV Sources]  →  [Extract]  →  [Validate]  →  [Transform]  →  [Load]
                                     ↓                             ↓
                              Quality Report              SQLite DB + CSV
```

## Files
| File | Purpose |
|------|---------|
| `pipeline/run_pipeline.py` | Main orchestrator — runs all stages |
| `pipeline/validators.py` | Reusable validation functions |
| `pipeline/transformers.py` | Reusable transformation functions |

## How to Run
```bash
pip install -r requirements.txt
python pipeline/run_pipeline.py
```

## Stage Details

### Extract
Generates or loads raw CSV data from source systems.
In production, this would connect to APIs, SFTP servers, or databases.

### Validate
Runs a suite of data quality checks:
- No null values in key columns
- No negative quantities
- No future-dated records
- No duplicate primary keys
- Values within expected ranges

### Transform
Applies business logic:
- Date feature extraction (year, month, quarter, weekday)
- KPI computation (variance %, on-time flag, days late)
- Vendor name standardisation
- Anomaly flagging (Z-score based)
- Audit metadata (loaded_at, source, record hash)

### Load
Writes outputs to:
- SQLite database (for SQL querying)
- CSV files (for Excel/Power BI consumption)

## Extending the Pipeline
To add a new data source:
1. Add an `extract_<source>()` function in `run_pipeline.py`
2. Add validation checks using functions from `validators.py`
3. Add transformation logic using functions from `transformers.py`
4. Add a `load_<source>()` function to write to DB
