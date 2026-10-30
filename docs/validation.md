# Validation

## Emulation

Validated on 2026-10-31:

- FIDO: 282 passed, 2 skipped
- OpenPGP: 1095 passed, 8 skipped
- PIV: 279 passed, 1 skipped
- Combined table: 161 entries, OpenPGP FCI at index 159
- `yubikey5` builds contain `Yubico` / `Yubico YubiKey`
- `yubikey5` UF2 device descriptor contains `50 10 07 04` (`1050:0407`)
- `default` UF2 device descriptor contains `ff fe fd fc` (`FEFF:FCFD`)
- `pico_aio_rp2350_usb` preprocessor output contains
  `PICO_DEFAULT_WS2812_PIN 22` and `PICO_AIO_FORCE_WS2812 1`
- Switching `default` to `yubikey5` in the same board build directory
  recompiles only `usb_descriptors.c` and relinks

Artifact sizes:

| Board | Profile | text | bss |
|---|---|---:|---:|
| pico2 | default | 566848 | 89652 |
| pico2 | yubikey5 | 566864 | 89652 |
| rp2350-usb | default | 566448 | 89652 |
| rp2350-usb | yubikey5 | 566464 | 89652 |

## Hardware

Earlier RP2350 validation of the minimal `file_new()` fix passed:

- OpenPGP key generation
- Signature before power cycle
- Power cycle
- Signature after power cycle
- Signature verification
- Encrypt/decrypt round trip

The generic `pico-aio-pico2-yubikey5` UF2 was flashed on 2026-10-31.

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

The `pico-aio-rp2350-usb-yubikey5` UF2 was flashed on 2026-10-31.

WS2812 on GPIO22 was verified with RGB order:

- Not mounted: red blink
- Mounted: green blink
- CCID `SCARD_UNPOWER_CARD`: blue blink
- RGB order was required; the initial GRB setting turned the mounted green
  state into red

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
[41128275389](https://github.com/jeffpeng3/pico-aio/actions/runs/41128275389)
completed successfully in 2m25s.

The single `build-uf2` job builds four UF2 files:

- `pico-aio-rp2350-usb-default`
- `pico-aio-rp2350-usb-yubikey5`
- `pico-aio-pico2-default`
- `pico-aio-pico2-yubikey5`

The `rp2350-usb` default build is the base. The other configurations reuse
ccache and incremental compilation. Switching profile in the same board build
directory recompiles only `usb_descriptors.c`.

The run uploaded one `pico-aio-uf2` artifact containing 12 files (UF2, ELF, and
BIN for four configurations). Node 20 deprecation warnings are gone after
moving to `actions/checkout@v7`, `actions/upload-artifact@v7`, and
`actions/download-artifact@v8`.
