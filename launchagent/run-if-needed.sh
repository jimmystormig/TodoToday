#!/bin/bash
set -euo pipefail

# Only run the briefing once per day, and only after 7:00 AM.
# Designed to be called frequently (e.g. every 15 min) so that
# missed schedules due to sleep/wake are caught automatically.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
STAMP_FILE="$PROJECT_DIR/logs/.last-run-date"

TODAY="$(date +%Y-%m-%d)"
HOUR="$(date +%H)"

# Don't run before 7 AM
if [ "$HOUR" -lt 7 ]; then
    exit 0
fi

# Check if already ran today
if [ -f "$STAMP_FILE" ] && [ "$(cat "$STAMP_FILE")" = "$TODAY" ]; then
    exit 0
fi

# Record that we're running today (write early to prevent double runs)
mkdir -p "$(dirname "$STAMP_FILE")"
echo "$TODAY" > "$STAMP_FILE"

# Run the actual briefing (uv is on PATH via the LaunchAgent environment)
exec uv run --project "$PROJECT_DIR" todotoday
