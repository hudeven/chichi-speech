#!/bin/bash
# Startup script for Chichi Speech Service
# Handles:
# 1. Daemonizing (runs in background)
# 2. Auto-restart on failure
# 3. Managing dependencies (uv run)

# Configuration
PORT=${PORT:-9090}
HOST=${HOST:-"0.0.0.0"}
WORKERS=${WORKERS:-1}     # Default 1 worker to save RAM (1.7B model)
THREADS=${THREADS:-4}     # Threads per worker for IO handling
TIMEOUT=${TIMEOUT:-300}   # 5 minutes timeout for slow generations
# Set the virtual environment path (Local variable, passed to background process)
ENV_PATH=${UV_PROJECT_ENVIRONMENT:-"/Users/$USER/envs/chichi-speech"}
LOG_FILE="/tmp/chichi_server.log"

echo "=========================================="
echo "Starting Chichi Speech Service (Production)"
echo "Host: $HOST"
echo "Port: $PORT"
echo "Workers: $WORKERS"
echo "Threads per worker: $THREADS"
echo "Environment: $ENV_PATH"
echo "Log File: $LOG_FILE"
echo "=========================================="

# 1. Parse arguments
REF_AUDIO_ARG=""
REF_TEXT_ARG=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --ref-audio)
      REF_AUDIO_ARG="$2"
      shift # past argument
      shift # past value
      ;;
    --ref-text)
      REF_TEXT_ARG="$2"
      shift # past argument
      shift # past value
      ;;
    *)
      # Unknown option, maybe just skip or error? 
      # For now, let's assume valid args or ignore
      shift 
      ;;
  esac
done

if [ -n "$REF_AUDIO_ARG" ]; then
    echo "Using Ref Audio (CLI): $REF_AUDIO_ARG"
    export REF_AUDIO="$REF_AUDIO_ARG"
fi

if [ -n "$REF_TEXT_ARG" ]; then
    echo "Using Ref Text (CLI): $REF_TEXT_ARG"
    export REF_TEXT="$REF_TEXT_ARG"
fi

# 2. Kill any existing process on port
PID=$(lsof -ti :$PORT)
if [ -n "$PID" ]; then
    echo "Killing existing process on port $PORT (PID: $PID)..."
    kill -9 $PID
fi

# 2. Start the service with auto-restart loop
# We run this loop in the background.

nohup bash -c "
export UV_PROJECT_ENVIRONMENT='$ENV_PATH'
export BATCH_SIZE='${BATCH_SIZE}'
while true; do
  echo \"[$(date)] Starting gunicorn...\" >> $LOG_FILE
  # Use uv run to ensure environment is correct
  # We use uvicorn directly to avoid MPS/Forking issues with gunicorn
  # Since the endpoint is synchronous, uvicorn will run it in a threadpool,
  # handling concurrency effectively without multiple processes.
  uv run uvicorn chichi_speech.server:app \
      --host $HOST --port $PORT --workers 1 --timeout-keep-alive $TIMEOUT >> $LOG_FILE 2>&1
  
  EXIT_CODE=\$?
  echo \"[$(date)] Server exited with code \$EXIT_CODE. Respwaning in 1s...\" >> $LOG_FILE
  sleep 1
done
" > /dev/null 2>&1 &

NEW_PID=$!
echo $NEW_PID > /tmp/chichi_server.pid
echo "Service started in background with PID: $NEW_PID"
echo "To follow logs: tail -f $LOG_FILE"
echo "To stop: ./scripts/stop_server.sh"
