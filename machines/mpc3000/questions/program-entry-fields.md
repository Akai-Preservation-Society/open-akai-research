---
id: mpc3000.q.program-entry-fields
title: Program entry fields and record size
machine: mpc3000
area: os
status: open
priority: medium
needs: ["analysis", "emulator"]
summary: The program record size (believed 77Eh), the meaning of per-note entry bytes 1-17h (including byte 6, which 3K PLUS sets with a mute group) and of record fields +11h-+3Dh and +63Eh are not established.
related: ["mpc3000.program-records-and-pad-maps", "mpc3000.3kplus-lazy-chop"]
---

# Program entry fields and record size

## What is unknown

[program-records-and-pad-maps.md](../findings/program-records-and-pad-maps.md)
establishes the name at `+00`, the 64 per-note entries at `+3Eh` (byte 0 = Sound
number) and the pad map at `+73Eh`. Unknown: the record size actually stored at
`485F:0000` at run time (`77Eh` is a hypothesis), the program count at `485F:0002`,
what entry bytes 1-17h control (tuning, envelope, levels, voice mode are likely
candidates), why 3K PLUS sets entry byte 6 to 1 together with a mute group, and the
fields at `+11h`-`+3Dh` and the four-byte entries at `+63Eh`.

## Why it matters

Code that reassigns a pad's Sound must decide which of these fields to keep or reset,
and file tools need them to read PGM files.

## How to answer it

In MAME, read `485F:0000`-`0003` after start-up. Change one parameter at a time on the
Program pages and diff the record. Cross-check with the routines that draw those
pages, starting from callers of `program_record`.
