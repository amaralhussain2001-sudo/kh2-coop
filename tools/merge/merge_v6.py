"""Merged build 6 = merged-v5 + OWN DRIVE VALUES FOR THE SECOND HERO ACROSS ROOMS.

What was there (VERIFIED, test v1-drvgain): inside a room each hero's unit slot has its own Drive values
(slot+0x1B0 gauge, +0x1B1 bars, +0x1B2 max bars, +0x1B3, +0x1B4 / +0x1B8 two timers) and each player's hits fill
only his own; each HUD gauge shows its own character's slot (gauge+0x34 -> +0x48C -> +0x1B0..). But both slots
save them into the ONE place of the save data (party block 0x0032E020 + 0x1038 = 0x0032F058, 12 bytes; routine
0x001A1840) and load them from there (0x001A11E0): after a room change both heroes had the values of whoever was
written last.

The glue (two hooks):
  load  0x001A12B4: the second hero's slot (mark bit 31 of slot+0x250, lane D) reads the 12 bytes from its own
        copy instead, IF that copy is valid and the save data still holds what player 1's hero wrote last.
        If the save data was changed by anything else (a loaded save, New Game, the story), both heroes take the
        save data's values and the copy is not valid until the second hero is written again.
        Max bars are always the save data's (common).
  save  0x001A18C0 (+ 0x001A18C4): the second hero's slot writes the 12 bytes into its own copy (never into the
        save data); player 1's slot writes the save data as before and the glue remembers what it wrote.
  refill 0x001ADBEC: the game's one "full Drive" routine (0x001ADBC0) refills the second hero too.
The copy lives in memory only: a save on the memory card holds player 1's Drive values; after loading, both
heroes start with those. Max bars and Drive levels stay common (the same character record).

Routines 0x000F4600.., variables 0x000F47C0 (valid), 0x000F47C4 (what player 1 wrote last), 0x000F47D0 (the
second hero's copy). They rely on zero memory at boot (0x000F4000-0x000F4FFF was lane S1's range, never used).

SECOND GLUE: TEXT BOXES LISTEN TO EITHER CONTROLLER.
What was there (VERIFIED, lane S1 item G1 and test y1-box-plain): tutorial boxes and dialogue advance only on
controller 1; player 2 can open a dialogue but not close it. The message window's update (0x001ACBC0) asks for
logical controller 0 (call at 0x001ACBD4; found by a bit-coded search over the 43 getter calls, tests y2-bit0..5:
only with this call switched did player 2's Circle close the box). Now that call gets a scratch record
(0x000F4800, 0x60 bytes): the button words of both controllers OR-ed (+0x00..+0x2F), the stick part
(+0x30..+0x5F) from controller 1 or, when its stick is at rest, from controller 2. Routine at 0x000F4740.

THIRD GLUE: THE SECOND HERO CAN PICK UP PRIZES (HP orbs, MP, Drive orbs, munny).
What was there (VERIFIED, test v3-orbs): enemies killed by player 2 drop prizes that lie beside his hero and are
not taken; the munny counter (0x0032DF70) rose only when player 1's hero came near. The prize's update
(0x001A5140) asks three characters in turn whether the prize is in their reach (0x001C7950): "party member N" for
N = 0, 1, 2 (0x00176B20: the engine's player, then the two friends). The twin is not in that list.
Now the loop runs to N = 3 (word at 0x001A5258) and the call at 0x001A51F8 goes through prize_cand: with a twin,
N = 3 is the other hero; and so that neither hero wins every prize when both stand in reach, every other prize
(bit 6 of its address) asks the twin at N = 0 and player 1's hero at N = 3. Without a twin N = 3 gives nobody.
Whoever takes the prize gets its HP / MP / Drive; munny goes to the one wallet. Routine at 0x000F4840.
The reach test (0x001A4FF8) uses the asked character's own unit slot (+0x1C4 widens it), and the prize then flies
to whoever took it (0x001C79A0), so both heroes pull prizes in the same way.
NOT changed: a second pickup routine (0x001A5990, reached from 0x001C7ED4 and 0x001D29C0; HYPOTHESIS: item drops)
asks only the engine's player.

FOURTH CHANGE (same routine pad_both): START AND THE MAIN MENU LISTEN TO EITHER CONTROLLER.
Found by the same bit-coded search: START is looked for at the call 0x00138538 (pressed word, bit 0x2; tests
y4-startbit0..5: only the variant with this call switched opened the menu for player 2). The main menu's cursor
routine reads its controller at 0x002893A0 (tests y5-menubit0..5: player 2's Down moved the cursor exactly in
the four variants that had this call switched). The menu pages add "controller 1's buttons" to a common record
through one routine, 0x00287F90 (49 callers; its getter call is at 0x00287FA0). All three calls now get
pad_both's record. The game stops for both players while the menu is open, as it does for one.
(A first reading of the search pointed at 0x002B0960; that call is not the menu's cursor: test y6, first run.)

FIFTH GLUE: THE SECOND HERO'S ATTACK USES HIS OWN LOCK-ON TARGET.
What was there (VERIFIED, tests g1-grand-base, g3-grand-near, g4-grand-twinplayer, g5-plbit0..6): in the
Grandstander job player 2's swings never reached the ball's script as hits (its hit and landing counters stayed 0
and the job stalled); with the engine's player pointer set to the twin they did. A bit-coded search over the 119
loads of that pointer found the one place: routine 0x001874A0 (called from the attack motion's event handler at
0x0018958C for a hero, flag 2 at object+0x588). It asks whether the attacking hero is at, or within a distance
of, the target in the lock-on manager of THE ENGINE'S PLAYER (object+0xB40). Now, when the attacker is the twin,
the twin's own lock-on manager is used (hook 0x001874BC, routine lock_own at 0x000F48C0).
NOT changed: the sister routine 0x00187420 (called from 0x00189AB8; the search showed no effect on the ball).

SIXTH GLUE, AN EXPERIMENT THAT IS NOT IN THE BUILD (option --react): REACTION COMMANDS OFFERED TO BOTH HEROES.
What was there (lane S1 rows TTR-10 and TTR-15; VERIFIED again, tests h1-dusk-p1 / h1-dusk-p2): in the Old
Mansion fight where the Dusk cannot be damaged the story goes on after player 1's attacks (scene by frame 8900)
and never after player 2's; in every fight the prompts went "to S only". The bit-coded search (tests
h2-plbit0..6: the scene came in variants 0, 3 and 4 = index 25) found routine 0x00189E18(source object, command,
argument), reached from 0x00189490: it builds a target record and offers the command to the control object of
THE ENGINE'S PLAYER (object+0xB44): through 0x001BD418 when the source is that player himself, through
0x001BD3E0 when the source is anything else (an enemy, an object); on success it notes the command in the
player object (+0x50C, flag 0x20000 at +0x160).
Now (hook at the routine's entry 0x00189E18, routine react_both at 0x000F4A00): the source is the twin -> the
routine runs once with the twin as "the player" (his own control object, lane G's S2); the source is player 1's
hero -> as before; the source is anything else -> the routine runs twice, for player 1's hero and for the twin.
"The twin as the player" = the pointer 0x0034E948 holds the twin for the length of that one call.
RESULT: neither this nor a first try (only "the twin's own action counts as the player's") let the story go on
(tests h3-dusk-react, twice), and a run with ONLY the load at 0x00189E40 switched did not either (h4-site25).
So the search's reading "index 25 alone" was wrong: more than one of the 119 places is involved. Left out.

SEVENTH GLUE: THE SECOND HERO'S HITS COUNT IN THE MISSION SCRIPTS.
What was there (lane S1 row TTR-10; found 2026-11-11 by decoding the mission files' own scripts,
tools/lane-s1/extract_msn_ai.py, texts in local/analysis/lane-s1/msn): after every hit the damage code
(0x001B3E64 and 0x00176400 -> 0x00186148 -> 0x00196B58) calls the trigger OBJ_DAMAGE (key 6) of the mission
scripts with (damaged object, damage record). Eight mission scripts count a hit only when the attacker
(record+0x10) IS the engine's player (trap_obj_cmp with trap_sysobj_player): tt_dusk_ignore (TT14_MS109),
tt04_ms301 (TT04_MS301) and "ms_attackend" (AL00_MS101, BB01_MS101, CA01_MS101, HE06_MS101, HE19_MS204,
TT08_MS701). So the twin's hits never moved those counters and the story waited for player 1.
(Seifer's tutorial asks trap_sysobj_is_player instead, which is why that counter always counted the twin.)
Now (the jump at 0x00186154 goes to dmg_msn at 0x000F4900): when the attacker in the record is the twin, the
record names the engine's player for the length of the mission scripts' call, then the twin again. Nothing else
reads the record in between; the damaged object's own script has already run.

EIGHTH GLUE: PRIZES THAT FILL A MISSION GAUGE ARE TAKEN BY EITHER HERO.
What was there (read 2026-11-11; the "second pickup routine" of the notes): routine 0x001A5990(prize, gauge
number, amount), the step routine of two prize classes (called from 0x001C7EA8 and 0x001D29A0, amount from the
tables 0x0036E030 / 0x0036E3C8). When THE ENGINE'S PLAYER reaches the prize (0x001C7950) it is collected
(0x001C79A0) and the amount goes into the mission's gauge (0x001D8D08). The twin was never asked, so player 2
could not collect such prizes (HYPOTHESIS for which missions use them: the morale orbs of the Land of Dragons
missions, script trap_obj_scatter_prize_mu, are the likely ones).
Now (jump at the routine's entry 0x001A5990, routine gprize at 0x000F4B00): both heroes are asked; every other
prize (bit 6 of its address, like the fourth glue) asks the twin first.

NINTH GLUE: THE SECOND HERO CAN CHANGE HIS FORM (DRIVE) AND STAYS THE SECOND HERO.
What was there (VERIFIED, tests i7-drive-p2 and j2-drive-p1, roam disc with a Drive kit): player 1's Drive
(Limit Form) works: new body, own menu "Limit / Revert", two views stay. Player 2's Drive broke the game's
two-player state: after the change both screens showed ONE view of the new body. Reason (lane E's note, now
seen): a form change builds the new body directly with the constructor (jal 0x001D0980 at 0x001B6850, inside the
form-change routine; the old body is [s2]), not through the player factory, so none of the merged build's role
rules ran: the new body became the engine's player (camera, exits, HUD owner), shared PLAYER 1'S unit slot, and
when the old body ended the twin pointer was cleared.
The old body's end method (jalr at 0x001B6810, class method +0x20) runs first; there the merged build's rule for
a twin that ends releases his control object and clears the twin pointer. So "the old body is the twin" is noted
at that call (routine form_end, flag V_FT2) and used at the constructor call.
Now (hook at the constructor call, routine form_wrap at 0x000F4C40): when the old body was the twin
 - the search for "Sora's unit slot" finds the twin's own marked slot instead of player 1's (flag V_FT, read by
   form_d2, which replaces lane D's D2 at 0x001A1518: normally a marked slot is never found, during the twin's
   form change only the marked one is), so his HP, MP and Drive values go with him (the game's own write-back and
   load, through lane D's and the first glue's hooks);
 - the new body's slot is marked if it is not (the twin's slot had gone: stats loaded once more, as lane D does);
 - after the constructor the new body is the twin (lane E's pointer), and the engine's player, the last-built
   pointer and the game's attach (camera target, trigger owner, HUD owner, control object S) are player 1's hero's
   again, exactly as lane E's rule does after the factory.
Player 1's form change and one hero alone: unchanged (the constructor is called as before).
Three more things belong to it (found with the frame-by-frame probe tools/own/drv_probe2.py, test k3-drvtrace):
 - THE RECORD'S SLOT. A form change is run by a record (0x20 bytes, pointer 0x00351184; made by 0x001B60E0 /
   0x001B6298). For a real form it asks for "Sora's slot" by id (jal 0x001A1658 at 0x001B6148 / 0x001B6300) and
   the form's gauge and clock are started on THAT slot (0x001B6AB8 -> 0x001A1CC0). That was player 1's slot: the
   twin's new body had no clock and changed back at once, and player 1's gauge showed a form. Now, when the body
   that changes is the twin, that search finds his own slot (routine form_slot, same flag V_FT).
 - THE FORM NUMBER. The game keeps ONE current form (save data 0x0032F054). A request for the form that is
   current is ignored (0x001B6B10), the number is written there on a request (0x001B6BB0) and cleared when a form
   ends (0x001B6C84), and a new room builds the player in it (0x0016F0D0). The second hero now has his own number
   (V_TFORM): asked for him in the request (form_cur), written for him (form_set, form_zero), and used for the
   first-built hero of a room (form_build), who becomes the second hero when player 1's hero is built after him
   (lane E's rule). The save data's number stays player 1's. "First-built = second hero" is used only after two
   heroes have been built in one room once (V_TFV); a hero alone always takes the save data's number.
 - Not changed: the other readers of the save data's number (0x0016E9C0, 0x0016EECC, 0x00198064, 0x001B6C44,
   0x00256110) mean player 1's hero's form.

TENTH GLUE, AN EXPERIMENT THAT IS NOT IN THE BUILD (option --helper): THE SECOND HELPER GOES WITH THE SECOND HERO.
What was there (lane H, and again test l2-mu68-base: both helpers 350-950 units from player 1's hero and
1,600-2,800 from the twin): Donald, Goofy and the guests follow and help the engine's player only; their code
reads that pointer in many places. The user's rule: one helper each.
Now (jump at the entry of 0x0016A950 "an object thinks": it runs the object's script and its action list;
routine helper_think at 0x000F4E80): for the object in party place 2 (0x00348640), while a twin is there, the
engine's player pointer holds the twin for the length of that call. So everything that helper's script asks
about "the player" (where to go, whom to help) means the second hero. The helper in party place 1 and every
other object: unchanged.
(A first try through the helpers' class table, update method +0x0C = 0x0017DC98, changed nothing: test
l3-mu68-helper.)
RESULT: no effect either (same test again: the helper in place 2 stayed 340-680 units from player 1's hero and
about 2,000 from the twin, as without the glue). And the bit-coded search over the 119 loads of the engine's
player pointer (tests l4-helpbit0..6, Land of Dragons camp fight) showed no variant in which a helper went to the
twin. So in a fight the helpers are not led by that pointer at all (HYPOTHESIS: they go for the enemies, which
stood around player 1's hero in that test). A test in a quiet room with the heroes apart is still to do. Left out.

ELEVENTH GLUE: THE SKATEBOARD'S COMMANDS GO TO THE RIDER'S OWN CONTROL OBJECT.
What was there (VERIFIED, test n2-mail-menu on the Mail Delivery disc with a second board: both heroes ride, both
have board mode 1 at object+0xB70, but only player 1's control object has the board menu, id 14; player 2's
stays at the root menu and his screen showed a broken menu, the board menu's pictures with the normal rows):
when a hero gets on a board (trap_skateboard_ride -> 0x002EB890(hero, board) -> 0x00198860(board, 2)) the board
commands are opened on the control object of THE ENGINE'S PLAYER (load at 0x00198910, then 0x001BDB70), and
when the board is left (0x00198970(board), also run first by 0x00198860 for a board that is in use) they are
closed on that one too (load at 0x00198990). VERIFIED with a recorder at 0x001BDBD4 (test n4-mail-dbg): the
object of both routines is the board; the hero is s0 of 0x002EB890.
Now: the ride call (0x002EB8EC) notes the board when the rider is the twin (V_TBOARD); for that board the two
places take the twin (his control object, lane G's S2, object+0xB44); for every other board or vehicle the
engine's player as before (the two routines have 12 and 6 callers). Routines sk_ride, sk_who, sk_off at
0x000F4F00.
(In the first test both riders had been put on ONE board by the mission script, see tools/lane-s1/make_mail.py;
the second ride then "left" the board first, which emptied the note. A second version that compared the
routines' object with the twin was wrong.)

TWELFTH GLUE (not together with the --helper experiment, it uses the same hook): FOR AN OBJECT'S OWN THINKING
"THE PLAYER" IS THE HERO NEARER TO IT.
Idea: many things are written against "the player" in the object's own script (the moving bag of the Seven
Wonders offers its jump-on command after asking trap_sysobj_player; boss scripts take the player for their
scripted moves). Routine near_think (0x000F5000, jump at the entry of 0x0016A950 "an object thinks: its script
and its action list"): for an object that is neither a hero nor a helper (class table 0x00345C08), while a twin
is there, if the twin is nearer to it than player 1's hero (flat distance, positions at object+0x70 / +0x78),
the engine's player pointer holds the twin for the length of that call. A hero who is down (HP 0 in his unit
slot) is never taken: the other one is, whatever the distance.
(Tried on 2026-11-11 and taken out again, because the command they were made for did not move: "the hero in a
scripted move is the player for every object while the move holds the camera", "the twin in such a move thinks
as the player", and the same rules for the callbacks of an object's script, entry 0x0016CCE8. Tests g7-thorn,
g9-thorn. The edit scripts edit_merge_v6_nearest4/5/6.py are the record.) So that object's script, the commands
it offers and the moves it starts mean the nearer hero. Not sticky: the choice is made again at every step.
VERIFIED: the bag ride by player 2 alone (q3-bag-near, r1-bag-p2: gauge 100 -> 0, his own "Jump" prompt) and by
player 1 alone (r1-bag-p1); Twilight Thorn 12,000 frames with both or only player 2 pressing, the "Reversal"
prompt on player 2's screen, no crash (q4-thorn-near, r1-thorn-p2); the other special scenes unchanged (r1-*,
r2-grand-near); all suites in sync; a hero alone unchanged.

THIRTEENTH GLUE: WHEN THE HEROES SPLIT UP, ONE HELPER GOES WITH EACH (option --no-helpers leaves it out).
What was there: Donald, Goofy and the world's guest follow player 1's hero only. Found on 2026-11-11 in a quiet
room with helpers (disc test-s1-hb9f): the helpers are led by the game's own "follow" system (program
0x0010A000-0x0011C400), not by their scripts. Three tasks run it every step: 0x00111F50 (rebuilds the member
table 0x00341708 = leader, helper, helper; the leader is the engine's player, read at 0x00111E98; records the
leader's trail of steps at 0x003A9040; sets the places beside the leader; runs each helper's own update),
0x001122A0 and 0x00112388 (each helper's later updates). Proof: with the read at 0x00111E98 turned to the twin,
both helpers walked to the twin (test w-test-lead0); nine pointers to "the player" held on the twin changed
nothing; the old bit search never tried that read because it had index 0.
The glue: the three task routines are replaced by wrappers (the words that hand their addresses to the task
list at 0x001123F4 / 0x0011241C / 0x0011243C). Each wrapper runs the game's routine for player 1's hero and the
helpers that go with him, then, when a helper goes with the twin, a second time with the twin as the leader, the
twin's helpers in the table and the follow system's leader memory swapped for a second copy (0x000F5840...:
0x00341720-0x0034177F places and steps, 0x003417B0-0x003417DF ground / target / clocks, 0x003A9040-0x003A924F
the trail). The table itself always holds the true members again when a wrapper ends, and the game's own
rebuild (hooked at 0x00111F74) sees only true changes, so the lists that follow the party (0x00135818) are told
nothing new. Who goes with whom (hp_assign, once a step): while the heroes are less than 900 units apart all
helpers go with player 1's hero as before; farther apart, the pairing with the smaller sum of (squared)
distances is taken, one helper each, and kept until the heroes are less than 550 apart again. No twin: the
game's own behaviour, word for word. A helper decides where to walk while HE thinks (0x0016A950), outside
those tasks, so the twelfth glue's hook does the same swap for a helper that goes with the twin (nr_help),
and so do four methods of the helper class (class table 0x00345C08, words +0x08, +0x0C, +0x14, +0x20: hp_meth;
+0x08 runs the helper's follow object, whose states read the place beside the leader at 0x0010E464). The pass
word 0x000F5800 is 1 while the twin's memory is in, so nothing swaps twice.

FOURTEENTH GLUE, AN EXPERIMENT THAT IS NOT IN THE BUILD (option --evrc): THE COMMAND OF A SCRIPTED MOVE TO THE HERO IN THE MOVE.
A boss's scripted move is an event (object 0x0035037C) played from a timeline. When the timeline opens a
Reaction Command window, the event player's callback (0x00197D40, kind 1) hands the command to the engine's
player (0x00197DE0 / 0x00197DE4 -> 0x00196E98(event, hero)). With the twin in the move ("Break Raid" in Twilight
Thorn's throw) the command sat in player 1's menu and only player 1's Triangle started it (tests g7-thorn,
b5 / b6). Now the call goes through ev_rc (0x000F5B00): when exactly one hero carries the "in a scripted move"
bit (object +0x160, 0x4000) and it is the twin, the twin is handed in.
RESULT: no effect (tests h1-thorn-p2tri / h2-thorn-p1tri: "Break Raid" stayed in player 1's menu and only
player 1's Triangle started it). The command is put into the menu somewhere else (the fifteenth glue has it:
the call 0x00196E98 only sets what the event's camera looks at).

FIFTEENTH GLUE (option --no-reactown leaves it out; not together with --react): A HERO'S OWN MOTION OFFERS ITS
COMMAND TO THAT HERO.
What was there (found 2026-11-11 with the recorder tools/own/make_rec_offer.py at the entry of 0x001BD418
"offer a command to a control object's slot", test a1-rec-nopress): while Twilight Thorn throws the twin, "Break
Raid" (command 299) is offered 50 times, once a step, always by the call at 0x00189EF8 with the twin as the
source object and player 1's control object as the receiver. That is routine 0x00189E18(source, command,
argument), the routine of the sixth glue: a motion's own frame trigger (walker 0x00189F20, from the motion
update 0x0017F744 <- 0x001B95D8 <- 0x001B9840) offers a command. The routine takes THE ENGINE'S PLAYER (load at
0x00189E40), offers the command to his control object (+0xB44; 0x001BD418 when he is the source, 0x001BD3E0 when
the source is anything else) and notes it in his object (+0x50C, flag 0x20000 at +0x160). So the command of the
twin's own "being thrown" motion sat in player 1's menu.
Now (hook 0x00189E3C, routine react_own at 0x000F5B80): when the source is the twin, "the player" of that one
routine call is the twin: the offer goes to his own control object (lane G's S2) and the note into his own
object, exactly as the game does it for a hero alone. Any other source (an enemy, an object, player 1's hero):
unchanged.

SIXTEENTH GLUE (option --no-mash leaves it out): THE SCRIPT ENGINE'S TWO BUTTON TESTS LISTEN TO EITHER CONTROLLER.
What was there (read 2026-11-10 / 11): the script built-ins "button held" (0x0016DB98, table entry 0x0034DB30) and
"button pressed" (0x0016DBE0, 0x0034DB38) ask for logical controller 0. No mission script uses them; seven
object scripts do (B_EX170_LAST, B_EX370, B_EX420, F_HB090, F_MU070 ...): the button-mash parts of boss moves.
So a hero on controller 2 who is in such a move could not mash. Now the two getter calls (0x0016DBA8, 0x0016DBF0)
get pad_both's record (the second glue's routine): the buttons of both controllers OR-ed. Either player's
presses count, whoever is in the move.
NOT seen in a game (none of those scenes was reached by a test). The mechanism is the one of the second and
fourth glue (seen working for text boxes, START, the menus, the rules screens).

SEVENTEENTH GLUE (option --no-heal leaves it out): THE HELPERS HEAL THE OTHER HERO TOO.
What was there (read 2026-11-11 and then seen, tests f7-fheal-p2 / f8-fheal-p1h9 on the fight disc test-g-friends
with the kit tools/own/make_healkit.py): a helper's healing actions are entries of a table (Donald's at
0x003460C0: fire, blizzard, thunder, cure ...) with a condition routine each: 0x001140D0 for Cure, 0x00113AE0 for
a healing item, 0x00113D60 for an MP item. Each asks, in this order, the helper himself, his LEADER (place 0 of
the member table 0x00341708) and the other helper (0x00111E20) whether HP (0x0010F6B8) or MP (0x0010F6F8) is
below a rate, and the first one in need becomes the target. The leader is player 1's hero, or the twin for a
helper that goes with the twin after a split (thirteenth glue). So while all are together the twin was never
healed: Donald cured player 1's hero at 7 of 20 HP within 100 frames, and left the twin at 3 and then 0 of 20
for 1,500 frames while he cast attack magic five times.
Now the three calls of 0x00111E20 go through heal_item / heal_mp / heal_cure (0x000F7C00): before the other
helper, the OTHER HERO is asked with the game's own test and rate (the twin when the leader is player 1's hero,
player 1's hero when the leader is the twin). Order now: himself, his leader, the other hero, the other helper.
No twin: the game's own calls, word for word.

EIGHTEENTH GLUE (option --no-limit2 leaves it out): A LIMIT STARTED BY THE SECOND HERO RUNS FOR HIM.
What was there (tests g7-flimit-p2 / g7-flimit-p1 on the fight disc test-g-friends with a Limit kit, and the
recorder test g8-flimit-rec): player 2 can open "Limit" on the menu's second page, the list shows on his screen
and Whirli-Goof starts (his hero and Goofy, his MP goes to 0, Donald leaves). But the Limit's own commands
("Whirli-Goof" and its follow-ups) were put into PLAYER 1's menu, so player 2 could not go on and the Limit
ended after its first move (11 hits, where player 1's own Limit made 76). The commands come from the Limit's
own script: a Limit is an object (pointer 0x01D48CB0, made by 0x001B4430(limit id, hero); +12 = the hero, +52 =
its script), its step 0x001B5250 runs that script (call of 0x0016CD48 at 0x001B5330), and the script's
"set a command" routine (0x00174328, table entry 0x0034E228) takes the control object of THE ENGINE'S PLAYER.
Now (the call at 0x001B5330 goes through limit_run, 0x000F7E00): while the script of a Limit runs whose hero is
the twin, the engine's player pointer holds the twin. Player 1's Limits and a hero alone: the game's own call.

NINETEENTH GLUE (option --no-summon2 leaves it out): A SUMMON CALLED BY THE SECOND HERO IS HIS.
What was there (tests i2-summon-p1 / i2-summon-p2 on the fight disc test-g-friends with a Summon kit: charm bits
save + 0x36C4 = 0x39, Drive Forms present): player 1's Summon works beside a twin. Player 2's does not: the
"Summon" list shows on his screen, the cost is paid from his gauge, Donald and Goofy leave, but his hero stays
in the summon pose (motion 138) inside the light effect for the whole summon time, the summon friend never
appears, and the emulator log has fault lines (null friend, pc 0x0016A070 ...). Reason: the hero's Summon
command (0x001D1380: pose, effect at hero+2920, cost, then 0x001C8300(hero, summon)) starts a task (0x001C83F8)
that asks 0x001D14A0 for "the player object" = the word 0x00352400 = the hero built last = player 1's hero. The
task then waits on, releases and places the friend beside the WRONG hero.
Now: the Summon start notes whether the caller is the twin (sm_start at the jump 0x001D13FC, flag V_SUMTW
0x000F47F4); while that summon is out (its state word 0x01D49968 is not 0; the save byte 0x0032F055 is the
summon's NUMBER and is 0 for Genie, a first version tested it and did nothing), 0x001D14A0 answers the twin (sm_who; its
five users: the summon task, the two script routines 0x001741E0 / 0x00174210 that change the player's form
for a summon friend, and the friend's class at 0x001D04CC / 0x001D0614). SECOND PART (in near_think of the
twelfth glue): a summon friend (class table 0x00351E18, built on the helper class) thinks with the hero who
called him as "the player", not with the nearer one: his "appear" script waits for the PLAYER to stand in the
summon pose (tests i5-summon-p2, i6-sw-p2: with the first part alone the twin stayed in the pose and no scene
came). THIRD PART: the entrance scene itself is not played for a summon the twin calls (sm_skip at the call
0x001C8444): the summon task then takes the game's own path of the Config choice "Summon Effects: None" (the
caller's short motion 130, the friend placed beside him, action "appear_skip"). The friend appears beside the hero
who called him (0x001C84EC used the engine's player), and hits on the friend shorten the caller's summon gauge
(0x001C82C4). FOURTH PART, the one that mattered most (recorder at 0x001C8948, tests j1-rec-p1 / j1-rec-p2): every
hero's own frame routine (0x001D0F08, and 0x001D0D60 at a form's end) sends the summon away when HIS gauge
(unit slot + 436) is empty, he is in no form and the summon's state is 2. The hero who did not call the summon
has an empty gauge, so he dismissed the other hero's summon at once (player 1's hero two frames after player
2's call; the twin did the same to player 1's summon). Now a hero gets the state only for a summon he called
himself (sm_mine at the two calls of 0x001C8AB0). FIFTH PART: the second page of a command menu (0x001BE778,
s1 = the control object) showed "Dismiss" and the summon friend's rows to BOTH players; when the other player
pressed Dismiss the friend left but the caller's gauge stayed a SUMMON gauge (test i12-p1dismiss). Now only the
caller's menu gets those rows (sm_menu at 0x001BE7C8 / 0x001BE7F8); the other player's page keeps "Summon",
and every summon in his list is dim while a summon is out (sm_can at 0x001BC460). Player 1's Summons and a hero alone: the game's own answers.
SIXTH PART (sixth round, option --no-sumroom leaves it out = test build 10's file): A ROOM CHANGE WHILE A SUMMON
IS OUT. What was there (test k6-room-sum-p2, disc test-s1-hb9g, memory probe k8-room-slots): the player
constructors (0x001D095C / 0x001D0A64) give EVERY hero they build a SUMMON gauge (unit slot + 431 = 3) when the
save's summon number is set. After a door the hero who had not called the summon showed the friend's picture and
an empty SUMMON gauge in place of his Drive gauge. The role of a hero is not known inside the constructor (a
twin that is built first looks like player 1's hero until the second one is built), so the gauge is put right a
moment later: each frame the summon friend thinks (nr_sum -> sm_fix), a SUMMON gauge on the hero who did NOT
call him becomes a Drive gauge again (kind 1; his Drive values were loaded as always).

TWENTIETH GLUE (sixth round, option --no-promptguard leaves it out): THE POOL OF PROMPT OBJECTS IS NEVER EMPTIED
BY THE TWIN'S MENU. What was there (tests k16 to k22, disc test-s1-tt157, lane S1's long scripts "thorn-p2",
builds 9 to 11 before this glue; NOT with --no-reactown): late in the first boss fight the emulator log got 50
fault lines in one frame (frame 11412, pc 0x0013E2D8 ... 0x00237A68, addresses 0x41AFxxxx). The green prompt
of a command is an object from a pool of 9 (manager at [0x003486A4], 896 bytes each, free count at +8100,
index stack at +8064; take 0x0013E610, give back 0x0013E378 when the object's closing has run out). The routine
that takes one has NO test for "empty": with a free count of 0 it reads an index from the last object's own
data and writes the new object to a senseless address. After the twin's own command (fifteenth glue) the
record of HIS control object (0x000F19F8, routine 0x0019D588 "set the prompt's kind") asked for a new object
45 times in the "Reversal" part of the fight without the old ones coming back (free count 9 -> -5). Why his
are not given back is NOT understood (HYPOTHESIS: something clears the record's object word without the
release 0x0019D548). The guard: when fewer than 3 objects are free, a request for the twin's menu gets none
(0 = no object; the record asks again at its next change). Player 1's menu and a hero alone: the game's own
routine. So the pool can no longer go below 0; in such a fight the twin's green prompt may be missing for a
while (the command itself is in his menu).

TWENTY-FIRST GLUE (seventh round, option --no-bigpool leaves it out = test build 11's file): THE POOL OF PROMPT
OBJECTS HOLDS 18, NOT 9. This is the ROOT CAUSE behind the twentieth glue, found with a timeline of the pool
(tools/own/pool_trace_probe.py, test r1-pooltrace-sh on the patch without the guard): the twin's prompt objects
do NOT come back late. Every prompt object needs 10 frames (5 game steps) to close before it goes back to the
pool, for either player. In the "Reversal" part of the first boss fight the boss offers the command from a new
place every step; each change makes a record close its prompt and take a new one. One record alone can hold
1 open + 5 closing = 6 objects: the game's pool of 9 was made for ONE record. With two heroes there are two
records (player 1's 0x01C5FF28 and the twin's 0x000F19F8), both change in the same step, and together they
need up to 12 (seen: free count 7 -> 0 -> -2 in ten frames, both records taking one object per step).
Now the pool has 18 objects = the game's own number for each of the two records: the 13 words below (the
size of the block, the loop that builds the objects, the place of the index stack and of the free count in
the four routines that use them: build 0x0013E688, take 0x0013E610, give back 0x0013E378, end 0x0013E808).
8,096 bytes more from the game's heap. The guard of the twentieth glue stays (it reads the free count at its
new place) for cases nobody has seen.

TWENTY-SECOND GLUE (seventh round, option --no-snaptwin leaves it out): THE GAME'S CONTINUE SNAPSHOT ALSO HOLDS
THE SECOND HERO'S OWN VALUES. What was there (sixth round, test k14-sumdieB): the game keeps a snapshot for
Continue (the whole save data, taken at a room load by 0x001CD168, put back by 0x001CD388). The second hero's
own Drive / form / Summon values are not in the save data (first glue: his copy 0x000F47D0, "valid" 0x000F47C0,
"what player 1 wrote last" 0x000F47C4; ninth glue: his form number 0x000F47E8; nineteenth glue: "the twin
called the summon" 0x000F47F4). After a Continue the save data was the snapshot's again, so it no longer held
"what player 1 wrote last": the twin took player 1's values. His Summon that had come into the room with him
lost its gauge and left at once; a form he had entered the room in had no clock of his own.
Now: when the snapshot is taken, those words go into a second copy (0x000F7F38-0x000F7F6F, the same layout as
0x000F47C0-0x000F47F7; flag 0x000F7F34 = the copy belongs to the snapshot); when the snapshot is put back, they
come back with it; when the load menu fills the snapshot from a saved game (0x001CD2B8), the flag is cleared
(a saved game has no values of the twin: both heroes take the save's, as before). So after a Continue the
second hero is what he was when he came into the room, exactly as player 1's hero is. The board note
(0x000F47F0, an object address) is never put back. Three hooks, each in place of one "load a constant"
instruction of those routines (snap_take 0x001CD180, snap_put 0x001CD398, snap_none 0x001CD2D0); routine at
0x000F4980-0x000F49F3 (free between the seventh glue and the --react experiment).

TWENTY-THIRD GLUE (seventh round, option --no-healwho leaves it out): AN ITEM USED BY A HELPER GOES TO THE HERO
WHO NEEDS IT. What was there (test r19-hitems-p2, fight disc test-g-friends, Donald and Goofy carry Potions,
the twin at 3 of 20 HP): the seventeenth glue lets a helper choose the other hero as the one in need, and
Goofy did use his Potion, but the Potion healed PLAYER 1's hero (15 -> 20) and the twin stayed at 3. Reason: a
used item is applied by CHARACTER number, both heroes have the same number, and lane N's rule for that case
(n_heal at 0x000F2A9C, the call 0x001BA624) says "used by player 1's hero OR A FRIEND: the hero gets it, the
twin only when the twin is down". That rule was written before helpers could aim at the twin.
Now (the branch at 0x000F2B1C of n_heal goes through heal_who, 0x000F4F80): when the user is neither hero (a
helper, a guest), the item goes to the hero who has less of his HP (HP x the other's most HP, compared; a hero
who is down has 0 and so comes first). Used by player 1's hero or by the twin: lane N's rule, unchanged.

TWENTY-FOURTH GLUE (seventh round, option --no-wmpad leaves it out; needs the second glue's pad_both): THE WORLD
MAP LISTENS TO EITHER CONTROLLER. What was there (lane S3, and again test r30-worldmap-p2): the world map's
cursor ship is a player-type object of its own class (table 0x00361D00), built at 0x002C5EE0 with logical
controller 0 (call at 0x002C5F08); it keeps that pointer. Player 2 could answer "Jump to World Map? Yes" in the
save menu, and then his stick and buttons did nothing on the map. Now the cursor is built with pad_both's
record (both controllers' buttons, the stick of whoever moves it), and because nobody else asks for that record
on the world map, the cursor's per-frame method (class word +0x0C at 0x00361D0C, the game's 0x00178758) first
goes through wm_tick, which fills the record again every frame.

TWENTY-FIFTH GLUE (seventh round, option --no-nullguard leaves it out): TWO GAME ROUTINES NO LONGER READ THROUGH A
NULL POINTER. Both are the game's own code; with two heroes they are reached with "nothing found" more often
than with one, and each such time wrote "TLB Miss" lines into the emulator log (the emulator gives 0 for such a
read and drops such a write, so the game went on; a real PS2 would have read and written its lowest memory).
 (1) The loader's "give me the record of this object file" (0x001708F8): when the record is not in the list it
     calls an empty report routine (0x00170E58) and then reads and WRITES the record all the same (pc 0x00170930
     / 34 / 40, addresses 2 and 0x30). Reached when the twin is built in a new room while he is in a Drive Form:
     the room's preload knows player 1's form only (three lines a room, fifth round, part 4). Now the call of
     the report routine (0x00170928) goes through lf_guard: no record = the routine ends with 0, which is what
     the emulator's reads gave.
 (2) The script call trap_effect_pos (0, 53; routine 0x0016E378): it asks an effect for its body's position and
     copies 16 bytes from the answer, also when the effect has ended and the answer is 0 (pc 0x0016E3C0; 24 to
     32 lines in the long random roam run with magic, sixth section "Null reads"). Now (0x0016E3C0 / C4 go
     through ep_guard): no body = the position is (0, 0, 0, 0), again what the emulator's read gave.
Nothing else changes: with a record / a body the game's own instructions run.

TWENTY-SIXTH GLUE (seventh round, option --no-gummipad leaves it and the twenty-seventh out): IN THE GUMMI MENU
(AND IN A FLIGHT WITH ONE SHIP) CONTROLLER 1 ALSO LISTENS TO CONTROLLER 2. What was there (lane S3): the flight
and its menus are code modules of their own that ask for logical controller 0 in 6 + 35 places; player 2's
controller does nothing there, he watches. The game's controller task (0x00167618) fills the two logical
controller records once a frame (0x00167E70 calls 0x00167D68 for each). The second call (0x00167E90) goes
through gm_pad. A record is: +0x00 held, +0x08 pressed, +0x10 released, +0x18 repeat (64 bits each; the eight
logical buttons 0x1 reset, 0x2 START, 0x4 confirm, 0x8 cancel, 0x10/20/40/80 up/down/left/right, table
0x0036B628), +0x20 left stick, +0x30 right stick (x, y, 0, strength), +0x40 repeat clock, +0x44 the pad it
reads, +0x48 flags. gm_pad merges "record 1 into record 0": the four button words are OR-ed, and a stick of
controller 1 that is at rest (strength 0) takes controller 2's. It never touches +0x40 and up. (My first
version copied +0x30..+0x5F and so gave record 0 controller 2's pad pointer: player 1's buttons were dead in
the Gummi Menu. Found by test g3-p1menu against the no-patch control g4-stock-menu, fixed before any build.)
When it merges: the Gummi Menu module is in memory (0x62B0 at 0x01F18014) and the place is the world map
(world byte 0x0F at 0x0032BAE0); or the game mode word 0x0032BA24 is 2 (flight) and the rules of the
twenty-seventh glue below say so. (The Gummi Menu of a route runs with mode 1, not 3: test g1-gum-p2.)

TWENTY-SEVENTH GLUE (seventh round, option --no-ship2 leaves it out; it lives inside the twenty-sixth): A SECOND
GUMMI SHIP FOR PLAYER 2. This is lane S3's test patch "ship2own" (docs/lanes/S3-gummi-ship.md), moved into the
build. The flight module (ovl_gumibattle.x at 0x01F18000) is loaded for every flight, so gm_pad looks once a
frame: module signature 0x636A, and its three words still the game's own -> it writes the three hooks and
forgets the ships of the last flight. The hooks: (1) 0x01F21CD4 (was jal 0x01F20DD8), right after the game has
built the player's ship: g2_build builds a second player ship with the module's own constructor on logical
controller 1 and makes ship 1 "the player ship" (0x01F7DE44) again; ship 2's own offset from the flight path
starts 90 to the side. (2) the class table word 0x01F81068 (the player ship's update, was 0x01F219A8): g2_wrap
gives ship 2 ship 1's state (flying in, control, done, destroyed) and runs the game's update with ship 2's own
offset in the game's one offset place (0x01F7DEE0), then puts player 1's back. (3) 0x01F2191C (the end of the
fire handler, was j 0x01F1EE00): g2_fire runs the two fire routines for ship 2 as well.
The controllers in a flight with two ships: while ship 1 is under control (state 2) the records stay apart
(each player flies his own ship); only player 2's START reaches record 0, so he can pause. When the flight
stands still (no update of ship 2 for 8 frames: the pause menu) or ship 1 is not under control (flying in,
results, destroyed, "retry?"), the records are merged and either controller answers.
What ship 2 does NOT have (lane S3, seen again here): it is never damaged; the mission ends with ship 1; one
score, one hull gauge. Data: 0x000F2600-0x000F2653.

HOW THE MERGE IS DONE (both glues above and the one below; gm_pre at the call 0x00167E84, gm_pad at 0x00167E90):
"held" of record 0 becomes held-by-either; "pressed" = held by either now and by neither at the last frame;
"released" the other way round; "repeat" of either. So a button one player holds is one press, not one a frame.
Before the game updates record 0 again, gm_pre gives it controller 1's own held word back (kept at +0x40 of
the data), so the game's own pressed / released of controller 1 stay right. t9 says which of controller 2's
buttons take part: all, or START only (a flight with two ships).

TWENTY-NINTH GLUE (seventh round, option --no-ridetwin leaves it out; needs the eleventh): THE RIDE COMMANDS OF A
SPECIAL PLAYER OBJECT THAT IS PLAYER 2'S GO TO PLAYER 2'S MENU. Disc v5 puts a second Light Cycle, a second Pooh
flyer and a second carpet rider into the rooms. Such an object opens its own command set ("Attack / Charge /
Guard" on the cycle) in its constructor through the routine the skateboards use (0x00198860(vehicle, kind); the
vehicle is the hero himself here), and that routine takes the control object of THE ENGINE'S PLAYER (the eleventh
glue's finding). So player 2's cycle was steered by his stick, but his Circle and Square did nothing (test lc-p2:
no attack action 0xB8, no guard 0xBC; lc-p1: player 1 has both). Now the two places (0x00198910 open, 0x0019898C
close) go through sk_who2 / sk_off2: the eleventh glue's rule, and before the engine's player is taken: a vehicle
whose own control object pointer (+0xB44) is the twin's (0x000F1000) is a hero of player 2 and gets the commands
himself. Routines at 0x000F2680.

TWENTY-EIGHTH GLUE (seventh round, option --no-notwin leaves it out; it lives inside the twenty-sixth): WHEN
PLAYER 2 HAS NO HERO, HIS CONTROLLER ALSO DRIVES THE ONE HERO. Where the disc gives player 2 no hero (a special
player object without a second copy: the carpet escape, the sidecar, the toy cannon; and whatever nobody has
found yet), he used to watch. Now: outside a Gummi flight, when lane E's twin pointer 0x000F05CC has been 0 for
30 frames in a row (so not in the moment a room is built or the twin's object is exchanged), the records are
merged as above. The hero reads logical controller 0 (lane A: object + 0xB38), so either player
moves, jumps and attacks with him; the menus and scenes without any hero listen to either controller too (the
second glue's pad_both already did that for text boxes, START, the main menu and the rules screens).
With a twin nothing changes: each controller has its own hero.

  python -I tools/merge/merge_v6.py [outDir] [--no-ridetwin] [--no-notwin] [--no-ship2] [--no-gummipad] [--no-nullguard] [--no-wmpad] [--no-healwho] [--no-snaptwin] [--no-bigpool] [--no-drive] [--no-box] [--no-start] [--no-prize] [--no-lock] [--no-msn] [--no-gprize] [--no-form] [--no-board] [--no-helpers] [--no-nearest] [--no-reactown] [--no-mash] [--no-heal] [--no-limit2] [--no-summon2] [--no-sumroom] [--no-promptguard] [--helper] [--react]

Writes <outDir>/SLPM-66675_F266B00B.pnach and <outDir>/listing.txt. Default outDir: patches/merged-v6.
"""
import hashlib
import pathlib
import re
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
from asm import assemble  # noqa: E402
import mips  # noqa: E402

NAME = "SLPM-66675_F266B00B.pnach"
BASE = ROOT / "patches" / "merged-v5"
LINE = re.compile(r"^patch=(\d),EE,([0-9A-Fa-f]{8}),(\w+),([0-9A-Fa-f]{8})\s*(?://.*)?$")
GLUE_AT = 0x000F4600
GLUE_END = 0x000F47C0
O_VALID, O_LAST, O_OWN = 0x47C0, 0x47C4, 0x47D0      # offsets from 0x000F0000
OWN_BASE = 0x000F0000 + O_OWN - 0x1038               # so that base + 0x1038.. is the second hero's copy

SRC = """
dr_load:                          # hook 0x001A12B4 (jal). s0 = slot. Out: t5 = base of the Drive bytes (+0x1038..)
    lw t5,608(s0)                 # the instruction that sat there: the party save block (0 = not a hero)
    beq t5,zero,dl_out
    lw t4,0x250(s0)
    bgez t4,dl_out                # no mark: player 1's hero (or a hero alone)
    lui t4,0x000F
    lw t3,0x1038(t5)
    lw t2,{O_LAST}(t4)
    bne t3,t2,dl_ext
    lw t3,0x103C(t5)
    lw t2,{O_LAST4}(t4)
    bne t3,t2,dl_ext
    lw t3,0x1040(t5)
    lw t2,{O_LAST8}(t4)
    bne t3,t2,dl_ext
    lw t3,{O_VALID}(t4)
    beq t3,zero,dl_out            # the second hero has no values of his own yet: the saved ones
    lbu t3,0x103A(t5)             # max bars stay common: the save data's (player 1's hero wrote them)
    sb t3,{O_OWN2}(t4)
    lui t5,%hi(OWN_BASE)
    jr ra
    addiu t5,t5,%lo(OWN_BASE)     # his own copy
dl_ext:                           # the save data does not hold what player 1 wrote last (a loaded save, New Game,
    sw zero,{O_VALID}(t4)         # the story): both heroes take it; remember it as the common start
    lw t3,0x1038(t5)
    sw t3,{O_LAST}(t4)
    lw t3,0x103C(t5)
    sw t3,{O_LAST4}(t4)
    lw t3,0x1040(t5)
    sw t3,{O_LAST8}(t4)
dl_out:
    jr ra
    nop

dr_save:                          # hook 0x001A18C0 (j; 0x001A18C4 is now a nop). a0 = slot. Leaf routine: t-regs only
    lw t5,608(a0)                 # the instruction that sat there
    bne t5,zero,ds_go
    lw t4,0x250(a0)
    jr ra                         # not a hero's slot (the routine's own end)
    nop
ds_go:
    bgez t4,ds_p1
    lui t3,0x000F
    li t4,1
    sw t4,{O_VALID}(t3)           # the second hero: into his own copy
    lui t5,%hi(OWN_BASE)
    j 0x001A18CC
    addiu t5,t5,%lo(OWN_BASE)
ds_p1:
    lw t4,0x1B0(a0)               # player 1's hero: into the save data as before; remember the 12 bytes
    sw t4,{O_LAST}(t3)
    lw t4,0x1B4(a0)
    sw t4,{O_LAST4}(t3)
    lw t4,0x1B8(a0)
    j 0x001A18CC
    sw t4,{O_LAST8}(t3)

dr_refill:                        # hook 0x001ADBEC (jal 0x001A1C70): the game refills the hero's Drive (its only
    addiu sp,sp,-16               # "full Drive" routine, 0x001ADBC0). a0 = player 1's slot
    sd ra,0(sp)
    jal 0x001A1C70
    nop
    lui t7,0x000F
    sw zero,{O_VALID}(t7)         # a stored copy of the second hero is out of date: he takes the refilled values
    lw t6,0x05CC(t7)              # the twin's object (lane E's pointer, 0 = none)
    beq t6,zero,drf_out
    nop
    lw a0,0x48C(t6)               # his slot: refilled too
    beq a0,zero,drf_out
    nop
    jal 0x001A1C70
    nop
drf_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""
BOX_AT = 0x000F4740
BOX_END = 0x000F47C0
BOX_SCRATCH = 0x000F4800
BOX_SRC = """
pad_both:                         # hook 0x001ACBD4 (jal, was the getter with a0 = 0). Out: v0 = a record like a
    lui t7,0x0035                 # logical controller. t2-t7
    addiu t6,t7,-10560            # 0x0034D6C0: logical controller 0 (controller 1 is 0x60 further)
    lui v0,%hi(BOX_SCRATCH)
    addiu v0,v0,%lo(BOX_SCRATCH)
    addiu t3,t6,0x30
    move t2,v0
pb_or:                            # +0x00..+0x2F: button words (held, pressed, ...) of both controllers
    ld t5,0(t6)
    ld t4,0x60(t6)
    or t5,t5,t4
    sd t5,0(t2)
    addiu t6,t6,8
    bne t6,t3,pb_or
    addiu t2,t2,8
    lw t5,0x0C(t6)                # controller 0's stick strength (+0x3C)
    bne t5,zero,pb_copy
    addiu t3,t6,0x30
    addiu t6,t6,0x60              # at rest: controller 1's stick part
    addiu t3,t3,0x60
pb_copy:                          # +0x30..+0x5F
    ld t5,0(t6)
    sd t5,0(t2)
    addiu t6,t6,8
    bne t6,t3,pb_copy
    addiu t2,t2,8
    jr ra
    nop
"""
BOX_HOOKS = (                     # (call of the getter, the word in its delay slot, what)
    (0x001ACBD4, 0x0000202D, "the message window asks for its controller: both controllers' buttons"),
    (0x00138538, 0x0000202D, "START (open the main menu) is looked for: on both controllers"),
    (0x002893A0, 0xA60F0014, "the main menu's cursor routine reads its controller: both controllers"),
    (0x00287FA0, 0x00000000, "the menu pages' 'add controller 1's buttons' routine (0x00287F90, 49 users): both controllers"),
    (0x0027DB64, 0x0000202D, "a mission's rules screen (routine 0x0027DB58) waits for a button: on both controllers"),
    (0x0013C798, 0x00000000, "the command menu is revealed by the first button press (0x0013C738): on either controller"),
)

HEAL_AT = 0x000F7C00              # seventeenth glue (the unused end of lane V2's range, zero in a run: probe e2-sheet)
HEAL_END = 0x000F7D40
HEAL_SRC = """
heal_h2:                          # common part. t8 = the target list, t9 = the game's "is in need" test (a0 = a
    addiu sp,sp,-48               # character, f12 = the rate), a0 = the helper. Out: v1 = 1 when the other hero is
    sd ra,0(sp)                   # in need; a0 as it came
    sd a0,8(sp)
    sd t8,24(sp)
    sd zero,32(sp)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin (lane E's pointer, 0 = none)
    beq t6,zero,hh_out
    lui t5,0x0034
    lw t4,5896(t5)                # 0x00341708: this helper's leader (place 0 of the member table)
    bne t4,t6,hh_have             # the leader is player 1's hero: the other hero is the twin
    lui t5,0x0035
    lw t6,-5816(t5)               # the leader is the twin (the heroes are split): the other hero is player 1's
hh_have:
    beq t6,zero,hh_out
    sd t6,16(sp)
    beq t6,t4,hh_out
    nop
    jalr t9
    move a0,t6
    beq v0,zero,hh_out
    li t7,1
    sd t7,32(sp)
    jal 0x00190140                # has the list a target already?
    ld a0,24(sp)
    beq v0,zero,hh_set
    ld t8,24(sp)
    lw t7,0(t8)
    bne t7,zero,hh_out
    nop
hh_set:
    ld a0,24(sp)
    ld a1,16(sp)
    jal 0x00190878                # the other hero is the target
    move a2,zero
hh_out:
    ld v1,32(sp)
    ld ra,0(sp)
    ld a0,8(sp)
    jr ra
    addiu sp,sp,48

heal_item:                        # call at 0x00113C10 (was: jal 0x00111E20, a0 = the helper): a healing item.
    addiu sp,sp,-16               # s0 = the list, s5 = how many are in need
    sd ra,0(sp)
    lui t7,0x0037
    lwc1 f12,-23160(t7)           # 0x0036A588: the HP rate of the game's own tests in this routine
    lui t9,0x0010
    ori t9,t9,0xF6B8              # 0x0010F6B8: HP below the rate?
    jal heal_h2
    move t8,s0
    addu s5,s5,v1
    ld ra,0(sp)
    j 0x00111E20                  # then the game's last candidate, the other helper
    addiu sp,sp,16

heal_mp:                          # call at 0x00113E58: an MP item. s0 = the list, f20 = the rate, s5 = how many
    addiu sp,sp,-16
    sd ra,0(sp)
    mov.s f12,f20
    lui t9,0x0010
    ori t9,t9,0xF6F8              # 0x0010F6F8: MP below the rate?
    jal heal_h2
    move t8,s0
    addu s5,s5,v1
    ld ra,0(sp)
    j 0x00111E20
    addiu sp,sp,16

heal_cure:                        # call at 0x00114214: Cure. s2 = the list, f20 = the rate
    addiu sp,sp,-16
    sd ra,0(sp)
    mov.s f12,f20
    lui t9,0x0010
    ori t9,t9,0xF6B8
    jal heal_h2
    move t8,s2
    ld ra,0(sp)
    j 0x00111E20
    addiu sp,sp,16
"""
HEAL_HOOKS = (                    # (call of 0x00111E20, the word in its delay slot, routine, what)
    (0x00113C10, 0x8E440004, "heal_item", "a helper's healing item: the other hero is asked before the other helper"),
    (0x00113E58, 0x8E440004, "heal_mp", "a helper's MP item: the same"),
    (0x00114214, 0x8E640004, "heal_cure", "a helper's Cure: the same"),
)

LIMIT_AT = 0x000F7E00             # eighteenth glue
LIMIT_END = 0x000F7E80
LIMIT_SRC = """
limit_run:                        # call at 0x001B5330 (was: jal 0x0016CD48; a0 = the Limit's script, a1 = 0).
    lui t7,0x000F                 # s0 = the Limit object (+12 = the hero who does it)
    lw t6,0x05CC(t7)              # the twin (lane E's pointer, 0 = none)
    beq t6,zero,lr_plain
    lw t5,12(s0)
    bne t5,t6,lr_plain            # player 1's hero does it: as it is
    lui t4,0x0035
    addiu sp,sp,-16
    sd ra,0(sp)
    lw t3,-5816(t4)
    sd t3,8(sp)
    jal 0x0016CD48                # the twin's Limit: its script runs with the twin as "the player"
    sw t6,-5816(t4)
    ld t3,8(sp)
    lui t4,0x0035
    sw t3,-5816(t4)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
lr_plain:
    j 0x0016CD48
    nop
"""
LIMIT_HOOK = (0x001B5330, 0x0C05B352, 0x0000282D, "a Limit's own script runs: for the hero who does the Limit")

SUMMON_AT = 0x000F7D40            # nineteenth glue
SUMMON_END = 0x000F7E00
V_SUMTW = 0x000F47F4              # 1 = the summon that is out was called by the twin
SUMMON_SRC = """
sm_start:                         # the jump at 0x001D13FC (was: j 0x001C8300). a0 = the hero who summons
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin (0 = none)
    xor t6,t6,a0
    sltiu t6,t6,1
    j 0x001C8300
    sw t6,{O_SUMTW}(t7)
sm_who:                           # in place of 0x001D14A0 "the player object" (the summon task, two script
    lui t7,0x0035                 # routines of the summon friends, the summon friend's class). Uses t5-t7
    lw v0,9216(t7)                # 0x00352400: the game's own answer (player 1's hero)
    lui t6,0x000F
    lw t5,{O_SUMTW}(t6)
    beq t5,zero,sw_out
    lui t5,0x01D5
    lw t5,-26264(t5)              # 0x01D49968: the summon's state (0 = no summon is out; 2 being called / out,
    beq t5,zero,sw_out            # 1 its entrance scene, 3 being dismissed)
    lw t6,0x05CC(t6)
    movn v0,t6,t6                 # the twin called it: he is the player of this summon
sw_out:
    jr ra
    nop
sm_skip:                          # call at 0x001C8444 (was: jal 0x001C8788 "is the entrance scene played?").
    lui t7,0x000F                 # a0 = the summon's number, a1 = the hero who called (never 0)
    lw t6,0x05CC(t7)
    bne a1,t6,ss_game
    nop
    jr ra                         # the twin calls: no entrance scene, the game's own "Summon Effects: None" way
    move v0,zero                  # (the scene is written for the engine's player)
ss_game:
    j 0x001C8788
    nop
sm_t6:                            # call at 0x001C82C4 (was: lw t6,-5816(t7)): the summon friend was hit, the
    addiu sp,sp,-16               # summon gauge of ... the hero who called him goes down
    sd ra,0(sp)
    sd v0,8(sp)
    jal sm_who
    nop
    move t6,v0
    ld v0,8(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""
SUMMON2_AT = 0x000F7E80           # nineteenth glue, second block (0x000F7E80-0x000F7EFF)
SUMMON2_END = 0x000F7F00
SUMMON2_SRC = """
sm_mine:                          # calls at 0x001D1028 and 0x001D0E7C (were: jal 0x001C8AB0 "the summon's state").
    lui t7,0x000F                 # s0 = a hero whose own gauge is empty and who is in no form: the game then lets
    lw t6,0x05CC(t7)              # him send the summon away. Only the hero who called it may do that
    xor t6,t6,s0
sm_cmp:
    sltiu t6,t6,1                 # 1 = the one who asks is the twin
    lw t5,{O_SUMTW}(t7)
    bne t6,t5,sm_no
    lui t7,0x01D5
    jr ra
    lw v0,-26264(t7)              # his own summon: the game's answer
sm_no:
    jr ra
    move v0,zero                  # the other hero's summon: "no summon is out" for him
sm_menu:                          # calls at 0x001BE7C8 and 0x001BE7F8 (were: jal 0x001C8AB0): the second page of a
    lui t7,0x000F                 # command menu is built, s1 = its control object (0x000F1000 = the twin's).
    ori t6,t7,0x1000              # "Dismiss" and the summon friend's rows only in the menu of the player who
    b sm_cmp                      # called the summon; the other player keeps his own page with "Summon"
    xor t6,t6,s1
sm_can:                           # call at 0x001BC460 (was: jal 0x001BC050, one of the tests "can this summon be
    lui t7,0x01D5                 # called now?"; not 0 = no). While any summon is out nobody can call another one
    lw t7,-26264(t7)              # (the game never asked: its menu showed "Dismiss" in that place)
    bne t7,zero,sc_no
    nop
    j 0x001BC050
    nop
sc_no:
    jr ra
    li v0,1
"""
SUMMON3_AT = 0x000F7F80           # nineteenth glue, part 6 (0x000F7F80-0x000F7FBF; option --no-sumroom leaves it out).
SUMMON3_END = 0x000F7FC0          # NOT 0x000F7F00-0x000F7F33: lane V2's variables live there (own screens write them)
SUMMON3_SRC = """
sm_fix:                           # from nr_sum (a summon friend thinks, every frame): a0 = the friend, t4 = player 1's
    lw t3,{O_SUMTW}(t7)           # hero, t6 = the twin, t5 = 0x00350000, t7 = 0x000F0000. 1 = the twin called him
    movz t2,t6,t3                 # the OTHER hero: the twin if player 1 called,
    movn t2,t4,t3                 #                 player 1's hero if the twin called
    lw t2,0x48C(t2)               # his unit slot
    beq t2,zero,sf_go
    li t1,3
    lbu t0,431(t2)                # the kind of his gauge (1 Drive, 2 form, 3 Summon)
    bne t0,t1,sf_go
    li t1,1
    sb t1,431(t2)                 # a SUMMON gauge on the hero who did not call: a Drive gauge again
sf_go:
    bne t3,zero,nr_twin           # the twin called him: he thinks with the twin as "the player"
    nop
    j nr_body                     # player 1's hero called him: the engine's player as it is
    nop
"""
PROMPT_AT = 0x000F7FC0            # twentieth glue (0x000F7FC0-0x000F7FFF; option --no-promptguard leaves it out)
PROMPT_END = 0x000F8000
PROMPT_SRC = """
sp_alloc:                         # call at 0x0019D5D4 (was: jal 0x0013E610 "take a prompt object from the pool").
    srl t6,s1,12                  # a0 = the prompt's type (set in the delay slot), s1 = the record that asks.
    li t5,0xF1                    # the twin's control object S2 lives at 0x000F1000-0x000F1FFF
    bne t6,t5,sa_go               # player 1's menu: the game's own routine
    lui t7,0x0035
    lw t7,-31068(t7)              # the pool (0x003486A4): 9 objects of 896 bytes, free count at +8100
    lw t7,8100(t7)
    slti t7,t7,3
    beq t7,zero,sa_go             # three or more are free: as the game does it
    nop
    jr ra
    move v0,zero                  # fewer: no prompt object for the twin's menu this time (0 = none, asked again later)
sa_go:
    j 0x0013E610
    nop
"""
PROMPT_HOOK = (0x0019D5D4, 0x0C04F984, "a prompt object for a menu: never the pool's last ones for the twin's menu")

SNAP_AT = 0x000F4980              # twenty-second glue (0x000F4980-0x000F49FF; option --no-snaptwin leaves it out)
SNAP_END = 0x000F4A00
SNAP_SRC = """
snap_take:                        # 0x001CD180 (was: lui t5,0x1) in "take the Continue snapshot" (0x001CD168), after
    lui t1,0x000F                 # the game said yes. t1-t4 are free there; t6 / t7 must stay.
    addiu t2,t1,0x7F38            # to: the copy that belongs to the snapshot
    addiu t1,t1,0x47C0            # from: the twin's own words
    li t3,1
    j snap_copy
    sw t3,-4(t2)                  # 0x000F7F34 = 1: the snapshot has the twin's values
snap_put:                         # 0x001CD398 (was: lui t5,0x1) in "put the snapshot back" (0x001CD388, Continue)
    lui t2,0x000F
    addiu t1,t2,0x7F38
    lw t3,-4(t1)
    beq t3,zero,snap_ret          # a snapshot from the load menu: no values of the twin (both take the save's)
    addiu t2,t2,0x47C0
snap_copy:                        # valid, "player 1 wrote last", the twin's copy (0x20 bytes), his form number
    ld t3,0(t1)                   # (+0x28), "the twin called the summon" (+0x34)
    ld t4,8(t1)
    sd t3,0(t2)
    sd t4,8(t2)
    ld t3,16(t1)
    ld t4,24(t1)
    sd t3,16(t2)
    sd t4,24(t2)
    lw t3,0x28(t1)
    lw t4,0x34(t1)
    sw t3,0x28(t2)
    sw t4,0x34(t2)
snap_ret:
    jr ra
    lui t5,0x1                    # the instruction that sat at both hooks
snap_none:                        # 0x001CD2D0 (was: ori t5,t5,0xFC0) in "the load menu fills the snapshot" (0x001CD2B8)
    lui t1,0x000F
    sw zero,0x7F34(t1)
    jr ra
    ori t5,t5,0xFC0
"""
SNAP_HOOKS = (                    # (address, word expected, label, what)
    (0x001CD180, 0x3C0D0001, "snap_take", "the Continue snapshot is taken: the twin's own values too"),
    (0x001CD398, 0x3C0D0001, "snap_put", "the snapshot is put back (Continue): the twin's own values too"),
    (0x001CD2D0, 0x35AD0FC0, "snap_none", "the load menu fills the snapshot: it has no values of the twin"),
)

HWHO_AT = 0x000F4F80              # twenty-third glue (0x000F4F80-0x000F4FFF, the unused end of the board glue's block)
HWHO_END = 0x000F5000
HWHO_SRC = """
heal_who:                         # from 0x000F2B1C in lane N's n_heal (was: beq t4,zero,n_he_game / nop).
    beq t5,t6,hw_old              # t5 = the user's object, t6 = player 1's hero, s5 = the twin,
    nop                           # t4 / t3 = the twin / the hero is down. Used by player 1's hero: lane N's rule
    lw t7,0x48C(t6)               # used by a helper: the hero who has less of his HP
    lw t8,0x48C(s5)
    beq t7,zero,hw_old
    nop
    beq t8,zero,hw_old
    nop
    lw t0,0(t7)                   # player 1's hero: HP, most HP
    lw t1,4(t7)
    lw t2,0(t8)                   # the twin: HP, most HP
    lw t9,4(t8)
    .word 0x01194018              # mult t0,t0,t9   (player 1's HP x the twin's most HP)
    .word 0x01495018              # mult t2,t2,t1   (the twin's HP x player 1's most HP)
    slt t7,t2,t0
    beq t7,zero,hw_game           # the twin has not less: player 1's hero gets it (the game's routine)
    nop
    j 0x000F2B3C                  # n_he_twin: the effect on the twin's own slot
    nop
hw_old:
    beq t4,zero,hw_game           # (the two instructions that sat at the hook)
    nop
    j 0x000F2B24                  # lane N's rule goes on
    nop
hw_game:
    j 0x000F2B78                  # n_he_game
    nop
"""
HWHO_HOOK = (0x000F2B1C, 0x11800016, 0x00000000, "lane N's item rule: a helper's item goes to the hero who has less HP")

WMPAD_AT = 0x000F4FE4             # twenty-fourth glue (0x000F4FE4-0x000F4FFF, behind heal_who)
WMPAD_END = 0x000F5000
WMPAD_SRC = """
wm_tick:                          # the world map cursor's per-frame method (class word 0x00361D0C, was 0x00178758)
    addiu sp,sp,-16
    sd ra,0(sp)
    jal pad_both                  # fill the both-controllers record again (it keeps a0)
    nop
    ld ra,0(sp)
    j 0x00178758
    addiu sp,sp,16
"""
WMPAD_HOOKS = (                   # (address, word expected, kind, what)
    (0x002C5F08, 0x0C059FC6, "jal_pad", "the world map's cursor is built: with both controllers' record"),
    (0x00361D0C, 0x00178758, "tick", "the cursor's per-frame method: the record is filled every frame"),
)

NULL1_AT = 0x000F7E50             # twenty-fifth glue, part 1 (0x000F7E50-0x000F7E7F, behind the Limit glue)
NULL1_END = 0x000F7E80
NULL1_SRC = """
lf_guard:                         # call at 0x00170928 (was: jal 0x00170E58, the loader's empty "not found" report).
    beq s0,zero,lg_null           # s0 = the record (0 = not in the list). A record with too many users: the game's
    nop                           # routine, back to 0x00170930
    j 0x00170E58
    nop
lg_null:
    jal 0x00170E58                # no record: the report, then the end of 0x001708F8 with the answer 0
    nop                           # (its frame: s0 at 0, ra at 8)
    ld ra,8(sp)
    ld s0,0(sp)
    move v0,zero
    jr ra
    addiu sp,sp,16
"""
NULL2_AT = 0x000F7D1C             # part 2 (0x000F7D1C-0x000F7D3F, behind the heal glue)
NULL2_END = 0x000F7D40
NULL2_SRC = """
ep_guard:                         # from 0x0016E3C0 in trap_effect_pos (were: lq t0,0(v0) / sq t0,0(t7)).
    beq v0,zero,eg_zero           # v0 = the effect body's position (0 = the effect has ended), t7 = 0x004F6360
    nop
    .word 0x78480000              # lq t0,0(v0)
    .word 0x7DE80000              # sq t0,0(t7)
    j 0x0016E3C8
    nop
eg_zero:
    .word 0x7DE00000              # sq zero,0(t7)
    j 0x0016E3C8
    nop
"""
NULL_HOOKS = (                    # (address, word expected, kind, label, what)
    (0x00170928, 0x0C05C396, "jal", "lf_guard", "the loader's record getter: no record = answer 0, nothing read through 0"),
    (0x0016E3C0, 0x78480000, "j", "ep_guard", "trap_effect_pos: an ended effect has the position 0, nothing read through 0"),
    (0x0016E3C4, 0x7DE80000, "nop", None, "(the copy is done in ep_guard)"),
)

GMV = 0x000F2600                  # data of the Gummi glues (0x000F2600-0x000F2653, zero at the start): +0 ship 1,
#                                   +4 ship 2, +8 ship 2's update count, +0xC that count at the last frame,
#                                   +0x10 ship 2's own offset (16 bytes), +0x20 player 1's offset kept during
#                                   ship 2's update (16 bytes), +0x30 frames without an update of ship 2,
#                                   +0x38 records merged at the last frame, +0x40 controller 1's own held word,
#                                   +0x48 what either controller held at the last frame,
#                                   +0x50 frames in a row without a twin
GMPAD_AT = 0x000F2200             # twenty-sixth and twenty-seventh glue (0x000F2200-0x000F25FF: lane H's range
GMPAD_END = 0x000F2600            # behind its routines, which end at 0x000F21E7; lane H has no variables)
GMPAD_SRC = """
gm_pre:                           # call at 0x00167E84 (was: jal 0x00167D68 with a0 = logical controller 0).
    lui t7,0x000F
    lw t6,0x2638(t7)              # were the records merged at the last frame?
    beq t6,zero,gq_go
    nop
    ld t5,0x2640(t7)              # then record 0 gets controller 1's own "held" word back first, so the game's
    sd t5,0(a0)                   # update sees what controller 1 really did
gq_go:
    j 0x00167D68
    nop
gm_pad:                           # call at 0x00167E90 (was: jal 0x00167D68 with a0 = logical controller 1).
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x00167D68                # the game's update of record 1
    nop
    lui t7,0x01F2
    lhu t6,-32748(t7)             # 0x01F18014: which Gummi module is in memory (0x636A flight, 0x62B0 menu)
@SHIP2_INSTALL@
    addiu t9,zero,-1              # t9 = which of controller 2's buttons go into record 0: all of them
    lui t7,0x0033
    lw t5,-17884(t7)              # the game mode word 0x0032BA24: 2 = Gummi flight
    addiu t4,zero,2
    beq t5,t4,gp_flight
    nop
@NOTWIN@
    ori t4,zero,0x62B0
    bne t6,t4,gp_out              # not the flight: the Gummi Menu module, and the place is the world map?
    nop
    lbu t5,-17696(t7)             # the world byte of the place record 0x0032BAE0
    addiu t4,zero,0x0F
    bne t5,t4,gp_out
    nop
    b gp_merge
    nop
gp_flight:
@SHIP2_FLIGHT@
gp_merge:
    lui t7,0x0035
    addiu t6,t7,-10560            # 0x0034D6C0: record 0 (record 1 is 0x60 further). A record (read in 0x001676B0,
    lui t7,0x000F                 # 0x00167CD0): +0x00 held, +0x08 pressed, +0x10 released, +0x18 repeat (64 bits
    ld t0,0(t6)                   # each); +0x20 and +0x30 the two sticks (x, y, 0, strength as floats);
    sd t0,0x2640(t7)              # +0x40 repeat clock, +0x44 its pad, +0x48 flags (never touched here).
    ld t1,0x60(t6)                # Controller 1's own held word is kept for gm_pre.
    and t1,t1,t9
    or t1,t1,t0                   # held by either
    lw t2,0x2638(t7)
    bne t2,zero,gp_have
    ld t3,0x2648(t7)              # (what either held at the last frame)
    ld t4,8(t6)                   # the first merged frame: pressed and released of both records
    ld t5,0x68(t6)
    and t5,t5,t9
    or t4,t4,t5
    ld t5,0x10(t6)
    ld t8,0x70(t6)
    and t8,t8,t9
    b gp_store
    or t5,t5,t8
gp_have:
    nor t4,t3,zero
    and t4,t4,t1                  # pressed = held now, not held before
    nor t5,t1,zero
    and t5,t5,t3                  # released = held before, not held now
gp_store:
    sd t1,0(t6)
    sd t4,8(t6)
    sd t5,0x10(t6)
    ld t4,0x18(t6)
    ld t5,0x78(t6)
    and t5,t5,t9
    or t4,t4,t5
    sd t4,0x18(t6)                # repeat: of either
    sd t1,0x2648(t7)
    addiu t2,zero,1
    sw t2,0x2638(t7)
    bgez t9,gp_ret                # START only: no sticks
    nop
    lw t5,0x2C(t6)                # a stick of controller 1 that is at rest (strength 0) takes controller 2's
    bne t5,zero,gp_rs
    nop
    ld t5,0x80(t6)
    ld t4,0x88(t6)
    sd t5,0x20(t6)
    sd t4,0x28(t6)
gp_rs:
    lw t5,0x3C(t6)
    bne t5,zero,gp_ret
    nop
    ld t5,0x90(t6)
    ld t4,0x98(t6)
    sd t5,0x30(t6)
    b gp_ret
    sd t4,0x38(t6)
gp_out:
    lui t7,0x000F
    sw zero,0x2638(t7)            # not merged at this frame
gp_ret:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""
# twenty-eighth glue (inside gm_pad): player 2 has no hero in this scene -> his controller also drives the one hero.
NOTWIN_SRC = """
    lui t4,0x000F
    lw t3,0x05CC(t4)              # the twin (lane E's pointer)
    beq t3,zero,gn_none
    lw t5,0x2650(t4)              # (for how many frames there has been no twin)
    b gn_twin
    sw zero,0x2650(t4)
gn_none:                          # no twin for 30 frames in a row (half a second): player 2 really has no hero here.
    addiu t5,t5,1                 # (A twin is also gone for a moment when a room is built or his object is
    sw t5,0x2650(t4)              # exchanged; his button presses of that moment must not reach player 1's hero.)
    slti t5,t5,30
    beq t5,zero,gp_merge
    nop
gn_twin:
"""
# twenty-seventh glue, part 1 (inside gm_pad, once a frame): a freshly loaded flight module gets its three hooks.
SHIP2_INSTALL = """
    ori t4,zero,0x636A
    bne t6,t4,gp_noinst           # the flight module is in memory
    lui t3,0x01F2
    lw t5,0x1CD4(t3)              # 0x01F21CD4 still holds the module's own call (jal 0x01F20DD8)
    lui t4,0x0C7C
    ori t4,t4,0x8376
    bne t5,t4,gp_noinst
    lw t5,0x191C(t3)              # 0x01F2191C still holds j 0x01F1EE00
    lui t4,0x087C
    ori t4,t4,0x7B80
    bne t5,t4,gp_noinst
    lui t2,0x01F8
    lw t5,0x1068(t2)              # 0x01F81068 (class table, the player ship's update) still holds 0x01F219A8
    lui t4,0x01F2
    ori t4,t4,0x19A8
    bne t5,t4,gp_noinst
    lui t4,@JAL_BUILD_HI@
    ori t4,t4,@JAL_BUILD_LO@
    sw t4,0x1CD4(t3)              # jal g2_build
    lui t4,@J_FIRE_HI@
    ori t4,t4,@J_FIRE_LO@
    sw t4,0x191C(t3)              # j g2_fire
    lui t4,%hi(g2_wrap)
    addiu t4,t4,%lo(g2_wrap)
    sw t4,0x1068(t2)              # the update of a player ship goes through g2_wrap
    lui t4,0x000F
    sw zero,0x2600(t4)            # a new flight: no ships yet
    sw zero,0x2604(t4)
gp_noinst:
"""
# part 2 (inside gm_pad, in the flight): with a second ship under control the controllers stay apart.
SHIP2_FLIGHT = """
    ori t4,zero,0x636A
    bne t6,t4,gp_merge            # mode 2 without the flight module: the Gummi Menu after a failed flight (seen in
    lui t4,0x000F                 # the route 4 run): either controller, and the old ships are not looked at
    lw t5,0x2604(t4)              # ship 2
    beq t5,zero,gp_merge          # none (the module was not hooked in time): both controllers fly the one ship
    lw t5,0x2600(t4)              # ship 1
    beq t5,zero,gp_merge
    nop
    lw t5,0x50C(t5)               # ship 1's state: 2 = under control. Before and after (flying in, results,
    addiu t3,zero,2               # destroyed, the menus there): either controller answers
    bne t5,t3,gp_merge
    lw t5,0x2608(t4)              # ship 2's update count now and at the last frame
    lw t3,0x260C(t4)
    sw t5,0x260C(t4)
    bne t5,t3,gp_run
    lw t3,0x2630(t4)              # frames without an update of ship 2
    addiu t3,t3,1
    sw t3,0x2630(t4)
    slti t3,t3,8
    beq t3,zero,gp_merge          # 8 frames without one: the flight stands still (its pause menu): either controller
    nop
    b gp_start
    nop
gp_run:
    sw zero,0x2630(t4)
gp_start:                         # flying: of player 2's logical buttons only START (0x2: the pause) reaches record 0
    b gp_merge
    addiu t9,zero,2
"""
# part 3: the three routines the module calls (lane S3's test patch "ship2own", verified there on route 0).
SHIP2_SRC = """
g2_build:                         # the flight module's call at 0x01F21CD4 (was: jal 0x01F20DD8; its delay slot
    addiu sp,sp,-32               # puts ship 1 = s0 into a0), right after the game has built the player's ship
    sd ra,0(sp)
    sd s4,8(sp)
    jal 0x01F20DD8                # the call that was here
    daddu a0,s0,zero
    jal 0x01F19160                # the module's own "new": 0x1440 bytes for a second player ship
    addiu a0,zero,0x1440
    beq v0,zero,gb_out
    daddu s4,v0,zero
    jal 0x00167F18                # logical controller 1 = player 2's
    addiu a0,zero,1
    daddu a0,s4,zero
    daddu a1,v0,zero
    addiu a2,sp,32                # the caller's position vector
    jal 0x01F1E4A8                # the player ship's constructor (object, controller, position, rotation)
    daddu a3,s1,zero              # the caller's rotation vector
    lui t7,0x000F
    sw s0,0x2600(t7)              # ship 1
    sw s4,0x2604(t7)              # ship 2
    sw zero,0x2608(t7)
    lui t6,0x01F8
    sw s0,-8636(t6)               # 0x01F7DE44 "the player ship" is ship 1 again
    addiu t6,t6,-8480             # 0x01F7DEE0: the offset from the flight path (x, y, ...), one for the game
    ld t0,0(t6)
    ld t1,8(t6)
    sd t0,0x2610(t7)              # ship 2's own offset starts as the game's, 90 to the side
    sd t1,0x2618(t7)
    lui t0,0x42B4
    sw t0,0x2610(t7)
gb_out:
    ld ra,0(sp)
    ld s4,8(sp)
    jr ra
    addiu sp,sp,32
g2_wrap:                          # the player ship's update in the class table 0x01F81068 (was 0x01F219A8; a0 = ship)
    lui t7,0x000F
    lw t6,0x2604(t7)
    beq a0,t6,gw_two
    nop
    j 0x01F219A8                  # any other ship: the game's update, untouched
    nop
gw_two:
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    daddu s0,a0,zero
    lw t4,0x2608(t7)
    addiu t4,t4,1
    sw t4,0x2608(t7)              # count ship 2's updates
    lw t5,0x2600(t7)
    beq t5,zero,gw_in
    nop
    lw t4,0x50C(t5)
    sw t4,0x50C(s0)               # ship 2's state (flying in, control, done, destroyed) = ship 1's
gw_in:
    lui t6,0x01F8
    addiu t6,t6,-8480             # the game's one offset
    ld t0,0(t6)
    ld t1,8(t6)
    sd t0,0x2620(t7)              # keep player 1's
    sd t1,0x2628(t7)
    ld t2,0x2610(t7)
    ld t3,0x2618(t7)
    sd t2,0(t6)                   # ship 2's own for the length of its update
    sd t3,8(t6)
    jal 0x01F219A8
    daddu a0,s0,zero
    lui t7,0x000F
    lui t6,0x01F8
    addiu t6,t6,-8480
    ld t0,0(t6)
    ld t1,8(t6)
    sd t0,0x2610(t7)              # what the update made of it
    sd t1,0x2618(t7)
    ld t2,0x2620(t7)
    ld t3,0x2628(t7)
    sd t2,0(t6)                   # player 1's again
    sd t3,8(t6)
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,32
g2_fire:                          # the end of the fire handler (0x01F2191C was: j 0x01F1EE00 with a0 = the player ship)
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x01F1EE00
    nop
    lui t7,0x000F
    lw a0,0x2604(t7)
    beq a0,zero,gf_out
    nop
    lw t6,0x50C(a0)
    addiu t5,zero,2
    bne t6,t5,gf_out              # only a ship under control fires
    nop
    jal 0x01F1ED28                # the same two routines for ship 2
    nop
    lui t7,0x000F
    jal 0x01F1EE00
    lw a0,0x2604(t7)
gf_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""
GMPAD_HOOK = (0x00167E90, 0x0C059F5A, "the controller task's update of record 1: then record 0 may get both")
GMPRE_HOOK = (0x00167E84, 0x0C059F5A, "the controller task's update of record 0: controller 1's own held word first")

POOL_N = 18                       # twenty-first glue: the pool of prompt objects (the game: 9 objects of 896 bytes)
POOL_STACK = POOL_N * 896         # the index stack (the game: 8064)
POOL_COUNT = POOL_STACK + 4 * POOL_N   # the free count (the game: 8100)
POOL_SIZE = (POOL_COUNT + 4 + 15) // 16 * 16   # the block (the game: 8112)
POOL_WORDS = (                    # (address, word expected, new word, what)
    (0x0013E6A0, 0x24120008, 0x24120000 | (POOL_N - 1), "build: the loop makes %d objects" % POOL_N),
    (0x0013E6C8, 0x24041FB0, 0x24040000 | POOL_SIZE, "build: the size of the block"),
    (0x0013E744, 0x268E1F80, 0x268E0000 | POOL_STACK, "build: the index stack"),
    (0x0013E750, 0x29AF0009, 0x29AF0000 | POOL_N, "build: %d indexes" % POOL_N),
    (0x0013E764, 0x240F0009, 0x240F0000 | POOL_N, "build: %d objects are free" % POOL_N),
    (0x0013E76C, 0xAE8F1FA4, 0xAE8F0000 | POOL_COUNT, "build: the free count"),
    (0x0013E38C, 0x8D8E1FA4, 0x8D8E0000 | POOL_COUNT, "give back: the free count"),
    (0x0013E3A4, 0xAD8E1FA4, 0xAD8E0000 | POOL_COUNT, "give back: the free count"),
    (0x0013E3AC, 0xADE41F80, 0xADE40000 | POOL_STACK, "give back: the index stack"),
    (0x0013E628, 0x8E0E1FA4, 0x8E0E0000 | POOL_COUNT, "take: the free count"),
    (0x0013E634, 0xAE0E1FA4, 0xAE0E0000 | POOL_COUNT, "take: the free count"),
    (0x0013E63C, 0x8DED1F80, 0x8DED0000 | POOL_STACK, "take: the index stack"),
    (0x0013E848, 0x26301F80, 0x26300000 | POOL_STACK, "end: the last object"),
)
assert POOL_SIZE < 0x8000

SUMMON_HOOKS = (                  # (address, word expected, kind, label, what)
    (0x001D13FC, 0x080720C0, "j", "sm_start", "a hero calls a summon: who it is"),
    (0x001D14A0, 0x3C0F0035, "j", "sm_who", "the summon code's 'player object': the hero who called the summon"),
    (0x001D14A4, 0x03E00008, "nop", None, "(the old routine's return)"),
    (0x001C82C4, 0x8DEEE948, "jal", "sm_t6", "the summon gauge that pays for the friend's hits: the caller's"),
    (0x001C8444, 0x0C0721E2, "jal", "sm_skip", "the entrance scene: not for a summon the twin calls"),
    (0x001D1028, 0x0C0722AC, "jal", "sm_mine", "empty gauge, every frame: only the caller sends his summon away"),
    (0x001D0E7C, 0x0C0722AC, "jal", "sm_mine", "empty gauge, form end: only the caller sends his summon away"),
    (0x001BE7C8, 0x0C0722AC, "jal", "sm_menu", "menu page 2, row 2 (Summon / Dismiss): by the menu's own player"),
    (0x001BE7F8, 0x0C0722AC, "jal", "sm_menu", "menu page 2, the summon friend's rows: by the menu's own player"),
    (0x001BC460, 0x0C06F014, "jal", "sm_can", "a summon in the list is dim while any summon is out"),
    (0x001C84EC, 0x8DE4E948, "word:0240202D", None, "the summon friend appears beside the hero who called him (daddu a0,s2,zero)"),
)

MASH_HOOKS = (                    # the same form as BOX_HOOKS; sixteenth glue
    (0x0016DBA8, 0x0000202D, "the script engine's 'button held' test (0x0016DB98): either controller"),
    (0x0016DBF0, 0x0000202D, "the script engine's 'button pressed' test (0x0016DBE0): either controller"),
)

PRIZE_AT = 0x000F4840
PRIZE_END = 0x000F48C0
PRIZE_SRC = """
prize_cand:                       # hook 0x001A51F8 (jal 0x00176B20 "party member N"). a0 = N (0..3), s2 = the prize
    li t5,3
    lui t7,0x000F
    beq a0,t5,pc_last
    lw t6,0x05CC(t7)              # the twin's object (lane E's pointer, 0 = none)
    beq t6,zero,pc_game           # no twin: the game's list
    srl t4,s2,6
    andi t4,t4,1                  # with a twin: every other prize asks the twin first
    beq t4,zero,pc_game
    nop
    bne a0,zero,pc_game
    nop
    jr ra                         # N = 0 for such a prize: the twin
    move v0,t6
pc_game:
    j 0x00176B20
    nop
pc_last:                          # N = 3: the hero that was not asked at N = 0
    beq t6,zero,pc_ret            # no twin: nobody
    move v0,zero
    srl t4,s2,6
    andi t4,t4,1
    beq t4,zero,pc_ret
    move v0,t6                    # the twin
    lui t7,0x0035
    lw v0,-5816(t7)               # 0x0034E948: the engine's player (player 1's hero)
pc_ret:
    jr ra
    nop
"""
PRIZE_HOOKS = (
    (0x001A51F8, 0x0C05DAC8, "jal", "a prize asks for party member N: N = 3 and the turn rule for the second hero"),
    (0x001A5258, 0x2A2F0003, 0x2A2F0004, "the prize's loop over party members runs to N = 3 (slti t7,s1,4)"),
)

LOCK_AT = 0x000F48C0
LOCK_END = 0x000F4900
LOCK_SRC = """
lock_own:                         # hook 0x001874BC (j). The instruction at 0x001874C0 runs in its delay slot, so
    lui t6,0x000F                 # s0 = the engine's player here. a0 = the attacking hero
    lw t6,0x05CC(t6)              # the twin (lane E's pointer, 0 = none)
    bne a0,t6,lo_go
    daddu s1,a0,zero              # the instruction that sat at 0x001874BC
    daddu s0,a0,zero              # the twin attacks: his own lock-on manager (object+0xB40)
lo_go:
    j 0x001874C4
    nop
"""
LOCK_HOOK = (0x001874BC, 0x0080882D, "an attacking hero's target test: the twin's own lock-on manager for the twin")

MSN_AT = 0x000F4900
MSN_END = 0x000F4980
MSN_SRC = """
dmg_msn:                          # jump at 0x00186154 (its delay slot, addiu sp,sp,16, has run): a0 = the damaged
    lui t6,0x000F                 # object, a1 = the damage record. Goes on to 0x00196B58 (mission scripts, key 6)
    lw t6,0x05CC(t6)              # the twin (lane E's pointer, 0 = none)
    beq t6,zero,dm_plain
    nop
    beq a1,zero,dm_plain
    nop
    lw t5,16(a1)                  # the attacker
    bne t5,t6,dm_plain
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    daddu s0,a1,zero
    daddu s1,t5,zero
    lui t4,0x0035
    lw t4,-5816(t4)               # the engine's player
    jal 0x00196B58
    sw t4,16(a1)                  # for the mission scripts the twin's hit is the player's hit
    sw s1,16(s0)                  # the record names the twin again
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    jr ra
    addiu sp,sp,32
dm_plain:
    j 0x00196B58
    nop
"""
MSN_HOOK = (0x00186154, 0x08065AD6, "the damage event for the mission scripts: the twin's hit counts as the player's")

GPRIZE_AT = 0x000F4B00
GPRIZE_END = 0x000F4C40
GPRIZE_SRC = """
gprize:                           # jump at 0x001A5990 (the slot holds nop). a0 = the prize, a1 = the gauge's
    addiu sp,sp,-64               # number, f12 = the amount
    swc1 f20,48(sp)
    sd s0,0(sp)
    sd s1,8(sp)
    sd s2,16(sp)
    sd ra,24(sp)
    sd s3,32(sp)
    mov.s f20,f12
    move s1,a0
    move s2,a1
    lui t7,0x0035
    lw s0,-5816(t7)               # the engine's player
    lui t7,0x000F
    lw s3,0x05CC(t7)              # the twin (lane E's pointer, 0 = none)
    beq s3,zero,gp_first
    andi t6,s1,0x40
    beq t6,zero,gp_first          # every other prize asks the twin first
    nop
    move t6,s0
    move s0,s3
    move s3,t6
gp_first:
    jal gp_one
    nop
    bne v0,zero,gp_got
    nop
    beq s3,zero,gp_out
    move s0,s3
    jal gp_one
    nop
    beq v0,zero,gp_out
    nop
gp_got:
    mov.s f12,f20
    move a0,s2
    ld s0,0(sp)
    ld s1,8(sp)
    ld s2,16(sp)
    ld ra,24(sp)
    ld s3,32(sp)
    lwc1 f20,48(sp)
    j 0x001D8D08                  # the amount goes into the mission's gauge
    addiu sp,sp,64
gp_out:
    ld s0,0(sp)
    ld s1,8(sp)
    ld s2,16(sp)
    ld ra,24(sp)
    ld s3,32(sp)
    lwc1 f20,48(sp)
    jr ra
    addiu sp,sp,64
gp_one:                           # s0 = a hero, s1 = the prize. v0 = 1 when he took it (the routine's own steps)
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x0019BA60
    move a0,s0
    beq v0,zero,go_out
    nop
    lw t7,40(s1)
    andi t7,t7,0x1
    beq t7,zero,go_no
    mtc1 zero,f12
    move a0,s1
    move a1,s0
    jal 0x001C7950                # in reach?
    mov.s f13,f12
    beq v0,zero,go_out
    nop
    move a0,s1
    move a1,s0
    jal 0x001C79A0                # collected by this hero
    move a2,zero
    li v0,1
go_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
go_no:
    b go_out
    move v0,zero
"""
GPRIZE_HOOK = (0x001A5990, 0x27BDFFD0, "a prize that fills a mission gauge: either hero takes it")

FORM_AT = 0x000F4C40
FORM_END = 0x000F4E80
V_FT = 0x000F47E0                 # 1 while a slot search must find the twin's own (marked) slot
V_FT2 = 0x000F47E4                # 1 from the old body's end to the constructor call, when the old body is the twin
V_TFORM = 0x000F47E8              # the second hero's own current form number (a byte; 0 = none)
V_TFV = 0x000F47EC                # 1 once two heroes have been built in one room
FORM_SRC = """
form_end:                         # hook 0x001B6810 (was: jalr t7, the old body's end method). a0 = the old body
    lui t5,0x000F
    lw t4,0x05CC(t5)              # the twin (lane E's pointer, 0 = none)
    xor t4,t4,a0
    sltiu t4,t4,1                 # 1 = the old body is the twin
    jr t7                         # the end method; it returns into the form-change routine
    sw t4,%lo(V_FT2)(t5)
form_wrap:                        # hook 0x001B6850 (was: jal 0x001D0980, the player constructor; the instruction
    lui t7,0x000F                 # after it has run). s1 = the new body's memory. The constructor's arguments
    lw t6,%lo(V_FT2)(t7)          # (a0-a3, t0, f12) stay untouched
    beq t6,zero,fw_plain
    sw zero,%lo(V_FT2)(t7)
    addiu sp,sp,-32
    sd ra,0(sp)
    li t6,1
    sw t6,%lo(V_FT)(t7)           # the slot search finds the twin's own slot now (form_d2)
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player = player 1's hero
    jal 0x001D0980
    sd t4,8(sp)
    lui t7,0x000F
    sw zero,%lo(V_FT)(t7)
    sw s1,0x05CC(t7)              # the new body is the twin
    lw t3,0x48C(s1)               # his unit slot
    beq t3,zero,fw_role
    nop
    lw t2,0x250(t3)
    bltz t2,fw_role               # marked: it is his own slot, as before the change
    lui t1,0x8000
    or t2,t2,t1
    sw t2,0x250(t3)               # (his old slot was gone: this one becomes the marked one,
    move a0,t3
    jal 0x001A11E0                # and its stats are loaded once more as a marked slot: own HP / MP bytes)
    move a1,zero
fw_role:
    ld t4,8(sp)
    lui t5,0x0035
    beq t4,zero,fw_done           # (no engine player before: nothing to give back)
    nop
    sw t4,-5816(t5)               # the engine's player is player 1's hero again
    sw t4,0x2400(t5)              # 0x00352400: the last-built object of the main player class
    lw t3,0x48C(t4)
    beq t3,zero,fw_att
    nop
    sw t4,0x25C(t3)               # his unit slot's back pointer
fw_att:
    jal 0x001781A8                # the game's attach for player 1's hero: camera target, trigger owner, HUD owner, S
    move a0,t4
fw_done:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
fw_plain:
    j 0x001D0980
    nop
form_d2:                          # replaces lane D's D2 (hook 0x001A1518, the find-slot-by-id loop). s0 = slot,
    bne t7,s1,fd_next             # s1 = wanted id, t7 = the slot's id
    lw t6,0x250(s0)
    lui t5,0x000F
    lw t5,%lo(V_FT)(t5)
    srl t6,t6,31                  # 1 = a marked slot (the twin's)
    bne t6,t5,fd_next             # normally only an unmarked slot is found; for the twin only his
    nop
    j 0x001A1520                  # found
    nop
fd_next:
    j 0x001A14C4                  # loop head
    nop
form_slot:                        # hooks 0x001B6148 and 0x001B6300 (were: jal 0x001A1658, "Sora's slot" for the
    lw t6,0(s0)                   # form-change record). s0 = the record, [s0] = the body that changes
    lui t7,0x000F
    lw t5,0x05CC(t7)
    bne t6,t5,fsl_plain
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    li t6,1
    jal 0x001A1658
    sw t6,%lo(V_FT)(t7)           # the twin changes: the record holds his own slot
    lui t7,0x000F
    sw zero,%lo(V_FT)(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
fsl_plain:
    j 0x001A1658
    nop
form_cur:                         # hook 0x001B6B30 (the next word is now a nop): "is the wanted form the current
    lui t7,0x0033                 # one?" s1 = the hero that asks. Out: t6 = his current form number
    lbu t6,-4012(t7)              # the save data's number: player 1's hero
    lui t5,0x000F
    lw t4,0x05CC(t5)
    bne s1,t4,fc_out
    nop
    lbu t6,%lo(V_TFORM)(t5)       # the twin: his own
fc_out:
    jr ra
    nop
form_set:                         # hook 0x001B6BAC (the word that sat there runs in the slot after it): the new
    lui t5,0x000F                 # form number is noted. s1 = the hero, s0 = the number
    lw t4,0x05CC(t5)
    beq s1,t4,fst_tw
    lui t6,0x0033
    jr ra
    sb s0,-4012(t6)               # player 1's hero: the save data, as before
fst_tw:
    jr ra
    sb s0,%lo(V_TFORM)(t5)
form_zero:                        # hook 0x001B6C78 (0x001B6C84 is now a nop): a hero's form ends. s0 = the hero.
    lui t5,0x000F                 # Keeps a0
    lw t4,0x05CC(t5)
    beq s0,t4,fz_tw
    lui t7,0x0033
    jr ra
    sb zero,-4012(t7)
fz_tw:
    jr ra
    sb zero,%lo(V_TFORM)(t5)
form_build:                       # hook 0x0016F0CC (0x0016F0D0 is now a nop): a room builds a player object from
    lui t7,0x0033                 # the PLAYER placeholder. Out: s0 = the form number to build it in
    lbu s0,-4012(t7)
    lui t6,0x0035
    lw t6,-5816(t6)               # the engine's player
    lui t5,0x000F
    beq t6,zero,fb_first
    li t4,1
    jr ra
    sw t4,%lo(V_TFV)(t5)          # a second hero is built in this room: this game has two
fb_first:
    lw t4,%lo(V_TFV)(t5)
    beq t4,zero,fb_out
    nop
    lbu s0,%lo(V_TFORM)(t5)       # the first-built hero becomes the second hero: his own form
fb_out:
    jr ra
    nop
"""
FORM_MORE = (                     # (address, word expected, word after it expected, routine, kind, what)
    (0x001B6148, 0x0C068596, 0x2405FFFF, "form_slot", "jal", "the form-change record asks for Sora's slot (first maker)"),
    (0x001B6300, 0x0C068596, 0x2405FFFF, "form_slot", "jal", "the form-change record asks for Sora's slot (second maker)"),
    (0x001B6B30, 0x3C0F0033, 0x91EEF054, "form_cur", "jal+nop", "a form is asked for: compared with the asking hero's own form"),
    (0x001B6BAC, 0xAE2F0108, 0xA1D03524, "form_set", "jal+move", "the new form number is noted: the twin's in his own place"),
    (0x001B6C78, 0x3C0F0033, 0x24040020, "form_zero", "jal", "a form ends: the twin's own number is cleared"),
    (0x0016F0CC, 0x3C0F0033, 0x91F0F054, "form_build", "jal+nop", "a room builds a player object: in that hero's own form"),
)
FORM_NOP = (0x001B6C84, 0xA1E0F054, "(the save data's number was cleared here; form_zero does it)")
FORM_END_HOOK = (0x001B6810, 0x01E0F809, "the old body's end method in a form change: note whether it is the twin")
FORM_HOOK = (0x001B6850, 0x0C074260, "a form change builds the new body: the twin stays the twin")
FORM_D2 = (0x001A1518, 0x0803C057, "the slot search (lane D's D2): during the twin's form change his own slot is found")

HELPER_AT = 0x000F4E80
HELPER_END = 0x000F4F00
HELPER_SRC = """
helper_think:                     # jump at 0x0016A950 (its second word is now a nop). a0 = the object that thinks
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin (lane E's pointer, 0 = none)
    beq t6,zero,ht_body
    lui t5,0x0035
    lw t4,-31168(t5)              # 0x00348640: the party table's place 2 (the second helper)
    bne a0,t4,ht_body
    nop
    lw t4,-5816(t5)               # the engine's player
    beq t4,zero,ht_body
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd t4,8(sp)
    jal ht_body                   # he thinks with the twin as "the player"
    sw t6,-5816(t5)
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
ht_body:
    addiu sp,sp,-16               # the two instructions that sat at 0x0016A950
    j 0x0016A958
    sd s0,0(sp)
"""
HELPER_HOOK = (0x0016A950, 0x27BDFFF0, 0xFFB00000, "an object thinks: the second helper with the second hero as the player")

BOARD_AT = 0x000F4F00
BOARD_END = 0x000F5000
V_TBOARD = 0x000F47F0             # the board the twin rides (0 = none)
BOARD_SRC = """
sk_ride:                          # hook 0x002EB8EC (was: jal 0x00198860). a0 = the board, s0 = the hero that
    lui t7,0x000F                 # gets on
    lw t6,0x05CC(t7)              # the twin (lane E's pointer, 0 = none)
    lw t5,%lo(V_TBOARD)(t7)
    bne s0,t6,skr_other
    nop
    j 0x00198860
    sw a0,%lo(V_TBOARD)(t7)       # the twin's board
skr_other:
    bne t5,a0,skr_go              # another rider on the board that was noted (an old note): forget it
    nop
    sw zero,%lo(V_TBOARD)(t7)
skr_go:
    j 0x00198860
    nop
sk_who:                           # hook 0x00198910 (was: lw t6,-5816(t7), the engine's player). s2 = the board.
    lui t5,0x000F                 # Out: t6 = the hero whose control object gets the board commands
    lw t6,%lo(V_TBOARD)(t5)
    bne t6,s2,skw_p1
    lui t7,0x0035
    lw t6,0x05CC(t5)
    bne t6,zero,skw_out           # the twin's board: the twin
    nop
skw_p1:
    lw t6,-5816(t7)
skw_out:
    jr ra
    nop
sk_off:                           # hook 0x0019898C (0x00198990 is now a nop). s0 = the board that is left.
    lui t5,0x000F                 # Out: t6 = the hero whose control object leaves the board commands
    lw t6,%lo(V_TBOARD)(t5)
    bne t6,s0,sko_p1
    lui t7,0x0035
    lw t6,0x05CC(t5)
    bne t6,zero,sko_out           # (the note stays: 0x00198860 runs this first for a board in use)
    nop
sko_p1:
    lw t6,-5816(t7)
sko_out:
    jr ra
    nop
"""
BOARD_HOOKS = (                   # (address, word expected, word after it expected, routine, nop the next word, what)
    (0x002EB8EC, 0x0C066218, 0x24050002, "sk_ride", False, "a hero gets on a board: the twin's board is noted"),
    (0x00198910, 0x8DEEE948, 0x0200302D, "sk_who", False, "the board commands open: on the rider's control object"),
    (0x0019898C, 0x3C0F0035, 0x8DEEE948, "sk_off", True, "the board commands close: on the rider's control object"),
)

RIDE_AT = 0x000F2680              # twenty-ninth glue (0x000F2680-0x000F26FF: lane H's range behind the Gummi data)
RIDE_END = 0x000F2700
RIDE_SRC = """
sk_who2:                          # hook 0x00198910 in place of the eleventh glue's sk_who. s2 = the vehicle.
    lui t5,0x000F                 # Out: t6 = the hero whose control object gets the ride commands
    lw t6,%lo(V_TBOARD)(t5)
    bne t6,s2,sw2_self
    lui t7,0x0035
    lw t6,0x05CC(t5)
    bne t6,zero,sw2_out           # the twin's board: the twin (as sk_who)
    nop
sw2_self:
    lw t6,0xB44(s2)               # the vehicle IS a hero whose control object is the twin's (0x000F1000): a special
    ori t4,t5,0x1000              # player object built as the twin (Light Cycle, the Pooh flyer, the carpet rider)
    bne t6,t4,sw2_p1              # opens its ride commands itself, in its constructor
    nop
    jr ra
    move t6,s2
sw2_p1:
    lw t6,-5816(t7)
sw2_out:
    jr ra
    nop
sk_off2:                          # hook 0x0019898C in place of sk_off. s0 = the vehicle that is left.
    lui t5,0x000F
    lw t6,%lo(V_TBOARD)(t5)
    bne t6,s0,so2_self
    lui t7,0x0035
    lw t6,0x05CC(t5)
    bne t6,zero,so2_out
    nop
so2_self:
    lw t6,0xB44(s0)
    ori t4,t5,0x1000
    bne t6,t4,so2_p1
    nop
    jr ra
    move t6,s0
so2_p1:
    lw t6,-5816(t7)
so2_out:
    jr ra
    nop
"""

NEAR_AT = 0x000F5000
NEAR_END = 0x000F5280
NEAR_SRC = """
near_think:                       # jump at 0x0016A950 (its second word is now a nop). a0 = the object that thinks
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin (lane E's pointer, 0 = none)
    beq t6,zero,nr_body
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player = player 1's hero
    beq t4,zero,nr_body
    nop
    beq a0,t4,nr_body             # the heroes think as themselves
    nop
    beq a0,t6,nr_body
    lw t3,0(a0)
    lui t2,0x0034
    ori t2,t2,0x5C08
    beq t3,t2,nr_body             # a helper: unchanged
    nop
    lw t3,0x48C(t6)               # the twin's unit slot
    beq t3,zero,nr_body
    nop
    lw t3,0(t3)
    beq t3,zero,nr_body           # the twin is down (HP 0): player 1's hero
    nop
    lw t2,0x48C(t4)
    beq t2,zero,nr_dist
    nop
    lw t2,0(t2)
    beq t2,zero,nr_twin           # player 1's hero is down: the twin
    nop
nr_dist:
    lwc1 f0,0x70(a0)
    lwc1 f1,0x78(a0)
    lwc1 f2,0x70(t4)
    lwc1 f3,0x78(t4)
    sub.s f2,f2,f0
    sub.s f3,f3,f1
    mul.s f2,f2,f2
    mul.s f3,f3,f3
    add.s f2,f2,f3                # distance to player 1's hero, squared
    lwc1 f4,0x70(t6)
    lwc1 f5,0x78(t6)
    sub.s f4,f4,f0
    sub.s f5,f5,f1
    mul.s f4,f4,f4
    mul.s f5,f5,f5
    add.s f4,f4,f5                # distance to the twin, squared
    c.lt.s f4,f2
    bc1f nr_body                  # player 1's hero is nearer (or as near): as it is
    nop
nr_twin:
    addiu sp,sp,-32
    sd ra,0(sp)
    sd t4,8(sp)
    jal nr_body                   # this object thinks with the twin as "the player"
    sw t6,-5816(t5)
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
nr_body:
    addiu sp,sp,-16               # the two instructions that sat at 0x0016A950
    j 0x0016A958
    sd s0,0(sp)
"""

HELP_AT = 0x000F5280
HELP_END = 0x000F5800
HELP_DATA = 0x000F5800            # +0 pass, +4 split, +8 / +C who the two helpers go with (0 player 1, 1 the twin),
#                                   +10 the true member table (3 words), +40 the second copy of the leader memory
HELP_SRC = """
hp_x:                             # swap t2 words at t0 and t1 (both move on)
    lw t3,0(t0)
    lw t4,0(t1)
    sw t4,0(t0)
    sw t3,0(t1)
    addiu t2,t2,-1
    addiu t0,t0,4
    bne t2,zero,hp_x
    addiu t1,t1,4
    jr ra
    nop
hp_swap:                          # the follow system's leader memory <-> the second copy
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t0,0x0034
    addiu t0,t0,0x1720
    lui t1,0x000F
    addiu t1,t1,0x5840
    jal hp_x
    li t2,24
    lui t0,0x0034
    addiu t0,t0,0x17B0
    jal hp_x
    li t2,12
    lui t0,0x003B
    addiu t0,t0,-28608            # 0x003A9040: the trail
    jal hp_x
    li t2,132
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
hp_table:                         # a0 = pass: the member table as that pass must see it
    lui t7,0x000F
    addiu t7,t7,0x5800
    lui t6,0x0034
    addiu t6,t6,0x1708
    lw t0,0x10(t7)
    beq a0,zero,ht_l
    lui t1,0x000F
    lw t0,0x05CC(t1)              # pass 1: the leader is the twin
ht_l:
    sw t0,0(t6)
    lw t0,0x14(t7)
    lw t1,0x08(t7)
    beq t1,a0,ht_1
    nop
    move t0,zero
ht_1:
    sw t0,4(t6)
    lw t0,0x18(t7)
    lw t1,0x0C(t7)
    beq t1,a0,ht_2
    nop
    move t0,zero
ht_2:
    jr ra
    sw t0,8(t6)
hp_full:                          # the member table as the game made it
    lui t7,0x000F
    addiu t7,t7,0x5800
    lui t6,0x0034
    addiu t6,t6,0x1708
    lw t0,0x10(t7)
    lw t1,0x14(t7)
    lw t2,0x18(t7)
    sw t0,0(t6)
    sw t1,4(t6)
    jr ra
    sw t2,8(t6)
hp_pass1q:                        # v0 = 1 when a helper that is there goes with the twin
    lui t7,0x000F
    lw t6,0x05CC(t7)
    beq t6,zero,pq_no
    addiu t7,t7,0x5800
    lw t0,0x08(t7)
    beq t0,zero,pq_2
    lw t1,0x14(t7)
    bne t1,zero,pq_yes
    nop
pq_2:
    lw t0,0x0C(t7)
    beq t0,zero,pq_no
    lw t1,0x18(t7)
    bne t1,zero,pq_yes
    nop
pq_no:
    jr ra
    move v0,zero
pq_yes:
    jr ra
    li v0,1
hp_d2:                            # f0 = flat squared distance of the objects a0 and a1 (0 when one is missing)
    mtc1 zero,f0
    beq a0,zero,hd_end
    nop
    beq a1,zero,hd_end
    nop
    lwc1 f0,0x70(a0)
    lwc1 f1,0x78(a0)
    lwc1 f2,0x70(a1)
    lwc1 f3,0x78(a1)
    sub.s f0,f0,f2
    sub.s f1,f1,f3
    mul.s f0,f0,f0
    mul.s f1,f1,f1
    add.s f0,f0,f1
hd_end:
    jr ra
    nop
hp_assign:                        # once a step: who goes with whom
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    lui s2,0x000F
    lw s1,0x05CC(s2)              # the twin
    addiu s2,s2,0x5800
    beq s1,zero,ha_none
    lui t5,0x0035
    lw s0,-5816(t5)               # player 1's hero
    beq s0,zero,ha_none
    move a0,s0
    jal hp_d2
    move a1,s1
    lw t0,0x04(s2)
    bne t0,zero,ha_split
    lui t1,0x4945
    ori t1,t1,0xC100              # 810000.0 = 900 * 900
    mtc1 t1,f6
    c.lt.s f6,f0
    bc1f ha_done                  # together: everybody with player 1's hero (as it is)
    nop
    li t0,1
    sw t0,0x04(s2)                # the heroes have split up
    lui t0,0x0034
    addiu t0,t0,0x1720
    lui t1,0x000F
    addiu t1,t1,0x5840
    li t2,168
ha_cp:                            # the second copy starts as a copy ...
    lw t3,0(t0)
    sw t3,0(t1)
    addiu t2,t2,-1
    addiu t1,t1,4
    beq t2,zero,ha_cpd
    addiu t0,t0,4
    li t3,144
    bne t2,t3,ha_cp2
    nop
    lui t0,0x0034
    b ha_cp
    addiu t0,t0,0x17B0
ha_cp2:
    li t3,132
    bne t2,t3,ha_cp
    nop
    lui t0,0x003B
    b ha_cp
    addiu t0,t0,-28608
ha_cpd:
    lui t1,0x000F
    addiu t1,t1,0x58D0            # ... with an empty trail (as the game's own reset 0x0010B550 leaves it)
    li t3,-1
    sw zero,0(t1)
    sw t3,4(t1)
    lui t2,0x01C6
    lw a0,0x0528(t2)              # helper 1
    jal hp_d2
    move a1,s0
    swc1 f0,32(sp)
    lui t2,0x01C6
    lw a0,0x052C(t2)              # helper 2
    jal hp_d2
    move a1,s1
    lwc1 f1,32(sp)
    add.s f0,f0,f1
    swc1 f0,32(sp)                # helper 1 with player 1 + helper 2 with the twin
    lui t2,0x01C6
    lw a0,0x0528(t2)
    jal hp_d2
    move a1,s1
    swc1 f0,36(sp)
    lui t2,0x01C6
    lw a0,0x052C(t2)
    jal hp_d2
    move a1,s0
    lwc1 f1,36(sp)
    add.s f0,f0,f1                # helper 1 with the twin + helper 2 with player 1
    lwc1 f1,32(sp)
    c.lt.s f0,f1
    li t0,1
    bc1t ha_swapd
    nop
    sw zero,0x08(s2)
    b ha_done
    sw t0,0x0C(s2)
ha_swapd:
    sw t0,0x08(s2)
    b ha_done
    sw zero,0x0C(s2)
ha_split:
    lui t1,0x4893
    ori t1,t1,0xB480              # 302500.0 = 550 * 550
    mtc1 t1,f6
    c.lt.s f0,f6
    bc1f ha_done                  # still apart: the pairing stays
    nop
ha_none:
    sw zero,0x04(s2)
    sw zero,0x08(s2)
    sw zero,0x0C(s2)
ha_done:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    jr ra
    addiu sp,sp,48
hp_rebuild:                       # call at 0x00111F74 (was: jal 0x00111E50, the game's rebuild of the member table)
    lui t7,0x000F
    lw t6,0x5800(t7)
    bne t6,zero,hr_p1
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x00111E50                # pass 0: the game's own rebuild (it tells the party lists about true changes)
    nop
    lui t7,0x000F
    addiu t7,t7,0x5800
    lui t6,0x0034
    addiu t6,t6,0x1708
    lw t0,0(t6)
    lw t1,4(t6)
    lw t2,8(t6)
    sw t0,0x10(t7)                # remember the true table
    sw t1,0x14(t7)
    sw t2,0x18(t7)
    ld ra,0(sp)
    addiu sp,sp,16
    j hp_table                    # and hide the helpers that go with the twin
    move a0,zero
hr_p1:
    j hp_table
    li a0,1
hp_taskA:                         # task routines (their addresses are handed to the task list at 0x001123F0...)
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    jal hp_assign
    move s2,a0
    lui s0,0x0011
    addiu s0,s0,0x1F50
    b hp_body
    move s1,zero
hp_taskB:
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    move s2,a0
    lui s0,0x0011
    addiu s0,s0,0x22A0
    b hp_body
    li s1,1
hp_taskC:
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    move s2,a0
    lui s0,0x0011
    addiu s0,s0,0x2388
    li s1,1
hp_body:
    beq s1,zero,hb_p0             # (the first task sets the table itself, after the game's rebuild)
    nop
    jal hp_table
    move a0,zero
hb_p0:
    jalr s0                       # for player 1's hero and his helpers
    move a0,s2
    jal hp_pass1q
    nop
    beq v0,zero,hb_end
    nop
    jal hp_swap
    nop
    lui t7,0x000F
    li t6,1
    sw t6,0x5800(t7)
    jal hp_table
    li a0,1
    jalr s0                       # for the twin and his helpers
    move a0,s2
    lui t7,0x000F
    jal hp_swap
    sw zero,0x5800(t7)
hb_end:
    jal hp_full
    nop
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    jr ra
    addiu sp,sp,48
hp_m08:                           # the helper class's methods (class table 0x00345C08, words +0x08, +0x0C, +0x14, +0x20)
    lui t9,0x0010
    b hp_meth
    ori t9,t9,0xC7F0
hp_m0C:
    lui t9,0x0017
    b hp_meth
    ori t9,t9,0xDC98
hp_m14:
    lui t9,0x0011
    b hp_meth
    ori t9,t9,0x1520
hp_m20:
    lui t9,0x0017
    ori t9,t9,0xDC38
hp_meth:                          # a0 = the helper, t9 = the game's method. Does he go with the twin?
    lui t7,0x000F
    addiu t7,t7,0x5800
    lw t3,0(t7)
    bne t3,zero,hm_plain          # the twin's memory is in already
    lw t3,0x14(t7)
    bne a0,t3,hm_2
    lw t2,0x08(t7)
    bne t2,zero,hm_go
    nop
    jr t9
    nop
hm_2:
    lw t3,0x18(t7)
    bne a0,t3,hm_plain
    lw t2,0x0C(t7)
    bne t2,zero,hm_go
    nop
hm_plain:
    jr t9
    nop
hm_go:
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    move s0,a0
    move s1,t9
    li t3,1
    jal hp_swap
    sw t3,0(t7)
    jal hp_table
    li a0,1
    jalr s1
    move a0,s0
    jal hp_swap
    nop
    jal hp_full
    nop
    lui t7,0x000F
    sw zero,0x5800(t7)
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    jr ra
    addiu sp,sp,32
"""
# (address, word the program has, what the new word is made from, text)
HELP_HOOKS = (
    (0x00111F74, 0x0C044794, "jal:hp_rebuild", "the member table's rebuild in the first follow task"),
    (0x001123F4, 0x3C070011, "lui", "first follow task: high half of its routine's address"),
    (0x001123FC, 0x24E71F50, "lo:hp_taskA", "first follow task: low half (was 0x00111F50)"),
    (0x0011241C, 0x3C070011, "lui", "second follow task: high half"),
    (0x00112424, 0x24E722A0, "lo:hp_taskB", "second follow task: low half (was 0x001122A0)"),
    (0x0011243C, 0x3C070011, "lui", "third follow task: high half"),
    (0x00112444, 0x24E72388, "lo:hp_taskC", "third follow task: low half (was 0x00112388)"),
    (0x00345C10, 0x0010C7F0, "data:hp_m08", "helper class table +0x08"),
    (0x00345C14, 0x0017DC98, "data:hp_m0C", "helper class table +0x0C"),
    (0x00345C1C, 0x00111520, "data:hp_m14", "helper class table +0x14"),
    (0x00345C28, 0x0017DC38, "data:hp_m20", "helper class table +0x20"),
)

NEAR_HELP_SRC = """
nr_help:                          # a helper thinks (a0). Does he go with the twin?
    lui t7,0x000F
    addiu t7,t7,0x5800
    lw t3,0(t7)
    bne t3,zero,nr_body           # the twin's memory is in already
    nop
    lw t3,0x14(t7)                # the true member table, place 1
    bne a0,t3,nh_2
    lw t2,0x08(t7)
    bne t2,zero,nh_go
    nop
    b nr_body
    nop
nh_2:
    lw t3,0x18(t7)
    bne a0,t3,nr_body
    lw t2,0x0C(t7)
    beq t2,zero,nr_body
    nop
nh_go:
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    li t3,1
    sw t3,0(t7)
    jal hp_swap                   # the twin's copy of the follow system's leader memory
    move s0,a0
    jal hp_table                  # the twin as the leader, his helpers in the table
    li a0,1
    jal nr_body
    move a0,s0
    jal hp_swap
    nop
    jal hp_full
    nop
    lui t7,0x000F
    sw zero,0x5800(t7)
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,32
"""

EVRC_AT = 0x000F5B00
EVRC_END = 0x000F5B80
EVRC_SRC = """
ev_rc:                            # call at 0x00197DE4 (was: jal 0x00196E98). a0 = the event, a1 = the engine's player
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,er_go
    nop
    beq a1,zero,er_go
    nop
    lw t3,0x160(t6)               # bit 0x4000: this hero is in a scripted move
    lw t2,0x160(a1)
    srl t3,t3,14
    srl t2,t2,14
    andi t3,t3,1
    andi t2,t2,1
    beq t3,t2,er_go               # both or neither: as it is
    nop
    beq t3,zero,er_go             # player 1's hero is the one in the move
    nop
    move a1,t6                    # the twin is: the command is his
er_go:
    j 0x00196E98
    nop
"""
EVRC_HOOK = (0x00197DE4, 0x0C065BA6, "the command a scripted move's timeline opens: to the hero in the move")

ROWN_AT = 0x000F5B80
ROWN_END = 0x000F5BC0
ROWN_SRC = """
react_own:                        # hook 0x00189E3C (jal; the word that sat there now sits at 0x00189E40).
    lui t7,0x0035                 # s1 = the object whose motion offers the command
    lw s0,-5816(t7)               # the engine's player (the instruction that sat at 0x00189E40)
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin (lane E's pointer, 0 = none)
    beq t6,zero,ro_out
    nop
    bne s1,t6,ro_out              # an enemy, an object or player 1's hero offers it: as it is
    nop
    move s0,s1                    # the twin's own motion offers it: his own control object, his own note
ro_out:
    jr ra
    nop
"""
ROWN_HOOK = (0x00189E3C, 0x00A0982D, 0x8DF0E948, "a hero's own motion offers a command: to that hero's control object")

REACT_AT = 0x000F4A00
REACT_END = 0x000F4B00
REACT_SRC = """
react_both:                       # hook 0x00189E18 (j; the routine's second instruction runs in the delay slot).
    lui t6,0x000F                 # a0 = source object, a1 = command, a2 = argument
    lw t6,0x05CC(t6)              # the twin (lane E's pointer, 0 = none)
    beq t6,zero,rb_plain          # no twin: the routine as it is
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player
    beq a0,t4,rb_plain            # player 1's hero is the source: as it is
    nop
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    sd s3,32(sp)
    move s0,a0
    move s1,a1
    move s2,a2
    beq a0,t6,rb_twin             # the twin is the source: only for him
    move s3,t6
    jal rb_orig                   # an enemy or an object is the source: first for player 1's hero
    nop
rb_twin:
    lui t5,0x0035
    lw t4,-5816(t5)
    sd t4,40(sp)                  # the engine's player, to put back
    sw s3,-5816(t5)               # for this one call "the player" is the twin
    move a0,s0
    move a1,s1
    jal rb_orig
    move a2,s2
    ld t4,40(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    ld s3,32(sp)
    jr ra
    addiu sp,sp,48
rb_plain:
rb_orig:                          # the routine itself
    addiu sp,sp,-80               # the instruction that sat at 0x00189E18
    j 0x00189E20
    lui t7,0x35                   # (0x00189E1C again)
"""
REACT_HOOK = (0x00189E18, 0x27BDFFB0, "a Reaction Command is offered: to the hero it belongs to, or to both heroes")

HOOKS = (
    (0x001A12B4, 0x8E0D0260, "jal", "dr_load", "slot loads its Drive values: the second hero from his own copy"),
    (0x001A18C0, 0x8C8D0260, "j", "dr_save", "slot writes its Drive values: the second hero into his own copy"),
    (0x001A18C4, 0x11A00010, "nop", None, "(the branch that sat here is inside dr_save)"),
    (0x001ADBEC, 0x0C06871C, "jal", "dr_refill", "the game's full Drive refill: both heroes"),
)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = ROOT / (args[0] if args else "patches/merged-v6")
    order, words = [], {}
    for raw in (BASE / NAME).read_text(encoding="utf-8").splitlines():
        m = LINE.match(raw.strip())
        if not m:
            continue
        a = int(m.group(2), 16)
        assert m.group(1) == "1" and m.group(3).lower() == "word" and a not in words, raw
        order.append(a)
        words[a] = int(m.group(4), 16)
    origin = {}
    for raw in (BASE / "listing.txt").read_text(encoding="utf-8").splitlines():
        parts = raw.split(None, 2)
        if len(parts) == 3:
            origin[int(parts[0], 16)] = parts[2]

    n_glue = 0
    if "--no-drive" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        src = SRC.format(O_VALID=O_VALID, O_LAST=O_LAST, O_LAST4=O_LAST + 4, O_LAST8=O_LAST + 8, O_OWN2=O_OWN + 2)
        code, labels = assemble(GLUE_AT, src, {"OWN_BASE": OWN_BASE})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert GLUE_AT + 4 * len(code) <= GLUE_END, "glue too long"
        for i, w in enumerate(code):
            a = GLUE_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (own Drive values for the second hero)"
        for a in range(0x000F0000 + O_VALID, 0x000F0000 + O_OWN + 12, 4):
            assert a not in words, "variable address written by the patch: %08X" % a
        for a, orig, kind, label, what in HOOKS:
            assert a not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<I", elf.data, off + a - va)[0]
            assert have == orig, "hook %08X: program has %08X, expected %08X" % (a, have, orig)
            if kind == "nop":
                w = 0
            else:
                w = ((3 if kind == "jal" else 2) << 26) | ((labels[label] >> 2) & 0x3FFFFFF)
            words[a] = w
            order.append(a)
            origin[a] = "glue hook (own Drive values): " + what
        n_glue = len(code) + len(HOOKS)

    if "--no-box" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(BOX_AT, BOX_SRC, {"BOX_SCRATCH": BOX_SCRATCH})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert BOX_AT + 4 * len(code) <= BOX_END, "text box glue too long"
        for i, w in enumerate(code):
            a = BOX_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (text boxes listen to either controller)"
        for a in range(BOX_SCRATCH, BOX_SCRATCH + 0x60, 4):
            assert a not in words, "scratch address written by the patch: %08X" % a
        hooks = BOX_HOOKS if "--no-start" not in sys.argv else BOX_HOOKS[:1]
        for a, slot, what in hooks:
            assert a not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<I", elf.data, off + a - va)[0]
            assert have == 0x0C059FC6, "hook %08X: program has %08X, expected the getter call" % (a, have)
            assert struct.unpack_from("<I", elf.data, off + a + 4 - va)[0] == slot, "hook %08X: unexpected delay slot" % a
            words[a] = (3 << 26) | ((labels["pad_both"] >> 2) & 0x3FFFFFF)
            order.append(a)
            origin[a] = "glue hook (either controller): " + what
        n_glue += len(code) + len(hooks)
        pad_both_at = labels["pad_both"]

    if "--no-prize" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(PRIZE_AT, PRIZE_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert PRIZE_AT + 4 * len(code) <= PRIZE_END, "prize glue too long"
        for i, w in enumerate(code):
            a = PRIZE_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the second hero can pick up prizes)"
        for a, orig, new, what in PRIZE_HOOKS:
            assert a not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<I", elf.data, off + a - va)[0]
            assert have == orig, "hook %08X: program has %08X, expected %08X" % (a, have, orig)
            words[a] = ((3 << 26) | ((labels["prize_cand"] >> 2) & 0x3FFFFFF)) if new == "jal" else new
            order.append(a)
            origin[a] = "glue hook (prizes): " + what
        n_glue += len(code) + len(PRIZE_HOOKS)

    if "--no-lock" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(LOCK_AT, LOCK_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert LOCK_AT + 4 * len(code) <= LOCK_END, "lock glue too long"
        for i, w in enumerate(code):
            a = LOCK_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the second hero's attack uses his own lock-on target)"
        a, orig, what = LOCK_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (orig, 0x8DF0E948), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (2 << 26) | ((labels["lock_own"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (lock-on): " + what
        n_glue += len(code) + 1

    if "--no-msn" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(MSN_AT, MSN_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert MSN_AT + 4 * len(code) <= MSN_END, "mission glue too long"
        for i, w in enumerate(code):
            a = MSN_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the second hero's hits count in the mission scripts)"
        a, orig, what = MSN_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (orig, 0x27BD0010), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (2 << 26) | ((labels["dmg_msn"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (mission scripts): " + what
        n_glue += len(code) + 1

    if "--no-gprize" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(GPRIZE_AT, GPRIZE_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert GPRIZE_AT + 4 * len(code) <= GPRIZE_END, "gauge-prize glue too long"
        for i, w in enumerate(code):
            a = GPRIZE_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (prizes that fill a mission gauge: either hero)"
        a, orig, what = GPRIZE_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (orig, 0x3C0F0035), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (2 << 26) | ((labels["gprize"] >> 2) & 0x3FFFFFF)
        words[a + 4] = 0
        order += [a, a + 4]
        origin[a] = "glue hook (gauge prizes): " + what
        origin[a + 4] = "glue hook (gauge prizes): its delay slot"
        n_glue += len(code) + 2

    if "--no-form" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(FORM_AT, FORM_SRC, {"V_FT": V_FT, "V_FT2": V_FT2, "V_TFORM": V_TFORM, "V_TFV": V_TFV})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert FORM_AT + 4 * len(code) <= FORM_END, "form glue too long"
        for i, w in enumerate(code):
            a = FORM_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the second hero's form change)"
        a, orig, what = FORM_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (orig, 0x8DE70B38), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (3 << 26) | ((labels["form_wrap"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (form change): " + what
        a, orig, what = FORM_END_HOOK
        assert a not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (orig, 0), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (3 << 26) | ((labels["form_end"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (form change): " + what
        n_glue += 1
        for a, w0, w1, routine, kind, what in FORM_MORE:
            assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<2I", elf.data, off + a - va)
            assert have == (w0, w1), "hook %08X: program has %08X %08X" % ((a,) + have)
            words[a] = (3 << 26) | ((labels[routine] >> 2) & 0x3FFFFFF)
            order.append(a)
            origin[a] = "glue hook (form change): " + what
            n_glue += 1
            if kind == "jal+nop":
                words[a + 4] = 0
            elif kind == "jal+move":
                words[a + 4] = w0
            if kind != "jal":
                order.append(a + 4)
                origin[a + 4] = "glue hook (form change): the slot after it"
                n_glue += 1
        a, orig, what = FORM_NOP
        assert a not in words, "hook address already used: %08X" % a
        assert struct.unpack_from("<I", elf.data, off + a - va)[0] == orig
        words[a] = 0
        order.append(a)
        origin[a] = "glue hook (form change): " + what
        n_glue += 1
        a, old, what = FORM_D2
        assert words.get(a) == old, "lane D's D2 hook is not where it was: %08X" % words.get(a, 0)
        words[a] = (2 << 26) | ((labels["form_d2"] >> 2) & 0x3FFFFFF)
        origin[a] = "glue hook (form change; was lane D's D2): " + what
        n_glue += len(code) + 1

    if "--no-board" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(BOARD_AT, BOARD_SRC, {"V_TBOARD": V_TBOARD})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert BOARD_AT + 4 * len(code) <= BOARD_END, "board glue too long"
        for i, w in enumerate(code):
            a = BOARD_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the board commands go to the rider's control object)"
        n_glue += len(code)
        for a, w0, w1, routine, nop_next, what in BOARD_HOOKS:
            assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<2I", elf.data, off + a - va)
            assert have == (w0, w1), "hook %08X: program has %08X %08X" % ((a,) + have)
            words[a] = (3 << 26) | ((labels[routine] >> 2) & 0x3FFFFFF)
            order.append(a)
            origin[a] = "glue hook (board): " + what
            n_glue += 1
            if nop_next:
                words[a + 4] = 0
                order.append(a + 4)
                origin[a + 4] = "glue hook (board): the slot after it"
                n_glue += 1
        if "--no-ridetwin" not in sys.argv:                              # twenty-ninth glue
            code, lab2 = assemble(RIDE_AT, RIDE_SRC, {"V_TBOARD": V_TBOARD})
            code = [w if isinstance(w, int) else w[1] for w in code]
            assert RIDE_AT + 4 * len(code) <= RIDE_END, "ride glue too long"
            for i, w in enumerate(code):
                a = RIDE_AT + 4 * i
                assert a not in words, "glue address already used: %08X" % a
                words[a] = w
                order.append(a)
                origin[a] = "glue (a special player object built as the twin: its ride commands on its own control object)"
            for a, routine in ((0x00198910, "sk_who2"), (0x0019898C, "sk_off2")):
                assert a in words
                words[a] = (3 << 26) | ((lab2[routine] >> 2) & 0x3FFFFFF)
                origin[a] += " (twenty-ninth glue: also a hero that is its own vehicle)"
            n_glue += len(code)

    if "--helper" in sys.argv:         # EXPERIMENT, not in the build (no effect seen: tests l3-mu68-helper, l4-helpbit0..6)
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(HELPER_AT, HELPER_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert HELPER_AT + 4 * len(code) <= HELPER_END, "helper glue too long"
        for i, w in enumerate(code):
            a = HELPER_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the second helper goes with the second hero)"
        a, w0, w1, what = HELPER_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (w0, w1), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (2 << 26) | ((labels["helper_think"] >> 2) & 0x3FFFFFF)
        words[a + 4] = 0
        order += [a, a + 4]
        origin[a] = "glue hook (helpers): " + what
        origin[a + 4] = "glue hook (helpers): its delay slot"
        n_glue += 1
        n_glue += len(code) + 1

    if "--no-nearest" not in sys.argv and "--helper" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        near_src = NEAR_SRC
        if "--no-summon2" not in sys.argv:   # nineteenth glue, second part: a summon friend thinks for his caller
            a0_ = "    lw t3,0x48C(t6)               # the twin's unit slot"
            assert near_src.count(a0_) == 1
            near_src = near_src.replace(a0_, """    lui t2,0x0035
    ori t2,t2,0x1E18              # a summon friend (class table 0x00351E18)
    beq t3,t2,nr_sum
    nop
""" + a0_) + ("""
nr_sum:                           # he thinks for the hero who called him, wherever the two heroes stand
    lui t3,0x000F
    lw t3,%d(t3)
    bne t3,zero,nr_twin           # the twin called him
    nop
    b nr_body                     # player 1's hero called him: the engine's player as it is
    nop
""" % (V_SUMTW - 0x000F0000) if "--no-sumroom" in sys.argv else """
nr_sum:                           # he thinks for the hero who called him, wherever the two heroes stand;
    j sm_fix                      # first the OTHER hero's gauge is looked at (nineteenth glue, part 6)
    nop
""")
            near_syms_sum = {} if "--no-sumroom" in sys.argv else {"sm_fix": SUMMON3_AT}
        if "--helper2" in sys.argv:      # EXPERIMENT: the second helper is led by the twin (player pointer and party place 0)
            a0_, b0_ = "    beq t3,t2,nr_body             # a helper: unchanged", "    beq t3,t2,nr_helper"
            assert near_src.count(a0_) == 1
            near_src = near_src.replace(a0_, b0_) + """
nr_helper:
    lw t3,-31168(t5)              # 0x00348640: party place 2
    bne a0,t3,nr_body
    nop
    lw t3,0x48C(t6)
    beq t3,zero,nr_body
    nop
    lw t3,0(t3)
    beq t3,zero,nr_body           # the twin is down: the helper stays with player 1's hero
    nop
    addiu sp,sp,-48
    sd ra,0(sp)
    sd t4,8(sp)
    lw t3,-31176(t5)              # 0x00348638: party place 0
    sd t3,16(sp)
    sw t6,-31176(t5)
    jal nr_body
    sw t6,-5816(t5)
    ld t4,8(sp)
    ld t3,16(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    sw t3,-31176(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
"""
        near_syms = dict(near_syms_sum) if "--no-summon2" not in sys.argv else {}
        if "--no-helpers" not in sys.argv:   # a helper that goes with the twin thinks with the twin's follow memory
            _c, hl = assemble(HELP_AT, HELP_SRC, {})
            near_syms.update({k: hl[k] for k in ("hp_swap", "hp_table", "hp_full")})
            a0_, b0_ = "    beq t3,t2,nr_body             # a helper: unchanged", "    beq t3,t2,nr_help"
            if near_src.count(a0_) == 1:
                near_src = near_src.replace(a0_, b0_) + NEAR_HELP_SRC
        code, labels = assemble(NEAR_AT, near_src, near_syms)
        near_labels = labels
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert NEAR_AT + 4 * len(code) <= NEAR_END, "nearest glue too long"
        for i, w in enumerate(code):
            a = NEAR_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (an object thinks with the nearer hero as the player)"
        a, w0, w1, _what = HELPER_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (w0, w1), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (2 << 26) | ((labels["near_think"] >> 2) & 0x3FFFFFF)
        words[a + 4] = 0
        order += [a, a + 4]
        origin[a] = "glue hook (nearest): an object thinks"
        origin[a + 4] = "glue hook (nearest): its delay slot"
        n_glue += len(code) + 2

    if "--no-helpers" not in sys.argv and ("--no-nearest" in sys.argv or "--helper" in sys.argv):
        print("note: the helpers glue needs the 'an object thinks' hook of the nearest-hero glue; left out")
    elif "--no-helpers" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(HELP_AT, HELP_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert HELP_AT + 4 * len(code) <= HELP_END, "helper glue too long: %d words" % len(code)
        for i, w in enumerate(code):
            a = HELP_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (one helper goes with each hero when they split up)"
        n_glue += len(code)
        for a, w0, how, what in HELP_HOOKS:
            assert a not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<I", elf.data, off + a - va)[0]
            assert have == w0, "hook %08X: program has %08X" % (a, have)
            if how == "lui":
                w = 0x3C07000F                                      # lui a3,0x000F
            elif how.startswith("lo:"):
                lo = labels[how[3:]] & 0xFFFF
                assert labels[how[3:]] >> 16 == 0x000F and lo < 0x8000
                w = 0x24E70000 | lo                                 # addiu a3,a3,lo
            elif how.startswith("data:"):
                w = labels[how[5:]]
            else:
                w = (3 << 26) | ((labels[how[4:]] >> 2) & 0x3FFFFFF)
            words[a] = w
            order.append(a)
            origin[a] = "glue hook (helpers): " + what
            n_glue += 1

    if "--evrc" in sys.argv:           # EXPERIMENT, not in the build (no effect seen: tests h1-thorn-p2tri, h2-thorn-p1tri)
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(EVRC_AT, EVRC_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert EVRC_AT + 4 * len(code) <= EVRC_END, "event command glue too long"
        for i, w in enumerate(code):
            a = EVRC_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (a scripted move's command goes to the hero in the move)"
        a, w0, what = EVRC_HOOK
        assert a not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<I", elf.data, off + a - va)[0]
        assert have == w0, "hook %08X: program has %08X" % (a, have)
        words[a] = (3 << 26) | ((labels["ev_rc"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (event command): " + what
        n_glue += len(code) + 1

    if "--no-mash" not in sys.argv and "--no-box" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        for a, slot, what in MASH_HOOKS:
            assert a not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<I", elf.data, off + a - va)[0]
            assert have == 0x0C059FC6, "hook %08X: program has %08X, expected the getter call" % (a, have)
            assert struct.unpack_from("<I", elf.data, off + a + 4 - va)[0] == slot, "hook %08X: unexpected delay slot" % a
            words[a] = (3 << 26) | ((pad_both_at >> 2) & 0x3FFFFFF)
            order.append(a)
            origin[a] = "glue hook (either controller): " + what
        n_glue += len(MASH_HOOKS)

    if "--no-summon2" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(SUMMON_AT, SUMMON_SRC.format(O_SUMTW=V_SUMTW - 0x000F0000), {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert SUMMON_AT + 4 * len(code) <= SUMMON_END, "summon glue too long (%d words)" % len(code)
        assert V_SUMTW not in words, "variable address written by the patch"
        code2, labels2 = assemble(SUMMON2_AT, SUMMON2_SRC.format(O_SUMTW=V_SUMTW - 0x000F0000), {})
        code2 = [w if isinstance(w, int) else w[1] for w in code2]
        assert SUMMON2_AT + 4 * len(code2) <= SUMMON2_END, "summon glue 2 too long (%d words)" % len(code2)
        labels = dict(labels, **labels2)
        code3 = []
        if "--no-sumroom" not in sys.argv and "--no-nearest" not in sys.argv and "--helper" not in sys.argv:
            code3, _l3 = assemble(SUMMON3_AT, SUMMON3_SRC.format(O_SUMTW=V_SUMTW - 0x000F0000),
                                  {k: near_labels[k] for k in ("nr_twin", "nr_body")})
            code3 = [w if isinstance(w, int) else w[1] for w in code3]
            assert SUMMON3_AT + 4 * len(code3) <= SUMMON3_END, "summon glue 3 too long (%d words)" % len(code3)
        for at, block in ((SUMMON_AT, code), (SUMMON2_AT, code2), (SUMMON3_AT, code3)):
            for i, w in enumerate(block):
                a = at + 4 * i
                assert a not in words, "glue address already used: %08X" % a
                words[a] = w
                order.append(a)
                origin[a] = "glue (a summon called by the second hero is his)"
        code = code + code2 + code3
        for a, w0, kind, label, what in SUMMON_HOOKS:
            if label == "sm_skip" and "--sum-scene" in sys.argv:   # test option: the game's entrance scene
                continue
            assert a not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<I", elf.data, off + a - va)[0]
            assert have == w0, "hook %08X: program has %08X" % (a, have)
            if kind == "nop":
                w = 0
            elif kind.startswith("word:"):
                w = int(kind[5:], 16)
            else:
                w = ((3 if kind == "jal" else 2) << 26) | ((labels[label] >> 2) & 0x3FFFFFF)
            words[a] = w
            order.append(a)
            origin[a] = "glue hook (summon): " + what
        n_glue += len(code) + len(SUMMON_HOOKS)

    if "--no-promptguard" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        src = PROMPT_SRC if "--no-bigpool" in sys.argv else PROMPT_SRC.replace("lw t7,8100(t7)", "lw t7,%d(t7)" % POOL_COUNT)
        assert "--no-bigpool" in sys.argv or src != PROMPT_SRC
        code, labels = assemble(PROMPT_AT, src, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert PROMPT_AT + 4 * len(code) <= PROMPT_END, "prompt guard too long"
        for i, w in enumerate(code):
            a = PROMPT_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the prompt pool is never emptied by the twin's menu)"
        a, w0, what = PROMPT_HOOK
        assert a not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<I", elf.data, off + a - va)[0]
        assert have == w0, "hook %08X: program has %08X" % (a, have)
        words[a] = (3 << 26) | ((labels["sp_alloc"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (prompt pool): " + what
        n_glue += len(code) + 1

    if "--no-snaptwin" not in sys.argv and "--no-drive" not in sys.argv:   # twenty-second glue
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(SNAP_AT, SNAP_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert SNAP_AT + 4 * len(code) <= SNAP_END, "snapshot glue too long (%d words)" % len(code)
        for i, w in enumerate(code):
            a = SNAP_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the Continue snapshot holds the twin's own values)"
        for a, w0, label, what in SNAP_HOOKS:
            assert a not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<I", elf.data, off + a - va)[0]
            assert have == w0, "hook %08X: program has %08X" % (a, have)
            words[a] = (3 << 26) | ((labels[label] >> 2) & 0x3FFFFFF)
            order.append(a)
            origin[a] = "glue hook (Continue snapshot): " + what
        n_glue += len(code) + len(SNAP_HOOKS)

    if "--no-gummipad" not in sys.argv:                                  # twenty-sixth glue (+ twenty-seventh)
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        ship2 = "--no-ship2" not in sys.argv
        src = GMPAD_SRC.replace("@SHIP2_INSTALL@", SHIP2_INSTALL if ship2 else "").replace("@SHIP2_FLIGHT@", SHIP2_FLIGHT if ship2 else "")
        src = src.replace("@NOTWIN@", "" if "--no-notwin" in sys.argv else NOTWIN_SRC)
        if ship2:
            src += SHIP2_SRC
            zero = src
            for k in ("@JAL_BUILD_HI@", "@JAL_BUILD_LO@", "@J_FIRE_HI@", "@J_FIRE_LO@"):
                zero = zero.replace(k, "0")
            _c, lab0 = assemble(GMPAD_AT, zero, {})
            jb = (3 << 26) | ((lab0["g2_build"] >> 2) & 0x3FFFFFF)
            jf = (2 << 26) | ((lab0["g2_fire"] >> 2) & 0x3FFFFFF)
            for k, v in (("@JAL_BUILD_HI@", jb >> 16), ("@JAL_BUILD_LO@", jb & 0xFFFF), ("@J_FIRE_HI@", jf >> 16), ("@J_FIRE_LO@", jf & 0xFFFF)):
                src = src.replace(k, "0x%04X" % v)
        code, labels = assemble(GMPAD_AT, src, {})
        if ship2:
            assert labels["g2_build"] == lab0["g2_build"] and labels["g2_fire"] == lab0["g2_fire"]
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert GMPAD_AT + 4 * len(code) <= GMPAD_END, "gm_pad too long (%d words)" % len(code)
        for i, w in enumerate(code):
            a = GMPAD_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = ("glue (Gummi flight and menu: either controller; a second ship for player 2)" if ship2
                         else "glue (Gummi flight and menu: controller 1 also listens to controller 2)")
        a, w0, what = GMPAD_HOOK
        assert a not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<I", elf.data, off + a - va)[0]
        assert have == w0, "hook %08X: program has %08X" % (a, have)
        words[a] = (3 << 26) | ((labels["gm_pad"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (Gummi pad): " + what
        a, w0, what = GMPRE_HOOK
        assert a not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<I", elf.data, off + a - va)[0]
        assert have == w0, "hook %08X: program has %08X" % (a, have)
        words[a] = (3 << 26) | ((labels["gm_pre"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (Gummi pad): " + what
        n_glue += len(code) + 2
        print("Gummi glue: %d words at %08X-%08X (second ship: %s)" % (len(code), GMPAD_AT, GMPAD_AT + 4 * len(code) - 1, ship2))

    if "--no-nullguard" not in sys.argv:                                 # twenty-fifth glue
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        labels = {}
        for at, end, src in ((NULL1_AT, NULL1_END, NULL1_SRC), (NULL2_AT, NULL2_END, NULL2_SRC)):
            code, lab = assemble(at, src, {})
            code = [w if isinstance(w, int) else w[1] for w in code]
            assert at + 4 * len(code) <= end, "null guard too long (%d words at %08X)" % (len(code), at)
            labels.update(lab)
            for i, w in enumerate(code):
                a = at + 4 * i
                assert a not in words, "glue address already used: %08X" % a
                words[a] = w
                order.append(a)
                origin[a] = "glue (no read through a null pointer)"
            n_glue += len(code)
        for a, w0, kind, label, what in NULL_HOOKS:
            assert a not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<I", elf.data, off + a - va)[0]
            assert have == w0, "hook %08X: program has %08X" % (a, have)
            words[a] = 0 if kind == "nop" else ((3 if kind == "jal" else 2) << 26) | ((labels[label] >> 2) & 0x3FFFFFF)
            order.append(a)
            origin[a] = "glue hook (null guard): " + what
        n_glue += len(NULL_HOOKS)

    if "--no-wmpad" not in sys.argv and "--no-box" not in sys.argv:      # twenty-fourth glue
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(WMPAD_AT, WMPAD_SRC, {"pad_both": pad_both_at})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert WMPAD_AT + 4 * len(code) <= WMPAD_END, "wm_tick too long (%d words)" % len(code)
        for i, w in enumerate(code):
            a = WMPAD_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the world map listens to either controller)"
        for a, w0, kind, what in WMPAD_HOOKS:
            assert a not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<I", elf.data, off + a - va)[0]
            assert have == w0, "hook %08X: program has %08X" % (a, have)
            words[a] = ((3 << 26) | ((pad_both_at >> 2) & 0x3FFFFFF)) if kind == "jal_pad" else labels["wm_tick"]
            order.append(a)
            origin[a] = "glue hook (world map): " + what
        n_glue += len(code) + len(WMPAD_HOOKS)

    if "--no-healwho" not in sys.argv and "--no-heal" not in sys.argv:   # twenty-third glue
        code, labels = assemble(HWHO_AT, HWHO_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert HWHO_AT + 4 * len(code) <= HWHO_END, "heal_who too long (%d words)" % len(code)
        for i, w in enumerate(code):
            a = HWHO_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (a helper's item goes to the hero who needs it)"
        a, w0, w1, what = HWHO_HOOK                # a word of the BASE patch (lane N's routine) is replaced
        assert words.get(a) == w0 and words.get(a + 4) == w1, "lane N's n_heal is not where it was: %08X" % a
        words[a] = (2 << 26) | ((labels["heal_who"] >> 2) & 0x3FFFFFF)
        origin[a] = "glue hook (lane N's n_heal): " + what
        n_glue += len(code)

    if "--no-bigpool" not in sys.argv:      # twenty-first glue: 18 prompt objects
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        for a, w0, w1, what in POOL_WORDS:
            assert a not in words, "pool word already used: %08X" % a
            have = struct.unpack_from("<I", elf.data, off + a - va)[0]
            assert have == w0, "pool word %08X: program has %08X" % (a, have)
            words[a] = w1
            order.append(a)
            origin[a] = "glue (the pool of prompt objects holds %d): %s" % (POOL_N, what)
        n_glue += len(POOL_WORDS)

    if "--no-limit2" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(LIMIT_AT, LIMIT_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert LIMIT_AT + 4 * len(code) <= LIMIT_END, "limit glue too long (%d words)" % len(code)
        for i, w in enumerate(code):
            a = LIMIT_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (a Limit started by the second hero runs for him)"
        a, w0, w1, what = LIMIT_HOOK
        assert a not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (w0, w1), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (3 << 26) | ((labels["limit_run"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (Limit): " + what
        n_glue += len(code) + 1

    if "--no-heal" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(HEAL_AT, HEAL_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert HEAL_AT + 4 * len(code) <= HEAL_END, "heal glue too long (%d words)" % len(code)
        for i, w in enumerate(code):
            a = HEAL_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (the helpers heal the other hero too)"
        for a, slot, label, what in HEAL_HOOKS:
            assert a not in words, "hook address already used: %08X" % a
            have = struct.unpack_from("<2I", elf.data, off + a - va)
            assert have == (0x0C044788, slot), "hook %08X: program has %08X %08X" % ((a,) + have)
            words[a] = (3 << 26) | ((labels[label] >> 2) & 0x3FFFFFF)
            order.append(a)
            origin[a] = "glue hook (helpers heal): " + what
        n_glue += len(code) + len(HEAL_HOOKS)

    if "--no-reactown" not in sys.argv and "--react" not in sys.argv:
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(ROWN_AT, ROWN_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert ROWN_AT + 4 * len(code) <= ROWN_END, "own command glue too long"
        for i, w in enumerate(code):
            a = ROWN_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (a hero's own motion offers its command to that hero)"
        a, w0, w1, what = ROWN_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (w0, w1), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (3 << 26) | ((labels["react_own"] >> 2) & 0x3FFFFFF)
        words[a + 4] = w0                # daddu s3,a1,zero, now in the delay slot
        order += [a, a + 4]
        origin[a] = "glue hook (own command): " + what
        origin[a + 4] = "glue hook (own command): (the instruction that sat one word earlier)"
        n_glue += len(code) + 2

    if "--react" in sys.argv:          # EXPERIMENT, not in the build (it did not cure the fight it was made for)
        elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
        va, off, _fs = elf.segs[0]
        code, labels = assemble(REACT_AT, REACT_SRC, {})
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert REACT_AT + 4 * len(code) <= REACT_END, "react glue too long"
        for i, w in enumerate(code):
            a = REACT_AT + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue (Reaction Commands are offered to both heroes)"
        a, orig, what = REACT_HOOK
        assert a not in words and (a + 4) not in words, "hook address already used: %08X" % a
        have = struct.unpack_from("<2I", elf.data, off + a - va)
        assert have == (orig, 0x3C0F0035), "hook %08X: program has %08X %08X" % ((a,) + have)
        words[a] = (2 << 26) | ((labels["react_both"] >> 2) & 0x3FFFFFF)
        order.append(a)
        origin[a] = "glue hook (control object): " + what
        n_glue += len(code) + 1

    out.mkdir(parents=True, exist_ok=True)
    head = [
        "gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
        "comment=Two-player project, MERGED BUILD 6: merged build 5 (twin on pad 2, own HP, commands, exits, enemy",
        "comment=targeting, down and rescue, gauge for player 2, boss HP gauge, ring rule) + own Drive values for the",
        "comment=second hero across rooms + text boxes listen to either controller + prizes for the second hero.",
        "comment=Every PC in an online game must have this same file.",
    ]
    body = ["patch=1,EE,%08X,word,%08X" % (a, words[a]) for a in order]
    (out / NAME).write_text("\n".join(head + body) + "\n", encoding="utf-8")
    listing = ["%08X %08X  %s" % (a, words[a], origin.get(a, "merged-v5")) for a in sorted(words)]
    (out / "listing.txt").write_text("\n".join(listing) + "\n", encoding="utf-8")
    print("merged-v5 words:", len(order) - n_glue, "+ glue words:", n_glue, "=", len(order))
    print("written:", out / NAME)
    print("sha1:", hashlib.sha1((out / NAME).read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
