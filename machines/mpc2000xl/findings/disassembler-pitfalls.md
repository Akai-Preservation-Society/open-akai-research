---
id: mpc2000xl.disassembler-pitfalls
title: Assembler and disassembler pitfalls on the MPC2000XL
machine: mpc2000xl
area: tooling
firmware: ["hardware"]
status: hardware
hardware_tested: partial
summary: Assemble for the 80186; 386 encodings fault on the V53A. Inline-operand interrupts, V53-only instructions and screen programs that mix code and data all break linear disassembly.
contributors: ["open-akai-research"]
last_verified: 2026-10-07
depends_on: ["mpc2000xl.abi-and-hooks"]
---

# Assembler and disassembler pitfalls on the MPC2000XL

## Claims

- **[hardware]** The V53A rejects 386 encodings. A build whose assembler emitted a near conditional jump as `0F 85 rel16` faulted on the machine. Assemble with `CPU 186` (NASM) or the equivalent.
- **[hardware]** Assembler listing addresses can be section-relative. A hook built from a listing without the section's origin jumped to the wrong place and crashed on entering the ASSIGN screen. Check every absolute address a build emits against the final image.
- **[static]** `0F E0 ib` is `BRKXA` and `0F F0 ib` is `RETXA`; x86 disassemblers read them as other instructions and lose the stream after them.
- **[static]** `INT 8Fh`, `96h`, `97h` and `9Ch` are followed by operand bytes, not code ([abi-and-hooks.md](abi-and-hooks.md)). So are many screen programs, which mix records and code.
- **[static]** Convert runtime `seg:off` to a file offset with `seg × 16 + off` before looking anything up in the image; physical ROM addresses are file offset + `0x80000`.
- **[hardware]** A composite of features that each passed alone can fail together. Test the exact final image.

## Evidence

- Hardware results from 2026 bench sessions on one unit (the `0F 85` fault, the listing-origin crash, a nine-feature composite that failed where its parts had passed).

## Open questions

- None known.
