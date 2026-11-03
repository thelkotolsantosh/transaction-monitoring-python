from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.generate_data import generate_dataset
from src.risk_engine import monitor_transactions


DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")


def run() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    transactions_file = DATA_DIR / "transactions.csv"
    customers_file = DATA_DIR / "customers.csv"

    if not transactions_file.exists() or not customers_file.exists():
        print("Input data not found. Generating synthetic data...")
        generate_dataset(output_dir=DATA_DIR)

    transactions = pd.read_csv(
        transactions_file,
        parse_dates=["timestamp", "signup_date"],
    )

    monitored = monitor_transactions(transactions)
    monitored.to_csv(OUTPUT_DIR / "monitored_transactions.csv", index=False)

    alerts = monitored[monitored["risk_level"].isin(["High", "Critical"])].copy()
    alerts.to_csv(OUTPUT_DIR / "alerts.csv", index=False)

    print(f"Transactions reviewed: {len(monitored):,}")
    print(f"High/Critical alerts: {len(alerts):,}")
    print("Saved outputs/monitored_transactions.csv")
    print("Saved outputs/alerts.csv")


if __name__ == "__main__":
    run()
