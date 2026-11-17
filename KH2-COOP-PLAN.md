# Kingdom Hearts II Final Mix: two players on PS2-ONLINE

Plan written 2026-11-10, revised the same day (P2 is now a twin of P1's character).
Status: **Phase 0 in progress since 2026-11-10** (current state: `docs/STATE.md`). The original disc file, the BIOS
and the Desktop package are unchanged; all work is in this folder's `local\` sandbox.

## 1. What is decided

- PS2 version, played through `Desktop\PS2-ONLINE` (lockstep: only button presses travel).
- Screen (revised 2026-11-10 after the user asked what is best overall): **the aim is an own screen for each
  player** (each PC shows a full picture from its own player's camera; both characters in the same room; still only
  buttons travel). The shared screen (same picture on both PCs, one camera) is built first as the base and stays
  as the fallback. Own screens are committed only after a camera test that the user sees and approves.
- The Warriors project is not used.
- The rule for the whole project: **in every phase, player 2 (P2) is a real player with a soul, as if the game
  had been made for two. Never a shadow that only follows Sora.**
- **P2 is a twin of whatever P1 is** (user's idea): P1 is Sora, P2 is a Sora. P1 is Roxas, P2 is a Roxas. P1 is the
  lion, P2 is a lion. Donald and Goofy stay in the party as they are (AI). Munny and items are shared.
- Picture rate (decided by the user 2026-11-10): the game stays at its original 30 pictures per second in play.
  The game's own settings have no 60 option; the 60 patch from the emulator's collection is not used.
- **P2 is equal to P1, exactly** (user, 2026-11-10): the same skills, the same moves, and enemies and bosses target
  P2 the same way they target P1. The parity list in section 5 is how this is checked.

### Decisions of 2026-11-10 (evening): "do everything as your recommendations, except bosses get 75 % more HP"

| # | Topic | Decided |
|---|---|---|
| 1 | Screens | **Own screens** (Phase 2B is now committed): each PC shows its own player's camera and its own HUD; both heroes in the same room; original 30 pictures per second; only buttons travel. First joined build 2026-11-10 evening: `patches\merged-v6-own` + emulator build `view12` (test package build 3); state in `docs\STATE.md`. |
| 2 | Level and experience | Shared: both heroes are always equally strong. HP and MP stay separate. |
| 3 | Player 2's Keyblade and skills | Same as player 1's for now; own choices later (Phase 4). **Replaced by row 39 (2026-11-13).** |
| 4 | Telling the heroes apart | No sign over the heroes' heads (changed by the user 2026-11-10 evening: "I can see which one is 1P and 2P without the icon"). A marker on a map would be fine. Taken out in merged build 4. |
| 5 | Drive Forms | Both heroes can use any form, like player 1, if the game allows it (feasibility test first). |
| 6 | Minigames built for one | Team play: scores and counters add up, win or lose together. |
| 7 | Difficulty | Normal enemies as in the original. **Bosses get 75 % more HP when there are two players.** Decided 2026-11-10 evening: every boss gets the full +75 % (the enemy HP gauge is patched to show more than 3400 HP); Pete in the Underworld cave gets +40 % (90 s limit). In merged build 4. |
| 8 | First test with the friend | After the current round (enemies target both, down like Goofy, exits fixed), on the shared screen. Changed 2026-11-10 evening: the user noticed "the camera shows the main person in both clients", so the test package now holds the OWN-SCREEN build; the shared-screen build is in it as a fallback file. |
| 9 | Reaction Commands that carry the hero through a scripted move (mostly bosses) | **Both heroes do the move together** ("try to do B so both must have same experience"). Working rule: both players see the prompt; if both press in time both heroes perform it; if only one presses, that hero performs it and the other keeps playing. "Whoever presses does it alone" is the fallback only where two heroes in the move is proven impossible, reported to the user per fight. **STATUS 2026-11-14 (test build 13): the first half is built.** A boss's paired move takes the hero it holds or the nearer one, and its green command is in THAT player's menu only; seen in Shan-Yu's clash, player 2 alone wins it. The same code serves all 52 boss scripts with paired moves; only Shan-Yu and the Twilight Thorn were looked at. "Both heroes in the move together" is NOT BUILT YET (corrected 2026-11-14 after the user asked: this is NOT a final decision; his decision of 2026-11-10 stands, "try both together, one hero alone only where two is proven impossible, per fight"; it is an open job, fight by fight). My reasons of risk for not building it in the eighth round: the move has one victim's place, and a second victim would spread the "held for ever" fault of Xigbar and Luxord. **BUILD 14:** a boss's green command is taken by ONE hero: the hero who presses is "the player" of the boss's script for that move, and a boss that holds one hero does not take the other hero's press. That cures Xigbar's sniper part (it never ended when both pressed) and Luxord's card trick (a hero stayed held for the whole fight). THE PER-FIGHT REPORT with the reasons: docs\ROW9-PAIRED-MOVES.md (evidence: docs\STATE.md, Eighth round, parts 32, 33, 40, 45 to 50). **STATUS 2026-11-14, later (test build 16): THE SECOND HALF IS BUILT AND VERIFIED FOR THE FIRST FIGHT, SHAN-YU'S CLASH.** When the boss's script hooks its clash onto one hero and the other hero is up, free and within 500 units, the other hero is put beside him, gets his own copy of the hooked script, has "Press" and "Takedown" in his own menu, and his own Triangle pushes; one press makes both heroes push and counts once; the clash's clock runs as in the game; a hero far away stays free; a grab or the falcon's lift stays one hero's. STILL OPEN under this row: every other boss with a forced, hooked move (43 of the 99 boss scripts hook a script onto the hero; each fight needs its room in the glue's switch, its numbers to keep, and its own runs). No fight has been PROVEN impossible. (docs\STATE.md, Eighth round, parts 61 to 66.) **STATUS 2026-11-15 (test build 18): THE OTHER FIGHTS WERE PLAYED ON PURPOSE WITH TWO HEROES** (ten boss rooms, both players pressing, 20,000 frames each: the Dark Thorn, Cerberus, Scar, Xaldin, Demyx twice, the Hydra, the Groundshaker, the last Xemnas, the armoured Xemnas). Read in their scripts: the moves these bosses force on a hero are HOLDS of one hero by the boss's body (a grab, a ride, a throw), not a face-to-face struggle like Shan-Yu's clash; the boss takes either hero and the other stays free and fights. A FAULT WAS FOUND: at the Groundshaker one step of a hold landed on the free hero, who was then held for ever (builds 12 to 17). Glue 60: a hero in one and the same captured motion for 1,800 steps (a minute) is let go; shown with a stray capture made on purpose (without the glue he stays frozen, with it he plays on). Glue 59 (send the capture to the held hero) was tried first and made the Hydra worse; no build uses it. "Both heroes inside the same hold" is NOT built for these fights: it would put two heroes into one hand; that is my reading, and whether these holds may stay one hero's is the user's to say (REQUIREMENT-full-parity.md). (docs\STATE.md, Eighth round, parts 79 to 83; docs\ROW9-PAIRED-MOVES.md.) **STATUS 2026-11-15, later (test build 20; the user's word of that day: NO OK for "a boss's hold takes one hero"): BOTH HEROES INSIDE THE SAME HOLD IS BUILT** (glue 65): when a boss's script captures a hero or attaches him to itself, and that is not the answer to this hero's own green command, the other hero is put into the same hold, wherever he stands; one script drives the hold for both; both are let go together. Seen at Cerberus, Scar, the Dark Thorn, the Hydra, the Groundshaker's ride, the armoured Xemnas and the last Xemnas (his opening, the part where Riku frees Sora, the laser part: both reached by a script), and in the 40 other fights of the report, played on purpose. While a boss holds both heroes both controllers count (glue 68): both players steer Riku. The Groundshaker's REAL cause is found and cured (its attack-hit routine captured a bystander); the one-minute rule and a rule for a mirror hero left behind stay as nets, with a "let him go" that works. Luxord's tricks let the loser go in time (glue 67: the other hero's hit broke off the act that frees him). NOT A PAIR, MY RECOMMENDED OPTION, IT WAITS FOR THE USER'S OK: a move that a hero starts with his own green command stays that hero's own (the boss has one body and one act, steered by the presses of the hero who took the command; a second hero inside could only be a passenger). (docs\STATE.md, Ninth round, parts 93 to 101; docs\ROW9-PAIRED-MOVES.md.) **2026-11-15, evening: THE USER'S OK: a move a hero starts with his own green command stays that hero's alone; the other keeps fighting ('B OK. Keep player-initiated green Reaction Commands exclusive to the player who activates them. The other player should remain free to continue fighting.'). His next word on the automatic grabs: a single-target attack takes only the targeted hero, a genuinely shared mechanic both (docs\STATE.md, part 109 and after).** **STATUS 2026-11-15, night (test build 21; the user's items 1 and 4 of that evening): A BOSS'S AUTOMATIC GRAB TAKES ONLY THE HERO IT AIMS AT; THE OTHER PLAYER KEEPS FIGHTING. Every boss capture in the 40 fights and the ten boss rooms is single-target except the last Xemnas's laser dome (move 0x106), the game's own party move: there both heroes stand in it, each player has his own Reflect in his own menu, a press of either counts once (the dome's pieces run on player 1's hero, the one its lasers aim at; the mirror gives each move to player 2's hero) and the dome ends once. Glue 68 (the two controllers made one in a hold) is left out: each player keeps his own controller, one press never counts twice (also measured in Shan-Yu's clash: the push count goes up once a push). Shan-Yu's old stray calls: 0 in the runs. The Samurai duel by player 2: verified. The last Xemnas's Riku part with one hero held: the held hero's player plays Riku and ended the part with his own command in a test (run rs4, eh20 98). NOT VERIFIED (for the user's playthrough): the Large Body's Full Swing (never offered in the tests). Mail Delivery and the skate challenges keep build 20's pair (a board or gimmick is no enemy).** (docs\STATE.md, Ninth round, parts 110 to 115.) **CORRECTION 2026-11-16 (the 40 fights on BUILD 21's FILE (v129), tag rs5, and runs ob1 .. ob3 with the captors' kinds): besides the laser dome, the moves of things that are NO ENEMY take both heroes as in build 20 (the Storm Rider fight's whirlwinds F_MU070_BOSS, kind G_OBJ; moving parts of The World That Never Was F_EH070 / F_EH080 / F_EH110, kind F_OBJ; the skateboards, Mail Delivery). Every enemy's grab (BOSS, ZAKO, L_BOSS, E_OBJ ...) took only its target. 40 of 40 in sync.** |
| 10 | Drive gauge | **Each hero has his own** (the user asked "each person will have his own?"; then said "for your question use the Recommended", 2026-11-10 night; the recommended option was own gauges). Each player's hits fill only his own; the values stay apart across rooms (merged build 6). Max bars and Drive levels stay common. The save file holds player 1's values. |
| 11 | Munny, items, skills | **Munny and the item stock are common** (one wallet, as the game has it). Level, abilities and equipment are the same for both (row 2 and row 3). The user asked "is the money shared, but their skills different?" on 2026-11-10 night; answered: shared wallet, same skills today; own skills and equipment stay a Phase 4 job unless the user asks for it sooner. **Replaced by row 39 (2026-11-13): each player gets everything in full and chooses alone.** |
| 12 | Text boxes | **Either player's Circle closes tutorial boxes and talk text** (taken as the recommended option 2026-11-10 night; before, only controller 1 could, and player 2 could open a dialogue but not close it). START, the main menu and the save menu are still controller 1 only. |
| 13 | What enemies drop (HP, MP, Drive balls, munny) | **Both heroes pick them up.** HP / MP / Drive go to the hero who took the ball, munny into the one wallet. When both heroes stand in reach, every other ball asks player 2's hero first (taken as the recommended option 2026-11-10 night). |
| 14 | Player 2's attack target | **Each hero's attack motions test against his own lock-on target** (a fault fix, 2026-11-11: the game used player 1's target for both, which is why the Grandstander ball ignored player 2's hits). Player 2 now also does about twice the damage per swing window in the fight test. |
| 15 | Drive Forms with two heroes | **Each player can use Drive; one form at a time** (2026-11-11, taken as the recommended option). Only the hero who chose it changes; he has his own form gauge, his own menu and keeps the form through a door. While one hero is in a form the other's Drive row is dim: that is the game's own lock, kept because a form uses up Donald or Goofy. Tested with Limit Form. **Changed by row 44 (2026-11-13): two forms at once.** |
| 16 | Counters of mission scripts | **A hit by the second hero counts as a hit by the player** in the mission scripts' damage event (2026-11-11). Fixes the two "cannot be hurt" fights of the prologue and six later missions with the same script. |
| 17 | Full screens of the small games | **Rules screens and the Game Over menu work on either controller**; the first button press of EITHER player brings the command menu up (2026-11-11). Result screens: not found to need a button yet. |
| 18 | Skateboards | **Each player has his own board and his own board commands** (2026-11-11). Mail Delivery starts both heroes on a board each; this needed a new disc file (TEST v3: a second board in the job's room data and a changed mission script). The skate challenges of other worlds still have one board. |
| 19 | Things in a room and bosses | **They deal with the NEARER hero** (2026-11-11, taken as the recommended option): an object's own script sees the nearer hero as "the player", a hero who is down is skipped. So either player can ride the bag, and a boss's Reaction Command goes to the player who stands nearer. Helpers and the heroes themselves are not changed. |
| 20 | Donald and Goofy | **One helper goes with each hero when the heroes are far apart** (the user's rule of 2026-11-10, built 2026-11-11; numbers taken as the recommended option): closer than 900 units everybody follows player 1's hero as before; farther apart each hero gets the helper who is nearer to him; they are one group again when the heroes are closer than 550. |
| 21 | Skateboards in free roam and the skate challenges | **A second board beside EVERY skateboard of the game** (2026-11-11, taken as the recommended option; new disc file v4): 147 places in 29 rooms. The five skate challenges put each player on a board; either player's tricks and checkpoints count. |
| 22 | A boss's scripted move (it grabs a hero) | **The player whose hero is in the move sees the move; the other player keeps his own camera** (2026-11-11, taken as the recommended option). Story scenes stay one picture for both. |
| 23 | The follow-up command of a boss's scripted move | **It belongs to the hero who is in the move** (2026-11-11 late, the user's job 1). A hero's own motion offers the command; it now goes to that hero's own menu and his Triangle starts it ("Break Raid" in Twilight Thorn's throw). |
| 24 | The command menu's look (frame and picture sheet) | **Each player has his own** (2026-11-11 late, the user's job 2; own screens only). One player on a skateboard and one on foot each see their own right menu. A world's own menu style is the same for both. |
| 25 | Whom Donald and Goofy heal | **Both heroes** (2026-11-11 late, taken as the recommended option after the user's job 4 showed that player 2's hero was never healed). Order of a helper's Cure and items: himself, the hero he follows, the other hero, the other helper. |
| 26 | Button-mash parts of boss moves | **Either controller counts** (2026-11-11 late, taken as the recommended option; the script engine's two button tests read both controllers). Not seen in a game yet. |
| 27 | Limits (team attacks with Donald, Goofy or a guest) | **A Limit belongs to the player who started it** (2026-11-11 late, taken as the recommended option): its commands show in his menu and he plays it to the end. As in the original game the other helper leaves while it runs; the other player keeps playing. Tried with Whirli-Goof, Comet and Trinity. |
| 28 | Summons (Genie, Peter Pan, ...) | **A Summon belongs to the player who called it** (2026-11-11 night, taken as the recommended option): the summoned friend comes to that player's hero and fights beside him; his picture, the SUMMON gauge, "Dismiss" and the friend's own commands show on that player's screen only; only he can send the friend away (Dismiss, or his gauge runs out). Only ONE Summon at a time: while one is out the other player's Summon list is grey. Player 1's call shows the game's entrance movie on player 1's screen (both wait, as in the original game). Player 2's call has NO movie: the game's own "no summon effects" way, the friend just appears (the movie is written for the engine's player; a tested other way, `--sum-scene`, played it on player 1's screen with player 1's hero as the actor). |
| 29 | Who player 2 is in the user's test | **The user's own second PC at home, not a friend** (user, 2026-11-11 night: "i will not send it to friend to my second PC only so prepare everything to be ready"). The host folder `dist\PS2-ONLINE-KH2-TEST` is made complete (program, BIOS, patches, the two-player disc file) so that ONE folder copy to the second PC is all; the same-house steps are in `dist\START-HERE (TWO PCs AT HOME).txt` (tool `tools\package\finish_two_pcs.py`). The friend zip is still built. |
| 30 | Small things of Summons, Limits and Continue (test build 11) | **Left as they are and named in the read-me** (2026-11-12, taken as the recommended option; the user: "continue until you finish everything"). (a) Stitch, the Summon that walks on the screen glass, shows on both screens. (b) After a Continue a Summon that player 2 had brought into the room leaves at once. (c) While the heroes are far apart player 2's Limits are grey (a next job). (d) Continue inside a boss fight goes back to the last normal room and plays its scene again: the game's own way, VERIFIED with two heroes in one fight by a test line. (e) Two faults were FIXED, not left: the other player's Drive gauge after a door with a Summon out, and the game's pool of prompt objects running empty in a long boss fight (a hidden fault of builds 9 and 10). Details: `docs\STATE.md`, "Sixth round". |
| 31 | The game's pool of green command signs (test build 12) | (Rows 31 to 38 are TEST BUILD 12, in `dist\` since 2026-11-13 night: package id 33d4076d2325, disc "TEST v5"; whole regression clean, rehearsed. `docs\STATE.md`, PICK UP HERE.) **18 signs instead of 9** (2026-11-12, seventh round, taken as the recommended option). The game sized its pool for ONE menu; two menus need up to 12 in a boss's "Reversal" part. The guard of build 11 stays. Row 30 (c) was WRONG: player 2's Limits are not grey when the heroes are far apart; a Limit needs a fight, for both players, as in the game. |
| 32 | What "Continue" gives player 2 back | **His own Drive, form and Summon values from the moment he came into the room** (2026-11-12, recommended option), as the game does for player 1. So his Summon no longer leaves after a Continue (row 30 (b) is solved), and a form he entered inside the room is gone after it, as player 1's is. A SAVED game still holds player 1's values only (row 10). |
| 33 | Whom Donald's or Goofy's Potion goes to | **The hero with less HP** (2026-11-12, recommended option). Before, a helper's item always went to player 1's hero, also when player 2's was the one in need. |
| 34 | The world map, the Gummi Menu and the screens where nobody has a hero | **Either controller** (2026-11-12, recommended option), like the text boxes, the rules screens and the main menu before (rows 12 and 17). |
| 35 | The Gummi Ship | **Player 2 flies his own ship** (2026-11-12, recommended option; lane S3's proof moved into the build): own stick, own place, own guns; his START pauses; either controller answers the pause menu, the results and "Retry". NOT done, named in the read-me: his ship cannot be damaged, the mission ends with player 1's ship, one score and one hull gauge. Reason and evidence: `docs\STATE.md`, seventh round, part 7c. **STATUS 2026-11-14 (test build 16): PLAYER 2'S SHIP CAN BE HIT AND HAS ITS OWN HULL** (fifty-first glue: every shot's question "does this touch the player ship" is also asked for ship 2). The mission is over when EITHER ship falls (the Light Cycle rule of row 36); the one hull gauge shows the weaker ship; a repair mends both. Still one score, one gauge with no mark for whose ship it shows, one lock-on. (docs\STATE.md, Eighth round, parts 67 and 69.) **STATUS 2026-11-15 (test build 20): A SCORE FOR EACH PLAYER** (glue 66): a cannon shot's points go to the ship that fired it; player 1's number stands in the SCORE frame, player 2's beside it; a digit left of the hull gauge says whose ship the gauge shows. The points of other weapons than cannons cannot be told apart yet and go to player 1's number; the mission's result and medals use the sum, as before. (docs\STATE.md, Ninth round, part 97.) **STATUS 2026-11-15, later (test build 21): build 20's second score row made some Gummi routes fly a little differently (its ten pictures lay in the flight module's own heap); they lie in the patch's own memory now, and route 8 is build 19's to the point again.** (docs\STATE.md, Ninth round, parts 103, 104, 106, 107.) **Build 22 (2026-11-16): glue 77 (the points of weapons other than cannons to the ship that fired) was tried and is left out: it faulted in its tests (STATE part 124); those points still go to player 1's number.** **Build 24 (2026-11-16): glue 78 gives the points of the other weapons to the ship that fired (glue 77 stays out; its crash came from lying inside glue 66's old table, part 130).** |
| 36 | The special rides where the disc had no hero for player 2 | **Disc v5: a second Light Cycle, a second flying Sora in the Pooh game, a second carpet rider** (2026-11-12, recommended option; 18 places in the room data, the original object built first). Each is moved by its own controller. Known: on the carpet player 2's hero flies in the riding pose WITHOUT a carpet under him (the one carpet follows the engine's player); in the Light Cycle the ride is over when EITHER cycle is destroyed (the game's rule for a rider, no rescue on a cycle). NOT doubled, because a second object does not work there (confused pictures, 50 fault lines each): the toy cannon, the sidecar, the carpet escape. See row 37. **STATUS 2026-11-14 (test build 16): A CARPET UNDER EACH HERO** (fifty-second glue: a second carpet is made with the game's own routine when both heroes are carpet riders; its state routine follows player 2's hero; no new disc). The toy cannon, the sidecar and the carpet escape are still one hero for both (row 37): NOT built, and not proven impossible; what is known is in docs\STATE.md, Eighth round, part 67 and the parts after it. **STATUS 2026-11-14, later (test build 18): the toy cannon, the sidecar and the carpet escape have a second hero now, see row 37.** **STATUS 2026-11-15 (test build 20): the toy cannon has a view for each player now, see row 37.** |
| 37 | Player 2 has no hero in a scene | **His controller also drives the one hero** (2026-11-12, recommended option; twenty-eighth glue). So he is never a spectator: in the carpet escape, on the sidecar and at the toy cannon both players steer and shoot the one hero or cannon; menus and scenes without heroes listen to either controller. With a hero of his own nothing changes. This is the fallback of soul rule 7, not its fulfilment: a vehicle of his own in those three small games is still open (reason: `docs\STATE.md`, part 7e). **STATUS 2026-11-14 (test build 18): THE THREE ONE-HERO SMALL GAMES HAVE A HERO OR A VEHICLE FOR EACH PLAYER.** The second one is MADE AT RUN TIME with the game's own "make an object" (no new disc; the build's identity rule makes it player 2's). The carpet escape: he gets the escape's own state and a second escape carpet that follows him. The sidecar: he gets the sidecar's own state. The toy cannon: a second cannon; one shared view there, because the cannon's camera kind exists for camera 1 only. In every other scene without a hero for player 2 his controller still drives the one hero, as before. All three were played by scripts: the escape to its end, the sidecar through a Game Over and "Continue", the toy cannon to its end and on into the next room. Not yet played by two people, and not from the story (the test runs jump into the rooms). (docs\STATE.md, Eighth round, parts 70, 71, 73, 74 and 76 to 78.) **STATUS 2026-11-15 (test build 20): THE TOY CANNON HAS A VIEW FOR EACH PLAYER** (the own-screen option `--cannon2view`: camera 2 is the game's still view, moved to player 2's cannon). The three small games were also started by the story's own jump ("Type 2"), and the sidecar from its story scene; walking into the toy cannon and the carpet escape through the story's talk point cannot be done by a test script (the test start has not the story's progress). This row's rule is taken for a boss's hold too: while both heroes are held, both controllers count (glue 68, row 9). (docs\STATE.md, Ninth round, parts 95, 97, 98, 100.) |
| 38 | Own screens: Stitch and the sound | **Left as they are** (2026-11-12, recommended option; kind c in the state file, parts 5c and 5e): Stitch shows on both screens; the sound is one sound for both PCs, heard from player 1's camera (the network play sends button presses only, the emulator on each PC plays the same game state). |
| 39 | What each player gets and what he chooses (replaces rows 3 and 11) | **What the game GIVES, each player gets in full, as a single player would; what you CHOOSE, each player chooses alone** (user, 2026-11-13: "both of them getting same items and metarils or points etc .. but they can select which skills to upgrade each one alone (so the amount of gold or points for 1player alone single player should be same for 2 not devidede between them but the skills each one can upgrade or use what weapons he like"). GIVEN IN FULL TO EACH: munny, items, synthesis materials, Keyblades, armour and accessories found, abilities learned, AP, experience (same level, row 2). CHOSEN ALONE: the Keyblade he holds, the armour and accessories he wears, the abilities he equips with his own AP, his shortcuts, what he buys, uses up or synthesises. My reading, taken as the recommended option (correct it if the user says otherwise): each player has his OWN bag and wallet; every pickup, chest, prize and story reward goes into BOTH in full; a Potion one player drinks or munny he spends leaves only his own. Drive Form levels and growth abilities stay common (row 10). NOT BUILT: today the twin reads player 1's record for stats, abilities and equipment (lane D) and the save file holds one Sora; it needs a second record, a place for it in the save and menus that show each player his own. Feasibility study first. Comparison with the Steam co-op mod (TCM-Murray) of 2026-11-13: theirs also keeps items and gear per player. **STATUS 2026-11-14: NOT BUILT.** The feasibility study is written (docs\STATE.md, Eighth round, part 25): feasible in three stages, the one real risk is the place in the save file. **STATUS 2026-11-14, later (test build 15): STAGE 1a IS BUILT AND VERIFIED: player 2's own ARMOUR AND ACCESSORIES.** He chooses them in the pause menu when HE opened it; the bag is common. His eight places live inside Sora's own record, in the places 5 to 8 that the hero never has (a test showed that they do nothing for the hero), so they are saved with the game's own save and no new place in the save file was needed. STILL OPEN under this row: own Keyblade (the weapon's model and files), own abilities (it is not known whether the game keeps the ability list in a fixed order), own item places, own bag and wallet, "everything given goes to each". (docs\STATE.md, Eighth round, parts 52 to 58.) **STATUS 2026-11-15 (test build 18): STAGE 1b IS BUILT AND VERIFIED: PLAYER 2 SWITCHES HIS OWN ABILITIES.** Read: the ability list only grows (a new ability takes the first empty place), so his switches are one bit per place: five shorts with a mark, kept in King Mickey's record in the save data (item places he never has), saved with the game's own save. His pause menu shows and edits his; in a fight each hero has the abilities of his own switches; an ability the game gives goes to both. STILL OPEN under this row: own Keyblade, own item places, own bag and wallet, "everything given goes to each" for items and munny. (docs\STATE.md, Eighth round, parts 79 to 83.) **STATUS 2026-11-15, later (test build 19): a fault of builds 15 to 18 is cured: player 2's "Items" list was built from his copy of the record and kept items that were gone (he could take a Potion that was not there); glue 61 makes his list from the item places as they are. The item places themselves are still one set for both (own item places: still open).** **STATUS 2026-11-15, later (test build 20): THE REST IS BUILT.** Player 2 has his own item places, his own stock of the fight items and his own shortcuts (glue 62) and his own Keyblade (glue 63; glue 64 binds a weapon to its files by name, register F8). What the game gives is there for each player: a fight item goes into both stocks; a Keyblade, an armour or an accessory comes twice into the bag. Still common, and said so in the read-me: the bag itself (with two of each thing given), the wallet (a purchase gives the thing to both), the materials, a Drive Form's second Keyblade. (docs\STATE.md, Ninth round, parts 89 to 92 and 95.) **STATUS 2026-11-15, later (test build 21; the user's answer D of that day: "each player his own bag and wallet; the money they gain goes to both; while they spend it each one alone"): OWN WALLET AND OWN BAG ARE BUILT.** Munny the game gives goes into both wallets; a shop or the Moogle is the shop of the player who opened it (his munny, his things); player 2's pause menu shows his munny and his bag; what the game gives goes into both bags, once into each. His bag (Keyblades, armour, accessories, materials) lives in King Mickey's ability places 16 to 79 (read-proven: never cleared after a New Game, never read as abilities) and keeps up to 7 of one Keyblade, armour or accessory. Still common: Tent, Boosts, Drive recoveries, the helpers' and guests' weapons, recipes, Torn Pages, elements, key items. Also cured: player 2 could not finish a purchase (his buttons did nothing in "Buy how many?"). (docs\STATE.md, Ninth round, parts 105 to 108.) **Build 22 (2026-11-16): a target choice for single healing items (glue 73); an item an enemy drops is picked up by either hero and goes into both bags (glue 74).** |
| 40 | A boss breaking out of a combo (the game's "revenge" count) | **Both heroes' hits count, each hit a bit less** (user approved 2026-11-13, "yes approve 3 and 4 and 5 and 6"; the idea comes from the Steam co-op mod). The same for both heroes (parity): so a boss neither stays stuck in player 2's combo forever nor breaks out twice as fast. Test first whether the game already counts player 2's hits; the amount is tuned in that test. Not built. **STATUS 2026-11-14 (test build 13): BUILT AND VERIFIED.** The game counted both heroes' hits in full (a real gap); now each hero's hit counts three quarters while there are two heroes. |
| 41 | Safe during your own Limit | **Whoever is doing a Limit cannot be hurt while it plays**, player 2 as player 1 in the original game (user approved 2026-11-13). Test first; built only if player 2's hero can be hurt during his Limit. **STATUS 2026-11-14: TESTED, NO GAP, NOTHING BUILT.** Player 2 was not hurt once during three Limits. |
| 42 | The 1000 Heartless (and any other fight that uses the same crowd system) | **The game's limit of about 20 fighters at once is split evenly between the two heroes; each enemy goes to the nearer hero** (user approved 2026-11-13). Test first with player 2 far from player 1; built only if player 2 is left without enemies or enemies vanish near him. **STATUS 2026-11-14: TESTED, NO GAP, NOTHING BUILT.** Both heroes fight their own crowds. |
| 43 | Getting up after falling | **A hero who gets up by himself comes back with HP just above the game's low-HP warning line** (user approved 2026-11-13; the Steam mod uses 26 % instead of 25 %). First find where the game's line is; today lane N gives 25 %. Not built. **STATUS 2026-11-14 (test build 13): BUILT AND VERIFIED.** 26 of 100 HP instead of 25. |
| 44 | Two Drive Forms at the same time (changes row 15) | **Both heroes can be in a form at once; a form is refused only when the helper it needs is already away** (user approved 2026-11-13, "also 1 and 2 is approved from the better decisitons"; the rule of the Steam co-op mod). So player 1 in Valor (Goofy leaves) and player 2 in Wisdom (Donald leaves) works; Limit Form needs no helper and works at any time; Master, Final and Anti need both helpers, so only when no form holds one. Risk: two forms' files in the PS2's 32 MB; measure first (plan section 8, risk 3). Not built. **STATUS 2026-11-14 (test build 13): BUILT AND VERIFIED** for Valor + Wisdom, Limit + Limit, Limit + Final, also through a door. A second form is refused when its helper is away or when the game's file memory has no room (seen in the Hydra's room). When one form ends only its own helpers come back. |
| 45 | King Mickey's rescue (11 missions) with two heroes | **Approved: Mickey's rescue works for two** (user approved 2026-11-13). Mickey comes when both heroes are down; his Healing Light brings BOTH heroes back. First try (soul rule, nobody watches): each player gets his own Mickey, the twin way. Fallback if two Mickeys are proven impossible (reported to the user): the Steam mod's rule, one player plays Mickey (picked by a roll from the game's own random numbers, identical on both PCs), the other stays down until the Healing Light. Not built; first test what the game does today with two heroes. **STATUS 2026-11-14 (test build 13): BUILT AND VERIFIED: A KING MICKEY FOR EACH PLAYER** (Shan-Yu, Storm Rider, the Hydra). The two Mickeys share one HP bar and one Drive gauge; whichever ends the rescue, both heroes come back. The fallback (one Mickey by a roll) was not needed. |
| 46 | TEST BUILD 13 (eighth round, 2026-11-14) | Build 12 + fourteen new glues (30 to 43, `tools\merge\merge_v7.py`): enemy groups wake up for player 2 too; rows 40, 43, 44, 45 and the first half of row 9; the Keyblade change in the menu no longer stops the game with two heroes; a form kept through a door no longer brings back the helpers it uses. The disc file is the same as in build 12. Details and evidence: docs\STATE.md, section "Eighth round". |
| 47 | TEST BUILD 14 (eighth round, 2026-11-14) | Build 13 + three glues (44, 45, 47; the same builder with no option): a boss's Reaction Command is taken by one hero (the sender is the script's player; a boss that holds one hero does not take the other hero's command); Luxord's card / die takes the hero the trick is played on. Closes the faults F10 (Xigbar's sniper part) and F11 (Luxord's card trick) of builds 12 and 13. The disc file is still the one of build 12. Details and evidence: docs\STATE.md, section "Eighth round", parts 45 to 50. |
| 48 | TEST BUILD 15 (eighth round, 2026-11-14) | Build 14 + two glues (48, 49; `tools\merge\merge_v7.py --ownrec --ownmenu`): the second hero's unit slot reads a view of the hero's record with player 2's armour and accessory places; while player 2's pause menu is open his places and the hero's change places in that record. Plan row 39, stage 1a. The disc file is still the one of build 12. Details and evidence: docs\STATE.md, section "Eighth round", parts 52 to 58. |
| 49 | TEST BUILD 16 (eighth round, 2026-11-14) | Build 15 + three glues (50, 51, 52; `tools\merge\merge_v7.py --ownrec --ownmenu --together --ship2hit --carpet2`): both heroes in Shan-Yu's clash (plan row 9, second half, first fight); player 2's Gummi ship can be hit and has its own hull (row 35); a carpet under each hero (row 36). The disc file is still the one of build 12. Details and evidence: docs\STATE.md, section "Eighth round", parts 61 to 70. |
| 50 | TEST BUILD 18 (eighth round, 2026-11-15) | Build 16 + seven glues (53 to 58 and 60; `tools\merge\merge_v7.py --ownrec --ownmenu --together --ship2hit --carpet2 --norec --escape2 --sidecar2 --twinmake --hudowner --ownabil --holdwatch`) and the own-screen option `--cannon1view` of `tools\own\make_own.py`: a second hero, made at run time, in the carpet escape, on the sidecar and at the toy cannon (plan rows 36 and 37); player 2's own ability switches (row 39); no hero is held for ever (row 9). BUILD 17 was build 16 + the glues 53 to 56; it was packaged and rehearsed, but a 60,000-frame run of the toy cannon then showed 50 fault lines at the game's end (the HUD's owner became a cannon, which has no HP record; cured by glue 57); it was never given out. The disc file is still the one of build 12. Details and evidence: docs\STATE.md, section "Eighth round", parts 70 to 83. |
| 51 | TEST BUILD 19 (eighth round, 2026-11-15) | Build 18 + glue 61 (`tools\merge\merge_v7.py --ownrec --ownmenu --together --ship2hit --carpet2 --norec --escape2 --sidecar2 --twinmake --hudowner --ownabil --holdwatch --itemsync`; the own-screen option `--cannon1view`): player 2's "Items" list shows the item places as they are. Builds 17 and 18 were packaged, rehearsed and never given out; build 19 is the one the user gets after build 16. The disc file is still the one of build 12. Details and evidence: docs\STATE.md, section "Eighth round", parts 84 to 86. |
| 52 | TEST BUILD 20 (ninth round, 2026-11-15) | Build 19 + seven glues (62 to 68; `tools\merge\merge_v7.py --ownrec --ownmenu --together --ship2hit --carpet2 --norec --escape2 --sidecar2 --twinmake --hudowner --ownabil --holdwatch --itemsync --ownitems --ownkey --bindname --holdpair --ship2score --trickguard --holdpads`) and the own-screen option `--cannon2view` of `tools\own\make_own.py`: player 2's own item places, fight items, shortcuts and Keyblade (row 39); both heroes inside the same hold of a boss, the Groundshaker's cause cured, Luxord's tricks, both controllers in a hold (row 9); a view for each player at the toy cannon (rows 36, 37); a score for each player in the Gummi flight (row 35). The disc file is still the one of build 12. Details and evidence: docs\STATE.md, section "Ninth round", parts 89 to 101. |
| 53 | TEST BUILD 21 (ninth round, 2026-11-15) | Build 20 + three glues (69 to 71; `tools\merge\merge_v7.py ... --trickguard --holdshared --ownwallet --shoppad --ownbag`) and the sixty-sixth glue's sixth and seventh forms: player 2's own wallet and own bag (row 39), player 2's buttons in the shop's quantity box, the Gummi flight as the game's again (row 35), and the sixty-fifth glue's fifth form (row 9: a boss's grab takes only its target; the last Xemnas's laser dome takes both, each player with his own Reflect; glue 68 left out). Built and tested on Opus 5.5 after the user switched the session's model. The disc file is still the one of build 12. Details and evidence: docs\STATE.md, section "Ninth round", parts 103 to 115. **Package of build 21: aa9b18abfa09 (2026-11-16 00:03; the read-me corrected for the shared moves; the game files are those of e24a7e8821cf, both rehearsed).** |
| 54 | TEST BUILD 22 (tenth round, 2026-11-16) | Build 21 + five glues (72 to 76; `tools\merge\merge_v7.py ... --ownbag --drivesave --itemtarget --boxpick --formroom --setposguard`): player 2's own Drive gauge in the save (72); a target choice for Potions / Hi-Potions / Ethers / Elixirs, the PARTY window shows both heroes, the first "Sora" is player 1, the last player 2 (73); player 2 picks up the item boxes enemies drop (74); his Drive Form files are asked for again in a new room (75); trap_effect_set_pos skips an ended effect (76, the Fortuneteller's Clear Shot). Glue 77 (Gummi points of non-cannon weapons) faulted in its tests and is NOT in the build. Package 73330f051af3 (2026-11-16 10:46; disc TEST v5 unchanged); the user tests it while the last checks run. Details: docs\STATE.md, section "Tenth round", parts 119 to 125. |
| 55 | TEST BUILD 23 (tenth round, 2026-11-16) | Build 22 + ONE FIX: glue 66's shots' table (the Gummi flight's "which ship fired" byte per cannon shot, 4 KB) moved from 0x000EE800 to 0x000DF000 (`tools\merge\edit_merge_v7_gqtable.py`; patches\merged-v17 differs from merged-v16 in two words). Build 22 had placed glues 72 to 75 (333 words) inside that table, so a cannon shot could change a byte of their code until the next frame; the builder now checks the table and the own pictures at the END of a build. Package 9d40745f3298 (disc TEST v5 unchanged), rehearsal p28 clean. Also verified: Load Game from the title screen gives player 2 his saved Drive gauge; a Drive Form through five doors in a row. Details: docs\STATE.md, section "Tenth round", part 130. |
| 56 | TEST BUILD 24 (tenth round, 2026-11-16) | Build 23 + glue 78 (`--gummitag`): in the Gummi Ship the points of weapons other than the cannons go to the ship that fired (the firing ship is written into the weapon's hit values, which every shot copies; cannons keep glue 66's table). Package 98dad91e6e9e (disc TEST v5 unchanged), regression b33 clean, 40 fights rs8 as build 22, rehearsal p30 clean; the user's copy Desktop\PS2-ONLINE-KH2-TEST-b24. Also answered: doors in a Drive Form keep a Keyblade copy per door in the ORIGINAL game too (one-hero disc), 16 doors never ran out of memory; the nine boss scripts in no room file: three unused by the game, six met in their makers' fights with two heroes. Details: docs\STATE.md, section "Tenth round", parts 134 to 137. |

## 2. What is verified today (read-only, nothing modified)

| Fact | Evidence |
|---|---|
| Disc is Kingdom Hearts II Final Mix (Japan), SLPM-66675, VER 1.01, NTSC | `SYSTEM.CNF` inside the ISO |
| Clean, unmodified dump | 4,330,192,896 bytes, SHA-1 `81c177a374e1bddf8453c8c96493d4e715a19236` = Redump entry |
| Game program is `SLPM_666.75` (2,629,364 bytes); data in `KH2.IMG` + `KH2.IDX` + `OVL.IMG` | ISO root directory |
| PS2-ONLINE package `9e49d3f8243e` is lockstep and stable | last two sessions: 329,480 and 143,747 frames, "never out of sync" |
| A per-game patch file (.pnach) is supported and compared when a friend joins | Digimon patch in `emulator\patches`, tests r02 / t11 |
| "2 players, no multitap" layout exists (P1 = port 1, P2 = port 2) | launcher + test t13 |
| Emulator source and test tools exist | `Desktop\New folder\digimon-online` (PCSX2 v2.9.115 + PS2Net, several copies on one PC with scripted buttons) |
| Tools already on this PC | Ghidra 12.1.4; OpenKH tools (IdxImg, Bdxio for AI scripts, SpawnScript, Bar) |

| English-text copy of the disc builds, boots and shows English menus | test en02; file `local\iso\Kingdom Hearts II - Final Mix (English text).iso`, SHA-1 `cd98705cb44a036fd164d2833d658aba67e79d6b`, same result when built twice |
| The game program is the same in the English copy (same CRC F266B00B) | lobby line in every test log |
| **The game reads controller port 2 every frame** | test s01: reply bytes slot0 = slot1 (for example 43128 / 43128 per 10 s) |
| First sync result: two copies, 12,000 frames (boot, menus, New Game, opening movie), random buttons on pad 2 | test s01: 187 digests compared, never out of sync, screenshots byte-identical |

Text on the original disc is Japanese (voices are English). The project uses the English-text copy.

## 3. What is NOT verified yet

- That KH2 Final Mix stays in sync on PS2-ONLINE **during real play** (fights, room changes, cutscenes, saving).
  Only boot, menus and the opening movie are tested so far.
- **Whether the game accepts a second player character at the same time.** I searched and found no public mod or
  cheat that shows it, for any version. This is original work and the biggest unknown of the project.
- Community memory maps exist for exactly this disc (OpenKH and the KH2 Randomizer support it). They will help,
  but every address we use has to be checked on our disc first.

## 4. The soul rules (they apply in every phase)

A phase is not finished unless these hold for everything that phase covers.

1. **Never benched.** Whenever P1 can play, P2 can play.
2. **Direct control.** P2's stick and buttons move the character. No AI decides for them. Same reaction speed as P1.
3. **Equal to P1.** Everything P1 can do, P2 can do, on P2's own buttons and P2's own target. Everything the game
   does to P1 (enemy and boss attacks, grabs, status effects), it can do to P2.
4. **Seen.** The camera keeps P2 in the picture. P2 has their own gauge and can be told apart from P1 at a glance.
5. **Counts.** P2 can win a fight, save P1, and fall with consequences. The result depends on both players.
6. **Grows.** P2's Keyblade and abilities become P2's own choices (Phase 4).

7. **Full parity in every special sequence** (user requirement 2026-11-10, full text in
   `docs/REQUIREMENT-full-parity.md`). Whenever the game gives P1 a special vehicle, mount, transformation,
   movement mechanic, weapon, ability, interaction or temporary mode, P2 gets the equivalent, independently
   controlled, at the same time. P2 is never an AI passenger or a spectator. A world or mission is never
   "complete" because P1 can finish it while P2 follows or waits.

Every phase has a **soul test**: something a human can try and see, played online on two PCs.

## 4B. Full gameplay parity: every world, mission, minigame and boss (user requirement 2026-11-10)

The user's text is kept verbatim in `docs/REQUIREMENT-full-parity.md` and is the authority. In short:

1. A personal vehicle or mount for P1 means an equivalent, independent one for P2 (example: two Magic Carpets).
2. Both players have direct control. P2 never becomes an AI passenger or a spectator.
3. Both can attack, defend, interact and use the mode's special abilities whenever that mode allows them.
4. The special mechanic works for both at once: collisions, damage, enemy targeting, animations, transitions.
5. A sequence built for one character or vehicle is investigated and adapted for two active players.
6. Both take part in the same story events and progression without losing their gameplay.
7. Never "done" because P1 can finish while P2 follows or waits.

Examples named by the user (not a complete list): Magic Carpet (Agrabah), Light Cycle (Space Paranoids), Gummi
Ship, lions (Pride Lands), skateboard and Struggle (Twilight Town), the musical (Atlantica), Roxas's prologue,
boss mechanics and Reaction Commands.

**Before any of it is implemented: the audit.** One checklist for the whole game, `docs/PARITY-CHECKLIST.md`
(lane P), built from the game's data and then confirmed in play. For every world, mission, minigame, special
movement sequence and boss it states: the original mechanic; what P1 can do; what P2 must be able to do; whether
each player needs a separate object, vehicle, character state or interaction; the adaptation needed; and how it
is verified with two human players. Every later phase takes its tests from this checklist.

This replaces the earlier idea that a minigame could stay "P1 only". An exception needs proof that two players
are impossible there and the user's explicit OK; none is assumed.

Honest status: for most special modes it is NOT yet known whether the game can run two of them (two carpets, two
light cycles, two ships). Each gets its own feasibility test, like the twin test did, before work is promised.

## 5. Who P2 is: the twin

P2 plays a second copy of the character P1 is playing at that moment.

Why this is better for the soul rule than playing Donald or Goofy:
- P2 has the full Sora move list from the first playable build.
- Almost nothing benches P2: in the Roxas opening there are two Roxas, in fights Sora has alone there are two Soras,
  and Drive Forms take Donald or Goofy, not P2.
- Donald and Goofy stay, so the party feels like the original game with one more hero.
- The same character twice should reuse the same files in memory (HYPOTHESIS, to check in Phase 0).

What it costs:
- The game is built around exactly one player: one command menu, one lock-on, one camera, and enemies, doors, chests
  and save points all look for "the player". Each of these has to be found and taught about two.
- Two identical characters on one screen. P2 needs a visible difference (colour or marker).
- Drive Forms with two Soras: who gets Donald, who gets Goofy, and whether two forms fit in the PS2's 32 MB memory.

Shared and separate (proposal):
- Shared: munny, item stock, story progress, level and experience.
- Separate: HP, MP, target, position. From Phase 4: Keyblade and abilities.

### Two design rules (decided by the user, 2026-11-10)

**Donald and Goofy belong to the team, not to one player.**
- They stay near the group, heal and protect whichever hero needs it, and either player can start a Limit or a
  Drive Form with them. If both players want the same friend at the same moment, the first press wins.
- Honest order: in Phase 1 they still follow P1 as the original game does, because nothing about them is changed
  yet. Equal treatment of both heroes is Phase 2 work (helping, healing) and Phase 3 work (Limits, Drive Forms).

**When the heroes split up, one helper goes with each** (decided by the user 2026-11-10; "usually they will not
be split"): each helper goes with the hero nearest to them, so one player has Donald and the other Goofy; together
again, they act as one group.

**A fallen hero far away is not left alone** (proposed with the rule above, user said to continue): the nearest
helper runs over; Donald casts Cure on them if he has it and MP; either helper uses a Potion on them if he
carries one; otherwise the hero gets up alone after a while. How far the helpers' AI can be redirected is
unknown until Phase 2 (HYPOTHESIS).

**Room exits: both players must stand at the exit.** (User: "because we will be always together".)
- The PS2 holds one room in memory, so the two players can never be in different rooms.
- An exit, a boss room or a story event starts only when both heroes are there. Either player can be the first.
- While one hero waits at the exit, the screen shows that the exit is waiting for the other player.
- No exception for a missing player (user: "we always going to be play as 2 person not a single person").
  The mod is for two players only. If a connection is lost, the session is restarted from the last save.
- Order: this rule is part of Phase 1, because no play is possible without room changes.

### The parity list (P2 = P1)

One table, kept up to date in every phase. Each line is marked: works / not yet / needs your decision.

| P1 can... | Phase where P2 gets it |
|---|---|
| Run, jump, guard, dodge, full ground and air combos | 1 |
| Use every equipped skill (combo skills, High Jump, Quick Run, Aerial Dodge, Glide and the rest) | 1 |
| Use magic, items and shortcuts | 1 |
| Lock on to their own target | 1 |
| Be targeted and attacked by normal enemies | 1 |
| Be targeted by bosses, including grabs and special attacks | 2 |
| Use Reaction Commands, open chests, pick up drops, use save points | 2 |
| Fall, be rescued, cause Game Over | 2 |
| Use Limits, Summons and Drive Forms | 3 |
| Play as Roxas, the lion and the other changed characters | 3 |
| Open the menu, choose Keyblade and skills | 4 |

Three places where "exactly the same" is not possible, so you know now:
- **One camera.** Both players share one picture. The camera serves both; it cannot follow each player alone.
- **Cutscenes.** The story scenes were made with one Sora. P2 is not added into them.
- **Drive Forms.** There are only two friends to fuse with (Donald and Goofy), so both heroes cannot be in a form
  that needs both friends at the same moment.

**Fallback.** If Phase 0 shows the engine cannot run a second player character, I stop and report. The fallback is
P2 playing Donald / Goofy / the world guest. You decide then; I will not switch silently.

## 6. Phases

Each phase ends with a build you can play with your friend, a soul test, and a stop for your OK.

### Phase 0: Ground truth (the only phase without new gameplay)
- Project folder with sandbox copies. `MY-GAMES`, the BIOS and the Desktop package are never modified while developing.
- Stock sync test: two emulator copies on this PC, unmodified game: boot, new game, first fights, room changes,
  a cutscene, a movie, a save. Result must be "never out of sync".
- Read the poll counters in the log: does KH2 read controller port 2?
- Load the game program in Ghidra. Check the community memory maps against our disc.
- **The twin test:** make the game create a second copy of the player character in a normal room and record what
  happens: does it load, does it stand, what does it listen to, does anything break (camera, enemies, room exits)?
- **For P2:** the control sheet, and the **bench list**: every part of the game where the twin needs special care
  (Drive Forms, changed-character worlds, minigames, Gummi Ship, forced events).
- Gates: (1) if KH2 cannot stay in sync, stop and fix the emulator first. (2) if the twin is impossible, stop and
  report with the fallback.

### Phase 1: P2 takes the controller
- P2's pad fully controls the twin in normal rooms: run (analog), jump, full ground and air combos, guard, dodge,
  magic, items, and every skill P1 has equipped. No AI in it at all.
- Normal enemies target and attack P2 the same way they do P1.
- P2 has their own target (lock-on separate from P1's).
- The camera keeps both players on screen. Neither player is pulled to the other while both are in the room.
- P2 can be told apart: different colour or a clear marker. P2 has an HP/MP gauge on screen.
- Donald and Goofy keep fighting as AI.
- **Soul test:** P1 puts the controller down. P2 alone clears a room of enemies. Button-to-action delay is the same
  as P1's (measured in frames). Online, two PCs, in sync.

### Phase 1C: camera test for own screens (a gate, not a promise)
- Runs after P2 has its own controller. HYPOTHESIS to test: the game keeps a camera for each player on both PCs,
  draws the two views in turn, and each PC shows only its own view. Nothing differs between the PCs inside the
  game, so it cannot cause "OUT OF SYNC".
- Measured so far: the first town already shows only 30 different pictures per second (each picture lasts two
  video frames); menus run at 60. Fights and other areas: being measured.
- The test must show: two cameras that each follow their own player, movement relative to the right camera,
  the picture rate each player really gets, and which screen effects break.
- Result goes to the user with screenshots. Yes = Phase 2B. No = the shared screen stays the way to play.

### Phase 2B: own screens (COMMITTED: Phase 1C passed, lane K, and the user chose own screens on 2026-11-10)
- Each PC shows its own player's camera and its own HUD. The emulator chooses which view to show; the game on
  both PCs stays identical.
- Lock-on, targets and prompts belong to the right player's view.
- Try for the full picture rate (both views drawn in every step) as an upgrade; report honestly if it fails.
- The exit rule does not change: one room for both players, both at the exit.
- **Soul test:** both players in the same fight room, far apart, each with their own full picture, online, in sync.

### Phase 2: P2 counts
(Tests of this phase come from the boss and Reaction Command lines of the parity checklist.)
- Bosses see two heroes: they choose P2 as a target, and their grabs and special attacks work on P2 too.
- Down and rescue (decided by the user 2026-11-10, "exactly like Goofy"): a hero whose HP reaches 0 goes down
  and stays in the room. The other player can bring them back with a Potion or Cure, as with Goofy; if nobody
  does, they get up by themselves after a while. Game Over only when both heroes are down at the same time.
  Donald and Goofy are unchanged. Needs first: an own HP and MP bar for each hero (today they share one).
- P2 can use Reaction Commands, open chests, pick up orbs and drops, use save points.
- Shared munny and items; shared experience and level-ups.
- A damage counter in the log (P1 share / P2 share per fight), so "not a shadow" is a number we can check.
- **Soul test:** in a boss fight, P1 falls and P2 saves the run; P2 lands the last hit. Both seen online.

### Phase 3A: the parity audit (before any special sequence is implemented)
- Lane P writes `docs/PARITY-CHECKLIST.md` from the game data (303 mission files, 56 player-type objects, every
  room's spawn data, command and Reaction Command tables) and marks what is read from data and what is from memory.
- Each special mode then gets a short feasibility test (can the game run two of them?) in the order the story
  meets them, and a size estimate.
- Result goes to the user as a list: works as is / needs adaptation (what kind) / not yet known.

### Phase 3: The whole game with a twin
- The twin follows P1's character everywhere: Roxas in the opening, the lion in Pride Lands, the costumes in
  Halloween Town, Space Paranoids and Timeless River.
- Drive Forms for two. First design to test: each hero can fuse with one friend (one takes Goofy, the other Donald);
  forms that need both friends are for one hero at a time. Memory use is measured, not assumed.
- Limits and team moves with Donald, Goofy and guests work for either hero.
- Boss fights and forced events: both heroes are placed correctly at the start and after cutscenes.
- Minigames, vehicles, mounts, the Gummi Ship and every other special mode: BOTH players play at the same time,
  each with their own independently controlled vehicle or character (rule 7, section 4B). Each mode gets a
  feasibility test first; an exception needs proof and the user's OK. None is left silently broken.
- **Soul test:** every line of `docs/PARITY-CHECKLIST.md` is checked by two human players: first visit of every
  world, every mission, minigame and boss, with both players in direct control the whole time.

### Phase 4: P2 grows
(Includes the abilities and equipment each special mode gives or takes away, per the parity checklist.)
- P2 opens the menu with their own pad. P2 has their own Keyblade, abilities and shortcuts.
- Balance for two heroes plus Donald and Goofy: enemy HP and damage, which difficulty to recommend.
- **Soul test:** two hours of play with P2's damage share between 35 % and 65 % in boss fights, and P2 reports
  they never ran out of things to do.

### Phase 5: Made for two
(The full playthrough ticks every line of the parity checklist with two human players.)
- P2 button prompts and command list on screen.
- Camera polish for bosses and small rooms. Cutscene skip by vote. Either player can pause.
- "2 Players" on the title screen, one shared save.
- Launcher: KH2 as a ready game, patch files checked when joining, update zip for your friend
  (friend uses their own disc file and BIOS, same as now).
- **Soul test:** full playthrough from start to credits over the internet, zero "OUT OF SYNC", bug list closed.

### Phase 6 (optional): P2 picks somebody else
P2 may choose a different hero (for example Roxas, Riku or Mickey) or play Donald / Goofy. Only after Phase 5.

## 7. How the work is done

- Evidence, not guesses: every technical claim is marked VERIFIED (with where and how) or HYPOTHESIS.
- I test on this PC with two emulator copies and scripted buttons. You and your friend do the human and internet tests.
- The mod is delivered the way the package already works: patch files that must be identical on both PCs
  (the join check refuses a mismatch). If game files have to change, a small patcher makes the same result on both
  PCs from each player's own disc file. The disc file itself is never shared.
- Failed tests are reported as clearly as passed ones.

## 8. Main risks

1. KH2 sync on PS2-ONLINE is untested (Phase 0 answers it).
2. The engine may refuse a second player character, or accept it only with heavy changes. No public example exists.
   Phase 0's twin test and Phase 1 are the make-or-break; both have a stop and a fallback.
3. PS2 memory (32 MB): two heroes in two different Drive Forms may not fit.
4. One camera for two players in tight rooms and boss arenas.
5. Everything in the game that looks for "the player" (doors, cutscene triggers, chests) must behave with two.

## 9. Decisions needed from the user

1. **Language: decided 2026-11-10, English text** (voices are already English). Both PCs must end up with the
   byte-identical English game file, made from each player's own original disc file. Every address we find
   belongs to that exact file.
