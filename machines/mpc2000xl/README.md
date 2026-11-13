# Akai MPC2000XL

Entry point for the MPC2000XL (1999). One-line facts are in
[machine.toml](machine.toml); known firmware images in
[firmware.toml](firmware.toml). All code-level findings are for
**OS 1.20** (`mpc2000xl-os1.20`).

## What you can do today

| You want to | State | Read |
|---|---|---|
| Change OS 1.20 and flash it, with a way back | Works, run on real hardware many times | [findings/build-a-patch.md](findings/build-a-patch.md) |
| Know why a bad image is not a brick | Boot block never written; recovery loader | [findings/rom-and-flash.md](findings/rom-and-flash.md) |
| React to keys, pads, the DATA wheel or the slider | Every report header and handler is known; wheel direction confirmed on hardware | [findings/panel-protocol.md](findings/panel-protocol.md) |
| Drive the 13 panel LEDs | Every port confirmed on hardware | [findings/panel-protocol.md](findings/panel-protocol.md) |
| Send MIDI from added code | Works on hardware (OUT B) | [findings/midi-output.md](findings/midi-output.md) |
| Draw text and soft keys | Inline OS services; a pop-up has run on hardware | [findings/abi-and-hooks.md](findings/abi-and-hooks.md) |
| Call screen, editor, voice and DSP routines; read programs and sounds in RAM | Entry points checked; arguments from a mod source, untested here | [findings/os-services-from-mods.md](findings/os-services-from-mods.md) |
| Read or write .SND files on a computer | Layout complete, checked against machine-written files | [findings/file-formats.md](findings/file-formats.md) |

## What you cannot do yet from this repository

| You want to | Missing | Question |
|---|---|---|
| Change sampling, playback or audio processing | The L6028 sample engine | [sample-engine](questions/sample-engine.md) |
| Change most screens or the sequencer | Named routines for OS 1.20 | [os120-code-map](questions/os120-code-map.md) |
| Read or write sequences | Event and song formats | [sequence-format](questions/sequence-format.md) |
| React to MIDI input or sync | The input path | [midi-input](questions/midi-input.md) |

The full list is in [../../GAPS.md](../../GAPS.md).

## Reading order

1. [findings/hardware-overview.md](findings/hardware-overview.md) and [findings/memory-and-io-map.md](findings/memory-and-io-map.md). Tables in [hardware/](hardware/).
2. [findings/rom-and-flash.md](findings/rom-and-flash.md): the image and the update. **Required** before flashing anything.
3. [findings/address-model.md](findings/address-model.md): **required** before using any address. Different from the MPC3000's.
4. [findings/disassembler-pitfalls.md](findings/disassembler-pitfalls.md) and [findings/abi-and-hooks.md](findings/abi-and-hooks.md): **required** before writing code.
5. [findings/code-space.md](findings/code-space.md), then [findings/build-a-patch.md](findings/build-a-patch.md).
6. As needed: [findings/os-services-from-mods.md](findings/os-services-from-mods.md), [findings/boot-and-panel-handshake.md](findings/boot-and-panel-handshake.md), [findings/panel-protocol.md](findings/panel-protocol.md), [findings/midi-output.md](findings/midi-output.md), [findings/file-formats.md](findings/file-formats.md).

## Firmware images

| Id | What | Examined here |
|---|---|---|
| `mpc2000xl-os1.20` | Akai OS 1.20, also the update file `MPC2KXL.BIN` | All code-level findings |
| `mpc2000xl-os1.14` | Akai OS 1.14 | Comparison only (identical boot block) |
| `mpc2000xl-panel-v1.00` | Panel MCU program | ID handshake |

## Tools

- [tools/xlimage.py](tools/xlimage.py): boot-block checks, checksum repair, and a comparison that refuses changes to protected ranges.
- [symbols/](symbols/) and [pins/](pins/): named addresses and byte-range hashes; `python3 tools/oar.py verify mpc2000xl-os1.20 MPC2KXL.BIN`.

## Emulation

vubeatz's experimental [mpc2000xl-emulator](https://github.com/dariuszchynek/mpc2000xl-emulator)
(a MAME target, BSD-3-Clause) runs stock OS 1.20 from its reset vector and,
by its author's account, reaches the main screen; audio, MIDI and floppy
saving are not working or not verified. It is listed in
[../../docs/external-resources.md](../../docs/external-resources.md). No
finding here relies on it yet. A private emulator also boots OS 1.20 to the main screen by answering
the panel ID handshake ([findings/boot-and-panel-handshake.md](findings/boot-and-panel-handshake.md));
results from it are tagged `emulator`.
