# Patches

Each directory targets one pinned upstream submodule. Apply from the repository
root:

```bash
tools/apply-patches.sh
```

`series` files define the order. Patches are relative to the submodule root and
must be applied from that directory, which the script handles.

`pico-keys-sdk` is now a fork and is pinned as a submodule commit. SDK changes
are fork commits, not AIO patches. FIDO and OpenPGP still use small namespace
and integration patches.

See `docs/upstream.md` for SDK fork tracking.
