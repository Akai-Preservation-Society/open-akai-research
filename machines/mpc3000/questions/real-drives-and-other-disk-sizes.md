---
id: mpc3000.q.real-drives-and-other-disk-sizes
title: Real floppy drives, and 720K / 800K disks
machine: mpc3000
area: storage
status: open
priority: low
needs: ["hardware", "emulator"]
summary: The floppy loader has run from a 1.44M image on a drive emulator. Real drives and the two smaller formats have not been tried.
related: ["mpc3000.floppy-sys-loader"]
---
# Real floppy drives, and 720K / 800K disks

## What is unknown

Unknown: behaviour with a physical 3.5-inch drive and real media, disk-change and ready-line timing, whether 720K and 800K disks load a `.SYS` file, what the BIOS does when no built-in geometry matches, and whether the controller register writes mean what they appear to (no µPD72069 datasheet was available).

## Why it matters

People with original drives need to know the route works for them.

## How to answer it

Boot the hello disk from a real drive on each EPROM OS version. In the emulator, repeat with 720K and 800K images.
