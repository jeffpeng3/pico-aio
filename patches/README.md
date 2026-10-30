# Patches

Each directory targets one pinned submodule. Apply from the repository root:

```bash
tools/apply-patches.sh
```

`series` files define the order. Patches are relative to the submodule root and
must be applied from that directory, which the script handles.

The upstream-tracking patch is:

- `pico-keys-sdk/0001-fs-initialize-dynamic-file-entries.patch`

Remove it after `polhenarejos/pico-keys-sdk#39` is fixed upstream. See
`docs/upstream.md`.
