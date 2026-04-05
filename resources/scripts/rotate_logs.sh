#!/usr/bin/env bash
set -euo pipefail

LOG_PATH="${1:-/var/log/myapp}"
RETENTION_DAYS="${2:-14}"

find "$LOG_PATH" -type f -name '*.log' -mtime +"$RETENTION_DAYS" -delete
