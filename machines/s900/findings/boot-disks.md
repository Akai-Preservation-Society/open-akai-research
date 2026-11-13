---
id: s900.boot-disks
title: Booting the S900 from floppy, and the layout of S900 boot disks
machine: s900
area: storage
firmware: ["s900-v1.2a", "s900-v1.2b", "s900-os4.0-disk", "s900-fx-2026.10.16-disk"]
status: documented
hardware_tested: no
summary: An S900 with ROM 1.2 loads a boot disk at power-on or from DISK page 01, so a replacement OS needs no ROM change. Disks are 800 KB DD. The OS 4.0 disk and S900FX both boot from a 140-byte FIXUPS file at block 4 followed by an OS file of type F.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["S900FX README for release 2026.10.16 (Mike Feedback)", "S900-OS4.img (s900fx.com, Akai-S900-OS4.zip) and S900FX-2026.10.16.img (disk images)"]
---

# Booting the S900 from floppy, and the layout of S900 boot disks

The reversible route for running other code on an S900: a floppy the
stock ROM loads into RAM.

## Claims

- **[documented]** S900FX loads automatically when its disk is in the drive at power-on. If it was not presented then, it is loaded from DISK page 01, "Clear memory and load entire disk", ENT.
- **[documented]** S900FX needs ROM OS 1.2 (any revision); its author verified 1.2A and 1.2B.
- **[open]** Whether a key held at power-on makes the S900 wait for software over MIDI, as the S950FX README states for the S950.
- **[documented]** The S900 reads only DD disks: 80 cylinders, 2 sides, 5 sectors of 1,024 bytes, 819,200 bytes raw (Greaseweazle `akai.800`). An HD disk works only with its density hole taped.
- **[documented]** On a FlashFloppy Gotek, `interface = akai-s950` works on the S900FX developer's S900; FlashFloppy's own documentation lists `interface = shugart` for the S900.
- **[static]** Disk layout as seen in both images: the same 24-byte directory entries and `0x600` block table as on the S950 ([../../s950/findings/boot-disks.md](../../s950/findings/boot-disks.md)), with file data from block 4.
- **[static]** Both the OS 4.0 disk and S900FX start with a file named `FIXUPS`, type `F`, 140 bytes, at block 4, followed by the OS file, also type `F`:
  - OS 4.0: `S900 4.0`, 45,131 bytes, from block 5;
  - S900FX: `S900FX`, 29,601 bytes, from block 5.

  The two `FIXUPS` files are not identical, and their bytes look like x86 code.
- **[hypothesis]** The ROM's power-on load runs a short type-`F` file first (`FIXUPS`), which prepares the machine before the OS file is loaded. Reason: both independent boot disks share this structure. Not traced in the ROM.
- **[open]** Where the ROM loads type-`F` files and how it starts them.

## Evidence

- Documented claims come from the S900FX README (release 2026.10.16), not checked here on a machine.
- Static claims come from the directory and table bytes of `S900-OS4.img` and `S900FX-2026.10.16.img` (hashes in [../firmware.toml](../firmware.toml)), read on 2026-11-13. The program files were not examined beyond a glance at the first bytes of `FIXUPS`.

## Open questions

- [Akai S900: the first things to establish](../questions/first-steps.md)
