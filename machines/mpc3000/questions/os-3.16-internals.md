---
id: mpc3000.q.os-3.16-internals
title: OS 3.16 internals
machine: mpc3000
area: os
status: open
priority: high
needs: ["analysis", "emulator"]
summary: OS 3.16 is a floppy-loaded MZ program and the natural base for floppy-delivered features, but nothing about its inside is documented here.
related: ["mpc3000.build-a-floppy-sys", "mpc3000.floppy-sys-loader"]
---
# OS 3.16 internals

## What is unknown

`M3K316.SYS` is identified by hash in `firmware.toml`. Unknown here: its segment layout and relocation table, where each OS routine sits compared with the EPROM images, where unused space is, how it differs from 3.12, and how to add code to it and still produce a file the ROM loader accepts.

## Why it matters

Features have been added to 3.16 and run on real hardware, so the route works. Without a published map every developer has to rediscover the image. This is the most valuable single contribution for people who want new features without burning EPROMs.

## How to answer it

Parse the MZ header and relocation table; find the OS entry and the copy of the startup path; match routines against the EPROM images by byte signature; publish the results as findings keyed to `mpc3000-v3.16-sys` with file offsets into the `.SYS` file, a symbol table and pins. Verify changes in the emulator by loading the modified file from a floppy image.
