---
id: s3200.peripherals
title: Peripheral set-up in OS 2.00 (V53 units, interrupts, serial/MIDI, memory ID)
machine: s3200
area: cpu
firmware: ["s3200-v2.00"]
status: static
hardware_tested: no
summary: OS 2.00 uses the V53's on-chip units at I/O 0xC000-0xC03F (interrupt controller 0xC010, serial 0xC020, timer 0xC030), with INT 8 serial receive, INT 9 tick and INT 11 floppy. MAME puts MIDI on that serial unit. The SIMM-ID probe at 0x20F08 matches MAME's table.
contributors: ["open-akai-research"]
last_verified: 2026-11-13
sources: ["MAME src/mame/akai/s3000.cpp at commit c2caa8969adb"]
depends_on: ["s3200.address-model"]
---

# Peripheral set-up in OS 2.00 (V53 units, interrupts, serial/MIDI, memory ID)

What the OS does to the CPU's own peripherals and to the board's
configuration port. Port tables: [../hardware/io-ports.csv](../hardware/io-ports.csv)
and [../hardware/interrupts.csv](../hardware/interrupts.csv).

## Claims

### System registers and the 0xC000 block

- **[static]** In one straight-line sequence at file `0x205F7-0x206A8` (`2033:02C7` onward), the OS writes ports `0xC000`, `0xC001`, `0xC006`, `0xC008`, then the timer block `0xC030-0xC036`, then V53 system registers in `0xFFEA-0xFFFF`. Among these are `0xFFFD` <- `0x0F` (at `0x20649`), then `0xFFFC` <- `0xC0`, `0xFFFB` <- `0x00`, `0xFFFA` <- `0x10`, `0xFFF8` <- `0x20`, `0xFFF9` <- `0x30` (at `0x2068B-0x206A8`). Then it programs `0xC010`/`0xC012`.
- **[hypothesis]** `0xFFFD`, `0xFFFC`, `0xFFFB`, `0xFFFA`, `0xFFF8` and `0xFFF9` are the V53's OPSEL, OPHA, DULA, IULA, SULA and TULA registers. If so, the writes enable all four on-chip units and place DMA at `0xC000`, the interrupt controller at `0xC010`, the serial unit at `0xC020` and the timer at `0xC030`. The register names are recalled from the V53 datasheet, which is not cited here. The firmware's own use of these ports (next claims) is consistent with this reading.
- **[open]** The timer and DMA ports at `0xC0xx` are written *before* `0xFFFC` <- `0xC0`. Either the units already sit at `0xC000` after reset or after the boot block, or those first writes go somewhere else. Not established; see [../questions/peripheral-relocation.md](../questions/peripheral-relocation.md).
- **[static]** Interrupt controller: `0xC010` <- `0x13`, then `0xC012` <- `0x08`, `0x03` (8259-style ICW1, ICW2 = vector base 8, ICW4) at `0x206AA`. Further writes follow (`0xC010` <- `0x2B`, `0xC012` <- `0xCC`, `0xF4`).
- **[static]** Timer: `0xC036` <- `0x24`, `0x56`, `0xA4` (8254-style control words), then counter 1 (`0xC032`) <- 2, counter 2 (`0xC034`) <- 0, counter 0 (`0xC030`) <- 2, at `0x2061E`.

### Interrupts

- **[static]** The image IVT gives: INT 8 = `0FE9:15DC` (file `0x1146C`), INT 9 = `0FE9:157B` (file `0x1140B`), INT 11 = `0000:7640` (file `0x7640`). INT 1-6, 10 and 12-14 point at `2033:0B10`, INT 15 at `2033:0B11`, and INT 7 holds `000C:0000`. INT 0 is installed at run time as `2033:0AE3`.
- **[documented]** MAME wires IRQ0 to the serial receive interrupt, IRQ1 to timer 0, IRQ2 to SCSI, IRQ3 to the floppy controller and IRQ4 to serial transmit-ready. With vector base 8 these are INT 8, 9, 10, 11 and 12.
- **[static]** The INT 9 handler reads port `0x50` (the KLCS key port in MAME's map) on each call, which fits a timer-driven key scan.
- **[static]** The INT 11 handler is 7 bytes inside DGROUP at `0x7640`: it sets bit 5 of `[CS:75B0]` and returns. The floppy driver waits for that bit after recalibrate, seek and read (loop at `0x19A73`) and clears it after the result phase (`0x19BE1`). Together with MAME's IRQ3 this makes INT 11 the floppy-controller interrupt.
- **[emulator]** In the contributor's emulator, no floppy command after a recalibrate completed until INT 11 was delivered; with it, a floppy mount read the header and directory.

### Serial unit and MIDI

- **[static]** Serial set-up at `0x113E0` (`0FE9:1550`): `0xC024` <- `0x4E` (8251-style mode: x16 clock, 8 data bits, 1 stop bit), `0xC022` <- `0x35` (transmit and receive enable, error reset, RTS), `0xC026` <- `0x02`, then a dummy read of `0xC020`.
- **[static]** The INT 8 handler at `0x1146C` reads status `0xC022`, then data `0xC020`, and stores the byte in a ring at `0x200-0x2FF` (pointer `[0x6C90]`, 8-bit wrap). The transmit helper at `0x2070C` (`2033:03DC`) waits for `0xC022` bit 0 and writes AH to `0xC020`.
- **[documented]** MAME connects MIDI IN to the V53's receive pin and MIDI OUT to its transmit pin. So MIDI is this serial unit.
- **[emulator]** Bytes delivered as `0xC022` bit 1 + `0xC020` + INT 8 landed in the ring. After the input `F0 47 00 02 48 F7` the OS sent `F0 47 00 03 48 01 00`, 12 name bytes in the Akai character set, and `F7`.
- **[hypothesis]** That exchange is a program-list request and reply in Akai's S1000 SysEx numbering. The numbering is recalled, not taken from a cited document.

### Memory ID and configuration port

- **[documented]** MAME: ports `0x60-0x67` on the S3000 read a 74HC245 (IC16): bits 0-3 a SIMM ID code from the wave-memory board, bits 4-5 footswitches, bits 6-7 ID jumpers. MAME describes the OS 2.00 RAM-detection routine "at PC=0x20ed9": write 0, read back, write a timer-derived value AND 7, read back, and compare against a 9-byte-stride table. It lists SIMM codes for 2, 8 and 32 MiB DRAM and SRAM, and "no SIMM".
- **[static]** The bytes agree. The loop at `0x20F08` (`2033:0BD8`) writes each of ports `0x60`, `0x62`, `0x64`, `0x66` (DX from `0x60`, step 2, CX=4) with 0, reads back the low 4 bits, compares them with a table at `DS:7F70`, writes a non-zero value from `2033:1014` AND 7, multiplies by 9 and compares again. The 72-byte table at `0x7F70` equals MAME's `s3000_memory_magic` byte for byte. On a match it reads a per-type byte from `0x7FB8` and adds it to totals at `0x7FFB`/`0x7FFC`.
- **[emulator]** The emulator returned `0xC0`, `0x40` or `0x80` on port `0x60` for a whole boot; the set of addresses written did not change ([memory-use.md](memory-use.md)).

## Evidence

- Static: `ndisasm -b16` of the linear image at the offsets above, 2026-11-02 (contributor) and 2026-11-13 (re-read of `0x205F7-0x206D0`, `0x1140B` and `0x20F08`, and the IVT decoded as 16 far pointers). Pins: `0x2063D` (108 bytes, the system-register writes), `0x2061E`, `0x206AA`, `0x113E0`, `0x1146C`, `0x2070C`, `0x20` (8), `0x2C` (4), `0x7640` (7), `0x19A73`, `0x20F08` (90), `0x7F70` (72).
- The relocation-order note comes from that 2026-11-13 re-read. The contributor's earlier record placed all six relocation writes at `0x20649-0x20678`; only the `0xFFFD` write is there.
- Documented: MAME `s3000.cpp` at `c2caa8969adb`: `base()` interrupt and DMA wiring, `rxd_w`/`txd_handler_cb`, `id_r`/`id_w` and the comment above them, and the `s3000_memory_magic` table, compared byte for byte on 2026-11-13.
- Emulator: the contributor's own unpublished 8086 emulator with invented peripheral stubs, 2026-11-02, one execution per run (floppy mount, MIDI with SysEx). Not checked on hardware.

## Open questions

- [Peripheral relocation order and the V53 registers](../questions/peripheral-relocation.md)
- [Is the S3200 an XL board, and does it run this image?](../questions/s3200-hardware-and-os.md)
