#!/bin/bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

"$ROOT/tools/apply-patches.sh"
"$ROOT/tests/build-in-docker.sh"
"$ROOT/tests/run-in-docker.sh"
