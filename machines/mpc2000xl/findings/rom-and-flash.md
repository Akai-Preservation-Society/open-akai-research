---
id: mpc2000xl.rom-and-flash
title: The OS image, the flash update, the boot checksum and recovery
machine: mpc2000xl
area: firmware
firmware: ["mpc2000xl-os1.20"]
status: hardware
hardware_tested: yes
summary: The OS update file is the flat 512 KiB flash image. An update never writes the boot block, every cold boot checks a magic string and a word sum, and a failed image drops to a disk recovery loader rather than bricking the unit.
contributors: ["open-akai-research"]
last_verified: 2026-09-30
depends_on: ["mpc2000xl.memory-and-io-map"]
---

# The OS image, the flash update, the boot checksum and recovery

This is what makes the MPC2000XL the easiest machine here to modify: Akai's
own update path flashes whatever image you give it, and the boot block that
checks the image is never touched.

## Claims

### The image

- **[static]** Akai's update file `MPC2KXL.BIN` is byte-identical to the 524,288-byte flash image (SHA-256 `100e3375…7bab` for OS 1.20). There is no container: patching the update file is patching the OS.
- **[static]** OS 1.20 still carries the internal string `1.14c -74 Jul. 15,2004`. Identify images by hash.
- **[static]** The dword at file `0xA8` holds `0x461`, where the text `MPC2000XL` sits: this is the magic the boot block checks.
- **[static]** The checksum is a 16-bit little-endian word sum over file `0x00000-0x77FFD`, stored at `0x77FFE`. Stock 1.20's is `5ACBh`. [../tools/xlimage.py](../tools/xlimage.py) computes and repairs it.
- **[static]** The reset vector at file `0x7FFF0` is `EA 00 04 00 FC`, a far jump to `FC00:0400` (file `0x7C400`), in the boot block.
- **[static]** The boot block `0x7C000-0x7FFFF` is byte-identical in OS 1.14 and 1.20.

### What an update writes

- **[static]** The update erases file `0x00000-0x7BFFF` and programs `0x00000-0x77FFF`, the checksum word last. `0x78000-0x7BFFF` is left erased. `0x7C000-0x7FFFF`, the boot and recovery block, is never touched.
- **[static]** The updater recomputes the checksum before it flashes, so a stale checksum on the media is not by itself fatal. Repair it anyway: the boot check is what protects you if anything else goes wrong.
- **[static]** The only code path that writes the boot block is the deliberate boot-ROM reflash (`JP20 Change P-ROM ==> F-ROM`). That is the one route that can leave the unit unable to start if power fails. Never use it for a mod.
- **[hardware]** Updates are run from the LOAD screen: SHIFT+LOAD, choose the drive, select `MPC2KXL.BIN`, DO IT (F6), confirm. The screen shows `Loading:MPC2KXL.BIN`, `Flash memory block1 erase !` and `Flash memory write 100%`.
- **[hardware]** Stock 1.20 and a modified image were each flashed twice, alternately, with power cycles in between, on one unit; both came up normally each time.

### The boot check and recovery

- **[static]** On every cold boot the boot block checks the magic first and then the word sum. If either fails it does not start the OS: it falls into a loader that shows `Insert MPC2000XL Disk !` and waits for a disk holding `MPC2KXL.BIN`.
- **[hardware]** Holding REC+OVERDUB at power-on forces that recovery loader. From it, stock `MPC2KXL.BIN` loaded from SCSI ID 0 and the unit returned to normal operation.
- **[hardware]** The recovery loader did not load the file from a SCSI volume formatted on a computer; a volume formatted by the MPC worked.
- **[open]** Recovery from other SCSI IDs, other FAT layouts and the floppy drive; and the result of losing power in the middle of an update. The boot block survives by construction, so the expected outcome is the recovery loader, but this has not been tried.
- **[hypothesis]** Physical `0xF8000-0xF9FFF` (file `0x78000-0x79FFF`) is a firmware parameter-log window. It lies in the range an update erases, so an update would wipe whatever is kept there.

## Evidence

- **Static:** the image identity, magic, checksum, reset vector and boot-block identity were re-checked against the OS 1.20 and 1.14 files on 2026-11-13 and are pinned in [../pins/mpc2000xl-os1.20.csv](../pins/mpc2000xl-os1.20.csv). The update's erase and program ranges and the boot check were decoded from the updater (`0x1E962`, `0x1EAB8`) and the boot block's integrity handler (file `0x7C7BD`).
- **Hardware:** recovery chord and SCSI-0 rollback on 2026-07-21 (one unit, through a ZuluSCSI); alternating stock and modified flashes with power cycles on 2026-09-30; many further modified images flashed and benched from July to October 2026.

## Open questions

- [Power loss during an update](../questions/power-loss-during-update.md)
