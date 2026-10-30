#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
IMAGE=${IMAGE:-pico-aio-run:bookworm}

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    (cd "$ROOT/third_party/pico-openpgp" && docker build -t pico-aio-test:bookworm -f tests/docker/bookworm/Dockerfile .)
    (cd "$ROOT/tests" && docker build -t "$IMAGE" .)
fi

docker run --rm --privileged \
    --volume "$ROOT:$ROOT" \
    --workdir "$ROOT" \
    "$IMAGE" \
    "$ROOT/tests/run-tests.sh"
