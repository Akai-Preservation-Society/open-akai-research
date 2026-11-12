---
id: mpc3000.q.disk-file-formats
title: Disk file formats (SND, PGM, APS, SEQ, ALL, PAR)
machine: mpc3000
area: file-format
status: open
priority: medium
needs: ["analysis", "document"]
summary: The byte layout of the files the MPC3000 saves and loads is not documented here.
---
# Disk file formats (SND, PGM, APS, SEQ, ALL, PAR)

## What is unknown

Unknown here: the header and body layout of sound (`.SND`), program (`.PGM`), all-programs-and-sounds (`.APS`), sequence (`.SEQ`), all-sequences (`.ALL`) and parameter (`.PAR`) files, how 16-character names are stored in FAT directory entries (the BIOS compares eight extra name bytes at entry offset `0Ch`), and which fields changed between OS versions.

## Why it matters

Tools on a computer cannot create or convert files for the machine without it, and OS changes that add stored settings must not break existing files.

## How to answer it

Save small known objects from the emulator and diff the files; cross-check with the load and save routines once they are named. Descriptions published by other projects can be cited as `documented` and then confirmed. File-format documents that apply to several machines belong in the top-level `formats/` folder.
