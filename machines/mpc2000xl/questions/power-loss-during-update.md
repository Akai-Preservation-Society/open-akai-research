---
id: mpc2000xl.q.power-loss-during-update
title: Power loss during an OS update
machine: mpc2000xl
area: firmware
status: open
priority: medium
needs: ["hardware"]
summary: What a unit does when power fails in the middle of a routine OS update has not been tried.
related: ["mpc2000xl.rom-and-flash"]
---

# Power loss during an OS update

## What is unknown

The update never writes the boot block, so the boot checks should fail and the recovery loader should appear. Not tested; nor is recovery from the floppy drive, from SCSI IDs other than 0, or from a volume formatted by a computer (one attempt failed).

## Why it matters

It decides how much risk a user takes each time they flash.

## How to answer it

On a unit you are prepared to recover, cut power during `Flash memory write`, then power on and restore stock from the recovery loader. Repeat the recovery from floppy and from another SCSI ID.
