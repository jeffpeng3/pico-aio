# Testing

## Host emulation

```bash
tools/test.sh
```

This builds a Docker image, compiles the emulation binary, and runs the upstream
FIDO, OpenPGP, and PIV test suites.

Expected baseline:

| Suite | Result |
|---|---|
| FIDO | 282 passed, 2 skipped |
| OpenPGP | 1095 passed, 8 skipped |
| PIV | 279 passed, 1 skipped |

Vault tests are excluded because they require external enrollment secrets.

## Persistence diagnostic

`tests/repro_persistence.py` generates OpenPGP keys in emulation, restarts the
emulator while preserving `memory.flash`, and attempts a signature.

The emulator uses a stable CI serial when built with `ENABLE_EMULATION=ON`
(`__FOR_CI` plus `PICO_HSM_CI_DEVICE_ID`). Even with a stable serial, gpg card
reinsertion after an emulator restart is not a reliable oracle. Hardware is the
authoritative persistence test.

## Hardware

See `docs/validation.md`.
