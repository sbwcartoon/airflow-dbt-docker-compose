from airflow.hooks.base import BaseHook
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_source_engine() -> Engine:
    src_hook = BaseHook.get_connection("source_db")
    return create_engine(src_hook.get_uri())


def get_analytics_engine() -> Engine:
    analytics_hook = BaseHook.get_connection("analytics_db")
    return create_engine(analytics_hook.get_uri())
