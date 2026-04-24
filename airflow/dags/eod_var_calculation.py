"""Nightly VaR calculation across all portfolios."""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator


default_args = {"owner": "risk-team", "retries": 2, "retry_delay": timedelta(minutes=5)}


with DAG(
    "eod_var_calculation",
    default_args=default_args,
    description="Compute EOD VaR/ES for all portfolios",
    start_date=datetime(2026, 1, 1),
    schedule_interval="30 17 * * 1-5",
    catchup=False,
    tags=["risk", "var"],
) as dag:

    fetch_market_data = BashOperator(
        task_id="fetch_market_data",
        bash_command="python /opt/scripts/fetch_market_data.py",
    )

    compute_var = BashOperator(
        task_id="compute_var",
        bash_command="python -m src.risk.var --method monte_carlo --confidence 0.99",
    )

    run_stress_tests = BashOperator(
        task_id="stress_tests",
        bash_command="python -c 'from src.risk import stress_test; import pandas as pd; "
                     "p = pd.read_csv(\"data/sample_portfolio.csv\"); "
                     "print(stress_test.run_all(p))'",
    )

    load_redshift = BashOperator(
        task_id="load_redshift",
        bash_command="python -m src.etl.load_to_redshift",
    )

    fetch_market_data >> compute_var >> run_stress_tests >> load_redshift
