---
id: mpc2000xl.midi-output
title: MIDI ports and how to send MIDI from added code
machine: mpc2000xl
area: midi
firmware: ["mpc2000xl-os1.20"]
status: hardware
hardware_tested: partial
summary: The two MIDI outputs are the two channels of an MB89371A. The OS's enqueue routines take a status byte and data in registers, handle running status, and are safe to call from added code inside a short critical section. SIO2 drives MIDI OUT B on hardware.
contributors: ["open-akai-research"]
last_verified: 2026-10-07
depends_on: ["mpc2000xl.memory-and-io-map", "mpc2000xl.abi-and-hooks"]
---

# MIDI ports and how to send MIDI from added code

## Claims

- **[static]** SIO1 is at I/O `0x180-0x186` and SIO2 at `0x1A0-0x1A6`, each with data, status/command, baud-rate and mode registers at `+0`, `+2`, `+4`, `+6`. The OS sets both up as 8 data bits, no parity, one stop bit, ×64 clock.
- **[hardware]** SIO2 drives the MIDI OUT B jack: messages queued for SIO2 appeared on OUT B and nothing on OUT A.
- **[static]** SIO1 drives MIDI OUT A (its transmit interrupt, input 7, is the schematic's `INTTX1`). Not separately confirmed on hardware.
- **[static]** To send a message, far-call `0000:3BD6` for OUT A or `0000:3C3C` for OUT B with `DS = 0FE7`, `AH` = status byte, `AL` = first data byte, `CL` = second data byte (not used for `C0h`-`DFh`). The routine applies running status (state at `0FE7:0EA4` and `0FE7:11AE`; any status `F0h` or above resets it), queues into a 512-byte ring, starts the transmitter and marks the channel busy.
- **[static]** When a ring is within 16 bytes of full the routine drops the oldest data rather than blocking.
- **[static]** The routine is not re-entrant: it reads then writes the ring's write index without masking interrupts. Called from outside the sequencer's own context, wrap the call in `PUSHF; CLI … POPF`.
- **[hardware]** Program Change messages sent this way from added code came out of MIDI OUT B.
- **[emulator]** Note On and Off, Control Change and Polyphonic Key Pressure sent the same way produce the expected bytes in the OUT B ring, with running status applied.
- **[static]** Both MIDI inputs and the panel link share receive interrupt input 4.
- **[open]** The exact baud-rate clock (the MIDI rate is set by a divisor whose oscillator source is not documented here), the MIDI input parser, and the sample-dump engine.

## Evidence

- **Static:** OS 1.20 SIO set-up at `0x0066D`/`0x0069D`, enqueue routines at `0x03BD6` and `0x03C3C` (pinned), transmit handler at `0x00DD3`.
- **Hardware:** 2026-10-07, one unit, a test image sending Program Change messages to OUT B for each LED step; the full key, pad and slider mapping was checked in the emulator.

## Open questions

- [MIDI input and sync](../questions/midi-input.md)
