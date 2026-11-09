# Alien vs. Predator (Capcom CPS-2, 1994): existing RE, hacking and porting work, plus hardware and software parameters

Research date: 2026-11-09. Method note: in this session only GitHub (raw.githubusercontent.com, plus GitHub search APIs) and gitlab.com could be reached directly. Wikipedia, sudden-desu.net, tcrf.net, tasvideos.org, hardcoregaming101.net, arcade-projects.com, bilibili, gitee, archive.org, codeberg.org and speedrun.com were blocked by the session's network policy. Findings from those sites come only from search-engine summaries, and they are marked that way below. Everything taken from GitHub-hosted source (MAME, HBMAME, cps2recomp, mame-rr, FBNeo cheats) was read directly.

## 1. Does a public disassembly, decompilation, ROM map, IDA/Ghidra database or source reimplementation exist?

### Takeaway
No classic annotated disassembly or IDA/Ghidra database of AvP was found. There is something more advanced, though: as of October 2026 a working **static recompilation** of the entire game exists. It is **tmcleroy/cps2recomp** (GPL-3.0-only, active as of 2026-11-09), with a published, documented RAM and ROM map for the `avspu` set. A second, thinner standalone repo (**omegakatana92/Alien-vs-Predator-arcade-Recomp-**, 2026-10-17) uses the same toolkit, and an **empty** Saturn port repo was created on 2026-11-06.

### Cited Findings
**tmcleroy/cps2recomp (main project; covers AvP among about 29 CPS-1/CPS-2 games)**
- Project description: "CPS-2 Recomp: unofficial native PC ports of Capcom CPS-2 arcade games ... via static recompilation". Repo created 2026-10-13, last pushed 2026-11-09T02:58Z, 171 stars at search time, licence GPL-3.0 — [GitHub search API result for tmcleroy/cps2recomp](https://github.com/tmcleroy/cps2recomp)
- How it works: "Each game's 68000 program is translated ahead of time into C++ and compiled into that game's program, and the parts its features touch are rewritten by hand as readable C++, each checked call by call against the game's own code. The board (video, the QSound chip, the sound CPU, the settings memory) is code written for this project, not an emulator." No ROM data is in the repo; users supply their own set — [cps2recomp README](https://github.com/tmcleroy/cps2recomp/blob/HEAD/README.md)
- The project's game table lists "Alien vs. Predator (1994) | `avspu` (USA 940520) | Beat-'em-up: three players, a stage to start at, score attack" — [cps2recomp README](https://github.com/tmcleroy/cps2recomp/blob/HEAD/README.md)
- AvP status: "**Beta.** The game plays through its first rounds in made-up play and its code is checked instruction by instruction, but nobody has played it by hand yet." Builds for macOS, Linux/Steam Deck and Windows. Features: 3 players, start at any of 7 rounds, score attack, stage viewer, model viewer, attract-mode modes, custom soundtrack, rapid fire, cheats (infinite health, lives, time), the board's operator settings, run-ahead — [cps2recomp games/avsp/README.md](https://github.com/tmcleroy/cps2recomp/blob/HEAD/games/avsp/README.md)
- Other accepted sets: `avsp`, `avspj`, `avspa` and `avsph` are accepted as "the same release's other sets". Older collections with the pre-2021 graphics dumps of `avp.14m/16m/18m/20m`, or with no key file, "will not do" — [games/avsp/README.md](https://github.com/tmcleroy/cps2recomp/blob/HEAD/games/avsp/README.md)
- Translation coverage, dated "How it is made (2026-10-18)": "`make explore` found the code (82,889 instructions; none left to the interpreter but 25 a guess took for code); the sound program, Capcom's QSound driver of November 1993, is translated too (2,153 instructions). `make check` passes." — [games/avsp/PROGRESS.md](https://github.com/tmcleroy/cps2recomp/blob/HEAD/games/avsp/PROGRESS.md)
- Changelog: AvP (and CPS-1 Cadillacs and Dinosaurs) arrived in release **0.4.0-beta.2** as "Two beat-'em-ups for three players ... Both translated whole and checked (`make check`)". Release 0.3.0 is dated 2026-10-15; later releases (through 1.4.0 and "Unreleased") carry no dates. Later releases added beat-'em-up modes (attract, score attack, stage and model viewers) and a native palette upload "in eight games ... Alien vs. Predator" — [cps2recomp CHANGELOG.md](https://github.com/tmcleroy/cps2recomp/blob/HEAD/CHANGELOG.md)
- Region handling: game.cfg says "avspu is the USA release of the one revision (940520); the other regions differ only in their words". It sets `region_at = 000CAC` ("move.w #region,d16(a5)") and `online_words = 000CAE`, and every clone in MAME was "compared with the game's own, deciphered, word by word" — [games/avsp/game.cfg](https://github.com/tmcleroy/cps2recomp/blob/HEAD/games/avsp/game.cfg); [CHANGELOG.md](https://github.com/tmcleroy/cps2recomp/blob/HEAD/CHANGELOG.md)
- game.cfg also gives `code_end = 200000`, `players = 3`, `buttons = Attack | Jump | Shoot`, and a list of the 68000 instruction addresses that write video registers (`video_writes = 0005A4 0005B4 ... 001378`) — [games/avsp/game.cfg](https://github.com/tmcleroy/cps2recomp/blob/HEAD/games/avsp/game.cfg)
- Published names header (GPL-3.0-only, © 2026 Tommy McLeroy) with RAM addresses and how each was found — [games/avsp/src/avsp.h](https://github.com/tmcleroy/cps2recomp/blob/HEAD/games/avsp/src/avsp.h). Its contents are in section 2.
- The project rules forbid committing any game data: "nothing from the game, ever"; "the names header's addresses are numbers" — [games/avsp/README.md](https://github.com/tmcleroy/cps2recomp/blob/HEAD/games/avsp/README.md)

**omegakatana92/Alien-vs-Predator-arcade-Recomp-**
- Description: "Native PC port of Alien vs. Predator (Capcom, 1994, CPS-2 arcade), made by static recompilation with cps2recomp." Created 2026-10-17T03:15Z, last pushed 2026-10-17T04:04Z, 335 KB, C++, GPL-3.0, 2 stars — [GitHub search API result](https://github.com/omegakatana92/Alien-vs-Predator-arcade-Recomp-)
- Uses a vendored copy of the toolkit (`v0.3.0`) and accepts only the `avsp` set (Europe 940520). It refuses `avspa`, `avspj` and `avspu` by checksum. Build targets: `make explore` ("about ten minutes"), `make`, `make check` and `make check-blocks`. Debug flags: `--dump-ram`, `--trace`, `--watch`, `--poke`, `--movie` — [README](https://github.com/omegakatana92/Alien-vs-Predator-arcade-Recomp-/blob/HEAD/README.md)
- "No game-specific address has been found yet: `games/avsp/src/` is empty" — [games/avsp/PROGRESS.md](https://github.com/omegakatana92/Alien-vs-Predator-arcade-Recomp-/blob/HEAD/games/avsp/PROGRESS.md)
- Its README wrongly calls AvP "a trademark of Capcom Co., Ltd.". The cps2recomp page instead disclaims affiliation with "Capcom or 20th Century Studios" — [omegakatana92 README](https://github.com/omegakatana92/Alien-vs-Predator-arcade-Recomp-/blob/HEAD/README.md); [cps2recomp avsp README](https://github.com/tmcleroy/cps2recomp/blob/HEAD/games/avsp/README.md)

**princeendo/avp_saturn_version**
- Description: "Porting Alien vs Predator (Arcade) to Saturn". Created 2026-11-06T14:16:52Z, pushed 2026-11-06T14:16:54Z, **size 0** (empty), no language, 0 stars. No README could be fetched (404 on main and master) — [GitHub search API result](https://github.com/princeendo/avp_saturn_version)

**Other repositories searched (nothing found)**
- GitHub repository searches for "avsp", "alien vs predator cps2", "avsp disassembly", "avsp mame", "alien vs predator disassembly", "avp arcade capcom" and others returned only the three repos above. The rest were unrelated AviSynth or speech projects — [GitHub repository search](https://github.com/search?q=avsp&type=repositories)
- GitHub code search for "Alien vs. Predator" + avsp + ff8000 found only cps2recomp files (`avsp.h`, `PROGRESS.md`, `CHANGELOG.md`). No `.asm` files for `avspu` were found — [GitHub code search](https://github.com/search?q=avsp+ff8000&type=code)
- GitLab project searches ("avsp", "alien vs predator arcade", "avp cps2", "cps2 disassembly") found nothing relevant — [GitLab projects API](https://gitlab.com/api/v4/projects?search=avsp)
- zengfr, a Chinese romhacker who shares IDA databases for arcade games, lists Cadillacs and Dinosaurs, Violent Storm, KOF'97, The Punisher, Final Fight "and others". AvP is not listed, and a code search of zengfr/romhack for "avsp" found only a copy of the beat-'em-up hitbox Lua script — [zengfr/ida-pro-idb-database README](https://github.com/zengfr/ida-pro-idb-database/blob/main/README.md); [zengfr/romhack](https://github.com/zengfr/romhack)
- sudden-desu.net (Ryou) has a disassembly-based article, "Alien vs Predator: Debug Tools and Alternate Staff Credits" (seen only via search summaries). Per the summary it says the code has no references to the CPS2 debug DIP switches but still contains "a bunch of debugging tools and an alternate staff roll". It also gives a cheat script that replaces the standard test menu with a debug menu, and says a hidden test menu "is accessed when the byte @ 0xFF21AA equals 2 while the standard test menu is active" — [sudden-desu.net AvP article](https://sudden-desu.net/entry/alien-vs-predator/). A companion article lists AvP among games using CPS2 debug switches (an apparent contradiction with the first article; seen only via search summary) — [CPS2 Debug Switches and the Games That Love Them](https://sudden-desu.net/entry/cps2-debug-switches-and-the-games-that-love-them)
- TCRF has an "Alien vs. Predator (Arcade)" page. Per the search snippet it covers unused graphics (an unused enemy-troop icon and an unused skulls item) — [TCRF](https://new.tcrf.net/Alien_vs._Predator_(Arcade))

### Inferences
- For a disassembly/port project, cps2recomp is the obvious prior art. It has already solved code discovery (indirect jumps found by "explore" play), opcode decryption at load time, a native CPS-2 board model, and QSound/Z80 translation, and it has proven a full translation of AvP's 68000 code (about 83k instructions). It does not publish a disassembly listing: one is generated locally from the user's ROM (`work/avsp/program.lst`, which the `--watch` instructions in [omegakatana92 PROGRESS.md](https://github.com/omegakatana92/Alien-vs-Predator-arcade-Recomp-/blob/HEAD/games/avsp/PROGRESS.md) refer to), because the ROM is not distributed.
- cps2recomp is GPL-3.0-only, so any project that reuses its code or names headers inherits GPL-3.0 obligations. Facts (addresses) can be independently re-derived.
- The Saturn repo is only a placeholder at the moment and does not count as existing work.

### Gaps
- Could not read the full sudden-desu article or the TCRF page (host blocked). The exact debug-menu addresses, the "MAME driver tweak" and the alternate staff credits remain unverified beyond search snippets.
- Found no Ghidra/IDA database, no annotated `.asm`, and no Japanese or Chinese disassembly write-up for AvP. Japanese and Chinese community sites (bilibili, tieba, gitee, 66rpg) could not be fetched; searches returned only gameplay videos.
- Could not get exact release dates for cps2recomp 0.4.0-beta.2 (the GitHub releases API was blocked for this repo).

## 2. ROM hacks, cheat databases, RAM maps, TAS, speedrun docs, hitbox scripts

### Takeaway
Solid community RAM knowledge exists:
- the mame-rr beat-'em-up hitbox Lua script (2011) gives AvP's object tables and hitbox format;
- the FBNeo cheat file gives player-struct fields;
- MAME's hiscore.dat gives the high-score table address;
- cps2recomp's `avsp.h`/`PROGRESS.md` (2026) is the richest RAM/ROM map, with routine addresses.

HBMAME carries six AvP hack sets (2017–2020). No TAS was found.

### Cited Findings
**Hitbox viewer (mame-rr Lua)**
- `beatemup-hitboxes.lua` prints "CPS-2 beat 'em up hitbox viewer", "November 11, 2011", "http://code.google.com/p/mame-rr/wiki/Hitboxes". Its profile list includes `ffight`, `avsp`, `ddtod` and others — [TASEmulators/mame-rr beatemup-hitboxes.lua](https://github.com/TASEmulators/mame-rr/blob/HEAD/mame-rr/lua/beatemup-hitboxes.lua)
- AvP profile:
  - `screen_left = 0xFF8288`, `game_phase = 0xFFEE0A`
  - object offsets `flip_x = 0x0F`, `pos_x = 0x10`, `hitbox_ptr = 0x50`
  - object tables:
    - players `0xFF8380`, 3 × `0x100`
    - player projectiles `0xFF8680`, 0x18 × `0x80`
    - enemies `0xFF9280`, 0x18 × `0xC0`, hp at +0x40
    - enemy projectiles `0xFFA480`, 0x18 × `0x80`
    - misc `0xFFB080`, 0x3C × `0x80`, harmless
  - box format: bytes val_x, val_y, rad_x, rad_y
  - box lists via anim_ptr `+0x1C`: vulnerability id at +0x08 (id_space 8, table +0x00); attack id at +0x09 (id_space 0x10, table +0x02)
  - the box address is `readdword(obj+0x50) + readwordsigned(that + addr_table) + id*id_space` — [same file, lines 160–192](https://github.com/TASEmulators/mame-rr/blob/HEAD/mame-rr/lua/beatemup-hitboxes.lua)
- Copies of the same script exist in Jesuszilla/mame-rr-scripts, douglaslassance/mame-setup, zengfr/romhack (CPS1/), incstring/Fba-shuffle-v2.4.0 and tuhuihuai/3DMGAME-FBA_shuffle — [GitHub code search "avsp 0xFF8380"](https://github.com/search?q=avsp+0xFF8380&type=code)
- A TASVideos forum thread, "Hitbox scripts for fighting games", is the related discussion (not fetched) — [tasvideos.org/Forum/Topics/9942](https://tasvideos.org/Forum/Topics/9942)

**cps2recomp RAM/ROM map (set `avspu`, 2026)** — all from [avsp.h](https://github.com/tmcleroy/cps2recomp/blob/HEAD/games/avsp/src/avsp.h) and [PROGRESS.md](https://github.com/tmcleroy/cps2recomp/blob/HEAD/games/avsp/PROGRESS.md):
- Base: "The game keeps its variables at A5 = FF8000."
- Attract and game mode:
  - mode word A5+00, sub-step A5+04
  - steps 2–C at boot, then the attract parts every 4 steps from 4 to 68; 0x10 = title, 0x02 = in game, 0x6C = loop end
  - attract routine table at `004706` (routines 486A notices, 4C14 QSound logo, 48DE story, 4938 title, 4C1A character file, 4C98 how-to-play, 4CF6 demo, 48E4 best scores)
  - next attract character at A5-6FF6, advanced at 004E9A
- Credits: A5+18C (byte, max 9; 0016B4 caps it).
- Settings:
  - the EEPROM record's RAM copy is at FF0EF0; routine 003C5E copies it into variables (called at 000D1A, and again on test-menu exit at 0B3C64)
  - variables: coin 1CD (9 = free play), continue 1BE, flip 1B2, demo sound 1AD, sound 1D2, player mode 1CE (0 = three players/three chutes, 1 = three/one chute, 2 = two, the factory default), difficulty 1CF (0–7), extend 1D0, lives 1D1
  - derived: three-players flag 1C5, chute-each flag 1C6
- Progression and clock:
  - scene A5+1E8 (word, steps of 2), set to 2 by 0082DC
  - round shown A5+222 from table 00CCA0; 7 rounds whose first scenes are {0,3,5,6,8,9,14}
  - clock: minutes A5+224, BCD seconds A5+225, frame counter A5+221 (from 0x3C), decremented at 0085A4
- Players: 3 records of 0x100 at FF8380, walked by 01CC3E. Fields:
  - +00 in-play
  - +10 X (word), +14 Y (word)
  - +41 health (0x65 full; FF when down), +45 max health
  - +D2 character (0 Predator Warrior, 1 Maj. Schaefer, 2 Predator Hunter, 3 Lt. Kurosawa)
  - +E0 score (BCD long)
  - +F1 lives
- Camera:
  - record at FF8268: X at +20 (also +10, +28), Y at +24, limits at +30/+32 and +34/+36 from table 0B0550
  - per-frame driver 0AF858; scene camera routines are dispatched from table 0AF8D4 (0AF8B4)
  - 0B0680 follows the players (0B0C22 finds them); 0B06B6 draws new scroll columns every 16 px; 0B0786 handles vertical
  - map page table at A5-6142
- Enemies:
  - pool of 24 × 0xC0 at FF9280; allocator 01769E (Z flag set when full)
  - 01B922 runs the first four, 01B980 the other twenty; kind at +02
  - animation frame pointer at +1C; anim start 016518, step 016536; timer +0A
  - kill writes 04000000 to +04, FFFF to +40/+42, 0C to +49 (0229xx)
  - object draw routine 0A9B48
- Character animation lists at 15E240, 162F90, 168564, 16D122…, reached through tables 01B0E0, 01B104, 021FFA plus code at 021E10. Pictures live in 100000–1FFFFF.
- Sound: Z80 song table at 9006 after a count word (0x38D, as written in PROGRESS.md); 26 music pieces named in `music.cpp`.
- Not yet found: weapon heat and Predator cannon variables; the endings were not reached.

**FBNeo cheat file (RAM fields; player stride 0x100)** — [finalburnneo/FBNeo-cheats cheats/avsp.ini](https://github.com/finalburnneo/FBNeo-cheats/blob/master/cheats/avsp.ini):
- Global: Infinite Time `FF8225=0x59`; Finish Scene `FF81F3=FF`; Select Region `FF81C9` (00 Japan, 02 USA, 04 Hispanic, 06 Asia, 08 Euro).
- P1:
  - lives `FF8471=09`; health `FF83C1=0x65`
  - special `FF840B=00, FF840C=40`; super `FF842F=E4`
  - invincibility `FF83CC=01, FF83F0=10, FF841F=00, FF8429=00`
  - rapid-fire weapon `FF846E=00`; character select `FF8452` (0–3)
  - transparency `FF8381=00`; stealth `FF83AE=00`; speed-up `FF838B=00`
  - always Ultimate Shot `FF842E=02, FF842F=3F`; Linn quick Soukeiha `FF8437=4F`
- P2 and P3 are the same fields at +0x100 and +0x200.

**MAME hiscore plugin**
- `avsp/avspa/avspd/avsph/avspj/avspu: @:maincpu,program,ffeac0,31d,01,01` and `@:maincpu,program,ffedda,1,44,44` — [MAME plugins/hiscore/hiscore.dat](https://github.com/mamedev/mame/blob/master/plugins/hiscore/hiscore.dat)

**ROM hacks (HBMAME, licence header "GPL_2.0", © Robbbert)** — [Robbbert/hbmame src/hbmame/drivers/cps2mis.cpp](https://github.com/Robbbert/hbmame/blob/master/src/hbmame/drivers/cps2mis.cpp):
- `avsp01` "Alien vs. Predator (940520U, 1 Vs 3 Plus, 2017-12-30)" — cps2 (encrypted), avspu key; alt names avspu3p, avspp. Changes p1/p2.
- `avsp02` "(940520U, Enhanced Edition, 2018-02-26)" — cps2; alt names avspu3p, avspu3pp. Changes p1, p2 and p3 (p3 is the 0x100000 data ROM).
- `avsp03` "(940520E, Ultimate Evolution Edition, 2020-05-08)" — dead_cps2 (decrypted); alt name avspdp.
- `avsp04` "(940520E, Ultimate Evolution Edition, 2020-09-01)" — dead_cps2.
- `avsp05` "(940520H, Modified Edition, 2020-08-30)" — cps2, avsph key.
- `avsp06` "Razoola, (940520U, Phoenix edition)" — dead_cps2.
- All hacks are credited only as "hack"; the authors are not named in HBMAME.

**TAS / speedrun**
- No TASVideos submission or publication for arcade AvP was found in searches. The only MAME-rr TAS in the results was for an unrelated game — [TASVideos 5478S (unrelated example)](https://tasvideos.org/5478S)
- speedrun.com has an "avparcade" leaderboard with Any% categories per character (Predator Warrior, Predator Hunter, Linn Kurosawa, Dutch Schaefer); seen via search summary — [speedrun.com/avparcade](https://www.speedrun.com/ru-RU/avparcade)

### Inferences
- The RAM sources agree with each other. FF8380 player base / +0x100 stride appears in cps2recomp, mame-rr and FBNeo. Health at +0x41 (FF83C1), lives at +0xF1 (FF8471), character at +0xD2 (FF8452) and the clock at FF8225 match across cps2recomp and FBNeo. The 24 × 0xC0 enemy pool at FF9280 matches cps2recomp and mame-rr. This gives a cross-validated RAM baseline.
- FBNeo's region byte FF81C9 (= A5+0x1C9) lines up with cps2recomp's finding that the region is written by `move.w #region,d16(a5)` at 000CAC.
- HBMAME hack sets avsp03/avsp04/avsp06 run on `dead_cps2`, which means they ship fully decrypted program ROMs. avsp02 also modifies the 0x100000–0x17FFFF ROM, so hackers have edited game data as well as code.

### Gaps
- Could not get Pugsy's MAME `cheat.xml` for avsp (mamecheat.co.uk was not attempted because of network policy; the cheat 7z is not on GitHub). FBNeo cheats were used instead.
- No hitbox data dump or frame data for AvP enemies beyond the Lua script logic.
- No author or forum provenance for the HBMAME hacks (they are probably Chinese-community hacks, given the naming style, but this is unverified).
- No RAM watch (.wch) files or TAS input files for AvP were found.

## 3. Fan remakes, OpenBOR mods, PC ports, official re-releases

### Takeaway
The only official home release is the **Capcom Home Arcade** plug-and-play (2019, FB Alpha-based emulation). AvP was excluded from the Capcom Beat 'Em Up Bundle and both Capcom Arcade Stadium collections, almost certainly for licensing reasons. Fan-side work: the recomp PC ports (section 1), an OpenBOR fan game ("AVP: Battlegrounds"), and some OpenBOR forum interest.

### Cited Findings
- Capcom Home Arcade (Koch Media, 2019): 16 CPS1/CPS2 games including Alien vs. Predator, with "emulation provided by FB Alpha". The FB Alpha licensing was disputed by other FBA team members, who forked FB Neo — [Nintendo Life, 2019-04](https://www.nintendolife.com/news/2019/04/capcom_home_arcade_is_a_plug-and-play_arcade_stick_but_is_the_emulation_legit); [Gematsu](https://gematsu.com/2019/04/capcom-home-arcade-plug-and-play-device-announced); [Co-Optimus](https://www.co-optimus.com/article/16029/enjoy-classic-capcom-arcade-games-in-your-home.html) (via search summaries)
- Hardcore Gaming 101 (via search summary): the Beat 'Em Up Bundle omitted AvP "presumably due to licensing issues"; Capcom "did manage to license and include Alien vs. Predator in their Capcom Home Arcade". Retronauts called the Home Arcade "the only way to play Alien vs. Predator legally" — [HG101](https://www.hardcoregaming101.net/alien-vs-predator-capcom/); [Retronauts](https://retronauts.com/article/1175/capcom-home-arcade-brings-a-big-capcom-logo-to-your-place-of-residence-or-domicile). Note: the HG101 summary calls the bundle "2017"; the bundle itself shipped in 2018 (not verified here).
- Capcom Arcade Stadium and Capcom Arcade 2nd Stadium did not include AvP (nor The Punisher, Cadillacs and Dinosaurs or the D&D games) — [Nintendo Life 2nd Stadium leak, 2022-06](https://www.nintendolife.com/news/2022/06/oops-it-looks-like-capcom-arcade-2nd-stadiums-line-up-has-leaked); [Limited Run Games blog](https://limitedrungames.com/blogs/news/in-this-beat-em-up-renaissance-why-was-aliens-vs-predator-left-for-dead) (via search summaries)
- "AVP: Battlegrounds" is an OpenBOR side-scroller on GameJolt, positioned as a spiritual successor to Capcom's arcade game, with characters from other Alien/Predator media — [GameJolt](https://ssr.gamejolt.net/games/avp-battlegrounds/1076588). ChronoCrash has an "AvP OpenBOR Projects?" thread mentioning an "Alien vs predator aftermath" demo — [ChronoCrash](https://chronocrash.com/forum/threads/avp-openbor-projects.7822/) (both via search summaries; status and dates unverified)
- Time Extension (March 2026): "I still dream of this becoming a reality: this Alien vs Predator concept could have resurrected Capcom's coin-op classic" (image credited to David Liu). Only the headline is known — [Time Extension](https://www.timeextension.com/news/2026/03/i-still-dream-of-this-becoming-a-reality-this-alien-vs-predator-concept-could-have-resurrected-capcoms-coin-op-classic)
- Rely on Horror: "(UPDATE) Capcom Appears to be Teasing an Alien vs Predator Re-Release" (date and content not verified) — [Rely on Horror](https://relyonhorror.com/latest-news/capcom-appears-to-be-teasing-an-alien-vs-predator-re-release)
- Native PC ports: the cps2recomp AvP port (beta, 2026) and the omegakatana92 standalone recomp (2026-10-17) — see section 1.

### Inferences
- The IP is co-owned or licensed through Fox, now 20th Century Studios/Disney, which explains why AvP is absent from Capcom collections. Any PC port is unofficial, and a bring-your-own-ROM model like cps2recomp's is the established community approach.

### Gaps
- No primary source (Capcom/Disney statement) on the licensing terms.
- AVP: Battlegrounds release status and engine details are unverified.

## 4. Hardware specifics from MAME (cps2.cpp, cps1.h, cps2crypt.cpp)

### Takeaway
AvP is a standard 3-player, 3-button CPS-2 game with no game-specific protection or quirks beyond CPS-2 opcode encryption:
- 68000 @ 16 MHz and Z80 @ 8 MHz (QSound)
- 2 MiB program ROM, 12 MiB of graphics ROM, 128 KiB Z80 program, 4 MiB QSound samples
- a 20-byte per-region key, and a 93C46 EEPROM
- all regional sets dated 940520

### Cited Findings
All from [MAME src/mame/capcom/cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp) (master as of 2026-11-09) unless noted.

**Sets (GAME lines)**
- All sets: year 1994, machine `cps2`, inputs `cps2_3p3b`, init `init_cps2`, ROT0, MACHINE_SUPPORTS_SAVE, with no imperfect or not-working flags.
  - `avsp` "Alien vs. Predator (Europe 940520)" (parent)
  - `avspu` (USA 940520), `avspj` (Japan 940520), `avspa` (Asia 940520), `avsph` (Hispanic 940520)
  - `avspd` "Alien vs. Predator (Europe 940520 Phoenix Edition) (bootleg)" uses machine `dead_cps2`

**Main CPU program** (region CODE_SIZE = 0x400000; ROM_LOAD16_WORD_SWAP)

| Offset | Size | Europe file (CRC) | Notes |
|---|---|---|---|
| 0x000000 | 0x80000 | `avpe.03d` (774334a9) | region-specific |
| 0x080000 | 0x80000 | `avpe.04d` (7fa83769) | region-specific |
| 0x100000 | 0x80000 | `avp.05d` (fbfb5d7a) | shared by all regions |
| 0x180000 | 0x80000 | `avp.06` (190b817f) | shared by all regions |

Total program: 2 MiB. Region-specific 03d/04d CRCs:
- USA `avpu.03d` 42757950 / `avpu.04d` 5abcdee6
- Japan `avpj` 49799119 / 8cd2bba8
- Asia `avpa` 6c1c1858 / 94f50b0c
- Hispanic `avph` 3e440447 / af6fc82f

**Graphics** (region 0x1000000; ROM_LOAD64_WORD, 4-way interleave)
- `avp.13m/15m/17m/19m`: 0x200000 each (LH53706A–D), at 0x000000–0x7FFFFF
- `avp.14m/16m/18m/20m`: 0x100000 each (LH53855G–K), at 0x800000–0xBFFFFF
- That is 12 MiB of tiles. CRCs: 8f8b5ae4, b00280df, 94403195, e1981245; 39933b1e, 85412860, 2e2beb06, e4798d1a.

**Sound**
- Z80 program `avp.01` (2d3b4220): 0x8000 loaded at 0x0000, then ROM_CONTINUE 0x18000 at 0x10000 (128 KiB total). QSOUND_SIZE region is 0x50000; banks are configured as 0x4000-byte entries from 0x10000.
- QSound samples: `avp.11m` (83499817) + `avp.12m` (f4110d49), 0x200000 each = 4 MiB, ROM_LOAD16_WORD_SWAP.

**Keys** (0x14 = 20 bytes each)
- `avsp.key` e69fa35b, `avspu.key` 4e68e346, `avspj.key` 3d5ccc08, `avspa.key` 728efc00, `avsph.key` cae7b680
- `avspd` uses `phoenix.key` 2cf772b0

**Clocks and machine**
- `M68000(config, m_maincpu, 16_MHz_XTAL)`; `Z80(config, m_audiocpu, 8_MHz_XTAL)`; the Z80 periodic IRQ is `8_MHz_XTAL / 32000` ("measured 250Hz")
- `EEPROM_93C46_16BIT`; stereo QSound; palette 0xC00 entries
- `m_maincpu->set_addrmap(AS_OPCODES, &cps2_state::decrypted_opcodes_map)`: decrypted opcodes form a separate address space over 0x000000–0x3FFFFF

**Video timing** — [MAME cps1.h](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps1.h)
- `CPS_PIXEL_CLOCK = XTAL(16'000'000)/2`
- HTOTAL 512, HBEND 64, HBSTART 448 (384 px visible)
- VTOTAL 262, VBEND 16, VBSTART 240 (224 lines visible)

**68000 memory map** (`cps2_base_map` / `cps2_map`)

| Address | Use |
|---|---|
| 0x000000–0x3FFFFF | ROM |
| 0x400000–0x40000B | CPS2 object output |
| 0x618000–0x619FFF | QSound shared RAM |
| 0x660000–0x663FFF | optional extra RAM ("Many games store highscores") |
| 0x700000 / 0x708000 | object RAM, bank switched at 0x8040E0 |
| 0x804000 / 0x804010 / 0x804020 | IN0 / IN1 / IN2 + EEPROM |
| 0x804030 | volume / add-on detect |
| 0x804040 | EEPROM write |
| 0x8040B0 | DIP switches ("only present on development hardware") |
| 0x804100 | CPS-A |
| 0x804140 | CPS-B |
| 0x900000–0x92FFFF | video RAM |
| 0xFF0000–0xFFFFFF | work RAM |

On a dead board (`dead_cps2_map`), work RAM is 0xFF0000–0xFFFFEF and the object output moves to 0xFFFFF0–0xFFFFFB.

**Inputs**
- `cps2_3p3b` = `cps2_3p4b` with button 4 removed for P1, P2 and P3, i.e. 3 players × 3 buttons. cps2recomp names the buttons Attack, Jump and Shoot, and places players 3/4 at 804010 — [cps2recomp avsp PROGRESS.md](https://github.com/tmcleroy/cps2recomp/blob/HEAD/games/avsp/PROGRESS.md)
- The factory player mode is 2 players; 3 players is an operator setting (player mode A5+1CE) — [cps2recomp avsp.h](https://github.com/tmcleroy/cps2recomp/blob/HEAD/games/avsp/src/avsp.h)

**Encryption** — [MAME cps2crypt.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2crypt.cpp)
- "The encryption only affects opcodes, not data. It consists of two 4-round Feistel networks (FN) and involves both the 16-bit opcode and the low 16 bits of the address", with a 64-bit key: `D = FN2( E, K XOR EX( FN1(A, K ) ) )`.
- Credits: Andreas Naive (algorithm), Nicola Salmoria (code), Charles MacDonald and Razoola (hardware extraction).
- The encrypted address range is derived from the key: `upper = (((~decoded[9] & 0x3ff) << 14) | 0x3fff) + 1` (cps2.cpp).

**Sound program** — header notes in [cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp):
- "in all CPS2 games, Capcom chose not to use the Kabuki encryption since none of the CPS2 games have an encrypted sound program"
- The AvP Z80 driver is "Capcom's QSound driver of November 1993" — [cps2recomp PROGRESS.md](https://github.com/tmcleroy/cps2recomp/blob/HEAD/games/avsp/PROGRESS.md)

**Dump history**
- MAME commit 163659b50a (2021-10-26): "cps2.cpp: corrected some overdumps for avsp [Guru]" — [MAME commit](https://github.com/mamedev/mame/commit/163659b50a)
- HBMAME still loads the old 0x200000 dumps for slots c5–c8 (CRCs ebba093e, fb228297, 34fb7232, f90baa21) — [HBMAME cps2.cpp](https://github.com/Robbbert/hbmame/blob/master/src/hbmame/drivers/cps2.cpp)
- cps2recomp rejects those older dumps — [cps2recomp avsp README](https://github.com/tmcleroy/cps2recomp/blob/HEAD/games/avsp/README.md)

**Driver notes**
- There is no avsp-specific comment block, DIP or protection handling in cps2.cpp.
- The CPS2 header notes that the board's decryption key is held in battery-backed SRAM ("suicide" battery) — [cps2.cpp header](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)

### Inferences
- Computed refresh rate: 8 MHz / (512 × 262) ≈ 59.64 Hz, with a 384×224 active picture.
- Only 03d/04d differ between regions (1 MiB). cps2recomp says the code is identical apart from region and checksum words, so one disassembly can cover all five regional sets with small patches.
- The 0x100000–0x1FFFFF ROMs (05d/06) are shared and appear to hold mainly data: animation lists at 15E240+ and pictures in 100000–1FFFFF per cps2recomp. The last code address cited by cps2recomp is around 0B3C6A.

### Gaps
- The key bytes, and therefore the exact encrypted range for avsp, were not examined. No key or ROM files were downloaded, by design.
- The B-board/model number (arcade-history lists "Model J9008E" for one entry) and the exact regional release dates (as opposed to the 940520 ROM date) could not be verified, because Wikipedia and arcade-history were blocked.

## 5. Home console ports and disambiguation

### Takeaway
The CPS-2 game was never ported to a home console. A Sega 32X version was planned or announced for 1995 but never released. The only home release is the 2019 Capcom Home Arcade (emulated). The SNES (1993) and Atari Jaguar (1994) "Alien vs Predator" titles are different games. MAME's Jaguar software list even reuses the short name `avsp` for the Jaguar game.

### Cited Findings
- Wikipedia (via mirrors and search summary): "was never ported to any home systems"; a 32X version "was announced for 1995 but it was never released"; it was included on the Capcom Home Arcade in 2019 — [Wikipedia](https://en.wikipedia.org/wiki/Alien_vs._Predator_(arcade_game)); [Sega-16 "Lost in the Arcade"](https://www.sega-16.com/2005/12/lost-in-the-arcade-capcom-games/) (via search summaries)
- A Capcom 32X list says this game, like Capcom's other 32X titles, was cancelled — [rq87 32X list](https://rq87.flyingomelette.com/RQ/32X/u.html) (via search summary). The CES 1994 announcement detail is unverified.
- One article claimed ports to Saturn and PlayStation. The search summary flagged this as contradicted by every other source — [SVG](https://www.svg.com/2287040/arcade-games-1994-hold-up-today/?zsource=aol) (unreliable)
- The Jaguar AvP is a different game. MAME's `hash/jaguar.xml` has `<software name="avsp" supported="no"> <description>Alien vs Predator</description> <year>1994</year> <publisher>Atari</publisher>` — [MAME jaguar.xml](https://github.com/mamedev/mame/blob/master/hash/jaguar.xml). A 2026-01-02 MAME commit, "atari/jaguar_v.cpp: blitter readback fix for avsp", refers to that Jaguar title, not the CPS-2 game — [GitHub commit search](https://github.com/search?q=avsp+repo%3Amamedev%2Fmame&type=commits)
- TCRF has separate pages for the SNES and Jaguar versions — [TCRF SNES](https://new.tcrf.net/Alien_vs._Predator_(SNES)); [TCRF Jaguar](https://new.tcrf.net/Alien_vs._Predator_(Jaguar))

### Inferences
- When searching MAME issues or commits for "avsp", results must be filtered by driver (capcom/cps2 vs atari/jaguar) to avoid confusion.

### Gaps
- No primary 1994–95 magazine source for the 32X announcement was retrieved.

## 6. Decrypted sets (avspd / Phoenix) and what they imply for disassembly

### Takeaway
`avspd` (Razoola-style "Phoenix Edition", Europe 940520) supplies fully decrypted program ROMs that run on a "dead" CPS-2 memory map. It, and the HBMAME decrypted hacks, show that a plain-binary 68000 image of AvP is easy to get. Encryption is a solved, non-issue for a disassembly: MAME, and cps2recomp at load time, decrypt with the per-set key.

### Cited Findings
- `avspd` program ROMs: `avped.03d` (66aa8aad), `avped.04d` (579306c2), `avp.05d` (fbfb5d7a, **identical** to the encrypted sets), `avpd.06` (63094539, **differs** from `avp.06` 190b817f). It also has a zero-filled `user1` region of 0x100000, `phoenix.key`, and machine `dead_cps2` — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- MAME's note: "The Phoenix sets were created by Razoola as a method of allowing the games to run on CPS2 boards where the battery had died. When this happens the boards run non-encrypted code, but the memory mapping is changed. As the original games have encrypted code mixed with decrypted data the program roms must be carefully modified in order to correctly contain only decrypted code and data, as well as modification to compensate for the memory map changes ... there were sometimes errors introduced into the 'Phoenix' sets." It adds that these sets became the basis of bootleg conversions and "All sets are marked as bootleg" — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- On a dead board "the only encrypted range is actually FF0000-FFFFFF" (key decoded[9] == 0xffff) — [MAME cps2.cpp](https://github.com/mamedev/mame/blob/master/src/mame/capcom/cps2.cpp)
- HBMAME adds `avsp06` (Razoola, "940520U, Phoenix edition", dead_cps2) and the decrypted-base hacks `avsp03`/`avsp04` — [HBMAME cps2mis.cpp](https://github.com/Robbbert/hbmame/blob/master/src/hbmame/drivers/cps2mis.cpp)
- cps2recomp needs the original set plus key and deciphers "on the fly, as the board does". Its CHANGELOG says clone sets were "compared with the game's own, deciphered, word by word" — [omegakatana92 README](https://github.com/omegakatana92/Alien-vs-Predator-arcade-Recomp-/blob/HEAD/README.md); [cps2recomp CHANGELOG](https://github.com/tmcleroy/cps2recomp/blob/HEAD/CHANGELOG.md)

### Inferences
- `avp.05d` being byte-identical between the encrypted and Phoenix sets strongly suggests that 0x100000–0x17FFFF contains no executed code (data only). This fits cps2recomp's finding that animation and picture data sit in 100000–1FFFFF. `avpd.06` differs, probably because of Phoenix patch code or memory-map fix-ups placed there (unverified).
- For a disassembly, building from the original encrypted set plus key (as MAME's cps2crypt or cps2recomp do) is cleaner than building from avspd. The Phoenix sets contain Razoola's modifications for the dead-board map (the object output moves to FFFFF0, and some patches) and, per MAME, sometimes errors. Phoenix ROMs are still useful as a quick cross-check of decrypted opcodes.
- Because the 68000 encryption covers opcodes only, data tables (animations, hitbox tables via +0x50 pointers, the attract table at 004706, the round table at 00CCA0, the camera tables at 0B0550 and 0AF8D4) can be read directly from the encrypted ROM without decryption. Only instruction words need the cipher.

### Gaps
- The exact contents of Razoola's patches in `avpd.06` were not examined (no ROMs downloaded).
- Not verified whether an "avspud"/"avspjd"-style decrypted set exists for other regions in MAME; only `avspd` (Europe) is in current MAME, plus HBMAME's `avsp06` (USA).
