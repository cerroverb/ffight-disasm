The Board page's hook in `games/avsp/src/game.cpp` (run at 000D20 and 0B3C6A) overwrote the two variables the game works out from the player mode, with modes 0 and 2 the other way round. The game's own routine at 003C5E (003D3C-003D5A) sets them as follows.

| player mode (1CE) | 1C5 | 1C6 | meaning |
| --- | --- | --- | --- |
| 0 | 0 | 0 | three players, a chute each |
| 1 | 1 | 0 | three players, one chute |
| 2 (factory) | 1 | 1 | two players, one chute |

The hook set 1C5 = (mode != 2) and 1C6 = (mode == 0). With both at 0 the game keeps a credit count for each player (00160A) and takes the third player's coin and start. So in Pure, on a board as it left the factory, AvP played as a three-player, three-chute cabinet, and the Board page's "Three, a chute each" played as two players. "Three, one chute", which Enhanced uses, was already right.

This change computes them as 003D3C-003D5A does. It also renames `kThreePlayers`/`kThreeChutes` to `kOneChute`/`kTwoPlayers` to match what the game does with them, and updates PROGRESS.md and CHANGELOG.md.

**How it was found.** Work RAM (FF0000-FFFFFF) was compared with MAME 0.264 after every frame under the same input, from power-on with a blank settings memory, Pure, set `avsp`. FF81C5/FF81C6 were the first bytes apart (MAME 01 01, cps2recomp 00 00), with the settings record at FF0EF0 and 1CE identical. The comparison scripts are in https://github.com/cerroverb/ffight-disasm/tree/claude/serene-johnson-z6j22m/avsp-compare.

**Effect, measured the same way.** A coin on the third chute at frame 2400 and the third player's start at 2460, Pure, blank settings memory:

- MAME: no credit, still in the attract mode at frame 2700.
- cps2recomp d3bf22f: a credit on the third player's own count (FF819C = 01), and a game started (A5+00 = 0002).
- With this change: as MAME.

**Note.** With every feature off, the game no longer runs exactly as before. That is the point of the change: Pure now matches the board. Hashes of earlier AvP movies that use the third player's coin or start will differ.

- [x] Nothing from a game (files, save states, generated code, entry lists, listings, dumps, screenshots other than the README's), no keys or key values, nothing from Capcom's own materials or a leak, no emulator's code. `make audit` passes.
- [x] What is about one game is in that game's `games/<id>/` (its `game.cfg` or sources), not the toolkit.
- [x] If the translators, the machine, the picture, the sound or a game's code changed: `make GAME=<id> check` over the ladder movie and `make GAME=<id> check-rewrites` pass for every game (with every feature off a game runs as before). Only avsp changed. AvP has no ladder movie and no `check_rewrites.sh`, so `make GAME=avsp check FRAMES=20000` was run with its made-up input after `make GAME=avsp explore`: "translated code does what the interpreter does (20000 frames)" and "two runs alike". Before `explore`, the same check failed on both d3bf22f and this change, at frames 483 and 77.
- [ ] Gameplay and control changes are an optional feature, off in Pure. Not applicable: this is a fix that makes Pure match the board.
- [x] No added input lag or lost speed. Two byte writes in a hook that runs at power-on and when the test menu is left.
- [x] Keyboard and gamepad both still work. No input code changed.
- [x] `recomp-common/` is unchanged.
- [x] A line in `CHANGELOG.md` under "Unreleased".

Not run: `make check` stopped while downloading Dear ImGui for the launcher. The build machine's network refused the github.com archive. `make audit` (part of it) passed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_017uZUcLorPMd5nBmW5X4g75
