---
id: s3200.hardware-overview
title: S3200 hardware overview, and why the board type is in doubt
machine: s3200
area: hardware
firmware: ["hardware"]
status: documented
hardware_tested: no
summary: Chips, buses and options of the S3000 family from MAME's driver. MAME says the S3200 uses the XL board, but the only OS image studied here is the S3000-board 256 KiB pair. Read this before assuming any map applies to an S3200.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["MAME src/mame/akai/s3000.cpp at commit c2caa8969adb (2026-11-13), driver flagged MACHINE_NOT_WORKING"]
---

# S3200 hardware overview, and why the board type is in doubt

What the S3000-family boards contain, as MAME describes them, and the
one conflict that decides whether the rest of this folder applies to a
given S3200.

## Claims

- **[documented]** MAME's `s3000.cpp` covers the S2000, S2800, S3000, CD3000i, S3200, S3000XL, S3200XL and CD3000XL. It says they are built on variants of the MPC3000 hardware without the panel sub-CPU.
- **[documented]** MAME's header says: "the S2000 and S3200 are based on the XL hardware, not the base S3000/CD3000i hardware." MAME defines machines `s2000`, `s3000`, `cd3000i`, `s3000xl` and `cd3000xl`, but no `s3200`.
- **[documented]** Common to all: NEC V53A at 32 MHz crystal (CLKOUT 16 MHz), uPD72069 floppy controller, MB89352 SCSI controller, L7A1045-L6028 sample DSP, LC7981 graphic LCD (HD61830-compatible, 240 x 64) on the 3x00 and S2800, 8255-class key/LED chip (KLCS), MIDI on the V53's own serial unit.
- **[documented]** The IB304F filter board (L7A0906-L6029, second filter and envelope) and the EB16 effects board (L7A1414-L6038) are optional on other models and fitted as standard on the S3200.
- **[documented]** Two board maps differ. S3000/CD3000i: RAM 0x000000-0x0BFFFF, ROM 0x0C0000-0x0FFFFF (256 KiB), switched to RAM by port 0x68 bit 4; LCD at I/O 0x48/0x4A; memory-ID port at 0x60-0x67. XL: ROM 0x080000-0x0FFFFF (512 KiB), RAM 0x000000-0x07FFFF and 0x180000-0x1FFFFF; LCD at I/O 0x60/0x62; an extra 8255 (WADCS) at 0xC0. Both are in [../hardware/memory-map.csv](../hardware/memory-map.csv) and [../hardware/io-ports.csv](../hardware/io-ports.csv), each row naming its map.
- **[documented]** Interrupt lines in MAME: IRQ0 serial receive, IRQ1 timer 0, IRQ2 SCSI, IRQ3 floppy, IRQ4 serial transmit ready. DMA: channel 0 SCSI, 1 floppy, 3 sample DSP.
- **[documented]** Stock wave memory is 2 MiB. MAME says the S3000 recognises at most 8 MiW (16 MiB), and that its sizing routine accepts 32 MiB SIMMs that its memory test cannot handle.
- **[documented]** MAME gives a wave-memory test for the S3000 family: after boot, press MARK and NAME together, release, then press "+ / <".
- **[static]** The s3200-v2.00 image is 262,144 bytes and its reset vector expects it at physical 0xC0000-0xFFFFF, the S3000 map ([address-model.md](address-model.md)). It would not sit at the XL map's 0x80000 reset window as built. So either the S3200 is not the XL board, or an S3200 runs a different OS than this image.
- **[open]** Which board an S3200 really has, and which OS images it accepts. See [../questions/s3200-hardware-and-os.md](../questions/s3200-hardware-and-os.md).

## Evidence

- Every `documented` claim is read from MAME `src/mame/akai/s3000.cpp` at commit `c2caa8969adb`, fetched 2026-11-13. The driver is flagged not working; its author marks some details as guesses (for example port 0x68 bits 5-7 "unknown").
- The `static` claim uses the image size from [../firmware.toml](../firmware.toml) and the reset vector pinned at `0x3FFF0`.
- Nothing here was checked on an S3200 board, a photo of one, or a service manual.

## Open questions

- [Is the S3200 an XL board, and does it run this image?](../questions/s3200-hardware-and-os.md)
- [The sample engine, filter and effects DSPs](../questions/sample-engine.md)
- [Panel, data wheel and LCD](../questions/panel-and-lcd.md)
