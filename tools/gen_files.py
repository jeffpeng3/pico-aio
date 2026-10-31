#!/usr/bin/env python3
"""Generate the merged FIDO + OpenPGP file table for pico-aio."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def read_defines(*paths: Path) -> dict[str, int]:
    defines: dict[str, int] = {}
    for path in paths:
        text = path.read_text()
        for match in re.finditer(
            r"^\s*#define\s+([A-Za-z_]\w*)\s+(0x[0-9A-Fa-f]+|\d+)\b",
            text,
            re.MULTILINE,
        ):
            defines[match.group(1)] = int(match.group(2), 0)
    return defines


def matching_brace(text: str, start: int) -> int:
    depth = 0
    i = start
    state = "code"
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if state == "code":
            if ch == "/" and nxt == "*":
                state = "block"
                i += 2
                continue
            if ch == "/" and nxt == "/":
                state = "line"
                i += 2
                continue
            if ch == '"':
                state = "string"
                i += 1
                continue
            if ch == "'":
                state = "char"
                i += 1
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return i
        elif state == "block":
            if ch == "*" and nxt == "/":
                state = "code"
                i += 2
                continue
        elif state == "line":
            if ch == "\n":
                state = "code"
        elif state in ("string", "char"):
            if ch == "\\":
                i += 2
                continue
            if (state == "string" and ch == '"') or (state == "char" and ch == "'"):
                state = "code"
        i += 1
    raise ValueError("unbalanced braces")


def split_entries(body: str) -> list[str]:
    entries: list[str] = []
    depth = 0
    start = None
    i = 0
    state = "code"
    while i < len(body):
        ch = body[i]
        nxt = body[i + 1] if i + 1 < len(body) else ""
        if state == "code":
            if ch == "/" and nxt == "*":
                state = "block"
                i += 2
                continue
            if ch == "/" and nxt == "/":
                state = "line"
                i += 2
                continue
            if ch == '"':
                state = "string"
                i += 1
                continue
            if ch == "'":
                state = "char"
                i += 1
                continue
            if ch == "{":
                if depth == 0:
                    start = i
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0 and start is not None:
                    entries.append(body[start : i + 1])
                    start = None
        elif state == "block":
            if ch == "*" and nxt == "/":
                state = "code"
                i += 2
                continue
        elif state == "line":
            if ch == "\n":
                state = "code"
        elif state in ("string", "char"):
            if ch == "\\":
                i += 2
                continue
            if (state == "string" and ch == '"') or (state == "char" and ch == "'"):
                state = "code"
        i += 1
    return entries


def table_body(path: Path) -> str:
    text = path.read_text()
    match = re.search(r"file_entry_t\s+file_entries\s*\[\s*\]\s*=\s*", text)
    if not match:
        raise ValueError(f"file_entries not found in {path}")
    open_brace = text.index("{", match.end())
    close_brace = matching_brace(text, open_brace)
    return text[open_brace + 1 : close_brace]


def entry_fid(entry: str, defines: dict[str, int]) -> int | None:
    match = re.search(r"\.fid\s*=\s*([^,}]+)", entry)
    if not match:
        return None
    expr = match.group(1).strip()
    if re.fullmatch(r"0x[0-9A-Fa-f]+|\d+", expr):
        return int(expr, 0)
    if re.fullmatch(r"[A-Za-z_]\w*", expr):
        return defines[expr]
    raise ValueError(f"cannot resolve fid expression: {expr}")


def set_fid(entry: str, value: int) -> str:
    return re.sub(
        r"\.fid\s*=\s*[^,}]+",
        f".fid = 0x{value:04X}",
        entry,
        count=1,
    )


def entry_has_name(entry: str, name: str) -> bool:
    return bool(re.search(rf"\.name\s*=\s*{re.escape(name)}\b", entry))


def entry_parent(entry: str) -> int:
    match = re.search(r"\.parent\s*=\s*(0x[0-9A-Fa-f]+|\d+)", entry)
    return int(match.group(1), 0) if match else 0xFF


def set_ns(entry: str, ns: int) -> str:
    ns_names = {
        0: "FILE_NS_HSM",
        1: "FILE_NS_OPENPGP",
        2: "FILE_NS_FIDO",
        3: "FILE_NS_SHARED",
    }
    return re.sub(
        r"(\.fid\s*=\s*[^,}]+)",
        rf"\1, .ns = {ns_names[ns]}",
        entry,
        count=1,
    )


def set_parent(entry: str, parent: int) -> str:
    return re.sub(
        r"\.parent\s*=\s*[^,}]+",
        f".parent = 0x{parent:02X}",
        entry,
        count=1,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk-dir", type=Path, required=True)
    parser.add_argument("--fido-dir", type=Path, required=True)
    parser.add_argument("--openpgp-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    defines = read_defines(
        args.sdk_dir / "src" / "fs" / "file.h",
        args.fido_dir / "src" / "fido" / "files.h",
        args.openpgp_dir / "src" / "openpgp" / "files.h",
    )

    fido_entries = split_entries(table_body(args.fido_dir / "src" / "fido" / "files.c"))
    pgp_entries = split_entries(
        table_body(args.openpgp_dir / "src" / "openpgp" / "files.c")
    )

    # Shared objects are available from every applet.
    shared_fids = {0xCE03, 0xCE04}

    records: list[dict] = []
    shared: list[dict] = []
    seen_input: set[tuple[int, int]] = set()
    for source, entries, ns in (
        ("fido", fido_entries, 2),
        ("openpgp", pgp_entries, 1),
    ):
        for orig_index, entry in enumerate(entries):
            fid = entry_fid(entry, defines)
            if fid is None:
                continue
            if source == "fido" and fid == 0:
                continue
            if source == "openpgp" and fid == 0 and not entry_has_name(entry, "openpgp_aid"):
                continue
            if fid in shared_fids:
                if not any(item["fid"] == fid for item in shared):
                    shared.append(
                        {
                            "entry": entry,
                            "fid": fid,
                            "source": source,
                            "orig_index": orig_index,
                            "ns": 3,
                            "parent_orig": entry_parent(entry),
                        }
                    )
                continue
            key = (ns, fid)
            if key in seen_input:
                print(f"duplicate source FID skipped: ns={ns} fid=0x{fid:04X}")
                continue
            seen_input.add(key)
            records.append(
                {
                    "entry": entry,
                    "fid": fid,
                    "source": source,
                    "orig_index": orig_index,
                    "ns": ns,
                    "parent_orig": entry_parent(entry),
                }
            )

    shared_mf = {
        "entry": (
            "{ .fid = 0x3F00, .parent = 0xFF, "
            ".name = NULL, .type = FILE_TYPE_DF, .data = NULL, "
            ".ef_structure = 0, .acl = { 0 } }"
        ),
        "fid": 0x3F00,
        "source": "shared",
        "orig_index": None,
        "ns": 3,
        "parent_orig": 0xFF,
    }

    combined = records + [shared_mf] + shared

    index: dict[tuple[str, int], int] = {}
    mf_index: dict[int, int] = {}
    for i, record in enumerate(combined):
        if record["orig_index"] is not None:
            index[(record["source"], record["orig_index"])] = i
        if record["fid"] == 0x3F00 and record["parent_orig"] == 0xFF:
            mf_index[record["ns"]] = i

    seen: dict[tuple[int, int], str] = {}
    for record in combined:
        key = (record["ns"], record["fid"])
        if key in seen:
            raise SystemExit(
                f"duplicate FID after merge: ns={record['ns']} fid=0x{record['fid']:04X}"
            )
        seen[key] = record["source"]

    rendered: list[str] = []
    for record in combined:
        parent = record["parent_orig"]
        if record["fid"] == 0x3F00:
            parent = 0xFF
        elif record["ns"] == 3 and record["source"] != "shared":
            parent = mf_index[3]
        elif parent != 0xFF:
            mapped = index.get((record["source"], parent))
            if mapped is None:
                raise SystemExit(
                    f"missing parent index for {record['source']} "
                    f"fid=0x{record['fid']:04X} parent={parent}"
                )
            parent = mapped
        entry = set_fid(record["entry"], record["fid"])
        entry = set_ns(entry, record["ns"])
        entry = set_parent(entry, parent)
        rendered.append(entry)

    openpgp_index = None
    for index_, record in enumerate(combined):
        if entry_has_name(record["entry"], "openpgp_aid"):
            openpgp_index = index_
            break
    if openpgp_index is None:
        raise SystemExit("OpenPGP FCI entry not found")

    openpgp_mf = mf_index.get(1)
    if openpgp_mf is None:
        raise SystemExit("OpenPGP MF entry not found")

    lines: list[str] = [
        "/* Generated by tools/gen_files.py. Do not edit manually. */",
        '#include "picokeys.h"',
        "",
        "extern uint8_t openpgp_aid[];",
        "extern uint8_t openpgp_aid_full[];",
        "extern uint8_t historical_bytes[];",
        "extern uint8_t exlen_info[];",
        "extern uint8_t extended_capabilities[];",
    ]
    for name in (
        "parse_ch_data",
        "parse_sec_tpl",
        "parse_ch_cert",
        "parse_gfm",
        "parse_fp",
        "parse_cafp",
        "parse_ts",
        "parse_keyinfo",
        "parse_algoinfo",
        "parse_app_data",
        "parse_discrete_do",
        "parse_pw_status",
    ):
        lines.append(f"extern int {name}(const file_t *f, int mode);")
    lines.extend(
        [
            "extern int piv_parse_discovery(const file_t *f);",
            "",
            "file_entry_t file_entries[] = {",
        ]
    )
    for index_, entry in enumerate(rendered):
        lines.append(f"    /* {index_:3d} */ {entry},")
    lines.extend(
        [
            "    { .fid = 0x0000, .ns = FILE_NS_SHARED, .parent = 0xFF, .name = NULL, "
            ".type = FILE_TYPE_NOT_KNOWN, .data = NULL, .ef_structure = 0, .acl = { 0 } }",
            "};",
            "",
            f"const file_t *MF = &file_entries[{openpgp_mf}].file;",
            f"const file_t *file_openpgp = &file_entries[{openpgp_index}].file;",
            "const file_entry_t *file_last = "
            "&file_entries[sizeof(file_entries) / sizeof(file_entry_t) - 1];",
            "",
        ]
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines))
    print(f"wrote {args.output}")
    print(f"entries: {len(combined) + 1}, openpgp entry index: {openpgp_index}")


if __name__ == "__main__":
    main()
