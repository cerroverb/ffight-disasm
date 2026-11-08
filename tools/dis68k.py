#!/usr/bin/env python3
"""68000 instruction decoder emitting GNU as (Motorola syntax, --register-prefix-optional).

decode(mem, pc) -> Ins or None (None = not a valid 68000 instruction).
Every operand size is explicit so the assembler has no encoding choices to make.
Encodings the assembler still re-chooses are caught by the build round-trip check,
not trusted here.
"""
from dataclasses import dataclass, field

COND = ["t", "f", "hi", "ls", "cc", "cs", "ne", "eq", "vc", "vs", "pl", "mi", "ge", "lt", "gt", "le"]
SZ = {0: "b", 1: "w", 2: "l"}


def areg(n):
    return "sp" if n == 7 else f"a{n}"


def hx(v):
    return f"0x{v:x}" if v >= 0 else f"-0x{-v:x}"


def s8(v):
    return v - 0x100 if v & 0x80 else v


def s16(v):
    return v - 0x10000 if v & 0x8000 else v


@dataclass
class Ins:
    pc: int
    length: int = 2
    text: str = ""
    flow: str = "next"          # next | stop | branch | call | jump | cond
    targets: list = field(default_factory=list)   # code targets (absolute addresses)
    refs: list = field(default_factory=list)      # (kind, address) for label substitution


class Bad(Exception):
    pass


class D:
    def __init__(self, mem, pc):
        self.mem = mem
        self.pc = pc
        self.p = pc + 2
        self.ins = Ins(pc)

    def w(self):
        if self.p + 2 > len(self.mem):
            raise Bad
        v = (self.mem[self.p] << 8) | self.mem[self.p + 1]
        self.p += 2
        return v

    def l(self):
        return (self.w() << 16) | self.w()

    def imm(self, size):
        if size == "b":
            v = self.w()
            if v & 0xFF00 == 0xFF00 and v & 0x80:
                return f"#{hx(s8(v & 0xFF))}"    # sign-extended byte immediate, e.g. 0xFFFF = #-1
            if v & 0xFF00:
                raise Bad
            return f"#{hx(v)}"
        if size == "w":
            return f"#{hx(self.w())}"
        return f"#{hx(self.l())}"

    def ea(self, mode, reg, size, allow):
        """allow: set of class letters. d=Dn a=An m=memory p=pc-relative i=immediate"""
        if mode == 0:
            if "d" not in allow:
                raise Bad
            return f"d{reg}"
        if mode == 1:
            if "a" not in allow or size == "b":
                raise Bad
            return areg(reg)
        if mode == 7 and reg == 4:
            if "i" not in allow:
                raise Bad
            return self.imm(size)
        if mode == 7 and reg in (2, 3):
            if "p" not in allow:
                raise Bad
        elif mode >= 2 and mode <= 7:
            if "m" not in allow and not ("c" in allow and mode in (2, 5, 6, 7)):
                raise Bad
        if mode == 2:
            return f"({areg(reg)})"
        if mode == 3:
            if "c" in allow and "m" not in allow:
                raise Bad
            return f"({areg(reg)})+"
        if mode == 4:
            if "c" in allow and "m" not in allow:
                raise Bad
            return f"-({areg(reg)})"
        if mode == 5:
            d = s16(self.w())
            return f"({hx(d)},{areg(reg)})"
        if mode == 6:
            return f"({hx(self.idx_disp())},{areg(reg)},{self.idx_reg})"
        if mode == 7:
            if reg == 0:
                v = self.w()
                a = v | 0xFFFF0000 if v & 0x8000 else v
                self.ins.refs.append(("absw", a & 0xFFFFFF))
                return f"({hx(v)}).w"
            if reg == 1:
                v = self.l()
                self.ins.refs.append(("absl", v))
                return f"({hx(v)}).l"
            if reg == 2:
                base = self.p
                d = s16(self.w())
                t = base + d
                self.ins.refs.append(("pcrel", t))
                return f"(PCREL_{t:06X},pc)"
            if reg == 3:
                base = self.p
                d = self.idx_disp()
                t = base + d
                self.ins.refs.append(("pcrel", t))
                return f"(PCREL_{t:06X},pc,{self.idx_reg})"
        raise Bad

    def idx_disp(self):
        e = self.w()
        if e & 0x0700:          # 68000 brief format only: bits 10-8 must be 0
            raise Bad
        r = (e >> 12) & 7
        rn = areg(r) if e & 0x8000 else f"d{r}"
        self.idx_reg = f"{rn}.{'l' if e & 0x0800 else 'w'}"
        return s8(e & 0xFF)


def reglist(mask, predec):
    if predec:
        mask = int(f"{mask:016b}"[::-1], 2)
    names = [f"d{i}" for i in range(8)] + [f"a{i}" for i in range(8)]
    out, i = [], 0
    while i < 16:
        if mask & (1 << i):
            j = i
            while j + 1 < 16 and mask & (1 << (j + 1)) and (j + 1) // 8 == i // 8:
                j += 1
            out.append(names[i] if i == j else f"{names[i]}-{names[j]}")
            i = j + 1
        else:
            i += 1
    if not out:
        raise Bad
    return "/".join(out)


DA = set("dam")        # data or address register, memory (no pc, no imm) = alterable
DALT = set("dm")       # data alterable
ANY = set("dampi")
DATA = set("dmpi")      # data addressing (no An)
MALT = set("m")         # memory alterable
CTRL = set("cp")        # control (incl pc-relative)
CTRL_NOPC = set("c")


def decode(mem, pc):
    if pc & 1 or pc + 2 > len(mem):
        return None
    d = D(mem, pc)
    try:
        _decode(d, (mem[pc] << 8) | mem[pc + 1])
    except Bad:
        return None
    d.ins.length = d.p - pc
    return d.ins


def _decode(d, op):
    I = d.ins
    top = op >> 12
    mode, reg = (op >> 3) & 7, op & 7
    rx = (op >> 9) & 7
    szb = (op >> 6) & 3

    def setx(t, flow="next"):
        I.text = t
        I.flow = flow

    if top == 0:
        if op & 0x0100 and mode == 1:
            o = (op >> 6) & 3
            s = "w" if o in (0, 2) else "l"
            disp = s16(d.w())
            mem_ = f"({hx(disp)},{areg(reg)})"
            return setx(f"movep.{s}\t{mem_},d{rx}" if o < 2 else f"movep.{s}\td{rx},{mem_}")
        names = ["btst", "bchg", "bclr", "bset"]
        if op & 0x0100:
            n = names[szb]
            allow = set("dmpi") if n == "btst" else DALT
            if n == "btst" and mode == 7 and reg == 4:
                return setx(f"btst\td{rx},{d.imm('b')}")
            return setx(f"{n}\td{rx},{d.ea(mode, reg, 'b', allow)}")
        if (op & 0x0F00) == 0x0800:
            n = names[szb]
            b = d.w()
            if b & 0xFF00:
                raise Bad
            allow = set("dmp") if n == "btst" else DALT
            return setx(f"{n}\t#{b},{d.ea(mode, reg, 'b', allow)}")
        imm_names = {0: "ori", 1: "andi", 2: "subi", 3: "addi", 5: "eori", 6: "cmpi"}
        k = (op >> 9) & 7
        if k not in imm_names or szb == 3:
            raise Bad
        n, s = imm_names[k], SZ[szb]
        if mode == 7 and reg == 4:
            if n in ("ori", "andi", "eori") and s in ("b", "w"):
                v = d.w()
                if s == "b":
                    if v & 0xFF00:
                        raise Bad
                    return setx(f"{n}.b\t#{hx(v)},ccr")
                return setx(f"{n}.w\t#{hx(v)},sr")
            raise Bad
        src = d.imm(s)
        allow = set("dmp") if n == "cmpi" else DALT
        if n == "cmpi" and mode == 7 and reg in (2, 3):
            raise Bad   # cmpi to pc-relative is 68020+
        return setx(f"{n}.{s}\t{src},{d.ea(mode, reg, s, allow)}")

    if top in (1, 2, 3):
        s = {1: "b", 3: "w", 2: "l"}[top]
        src = d.ea(mode, reg, s, ANY)
        dmode, dreg = (op >> 6) & 7, rx
        if dmode == 1:
            if s == "b":
                raise Bad
            return setx(f"movea.{s}\t{src},{areg(dreg)}")
        return setx(f"move.{s}\t{src},{d.ea(dmode, dreg, s, DALT)}")

    if top == 4:
        if (op & 0x01C0) == 0x01C0:
            return setx(f"lea\t{d.ea(mode, reg, 'l', CTRL)},{areg(rx)}")
        if (op & 0x01C0) == 0x0180:
            return setx(f"chk.w\t{d.ea(mode, reg, 'w', DATA)},d{rx}")
        hi = (op >> 8) & 0xF
        if hi in (0, 2, 4, 6):
            if szb == 3:
                if hi == 0:
                    return setx(f"move.w\tsr,{d.ea(mode, reg, 'w', DALT)}")
                if hi == 4:
                    return setx(f"move.w\t{d.ea(mode, reg, 'w', DATA)},ccr")
                if hi == 6:
                    return setx(f"move.w\t{d.ea(mode, reg, 'w', DATA)},sr")
                raise Bad
            n = {0: "negx", 2: "clr", 4: "neg", 6: "not"}[hi]
            s = SZ[szb]
            return setx(f"{n}.{s}\t{d.ea(mode, reg, s, DALT)}")
        if hi == 8:
            if szb == 0:
                return setx(f"nbcd.b\t{d.ea(mode, reg, 'b', DALT)}")
            if szb == 1:
                if mode == 0:
                    return setx(f"swap\td{reg}")
                return setx(f"pea\t{d.ea(mode, reg, 'l', CTRL)}")
            if mode == 0:
                return setx(f"ext.{'w' if szb == 2 else 'l'}\td{reg}")
            s = "w" if szb == 2 else "l"
            mask = d.w()
            if mode in (3,) or mode == 7 and reg in (2, 3, 4):
                raise Bad
            allow = set("m") if mode == 4 else CTRL_NOPC
            ea = d.ea(mode, reg, s, allow)
            return setx(f"movem.{s}\t{reglist(mask, mode == 4)},{ea}")
        if hi == 0xA:
            if op == 0x4AFC:
                return setx("illegal", "stop")
            if szb == 3:
                return setx(f"tas.b\t{d.ea(mode, reg, 'b', DALT)}")
            s = SZ[szb]
            return setx(f"tst.{s}\t{d.ea(mode, reg, s, DALT)}")
        if hi == 0xC:
            if szb in (2, 3):
                s = "w" if szb == 2 else "l"
                mask = d.w()
                if mode == 4 or mode == 7 and reg == 4:
                    raise Bad
                allow = set("cp") | ({"m"} if mode == 3 else set())
                ea = d.ea(mode, reg, s, allow)
                return setx(f"movem.{s}\t{ea},{reglist(mask, False)}")
            raise Bad
        if hi == 0xE:
            if 0x4E40 <= op <= 0x4E4F:
                return setx(f"trap\t#{op & 0xF}")
            if 0x4E50 <= op <= 0x4E57:
                return setx(f"link.w\t{areg(reg)},#{hx(s16(d.w()))}")
            if 0x4E58 <= op <= 0x4E5F:
                return setx(f"unlk\t{areg(reg)}")
            if 0x4E60 <= op <= 0x4E67:
                return setx(f"move.l\t{areg(reg)},usp")
            if 0x4E68 <= op <= 0x4E6F:
                return setx(f"move.l\tusp,{areg(reg)}")
            simple = {0x4E70: ("reset", "next"), 0x4E71: ("nop", "next"), 0x4E73: ("rte", "stop"),
                      0x4E75: ("rts", "stop"), 0x4E76: ("trapv", "next"), 0x4E77: ("rtr", "stop")}
            if op in simple:
                return setx(*simple[op])
            if op == 0x4E72:
                return setx(f"stop\t#{hx(d.w())}")
            if (op & 0xFFC0) in (0x4E80, 0x4EC0):
                n = "jsr" if (op & 0xFFC0) == 0x4E80 else "jmp"
                ea = d.ea(mode, reg, "l", CTRL)
                tgt = None
                if mode == 7 and reg in (0, 1, 2):
                    k, a = I.refs[-1]
                    tgt = a
                if tgt is not None:
                    I.targets.append(tgt)
                return setx(f"{n}\t{ea}", "call" if n == "jsr" else ("jump" if tgt is not None else "stop"))
        raise Bad

    if top == 5:
        if szb == 3:
            c = COND[(op >> 8) & 0xF]
            if mode == 1:
                base = d.p
                t = base + s16(d.w())
                I.targets.append(t)
                return setx(f"db{c}\td{reg},CODE_{t:06X}", "cond")
            return setx(f"s{c}\t{d.ea(mode, reg, 'b', DALT)}")
        n = "subq" if op & 0x0100 else "addq"
        q = rx or 8
        s = SZ[szb]
        return setx(f"{n}.{s}\t#{q},{d.ea(mode, reg, s, DA)}")

    if top == 6:
        c = (op >> 8) & 0xF
        disp = op & 0xFF
        base = d.p
        if disp == 0:
            t = base + s16(d.w())
            sfx = "w"
        elif disp == 0xFF:
            raise Bad          # 68020 long branch
        else:
            t = base + s8(disp)
            sfx = "s"
        I.targets.append(t)
        if c == 0:
            return setx(f"bra.{sfx}\tCODE_{t:06X}", "jump")
        if c == 1:
            return setx(f"bsr.{sfx}\tCODE_{t:06X}", "call")
        return setx(f"b{COND[c]}.{sfx}\tCODE_{t:06X}", "cond")

    if top == 7:
        if op & 0x0100:
            raise Bad
        return setx(f"moveq\t#{s8(op & 0xFF)},d{rx}")

    if top in (8, 9, 0xB, 0xC, 0xD):
        opm = (op >> 6) & 7
        if top == 8:
            if opm == 3:
                return setx(f"divu.w\t{d.ea(mode, reg, 'w', DATA)},d{rx}")
            if opm == 7:
                return setx(f"divs.w\t{d.ea(mode, reg, 'w', DATA)},d{rx}")
            if opm == 4 and mode in (0, 1):
                return setx(f"sbcd.b\td{reg},d{rx}" if mode == 0 else f"sbcd.b\t-({areg(reg)}),-({areg(rx)})")
            return logic(d, "or", opm, mode, reg, rx)
        if top == 0xC:
            if opm == 3:
                return setx(f"mulu.w\t{d.ea(mode, reg, 'w', DATA)},d{rx}")
            if opm == 7:
                return setx(f"muls.w\t{d.ea(mode, reg, 'w', DATA)},d{rx}")
            if opm == 4 and mode in (0, 1):
                return setx(f"abcd.b\td{reg},d{rx}" if mode == 0 else f"abcd.b\t-({areg(reg)}),-({areg(rx)})")
            if opm == 5 and mode == 0:
                return setx(f"exg\td{rx},d{reg}")
            if opm == 5 and mode == 1:
                return setx(f"exg\t{areg(rx)},{areg(reg)}")
            if opm == 6 and mode == 1:
                return setx(f"exg\td{rx},{areg(reg)}")
            return logic(d, "and", opm, mode, reg, rx)
        if top in (9, 0xD):
            n = "sub" if top == 9 else "add"
            if opm in (3, 7):
                s = "w" if opm == 3 else "l"
                return setx(f"{n}a.{s}\t{d.ea(mode, reg, s, ANY)},{areg(rx)}")
            if opm >= 4 and mode in (0, 1):
                s = SZ[opm - 4]
                return setx(f"{n}x.{s}\td{reg},d{rx}" if mode == 0 else f"{n}x.{s}\t-({areg(reg)}),-({areg(rx)})")
            s = SZ[opm & 3]
            if opm < 4:
                return setx(f"{n}.{s}\t{d.ea(mode, reg, s, ANY)},d{rx}")
            return setx(f"{n}.{s}\td{rx},{d.ea(mode, reg, s, MALT)}")
        if top == 0xB:
            if opm in (3, 7):
                s = "w" if opm == 3 else "l"
                return setx(f"cmpa.{s}\t{d.ea(mode, reg, s, ANY)},{areg(rx)}")
            if opm < 4:
                s = SZ[opm]
                return setx(f"cmp.{s}\t{d.ea(mode, reg, s, ANY)},d{rx}")
            s = SZ[opm - 4]
            if mode == 1:
                return setx(f"cmpm.{s}\t({areg(reg)})+,({areg(rx)})+")
            return setx(f"eor.{s}\td{rx},{d.ea(mode, reg, s, DALT)}")

    if top == 0xE:
        names = ["as", "ls", "rox", "ro"]
        if szb == 3:
            if op & 0x0800:
                raise Bad
            n = names[(op >> 9) & 3] + ("l" if op & 0x0100 else "r")
            return setx(f"{n}.w\t{d.ea(mode, reg, 'w', MALT)}")
        n = names[(op >> 3) & 3] + ("l" if op & 0x0100 else "r")
        s = SZ[szb]
        if op & 0x20:
            return setx(f"{n}.{s}\td{rx},d{reg}")
        return setx(f"{n}.{s}\t#{rx or 8},d{reg}")

    raise Bad   # line A / line F


def logic(d, n, opm, mode, reg, rx):
    if opm == 3 or opm == 7:
        raise Bad
    s = SZ[opm & 3]
    if opm < 4:
        d.ins.text = f"{n}.{s}\t{d.ea(mode, reg, s, DATA)},d{rx}"
    else:
        d.ins.text = f"{n}.{s}\td{rx},{d.ea(mode, reg, s, MALT)}"
    d.ins.flow = "next"
