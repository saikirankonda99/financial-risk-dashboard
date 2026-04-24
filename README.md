# Financial Risk & Portfolio Dashboard

[![Python](https://img.shields.io/badge/Python-3.11-yellow)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/AWS-Redshift-orange)](https://aws.amazon.com/redshift/)
[![Airflow](https://img.shields.io/badge/Airflow-2.8-blue)](https://airflow.apache.org/)
[![Tableau](https://img.shields.io/badge/Tableau-Desktop-informational)](https://www.tableau.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Real-time portfolio risk monitoring dashboard aggregating trading and transaction data from 12 upstream systems. Applies time-series forecasting and Monte Carlo simulation to compute Value-at-Risk (VaR) and Expected Shortfall (ES) scenarios.

> **Impact:** Shifted the finance team from weekly to **intraday risk reporting**, enabling faster response to market-moving events.

---

## Architecture

```
 12 Trading /            AWS Lambda             Amazon S3          Amazon Redshift
 Transaction    ──────▶  Ingestors    ──────▶   Data Lake  ──────▶ (Analytics DW)
 Systems                                                                   │
                                                                           ▼
                                                                ┌──────────────────┐
                                                                │  Airflow DAGs    │
                                                                │  ETL + Monte     │
                                                                │  Carlo + VaR     │
                                                                └────────┬─────────┘
                                                                         │
                                                                         ▼
                                                                ┌──────────────────┐
                                                                │  Tableau / QuickSight
                                                                │  Risk Dashboards │
                                                                └──────────────────┘
```

## Tech Stack

| Layer | Tool |
|---|---|
| Ingestion | AWS Lambda, Kinesis, Python |
| Storage | S3 (Parquet), Redshift |
| Transform | Python, SQL, dbt |
| Orchestration | Apache Airflow (MWAA) |
| Modeling | NumPy, SciPy, pandas, arch (GARCH) |
| Viz | Tableau, QuickSight, Plotly |

## Key Features

- **Real-time position aggregation** across 12 source systems via Kinesis streams
- **Value-at-Risk (VaR)** — Historical, Parametric, and Monte Carlo methodologies
- **Expected Shortfall (ES/CVaR)** — tail-risk measure beyond VaR
- **Monte Carlo simulation** — 10,000-path stock price simulation with GBM
- **GARCH volatility forecasting** — dynamic vol inputs instead of flat historical
- **Stress testing** — shock scenarios (rate +100bps, equity -20%, FX crash)
- **Backtesting** — Kupiec POF + Christoffersen independence tests

## Repository Structure

```
financial-risk-dashboard/
├── src/
│   ├── ingestion/
│   │   ├── kinesis_consumer.py
│   │   └── market_data_fetcher.py
│   ├── risk/
│   │   ├── var.py                 # Historical / Parametric / MC VaR
│   │   ├── expected_shortfall.py
│   │   ├── monte_carlo.py         # GBM simulation
│   │   ├── garch_volatility.py
│   │   └── stress_test.py
│   ├── etl/
│   │   ├── load_to_redshift.py
│   │   └── daily_positions.py
│   └── backtest/
│       └── var_backtest.py
├── airflow/dags/
│   ├── intraday_risk.py
│   └── eod_var_calculation.py
├── dashboards/tableau/
│   ├── portfolio_risk.twb
│   └── screenshots/
├── notebooks/
│   ├── 01_var_methodology.ipynb
│   └── 02_monte_carlo_demo.ipynb
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample_portfolio.csv
├── scripts/
│   ├── generate_mock_trades.py
│   └── fetch_market_data.py
├── tests/
├── sql/
│   ├── create_schemas.sql
│   └── analytics/
└── README.md
```

## Quick Start

### 1. Install

```bash
git clone https://github.com/YOUR_USERNAME/financial-risk-dashboard.git
cd financial-risk-dashboard
pip install -r requirements.txt
```

### 2. Generate sample portfolio + market data

```bash
python scripts/generate_mock_trades.py --n-positions 500
```

### 3. Compute VaR

```bash
python -m src.risk.var --portfolio data/sample_portfolio.csv --method monte_carlo --confidence 0.99
```

Sample output:
```
Portfolio Value:         $12,458,320.00
1-day 99% VaR (MC):      $  342,117.85   (2.75%)
1-day 99% ES (MC):       $  418,093.20   (3.36%)
Simulations:             10,000
```

### 4. Run backtesting

```bash
python -m src.backtest.var_backtest --lookback 252 --confidence 0.99
```

### 5. Launch Airflow (optional)

```bash
cd airflow && airflow standalone
```

## VaR Methodologies

### Historical Simulation
Ranks the past N daily P&L observations. 99% VaR = 1st percentile loss.

### Parametric (Variance-Covariance)
Assumes returns are normally distributed: `VaR = Portfolio × σ × √t × Z`

### Monte Carlo
Simulates 10,000 paths via Geometric Brownian Motion using GARCH-forecasted volatility and a Cholesky-decomposed covariance matrix for multi-asset portfolios.

## Dashboards

| Dashboard | KPIs |
|---|---|
| **Portfolio Overview** | Total NAV, daily P&L, top positions |
| **Risk Heatmap** | VaR/ES by asset class, sector, region |
| **Stress Scenarios** | Impact of rate, equity, FX shocks |
| **Backtest Results** | VaR breaches vs. expected, Kupiec POF test |

## Results on Sample Portfolio

| Metric | Value |
|---|---|
| Portfolio NAV | $12.4M |
| 99% 1-day VaR (MC) | $342K |
| 99% 1-day ES (MC) | $418K |
| VaR breach rate (252d backtest) | 1.2% (expected 1.0%) |
| Kupiec POF p-value | 0.68 (accept) |

## License

MIT — see [LICENSE](LICENSE).

---

**Author:** Sai Kiran Konda · [LinkedIn](https://linkedin.com/in/sai-kirankonda) · saikiran1.konda@gmail.com
