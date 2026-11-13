---
id: s3200.q.sample-engine
title: The sample engine, filter and effects DSPs
machine: s3200
area: audio
status: open
priority: high
needs: ["analysis", "emulator", "hardware", "document"]
summary: How OS 2.00 drives the L7A1045-L6028 sample DSP, and the S3200's standard filter and effects boards, has not been studied.
related: ["s3200.hardware-overview"]
---
# The sample engine, filter and effects DSPs

## What is unknown

Unknown: the DSP register protocol at I/O `0x80-0x8F`, DMA channel 3 use, voice allocation, and the filter (IB304F) and effects (EB16, I/O `0xA0-0xA5`) programming. MAME lists the chips but treats effects writes as no-ops.

## Why it matters

Any change to sound, sampling or playback needs it.

## How to answer it

Find the OS writes to ports `0x80-0x8F` and `0xA0-0xA5` and the DMA channel 3 set-up, and record them as `static` claims. Compare with the MPC3000 and MPC2000XL sections only as a guide, re-checking every address in this image.
