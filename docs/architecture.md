# Architecture

pico-aio links three upstream source trees into one firmware:

```text
pico-keys-sdk  shared filesystem, USB, crypto, containers, management
pico-fido      FIDO2/U2F/OATH/OTP applets and management applet
pico-openpgp   OpenPGP and PIV applets
pico-sdk       Raspberry Pi Pico SDK
```

The build uses one shared `pico-keys-sdk` checkout. The `pico-keys-sdk` gitlinks
inside the `pico-fido` and `pico-openpgp` submodules are not initialized or used.

## Combined file table

Both application repositories define a standalone `file_entries[]` table. For
the combined firmware:

1. `pico-fido/src/fido/files.c` and `pico-openpgp/src/openpgp/files.c` guard
   their tables with `PICO_FIDO2_COMBINED_FILES`.
2. `tools/gen_files.py` parses both tables and emits one merged table.
3. The merged table keeps FIDO entries, removes duplicate MF/end markers,
   and drops the OpenPGP vault-key duplicate at FID 0xCE03.
4. CMake places the generated file in the build directory and compiles it into
   `pico_fido2`.

The generator resolves `file_openpgp` by the `openpgp_aid` name instead of
hardcoding an index. Current output is 161 entries with the OpenPGP FCI at
index 159.

## Applet selection

`pico-keys-sdk/src/main.c` is patched to select the longest matching AID prefix
and to use exact matching for `app_exists()`. This keeps OpenPGP, PIV, FIDO, and
the management applet from resolving to the wrong applet when AIDs share a
prefix.

## PIV symbol collision

Both FIDO and PIV define `cmd_version()`. The PIV implementation is renamed to
`cmd_piv_version()` in the downstream patch so the two applets can link into one
binary.
