from pathlib import Path

import pandas as pd
import streamlit as st

from src.generate_data import generate_dataset
from src.risk_engine import monitor_transactions


DATA_FILE = Path("data/transactions.csv")
OUTPUT_FILE = Path("outputs/monitored_transactions.csv")

st.set_page_config(page_title="Transaction Monitoring Dashboard", layout="wide")
st.title("Transaction Monitoring & Risk Alerting Dashboard")
st.caption("Portfolio project using synthetic data and transparent rule-based monitoring.")

if not DATA_FILE.exists():
    generate_dataset(output_dir="data")

if not OUTPUT_FILE.exists():
    transactions = pd.read_csv(DATA_FILE, parse_dates=["timestamp", "signup_date"])
    monitored = monitor_transactions(transactions)
    Path("outputs").mkdir(exist_ok=True)
    monitored.to_csv(OUTPUT_FILE, index=False)

monitored = pd.read_csv(OUTPUT_FILE, parse_dates=["timestamp", "signup_date"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Transactions", f"{len(monitored):,}")
col2.metric("Critical", int((monitored["risk_level"] == "Critical").sum()))
col3.metric("High", int((monitored["risk_level"] == "High").sum()))
col4.metric("Average Risk Score", f"{monitored['risk_score'].mean():.1f}")

st.subheader("Risk distribution")
risk_counts = (
    monitored["risk_level"]
    .value_counts()
    .reindex(["Low", "Medium", "High", "Critical"], fill_value=0)
)
st.bar_chart(risk_counts)

st.subheader("Filter alerts")
selected_levels = st.multiselect(
    "Risk level",
    options=["Low", "Medium", "High", "Critical"],
    default=["High", "Critical"],
)

min_score = st.slider(
    "Minimum risk score",
    min_value=int(monitored["risk_score"].min()),
    max_value=int(monitored["risk_score"].max()),
    value=min(40, int(monitored["risk_score"].max())),
)

filtered = monitored[
    monitored["risk_level"].isin(selected_levels)
    & (monitored["risk_score"] >= min_score)
].copy()

st.dataframe(
    filtered[
        [
            "transaction_id",
            "customer_id",
            "timestamp",
            "amount",
            "transaction_country",
            "home_country",
            "velocity_24h",
            "risk_score",
            "risk_level",
            "risk_reasons",
        ]
    ],
    use_container_width=True,
)

st.download_button(
    "Download filtered alerts as CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_transaction_alerts.csv",
    mime="text/csv",
)
