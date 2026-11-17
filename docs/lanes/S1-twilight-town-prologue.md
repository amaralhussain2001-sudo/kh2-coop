# Lane S1: Twilight Town prologue with two Roxas (feasibility tests)

Task: for every Twilight Town prologue row of the checklist (TTR-01 … TTR-15) run short two-player tests on the
merged build (two player-controlled Roxas) and say for each: does it start, does each player keep direct control,
do counters / timers / scores count player 2, who wins and loses, what a second special object would be, what
breaks. Plus the plain New Game flow on `kh2-coop-v1.iso` as far as scripts get.

Status 2026-11-10: TESTS FINISHED, nothing of this lane is in the merged build. All patches of this lane are
TEST ONLY. Test discs are deleted; recipes and results are kept (section 9).

Evidence labels: **VERIFIED** = seen in a test of this lane (test id given) or read in this disc's data.
**HYPOTHESIS** = reasoned, not tested. All tests ran on ONE PC with scripted buttons, no human played.
"Hero" = player 1's Roxas (the engine's player). "Twin" = player 2's Roxas. Unless said otherwise a test is two
linked emulator copies in a lockstep session; all of them stayed in sync and every screenshot pair was identical.

Decisions this report follows (coordinator): minigames are TEAM PLAY (same side, scores add up, win or lose
together); level and experience shared; normal enemies unchanged, bosses +75 % HP (another lane); each PC shows
its own player's view (other lanes); scripted Reaction Command moves: the target is BOTH heroes in the move.

Effort classes: **E0** nothing beyond the base and the general items below. **E1** small: a data line or a few
instructions, hours to a day. **E2** medium: a new routine or a mission-specific rule with tests, days.
**E3** large: engine behaviour has to be worked out first, a week or more, outcome not certain.

---

## 1. Results by checklist row

Row results judge the row's OWN mechanics. Seven general items (section 2) apply to every row, belong to other
lanes and are not repeated as row results.

| Row | Sequence | Result | Evidence (tests) | A full version needs | Effort |
|---|---|---|---|---|---|
| TTR-01 | First control and tutorials | **Works as is.** Walk step, Talk, lock-on, chest and the Struggle weapon pick-up all react to player 2. NOT REACHED: save-point tutorial (cannot be jumped to). | s1-flow-a1/a2/a3/ctl2, s1-d-talk-p2, s1-c-lock-p2, s1-d-chest-p2, s1-d-pick-p2/p1 | Only the general items: text boxes on either controller (G1), the "both heroes in the trigger" rule (G2). | E0 |
| TTR-02 | Seifer duels | **Works as is.** Pad 2 alone wins three of the four fights; the tutorial fight's hit counter counts the twin's hits. | s1-f-seifer2/3/4, s1-e-seifertut-count, s1-c-seifertut-p2 | General items only (G3: Seifer goes only for the hero). | E0 |
| TTR-03 | Job: Mail Delivery | **Needs real adaptation** (second rider). The hero starts on the board, the twin starts on foot and cannot mount a second board placed for it. | s1-job-mail-p2, s1-job-mail-2boards/-b/-c; free roam: s1-skate-s2, s1-e-board-one | Second board in the mission's group (data, done in the test) + the mission start must put the twin on it + own board menu for player 2. Letters by the twin: not tested. | E2 |
| TTR-04 | Job: Cargo Climb | **Works as is.** The cargo reacts to the twin's hits. NOT FINISHED: the job's end was not reached. | s1-job-cargo-p2mash, -p2, -idle | Nothing known. Time-only job, one shared clock. | E0 |
| TTR-05 | Job: Grandstander | **Needs real adaptation** (ball rule). After the twin's hits the ball is gone from its place, 0 HIT is counted, REST stays 5/5 and the job stalls. With pad 1: 8 HIT, REST runs down, job ends. | s1-job-grand-near, -p2mash, -p2few, -track, -p2 | The ball must treat a hit by the twin like a hit by the hero (count it, keep the juggle going). The place is not located yet. | E2 |
| TTR-06 | Job: Poster Duty | **Works as is.** Pad 2's Triangle puts up a poster, the one counter shows 1/20. | s1-job-poster-p2rc | Player 2 needs to see the "Post" prompt (G5). | E0 |
| TTR-07 | Job: Bumble-Buster | **Works as is.** Bees die to pad 2 alone. NOT FINISHED: end not reached. | s1-job-bees-p2 | Nothing known. | E0 |
| TTR-08 | Job: Junk Sweep | **Works as is** for the counter: the one swing counter counts the twin's swings (12 → 26). NOT FINISHED: no junk was broken by the twin in the test (random walking). | s1-job-junk-p2 | Team rule = both players' swings in one count: already so. | E0 |
| TTR-09 | Struggle tournament | **Works as is** for the score: one orb count per side; orbs knocked out and picked up by the twin go to the heroes' count. NOT TESTED: whether the twin loses orbs when hit (opponents never attack it today, G3). | s1-tt84-p2only | After lane H: check that a hit on the twin spills the team's orbs; if not, a small rule patch. | E0 (E1 if the check fails) |
| TTR-10 | Nobody fights | **Works with a small change** (hit counter). Five fights are won by pad 2 alone. In the two "cannot be damaged" fights the hit counter does not count the twin's hits (stays 1 in 7,000 frames; with pad 1 it reaches 10 and the story goes on). | s1-f-alley, -sandlot-nob, -basement, -dusk-old2, -serenity; s1-f-dusk-old1, s1-f-sandlot-myst, s1-c-dusk1-p1, s1-c-myst-p1 | The hit counter of TT14_MS109 and TT04_MS301 must also count the twin's hits (place not located). Not blocking: player 1 can always do it. | E1 (HYPOTHESIS for the size) |
| TTR-11 | Axel, twice | **Works as is.** Pad 2 alone wins both (100 → 9 → scene; 300 → 0). The twin holds two Keyblades in the second fight (one enlarged picture). | s1-f-axel1, s1-f-axel2 | General items; the "Burst Frontier" prompt is shown to player 1 only (section 3). The boss bonus went to the hero only (G6). | E0 |
| TTR-12 | Seven Wonders: wall balls, Vivis, Shadow Roxas | **Works as is** for two of three: Shadow Roxas beaten by pad 2 alone, the Vivi copies beaten with both pads and the closing scene plays. NOT FINISHED: wall balls (both heroes walked up the alley, nothing ended; reason not found). | s1-f-mirror, s1-e-vivis-both, s1-f-vivis, s1-c-balls-p1up/-bothup, s1-f-balls | Wall balls: find the end condition (probably a trigger at the wall, then G2 applies). | E0 (wall balls open) |
| TTR-13 | Seven Wonders: the moving bag | **Needs real adaptation** (second rider). Only the hero gets on the bag: with pad 1 the gauge falls 100 → 20 → 0 and the scene plays; with pad 2 and the same buttons the gauge stays 100 for 5,000 and 7,000 frames. | s1-c-bag-p1, s1-c-bag-p2, s1-f-bag | The ride is a scripted Reaction Command move: see section 3 (both heroes in a move). | E2-E3 |
| TTR-14 | Station of Serenity fight | **Works as is.** Three Dusks die to pad 2 alone; the chest opens for pad 2. | s1-f-serenity, s1-d-chest-p2, s1-c-myst-p1 | General items only. | E0 |
| TTR-15 | Twilight Thorn | **Needs real adaptation** (scripted moves). The fight runs, both heroes damage the boss (300 → 161 with both pads), but every scripted move takes only the engine's player and its three prompts go only to that hero. One game crash seen under a test-only condition (section 3.6). | s1-g-thorn-none/-p1/-p2/-both/-redir/-redir-tri, s1-c-thorn-*, s1-f-thorn, s1-r-thorn-* | Section 3: second hero in the move, prompts for both, camera per player. | E3 |

**Counts: works as is 10 · works with a small change 1 · needs real adaptation 4 · blocked 0.**
Parts not reached or not finished inside those rows: save tutorial (TTR-01), end of Cargo Climb / Bumble-Buster /
Junk Sweep (TTR-04/07/08), orb loss of the twin (TTR-09), wall balls (TTR-12), Roxas's equipment across the days
and the rest of the New Game flow after the first shop scene (section 5).

---

## 2. General items (seen in these rows, owned by other lanes)

| # | Item | Evidence | Label |
|---|---|---|---|
| G1 | **Rules screens, tutorial boxes, dialogue and result screens advance only on controller 1.** A two-player run with player 1 idle stops at the first box. Player 2 can OPEN a dialogue (Talk, Pick It Up, chest) but cannot close it. | s1-tt84-p2only first run (4,000 frames on the Struggle rules screen), s1-f-seifer-tut, s1-f-tut-talk, s1-f-tut-lock, s1-f-chest, s1-d-pick-p2, s1-d-talk-p2 | VERIFIED |
| G2 | **Tutorial / event triggers need BOTH heroes inside** (lane E's rule). At the Armor Shop the hero alone waited 900+ frames; the box appeared when the twin arrived. On the plain disc a lone Roxas triggers it at once. | s1-flow-a1, s1-flow-a2, s1-flow-a3, s1-flow-ctl2 | VERIFIED |
| G3 | Opponents and enemies go only for the hero (lane H). Area attacks DO hit the twin (Twilight Thorn: twin thrown, action 0x12/0x13). | all fights; s1-g-thorn-none | VERIFIED |
| G4 | **HP is one number for both heroes in this build.** In every sample of the Thorn runs both HP values fell in step (20→19→18→17→14→11→8), also for a twin standing 880 units away from the hit. Either hero at 0 = Game Over (seen once, lane N). | s1-g-thorn-none/-p2, s1-r-thorn-rep-nohold | VERIFIED |
| G5 | The command menu, Reaction Command prompt, skateboard menu and mission meters are drawn for player 1 only; the camera follows the hero and the twin walks out of the picture. With own screens each PC needs its own set. | every picture | VERIFIED |
| G6 | **The boss bonus went to the hero only**: after Axel II the hero has 20/25 HP, the twin 20/20. For the "shared level" lane. | s1-f-axel2 frame 11900 | VERIFIED |
| G7 | Cut-scenes show one Roxas. After a scene both heroes are back (alley, Vivis, Station of Serenity). | s1-f-alley, s1-e-vivis-both, s1-c-myst-p1 | VERIFIED |

Fixed or special cameras met in the prologue (for the own-screen lanes): the Struggle match camera (frames the
hero and the opponent); the skateboard camera (behind the hero's board); the bag ride; every Twilight Thorn
scripted move (close-ups and fly-bys of the carried hero, section 3.4); the tutorial lock-on step (camera turns
to the cat); intro pans of every job and fight ("READY / GO").

Timed prologue fights where +75 % boss HP matters: only the three Struggle matches have a clock and they are
decided by orbs, not by the opponent's HP (Hayner 200 HP, he never reached 0 in the test), so the extra HP changes
nothing there. Seifer, Axel and Twilight Thorn have no clock. Bumble-Buster has a count-up clock but bees are
normal enemies.

---

## 3. Twilight Thorn and the other Reaction Commands

Tests: six runs of the fight's first 4,400 frames with a dense read-only probe (about 3 samples per frame:
both heroes' action number, position, HP, each control object's Reaction Command bytes, the engine's "player"
and camera pointers, object dumps at every action change). Tool: `tools\lane-s1\s1rc.py`, timeline
`s1rcsum.py`, pointer search `s1rcdump.py`. Frame numbers are good to about 10 frames.
Control objects (lane G): S = player 1's, S2 = player 2's; each has its own Reaction Command slot
(+0xA1E command number, +0xA21 state: 0 = usable, 5 = none, 8 = being performed).

### 3.1 The scripted sequence (nobody presses: s1-g-thorn-none)

| Frame | Hero (engine's player) | Twin | Offered |
|---|---|---|---|
| 4600 | free at (0,0,-860) | free at (110,0,-860) | - |
| 5041 | action 0xFD, pulled to (0,0,0), lifted to height 700 | untouched, free | - |
| 5466 | action 0x103 (held) | free | - |
| 5706-5745 | held | free | **0x29 to S only** (first prompt, "Key Counter" by its place in the fight) |
| 5749-5820 | HP 20 → 17 (prompt missed) | HP shows the same numbers (G4) | - |
| 6060 / 6230 | 0xFF, then 0x104 | free | - |
| 6449-6490 | held | free | **0x2A to S only** (second prompt) |
| 6496 | HP → 14, at 6790 dropped at (0,0,1159), free at 6817 | pushed about 200 units, free | - |
| 7393 | action 0x101, pulled to the centre, thrown to (669,-2543,968) | free | - |
| 7997-8098 | in the air | free | **0x2B to S only** (third prompt) |
| 8382 / 8609 | HP → 11, free | free | - |
| 8652 | thrown by an area attack (0x10) | **thrown too (0x12), HP → 8** | - |
| 8697-8774 | in the air | in the air | **0x59 to S and to S2** ("Use Reversal to dodge attacks!" appears now) |

### 3.2 Who answers a prompt, and who performs the move

| Test | Buttons | What happened | Label |
|---|---|---|---|
| s1-g-thorn-p1 | pad 1 Triangle only | 0x29 at f5708 → hero action 0xFE six frames later, boss 300 → 294. 0x2A at f6242 → hero 0x100, boss → 288. 0x2B at f7675 → hero 0x102, boss → 268. No HP lost. Twin idle and untouched all the time. | VERIFIED |
| s1-g-thorn-p2 | pad 2 Triangle only | 0x29 / 0x2A / 0x2B are offered to S only and **pad 2 does not answer them**: the hero loses HP exactly as with nobody pressing. At f8681 0x59 is offered to S2 → **the twin performs it itself** (action 0xFC, S2 state 8, moves 600 units through the air and lands). The hero, offered 0x59 at the same time, does nothing (pad 1 idle). | VERIFIED |
| s1-g-thorn-both | both pads Triangle | Same as pad 1 only for the three scripted moves (hero performs, twin stays free). | VERIFIED |
| s1-c-thorn-p2 (earlier) | pad 2 Triangle + Circle | While the hero is held the twin walks and attacks: boss 300 → 278 by the twin alone. So the hero outside the move is **not frozen and not hit during the holds**. | VERIFIED |

Rule read from this: **a prompt belongs to one control object; only that hero's controller answers it; that hero
performs it.** "Reversal" (0x59) is handed out per hero (each hero that is thrown gets its own) and works for
player 2 today. The three scripted Thorn prompts are handed only to the hero the boss is holding.

### 3.3 How the scripted move takes hold of the hero

**It takes the engine's player, not the hero who pressed.** The opening grab happens with no button at all and
always takes the hero. One-copy test with a test write (lane M's trick: keep the twin's address in the engine's
two "player" pointers 0x0034E948 and 0x00352400):

| Test | Result | Label |
|---|---|---|
| s1-g-thorn-redir (one copy, pad 1 idle) | **The whole sequence takes the twin instead**: twin 0x103 at height 700, 0x104, 0x101, thrown to the same point (669,-2543,968); 0x29 / 0x2A / 0x2B are offered to **S2**; same frames and same HP losses as the hero in 3.1. The hero stays free on the floor and is later thrown by the area attack. | VERIFIED |
| s1-g-thorn-redir-tri (one copy, pad 1 Triangle) | Pad 1 does not answer the twin's three prompts (same HP losses). Pad 1 does answer the hero's own Reversal (hero action 0xFC, S state 8). | VERIFIED |

So the move uses the global "player" pointer at the moment each step starts, and the twin's object can be carried
through the complete sequence: same action numbers, same positions, prompts in its own control object.

Pointers found in the dumps (names are HYPOTHESIS, offsets VERIFIED in s1-g-thorn-p1 and -redir):
the carried hero holds the boss's address at **+0x23C** (from the grab on) and **+0x570** (while held), and they
are cleared when it is released; the boss holds the carried hero's address at **+0xAE4 / +0xAEC** after the first
performed command, and the hero's address at +0x9F4 all the time (also when the twin is carried).
The positions are absolute points of the arena ((0,0,0), height 700, (669,-2543,968)), not offsets from where the
hero stood.

### 3.4 Camera

The camera target pointer (0x00348754) was player 1's hero in every sample of every run, also while the twin was
the one carried. The move's own scripted cameras (close-up of the bound Roxas, the fly-by in the air, the energy
ball) still play and **show the carried Roxas**, whoever it is (pictures of s1-g-thorn-redir, frames 5600-6000 and
7600-8000); between the moves the picture returns to the hero. With own screens: the player whose hero is carried
needs these cameras; the other player needs an ordinary camera on a hero that is free during that time.

### 3.5 Can both heroes be in the move at the same moment? (the user's target)

- NOT TESTED directly: no test put both heroes into one move at once. That needs code, not a memory write.
- For it: the twin can be the carried hero with everything working (3.3), so its object, animations and control
  object are fit for the move. Reversal already works for each hero on its own.
- Against "for free": the boss's sequence is written for ONE hero. It keeps single pointers to it, it sends the
  hero to fixed points, the three prompts are given to one control object, and one result (performed or missed)
  drives the boss's next step.
- What "both together" needs (HYPOTHESIS, in this order):
  1. At each step where the boss puts "the player" into a scripted action (0xFD, 0x103, 0xFF, 0x104, 0x101),
     do the same for the second hero, at the same point plus a side offset (the two would stand inside each other
     otherwise). The routine that sets the action is not located; the places to look are the users of
     0x0034E948 in the boss's script commands (lane G lists 15 script-command places that reach "the player").
  2. Offer each prompt to S and S2 at the same time (today: only the held hero's control object).
  3. Per hero: pressed in time → that hero plays the answer (0xFE, 0x100, 0x102); not pressed → that hero takes
     the miss. Decide whether the boss takes the damage once or once per hero.
  4. The boss's next step waits for one result: feed it "performed" if at least one hero performed.
  5. Cameras per player (3.4) and the prompt on player 2's screen (G5).
- The working rule "only one presses in time → that hero performs, the other keeps playing freely" does not fit
  the Thorn's first three moves as they are: both heroes would already be held when the prompt appears. For these
  the natural rule is: both are held, each answers for himself.
- Fallback that needs far less: keep one hero in the move, but choose which (for example alternate, or the one
  nearer the boss) by setting the two "player" pointers before the grab. The redirect test shows this works for
  the whole sequence. It is not the target ("player 1 only" is then gone, but it is still one hero at a time).
- **Judgment: feasible, E3.** Nothing found says two heroes in the move is impossible; the open risk is the
  boss script's single-hero bookkeeping, which nobody has read yet.

### 3.6 The crash seen in this fight

- With player 1 idle, pad 2 pressing Circle every 10 frames and the TEST-ONLY patch that holds both heroes' HP
  at 20, the game crashed at about frame 11,234, three times out of three, identical in both copies
  (s1-f-thorn, s1-r-thorn-rep, s1-r-thorn-last). Log: the stack pointer holds a number (0x41AFAFA4) when
  routine 0x0013E2D8 is entered, then "Jump to unmapped recLUT page (PC 0x3A9E1694)". Logs:
  `local\analysis\lane-s1\thorn-crash-rep-emulog-p1.txt` / `-p2.txt`.
- The same buttons WITHOUT the HP hold end in a normal Game Over between frames 9,500 and 10,500
  (s1-r-thorn-rep-nohold), so in the crashing runs the heroes were kept alive past a lethal hit for about
  1,000 frames; just before the crash both were being hit by the lightning at the platform's edge.
  (The log copy of the first run was overwritten; the two repeats' logs are kept, also in
  `local\tests\s1-r-thorn-last\emulog_p1.txt`.)
- No crash in three other two-Roxas runs with the HP hold to frame 12,000 (s1-c-thorn-both, -p2, -twin-idle)
  nor in the one-Roxas control (s1-c-thorn-solo-idle), nor in the six runs of this section without the hold
  (to frame 9,000).
- Reading: most likely an effect of the test's HP hold, NOT shown to be a fault of the two-player build
  (HYPOTHESIS). To settle it: repeat a long two-player fight once lane N's "down" state exists.

### 3.7 The other prologue Reaction Commands

| Command | Where | With two heroes | Label |
|---|---|---|---|
| Talk, Open (chest), Post (poster), Pick It Up (Struggle weapon) | tutorials, Poster Duty | Each hero has its own; the twin's Triangle works on the thing next to the twin. Player 2 has no prompt on screen (G5); the dialogue that opens needs controller 1 (G1). | VERIFIED (s1-d-talk-p2, s1-d-chest-p2, s1-job-poster-p2rc, s1-d-pick-p2) |
| Pick It Up, detail | Sandlot, TT04_MS106 | Pad 2's Triangle opened "The weapon on the right's not bad." (twin stood beside that weapon). In the same spot pad 1's Triangle did nothing in 110 presses although "Pick It Up" was shown, dim. HYPOTHESIS: the hero's start place is just outside the range and the prompt is shown dim; not a fault. To check by walking one step. | VERIFIED facts, cause open |
| Hop On (skateboard) | free roam | Own per hero, works for the twin on its own board (section 4). Not in the Mail Delivery mission. | VERIFIED |
| Save | save point | NOT REACHED here. Lane G: player 2 can open the save menu, only player 1 can use it. | lane G |
| Reversal (0x59) | Dusks, Twilight Thorn | Own per hero; the twin performed it with pad 2 in the Thorn fight. On Dusks the prompt was seen for player 1; the twin's use there was not tested (Dusks never attack the twin, G3). | VERIFIED for the Thorn |
| "Burst Frontier" | Axel II | Prompt seen for player 1. Not tested with pad 2. | open |
| Jump on the bag | Sunset Hill | Only the hero rode (TTR-13). Whether the prompt is offered to S2 was not sampled. | VERIFIED result, cause open |
| Key Counter / second / third prompt (0x29, 0x2A, 0x2B) | Twilight Thorn | Offered only to the held hero (3.1-3.3). | VERIFIED |

---

## 4. Details per row

**TTR-01 tutorials.** Both players have direct control from the first frame of control (two Roxas, New Game on
`kh2-coop-v1.iso`, s1-flow-*). "Approach the Armor Shop": needs both heroes in the trigger (G2), then the box,
then the shop scene after pad 1's Circle. Lock-on: with pad 1 idle since frame 5300, pad 2's R1 at 5600 brought
the next box "Locking on is useful…" (s1-c-lock-p2). Chest: pad 2's Triangle opened it, "Items command has been
added" followed (s1-d-chest-p2). Talk: pad 1 never pressed Triangle; after pad 2's Triangle presses began a
dialogue "The best way to get info is to ask!…" opened and waited for controller 1 (s1-d-talk-p2); which shop
owner spoke, and so whether the step itself was completed by player 2, was not determined. Weapon pick-up: see
3.7. The choice is one for both (shared stats). Save tutorial: tt02 program 0x02 is below 51 and cannot be
reached by a jump disc.

**TTR-02 Seifer.** TT04_MS108: Seifer 60 → 2 → scene with only pad 2 attacking (s1-f-seifer2). TT03_MS400:
100 → 58 → next program with both heroes present (s1-f-seifer3). TT04_MS500: 100 → 0 (s1-f-seifer4). Tutorial
fight TT04_MS107: hero standing still, twin attacking: counter 0 → 2 → 3, Seifer 60 → 49, then the next tutorial
box (s1-e-seifertut-count): **this counter counts the twin**. Seifer attacks only the hero (G3). No clock.

**TTR-03 Mail Delivery.** Starts with both. The hero is on the board at once (action 0xFC; menu Heelflip /
Get Off (dim) / Jump; 0/5 LETTER; clock). The twin stands on foot beside him and can walk and jump
(s1-job-mail-p2). A second board (object 0x05AB) added to the mission's group b_40 beside the twin is there but
pad 2's Triangle does not mount it, in three tries, the last from 47 units (s1-job-mail-2boards, -b, -c).
HYPOTHESIS: the mission mounts the engine's player by script and switches Hop On / Get Off off ("Get Off" is dim
for the hero too). Letters handed over by the twin and the sum in the counter: not tested (the twin cannot keep
up on foot). Full version: mount the twin at mission start the way the hero is mounted (the place is not
located), second board by data, letter count is one counter already.

**TTR-04 Cargo Climb.** Count-up clock only. With only pad 2 attacking: hit sparks on the cargo, the cargo moves,
the idle hero is pushed 470 units by it (s1-job-cargo-p2mash; control with nobody acting: nothing moves,
s1-job-cargo-idle). The top of the hill was not reached in 5,000 frames of unsteered attacks.

**TTR-05 Grandstander.** Pad 1 only: "8 HIT, MAX HIT 5", REST 5 → 0, result screen (s1-job-grand-p2). Pad 2
only, twin placed 60 units from the ball: after its swings the ball is gone from the picture (frame 5100 on),
the counter stays 0 HIT and REST 5/5 to the end of the run, 2,400 frames (s1-job-grand-near; same counters in
-p2mash, -p2few). So the twin's hit moves the ball without the game's bookkeeping, and the job hangs. Team play
needs: the twin's hit counted in the same HIT / MAX HIT counter and handled as a juggle hit; not known yet
whether that is one owner check or more.

**TTR-06 Poster Duty.** Twin placed at a poster spot, pad 1 idle: pad 2's Triangle posts, the counter reads 1/20
(s1-job-poster-p2rc). One counter, one clock: the sum is already what is shown.

**TTR-07 Bumble-Buster.** Three bee groups [7/7 2/7 7/7] → [7/7] with only pad 2 (random buttons) in 4,500
frames (s1-job-bees-p2). Count-up clock. Bees attack only the hero (G3).

**TTR-08 Junk Sweep.** Swing counter 12 → 13 → 18 → 26 with only pad 2 swinging; junk left stayed 9
(s1-job-junk-p2, random walking, so no junk was near). Fewer swings is better, so "scores add up" = both
players' swings in the one counter, which is what happens.

**TTR-09 Struggle.** Rules screen needs pad 1 (G1). Match Hayner: 100/100 orbs at start. With pad 1 idle and
pad 2 on random buttons: heroes' count 101 → 110 while Hayner's falls 94 → 83 (the twin's hits knock orbs out
and the twin picks them up; the hero stands 850 units away), Hayner's HP 200 → 173. Then Hayner beats the idle
hero: 74/106, 38/153, 0/193; lost on time; the story moved on (s1-tt84-p2only). So the team count exists and
counts player 2. Open: orb loss when the twin is hit. Vivi and Setzer matches use the same program type; not run.

**TTR-10 Nobody fights.** Alley TT03_MS601: two Dusks killed by pad 2, scene, free roam with both
(s1-f-alley). Sandlot TT05_MS403: three Dusks, scene (s1-f-sandlot-nob). Mansion basement TT19_MS602: four,
scene (s1-f-basement). Old Mansion TT14_MS110 (after the Keyblade appears): Dusk 4/32 → dead by the twin, so the
twin's weapon works there (s1-f-dusk-old2). The two fights where the enemy cannot be damaged (TT14_MS109, bat;
TT04_MS301): the twin swings at the Dusk with hit sparks, the hit counter stays 1 for 7,000 frames, the enemy
stays 32/32 (s1-f-dusk-old1, s1-f-sandlot-myst); with pad 1 attacking the counter reaches 10 within 1,500 frames
and the story continues, through to the Station of Serenity with both heroes (s1-c-dusk1-p1, s1-c-myst-p1).
Note the difference to Seifer's tutorial counter, which does count the twin: there the enemy takes damage.

**TTR-11 Axel.** First fight 100 → 9 → scene, second (burning floor) 300 → 0, both with only pad 2 attacking
(s1-f-axel1, s1-f-axel2). The hero has two Keyblades; the enlarged picture of frame 4800 shows a dark blade in
the twin's right hand and a pale one in its left (`local\analysis\lane-s1\axel2-twin-crop.png`; small picture,
to confirm by eye). After the win the hero's HP is 20/25, the twin's 20/20 (G6). Whether the fire floor hurts
the twin could not be seen (HP was held in these runs).

**TTR-12 Seven Wonders.** Shadow Roxas 100 → 36 → scene with only pad 2 (s1-f-mirror). Vivi copies: with only
pad 2 none died in the window (the twin wandered off, s1-f-vivis); with both pads three copies → 0, closing
scene, both heroes back (s1-e-vivis-both). Wall balls: fight starts, both heroes were walked up the alley to
about (1290,-1868,1803) and stopped there; nothing ended (s1-c-balls-p1up, -bothup). Not determined why.

**TTR-13 the bag.** Gauge 100.0. Pad 1 Triangle + Circle: hero on the bag (action 0xFE) by frame 8500, gauge
20.4, then 0 and the scene "Oh, it was just a dog." (s1-c-bag-p1). Pad 2 with the same buttons, reaching the
same spot (81,-3500,-1380): never on the bag, gauge 100 to the end (s1-c-bag-p2, s1-f-bag). Whether the twin was
in range at the right moment is not certain; the result fits the Thorn finding (the ride goes to the engine's
player).

**TTR-14 Station of Serenity.** Three Dusks [25 18 22 of 32] → 0 with only pad 2 (s1-f-serenity). Chest: TTR-01.

**TTR-15 Twilight Thorn.** Section 3. Further: with both pads on Triangle + Circle the boss went 300 → 161 in
7,000 frames and two helper enemies (20 HP) appeared (s1-c-thorn-both). No clock.

---

## 5. The skateboard (second special object)

| Fact | Evidence | Label |
|---|---|---|
| The board is its own object: F_TT010 = 0x05AB (Roxas), F_TT010_SORA = 0x081A, world variants 0x08C0-0x08C5. | object list, room data | VERIFIED |
| In free roam the boards are placed by the room's map programs, one per entrance: tt06 / tt07 groups m_96, m_97 (Roxas boards) and m_94, m_95 (Sora boards). In Mail Delivery the board is in the mission group (tt06 b_40, at (33,-700,3206) beside the player's place). | room data | VERIFIED |
| **Two heroes can each ride their own board in free roam.** Two Sora boards placed by room data, two Soras: each hops on with his own Triangle; the hero rode about 2,200 units on pad 1 while the twin stood on its board, then the twin rode on pad 2; in sync. | s1-skate-s2 | VERIFIED |
| With ONE board only one rides: the hero got it; the twin's Triangle (once before, twice after) did nothing; the hero rode away. | s1-e-board-one | VERIFIED (whether the twin was in range for its first press is not certain) |
| The board must match the hero: Roxas's board under a Sora froze both in action 0xFC. | s1-skate-one, s1-skate-two | VERIFIED |
| The board menu (Heelflip / Get Off / Jump) is drawn for player 1 only. | pictures | VERIFIED |
| Roxas on Roxas boards in FREE ROAM with a twin: not tested (a jump on a fresh save gives Sora). In the mission the hero rides it normally. | - | HYPOTHESIS: same as Sora |
| In the Mail Delivery mission the second board is not mountable (TTR-03). | s1-job-mail-2boards* | VERIFIED |

A full version needs: one extra board per place where one stands (data, by the room tool: `Kh2Tool ard-add`,
recipes in `local\variants\s1-skate-src` and `s1-mail-src`), the mission mount for the twin, the board menu on
player 2's screen.

---

## 6. Plain New Game flow (`kh2-coop-v1.iso`, merged patch, two copies)

| Step | Result | Test |
|---|---|---|
| New Game, opening scenes skipped with START → Skip (controller 1) | reaches first control at about frame 6,200 | s1-flow-cal |
| First control, Market Street | two Roxas, each on his own controller | s1-flow-a1 |
| "Approach the Armor Shop" | hero alone in the trigger: nothing for 900+ frames; twin arrives: info box; pad 1's Circle: shop scene plays | s1-flow-a1, -a2, -a3 |
| Same on the plain English disc, one Roxas | box appears as soon as he arrives | s1-flow-ctl2 |
| Everything after the first shop scene | NOT REACHED by scripts in the flow. The later steps were tested through jump discs instead (rows above). | - |

---

## 7. What a later lane must know

1. Counters fall into two kinds. Driven by the OBJECT that is hit or used, they already count player 2: Struggle
   orbs, posters, junk swings, kills, Seifer's tutorial hits, the cargo. Driven by "the player's" own action,
   they do not: Grandstander's HIT, the two cannot-be-damaged fights, and every ride (board in the mission, bag,
   Thorn moves).
2. A scripted move takes the engine's "player" pointer (0x0034E948 / 0x00352400) at the moment it starts; the
   twin can be carried if it is the one pointed at (section 3.3).
3. Reaction Commands are per control object; each controller answers only its own.
4. HP is still one number for both heroes in merged-v2 (G4); a test that holds HP must hold both slots
   (twin 0x01C6C750, hero 0x01C6C4E8 on these discs). Holding HP past a lethal hit crashed one fight (3.6).
5. Action numbers 0xFC-0x107 are scripted-motion slots whose meaning depends on the scene (0xFC = standing on a
   board in town, = Reversal move in the Thorn fight).
6. Mission meters used here: counters at 0x01D48EFC + 0x38·k (first word), gauges at 0x01D48FA4 + 0x34·k
   (float), clock word at 0x00349DF8.
7. A jump into a prologue mission gives two Roxas; a free-roam jump on a fresh save gives two Soras.
8. The session log's time stamps run about 6.9 s ahead of the Windows tick count (s1rcsum.py corrects it).

## 8. What remains

- Mount the twin in Mail Delivery; find the Grandstander ball rule and the hit-counter rule (TTR-03, 05, 10).
- Both heroes in a scripted move: read the Thorn's script for the place that sets the player's action (3.5).
- Bag: sample S2's prompt at the bag; then the same work as the Thorn.
- After lane H: orb loss of the twin in the Struggle; Reversal by the twin on Dusks; fire floor on the twin.
- After lane N: a long Thorn fight without any HP hold, to settle the crash (3.6).
- Wall balls end condition; ends of Cargo Climb, Bumble-Buster and Junk Sweep with real play.
- Pick It Up with player 1 after one step forward; "Burst Frontier" with pad 2; save tutorial; Struggle matches
  against Vivi and Setzer; Roxas's equipment across the days; the New Game flow beyond the first shop scene.
- Everything here is scripted buttons on one PC; no human has played these rows.

## 9. What is on disk

- Tools: `tools\lane-s1\` (build_disc.py, run_s1.py, batch.py, s1probe.py, s1sum.py, s1track.py, s1rc.py,
  s1rcsum.py, s1rcdump.py, make_god.py, copies of pine.py / mprobe.py, `mods\`, `data\overrides_*.csv`).
- Test-only patches: `patches\lane-s1-god`, `lane-s1-god-hero`, `lane-s1-hp-solo`. Never for the game patch.
- Results: 77 folders `local\tests\s1-*` (pictures, contact sheets, probe.txt, rc.csv, saved emulator logs from
  the later runs), scripts in `tests\scripts\lane-s1\`.
- Recipes: 44 folders `local\variants\s1-*` (every disc can be rebuilt in about 17 s with build_disc.py).
- Work files: `local\analysis\lane-s1\` (batch files and their result lines, all-summaries.txt, crash logs,
  the 15 checklist rows, the mission list).
- Emulator copies `local\run-s1`, `run-s1b`, `run-s1c` (not running).
- Deleted: all `local\iso\test-s1-*.iso`. The code cave 0x000F4000-0x000F4FFF was not used.

Jump numbers (world TT): Struggle 84; jobs Cargo 89, Grandstander 90, Mail 91, Junk 100, Bees 101, Poster 102;
Seifer 77 (tutorial), 78, 180, 181; Nobodies 73, 86, 79, 127, 128, 134, 154; Axel 87, 137; wall balls 120,
Shadow Roxas 121, Vivis 159, bag 125; Twilight Thorn 157; chest 155; tutorials 95, 97, 99; weapon choice 76.
