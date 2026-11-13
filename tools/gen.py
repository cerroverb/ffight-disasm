#!/usr/bin/env python3
"""Generate src/ffight.s from rom/maincpu.bin.

Code is found by recursive descent from the 68000 vector table plus
tools/entry_points.txt. Everything not reached is emitted as data bytes.
Each instruction is round-trip checked through the assembler (.org check build);
any instruction the assembler does not reproduce exactly is emitted as raw .short
words with the instruction kept as a comment, and listed in build/fallback.txt.

usage: gen.py ROM OUT.s [--check-only]
"""
import os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dis68k import decode

CROSS = os.environ.get("CROSS", "m68k-linux-gnu-")
AS = [CROSS + "as", "-m68000", "--register-prefix-optional"]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

rom = open(sys.argv[1], "rb").read()
OUT = sys.argv[2]
SIZE = len(rom)


def rd32(a):
    return int.from_bytes(rom[a:a + 4], "big")


# ---------------------------------------------------------------- code discovery
entries = set()
vectors = {}
for i in range(256):
    v = rd32(i * 4)
    vectors[i] = v
    if i >= 1 and v < SIZE and not v & 1 and v >= 0x400:
        entries.add(v)
ep_file = os.path.join(ROOT, "tools", "entry_points.txt")
if os.path.exists(ep_file):
    for line in open(ep_file):
        line = line.split("#")[0].strip()
        if line:
            entries.add(int(line, 16))

tr_dir = os.path.join(ROOT, "traces")
if os.path.isdir(tr_dir):
    for fn in sorted(os.listdir(tr_dir)):
        if fn.endswith(".txt"):
            # a run still going rewrites its file now and then: skip a cut last line
            entries |= {int(x, 16) for x in open(os.path.join(tr_dir, fn)) if re.fullmatch(r"[0-9a-fA-F]{6}\n", x)}

owner = [None] * SIZE         # address of instruction covering each byte
ins_at = {}
bad_paths = []
jump_tables = {}              # table address -> targets
seen = set()


def plausible_code(t):
    """True when t starts known code, or decodes as a few instructions in a row."""
    a = t
    for _ in range(4):
        if a >= SIZE or a & 1:
            return False
        if owner[a] is not None:
            return owner[a] == a
        ins = decode(rom, a)
        if ins is None:
            return False
        if ins.flow in ("stop", "jump"):
            return True
        a += ins.length
    return True


def jump_table_targets(table, referenced):
    """Word offsets relative to the table, as in `move.w (T,pc,d0.w),d0; jmp (T,pc,d0.w)`.
    The table ends where its first (lowest) target begins, or at the next address
    referenced by any known instruction (a following data table)."""
    targets = []
    end = min([SIZE] + [r for r in referenced if r > table])
    a = table
    while a + 1 < end and len(targets) < 256:
        w = int.from_bytes(rom[a:a + 2], "big")
        t = table + (w - 0x10000 if w & 0x8000 else w)
        if t & 1 or t <= table or t >= SIZE or not plausible_code(t):
            break
        targets.append(t)
        end = min(end, t)
        a += 2
    jump_tables[table] = targets
    return targets


JT_INDEX = re.compile(r"(jmp|jsr)\t\(PCREL_([0-9A-F]{6}),pc,(d[0-7])\.w\)$")
JT_LOAD = re.compile(r"move\.w\t\(PCREL_([0-9A-F]{6}),pc,(d[0-7])\.w\),(d[0-7])$")

seen = set()


def discover(work):
    """Recursive descent from the given addresses."""
    while work:
        a = work.pop()
        while True:
            if a in seen or a >= SIZE or a & 1:
                break
            if owner[a] is not None:
                if owner[a] != a:
                    bad_paths.append(a)
                break
            ins = decode(rom, a)
            if ins is None or any(owner[b] is not None for b in range(a, a + ins.length)):
                bad_paths.append(a)
                break
            seen.add(a)
            ins_at[a] = ins
            for b in range(a, a + ins.length):
                owner[b] = a
            for t in ins.targets:
                if t < SIZE and not t & 1:
                    work.append(t)
            if ins.flow in ("stop", "jump"):
                break
            a += ins.length


def new_jump_tables(bounds):
    """Targets of jump tables not followed yet: a jmp/jsr through (T,pc,dN.w) whose
    preceding instruction loaded dN from the same table (with any index register)."""
    found = []
    referenced = {addr for ins in ins_at.values() for kind, addr in ins.refs if addr < SIZE}
    referenced |= {t for ins in ins_at.values() for t in ins.targets} | bounds
    for a, ins in sorted(ins_at.items()):
        m = JT_INDEX.match(ins.text)
        if not m or int(m.group(2), 16) in jump_tables:
            continue
        prev = ins_at.get(owner[a - 2]) if a >= 2 and owner[a - 2] is not None else None
        pm = JT_LOAD.match(prev.text) if prev else None
        if pm and pm.group(1) == m.group(2) and pm.group(3) == m.group(3):
            targets = jump_table_targets(int(m.group(2), 16), referenced)
            referenced |= set(targets)
            found += targets
    return found


def discover_all(bounds):
    """Full discovery from scratch. bounds: addresses known to be referenced from an
    earlier pass, so that a jump table processed before the code after it is found
    does not read into that code."""
    owner[:] = [None] * SIZE
    ins_at.clear(); bad_paths.clear(); jump_tables.clear(); seen.clear()
    discover(sorted(entries))
    while True:
        targets = new_jump_tables(bounds)
        if not targets:
            break
        discover(targets)
    refs = {addr for ins in ins_at.values() for kind, addr in ins.refs if addr < SIZE}
    refs |= {t for ins in ins_at.values() for t in ins.targets}
    refs |= {t for targets in jump_tables.values() for t in targets}
    return refs


bounds = set()
for _ in range(10):
    refs = discover_all(bounds)
    if refs <= bounds:
        break
    bounds |= refs

# ---------------------------------------------------------------- labels
labels = {}


def read_table(name):
    """ADDRESS NAME lines from tools/NAME, '#' starts a comment."""
    path = os.path.join(ROOT, "tools", name)
    table = {}
    if os.path.exists(path):
        for line in open(path):
            parts = line.split("#")[0].split()
            if len(parts) >= 2:
                table[int(parts[0], 16)] = parts[1]
    return table


for addr, name in read_table("names.txt").items():
    if addr < SIZE and owner[addr] in (None, addr):
        labels[addr] = name
hardware = read_table("hardware.txt")   # absolute addresses outside the ROM, emitted as .equ
hardware.update(read_table("ram.txt"))


def want_label(addr):
    if addr >= SIZE or addr < 0x400:
        return None     # outside the image, or inside the vector table (emitted as .long)
    if owner[addr] is not None and owner[addr] != addr:
        return None     # middle of an instruction: cannot place a label
    if addr not in labels:
        labels[addr] = (f"loc_{addr:06X}" if addr in ins_at else f"dat_{addr:06X}")
    return labels[addr]


for i, v in vectors.items():
    if i >= 1 and v in ins_at:
        want_label(v)
for table, targets in jump_tables.items():
    if not targets:
        continue        # no plausible entry: the bytes stay data
    want_label(table)
    for t in targets:
        want_label(t)

absolute_refs = []   # placeholders that could not become labels


def resolve(text, ins):
    def sub(m):
        kind, addr = m.group(1), int(m.group(2), 16)
        lab = want_label(addr)
        if lab is None:
            absolute_refs.append((ins.pc, addr))
            return f"0x{addr:x}"
        return lab
    text = re.sub(r"(CODE|PCREL)_([0-9A-F]{6})", sub, text)
    for kind, addr in ins.refs:
        if kind == "absl" and addr < SIZE:
            lab = want_label(addr)
            if lab:
                text = text.replace(f"(0x{addr:x}).l", f"({lab}).l", 1)
        if kind == "absl" and addr in hardware:
            text = text.replace(f"(0x{addr:x}).l", f"({hardware[addr]}).l", 1)
        if kind == "absw" and addr < 0x8000:
            lab = want_label(addr)
            if lab:
                text = text.replace(f"(0x{addr:x}).w", f"({lab}).w", 1)
    return text


texts = {a: resolve(i.text, i) for a, i in sorted(ins_at.items())}
# labels may have been created after some text resolution; second pass is not
# needed because want_label only adds names, never changes existing text.

fallback = set()
fb_path = os.path.join(ROOT, "build", "fallback.txt")


def emit(check):
    out = ["| Final Fight (World, MAME set ffight) 68000 program", "| generated by tools/gen.py", ""]
    out += [f"\t.equ\t{name},0x{addr:x}" for addr, name in sorted(hardware.items())]
    out += ["", "\t.text", ""]
    out.append("| ---- 68000 exception vector table")
    for i in range(256):
        v = vectors[i]
        lab = labels.get(v) if (i >= 1 and v in ins_at) else None
        out.append(f"\t.long\t{lab if lab else f'0x{v:08x}'}\t| vector {i}")
    a = 0x400
    pending = []

    def flush():
        while pending:
            chunk = pending[:16]
            del pending[:16]
            out.append("\t.byte\t" + ",".join(f"0x{b:02x}" for b in chunk))
    while a < SIZE:
        if a in labels and not (a in ins_at):
            flush()
            out.append(f"{labels[a]}:")
        if jump_tables.get(a) and a in labels and a not in ins_at:
            # an empty table would not advance a; the label was written just above
            flush()
            for t in jump_tables[a]:
                out.append(f"\t.short\t{labels[t]}-{labels[a]}")
            a += 2 * len(jump_tables[a])
            continue
        if a in ins_at:
            flush()
            ins = ins_at[a]
            if check:
                out.append(f"\t.org\t0x{a:x}")
            if a in labels:
                out.append(f"{labels[a]}:")
            if a in fallback:
                words = ",".join(f"0x{rom[b] << 8 | rom[b + 1]:04x}" for b in range(a, a + ins.length, 2))
                out.append(f"\t.short\t{words}\t| {texts[a]}  [raw: assembler re-encodes]")
            else:
                out.append(f"\t{texts[a]}")
            a += ins.length
        else:
            pending.append(rom[a])
            a += 1
    flush()
    return "\n".join(out) + "\n"


def assemble(src_text, tmpdir):
    s = os.path.join(tmpdir, "x.s")
    o = os.path.join(tmpdir, "x.o")
    open(s, "w").write(src_text)
    p = subprocess.run(AS + ["-o", o, s], capture_output=True, text=True)
    return p, o


def section_bytes(o, tmpdir):
    b = os.path.join(tmpdir, "x.bin")
    ld = os.path.join(tmpdir, "x.elf")
    subprocess.run([CROSS + "ld", "-n", "-Ttext=0", "-e", "0", "-o", ld, o], check=True)
    subprocess.run([CROSS + "objcopy", "-O", "binary", "-j", ".text", ld, b], check=True)
    return open(b, "rb").read()


with tempfile.TemporaryDirectory() as td:
    for it in range(10):
        src = emit(check=True)
        p, o = assemble(src, td)
        lines = src.split("\n")
        new_fb = set()
        if p.returncode != 0:
            for m in re.finditer(r":(\d+): Error", p.stderr):
                ln = int(m.group(1)) - 1
                # find the instruction address from the nearest preceding .org
                for k in range(ln, -1, -1):
                    mm = re.match(r"\t\.org\t0x([0-9a-f]+)", lines[k])
                    if mm:
                        new_fb.add(int(mm.group(1), 16))
                        break
            if not new_fb:
                sys.exit("assembler failed:\n" + p.stderr[:3000])
        else:
            built = section_bytes(o, td)
            for a, ins in ins_at.items():
                if a in fallback:
                    continue
                if built[a:a + ins.length] != rom[a:a + ins.length]:
                    new_fb.add(a)
        new_fb -= fallback
        print(f"check pass {it}: {len(new_fb)} instructions need raw fallback")
        if not new_fb and p.returncode == 0:
            break
        fallback |= new_fb
    else:
        sys.exit("round-trip check did not converge in 10 passes:\n" + p.stderr[:3000])

os.makedirs(os.path.dirname(fb_path), exist_ok=True)
with open(fb_path, "w") as f:
    for a in sorted(fallback):
        f.write(f"{a:06x}\t{texts[a]}\n")
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
open(OUT, "w").write(emit(check=False))

code_bytes = sum(i.length for i in ins_at.values())
print(f"instructions: {len(ins_at)}  code bytes: {code_bytes} ({100 * code_bytes / SIZE:.1f}% of 1 MiB)")
print(f"raw fallback instructions: {len(fallback)}  labels: {len(labels)}  jump tables: {len(jump_tables)}")
print(f"paths stopped at invalid/overlapping code: {len(bad_paths)}  unlabelable refs: {len(absolute_refs)}")
with open(os.path.join(ROOT, "build", "jump_tables.txt"), "w") as f:
    for t, targets in sorted(jump_tables.items()):
        f.write(f"{t:06x} {len(targets)} entries: " + " ".join(f"{x:06x}" for x in targets) + "\n")
with open(os.path.join(ROOT, "build", "bad_paths.txt"), "w") as f:
    for a in sorted(set(bad_paths)):
        f.write(f"{a:06x}\n")
