---
id: mpc2000xl.q.sequence-format
title: Sequence files and event format
machine: mpc2000xl
area: file-format
status: open
priority: medium
needs: ["analysis", "hardware"]
summary: The .ALL container framing is known. The standalone .SEQ file, the event records and the song format are not documented here.
related: ["mpc2000xl.file-formats"]
---

# Sequence files and event format

## What is unknown

Known: the `.ALL` prefix, its 99-entry directory and how sequence images are appended. Unknown: the `.SEQ` envelope, the in-sequence event and track records, song data and the `.PAR` file.

## Why it matters

Tools that read or write sequences on a computer, and sequencer features, need it.

## How to answer it

Save small known sequences from the machine (one note, one track, a tempo change), diff the files, and confirm against the loader and writer code.
