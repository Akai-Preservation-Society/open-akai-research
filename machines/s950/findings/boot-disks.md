---
id: s950.boot-disks
title: Booting the S950 from floppy or SCSI, and the disk layout boot disks use
machine: s950
area: storage
firmware: ["s950-v1.0a", "s950-v1.2a", "s950-v1.2b", "s950-fx-2026.10.20-disk"]
status: documented
hardware_tested: no
summary: Every S950 ROM loads a boot disk at power-on (or from DISK page 02), from floppy or a SCSI volume, so a replacement OS needs no ROM change. DD and HD layouts are chosen from the drive's density line. Directory entries are 24 bytes and blocks 1 KiB.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["S950FX README for release 2026.10.20 (Mike Feedback)", "Akai S950 Operator's Manual (as hosted on s950fx.com), Getting started and Disk chapters", "S950FX-2026.10.20.img and S950FX-HD-2026.10.20.img (disk images)"]
---

# Booting the S950 from floppy or SCSI, and the disk layout boot disks use

This is the reversible route for running other code on an S950: a disk
the stock ROM loads into RAM. S950FX is a working example of it.

## Claims

### Loading

- **[documented]** With a disk in the drive at power-on, the S950 loads it automatically. The operator's manual says this takes around 40 seconds for a full disk.
- **[documented]** If no disk was presented at power-on, the same load is started from DISK page 02, "Clear mem & load disk", key 1.
- **[documented]** S950FX states that ROM versions 1.0A, 1.2A and 1.2B all load its disk identically.
- **[documented]** A key held at the moment of power-on makes the S950 wait for software over MIDI instead of loading the disk (S950FX README, explaining why DISK must be pressed only after switching on).
- **[documented]** A boot disk can also be loaded from a SCSI volume.
  - The S950 is SCSI ID 7.
  - The stock OS shows its disk pages only with a floppy in the drive; otherwise DISK shows `OOPS! Disk not mounted`.
  - On DISK page 01, set `SCSI #` and choose the volume with `Slct,create`, then load from page 02.
  - S950FX ships a ZuluSCSI image (`HD00_512 …`, 512-byte sectors, one volume) and reports this tested on hardware at SCSI IDs 0 and 1.

### Media

- **[documented]** DD disks hold an 800 KB Akai format: 80 cylinders, 2 sides, 5 sectors of 1,024 bytes, 819,200 bytes raw. HD disks hold 1.6 MB: 10 sectors per side, 1,638,400 bytes raw. Neither is a PC format. Greaseweazle calls them `akai.800` and `akai.1600`.
- **[documented]** The S950 picks the DD or HD layout from the drive's density signal, not from the disk contents. An HD disk with its density hole taped is read as DD and fails. A FlashFloppy Gotek needs `pin02 = dens` to serve the HD image.
- **[documented]** FlashFloppy settings: `host = akai`, `interface = akai-s950`. HxC needs an HFE built with the S900/S950 layout. Users report a single jumper on S0 for Akai samplers.
- **[documented]** Without memory expansion, a full HD disk does not fit in RAM in one pass (the S950COPY copier copies HD disks in two halves on such units).

### Layout seen in the boot-disk images

- **[static]** The directory starts at disk offset 0: 24-byte entries, each
  - `+0x00` name, 10 ASCII characters padded with spaces;
  - `+0x0A` six zero bytes;
  - `+0x10` type letter;
  - `+0x11` 24-bit little-endian length;
  - `+0x14` 16-bit start block.
- **[static]** From offset `0x600` there is one 16-bit word per 1 KiB block. A file's chain is FAT[b] = next block, and the last block has bit 15 set (`0x8000`).
- **[static]** File data starts at block 4 on the DD image and block 5 on the HD image. That is the first whole block after a 1,600-word or 3,200-word table from `0x600`.
- **[static]** S950FX's program files are type `M` with length field `0xFFFF`; its settings file `CONFIG` is type `C`, 1,000 bytes.
- **[hypothesis]** This is the stock S950 disk format rather than something specific to these images. Reason: the stock ROM loads these disks. Test: image a disk the S950 itself formatted and saved to.
- **[open]** Which directory entries the ROM's power-on load executes, where it puts them in RAM, and how it starts them.

## Evidence

- Documented claims come from the S950FX README (release 2026.10.20) and Akai's operator's manual. Neither was checked here on a machine.
- Static claims come from reading the directory and table bytes of `S950FX-2026.10.20.img` and `S950FX-HD-2026.10.20.img` (hashes in [../firmware.toml](../firmware.toml)) on 2026-11-13. The program files themselves were not examined.

## Open questions

- [Akai S950: the first things to establish](../questions/first-steps.md)
