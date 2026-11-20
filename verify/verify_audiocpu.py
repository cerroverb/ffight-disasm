#!/usr/bin/env python3
# Verifies a built Z80 sound ROM against the SHA-1 copied from MAME cps1.cpp (ROM_START( ffight ), ff_09.12b).
import hashlib, sys
EXPECT = "ec3db29fdd6200e9a8f4f8073a7e34aef731354f"
b = open(sys.argv[1], "rb").read()
if len(b) != 0x10000: sys.exit(f"FAIL size {len(b):#x}")
h = hashlib.sha1(b).hexdigest()
print(f"{'OK  ' if h == EXPECT else 'FAIL'} ff_09.12b {h}")
sys.exit(0 if h == EXPECT else 1)
