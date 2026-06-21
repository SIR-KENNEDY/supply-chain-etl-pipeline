"""
validators.py
=============
Reusable validation functions for the ETL pipeline.
Each validator returns (passed: bool, message: str, failure_count: int).
"""
import pandas as pd
from typing import Tuple

def check_no_nulls(df: pd.DataFrame, col: str) -> Tuple[bool, str, int]:
    n = df[col].isna().sum()
    return n == 0, f"No nulls in [{col}]", int(n)

def check_positive(df: pd.DataFrame, col: str) -> Tuple[bool, str, int]:
    n = (df[col] <= 0).sum() if col in df.columns else 0
    return n == 0, f"[{col}] > 0", int(n)

def check_no_negatives(df: pd.DataFrame, col: str) -> Tuple[bool, str, int]:
    n = (df[col] < 0).sum() if col in df.columns else 0
    return n == 0, f"[{col}] >= 0", int(n)

def check_no_duplicates(df: pd.DataFrame, col: str) -> Tuple[bool, str, int]:
    n = df[col].duplicated().sum()
    return n == 0, f"No duplicate [{col}]", int(n)

def check_date_not_future(df: pd.DataFrame, col: str) -> Tuple[bool, str, int]:
    n = (df[col] > pd.Timestamp("today")).sum() if col in df.columns else 0
    return n == 0, f"[{col}] not in future", int(n)

def check_value_range(df: pd.DataFrame, col: str, lo, hi) -> Tuple[bool, str, int]:
    n = (~df[col].between(lo, hi)).sum() if col in df.columns else 0
    return n == 0, f"[{col}] between {lo} and {hi}", int(n)

def check_referential_integrity(df: pd.DataFrame, col: str, valid_values) -> Tuple[bool, str, int]:
    n = (~df[col].isin(valid_values)).sum() if col in df.columns else 0
    return n == 0, f"[{col}] in allowed set", int(n)

def run_suite(df: pd.DataFrame, checks: list) -> pd.DataFrame:
    """Run a list of (validator_fn, args) and return a report DataFrame."""
    results = []
    for fn, args in checks:
        passed, msg, failures = fn(df, *args)
        results.append({
            "check": msg,
            "status": "PASS" if passed else ("WARN" if failures < 5 else "FAIL"),
            "failures": failures,
        })
    return pd.DataFrame(results)
