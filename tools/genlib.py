"""CPU-independent parts of the source generators (tools/gen.py, tools/genz80.py)."""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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


def read_addresses(name):
    """One hex address per line from tools/NAME, '#' starts a comment."""
    path = os.path.join(ROOT, "tools", name)
    if not os.path.exists(path):
        return set()
    return {int(x, 16) for x in (line.split("#")[0].strip() for line in open(path)) if x}


def read_traces(subdir, digits):
    """Executed PCs from every traces/SUBDIR/*.txt file (SUBDIR "" for traces/ itself).
    A run still going rewrites its file now and then: a cut last line is skipped."""
    tr_dir = os.path.join(ROOT, "traces", subdir)
    pcs = set()
    if os.path.isdir(tr_dir):
        for fn in sorted(os.listdir(tr_dir)):
            if fn.endswith(".txt"):
                pcs |= {int(x, 16) for x in open(os.path.join(tr_dir, fn))
                        if re.fullmatch(f"[0-9a-fA-F]{{{digits}}}\n", x)}
    return pcs


def discover(rom, decode, work, align, owner, ins_at, seen, bad_paths):
    """Recursive descent from the addresses in work. Fills owner (address of the
    instruction covering each byte), ins_at, seen and bad_paths (paths that ran
    into an invalid or overlapping instruction)."""
    size = len(rom)
    while work:
        a = work.pop()
        while True:
            if a in seen or a >= size or a % align:
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
                if t < size and not t % align:
                    work.append(t)
            if ins.flow in ("stop", "jump"):
                break
            a += ins.length


def roundtrip(emit, build, rom, ins_at, fallback):
    """Assemble emit(check=True) (which places a `.org 0xADDR` before every
    instruction) until every instruction not in fallback reproduces the ROM bytes.
    build(src) -> (CompletedProcess of the assembler, built image or None).
    Adds failing instruction addresses to fallback; exits if it does not converge."""
    for it in range(10):
        src = emit(check=True)
        p, built = build(src)
        lines = src.split("\n")
        new_fb = set()
        if p.returncode != 0:
            for m in re.finditer(r":(\d+): Error", p.stderr):
                ln = int(m.group(1)) - 1
                # the instruction address is in the nearest preceding .org
                for k in range(ln, -1, -1):
                    mm = re.match(r"\t\.org\t0x([0-9a-f]+)", lines[k])
                    if mm:
                        new_fb.add(int(mm.group(1), 16))
                        break
            if not new_fb:
                sys.exit("assembler failed:\n" + p.stderr[:3000])
        else:
            for a, ins in ins_at.items():
                if a not in fallback and built[a:a + ins.length] != rom[a:a + ins.length]:
                    new_fb.add(a)
        new_fb -= fallback
        print(f"check pass {it}: {len(new_fb)} instructions need raw fallback")
        if not new_fb and p.returncode == 0:
            return
        fallback |= new_fb
    sys.exit("round-trip check did not converge in 10 passes:\n" + p.stderr[:3000])
