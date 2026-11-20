#!/usr/bin/env python3
"""Z80 instruction decoder emitting GNU as Zilog syntax.

decode(mem, pc) -> Ins or None (None = not a documented Z80 instruction).
The table layout follows the x/y/z/p/q opcode field scheme in Cristian Dinu,
"Decoding Z80 Opcodes" (http://www.z80.info/decoding.htm). Undocumented
encodings (IXH/IXL/IYH/IYL, SLL, DDCB register copies, ED aliases, redundant
DD/FD prefixes) are rejected so that a path into data stops early.
Encodings the assembler chooses differently are caught by the generator's
round-trip check, not trusted here.

Code targets are written as CODE_XXXX and memory operands as MEM_XXXX; the
generator replaces them with labels.
"""
from dataclasses import dataclass, field

R = ["b", "c", "d", "e", "h", "l", "(hl)", "a"]
RP = ["bc", "de", "hl", "sp"]
RP2 = ["bc", "de", "hl", "af"]
CC = ["nz", "z", "nc", "c", "po", "pe", "p", "m"]
ALU = ["add a,", "adc a,", "sub ", "sbc a,", "and ", "xor ", "or ", "cp "]
ROT = ["rlc", "rrc", "rl", "rr", "sla", "sra", None, "srl"]   # 6 = SLL, undocumented
X0Z7 = ["rlca", "rrca", "rla", "rra", "daa", "cpl", "scf", "ccf"]
BLI = [["ldi", "cpi", "ini", "outi"], ["ldd", "cpd", "ind", "outd"],
       ["ldir", "cpir", "inir", "otir"], ["lddr", "cpdr", "indr", "otdr"]]


@dataclass
class Ins:
    pc: int
    length: int = 1
    text: str = ""
    flow: str = "next"          # next | stop | call | jump | cond
    targets: list = field(default_factory=list)   # code targets (absolute addresses)
    refs: list = field(default_factory=list)      # (kind, address): "mem" for (nn) operands, "imm" for 16-bit immediates


class Bad(Exception):
    pass


def hx(v):
    return f"0x{v:x}"


class D:
    def __init__(self, mem, pc):
        self.mem = mem
        self.pc = pc
        self.p = pc
        self.ins = Ins(pc)

    def b(self):
        if self.p >= len(self.mem):
            raise Bad
        v = self.mem[self.p]
        self.p += 1
        return v

    def nn(self):
        lo = self.b()
        return lo | self.b() << 8

    def d(self):
        v = self.b()
        return v - 0x100 if v & 0x80 else v

    def target(self, t, flow):
        t &= 0xFFFF
        self.ins.targets.append(t)
        self.ins.flow = flow
        return f"CODE_{t:04X}"

    def mem_nn(self):
        a = self.nn()
        self.ins.refs.append(("mem", a))
        return f"(MEM_{a:04X})"

    def imm_nn(self):
        a = self.nn()
        self.ins.refs.append(("imm", a))
        return hx(a)


def idx_mem(dd, disp):
    return f"({dd}+{disp})" if disp >= 0 else f"({dd}-{-disp})"


def decode_main(s, op, dd):
    """Unprefixed opcode op, or the DD/FD form when dd is "ix"/"iy".
    With dd set, (hl) becomes (dd+d), hl becomes dd, and h/l are undocumented
    unless the same instruction also has the (dd+d) operand."""
    x, y, z = op >> 6, (op >> 3) & 7, op & 7
    p, q = y >> 1, y & 1
    used = {"idx": False}

    def disp_needed(*regs):
        return dd is not None and 6 in regs

    disp = s.d() if disp_needed(*(
        [y] if (x == 0 and z in (4, 5, 6)) else
        [y, z] if (x == 1 and not (y == 6 and z == 6)) else
        [z] if x == 2 else [])) else None

    def r(i, other_has_mem=False):
        if dd is None:
            return R[i]
        if i == 6:
            used["idx"] = True
            return idx_mem(dd, disp)
        if i in (4, 5) and not other_has_mem:
            raise Bad       # IXH/IXL/IYH/IYL
        return R[i]

    def hl():
        if dd is None:
            return "hl"
        used["idx"] = True
        return dd

    def rp(i):
        return hl() if i == 2 else RP[i]

    def rp2(i):
        return hl() if i == 2 else RP2[i]

    t = None
    if x == 0:
        if z == 0:
            if y == 0:
                t = "nop"
            elif y == 1:
                t = "ex af,af'"
            else:
                e = s.d()
                tgt = s.target(s.p + e, "jump" if y == 3 else "cond")
                t = {2: f"djnz {tgt}", 3: f"jr {tgt}"}.get(y) or f"jr {CC[y - 4]},{tgt}"
        elif z == 1:
            t = f"ld {rp(p)},{s.imm_nn()}" if q == 0 else f"add {hl()},{rp(p)}"
        elif z == 2:
            if p == 0:
                t = "ld (bc),a" if q == 0 else "ld a,(bc)"
            elif p == 1:
                t = "ld (de),a" if q == 0 else "ld a,(de)"
            elif p == 2:
                m = s.mem_nn()
                t = f"ld {m},{hl()}" if q == 0 else f"ld {hl()},{m}"
            else:
                m = s.mem_nn()
                t = f"ld {m},a" if q == 0 else f"ld a,{m}"
        elif z == 3:
            t = f"{'inc' if q == 0 else 'dec'} {rp(p)}"
        elif z in (4, 5):
            t = f"{'inc' if z == 4 else 'dec'} {r(y)}"
        elif z == 6:
            dst = r(y)
            t = f"ld {dst},{hx(s.b())}"
        else:
            t = X0Z7[y]
    elif x == 1:
        if y == 6 and z == 6:
            t = "halt"
        else:
            t = f"ld {r(y, z == 6)},{r(z, y == 6)}"
    elif x == 2:
        t = ALU[y] + r(z)
    else:
        if z == 0:
            t = f"ret {CC[y]}"
            s.ins.flow = "next"
        elif z == 1:
            if q == 0:
                t = f"pop {rp2(p)}"
            elif p == 0:
                t = "ret"
                s.ins.flow = "stop"
            elif p == 1:
                t = "exx"
            elif p == 2:
                t = f"jp ({hl()})"
                s.ins.flow = "stop"
            else:
                t = f"ld sp,{hl()}"
        elif z == 2:
            t = f"jp {CC[y]},{s.target(s.nn(), 'cond')}"
        elif z == 3:
            if y == 0:
                t = f"jp {s.target(s.nn(), 'jump')}"
            elif y == 2:
                t = f"out ({hx(s.b())}),a"
            elif y == 3:
                t = f"in a,({hx(s.b())})"
            elif y == 4:
                t = f"ex (sp),{hl()}"
            elif y == 5:
                if dd is not None:
                    raise Bad   # DD EB is ex de,hl with a redundant prefix
                t = "ex de,hl"
            elif y == 6:
                t = "di"
            elif y == 7:
                t = "ei"
            else:
                raise Bad       # CB handled by the caller
        elif z == 4:
            t = f"call {CC[y]},{s.target(s.nn(), 'call')}"
        elif z == 5:
            if q == 0:
                t = f"push {rp2(p)}"
            elif p == 0:
                t = f"call {s.target(s.nn(), 'call')}"
            else:
                raise Bad       # prefixes handled by the caller
        elif z == 6:
            t = ALU[y] + hx(s.b())
        else:
            t = f"rst {hx(y * 8)}"
            s.target(y * 8, "call")
    if dd is not None and not used["idx"]:
        raise Bad               # prefix has no effect: undocumented
    return t


def decode_cb(s, dd):
    disp = s.d() if dd is not None else None
    op = s.b()
    x, y, z = op >> 6, (op >> 3) & 7, op & 7
    if dd is not None:
        if z != 6:
            raise Bad           # DDCB with a register copy: undocumented
        opnd = idx_mem(dd, disp)
    else:
        opnd = R[z]
    if x == 0:
        if ROT[y] is None:
            raise Bad
        return f"{ROT[y]} {opnd}"
    return f"{['', 'bit', 'res', 'set'][x]} {y},{opnd}"


def decode_ed(s):
    op = s.b()
    x, y, z = op >> 6, (op >> 3) & 7, op & 7
    p, q = y >> 1, y & 1
    if x == 1:
        if z == 0 and y != 6:
            return f"in {R[y]},(c)"
        if z == 1 and y != 6:
            return f"out (c),{R[y]}"
        if z == 2:
            return f"{'sbc' if q == 0 else 'adc'} hl,{RP[p]}"
        if z == 3:
            m = s.mem_nn()
            return f"ld {m},{RP[p]}" if q == 0 else f"ld {RP[p]},{m}"
        if z == 4 and y == 0:
            return "neg"
        if z == 5 and y in (0, 1):
            s.ins.flow = "stop"
            return "retn" if y == 0 else "reti"
        if z == 6 and y in (0, 2, 3):
            return f"im {[0, None, 1, 2][y]}"
        if z == 7 and y <= 5:
            return ["ld i,a", "ld r,a", "ld a,i", "ld a,r", "rrd", "rld"][y]
    if x == 2 and z <= 3 and y >= 4:
        return BLI[y - 4][z]
    raise Bad


def decode(mem, pc):
    s = D(mem, pc)
    try:
        op = s.b()
        dd = None
        if op in (0xDD, 0xFD):
            dd = "ix" if op == 0xDD else "iy"
            op = s.b()
            if op in (0xDD, 0xED, 0xFD):
                raise Bad
        if op == 0xCB:
            s.ins.text = decode_cb(s, dd)
        elif op == 0xED:
            s.ins.text = decode_ed(s)
        else:
            s.ins.text = decode_main(s, op, dd)
    except Bad:
        return None
    s.ins.length = s.p - pc
    return s.ins
