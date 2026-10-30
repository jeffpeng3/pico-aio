#!/bin/bash
set -euo pipefail

REPO=polhenarejos/pico-keys-sdk
ISSUE=39

if command -v gh >/dev/null 2>&1; then
    state=$(gh issue view "$ISSUE" --repo "$REPO" --json state --jq .state)
else
    state=$(curl -fsSL "https://api.github.com/repos/$REPO/issues/$ISSUE" \
        | python3 -c 'import json,sys; print(json.load(sys.stdin)["state"])')
fi

echo "$REPO#$ISSUE: $state"
if [ "$state" != "OPEN" ]; then
    echo "upstream issue is no longer open; remove patch 0001 and bump pico-keys-sdk" >&2
    exit 1
fi
