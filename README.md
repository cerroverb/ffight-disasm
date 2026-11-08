Tools to produce a byte-identical, reassemblable 68000 disassembly of Capcom's Final Fight (1989, CP System), MAME set `ffight` (World).

This repository contains no ROM data and no Capcom code. The disassembly source is generated locally from your own ROM dump.

Status
- the generated source rebuilds all five 68000 program ROM chips byte-identically (checked by SHA-1)
- code is found by recursive descent from the vector table and from MAME execution traces (attract mode and bot gameplay runs in `traces/`)
- Z80 sound program, names and comments are not started

Requirements: m68k cross binutils, MAME, Python 3, make and gcc. On Ubuntu 24.04:

```bash
sudo apt install binutils-m68k-linux-gnu mame python3 make gcc
```

If your cross binutils use another prefix, set it, e.g. `export CROSS=m68k-elf-`.

Build and verify:

```bash
mkdir -p rom
cp /path/to/ffight.zip rom/
python3 tools/combine_rom.py rom/ffight.zip rom/maincpu.bin
python3 tools/gen.py rom/maincpu.bin src/ffight.s
make verify
./verify/mutation_test.sh
```

`make verify` must print `OK` for all five chips and `NOT covered by an instruction (FAIL): 0`. The build (`make`) reads only `src/`, never the ROM.

The checks:
- `verify/verify_maincpu.py` compares the SHA-1 of each rebuilt program chip with the values in MAME `cps1.cpp`, `ROM_START( ffight )`, so any byte difference fails
- `verify/check_coverage.py` reads the assembler's own listing and fails if any address executed in a MAME trace is not the start of an assembled instruction, so code cannot be left as `.byte` data or copied in as raw bytes
- `tools/gen.py` assembles every instruction at its address and compares the bytes. Instructions GNU as re-encodes (e.g. `(0,a0)` becomes `(a0)`) are emitted as raw words with the instruction in a comment and listed in `build/fallback.txt`
- `verify/mutation_test.sh` makes five broken copies of the source and checks that each one fails

Gameplay traces come from `bot/bot.lua`, a MAME Lua bot that walks to the nearest enemy, attacks and keeps continuing (object layout from the mame-rr `beatemup-hitboxes.lua` script). `tools/trace_bot.sh NAME CHAR SECONDS` runs it under the MAME debugger `trace` command and writes `traces/NAME.txt` and a replay in `build/mame/inp/`. Traced runs are slow.

Files:
- `tools/dis68k.py` 68000 decoder emitting GNU as Motorola syntax with explicit sizes
- `tools/gen.py` source generator (recursive descent, labels, round-trip check)
- `tools/names.txt` label names (exception vectors, interrupt handlers, self test, named routines), applied by the generator
- `tools/ram.txt` work RAM variable names, used for absolute operands
- `tools/hardware.txt` CPS1 hardware addresses, emitted as `.equ` and used for absolute operands; from MAME `cps1.cpp`, `cps1.h` and `cps1_v.cpp`
- `tools/combine_rom.py` builds the 1 MiB 68000 image from the MAME set
- `tools/collect_pcs.c`, `tools/collect_pcs.py` reduce a MAME trace to the set of executed PCs
- `traces/` executed-PC lists from MAME runs (addresses only)
- `verify/` verification scripts

License: GPLv3 (see `LICENSE`). It covers the tools, labels, comments and documentation in this repository only. Final Fight is © Capcom.
