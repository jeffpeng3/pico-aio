#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

if [ ! -f "$ROOT/.gitmodules" ]; then
    echo "missing .gitmodules" >&2
    exit 1
fi

git submodule update --init \
    third_party/pico-keys-sdk \
    third_party/pico-fido \
    third_party/pico-openpgp \
    third_party/pico-sdk

# Pico SDK needs its own libraries. Do not recurse into the application
# submodules: pico-fido and pico-openpgp carry their own pico-keys-sdk
# gitlinks, which are not used by this combined build.
git -C "$ROOT/third_party/pico-sdk" submodule update --init --recursive

echo "bootstrap complete"
