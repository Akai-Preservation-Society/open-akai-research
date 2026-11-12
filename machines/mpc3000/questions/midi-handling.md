---
id: mpc3000.q.midi-handling
title: MIDI handling
machine: mpc3000
area: midi
status: open
priority: medium
needs: ["analysis", "emulator"]
summary: Where MIDI bytes are received, parsed and sent inside the OS is not documented.
related: ["mpc3000.interrupt-vectors", "mpc3000.memory-and-io-map"]
---
# MIDI handling

## What is unknown

The UART is at ports `0x00C0-0x00DF` with transmit-ready on IRQ4 and receive on IRQ5 and IRQ7. Unknown: the receive and transmit buffers, the parser, how MIDI and panel bytes are separated on the shared receivers, sync (clock, MTC, SMPTE) handling, and the sample-dump code.

## Why it matters

Needed for any MIDI feature and for using MIDI as a debugging or screen-mirroring channel.

## How to answer it

Find the handlers behind the UART interrupts (see `findings/interrupt-vectors.md`), then follow the buffers they fill. In the emulator, send single MIDI bytes and watch which RAM changes.
