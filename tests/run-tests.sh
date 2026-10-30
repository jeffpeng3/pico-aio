#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
BUILD=${BUILD:-"$ROOT/build/docker"}
BIN="$BUILD/pico_fido2"
FIDO_DIR="$ROOT/third_party/pico-fido"
PGP_DIR="$ROOT/third_party/pico-openpgp"
PIDFILE=/tmp/pico_aio.pid

export PICO_HSM_CI_DEVICE_ID=pico-aio-ci

if [ ! -x "$BIN" ]; then
    echo "missing $BIN; run tests/build-in-docker.sh first" >&2
    exit 1
fi

start_emulator() {
    stop_emulator
    pkill -x pcscd 2>/dev/null || true
    sleep 1
    /usr/sbin/pcscd >/tmp/pcscd.log 2>&1 &
    sleep 1
    rm -f "$ROOT/memory.flash"
    (cd "$ROOT" && "$BIN" >/tmp/pico_aio.log 2>&1 & echo $! >"$PIDFILE")
    sleep 2
}

stop_emulator() {
    if [ -f "$PIDFILE" ]; then
        kill "$(cat "$PIDFILE")" 2>/dev/null || true
        rm -f "$PIDFILE"
    fi
}

trap stop_emulator EXIT

cp -R "$FIDO_DIR/tests/docker/fido2/"* /usr/local/lib/python3.11/dist-packages/fido2/hid/

start_emulator
if ! opensc-tool -an 2>&1 | grep -q "3b:da:18:ff:81:b1:fe:75"; then
    echo "OpenPGP card was not detected in emulation" >&2
    tail -60 /tmp/pico_aio.log >&2 || true
    exit 1
fi

echo "=== FIDO tests ==="
(cd "$FIDO_DIR" && pytest tests/pico-fido -W ignore::DeprecationWarning -q -k "not vault")

start_emulator
echo "=== OpenPGP tests ==="
(cd "$PGP_DIR" && pytest tests/openpgp -W ignore::DeprecationWarning -q \
    -k "not vault" \
    --deselect tests/openpgp/040_extra/test_040_pcsc.py::test_management_applet_config)

start_emulator
echo "=== PIV tests ==="
(cd "$PGP_DIR" && pytest tests/piv -W ignore::DeprecationWarning -q)
