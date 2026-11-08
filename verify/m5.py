#!/usr/bin/env python3
# Mutation 5: replace "moveq #0,d1" + following "move.l d1,(a0)+" (0x7200 0x20c1) with one
# raw line of identical bytes that claims to be a single instruction. Bytes are unchanged.
import sys
p = sys.argv[1]; L = open(p).read().split("\n")
i = L.index("\tmoveq\t#0,d1")
assert L[i + 1] == "loc_000412:" and L[i + 2] == "\tmove.l\td1,(a0)+"
L[i:i + 3] = ["\t.short\t0x7200,0x20c1\t| moveq #0,d1  [raw: assembler re-encodes]", "loc_000412 = . - 2"]
open(p, "w").write("\n".join(L))
