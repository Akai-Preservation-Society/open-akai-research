---
id: s3200.os-load-and-save
title: Loading and saving the OS from disk, and the power-on autoload
machine: s3200
area: boot
firmware: ["s3200-v2.00"]
status: static
hardware_tested: no
summary: At power-on OS 2.00 loads a type-0x63 OS file from floppy, else hard disk partition A volume 1, if its directory version word is at least 0x0C00 (2.00). The file is the raw 256 KiB image, read to 0x50000 and copied down. No content check. Not run on hardware.
contributors: ["open-akai-research"]
last_verified: 2026-11-02
depends_on: ["s3200.address-model", "s3200.disk-formats"]
---

# Loading and saving the OS from disk, and the power-on autoload

This is the route for running a changed OS without touching the
EPROMs: a disk file the ROM OS loads into RAM. **It has not been run on
a real unit.** Read [address-model.md](address-model.md) first.

## Claims

### The OS file

- **[static]** An OS file is the raw linear image, `0x40000` bytes, file offset = logical address. Its directory entry has type `0x63`, 24-bit length `0x040000`, and a version word at entry `+0x16` (layout in [disk-formats.md](disk-formats.md)). The loader matches only the type, so the name does not matter.
- **[static]** Version encoding: high byte = major + 10, low byte = minor in hundredths, shown as `(hi-10).lo` with two digits (`0x1B3BB`). `0x0C00` is 2.00; the default written at `0x2484A` is `0x0B32` = 1.50.
- **[static]** The image carries its own version at file `0x1C` (minor) and `0x1E` (major + 10). The RAM entry copies `[0x1E]` to `[0x1D]`, making word `[0x001C]` = `0x0C00` for 2.00. The loader gates on the directory word, not on the file's `[0x1C]`.

### LOAD > OPERATING SYSTEM (`0FE9:B430`, file `0x1B2C0`)

- **[static]** Reached from the LOAD type dispatcher (type 6 at `0x1A460`) and from the autoload. It looks for a type-`0x63` file; if none is found it shows `NO SYSTEM IN THIS VOLUME` (not during autoload).
- **[static]** During autoload (`[0x7812]` bit 0) it gives up if the directory version is below the running version `[0x001C]`, or if `[0x7F60]` is 0. In any load, a version high byte below `0x0A` gives the no-system message.
- **[static]** It shows `loading OPERATING SYSTEM XX.XX`, reads the file in 32 KiB pieces to `5000:0000` upward, whole 64 KiB banks only (the high byte of the 24-bit length), then at `0x1B35C` disables interrupts, copies the `0x4E`-byte stub from `2033:386B` (file `0x23B9B`) to `8000:FF00` and jumps there.
- **[static]** The stub copies `5000-8000:0000` to `0000-3000:0000` and jumps to `0000:0050`. No checksum or content check is applied to the file. An earlier reading that `0x1B9C0` validates the staged OS was wrong: that routine checks hard-disk headers and is not on this path.
- **[static]** Because the stub is copied over the staged bytes for file `0x3FF00-0x3FF4D`, a disk-booted OS always has stub code there, whatever the file held. These bytes are zero in the stock image. Put nothing a mod needs there.
- **[static]** Under disk loading the file's boot block (`0x1FE80-0x1FFD5`) and reset vector never run. A change there does nothing from disk but does change cold boot if the same image is burned to EPROM.

### Power-on autoload (`0FE9:9EA6`, file `0x19D36`)

- **[static]** OS start shows the boot screen (`0x1B37C`, called at `0xFFB4`) and then calls `0x19D36` (at `0xFFC9`). Unless soft-restart flag `[0x0052]` bit 0 is set, it sets `[0x7812]` bit 0, chooses load type 6 (OS) and runs the load on drive `[0x6E69]` = 0 (floppy). If the drive check fails it switches to the hard disk, partition A, first volume ([disk-formats.md](disk-formats.md)).
- **[static]** The boot block sets `[0x7F60]` = 1 (`0x1FF23`). The stock image and every saved OS file hold 0 there, so an OS loaded from disk does not load itself again.
- **[static]** So a unit started with a floppy holding a type-`0x63` file of version 2.00 or later in the drive should load that OS with no key presses, and starting without that floppy returns to the ROM OS. With an empty floppy drive the hard disk is tried, so a bad OS on the hard disk comes back at every power-on until the disk is removed or a data floppy is inserted.
- **[emulator]** In the contributor's emulator, a boot with an OS floppy autoloaded it: the copier in the RAM entry rewrote all of `0x00000-0x3FFFF` and the OS restarted.

### SAVE > OPERATING SYSTEM (`0FE9:B3AC`, file `0x1B23C`)

- **[static]** Reached from the SAVE type dispatcher (type 6 at `0x1A20D`). Clears `[0x7F60]`, creates a type-`0x63` entry of length `0x040000` with the running version, shows `saving OPERATING SYSTEM XX.XX`, and writes `0000:0000` to `3000:FFFF` in 32 KiB pieces. The saved file is the live RAM copy, including the IVT and run-time variables.
- **[emulator]** Calling this routine directly in the emulator after a boot (the SAVE screens were skipped; there is no panel model) produced a file that differed from the image only inside the known write ranges ([memory-use.md](memory-use.md)) plus the SAVE path's variables `0x760A-0x760B` and `0x7620-0x7623`.

### A place to mark a build

- **[static]** The 9 bytes `OPERATING` at `0x6111` have one reader, the boot screen at `0x1B37C`, which copies exactly 9 bytes, then ` SYSTEM`, the version digits and `   N Mwords fitted`. The LOAD and SAVE messages use their own prefixes (`0x6108`, `0x60FF`). No code writes `0x6111-0x6119`. Changing these 9 bytes should change only the first word of the boot line, at cold boot and after a disk load (the image holds `[0x0052]` = 0).

## Evidence

- Static: `ndisasm -b16` of the pinned ranges `0x19D36` (90), `0xFF95` (64), `0x1B2C0` (44), `0x1B2EC` (144), `0x1B23C` (132), `0x23B9B` (78), `0x1B37C` (52), `0x1B3BB` (40), `0x6111` (9), `0x1C` (4), `0x3FF00` (78), read by the contributor 2026-10-21 and corrected 2026-10-21 (the relaunch caller) and 2026-11-02.
- Emulator: the contributor's own unpublished 8086 emulator with a hand-written floppy-controller and DMA model, 2026-11-02, one execution each for the autoload and the SAVE call.
- No floppy or hard disk written by these rules has been read by a real unit, and no real unit's SAVE OS file has been examined.

## Open questions

- [A first hardware run](../questions/first-hardware-run.md)
- [Disk images on real media](../questions/disk-images-on-hardware.md)
- [Run-time writes and free space, on hardware](../questions/runtime-writes-and-free-space.md)
