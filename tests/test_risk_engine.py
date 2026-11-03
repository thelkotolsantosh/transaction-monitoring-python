import pandas as pd

from src.risk_engine import add_velocity_feature, monitor_transactions, score_transaction


RULES = {
    "weights": {
        "high_amount": 25,
        "very_high_amount": 35,
        "high_velocity": 20,
        "risky_country": 20,
        "country_mismatch": 15,
        "night_transaction": 10,
        "new_account": 10,
        "high_risk_customer": 25,
    },
    "thresholds": {
        "high_amount": 5000,
        "very_high_amount": 10000,
        "velocity_count_24h": 5,
        "new_account_days": 30,
        "night_start_hour": 0,
        "night_end_hour": 5,
    },
    "risk_levels": {
        "low_max": 19,
        "medium_max": 39,
        "high_max": 69,
    },
    "risky_countries": ["IR", "KP", "SY"],
}


def test_low_risk_transaction():
    row = pd.Series(
        {
            "amount": 100,
            "velocity_24h": 1,
            "transaction_country": "IN",
            "home_country": "IN",
            "timestamp": pd.Timestamp("2026-01-10 12:00:00"),
            "signup_date": pd.Timestamp("2024-01-01"),
            "customer_risk": "Low",
        }
    )

    score, level, reasons = score_transaction(row, RULES)
    assert score == 0
    assert level == "Low"
    assert reasons == "no rule triggered"


def test_critical_transaction():
    row = pd.Series(
        {
            "amount": 15000,
            "velocity_24h": 7,
            "transaction_country": "IR",
            "home_country": "IN",
            "timestamp": pd.Timestamp("2026-01-10 02:00:00"),
            "signup_date": pd.Timestamp("2026-01-01"),
            "customer_risk": "High",
        }
    )

    score, level, reasons = score_transaction(row, RULES)
    assert score == 135
    assert level == "Critical"
    assert "very high transaction amount" in reasons
    assert "high transaction velocity" in reasons
    assert "high-risk country" in reasons


def test_velocity_feature_counts_transactions_in_24_hours():
    tx = pd.DataFrame(
        {
            "transaction_id": ["T1", "T2", "T3"],
            "customer_id": ["C1", "C1", "C1"],
            "timestamp": pd.to_datetime(
                [
                    "2026-01-01 10:00:00",
                    "2026-01-01 12:00:00",
                    "2026-01-02 11:00:00",
                ]
            ),
        }
    )

    result = add_velocity_feature(tx)
    assert result["velocity_24h"].tolist() == [1, 2, 2]


def test_monitor_transactions_adds_risk_columns():
    tx = pd.DataFrame(
        {
            "transaction_id": ["T1"],
            "customer_id": ["C1"],
            "timestamp": pd.to_datetime(["2026-01-01 12:00:00"]),
            "amount": [100],
            "transaction_country": ["IN"],
            "home_country": ["IN"],
            "customer_risk": ["Low"],
            "signup_date": pd.to_datetime(["2024-01-01"]),
        }
    )

    result = monitor_transactions(tx, rules=RULES)
    assert {"velocity_24h", "risk_score", "risk_level", "risk_reasons"}.issubset(result.columns)
    assert result.loc[0, "risk_level"] == "Low"
