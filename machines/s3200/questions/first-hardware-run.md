---
id: s3200.q.first-hardware-run
title: A first hardware run of OS 2.00 and a disk-loaded image
machine: s3200
area: boot
status: open
priority: high
needs: ["hardware"]
summary: No claim in this folder has been checked on a real unit. The first test is the stock boot line, then one image loaded from floppy whose only change is the 9-byte boot-screen prefix.
blocks: ["s3200.os-load-and-save"]
related: ["s3200.eprom-layout", "s3200.disk-formats"]
---
# A first hardware run of OS 2.00 and a disk-loaded image

## What is unknown

Unknown: everything that depends on real hardware. The stock boot line is expected to read `OPERATING SYSTEM 2.00   N Mwords fitted`; a type-`0x63` file of version 2.00 or later is expected to autoload at power-on; and a change to `0x6111-0x6119` is expected to show in place of `OPERATING`. All three are `static` or `emulator` claims.

## Why it matters

Until one disk-loaded image has run, the reversible route for any change ([../findings/os-load-and-save.md](../findings/os-load-and-save.md)) is a prediction, and so is the claim that no ROM checksum blocks a patched image.

## How to answer it

On a unit with backed-up data, stock EPROMs (hashes checked) and a spare floppy:

1. Power on with no floppy and no hard disk holding an OS. Photograph the boot line.
2. Build an image that differs from `s3200-v2.00` only at `0x6111-0x6119`; share it as a patch manifest (`oar.py patch-diff`), not as an image. Put it on a floppy as a type-`0x63` file with version word `0x0C00`.
3. Power on with that floppy. Expect `loading OPERATING SYSTEM 2.00`, then the boot line with the new 9 characters.
4. Remove the floppy and power-cycle. Expect the stock boot line.

Stop at any freeze, reset loop or unexpected disk write. Record the date, the image hashes and photos.
