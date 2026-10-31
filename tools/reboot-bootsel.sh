#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
ATTACH=0
if [ "${1:-}" = "--attach" ]; then
    ATTACH=1
fi

# Select the rescue applet and request the debug-only BOOTSEL reset.
timeout 15 opensc-tool \
    -s "00 A4 04 00 08 A0 58 3F C1 9B 7E 4F 21" \
    -s "80 1F 02 00" || true

sleep 3
if [ "$ATTACH" = "1" ]; then
    "$ROOT/tools/attach-bootsel.sh"
fi
