# Lane N - down and rescue (checklist row GW-10)

Game: KH2 Final Mix SLPM-66675, CRC F266B00B. Base: `patches\merged-v2` (lines unchanged).
Rule asked for (user's decision "A, exactly like Goofy"): a hero at 0 HP goes DOWN and stays in the room; the other
player can bring him back with a Potion or Cure; if nobody does, he gets up by himself; GAME OVER only when both
heroes are down at the same time; Donald and Goofy unchanged.

Words used here: "hero" = player 1's hero (the engine's player object, pointer 0x0034E948); "twin" = player 2's
hero (lane E's pointer 0x000F05CC). Frames are session frames (game counter 0x0034D4BC + 152).
Every claim is marked VERIFIED (test id) or HYPOTHESIS. Test results are in `local\tests\<test id>\`.

## 0. Result in one table

| Step | State | Short |
|---|---|---|
| 1 learn friend fall / Sora's defeat | done, except the King Mickey path (not located) | section 1 |
| 2 fallen-hero behaviour | done | section 2 |
| 3 healing across heroes | Potion done (automatic target), Cure done, HP orbs NOT (twin cannot pick up orbs: static finding, not this lane's change), no on-screen target choice | section 3 |
| 4 Game Over only when both are down, Continue | done (order hero first, twin second; other order not run) | section 4 |
| 5 camera / HUD / missions | described; one mission rule found; Mickey, Drive Forms, room change while down NOT tested | section 5 |

**Mergeable patch: `patches\lane-n-down-v2\SLPM-66675_F266B00B.pnach`** (+ `listing.txt`), SHA-1
db665f7f203191ecfb156edd5a5ef92db5a10c92, 566 merged-v2 lines unchanged + 378 lane N lines. Made by
`python -I tools\lane-n\make_down.py patches\lane-n-down-v2`. The older `patches\lane-n-down-v1` (instant revive,
wrong) was deleted.

## 1. What the game does (step 1)

### Fallen Donald / Goofy
| Fact | Where | Evidence |
|---|---|---|
| Friend class table 0x00345C08; fallen flag = object+0x7F8 bit value 4; lying motion 0x36 (object+0x154), get-up motion 0x37 | - | VERIFIED n-base-hbf2, n-v5-hb-friend-base |
| Timer = object+0xB40 (float, 1/60 s). Start value = parameter block (object+0x12C) +0x18 x unit slot +0x228: Donald 3600 (60 s), Goofy 2700 (45 s) | routine 0x0017DCC0 | VERIFIED n-base-hbf2 (values), n-v5-hb-friend-base (Goofy down 4700, up 7400) |
| Timer runs with the frame time 0x00349E10 (2.0 per game step); outside a fight (0x01C61958 = 0) it runs x battle table (pointer 0x00352130) +0x5C = 8 | 0x0017DCC0 | static; factor 8 VERIFIED on the heroes (n-v7-gameover: down 336 frames outside a fight) |
| At 0: 0x0017DE70 gives an HP change of max HP x table+0x54 (0.5); the revive routine 0x0017E138 scales any heal on a fallen friend by 0.5 again, clears the flag and plays motion 0x37. Result 25 % of max HP | 0x0017DE70, 0x0017E138, called from the HP routine 0x00187520 | VERIFIED Goofy 7/28 (n-v5-hb-friend-base) |
| A Potion or Cure on a fallen friend revives him through the same 0x0017E138 | 0x00187520 | VERIFIED n-v5-hb-cure-fallen (both friends fallen at 4700, up at 4786 with 3 HP after Sora's Cure); n-v5-hb-friend-base (Donald revived by his own Cure and later by Goofy's item) |
| Enemies cannot hit a fallen object: the hit loop 0x0018ED18 skips objects that 0x0019BB58 rejects (fallen flag). Heal-type hits (attack data +4 = 5 or 6) are still accepted by 0x001762F8 | 0x0018ED18, 0x0019BB58, 0x001762F8 | static + VERIFIED on a hero (n-v8-timer-default: 2700 frames at 0 HP in a running fight) |

### Sora's defeat
- HP change: class method +0x78 (0x0017A480) -> 0x00177C50 -> 0x00187520 -> unit slot 0x001A1910; when HP becomes 0:
  0x00187818 calls class method +0x5C if the object is not fallen yet. VERIFIED (static; the forced-fall test tool
  goes through this path).
- Player class table 0x00352410, +0x5C = 0x001D0D60: base routine 0x00179E18 (commands off 0x001D6A80, cry, fallen
  flag), 0x001D0EB8 (motion 0x36, action state 0x29 by 0x0016BD60 = takes no input), then the Game Over start
  0x001AEDF8 (through 0x001AF290 / 0x001AF328 / 0x001AF360). Game Over sequence pointer 0x00350DF0 (non-zero while
  it runs). VERIFIED static + n-v8-solo-killfull (go flag at the frame of the defeat).
- Mission-handled branch: flag 0x0034F240 & 0x20000 (the mission decides instead of the Game Over). Static only.
- Drive Form branch 0x001B6C60 (forms 1-6 and 0xC): seen, not understood. HYPOTHESIS.
- **King Mickey rescue: NOT located.** HYPOTHESIS: it is decided inside 0x001D0D60 / the Game Over sequence. Lane N
  jumps to the unchanged 0x001D0D60 when the second hero falls, so Mickey can only appear at that moment. Not tested.
- "Player is up again" routine of the game: 0x00179F10 (action state 0, control object); commands on 0x001D6AB0.

## 2. The fallen-hero behaviour (step 2) - done

A hero that reaches 0 HP while the other hero is standing:
| Point | Result | Evidence |
|---|---|---|
| Goes down, stays in the room, no Game Over | yes, for hero and for twin | VERIFIED n-v8-cure-hero, n-v8-cure-twin, n-v8-nat-hero, n-v8-nat-twin (natural enemy hit), n-v7-gameover, n-v8-newgame (two Roxas on kh2-coop-v1.iso) |
| Pose | the hero's own lying motion 0x36 (the game's own defeat pose); on revive the hero's own recover motion 6, then idle (a hero has no friend get-up motion 0x37) | VERIFIED all tests above (act 36 -> 06 -> 00) |
| Control while down | off (action state 0x29, commands off); stick, attack, jump do nothing; after the revive run / jump / attack work again | VERIFIED n-v3-fight-a (hero, one copy), n-v3-twin-b (twin, 2 copies), n-v8-nat-hero / n-v8-nat-twin (buttons pressed while down and after) |
| Gets up by himself | yes. Time = 2700/60 s = 45 s in a fight (Goofy's value; a player's own table value is 0), 8 times faster outside a fight, exactly as a friend's timer | VERIFIED n-v8-timer-default (twin down 4760, up 7460 = 2700 frames, in a fight), n-v7-gameover and n-v8-long-roam (336 frames outside a fight) |
| HP when he gets up by himself | 25 % of max HP (5/20), the friend's own routines 0x0017DE70 + 0x0017E138 | VERIFIED same tests; Goofy 7/28 |
| Enemies | cannot damage a down hero (HP stays 0, no reactions; pushes move him a little). They keep standing around player 1's hero if he is the one down; they do not switch to the twin (that is lane H) | VERIFIED n-v8-timer-default, n-v3-fight-a |
| Donald and Goofy | unchanged: same forced falls with and without lane N give the same timeline (97 common probe frames, 1 differs by sampling time) and byte-identical screenshots at 4800 and 7000 | VERIFIED n-v5-hb-friend-base vs n-v5-hb-friend-full |
| One player alone (disc without twin) | byte-identical: random buttons 3700-11000, 7 of 7 screenshots identical to merged-v2, 964 of 966 probe frames equal (2 differ by sampling time); forced defeat: Game Over at once, Continue, 6 of 6 screenshots identical, 55 of 55 probe frames equal | VERIFIED n-v8-solo-base vs n-v8-solo-full; n-v8-solo-killonly vs n-v8-solo-killfull |
| Sync | never out of sync in any 2-copy test; long runs with random buttons on both pads and forced falls: free-roam disc 30,000 frames, 468 digests, 9 of 9 screenshot pairs identical, 8 falls, one Game Over + Continue inside; fight disc 7,300 frames, 114 digests, 4 of 4 pairs, 3 falls | VERIFIED n-v8-long-roam, n-v8-long-fight |

Only the main player class (table 0x00352410) is changed. Other player class tables that share the HP routine
(+0x78 words at 0x0034E9D0, 0x00352258, 0x00352300, 0x003523D8, 0x00352530, 0x00361D78, 0x003620D8, 0x00362338,
0x00362658, 0x00362A98) keep the game's own defeat. Which characters use them is not known (HYPOTHESIS: special
forms / special player characters). Sora and Roxas use 0x00352410 (VERIFIED n-v8-newgame, fight and roam discs).

## 3. Healing across heroes (step 3)

### Potion (items used in a fight) - done, automatic target
How the game does it: a used item is queued; 0x001BA598 applies it and calls 0x001A2A50(effect, target status id,
user status id, boost) at 0x001BA624. The target is a CHARACTER id, and both heroes have the same id, so the twin
was never reached. Lane N replaces that one call (`n_heal`):
- item on the heroes' id used by player 1 (or by a friend): goes to the hero; only if the twin is down and the hero
  is not, it goes to the twin;
- used by player 2: goes to the twin; if the hero is down, to the hero;
- party-wide effects: the game's routine, then the same effect on the twin's own unit slot.

| Test (2 linked copies, in sync) | Result |
|---|---|
| n-v8-potion | twin down at 4760; player 1's Potion (shortcut) at 4802 -> twin up at 4856 with 4/20. Second Potion with the twin up: hero 5 -> 13. VERIFIED |
| n-v8-potion-p2 | hero down at 4760; player 2's Potion at 4802 -> hero up at 4856. Second Potion: twin 5 -> 13. VERIFIED |

Not done / what blocks it:
- **No choice of the other hero as a target on screen.** The item target list has one row per character id, and
  the heal is applied by character id; "Sora" is one row for both heroes. A separate row needs menu work, and
  player 2 has no visible menu at all (lane G, open problem 3). Nearest working version = the automatic rule above.
- A standing hero cannot give a Potion to a standing, hurt other hero (it goes to the user).
- Party-wide items (Mega-Potion ...) on the twin: code is there (`n_he_party`), NOT tested.
- Items used from the pause menu outside a fight (0x00263778 -> call at 0x002637BC) are not hooked: hero's slot only.

### Cure - done
How the game does it (VERIFIED by trace tests n-v4-cure-dbg2, n-v5-hb-cure-a..., n-v7-cure-trace):
- Cure is a script. The script thread being run is at 0x0034D8A4 (set by 0x0016CD48), thread+0x38 = the caster's
  object. The script asks the script command "party member N" (0x00173E88, table entry 0x0034DFE8) for N = 0, 1, 2
  (0 = the engine's player, 1 and 2 = the friends) and, for each one close enough to the caster, calls the script
  command "deliver this attack to this object" (0x0018FAB0, table entry 0x0034EFB8), which builds a hit record
  (0x0018DB38) and calls the object's take-a-hit method (+0x64).
- Range: Goofy is healed at 280 units from the caster and not at 289 (tests n-v5-hb-range-250 / 280 / 289 / 298 /
  310 / 375 / 440 / 500 and -a = 1500). Lane N uses 285 between the heroes.
- So before lane N: player 1's Cure never reached the twin, and player 2's Cure healed player 1's hero when he was
  near and never player 2's own hero (VERIFIED n-v6-cure-both, second cast: MP spent, nobody healed).

Lane N: `n_party` answers "party member 0" with the twin when the running script belongs to the twin; `n_cure`
gives a hero's Cure to the caster always and to the other hero when within 285 units (also when he is down).
Friends' Cures and Cures reaching friends are unchanged.

| Test (2 linked copies, in sync) | Result |
|---|---|
| n-v8-cure-twin (disc with Donald and Goofy) | twin down at 4700; player 1's Cure -> twin up at 4786 with 7/20. VERIFIED |
| n-v8-cure-hero | hero down at 4760; player 2's Cure -> hero up at 4826 with 7/20. VERIFIED |
| n-v6-cure-both (first cast) | both at 5/20 and close: player 1's Cure -> both 19/20. VERIFIED |
| n-v7-cure-far | heroes about 490 units apart: player 2's Cure heals the twin 5 -> 19, the hero not. VERIFIED |
| n-v5-hb-cure-fallen (one copy) | the same Cure revives fallen Donald and Goofy when close (the game's own behaviour) |

Notes: a hero revived by Cure has 7/20, fallen friends revived by the same Cure had 3/28 and 3/18. The game computes
the amount per target (0x001A1E20); why a player-type target gets more is not worked out (HYPOTHESIS: the low-HP
bonus slot+0x240 / table+0x178). Player 1's Cure with the twin far away: not run as its own test (player 1's own
heal is the game's unchanged path; the range branch is the one VERIFIED in n-v7-cure-far).
`n_party` changes "party member 0" for EVERY script that belongs to the twin; only Cure was tested (HYPOTHESIS for
other twin-owned scripts: correct, since "the player" of player 2's script is player 2's hero).
Donald's Cure: he never chooses the twin (not in his list); when he heals the hero the twin gets nothing. Left for
the helper lane.

### HP orbs - NOT done
Static finding (HYPOTHESIS, not tested): the pick-up routine 0x001A5140 only asks party members 0-2 that are not
fallen (call of 0x00176B20 at 0x001A51F8), so the hero and the friends pick up orbs and the twin does not. Lane N
does not change this. A down hero does not pick up (the game's own fallen check). An orb heal is an HP change on
the collector's own object, so once the twin is added to that loop it will fill the twin's own HP.
Also seen: a save point refilled the hero and not the twin (n-v8-long-roam, 14388-14416) - lane D's area.

## 4. Game Over only when both are down; Continue (step 4) - done

`n_die`: if there is no twin, or the object is neither hero nor twin, or the OTHER hero is already fallen, the
game's own routine 0x001D0D60 runs unchanged (Game Over, mission rule, Mickey).
| Test | Result |
|---|---|
| n-v7-gameover (2 copies, free-roam disc, 129 digests in sync) | hero down at 5000 (no Game Over); twin falls at 5120 while the hero is down -> Game Over screen (Continue / Load Game); Continue at 5510 -> room rebuilt, hero 20/20 and twin 20/20 standing, down flags 0; a later fall of the twin (7600) is again "down", up at 7938 with 5/20. VERIFIED |
| n-v8-long-roam | the same inside the 30,000-frame random run (18000 / 18100, Continue at about 18364). VERIFIED |
| n-v8-solo-killfull | one player alone: Game Over at once, as the original. VERIFIED |
Not run: the order "twin down first, then the hero" (same code path with the roles swapped), and Game Over on a
mission disc (Continue crashes there without lane N too - lane B).

## 5. Camera, HUD, missions (step 5)

- **Camera** (shared screen): stays on player 1's hero. While he is down it sits close and low behind the lying
  hero with the game's defeat light ring in the picture (`n-v7-gameover\p1_f005060.png`,
  `n-v8-long-roam\p1_f027100.png`); player 2's hero can be out of the picture. In the first second of the fall the
  normal fight view is kept (`n-v5-cure-hero\p1_f004790.png`). When the twin is down the camera is normal.
- **HUD**: player 1's face turns red with an empty HP bar; the command menu is still drawn although commands are
  off; there is no "down" sign and no countdown. Player 2 has no HUD of its own (other lanes).
- **Missions with their own fail rule.** VERIFIED example, Hollow Bastion fight with Donald and Goofy
  (test-n-hbf): when player 1's hero loses all HP there, his HP stops at 6/20 and about 18 frames later the fight
  is taken down and the story scene follows (n-v8-hb-mission; the same when his HP is held at 5, n-v5-hb-cure-a).
  The rule looks only at the engine's player: with the twin at 0 HP the fight goes on and the twin is "down"
  (n-v8-cure-twin). So in such missions player 1's hero cannot go down, player 2's can.
  NOT tested: missions that fail on a hero's defeat (flag 0x0034F240 & 0x20000) - lane N only lets that branch
  run when the second hero falls; missions with timers / gauges; King Mickey; Drive Forms while down or falling;
  a room change or story scene starting while a hero is down.

## 6. The patch

### Hook sites (all of them)
| Address | Was | Now | Kind | Meaning |
|---|---|---|---|---|
| 0x0035246C | 0x001D0D60 | n_die 0x000F2800 | player class table +0x5C | HP reached 0 |
| 0x0035241C | 0x00178758 | n_tick 0x000F28D0 | player class table +0x0C | per-frame update: the timer |
| 0x00352488 | 0x0017A480 | n_hp 0x000F2990 | player class table +0x78 | HP change: a heal on a down hero revives |
| 0x001BA624 | jal 0x001A2A50 | jal n_heal | call site | a queued item takes effect |
| 0x0034EFB8 | 0x0018FAB0 | n_cure 0x000F2C74 | script command table | deliver an attack to an object (Cure) |
| 0x0034DFE8 | 0x00173E88 | n_party 0x000F2C34 | script command table | party member number N |

No game code is overwritten except the one `jal`. **No merged-v2 hook is touched**; the generator stops if any lane
N address is already written by the base file.

### Memory
- Routines: 0x000F2800-0x000F2DCB (371 words) of the given area 0x000F2800-0x000F2FFF.
- Variables 0x000F2FC0-0x000F2FDF (not written by the file, zero at boot): +0x00 / +0x04 timer hero / twin (float,
  1/60 s); **+0x08 / +0x0C = 1 while hero / twin is down by lane N's rule**; +0x10 / +0x14 falls counted;
  +0x18 / +0x1C revives counted.
- 0x000F2F80-0x000F2FBF and 0x000F2FE0-0x000F2FEF are written only by `--debug` test variants.
- The area is all zero in a run without any patch (boot, title, New Game, random play; 7 samples): VERIFIED
  n-v8-cave-unpatched.

### For the merge
- **Lane H (enemy targeting, hooks 0x00190A74, 0x00190B28, 0x001909A8): no address in common.** How to tell that a
  hero is down: **object+0x7F8, bit value 4** (the game's own fallen flag; the game's own test is 0x0019BB58, which
  returns 0 for a fallen object). It is set for lane N's down state and for the game's own defeat. Lane N's own
  flags 0x000F2FC8 (hero) / 0x000F2FCC (twin) are 1 only in the down state. A down hero must not be chosen; today
  enemies stay on player 1's hero when he is down and cannot hurt him.
- **Lane R (exits, hooks 0x0019A168, 0x00182D04, 0x0019A57C, 0x0019A590): no address in common.** Recommended
  rule: while either hero is down (flag above) do NOT change the room. Outside a fight the hero is up again after
  about 5.6 s, in a fight after at most 45 s or one Potion / Cure. Reason: a room change rebuilds both hero
  objects; lane N then forgets the down state (n_tick clears its flag for an object that is not fallen), and lane D
  carries each hero's HP into the new room, so the hero would probably arrive standing with 0 HP (HYPOTHESIS, not
  tested).
- Lane G / E: `n_party` and `n_cure` are table words of the script command tables at 0x0034DFE8 and 0x0034EFB8;
  lane G's known entries are at 0x0034E7xx. No overlap.

## 7. Open problems / next steps
1. HP orbs for the twin (section 3) - add the twin to the loop at 0x001A51F8 and test with orb drops.
2. A real target choice for items (needs a menu row and player 2's menu).
3. Camera and HUD while player 1 is down (low camera, no sign, no countdown).
4. Enemies do not move on from a down player 1 (lane H must skip heroes with the fallen flag).
5. Not tested: King Mickey, Drive Forms, missions that fail on defeat, room change / story scene while a hero is
   down, twin-first-then-hero Game Over, party-wide items, pause-menu items, other player class tables.
6. Cure amount on a revived hero (7) differs from a revived friend (3); the game's own formula, not explained.

## 8. Files
- Patch generator `tools\lane-n\make_down.py` (options: `--time N`, `--cure-range N`, `--no-die/-tick/-hp/-heal/
  -cure/-party`, test only: `--debug`, `--kill WHO@FRAME,...` (hero | twin | f0 | f1 lose all HP at that frame, the
  same on both PCs), `--extra FILE`).
- Test tools in `tools\lane-n\`: `nrun.sh` (one run with the probe; run-n, port 29450, PINE 28121), `nprobe.py`,
  `nsum.py`, `probecmp.py`, `ringsum.py`, `dbgsum.py`, `cavecheck.py`, `make_testlines.py` (HP / MP hold windows,
  `kit`, `potions`), `ndiff.py`, `vt.py`, `vcall.py`, `gh.sh` (Ghidra dumps into `local\analysis\n\`).
- Button scripts `tests\scripts\lane-n\`. Test variants of the patch `local\patches-n\`. Results `local\tests\n-*`.
- Test discs were deleted. Rebuild (base = `local\iso\English text build3 (candidate).iso`, read only):
  `dotnet local\build\Kh2Tool\Kh2Tool.dll inject <base> local\iso\test-n-hbf.iso local\variants\m-test-m-hbf\built <report>`
  (SHA-1 52559727ae350d177c53ca50c1ba85b31650a0de) and the same with `local\variants\m-test-m-solo\built` for
  `test-n-solo.iso` (SHA-1 f97f0d692529862d7377faaeb48766358ac780f0).

Repeat one test, example (twin down, player 1's Cure):
```
python -I tools\lane-n\make_testlines.py local\patches-n\lines\kit.txt kit
python -I tools\lane-n\make_down.py local\patches-n\hb-kill-twin --kill twin@4700 --extra local\patches-n\lines\kit.txt
bash tools/lane-n/nrun.sh n-v8-cure-twin test-n-hbf.iso 4960 2 "4730,4800,4900" 2 tests/scripts/lane-n/cure_hb_p1.txt tests/scripts/lane-n/idle_p2.txt idle "<full path>/local/patches-n/hb-kill-twin" 4650 --every 1
python -I tools\lane-n\nsum.py local\tests\n-v8-cure-twin\probe.txt --from 4690
```
Which tests ran which code: n-v8-solo-full ran the delivered file itself; n-v8-nat-hero / n-v8-nat-twin ran the
delivered routines with a 10 s timer and test HP lines; all other n-v8 tests ran the delivered routines plus the
test-only forced-fall block at the start of n_tick (and the test skill kit where magic or items are used).
