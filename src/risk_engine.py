from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import pandas as pd


DEFAULT_RULES_PATH = Path(__file__).resolve().parents[1] / "config" / "risk_rules.json"


def load_rules(path: str | Path = DEFAULT_RULES_PATH) -> Dict[str, Any]:
    """Load risk configuration from JSON."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _risk_level(score: int, risk_levels: Dict[str, int]) -> str:
    if score <= risk_levels["low_max"]:
        return "Low"
    if score <= risk_levels["medium_max"]:
        return "Medium"
    if score <= risk_levels["high_max"]:
        return "High"
    return "Critical"


def score_transaction(
    row: pd.Series,
    rules: Dict[str, Any],
) -> Tuple[int, str, str]:
    """Score one enriched transaction and return score, level, and reasons."""
    weights = rules["weights"]
    thresholds = rules["thresholds"]
    reasons: list[str] = []
    score = 0

    amount = float(row["amount"])
    if amount >= thresholds["very_high_amount"]:
        score += weights["very_high_amount"]
        reasons.append("very high transaction amount")
    elif amount >= thresholds["high_amount"]:
        score += weights["high_amount"]
        reasons.append("high transaction amount")

    if int(row.get("velocity_24h", 1)) >= thresholds["velocity_count_24h"]:
        score += weights["high_velocity"]
        reasons.append("high transaction velocity in 24h")

    if row["transaction_country"] in rules["risky_countries"]:
        score += weights["risky_country"]
        reasons.append("transaction in configured high-risk country")

    if row["transaction_country"] != row["home_country"]:
        score += weights["country_mismatch"]
        reasons.append("transaction country differs from customer home country")

    hour = pd.Timestamp(row["timestamp"]).hour
    if thresholds["night_start_hour"] <= hour <= thresholds["night_end_hour"]:
        score += weights["night_transaction"]
        reasons.append("transaction occurred during configured night hours")

    account_age_days = (pd.Timestamp(row["timestamp"]) - pd.Timestamp(row["signup_date"])).days
    if account_age_days <= thresholds["new_account_days"]:
        score += weights["new_account"]
        reasons.append("new customer account")

    if str(row["customer_risk"]).lower() == "high":
        score += weights["high_risk_customer"]
        reasons.append("customer already classified as high risk")

    risk_level = _risk_level(score, rules["risk_levels"])
    return score, risk_level, "; ".join(reasons) if reasons else "no rule triggered"


def add_velocity_feature(transactions: pd.DataFrame) -> pd.DataFrame:
    """Add count of each customer's transactions in the previous 24 hours."""
    if transactions.empty:
        result = transactions.copy()
        result["velocity_24h"] = pd.Series(dtype="int64")
        return result

    required = {"transaction_id", "customer_id", "timestamp"}
    missing = required - set(transactions.columns)
    if missing:
        raise ValueError(f"Missing columns for velocity calculation: {sorted(missing)}")

    working = transactions.copy()
    working["timestamp"] = pd.to_datetime(working["timestamp"])
    working = working.sort_values(["customer_id", "timestamp", "transaction_id"]).reset_index(drop=True)

    frames: list[pd.DataFrame] = []
    for _, group in working.groupby("customer_id", sort=False):
        group = group.sort_values("timestamp").copy()
        indexed = group.set_index("timestamp")
        counts = indexed["transaction_id"].rolling("24h").count().astype(int)
        group["velocity_24h"] = counts.to_numpy()
        frames.append(group)

    return pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)


def monitor_transactions(
    transactions: pd.DataFrame,
    rules: Dict[str, Any] | None = None,
) -> pd.DataFrame:
    """Run all monitoring rules against a transaction DataFrame."""
    rules = rules or load_rules()

    required_columns: Iterable[str] = (
        "transaction_id",
        "customer_id",
        "timestamp",
        "amount",
        "transaction_country",
        "home_country",
        "customer_risk",
        "signup_date",
    )
    missing = set(required_columns) - set(transactions.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    enriched = add_velocity_feature(transactions)

    scored = enriched.apply(
        lambda row: score_transaction(row, rules),
        axis=1,
        result_type="expand",
    )
    scored.columns = ["risk_score", "risk_level", "risk_reasons"]

    result = pd.concat([enriched.reset_index(drop=True), scored], axis=1)
    return result.sort_values(["risk_score", "timestamp"], ascending=[False, False]).reset_index(drop=True)
