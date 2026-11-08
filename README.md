# Final Fight (CPS1 arcade) disassembly tools

Tools to produce a byte-identical, reassemblable 68000 disassembly of Capcom's
*Final Fight* (1989, CP System), MAME set `ffight` (World).

This repository contains **no ROM data and no Capcom code**. The disassembly
source is generated locally from your own ROM dump.

## Status

| Item | State |
|---|---|
| Generated source rebuilds all five 68000 program ROM chips byte-identically | yes (verified by SHA-1, see below) |
| Code found by recursive descent from the vector table | yes |
| Code found from MAME execution traces | in progress |
| Z80 sound program | not started |
| Names / comments | not started |

## Requirements (Ubuntu 24.04)

```bash
sudo apt install binutils-m68k-linux-gnu mame python3 make
```

## Build and verify

```bash
mkdir -p rom
cp /path/to/ffight.zip rom/
python3 tools/combine_rom.py rom/ffight.zip rom/maincpu.bin
python3 tools/gen.py rom/maincpu.bin src/ffight.s
make verify
```

`make verify` must print `OK` for all five chips and `NOT covered ... : 0`.

## Anti-cheat checks

| Check | File | Catches |
|---|---|---|
| SHA-1 of each rebuilt program chip against the values in MAME `cps1.cpp` `ROM_START( ffight )` | `verify/verify_maincpu.py` | Any byte difference |
| Every executed address in a MAME trace must be the start of an assembled instruction, read from the assembler's own listing | `verify/check_coverage.py` | Code left as `.byte` data, fake matches by copying bytes |
| Per-instruction assembler round-trip; instructions GNU as re-encodes are emitted as raw words with the instruction in a comment and listed in `build/fallback.txt` | `tools/gen.py` | Silent assembler re-encoding |

The build (`make`) reads only `src/`. It never reads the ROM.

## Layout

| Path | Contents |
|---|---|
| `tools/dis68k.py` | 68000 decoder emitting GNU as Motorola syntax with explicit sizes |
| `tools/gen.py` | Source generator (recursive descent, labels, round-trip check) |
| `tools/combine_rom.py` | Builds the 1 MiB 68000 image from the MAME set |
| `tools/collect_pcs.py` | Reduces a MAME debugger trace to the set of executed PCs |
| `tools/entry_points.txt` | Extra code entry points |
| `traces/` | Executed-PC lists from MAME runs (addresses only) |
| `verify/` | Verification scripts |

## License

GPLv3 (see `LICENSE`). Covers the tools, labels, comments and documentation in
this repository only. *Final Fight* is © Capcom.
