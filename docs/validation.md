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

The `pico-aio-pico2-yubikey5` UF2 was flashed on 2026-10-31.

`ykman info` reports:

```text
Device type: YubiKey 5A
Firmware version: 8.2.0
Enabled USB interfaces: OTP, FIDO, CCID

Yubico OTP   Enabled
FIDO U2F     Enabled
FIDO2        Enabled
OATH         Enabled
PIV          Enabled
OpenPGP      Enabled
```

`ykman piv info` reads PIV 5.7.0 metadata. `ykman oath info` reads OATH 8.2.0.
`ykman config usb --list` reports OTP, U2F, FIDO2, OATH, PIV, and OpenPGP.

The OpenPGP applet was validated with the existing Var1 User key:

- `gpg --card-status` shows OpenPGP card v3.4 and all three keys
- `gpg --detach-sign` succeeds
- `gpg --verify` reports `Good signature`
- encrypt/decrypt round trip returns MATCH

After flashing, kill stale gpg agents once:

```bash
gpgconf --kill all
pkill -x scdaemon
```

Without that, gpg can loop on a stale `CONFIRM 1` inquiry from the old reader.

Hardware smoke test:

```bash
tests/hardware/ykman-smoke.sh
```

## CI

GitHub Actions run
[41116851659](https://github.com/jeffpeng3/pico-aio/actions/runs/41116851659)
completed successfully.

Artifacts:

- `pico-aio-pico2-default`
- `pico-aio-pico2-yubikey5`
- `pico-aio-pico-default`
- `pico-aio-pico-yubikey5`

The downloaded `pico2-yubikey5` UF2 contains USB descriptor bytes
`50 10 07 04`, and the downloaded `pico` default UF2 contains
`ff fe fd fc`.
