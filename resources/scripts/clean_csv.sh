#!/usr/bin/env bash
set -euo pipefail

INPUT="${1:?input csv required}"
OUTPUT="${2:-clean.csv}"

tr ';' ',' < "$INPUT" | sed 's/[[:space:]]\+$//' > "$OUTPUT"
