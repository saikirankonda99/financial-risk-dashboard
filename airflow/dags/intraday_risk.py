"""Intraday risk refresh - runs every 15 minutes during trading hours."""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    "intraday_risk",
    default_args={"owner": "risk-team", "retries": 1},
    start_date=datetime(2026, 1, 1),
    schedule_interval="*/15 9-16 * * 1-5",
    catchup=False,
    tags=["risk", "intraday"],
) as dag:

    consume_kinesis = BashOperator(
        task_id="consume_kinesis_trades",
        bash_command="python -m src.ingestion.kinesis_consumer --batch-size 1000",
    )

    update_positions = BashOperator(
        task_id="update_positions",
        bash_command="python -m src.etl.daily_positions",
    )

    refresh_var = BashOperator(
        task_id="refresh_var",
        bash_command="python -m src.risk.var --method parametric --horizon 1",
    )

    consume_kinesis >> update_positions >> refresh_var
