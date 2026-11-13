---
id: s3200.q.disk-images-on-hardware
title: Disk images on real media
machine: s3200
area: storage
status: open
priority: high
needs: ["hardware"]
summary: The floppy and hard-disk layouts come from the firmware only. Nobody has compared them with a disk a real unit formatted or saved to.
blocks: ["s3200.os-load-and-save"]
related: ["s3200.disk-formats"]
---
# Disk images on real media

## What is unknown

Unknown: whether disks formatted and written by a real unit match [../findings/disk-formats.md](../findings/disk-formats.md). In particular the legacy-entry contents, the label trailer, directory entry bytes `+0x0C-0x0E`, and whether a hard-disk image on an SD-card SCSI emulator is seen as the current hard disk at power-on.

## Why it matters

A host tool that writes OS files must match what the unit reads. A wrong trailer or entry field could make the unit refuse the disk or, worse, write to it.

## How to answer it

1. Format a floppy on the unit and image it sector by sector (for example with a flux-level reader set to 1,024-byte sectors). Check offset `0x10` = `0xFF`, FAT words `0x4000` for blocks 0-16, and the trailer at `0x600 + 2*blocks`.
2. SAVE > OPERATING SYSTEM to that floppy, image it again, and record the type-`0x63` entry in full.
3. Repeat on a hard-disk image: format, create volume 1 in partition A, save the OS, and check the header sum, volume table and FAT against the finding.
