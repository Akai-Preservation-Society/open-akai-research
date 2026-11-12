---
id: mpc3000.q.stock-os-code-map
title: A code map for the stock OS images (3.08, 3.11, 3.12)
machine: mpc3000
area: os
status: open
priority: high
needs: ["firmware-image", "analysis"]
summary: Most code-level findings were established on the Vailixi 3.50 reference image. The same facts are needed for the Akai images most machines carry.
related: ["mpc3000.interrupt-vectors", "mpc3000.calling-conventions", "mpc3000.bios-services", "mpc3000.rom-free-space"]
---
# A code map for the stock OS images (3.08, 3.11, 3.12)

## What is unknown

For 3.08, 3.11 and 3.12 this repository knows the boot path, the floppy loader, the MZ loader and the page tables. It does not have, for those images:

- the interrupt vector table after boot and who installs each vector;
- confirmation of the calling conventions routine by routine;
- the BIOS service entry points other than `INT 45h`;
- any named OS routine beyond the startup loader;
- a survey of unused space inside the OS code range.

## Why it matters

Most MPC3000s run 3.11 or 3.12. An agent asked to change behaviour on such a machine has almost no named addresses to work from, and must not borrow them from another image.

## How to answer it

Repeat the analyses in `findings/interrupt-vectors.md`, `findings/calling-conventions.md` and `findings/bios-services.md` on a 3.12 image first, following control flow from the reset vector. Record each routine in `symbols/mpc3000-v3.12.csv` with a pin. Routines that are byte-identical to the 3.50 image can be found quickly by hashing the 3.50 pin ranges at nearby offsets.
