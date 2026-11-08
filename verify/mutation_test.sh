#!/bin/bash
# Proves the checks can fail. Each mutation must make `make verify` FAIL.
# Runs on a temporary copy of src/; the real source is never modified.
set -u
cd "$(dirname "$0")/.."
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
cp -r src Makefile verify traces "$T"/ && mkdir -p "$T/build" "$T/rom"
cp rom/maincpu.bin "$T/rom/"
pass=0; fail=0
run() {   # name, then a command that mutates $T/src/ffight.s
  local name="$1"; shift
  cp src/ffight.s "$T/src/ffight.s"
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
run "one immediate changed"          m1
run "instruction replaced by .byte"  m2
run "whole ROM via .incbin"          m3
run "raw fallback tags removed"      m4
run "data disguised as raw instruction" m5
# sanity: unmodified source must PASS
cp src/ffight.s "$T/src/ffight.s"
if make -s -C "$T" verify >/dev/null 2>&1; then echo "unmodified source: PASS"; else echo "unmodified source: FAIL"; fail=$((fail+1)); fi
echo "caught $pass of 5 mutations, problems: $fail"
[ "$fail" -eq 0 ]
