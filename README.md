# avsp-research

Alien vs. Predator (Capcom CPS2, 1994) research and tools, kept apart from the Final Fight disassembly. This branch
has no history in common with the Final Fight branches. No ROM data, keys or RAM dumps are here.

State as of 2026-11-09.

## Contents

| Path | What |
| --- | --- |
| `report/Alien vs Predator CPS2 port viability.md` | Research report: viability of a byte-identical AvP disassembly and a native Linux/Wayland port, existing projects, tools, legal, recommended path |
| `research_notes/` | The five research notes the report was written from (private repository names removed) |
| `avsp-compare/` | MAME against cps2recomp comparison: `run.sh`, `mame_dump.lua`, `compare.py`, README |
| `avsp-compare/upstream/` | The cps2recomp patch and PR text submitted as tmcleroy/cps2recomp#323 |
| `results/run-patched-explored/` | Comparison output with the patch applied and `explore` run (summary, reports, JSON, input movie) |
| `results/third-player-test/` | Input movie, check script and result of the third-player coin and start test |
| `results/cps2recomp_checks.log` | `explore` and `make GAME=avsp check FRAMES=20000` output, patched and unpatched |

## Status

- Pull request open at https://github.com/tmcleroy/cps2recomp/pull/323 (fork cerroverb/cps2recomp, branch
  `avsp-player-mode`). Its description links to commit `74acfe0` of cerroverb/ffight-disasm for the scripts; the same
  scripts are in `avsp-compare/` here.
- The AvP files were removed from the ffight-disasm branch `claude/serene-johnson-z6j22m` by commit `9382424`.
  Commits `e87e92c`, `7004afe`, `74acfe0` there still hold them.
- No AvP disassembly has been started.

## Findings

### Research (report)

- A native port exists: tmcleroy/cps2recomp, static recompilation to C++ on SDL 3, AvP in beta (set `avspu`, other
  regions accepted). No public AvP disassembly, IDA/Ghidra database or decompilation was found.
- The ffight-disasm tooling transfers. The new work for a byte-identical AvP rebuild is CPS2 opcode encryption:
  decode from a decrypted image, keep data from the raw image, re-encrypt only opcode words (MAME's cipher only
  decrypts), and settle whether PC-relative jump-table reads are decrypted.

### cps2recomp against MAME 0.264 (work RAM FF0000-FFFFFF after every frame)

- **Player mode hook (bug, PR #323).** The game's 003C5E (003D3C-003D5A) sets FF81C5 = one coin chute (modes 1, 2)
  and FF81C6 = two players only (mode 2). cps2recomp's Board page hook (`games/avsp/src/game.cpp`, run at 000D20 and
  0B3C6A) set them with modes 0 and 2 swapped. Effect in Pure on a factory board: a third player's coin and start
  were taken (FF819C credit, game started) where MAME takes neither. These were the first bytes apart after
  power-on.
- **FF0118 (not a bug).** State byte of task 6 in the task table (16 tasks of 0x20 bytes from FF0058). Task 6 yields
  with `trap #4` every scheduler pass (001096-0010AC writes 04) and is resumed at 000DE6 (writes 08). Its value at a
  frame's end depends only on where the 68000 is inside the frame. `compare.py` leaves it out by default.
- **FF8018 (lag frames).** Vblank counter (A5+18, incremented at 000E80). With arcade timing on, MAME and cps2recomp
  place one lag frame differently at MAME frame 464; for the next 300 frames only this byte differs, and at frame 764
  they match again. Neither side models the board's timing exactly (MAME uses a 68000 clock scale in place of wait
  states), so this does not show either is wrong.
- **After input starts**, with FF8018 also left out, the bytes that come and go are FF8060-FF8069 and FF819B, with
  stretches of 0 bytes apart. Not identified; input landing a frame apart after a lag frame is the unverified
  explanation.
- Results with the patch, `explore` run, 6000 frames, seed 1, input from frame 900:

```
arcade timing off  boot shift +33  paired 902 of 6000  lasting divergence from MAME frame 928
arcade timing on   boot shift +13  paired 514 of 6000  lasting divergence from MAME frame 464
```

### cps2recomp checks

- `make audit` passed. `make GAME=avsp check FRAMES=20000` passed on both d3bf22f and the patch after `explore`;
  before `explore` it failed on both (frames 483 and 77).
- `make check` did not finish in the cloud session: downloading Dear ImGui from github.com was refused by its network.
- AvP has no `check_rewrites.sh` and no ladder movie.

## Setup notes

- ROM set used: merged `avsp.zip` (MAME current: corrected 1 MB `avp.14m/16m/18m/20m`, every region's key inside).
  cps2recomp picks the set `avsp` (Europe) from it. An older non-merged `avspu.zip` without `avspu.key` and with the
  old 2 MB graphics dumps does not work with cps2recomp.
- MAME needs `qsound.zip` (`dl-1425.bin`) beside the set. MAME 0.264 (Ubuntu package) looks for it as
  `qsound_hle.zip`; newer MAME as `qsound.zip`.
- Owner's machine: CachyOS, ROMs in `/mnt/8tb-ssd/Emulation/roms/mame/`, cps2recomp in `~/cps2recomp` (built,
  `explore` run). On CachyOS leave `zlib` out of pacman installs (`zlib-ng-compat` provides it).
- cps2recomp was researched at commit `d3bf22f` (2026-11-08).
- Cloud session build: SDL 3.4.18 from source with `-DSDL_X11=OFF -DSDL_UNIX_CONSOLE_BUILD=ON`, then
  `CMAKE_PREFIX_PATH=<sdl3 prefix> make GAME=avsp` twice and `make GAME=avsp explore`.

## Reproduce the comparison

```
ROMPATH=/mnt/8tb-ssd/Emulation/roms/mame CPS2RECOMP=~/cps2recomp OUT=$HOME/avsp-compare-out avsp-compare/run.sh
```

`compare.py --exclude 7C00-7FFF --exclude 0118 --exclude 8018` gives the comparison without the vblank counter.

## Open items

- Identify FF8060-FF8069 and FF819B.
- Compare against a board-level reference (jotego's jtcps2 simulated, as cps2recomp's docs/ARCADE_ACCURACY.md does
  for SFA2) instead of MAME for timing.
- AvP byte-identical disassembly: CPS2 cipher encrypt step, code/data bitmap, PC-relative jump-table question,
  `gen.py` for `avspu`, bot port, Z80 sound program.
- Watch PR #323 for review.
