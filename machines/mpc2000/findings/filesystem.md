---
id: mpc2000.filesystem
title: Disk services in OS 1.72 (INT 2Ch, INT 2Dh, the F000 workspace, 16-character names)
machine: mpc2000
area: storage
firmware: ["mpc2000-v1.72-sys", "mpc2000-v1.72-exe"]
status: documented
hardware_tested: no
summary: OS 1.72 reaches floppy and SCSI FAT volumes through INT 2Ch (BL = function, BH = drive) and SCSI sectors through INT 2Dh; state lives in segment F000. Akai's 16-character names use FAT entry bytes 12-19. From a mod source; untested here.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["vubeatz (Dariusz Chynek), mpc2000_2000xl_mod_pack at commit eb8ece6, mods/*.S (PolyForm Noncommercial 1.0.0; facts restated, no code copied)"]
depends_on: ["mpc2000.os-files"]
---

# Disk services in OS 1.72

## Claims

- **[documented]** `INT 2Ch` is the filesystem service. BL = function, BH = drive (0 = floppy, 1-8 = SCSI IDs). On return CF set = error, with AX = error code (1 = write-protected).

  | BL | Function |
  |---|---|
  | 0, 1 | Reset / mount. 1 also returns AL = `13h` for an MPC2000 partition table, `14h` for a DOS partition table, DL = partition count |
  | 2, 3, 16h | First, next, previous directory entry |
  | 4 | Open |
  | 7 | Create (CX = time, DX = date, ES:SI = name) |
  | 8, 9 | Write byte; write block (ES:SI, CX bytes) |
  | 0Ah | Close |
  | 0Eh | Find |
  | 0Fh, 10h | Motor housekeeping |
  | 11h | Media check |
  | 12h | Floppy controller completion notice |
  | 14h | Delete |
  | 17h | Select partition |
  | 18h, 19h | Floppy format set-up; low-level format |

- **[static]** LOAD's DO IT handler at EXE `0000:E98F` begins by calling `INT 2Ch` with BL = `11h` and BH = the byte at `1F31:78A8`, which fits "media check on the current drive".
- **[static]** The routine at EXE `0FE8:1A17` tests bits 6-7 of `F000:F8F4` after a floppy write.
- **[documented]** `INT 2Dh` is SCSI sector I/O: AH = 1 read, 2 write; BX:DX = LBA (high:low); CX = sector count; ES:DI = buffer; DS = `F000`. Only 512-byte sectors and two FAT copies are supported.
- **[documented]** Segment `F000` is the filesystem workspace. Floppy: `F890` write-protect, `F892` mounted (0 = OK), `F893` open-file state (2 = writing), `F89A` FAT size, `F8A2`/`F8A4` root directory start/end, `F8B4`/`F8B6` file size, `F8B8` first cluster, `F8E7` sector-size code (2 = 512), `F8E8` sectors per track, `F8F4` FDC status (`C0h` = error); DMA buffer `F000:5000`. SCSI: `F903` mounted, `F965` FAT bits (12 or 16), `F985`/`F987` partition LBA, `F995` data start, FAT12 cache at `E000`-`F800`.
- **[documented]** Names are 16 characters plus a 3-character extension. The FAT directory entry holds characters 1-8 in the usual name field, the extension at +8, and characters 9-16 in entry bytes +12 to +19, which DOS reserves. This is not VFAT.
- **[documented]** File types seen: PGM, SND, APS, ALL, and `.PRG` inside the empty-program template.
- **[documented]** File-list UI state in EXE `1F31`: current drive `78A8`, partition `78B0`, type filter `78C0`, highlighted row (0-4) `78C1`, selected name (16 + '.' + 3) `78C9`.

## Evidence

- Documented: from the vubeatz mod source, whose folder and file features call these services. Not run here.
- Static, 2026-11-13: the two EXE routines were disassembled at the offsets in [../symbols/mpc2000-v1.72-exe.csv](../symbols/mpc2000-v1.72-exe.csv) and pinned.

## Open questions

- [How OS 1.72 is loaded and where it runs](../questions/os-load-path.md)
