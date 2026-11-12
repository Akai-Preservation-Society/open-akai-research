---
id: mpc3000.q.patched-rom-os-from-ram
title: Running a patched copy of a stock EPROM OS from RAM
machine: mpc3000
area: modding
status: open
priority: high
needs: ["firmware-image", "analysis", "emulator", "hardware"]
summary: A floppy program can place a patched copy of the EPROM OS in RAM and restart it. This has been shown in the emulator for one image only; the details for the stock images are missing.
blocks: ["mpc3000.build-a-floppy-sys"]
related: ["mpc3000.floppy-sys-loader", "mpc3000.address-model"]
---
# Running a patched copy of a stock EPROM OS from RAM

## What is unknown

After the hand-off to a floppy program, the address range that held the OS code is RAM. In the demonstration, a builder on the user's computer packed the OS code and initialised data from the user's own EPROM dump, with byte patches applied, into the `.SYS` file; a stub in the file moved them into that RAM and jumped back into the boot path after the point where the data copy and page-table load normally happen. A stub that instead copies the code out of the EPROM at run time (by pointing a spare page at the ROM), so that the file would carry no firmware, has not been tried. Unknown for 3.08, 3.11 and 3.12: the exact source ranges, the stack the boot path expects, the re-entry address, and the one patch needed to stop the restarted OS from loading the `.SYS` file a second time. Unknown for every image: whether it works on a real machine.

## Why it matters

It would let an end user apply small fixes to the OS their machine already has, from a floppy, with no EPROM programmer and nothing permanent.

## How to answer it

Work on a 3.12 image. Find the boot code that copies the initialised data and loads the second page table (the vector template names the stages: slots `11h`, `12h`, `14h`). Identify the instruction in the startup-file loader that branches past the SYS step. Build the stub, confirm in the emulator that the OS pages read back as RAM while it runs and that a patched string appears, then try it on hardware. Have the stub refuse to run when the EPROM is not the image it was built for.
