#!/usr/bin/env python3
# Reads a MAME debugger trace stream and writes the sorted set of executed 68000 PCs.
import re, sys
pcs = set()
rx = re.compile(r'([0-9A-F]{6}): ')
for line in open(sys.argv[1], errors='replace'):
    m = rx.match(line)
    if m:
        pcs.add(int(m.group(1), 16))
open(sys.argv[2], 'w').write(''.join(f'{p:06x}\n' for p in sorted(pcs)))
print('unique pcs', len(pcs))
