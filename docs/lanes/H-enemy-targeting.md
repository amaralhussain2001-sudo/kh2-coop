# Lane H: enemies and bosses choose between BOTH heroes

Written 2026-11-10. Game program CRC F266B00B (Kingdom Hearts II Final Mix, SLPM-66675). Base: merged build v2
(`patches\merged-v2`, SHA-1 9168afbc...). All tests SINGLE-PC, two linked emulator copies in `local\run-h`
(port 29350, PINE 28111), scripted or random buttons, no humans. Every run below ended "never out of sync".
Labels: VERIFIED (test id / address / how) or HYPOTHESIS. Test folders: `local\tests\h-*`.

## Result

**WORKS for the way enemies and bosses pick whom to attack** (the engine's "target search"). With the delivered
patch an enemy or boss that would have gone for "the player" now chooses between player 1's hero and the twin.
One player object alone plays exactly as the merged base. Other code that goes straight to "the player" (30 sites
in the world / boss / minigame modules, the helpers' following) is NOT changed: see "What else reads the same
source".

**Delivered patch:** `patches\lane-h-target-v1\SLPM-66675_F266B00B.pnach` (692 lines: the 563 words of
`patches\merged-v2` unchanged + 122 routine words + 3 hook words), SHA-1 33875fff65b2449ef6df9da05f07e64b2997ca33,
with `listing.txt`. Generator: `python -I tools\lane-h\make_h.py patches\lane-h-target-v1`.

### The rule (uses only game state, so two PCs stay identical)

When a target search ends on "the player" and a twin exists, the searching enemy looks at its distance to each hero:

1. **A hero at 0 HP is never chosen** (the other one is).
2. **One hero clearly closer** (the other is more than 1.5 times as far): the nearer hero.
3. **Both about as close** (neither more than 1.25 times as far as the other): the two heroes **share the enemy in
   turns**. Each enemy's turn changes every 512 video frames (about 8.5 s), and every enemy has its own phase
   (taken from its object address), so at any moment about half of the enemies prefer each hero.
4. **In between** (1.25 to 1.5 times): the enemy keeps the hero it already targets, otherwise the nearer one.

Why this rule: locality feels like the original for each player (enemies beside you fight you, wherever the other
player is); turns keep it fair when both stand together, including a single boss, which would otherwise stay on one
hero for the whole fight; the middle band stops flip-flopping at the edge. A first version ("nearer hero, switch only
when the other is 1.5 times closer", test names `h-t1-*`) left a lone boss on one hero and sent whole enemy waves to
the hero standing slightly nearer their spawn spots; that is why turns were added.
The three numbers are generator options (`--khi`, `--klo`, `--epoch`); they are a first tuning, not played by humans.

### Tests with the delivered patch (`patches\lane-h-target-v1`; `h-t2-*` = the same bytes under an earlier name)

"hits" = number of times a hero's HP dropped. "on hero / on twin" = how many enemies had that hero as their target,
averaged over the window. All pads idle unless said. One video frame = 1/60 s.

| Test | Scene | Merged base (v2) | With lane H |
|---|---|---|---|
| h-base-farhero / h-v1-farhero | Port Royal fight (6 enemies), **player 1's hero 2,470 units away, twin among the enemies**, 41 s | all 6 enemies on the hero; nobody is hit at all | **all 6 on the twin; twin HP 20 -> 0 (12 hits), hero 20 -> 20 (0 hits)**. VERIFIED |
| h-v1-fartwin | same fight, **twin 2,560 units away, hero among the enemies** | (not run; the base always goes for the hero) | **all 6 on the hero; hero 20 -> 2 (10 hits), twin 20 -> 20 (0 hits)**. VERIFIED |
| h-base-near-idle / h-t2-near-idle | same fight, heroes start 110 units apart, 41 s | 6 on hero, 0 on twin; hero 11 hits (20 -> 1), twin 1 stray hit | 4.0 / 2.0, then 3.0 / 3.0; **hero 8 hits (20 -> 4), twin 9 hits (20 -> 3)**; 5 target changes by 5 enemies. VERIFIED |
| h-v1-fight-rand | same fight, **random buttons on both pads**, 43 s | (lane M: in sync) | 2.8 / 2.6, 3.0 / 2.0, 2.0 / 2.0, 1.0 / 2.0 per quarter; hero 6 hits, twin 3; enemy HP 60 -> 21; 114 digests. VERIFIED |
| h-v1-away | same fight, player 2 runs about 1,500 units away from frame 5000 | - | at the start 5.3 / 0.7; once player 2 is 1,500 away the two enemies that had the twin change to the hero (2 target changes) and it stays 6 / 0; hero 11 hits (20 -> 1), twin 0. VERIFIED (the script's walk back did not bring player 2 back: the heroes stayed 1,360-2,270 apart) |
| h-v1-attack | same fight, both players press attack every 20 frames | - | both heroes fight: enemy HP 60 -> 5, a new wave, 52 -> 29; targets 2.3 / 1.2, 3.0 / 1.0, 2.9 / 1.5, 2.3 / 1.4 per quarter; hero 3 hits, twin 3 hits; 4 target changes. VERIFIED |
| h-base-dg / h-v1-dg | same fight **with Donald and Goofy** (Party DEFAULT), heroes together | every enemy on the hero, none on the twin; hero 4 hits, twin 0 | first two quarters 2.4 / 1.1 and 2.8 / 1.1, later waves mostly on the hero (5.4 / 0.0, 3.9 / 0.2: they appear on the hero's side while the heroes stand 400-600 apart); hero 4 hits, twin 2; Donald and Goofy fight and enemies die as in the base; 6 target changes. VERIFIED: the room still behaves |
| h-v1-dg-farhero | with Donald and Goofy, hero 2,470 units away, twin among the enemies | - | all 6 on the twin; **twin 20 -> 0 (12 hits), hero 0 hits**. Donald and Goofy do NOT help the twin: they stay about 800 units from both heroes and the enemies' HP stays 60 -> 60 (helpers follow player 1, see below). VERIFIED |
| h-v1-dg-attack-long | with Donald and Goofy, both players attack | - | the fight is WON at frame 6806 (35 s); the session stays in sync through the mission end to frame 8400 (131 digests). VERIFIED |
| h-base-alboss-idle / h-v1-alboss-idle / h-v1-alboss-long | **Boss fight: Volcanic Lord + Blizzard Lord** (Agrabah, al03 program 0x3B, objects 0x040B / 0x040C, type BOSS), Goofy and Aladdin present | both bosses on the hero for all 47 s; hero 12 hits, twin 2 | 47 s: 1.5 / 0.5, 0.1 / 1.9, 1.1 / 0.9, 1.4 / 0.6 per quarter; hero 9 hits, twin 4. **72 s: hero 9 hits, twin 7; 11 target changes by the 2 bosses** (142 digests). VERIFIED |
| h-base-axel-idle / h-v1-axel-idle | **Boss fight: one boss, Axel** (Twilight Town, tt20 program 0x89, object 0x0051, type BOSS), two Roxas | Axel on the hero for the whole fight; hero 14 hits and defeated after 37 s, twin 0 hits | Axel on the hero, then on the twin for two quarters, then the hero again: **hero 13 hits, twin 7 hits**, 2 target changes in 47 s. VERIFIED |
| h-base-solo-rand / h-v1-solo-rand | **one player object alone** (disc without twin), random buttons, 7,000 frames | reference | **the same**: 6 of 6 screenshots byte-identical (frames 5000, 6000, 6800 on both copies) and every recorded value identical for 1,125 frames (HP, positions, enemy HP and targets). VERIFIED |
| h-v1-sync-roam | free roam, Merlin's house -> Borough, **random buttons on both pads, 34,000 frames** | (lane M: in sync) | **never out of sync, 531 digests, 8 of 8 screenshot pairs identical**; at 7 checkpoints all patch words of this lane intact. VERIFIED |
| h-cave-nopatch | UNPATCHED game (disc without twin): boot, title, New Game, three room changes, a fight; 8 checkpoints | **0 non-zero words in 0x000F2000-0x000F27FF at every checkpoint**. VERIFIED (lane M's wide check of 0x00080000-0x000FFFFF says the same) | - |
| h-v1-flags | fight, one look at frame 5000 | - | both heroes carry the "is the player" flag the scripts test (object+0x588 bit 0x80; value 0x01000087 on both); the six enemies are type ZAKO and their target records hold search mode 0. VERIFIED |

Not reached: "both near for a full minute" with the small enemies. The heroes (20 HP) fall or win in about 40 s;
the 72-second sample is the two-boss fight.

## What was found: how an enemy gets its target (all for CRC F266B00B)

| Thing | Address | Status |
|---|---|---|
| AI scripts call the engine through "trap" tables: records of (function, argument word). List of tables | 0x0034DBF8: table 0 = 0x0034D8B0, 1 = 0x0034DD00, 2 = 0x0034EF30, 4 = 0x003504E0, 5 = 0x00362F48, 6 = 0x00363060, ... | VERIFIED (`tools\lane-h\traptables.py`; the argument counts match OpenKH's script decoder for every entry checked) |
| Script call "search a target" (table 1, number 121; 3 in) | 0x001745A0 -> `Search(record, mode, object)` 0x00190920 | VERIFIED (disassembly) |
| The search's seven modes (jump table 0x0036CD28) | 0: 0x00190A28, 1: 0x00190A80, 2: inline at 0x001909A0, 3 and 5: 0x00191218, 4: 0x00190B30, 6: 0x00190F80 | VERIFIED |
| **Mode 0** | a decoy from the "before the player" list if there is one, else **the engine's player** (0x0034E948) | VERIFIED |
| **Mode 1** | decoy list; else the object remembered at object+0xAEC if the searcher's own target-type byte is not 1, that object is valid and its flag 0x4 at +0x7F8 is clear; else **the engine's player** | VERIFIED (code); what +0xAEC holds is a HYPOTHESIS (who last hurt it) |
| **Mode 2** | **the engine's player**, nothing else | VERIFIED |
| Modes 3-6 | nearest-object searches used by friends and by the player's own lock-on (0x0019CE48) | VERIFIED (callers); not touched |
| Every battle object **stores its target**: record at object+0x9F4 (object, part, a pointer, mode) | read by script call table 2 number 23 (0x0018F140); set by 0x00190878 | VERIFIED; the recorder reads it |
| Default at creation: `Search(object+0x9F4, mode 2, object)` | 0x001D7E00, 24 callers | VERIFIED |
| "Before the player" decoy list: 8 entries (priority, object) | 0x01C60D10; chosen by 0x001CD7A8 (lowest priority number, ties by the game's random number 0x003638D0); filled by script call table 1 number 162 (0x00174668 -> 0x00191398) | VERIFIED (code); who uses it in play: not looked at |
| Script call "get the player" (table 1, number 3) | 0x00171068 -> 0x0016B0D0 = the engine's player | VERIFIED |
| Script call "my last attacker" (table 2, number 88) | 0x0018F428: object+0xAE4 if valid, else the engine's player | VERIFIED |
| Script call "is this the player" (table 1, number 309) | 0x00171090: flag bit 0x80 at object+0x588, not a pointer comparison | VERIFIED; both heroes have the bit (h-v1-flags) |
| Script call "party member N" (table 1, number 93) | 0x00173E88 -> 0x00176B20: N = 0 the engine's player, N >= 1 the friends | VERIFIED; the twin is not in this list |
| The object whose AI script runs | 0x0016A950 runs the script context at object+0x484 through 0x0016CD48, which sets 0x0034D8A0 / 0x0034D8A4 while it runs | VERIFIED |
| The engine's player pointer 0x0034E948 is loaded at 116 code sites | 30 of them in the world / boss / minigame modules (0x002B-0x002E), 24 in battle-object / target / trigger code, 39 in unit / friend / command / menu code | VERIFIED (`elfscan.py`) |
| The other pointer lane D wrote, 0x00352400 | has ONE reader (0x001D14A8, the placeholder's form lookup). Enemy targeting depends on 0x0034E948 only | VERIFIED |

**Survey of all 967 AI scripts** (decoded with the user's OpenKH tools, `tools\lane-h\ai_survey.py`,
`local\analysis\h\ai_survey.csv`): 154 of 155 ZAKO, 21 of 21 L_ZAKO, 93 of 95 BOSS and 12 of 13 L_BOSS scripts hold the
target search; the modes written in the scripts are 0, 1 and 2 (455, 477 and 552 scripts; mode 3 in 22). So small
enemies, large enemies and **bosses use the same three modes**; a boss differs only by having more direct calls of
"get the player" (most: B_EX180 12, B_AL020 10, B_NM110 10) and by native code in the boss modules.
How often they search (test builds with counters, `h-dbg-*`): about one search per enemy every 3.7 s for the small
enemies, 0.7 per second per boss for the two lords, once in 10-15 s for Axel.

## The patch

Hook sites (none is used by merged build v2; the generator checks the original instruction of each and stops on any
address used twice):

| Address | Was | Now | Meaning |
|---|---|---|---|
| 0x00190A74 | `j 0x00190878` | `j 0x000F2000` | end of search mode 0 |
| 0x00190B28 | `j 0x00190878` | `j 0x000F2000` | end of search mode 1 |
| 0x001909A8 | `jal 0x00190878` | `jal 0x000F2000` | search mode 2 |

All three reach one routine with the target record in a0, the object the search ended on in a1 and the searching
object in s0 (the dispatcher's saved register; the two mode handlers are called only from the dispatcher).
- `h_tail` (0x000F2000): if a1 is not the engine's player (a decoy or the remembered object), or there is no twin
  (lane E's pointer 0x000F05CC is 0), it jumps on to the game's routine unchanged. Otherwise it calls `h_choose` and
  puts the chosen hero into a1.
- `h_choose` (0x000F2068): the rule above. It reads each hero's HP through its unit slot (object+0x48C), the three
  positions through the game's own routine 0x0016C028, the previous target from the record, and the game's frame
  counter 0x0034D4BC for the turns.
- Routines: 0x000F2000-0x000F21E7 (122 words) of the assigned cave 0x000F2000-0x000F27FF. **No variables**: the
  delivered patch keeps no data of its own.
- Merged-v2 hooks touched: **none**. It reads lane E's twin pointer and the unit slots as lane D / the merge set them
  (hero = plain slot, twin = marked slot; found through each object, not by address).

Every word with its meaning: `patches\lane-h-target-v1\listing.txt`.

## What else reads the same source, and what changed for it

1. **Friends' target records.** Donald, Goofy and guests are battle objects too; at creation they also run
   "target = the player" (0x001D7E00), so for their first 39 frames their record can now hold the twin instead of
   the hero (seen: 39 frames on a hero in the base, 0 or 39 with the rule). No effect was seen. They then use the
   nearest-enemy modes, which are untouched.
2. **Helpers' following and healing: NOT changed.** They use native code that reads the engine's player. VERIFIED
   by position: in every test Donald, Goofy and Aladdin stay with player 1's hero (for example 285 and 424 units from
   the hero, 1,757 and 1,704 from the twin in the 72-second boss fight). See h-v1-dg-farhero for what that means
   when the twin fights alone. The user's rule "one helper each when the heroes split, come to a fallen hero" is
   still to do.
3. **Reaction Commands: NOT changed** by this lane (nothing here touches them). Not tested.
4. **Enemy shots and aimed attacks** follow the target record (script call "target position"), so they go to the
   chosen hero. VERIFIED only through the hits counted above, not shot by shot.
5. **Script call "get the player" and "my last attacker": NOT changed in the delivered patch.** A second part was
   written for them (`tools\lane-h\h_ptrap.py`, generator option `--player-trap`, test folder `patches\lane-h-t3`):
   the calling enemy would get the hero in its own target record. In four scenes (small enemies, with Donald and
   Goofy, the two lords, Axel) the counters of a test build showed that an enemy with a twin in the room **never
   made that call** (0 calls in 30-45 s each, `h-dbg-*`), so the part could not be seen working and is left out.
   Where a script does make the call (far-away / off-screen handling in the shared script library, some boss
   patterns) it still gets player 1's hero. HYPOTHESIS: this matters for specific bosses; to revisit with the
   parity checklist.
6. **Script call "party member N"** and **30 native sites in the boss / minigame modules** still mean player 1's
   hero only. A boss move written against "the player" directly (grabs, scripted moves, arena logic) will ignore
   the twin. Not examined boss by boss.
7. **Decoys** ("before the player" list): unchanged; a decoy still wins over both heroes.

## Still open

1. **Helpers stay with player 1** (point 2). With the hero far away the twin fights alone.
2. **A hero at 0 HP = Game Over** (lanes D / N). The rule already skips a hero at 0 HP, for when "down like
   Goofy" exists; that path could not be tested because the fight ends.
3. **Bosses with native "the player" code** (point 6) and the script calls of point 5.
4. **Tuning** (1.5 / 1.25 / 8.5 s) is a first guess, never played by humans.
5. **Waves that appear beside one hero** all pick that hero when the heroes stand a few hundred units apart
   (h-v1-dg, later quarters). That is the rule working as written ("clearly closer"), but a human may find it uneven.
6. Tested in three places only: the Port Royal fight, the Agrabah boss room, the Axel fight. Forms other than Sora
   and Roxas, Drive Forms, summons, mission types with a decoy: not tested.
7. The searching object can be any battle object whose search ends on "the player", not only enemies (friends at
   creation, point 1). No restriction by object type was added because no harm was seen.
8. Position 0x000F2000-0x000F21E7 relies on that memory being unused: shown for boot, title, a save, three room
   changes and a fight, not for every world.

## How to repeat

```
python -I tools\kh2_session.py make 2 --run-dir run-h
python -I tools\lane-h\make_h.py patches\lane-h-target-v1
python -I tools\lane-h\build_disc_h.py farhero --overlay local\variants\b-ca\b7\ard --rooms ca02,tt01 --move-hero "ca02:-539.7:-1204.1:1965.8:-149.2:-1748.7"
python -I tools\lane-h\build_disc_h.py fartwin --overlay local\variants\b-ca\b7\ard --rooms ca02,tt01 --move-twin "ca02:-539.7:-1204.1:1965.8:-149.2:-1748.7"
python -I tools\lane-h\build_disc_h.py dg      --jump "CA 55" --party DEFAULT --rooms ca02,tt01
python -I tools\lane-h\build_disc_h.py alboss  --jump "AL 59" --party - --rooms al03,tt01
python -I tools\lane-h\build_disc_h.py axel    --jump "TT 137" --party - --rooms tt20,tt01
python -I tools\lane-h\build_disc_h.py solo    --no-twin --overlay local\variants\b-ca\b7\ard
tools\lane-h\hrun.sh <test> <disc> <frames> <speed> 2 <p1 script> <p2 script> idle|random <patch folder> 4700 <end> <windows> <snaps>
tools\lane-h\batch.sh <out.txt> <patch folder> <prefix> <disc:test[:frames[:p1[:p2[:then]]]]> ...
tools\lane-h\hcaverun.sh ...      (memory check; with a patch folder it compares the words with the file)
```
Discs are built from `English text build3 (candidate).iso` with lane J's placement tool and override file, twin
record before the placeholder, as `local\iso\test-h-<name>.iso` (about 20 s each).

## Files of this lane

- `tools\lane-h\`: `make_h.py` (generator), `h_ptrap.py` (the part that is not delivered), `build_disc_h.py`,
  `hrec.py` (recorder: hits, targets, target changes, where party members stand), `hrun.sh`, `batch.sh`, `hcave.py`,
  `hcaverun.sh`, `peek_flags.py`, `ai_survey.py`, `traptables.py`, `find_traps.py`, `find_traps2.py`, `findword.py`,
  `short_refs.py`, and copies of `asm.py`, `mips.py`, `pine.py`, `elfscan.py`, `callers.py`, `findimm.py`, `mprobe.py`,
  `mrec.py`, `psum.py`, `gh.sh` + `ghidra\` (Ghidra project copy: `local\ghidra-h`).
- Patches: **`patches\lane-h-target-v1`** (delivered). Experiments, not for use: `patches\lane-h-t1` (first rule),
  `patches\lane-h-t2` (same bytes as the delivered file), `patches\lane-h-t3` (with the undelivered script-call part),
  `patches\lane-h-t3-debug` (test build with counters).
- Button scripts: `tests\scripts\lane-h\`. Analysis (decompiled text, script survey, batch results):
  `local\analysis\h\`.
- Discs: all seven `test-h-*.iso` are deleted; recipes and reports are in `local\variants\h-*`.
- Emulator copies `local\run-h` (2) are left in place. No emulator of this lane is running.
- Not edited: other lanes' folders and patches, the shared tools, `docs\STATE.md`, the plan, the requirement and
  checklist files, the memory folder.
