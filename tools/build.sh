#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
BOARD=${BOARD:-pico2}
PROFILE=${PROFILE:-default}
BUILD_DIR=${BUILD_DIR:-"$ROOT/build/$BOARD-$PROFILE"}
CLEAN=0

while [ "$#" -gt 0 ]; do
    case "$1" in
        --board) BOARD=$2; shift 2 ;;
        --profile) PROFILE=$2; shift 2 ;;
        --build-dir) BUILD_DIR=$2; shift 2 ;;
        --clean) CLEAN=1; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

cd "$ROOT"
"$ROOT/tools/apply-patches.sh"

if [ "$CLEAN" = "1" ]; then
    rm -rf "$BUILD_DIR"
fi

cmake -S "$ROOT" -B "$BUILD_DIR" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DPICO_BOARD="$BOARD" \
    -DPICO_AIO_USB_PROFILE="$PROFILE"

cmake --build "$BUILD_DIR" --parallel "$(nproc)"

mkdir -p "$ROOT/dist"
for ext in uf2 elf bin; do
    src="$BUILD_DIR/pico_fido2.$ext"
    if [ -f "$src" ]; then
        dst="$ROOT/dist/pico-aio-$BOARD-$PROFILE.$ext"
        cp "$src" "$dst"
        echo "artifact: $dst"
    fi
done
