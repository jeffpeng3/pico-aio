# Upstream tracking

## SDK fork

- Fork: https://github.com/jeffpeng3/pico-keys-sdk
- Branch: `main`
- Main repo pins the fork commit in `versions.lock`

The fork owns upstream synchronization:

```bash
git -C third_party/pico-keys-sdk fetch upstream
git -C third_party/pico-keys-sdk rebase upstream/main
```

AIO does not fetch, rebase, or check the SDK upstream.

## Issue 39

- Issue: https://github.com/polhenarejos/pico-keys-sdk/issues/39
- Fork commit: `fs: initialize dynamic file entries`
- Status: fixed downstream, pending upstream

When upstream includes the fix, drop or rebase the corresponding fork commit
and update the pinned submodule commit. The AIO build does not have an SDK
patch to remove.

## Namespace downstream commits

The fork `main` branch contains these downstream commits:

```text
fs: initialize dynamic file entries
main: match longest AID prefix
usb: make VID/PID and strings source-local
cmake: support custom board headers and subdirectory layout
led: force board WS2812
fs: add namespace to file store and flash records
fs: namespace object containers and shared vault
main: assign namespace on applet selection
```

These are downstream-only and are not expected to be upstreamed as a group.
