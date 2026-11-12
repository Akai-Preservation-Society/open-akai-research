---
id: mpc3000.q.sample-engine-dsp
title: Sample engine and DSP registers
machine: mpc3000
area: audio
status: open
priority: high
needs: ["analysis", "emulator", "hardware", "document"]
summary: How the OS drives the L7A1045 sample DSP (voice allocation, register writes, sample memory layout, recording) is not documented.
related: ["mpc3000.hardware-overview"]
---
# Sample engine and DSP registers

## What is unknown

The DSP is at I/O ports `0x0060-0x006F` and uses DMA channel 3. No manufacturer datasheet is known. Unknown here: the meaning of each register, how a voice is started and stopped, how sample memory is addressed and allocated, how sampling (recording) works, and the mixer and effects paths.

## Why it matters

Almost every feature people ask for (chopping, new playback modes, monitoring, time-stretch) touches the sample engine.

## How to answer it

Start from the MAME device `l7a1045_l6028_dsp_a.cpp`, which records what its author worked out. Trace the OS's writes to ports `0x60-0x6F` in the emulator while playing one pad, and name the routines that make them. Check audible results on hardware.
