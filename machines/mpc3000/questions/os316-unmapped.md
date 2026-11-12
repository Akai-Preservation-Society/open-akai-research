---
id: mpc3000.q.os316-unmapped
title: Unmapped areas of OS 3.16
machine: mpc3000
area: os
status: open
priority: high
needs: ["analysis", "emulator"]
summary: OS 3.16's structure, start-up and 111 routines are mapped. Its sequencer, MIDI, most disk code, the Mixer and five of its eight tasks are not.
related: ["mpc3000.os316-structure", "mpc3000.os316-extending", "mpc3000.q.sequencer-model", "mpc3000.q.midi-handling"]
---

# Unmapped areas of OS 3.16

## What is unknown

[os316-structure.md](../findings/os316-structure.md) maps the file, start-up,
memory, tasks, interrupt installs, the LCD and field-editor routines, Sound
allocation and playback entry points, file I/O and part of the SCSI code.
Not mapped:

- the sequencer: sequence, track and event structures, record and quantise, Song mode beyond the page entry;
- MIDI: the parser beyond the live-in reader, sync, MIDI file and sample-dump code;
- the Mixer and effects pages;
- the save and load code for SEQ, ALL and PAR files;
- the roles of AMX tasks 1, 3, 4, 5 and 6, and what each handler at vectors `08h`-`0Eh` does;
- 3.16's own BIOS services, beyond the fact that it installs them.

## Why it matters

Route C makes 3.16 the practical base for new features. A feature in any
of these areas means mapping the area first.

## How to answer it

Most 3.16 code matches the EPROM operating systems once relocated segment
words are masked. Name a routine in an EPROM image (or in 3.16 directly)
by following its callers from a page that is already mapped, confirm what
it does in MAME, then add a row to `symbols/mpc3000-v3.16-sys.csv` with a
pin. Record the matching-byte count in the row's notes as the existing rows do.
