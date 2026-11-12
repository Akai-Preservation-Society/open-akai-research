---
id: mpc3000.eprom-layout
title: MPC3000 OS EPROM layout and how to identify an image
machine: mpc3000
area: firmware
firmware: ["mpc3000-v3.08", "mpc3000-v3.11", "mpc3000-v3.12", "mpc3000-vailixi-3.50"]
status: static
hardware_tested: partial
summary: The OS is two interleaved 256 KiB EPROMs. This gives the layout of the interleaved image, the reset path, and the rule that an image is identified by hash, never by the version it prints.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["MAME src/mame/akai/mpc3000.cpp (ROM definitions)", "Akai MPC3000 service manual (parts list)"]
---

# MPC3000 OS EPROM layout and how to identify an image

## Claims

- **[documented]** The OS is stored in two AM27C020 EPROMs, 262,144 bytes each: IC13 holds the even ("LS") bytes and IC14 the odd ("MS") bytes of a 16-bit-wide program.
- **[static]** Interleave them (`linear[0::2] = LS`, `linear[1::2] = MS`) to get the 524,288-byte linear image the CPU sees. `python3 tools/oar.py interleave LS MS -o linear.bin` does this and `split` reverses it. Neither chip file is a program by itself.
- **[static]** Hashes of every known image are in [../firmware.toml](../firmware.toml). Chip hashes for 3.11, 3.12 and Vailixi 3.50 equal the MAME ROM set. 3.08 is not in MAME. 3.10 is in MAME but nobody here has examined it.
- **[static]** In all four examined images the bytes at linear `0x7FFF0` are `EA 00 00 F0 FF` (`JMP FAR FFF0:0000`), and the reset stub at `0x7FF00-0x7FF43` is byte-identical.
- **[static]** Regions of the linear image (3.11, 3.12 and Vailixi 3.50 share this shape; exact ends are from Vailixi 3.50):

  | Linear range | Contents |
  |---|---|
  | `0x00000-0x00053` | Interrupt vectors used only before extended addressing is switched on |
  | `0x00054-0x1FFFF` | Empty (`FF`) |
  | `0x20000-0x27C91` | Initialised data ("DGROUP") and strings, copied to RAM at boot |
  | `0x30000-0x73FFF` | OS application code (with `FF` padding at the end) |
  | `0x74000-0x77FFF` | Empty (`FF`) |
  | `0x78000-0x7FFFF` | BIOS (`F800:`), boot and page-table code (`FAC0:`), AMX kernel (`FB00:`), reset stub |

- **[static]** OS 3.08 is laid out differently: its initialised data starts at linear `0x30000` and its OS entry is at `B6ED:0000`. Do not apply 3.11/3.12/3.50 offsets to it.
- **[static]** The Vailixi 3.50 reference image prints its name from linear `0x210F5` (`Vailixi 3.50 (---/--/----)`) and its BIOS banner from `0x78125` (`MPC-3000 BIOS 21/08/07`).
- **[hardware]** A physical MPC3000 whose screen reported OS version 3.50 did not hold the reference image: bytes in its BIOS region (above linear `0x78000`) differed. So the version on screen does not identify the bytes. Before using any address keyed to a firmware id, hash the image, or run `oar.py verify`.
- **[static]** OS 3.16 is not an EPROM image. It is a 458,047-byte DOS MZ file (`M3K316.SYS`) that the EPROM OS loads from floppy into RAM; see [floppy-sys-loader.md](floppy-sys-loader.md).

## Evidence

- Hashes, the reset bytes, the identical reset stub and the empty ranges were computed from dumps of 3.08, 3.11, 3.12 and Vailixi 3.50 on 2026-11-13 and are pinned in [../pins/](../pins/).
- Region boundaries come from static analysis of `mpc3000-vailixi-3.50` (2026-09-21 to 2026-09-25).
- The hardware claim: on 2026-10-01 a small program loaded from floppy on a real unit summed and dumped part of the ROM as the CPU sees it; the result differed from the reference image and the disk image was read back unchanged afterwards. One unit, one session.

## Open questions

- [OS 3.10 has not been examined](../questions/os-3.10-image.md)
- [A code map for the stock OS images](../questions/stock-os-code-map.md)
