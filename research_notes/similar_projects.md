# Similar Projects: Disassemblies, Decompilations, Recompilations and Native Ports Comparable to an Alien vs. Predator (CPS-2) Port

Research date: 2026-11-09. Repo dates (created / last push) and star counts come from the GitHub search API on 2026-11-09 unless noted. Commit counts and first/last commit dates come from blobless `git clone` of the repo on the same day. Some hosts could not be reached from this session (timeextension.com, kotaku.com.au, reassembler.blogspot.com), so facts from those sites come from search-engine snippets only. They are marked as such.

**Headline finding.** A native, statically recompiled port of Alien vs. Predator already exists, in beta. It is part of `tmcleroy/cps2recomp` (GPL-3.0). It targets the `avspu` set and supports Linux x86_64 and SteamOS. It reached three-player play on 2026-10-18 and is still being worked on as of 2026-11-04. Any plan for an AvP disassembly or native Linux port should start from this fact.

## Q1. Capcom CPS1/CPS2/CPS3 projects (disassemblies, decomps, reimplementations, ports)

### Takeaway
In October and November 2026, Capcom CPS work moved from almost nothing to an active static-recompilation scene. `cps2recomp` already ships native ports of 29 CPS-1 and CPS-2 games, AvP included (beta), plus the beat 'em ups Cadillacs and Dinosaurs and The Punisher. A third party has already built D&D: Shadow over Mystara on the same toolkit. By contrast, human-readable disassemblies or matching decompilations of CPS games are almost nonexistent. `cerroverb/ffight-disasm` (this repo) is the only Final Fight CPS-1 disassembly found.

### Cited Findings

**tmcleroy/cps2recomp (CPS-2 Recomp): the direct precedent, and it already covers AvP**
- URL: https://github.com/tmcleroy/cps2recomp. Author: Tommy McLeroy. Licence: GPL-3.0-only. 171 stars. Repo created 2026-10-13; last commit 2026-11-08; 724 commits (706 McLeroy, 15 "two4teezee", 3 "sunkpoet-lang"); release tags v1.0.0 through v1.4.0 — [repo](https://github.com/tmcleroy/cps2recomp) (git log)
- The first commit, "cps2recomp 0.1.0" (2026-10-13), adds 116 files and 19,331 lines in one go. So the toolkit was developed before this repo existed. Two predecessor repos, `tmcleroy/vampire-savior-recomp` (created 2026-10-13) and `tmcleroy/sfa2-recomp` (created 2026-10-15), are marked "Moved to tmcleroy/cps2recomp" — [repo](https://github.com/tmcleroy/cps2recomp); [vampire-savior-recomp](https://github.com/tmcleroy/vampire-savior-recomp); [sfa2-recomp](https://github.com/tmcleroy/sfa2-recomp)
- The same author also runs static-recompilation ports for other platforms: Muscle March (WiiWare, created 2026-10-08), Soulcalibur II (Xbox, created 2026-11-02, 143 stars) and a Saturn toolkit, `satrecomp` — [soulcalibur2-recomp](https://github.com/tmcleroy/soulcalibur2-recomp); [muscle-march-recomp](https://github.com/tmcleroy/muscle-march-recomp); [satrecomp](https://github.com/tmcleroy/satrecomp)
- Games listed: 29 in total. CPS-2 titles include SSF2, SSF2T, HSF2, the SF Alpha series, the Marvel and X-Men games, Darkstalkers, Vampire Savior, Cyberbots, Puzzle Fighter, Giga Wing and **Alien vs. Predator (`avspu`, USA 940520)**. CPS-1 titles include SF2, SF2CE, SF2HF, Ghouls'n Ghosts, **Cadillacs and Dinosaurs (`dino`)** and **The Punisher (`punisheru`)** — [README](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/README.md)
- Method: "Each game's 68000 program is translated ahead of time into C++ and compiled into that game's program, and the parts its features touch are rewritten by hand as readable C++, each checked call by call against the game's own code. The board (video, the QSound chip, the sound CPU, the settings memory) is code written for this project, not an emulator." — [README](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/README.md)
- Toolkit details:
  - `tools/recomp.py` translates the 68000 code and `tools/recompz80.py` the Z80 code.
  - Code is found "by reading the program and by made-up play (`tools/explore.sh`)". Code not yet found "runs in an interpreter, and is counted, so that the count can be driven to zero".
  - Capcom's sound driver v2.01b is also reimplemented as ordinary C++.
  - Rendering uses SDL3's GPU API (Metal, Vulkan or D3D12).
  - A checker compares memory, registers and timing for hand rewrites.
  - Determinism is checked with per-frame hashes of input movies.

  — [docs/TOOLKIT.md](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/docs/TOOLKIT.md)
- Third-party code and facts: the CPS-2 program cipher is MAME's (BSD-3-Clause; Andreas Naive and Nicola Salmoria). The QSound model follows MAME's. Hardware facts follow MAME's CPS-1 and CPS-2 drivers. The CPS-1 Kabuki keys are not stored; they are "worked out from the player's own ROM" — [README](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/README.md)
- ROM and asset handling:
  - "No game files are included". Players need their own ROM set plus the CPS-2 key file, and "Your ROM sets are only ever read".
  - The `make GAME=<id> explore` step (about 10 minutes) translates the code on the user's machine.
  - CONTRIBUTING forbids adding anything from a game, anything generated from a game, any key, or anything from leaked material.

  — [README](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/README.md); [CONTRIBUTING.md](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/CONTRIBUTING.md)
- Platforms: macOS 13+, Linux x86_64 and ARM64 (SteamOS included), Windows 10/11 and Android 9+, with Vulkan. Extras include rollback netplay, save states, run-ahead, widescreen (fighting games), shaders and an optional cycle-timing mode "checked frame by frame against a cycle-exact model" of the board — [README](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/README.md)

**AvP inside cps2recomp (games/avsp)**
- Status: "**Beta.** The game plays through its first rounds in made-up play and its code is checked instruction by instruction, but nobody has played it by hand yet." Features: three players, start-at-round, score attack, stage and model viewers, cheats, custom soundtrack. Linux x86_64 and SteamOS are supported. Required set: `avspu` with `avspu.key`. The other 940520 regional sets also work. "Some older collections have the set without its key file, or with older dumps of four graphics ROMs (avp.14m, 16m, 18m, 20m): those will not do." — [games/avsp/README.md](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/games/avsp/README.md)
- Progress notes, dated 2026-10-18:
  - "`make explore` found the code (82,889 instructions; none left to the interpreter but 25 a guess took for code)".
  - "the sound program, Capcom's QSound driver of November 1993, is translated too (2,153 instructions). `make check` passes."
  - A RAM map is documented, for example: A5 = FF8000; three player records of 0x100 from FF8380; an enemy pool of 24 records of 0xC0 from FF9280; the camera at FF8268; the show and attract state table at 004706.

  — [games/avsp/PROGRESS.md](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/games/avsp/PROGRESS.md)
- Not done yet, per the same notes:
  - two music pieces are not placed, and the endings have not been reached;
  - the stage viewer has gaps;
  - weapon cheats are not found;
  - "Nobody has played it by hand; the sound has not been listened to."

  — [games/avsp/PROGRESS.md](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/games/avsp/PROGRESS.md)
- Timeline from git:
  - On 2026-10-18 three commits added AvP: the game itself (three players, free play, settings, cheats, start-at-round), then its pages and notes, then the custom soundtrack. Cadillacs and Dinosaurs was added the same day.
  - Later AvP-related commits run to 2026-11-04 ("The picture at the game's level…").
  - The AvP-specific source in `games/avsp/src` is 9 files of about 38 KB. All translated code is generated at build time from the user's ROM.

  — [repo](https://github.com/tmcleroy/cps2recomp) (git log, `git ls-tree`)
- The README notes that the "names header's addresses are numbers" (avsp.h), meaning the repo publishes symbol names and addresses but no disassembly listing — [games/avsp/README.md](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/games/avsp/README.md)

**Other CPS-2 and CPS-1 projects**
- `ohackercego/ddsom-recomp`: D&D: Shadow over Mystara (CPS-2, `ddsom`/`ddsomu`, build 950101), built on the cps2recomp toolkit.
  - 8 commits between 2026-10-21 and 2026-10-23 (authors "azurejoga" 7, ohackercego 1); 2 stars.
  - Unlike upstream, the repo **commits the generated translation** ("`work/ddsom/` … thousands of generated `native_*.cpp` … This is the actual native translation of the original program") and a prebuilt Windows `ddsom.exe` (~21 MB).
  - It leaves out the ROM and the 20-byte key.

  — [ddsom-recomp README](https://raw.githubusercontent.com/ohackercego/ddsom-recomp/HEAD/README.md); [repo](https://github.com/ohackercego/ddsom-recomp)
- `sp00nznet/cps1recomp`: "Drop-in CPS1 hardware for your static recompilation project" (created 2026-03-21, last push 2026-09-21, 4 stars).
  - Hardware: Z80 interpreted, YM2151 through ymfm, its own OKI6295 decoder and a software CPS-A/B renderer.
  - Its game table lists SF2 "In Progress" and Final Fight, Ghouls, Strider "Planned"; Captain Commando and Knights of the Round are listed with no status.

  — [cps1recomp README](https://raw.githubusercontent.com/sp00nznet/cps1recomp/HEAD/README.md)
- `sp00nznet/sf2`: SF2 recompiled on cps1recomp. It runs "from boot to the character-select screen". One CPS-B register still uses a "provisional readback value (`0x0407`)". It needed per-fiber 68k register snapshots to fix the game's cooperative task system — [sf2 README](https://raw.githubusercontent.com/sp00nznet/sf2/HEAD/README.md)
- `Xalcker/SF2Recomp` (created 2026-10-21, last push 2026-11-05, GPL-2.0):
  - Static recompilation of SF2 World Warrior (`sf2`, 910522) to portable C.
  - Says outright that it is "developed with AI assistance (Claude)".
  - "frame-exact against MAME 0.289 on fourteen full playthroughs" (603,050 frames), covering 73.8% of the code with no fallback.
  - Runs on macOS, Linux, Windows and WebAssembly.

  — [SF2Recomp README](https://raw.githubusercontent.com/Xalcker/SF2Recomp/HEAD/README.md)
- `ArthurReboulSalze/RetroRecomp` (created 2026-09-27, last push 2026-11-08): a multi-system recompiler front-end with Capcom CPS-1 and CPS-2 profiles. CPS-2 is not among the six systems it marks experimental. "Powered by mstan & RetroPortingToolKit" — [RetroRecomp README](https://raw.githubusercontent.com/ArthurReboulSalze/RetroRecomp/HEAD/README.md)
- `sunkpoet-lang/neogeo-recomp`: Neo Geo ports "built on the static recompilation toolkit of CPS-2 Recomp". It reuses the CPS-2 toolkit's 68000/Z80 translators and launcher for KOF '97, '98 and 2002 — [neogeo-recomp README](https://raw.githubusercontent.com/sunkpoet-lang/neogeo-recomp/HEAD/README.md)

**Pre-2026 and hand-made CPS work**
- SF2 Platinum (Ben Torkington): Kotaku Australia described it as an attempt to reverse engineer Street Fighter 2 and code it from the ground up for modern systems in C and OpenGL. This comes from a search snippet; the page was not reachable — [Kotaku AU](https://www.kotaku.com.au/?p=814688)
  - An aggregator lists `bentorkington/sf2ww` as "A clone of Street Fighter 2 World Warrior, written from scratch in C + OpenGL", about 97 stars, last updated February 2025 — [relatedrepos](https://relatedrepos.com/gh/bentorkington/sf2ww)
  - Ben Torkington's CPS-1 sound tool README says "Talk to me at @sf2platinum on Twitter", which links the handle to him. That tool is `bentorkington/cps1-sound-extract` (2020-09-04 to 2022-01-30, 13 stars), "Tools for extracting MIDI files and samples from CPS1 based arcade games" — [cps1-sound-extract README](https://raw.githubusercontent.com/bentorkington/cps1-sound-extract/HEAD/README.md)
  - The org repo `sf2platinum/sf2platinum` exists (created and last pushed 2015-12-28, 1 star) but its README is not retrievable — [GitHub search API result](https://github.com/sf2platinum/sf2platinum)
- Fabien Sanglard has published technical write-ups on SF2's CPS-1 sound system and sprite sheets, which document the hardware rather than port the game — [sf2_sound_system](https://fabiensanglard.net/sf2_sound_system/); [sf2_sheets](https://fabiensanglard.net/sf2_sheets/)
- `cerroverb/ffight-disasm` (created 2026-11-08): "Final Fight CPS1 disassembly tools (no ROM data)". It is the only CPS-1 Final Fight disassembly the GitHub search found. Other "final fight disassembly" hits were for the NES Mighty Final Fight (`ghostdogtm/mighty_final_fight_nes_disassembly`, 2026-10-19) — [GitHub search API result](https://github.com/cerroverb/ffight-disasm); [ghostdogtm](https://github.com/ghostdogtm/mighty_final_fight_nes_disassembly)
- Captain Commando: only ROM hacks and editors (`GameHackFan/captre`, "Captain Commando Readjusted (Arcade)", 2022–2023), not disassemblies — [captre](https://github.com/GameHackFan/captre)
- Shadow over Mystara: a C++/SDL "tribute redesign", `Wilhelman/DD-Wrath-of-Silumgar` (2018–2020, 10 stars). It is a fan remake, not reverse engineering — [repo](https://github.com/Wilhelman/DD-Wrath-of-Silumgar)
- `ArcadeHacker/ArcadeHacker_CPS2` (2016–2022, 62 stars): CPS-2 security-key programming, i.e. hardware support for the encryption that ports must handle — [repo](https://github.com/ArcadeHacker/ArcadeHacker_CPS2)

### Inferences
- **Rewriting AvP from scratch would duplicate work.** A working beta static recompilation of AvP, on Linux, with a documented RAM map, already exists in a GPL-3 project that takes outside contributions. What remains open in AvP specifically is: a human-readable annotated disassembly or decompilation (cps2recomp publishes names and addresses, not a listing), hand play-testing, endings, sound checking, and possibly a Wayland-specific frontend (SDL3 supports Wayland natively, but cps2recomp does not mention it).
- Adding a game is fast once a CPS-2 toolkit exists: AvP and D&D SoM each took one to three days in git history. Most of the effort sits in the shared toolkit (the board model, QSound, the code-discovery heuristics), not in each game.
- The `ddsom-recomp` approach, committing generated translated code and a prebuilt exe, carries more legal risk than cps2recomp's model, where the user builds the code from their own ROM.

### Gaps
- When cps2recomp's private development actually began, and how much AI help it had, is unknown. The 19k-line initial import and 724 commits in 26 days suggest heavy tooling or AI help, but no source states it (SF2Recomp states AI help explicitly).
- Whether `bentorkington/sf2ww` was deleted, made private or taken down: it no longer appears in `user:bentorkington` search results. Its README returned 404, and github.com web pages returned HTTP 403 through this session's proxy, so the reason could not be checked.
- No disassembly or decomp was found for Knights of the Round, Armored Warriors, Battle Circuit, Darkstalkers (outside cps2recomp), or any CPS-3 game.

## Q2. Other 68000 arcade and console projects (Sonic, Streets of Rage, Neo Geo, Sega System 16/18, Golden Axe, Shinobi, Amiga)

### Takeaway
The long-running, community-maintained 68000 disassemblies are the Sonic Retro Mega Drive ones. Cannonball (OutRun, Sega OutRun hardware, 68000) is the classic precedent for a hand-rewritten native arcade engine: one main author, years of work. In 2026 a wave of 68000 static recompilers appeared for Mega Drive, Neo Geo and Amiga, plus a family of verified C decompilations of Sega and Konami arcade games (cheviman).

### Cited Findings

**Sonic and Retro Engine**
- `sonicretro/s1disasm` (GitHub repo created 2013-12-02, last push 2026-11-08, 461 stars), `s2disasm` (323 stars) and `skdisasm` (268 stars) are still maintained. The 2013 GitHub dates are migration dates, not when the projects began — [s1disasm](https://github.com/sonicretro/s1disasm); [s2disasm](https://github.com/sonicretro/s2disasm); [skdisasm](https://github.com/sonicretro/skdisasm)
- RSDK decompilations are not of 68000 code. They decompile Christian Whitehead's Retro Engine remasters: `RSDKv4-Decompilation` (Sonic 1/2 2013, 1,158 stars, created 2020-12-15), `Sonic-Mania-Decompilation` (829 stars, 2020-02-13) and `RSDKv3-Decompilation` (Sonic CD 2011, 718 stars, 2020-04-15) — [RSDKv4](https://github.com/RSDKModding/RSDKv4-Decompilation); [Mania](https://github.com/RSDKModding/Sonic-Mania-Decompilation); [RSDKv3](https://github.com/RSDKModding/RSDKv3-Decompilation)
- RSDK FAQ: the decompilation aims "to minimize piracy and ensure an extra layer of legal protection" by requiring the official data files — [RSDKv5 FAQ mirror](https://github.hscsec.cn/RSDKModding/RSDKv5-Decompilation/blob/master/FAQ.md)
- Sonic 68000 static recompilations in 2026:
  - `mstan/segagenesisrecomp` (created 2026-03-25, 60 stars) with Sonic 1, 2 and 3&K recomps (29–40 stars each) — [segagenesisrecomp](https://github.com/mstan/segagenesisrecomp); [Sonic2Recomp](https://github.com/mstan/SonicTheHedgehog2Recomp)
  - `nico3185/pixel_sorcery` (created 2026-10-26): Sonic 1/2/3/S&K, Castle of Illusion, QuackShot and World of Illusion as native C, "checked against the original game running in Genesis Plus GX until the two agree at every controller poll". It distributes no generated C — [pixel_sorcery README](https://raw.githubusercontent.com/nico3185/pixel_sorcery/HEAD/README.md)

**Streets of Rage (closest console beat 'em up analogue)**
- `Dandaman955/Streets-of-Rage-1-Disassembly-Redux` (2015, 5 stars). The author restarted it after losing the original to a broken hard drive — [repo](https://github.com/Dandaman955/Streets-of-Rage-1-Disassembly-Redux)
- `RuiNelson/RageDecompiler` (2026-07-07 to 2026-10-25): "Python disassembly and recompilation tools for Streets of Rage reverse engineering" — [repo](https://github.com/RuiNelson/RageDecompiler)
- `OriginalSwayze/Streets-Of-Rage-Recomp` (created 2026-11-01, 16 stars): SoR 1, 2 and 3 as static recompilations ("not decompilations"); "anything not yet covered runs on an interpreter".
  - Setup downloads a toolchain and builds each game from the user's ROM. "there are no ready-made game programs to download: a built game contains the game's own code, translated to C".
  - The engine comes from the author's Beyond Oasis Recomp.

  — [README](https://raw.githubusercontent.com/OriginalSwayze/Streets-Of-Rage-Recomp/HEAD/README.md)

**Sega arcade (System 16/18/OutRun/System 32)**
- Cannonball, `djyt/cannonball`, by Chris White ("reassembler"): created 2012-09-24, last push 2023-12-26, 891 stars.
  - "The original 68000 and Z80 assembler code has been rewritten in C++ … It requires the original ROMs, as these contain elements including the graphics and audio data." Built for Windows, Mac, Linux, Pandora and Raspberry Pi; Wii, Pi4 and other ports are kept by others — [README](https://raw.githubusercontent.com/djyt/cannonball/HEAD/README.md)
  - In a release post (Dec 2012) the author said the full codebase was decompiled and rewritten in C++, Z80 sound code included. A shmups forum post quotes him calling it the result of "years of reverse engineering". Both come from search snippets — [Sonic Retro forum post](https://forums.sonicretro.org/goto/post?id=724150); [shmups.system11.org](https://shmups.system11.org/viewtopic.php?p=864082)
  - The Reassembler blog had covered porting 68k sprite routines to C++ by November 2010. By August 2012 the whole game was ported except sound and the service mode. Both come from search snippets; the blog was unreachable from this session — [Nov 2010](https://reassembler.blogspot.com/2010/11); [Aug 2012](https://reassembler.blogspot.com/2012/08/light-at-end-of-tunnel.html)
  - Derivative ports are still appearing in 2026: `PicoPlus-devel/pico-outrun` (RP2350, created 2026-09-05), `Xalior/pi-cannonball` (bare-metal Pi, 2026-07-29) and `haroldo-ok/cannonball-outrun-32x` ("WIP vibe-port", 2026-07-27) — [pico-outrun](https://github.com/PicoPlus-devel/pico-outrun); [pi-cannonball](https://github.com/Xalior/pi-cannonball); [32x](https://github.com/haroldo-ok/cannonball-outrun-32x)
- `chaotix359/Super-Hang-On-Ultimate` (created 2026-11-05, v0.9.26 alpha, MIT): a native Windows and macOS port of the arcade Super Hang-On.
  - It uses a 68000→C recompiler, hand patches (`patches/`), a coverage file, Musashi (68000) and Nuked OPM/OPN2.
  - `setup.py` generates the game code from the user's `shangon.zip`.

  — [README](https://raw.githubusercontent.com/chaotix359/Super-Hang-On-Ultimate/HEAD/README.md)
- `cheviman/segasonic-decomp` (System 32, created 2026-10-13, 45 commits, single author "Sebastian Toyos") and `cheviman/outrunners-decomp` (System Multi 32, created 2026-10-20), each with native port repos (`segasonic-port` 38 stars, `outrunners-port` 68 stars). Note that System 32 uses a V60 CPU, not a 68000 — [cheviman repos via GitHub search](https://github.com/cheviman/segasonic-decomp); [outrunners-port](https://github.com/cheviman/outrunners-port)
- Golden Axe: only `fromasmtodisasm/Golden-Axe-2-Disassembly` (Mega Drive, 2018, 0 stars) was found. Searches for OutRun, Shinobi and Golden Axe arcade disassemblies found nothing else — [repo](https://github.com/fromasmtodisasm/Golden-Axe-2-Disassembly)

**Neo Geo**
- `jwestfall69/neogeo-diag-bios` (54 stars) is a disassembly of a diagnostics BIOS. No Metal Slug or KOF disassembly was found. KOF games instead have 2026 static recompilations: `omegakatana92/The-King-of-Fighters-97-Recomp` and `-98-Recomp` (on sp00nznet's neogeorecomp) and `sunkpoet-lang/neogeo-recomp` — [neogeo-diag-bios](https://github.com/jwestfall69/neogeo-diag-bios); [KOF97 recomp](https://github.com/omegakatana92/The-King-of-Fighters-97-Recomp); [neogeo-recomp](https://raw.githubusercontent.com/sunkpoet-lang/neogeo-recomp/HEAD/README.md)

**Amiga and Atari ST**
- `griches/JamesPond2RobocodRecomp` (created 2026-10-25, 23 stars): static recompilation to C++/SDL3. Also `moechofe/AmigaRecomp` (2026-10-10), `OMKR/DuckTales-…-Amiga-Recompilation` ("using Claude", 2026-10-13), and Atari ST in RetroRecomp, marked experimental — [JamesPond2](https://github.com/griches/JamesPond2RobocodRecomp); [DuckTales](https://github.com/OMKR/DuckTales-The-Quest-for-Gold-Amiga-Recompilation); [RetroRecomp](https://raw.githubusercontent.com/ArthurReboulSalze/RetroRecomp/HEAD/README.md)

### Inferences
- Cannonball still stands as the example of a hand rewrite: a single developer, about 2009/2010 to late 2012, a full 68000 + Z80 rewrite, ROMs needed for assets. It became the best-known arcade native port and spawned more than a dozen downstream ports. The cost was multi-year effort for one game.
- On 68000 code, the 2026 recompilers do in days to weeks what hand disassembly and rewriting used to take years to do. The trade-off is readability: generated C/C++ is not a documented source base.

### Gaps
- Sonic 1 disassembly origins (pre-GitHub, Hivebrain era) and Cannonball's exact start date could not be checked from primary sources: reassembler.blogspot.com and Sonic Retro wiki pages were not reachable.
- No Shinobi, Golden Axe (arcade), Metal Slug or KOF hand disassemblies were found. That does not prove none exist off GitHub (romhacking.net was not searched for lack of time and tool budget).

## Q3. Static recompilation relevant to 68000, general recomp precedent, and use on CPS1/CPS2

### Takeaway
68000 static recompilation went from almost nothing to a crowded field in 2026: at least six independent Mega Drive recompilers, two CPS-1 toolkits, one CPS-2 toolkit (cps2recomp) and two Neo Geo toolkits. All of them follow N64Recomp, XenonRecomp and PS2Recomp. The method has already been applied to CPS-1 (SF2, Dino, Punisher, Ghouls) and CPS-2 (AvP, D&D SoM and about 20 others).

### Cited Findings
- General precedent:
  - `N64Recomp/N64Recomp` (created 2022-11-16, 8,368 stars) — [repo](https://github.com/N64Recomp/N64Recomp)
  - `hedge-dev/XenonRecomp` (created 2024-09-07, 6,685 stars) and `hedge-dev/UnleashedRecomp` (5,358 stars) — [XenonRecomp](https://github.com/hedge-dev/XenonRecomp); [UnleashedRecomp](https://github.com/hedge-dev/UnleashedRecomp)
  - `rexglue/rexglue-sdk` (created 2026-01-22, 1,264 stars) — [rexglue](https://github.com/rexglue/rexglue-sdk)
  - `ran-j/PS2Recomp` (created 2025-04-12, 3,815 stars) — [PS2Recomp](https://github.com/ran-j/PS2Recomp)
  - `arcanite24/gb-recompiled` (created 2026-01-03, 458 stars) — [gb-recompiled](https://github.com/arcanite24/gb-recompiled)
- 68000 recompilers for Mega Drive/Genesis:
  - `sp00nznet/genrecomp` (created 2026-03-15; alpha; "The chips come from Genesis Plus GX. The 68000 is never emulated"; two titles playable) — [genrecomp README](https://raw.githubusercontent.com/sp00nznet/genrecomp/HEAD/README.md)
  - `mstan/segagenesisrecomp` (2026-03-25, "R.A.I.D. community") — [repo](https://github.com/mstan/segagenesisrecomp)
  - `nico3185/pixel_sorcery` (2026-10-26) — [README](https://raw.githubusercontent.com/nico3185/pixel_sorcery/HEAD/README.md)
  - `testdriveupgrade/MegaDriveRecomp` (2026-04-28, 22 stars) — [repo](https://github.com/testdriveupgrade/MegaDriveRecomp)
  - `GalaxyShad/MegaDriveRecompiler` (2025-03-12) — [repo](https://github.com/GalaxyShad/MegaDriveRecompiler)
  - `matiaszanolli/aerobiz-disasm` ("Complete static recompilation of Aerobiz Supersonic", 2026-02-23) — [repo](https://github.com/matiaszanolli/aerobiz-disasm)
  - `ohackercego/AlisiaDragoonRecomp` (2026-10-24) says "**100% recompiled** … zero ROM addresses fall back to the Tier-3 interpreter", with the Z80 also recompiled — [README](https://raw.githubusercontent.com/ohackercego/AlisiaDragoonRecomp/HEAD/README.md)
- Other 68000-side toolkits:
  - `vs-sr-dev/saturnkit` (2026-09-26) replaces the Saturn's hardware, the sound 68000 included — [repo](https://github.com/vs-sr-dev/saturnkit)
  - `mstan/cdirecomp` (CD-i, 68000-family CPU, 2026-06-19) — [repo](https://github.com/mstan/cdirecomp)
- On CPS-1 and CPS-2: cps2recomp (tmcleroy), cps1recomp + sf2 (sp00nznet), SF2Recomp (Xalcker), RetroRecomp's CPS-1 and CPS-2 profiles, and ddsom-recomp. All are listed in Q1 with sources.
- Common technical patterns:
  - **Code discovery and coverage:**
    - cps2recomp drives the count of interpreter-run code to zero with "made-up play" — [TOOLKIT.md](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/docs/TOOLKIT.md)
    - SF2Recomp reports 73.8% of code executed with no fallback — [SF2Recomp](https://raw.githubusercontent.com/Xalcker/SF2Recomp/HEAD/README.md)
    - Streets of Rage Recomp runs uncovered code on an interpreter — [SoR Recomp](https://raw.githubusercontent.com/OriginalSwayze/Streets-Of-Rage-Recomp/HEAD/README.md)
  - **Verification:**
    - frame-exact against MAME (SF2Recomp, tmntarcade-decomp) — [SF2Recomp](https://raw.githubusercontent.com/Xalcker/SF2Recomp/HEAD/README.md); [tmntarcade-decomp](https://raw.githubusercontent.com/cheviman/tmntarcade-decomp/HEAD/README.md)
    - per-poll matching against Genesis Plus GX (pixel_sorcery) — [pixel_sorcery](https://raw.githubusercontent.com/nico3185/pixel_sorcery/HEAD/README.md)
    - interpreter-versus-translation checks and per-frame hashes (cps2recomp) — [TOOLKIT.md](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/docs/TOOLKIT.md)
  - **Arcade task systems:** cooperative task and fiber systems in Capcom code needed special handling (sp00nznet/sf2 had to snapshot 68k registers per fiber) — [sf2 README](https://raw.githubusercontent.com/sp00nznet/sf2/HEAD/README.md)
- AI help is stated openly by several 2026 projects:
  - SF2Recomp ("developed with AI assistance (Claude)") — [SF2Recomp](https://raw.githubusercontent.com/Xalcker/SF2Recomp/HEAD/README.md)
  - DuckTales Amiga ("using Claude") — [repo](https://github.com/OMKR/DuckTales-The-Quest-for-Gold-Amiga-Recompilation)
  - Pilotwings 64 ("AI-coded") — [repo](https://github.com/danielgomesvieira2000/pilotwings-64-recomp)
  - the Cannonball 32X port ("vibe-port") — [repo](https://github.com/haroldo-ok/cannonball-outrun-32x)

### Inferences
- For CPS-2 in particular, the CPS-2 encryption (per-game key, MAME's cps2crypt) and QSound are solved, shared problems in cps2recomp. A new AvP project would face them again unless it reuses that GPL code, which would also put the new project under the GPL.
- A static recompile's translated code is tied to one ROM revision ("each port is made from one version's program"). For AvP all regions are one program revision (per PROGRESS.md), so this costs nothing here.

### Gaps
- How mature the many 2026 Mega Drive recompilers are relative to each other could not be compared; most are less than a year old and self-reported.

## Q4. Other arcade native ports via reverse engineering (beat 'em ups and 68000 first)

### Takeaway
The best match to AvP outside Capcom is Konami's TMNT (1989, 68000 + Z80, four-player beat 'em up). In 2026 it got a full verified C decompilation with every function named, and a native multi-platform port (`cheviman/tmntarcade-decomp` and `tmnt-port`), with The Simpsons decomp just begun. No Technos (Double Dragon), Toaplan, Psikyo or Data East disassemblies or native ports were found. For those, FPGA cores are the main preservation effort.

### Cited Findings
- `cheviman/tmntarcade-decomp` (created 2026-10-29; 20 commits, all by "Sebastian Toyos"; 17 stars). Status "As of 04-11-2026":
  - 18 test scenarios over 513,383 frames, running 25,526 addresses of the 68000 program.
  - A MAME-identical 68000 disassembler, and a static analysis that finds 28,515 instructions.
  - "Every byte of both programs explained: the 68000's 32.5 % code, 65.9 % data".
  - "2,058 functions of the 68000 program and 381 of the sound program, no goto, every function, variable … with a name".
  - "The game matches the reference in state, picture and sound in all 18 scenarios, frame by frame".
  - The board is rebuilt in C, with the Konami video chips drawing "what MAME draws pixel for pixel" and ymfm for the YM2151.
  - Assets are extracted to sheets, WAV and MIDI and "build back into the ROM set byte for byte".

  — [README](https://raw.githubusercontent.com/cheviman/tmntarcade-decomp/HEAD/README.md); [repo](https://github.com/cheviman/tmntarcade-decomp) (git log)
- Method note: it follows the method of the same author's segasonic-decomp and outrunners-decomp and shares a core, `cheviman/arcade-decomp`. As with sm64, "you bring your own ROM set … the tools verify it, extract the assets, and you build your own executable, which runs from the assets and opens no ROM" — [README](https://raw.githubusercontent.com/cheviman/tmntarcade-decomp/HEAD/README.md)
- `cheviman/tmnt-port` (created 2026-11-04, 44 stars, BSD-3):
  - TMNT Arcade, plus a "console version" with boss rush and other modes.
  - Platforms: Windows, Linux, macOS, Switch (NSP built locally), Android and Anbernic handhelds.
  - LAN multiplayer via `cheviman/arcade-lan`.
  - "What a tool makes has the game's data in it: it is yours alone, never share it."

  — [README](https://raw.githubusercontent.com/cheviman/tmnt-port/HEAD/README.md)
- `cheviman/simpsons-decomp` (created 2026-11-05): "A decompilation of Konami's 1991 arcade game The Simpsons (053248 + Z80) into readable C, checked frame by frame against MAME". Note that the 053248 is a Konami 6809-derivative CPU, not a 68000 — [GitHub search API result](https://github.com/cheviman/simpsons-decomp)
- Older TMNT fan efforts are remakes, not reverse engineering: `codeck1/TMNT-Arcade` (2016) and `valenzuelagustavo/TMNT-ARCADE-MEGADRIVE-PORT` (2026, a Genesis port) — [codeck1](https://github.com/codeck1/TMNT-Arcade); [valenzuelagustavo](https://github.com/valenzuelagustavo/TMNT-ARCADE-MEGADRIVE-PORT)
- Toaplan: the GitHub results are FPGA cores (`va7deo/zerowing` Toaplan V1 for MiSTer, 49 stars; Toaplan V2 cores), not disassemblies — [zerowing](https://github.com/va7deo/zerowing)
- Williams: `ScottTunstall/Robotron2084` "Annotated reverse engineering of Robotron 2084 arcade" (2025-03-01, 4 stars) — [repo](https://github.com/ScottTunstall/Robotron2084)
- Taito Rastan: `antxiko/RastanSaga-disassembly` is the MSX2 version (Z80), "a commented disassembly that reassembles byte for byte" (2026-10-04), not the arcade — [repo](https://github.com/antxiko/RastanSaga-disassembly)
- Donkey Kong: `RussianManSMWC/Donkey-Kong-NES-Disassembly` (30 stars) is the NES version, not the arcade — [repo](https://github.com/RussianManSMWC/Donkey-Kong-NES-Disassembly)

### Inferences
- tmntarcade-decomp is the strongest model for a "readable source" deliverable for a 68000 beat 'em up: a matching or behaviour-verified C decomp checked against MAME, plus an asset extractor and a native runtime. It is complementary to cps2recomp's opaque translated code. An AvP project that wants to stand apart from cps2recomp would aim for this kind of output.
- AvP's 82,889 instructions (cps2recomp count) are about 2.9 times TMNT's 28,515, so a full named decomp of AvP is a much bigger job than TMNT. This is a rough comparison: the two tools count differently.

### Gaps
- No Double Dragon (Technos) arcade disassembly, Psikyo or Data East reverse-engineering project, Galaxian/Pac-Man arcade reimplementation, or Defender disassembly turned up in GitHub search. romhacking.net, Codeberg and GitLab were not searched within the tool budget.
- How long tmntarcade-decomp took in practice is unclear: its public history covers only 2026-10-29 to 2026-11-07, which suggests earlier private work or heavy automation, and no source says which.

## Q5. Effort: years, contributors, method, and how graphics and sound hardware were handled

### Takeaway
Effort falls into three tiers.
1. **Hand rewrite**, as with Cannonball: one person, years.
2. **Verified decomp with a shared toolkit**, as with cheviman: one person, weeks of public history per game.
3. **Static recompilation with a shared board model**, as with cps2recomp: one person, days per game once the toolkit exists.

Nearly every project rebuilds the video in its own code, using MAME as the reference. Sound is either embedded third-party chip cores (ymfm, Nuked, Genesis Plus GX) or reimplemented, sometimes with the sound CPU's own driver translated too.

### Cited Findings

Catalog summary. Sources are in the per-project entries above.

| Project | Target (CPU) | Author / team | Start → last activity | Method | Native playable? | ROM/asset handling | Graphics/sound |
|---|---|---|---|---|---|---|---|
| tmcleroy/cps2recomp | 29 CPS-1/CPS-2 games incl. **AvP** (68000+Z80) | T. McLeroy (+2 minor) | repo 2026-10-13 (earlier private) → 2026-11-08 | static recomp to C++ + hand rewrites | Yes; AvP beta | user ROM + key; code generated locally | own video; QSound modelled on MAME; Z80 translated |
| ohackercego/ddsom-recomp | D&D SoM CPS-2 | azurejoga, ohackercego | 2026-10-21 → 10-23 | cps2recomp toolkit | Yes (Windows exe) | ROM/key excluded, but generated code + exe committed | as cps2recomp |
| sp00nznet/cps1recomp + sf2 | CPS-1 SF2 | sp00nznet | 2026-03-21 → 09-21 | static recomp to C | Partly (to char select) | user ROM | own renderer; Z80 interpreted; ymfm |
| Xalcker/SF2Recomp | CPS-1 SF2 | Xalcker, AI-assisted | 2026-10-21 → 11-05 | static recomp to C | Yes | user ROM; generated at build | frame-exact vs MAME 0.289 |
| djyt/cannonball | OutRun (68000+Z80) | Chris White (+ porters) | about 2010 → 2012 release → 2023 push | hand rewrite in C++ | Yes | needs original ROMs for assets | reimplemented, Z80 sound code rewritten |
| cheviman/tmntarcade-decomp + tmnt-port | Konami TMNT (68000+Z80) | Sebastian Toyos | 2026-10-29 → 11-08 | verified C decomp | Yes (PC, Switch, Android) | assets extracted from user ROM | board in C; ymfm; MAME-exact |
| chaotix359/Super-Hang-On-Ultimate | Sega Super Hang-On (68000) | chaotix359 | 2026-11-05 → 11-07 | recomp + patches | Yes (alpha) | user ROM; code generated by setup.py | Musashi, Nuked OPM/OPN2 |
| OriginalSwayze/Streets-Of-Rage-Recomp | MD SoR 1-3 (68000) | OriginalSwayze | 2026-11-01 → 11-09 | static recomp + interpreter fallback | Yes | built on user PC from ROM | from Beyond Oasis Recomp engine |
| sonicretro s1/s2/skdisasm | MD Sonic (68000) | community | pre-2013 → 2026-11 | hand disassembly | No (reassembles ROM) | no ROM in repo | n/a |
| SF2 Platinum / sf2ww | CPS-1 SF2 | Ben Torkington | repo 2015 → aggregator says Feb 2025 | RE + C/OpenGL rewrite | Unverified | Unverified | Unverified |

- Cannonball's effort: "years of reverse engineering" (author, via search snippet); the 2010 blog covered sprite routines and August 2012 had the whole game except sound and service mode — [shmups.system11.org](https://shmups.system11.org/viewtopic.php?p=864082); [reassembler Aug 2012](https://reassembler.blogspot.com/2012/08/light-at-end-of-tunnel.html)
- Hand-matching decomps of 68000 code are slow by comparison. The Zelda OoT N64 decomp, MIPS rather than 68000 but cited for scale, took a large team about 18+ months to near completion — [Nintendo Life 2021](https://www.nintendolife.com/news/2021/08/after_18_months_zelda_ocarina_of_time_fans_are_almost_done_decompiling_the_game)
- `biggestsonicfan/stfdecomp` (Model 2, i960) is "an accumulation of many years of work" with several named collaborators. It shows how slowly a pre-AI decomp of a mid-90s arcade engine moves — [README](https://raw.githubusercontent.com/biggestsonicfan/stfdecomp/HEAD/README.md)
- Hardware approaches:
  - Board reimplemented natively: cps2recomp, tmntarcade-decomp, cps1recomp — [cps2recomp TOOLKIT](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/docs/TOOLKIT.md); [tmntarcade-decomp](https://raw.githubusercontent.com/cheviman/tmntarcade-decomp/HEAD/README.md); [cps1recomp](https://raw.githubusercontent.com/sp00nznet/cps1recomp/HEAD/README.md)
  - Emulator chip cores embedded: genrecomp (Genesis Plus GX), Super Hang-On Ultimate (Musashi + Nuked) — [genrecomp](https://raw.githubusercontent.com/sp00nznet/genrecomp/HEAD/README.md); [SHO Ultimate](https://raw.githubusercontent.com/chaotix359/Super-Hang-On-Ultimate/HEAD/README.md)

### Inferences
- Lesson 1: for AvP, the cheapest route to a playable native Linux build is to use or contribute to cps2recomp (AvP is already there). The remaining value lies in readability and documentation (a disassembly or decomp), testing, and platform polish (Wayland).
- Lesson 2: a hand-annotated disassembly of AvP is likely a multi-year single-person job if done the Cannonball way. AI-assisted and toolkit-driven approaches seem to compress this a great deal, but how much is not documented.
- Lesson 3: the shared pieces (CPS-2 decryption, CPS-A/B video, QSound, the Z80 driver) take most of the effort and are already available under GPL-3 (cps2recomp) or as MAME references.

### Gaps
- No project published hour counts. The effort numbers above are calendar time and commit counts, not person-hours.
- Whether SF2 Platinum was ever playable could not be checked.

## Q6. Legal outcomes of comparable projects

### Takeaway
No takedown of a disassembly, decomp or recomp of a CPS game was found as of 2026-11-09. The large 2026 recomp scene, cps2recomp included, works under a "tools only, bring your own ROM, generate code locally" model and is still online. Capcom does enforce against fan games that use its characters and against mods and translations. Sega shut down Streets of Rage Remake in 2011 but tolerates non-commercial Sonic projects. Nintendo has left the matching decomps alone but went after distributed PC-port builds. AvP adds a second rights holder (20th Century Studios/Disney) for the Alien and Predator IP.

### Cited Findings
- GitHub DMCA repository: a code search for "capcom" in `github/dmca` returns only 4 files.
  - A 2020-01-10 Capcom notice against `SHNecro/ShanghaiEXE`, a Mega Man Battle Network fan game — [notice](https://github.com/github/dmca/blob/master/2020/01/2020-01-10-capcom.md)
  - A 2025-01-30 Capcom notice against a Dragon's Dogma Online translation repo. GitHub "did not find sufficient information to determine a valid anti-circumvention claim" but found "other valid copyright claim(s)" — [notice](https://github.com/github/dmca/blob/master/2025/01/2025-01-30-capcom.md)
  - The other two hits are an ESA notice and a data CSV. None concerns CPS games or reverse engineering of arcade code.
- Capcom forced the fan fighting game "SEGA VS CAPCOM: THE NEXT LEVEL" offline in September 2026 for using Capcom characters. This comes from search snippets; the primary page was unreachable — [Time Extension](https://www.timeextension.com/news/2026/09/sega-vs-capcom-fan-project-shut-down-for-using-capcoms-characters-and-likeness); [Netto's Game Room](https://www.nettosgameroom.com/2026/09/capcom-shuts-down-sega-vs-capcom-next.html)
- Capcom issued DMCA notices to Street Fighter V costume modders (2017) — [TechSpot](https://www.techspot.com/news/70475-capcom-hands-out-dmca-takedown-notices-street-fighter.html); [PC Gamer](https://www.pcgamer.com/au/street-fighter-costume-modders-issued-dmca-takedown-notice-from-capcom)
- Capcom backed and released the fan game Street Fighter X Mega Man in 2012 (per search summary) — [Destructoid](https://destructoid.com/?p=239869)
- Sega sent Bomber Games a cease-and-desist for Streets of Rage Remake in April 2011, shortly after release. Bomber Games complied. Sega said it "need[s] to protect our intellectual property rights" — [Engadget](https://www.engadget.com/2011-04-11-streets-of-rage-remake-taken-down.html); [Game Informer](https://www.gameinformer.com/b/news/archive/2011/04/13/sega-pulls-fan-made-streets-of-rage-remake-39-to-protect-ip-39.aspx); [Wikipedia](https://en.wikipedia.org/wiki/Streets_of_Rage_Remake)
- Sega said in 2021 it usually has no issue with non-monetized Sonic fan games, "for legal reasons" with occasional exceptions — [Nintendo Life](https://www.nintendolife.com/news/2021/05/sega_is_still_cool_with_sonic_fan_games_provided_no_profit_is_involved)
- Sega later worked with Christian Whitehead, whose Retro Engine fan work led to official ports. Before licensing his technology, Sega checked he had not used its code — [PowerUp Gaming, 2026-11-03](https://powerupgaming.co.uk/2026/11/03/sega-had-to-make-sure-sonic-mania-head-hadnt-stolen-sonics-code-before-working-with-him/)
- Nintendo: the SM64 decompilation (2019) itself was not taken down. In May 2020 Nintendo filed copyright complaints against sites hosting compiled builds of the SM64 PC port, and against videos — [VGC](https://www.videogameschronicle.com//news/nintendo-takes-action-against-mario-64-pc-port); [Nintendo Life](https://www.nintendolife.com/news/2020/05/nintendo_cracks_down_on_the_super_mario_64_pc_port); [GameSpot](https://gamespot.com/articles/nintendo-is-trying-to-shut-down-that-super-mario-6/1100-6477117/)
- The legality of publishing reverse-engineered code is treated in academic work as unsettled (fair use analysis) — [UC Law SF Hastings Sci & Tech LJ](https://repository.uclawsf.edu/hastings_science_technology_law_journal/vol12/iss1/3)
- Mitigations the comparable projects use:
  - cps2recomp: no game data, no keys, no generated code, no pointers to ROM sources; "not affiliated with … Capcom or 20th Century Studios" — [CONTRIBUTING.md](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/CONTRIBUTING.md); [AvP page](https://raw.githubusercontent.com/tmcleroy/cps2recomp/HEAD/games/avsp/README.md)
  - Cannonball: requires the original ROMs — [README](https://raw.githubusercontent.com/djyt/cannonball/HEAD/README.md)
  - tmnt-port: tells users the built output "is yours alone, never share it" — [README](https://raw.githubusercontent.com/cheviman/tmnt-port/HEAD/README.md)
  - Streets of Rage Recomp: refuses to ship built programs — [README](https://raw.githubusercontent.com/OriginalSwayze/Streets-Of-Rage-Recomp/HEAD/README.md)

### Inferences
- The pattern across Capcom, Sega and Nintendo is that enforcement targets distributed playable builds, assets and character use in new fan games far more than tools-only reverse-engineering repos. A "bring your own ROM and key, generate locally" AvP project matches the model that has survived so far. That is not a legal guarantee.
- AvP's licensed IP (Capcom code and art; Alien and Predator characters owned by 20th Century Studios/Disney) adds a second possible claimant. That may make a takedown more likely than for Capcom-owned titles, though no source shows enforcement for this game.
- `ddsom-recomp` committing generated code derived from the ROM, plus an exe, is the kind of artifact most likely to draw a notice (by analogy with Nintendo's 2020 actions against compiled builds).

### Gaps
- No primary-source statement from Capcom on disassemblies, decomps or recomps of its arcade games was found.
- Whether Disney or 20th Century Studios has ever enforced against AvP arcade fan or RE projects was not found.
- The 2026 Time Extension article could not be fetched (host blocked in this session), so the details of the SEGA VS CAPCOM shutdown rest on search snippets.
