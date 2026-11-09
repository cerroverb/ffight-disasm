# CPS2 tooling for Alien vs. Predator (MAME set `avsp`): disassembly, rebuild, assets, native port

Research date: 2026-11-09. Sources were read directly where the session's network allowed it: GitHub raw files of MAME master, FBNeo master, cps2recomp main and several small repos, plus GitHub repository search. sun.hasenbraten.de (vasm), john.ccac.rwth-aachen.de (AS), docs.mamedev.org, fabiensanglard.net and demo.gitea.com were blocked or did not resolve. Claims about those come from search snippets or are listed under Gaps. No ROMs were downloaded.

**Most important finding:** a native, statically recompiled PC port of Alien vs. Predator already exists. **cps2recomp** (GPL-3.0-only) supports Linux and is in beta for `avspu`. It produces C++, not reassemblable assembly, so a byte-identical disassembly would still be new work. The port is covered in detail under the last question.

Tool inventory at a glance (verified items only; details and URLs below):

| Stage | Tool | License | Last activity seen | Fitness |
| --- | --- | --- | --- | --- |
| Decryption reference | MAME `src/mame/capcom/cps2crypt.cpp` + `init_cps2crypt()` in `cps2.cpp` | BSD-3-Clause | MAME master, Nov 2026 | Canonical. Decrypt only; encryption must be written (the Feistel network can be inverted) |
| Decryption (alt) | FBNeo `src/burn/drv/capcom/cps2_crpt.cpp` | FBNeo non-commercial license | pushed 2026-11-09 | Same algorithm (same credits); license unsuitable for reuse |
| Decrypt/encrypt library | MBDesu/cps2-utils (TypeScript/npm) | MIT | "split binary" done 2023-07-15; 11 commits | Claims decrypt, encrypt and Darksoft conversion; its own TODO list leaves decrypt/encrypt unchecked |
| Decrypted opcode dump | MAME debugger `saveo` (opcodes address space) | MAME | current docs | Zero-code way to get the decrypted opcode view |
| Disassembly/RE | Ghidra 68000 processor module | Apache-2.0 (Ghidra; not verified this session) | NSA master | Analysis only; no CPS2 loader found |
| Disassembly/RE | alexforencich/binaryninja-m68k | MIT | v0.1 README | Analysis/lifting only |
| Rebuild (assembler) | GNU as (binutils m68k) via this repo's `dis68k.py`/`gen.py` | GPL (binutils) | used in this repo | Already proven byte-identical on CPS1 Final Fight |
| Native port toolkit | tmcleroy/cps2recomp | GPL-3.0-only | pushed 2026-11-09 | Already ports AvP (beta) to Linux/macOS/Windows |
| Video reference | MAME `cps2.cpp` + `cps1_v.cpp` | BSD-3-Clause | MAME master | Can be relicensed into a port (BSD-3) |
| Audio | MAME `qsoundhle.cpp` (HLE) / `qsound.cpp` (DSP16 LLE) | BSD-3-Clause | MAME master | HLE is self-contained C++; LLE needs DSP16 core + DL-1425 ROM |
| Audio | ValleyBell/qsound-hle (DSP disassembly + C HLE) | BSD-3-Clause | 2018-07-25 | Standalone C, linkable |
| GFX ROM interleave | goosechooser/cps2-gfx-file-manip (Python 3) | MIT | 2017-02-10 | Only (de)interleaves; no tile viewer |

## CPS2 encryption: how it works, decryptors, key files, and handling it in a byte-identical rebuild

### Takeaway
The cipher encrypts only 68000 opcode fetches, one 16-bit word at a time. Each word is decrypted as D = FN2(E, K XOR EX(FN1(A, K))): two 4-round Feistel networks keyed by a 64-bit master key and the low 16 bits of the word address. Only addresses below a per-game upper limit are encrypted. MAME's BSD-3 code decrypts but does not encrypt, so a byte-identical rebuild has to (a) assemble plaintext and (b) re-encrypt exactly the words the CPU fetches as opcodes, leaving data words raw. That requires an exact code/data word map, and it raises the question, still open, of whether PC-relative operand reads also go through decryption.

### Cited Findings
- MAME's CPS-2 encryption file is BSD-3-Clause (copyright holders Paul Leaman, Andreas Naive, Nicola Salmoria, Charles MacDonald). Credit: "All credit goes to Andreas Naive for breaking the encryption algorithm. Code by Nicola Salmoria. Thanks to Charles MacDonald and Razoola for extracting the data from the hardware." — [MAME cps2crypt.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2crypt.cpp)
- "The encryption only affects opcodes, not data. It consists of two 4-round Feistel networks (FN) and involves both the 16-bit opcode and the low 16 bits of the address." Formula: `D = FN2( E, K XOR EX( FN1(A, K ) ) )`, where K is a 64-bit key and EX expands 16 bits to 64. Each round uses four 6-input/2-output s-boxes. — [MAME cps2crypt.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2crypt.cpp)
- "The encryption does _not_ cover the entire address space. The range covered differs per game." A per-game watchdog (a 68000 opcode sequence) must run "at least once every few seconds" or the hardware disables decryption. — [MAME cps2crypt.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2crypt.cpp)
- Signature of MAME's decrypt function: `cps2_decrypt(machine, uint16_t *rom, uint16_t *dec, int length, const uint32_t *master_key, uint32_t lower_limit, uint32_t upper_limit)`. It loops over all 0x10000 low-address values, computes the FN1 seed and the expanded FN2 subkey for each, and decrypts every word `a` with `a ≡ i (mod 0x10000)` inside [lower, upper]. Words outside the range are copied unchanged. There is no encrypt function in the file. — [MAME cps2crypt.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2crypt.cpp)
- Key file decoding (`init_cps2crypt`): the 20-byte key region is unpacked as 160 bits with `bit = (317 - b) % 160` into ten 16-bit words. decoded[0..3] form the two 32-bit master-key halves. decoded[4..6] hold the watchdog instruction words, decoded[7] is 0x4000 ("bits 8 to 23 of CPS2 object output address") and decoded[8] is 0x0900. decoded[9] sets the range: `upper = (((~decoded[9] & 0x3ff) << 14) | 0x3fff) + 1`, `lower = 0`. A dead board (decoded[9] == 0xffff) encrypts only FF0000–FFFFFF. — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- MAME exposes the result as a separate opcode space: `map(0x000000, 0x3fffff).rom().share(m_decrypted_opcodes)` in `decrypted_opcodes_map`, installed with `m_maincpu->set_addrmap(AS_OPCODES, ...)`. — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- `avsp` (Europe 940520) program ROMs, all `ROM_LOAD16_WORD_SWAP` 0x80000 bytes:
  - `avpe.03d` @0x000000 (SHA1 f60b0e39…)
  - `avpe.04d` @0x080000 (930f02e4…)
  - `avp.05d` @0x100000 (5549bc9d…)
  - `avp.06` @0x180000 (9bcfc0a0…)
  - key `avsp.key`, 0x14 bytes, CRC e69fa35b, SHA1 ed0ca61e…
  - Regional sets avspu/avspj/avspa/avsph each have their own `.key`.
  — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- `avspd` "Alien vs. Predator (Europe 940520 Phoenix Edition) (bootleg)" runs on `dead_cps2` with `phoenix.key` (CRC 2cf772b0). Its program ROMs: `avped.03d`, `avped.04d`, `avp.05d` (the same file as in `avsp`) and `avpd.06`. Graphics, Z80 and QSound ROMs are identical to `avsp`. — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- The driver header credits "Razoola, Ange 'Crashtest' Albertini and the CPS2 decryption team for their initial work on extracting decrypted code." — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- Phoenix sets "simply remove the encryption of the roms" to revive dead (battery-suicided) boards. MiSTer's CPS2 core added Phoenix sets in late 2021. — [misterfpga.org thread](https://misterfpga.org/viewtopic.php?p=36928)
- Darksoft multi-cart users pick the "Darksoft CPS2 2020" archive if they have a key-writing cable, otherwise the "OLD Decrypted" archive (forum guidance, not official Darksoft docs). — [arcade-projects.com post](https://www.arcade-projects.com/goto/post?id=274612)
- MBDesu/cps2-utils: a TypeScript/npm library (`Cps2Rom` class built from a MAME .zip), MIT. Its About text claims "decryption, encryption, conversion to Darksoft format", and it exposes `decryptOpcodes()` / `getDecryptedOpcodes()`. Its TODO list still has Decrypt/Encrypt unchecked. — [github.com/MBDesu/cps2-utils](https://github.com/MBDesu/cps2-utils)
- FBNeo has its own copy of the cipher, `src/burn/drv/capcom/cps2_crpt.cpp` (804 lines), with the same credit header ("All credit goes to Andreas Naive… Code by Nicola Salmoria"). — [FBNeo cps2_crpt.cpp](https://github.com/finalburnneo/FBNeo/blob/master/src/burn/drv/capcom/cps2_crpt.cpp)
- cps2recomp deciphers the player's set at runtime "with the set's own key file, as the board does when it starts; no key is in this repository". Its `machine/cps2crypt.*` is MAME's BSD-3 code. — [cps2recomp docs/TOOLKIT.md](https://github.com/tmcleroy/cps2recomp/blob/main/docs/TOOLKIT.md); [cps2recomp README](https://github.com/tmcleroy/cps2recomp)
- Hardware programming tools for keys (not needed for software RE):
  - jwestfall69/openkey-cps2, "CPS2 Programmer", Unlicense, pushed 2026-05-20
  - ArcadeHacker/ArcadeHacker_CPS2, "Capcom CPS2 security programming", no license, pushed 2022-06-27

  — GitHub search API results ([openkey-cps2](https://github.com/jwestfall69/openkey-cps2), [ArcadeHacker_CPS2](https://github.com/ArcadeHacker/ArcadeHacker_CPS2))
- Per the ArcadeHacker blog, the B-board's DL-1525 is "a gate array surrounding a Motorola 68000 megacell core" (search snippet). — [arcadehacker.blogspot.com 2018/01](https://arcadehacker.blogspot.com/2018/01)
- MAME's microcode-generated 68000 core sends each bus access to `m_opcodes` or `m_program` according to the microcode's SSW_PROGRAM / SSW_DATA classification of that access (`["m_opcodes", "m_program"][ci[2]]`, with `"SSW_PROGRAM", "SSW_DATA", "SSW_CPU"`). — [MAME m68000gen.py](https://github.com/mamedev/mame/blob/master/src/devices/cpu/m68000/m68000gen.py)

### Inferences
- **Producing a decrypted opcode image.** The simplest route needs no third-party code. Run `avsp` in MAME with `-debug`, then use `saveo op.bin,0,200000` (opcode space = decrypted view) and `save raw.bin,0,200000` (program space = data view, i.e. the raw ROM as the CPU sees it). The two can be diffed: words that differ lie inside the encrypted range. Equivalently, compile MAME's BSD-3 `cps2_decrypt` and the `init_cps2crypt` key unpacking into a small standalone C program. That is about 700 lines; you replace the `running_machine`/UI progress call. The output is two 2 MiB images.
- **What the disassembler should read.** Instruction words, including extension and immediate words, come from the opcode image. Absolute-addressed data comes from the raw image. A disassembler that sees only one image will mis-decode one or the other.
- **Encryption for the rebuild.** Each round updates one 8-bit half by XOR with a function of the other half, so FN2 can be inverted by running the four rounds in reverse order (round 4 first) with the same per-address subkeys. Encrypting is therefore a small change to MAME's code. Recommended build:
  1. Assemble plaintext into a "logical" image: code words as plaintext, data words as their raw ROM values.
  2. Re-encrypt only the words in [lower, upper) that the CPU fetches through the opcode space. The disassembler/generator, which knows every instruction extent, emits a bitmap of those words.
  3. Split the image into the four `ROM_LOAD16_WORD_SWAP` chips and compare SHA-1s.

  Self-test: run decrypt(encrypt(x)) over all words and verify it returns x.
- **Open question: PC-relative reads.** On a real 68000, PC-relative operand reads are program-space accesses. MAME's core picks the opcodes or program space from the microcode's program/data classification. If the CPS2 hardware also decrypts those reads, then jump tables read via `(d8,pc,Xn)`, like the `move.w (T,pc,d0.w),d0; jmp (T,pc,d0.w)` pattern this repo already detects, are stored encrypted in ROM and must go in the "encrypt" bitmap. This must be verified empirically on one avsp jump table: compare the raw vs opcode-space words at the table address.
- **Range lower than avp.05d?** `avp.05d` (0x100000–0x17FFFF) is byte-identical in the encrypted `avsp` set and the decrypted Phoenix `avspd` set. Either the encrypted range ends at or below 0x100000, or that 512 KiB contains no executed code. cps2recomp's AvP notes put the character animation lists at 0x15E240+ (data), which fits either reading. Decoding `avsp.key` locally gives the exact upper limit.
- **Phoenix sets are not a byte-identical target.** `avspd` also changes `avpd.06` and the first two chips. The Phoenix (decrypted) set is still useful as a cross-check of a decrypted image, but only for words the Phoenix authors decrypted. The rebuild target should stay the original encrypted chips and the original key.

### Gaps
- I could not open the jwestfall69 "mad" `util/rom-cps2-encrypt.cpp`, which a search hit placed on a demo.gitea.com mirror (host not reachable). The file is not on GitHub main under `util/` with the names tried (`rom-cps2-encrypt.cpp/.c`). A ready-made BSD/PD CPS2 encryptor is therefore unverified.
- Standalone "cps2dec"-style command-line decryptors: the GitHub search for "cps2 decrypt" and "cps2dec" returned no repositories. Razoola's original Phoenix tooling and the CPS2Shock XOR-table era are not documented in any source I could reach.
- Whether CPS2 decryption applies to PC-relative operand reads on real hardware (see Inferences) is unverified.
- The actual numeric upper limit for `avsp` was not derived, because it needs the key file and no ROMs were downloaded.

## 68000 disassemblers and RE suites: which can emit reassemblable output?

### Takeaway
No CPS2-specific loader exists for Ghidra, IDA or Binary Ninja in any source I found. Ghidra (68000 module) and Binary Ninja (MIT m68k plugin) are fine for interactive analysis of the decrypted image, but neither is a reassembly generator. The proven route to byte-identical output is a custom generator like this repository's `tools/dis68k.py` + `tools/gen.py` (GNU as Motorola syntax, round-trip checked per instruction), fed MAME traces. cps2recomp's pipeline (recursive descent plus "made-up play" exploration, then translation to C++) is the closest CPS2-specific prior art, and it targets C++, not assembly.

### Cited Findings
- Ghidra ships a 68000 processor module with language IDs `68000:BE:32:default`, `MC68020`, `MC68030`, `CPU32` and `Coldfire`. — [Ghidra 68000.ldefs](https://github.com/NationalSecurityAgency/ghidra/blob/master/Ghidra/Processors/68000/data/languages/68000.ldefs)
- A search for a Ghidra CPS2 loader returned nothing CPS2-specific. The only Ghidra extension in the results was a PS2 loader. — [search result: ghidra-emotionengine-reloaded](https://github.com/chaoticgd/ghidra-emotionengine-reloaded)
- Binary Ninja m68k plugin (Alex Forencich), "A disassembler and lifter for the Motorola 68k architecture… generates LLIL". MIT. README shows v0.1 with minimum Binary Ninja 1.0.13. — [alexforencich/binaryninja-m68k](https://github.com/alexforencich/binaryninja-m68k)
- This repository's existing pipeline:
  - code is found by recursive descent from the vector table, from MAME execution traces and through `move.w (T,pc,d0.w),d0; jmp (T,pc,d0.w)` jump tables
  - `tools/gen.py` "assembles every instruction at its address and compares the bytes"
  - instructions GNU as re-encodes, e.g. `(0,a0)` → `(a0)`, are emitted as raw words, and coverage is checked against traces

  — local file `/home/user/ffight-disasm/README.md`
- cps2recomp: `tools/recomp.py` turns the 68000 program into C++ and `tools/recompz80.py` does the same for the sound CPU. "The code is found by reading the program and by made-up play (`tools/explore.sh`). Code it has not found yet runs in an interpreter, and is counted." — [cps2recomp docs/TOOLKIT.md](https://github.com/tmcleroy/cps2recomp/blob/main/docs/TOOLKIT.md)
- For AvP specifically, cps2recomp's explore found "82,889 instructions; none left to the interpreter but 25 a guess took for code", plus 2,153 instructions of the Z80 sound program (dated 2026-10-18). — [cps2recomp games/avsp/PROGRESS.md](https://github.com/tmcleroy/cps2recomp/blob/main/games/avsp/PROGRESS.md)
- cps2recomp's `tools/portmap.py` maps two related programs (anchors, side-by-side walking, jump tables). That is useful for porting labels between regional sets. — [cps2recomp docs/TOOLKIT.md](https://github.com/tmcleroy/cps2recomp/blob/main/docs/TOOLKIT.md)
- MAME's debugger `trace` command (`trace {<filename>|off}[,<CPU>[,[noloop|logerror][,<action>]]]`) logs executed instructions. `noloop` logs every instruction instead of condensing loops. — [MAME docs execution.rst](https://github.com/mamedev/mame/blob/master/docs/source/debugger/execution.rst)

### Inferences
- The fastest path to a byte-identical AvP disassembly is to generalize the existing ffight `gen.py`:
  - add a second input image (opcode view vs raw view)
  - add CPS2 hardware equates (from `cps2.cpp`)
  - emit an "opcode words" bitmap for the re-encryption step
  - reuse the MAME trace-based coverage check (MAME traces disassemble the decrypted opcode space, so trace PCs map directly)
- cps2recomp's AvP PROGRESS.md publishes many addresses and their meanings: A5 = FF8000, settings record FF0EF0, attract table 004706, player records FF8380, enemy pool FF9280, camera FF8268, song table at Z80 9006, and more. They can seed `names.txt`/`ram.txt` for the avsp disassembly. Licensing: the facts are addresses, but copying prose or naming wholesale from a GPL-3.0-only project into this GPLv3 repository should be done with attribution.
- Ghidra could serve as a cross-check viewer: load the decrypted opcode image at 0x000000 as raw 68000:BE:32:default and add memory blocks for 0xFF0000 RAM and 0x900000 GFX RAM. It is not a source of reassemblable output.

### Gaps
- IDA Pro 68k support and any IDA CPS2 loader; radare2/rizin m68k (Capstone-based); standalone disassemblers named in the brief (dis68k, m68kdis, Musashi's disassembler, "68kdisasm", Dasm68k, ReGen, IRA): none were checked this session. The GitHub search for "m68k disassembler" / "68000 disassembler" hit the rate limit. Background knowledge, unverified: IDA has a 68k processor module; rizin/radare2 disassemble m68k via Capstone; IRA (Amiga) and ReGen (Windows) produce re-assemblable source for some assemblers. Treat all of these as unconfirmed.
- No tracing-assisted CPS2 disassembler other than this repo's approach and cps2recomp's explore was found.

## Assemblers for byte-identical rebuilds (vasm, GNU as, AS/asl, others)

### Takeaway
GNU as (binutils `m68k-linux-gnu`/`m68k-elf`, invoked with `-m68000 --register-prefix-optional`) is already proven byte-identical on CPS1 Final Fight in this repository. Its few re-encodings, like `(0,a0)` → `(a0)`, are handled by emitting raw words. vasm uses a custom "VASMBSD" license that restricts commercial use and distribution of modified versions. AS (asl) is GPL. Switching assemblers brings no benefit for byte-identity, and any assembler's optimizer (branch shortening, `move`→`moveq`, displacement folding) must be off or bypassed.

### Cited Findings
- This repo's Makefile assembles with `$(CROSS)as -m68000 --register-prefix-optional`, links with `ld -Ttext=0` and extracts `.text` with `objcopy -O binary`. The README says the source "rebuilds all five 68000 program ROM chips byte-identically (checked by SHA-1)". Instructions GNU as re-encodes "are emitted as raw words with the instruction in a comment and listed in `build/fallback.txt`". — local `/home/user/ffight-disasm/Makefile`, `/home/user/ffight-disasm/README.md`
- GNU as has an m68k target ("The Motorola 680x0 version of as"). — [GNU as manual, m68k chapter](https://ftp.gnu.org/old-gnu/Manuals/gas/html_chapter/as_18.html)
- vasm: FreeBSD's port lists the license as "VASMBSD", installed as a separate license file. A secondary wiki summary says the license requires "written consent for distributing modified versions and commercial usage". The Motorola-syntax module (Frank Wille) "is covered by the vasm copyright". Mot syntax is Devpac-compatible. — [FreshPorts devel/vasm](https://freshports.org/devel/vasm/); [FreeBSD pkg-descr](https://cgit.freebsd.org/ports/plain/devel/vasm/pkg-descr); [vasm syntax_mot doc mirror](https://git.applefritter.com/Macintosh-SW/NetBoot/src/branch/master/vasm-1/doc/syntax_mot.texi)
- AS (Alfred Arnold's Macro Assembler, `asl`) is distributed under the GNU GPL. A GitHub mirror labels v1.42 Beta as GPL 2. AS "began as an extension of a macro assembler for the 68000 family". — [AS manual (mirror)](https://ubuntourist.codeberg.page/Altair-8800/_static/as_EN.html); [github.com/linuxha/asl](https://github.com/linuxha/asl)

### Inferences
- For a CPS2 rebuild the assembler only has to produce the plaintext logical image. Encryption is a separate post-link step, so assembler choice is independent of encryption.
- Stay on GNU as for continuity with ffight-disasm: same generator, same fallback mechanism and same Ubuntu packages (`binutils-m68k-linux-gnu`). vasm's license would complicate redistributing a toolchain or modified assembler. asl is GPL and the Sonic community's tool of choice, but would need a new syntax emitter.

### Gaps
- The current vasm release number and date, and the full VASMBSD text, could not be fetched (host blocked). The current asl build number and date could not be fetched either.
- No source was found on specific GNU as / vasm / asl optimizations that break byte-identity on 68000 (e.g. vasm `-no-opt`, asl `SUPMODE`/`PADDING`). This repo's empirical fallback list is the only verified data point.

## MAME debugging: debugger commands, Lua API, CPS2-specific scripts; FBNeo comparison

### Takeaway
Stock MAME provides everything needed:
- `trace` for execution coverage
- `bpset`/`wpset` (also from Lua) for breakpoints and watchpoints
- `saveo`/`save` to dump decrypted vs raw program images
- Lua memory taps (`install_read_tap`/`install_write_tap`) and frame callbacks for RAM loggers and bots

CPS2 hitbox scripts exist, but they were written for the MAME-RR/FBA-RR forks and have to be ported to the modern MAME Lua API.

### Cited Findings
- `trace {<filename>|off}[,<CPU>[,[noloop|logerror][,<action>]]]` traces execution to a file. `traceover` skips subroutines and `traceflush` flushes. — [MAME debugger execution.rst](https://github.com/mamedev/mame/blob/master/docs/source/debugger/execution.rst)
- `save[{d|i|o}] <filename>,<address>[:<space>],<length>`: "`saveo` defaults to the space with index 3 (opcodes)". Address-space identifiers can be given explicitly, e.g. `:program`. — [MAME debugger memory.rst](https://github.com/mamedev/mame/blob/master/docs/source/debugger/memory.rst); [MAME debugger index.rst](https://github.com/mamedev/mame/blob/master/docs/source/debugger/index.rst)
- Lua interface:
  - present since MAME 0.148
  - usable via the interactive console, `-autoboot_script` or plugins
  - "The Lua API is not yet declared stable and may suddenly change without prior notice"
  - covers frame hooks, overlay drawing, memory read/write and register get/set

  — [MAME luascript index.rst](https://github.com/mamedev/mame/blob/master/docs/source/luascript/index.rst)
- Lua debugger bindings: `debug:bpset(addr, [cond], [act])`, `debug:wpset(space, type, addr, len, [cond], [act])`, plus `debugger.consolelog[]`, `debugger.errorlog[]` and `debugger.execution_state`. — [MAME luascript ref-debugger.rst](https://github.com/mamedev/mame/blob/master/docs/source/luascript/ref-debugger.rst)
- Memory taps: `space:install_read_tap(start, end, name, callback)` and `space:install_write_tap(...)`. — [MAME luascript ref-mem.rst](https://github.com/mamedev/mame/blob/master/docs/source/luascript/ref-mem.rst)
- A community CPS-2 hitbox script covers SFA2, SFA3, Vampire Savior, VH2 and others, and "displays correctly in both FBA-RR and MAME-RR". Throwboxes are shown properly only in FBA-RR. Original hosting was Google Code; backups are listed on the Fight an Vidya wiki. — [TASVideos hitbox thread](https://tasvideos.org/Forum/Topics/9942); [Fight an Vidya wiki](https://fightanvidya.com/wiki/index.php/Collecting_Framedata_and_Hitboxes)
- This repo already uses a Lua bot (`bot/bot.lua`) under the MAME `trace` command, with object layout taken from the mame-rr `beatemup-hitboxes.lua` script. — local `/home/user/ffight-disasm/README.md`
- cps2recomp built AvP-specific bots to play each scene to its end ("How far each scene's camera goes was found by playing each to its end with a bot"). — [cps2recomp games/avsp/PROGRESS.md](https://github.com/tmcleroy/cps2recomp/blob/main/games/avsp/PROGRESS.md)
- FBNeo: actively maintained (repository pushed 2026-11-09, ~1.57k stars per GitHub search). Its CPS code lives in `src/burn/drv/capcom/`, e.g. `cps_obj.cpp` for sprites, `qs.cpp`/`qs_z.cpp` for QSound/Z80 and `cps2_crpt.cpp`. — [FBNeo repository](https://github.com/finalburnneo/FBNeo); [FBNeo cps_obj.cpp](https://github.com/finalburnneo/FBNeo/blob/master/src/burn/drv/capcom/cps_obj.cpp)

### Inferences
- For avsp, the ffight workflow carries over almost unchanged: a `trace` + `collect_pcs` coverage pipeline, and a Lua bot (`bot.lua`) adapted to AvP's player and enemy records. cps2recomp's notes give the addresses: players at FF8380 (0x100 each, +41 health), enemies at FF9280 (24 × 0xC0).
- Lua write taps on 0x708000–0x70FFFF (object RAM), 0x900000–0x92FFFF (GFX RAM) and 0x804100–0x80417F (CPS-A/B) would give a register/VRAM access log. That log would serve as a "golden" reference for validating a native renderer.

### Gaps
- I found no ready-made stock-MAME (modern Lua API) CPS2 or AvP-specific RAM dumper or hitbox script. The MAME-RR scripts would need porting, and an AvP entry in them is not confirmed.
- MAME's cps2 driver has no special debug views beyond the generic tile/palette viewer. This was not verified in docs this session.

## Graphics: CPS2 GFX ROM format, sprites/objects, palette, tilemaps, row scroll; extraction tools

### Takeaway
The CPS2 GFX ROMs are loaded as 64-bit interleaved words (`ROM_LOAD64_WORD`, four chips per bank), then "unshuffled" per 2 MiB bank, giving 4bpp tiles in CPS1 layout. Tile sizes are 8×8 (scroll1), 16×16 (sprites and scroll2) and 32×32 (scroll3). Objects are 4-word entries in double-buffered object RAM (bank swap at 0x8040E0) and are latched at vblank. Tooling is thin: MAME's built-in GFX viewer, a 2017 MIT Python (de)interleaver, and MAME's BSD-3 decode and render code as the reference implementation.

### Cited Findings
- avsp's GFX region is 0x1000000 bytes:
  - `avp.13m/15m/17m/19m` (4 × 2 MiB, `ROM_LOAD64_WORD` at offsets 0/2/4/6)
  - `avp.14m/16m/18m/20m` (4 × 1 MiB at 0x800000+0/2/4/6)

  — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- `cps2_gfx_decode()` runs `unshuffle()` over each 0x200000-byte bank as 64-bit units. The recursive unshuffle swaps the middle quarters at each level. — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- CPS-A registers: 0x00 OBJ RAM base, 0x02 Scroll1 (8×8) base, 0x04 Scroll2 (16×16) base, 0x06 Scroll3 (32×32) base, 0x08 rowscroll RAM base, 0x0A palette base. Writing the palette base copies the palette from GFX RAM to dedicated RAM. CPS-B 0x20 is "Start offset for the rowscroll matrix", 0x26 the layer control register, 0x30 palette control (bits select which pages to copy: sprites, scroll1-3, stars1-2). — [MAME cps1_v.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps1_v.cpp)
- GFX address layout of the 23-bit B-board request: sprite `000ccccccccccccccccyyyy`, scroll1 `001?ccccccccccccccccyyy`, scroll2 `010ccccccccccccccccyyyy`, scroll3 `011ccccccccccccccyyyyyx`. "16x16 tiles are used for BOTH sprites and scroll2." 32×32 tiles have a 14-bit code. — [MAME cps1_v.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps1_v.cpp)
- CPS2 memory map:
  - object RAM 0x700000–0x701FFF ("no game seems to use it directly") and 0x708000–0x709FFF (mirror 0x6000)
  - object-RAM bank swap bit 0 at 0x8040E0
  - CPS-A at 0x804100–0x80413F and CPS-B at 0x804140–0x80417F (mirrors at 0x800100/0x800140)
  - video RAM 0x900000–0x92FFFF
  - work RAM 0xFF0000–0xFFFFFF
  - "CPS2 object output" registers at 0x400000–0x40000B
  - QSound shared RAM 0x618000–0x619FFF
  - EEPROM port 0x804040

  — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- Object output registers: 0x00 OBJ_BASE ("Unknown"), 0x04 layer priorities, 0x08 X offset (usually 0x0040), 0x0A Y offset (always 0x0010). Object RAM size is 0x2000. The object list is buffered (`m_cps2_buffered_obj`), and `cps2_objram_latch` is appended to the screen's vblank. — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- Sprite entry (4 words):
  - word 0 = X, with bits 13–15 the priority
  - word 1 = Y, with bits 13–14 added to the code as `(y & 0x6000) << 3`
  - word 2 = code
  - word 3 = attributes: bits 0–4 colour, bit 5 flip X, bit 6 flip Y, bit 7 "relative to offset"
  - End of list: word1 ≥ 0x8000 or word3 ≥ 0xFF00
  - Drawn back to front, with transparent pen 15

  — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- goosechooser/cps2-gfx-file-manip: CLI tool, Python 3.6+, MIT, last push 2017-02-10. "lets you (de)interleave CPS2 graphics files" (e.g. `sfx.14m` + `16m` + `18m` + `20m` into a combined file and back). — [goosechooser/cps2-gfx-file-manip](https://github.com/goosechooser/cps2-gfx-file-manip)
- cps2recomp's AvP port documents the object/animation format: an object's frame at +1C (time word, next-pointer flag, picture address), animation lists per character at 15E240/162F90/168564/16D122, and draw routine 0A9B48. It also has a "model viewer" that renders any character at any animation frame. — [cps2recomp games/avsp/PROGRESS.md](https://github.com/tmcleroy/cps2recomp/blob/main/games/avsp/PROGRESS.md); [cps2recomp games/avsp/README.md](https://github.com/tmcleroy/cps2recomp/blob/main/games/avsp/README.md)
- cps2recomp notes that "Some older collections have the set without its key file, or with older dumps of four graphics ROMs (`avp.14m`, `16m`, `18m`, `20m`): those will not do" (redumped). — [cps2recomp games/avsp/README.md](https://github.com/tmcleroy/cps2recomp/blob/main/games/avsp/README.md)

### Inferences
- An asset extractor for AvP is best written as a small tool (Python or C) that:
  1. interleaves the 8 GFX ROMs exactly as `ROM_LOAD64_WORD` does
  2. applies the 2 MiB-bank unshuffle
  3. decodes 4bpp planar 16×16 tiles using MAME's CPS1 gfx layouts
  4. resolves palettes from GFX RAM captures, because CPS palettes are written at runtime from 68000 data to GFX RAM, then copied by the palette-base write

  Full sprite "frames" require walking the 68000-side animation/frame tables, which the disassembly will document.
- The Final Fight project's GFX knowledge (CPS1) mostly transfers. The CPS2 differences are the extra unshuffle, the separate object RAM with bank swap and vblank latch, the 0x400000 object-output registers, and IRQ4 raster effects.

### Gaps
- The palette word format (CPS's 4-bit brightness + 4-4-4 RGB), the sprite block-size bits in attribute bits 8–15, and the tilemap entry formats were not extracted from source this session. They are in `cps1_v.cpp` (`cps1_build_palette`, the tile-info callbacks) and should be read there.
- Generic tile tools (Tile Molester, YY-CHR), MAME's F4 GFX viewer, Spriters Resource AvP rips, and any dedicated "CPS2 sprite ripper": none were verified this session. The GitHub search for "cps2 sprite" hit the rate limit.

## Audio: QSound (DL-1425), the Capcom Z80 driver, MAME implementations, ValleyBell's work, VGM logging

### Takeaway
The Z80 sound program (`avp.01`) drives a DL-1425 QSound chip, a DSP16A with mask ROM, via shared RAM. MAME has two BSD-3 implementations:
- `qsoundhle.cpp` (superctr and Valley Bell): an HLE "based on disassembled DSP code", easily extracted
- `qsound.cpp` (Vas Crabb): an LLE that needs a DSP16 core and the DL-1425 internal ROM

ValleyBell/qsound-hle (BSD-3) provides the DSP disassembly and standalone C emulators. cps2recomp has already translated AvP's Z80 driver to C++.

### Cited Findings
- avsp audio ROMs: `avp.01` (Z80 program, 0x8000 + `ROM_CONTINUE` 0x18000 banked) and QSound samples `avp.11m` + `avp.12m` (2 × 2 MiB, `ROM_LOAD16_WORD_SWAP`, 4 MiB total). — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- The sound CPU is a Z80 or Kabuki, but "in all CPS2 games, Capcom chose not to use the Kabuki encryption since none of the CPS2 games have an encrypted sound program". — [MAME cps2.cpp header](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- MAME `qsound.cpp` (BSD-3-Clause, Vas Crabb):
  - "Sixteen-channel sample player"
  - the key components are a DSP16A, a TDA1543 DAC and a TC9185P volume control
  - commands are address/data word pairs into DSP RAM
  - samples are 8-bit ROM data
  - sample rate 24.03846 kHz (60 MHz / 2 / 1248)
  - the DSP16A is required, since the program uses 2 kilowords of internal RAM

  — [MAME qsound.cpp](https://github.com/mamedev/mame/blob/master/src/devices/sound/qsound.cpp)
- MAME `qsoundhle.cpp`: BSD-3-Clause, copyright holders superctr and Valley Bell, "Capcom QSound DL-1425 (HLE)… Based on disassembled DSP code". It searches the parent `QSOUND` device's ROMs. — [MAME qsoundhle.cpp](https://github.com/mamedev/mame/blob/master/src/devices/sound/qsoundhle.cpp)
- ValleyBell/qsound-hle (BSD-3-Clause, last push 2018-07-25):
  - DL-1425 = DSP16A with mask ROM; 16 PCM channels (loopable) + 3 ADPCM channels; FIR filters and echo
  - the DSP program was written by Brian Schmidt
  - files: `qsound_dl-1425.asm` (ROM disassembly), `old/qsound_vb.c` (port from libvgm) and `qsound.c` (new emulator by ctr)
  - "There is no known game that uses the ADPCM channels."

  — [github.com/ValleyBell/qsound-hle](https://github.com/ValleyBell/qsound-hle)
- AvP's sound program is "Capcom's QSound driver of November 1993" and was translated by cps2recomp (2,153 instructions). The song table is at Z80 9006 after a count word (0x38D); 26 pieces of music are named. cps2recomp also has Capcom's sound driver v2.01b reimplemented as C++ (`sound/driver.cpp`) "for games that have that version". — [cps2recomp games/avsp/PROGRESS.md](https://github.com/tmcleroy/cps2recomp/blob/main/games/avsp/PROGRESS.md); [cps2recomp docs/TOOLKIT.md](https://github.com/tmcleroy/cps2recomp/blob/main/docs/TOOLKIT.md)
- cps2recomp's QSound model "follows MAME's (superctr, Valley Bell)". — [cps2recomp README](https://github.com/tmcleroy/cps2recomp)
- vgmrips MAME VGM mod: version 0.272 (2024-11-30) is listed as current, and QSound is among the loggable chips (search snippet of the wiki). A MAME bug report about QSound VGMs showing "Bad rip" in a player put the fault in the player, not the logging. — [vgmrips wiki: MAME/MESS VGM mod](https://vgmrips.net/wiki/MAME/MESS_VGM_mod); [MAME Testers 9008](https://mametesters.org/view.php?id=9008)

### Inferences
- For a native port, the cleanest audio stack is:
  - translate or re-host the Z80 driver: either run a small BSD/MIT Z80 core on `avp.01`, or follow cps2recomp and translate it
  - feed the QSound register writes into a QSound HLE extracted from MAME `qsoundhle.cpp` or ValleyBell's `qsound.c` (both BSD-3, so compatible with GPL or permissive port licensing)

  The LLE path adds the DSP16 core and needs the DL-1425 ROM, which is extra ROM data the user must supply.
- For the byte-identical goal, the Z80 program is not encrypted, so a second, simpler disassembly (Z80) can be verified by SHA-1 of `avp.01` alone.

### Gaps
- ctrmml and other modern QSound drivers, CPS2 sample-extraction tools, and ValleyBell's blog posts were not verified this session. The libvgm README fetch returned 404 at the guessed path.
- Whether the current vgmrips MAME VGM mod (0.272) logs CPS2 QSound cleanly for AvP specifically is unverified.

## CPS2 hardware documentation sources

### Takeaway
The most reliable and current hardware documentation is the MAME source itself. `cps2.cpp` covers the board layout, memory map and object output registers, `cps1_v.cpp` the CPS-A/CPS-B registers, raster counters and GFX addressing, and `cps2crypt.cpp` the cipher. All are BSD-3. Charles MacDonald's role is credited in the cipher work, but I could not locate a standalone "CPS2 hardware notes" document from him.

### Cited Findings
- `cps2.cpp` header: it describes the A-board/B-board split, regional colour coding and battery-backed key SRAM ("If the battery dies the system kills itself"). The A-board parts include CAPCOM-Q1 DL-1425 DSP-16A, CPS-B-21 DL-0921, CPS-A-01 DL-0311, DL-1123 I/O and 93C46 EEPROMs. — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- Raster interrupts: CPS-B registers 0x0E (raster counter X offset), 0x10 and 0x12 (raster counters 1 and 2) are "only supported on CPS-B-21. It can trigger IRQ4 on a scanline… CPS2 uses it for raster effects. Certainly used by ssf2… msh… and maybe others." MAME drives this with a per-scanline timer (`raster_scanline`). — [MAME cps1_v.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps1_v.cpp); [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- "Extra adapter memory (0x660000-0x663fff) available when bit 14 = 0" of 0x804030; "Many games store highscores and other info here if available." — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- MAME is the wrong target for cycle-exact timing: "HACK: RAM access waitstates etc. aren't emulated - slow the CPU to compensate" (`set_clock_scale(0.7375)`). — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- cps2recomp claims "a cycle-exact model of" the board's 68000 waits and video DMA (docs/TIMING.md). — [cps2recomp README](https://github.com/tmcleroy/cps2recomp)
- ArcadeHacker blog: custom-chip analysis (DL-1525 = 68000 megacell in a gate array), and credit for the cipher crack to "Charles McDonald, Andreas Naive and Nicola Salmoria" (search snippets). — [arcadehacker.blogspot.com 2018/01](https://arcadehacker.blogspot.com/2018/01); [arcadehacker.blogspot.com 2017](https://arcadehacker.blogspot.com/2017)
- Other references surfaced by search but not read:
  - a CPS2 B-board wiring list on arcade-projects.com ([thread](https://www.arcade-projects.com/threads/cps2-b-board-complete-wiring-list.9291))
  - "CPS2 Debug Switches and the Games That Love Them" ([sudden-desu.net](https://sudden-desu.net/entry/cps2-debug-switches-and-the-games-that-love-them))
  - Data Crystal's CPS2 page ([datacrystal.tcrf.net](https://datacrystal.tcrf.net/wiki/Capcom_Play_System_2))
  - wiki.arcadeotaku.com CPS2 ([page](https://wiki.arcadeotaku.com/w/CPS2))

### Inferences
- MAME's 0x8040B0 DIP switch read ("only present on development hardware") together with the sudden-desu article suggests AvP may contain developer debug code paths. Worth checking during disassembly, but unverified for AvP.

### Gaps
- No Charles MacDonald CPS2-specific hardware text was found; his reachable hardware notes cover Sega systems, SNES, Neo-Geo and others. The "CPS2 technical notes", Darksoft documentation and the Arcade-Projects wiki were not readable in this session.
- Which CPS-B configuration and per-game ID values CPS2 uses were not extracted. Search `cps2.cpp` for the `cps2_state` CPS-B config.

## Standalone CPS2 rendering library/core for a native Linux port; licenses

### Takeaway
MAME's CPS2 video (`cps2.cpp` + `cps1_v.cpp`), cipher and both QSound cores are BSD-3-Clause per their SPDX headers, so they can legally be extracted and linked into a native port under any license, with attribution. FBNeo's CPS code is under a non-commercial, no-donations license that is not open-source-compatible. The decisive fact for viability is that cps2recomp (GPL-3.0-only, very active, pushed 2026-11-09) already ships an AvP native port (beta) for Linux x86_64/ARM64 and others, built by static recompilation with its own board model. That port already covers video, QSound and the Z80 driver.

### Cited Findings
- SPDX headers (all `// license:BSD-3-Clause`):
  - `cps2crypt.cpp` (Leaman, Naive, Salmoria, MacDonald)
  - `cps2.cpp` (Leaman, Naive, Salmoria)
  - `cps1_v.cpp` and `cps1.h` (Paul Leaman)
  - `qsound.cpp` (Vas Crabb)
  - `qsoundhle.cpp` (superctr, Valley Bell)
  - `cps2comm.cpp` (Vas Crabb)

  — [MAME src/mame/capcom](https://github.com/mamedev/mame/tree/master/src/mame/capcom); [MAME src/devices/sound](https://github.com/mamedev/mame/tree/master/src/devices/sound)
- FBNeo license excerpts:
  - "You may not sell, lease, rent or otherwise seek to gain monetary profit from FB Neo"
  - "You must make public any changes you make to the source code"
  - "You may not ask for donations to support your work on any project that uses the FB Neo source code"
  - "Due to the use of MAME code in FB Neo, FB Neo is also subject to the terms of the MAME license."
  - GitHub reports the license as NOASSERTION.

  — [FBNeo src/license.txt](https://github.com/finalburnneo/FBNeo/blob/master/src/license.txt)
- cps2recomp (tmcleroy/cps2recomp), with about 171 stars and a push on 2026-11-09 per the GitHub search API:
  - "Unofficial native PC ports of Capcom's CPS-2 arcade games… for macOS, Linux (Steam Deck and ARM64 included), Windows and Android"
  - "Each game's program is translated ahead of time into C++ and runs on a machine written for this project, not an emulator"
  - license GPL-3.0-only
  - uses SDL 3 (zlib), Dear ImGui (MIT), Inter font (OFL)
  - build: "C++20 compiler… CMake, Ninja, Python 3, zlib and SDL 3"

  — [cps2recomp README](https://github.com/tmcleroy/cps2recomp); [cps2recomp docs/TOOLKIT.md](https://github.com/tmcleroy/cps2recomp/blob/main/docs/TOOLKIT.md)
- cps2recomp's game table lists "Alien vs. Predator (1994) | `avspu` (USA 940520) | Beat-'em-up: three players, a stage to start at, score attack". Per the AvP page:
  - "**Beta.** The game plays through its first rounds in made-up play and its code is checked instruction by instruction, but nobody has played it by hand yet."
  - other regional sets (avsp, avspj, avspa, avsph) work too
  - build with `make GAME=avsp` / `make GAME=avsp explore` / `make GAME=avsp check`

  — [cps2recomp games/avsp/README.md](https://github.com/tmcleroy/cps2recomp/blob/main/games/avsp/README.md)
- cps2recomp's verification:
  - "Translated code is checked against the interpreter, the sound driver's every chip write against the Z80's, and runs of the same input movie must give the same per-frame hashes"
  - readable hand rewrites are checked "on every call" against the original (memory, registers, timing, optionally video RAM)

  — [cps2recomp docs/TOOLKIT.md](https://github.com/tmcleroy/cps2recomp/blob/main/docs/TOOLKIT.md)
- The same author's earlier per-game repos (vampire-savior-recomp, sfa2-recomp) were "Moved to tmcleroy/cps2recomp". A third party has made a Cadillacs and Dinosaurs recomp "built by static recompilation with cps2recomp" (GPL-3.0, pushed 2026-10-22), which shows the toolkit can be reused. — GitHub search API ([tmcleroy/vampire-savior-recomp](https://github.com/tmcleroy/vampire-savior-recomp), [omegakatana92/Cadillacs-and-Dinosaurs-Recomp](https://github.com/omegakatana92/Cadillacs-and-Dinosaurs-Recomp))
- Other emulator cores:
  - NJEMU (CPS1/CPS2/Neo-Geo for PSP), GPL-3.0, last push 2023-08-06
  - barry65536/FBAlpha, last push 2019-10-27, no license metadata

  — GitHub search API ([phoe-nix/NJEMU](https://github.com/phoe-nix/NJEMU); [barry65536/FBAlpha](https://github.com/barry65536/FBAlpha))

### Inferences
- **Native-port viability is effectively proven.** A Linux-native AvP built from the original 68000 program already exists (beta). A new port from this project would differ by being built from a human-readable, byte-identically reassemblable disassembly rather than machine-translated C++. That is a documentation and maintainability gain, not a feasibility gain. The report should frame the project's added value around the disassembly (labels, data formats, rebuildable source) and possibly around contributing names and facts back to, or reusing, cps2recomp's board model.
- **Licensing.** This repository is GPLv3, and cps2recomp is GPL-3.0-only. Code reuse from cps2recomp is compatible if the port is GPL-3.0. MAME's BSD-3 CPS2/QSound pieces can be used in either. FBNeo code should be avoided.
- **Port architecture options**, ranked by effort:
  1. contribute to or fork cps2recomp's AvP game folder
  2. a static-recompilation or hand-port that uses the reassemblable disassembly as source of truth, plus a BSD-3 MAME-derived CPS2 video/QSound layer
  3. re-host the 68000 code on an interpreter core (Musashi or similar), which is the least "native"

### Gaps
- Musashi's current license (MIT in recent upstream, per background knowledge) was not verified; the raw LICENSE fetch failed. Moira and other 68000 cores were not checked.
- No standalone, already-extracted "libcps2video" library was found. The GitHub search for CPS2 graphics returned only the 2017 interleaver.
- The latest MAME release tag and date could not be retrieved; GitHub API repo endpoints were blocked for this session. All MAME citations are from the `master` branch fetched on 2026-11-09.
- cps2recomp's real-world quality on AvP (hand-played bugs, audio accuracy) is unknown beyond its own "beta" statement.
