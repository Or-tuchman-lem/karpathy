#!/bin/bash
# Monitor Karpathy logs in real-time
# Usage: ./monitor_logs.sh

echo "🔍 Monitoring Karpathy logs..."
echo "Press Ctrl+C to stop"
echo ""

# Find the most recent terminal log file
TERMINAL_FILE=$(ls -t ~/.cursor/projects/Users-or-tuchman-src-karpathy/terminals/*.txt 2>/dev/null | head -1)

if [ -z "$TERMINAL_FILE" ]; then
    echo "❌ No terminal log file found"
    exit 1
fi

echo "📁 Watching: $TERMINAL_FILE"
echo ""

# Follow the log file with color highlighting
tail -f "$TERMINAL_FILE" | grep --line-buffered -E "KARPATHY|LiteLLM|ERROR|delegate|skill|tool|Using|Task|Expert" --color=always
