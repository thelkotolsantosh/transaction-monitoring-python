from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


COUNTRIES = ["IN", "US", "GB", "AE", "SG", "DE", "IR", "KP", "SY"]
CHANNELS = ["card", "bank_transfer", "wallet", "upi"]
MERCHANT_CATEGORIES = [
    "grocery",
    "electronics",
    "travel",
    "fuel",
    "entertainment",
    "cash_equivalent",
]


def generate_customers(
    n_customers: int = 500,
    seed: int = 42,
    reference_date: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Create a synthetic customer master table."""
    rng = np.random.default_rng(seed)
    ref_date = pd.Timestamp(reference_date) if reference_date is not None else pd.Timestamp.today().normalize()

    customer_ids = [f"CUST{i:05d}" for i in range(1, n_customers + 1)]
    signup_days_ago = rng.integers(1, 1500, size=n_customers)

    customers = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "home_country": rng.choice(COUNTRIES[:6], size=n_customers),
            "customer_risk": rng.choice(
                ["Low", "Medium", "High"],
                size=n_customers,
                p=[0.70, 0.22, 0.08],
            ),
            "signup_date": ref_date - pd.to_timedelta(signup_days_ago, unit="D"),
        }
    )
    return customers


def generate_transactions(
    customers: pd.DataFrame,
    n_transactions: int = 10_000,
    seed: int = 42,
    reference_date: str | pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Create synthetic transactions linked to the supplied customer table."""
    rng = np.random.default_rng(seed + 1)
    ref_date = pd.Timestamp(reference_date) if reference_date is not None else pd.Timestamp.today().floor("s")

    customer_ids = rng.choice(customers["customer_id"], size=n_transactions)
    customer_lookup = customers.set_index("customer_id")

    # Most transactions are small, but a long tail creates occasional large values.
    amounts = np.round(rng.lognormal(mean=5.4, sigma=1.05, size=n_transactions), 2)

    # Transactions are spread across the last 60 days.
    seconds_ago = rng.integers(0, 60 * 24 * 60 * 60, size=n_transactions)
    timestamps = ref_date - pd.to_timedelta(seconds_ago, unit="s")

    countries = rng.choice(
        COUNTRIES,
        size=n_transactions,
        p=[0.47, 0.13, 0.08, 0.08, 0.06, 0.06, 0.04, 0.03, 0.05],
    )

    transactions = pd.DataFrame(
        {
            "transaction_id": [f"TXN{i:07d}" for i in range(1, n_transactions + 1)],
            "customer_id": customer_ids,
            "timestamp": pd.to_datetime(timestamps),
            "amount": amounts,
            "transaction_country": countries,
            "channel": rng.choice(CHANNELS, size=n_transactions),
            "merchant_category": rng.choice(MERCHANT_CATEGORIES, size=n_transactions),
        }
    )

    transactions["home_country"] = transactions["customer_id"].map(customer_lookup["home_country"])
    transactions["customer_risk"] = transactions["customer_id"].map(customer_lookup["customer_risk"])
    transactions["signup_date"] = transactions["customer_id"].map(customer_lookup["signup_date"])

    return transactions.sort_values("timestamp").reset_index(drop=True)


def generate_dataset(
    output_dir: str | Path = "data",
    n_customers: int = 500,
    n_transactions: int = 10_000,
    seed: int = 42,
    reference_date: str | pd.Timestamp | None = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Generate and save customer and transaction CSV files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    customers = generate_customers(n_customers=n_customers, seed=seed, reference_date=reference_date)
    transactions = generate_transactions(
        customers=customers,
        n_transactions=n_transactions,
        seed=seed,
        reference_date=reference_date,
    )

    customers.to_csv(output_path / "customers.csv", index=False)
    transactions.to_csv(output_path / "transactions.csv", index=False)
    return customers, transactions


if __name__ == "__main__":
    generate_dataset()
    print("Synthetic data created in the data/ folder.")
