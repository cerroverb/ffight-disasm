Compares the cps2recomp Final Fight port (github.com/cerroverb/cps2recomp, branch ffight) with MAME under the same
input. No ROM data here: the ROM set stays the player's own.

Needs: MAME (tested with 0.264), a cps2recomp build of ffight (build/ffight/ffight, set in rom/ffight/), Python 3
with numpy, and a MAME rompath holding ffight.zip.

Files
- `mame_ram.lua`: MAME autoboot script. Replays a cps2recomp input movie (FF_MOVIE) and writes the 68000 work RAM
  (FF0000-FFFFFF, 64 KiB) after every frame to FF_OUT, for FF_FRAMES frames. FF_SHIFT moves the input: -1 lines the
  movie up with the port (the port applies a frame's input one frame earlier than this script does).
- `mame_chip.lua`: MAME autoboot script part. Logs the Z80's writes to the YM2151 and OKI with their Z80 time.
- `compare.py`: pairs MAME's RAM frames with the port's (`--trace 0000-FFFF:FILE`) and reports the first lasting
  divergence. Use `--exclude 0E00-0FFF --exclude 10B0-10B0` for Final Fight (the stack below FF1000 and a task state
  byte, which depend only on where the 68000 is inside a frame).
- `every10.py`: keeps every tenth 64 KiB frame of a RAM trace (for long runs: `--trace` into a fifo, this on the
  other end).
- `dropouts.py`: finds gaps in a recording of the live sound (3 ms or more where the game's own sound, from
  `--audio-dump` of a headless run, is not silent). Usage: `dropouts.py HEADLESS.wav RECORDING.wav ...`

Example (12000 frames of made-up play, Pure settings)

```sh
printf '[features]\npreset=pure\n' > settings.ini
build/ffight/ffight --rom rom/ffight --settings settings.ini --headless --frames 12000 --auto 7:400 --record movie.txt
build/ffight/ffight --rom rom/ffight --settings settings.ini --headless --frames 12000 --movie movie.txt --trace 0000-FFFF:port.bin
FF_MOVIE=movie.txt FF_OUT=mame.bin FF_FRAMES=12000 FF_SHIFT=-1 mame ffight -rompath ROMPATH -video none -sound none \
    -nothrottle -skip_gameinfo -noplugins -autoboot_script port-compare/mame_ram.lua
python3 port-compare/compare.py mame.bin port.bin --exclude 0E00-0FFF --exclude 10B0-10B0
```

Results so far (cps2recomp ffight branch 9646d7a, MAME 0.264): 12000 frames the same as MAME but 20 frames of the
start-up RAM test; 108000 frames (stages 1 to 3) every tenth the same but two in the RAM test; the Z80 writes the
same 227,260 times to the sound chips in 6000 frames.
