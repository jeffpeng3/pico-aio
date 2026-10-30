# Upstream tracking

## pico-keys-sdk issue 39

- Repository: `polhenarejos/pico-keys-sdk`
- Issue: https://github.com/polhenarejos/pico-keys-sdk/issues/39
- Patch: `patches/pico-keys-sdk/0001-fs-initialize-dynamic-file-entries.patch`
- Status: open
- Pinned SDK: `a2f0a51588fb523f2d6614e008b4bdbb45e443f1`

The patch changes `file_new()` back to full `file_t` initialization:

```diff
-    f->data = NULL;
+    memset(f, 0, sizeof(*f));
     f->fid = fid;
```

## Removal procedure

When upstream fixes the issue:

1. Bump `third_party/pico-keys-sdk` to the fixed commit.
2. Update `versions.lock`.
3. Delete `patches/pico-keys-sdk/0001-fs-initialize-dynamic-file-entries.patch`.
4. Remove its line from `patches/pico-keys-sdk/series`.
5. Remove its check from `cmake/check_patches.cmake`.
6. Run `tools/test.sh` and rebuild the UF2 profiles.

`tools/check-upstream.sh` reports the current issue state. The weekly GitHub
Actions workflow runs the same check.
