#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

for repo in \
    third_party/pico-keys-sdk \
    third_party/pico-fido \
    third_party/pico-openpgp \
    third_party/pico-sdk; do
    echo "reset: $repo"
    git -C "$repo" reset --hard HEAD
done

echo "submodules reset; fetched third-party dependency trees are preserved"
