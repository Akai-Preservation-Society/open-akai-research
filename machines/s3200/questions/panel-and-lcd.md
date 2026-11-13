---
id: s3200.q.panel-and-lcd
title: Panel, data wheel and LCD
machine: s3200
area: panel
status: open
priority: medium
needs: ["analysis", "emulator", "hardware"]
summary: The key matrix, data wheel, LED latch and LCD driving are described only by MAME. Their handlers in OS 2.00 are not mapped.
related: ["s3200.hardware-overview", "s3200.peripherals"]
---
# Panel, data wheel and LCD

## What is unknown

Unknown: the OS routines that scan keys and the wheel (the INT 9 handler at `0x1140B` reads port `0x50`), set LEDs, and draw on the LCD (MAME: LC7981 at `0x48/0x4A` on the S3000 map). Known: MAME's key matrix and LED assignments.

## Why it matters

Adding a screen or a key action, and driving the emulator through SAVE and other screens, both need it.

## How to answer it

Follow the INT 9 handler's tables at `0x6CC2-0x6CE4`, then find the writers of the LCD ports. Confirm the key matrix against MAME's `INPUT_PORTS_START(s3000)` and on hardware.
