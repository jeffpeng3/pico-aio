# Third-party components

pico-aio is an unofficial combined firmware. It is not affiliated with
Pol Henarejos, Raspberry Pi Ltd, or Yubico AB.

| Component | Source | License |
|---|---|---|
| Pico Keys SDK | https://github.com/polhenarejos/pico-keys-sdk | AGPL-3.0 |
| Pico FIDO | https://github.com/polhenarejos/pico-fido | AGPL-3.0 |
| Pico OpenPGP | https://github.com/polhenarejos/pico-openpgp | AGPL-3.0 |
| Raspberry Pi Pico SDK | https://github.com/raspberrypi/pico-sdk | BSD-3-Clause |

The Pico Keys SDK build fetches its own third-party dependencies:
Mbed TLS, TinyCBOR, and libcvc. See the SDK repository and its
`third-party/` trees for their licenses.
