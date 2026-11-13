---
id: s950.rom-images
title: S950 OS EPROM images - identity, reset vector, and the two different "1.2a" sets
machine: s950
area: firmware
firmware: ["s950-v1.0a", "s950-v1.2a", "s950-v1.2a-variant", "s950-v1.2b"]
status: static
hardware_tested: no
summary: S950 OS sets 1.0a and 1.2b published on s950fx.com equal MAME's. The "1.2A" files there have MAME's 1.2a LS chip but a different MS chip - 1.0a with 23 bytes changed. All sets reset to JMP FAR F000:FF80. 1.2b identifies itself as "1.5" in one string.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["MAME src/mame/akai/s900.cpp at commit c2caa8969adb (ROM sets)", "s950fx.com resources: Akai-S950-ROM-V1.0A.zip, -V1.2A.zip, -V1.2B.zip (downloaded 2026-11-13)"]
---

# S950 OS EPROM images - identity, reset vector, and the two different "1.2a" sets

How to tell which S950 OS a chip pair holds. Linear image = LS chip
(IC12) at even offsets, MS chip (IC11) at odd offsets
(`python3 tools/oar.py interleave LS MS -o linear.bin`); 65,536 bytes.

## Claims

- **[static]** The 1.0A and 1.2B chip files published on s950fx.com are byte-identical to MAME's sets. Whole-image SHA-256 values are now in [../firmware.toml](../firmware.toml).
- **[static]** The 1.2A files published there have MAME's 1.2a LS chip (crc32 `21af5435`) but a different MS chip (`2d96a2fb` against MAME's `e14ceba2`). They are recorded as `s950-v1.2a-variant`.
- **[static]** That variant is `s950-v1.0a` with 23 bytes changed:
  - the version digit `0` -> `2` at `0x2BDD` and `0x9FC0`;
  - 14 bytes at `0x004A-0x0057`, zero in 1.0a;
  - six bytes at `0x8693-0x8698`;
  - one byte at `0x3A0D`.
  So it is a small patch on 1.0a, not a rebuild.
- **[static]** 1.2B is a different build: its LS and MS chips each differ from the 1.2A variant in 29,830 bytes. Its strings sit at other offsets (model string `0x2B6E`, banner `0xA120`). The banner reads `AKAI S950 1.2  xxxx Kwords installed ... IB109 ... SCSI hard disk`, but the model string reads `MS950  1.5`.
- **[static]** In all three sets the five bytes at `0xFFF0` are `EA 80 FF 00 F0` (`JMP FAR F000:FF80`). With the ROM at physical `0x80000-0x8FFFF` mirrored up to `0xFFFFF` (MAME), physical `0xFFF80` is linear `0xFF80`. In 1.2B everything after those five bytes up to `0xFFFF` is `FF`.
- **[static]** 1.0a and the 1.2a variant contain the strings `S1000` and `S900` together (at `0x3F4C`; `0x409D` in 1.2B), which fits the owner's manual's statement that the S950 reads S900 and S1000 sound libraries.
- **[open]** Which MS chip Akai shipped as 1.2a: MAME's (`e14ceba2`) or the s950fx.com one (`2d96a2fb`). A dump of a factory-labelled 1.2a MS chip settles it.
- **[open]** What the 14-byte routine at `0x004A` and the patch at `0x8693` change. Not decoded.

## Evidence

- Static, 2026-11-13: chip files hashed and compared with MAME's CRC32 and SHA-1, interleaved, compared byte by byte, and searched for strings. Pins in [../pins/](../pins/) cover the reset bytes, the version strings and the changed ranges, so `oar.py verify` can check a dump.
- The reset-vector reading is one instruction, decoded by hand.

## Open questions

- [Akai S950: the first things to establish](../questions/first-steps.md)
