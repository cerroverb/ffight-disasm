#!/bin/bash
# usage: tools/trace_bot.sh NAME BOT_CHAR SECONDS
# Runs the bot under MAME with execution traces; writes traces/NAME.txt (68000),
# traces/z80/NAME.txt (Z80 sound CPU) and build/mame/inp/NAME.inp
# env: CPUS (default "maincpu audiocpu"), SCRIPT (autoboot script, default bot/bot.lua)
set -e
cd "$(dirname "$0")/.."
N=$1; C=$2; T=$3
CPUS=${CPUS:-maincpu audiocpu}
SCRIPT=${SCRIPT:-bot/bot.lua}
MAME=${MAME:-$(command -v mame || echo /usr/games/mame)}
[ -x build/collect_pcs ] || { mkdir -p build; gcc -O2 -o build/collect_pcs tools/collect_pcs.c; }
W=build/mame/run_$N; mkdir -p $W build/mame/inp traces/z80
: > $W/trace.cmd
for cpu in $CPUS; do
  case $cpu in
    maincpu)  out=traces/$N.txt; digits=6 ;;
    audiocpu) out=traces/z80/$N.txt; digits=4 ;;
    *) echo "unknown cpu $cpu"; exit 1 ;;
  esac
  printf 'trace %s/%s.fifo,%s,noloop\n' "$W" $cpu $cpu >> $W/trace.cmd
  [ -p $W/$cpu.fifo ] || mkfifo $W/$cpu.fifo
  build/collect_pcs $W/$cpu.fifo $out $digits > $W/collect_$cpu.log &
done
echo go >> $W/trace.cmd
BOT_CHAR=$C BOT_SNAP=120 SDL_VIDEODRIVER=offscreen QT_QPA_PLATFORM=offscreen "$MAME" ffight -rompath rom -debug -debugger qt \
  -debugscript $W/trace.cmd -autoboot_script $SCRIPT -video none -sound none -nothrottle -skip_gameinfo \
  -seconds_to_run $T -record $N.inp -input_directory build/mame/inp -snapshot_directory $W/snap \
  -cfg_directory $W/cfg -nvram_directory $W/nvram > $W/mame.log 2>&1
wait
for cpu in $CPUS; do echo "$N $cpu: $(cat $W/collect_$cpu.log)"; done
grep Average $W/mame.log
