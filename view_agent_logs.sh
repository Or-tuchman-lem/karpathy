#!/bin/bash
# View detailed agent command logs
# Usage: ./view_agent_logs.sh [follow]

echo "📋 Karpathy Agent Command Logs"
echo "=============================="
echo ""

LOG_DIR="sandbox/logs"

if [ ! -d "$LOG_DIR" ]; then
    echo "❌ No logs directory found at $LOG_DIR"
    exit 1
fi

# Get the most recent log file
LATEST_LOG=$(ls -t "$LOG_DIR"/karpathy_*.log 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "❌ No log files found in $LOG_DIR"
    exit 1
fi

echo "📁 Reading: $LATEST_LOG"
echo ""

if [ "$1" = "follow" ] || [ "$1" = "-f" ]; then
    echo "🔄 Following log (Ctrl+C to stop)..."
    echo "======================================"
    echo ""
    tail -f "$LATEST_LOG"
else
    echo "📖 Showing full log:"
    echo "======================================"
    echo ""
    cat "$LATEST_LOG"
    echo ""
    echo "======================================"
    echo "💡 Tip: Run with 'follow' to watch in real-time:"
    echo "   ./view_agent_logs.sh follow"
fi
