---
id: s3200.memory-use
title: What OS 2.00 writes at run time, and why its zero areas are not free space
machine: s3200
area: memory
firmware: ["s3200-v2.00"]
status: static
hardware_tested: no
summary: The zero ranges 0x8060-0xFE8F and 0x352DB-0x3FFEF are run-time buffers, not free space. DGROUP variables start near 0x6AE0. Code segment 2033 holds variables at 0x24E4B and 0x2A961. No byte of the OS image has been shown free on hardware.
contributors: ["open-akai-research"]
last_verified: 2026-11-02
depends_on: ["s3200.code-structure"]
---

# What OS 2.00 writes at run time, and why its zero areas are not free space

Read this before placing added code or data anywhere in the image.
**No range is established as free.** Absence of a write in the runs
below does not make a byte free.

## Claims

### Ranges written by code (static)

- **[static]** `0x0000-0x03FF`: live IVT, RAM entry code at `0x50-0x83`, soft-restart flag `[0x0052]`, version word at `0x1C-0x1F`, initial stack `0x100-0x1FF` (SS:SP = `0000:0200`). Every byte here is executed, overwritten or read as state.
- **[static]** `0x6BA0-0x805F`: code in `0FE9` and `2033` writes over 1,000 distinct DS=0 addresses between `0x6BA0` and `0x80FA`, mixed with initialised strings and tables (strings `0x6BB2-0x6C6x`, tables near `0x7000` and `0x8010-0x805F`). A byte here may be patched only if it is shown to be read before it is written. Named variables are in [../symbols/s3200-v2.00.csv](../symbols/s3200-v2.00.csv), including `0x7F60` (ROM-boot flag), `0x7F61` and `0x7F62`, which must stay as in the image.
- **[static]** `0x8060-0xFE8F` (32,304 bytes) is zero in the image but used: disk transfer buffer `DS:9120`, a word table `0xA134-0xA150`, the display line `0xB91C-0xB944`, the hard-disk header `0xB94E`, the volume table `0xBA18` (100 x 16 bytes), and variables at `0x8501` and `0x8A2D-0x8A5D`.
- **[static]** `0x352DB-0x3FFEF` is zero in the image but is `2DF3` BSS: the 510-entry floppy directory buffer `2DF3:7C7A-AC49` (file `0x35BAA-0x38B79`) is cleared at `0x23DD3` and filled by every floppy mount, and `2DF3:73B0` (file `0x352E0`) is a display save area.
- **[static]** `0x3FF00-0x3FF4D` is replaced by the relaunch stub whenever an OS is loaded from disk ([os-load-and-save.md](os-load-and-save.md)).
- **[static]** Two variables inside code segment `2033`: `2033:4B1B-4B1D` (file `0x24E4B-0x24E4D`, after a `RETF`, written by the routine at `2033:4ACA`), and `2033:A631-A633` (file `0x2A961-0x2A963`, written by the routine at `2033:A634`). `2033:A609-A630` (file `0x2A939-0x2A960`) is a table of 10-byte records read through CS. Every other CS-relative operand in reachable code is a read.
- **[static]** Two string bytes are rewritten at run time: `0x64BF` and `0x64D0`, the first letter of "Qlist" in the saving and loading messages, set to `T` or `Q` by code at `0x1B67C-0x1B712`. Patches to them are lost, and moving that text breaks the writes.
- **[static]** At boot the OS patches the help text (`1FFE:018D-0190`, `0194`, `019C`) and DGROUP bytes `0x23A9`, `0x27CE` and `0xD1B` (code at `0x2044C`), and a table-driven copier at `0x20504` fills `2DF3` initialised data.

### Ranges written in emulator runs

- **[emulator]** One boot to the PROGRAMS IN MEMORY screen wrote, inside the image: `0x0-0x3`, `0x1D`, `0x52`, stack `0x19A-0x1FF`; DGROUP `0xD1B`, `0x23A9`, `0x27CE`, `0x2880-0x38FD` (3-byte groups), `0x48FC`, `0x4C17-0x4C27`, `0x5E94-0x5E95`, `0x6AE0-0x6B9F` (so variables start before `0x6BA0`), `0x6C50-0x8003`; BSS `0x8070-0xB944`; help text `0x2016D-0x2017C`; `0x24E4B-0x24E4D`; `2DF3` data `0x2EA15-0x314AA` and `0x35242-0x352D2`; `2DF3` BSS `0x352E0-0x35537`, `0x35560`, `0x355A0`, and one byte per `0x1B2`-byte record from `0x39330` up to `0x3C901`. Outside the image it wrote `0x47000-0x4FEDF` and `0x90000-0xBFFFF`. Nothing in `0FE9` code, the boot block or the reset vector was written.
- **[emulator]** Boots with port `0x60` = `0x40` and `0x80` wrote the same address set as `0xC0` (values not compared). A floppy mount adds `0xC058-0xD317`, `0x35BAA-0x38B79` (all 12,240 bytes, DMA channel 1), stack `0x18C-0x199` and disk variables in `0x64D0-0x7605`. MIDI input adds the receive ring `0x200-0x20D`, variables `0x6CA1-0x7923` and `0x3C7BE-0x3C96F`.
- **[emulator]** Across all runs, the only bytes written inside the two code segments (other than by LOAD OS, which rewrites everything) were `0x24E4B-0x24E4D`. `0x2A961-0x2A963` is written by code that no run reached.
- **[open]** Writes during SAVE through its real screens, sampling, editing, other screens and hard-disk use are not known; the emulator has no panel model. See [../questions/runtime-writes-and-free-space.md](../questions/runtime-writes-and-free-space.md).

## Evidence

- Static: an absolute-address write census over code `0xFE90-0x352DB` (DS=0 operands without override) and a classification of every CS-prefixed operand in the reseeded disassembly ([code-structure.md](code-structure.md)), done by the contributor's unpublished scripts on 2026-11-02. Repeat by reading the pinned ranges with `ndisasm -b16`: `0x8060` (32,304), `0x7F60` (4), `0x23DD3`, `0x24DFA`, `0x24E4A`, `0x24E55`, `0x2A939`, `0x2A961`, `0x2A973`, `0x1B67C`, `0x64BF`, `0x64D0`, `0x2044C`, `0x20504`.
- Emulator: the contributor's own unpublished 8086 emulator with invented peripheral stubs, one execution per configuration, 2026-11-02. The first run used port `0x60` = `0xC0`, no disk, no MIDI, no keys, and an INT 9 tick every 4,000 instructions, for 40,000,000 instructions from `0000:0000` with the boot block's hand-off state set by hand. Expectations were written down before the runs; two of them (no writes to `0x24E4B` and the help text) were falsified, which is how those writes were found.
- Nothing here is checked on hardware.

## Open questions

- [Run-time writes and free space, on hardware](../questions/runtime-writes-and-free-space.md)
