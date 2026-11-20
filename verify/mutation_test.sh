#!/bin/bash
# Proves the checks can fail. Each mutation must make `make verify` FAIL.
# Runs on a temporary copy of src/; the real source is never modified.
set -u
cd "$(dirname "$0")/.."
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
cp -r src Makefile verify traces "$T"/ && mkdir -p "$T/build" "$T/rom"
cp rom/maincpu.bin "$T/rom/"
python3 -I -c 'import sys, zipfile; open(sys.argv[2], "wb").write(zipfile.ZipFile(sys.argv[1]).read("ff_09.12b"))' \
  rom/ffight.zip "$T/rom/ff_09.bin"
pass=0; fail=0
run() {   # name, then a command that mutates $T/src/ffight.s or $T/src/sound.s
  local name="$1"; shift
  cp src/ffight.s src/sound.s "$T/src/"
  "$@"
  if make -s -C "$T" verify >"$T/out.txt" 2>&1; then
    echo "MUTATION NOT CAUGHT: $name"; fail=$((fail+1))
  else
    echo "caught: $name -> $(grep -E 'FAIL' "$T/out.txt" | head -1)"; pass=$((pass+1))
  fi
}
# 1: change one immediate in an executed instruction
m1() { sed -i '0,/^\tmove.w\t#0x3ffb,d0$/s//\tmove.w\t#0x3ffc,d0/' "$T/src/ffight.s"; }
# 2: turn an executed instruction into data bytes with identical bytes (fake code)
m2() { sed -i '0,/^\tmoveq\t#0,d1$/s//\t.byte\t0x72,0x00/' "$T/src/ffight.s"; }
# 3: replace the whole program with a copy of the original ROM (fake match)
m3() { printf '\t.text\n\t.incbin\t"rom/maincpu.bin"\n' > "$T/src/ffight.s"; }
# 4: hide a raw-word fallback as plain data by deleting its [raw:] tag
m4() { sed -i 's/\[raw: assembler re-encodes\]//' "$T/src/ffight.s"; }
# 5: disguise data as a raw-word "instruction" (two words that objdump does not decode as one instruction)
m5() { python3 -I verify/m5.py "$T/src/ffight.s"; }
# Z80 6: change the interrupt mode set at reset
z1() { sed -i '0,/^\tim 1$/s//\tim 2/' "$T/src/sound.s"; }
# Z80 7: turn the first executed instruction into a data byte with the same value
z2() { sed -i '0,/^\tdi$/s//\t.byte\t0xf3/' "$T/src/sound.s"; }
# Z80 8: replace the whole sound program with a copy of the original chip
z3() { printf '\t.text\n\t.incbin\t"rom/ff_09.bin"\n' > "$T/src/sound.s"; }
run "one immediate changed"          m1
run "instruction replaced by .byte"  m2
run "whole ROM via .incbin"          m3
run "raw fallback tags removed"      m4
run "data disguised as raw instruction" m5
run "Z80 immediate changed"          z1
run "Z80 instruction replaced by .byte" z2
run "Z80 whole chip via .incbin"     z3
# sanity: unmodified source must PASS
cp src/ffight.s src/sound.s "$T/src/"
if make -s -C "$T" verify >/dev/null 2>&1; then echo "unmodified source: PASS"; else echo "unmodified source: FAIL"; fail=$((fail+1)); fi
echo "caught $pass of 8 mutations, problems: $fail"
[ "$fail" -eq 0 ]
