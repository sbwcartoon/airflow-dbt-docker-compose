#!/bin/bash

set -e

ENV_FILE="$1"

if [ -z "$ENV_FILE" ]; then
  echo "Usage: $0 <env-file>"
  echo "Example: $0 .env.local"
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "Error: Env file '$ENV_FILE' not found!"
  exit 1
fi

echo "Start airflow and dbt..."
docker compose --env-file "$ENV_FILE" up --build -d
