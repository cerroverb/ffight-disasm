#!/bin/bash
# usage: tools/trace_bot.sh NAME BOT_CHAR SECONDS
# Runs the bot under MAME with an execution trace; writes traces/NAME.txt and build/mame/inp/NAME.inp
set -e
cd "$(dirname "$0")/.."
N=$1; C=$2; T=$3
MAME=${MAME:-$(command -v mame || echo /usr/games/mame)}
[ -x build/collect_pcs ] || { mkdir -p build; gcc -O2 -o build/collect_pcs tools/collect_pcs.c; }
W=build/mame/run_$N; mkdir -p $W build/mame/inp traces
printf 'trace %s/trace.fifo,maincpu,noloop\ngo\n' "$W" > $W/trace.cmd
[ -p $W/trace.fifo ] || mkfifo $W/trace.fifo
build/collect_pcs $W/trace.fifo traces/$N.txt > $W/collect.log &
BOT_CHAR=$C BOT_SNAP=120 SDL_VIDEODRIVER=offscreen QT_QPA_PLATFORM=offscreen "$MAME" ffight -rompath rom -debug -debugger qt \
  -debugscript $W/trace.cmd -autoboot_script bot/bot.lua -video none -sound none -nothrottle -skip_gameinfo \
  -seconds_to_run $T -record $N.inp -input_directory build/mame/inp -snapshot_directory $W/snap \
  -cfg_directory $W/cfg -nvram_directory $W/nvram > $W/mame.log 2>&1
wait
echo "$N: $(cat $W/collect.log) $(grep Average $W/mame.log)"
