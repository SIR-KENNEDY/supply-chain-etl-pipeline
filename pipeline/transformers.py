"""
transformers.py
===============
Transformation functions applied in the ETL pipeline Transform stage.
Each function takes a DataFrame and returns a transformed DataFrame.
"""
import pandas as pd
import numpy as np
from datetime import datetime

def add_date_features(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Extract year, month, quarter, day-of-week from a date column."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df["year"]         = df[date_col].dt.year
    df["month"]        = df[date_col].dt.month
    df["quarter"]      = df[date_col].dt.quarter
    df["day_of_week"]  = df[date_col].dt.dayofweek
    df["is_weekend"]   = (df["day_of_week"] >= 5).astype(int)
    df["week_of_year"] = df[date_col].dt.isocalendar().week.astype(int)
    return df

def compute_delivery_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Compute standard supply chain KPIs from delivery records."""
    df = df.copy()
    df["qty_variance"]      = df["qty_delivered"] - df["qty_ordered"]
    df["variance_pct"]      = (df["qty_variance"] / df["qty_ordered"] * 100).round(2)
    df["within_tolerance"]  = df["variance_pct"].between(-5, 5).astype(int)
    df["on_time"]           = (df["actual_date"] <= df["scheduled_date"]).astype(int)
    df["days_late"]         = (df["actual_date"] - df["scheduled_date"]).dt.days.clip(lower=0)
    return df

def standardise_vendor_names(df: pd.DataFrame, col: str = "vendor") -> pd.DataFrame:
    """Strip whitespace and title-case vendor names for consistency."""
    df = df.copy()
    df[col] = df[col].str.strip().str.title()
    return df

def flag_anomalies(df: pd.DataFrame, col: str, sigma: float = 3.0) -> pd.DataFrame:
    """Flag rows where a numeric column is more than N standard deviations from mean."""
    df = df.copy()
    mean, std = df[col].mean(), df[col].std()
    df[f"{col}_anomaly"] = (abs(df[col] - mean) > sigma * std).astype(int)
    return df

def add_audit_columns(df: pd.DataFrame, source: str = "etl") -> pd.DataFrame:
    """Add pipeline audit metadata columns."""
    df = df.copy()
    df["loaded_at"]  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df["source"]     = source
    df["record_hash"]= df.astype(str).apply(lambda r: hash(tuple(r)), axis=1)
    return df
