#!/usr/bin/env bash
set -e

echo "===================================="
echo "Starting Incoming Webhook Addon"
echo "===================================="

# Get configuration
CONFIG_PATH="/data/options.json"

# Extract configuration values
export JWT_SECRET=$(jq -r '.jwt_secret' $CONFIG_PATH)
export PORT=$(jq -r '.port' $CONFIG_PATH)
export LOG_LEVEL=$(jq -r '.log_level' $CONFIG_PATH)
export SWITCHES=$(jq -c '.switches' $CONFIG_PATH)

# Home Assistant configuration
export SUPERVISOR_TOKEN="${SUPERVISOR_TOKEN}"
export HA_URL="http://supervisor/core"

echo "Configuration loaded:"
echo "  Port: $PORT"
echo "  Log Level: $LOG_LEVEL"
echo "  Switches configured: $(echo $SWITCHES | jq length)"

# Start the FastAPI application
cd /app
exec python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT --log-level $(echo $LOG_LEVEL | tr '[:upper:]' '[:lower:]')
