---
id: s3200.q.rom-serial-loader
title: Purpose and caller of the ROM serial loader
machine: s3200
area: boot
status: open
priority: low
needs: ["analysis", "document", "hardware"]
summary: The ROM routine at DFE8:00D1 loads code over the serial unit, but nothing is known to call it, and from the running OS its jump lands in RAM.
related: ["s3200.rom-serial-loader"]
---
# Purpose and caller of the ROM serial loader

## What is unknown

Unknown: what reaches `0x192C6` (the only jump to `FFFF:0005`), what the loader is for, and which connector carries its serial lines. See [../findings/rom-serial-loader.md](../findings/rom-serial-loader.md).

## Why it matters

If a key combination or service mode reaches it with XAM off, it would be a recovery route that needs no disk. If not, it can be ignored.

## How to answer it

Trace the 6-byte record table at `0x2E8E0-0x2E993` and the users of `[0x7551]`/`[0x752B]` at `0x1900D-0x19058`, or show by full disassembly that `0x192C6` is unreachable. Look for a factory or service procedure in a service manual. On hardware, only with backed-up media, watch MIDI OUT for an echo.
