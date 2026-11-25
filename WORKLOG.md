# WORKLOG

Goal (User, 2026-11-20): a native Linux Wayland port of Final Fight built from a disassembly, no static recompiler. Approved dependencies: SDL3 (official repos), Musashi (MIT) and ymfm (BSD-3), vendored with citation. Ported hardware code comes from MAME (cps1.cpp, cps1_v.cpp, okim6295.cpp: BSD-3-Clause, checked 2026-11-20 at mamedev/mame master f09e0805).

## Done
- 2026-11-20: Z80 sound program disassembly. `tools/disz80.py`, `tools/genz80.py`, shared `tools/genlib.py` (gen.py output unchanged, checked with cmp). `src/sound.s` rebuilds ff_09.12b with the MAME SHA-1. Inline jump tables after `call 0x0021` handled. Exhaustive decoder test `verify/test_disz80.py`. Z80 coverage check and three Z80 mutations added.
- 2026-11-20: `tools/trace_bot.sh` traces the Z80 too (`CPUS`, `SCRIPT`). `bot/sound_cmds.lua` sends all 256 sound commands.

- 2026-11-25: sound command sweep finished, 1247 Z80 PCs in `traces/z80/sound_cmds.txt`, all already found by static discovery. `make verify` passes for all six chips, 8 of 8 mutations caught.

- 2026-11-25: gen.py follows long pointer tables (`movea.l (T,pc,dN.w),aM` then `jmp`/`jsr (aM)`): 29 tables, 44945 to 52932 instructions, 16.0% to 19.0% of the 68000 ROM. Verify and 8 of 8 mutations pass.

- 2026-11-25: self test return addresses 0x05E98E and 0x05EA92 (jmp (a5) from post_print_message) added as entry points. gen.py follows task routines passed to task_start (`movea.l #X,a0`; trap 0 stores a0 at slot offset 4, the scheduler resumes with jmp (a1) from offset 4): 18 routines, operands now labels. 57038 instructions, 20.5%. Verify and 8 of 8 mutations pass.

## Failed
- `BOT_CHAR` must be numeric (0 Guy, 1 Cody, 2 Haggar); a run with `guy` stopped the bot.

## Next
- Z80 traces from bot runs (sounds the 68000 sends in play), then remaining indirect jumps (`jp (hl)` other than the 0x0021 dispatcher).
- 68000 coverage beyond 16%, data tables, names.
- Port: decompile the disassembly to C routine by routine; CPS1 video from MAME cps1_v.cpp; Z80 sound via interpreter, YM2151 via ymfm, OKI6295 from MAME; SDL3 frontend.
