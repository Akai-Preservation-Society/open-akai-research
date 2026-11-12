---
id: mpc3000.rom-free-space
title: Unused space in the OS EPROMs
machine: mpc3000
area: modding
firmware: ["mpc3000-v3.08", "mpc3000-v3.11", "mpc3000-v3.12", "mpc3000-vailixi-3.50"]
status: static
hardware_tested: no
summary: Two blocks totalling 147,372 bytes of the 512 KiB image are empty and are not mapped by any of the firmware's page tables. Using them needs a page-table change; a smaller empty block inside the OS code range is directly reachable.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
depends_on: ["mpc3000.address-model", "mpc3000.eprom-layout"]
---

# Unused space in the OS EPROMs

For anyone planning an EPROM-based modification. If you only want to run
code, the floppy route in [build-a-floppy-sys.md](build-a-floppy-sys.md)
needs none of this.

## Claims

- **[static]** Two ranges of the linear image hold only `FF` in 3.08, 3.11, 3.12 and Vailixi 3.50:

  | Bank | Linear range | Bytes | In each chip file |
  |---|---|---|---|
  | Low | `0x00054-0x1FFFF` | 130,988 | `0x0002A-0x0FFFF` |
  | Page 61 | `0x74000-0x77FFF` | 16,384 | `0x3A000-0x3BFFF` |

- **[static]** In 3.11, 3.12 and Vailixi 3.50 none of the three page tables maps either bank while extended addressing is on (the tables are byte-identical in those three images). The page that would show the second bank, page 61, is pointed at the NVRAM instead. So the OS as shipped can neither execute nor read these bytes after the first mode switch.
- **[static]** It follows that code placed in a bank is unreachable until a page-table entry is changed to map it. Free bytes are not the same as usable bytes.
- **[static]** In Vailixi 3.50, an instruction-by-instruction walk of the code identified so far (2,483 far calls and jumps) found no direct transfer into either bank.
- **[static]** One byte inside the low bank matters: linear `0x0FFEF`. The EPROM's own vector for the non-maskable interrupt is `FFFF:FFFF`, which is that address. If an NMI arrived in the short window before extended addressing is switched on, the CPU would fetch there. A patch that fills the low bank should write `CF` (`IRET`) at `0x0FFEF`, or leave that byte and the one after it alone.
- **[static]** Vailixi 3.50 also has 14,392 `FF` bytes at linear `0x707C8-0x73FFF`, inside the OS code range (logical `F07C:0008` upward). This block *is* mapped while the OS runs, so code there is reachable with an ordinary far call. No identified code transfers into it.
- **[emulator]** In emulator sessions that visited the main screens of Vailixi 3.50, nothing read or executed that block.
- **[static]** In 3.08, 3.11 and 3.12 the range `0x707C8-0x73FFF` is **not** empty. Their free space inside the OS code range has not been surveyed.
- **[open]** Whether any code path reads the banks or the padding block in a way the analysis missed. Two places that could reprogram a page register are listed in the question below.
- **[open]** Whether the board's address decoding does anything outside what the firmware and the emulator map assume.

## Evidence

- The `FF` ranges were checked byte by byte in dumps of the four images on 2026-11-13, and are pinned in [../pins/](../pins/): `oar.py verify` fails if your image has anything else there.
- The page-table argument: each of the 64 words of each table was converted to its 24-bit base; a word selects ROM only when the base is below `0x100000`, and none of the resulting windows overlaps a bank (2026-09-23, on Vailixi 3.50; the tables' bytes were compared across 3.11 and 3.12 on 2026-11-13). For 3.08 only the third table was located.
- The far-transfer walk and the emulator sessions were on `mpc3000-vailixi-3.50` only.
- Nobody has burned EPROMs with code in these ranges.

## Open questions

- [Page-register writes at run time](../questions/page-register-writes-at-runtime.md)
- [PAL address decode](../questions/pal-address-decode.md)
- [A code map for the stock OS images](../questions/stock-os-code-map.md)
