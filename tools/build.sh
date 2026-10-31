#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
BOARD=${BOARD:-pico_aio_rp2350_usb}
PROFILE=${PROFILE:-default}
CLEAN=0
DEBUG_BOOTSEL=0

while [ "$#" -gt 0 ]; do
    case "$1" in
        --board) BOARD=$2; shift 2 ;;
        --profile) PROFILE=$2; shift 2 ;;
        --build-dir) BUILD_DIR=$2; shift 2 ;;
        --clean) CLEAN=1; shift ;;
        --debug-bootsel) DEBUG_BOOTSEL=1; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

cd "$ROOT"

case "$BOARD" in
    pico_aio_rp2350_usb) BOARD_LABEL=rp2350-usb ;;
    *) BOARD_LABEL=$BOARD ;;
esac

BUILD_DIR=${BUILD_DIR:-"$ROOT/build/$BOARD_LABEL"}

"$ROOT/tools/apply-patches.sh"

if [ "$CLEAN" = "1" ]; then
    rm -rf "$BUILD_DIR"
fi

CMAKE_EXTRA_ARGS=()
if [ "$DEBUG_BOOTSEL" = "1" ]; then
    CMAKE_EXTRA_ARGS+=(-DPICO_AIO_DEBUG_BOOTSEL=ON)
fi

CMAKE_LAUNCHER_ARGS=()
if [ "${USE_CCACHE:-1}" != "0" ] && command -v ccache >/dev/null 2>&1; then
    CMAKE_LAUNCHER_ARGS+=(
        -DCMAKE_C_COMPILER_LAUNCHER=ccache
        -DCMAKE_CXX_COMPILER_LAUNCHER=ccache
    )
fi

cmake -S "$ROOT" -B "$BUILD_DIR" -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DPICO_BOARD="$BOARD" \
    -DPICO_AIO_USB_PROFILE="$PROFILE" \
    "${CMAKE_EXTRA_ARGS[@]}" \
    "${CMAKE_LAUNCHER_ARGS[@]}"

cmake --build "$BUILD_DIR" --parallel "$(nproc)"

mkdir -p "$ROOT/dist"
for ext in uf2 elf bin; do
    src="$BUILD_DIR/pico_fido2.$ext"
    if [ -f "$src" ]; then
        suffix=""
    if [ "$DEBUG_BOOTSEL" = "1" ]; then
        suffix="-debug"
    fi
    dst="$ROOT/dist/pico-aio-$BOARD_LABEL-$PROFILE$suffix.$ext"
        cp "$src" "$dst"
        echo "artifact: $dst"
    fi
done
