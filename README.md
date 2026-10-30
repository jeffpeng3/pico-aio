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

## Patches

Patches are kept in `patches/` and applied to submodules, not committed inside
the submodules.

| Repository | Patch | Purpose |
|---|---|---|
| `pico-keys-sdk` | `0001-fs-initialize-dynamic-file-entries` | Fix `file_new()` stale state |
| `pico-keys-sdk` | `0002-main-longest-aid-match` | Correct multi-applet AID selection |
| `pico-keys-sdk` | `0003-usb-descriptor-overrides` | Allow manufacturer/product strings |
| `pico-keys-sdk` | `0004-import-relative-paths` | Support SDK in a subdirectory |
| `pico-keys-sdk` | `0005-led-force-board-ws2812` | Force WS2812 GPIO22 on the dedicated board |
| `pico-keys-sdk` | `0006-usb-config-header` | Keep USB profile defines out of global flags |
| `pico-keys-sdk` | `0007-usb-config-include` | Include the generated USB config header |
| `pico-keys-sdk` | `0008-board-header-path` | Read custom board headers from PICO_BOARD_HEADER_FILE |
| `pico-openpgp` | `0001-piv-rename-cmd-version` | Avoid `cmd_version` symbol collision |
| `pico-openpgp` | `0002-files-combined-table-guard` | Disable standalone file table |
| `pico-fido` | `0001-files-combined-table-guard` | Disable standalone file table |

The `file_new()` patch tracks upstream issue
[polhenarejos/pico-keys-sdk#39](https://github.com/polhenarejos/pico-keys-sdk/issues/39).
When upstream includes the fix, remove the patch and bump the submodule.

Manifest tolerance and key-load fallback experiments are intentionally not
included. The hardware failure is fixed by correct `file_new()` initialization.

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
