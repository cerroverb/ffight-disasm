#!/usr/bin/env python3
"""Fails if any 68000 address executed in a MAME trace is not the start of an
assembled instruction line in the source.

Independent of tools/gen.py: it reads the assembler's own listing (as -al), so the
address of every source line comes from the assembler, not from the generator.

usage: check_coverage.py LISTING PCS_FILE [PCS_FILE ...]
exit 1 if any executed PC is inside .byte/.short/.long/.incbin data.
"""
import re, sys

DATA_DIRECTIVES = (".byte", ".short", ".word", ".long", ".incbin", ".ascii", ".space", ".fill")
# gas listing line: "  123 0004 4E75      	rts"
rx = re.compile(r"^\s*\d+\s+([0-9a-f]{4,8})\s+([0-9A-F]+)\s*(.*)$")

kind_at = {}       # address -> "ins" | "raw" | "data"
raw_len = {}       # address -> byte length of a raw-word instruction line
for line in open(sys.argv[1], errors="replace"):
    m = rx.match(line)
    if not m:
        continue
    addr = int(m.group(1), 16)
    src = m.group(3).split("|")[0].strip()
    if not src or src.endswith(":"):
        continue
    op = src.split()[0]
    if op == ".short" and "[raw:" in line:
        k = "raw"
    elif op.startswith("."):
        if op not in DATA_DIRECTIVES:
            continue
        k = "data"
    else:
        k = "ins"
    nbytes = len(m.group(2)) // 2
    if k == "raw":
        words = src.split(None, 1)[1].split(",")
        raw_len[addr] = 2 * len(words)
    for b in range(addr, addr + nbytes):
        kind_at.setdefault(b, "start-" + k if b == addr else "inside-" + k)

pcs = set()
for f in sys.argv[2:]:
    pcs |= {int(x, 16) for x in open(f) if x.strip()}

bad = sorted(p for p in pcs if kind_at.get(p) not in ("start-ins", "start-raw"))
raw = sorted(p for p in pcs if kind_at.get(p) == "start-raw")

# Raw-word lines only count as instructions if an independent disassembler (objdump)
# decodes their bytes as exactly one instruction of the same length.
import os, subprocess
CROSS = os.environ.get("CROSS", "m68k-linux-gnu-")
binfile = sys.argv[1].replace(".lst", ".bin")
fake_raw = []
for p in raw:
    n = raw_len[p]
    out = subprocess.run([CROSS + "objdump", "-D", "-b", "binary", "-m", "m68k:68000",
                          f"--start-address={p}", f"--stop-address={p + n}", binfile],
                         capture_output=True, text=True).stdout
    insns = [l for l in out.splitlines() if re.match(r"^\s+[0-9a-f]+:\t", l)]
    if len(insns) != 1 or ".short" in insns[0]:
        fake_raw.append(p)
for p in fake_raw:
    raw.remove(p)
    bad.append(p)
    print(f"    {p:06x}  raw line is not one valid instruction per objdump")
bad.sort()
print(f"executed PCs: {len(pcs)}")
print(f"  as assembled instructions: {len(pcs) - len(bad) - len(raw)}")
print(f"  as raw-word fallback (instruction in comment): {len(raw)}")
print(f"  NOT covered by an instruction (FAIL): {len(bad)}")
for p in bad[:20]:
    print(f"    {p:06x}  {kind_at.get(p, 'not in listing')}")
sys.exit(1 if bad else 0)
