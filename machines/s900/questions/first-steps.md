---
id: s900.q.first-steps
title: "Akai S900: the first things to establish"
machine: s900
area: hardware
status: open
priority: high
needs: ["document", "firmware-image", "analysis"]
summary: Only documented hardware facts are recorded for this machine. This lists the foundations every later finding depends on.
---

# Akai S900: the first things to establish

## What is unknown

Progress so far: Items 1 to 3 are partly answered from MAME's driver source (`documented`, not checked against a machine). Item 5 looks promising: OS 2.0 and 4.0 were distributed as boot floppies and MAME models a ROM-unmap bit, but the floppy boot format is undocumented. Still unknown: whole-image SHA-256 hashes, the reset and boot path, and the disk OS format.

In the order it is needed:

1. **The hardware.** Main CPU, any secondary processors, RAM, how the firmware is stored (EPROM, flash, disk-loaded), display, storage and audio chips. Source: the service manual parts list and board photos.
2. **Firmware images.** Each OS version that exists, how it is packaged (one chip, an even/odd pair, a file on disk), and its hashes, recorded in `firmware.toml`.
3. **The address model.** How a position in the firmware image relates to an address the CPU uses, and where RAM and I/O are.
4. **The reset and boot path.** From the reset vector to the operating system's main loop.
5. **A way to run your own code** that can be undone: does the machine load an OS or program from disk into RAM?

## Why it matters

No address can be used safely before items 2 and 3 exist, and no change can be tested safely before item 5.

## How to answer it

Follow the shape of the MPC3000 section: `hardware-overview`, `memory-and-io-map`, `eprom-layout`, `address-model`, then the boot path. Start with what a service manual and a firmware dump give you without running anything. If an emulator driver exists for this machine (MAME has drivers for some Akai instruments), its source is a `documented` source for the memory map.
