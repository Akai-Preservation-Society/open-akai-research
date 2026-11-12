---
id: mpc3000.q.nvram-layout
title: NVRAM layout and what a RAM program may do to it
machine: mpc3000
area: memory
status: open
priority: medium
needs: ["analysis", "hardware"]
summary: The battery-backed memory behind page 61 holds settings, but its layout, checksum and the consequences of writing it are unknown.
related: ["mpc3000.address-model", "mpc3000.floppy-sys-loader"]
---
# NVRAM layout and what a RAM program may do to it

## What is unknown

Unknown: what each byte of the NVRAM window holds, whether the OS checks it at boot and what it does when the check fails, whether the chip is the LC3517 named in the parts list, and whether a floppy-loaded program that writes there can leave the EPROM OS misconfigured after the disk is removed.

## Why it matters

The floppy route is described as leaving nothing behind. That is only true if the NVRAM is left alone, and nobody has shown what happens otherwise.

## How to answer it

Find OS code that uses the segment mapping page 61 (one consumer reads through `ES = F400`), name the fields, and find the boot-time validation. On hardware, dump the window with a floppy program before and after changing a setting.
