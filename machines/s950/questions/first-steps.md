---
id: s950.q.first-steps
title: "Akai S950: the first things to establish"
machine: s950
area: hardware
status: open
priority: high
needs: ["document", "firmware-image", "analysis"]
summary: Only documented hardware facts are recorded for this machine. This lists the foundations every later finding depends on.
---

# Akai S950: the first things to establish

## What is unknown

Progress so far: Item 1 is answered from Akai's service manual parts lists and MAME ([hardware-overview](../findings/hardware-overview.md)). Item 2: 1.0a and 1.2b are hashed against dumps, and two different "1.2a" sets exist ([rom-images](../findings/rom-images.md)). Item 5: the ROM loads a boot disk into RAM from floppy or SCSI ([boot-disks](../findings/boot-disks.md)), but how it loads and starts the files is not traced. Still unknown: the address model beyond MAME's map, the reset and boot path in the ROM, and the boot-file format.

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
