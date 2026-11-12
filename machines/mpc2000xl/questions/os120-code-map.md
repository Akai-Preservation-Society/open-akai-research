---
id: mpc2000xl.q.os120-code-map
title: A map of the OS 1.20 code
machine: mpc2000xl
area: os
status: open
priority: high
needs: ["analysis", "emulator"]
summary: About 50 routines and data objects are named here. Most of OS 1.20 (screens, sequencer, sampler, disk) has no published names.
related: ["mpc2000xl.abi-and-hooks", "mpc2000xl.code-space"]
---

# A map of the OS 1.20 code

## What is unknown

The symbol table holds the boot path, panel input, LEDs, MIDI output, the tick, remapping and file dispatchers. Unknown here: the screen and mode dispatch, the Program and Sound workspaces, sampling, the sequencer, disk I/O beyond the file dispatchers, and which ranges of the image are never executed.

## Why it matters

Every feature request beyond panel, LED and MIDI behaviour needs named hook points.

## How to answer it

Anchor on a visible string, find the code that references it, follow it to its screen program and handlers, confirm in an emulator, then add rows to `symbols/mpc2000xl-os1.20.csv` with pins. Record ranges proven never to run as findings in `code-space.md`.
