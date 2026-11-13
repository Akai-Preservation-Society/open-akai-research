---
id: s3200.q.peripheral-relocation
title: Peripheral relocation order and the V53 registers
machine: s3200
area: cpu
status: open
priority: medium
needs: ["document", "analysis", "emulator"]
summary: OS 2.00 writes the 0xC0xx timer and DMA ports before it writes 0xFFFC=0xC0, and the V53 register names used here are recalled, not cited.
related: ["s3200.peripherals", "s3200.address-model"]
---
# Peripheral relocation order and the V53 registers

## What is unknown

Unknown: (1) whether the V53's on-chip units are already at `0xC000` when the OS writes `0xC000-0xC036` at `0x205F7-0x2063C`, before `0xFFFC` <- `0xC0` at `0x2068B`; (2) the exact meaning of `0xFFF8-0xFFFD` and of the other system registers written in `0xFFEA-0xFFFF`; (3) the meaning of the page-register values written by the boot block.

## Why it matters

Added code that uses the timer, DMA or serial unit depends on these addresses, and an emulator built on the wrong reading would give wrong results.

## How to answer it

Cite the NEC uPD70236 (V53) user's manual: the reset values and meaning of OPSEL, OPHA, DULA, IULA, SULA, TULA and the page registers. Check whether the boot block or the reset state already sets OPHA. MAME's `v5x` CPU device can serve as a second, `documented`, source.
