---
id: mpc3000.bios-services
title: BIOS software-interrupt services (LCD text, files, program load)
machine: mpc3000
area: os
firmware: ["mpc3000-vailixi-3.50"]
status: static
hardware_tested: partial
summary: The BIOS in the top 32 KiB of the EPROM offers services through software interrupts. INT 43h writes text to the LCD, INT 41h reads files, INT 45h loads an MZ program.
contributors: ["open-akai-research"]
last_verified: 2026-09-25
sources: ["MAME devices/video/hd61830 (register numbering used for comparison)"]
depends_on: ["mpc3000.address-model", "mpc3000.interrupt-vectors"]
---

# BIOS software-interrupt services

The BIOS occupies linear `0x78000-0x7FFFF` (`F800:` and up) and stays
mapped in every page table, so these services are available to the EPROM
OS and to a program loaded from floppy alike. Addresses below are for the
Vailixi 3.50 reference image. The `INT 45h` loader is byte-identical in
3.08, 3.11 and 3.12; the other services have not been compared across
images.

## Claims

### Which interrupt is which

- **[static]** Software-interrupt vectors set up by the BIOS:

  | Interrupt | Handler | Service |
  |---|---|---|
  | `INT 10h` | `FAC0:01A4` | Load the third page table (OS code range becomes RAM) |
  | `INT 11h` | BIOS error stub | Paint `System Error ... software bug of type 11h` |
  | `INT 41h` | `F800:0364` | File services, function in `AX` |
  | `INT 43h` | `F800:16AA` | LCD services, function in `AX` |
  | `INT 45h` | `F800:0143` | Load a DOS MZ executable |
  | `INT 46h` | `F800:18D6` | Function in `AX`; not described here |

### `INT 43h`: LCD

- **[static]** `AX` selects one of eight functions through a table of near pointers at `F800:16D4`. `AX` of 8 or more does nothing.

  | `AX` | Handler | What the code does |
  |---|---|---|
  | 0 | `F800:16E4` | Initialise the LCD controller |
  | 1 | `F800:171D` | Cursor to 0, then write 320 spaces (clear the text screen) |
  | 2 | `F800:1734` | Send one command/data pair to the controller, taken from `BX` |
  | 3 | `F800:1744` | Not described here |
  | 4 | `F800:1752` | Put the character in `BL` at the cursor, handling control characters |
  | 5 | `F800:1808` | Copy the text shadow buffer |
  | 6 | `F800:181B` | Not described here |
  | 7 | `F800:1839` | Convert the cursor position to row and column |

- **[static]** `AX=4` treats `0Dh` as carriage return (column 0 of the current row), `0Ah` as line feed (next row, up to row 7) and `0Ch` as clear screen (it runs function 1). `08h` and `7Fh` have handlers of their own whose behaviour is not described here. Any other byte is written at the cursor and the cursor advances.
- **[static]** The text screen is 320 cells, 8 rows of 40 characters. The BIOS keeps a shadow copy at `0040:662B` and the cursor at `0040:68AB`, and skips the hardware write when the cell already holds that character.
- **[static]** A character reaches the controller as command `0Ch` on port `0x00E2` followed by the character on port `0x00E0`; the cursor address is sent as commands `0Ah` (low) and `0Bh` (high).
- **[hardware]** Text sent one character at a time through `INT 43h AX=4`, with `0Dh 0Ah` first, appears on the LCD of a real MPC3000.
- **[hypothesis]** Commands `0Ah`, `0Bh` and `0Ch` are "cursor address low", "cursor address high" and "write display data" of an HD61830-class controller. This matches MAME's model of the chip, not an LC7981 datasheet.
- **[open]** Graphics. The OS draws waveforms and mixer pages, so the controller is used in a graphic mode somewhere; none of that is described here.

### `INT 41h`: files

- **[static]** Functions seen in use: `AX=2` open (name at `DS:DX`, returns a handle in `AX`), `AX=3` close, `AX=4` read (`BX` handle, `CX` count, `DS:DX` buffer, returns bytes read in `CX`), `AX=9` find first, `AX=0Ah` find next. Errors come back in `AH`.
- **[static]** There is no seek in the sequences examined: the MZ loader reaches a later part of a file by reading and discarding.
- **[open]** Every other `INT 41h` function, including any that write.

### `INT 45h`: program load

- **[static]** `DS:DX` = file name (up to 20 bytes, NUL-terminated), `ES` = load segment. Returns `AX=0`, entry offset in `BX`, entry segment in `ES`, stack in `SI:DI`. Full behaviour is in [floppy-sys-loader.md](floppy-sys-loader.md).
- **[hypothesis]** A loaded program could call `INT 45h` itself to chain-load a second file. Not tried.

### Text helpers inside the BIOS (near calls, not usable from outside segment `F800`)

- **[static]** `F800:1875` prints the NUL-terminated string that follows the `CALL` instruction and returns past it. `F800:1896` prints `AL` as two hex digits. Both go through `INT 43h AX=4`.

## Evidence

- Static decoding of `mpc3000-vailixi-3.50`, following the BIOS banner from the reset path to the two port writes (2026-09-21), and the loader's use of `INT 41h` and `INT 45h` (2026-09-25). The `INT 43h` entry and its function table are pinned in [../pins/mpc3000-vailixi-3.50.csv](../pins/mpc3000-vailixi-3.50.csv).
- Hardware: the test program described in [build-a-floppy-sys.md](build-a-floppy-sys.md) uses only `INT 43h AX=4`; its text was photographed on a physical unit on 2026-10-01.
- What the LCD glass shows for functions other than `AX=4` has not been observed.

## Open questions

- [LCD controller commands and graphics](../questions/lcd-controller-commands.md)
- [What RAM the BIOS still uses after hand-off](../questions/bios-data-area.md)
- [A code map for the stock OS images](../questions/stock-os-code-map.md)
