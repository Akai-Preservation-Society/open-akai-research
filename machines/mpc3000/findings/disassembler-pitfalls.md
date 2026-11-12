---
id: mpc3000.disassembler-pitfalls
title: Disassembler pitfalls on V53 firmware
machine: mpc3000
area: tooling
firmware: ["hardware"]
status: static
hardware_tested: no
summary: Common 8086 disassemblers mis-decode the V53 instructions BRKXA and RETXA and lose the instruction stream after them. Other traps are decoding one chip file alone and trusting raw opcode counts.
contributors: ["open-akai-research"]
last_verified: 2026-09-25
depends_on: ["mpc3000.address-model"]
---

# Disassembler pitfalls on V53 firmware

Read this before trusting any listing of MPC3000 code, including one you
produce yourself.

## Claims

- **[static]** `BRKXA imm8` is `0F E0 ib` and `RETXA imm8` is `0F F0 ib`. `ndisasm` and Capstone are 8086/x86 tools: they read `0F E0` as an MMX opcode and decode the following bytes wrongly. Scan any window for `0F E0` and `0F F0` before accepting a listing, and decode those sites by hand.
- **[static]** These byte pairs are rare. In the Vailixi 3.50 reference image `0F E0` occurs three times and `0F F0` twice, and the genuine instructions are in the boot and page-table code around `FAC0:`.
- **[static]** Decode the interleaved linear image, never a single chip file. A chip file holds every other byte of the program.
- **[static]** Counting opcode bytes over the whole image (for example `9A` for far calls) counts data too. Establish code by following control flow from known entries: the reset vector, vectors proven to be installed, and far-call targets of code already established.
- **[static]** Establish data by its consumer, the instruction that loads its address, not by how it looks. A string is located by the `PUSH` or `MOV` that references it.
- **[static]** An emulator trace shows one execution. It proves that a path runs, not that no other path exists.
- **[documented]** The V53 executes the 8086 instruction set plus the 80186 additions and its own extended-addressing instructions; assemblers targeting the 80186 produce valid code as long as they never emit `0F E0` or `0F F0` by accident (for example as data inside a code window that gets executed).

## Evidence

- Instruction encodings: NEC V-Series data book; MAME NEC core.
- The mis-decoding was observed with `ndisasm` and Capstone on the boot code of `mpc3000-vailixi-3.50`; byte-pair counts were recomputed on 2026-11-13.
- The method rules are the ones used to produce every static finding in this section.

## Open questions

- None known. A V53-aware instruction-length decoder would be a useful addition to `tools/`; none is included yet.
