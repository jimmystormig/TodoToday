#!/bin/bash
set -euo pipefail

PLIST_NAME="com.todotoday.briefing.plist"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE="$SCRIPT_DIR/$PLIST_NAME"
DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

# Locate uv
UV_PATH="$(command -v uv 2>/dev/null || echo "")"
if [ -z "$UV_PATH" ]; then
    echo "Error: uv not found in PATH. Install it first: https://docs.astral.sh/uv/"
    exit 1
fi
UV_BIN_DIR="$(dirname "$UV_PATH")"

# Unload if already loaded
if launchctl list 2>/dev/null | grep -q com.todotoday.briefing; then
    echo "Unloading existing agent..."
    launchctl unload "$DEST" 2>/dev/null || true
fi

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Fill in template and install
echo "Installing plist to $DEST"
sed \
    -e "s|__UV_PATH__|${UV_PATH}|g" \
    -e "s|__UV_BIN_DIR__|${UV_BIN_DIR}|g" \
    -e "s|__PROJECT_DIR__|${PROJECT_DIR}|g" \
    -e "s|__HOME__|${HOME}|g" \
    "$TEMPLATE" > "$DEST"

echo "Loading agent..."
launchctl load "$DEST"

echo "Done. The briefing will run daily at 7:00 AM (checks every 15 min after wake)."
echo "To test now: launchctl start com.todotoday.briefing"
