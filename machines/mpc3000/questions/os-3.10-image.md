---
id: mpc3000.q.os-3.10-image
title: OS 3.10 has not been examined
machine: mpc3000
area: firmware
status: open
priority: low
needs: ["firmware-image", "analysis"]
summary: OS 3.10 is listed in the MAME ROM set but no contributor has had the image, so no finding applies to it.
related: ["mpc3000.eprom-layout", "mpc3000.floppy-sys-loader"]
---
# OS 3.10 has not been examined

## What is unknown

Unknown: everything, including which load segment its floppy loader uses and whether its layout follows 3.08 or 3.11.

## Why it matters

A user with 3.10 EPROMs currently has no verified addresses at all.

## How to answer it

With a dump, run `oar.py identify`, then check each pin of the 3.11 set at the same offsets and locate the loader by its strings.
