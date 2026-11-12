---
id: mpc3000.q.bios-data-area
title: What RAM the BIOS uses
machine: mpc3000
area: memory
status: open
priority: medium
needs: ["analysis"]
summary: A program loaded from floppy shares RAM with BIOS services it calls, but the full set of BIOS variables is not mapped.
related: ["mpc3000.bios-services", "mpc3000.floppy-sys-loader"]
---
# What RAM the BIOS uses

## What is unknown

Known BIOS data in segment `0040`: the LCD shadow at `662B`, the cursor at `68AB`, loader buffers and stack at `63EC-6DC4`. The BIOS clears `0040:0000-68AF` at boot. Unknown: every other variable the BIOS services read or write, and therefore which RAM a floppy program must leave untouched if it keeps calling `INT 41h` or `INT 43h`.

## Why it matters

A program that overwrites a BIOS variable will fail in ways that are hard to diagnose.

## How to answer it

List every `DS:`-relative access in the BIOS service handlers with `DS = 0040` and publish the table as a hardware CSV.
