---
id: s3200.disk-formats
title: Floppy and hard-disk layouts as OS 2.00 reads and writes them
machine: s3200
area: storage
firmware: ["s3200-v2.00"]
status: static
hardware_tested: no
summary: From OS 2.00's own code. Floppies use 1 KiB blocks, header and FAT at block 0, a 510-entry directory at block 5. Hard disks use 8 KiB blocks, back-to-back partitions, each with a summed header, 100-volume table and FAT. Not compared with a disk a real unit wrote.
contributors: ["open-akai-research"]
last_verified: 2026-11-02
depends_on: ["s3200.address-model"]
---

# Floppy and hard-disk layouts as OS 2.00 reads and writes them

Enough to put an OS file (type `0x63`) on a floppy or hard-disk image
that OS 2.00 should accept. Everything here comes from the firmware's
code. Akai's on-disk formats are also described outside this
repository ([../../../docs/external-resources.md](../../../docs/external-resources.md));
those descriptions were not used here.

## Claims

### Floppy

- **[static]** 80 cylinders x 2 heads, 1,024-byte sectors (commands with N=3, table at `0x5EB8`). Double density: 5 sectors per track, 800 blocks. High density: 10 sectors per track, 1,600 blocks (`0x19B20-0x19B4B`).
- **[static]** Block b is at cylinder `b / (2*spt)`, head `(b mod 2*spt) / spt`, sector `b mod spt + 1` (`0x19859`). In a raw image in cylinder/head/sector order, block b is at byte `b * 1024` (DD 819,200 bytes, HD 1,638,400).
- **[static]** Header at disk offset 0, `0x600 + 2*blocks + 0x40` bytes long (`0x1962A`): `0x000-0x5FF` 64 legacy 24-byte entries, where entry 0's type byte (offset `0x10`) = `0xFF` marks the S3000 format; `0x600` the FAT, one little-endian word per block; then `0x40` bytes: a 12-character volume label (default `NOT NAMED`), a zero word, the OS version word, and `0x30` bytes copied from `0x6D95`.
- **[static]** If offset `0x10` is `0xFF`, the mount (`0x19664`) reads 510 x 24 bytes (`0x2FD0`) of directory from block 5; otherwise it uses the 64 legacy entries. Writing a block (`0x196C4`) is refused unless the disk is in S3000 format.
- **[static]** FAT values: 0 free; `0x4000` system (format marks blocks 0-16) and also "in progress"; `0x2000` bad block. A file's chain is FAT[b] = next block, and the last block holds `0xC000` (set at close, `0x19593`). Allocation takes the first free block above the previous one (`2033:3274`).
- **[static]** Directory entry, 24 bytes: `+0x00` name (12 characters in the Akai set, table at `0x530`: digits `0x00-0x09`, space `0x0A`, A-Z `0x0B-0x24`, `#+-.` `0x25-0x28`); `+0x0C-0x0F` metadata (`+0x0F` = model byte `[0x6C5B]`; the rest not decoded); `+0x10` type (0 = free); `+0x11` 24-bit length; `+0x14` first block; `+0x16` version word.
- **[hypothesis]** `+0x14` is the first block. It fits the read path but was not traced to a write.

### Hard disk (SCSI)

- **[static]** Blocks are 8 KiB. SCSI sectors are 512 bytes (16 per block) or 1,024 (8 per block), chosen at `0x1C9EE`. LBA = (sum of earlier partitions' sizes + block) shifted by the sector-size shift (`0x1C279`). In a raw image, block b of partition p is at byte `(start(p) + b) * 8192`. Partitions follow one another; word 0 of each partition header is its size in blocks (`0x1BBCD`).
- **[static]** Partition header at the partition's block 0: `+0x000` size N; `+0x002` 0x62 words 0, `0x0D05`, `0x1A0A`, ... (each `+0x0D05`); `+0x0C6` the 32-bit sum of the 0x63 words `+0x000-+0x0C4` (low word, then high word at `+0x0C8`); `+0x0CA` volume table, 100 x 16 bytes (12-character name; flags at `+0x0C`, bit 0 = in use, bit 1 = 510-entry S3000 directory; start block at `+0x0E`); `+0x70A` the FAT, N words. Header length is `2 * (0x385 + N)` bytes (`0x1BA03`). `0x1B9C0` checks the pattern and the sum.
- **[static]** Volume directory (`0x1BA65`): S3000 type = `0x2000` bytes from the start block plus `0xFD0` bytes from the block FAT[start] points to, 510 entries; S1000 type = `0xBD0` bytes, 126 entries. Entries use the floppy layout, with blocks counted within the partition. Find (`0x1BFBC`) requires volume flag bit 0; read (`0x1BFEF`) follows the FAT one block at a time; close (`0x1C0FD`) sets bit 15 of the last link.
- **[static]** When the floppy drive is empty, the power-on autoload falls back to the hard disk with one partition (`0x19D56`) and volume entry 0 (`0xBA18`), so a boot OS must be in partition A, first volume (`0x19D8F`).
- **[open]** Which SCSI ID the OS treats as the current hard disk at power-on, and whether ZuluSCSI-style emulated disks behave like the original drives.

## Evidence

- Static: `ndisasm -b16` of the pinned ranges `0x19859` (48), `0x1962A` (109), `0x194A7` (208), `0x235A4` (41), `0x236B0` (160), `0x5EB8` (9), `0x6D95` (48), `0x530` (41), `0x1BA65` (126), `0x1C279` (71), `0x1C9EE` (52), `0x1BFBC` (75), `0x19D8F` (58), `0x1BBCD` (46), `0x1B9C0` (117), `0x1BE07` (21), by the contributor 2026-10-21. The header-sum reading was corrected that day: `+0x0C8` is the high word of the sum, not a pattern constant.
- The contributor's own unpublished tool writes and reads floppy images by these rules. Its self-tests pass, but that shows only that the tool agrees with itself. No disk formatted or written by a real unit has been compared.

## Open questions

- [Disk images on real media](../questions/disk-images-on-hardware.md)
