#!/usr/bin/env python3
# Verifies a built 1 MiB 68000 image against the SHA-1 values in MAME cps1.cpp,
# ROM_START( ffight ), region "maincpu". usage: verify_maincpu.py IMAGE CPS1_CPP
# The chip layout is MAME's: ROM_LOAD16_BYTE pairs at 0x00000 and 0x40000, ROM_LOAD16_WORD_SWAP at 0x80000.
import hashlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mame_hashes import region_hashes
EXPECT = region_hashes(sys.argv[2], "maincpu")
b = open(sys.argv[1], "rb").read()
if len(b) != 0x100000: sys.exit(f"FAIL size {len(b):#x}")
chips = {
    "ff_36.11f":  b[0x00000:0x40000:2], "ff_42.11h":  b[0x00001:0x40000:2],
    "ff_37.12f":  b[0x40000:0x80000:2], "ffe_43.12h": b[0x40001:0x80000:2],
    "ff-32m.8h":  bytes(x for i in range(0x80000, 0x100000, 2) for x in (b[i+1], b[i])),
}
if set(chips) != set(EXPECT):
    sys.exit(f"FAIL chip list differs from MAME: here {sorted(chips)}, MAME {sorted(EXPECT)}")
ok = True
for n, d in chips.items():
    h = hashlib.sha1(d).hexdigest(); m = h == EXPECT[n]; ok &= m
    print(f"{'OK  ' if m else 'FAIL'} {n} {h}")
sys.exit(0 if ok else 1)
