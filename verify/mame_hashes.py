"""Expected chip SHA-1 values, read from MAME's own src/mame/capcom/cps1.cpp.

The answer key is not stored in this repository: the Makefile downloads
cps1.cpp from github.com/mamedev/mame at a pinned commit, and this module
reads ROM_START( ffight ) from it.

region_hashes(path, region) -> {chip name: sha1} for one ROM_REGION, e.g.
"maincpu" or "audiocpu". Exits if the set or the region is not found.
"""
import re, sys

ROM_SET = "ffight"


def region_hashes(path, region):
    text = open(path, encoding="utf-8", errors="replace").read()
    m = re.search(r"ROM_START\(\s*" + ROM_SET + r"\s*\)(.*?)ROM_END", text, re.S)
    if not m:
        sys.exit(f"FAIL ROM_START( {ROM_SET} ) not found in {path}")
    chips, current = {}, None
    for line in m.group(1).splitlines():
        r = re.search(r'ROM_REGION\w*\(\s*[^,]+,\s*"([^"]+)"', line)
        if r:
            current = r.group(1)
            continue
        c = re.search(r'ROM_LOAD\w*\(\s*"([^"]+)".*SHA1\(([0-9a-f]{40})\)', line)
        if c and current == region:
            chips[c.group(1)] = c.group(2)
    if not chips:
        sys.exit(f"FAIL no chips for region {region} in ROM_START( {ROM_SET} ) in {path}")
    return chips
