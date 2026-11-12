# Safety

These instruments are decades old, hard to replace, and worth caring
for. Software cannot usually destroy them, but careless work can leave
one unable to start, and careless hands can damage a board.

## Rules of thumb

1. **Back up before you change anything.** Read and save every EPROM you might replace, and check each read twice (two reads with the same hash). Keep the original chips; program new ones.
2. **Prefer routes that leave the machine unchanged.** A program loaded into RAM from a disk is gone when the power goes off. Use that route to learn and to test.
3. **One change at a time,** with a known-good way back for each.
4. **Know what state the machine keeps.** Battery-backed memory survives power-off. Code that writes there can change how the original OS behaves afterwards. On machines where this repository does not document that memory, treat it as off limits.
5. **Emulator first.** It is free to crash.
6. **Believe the evidence tags.** A finding marked `hardware_tested: no` has never been tried on a real machine. You may be the first; go carefully and report what happens.

## Electrical

- Unplug the machine before opening it. Power supplies hold charge after unplugging.
- EPROMs and CPUs are static-sensitive. Ground yourself.
- Old sockets and pins are brittle. Lever chips out evenly; never force one in. Note the orientation notch before removing anything.
- An EPROM inserted backwards can be destroyed and can damage the board.
- Displays and their backlight inverters carry high voltage.

## If the machine does not start after a change

- Remove any disk and power-cycle. A RAM-loaded program cannot survive that.
- If you replaced EPROMs, refit the originals.
- If settings look wrong, the battery-backed memory may have been altered; the machine's manual describes how to reinitialise it.
- Write down exactly what you did and what you saw, and open an issue. A failure report is evidence too.

## For agents

Before any step that changes hardware, or that could leave a machine
unable to start, stop and tell the user: what the step does, what
evidence class supports it, what could go wrong, and how to recover.
Proceed only when they say so.
