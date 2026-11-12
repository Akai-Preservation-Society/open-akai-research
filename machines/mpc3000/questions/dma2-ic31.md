---
id: mpc3000.q.dma2-ic31
title: What is on DMA channel 2
machine: mpc3000
area: hardware
status: open
priority: low
needs: ["document", "hardware"]
summary: DMA channel 2 is wired to IC31, whose function is not identified.
related: ["mpc3000.memory-and-io-map"]
---
# What is on DMA channel 2

## What is unknown

The MAME driver's author guesses a direct audio stream. No firmware code using channel 2 has been identified here.

## Why it matters

It may matter for direct-to-disk or digital I/O features.

## How to answer it

Find OS code that programs DMA channel 2 and see what it is used with; consult the schematic.
