# pico-aio

Unofficial all-in-one FIDO2, U2F, OATH, OTP, OpenPGP, and PIV firmware for
RP2350, built from pinned upstream submodules with explicit patches.

The primary target is the RP2350 USB board with a WS2812 LED on GPIO22.

This project is not affiliated with Pol Henarejos, Raspberry Pi Ltd, or
Yubico AB.

## Features

- FIDO2 / CTAP 2.1 / CTAP 1 / U2F
- Resident credentials, credential management, large blobs
- OATH and Yubico OTP applets
- OpenPGP card with on-device key generation
- PIV with YubiKey extension commands
- FIDO management applet with OpenPGP and PIV capability reporting
- EdDSA and libcvc support
- USB HID, CCID, and WebCCID interfaces
- Combined FIDO + OpenPGP file table generated at build time

## Boards

| Board | Description |
|---|---|
| `pico_aio_rp2350_usb` | RP2350 USB board, WS2812 on GPIO22 |
| `pico2` | Generic Raspberry Pi Pico 2 |

RP2040 is not built or tested.

## USB profiles

| Profile | VID:PID | Manufacturer / Product | Purpose |
|---|---|---|---|
| `default` | `FEFF:FCFD` | `Pico AIO` / `Pico AIO` | Public release, dummy USB ID |
| `local` | `2E8A:10FE` | `Pico AIO` / `Pico AIO` | Local CCID testing |
| `yubikey5` | `1050:0407` | `Yubico` / `Yubico YubiKey` | ykman compatibility |

`yubikey5` is a compatibility profile. It is not an official YubiKey and must
not be presented as one. The `default` profile is the safe public artifact.

## Build

No `PICO_SDK_PATH` is required. The Pico SDK is a submodule and CMake points at
it internally.

```bash
git clone https://github.com/jeffpeng3/pico-aio.git
cd pico-aio
tools/bootstrap.sh
tools/apply-patches.sh

cmake --preset rp2350-usb
cmake --build --preset rp2350-usb
```

Or use the wrapper:

```bash
tools/build.sh --board pico_aio_rp2350_usb --profile default
tools/build.sh --board pico_aio_rp2350_usb --profile yubikey5
```

Artifacts are copied to `dist/`.

If you cloned without `--recurse-submodules`, run `tools/bootstrap.sh`. Do not
run a global recursive submodule update for the application submodules; their
nested `pico-keys-sdk` gitlinks are not used by this build.

## CI

GitHub Actions builds all UF2 files in one job with ccache and a shared build
directory per board:

- `rp2350-usb` / `default`
- `rp2350-usb` / `yubikey5`
- `pico2` / `default`
- `pico2` / `yubikey5`

`rp2350-usb` default is the base build. The other configurations reuse ccache
and incremental compilation. Tagged releases attach the UF2 files and
`SHA256SUMS.txt`.

## Namespace

The file store is namespaced so FIDO, OpenPGP/PIV, and future HSM files do not
share the same FID space:

```c
FILE_NS_HSM
FILE_NS_OPENPGP
FILE_NS_FIDO
FILE_NS_SHARED
```

Shared vault files live in `FILE_NS_SHARED`. FIDO and OpenPGP/PIV separate
their vault keys with the SDK vault `app_id`.

## Patches and SDK fork

`pico-keys-sdk` is a fork:

```text
https://github.com/jeffpeng3/pico-keys-sdk
```

The fork `main` branch carries SDK changes, including the namespace
implementation, `file_new()` fix, USB descriptor overrides, custom board
header support, and WS2812 board support. AIO pins a fork commit and does not
apply SDK patches during the build.

FIDO and OpenPGP remain upstream submodules with small patches:

| Repository | Patch | Purpose |
|---|---|---|
| `pico-openpgp` | `0001-piv-rename-cmd-version` | Avoid `cmd_version` symbol collision |
| `pico-openpgp` | `0002-files-combined-table-guard` | Disable standalone file table |
| `pico-openpgp` | `0003-namespace-applets` | Namespace-aware applet registration and vault |
| `pico-fido` | `0001-files-combined-table-guard` | Disable standalone file table |
| `pico-fido` | `0002-namespace-applets` | Namespace-aware applet registration and containers |

The fork tracks upstream issue
[polhenarejos/pico-keys-sdk#39](https://github.com/polhenarejos/pico-keys-sdk/issues/39).
SDK upstream synchronization happens in the fork, not in AIO.

Manifest tolerance and key-load fallback experiments are intentionally not
included. The hardware failure is fixed by correct `file_new()` initialization.

## Debug BOOTSEL reboot

A debug-only build exposes a rescue APDU that reboots directly to BOOTSEL
without pressing the button. It is disabled by default.

```bash
tools/build.sh --board pico_aio_rp2350_usb --profile yubikey5 --debug-bootsel
```

Then:

```bash
tools/reboot-bootsel.sh --attach
```

This sends the rescue AID and `80 1F 02 00`. Do not publish debug UF2 files.

## Testing

Host emulation tests:

```bash
tools/test.sh
```

The suites cover FIDO, OpenPGP, and PIV. Hardware validation steps and current
results are in `docs/validation.md`.

## ykman compatibility

The `yubikey5` profile sets:

- USB VID/PID `1050:0407`
- manufacturer `Yubico`
- product `Yubico YubiKey`

The CCID reader name then contains `Yubico YubiKey`, which ykman uses to
identify the device. The FIDO layer also switches to YubiKey-compatible info
fields when VID is `0x1050`.

Suggested smoke test on hardware:

```bash
tests/hardware/ykman-smoke.sh
```

## License

AGPL-3.0. See `LICENSE` and `THIRD_PARTY.md`.
