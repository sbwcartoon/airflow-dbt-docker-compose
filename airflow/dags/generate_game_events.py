import os
import random
from typing import List, Dict, Any

import pandas as pd
from airflow.decorators import dag, task

from datetime import datetime, timedelta, UTC

from sqlalchemy import text

from utils.db_connection import get_source_engine


@dag(
    dag_id="generate_game_events",
    start_date=datetime(2025, 8, 1),
    schedule="*/5 * * * *",
    catchup=False,
    tags=["generate source data"],
)
def pipeline():
    @task
    def create_tables_if_not_exists():
        source_engine = get_source_engine()
        with source_engine.begin() as conn:
            conn.execute(text(f"create schema if not exists {os.getenv("SOURCE_POSTGRES_SCHEMA")}"))
            conn.execute(text(f"""
                        create table if not exists {os.getenv("SOURCE_POSTGRES_SCHEMA")}.game_events (
                            event_id serial primary key,
                            user_id int,
                            email text,
                            event_type text,
                            event_at timestamp
                        )
                        """))

    @task(
        retries=2,
        retry_delay=timedelta(minutes=2),
    )
    def add_data():
        events = generate_game_events()
        df = pd.DataFrame(events)

        source_engine = get_source_engine()
        df.to_sql(
            name="game_events",
            con=source_engine,
            schema=os.getenv("SOURCE_POSTGRES_SCHEMA"),
            if_exists="append",
            index=False,
            method=None,
            chunksize=1000,
        )

    create_tables_if_not_exists() >> add_data()


def generate_game_events(num_events: int = 5) -> List[Dict[str, Any]]:
    event_types = ["login", "logout", "match_start", "match_end", "purchase"]

    events = []
    for _ in range(num_events):
        user_id = str(random.randint(100, 200))

        events.append({
            "user_id": user_id,
            "email": f"{user_id}@example.com",
            "event_type": random.choice(event_types),
            "event_at": datetime.now(UTC) - timedelta(seconds=random.randint(0, 60 * 60 * 24)),
        })

    return events


dag = pipeline()
