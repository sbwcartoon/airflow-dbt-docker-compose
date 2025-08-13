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

if grep -q '^AIRFLOW_UID=' "$ENV_FILE" 2>/dev/null; then
  sed -i '' "s|^AIRFLOW_UID=.*|AIRFLOW_UID=$(id -u)|" "$ENV_FILE"
else
  printf "\nAIRFLOW_UID=%s\n" $(id -u) >> "$ENV_FILE"
fi

echo "Updated AIRFLOW_UID in $ENV_FILE"
