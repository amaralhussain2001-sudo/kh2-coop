# KH2 two-player online: improvement plan (2026-11-18, after build 27)

Where things stand: build 27 (exe `builds\card1` = own screens + smoother pacing + memory card transfer; patch `merged-v19` =
the glues up to 79 incl. "who opens a screen controls it"). Sources: docs/STATE.md parts 139 to 142, the read-me's "known problems",
KH2-COOP-PLAN.md, the user's open decisions (STATE lines 42/43) and the comparison with the Steam co-op mod (part 129).
Each item: what is wrong or missing, the improvement, WHY, size (S / M / L) and risk.

## A. Connection and smoothness

| # | Today | Improvement | Why | Size / risk |
|---|---|---|---|---|
| A1 | Both PCs sometimes freeze together for 0.4-0.6 s (2-3 s lost per 10 s in the first real session); cause not proven (HYPOTHESIS: packets held up on the way, e.g. Wi-Fi) | First MEASURE: the link logs each second's packet gaps and the round trip; the game log marks every wait over 100 ms with its frame. Then fix what it shows (cable instead of Wi-Fi; or a bigger buffer only for spikes) | The biggest stutter that is left; guessing would fix the wrong thing | S to measure, M to fix / low |
| A2 | Build 25: the faster PC slows down only AFTER it had to wait (wait + 3 ms) | Both PCs send how early the other's input arrives; the one that is ahead slows down a little before it ever waits (the way GGPO keeps two PCs centred) | Removes the remaining small waits; smoother when one PC is slower | M / medium (protocol change, both PCs update) |
| A3 | The input delay is chosen once in the lobby | Re-measure during play and change the delay at an agreed frame on both PCs | A connection that gets worse later would not stutter, a better one would answer faster | M / medium |
| A4 | A dropped player is removed after 20 s; he cannot come back | "Continue alone" for the host and a re-join that sends the host's state (save state) to the friend | One internet hiccup ends the evening today | L / high |

## B. Sync safety (the two PCs must stay the same)

| # | Today | Improvement | Why | Size / risk |
|---|---|---|---|---|
| B1 | Picture must be the same on both PCs, by hand (part 142: other values cannot be made fully safe for KH2) | The host's Picture goes into the join code; the friend's launcher sets the same value by itself and says so | Prevents the most common false "OUT OF SYNC" without asking the players to remember | S / low |
| B2 | Once "OUT OF SYNC", it stays so; the game goes on diverged | Recovery: the host sends its save state, both continue from the same point | Turns a lost session into a 5-second pause | L / high (save states must load the same on both) |
| B3 | Memory card: the host's card wins (build 26) | Before the game starts, the launcher shows "you will play with HOST's saves" and keeps only the last 5 backups | No surprise, no folder full of 8 MB backups | S / low |
| B4 | The join checks protocol, disc, BIOS, patches, settings, card | Also the package id (whole folder): a different build is refused with "update to build N" | A half-updated PC is found at the join, not by a strange fault later | S / low |
| B5 | The emulator SOURCE is at protocol 6 (part 142, not shipped) | Ship the next exe build with it (its new keys do nothing without a .view entry) and both PCs update together | Keeps source and shipped exe the same; no accidental mix | S / low |

## C. Speed (fps)

| # | Today | Improvement | Why | Size / risk |
|---|---|---|---|---|
| C1 | KH2 with own screens shows 30 game fps at 60 video fps: NORMAL, but looks like a problem | Say it in the read-me and in the launcher; show "game 30 / video 60 = normal" | Stops chasing a non-problem | S / none |
| C2 | The slower PC sets the pace for both; nobody sees which PC it is | The game log and a small on-screen note: "HUSSAIN's PC is at 52 fps: choose a lower Picture on both" | Tells the players the one setting that helps | S / low |
| C3 | First visits to new places stutter on both PCs (shaders are built on each PC, and lockstep shares every hitch) | Read-me tip; optional "warm-up" run alone through the rooms once | Hitches go away after the first visit | S / none |

## D. Playing together (the KH2 patch)

| # | Today | Improvement | Why | Size / risk |
|---|---|---|---|---|
| D1 | Build 27 owner rule tested on the pause menu, a shop, a talk; NOT on the Moogle, a save point opened by player 2, the world map, player 1's shop | One short run each | Make sure no screen locks out its own opener | S / low |
| D2 | A small game's rules screen belongs to whoever started it (the plan said "shared") | Your choice: keep, or make rules screens shared | Small, but it is a rule the players feel | S / low |
| D3 | Known: the sound follows player 1's camera; Stitch shows on both screens; Donald and Goofy follow player 1 while together; some Gummi points (ramming, special shots) go to player 1; some small games hear either controller (e.g. the whirlwinds) | Fix one by one, the most noticed first (sound per PC is the biggest: each PC could hear its own camera) | These are the things players notice every evening | M each / medium |
| D4 | Proposals 2 (each player's own form gauge view), 3 (look at the partner's gear, read-only) and 5 of your inspection: not chosen yet | Your choice | The Steam mod has 2 and 3 too | M / low |
| D5 | Player 2's hero is not in story scenes (the Steam mod shows a twin Sora there) | Put the twin into cutscenes where the scene allows | Player 2 feels part of the story | L / high (many scenes) |
| D6 | Balance (bosses +75 % HP) set from tests, not from play | Tune after your playthrough (per boss if needed) | Only real play shows if it is fun | S each / low |
| D7 | Luxord's card game, the paired boss moves, steering Riku: never played by two people | Your playthrough with logs | Scripts cannot judge feel | - |

## E. Testing and reports

| # | Today | Improvement | Why | Size / risk |
|---|---|---|---|---|
| E1 | The whole regression last ran on build 24 | Run it on build 27 now; adjust the old test scripts where player 2 answered player 1's menus (build 27 forbids that on purpose) | Catch side effects of the owner rule before you meet them | M / none |
| E2 | Logs are copied by hand from both PCs | "Send logs" button in the launcher: one zip with logs + emulog + package id | Faster, complete bug reports | S / none |
| E3 | I read logs by hand | A log reader: waits, freezes, out-of-sync chunk -> known cause (card, picture, real), card transfer, owner events | Every session gets the same careful check in seconds | S / none |
| E4 | The one-PC network test uses even jitter | Replay the jitter pattern of your real logs (bursts) | Future network changes are tested against your real line | S / none |
| E5 | No checklist for a playthrough | A short list per world: what to try, what to watch | Your evenings test the most in the least time | S / none |

## F. Folders and updates

| # | Today | Improvement | Why | Size / risk |
|---|---|---|---|---|
| F1 | Two folders: PS2-ONLINE (other games) and the KH2 test folder | Your decision (open since part 139's plan): keep separate while testing (recommended), or merge later | One folder is simpler, but the KH2 exe now changes the network part (card transfer), which you wanted untouched for other games | - |
| F2 | Updates are zips copied by hand | The launcher checks the package id at start and applies an update zip dropped next to it | No half-copied updates | M / low |
| F3 | Both players on one PC is not possible (comparison item) | A starter for two copies on one PC with two pads | Testing and couch play without a second PC | S / low |

## Order I recommend

1. NOW (small, safe, high value): B1, B4, B3, E2, E3, E1, D1, C1, C2.
2. AFTER YOUR NEXT EVENING'S LOGS: A1 (needs the measurement), D6 / D7, D3 in the order you notice them.
3. LARGER: A2, B2, A4, F2.
4. YOUR CHOICES FIRST: D2, D4, D5, F1.

## Decisions needed from you
1. Rules screens of small games: owner only (now) or shared? (D2)
2. Proposals 2, 3, 5: which, if any? (D4)
3. Twin Sora in story scenes: worth a large job? (D5)
4. One folder or two? (F1)
5. Start with phase 1 now?

## G. Inside the game: gameplay areas (asked 2026-11-18: "how we can improve it, what is the area inside the game")
Checked first: when one player opens the pause menu the game pauses for BOTH (run r11pm5: player 2's screen shows player 1's menu).

| # | Area | Today | Improvement | Why | Size / risk |
|---|---|---|---|---|---|
| G1 | Falling and reviving | A hero at 0 HP lies down; gets up alone after 45 s in a fight; Potion / Cure revives; no countdown shown; Game Over only when both are down | A visible countdown over the fallen hero; "hold Triangle beside your partner for 2 s" revives him with a quarter HP | Reviving each other is the heart of co-op; today it needs an item or a spell | M / medium |
| G2 | Difficulty | Bosses +75 % HP, ordinary enemies as in the original, so two heroes make normal fights easy | A co-op difficulty choice (host's launcher): ordinary enemies +50 % HP and a little more damage, bosses as now | Keeps fights a challenge with two Keyblades | S-M / low |
| G3 | Donald and Goofy | Together they follow player 1; they split only when the heroes are about 9 hero lengths apart | While two heroes play: Donald always with player 1, Goofy always with player 2 (or each helps whoever has less HP) | Player 2 gets his own support all the time | M / medium |
| G4 | Finding each other, room exits | Both must stand at an exit ("Waiting for the other player"); nothing shows where the partner is | An arrow at the screen edge pointing to the partner, with his name and HP; "call partner" (he is brought to you) after 10 s of waiting at an exit | Less searching and waiting with two own cameras | M / low |
| G5 | Sound | One sound for both PCs, heard from player 1's camera | Each PC hears from its own camera | Player 2 hears what his own screen shows | M / medium |
| G6 | Story scenes | Player 2's hero is not in the scenes; either player's START can skip a scene | (a) Skipping needs both players' START (no surprise skips); (b) later: player 2's hero in the scenes | (a) nobody misses a scene he wanted; (b) player 2 is part of the story | (a) S / low, (b) L / high |
| G7 | Pause menu | Pauses the game for both | A note on the partner's screen "HUSSAIN is in the menu"; keep the pause (one shared world: letting one player go on while the other browses would mean running the world under a menu = engine work with high risk) | The partner knows why everything stopped | S / none |
| G8 | Drive Forms, Summons, Limits | Own gauges; one Summon at a time; player 2's Summon has no entrance movie | Player 2's Summon gets its movie too (or neither); proposal 2: each player sees both form gauges | The same feel for both players | M / medium |
| G9 | Gear and planning | Own gear, wallet, bag; the partner's gear is invisible | Proposal 3: a read-only page "partner's gear" in the pause menu | Plan builds together without asking | M / low |
| G10 | Team moves | Each hero has his own reaction commands; Limits are hero + helper | A team Limit (both heroes) built from existing Limit moves | A move only possible together | L / high |
| G11 | Special rides and small games | Light Cycle: over when either cycle is destroyed; Gummi: one hull gauge shows the weaker ship; some small games hear either controller (the whirlwinds) | Light Cycle: a destroyed rider comes back after a few seconds; Gummi: both hulls shown; whirlwinds: each rider hears his own controller | Fairer and less confusing rides | M each / medium |
| G12 | Progression | Level and learned abilities shared; EXP shared; gear, Keyblade, items, munny, Drive own | Keep (fair, simple); show "+EXP" for both | Separate levels would split the balance | - |
| G13 | Bosses with special moves | Paired moves, Luxord, Xigbar, the last Xemnas built and tested by scripts only | Your playthrough decides what to adjust (save before them) | Scripts cannot judge feel | - |

Recommended first: G1, G4, G2, G7, G6a (most fun for the effort), then G3, G5, G9, G8; large: G6b, G10.
