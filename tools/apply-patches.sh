#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

source "$ROOT/versions.lock"

check_pin() {
    local path=$1
    local expected=$2
    local actual
    actual=$(git -C "$path" rev-parse HEAD)
    if [ "$actual" != "$expected" ]; then
        echo "submodule pin mismatch: $path" >&2
        echo "  expected: $expected" >&2
        echo "  actual:   $actual" >&2
        echo "run tools/reset-submodules.sh or update versions.lock intentionally" >&2
        exit 1
    fi
}

apply_repo() {
    local repo=$1
    local series=$2
    while IFS= read -r patch; do
        [ -z "$patch" ] && continue
        local file="$ROOT/patches/$series/$patch"
        if [ ! -f "$file" ]; then
            echo "missing patch: $file" >&2
            exit 1
        fi
        if git -C "$repo" apply --reverse --check "$file" >/dev/null 2>&1; then
            echo "already applied: $series/$patch"
            continue
        fi
        git -C "$repo" apply --check "$file"
        git -C "$repo" apply "$file"
        echo "applied: $series/$patch"
    done < "$ROOT/patches/$series/series"
}

check_pin "$ROOT/third_party/pico-keys-sdk" "$PICO_KEYS_SDK_COMMIT"
check_pin "$ROOT/third_party/pico-fido" "$PICO_FIDO_COMMIT"
check_pin "$ROOT/third_party/pico-openpgp" "$PICO_OPENPGP_COMMIT"
check_pin "$ROOT/third_party/pico-sdk" "$PICO_SDK_COMMIT"

apply_repo "$ROOT/third_party/pico-keys-sdk" pico-keys-sdk
apply_repo "$ROOT/third_party/pico-openpgp" pico-openpgp
apply_repo "$ROOT/third_party/pico-fido" pico-fido

echo "all required patches are applied"
