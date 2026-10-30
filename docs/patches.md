# Patch series

Patches live in `patches/<submodule>/` and are applied with:

```bash
tools/apply-patches.sh
```

Each repository has a `series` file with the apply order. The script verifies
the submodule HEAD against `versions.lock`, skips patches that are already
applied, and stops if a patch does not apply cleanly.

## Reset

```bash
tools/reset-submodules.sh
```

This runs `git reset --hard HEAD` in each submodule. Fetched dependency trees
inside `pico-keys-sdk/third-party/` are intentionally preserved.

## Updating a submodule

1. Update the submodule commit.
2. Update the matching entry in `versions.lock`.
3. Rebase or regenerate the patches.
4. Run `tools/test.sh`.
5. Build the `pico2` default and `yubikey5` profiles.

## Upstream status

The `file_new()` fix is a candidate upstream change. The issue is tracked in
`docs/upstream.md`.
