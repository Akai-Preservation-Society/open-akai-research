---
id: s900.rom-images
title: S900 OS EPROM images - identity, reset code, and the 1.2b set
machine: s900
area: firmware
firmware: ["s900-v1.2a", "s900-v1.2b", "s900-v1.2c"]
status: static
hardware_tested: no
summary: The S900 OS 1.2A files on s900fx.com equal MAME's 1.2a. Its 1.2B set shares MAME's 1.2c LS chip but has another MS chip, and differs from 1.2a in two bytes. Both reset through MOV AX,F800h / MOV DS,AX / JMP FAR FFF8:0000.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["MAME src/mame/akai/s900.cpp at commit c2caa8969adb (ROM sets)", "s900fx.com resources: Akai-S900-ROM-V1.2A.zip, -V1.2B.zip (downloaded 2026-11-13)"]
---

# S900 OS EPROM images - identity, reset code, and the 1.2b set

How to tell which S900 OS a chip pair holds. Linear image = LS chip
(IC12) at even offsets, MS chip (IC11) at odd offsets; 32,768 bytes.

## Claims

- **[static]** The 1.2A files published on s900fx.com are byte-identical to MAME's 1.2a set. A whole-image SHA-256 is now in [../firmware.toml](../firmware.toml).
- **[static]** The 1.2B files there have an LS chip identical to MAME's **1.2c** LS chip (crc32 `d0925ed4`) and an MS chip (`6dbfd383`) that matches neither MAME set. Recorded as `s900-v1.2b`.
- **[static]** The 1.2b linear image differs from 1.2a in exactly two bytes: `0x1404` (`3C` -> `3F`, an LS byte) and `0x2D05` (`72` -> `E3`, an MS byte). Both images carry `AKAI S900 VERSION 1,2` at `0x7DA0`.
- **[hypothesis]** MAME's "1.2c" and the published "1.2b" are the same revision, with MAME's MS chip differing in more than this one byte, or are two neighbouring revisions. Reason: identical LS chips. Test: compare MAME's 1.2c MS chip with `s900-v1.2b`'s byte by byte.
- **[static]** In both sets the last 16 bytes (`0x7FF0`) start `B8 00 F8 8E D8 EA 00 00 F8 FF`: `MOV AX,F800h; MOV DS,AX; JMP FAR FFF8:0000`. With the 32 KiB ROM mirrored up to `0xFFFFF` (MAME), physical `0xFFF80` is linear `0x7F80`.
- **[open]** What the two changed bytes do.

## Evidence

- Static, 2026-11-13: chip files hashed and compared with MAME's CRC32 and SHA-1, interleaved and compared. Pins in [../pins/](../pins/) cover the reset code, the version string and both changed bytes.

## Open questions

- [Akai S900: the first things to establish](../questions/first-steps.md)
