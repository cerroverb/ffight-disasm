Tools to produce a byte-identical, reassemblable disassembly of Capcom's Final Fight (1989, CP System), MAME set `ffight` (World): the 68000 main program and the Z80 sound program.

This repository contains no ROM data and no Capcom code. The disassembly source is generated locally from your own ROM dump.

Status
- the generated source rebuilds all five 68000 program ROM chips byte-identically (checked by SHA-1)
- code is found by recursive descent from the vector table, from MAME execution traces (attract mode and bot gameplay runs in `traces/`), from `tools/entry_points.txt` and through jump tables of the form `move.w (T,pc,d0.w),d0; jmp (T,pc,d0.w)` (a table ends at its lowest target or at the next referenced address)
- the generated Z80 source rebuilds the sound program chip `ff_09.12b` byte-identically (checked by SHA-1). Code is found by recursive descent from the reset and IM 1 addresses, from MAME Z80 traces in `traces/z80/` and through the inline jump tables that follow `call 0x0021`. The bank area (chip 0x8000-0xffff) is 0xff filled in this set
- names and comments are mostly not started

Requirements: m68k and Z80 cross binutils, MAME, Python 3, make and gcc. On Ubuntu 24.04:

```bash
sudo apt install binutils-m68k-linux-gnu binutils-z80 mame python3 make gcc
```

If your cross binutils use other prefixes, set them, e.g. `export CROSS=m68k-elf-` and `export ZCROSS=z80-elf-`.

Build and verify:

```bash
mkdir -p rom
cp /path/to/ffight.zip rom/
python3 tools/combine_rom.py rom/ffight.zip rom/maincpu.bin
python3 tools/gen.py rom/maincpu.bin src/ffight.s
python3 tools/genz80.py rom/ffight.zip src/sound.s
make verify
python3 verify/test_disz80.py
./verify/mutation_test.sh
```

`make verify` must print `OK` for all six chips and `NOT covered by an instruction (FAIL): 0` twice (68000 and Z80). The build (`make`) reads only `src/`, never the ROM.

The checks:
- `verify/verify_maincpu.py` and `verify/verify_audiocpu.py` compare the SHA-1 of each rebuilt program chip with the values in MAME `cps1.cpp`, `ROM_START( ffight )`, so any byte difference fails
- `verify/check_coverage.py` reads the assembler's own listing and fails if any address executed in a MAME trace is not the start of an assembled instruction, so code cannot be left as `.byte` data or copied in as raw bytes
- `tools/gen.py` assembles every instruction at its address and compares the bytes. Instructions GNU as re-encodes (e.g. `(0,a0)` becomes `(a0)`) are emitted as raw words with the instruction in a comment and listed in `build/fallback.txt`
- `verify/mutation_test.sh` makes eight broken copies of the sources and checks that each one fails
- `verify/test_disz80.py` decodes every Z80 opcode in every prefix group, assembles the result and compares the bytes, and checks that exactly the 698 documented encodings are accepted

Gameplay traces come from `bot/bot.lua`, a MAME Lua bot that walks to the nearest enemy, attacks and keeps continuing (object layout from the mame-rr `beatemup-hitboxes.lua` script). `tools/trace_bot.sh NAME CHAR SECONDS` runs it under the MAME debugger `trace` command and writes `traces/NAME.txt` and a replay in `build/mame/inp/`. Both CPUs are traced by default; `CPUS` and `SCRIPT` select the traced CPUs and the Lua script. `bot/sound_cmds.lua` sends every sound command 0x00-0xff to the Z80 (`CPUS=audiocpu SCRIPT=bot/sound_cmds.lua tools/trace_bot.sh sound_cmds 0 800`). Traced runs are slow.

Files:
- `tools/dis68k.py` 68000 decoder emitting GNU as Motorola syntax with explicit sizes
- `tools/gen.py` source generator (recursive descent, labels, round-trip check)
- `tools/names.txt` label names (exception vectors, interrupt handlers, self test, named routines), applied by the generator
- `tools/ram.txt` work RAM variable names, used for absolute operands
- `tools/hardware.txt` CPS1 hardware addresses, emitted as `.equ` and used for absolute operands; from MAME `cps1.cpp`, `cps1.h` and `cps1_v.cpp`
- `tools/disz80.py` Z80 decoder emitting GNU as Zilog syntax, documented instructions only (opcode field layout from C. Dinu, "Decoding Z80 Opcodes", z80.info)
- `tools/genz80.py` Z80 source generator; `tools/genlib.py` parts shared by both generators
- `tools/z80_names.txt`, `tools/z80_hardware.txt` Z80 label names and sound hardware addresses (from MAME `cps1.cpp` `sub_map`)
- `tools/combine_rom.py` builds the 1 MiB 68000 image from the MAME set
- `tools/collect_pcs.c`, `tools/collect_pcs.py` reduce a MAME trace to the set of executed PCs
- `traces/` executed-PC lists from MAME runs (addresses only), Z80 lists in `traces/z80/`
- `verify/` verification scripts

License: GPLv3 (see `LICENSE`). It covers the tools, labels, comments and documentation in this repository only. Final Fight is © Capcom.
