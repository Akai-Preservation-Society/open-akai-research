#!/usr/bin/env python3
"""sysdisk - build floppy-loadable programs for the Akai MPC3000.

The MPC3000 ROM loads the first `*.SYS` file on a floppy at power-on as a
DOS MZ executable and jumps to it. This tool wraps code in the header that
loader accepts, checks a file against the loader's rules, and packs a
1.44 MB FAT12 disk image. The rules it enforces are documented, with their
evidence, in ../findings/floppy-sys-loader.md and
../findings/build-a-floppy-sys.md.

Python 3.11 or newer, standard library only.

    python3 sysdisk.py hello --text "HELLO FROM RAM" -o build/HELLO.SYS --disk build/hello.img
    python3 sysdisk.py wrap body.bin -o build/MYMOD.SYS
    python3 sysdisk.py inspect build/MYMOD.SYS
    python3 sysdisk.py disk -o build/mymod.img build/MYMOD.SYS

Nothing here reads or writes firmware.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import struct
import sys
from pathlib import Path

# --- loader facts (all four EPROM OSes; see floppy-sys-loader.md) --------------

LOAD_BASES = {"3.12 / 3.50": 0x69000, "3.08 / 3.11": 0x70000}
RAM_END = 0xF4000            # logical page 61 starts here; do not reach it
MAX_LFARLC = 0x3E            # largest relocation-table offset proven to work
HEADER_BYTES = 32            # two paragraphs

# --- 1.44 MB FAT12 geometry the BIOS accepts ------------------------------------

# 512-byte sectors, 1 sector/cluster, 1 reserved, 2 FATs, 224 root entries,
# 2880 sectors, media F0, 9 sectors/FAT, 18 sectors/track, 2 heads, 0 hidden.
BPB = bytes([0x00, 0x02, 0x01, 0x01, 0x00, 0x02, 0xE0, 0x00, 0x40, 0x0B, 0xF0,
             0x09, 0x00, 0x12, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00])
BPS = 512
SECTORS = 2880
RESERVED = 1
FAT_COUNT = 2
ROOT_ENTRIES = 224
SECTORS_PER_FAT = 9
ROOT_SECTORS = ROOT_ENTRIES * 32 // BPS
ROOT_OFFSET = (RESERVED + FAT_COUNT * SECTORS_PER_FAT) * BPS
DATA_START = RESERVED + FAT_COUNT * SECTORS_PER_FAT + ROOT_SECTORS

# --- the hello program ----------------------------------------------------------

# 8086 code, position-independent, CS-relative. Prints a NUL-terminated string
# one character at a time through BIOS INT 43h AX=4 (character in BL), then
# spins. The code bytes are the ones run on a physical MPC3000 on 2026-10-01.
HELLO_CODE = bytes([
    0xFA,              # 0000  cli
    0xFC,              # 0001  cld
    0x0E,              # 0002  push cs
    0x1F,              # 0003  pop  ds            ; DS = CS
    0x0E,              # 0004  push cs
    0x17,              # 0005  pop  ss            ; SS = CS
    0xBC, 0x00, 0x01,  # 0006  mov  sp, 0100h     ; stack at the end of the image
    0xFB,              # 0009  sti
    0xBE, 0x1D, 0x00,  # 000A  mov  si, 001Dh     ; the string below
    0x8A, 0x1C,        # 000D  mov  bl, [si]
    0x84, 0xDB,        # 000F  test bl, bl
    0x74, 0x08,        # 0011  jz   001Bh
    0xB8, 0x04, 0x00,  # 0013  mov  ax, 4
    0xCD, 0x43,        # 0016  int  43h           ; BIOS: put character BL on the LCD
    0x46,              # 0018  inc  si
    0xEB, 0xF2,        # 0019  jmp  000Dh
    0xEB, 0xFE,        # 001B  jmp  001Bh         ; done: spin
])                     # 001D  string: CR LF text NUL
HELLO_IMAGE_BYTES = 0x100


def hello_image(text: bytes) -> bytes:
    if len(HELLO_CODE) != 0x1D:
        raise ValueError("hello code moved; fix the SI immediate and the jumps")
    if not text or any(c < 0x20 or c > 0x7E for c in text):
        raise ValueError("text must be printable ASCII")
    body = HELLO_CODE + b"\r\n" + text + b"\x00"
    if len(body) > 0x80:
        raise ValueError(f"text is too long ({len(text)} bytes; the limit is {0x80 - 0x1D - 3})")
    return body.ljust(HELLO_IMAGE_BYTES, b"\x00")


# --- MZ -------------------------------------------------------------------------

def pack_mz(body: bytes, *, ip: int = 0, cs: int = 0, ss: int = 0, sp: int = 0) -> bytes:
    """Wrap `body` in a 32-byte MZ header with no relocations.

    SS:SP of 0:0 keeps the loader's own stack (0040:69C4); set up your own
    stack in your first instructions, as the hello program does.
    """
    size = HEADER_BYTES + len(body)
    header = struct.pack(
        "<14H",
        0x5A4D,              # e_magic  'MZ'
        size % 512,          # e_cblp   bytes in the last 512-byte page
        (size + 511) // 512, # e_cp     pages in the file
        0,                   # e_crlc   relocation count
        HEADER_BYTES // 16,  # e_cparhdr header size in paragraphs
        0,                   # e_minalloc (ignored by the loader)
        0xFFFF,              # e_maxalloc (ignored)
        ss, sp,              # e_ss, e_sp
        0,                   # e_csum (ignored)
        ip, cs,              # e_ip, e_cs
        0x1C,                # e_lfarlc
        0,                   # e_ovno (ignored)
    )
    return header.ljust(HEADER_BYTES, b"\x00") + body


def inspect_mz(blob: bytes) -> tuple[list[str], list[str]]:
    """Replay the ROM loader's header handling. Returns (errors, notes)."""
    errors: list[str] = []
    notes: list[str] = []
    if len(blob) < 0x1C:
        return ["file is shorter than the 28-byte MZ header (loader returns AH=1)"], notes
    (magic, cblp, cp, crlc, cparhdr, _minalloc, _maxalloc, ss, sp, _csum, ip, cs,
     lfarlc, _ovno) = struct.unpack_from("<14H", blob)
    if magic != 0x5A4D:
        errors.append("first two bytes are not 'MZ' (loader returns AH=2; the machine then shows "
                      "'software bug of type 11h')")
        return errors, notes
    header = cparhdr * 16
    if cparhdr < 2:
        errors.append("e_cparhdr is below 2; the loader reads header_size - 1Ch bytes before the image")
    file_size = cp * 512 if cblp == 0 else (cp - 1) * 512 + cblp
    if file_size != len(blob):
        errors.append(f"e_cp/e_cblp describe {file_size} bytes but the file has {len(blob)}")
    image = file_size - header
    if image <= 0:
        errors.append("the header leaves no image")
    if crlc and lfarlc > MAX_LFARLC:
        errors.append(f"e_lfarlc is {lfarlc:#x}; the loader reads that many bytes into a fixed buffer "
                      f"with no bound, and only values up to {MAX_LFARLC:#x} are known to work")
    if crlc and lfarlc + crlc * 4 > header:
        errors.append("the relocation table runs past the header")
    notes.append(f"image {image} bytes, {crlc} relocation(s), entry {cs:04X}:{ip:04X} relative to the load segment")
    if ss == 0 and sp == 0:
        notes.append("SS:SP is 0:0, so the BIOS stack at 0040:69C4 is kept: set your own stack first")
    else:
        notes.append(f"stack {ss:04X}:{sp:04X} relative to the load segment")
    for name, base in LOAD_BASES.items():
        room = RAM_END - base
        left = room - image
        if left < 0:
            errors.append(f"on {name} EPROMs the image ends {-left} bytes past logical {RAM_END:#x}")
        else:
            notes.append(f"on {name} EPROMs: loads at {base:#07x}, {left} bytes left for BSS and stack "
                         f"below {RAM_END:#x}")
    if crlc > 500:
        notes.append(f"{crlc} relocations cost one 4-byte disk read each; expect a slow load")
    return errors, notes


# --- FAT12 ----------------------------------------------------------------------

def fat_name(name: str) -> bytes:
    base, _, ext = name.upper().partition(".")
    if not re.fullmatch(r"[A-Z0-9_]{1,8}", base) or not re.fullmatch(r"[A-Z0-9_]{0,3}", ext):
        raise ValueError(f"{name!r} is not an 8.3 name of A-Z, 0-9 and _")
    return base.ljust(8).encode() + ext.ljust(3).encode()


def fat12_set(fat: bytearray, cluster: int, value: int) -> None:
    offset = cluster + cluster // 2
    if cluster & 1:
        fat[offset] = (fat[offset] & 0x0F) | ((value & 0x0F) << 4)
        fat[offset + 1] = (value >> 4) & 0xFF
    else:
        fat[offset] = value & 0xFF
        fat[offset + 1] = (fat[offset + 1] & 0xF0) | ((value >> 8) & 0x0F)


def pack_fat12(files: list[tuple[str, bytes]], *, oem: bytes = b"OARSYS  ",
               volume_id: bytes = b"OAR1", label: bytes = b"OAR MPC3000") -> bytes:
    """1.44 MB FAT12 image. Files sit in the root directory, in list order,
    each contiguous. The image is a pure function of its inputs (no dates)."""
    if len(oem) != 8 or len(volume_id) != 4 or len(label) != 11:
        raise ValueError("OEM, volume id and label must be 8, 4 and 11 bytes")
    names = [fat_name(name) for name, _ in files]
    if len(set(names)) != len(names):
        raise ValueError("two files have the same disk name")
    if len(files) > ROOT_ENTRIES:
        raise ValueError("too many files for the root directory")
    disk = bytearray(SECTORS * BPS)
    disk[0:3] = b"\xEB\x3C\x90"
    disk[3:11] = oem
    disk[11:32] = BPB
    disk[0x26] = 0x29
    disk[0x27:0x2B] = volume_id
    disk[0x2B:0x36] = label
    disk[0x36:0x3E] = b"FAT12   "
    disk[0x1FE:0x200] = b"\x55\xAA"

    fat = bytearray(SECTORS_PER_FAT * BPS)
    fat[0:3] = b"\xF0\xFF\xFF"
    cluster = 2
    for index, (name, (_, data)) in enumerate(zip(names, files)):
        count = (len(data) + BPS - 1) // BPS
        if cluster + count - 2 > SECTORS - DATA_START:
            raise ValueError("files do not fit on a 1.44 MB disk")
        for c in range(cluster, cluster + count):
            fat12_set(fat, c, 0xFFF if c == cluster + count - 1 else c + 1)
        offset = (DATA_START + cluster - 2) * BPS
        disk[offset:offset + len(data)] = data
        entry = bytearray(32)
        entry[:11] = name
        entry[11] = 0x20                     # archive only: the loader skips 0x1E attributes
        struct.pack_into("<H", entry, 26, cluster if count else 0)
        struct.pack_into("<I", entry, 28, len(data))
        root = ROOT_OFFSET + index * 32
        disk[root:root + 32] = entry
        cluster += count
    for copy in range(FAT_COUNT):
        start = (RESERVED + copy * SECTORS_PER_FAT) * BPS
        disk[start:start + len(fat)] = fat
    return bytes(disk)


def read_root(disk: bytes) -> list[tuple[str, bytes]]:
    """Read back contiguous root-directory files written by pack_fat12."""
    out = []
    for index in range(ROOT_ENTRIES):
        entry = disk[ROOT_OFFSET + index * 32:ROOT_OFFSET + index * 32 + 32]
        if entry[0] == 0:
            break
        name = entry[:8].decode().rstrip() + "." + entry[8:11].decode().rstrip()
        first, = struct.unpack_from("<H", entry, 26)
        size, = struct.unpack_from("<I", entry, 28)
        offset = (DATA_START + first - 2) * BPS
        out.append((name.rstrip("."), disk[offset:offset + size]))
    return out


# --- commands -------------------------------------------------------------------

def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def write(path: str, blob: bytes) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(blob)
    print(f"wrote {path}: {len(blob)} bytes  sha256 {sha256(blob)}")


def report(blob: bytes) -> int:
    errors, notes = inspect_mz(blob)
    for note in notes:
        print("note ", note)
    for error in errors:
        print("ERROR", error)
    return 1 if errors else 0


def disk_from(paths: list[str]) -> bytes:
    files = [(Path(p).name, Path(p).read_bytes()) for p in paths]
    systems = [name for name, _ in files if name.upper().endswith(".SYS")]
    if not systems:
        print("note  no .SYS file: the machine will boot its EPROM OS from this disk")
    elif not files[0][0].upper().endswith(".SYS") or len(systems) > 1:
        print("note  the ROM loads only the FIRST .SYS in directory order; a bad first .SYS is fatal")
    for name, data in files:
        if name.upper().endswith(".SYS") and report(data):
            raise SystemExit(f"{name} would not load; not writing a disk")
    return pack_fat12(files)


def cmd_hello(args: argparse.Namespace) -> int:
    payload = pack_mz(hello_image(args.text.encode("ascii")))
    if report(payload):
        return 1
    write(args.output, payload)
    if args.disk:
        write(args.disk, pack_fat12([(Path(args.output).name, payload)]))
    return 0


def cmd_wrap(args: argparse.Namespace) -> int:
    payload = pack_mz(Path(args.body).read_bytes(), ip=args.ip, cs=args.cs, ss=args.ss, sp=args.sp)
    if report(payload):
        return 1
    write(args.output, payload)
    return 0


def cmd_inspect(args: argparse.Namespace) -> int:
    return report(Path(args.file).read_bytes())


def cmd_disk(args: argparse.Namespace) -> int:
    write(args.output, disk_from(args.files))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sysdisk", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    integer = lambda text: int(text, 0)  # noqa: E731

    p = sub.add_parser("hello", help="build the minimal text-printing program")
    p.add_argument("--text", default="HELLO FROM RAM")
    p.add_argument("-o", "--output", required=True, help="e.g. build/HELLO.SYS (8.3 name)")
    p.add_argument("--disk", help="also write a 1.44 MB disk image holding it")
    p.set_defaults(func=cmd_hello)

    p = sub.add_parser("wrap", help="wrap a flat binary in the MZ header the ROM accepts")
    p.add_argument("body", help="flat binary assembled for offset 0, no relocations")
    p.add_argument("-o", "--output", required=True)
    for flag in ("--ip", "--cs", "--ss", "--sp"):
        p.add_argument(flag, type=integer, default=0)
    p.set_defaults(func=cmd_wrap)

    p = sub.add_parser("inspect", help="check a .SYS file against the ROM loader's rules")
    p.add_argument("file")
    p.set_defaults(func=cmd_inspect)

    p = sub.add_parser("disk", help="pack files into a 1.44 MB FAT12 image, in the order given")
    p.add_argument("-o", "--output", required=True)
    p.add_argument("files", nargs="+")
    p.set_defaults(func=cmd_disk)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
