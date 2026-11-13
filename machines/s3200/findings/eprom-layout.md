---
id: s3200.eprom-layout
title: The OS 2.00 EPROM pair, how to identify it, and why it has no ROM checksum
machine: s3200
area: firmware
firmware: ["s3200-v2.00"]
status: static
hardware_tested: no
summary: OS 2.00 is two 128 KiB 27C010 EPROMs, LOW even bytes and HIGH odd. The pair equals MAME's s3000 v2.0 set. The labels 9C79/2900 are chip byte sums. Nothing in the firmware checks the ROM, so a patched image needs no checksum repair.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["MAME src/mame/akai/s3000.cpp at commit c2caa8969adb (ROM_START s3000)"]
---

# The OS 2.00 EPROM pair, how to identify it, and why it has no ROM checksum

How to turn two chip dumps into the linear image every offset in this
folder refers to, and how to tell it is the right image.

## Claims

- **[static]** The OS is two 131,072-byte EPROMs. Interleave them with the LOW chip's bytes at even offsets and the HIGH chip's at odd offsets (`python3 tools/oar.py interleave LOW HIGH -o linear.bin`). In that order the string at `0x400` reads `Error - Invalid Hardware Configuration` and the code decodes cleanly; the other order gives byte-swapped text.
- **[documented]** MAME loads its `s3000` "ver 2.0" set the same way (`akai s3x00 v2.0 low.bin` at even bytes, `high.bin` at odd bytes, `ROM_SKIP(1)`), on 27C010-size chips.
- **[static]** The contributor's chip files have the CRC32 and SHA-1 MAME lists for that set. Hashes of both chips and of the linear image are in [../firmware.toml](../firmware.toml). Check yours with `python3 tools/oar.py identify LOW HIGH`.
- **[static]** The chip labels `9C79` (LOW) and `2900` (HIGH) are the 16-bit sums of each chip's bytes, the value an EPROM programmer shows. A patched image keeps booting (next claim) but gets new sums, so record them for burning and read-back.
- **[static]** No ROM checksum is used. The boot block (`0x1FE80-0x1FF50`) only tests RAM, sets page registers and copies the ROM to RAM. The image stores no checksum word: it sums to no fixed value under byte-sum16, LE or BE word-sum16, CRC-16/XMODEM or CRC-32. A scan of every short backward loop found eight accumulate-without-store loops. None reads ROM or the code's RAM copy: `0x1BE07` and `0x1C95D` sum disk buffers, `0x1C296` and `0x2BCF2` add table sizes, `0x2BA98` averages sample bytes, `0x23E0D` and `0x2DEB8` walk record lengths, and `0x14BAD` is arithmetic.
- **[static]** Identifying strings: `S3000   ` at `0xF4E` (in a settings option list after `STANDARD`), `Error - Invalid Hardware Configuration` at `0x400`, and `OPERATING SYSTEM` at `0x6111`. S2800 messages appear at `0x3148E` and `0x31B50` (for example "... on the S2800."). There is no `S3200` string anywhere in the image.
- **[static]** The image's own version bytes (`0x1C` minor, `0x1E` major + 10) give 2.00 ([os-load-and-save.md](os-load-and-save.md)).
- **[static]** All 44,309 bytes from `0x352DB` to `0x3FFEF` are zero. This is not free space: see [memory-use.md](memory-use.md).
- **[hypothesis]** One OS build serves several models (S2800, S3000, possibly S3200), choosing behaviour from the configuration bits on port 0x60. Reasons: the S2800 messages and the memory-ID probe ([peripherals.md](peripherals.md)). Not tested: no model-specific branch has been traced.

## Evidence

- Interleave order, string offsets, chip sums and the zero tail: computed from the contributor's dumps on 2026-10-21 and re-checked on 2026-11-13. Pins: `0x400`, `0xF4E`, `0x352DB` (44,309 bytes) in [../pins/s3200-v2.00.csv](../pins/s3200-v2.00.csv).
- MAME match: CRC32 `12a657c9` / `1763a18d` and the SHA-1 values compared with `ROM_START( s3000 )` in MAME at commit `c2caa8969adb` on 2026-11-13.
- Checksum search: whole-image sums computed offline; loop census by a linear disassembly (`ndisasm -b16`) of the image, every short backward loop inspected. Pins `0x1FE80` (209 bytes), `0x1C95D`.
- The dumps came from a file set labelled "S3000 & S3200 V2.0" whose note says the binaries were rebuilt from HEX files. Its per-chip sums match the labels; it has not been compared with a dump read from the contributor's own unit.

## Open questions

- [Is the S3200 an XL board, and does it run this image?](../questions/s3200-hardware-and-os.md)
- [A first hardware run](../questions/first-hardware-run.md)
