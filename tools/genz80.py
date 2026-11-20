#!/usr/bin/env python3
"""Generate src/sound.s (Z80 sound program, ff_09.12b) from the MAME ffight set.

The 64 KiB chip holds the fixed Z80 ROM (file 0x0000-0x7fff, Z80 0x0000-0x7fff)
and two 16 KiB banks (file 0x8000-0xffff, both at Z80 0x8000-0xbfff), per MAME
cps1.cpp ROM_START( ffight ) and MACHINE_START cps1. Code is found by recursive
descent from the reset and IM 1 addresses, tools/z80_entry_points.txt and the
Z80 traces in traces/z80/. Only the fixed area is searched: in ffight both bank
areas are 0xff filled. Each instruction is round-trip checked through the
assembler like tools/gen.py; re-encoded instructions become raw .byte lines with
the instruction in a comment, listed in build/fallback_z80.txt.

usage: genz80.py ffight.zip OUT.s
"""
import os, re, subprocess, sys, tempfile, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from disz80 import decode
from genlib import ROOT, read_addresses, read_table, read_traces, discover, roundtrip

ZCROSS = os.environ.get("ZCROSS", "z80-unknown-coff-")
CHIP = "ff_09.12b"
FIXED = 0x8000              # end of the fixed ROM area in the Z80 address space
FILL_MIN = 64               # runs of identical data bytes at least this long become .fill

rom = zipfile.ZipFile(sys.argv[1]).read(CHIP)
OUT = sys.argv[2]
SIZE = len(rom)
fixed = rom[:FIXED]

entries = {0x0000, 0x0038} | read_addresses("z80_entry_points.txt") | read_traces("z80", 4)

# The routine at 0x0021 is `pop hl; call 0x002d; jp (hl)` and 0x002d computes
# hl = word at (hl + 2*a): a `call 0x0021` is followed by an inline table of
# little-endian code addresses indexed by A, and never returns to the bytes after it.
INLINE_TABLE_DISPATCH = 0x0021

owner = [None] * FIXED
ins_at = {}
bad_paths = []
jump_tables = {}            # table address -> targets


def decode_program(mem, pc):
    ins = decode(mem, pc)
    if ins and ins.text == f"call CODE_{INLINE_TABLE_DISPATCH:04X}":
        ins.flow = "jump"
    return ins


def plausible_code(t):
    """True when t starts known code, or decodes as a few instructions in a row."""
    a = t
    for _ in range(4):
        if a >= FIXED:
            return False
        if owner[a] is not None:
            return owner[a] == a
        ins = decode_program(fixed, a)
        if ins is None:
            return False
        if ins.flow in ("stop", "jump"):
            return True
        a += ins.length
    return True


def table_targets(table, referenced):
    """Entries until the lowest target so far or the next referenced address."""
    targets = []
    end = min([FIXED] + [r for r in referenced if r > table])
    a = table
    while a + 2 <= end and len(targets) < 256:
        t = fixed[a] | fixed[a + 1] << 8
        if t <= table or t >= FIXED or not plausible_code(t):
            break
        targets.append(t)
        end = min(end, t)
        a += 2
    jump_tables[table] = targets
    return targets


def referenced_addresses():
    refs = {addr for ins in ins_at.values() for kind, addr in ins.refs if addr < FIXED}
    refs |= {t for ins in ins_at.values() for t in ins.targets}
    return refs | {t for targets in jump_tables.values() for t in targets}


def discover_all(bounds):
    """Full discovery from scratch; bounds are addresses referenced in an earlier
    pass, so a table processed before the code after it is found stops in time."""
    owner[:] = [None] * FIXED
    ins_at.clear(); bad_paths.clear(); jump_tables.clear()
    seen = set()
    discover(fixed, decode_program, sorted(entries), 1, owner, ins_at, seen, bad_paths)
    while True:
        new = []
        referenced = referenced_addresses() | bounds
        for a, ins in sorted(ins_at.items()):
            table = a + ins.length
            if ins.text == f"call CODE_{INLINE_TABLE_DISPATCH:04X}" and table not in jump_tables:
                targets = table_targets(table, referenced)
                referenced |= set(targets)
                new += targets
        if not new:
            return referenced_addresses()
        discover(fixed, decode_program, new, 1, owner, ins_at, seen, bad_paths)


bounds = set()
for _ in range(10):
    refs = discover_all(bounds)
    if refs <= bounds:
        break
    bounds |= refs

# ---------------------------------------------------------------- labels
labels = {a: n for a, n in read_table("z80_names.txt").items() if a < FIXED and owner[a] in (None, a)}
hardware = read_table("z80_hardware.txt")
hardware.update(read_table("z80_ram.txt"))
unlabelable = []


def want_label(addr):
    if addr >= FIXED or (owner[addr] is not None and owner[addr] != addr):
        return None     # outside the fixed ROM, or middle of an instruction
    if addr not in labels:
        labels[addr] = f"loc_{addr:04X}" if addr in ins_at else f"dat_{addr:04X}"
    return labels[addr]


def resolve(ins):
    def sub(m):
        addr = int(m.group(2), 16)
        name = want_label(addr) or hardware.get(addr)
        if name is None:
            unlabelable.append((ins.pc, addr))
            return f"0x{addr:x}"
        return name
    return re.sub(r"(CODE|MEM)_([0-9A-F]{4})", sub, ins.text)


for table, targets in jump_tables.items():
    if targets and all(owner[b] is None for b in range(table, table + 2 * len(targets))):
        want_label(table)
        for t in targets:
            want_label(t)
    else:
        targets.clear()     # no entry, or bytes already decoded as code: stays as it is
texts = {a: resolve(i) for a, i in sorted(ins_at.items())}
fallback = set()


def data_lines(data):
    """.byte lines, 16 per line, with long runs of one value as .fill."""
    out, i = [], 0
    while i < len(data):
        j = i
        while j < len(data) and data[j] == data[i]:
            j += 1
        if j - i >= FILL_MIN:
            out.append(f"\t.fill\t0x{j - i:x},1,0x{data[i]:02x}")
            i = j
            continue
        k = i + 1
        while k < len(data) and k - i < 16:
            run = k
            while run < len(data) and data[run] == data[k]:
                run += 1
            if run - k >= FILL_MIN:
                break
            k += 1
        out.append("\t.byte\t" + ",".join(f"0x{b:02x}" for b in data[i:k]))
        i = k
    return out


def emit(check):
    out = ["; Final Fight (World, MAME set ffight) Z80 sound program, ff_09.12b",
           "; generated by tools/genz80.py", ""]
    out += [f"\t.equ\t{name},0x{addr:x}" for addr, name in sorted(hardware.items())]
    out += ["", "\t.text", ""]
    a = 0
    pending = []

    def flush():
        out.extend(data_lines(bytes(pending)))
        pending.clear()
    while a < FIXED:
        if a in ins_at:
            flush()
            ins = ins_at[a]
            if check:
                out.append(f"\t.org\t0x{a:x}")
            if a in labels:
                out.append(f"{labels[a]}:")
            if a in fallback:
                raw = ",".join(f"0x{b:02x}" for b in rom[a:a + ins.length])
                out.append(f"\t.byte\t{raw}\t; {texts[a]}  [raw: assembler re-encodes]")
            else:
                out.append(f"\t{texts[a]}")
            a += ins.length
            continue
        if a in labels:
            flush()
            out.append(f"{labels[a]}:")
        if jump_tables.get(a):
            flush()
            out.extend(f"\t.word\t{labels[t]}" for t in jump_tables[a])
            a += 2 * len(jump_tables[a])
            continue
        pending.append(rom[a])
        a += 1
    flush()
    out.append("")
    out.append("; banked ROM: file 0x8000-0xbfff is bank 0, 0xc000-0xffff bank 1, both at Z80 0x8000-0xbfff")
    out.extend(data_lines(rom[FIXED:]))
    return "\n".join(out) + "\n"


def build_image(src, td):
    s, o, elf, b = (os.path.join(td, n) for n in ("x.s", "x.o", "x.elf", "x.bin"))
    open(s, "w").write(src)
    p = subprocess.run([ZCROSS + "as", "-march=z80", "-o", o, s], capture_output=True, text=True)
    if p.returncode:
        return p, None
    subprocess.run([ZCROSS + "ld", "-Ttext=0", "-o", elf, o], check=True)
    subprocess.run([ZCROSS + "objcopy", "-O", "binary", "-j", ".text", elf, b], check=True)
    return p, open(b, "rb").read()


with tempfile.TemporaryDirectory() as td:
    roundtrip(emit, lambda src: build_image(src, td), rom, ins_at, fallback)

os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
with open(os.path.join(ROOT, "build", "fallback_z80.txt"), "w") as f:
    for a in sorted(fallback):
        f.write(f"{a:04x}\t{texts[a]}\n")
with open(os.path.join(ROOT, "build", "bad_paths_z80.txt"), "w") as f:
    for a in sorted(set(bad_paths)):
        f.write(f"{a:04x}\n")
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
open(OUT, "w").write(emit(check=False))

code_bytes = sum(i.length for i in ins_at.values())
print(f"instructions: {len(ins_at)}  code bytes: {code_bytes} ({100 * code_bytes / FIXED:.1f}% of the 32 KiB fixed ROM)")
print(f"raw fallback instructions: {len(fallback)}  labels: {len(labels)}  "
      f"inline jump tables: {sum(1 for t in jump_tables.values() if t)}")
print(f"paths stopped at invalid/overlapping code: {len(set(bad_paths))}  unlabelable refs: {len(unlabelable)}")
