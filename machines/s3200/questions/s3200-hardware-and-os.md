---
id: s3200.q.s3200-hardware-and-os
title: Is the S3200 an XL board, and does it run the OS 2.00 EPROM pair?
machine: s3200
area: hardware
status: open
priority: high
needs: ["hardware", "document", "firmware-image"]
summary: MAME says the S3200 uses the XL board, but the only image studied here is the S3000-board 256 KiB pair labelled S3000/S3200. Nobody has checked which an S3200 has.
blocks: ["s3200.address-model", "s3200.os-load-and-save"]
related: ["s3200.hardware-overview", "s3200.eprom-layout"]
---
# Is the S3200 an XL board, and does it run the OS 2.00 EPROM pair?

## What is unknown

Unknown: whether an S3200 has the S3000 board (256 KiB ROM at `0xC0000`, banking port `0x68`) or the XL board (512 KiB ROM at `0x80000`), and which OS images it runs.

Known: MAME's driver comment says the S3200 is XL-based but MAME defines no S3200 machine. The image in [../firmware.toml](../firmware.toml) is labelled "S3000/S3200 V2.0", equals MAME's `s3000` set, is 256 KiB with its reset vector at file `0x3FFF0` for a `0xC0000` base, and contains `S3000` but no `S3200` string ([../findings/eprom-layout.md](../findings/eprom-layout.md)). The file set's own name is the only link to the S3200.

## Why it matters

Every address in this folder is keyed to `s3200-v2.00`. If an S3200 runs an XL-class OS, none of them apply to it, and the disk-load route in [../findings/os-load-and-save.md](../findings/os-load-and-save.md) would need to be found again for that OS.

## How to answer it

1. On a real S3200, note the OS version on the boot screen, then remove the OS EPROM(s) and record their number, size and labels. Read them and run `python3 tools/oar.py identify`.
2. Photograph the main board and compare its ROM sockets and the parts at MAME's port `0x68` latch with an S3000 and an S3000XL.
3. Cite a service manual or parts list that names the S3200 board.

Settled when a dump read from an S3200 is matched by hash, or shown to differ.
