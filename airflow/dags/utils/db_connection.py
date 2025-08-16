import os

from airflow.hooks.base import BaseHook
from google.cloud.bigquery import Client
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_source_engine() -> Engine:
    src_hook = BaseHook.get_connection("source_db")
    return create_engine(src_hook.get_uri())


def get_analytics_client() -> Client:
    return Client(project=os.getenv("ANALYTICS_GCP_PROJECT_ID"))
