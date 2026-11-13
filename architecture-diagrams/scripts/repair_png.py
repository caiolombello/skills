#!/usr/bin/env python3
# Adapted from Agents365-ai/drawio-skill@2ee141e (MIT).
# See ../references/licenses/Agents365-drawio-skill-MIT.txt.
"""Repair truncated IEND chunk in draw.io -e PNG exports (issue #8).

draw.io's CLI emits -e PNGs with the 4-byte IEND length field but missing
the 8 bytes of "IEND" type + CRC. Strict PNG decoders and vision APIs
(Anthropic included) reject the file with 400 "Could not process image".
SVG/PDF are unaffected.

The default writes a sibling `*.repaired.png`; use `--in-place` only after
keeping a recoverable copy. The input is changed only when it has a valid PNG
signature and chunk stream followed by the exact four-byte truncated IEND
length marker described above.

Usage: python3 repair_png.py <diagram.drawio.png> [-o repaired.png]
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import zlib

SIGNATURE = b"\x89PNG\r\n\x1a\n"
IEND = b"\x00\x00\x00\x00IEND\xaeB`\x82"


def inspect_png(data: bytes) -> str:
    """Return `valid` or `truncated-iend`; reject every other corruption."""
    if not data.startswith(SIGNATURE):
        raise ValueError("input does not have a PNG signature")
    offset = len(SIGNATURE)
    while offset < len(data):
        remaining = len(data) - offset
        if remaining == 4 and data[offset:] == b"\x00\x00\x00\x00":
            return "truncated-iend"
        if remaining < 12:
            raise ValueError("PNG has a truncated chunk header or payload")
        length = int.from_bytes(data[offset:offset + 4], "big")
        chunk_type = data[offset + 4:offset + 8]
        end = offset + 12 + length
        if end > len(data):
            raise ValueError(f"PNG chunk {chunk_type!r} is truncated")
        payload = data[offset + 8:offset + 8 + length]
        expected_crc = int.from_bytes(data[offset + 8 + length:end], "big")
        actual_crc = zlib.crc32(chunk_type + payload) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise ValueError(f"PNG chunk {chunk_type!r} has an invalid CRC")
        if chunk_type == b"IEND":
            if length != 0:
                raise ValueError("PNG IEND chunk must have zero length")
            return "valid"
        offset = end
    raise ValueError("PNG has no IEND chunk or truncated IEND marker")


def repaired_bytes(data: bytes) -> bytes | None:
    state = inspect_png(data)
    if state == "valid":
        return None
    return data + IEND[4:]


def default_output(path: Path) -> Path:
    return path.with_name(f"{path.stem}.repaired{path.suffix}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safely repair a truncated PNG IEND chunk.")
    parser.add_argument("input", help="possibly truncated Draw.io PNG")
    parser.add_argument("-o", "--output", help="repaired output path")
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="replace the input explicitly instead of writing *.repaired.png",
    )
    parser.add_argument("--force", action="store_true", help="overwrite an existing output")
    args = parser.parse_args()
    if args.output and args.in_place:
        parser.error("--output and --in-place are mutually exclusive")
    source = Path(args.input)
    target = source if args.in_place else Path(args.output) if args.output else default_output(source)
    if not args.in_place:
        same_path = target.resolve() == source.resolve()
        same_file = source.exists() and target.exists() and target.samefile(source)
        if same_path or same_file:
            parser.error(
                "--output must differ from the input; use --in-place for an explicit replacement"
            )
    try:
        data = source.read_bytes()
        fixed = repaired_bytes(data)
        if fixed is None:
            print(f"no repair needed: {source}")
            raise SystemExit(0)
        if target.exists() and not args.force and not args.in_place:
            raise FileExistsError(f"{target} exists; pass --force to overwrite it")
        target.write_bytes(fixed)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print(f"repaired {source} -> {target}")
