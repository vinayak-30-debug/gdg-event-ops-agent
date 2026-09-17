#!/usr/bin/env bash
# Render Build Script
# Installs dependencies and reconstructs the service_account.json from an
# environment variable so that secrets never touch the Git repo.

set -o errexit  # exit on error

pip install --upgrade pip
pip install -r requirements.txt

# If the GOOGLE_SERVICE_ACCOUNT_JSON env var is set, write it to a file
# so that gspread can authenticate at runtime.
if [ -n "$GOOGLE_SERVICE_ACCOUNT_JSON" ]; then
    echo "$GOOGLE_SERVICE_ACCOUNT_JSON" > service_account.json
    echo "✓ service_account.json reconstructed from environment variable"
else
    echo "⚠ GOOGLE_SERVICE_ACCOUNT_JSON not set — Sheets integration will be unavailable"
fi
