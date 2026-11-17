# Plan row 9: a boss's scripted move with two heroes. The per-fight report

Written 2026-11-14 for job 10 of the job list ("build it or write the per-fight report"); brought up to test build
20 on 2026-11-15 (the ninth round: both heroes inside the same hold) and to TEST BUILD 21 on 2026-11-15 night (the
user's items 1 to 4: a boss's grab takes only the hero it aims at; only the last Xemnas's laser dome takes both). Made by
`python -I tools\own\row9_report.py`. The evidence behind every line is in `docs\STATE.md`, sections "Eighth round" and "Ninth round".
Words: VERIFIED = seen in a test run of this project. READ = read in the game's program, not run.
HYPOTHESIS = my best explanation, not proven.

## 1. What a scripted move is

- READ: a boss's script calls `trap_obj_motion_capture`. The game's routine 0x00180378 then takes ONE victim. It
  stops his own motion, plays the victim's part of the move from the BOSS's motion set on him, and holds him
  until the script lets go. The victim's place and pose come from the boss's motion. There is no second place.
- READ: 52 of the 99 boss scripts use that call (`local\analysis\boss-survey.txt`). The game was written for one
  hero, so every script asks for "the player" and holds exactly him.

## 2. What builds 13 and 14 do (the first half of row 9: BUILT)

- The move takes ONE hero: the hero the boss already holds, else the nearer one. VERIFIED at Shan-Yu.
- The move's command (for example "Press") is in THAT hero's menu, and that player's buttons count. VERIFIED at
  Shan-Yu: player 2 alone wins the fight.
- The other hero stays free. He can move, hit the boss and use his menu while his friend is in the move.
- This is done by the glues 36, 38, 39 and 43 of build 13, on top of the glues 12, 15 and 16 of the builds before.
- BUILD 14 ADDS: a boss's green command is taken by ONE hero. The hero who presses first does the move, and
  for that move HE is "the player" of the boss's script. While the boss holds him (and for a moment after), the
  other player's press on that boss does nothing. (Glues 44, 45 and 47.) VERIFIED at Xigbar and Luxord.

## 3. "Both heroes in the same move at once" (the second half of row 9): BUILT FOR THE FIRST FIGHT, Shan-Yu's clash (test build 16)

The user's decision of 2026-11-10 stands: both heroes do a boss's scripted move together; one hero alone is only
the fallback where two is PROVEN impossible, reported per fight. That proof exists for no fight.

WHAT BUILD 16 DOES, at Shan-Yu's gate (VERIFIED, runs tg35 to tg39 of candidate v74; STATE parts 61 to 66):
- When Shan-Yu's script hooks its clash onto one hero and the other hero is up, free and within 500 units, the
  other hero is put beside and a little behind the first and is in the clash too.
- Each player has "Press" (and "Takedown") in his own menu, and each player's Triangle pushes. One press makes
  both heroes push and counts once.
- The clash's clock runs as in the game (one script steps the boss's numbers).
- A hero who is far away stays free. A grab, or the falcon's lift, stays the grabbed hero's alone.

HOW (READ, then built): the hero's side of a boss's move is a script that the boss's script HOOKS onto the hero
(`trap_obj_hook`). The second hero gets his own copy of that hooked script. My three "reasons of risk" of the
first version of this report did not hold: the second hero plays the move where he is put, not inside the first;
with his own copy of the script his move ends by itself; and a hero who wants to stay free only has to stand
away.

THE OTHER FIGHTS (test build 20; STATE, "Ninth round", parts 93 to 100). The user's word of 2026-11-15: "a boss's
hold takes one hero" is an exception he gave no OK for: build "both heroes inside the same hold", or prove per
boss why it cannot be done.
BUILT (glue 65, `merge_v7.py --holdpair`; VERIFIED in the runs of the table):
- When an enemy's script captures a hero or attaches him to itself, and that is NOT the answer to this hero's own
  green command, the other hero (up, not held by another captor) is put into the same hold, wherever he stands:
  every call of the captor's script for the first hero (capture, attach, detach, place, direction, flags, the
  motion calls, "blow") is made for the second too. One script drives the hold; both are let go together.
- A hero who is down is not taken. Shan-Yu's room keeps its own rule (build 16).
- THE NETS: a mirror hero left behind is thrown off 40 steps after the named hero is free (or after 1,200 frames
  without a call that names him); a hero in one and the same captured motion for a minute is thrown off (glue 60
  of build 18). "Thrown off" = detach, "motion start 16", "blow" without speed: the one way of 14 tried that frees
  a hero (part 96).
- THE GROUNDSHAKER'S REAL CAUSE is found and cured, and LUXORD'S TRICKS let the loser go in time (glue 67): see
  their lines in the table.
WHAT IS NOT A PAIR, AND WHY (the per-boss reason asked for):
- A MOVE THAT A HERO STARTS WITH HIS OWN GREEN COMMAND (Xaldin's jumps, Demyx's water forms, Xigbar's sniper answer,
  Luxord's games, and the answers in the scripts of the sorting below). READ: such a move is an ACT OF THE BOSS:
  an object runs one act at a time, the act plays the boss's half of the paired motion and keeps ONE record of
  its partner in the script's work memory, and it is steered by the commands of the hero who pressed. So two
  heroes cannot each have their OWN copy of the move (VERIFIED the hard way in build 13: with two partners
  Xigbar's sniper part never ended and Luxord's trick held a hero for the whole fight; build 14 cured both by
  "the first press takes the command"). A second hero inside the SAME copy could only be a mirror without any
  input, for as long as the first player goes on pressing (Luxord's command game: 20 seconds; Xigbar's sniper
  part: to its end): a passenger, which `REQUIREMENT-full-parity.md` forbids. Outside the move he keeps playing,
  and the command is in his own menu as soon as the boss is free again. THE USER GAVE HIS OK ON 2026-11-15:
  "B OK. Keep player-initiated green Reaction Commands exclusive to the player who activates them. The other
  player should remain free to continue fighting"
- The mirror hero of a pair has no hooked script of his own (the boss's script hooks one piece onto one hero);
  where that piece reads a controller, it reads the named hero's. Build 20 (glue 68, `--holdpads`) made the two
  controllers one while both heroes were held. BUILD 21 LEAVES GLUE 68 OUT: each player keeps his own controller,
  one press never counts twice.
BUILD 21 (THE USER'S ITEM 4 OF 2026-11-15: "For single-target attacks, prefer capturing only the targeted player. For
genuinely shared boss mechanics, both players should participate meaningfully."): `tools\own\cap_kinds.py` sorted
every boss capture of the 40 fights and the ten boss rooms: all are SINGLE-TARGET (the boss's script takes one
victim with a move) except the last Xemnas's LASER DOME (move 0x106: the game itself captures the player and Riku).
Glue 65's fifth form (`--holdshared`) makes a pair only there; every other ENEMY's grab takes the hero the script
names, as the game; the stray-capture cure and the nets stay. A captor that is no enemy (a board, a gimmick: Mail
Delivery, the skate challenges) keeps build 20's pair (its fifth part, candidate v129: the regression of v128 had 49
fault lines at those games' ends without it). In the 40 fights on v129 such captors made pairs in three fights (runs ob1 ..
ob3 name them): the Storm Rider fight's whirlwinds (F_MU070_BOSS, kind G_OBJ, mu08 79) and moving parts of The World That
Never Was (F_EH070 / F_EH080 / F_EH110, kind F_OBJ, eh26 69 and eh28 68); every enemy there took only its target. In the dome each player has his own Reflect (co_two), a press of
player 2's hero is sent in player 1's hero's name (hs_rc: the dome's pieces run on the hero its lasers aim at), the
dome is never "a hero's own move" (hs_hf). Shan-Yu's clash keeps glue 50; its push count goes up once a push
(STATE part 112).

A FIRST SORTING OF THE OTHER FIGHTS (READ in the decoded scripts with `tools\own\row9_hooks.py`; it follows the
scripts' own calls from the REACTION_CALLBACK, so a hook that an act started by a command makes is counted as
"not an answer"; each line needs a human look before it is built):
- 17 of the 43 scripts have at least one hook that is NOT the direct answer to a hero's command (a move the boss
  may FORCE): B_MU100 Shan-Yu (1: the clash, BUILT); B_BB110 the Dark Thorn (1); B_CA040 / B_CA040_PUB the Grim
  Reaper (1); B_EX100 the Twilight Thorn (2, beside 7 answers); B_EX120 / _HB / _HB_LV99 (1); B_EX130 / _LV99
  Xaldin (1); B_EX170_LAST / _LV99 the last Xemnas (7, beside 10 answers); B_EX390 (1, in its start-up);
  B_HE020 Cerberus (1); B_HE100 the Hydra (1, beside 4 answers); B_LK110 Scar (1); B_LK120 the Groundshaker (3).
- In the other 26 scripts every hook is the answer to the hero's own command: there the move is that hero's
  own, and "one hero does it" is what the command means (builds 13 and 14).

## 4. The fights, one by one

How to read the table. "Sweep" = the mission sweep of the seventh round (build 12 candidate, level 1 heroes, 9,000
frames, `docs\PARITY-SWEEP.md`): it proves that the fight STARTS and RUNS with two heroes in sync; it does not
play the boss's move on purpose. The room match is by room: a script's object stands in that room; which of the
room's missions uses it was not followed. "State": OK = the move was looked at with two heroes and is right.
FIXED = a fault of earlier builds that a later build cures, seen in test runs.
PAIR = build 20 puts both heroes inside the same hold; seen in test runs (build 21: only the last Xemnas's laser dome).
SINGLE = build 21: the boss's grab takes only the hero it aims at, the other stays free; seen in test runs. OWN = in the test runs every capture was
the answer to a hero's own command (his own move, section 3). PLAYED = played on purpose with two heroes on
build 21's candidate (20,000 frames, both players Circle / Triangle / R1, HP held, the capture log): every hold
ended, in sync. RUN = the fight ran with two heroes
in this round, the move itself was not looked at. OPEN = a fault is open.
SWEEP = only the sweep. NO ROOM = the object stands in no room file (it is made by another object or by a script).

| Script | Kind | Rooms | Sweep (mission program: result, fault lines) | State | Seen with two heroes |
|---|---|---|---|---|---|
| `B_AL020` | L_BOSS | al05 | al05 62: OK-V5, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: al05 62: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times. |
| `B_AL100_1ST` | BOSS | - | - | NO ROOM |  |
| `B_AL100_2ND` | BOSS | - | - | NO ROOM |  |
| `B_AL100_FIRE` | BOSS | al03, he09 | al03 59: OK, 0; he09 124: OK, 0; he09 125: OK, 0; he09 175: OK-GAME, 19; he09 176: OK-GAME, 19 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: al03 59: in sync, 0 fault lines, player 1's hero held 5 times, player 2's 1 times (the longest hold in one action 180 frames); he09 124: in sync, 0 fault lines, player 1's hero held 2 times, player 2's 0 times (the longest hold in one action 336 frames). |
| `B_AL100_ICE` | BOSS | al03, he09 | al03 59: OK, 0; he09 124: OK, 0; he09 125: OK, 0; he09 175: OK-GAME, 19; he09 176: OK-GAME, 19 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: al03 59: in sync, 0 fault lines, player 1's hero held 5 times, player 2's 1 times (the longest hold in one action 180 frames); he09 124: in sync, 0 fault lines, player 1's hero held 2 times, player 2's 0 times (the longest hold in one action 336 frames). |
| `B_AL110` | ZAKO | - | - | NO ROOM |  |
| `B_AL120` | ZAKO | - | - | NO ROOM |  |
| `B_BB100` | BOSS | bb11 | bb11 72: OK, 0; bb11 80: OK, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: bb11 72: in sync, 0 fault lines, player 1's hero held 4 times, player 2's 1 times (the longest hold in one action 160 frames); bb11 80: in sync, 0 fault lines, player 1's hero held 2 times, player 2's 0 times (the longest hold in one action 130 frames). |
| `B_BB110` | BOSS | bb05 | bb05 78: OK, 0; bb05 81: OK, 0; bb05 79: OK, 0 | SINGLE | The Dark Thorn. READ: its forced move is a GRAB (the boss attaches the hero to his hand, carries and throws him). BUILD 20: BOTH HEROES INSIDE THE SAME GRAB. Seen on candidate v107 (run h7, STATE part 97): 2 pairs of 182 frames, both heroes thrown off together. An earlier form of the glue left a hero frozen here for 7,806 frames (part 96): its "let him go" did not work; the one that works was found by trying 14 ways. The answers to a hero's own command ("Catch" and what follows) stay that hero's. BUILD 21 (the user's item 4 of 2026-11-15: a single-target attack takes only the targeted player): THE GRAB TAKES ONLY THE HERO IT AIMS AT, the other hero stays free and fights (the ten boss rooms on v122 / v124, runs h10 / h11, and the 40 fights on v128, run rs4: no pair). ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: bb05 78: in sync, 0 fault lines, player 1's hero held 13 times, player 2's 4 times (the longest hold in one action 372 frames). |
| `B_CA010` | BOSS | ca10 | ca10 60: OK, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: ca10 60: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times. |
| `B_CA020` | ZAKO | ca01, ca07, ca09, ca10, ca12, ca13, ca14, ca15, ca20, ca21, ca22 | ca01 51: OK, 0; ca01 52: OK, 0; ca01 53: OK, 0; ca01 54: OK, 0; ca07 58: OK, 0; ca09 59: OK, 0; and 5 more | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: ca01 51: in sync, 50 fault lines, player 1's hero held 3 times, player 2's 0 times (the longest hold in one action 88 frames); ca10 60: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times. |
| `B_CA040` | ZAKO | ca01, ca02, ca03, ca05, ca07, ca09, ca10, ca12, ca13, ca14, ca15, ca18, ca21, ca22 | ca01 51: OK, 0; ca01 52: OK, 0; ca01 53: OK, 0; ca01 54: OK, 0; ca02 55: OK, 0; ca02 88: OK, 0; and 11 more | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: ca01 51: in sync, 50 fault lines, player 1's hero held 3 times, player 2's 0 times (the longest hold in one action 88 frames); ca02 55: in sync, 0 fault lines, player 1's hero held 1 times, player 2's 0 times (the longest hold in one action 72 frames); ca10 60: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times; ca18 85: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times. |
| `B_CA040_PUB` | ? | - | - | NO ROOM |  |
| `B_CA050` | BOSS | ca01, ca18 | ca01 51: OK, 0; ca01 52: OK, 0; ca01 53: OK, 0; ca01 54: OK, 0; ca18 85: OK, 0; ca18 11: OK, 0; and 1 more | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: ca01 51: in sync, 50 fault lines, player 1's hero held 3 times, player 2's 0 times (the longest hold in one action 88 frames); ca18 85: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times. |
| `B_EX100` | L_BOSS | tt34 | tt34 157: OK, 0 | OK | The Twilight Thorn. VERIFIED in every regression (k9-thorn, k9-thorn-nopress, k9-thorn-p2tri, k11-thorncont, b13-thorn-p2): the thrown hero's follow-up command works for player 2 and for nobody pressing; in sync, 0 fault lines. |
| `B_EX110` | BOSS | tt20 | tt20 137: OK, 0; tt20 213: OK, 0 | PLAYED | Axel (second fight). Ran with two heroes in the seventh round (runs r11-axel2-contB-p1 / -p2: the fight, a Game Over, Continue, the fight again): in sync, 0 fault lines. Its paired move was not looked at. ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: tt20 137: in sync, 0 fault lines, player 1's hero held 3 times, player 2's 0 times (the longest hold in one action 184 frames); tt20 213: in sync, 0 fault lines, player 1's hero held 2 times, player 2's 1 times (the longest hold in one action 180 frames). |
| `B_EX110_LV99` | BOSS | tt20 | tt20 137: OK, 0; tt20 213: OK, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: tt20 137: in sync, 0 fault lines, player 1's hero held 3 times, player 2's 0 times (the longest hold in one action 184 frames); tt20 213: in sync, 0 fault lines, player 1's hero held 2 times, player 2's 1 times (the longest hold in one action 180 frames). |
| `B_EX110_SKIRMISH` | BOSS | tt05 | tt05 189: OK, 0; tt05 84: OK, 0; tt05 85: OK, 0; tt05 88: OK, 0; tt05 86: OK, 0; tt05 87: OK, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: tt05 189: in sync, 0 fault lines, player 1's hero held 4 times, player 2's 7 times (the longest hold in one action 40 frames). |
| `B_EX120` | BOSS | he17 | he17 123: OK, 0; he17 2: OK, 0 | OWN | Demyx in the Underworld (the water forms: the hero takes a form by his own command). In the test runs every capture in this fight was the answer to a hero's OWN green command; such a move stays that hero's own (section 3, "what is not a pair, and why"). Every hold ended (the longest in one action 792 frames, run h7). ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: he17 123: in sync, 0 fault lines, player 1's hero held 10 times, player 2's 0 times (the longest hold in one action 120 frames). |
| `B_EX120_HB` | BOSS | hb04 | hb04 55: OK, 0; hb04 114: OK, 0; hb04 1: OK, 0 | OWN | Demyx in Hollow Bastion (the same moves as B_EX120). In the test runs every capture in this fight was the answer to a hero's OWN green command; such a move stays that hero's own (section 3, "what is not a pair, and why"). Every hold ended. ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: hb04 114: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times; hb04 55: in sync, 0 fault lines, player 1's hero held 14 times, player 2's 4 times (the longest hold in one action 792 frames). |
| `B_EX120_HB_LV99` | BOSS | hb04 | hb04 55: OK, 0; hb04 114: OK, 0; hb04 1: OK, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: hb04 114: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times; hb04 55: in sync, 0 fault lines, player 1's hero held 14 times, player 2's 4 times (the longest hold in one action 792 frames). |
| `B_EX130` | BOSS | bb15 | bb15 82: OK, 0; bb15 97: OK, 0 | OWN | Xaldin. READ: a blow-away of the hero who was hit, and the hero's own jumps ("Learn" / "Jump"). In the test runs every capture in this fight was the answer to a hero's OWN green command; such a move stays that hero's own (section 3, "what is not a pair, and why"). Every hold ended. ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: bb15 97: in sync, 0 fault lines, player 1's hero held 25 times, player 2's 0 times (the longest hold in one action 100 frames); bb15 82: in sync, 0 fault lines, player 1's hero held 11 times, player 2's 3 times (the longest hold in one action 342 frames). |
| `B_EX130_LV99` | BOSS | bb15 | bb15 82: OK, 0; bb15 97: OK, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: bb15 97: in sync, 0 fault lines, player 1's hero held 25 times, player 2's 0 times (the longest hold in one action 100 frames); bb15 82: in sync, 0 fault lines, player 1's hero held 11 times, player 2's 3 times (the longest hold in one action 342 frames). |
| `B_EX140` | BOSS | eh10 | eh10 57: OK, 0; eh10 100: OK, 0 | FIXED | Xigbar (story fight eh10 57; the data fight eh10 100 is `B_EX140_LV99`). FAULT F10 OF BUILDS 12 AND 13: his sniper part starts when a hero takes the green command "Warp Snipe". When BOTH players took it in the same moment he held both heroes and the part never ended (build 12: the game stopped there). With one player pressing it always worked (runs x15 to x18, build 13). BUILD 14 (glue 47): the first hero who presses does the move, the other player's press does nothing: one capture, 64 frames, then both fight on (runs x19, x20, x23, x24; Data Xigbar xd10, xd12). VERIFIED. |
| `B_EX140_LV99` | BOSS | eh10 | eh10 57: OK, 0; eh10 100: OK, 0 | FIXED | Data Xigbar: the same fault and the same cure as B_EX140 (runs xd9, xd10, xd12). |
| `B_EX150` | BOSS | eh14 | eh14 101: OK, 0; eh14 58: OK, 5 | FIXED | Luxord (story fight eh14 58). FAULT F11 OF BUILDS 12 AND 13: his trick pulled in the hero who pressed the command but turned "the player" into the card or the die; with two heroes that could be two different heroes, and one stayed held for the whole fight. BUILD 14 (glues 44, 45, 47): nobody is held for ever; both heroes are free and fight at the end of every run (lux10, lux11, lux14, lux15). When both players press in the same frame each gets his own change (one the card, one the die) and both come back. VERIFIED for "nobody stuck"; the card game itself cannot be judged by a test script. BUILD 20 (glue 67): see B_EX150_LV99; the story fight on candidate v113 (run lxR): player 1's hero held 11 times, player 2's 7 times, the longest hold in one action 114 frames. ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: eh14 101: in sync, 0 fault lines, player 1's hero held 10 times, player 2's 10 times (the longest hold in one action 392 frames). |
| `B_EX150_LV99` | BOSS | eh14 | eh14 101: OK, 0; eh14 58: OK, 5 | FIXED | Data Luxord. FAULT OF BUILDS 14 TO 19, found in the ninth round: a hero who lost a card or command trick stood in the captured move 254 for up to a minute (3,602 frames, run lxI; ended only by the one-minute rule). THE CAUSE (READ, then shown by a control, part 99): the act of Luxord that turns the loser into the card or the die, and so lets him go, waits 100 steps first; the OTHER hero's hit in that time started Luxord's damage act, which replaced it. With the other player not pressing the hold ends by itself (run lxQ: 130 frames). BUILD 20 (glue 67): while a hero stands in Luxord's trick, a hit takes HP but is no "reaction". Run lxP: player 1's hero lost five tricks (336, 126, 130, 130, 392 frames), player 2's three (128, 130, 130); every one ended by the script. ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: eh14 101: in sync, 0 fault lines, player 1's hero held 10 times, player 2's 10 times (the longest hold in one action 392 frames). |
| `B_EX170` | BOSS | eh19, eh23 | eh19 97: OK, 0; eh19 59: OK, 0; eh23 73: OK, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: eh19 97: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times; eh19 59: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 1 times (the longest hold in one action 780 frames); eh23 73: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times. |
| `B_EX170_LAST` | BOSS | eh20 | eh20 74: OK, 0; eh20 98: OK, 0 | PAIR | The last Xemnas. BUILD 20: BOTH HEROES INSIDE THE SAME HOLD in his opening move (move 0x101, runs h4 / h7), in THE PART WHERE RIKU MUST FREE SORA (run xeB, part 97: both Xemnas objects' HP written to 150 at frame 6500; the part runs from frame 10006 to 13434, both heroes held, the fight goes on) and in THE LASER PART AT THE END (runs xeC / xeD: HP 40 / 1; move 0x106 on both heroes and on Riku from frame 7690, both stand in the dome, the "Reflect" commands; the fight ends). WHO STEERS RIKU (part 100): the boss's script gives Riku to the player whose hero it named (runs xeG / xeH / xeI on v112: only that player's stick moved him). BUILD 20 (glue 68): while both heroes are held both controllers count, so BOTH PLAYERS STEER RIKU (run xeN on v115: player 1's stick alone moves him; xeO: player 2's; xeP: both mash, the part plays and the fight goes on). BUILD 21: HIS OPENING MOVE AND THE RIKU PART TAKE ONE HERO (the one the script names); the held hero's player steers Riku with his own stick (run xsB on v122) and his green commands reach the boss (run rkE on v127); THE END OF THE RIKU PART WITH ONE HERO HELD IS SEEN: run rs4 on v128 (the rematch eh20 98): player 1's hero held from 0x105, Riku played by player 1, move 0x104 SENT BY PLAYER 1 at frame 17560, the part ended and the fight went on (in seven shorter runs a button script did not bring Riku to Xemnas). THE LASER DOME STAYS THE ONE SHARED MOVE: both heroes stand in it, each player has his own Reflect in his own menu (glue 65 co_two), a press of either player is sent in player 1's hero's name so that every piece of the dome runs on the hero its lasers aim at (hs_rc), the count goes up once a press and the dome ends once (runs xt2 .. xt6 on v128: player 2 alone 41 reflects, player 1 alone 30, both 55; no step with two; STATE parts 111, 113). ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: eh20 98: in sync, 0 fault lines, player 1's hero held 4 times, player 2's 11 times (the longest hold in one action 578 frames); eh20 74: in sync, 0 fault lines, player 1's hero held 6 times, player 2's 15 times (the longest hold in one action 160 frames). |
| `B_EX170_LAST_LV99` | BOSS | eh20 | eh20 74: OK, 0; eh20 98: OK, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: eh20 98: in sync, 0 fault lines, player 1's hero held 4 times, player 2's 11 times (the longest hold in one action 578 frames); eh20 74: in sync, 0 fault lines, player 1's hero held 6 times, player 2's 15 times (the longest hold in one action 160 frames). |
| `B_EX170_LV99` | BOSS | eh19 | eh19 97: OK, 0; eh19 59: OK, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: eh19 97: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times; eh19 59: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 1 times (the longest hold in one action 780 frames). |
| `B_EX210` | ZAKO | - | - | NO ROOM |  |
| `B_EX220` | ZAKO | - | - | NO ROOM |  |
| `B_EX220_LV99` | ZAKO | - | - | NO ROOM |  |
| `B_EX240` | L_BOSS | eh26, eh27, eh28 | eh26 69: OK, 0; eh26 86: OK, 0; eh27 75: OK, 0; eh28 68: OK, 0 | PAIR | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: eh26 69: in sync, 0 fault lines, player 1's hero held 7 times, player 2's 4 times (the longest hold in one action 360 frames), BOTH HEROES INSIDE THE SAME HOLD 4 times (the longest 660 frames); eh27 75: in sync, 0 fault lines, player 1's hero held 1 times, player 2's 0 times (the longest hold in one action 360 frames); eh28 68: in sync, 0 fault lines, player 1's hero held 8 times, player 2's 9 times (the longest hold in one action 432 frames), BOTH HEROES INSIDE THE SAME HOLD 6 times (the longest 638 frames). |
| `B_EX270_SIDECAR` | BTLNPC | eh22 | eh22 72: SHARED, 0; eh22 90: SHARED, 35 | SWEEP |  |
| `B_EX370` | BOSS | hb34 | hb34 151: OK, 0; hb34 152: OK, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: hb34 151: in sync, 0 fault lines, player 1's hero held 1 times, player 2's 0 times (the longest hold in one action 194 frames); hb34 152: in sync, 0 fault lines, player 1's hero held 10 times, player 2's 0 times (the longest hold in one action 420 frames). |
| `B_EX390` | BOSS | eh21 | eh21 99: OK, 0; eh21 65: OK, 0 | SINGLE | The armoured Xemnas. BUILD 20: BOTH HEROES INSIDE THE SAME HOLD (the moves 0x100 and FD). Seen: candidate v104 (run h4): four pairs; candidate v107 (run h7): 10 pairs, every one ended for both. BUILD 21 (the user's item 4 of 2026-11-15: a single-target attack takes only the targeted player): THE GRAB TAKES ONLY THE HERO IT AIMS AT, the other hero stays free and fights (the ten boss rooms on v122 / v124, runs h10 / h11, and the 40 fights on v128, run rs4: no pair). ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: eh21 99: in sync, 0 fault lines, player 1's hero held 4 times, player 2's 7 times (the longest hold in one action 200 frames). |
| `B_EX400` | BOSS | hb33 | hb33 156: OK, 0; hb33 157: OK, 0; hb33 142: OK, 0; hb33 147: OK, 0; hb33 148: TEST-LIMIT, 0; hb33 155: OK, 0; and 1 more | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: hb33 156: in sync, 0 fault lines, player 1's hero held 1 times, player 2's 2 times (the longest hold in one action 240 frames); hb33 157: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times; hb33 142: in sync, 0 fault lines, player 1's hero held 7 times, player 2's 1 times (the longest hold in one action 316 frames); hb33 147: in sync, 0 fault lines, player 1's hero held 4 times, player 2's 2 times (the longest hold in one action 316 frames); hb33 155: in sync, 0 fault lines, player 1's hero held 2 times, player 2's 0 times (the longest hold in one action 320 frames). |
| `B_EX410` | ZAKO | - | - | NO ROOM |  |
| `B_EX420` | BOSS | dc07 | dc07 73: OK, 0; dc07 67: OK, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: dc07 73: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times; dc07 67: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times. |
| `B_HE020` | L_BOSS | he07, he09 | he07 114: OK, 0; he09 124: OK, 0; he09 125: OK, 0; he09 175: OK-GAME, 19; he09 176: OK-GAME, 19 | SINGLE | Cerberus. READ: a GRAB (the bite: the hero is attached to the boss). BUILD 20: BOTH HEROES INSIDE THE SAME BITE. Seen: candidate v104 (run h4, part 95): a pair from frame 7180 to 7658, the moves FD, FE, FF on both heroes in the same frames, both free within two frames; candidate v107 (run h7): 2 pairs. BUILD 21 (the user's item 4 of 2026-11-15: a single-target attack takes only the targeted player): THE GRAB TAKES ONLY THE HERO IT AIMS AT, the other hero stays free and fights (the ten boss rooms on v122 / v124, runs h10 / h11, and the 40 fights on v128, run rs4: no pair). ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: he07 114: in sync, 0 fault lines, player 1's hero held 7 times, player 2's 1 times (the longest hold in one action 420 frames); he09 124: in sync, 0 fault lines, player 1's hero held 2 times, player 2's 0 times (the longest hold in one action 336 frames). |
| `B_HE100` | L_BOSS | he18 | he18 171: OK, 0 | SINGLE | The Hydra. BUILD 20: BOTH HEROES INSIDE THE SAME HOLD. Seen on candidate v104 (run h4, part 95): three pairs of 94 frames (move FD on both heroes). THE FIFTY-NINTH GLUE (a try of build 18: send a boss's capture to the hero it already holds) made this fight worse; no build uses it. BUILD 21 (the user's item 4 of 2026-11-15: a single-target attack takes only the targeted player): THE GRAB TAKES ONLY THE HERO IT AIMS AT, the other hero stays free and fights (the ten boss rooms on v122 / v124, runs h10 / h11, and the 40 fights on v128, run rs4: no pair). ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: he18 171: in sync, 0 fault lines, player 1's hero held 9 times, player 2's 2 times (the longest hold in one action 118 frames). |
| `B_HE110` | L_BOSS | he18 | he18 171: OK, 0 | PLAYED | In the Hydra's room (see B_HE100). ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: he18 171: in sync, 0 fault lines, player 1's hero held 9 times, player 2's 2 times (the longest hold in one action 118 frames). |
| `B_LK110` | BOSS | lk14 | lk14 55: OK, 0 | SINGLE | Scar. READ: a GRAB (the hero is attached to the boss). BUILD 20: BOTH HEROES INSIDE THE SAME GRAB. Seen: candidate v104 (run h4): a pair of 506 frames, the moves FC, FD, FE on both, both free in the same frame; candidate v107 (run h7): 2 pairs. BUILD 21 (the user's item 4 of 2026-11-15: a single-target attack takes only the targeted player): THE GRAB TAKES ONLY THE HERO IT AIMS AT, the other hero stays free and fights (the ten boss rooms on v122 / v124, runs h10 / h11, and the 40 fights on v128, run rs4: no pair). ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: lk14 55: in sync, 0 fault lines, player 1's hero held 7 times, player 2's 4 times (the longest hold in one action 342 frames). |
| `B_LK120` | BOSS | lk15 | lk15 59: OK, 0 | FIXED | The Groundshaker. READ: its forced moves are RIDES (the hero is attached to the boss). THE FAULT OF BUILDS 12 TO 17 (a hero frozen for the rest of the fight) HAS ITS REAL CAUSE NOW (part 94): the script's attack-hit routine (OBJ_ATTACK -> L4217) captures, with move 254, whichever hero its attack HITS while the ride flag is set: also the hero who stands beside the ride, and nothing ever ends that capture. BUILD 20: a stray capture of a free bystander is not made (shown on a state made on purpose, run gsI: the hero stays free and joins the ride 42 frames later). BOTH HEROES RIDE TOGETHER (run h7: one pair of 996 frames). The nets stay (build 18's one-minute rule; the mirror's 40 steps), both shown on made states (runs gsG, gsH). ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: lk15 59: in sync, 0 fault lines, player 1's hero held 14 times, player 2's 5 times (the longest hold in one action 300 frames). |
| `B_MU100` | BOSS | mu09 | mu09 75: OK, 0; mu09 1: OK, 0 | OK | Shan-Yu. SINCE BUILD 16 BOTH HEROES ARE IN HIS CLASH when the second stands within 500 units: each has "Press" in his own menu, each one's Triangle pushes, the clash's clock is the game's (VERIFIED, runs tg35 to tg39; STATE parts 61 to 66). A hero far away stays free; then the clash takes the one hero, as in builds 13 to 15 (runs gp11 to gp14, cap6, cap7; STATE parts 32, 33, 38). |
| `B_MU110` | BOSS | mu09 | mu09 75: OK, 0; mu09 1: OK, 0 | OK | In Shan-Yu's room (the same fight as B_MU100, see there). |
| `B_MU120` | L_BOSS | mu08 | mu08 104: OK, 0; mu08 74: OK, 0; mu08 81: OK, 0; mu08 79: OK, 0 | PAIR | Storm Rider. Ran with two heroes and two King Mickeys (runs mkS, mkS3): in sync, 0 fault lines. Its paired move was not looked at. ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: mu08 104: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times; mu08 74: in sync, 50 fault lines, player 1's hero held 1 times, player 2's 3 times (the longest hold in one action 182 frames); mu08 81: in sync, 0 fault lines, player 1's hero held 1 times, player 2's 0 times (the longest hold in one action 182 frames); mu08 79: in sync, 0 fault lines, player 1's hero held 6 times, player 2's 5 times (the longest hold in one action 300 frames), BOTH HEROES INSIDE THE SAME HOLD 4 times (the longest 158 frames). |
| `B_NM100` | BOSS | nm03 | nm03 52: OK, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: nm03 52: in sync, 0 fault lines, player 1's hero held 1 times, player 2's 0 times (the longest hold in one action 100 frames). |
| `B_NM110` | BOSS | nm07 | nm07 71: OK, 0; nm07 64: OK, 0; nm07 1: OK, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: nm07 71: in sync, 0 fault lines, player 1's hero held 1 times, player 2's 5 times (the longest hold in one action 92 frames); nm07 64: in sync, 0 fault lines, player 1's hero held 4 times, player 2's 2 times (the longest hold in one action 92 frames). |
| `B_TR000` | BOSS | tr04 | tr04 55: OK, 0; tr04 56: OK, 0 | PLAYED | ON BUILD 21's FILE (v129), PLAYED ON PURPOSE WITH TWO HEROES: tr04 55: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times; tr04 56: in sync, 0 fault lines, player 1's hero held 0 times, player 2's 0 times. |

## 5. Totals

52 boss scripts use a paired move.

- OK: 3 scripts
- PAIR: 3 scripts
- SINGLE: 5 scripts
- FIXED: 5 scripts
- OWN: 3 scripts
- PLAYED: 23 scripts
- SWEEP: 1 scripts
- NO ROOM: 9 scripts

## 6. What is still open for row 9

- Xigbar's sniper part and Luxord's card trick are cured in build 14 in the test runs. Luxord's card game
  itself (does it feel right, can each player win it) cannot be judged by a test script.
- (Closed 2026-11-15 night: Shan-Yu's stray calls. Since build 16 both heroes are in the clash; runs syC / syD on
  v124: 0 captures outside a hero's own clash; the push count goes up once a push, runs syE2 / syG2. STATE part 112.)
- (Closed 2026-11-15: the moves that a hero starts with his own command stay that hero's own: THE USER'S OK.)
- (Seen 2026-11-15 night: the last Xemnas's "Riku frees Sora" part with ONE hero held ends by the held hero's
  player's own command, run rs4 eh20 98. How it feels to steer Riku is for the user's playthrough.)
- The pairs were made by test scripts that press Circle, Triangle and R1 blindly. How a pair looks and feels
  (two heroes in one hand) is for the user's test.
- The Samurai duel by player 2: VERIFIED in build 21's tests (Twilight Town tt19, runs smA / smC / smD: "Duel
  Stance" and "The End" in his own menu, the Samurai cut down; STATE part 114).
- The Large Body's command "Full Swing": NOT MET in a test (he05 in the eighth round; Agrabah al00 in the ninth, four
  runs of 11,000 frames: never offered). UNVERIFIED, for the user's playthrough.
