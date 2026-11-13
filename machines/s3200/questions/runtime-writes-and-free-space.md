---
id: s3200.q.runtime-writes-and-free-space
title: Run-time writes and free space, on hardware
machine: s3200
area: memory
status: open
priority: high
needs: ["hardware", "emulator", "analysis"]
summary: Which bytes of the OS image are never written at run time is known only from emulator runs with invented peripherals. No range is established as free for added code.
related: ["s3200.memory-use", "s3200.code-structure"]
---
# Run-time writes and free space, on hardware

## What is unknown

Unknown: writes during SAVE through its real screens, sampling, editing, other screens and hard-disk use; and the targets of the seven indirect sites with no known target ([../findings/code-structure.md](../findings/code-structure.md)). Known: the write maps in [../findings/memory-use.md](../findings/memory-use.md).

## Why it matters

Added code needs space the OS never writes. The zero areas are already known to be buffers, so space must be found by evidence, not by looking for zeros.

## How to answer it

1. On a unit: boot with no floppy, wait for PROGRAMS IN MEMORY, insert a blank floppy and SAVE > OPERATING SYSTEM. The saved file is the live RAM copy. Compare it with the image: no byte in `0xFE90-0x1FE7F` should differ, and in `0x20330-0x2DF2F` only `0x24E4B-0x24E4D` and `0x2A961-0x2A963`. Repeat after MIDI SysEx traffic and after loading a program.
2. Add a panel model to an emulator (the INT 9 handler polls port `0x50`) so that screens can be driven, and resolve the UI field records behind `0x110C1`, `0x11100` and `0x106FA`.
