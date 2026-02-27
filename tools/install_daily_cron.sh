#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <inventory_json_path> [HH:MM]"
  exit 1
fi

INVENTORY_PATH=$(realpath "$1")
SCHEDULE_TIME=${2:-"02:00"}
REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
PYTHON_BIN=${PYTHON_BIN:-python3}
LOG_DIR="$REPO_ROOT/backups/logs"
mkdir -p "$LOG_DIR"

HOUR=${SCHEDULE_TIME%:*}
MIN=${SCHEDULE_TIME#*:}

if [[ ! $HOUR =~ ^[0-9]{1,2}$ || ! $MIN =~ ^[0-9]{1,2}$ ]]; then
  echo "Invalid HH:MM value: $SCHEDULE_TIME"
  exit 1
fi

CRON_CMD="cd $REPO_ROOT && $PYTHON_BIN tools/cisco_backup.py --inventory $INVENTORY_PATH >> $LOG_DIR/backup.log 2>&1"
CRON_LINE="$MIN $HOUR * * * $CRON_CMD"

( crontab -l 2>/dev/null | rg -v "tools/cisco_backup.py" || true; echo "$CRON_LINE" ) | crontab -

echo "Installed/updated cron entry: $CRON_LINE"
