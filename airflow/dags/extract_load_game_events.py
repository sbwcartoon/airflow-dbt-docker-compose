import os

import pandas as pd

from airflow.decorators import dag, task

from datetime import datetime

from sqlalchemy import text

from utils.db_connection import get_analytics_engine, get_source_engine
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
        analytics_engine = get_analytics_engine()

        with analytics_engine.begin() as conn:
            conn.execute(text("create schema if not exists raw"))
            conn.execute(text("""
                              create table if not exists raw.game_events
                              (
                                  event_id int primary key,
                                  user_id int,
                                  email text,
                                  event_type text,
                                  event_at timestamp,
                                  loaded_at timestamp
                              )
                              """))

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
        analytics_engine = get_analytics_engine()

        with analytics_engine.begin() as conn:
            conn.execute(text("truncate table raw.game_events"))

            df.to_sql(
                name="game_events",
                con=conn,
                schema="raw",
                if_exists="append",
                index=False,
            )

    extracted_df = extract()
    preprocessed_df = preprocess(extracted_df)

    create_schema_and_tables_if_not_exists() >> extracted_df >> preprocessed_df >> load(preprocessed_df)


dag = pipeline()
