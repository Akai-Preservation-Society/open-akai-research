---
id: mpc2000xl.q.pgr5-gap
title: The PGR5 gap at cold boot
machine: mpc2000xl
area: memory
status: open
priority: low
needs: ["analysis", "hardware"]
summary: Code in the zero-filled file range 0x10036-0x104B3 works warm but freezes after a cold boot. Why is unknown.
related: ["mpc2000xl.address-model", "mpc2000xl.code-space"]
---

# The PGR5 gap at cold boot

## What is unknown

The range is 1,149 zero bytes in stock. Code there ran after a warm return from flashing and then froze or crashed at `1000:08F5` after a cold boot. How page 5 is mapped, or what writes there, during and after a cold boot is not known.

## Why it matters

It is the clearest case of 'zero bytes are not free space'; explaining it may also explain other ranges.

## How to answer it

Trace every write to logical `0x10036-0x104B3` and every page-register write that covers page 4 or 5 from reset to the main screen in an emulator with the boot block modelled.
