#!/bin/bash
set -euo pipefail

if lsusb 2>/dev/null | grep -q '2e8a:000f'; then
    echo "RP2350 BOOTSEL is already attached to WSL"
    exit 0
fi

BUSID=$(powershell.exe -NoProfile -Command "usbipd list" 2>/dev/null \
    | tr -d '\r' \
    | awk '/2e8a:000f/ { print $1; exit }')

if [ -z "$BUSID" ]; then
    echo "RP2350 BOOTSEL device not found in usbipd list" >&2
    exit 1
fi

powershell.exe -NoProfile -Command "usbipd attach --wsl --busid $BUSID"
