---
id: mpc2000xl.q.sample-engine
title: The L6028 sample engine
machine: mpc2000xl
area: audio
status: open
priority: high
needs: ["analysis", "emulator", "hardware", "document"]
summary: How the OS drives the L6028 DSP (voices, sample RAM transfers, recording) is not documented here.
related: ["mpc2000xl.hardware-overview", "mpc2000xl.memory-and-io-map"]
---

# The L6028 sample engine

## What is unknown

The DSP's per-voice registers are at I/O `0x80-0x8C`, it uses DMA channel 3, and sample RAM sits on its own bus. Unknown here: what each register does, how a voice starts and stops, how sample RAM is addressed and transferred, how recording and input monitoring work, and how transfers interact with sounding voices. No datasheet for the L6028 is known.

## Why it matters

Sampling, playback modes, chopping and any audio feature depend on it.

## How to answer it

Log every access to ports `0x80-0x8C` and DMA channel 3 in an emulator while playing one pad and while recording, name the routines, then confirm audibly on hardware.
