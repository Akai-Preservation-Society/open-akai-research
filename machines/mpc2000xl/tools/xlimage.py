#!/usr/bin/env python3
"""xlimage - check and finish MPC2000XL OS images before flashing.

The MPC2000XL OS update file (MPC2KXL.BIN) is the flat 512 KiB flash image.
At every cold boot the boot block checks a 9-byte magic and a 16-bit word
sum; an image that fails either drops the unit to the disk recovery loader.
This tool applies the same checks, repairs the sum, and compares a modified
image with the stock one for the regions that must not change. The rules are
documented, with their evidence, in ../findings/rom-and-flash.md and
../findings/code-space.md.

Python 3.11 or newer, standard library only.

    python3 xlimage.py check build/MPC2KXL.BIN
    python3 xlimage.py fix-checksum build/modified.bin -o build/MPC2KXL.BIN
    python3 xlimage.py compare stock.bin build/MPC2KXL.BIN

Nothing here contains firmware; every command reads files you supply.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
import sys
from pathlib import Path

IMAGE_SIZE = 0x80000
MAGIC_POINTER = 0xA8          # dword: file offset of the magic text
MAGIC = b"MPC2000XL"
CHECKSUM_OFFSET = 0x77FFE     # word sum of [0, CHECKSUM_OFFSET) is stored here
UPDATE_END = 0x78000          # an OS update programs only [0, 0x78000)

# Regions a mod must leave exactly as in stock (file offsets, end exclusive).
PROTECTED = [
    (0x10036, 0x104B3, "PGR5 gap: code here froze or crashed after a cold boot on hardware"),
    (0x25BDD, 0x25BED, "ALL-file loader header scratch"),
    (0x78000, 0x7C000, "erased by an update and never programmed"),
    (0x7C000, 0x80000, "boot and recovery block: never written by an OS update"),
]
STOCK_SHA256 = "100e3375b45072c209ffa2b1dbaecbf740c8c4ea29162827ac11cc6bf9cc7bab"


def word_sum(image: bytes) -> int:
    return sum(struct.unpack_from(f"<{CHECKSUM_OFFSET // 2}H", image)) & 0xFFFF


def stored_sum(image: bytes) -> int:
    return struct.unpack_from("<H", image, CHECKSUM_OFFSET)[0]


def problems(image: bytes) -> list[str]:
    """What the boot block's integrity check would reject, plus size."""
    out = []
    if len(image) != IMAGE_SIZE:
        return [f"size is {len(image)} bytes; the image must be exactly {IMAGE_SIZE}"]
    pointer = struct.unpack_from("<I", image, MAGIC_POINTER)[0]
    if pointer + len(MAGIC) > IMAGE_SIZE or image[pointer:pointer + len(MAGIC)] != MAGIC:
        out.append(f"magic: dword at 0xA8 is {pointer:#x} and does not point at 'MPC2000XL' "
                   "(the unit would boot to the recovery loader)")
    if word_sum(image) != stored_sum(image):
        out.append(f"checksum: word sum is {word_sum(image):04X}h but {stored_sum(image):04X}h is stored "
                   f"at {CHECKSUM_OFFSET:#x} (the unit would boot to the recovery loader)")
    return out


def fix_checksum(image: bytes) -> bytes:
    if len(image) != IMAGE_SIZE:
        raise SystemExit(f"size is {len(image)} bytes; expected {IMAGE_SIZE}")
    out = bytearray(image)
    struct.pack_into("<H", out, CHECKSUM_OFFSET, word_sum(image))
    return bytes(out)


def changed_ranges(a: bytes, b: bytes) -> list[tuple[int, int]]:
    ranges, start = [], None
    for index in range(len(a) + 1):
        differs = index < len(a) and a[index] != b[index]
        if differs and start is None:
            start = index
        elif not differs and start is not None:
            ranges.append((start, index))
            start = None
    return ranges


def compare(stock: bytes, modified: bytes) -> tuple[list[str], list[str]]:
    errors, notes = [], []
    if len(stock) != IMAGE_SIZE or len(modified) != IMAGE_SIZE:
        return ["both files must be 524,288 bytes"], notes
    if hashlib.sha256(stock).hexdigest() != STOCK_SHA256:
        notes.append("the first file is not stock OS 1.20 (sha256 differs); comparing anyway")
    ranges = changed_ranges(stock, modified)
    for start, end, why in PROTECTED:
        hits = [(a, b) for a, b in ranges if a < end and b > start]
        if hits:
            errors.append(f"{start:#07x}-{end:#07x} changed ({why}): "
                          + ", ".join(f"{a:#07x}-{b:#07x}" for a, b in hits))
    body = [(a, b) for a, b in ranges if not (a <= CHECKSUM_OFFSET and b >= CHECKSUM_OFFSET + 2 and b - a == 2)]
    notes.append(f"{len(ranges)} changed range(s), {sum(b - a for a, b in ranges)} byte(s)")
    for a, b in body[:40]:
        notes.append(f"  {a:#07x}-{b:#07x} ({b - a} bytes)")
    if len(body) > 40:
        notes.append(f"  ... {len(body) - 40} more")
    errors += problems(modified)
    return errors, notes


def cmd_check(args: argparse.Namespace) -> int:
    image = Path(args.image).read_bytes()
    found = problems(image)
    print(f"{args.image}: sha256 {hashlib.sha256(image).hexdigest()}")
    if hashlib.sha256(image).hexdigest() == STOCK_SHA256:
        print("note  this is stock OS 1.20")
    for item in found:
        print("ERROR", item)
    if not found:
        print(f"ok    magic present, checksum {stored_sum(image):04X}h valid")
    return 1 if found else 0


def cmd_fix(args: argparse.Namespace) -> int:
    source = Path(args.image).resolve()
    target = Path(args.output).resolve()
    if source == target:
        raise SystemExit("write to a new file; never overwrite the input")
    out = fix_checksum(Path(args.image).read_bytes())
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(out)
    print(f"wrote {args.output}: checksum {stored_sum(out):04X}h  sha256 {hashlib.sha256(out).hexdigest()}")
    for item in problems(out):
        print("ERROR", item)
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    errors, notes = compare(Path(args.stock).read_bytes(), Path(args.modified).read_bytes())
    for note in notes:
        print("note ", note)
    for error in errors:
        print("ERROR", error)
    if not errors:
        print("ok    protected regions untouched; image passes the boot checks")
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="xlimage", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("check", help="run the boot block's magic and checksum tests")
    p.add_argument("image")
    p.set_defaults(func=cmd_check)
    p = sub.add_parser("fix-checksum", help="write a copy with the checksum word repaired")
    p.add_argument("image")
    p.add_argument("-o", "--output", required=True)
    p.set_defaults(func=cmd_fix)
    p = sub.add_parser("compare", help="list changes and refuse changes to protected regions")
    p.add_argument("stock")
    p.add_argument("modified")
    p.set_defaults(func=cmd_compare)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
