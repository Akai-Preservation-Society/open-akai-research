---
id: mpc2000xl.build-a-patch
title: "Recipe: patch OS 1.20, flash it, and roll it back"
machine: mpc2000xl
area: modding
firmware: ["mpc2000xl-os1.20"]
status: hardware
hardware_tested: yes
summary: Step-by-step route for changing OS 1.20 - patch a copy of the image, repair its checksum, check protected regions, flash it with the stock updater and keep a stock image ready to roll back. Each step has been done on hardware.
contributors: ["open-akai-research"]
last_verified: 2026-09-30
depends_on: ["mpc2000xl.rom-and-flash", "mpc2000xl.code-space", "mpc2000xl.abi-and-hooks", "mpc2000xl.disassembler-pitfalls"]
---

# Recipe: patch OS 1.20, flash it, and roll it back

Unlike the MPC3000 floppy route, this changes the flash. It is still
recoverable: the boot block is never written, a bad image lands in the
recovery loader, and the stock image flashes back the same way.

## Claims

- **[hardware]** The steps below, with a same-length change to the VER screen's version text at file `0x30E43`, produced an image that flashed, cold-booted and showed the new text.
- **[hardware]** Larger changes built the same way (several thousand changed bytes, new code in reclaimed space) have been released and run on hardware.
- **[static]** A patch keeps the image exactly 524,288 bytes and changes only bytes below `0x78000`.
- **[hardware]** Restart cold (power off and on) after flashing. The update returns to the OS without a reboot, and code that worked warm has failed after a cold boot.

## Steps

1. **Identify the base.** `python3 tools/oar.py identify MPC2KXL.BIN` must say `mpc2000xl-os1.20`. Keep that file unchanged as your rollback image.
2. **Make the change on a copy.** Patch bytes at file offsets (see [code-space.md](code-space.md) for where not to write). For code, assemble with `CPU 186` and follow [abi-and-hooks.md](abi-and-hooks.md). Record the change as a manifest so it can be shared without the firmware:

   ```sh
   python3 tools/oar.py patch-diff MPC2KXL.BIN build/patched.bin \
       --firmware mpc2000xl-os1.20 --name my-change -o build/my-change.toml
   ```

3. **Repair the checksum and check the result:**

   ```sh
   python3 machines/mpc2000xl/tools/xlimage.py fix-checksum build/patched.bin -o build/MPC2KXL.BIN
   python3 machines/mpc2000xl/tools/xlimage.py compare MPC2KXL.BIN build/MPC2KXL.BIN
   ```

   `compare` must end with `ok`. It lists every changed range; make sure there are no others.
4. **Test in an emulator** if you can. A boot to the main screen proves little by itself: drive the changed screen with real key and pad input.
5. **Prepare media.** Put `build/MPC2KXL.BIN` at the root of a FAT floppy or SCSI volume, preferably one formatted by the MPC. Put the stock file on a second disk.
6. **Flash.** SHIFT+LOAD, choose the drive, select `MPC2KXL.BIN`, DO IT (F6), confirm. Wait for `Flash memory write 100%`. Do not power off during the write.
7. **Power off, power on,** and check the change.
8. **Roll back** by flashing the stock file the same way. If the unit shows `Insert MPC2000XL Disk !`, insert the stock disk there. Holding REC+OVERDUB at power-on forces that loader.

## Evidence

- **Hardware:** version-text patch flashed and cold-booted on 2026-07-05; stock and modified images flashed alternately with power cycles on 2026-09-30; released images v1.1-v1.3.2 (September-October 2026). All on one owner's unit.
- The `xlimage.py` rules are the boot block's own checks ([rom-and-flash.md](rom-and-flash.md)); `tests/test_xlimage.py` checks the tool against a synthetic image.

## Open questions

- [Power loss during an update](../questions/power-loss-during-update.md)
