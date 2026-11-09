#!/usr/bin/env python3
"""Compare two per-frame dumps of the CPS2 68000 work RAM (65536 bytes a frame).

The reference (MAME) frames are paired with identical frames of the other run (cps2recomp),
as in cps2recomp's docs/ARCADE_ACCURACY.md: each pair must lie within --window frames of the
previous pair, so a fixed offset between the two runs (boot timing) is allowed and reported.

Prints a report and exits 0 when no lasting divergence was found, 1 when one was, 2 on error.

  compare.py REFERENCE.bin OTHER.bin [--exclude 7C00-7FFF ...] [--window 30] [--lasting 30]
             [--names avsp.h] [--offset-only --before FRAME] [--json FILE]
"""
import argparse
import bisect
import hashlib
import json
import os
import re
import sys
from collections import Counter

FRAME = 0x10000
BASE = 0xFF0000


def parse_range(text):
    first, _, last = text.partition("-")
    low = int(first, 16) & 0xFFFF
    high = int(last or first, 16) & 0xFFFF
    if high < low:
        raise argparse.ArgumentTypeError("bad range " + text)
    return low, high


def frame_count(path):
    size = os.path.getsize(path)
    if size % FRAME:
        print(f"warning: {path} is not a whole number of frames ({size} bytes); the last part is ignored",
              file=sys.stderr)
    return size // FRAME


def masked(data, excludes):
    if not excludes:
        return data
    buf = bytearray(data)
    for low, high in excludes:
        buf[low:high + 1] = bytes(high - low + 1)
    return bytes(buf)


def hashes(path, excludes):
    out = []
    with open(path, "rb") as f:
        for _ in range(frame_count(path)):
            out.append(hashlib.blake2b(masked(f.read(FRAME), excludes), digest_size=16).digest())
    return out


def read_frame(path, index):
    with open(path, "rb") as f:
        f.seek(index * FRAME)
        return f.read(FRAME)


def load_names(path):
    """Work RAM addresses named in a header's 'constexpr uint32_t kName = EXPR, kOther = EXPR;' lines,
    where EXPR is a hex number or an earlier name, plus or minus hex numbers (kVars + 0x18C)."""
    names = {}
    if not path:
        return names
    values = {}
    decl = re.compile(r"constexpr\s+uint32_t\s+([^;]*);")
    item = re.compile(r"^\s*(\w+)\s*=\s*(.+?)\s*$")
    term = re.compile(r"([+-]?)\s*(0x[0-9A-Fa-f]+|\d+|\w+)")
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = decl.search(line.split("//")[0])
            if not m:
                continue
            for part in m.group(1).split(","):
                im = item.match(part)
                if not im:
                    continue
                total, ok = 0, True
                for sign, tok in term.findall(im.group(2)):
                    if tok in values:
                        v = values[tok]
                    elif re.fullmatch(r"0x[0-9A-Fa-f]+|\d+", tok):
                        v = int(tok, 0)
                    else:
                        ok = False
                        break
                    total += -v if sign == "-" else v
                if ok:
                    values[im.group(1)] = total
                    if 0xFF0000 <= total <= 0xFFFFFF:
                        names[total] = im.group(1)
    return names


def name_of(address, names):
    best = None
    for start in names:
        if start <= address and (best is None or start > best):
            best = start
    if best is None or address - best > 3:
        return ""
    return names[best] + (f"+{address - best:X}" if address != best else "")


def diff_count(a, b):
    """Bytes that differ between two frames."""
    x = int.from_bytes(a, "big") ^ int.from_bytes(b, "big")
    return FRAME - x.to_bytes(FRAME, "big").count(0)


def nearest(ref_path, other_path, i, offset, window, other_frames, excludes):
    """The other run's frame within window of i - offset that differs from reference frame i in the fewest bytes."""
    r = masked(read_frame(ref_path, i), excludes)
    best = (None, FRAME + 1)
    with open(other_path, "rb") as f:
        for j in range(max(0, i - offset - window), min(other_frames, i - offset + window + 1)):
            f.seek(j * FRAME)
            count = diff_count(r, masked(f.read(FRAME), excludes))
            if count < best[1] or (count == best[1] and abs(j - (i - offset)) < abs(best[0] - (i - offset))):
                best = (j, count)
    return best


def track(ref, other, window, first_window):
    """For each reference frame, the index of the paired frame of the other run, or None."""
    where = {}
    for j, h in enumerate(other):
        where.setdefault(h, []).append(j)
    pairs = []
    last = None  # (reference index, other index) of the previous pair
    for i, h in enumerate(ref):
        js = where.get(h, ())
        if last is None:
            low, high, expected = max(0, i - first_window), i + first_window, i
        else:
            expected = last[1] + (i - last[0])  # same offset as the previous pair
            low, high = max(last[1], expected - window), expected + window
        found = None
        k = bisect.bisect_left(js, low)
        while k < len(js) and js[k] <= high:
            if found is None or abs(js[k] - expected) < abs(found - expected):
                found = js[k]
            k += 1
        pairs.append(found)
        if found is not None:
            last = (i, found)
    return pairs


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("reference")
    ap.add_argument("other")
    ap.add_argument("--exclude", action="append", type=parse_range, default=None,
                    help="work RAM range left out, hex offsets or addresses (default: 7C00-7FFF, the stack, "
                         "and 0118, the state byte of task 6, which flips between running and ready within a frame)")
    ap.add_argument("--window", type=int, default=30,
                    help="most frames a pair may be from the offset of the previous pair (30)")
    ap.add_argument("--first-window", type=int, default=120, help="most offset allowed for the first pair (120)")
    ap.add_argument("--lasting", type=int, default=30,
                    help="unpaired reference frames in a row that count as a lasting divergence (30)")
    ap.add_argument("--names", help="header with work RAM names (cps2recomp games/avsp/src/avsp.h)")
    ap.add_argument("--max-diffs", type=int, default=40, help="differing bytes listed (40)")
    ap.add_argument("--offset-only", action="store_true",
                    help="print only the offset (reference index minus other index) of the last pair and exit")
    ap.add_argument("--before", type=int, default=None, help="with --offset-only: the last pair before this frame")
    ap.add_argument("--after", type=int, default=300,
                    help="after a lasting divergence, frames looked at for the nearest frame of the other run (300)")
    ap.add_argument("--json", help="also write the summary as JSON")
    a = ap.parse_args()
    excludes = a.exclude if a.exclude is not None else [(0x7C00, 0x7FFF), (0x0118, 0x0118)]

    for p in (a.reference, a.other):
        if not os.path.exists(p) or frame_count(p) == 0:
            print(f"error: {p} has no frames", file=sys.stderr)
            return 2

    ref = hashes(a.reference, excludes)
    other = hashes(a.other, excludes)
    pairs = track(ref, other, a.window, a.first_window)

    offsets = Counter(i - j for i, j in enumerate(pairs) if j is not None)
    if a.offset_only:
        # (the offset grows during the boot tests when the two runs' speeds differ: the last one is the one input meets)
        last = [i - j for i, j in enumerate(pairs) if j is not None and (a.before is None or i < a.before)]
        print(last[-1] if last else 0)
        return 0

    matched = sum(1 for j in pairs if j is not None)
    first_pair = next((i for i, j in enumerate(pairs) if j is not None), None)

    # lasting divergence: --lasting unpaired frames in a row, counted from the first pair on
    divergence = None
    run = 0
    for i in range(first_pair or 0, len(pairs)):
        if pairs[i] is None:
            run += 1
            if run == a.lasting:
                divergence = i - a.lasting + 1
                break
        else:
            run = 0
    isolated = 0
    stop = divergence if divergence is not None else len(pairs)
    for i in range(first_pair or 0, stop):
        if pairs[i] is None:
            isolated += 1

    print(f"reference frames        {len(ref)}  ({a.reference})")
    print(f"other frames            {len(other)}  ({a.other})")
    print(f"excluded work RAM       " + ", ".join(f"{BASE + lo:06X}-{BASE + hi:06X}" for lo, hi in excludes))
    print(f"paired frames           {matched} of {len(ref)}")
    print(f"first pair              " + ("none" if first_pair is None else f"reference {first_pair} = other {pairs[first_pair]}"))
    print(f"offsets (ref - other)   " + (", ".join(f"{o:+d} x{n}" for o, n in offsets.most_common(5)) or "none"))
    print(f"unpaired, then paired   {isolated}  (isolated frames before any lasting divergence)")
    if divergence is None:
        print("lasting divergence      none")
    else:
        print(f"lasting divergence      from reference frame {divergence} ({a.lasting} or more unpaired in a row)")

    detail = None
    if divergence is not None or first_pair is None:
        # the frame to look at, and the other run's frame nearest to it (fewest differing bytes) around the offset
        # of the last pair
        i = divergence if divergence is not None else 0
        last = next(((k, pairs[k]) for k in range(i - 1, -1, -1) if pairs[k] is not None), None)
        offset = (last[0] - last[1]) if last else 0
        j, _ = nearest(a.reference, a.other, i, offset, a.window, len(other), excludes)
        names = load_names(a.names)
        r = masked(read_frame(a.reference, i), excludes)
        o = masked(read_frame(a.other, j), excludes)
        diffs = [k for k in range(FRAME) if r[k] != o[k]]
        print(f"\nbytes differing at reference frame {i} against other frame {j}: {len(diffs)}")
        print("  address  ref  other  name")
        for k in diffs[:a.max_diffs]:
            print(f"  {BASE + k:06X}   {r[k]:02X}   {o[k]:02X}    {name_of(BASE + k, names)}")
        if len(diffs) > a.max_diffs:
            print(f"  ... {len(diffs) - a.max_diffs} more")
        detail = {"reference_frame": i, "other_frame": j, "bytes_differing": len(diffs),
                  "first": [{"address": f"{BASE + k:06X}", "ref": r[k], "other": o[k]} for k in diffs[:a.max_diffs]]}
        # after it: whether the runs stay a few bytes apart (a frame counter, a lag frame) or part for good
        print(f"\nafter the divergence, the other run's nearest frame (fewest differing bytes, within {a.window} frames):")
        print("  ref frame  other frame  offset  bytes differing  addresses")
        later = []
        step = max(1, a.after // 10)
        for k in range(i, min(len(ref), i + a.after + 1), step):
            jk, count = nearest(a.reference, a.other, k, offset, a.window, len(other), excludes)
            if jk is None:
                break
            rk = masked(read_frame(a.reference, k), excludes)
            ok = masked(read_frame(a.other, jk), excludes)
            where = [f"{BASE + n:06X}" for n in range(FRAME) if rk[n] != ok[n]][:6]
            print(f"  {k:9}  {jk:11}  {k - jk:+6}  {count:15}  {' '.join(where)}{' ...' if count > 6 else ''}")
            later.append({"reference_frame": k, "other_frame": jk, "bytes_differing": count})
            offset = k - jk
        detail["after"] = later

    if a.json:
        with open(a.json, "w") as f:
            json.dump({"reference_frames": len(ref), "other_frames": len(other), "paired": matched,
                       "first_pair": first_pair, "offsets": dict(offsets.most_common(5)),
                       "isolated_unpaired": isolated, "lasting_divergence": divergence, "detail": detail}, f, indent=1)
    return 1 if divergence is not None or first_pair is None else 0


if __name__ == "__main__":
    sys.exit(main())
