#!/usr/bin/env python3
"""Exhaustive check of tools/disz80.py against the GNU Z80 assembler.

Every opcode in every prefix group (none, CB, ED, DD, FD, DDCB, FDCB) is decoded
with fixed operand bytes, the text is assembled at the same address, and the
bytes must match. Also checks that the set of accepted opcodes is the documented
Z80 set: counts per group are compared with the documented totals (Zilog Z80
CPU User Manual UM0080 instruction set; totals counted from its opcode tables).
usage: test_disz80.py   (needs z80-unknown-coff-as on PATH, or ZCROSS set)
"""
import os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))
from disz80 import decode

ZCROSS = os.environ.get("ZCROSS", "z80-unknown-coff-")
ORG = 0x100
OPND = [0x05, 0x34, 0x12]       # displacement / immediate bytes after the opcode

cases = []
PREFIXES = (0xCB, 0xDD, 0xED, 0xFD)
for op in range(256):
    if op not in PREFIXES:
        cases.append(bytes([op]) + bytes(OPND))
    cases.append(bytes([0xCB, op]) + bytes(OPND))
    cases.append(bytes([0xED, op]) + bytes(OPND))
    for pre in (0xDD, 0xFD):
        if op != 0xCB:
            cases.append(bytes([pre, op]) + bytes(OPND))
        cases.append(bytes([pre, 0xCB, 0x05, op]))
# ED-prefixed ld (nn),hl and ld hl,(nn): the assembler always picks the shorter
# unprefixed encoding, so the generator emits these as raw bytes
REENCODED = {"ed630534", "ed6b0534"}

decoded = []
for c in cases:
    mem = bytes(ORG) + c
    ins = decode(mem, ORG)
    if ins is None:
        continue
    text = re.sub(r"(CODE|MEM)_([0-9A-F]{4})", lambda m: "0x" + m.group(2).lower(), ins.text)
    decoded.append((c[:ins.length], text))

with tempfile.TemporaryDirectory() as td:
    # each case at its own 8-byte slot, so relative jump targets are re-based per slot
    lines = []
    for i, (code, t) in enumerate(decoded):
        base = ORG + 8 * i
        ins = decode(bytes(base) + code, base)
        # code targets as section-relative expressions: the assembler refuses jr to an absolute number
        t2 = re.sub(r"CODE_([0-9A-F]{4})", lambda m: f".+{int(m.group(1), 16) - base}", ins.text)
        t2 = re.sub(r"MEM_([0-9A-F]{4})", lambda m: "0x" + m.group(1).lower(), t2)
        lines.append(f"\t.org 0x{base:x}\n\t{t2}\n")
    open(os.path.join(td, "t.s"), "w").write("\t.text\n" + "".join(lines))
    p = subprocess.run([ZCROSS + "as", "-march=z80", "-o", os.path.join(td, "t.o"), os.path.join(td, "t.s")],
                       capture_output=True, text=True)
    if p.returncode:
        sys.exit("assembler rejected decoder output:\n" + p.stderr[:3000])
    subprocess.run([ZCROSS + "ld", "-Ttext=0", "-o", os.path.join(td, "t.elf"), os.path.join(td, "t.o")], check=True)
    subprocess.run([ZCROSS + "objcopy", "-O", "binary", "-j", ".text", os.path.join(td, "t.elf"),
                    os.path.join(td, "t.bin")], check=True)
    built = open(os.path.join(td, "t.bin"), "rb").read()

mismatch = []
for i, (code, t) in enumerate(decoded):
    base = ORG + 8 * i
    got = built[base:base + len(code)]
    if got != code and code.hex() not in REENCODED:
        mismatch.append((code.hex(), got.hex(), t))
for m in mismatch:
    print("MISMATCH rom %s as %s  %s" % m)

# documented encodings: 256-4 prefixes; CB minus 8 SLL; ED 58; DD and FD 39 each; DDCB and FDCB 31 each
EXPECT = {"none": 252, "CB": 248, "ED": 58, "DD/FD": 78, "DDCB/FDCB": 62}
groups = {"none": 0, "CB": 0, "ED": 0, "DD/FD": 0, "DDCB/FDCB": 0}
for code, _ in decoded:
    if code[0] in (0xDD, 0xFD):
        groups["DDCB/FDCB" if code[1] == 0xCB else "DD/FD"] += 1
    else:
        groups["CB" if code[0] == 0xCB else "ED" if code[0] == 0xED else "none"] += 1
print("accepted encodings:", groups, "total", len(decoded))
print(f"round-trip mismatches: {len(mismatch)}")
print("expected:", EXPECT)
sys.exit(1 if mismatch or groups != EXPECT else 0)
