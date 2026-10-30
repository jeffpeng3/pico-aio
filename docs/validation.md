# Validation

## Emulation

Validated on 2026-10-31:

- FIDO: 282 passed, 2 skipped
- OpenPGP: 1095 passed, 8 skipped
- PIV: 279 passed, 1 skipped
- Combined table: 161 entries, OpenPGP FCI at index 159
- `yubikey5` ELF contains `Yubico` / `Yubico YubiKey`
- `yubikey5` UF2 device descriptor contains `50 10 07 04` (`1050:0407`)
- `default` UF2 device descriptor contains `ff fe fd fc` (`FEFF:FCFD`)

Artifact sizes:

| Profile | text | bss |
|---|---:|---:|
| default | 566848 | 89652 |
| yubikey5 | 566864 | 89652 |

## Hardware

Earlier RP2350 validation of the minimal `file_new()` fix passed:

- OpenPGP key generation
- Signature before power cycle
- Power cycle
- Signature after power cycle
- Signature verification
- Encrypt/decrypt round trip

The new `pico-aio` UF2 still needs a hardware flash and ykman smoke test. The
current test board was not reachable in BOOTSEL mode from the build host.

Hardware smoke test:

```bash
tests/hardware/ykman-smoke.sh
```

Expected checks:

- `ykman info` sees a YubiKey 4 compatible device
- `ykman piv info` reads PIV metadata
- `ykman oath info` reads OATH state
- `ykman config usb` reads the management applet
- `gpg --card-status` sees the OpenPGP applet
