#!/bin/bash
# Stop script for Chichi Speech Service

echo "Killing service on port 9090..."
lsof -ti :9090 | xargs kill -9 2>/dev/null || true

# Kill the background loop if PID file exists
if [ -f /tmp/chichi_server.pid ]; then
    PID=$(cat /tmp/chichi_server.pid)
    echo "Killing background loop (PID: $PID)..."
    kill -9 $PID 2>/dev/null || true
    rm /tmp/chichi_server.pid
fi

echo "Stopped."
