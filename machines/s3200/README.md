# Akai S3200

Entry point for the S3200 rack sampler. One-line facts are in
[machine.toml](machine.toml), known firmware images in
[firmware.toml](firmware.toml). All code-level findings are for one
image, **`s3200-v2.00`**: the OS 2.00 EPROM pair labelled "S3000/S3200",
which is byte-identical to MAME's `s3000` "ver 2.0" set.

**Read this first.** MAME's driver says the S3200 is built on the XL
board (512 KiB ROM at `0x80000`). This image is the S3000 board's 256 KiB
pair at `0xC0000` and contains no "S3200" string. Whether an S3200 runs
it is **not established**: see
[questions/s3200-hardware-and-os.md](questions/s3200-hardware-and-os.md).
Hash your own chips before using anything here
(`python3 tools/oar.py identify LOW HIGH`).

**Nothing in this folder has been run on a real unit.** Claims are
`static` (read from the bytes, pinned by hash), `emulator` (the
contributor's own unpublished emulator with invented peripherals), or
`documented` (MAME's driver source).

## What you can do today

| You want to | State | Read |
|---|---|---|
| Identify your OS chips | Hashes recorded, MAME match | [findings/eprom-layout.md](findings/eprom-layout.md) |
| Run a changed OS without burning EPROMs | Disk-load route mapped statically, not run on hardware | [findings/os-load-and-save.md](findings/os-load-and-save.md) |
| Write an OS file onto a floppy or hard-disk image | Layout read from the firmware | [findings/disk-formats.md](findings/disk-formats.md) |
| Know where code and data are | Segments and extents mapped | [findings/code-structure.md](findings/code-structure.md) |
| Use the timer, serial/MIDI or interrupts | Set-up mapped; relocation order open | [findings/peripherals.md](findings/peripherals.md) |

## What you cannot do yet from this repository

| You want to | Missing | Question |
|---|---|---|
| Trust any of this on an S3200 | Which board and OS the S3200 has | [s3200-hardware-and-os](questions/s3200-hardware-and-os.md) |
| Rely on the disk-load route | A first hardware run | [first-hardware-run](questions/first-hardware-run.md), [disk-images-on-hardware](questions/disk-images-on-hardware.md) |
| Place added code in the image | A range shown free on hardware | [runtime-writes-and-free-space](questions/runtime-writes-and-free-space.md) |
| Change sound, sampling, filters or effects | The DSP protocols | [sample-engine](questions/sample-engine.md) |
| Add a screen or a key action | Panel and LCD routines | [panel-and-lcd](questions/panel-and-lcd.md) |

The full list is in [../../GAPS.md](../../GAPS.md).

## Reading order

1. [findings/hardware-overview.md](findings/hardware-overview.md). Tables in [hardware/](hardware/); each row names the board map it belongs to.
2. [findings/eprom-layout.md](findings/eprom-layout.md): the image and how to identify it.
3. [findings/address-model.md](findings/address-model.md): **required** before using any address. Different from the MPC3000's and the MPC2000XL's.
4. [findings/code-structure.md](findings/code-structure.md) and [findings/memory-use.md](findings/memory-use.md): **required** before placing code.
5. [findings/os-load-and-save.md](findings/os-load-and-save.md) and [findings/disk-formats.md](findings/disk-formats.md).
6. As needed: [findings/peripherals.md](findings/peripherals.md), [findings/rom-serial-loader.md](findings/rom-serial-loader.md).

## Firmware images

| Id | What | Examined here |
|---|---|---|
| `s3200-v2.00` | OS 2.00 EPROM pair (LOW 9C79, HIGH 2900), MAME `s3000` ver 2.0 | All code-level findings |

MAME also lists S3000 OS 1.50, CD3000i 1.60 and 2.00, and XL-board
images. None has been examined here, and none is assumed to share an
address with `s3200-v2.00`.

## Tools

- [symbols/](symbols/) and [pins/](pins/): named addresses and byte-range hashes. `python3 tools/oar.py verify s3200-v2.00 linear.bin`.
- The contributor's emulator, disassembler scripts and floppy-image tool are not published, so `emulator` claims cannot yet be repeated by others.

## Emulation

MAME's `s3000` driver is flagged not working. No run of it is recorded
here. Results tagged `emulator` come from a private 8086 emulator that
starts at the RAM entry with invented peripheral responses.

## Outside this repository

Manuals, emulators and disk tools for the S3000 family are listed in
[../../docs/external-resources.md](../../docs/external-resources.md).
