---
id: mpc2000xl.q.midi-input
title: MIDI input and sync
machine: mpc2000xl
area: midi
status: open
priority: medium
needs: ["analysis", "emulator"]
summary: MIDI output is documented. The MIDI input path, parser, sync handling and the exact baud clock are not.
related: ["mpc2000xl.midi-output"]
---

# MIDI input and sync

## What is unknown

Both MIDI inputs and the panel link share interrupt input 4. Unknown: how the handler separates them, the input rings and parser, clock and MTC sync, and the oscillator behind the MIDI baud rate.

## Why it matters

MIDI-controlled features and sync fixes need it.

## How to answer it

Follow the vector-24h handler past the panel path; feed single MIDI bytes in an emulator and watch which RAM changes.
