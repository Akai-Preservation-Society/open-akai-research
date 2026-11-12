---
id: mpc3000.q.page-register-writes-at-runtime
title: Page-register writes at run time
machine: mpc3000
area: cpu
status: open
priority: low
needs: ["analysis", "emulator"]
summary: Two places in the OS can write an I/O port taken from a table and might therefore change a page register while the OS runs.
related: ["mpc3000.address-model", "mpc3000.rom-free-space"]
---
# Page-register writes at run time

## What is unknown

In the Vailixi 3.50 reference image, `DC5B:00BA` writes a byte to a port number read from a table indexed by a caller's value, and `D5DD:0163` writes to a port after a kernel call that changes the port register. Neither has been shown to stay outside `0xFF00-0xFF7E` on every path.

## Why it matters

If the OS remaps pages at run time, the claim that the empty EPROM ranges are never visible would need revisiting.

## How to answer it

Enumerate the callers and the table contents for each site. In the emulator, log all writes to `0xFF00-0xFF7E` across a long session.
