"""
run_pipeline.py — Modular ETL pipeline for supply chain data.
Stages: Extract → Validate → Transform → Load
"""
import pandas as pd, numpy as np, sqlite3, os, json
from datetime import datetime

np.random.seed(42)
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE,"data"); os.makedirs(DATA+"/raw",exist_ok=True); os.makedirs(DATA+"/processed",exist_ok=True)
DB   = os.path.join(DATA,"supply_chain.db")

# ── EXTRACT ────────────────────────────────────────────────────────
def extract():
    print("[EXTRACT] Generating synthetic source data...")
    n=500
    deliveries=pd.DataFrame({
        "waybill_no":[f"WB{i:06d}" for i in range(1,n+1)],
        "site_id":[f"SITE_{np.random.randint(1,51):03d}" for _ in range(n)],
        "vendor":np.random.choice(["FastFuel","NigerDiesel","SwiftHaul"],n),
        "date":pd.date_range("2023-01-01",periods=n,freq="14h").strftime("%Y-%m-%d"),
        "qty_ordered":np.random.randint(500,5000,n),
        "qty_delivered":np.random.randint(400,5100,n),
        "on_time":np.random.choice([0,1],n,p=[0.18,0.82]),
    })
    deliveries.to_csv(f"{DATA}/raw/deliveries.csv",index=False)
    print(f"  Extracted {len(deliveries)} delivery records.")
    return {"deliveries": deliveries}

# ── VALIDATE ───────────────────────────────────────────────────────
def validate(datasets):
    print("\n[VALIDATE] Running data quality checks...")
    df = datasets["deliveries"]
    issues=[]; clean=df.copy()
    missing=df.isnull().sum().sum()
    if missing>0: issues.append(f"Missing values: {missing}")
    dupes=df["waybill_no"].duplicated().sum()
    if dupes>0: issues.append(f"Duplicate waybills: {dupes}")
    neg=( df["qty_delivered"]<0 ).sum()
    if neg>0: issues.append(f"Negative qty_delivered: {neg}"); clean=clean[clean["qty_delivered"]>=0]
    for issue in issues: print(f"  ⚠️  {issue}")
    if not issues: print("  ✅ All checks passed.")
    print(f"  Records after validation: {len(clean):,}")
    return {"deliveries": clean}

# ── TRANSFORM ──────────────────────────────────────────────────────
def transform(datasets):
    print("\n[TRANSFORM] Applying business logic...")
    df = datasets["deliveries"].copy()
    df["date"]           = pd.to_datetime(df["date"])
    df["month"]          = df["date"].dt.to_period("M").astype(str)
    df["qty_variance"]   = df["qty_delivered"] - df["qty_ordered"]
    df["variance_pct"]   = (df["qty_variance"]/df["qty_ordered"]*100).round(2)
    df["accurate"]       = df["variance_pct"].between(-5,5).astype(int)
    df["loaded_at"]      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    vendor_scores=df.groupby("vendor").agg(
        deliveries=("waybill_no","count"),on_time_rate=("on_time","mean"),accuracy_rate=("accurate","mean")
    ).reset_index()
    vendor_scores["composite_score"]=(vendor_scores["on_time_rate"]*50+vendor_scores["accuracy_rate"]*50).round(2)
    print(f"  Enriched {len(df):,} records with {df.shape[1]} columns.")
    return {"deliveries":df,"vendor_scores":vendor_scores}

# ── LOAD ───────────────────────────────────────────────────────────
def load(datasets):
    print("\n[LOAD] Writing to SQLite database and CSV...")
    conn=sqlite3.connect(DB)
    for name,df in datasets.items():
        df.to_sql(name,conn,if_exists="replace",index=False)
        df.to_csv(f"{DATA}/processed/{name}.csv",index=False)
        print(f"  ✅ {name}: {len(df):,} rows → DB + CSV")
    conn.close()

# ── RUN ────────────────────────────────────────────────────────────
if __name__=="__main__":
    print("="*50)
    print("  SUPPLY CHAIN ETL PIPELINE")
    print("="*50)
    raw      = extract()
    validated= validate(raw)
    transformed=transform(validated)
    load(transformed)
    print("\n✅ Pipeline complete.")
    print(f"   Database: {DB}")
    print(f"   Outputs:  {DATA}/processed/")
