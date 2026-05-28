from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timezone, timedelta

from elt.extract import OpenMeteoCurrentExtractor, OpenMeteoHourlyExtractor
from elt.transform import transform_current, transform_hourly
from elt.load import load_current, load_hourly
from risk_engine import run_risk_engine


def run_current_pipeline():
    extractor = OpenMeteoCurrentExtractor()
    raw       = extractor.extract()
    df        = transform_current(raw)
    load_current(df)


def run_hourly_pipeline():
    extractor = OpenMeteoHourlyExtractor()
    raw       = extractor.extract()
    df        = transform_hourly(raw)
    load_hourly(df)


with DAG(
    dag_id="weather_pipeline",
    schedule_interval="*/15 * * * *",
    start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["alerto", "weather"],
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=2),
    },
) as dag:
    
    # ============ BRONZE ============

    task_current = PythonOperator(
        task_id="extract_transform_load_current",
        python_callable=run_current_pipeline,
    )

    task_hourly = PythonOperator(
        task_id="extract_transform_load_hourly_",
        python_callable=run_hourly_pipeline,
    )

    # ============ DBT DEPS ============

    task_dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=(
            "cd /opt/dbt && "
            "dbt deps --profiles-dir /opt/dbt --project-dir /opt/dbt"
        ),
    )

    # ============ SILVER ============

    task_dbt_silver_run = BashOperator(
        task_id="dbt_run_silver",
        bash_command=(
            "cd /opt/dbt && "
            "dbt run --select silver --profiles-dir /opt/dbt --project-dir /opt/dbt"
        ),
    )

    task_dbt_silver_test = BashOperator(
        task_id="dbt_test_silver",
        bash_command=(
            "cd /opt/dbt && "
            "dbt test --select silver --profiles-dir /opt/dbt --project-dir /opt/dbt"
        ),
    )

    # ============ GOLD ============

    task_dbt_gold_run = BashOperator(
        task_id="dbt_run_gold",
        bash_command=(
            "cd /opt/dbt && "
            "dbt run --select gold --profiles-dir /opt/dbt --project-dir /opt/dbt"
        ),
    )

    task_dbt_gold_test = BashOperator(
        task_id="dbt_test_gold",
        bash_command=(
            "cd /opt/dbt && "
            "dbt test --select gold --profiles-dir /opt/dbt --project-dir /opt/dbt"
        ),
    )

    # ============ RISK ENGINE ============

    task_risk_engine = PythonOperator(
        task_id="run_risk_engine",
        python_callable=run_risk_engine,
    )

    [task_current, task_hourly] >> task_dbt_deps >> task_dbt_silver_run >> task_dbt_silver_test >> task_dbt_gold_run >> task_dbt_gold_test >> task_risk_engine