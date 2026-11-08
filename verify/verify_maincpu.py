#!/usr/bin/env python3
# Verifies a built 1 MiB 68000 image against SHA-1 values copied from MAME cps1.cpp (ROM_START( ffight )).
import hashlib, sys
EXPECT = {
    "ff_36.11f":  "0756ae576a1f6d5b8b22f8630dca40ef38567ea6",
    "ff_42.11h":  "5045a467f3e228c02b4a355b52f58263ffa90113",
    "ff_37.12f":  "38f44434c8befd623953ae23d6e5ff4e201d6627",
    "ffe_43.12h": "de16873d1639ac1738be0937270b108a9914f263",
    "ff-32m.8h":  "d3362dadded31ccb7eaf71ef282d698d18edd722",
}
b = open(sys.argv[1], "rb").read()
if len(b) != 0x100000: sys.exit(f"FAIL size {len(b):#x}")
chips = {
    "ff_36.11f":  b[0x00000:0x40000:2], "ff_42.11h":  b[0x00001:0x40000:2],
    "ff_37.12f":  b[0x40000:0x80000:2], "ffe_43.12h": b[0x40001:0x80000:2],
    "ff-32m.8h":  bytes(x for i in range(0x80000, 0x100000, 2) for x in (b[i+1], b[i])),
}
ok = True
for n, d in chips.items():
    h = hashlib.sha1(d).hexdigest(); m = h == EXPECT[n]; ok &= m
    print(f"{'OK  ' if m else 'FAIL'} {n} {h}")
sys.exit(0 if ok else 1)
