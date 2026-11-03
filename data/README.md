# Data Folder

This project uses **synthetic data only**. No real customer, account, payment, or personally identifiable information is required.

Run:

```bash
python -m src.generate_data
```

That command creates:

- `customers.csv` — synthetic customer profiles.
- `transactions.csv` — synthetic transactions linked to those customers.

The generated CSV files are ignored by Git through `.gitignore` so the repository stays lightweight.
