---
id: mpc2000xl.q.tick-and-clock
title: Clock and timing on real hardware
machine: mpc2000xl
area: cpu
status: open
priority: medium
needs: ["hardware"]
summary: The CPU clock and the real system-tick period have not been measured.
related: ["mpc2000xl.abi-and-hooks"]
---

# Clock and timing on real hardware

## What is unknown

The crystal is 32 MHz; the core is assumed to run at 16 MHz. The tick is re-armed at the end of its own handler, so its period is 1 ms plus handler time; emulator estimates range from about 1.2 to 2.7 ms depending on the model and the image.

## Why it matters

Timing-sensitive additions (anything in the tick handler, audio or MIDI timing) need the real figures.

## How to answer it

Measure the timer output or toggle an LED port from the tick handler and time it with a scope or logic analyser; compare stock with a modified image.
