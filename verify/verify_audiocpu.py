#!/usr/bin/env python3
# Verifies a built Z80 sound ROM against the SHA-1 in MAME cps1.cpp, ROM_START( ffight ),
# region "audiocpu" (ff_09.12b). usage: verify_audiocpu.py IMAGE CPS1_CPP
import hashlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mame_hashes import region_hashes
EXPECT = region_hashes(sys.argv[2], "audiocpu")
if set(EXPECT) != {"ff_09.12b"}:
    sys.exit(f"FAIL chip list differs from MAME: MAME {sorted(EXPECT)}")
b = open(sys.argv[1], "rb").read()
if len(b) != 0x10000: sys.exit(f"FAIL size {len(b):#x}")
h = hashlib.sha1(b).hexdigest()
print(f"{'OK  ' if h == EXPECT['ff_09.12b'] else 'FAIL'} ff_09.12b {h}")
sys.exit(0 if h == EXPECT["ff_09.12b"] else 1)
