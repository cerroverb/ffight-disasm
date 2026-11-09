# avsp-compare

Compares cps2recomp's Alien vs. Predator with MAME by 68000 work RAM (FF0000-FFFFFF), after every frame, under the
same input. The result is printed and written to files, so nothing has to be checked by eye.

- `run.sh` records made-up play with cps2recomp, replays it in cps2recomp (arcade timing off and on) and in MAME,
  and compares each cps2recomp run with MAME.
- `mame_dump.lua` is the MAME autoboot script. It replays a cps2recomp movie and writes work RAM every frame.
- `compare.py` pairs each MAME frame with an identical cps2recomp frame within 30 frames of the previous pair's
  offset, and reports paired frames, the offset between the two runs and the first lasting divergence with the bytes
  that differ. After a divergence it lists, every 30 frames, the cps2recomp frame nearest to the MAME frame and the
  bytes still apart, which tells a lag frame (only the vblank counter FF8018 apart) from runs that part for good. Its
  exit status is 0 for no lasting divergence, 1 for one.
- `run.sh` shifts MAME's input by the offset of the last pair before input starts, so input meets the same game
  state on both sides when the two runs' boot tests take different times.

## Left out of the comparison by default

- FF7C00-FF7FFF, the stack.
- FF0118, the state byte of task 6 in the game's task table (16 tasks of 0x20 bytes from FF0058). Task 6 yields with
  `trap #4` on every pass of the scheduler, which writes 04 (001096-0010AC), and is set to 08 when it runs again
  (000DE6). Whether the frame ends while it runs depends only on where the 68000 is inside the frame, so this byte
  differs between any two runs whose timing differs, without the game's state differing.

## Needs

- A cps2recomp checkout built for avsp (`build/avsp/avsp`, set in `rom/avsp/`).
- MAME, and a rompath with the same set and `qsound.zip` (`dl-1425.bin`).
- Python 3.

## Run

```
ROMPATH=/path/to/mame/roms CPS2RECOMP=~/cps2recomp avsp-compare/run.sh
```

Optional environment: `FRAMES` (6000), `SEED` (1), `AUTO_FROM` (900), `OUT`, `MAME`, `RECOMP_ARGS`.

Output in `OUT`: `summary.txt`, `compare_timing_off.txt`, `compare_timing_on.txt`, the JSON of each, the movie and
the RAM dumps (64 KiB a frame a run).

## What it shows and does not

- Agreement with MAME, not with a board. MAME runs the CPS2 68000 with a clock scale in place of wait states.
- Work RAM only, at frame ends. Picture, sound, video RAM and timing inside a frame are not compared.
- The comparison is only as good as the input mapping. The script builds MAME's IN0, IN1 and IN2 words the way
  cps2recomp's `Machine::Input` does, and MAME's log counts frames whose input had no MAME field.
