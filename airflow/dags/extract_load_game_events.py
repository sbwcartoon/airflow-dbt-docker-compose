import os

import pandas as pd

from airflow.decorators import dag, task

from datetime import datetime

from google.api_core.exceptions import NotFound
from google.cloud.bigquery import Dataset, LoadJobConfig

from utils.db_connection import get_analytics_client, get_source_engine
from utils.preprocessing import mask_email


@dag(
    dag_id="extract_load_game_events",
    start_date=datetime(2025, 8, 1),
    schedule="*/10 * * * *",
    catchup=False,
    tags=["extract", "load"],
)
def pipeline():
    @task
    def create_schema_and_tables_if_not_exists():
        analytics_client = get_analytics_client()

        project_id = os.getenv("ANALYTICS_GCP_PROJECT_ID")
        dataset_id = "raw"
        table_id = f"{project_id}.{dataset_id}.game_events"
        try:
            analytics_client.get_dataset(f"{project_id}.{dataset_id}")
        except NotFound:
            dataset = Dataset(f"{project_id}.{dataset_id}")
            dataset.location = os.getenv("ANALYTICS_GCP_LOCATION", "US")
            analytics_client.create_dataset(dataset)

        query_job = analytics_client.query(f"""
                              create table if not exists `{table_id}`
                              (
                                  event_id int64,
                                  user_id int64,
                                  email string,
                                  event_type string,
                                  event_at timestamp,
                                  loaded_at timestamp
                              )
                              """)
        query_job.result()

    @task()
    def extract() -> pd.DataFrame:
        src_engine = get_source_engine()
        return pd.read_sql(
            sql=f"""
                select event_id,
                       user_id,
                       email,
                       event_type,
                       event_at,
                       now() as loaded_at
                from {os.getenv("SOURCE_POSTGRES_SCHEMA")}.game_events
                """,
            con=src_engine,
        )

    @task()
    def preprocess(df: pd.DataFrame) -> pd.DataFrame:
        df["email"] = df["email"].apply(lambda x: mask_email(x))
        return df

    @task()
    def load(df: pd.DataFrame) -> None:
        analytics_client = get_analytics_client()

        project_id = os.getenv("ANALYTICS_GCP_PROJECT_ID")
        dataset_id = "raw"
        table_id = f"{project_id}.{dataset_id}.game_events"

        analytics_client.query(f"truncate table `{table_id}`").result()

        job_config = LoadJobConfig(write_disposition="WRITE_APPEND")
        analytics_client.load_table_from_dataframe(
            dataframe=df,
            destination=table_id,
            job_config=job_config
        ).result()

    extracted_df = extract()
    preprocessed_df = preprocess(extracted_df)

    create_schema_and_tables_if_not_exists() >> extracted_df >> preprocessed_df >> load(preprocessed_df)


dag = pipeline()
