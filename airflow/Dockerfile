FROM apache/airflow:slim-3.0.4rc1-python3.12

WORKDIR /opt/airflow

COPY pyproject.toml poetry.lock ./
RUN pip install --upgrade pip poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

COPY ./dags ./dags

USER airflow
