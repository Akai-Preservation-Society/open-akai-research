---
id: mpc3000.q.icu-ports-c010-c011
title: Ports C010h and C011h
machine: mpc3000
area: cpu
status: open
priority: medium
needs: ["document", "analysis"]
summary: The BIOS writes ports C010h and C011h around interrupts. They are believed to be the on-chip interrupt controller, but this has not been confirmed.
related: ["mpc3000.interrupt-vectors", "mpc3000.address-model"]
---
# Ports C010h and C011h

## What is unknown

The boot code relocates the V53's on-chip units into I/O `0xC0xx`. The BIOS writes `FFh` and `F6h` to `C011h` and `60h` to `C010h`. Unknown: which unit each port belongs to, what the values mean (mask register? specific end-of-interrupt?), which vector base the interrupt controller is programmed with, and so which vector each hardware interrupt line uses.

## Why it matters

Until this is settled, the link between a hardware interrupt line and its handler is a guess, and a replacement program cannot enable interrupts safely.

## How to answer it

Read the relocation registers' definitions in the NEC V53 user's manual, compute where each unit lands for the values the boot code writes, and decode the initialisation writes to the interrupt controller.
