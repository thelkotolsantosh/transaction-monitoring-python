# Transaction Monitoring Project — 20 FAQs

## 1. What is the purpose of this project?
The project simulates a simple transaction-monitoring workflow. It generates synthetic customer and transaction data, checks each transaction against configurable risk rules, assigns a risk score, classifies the transaction as Low, Medium, High, or Critical risk, and exports alerts for investigation.

## 2. Why did you use synthetic data?
Real transaction data contains sensitive customer and financial information. Synthetic data lets me demonstrate the monitoring logic safely and publicly on GitHub without exposing confidential data.

## 3. What problem does the risk engine solve?
The risk engine converts several suspicious transaction patterns into a single explainable risk score. Instead of only saying that a transaction is suspicious, it also records the reasons that caused the score.

## 4. What rules are used in the project?
The current rules check transaction amount, 24-hour transaction velocity, risky countries, country mismatch, night-time activity, new accounts, and customers already classified as high risk.

## 5. Why are the rules stored in a JSON file?
Keeping rules in `config/risk_rules.json` separates business logic from Python code. Thresholds and weights can be changed without rewriting the monitoring engine.

## 6. How is the risk score calculated?
Each triggered rule adds a configured number of points. For example, a very high transaction amount can add one score, while a country mismatch or high transaction velocity adds additional points. The total becomes the transaction's risk score.

## 7. How are risk levels assigned?
The total score is compared with configurable limits. In the default configuration, lower scores are Low or Medium, while larger scores become High or Critical.

## 8. What is transaction velocity?
Transaction velocity is the number of transactions performed by the same customer within a short time window. This project counts a customer's transactions in the previous 24 hours, including the current transaction.

## 9. Why can high transaction velocity be risky?
A sudden burst of transactions can indicate account takeover, automated abuse, card testing, fraud, or unusual account behaviour. It does not prove fraud, but it can justify further review.

## 10. Why is country mismatch monitored?
If a customer's transaction country differs from the customer's recorded home country, the activity may deserve additional review. It can also be completely legitimate, such as travel, so the project uses it as one factor rather than a final fraud decision.

## 11. Why are night-time transactions monitored?
Unusual-hour activity can sometimes indicate suspicious behaviour. This project gives such transactions a small additional score. In a real system, the rule would normally be adjusted for customer behaviour, geography, and business context.

## 12. Does a High or Critical score mean the transaction is fraudulent?
No. The system creates alerts, not final fraud decisions. A high score means the transaction has multiple risk indicators and should be reviewed by an investigator or another decision process.

## 13. What does `generate_data.py` do?
It creates synthetic customer profiles and transactions. The output is saved as CSV files in the `data/` folder and becomes the input for the monitoring engine.

## 14. What does `risk_engine.py` do?
It contains the core monitoring logic. It loads risk rules, calculates transaction velocity, evaluates each transaction, assigns risk scores, and records the reasons behind each alert.

## 15. What does `main.py` do?
It is the main batch-processing entry point. It loads or generates data, runs the risk engine, saves all monitored transactions, and writes High and Critical transactions to a separate alerts file.

## 16. What is the purpose of the Streamlit dashboard?
The dashboard provides a simple visual interface for reviewing transaction counts, risk-level distribution, scores, alert reasons, and filtered suspicious transactions.

## 17. Why are automated tests included?
Tests confirm that important rules work as expected. They help catch mistakes when risk logic changes and demonstrate basic software-engineering discipline in a portfolio project.

## 18. What does GitHub Actions do in this repository?
GitHub Actions automatically installs the project dependencies and runs the tests whenever code is pushed or a pull request is opened. This provides a basic continuous-integration workflow.

## 19. How could this project be improved for a real environment?
Possible improvements include customer behavioural baselines, rolling amount totals, device and IP signals, sanctions screening, machine-learning models, database storage, case-management integration, alert prioritisation, authentication, audit logs, and monitoring of model or rule performance.

## 20. What did you learn by building this project?
The project demonstrates how transaction data moves from generation to enrichment, rule evaluation, risk scoring, alert creation, testing, reporting, and dashboard review. It also shows why explainability and configurable thresholds are important in risk-monitoring systems.
