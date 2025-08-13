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

sh init-airflow-uid.sh "$ENV_FILE"
sh init-ssh-key.sh "$ENV_FILE"
sh up.sh "$ENV_FILE"