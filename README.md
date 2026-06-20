# 🔄 Supply Chain ETL Pipeline

![Python](https://img.shields.io/badge/Python-3.10-blue) ![Pandas](https://img.shields.io/badge/Pandas-ETL-green) ![SQLite](https://img.shields.io/badge/SQLite-Database-lightgrey)

## Overview
A modular ETL (Extract, Transform, Load) pipeline that ingests raw supply chain data from multiple CSV sources, applies transformation rules and business logic, validates data quality, and loads into a SQLite analytical database.

## Pipeline Stages
```
[Extract]  Multiple CSV sources → raw DataFrames
    ↓
[Validate] Data quality checks → flag/reject bad records  
    ↓
[Transform] Enrich, join, compute derived fields
    ↓
[Load]     Analytical SQLite database + summary CSV
```

## How to Run
```bash
pip install -r requirements.txt
python pipeline/run_pipeline.py
```

## Skills Demonstrated
`ETL Design` `Pipeline Architecture` `Data Validation` `SQLite` `Pandas` `Modular Python`

---
*Kennedy Onuorah | [LinkedIn](https://www.linkedin.com/in/kennedy-onuorah-7a3793128)*
