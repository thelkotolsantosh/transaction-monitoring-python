# Transaction Monitoring & Risk Alerting in Python

A portfolio-ready **transaction monitoring and risk alerting project** built with Python and fully synthetic data.

The project simulates a simplified fraud / operational-risk monitoring workflow:

1. Generate synthetic customer and transaction data.
2. Enrich transactions with 24-hour transaction velocity.
3. Apply transparent rule-based risk scoring.
4. Assign **Low, Medium, High, or Critical** risk levels.
5. Record the exact reasons behind each score.
6. Export High and Critical alerts for review.
7. Review results in a Streamlit dashboard.
8. Validate core logic with automated tests.
9. Run tests automatically with GitHub Actions.

> **Important:** This repository is for education and portfolio demonstration. It does not use real customer data and is not a production fraud-detection system.

## Project Structure

```text
transaction-monitoring-python/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── config/
│   └── risk_rules.json
│
├── data/
│   └── README.md
│
├── outputs/
│   └── .gitkeep
│
├── src/
│   ├── __init__.py
│   ├── generate_data.py
│   ├── main.py
│   └── risk_engine.py
│
├── tests/
│   └── test_risk_engine.py
│
├── .gitignore
├── dashboard.py
├── FAQ.md
├── LICENSE
├── README.md
└── requirements.txt
```

## Risk Rules

The default rules are intentionally simple and explainable.

| Rule | Example logic | Default points |
|---|---|---:|
| High amount | Amount >= 5,000 | 25 |
| Very high amount | Amount >= 10,000 | 35 |
| High velocity | 5+ transactions within 24 hours | 20 |
| Risky country | Country appears in configured list | 20 |
| Country mismatch | Transaction country != home country | 15 |
| Night transaction | Between 00:00 and 05:59 | 10 |
| New account | Account age <= 30 days | 10 |
| High-risk customer | Customer risk = High | 25 |

The rules and thresholds are stored in:

```text
config/risk_rules.json
```

This means the monitoring policy can be changed without editing the scoring code.

## Risk Levels

Default score bands:

| Score | Risk level |
|---:|---|
| 0-19 | Low |
| 20-39 | Medium |
| 40-69 | High |
| 70+ | Critical |

## How the Files Work Together

```text
config/risk_rules.json
        │
        ▼
src/generate_data.py ──► data/customers.csv
        │                data/transactions.csv
        │
        ▼
src/main.py
        │
        ▼
src/risk_engine.py
        │
        ├── adds 24-hour velocity
        ├── applies risk rules
        ├── creates risk score
        ├── assigns risk level
        └── records alert reasons
        │
        ▼
outputs/monitored_transactions.csv
outputs/alerts.csv
        │
        ▼
dashboard.py
```

## Requirements

Recommended:

- Python 3.11 or 3.12
- pip
- Git

Python packages are listed in `requirements.txt`.

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/transaction-monitoring-python.git
cd transaction-monitoring-python
```

Create a virtual environment.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Project

### Option 1 — Run the full batch process

```bash
python -m src.main
```

If the CSV input files do not exist, the project automatically generates synthetic data first.

Expected output:

```text
Transactions reviewed: 10,000
High/Critical alerts: ...
Saved outputs/monitored_transactions.csv
Saved outputs/alerts.csv
```

### Option 2 — Generate only synthetic data

```bash
python -m src.generate_data
```

This creates:

```text
data/customers.csv
data/transactions.csv
```

## Run the Dashboard

```bash
streamlit run dashboard.py
```

The dashboard shows:

- total transactions;
- number of High and Critical alerts;
- average risk score;
- risk-level distribution;
- transaction-level alert reasons;
- filters by score and risk level;
- CSV download of filtered results.

## Run Tests

```bash
pytest -q
```

The tests validate:

- Low-risk scoring;
- Critical-risk scoring;
- 24-hour transaction velocity;
- expected monitoring output columns.

## GitHub Actions

The workflow file is located at:

```text
.github/workflows/tests.yml
```

On every push and pull request, GitHub automatically:

1. checks out the repository;
2. installs Python 3.12;
3. installs dependencies;
4. runs `pytest`.

## Example Alert

A transaction may receive a result similar to:

```text
Risk Score: 100
Risk Level: Critical
Reasons:
- very high transaction amount
- high transaction velocity in 24h
- transaction in configured high-risk country
- transaction country differs from customer home country
- customer already classified as high risk
```

This explainability is important because an analyst can see **why** the alert was generated.

## Why This Project Is Useful

This repository demonstrates practical skills relevant to fraud prevention, AML operations, risk monitoring, compliance analytics, and junior data/risk analyst roles:

- Python;
- Pandas;
- data generation and cleaning;
- transaction monitoring;
- configurable business rules;
- risk scoring;
- alert generation;
- explainable decision logic;
- automated testing;
- Streamlit dashboards;
- Git/GitHub;
- CI with GitHub Actions.

## Possible Future Improvements

The project can later be extended with:

- rolling 1-hour, 7-day, and 30-day transaction metrics;
- customer-specific behavioural baselines;
- amount deviation from normal customer behaviour;
- device and IP monitoring;
- merchant risk scoring;
- sanctions and watchlist screening;
- SQL/PostgreSQL storage;
- FastAPI API layer;
- case-management workflow;
- investigator notes and dispositions;
- machine-learning anomaly detection;
- model/rule performance tracking;
- Docker deployment;
- authentication and audit logs.

## Portfolio Talking Point

A concise interview explanation:

> I built a Python transaction-monitoring project using synthetic customer and payment data. The system calculates 24-hour transaction velocity, applies configurable risk rules, creates explainable risk scores, categorises transactions into four risk levels, and exports high-risk alerts. I also added automated tests, GitHub Actions, and a Streamlit dashboard so the project demonstrates both risk-monitoring logic and basic software-engineering practices.

## FAQ

See [`FAQ.md`](FAQ.md) for 20 common project and interview questions with answers.

## License

This project is released under the MIT License.
