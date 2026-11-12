---
id: mpc3000.q.sequencer-model
title: Sequencer data model and timing
machine: mpc3000
area: sequencer
status: open
priority: high
needs: ["analysis", "emulator"]
summary: How sequences, tracks and events are stored in memory, and how the timing interrupt plays them, is not documented.
related: ["mpc3000.interrupt-vectors"]
---
# Sequencer data model and timing

## What is unknown

Unknown: the in-memory format of a sequence, track and event; where the tempo clock comes from (the CPU's timers, the external sync timer, or both); which interrupt handler advances playback; how recording inserts events; how memory is reported as the "K" figure on the System Information screen.

## Why it matters

Needed for any change to recording, quantising, swing, song mode or track handling, and to read or write sequence files.

## How to answer it

Identify the timer interrupt handler among vectors `08h-0Eh`, follow what it reads each tick, and map the structures it walks. Compare memory before and after recording a single note in the emulator.
