#!/usr/bin/env python3
# Builds rom/maincpu.bin (1 MiB 68000 address space image) from the MAME ffight set.
# Layout taken from MAME cps1.cpp ROM_START( ffight ).
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
r = lambda n: z.read(n)
def il(even, odd): return bytes(x for p in zip(r(even), r(odd)) for x in p)
m = r("ff-32m.8h")
img = il("ff_36.11f", "ff_42.11h") + il("ff_37.12f", "ffe_43.12h") + bytes(x for i in range(0, len(m), 2) for x in (m[i+1], m[i]))
assert len(img) == 0x100000
open(sys.argv[2], "wb").write(img)
print("wrote", sys.argv[2], hex(len(img)))
