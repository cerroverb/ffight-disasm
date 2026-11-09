#!/usr/bin/env bash
# Alien vs. Predator: cps2recomp against MAME, frame by frame, by the 68000's work RAM.
#
# 1. cps2recomp records an input movie of made-up play (--auto SEED:AUTO_FROM:3).
# 2. cps2recomp replays it twice, arcade timing off and on, writing work RAM after every frame (--trace).
# 3. MAME replays the same movie (mame_dump.lua) on the same set, writing work RAM after every frame.
# 4. compare.py pairs the frames and reports paired frames, the boot offset and the first lasting divergence.
#    When the boot offset is not 0, MAME is run again with the movie shifted by it, so input lands on the
#    same game state on both sides.
#
# Environment (defaults in brackets):
#   ROMPATH     MAME rompath holding the set and qsound.zip            [required]
#   CPS2RECOMP  cps2recomp checkout with build/avsp/avsp and rom/avsp   [~/cps2recomp]
#   MAME        MAME binary                                             [mame on PATH, else /usr/games/mame]
#   FRAMES      frames per run                                          [6000]
#   SEED        made-up play seed                                       [1]
#   AUTO_FROM   first frame of made-up play                             [900]
#   OUT         output folder                                           [./avsp-compare-out/SEED-FRAMES]
#   RECOMP_ARGS extra arguments for every cps2recomp run                []
#
# Disk use: 64 KiB a frame a run (6000 frames: about 390 MB a run, 3 to 5 runs).
# Exit status: 0 when no run diverged, 1 when one did, 2 on a setup error.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${ROMPATH:?set ROMPATH to the MAME rompath (the folder with avsp.zip and qsound.zip)}"
CPS2RECOMP="${CPS2RECOMP:-$HOME/cps2recomp}"
if [ -z "${MAME:-}" ]; then
	MAME="$(command -v mame || true)"
	[ -n "$MAME" ] || MAME=/usr/games/mame
fi
FRAMES="${FRAMES:-6000}"
SEED="${SEED:-1}"
AUTO_FROM="${AUTO_FROM:-900}"
OUT="${OUT:-$PWD/avsp-compare-out/$SEED-$FRAMES}"
RECOMP_ARGS="${RECOMP_ARGS:-}"

recomp="$CPS2RECOMP/build/avsp/avsp"
romdir="$CPS2RECOMP/rom/avsp"
header="$CPS2RECOMP/games/avsp/src/avsp.h"
for f in "$recomp" "$MAME"; do
	[ -x "$f" ] || { echo "missing or not executable: $f" >&2; exit 2; }
done
[ -d "$romdir" ] || { echo "missing ROM folder: $romdir" >&2; exit 2; }
command -v python3 >/dev/null || { echo "python3 not found" >&2; exit 2; }

mkdir -p "$OUT"
printf '[features]\npreset=pure\n' > "$OUT/settings.ini"
export SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy

run_recomp() { # extra args...
	# shellcheck disable=SC2086
	"$recomp" --rom "$romdir" --settings "$OUT/settings.ini" --headless --frames "$FRAMES" $RECOMP_ARGS "$@"
}

echo "=== cps2recomp: record made-up play (seed $SEED from frame $AUTO_FROM, $FRAMES frames) ==="
run_recomp --auto "$SEED:$AUTO_FROM:3" --record "$OUT/movie.txt" 2>&1 | tee "$OUT/record.log"
set_name="$(sed -n 's/.*: the set \([a-z0-9]*\) .*/\1/p' "$OUT/record.log" | head -1)"
[ -n "$set_name" ] || { echo "could not read the set name from cps2recomp's output" >&2; exit 2; }
echo "set: $set_name"

for timing in off on; do
	echo "=== cps2recomp: replay, arcade timing $timing ==="
	features=()
	[ "$timing" = on ] && features=(--features arcade_timing)
	run_recomp --movie "$OUT/movie.txt" --trace "0000-FFFF:$OUT/recomp_timing_$timing.bin" "${features[@]}" \
		2>&1 | tee "$OUT/recomp_timing_$timing.log"
done

run_mame() { # shift
	local shift="$1" bin="$OUT/mame_shift_$1.bin"
	[ -s "$bin" ] && return 0
	echo "=== MAME: replay $set_name, movie shifted by $shift frames ==="
	rm -rf "$OUT/nvram_$shift" && mkdir -p "$OUT/nvram_$shift" "$OUT/mame_cfg"
	AVSP_MOVIE="$OUT/movie.txt" AVSP_OUT="$bin" AVSP_FRAMES="$FRAMES" AVSP_SHIFT="$shift" \
		"$MAME" "$set_name" -rompath "$ROMPATH" -video none -sound none -nothrottle -skip_gameinfo -noplugins \
		-nvram_directory "$OUT/nvram_$shift" -cfg_directory "$OUT/mame_cfg" \
		-seconds_to_run $((FRAMES / 59 + 60)) -autoboot_script "$here/mame_dump.lua" \
		2>&1 | tee "$OUT/mame_shift_$shift.log"
	[ -s "$bin" ] || { echo "MAME wrote no frames (see $OUT/mame_shift_$shift.log)" >&2; exit 2; }
}

run_mame 0
names=()
[ -f "$header" ] && names=(--names "$header")
status=0
summary="$OUT/summary.txt"
: > "$summary"
for timing in off on; do
	rbin="$OUT/recomp_timing_$timing.bin"
	shift="$(python3 "$here/compare.py" "$OUT/mame_shift_0.bin" "$rbin" --offset-only --before "$AUTO_FROM")"
	run_mame "$shift"
	echo "=== compare: MAME (shift $shift) against cps2recomp, arcade timing $timing ==="
	set +e
	python3 "$here/compare.py" "$OUT/mame_shift_$shift.bin" "$rbin" "${names[@]}" \
		--json "$OUT/compare_timing_$timing.json" | tee "$OUT/compare_timing_$timing.txt"
	rc=${PIPESTATUS[0]}
	set -e
	[ "$rc" -eq 2 ] && exit 2
	[ "$rc" -ne 0 ] && status=1
	python3 - "$OUT/compare_timing_$timing.json" "$timing" "$shift" >> "$summary" <<'EOF'
import json, sys
s = json.load(open(sys.argv[1]))
d = s["lasting_divergence"]
print(f"arcade timing {sys.argv[2]:3}  boot shift {int(sys.argv[3]):+d}  paired {s['paired']} of {s['reference_frames']}  "
      f"lasting divergence {'none' if d is None else 'from MAME frame ' + str(d)}")
EOF
done

echo "=== summary ($OUT/summary.txt) ==="
cat "$summary"
exit "$status"
