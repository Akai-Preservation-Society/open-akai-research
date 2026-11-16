---
id: mpc3000.q.3kplus-free-ram-at-runtime
title: Is RAM above the 3K PLUS cave free at run time?
machine: mpc3000
area: memory
status: open
priority: high
needs: ["emulator", "analysis"]
summary: Static analysis finds no 3K PLUS reference to logical F135C-F3FFF, but pointer writes, DMA and one unbounded MIDI Remote table index have not been ruled out at run time.
related: ["mpc3000.3kplus-structure", "mpc3000.os316-extending"]
---

# Is RAM above the 3K PLUS cave free at run time?

## What is unknown

[3kplus-structure.md](../findings/3kplus-structure.md) shows statically that the
resident cave ends at `7E00:A35B` (logical `F135B`) and that no direct, far-pointer or
segment reference reaches `F135C`-`F3FFF`. Not ruled out: writes through pointers
computed at run time, DMA (floppy, SCSI, sample DSP) into that range, and the MIDI
Remote bitmap at `7E00:A34C`, whose index has no upper bound and could reach
`7E00:A363` if a byte of `80h` or more gets there. For OS 3.16 alone, an emulator run
saw no access above its extent ([os316-extending.md](../findings/os316-extending.md));
nobody has watched 3K PLUS.

## Why it matters

Any code added to 3K PLUS must live there. A write into it at run time would corrupt
added code silently.

## How to answer it

In MAME (`mpc3000`, sets `vailixi`, `default`, `v311`), boot 3K PLUS from floppy and
install write watchpoints on physical `0x3F135C`-`0x3F3FFF` (OS 3.16 keeps
physical = `0x300000` + logical). Exercise everything the README lists, including
SCSI Disk mode, screen mirror, Input Thru and MIDI Remote SysEx with status and
real-time bytes inside the message. No write may occur after the start-up. Record
the MAME version and the sets used.
