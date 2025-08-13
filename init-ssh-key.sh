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

KEY_DIR="./dbt/ssh_host_keys"
KEY_FILE="$KEY_DIR/ssh_host_rsa_key"
PUB_KEY_FILE="$KEY_FILE.pub"

mkdir -p "$KEY_DIR"

if [ ! -f "$KEY_FILE" ]; then
  echo "Generating SSH host key at $KEY_FILE..."
  ssh-keygen -t rsa -f "$KEY_FILE" -N '' -q
  chmod 600 "$KEY_FILE"
  chmod 644 "$PUB_KEY_FILE"
else
  echo "SSH host key already exists at $KEY_FILE, skipping generation."
fi

if [ ! -f "$PUB_KEY_FILE" ]; then
  echo "Error: public key file not found: $PUB_KEY_FILE"
  exit 1
fi

PUB_KEY_CONTENT=$(cat "$PUB_KEY_FILE")

if grep -q '^SSH_HOST_KEY=' "$ENV_FILE" 2>/dev/null; then
  sed -i '' "s|^SSH_HOST_KEY=.*|SSH_HOST_KEY=\"$PUB_KEY_CONTENT\"|" "$ENV_FILE"
else
  printf '\nSSH_HOST_KEY="%s"\n' "$PUB_KEY_CONTENT" >> "$ENV_FILE"
fi

echo "Updated SSH_HOST_KEY in $ENV_FILE"
