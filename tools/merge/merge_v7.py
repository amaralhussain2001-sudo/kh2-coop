"""Merged build 7 = merged build 6 (TEST BUILD 12's shared-screen patch, patches/merged-v6, SHA-1 00e5112f...)
+ THE GLUES OF THE EIGHTH ROUND (2026-11-14). merge_v6.py is not changed any more: with no options it still writes
build 12's file. Every glue here has its option; with all of them left out the result is build 12 word for word.

NEW ROOM FOR ROUTINES. The old cave 0x000F0000-0x000F7FFF is nearly full. Memory 0x00096000-0x000EFFFF was all
zero at five points of a run of the build (boot, title, New Game, a fight; test r8z-HB17_MS405-66, probe
tools/own/zero_probe.py; below it sit the boot loader's leftovers, 0x00081DD0-0x00095061). This round uses
0x000E8000-0x000EFFFF for routines and 0x000E7C00-0x000E7FFF for values. (HYPOTHESIS that nothing else ever uses
it: the same kind of memory as the old cave, which the game has left alone in every test.)

THIRTIETH GLUE (option --no-eitherspawn leaves it out): ENEMY SPAWN ZONES ALSO REACT TO PLAYER 2'S HERO.
What was there (lane R, docs/lanes/R-exits.md, kind 2: 1,841 volumes in 139 rooms): a zone that makes its enemies
appear when "the hero" walks in is offered player 1's hero only. Player 2 walking ahead alone met nobody (test
r-11-spawn-x3, default patch: no enemies). Lane R built the cure as an option of its generator (--either-spawn,
tested: the enemies appear) and left it off until enemies would choose between the heroes (lane H, long in the
build). It was never merged.
Now: lane R's volume routine r_inside (0x000F3000) branches, when player 1's hero is NOT inside, to sp_either
(the word 0x000F3014 of the base patch: "beq v0,zero,ri_out" becomes "beq v0,zero,sp_either"): on the game's own
offer (not the second one), for kind 2 only, the twin's place is tested with the volume's own method; inside =
the zone fires. No second offer is made, so the spawn timers do not run twice (lane R's design, word for word).
While a hero is down no zone fires at all (the build's "no exit while a hero is down" wrapper, unchanged).

THIRTY-FIRST GLUE (option --no-revenge leaves it out): A BOSS'S "REVENGE" COUNT WITH TWO HEROES (plan row 40).
What was there (read in the program, then seen: tests r8rv1 / r8rv2 / r8rv3): every hit adds its attack's revenge
value (attack entry + 0x2A) to the target's counter (float at object + 0xAF0; routine 0x00185CB8, the add at
0x00185CE0-0x00185CE4); the boss's script breaks out of a combo when the counter is high enough. Nobody asks who
hit, so two heroes fill the counter up to twice as fast as one.
Now (the two instructions 0x00185CE0 / 0x00185CE4 go through rv_scale): while there is a twin, a hit whose
attacker (hit record + 0x10) is a player object (bit 0x80 of object + 0x588) adds REVENGE_FACTOR (0.75) of its value. So one hero alone
needs a third more hits before the boss breaks out, both together still fill it 1.5 times as fast as one hero
did. Helpers' hits, hits on anything by anybody else, and a game with one hero: unchanged.

THIRTY-SECOND GLUE (option --no-getup leaves it out): A HERO WHO GETS UP BY HIMSELF IS NOT IN THE LOW-HP WARNING
(plan row 43). What was there: lane N lets a fallen hero get up when his timer runs out, with the game's own
helper routine 0x0017DE70: most HP x 0.5, halved again by the revive = a quarter. The game's "HP is low" test is
0x001A2478: HP <= most HP >> 2. So he got up exactly ON the line, with the warning on (5 of 20).
Now (the base patch's word 0x000F2974, lane N's "jal 0x0017DE70", calls gu_fix): after the recovery, when his HP
is above 0 and not above the line, it is set to (most HP >> 2) + 1 (6 of 20), never above his most HP.
A hero brought back by a Potion or Cure: unchanged (the game's own amounts).

THIRTY-THIRD GLUE (option --no-keychange leaves it out): A KEYBLADE CHANGE IN THE PAUSE MENU NO LONGER STOPS THE
GAME (register G1 -> fault F5, found 2026-11-14: tests t15-keychg, r8kc2, r8kcvt).
What was there: the menu changes a weapon with 0x00175F68(record, character number, hand, item) (one caller,
0x002933D0). It takes the party member with that character number (player 1's hero for Sora), ends his weapon
object of that hand (0x0019C5D0, 0x00185A28), UNLOADS THE OLD WEAPON'S FILES (0x001703A8), loads the new ones
(0x0016EF58) and builds the new weapon (0x00176168(hero, weapon object, hand)). The twin holds the same Keyblade
(the same files) and was not asked: his weapon object kept pointing into the unloaded files. The next step that
moved his Keyblade called through a dead class table (0x0017FE74..84, object 0x01A947C0 = the twin's weapon in
the test) and the game ran to address 0. The Steam co-op mod had the same crash.
Now (the menu's jump goes to wc_both): when there is a twin and the changed character is his own (the same
character number, 0x0016A070), the twin's weapon of that hand is ended FIRST, exactly as the game ends the
hero's; then the game's routine runs; then the twin's new weapon is built for his own body with the game's own
steps (0x00185890(body's weapon set, item) -> 0x00176168(twin, object, hand), and the weapon's class method
+ 0x48 when the old weapon's end said so, as the game does). Another character's weapon (Donald, Goofy, a
guest), a game with one hero: the game's routine alone.
(When plan row 39 gives the twin his own Keyblade this routine stays the place: the files of a Keyblade that
either hero still holds must not go.)

THIRTY-FOURTH GLUE (option --no-twoforms leaves it out): BOTH HEROES CAN BE IN A DRIVE FORM AT THE SAME TIME
(plan row 44; it changes row 15's "one form at a time").
What was there (read, then seen with the row recorder tools/own/make_rowrec.py, tests t15-rowA / t15-rowB): the
main player class's constructor raises bit 0 of the lock word 0x00351EB8 when the body it builds is a form (1 to
6; 0x001D0CA4) and its destructor lowers it (0x001D0D48). A Limit and a Summon raise the same bit while they
run. Every asker asks "any bit?": the Drive list of a control object is not built while it is set (0x001BEB68)
and a form row is judged dim (0x001BC594). So while one hero was in a form the other hero's Drive did nothing.
The game's own "is the helper there" rule (0x001C99B0: Valor needs Goofy, Wisdom Donald, Limit Form nobody,
Master / Final both) already refuses a form only when its helper is away: exactly plan row 44's rule.
Now: (1) the two Drive askers go through fm_ask: locked for THIS hero when another bit of the word is set, when
he is in a form himself, or when bit 0 is set and NEITHER hero is in a form (then a Limit or a Summon holds it;
a form, a Limit and a Summon shut each other out, so while a hero is in a form bit 0 can only mean forms);
(2) the destructor's lowering goes through fm_lower: the bit stays while the OTHER hero is still in a form.
A form change itself is still one at a time (the lock word 0x00351EC0 bit 1 while a change runs: unchanged).
Limits and Summons stay shut for both players while either is in a form, as before.

THIRTY-FIFTH GLUE (option --no-formfiles leaves it out): A HERO'S FORM FILES STAY WHILE THE OTHER HERO CHANGES
Fault F6 of the eighth round (run tf2 / tf2b): with player 1 in Valor Form, player 2 picks Wisdom Form and the game
leaves to the PS2 browser 36 frames later. Read in the program: before a form's files are asked for, the form task
calls 0x00170320(5000) (at 0x001B66F8): every loaded file with a keep-number of 5000 or more (= the files of forms,
of a Summon, of King Mickey) is marked "may be thrown out" (0x00170018), and the next load throws them out when it
needs the room. The game never has two form bodies, so that is safe there; here player 1's body still uses them.
King Mickey's rescue does the same at 0x001D0080.
Now (second version, after runs tf3 / tfpm: asking for the files again made NEW entries and did not keep the ones in
use) the game's call is simply NOT MADE while the other hero is in a Drive Form (fk_form, at the form task) or
while any hero is in one (fk_mickey, at King Mickey's file request). With one hero: as the game.

THIRTY-SIXTH GLUE (option --no-nearcb leaves it out): A BOSS'S SCRIPTED MOVE TAKES THE HERO WHO IS IN IT, OR THE
NEARER HERO (plan row 9, first step; register G3).
What was there (runs gp4, cap0, cap1 of the eighth round): Shan-Yu's clash always takes PLAYER 1'S HERO, even when
he stands idle and player 2 fights alone; so player 2 can never win a clash. The recorder at the game's paired-move
routine 0x00180378 shows why: every call (moves 0xFC to 0xFF) comes from the boss's MOTION update (a frame trigger
of his animation runs a callback of his script: 0x001B9840 -> 0x0017F744 -> 0x0016CCE8 -> trap 0x00172440), and in
a callback "the player" is the engine's player = player 1's hero. The twelfth glue's rule "the nearer hero is the
player" holds only while the object THINKS (0x0016A950).
Now (jump at 0x0016CCE8, routine nc_trig): while a callback of the OWN script of an object runs that is neither a
hero nor a helper, and there is a twin: a hero who is held in a paired move by this object (hero + 0x240 = the
word at object + 0x140, bit 0x4000 of + 0x160) is "the player"; if none is, the nearer hero who is not down, as in the twelfth
glue. The engine's player pointer holds the twin for the length of that one callback only.
Added after run of270 (the recorder at "offer a command"): the command "Press" of the clash is offered by a frame
trigger of the HERO'S OWN clash motion: a callback of the hero's script calls the script routine 0x00174328, which
takes the engine's player's control object. So a callback of THE TWIN'S OWN script now also runs with the twin as
"the player" (player 1's hero's own script: unchanged).
(A sixth version of the twelfth glue had the "nearer" half of this on 2026-11-11, tests g7-thorn / g9-thorn; it
was taken out only because the command it was made for did not move. The "held by this object" half is new.)

THIRTY-SEVENTH GLUE (option --no-mickey leaves it out; --mickey1 keeps only its last part): KING MICKEY'S RESCUE
FOR TWO (plan row 45, register F1).
What was there: when both heroes are down in one of the eleven Mickey missions and the roll is won, the game parks
the engine's player (0x00179E48: the hero goes from 0x0034E948 to the parking place 0x0034E94C), builds King
Mickey as a NEW player object with the fallen hero's controller (0x001D00A8) and holds the hero in Mickey's paired
move 252. Player 1 plays Mickey; player 2 watches his fallen hero. The rescue ends in 0x001D0228 (paired move 253)
or 0x001D02C8 (move 254, Mickey's "Healing Light", effect kind 4): Mickey's end method, the parked hero back
(0x00179EB8), the paired move that lifts him. The twin stayed down for the rest of the fight.
Now:
(1) mk_both (the call at 0x001AF628): after the game's call, when the twin is down too, the same routine runs a
    second time with the twin as "the player": he is parked (in the glue's own place 0x000E7C00), a second Mickey
    is built with HIS controller and holds him in move 252. That Mickey is "the twin" (0x000F05CC) for the length
    of the rescue, so player 2's view, HUD, menu and controller are his. The engine's player and the game's attach
    go back to player 1's Mickey.
(2) mk_end (the two calls of the end routines, 0x00172EBC and 0x001BA5C8): whichever Mickey ends the rescue, both
    end: the game's routine for player 1's Mickey, then the same routine for the second Mickey with the twin in
    the parking place; the twin is the twin again, the engine's player is player 1's hero again.
(3) a twin who is still down after the rescue's end is brought back the way lane N brings a hero back (his class's
    HP change with lane N's "down" word set), and his HP is filled as the hero's is. With --mickey1 only this part
    is built (one Mickey, played by player 1; the Healing Light brings both heroes back).

THIRTY-EIGHTH GLUE (option --no-reactheld leaves it out): THE COMMAND OF A BOSS'S PAIRED MOVE GOES TO THE HERO WHO
IS HELD IN IT (plan row 9, first step, second half).
What was there (run gp5, candidate v39, pictures p1_f017000 / p2_f017000): with the thirty-sixth glue Shan-Yu's
clash takes PLAYER 2'S hero when he is the one who fights, but the command "Press" still sits in PLAYER 1'S menu.
It is offered by a frame trigger of the BOSS'S motion: routine 0x00189E18(source object, command, argument) gives
it to the control object of the engine's player. The fifteenth glue (react_own, hook 0x00189E3C) hands the twin in
only when the twin himself is the source.
Now the hook goes to ro2: the twin is "the player" of that one offer when he is the source (as before) OR when he
is held in a paired move by the source (twin + 0x240 = the source, bit 0x4000 of + 0x160). Everything else: as it
was.

THIRTY-NINTH GLUE (option --no-thinkheld leaves it out): AN OBJECT THAT HOLDS A HERO IN A PAIRED MOVE ALSO THINKS
WITH THAT HERO AS THE PLAYER (plan row 9, first step, third half).
What was there (run cap2, candidate v39, the recorder at 0x00180378): one clash of Shan-Yu MIXED the heroes: the
start (moves 0xFC, 0xFD) took the twin, the next pushes (0xFF, 0xFD) took player 1's hero, the end (0xFE) the twin
again. The thirty-sixth glue keeps "the hero who is held" for the script's CALLBACKS, but while the boss THINKS the
twelfth glue still hands in the NEARER hero, and part of the clash is started from there.
Now the jump at 0x0016A950 goes to nt_held first: for an object that is neither a hero nor a helper, the twin is
the player of its thinking while the twin is held by it (twin + 0x240 = the object, bit 0x4000 of + 0x160); while
player 1's hero is held by it the thinking runs as the game's (no "nearer" rule); otherwise the twelfth glue's
near_think (0x000F5000) decides as before.

FORTIETH GLUE (option --no-helperform leaves it out): A HELPER WHOM THE TWIN'S DRIVE FORM USES STAYS AWAY WHEN A
ROOM IS BUILT (register G5, "Final Form after a room change"; plan row 44).
What was there (run ffd3, build 12, picture p2_f006260): player 2 goes through a door in Final Form (which uses
Donald and Goofy). In the new room he is still in Final Form, and BOTH HELPERS STAND THERE AGAIN. Read in the
program: when a helper is put into a room, routine 0x0017E4xx asks 0x001C9958(form, the helper's kind) with the
save's form byte (0x0032F054 = player 1's form) and sends him away when that form uses him. The twin's own form
number (0x000F47E8, ninth glue) is not asked.
Now the call at 0x0017E488 goes through hf_either: the game's question for player 1's form, then, when the answer
is no and there is a twin, the same question for the twin's form.

FORTY-FIRST GLUE (option --no-formbase leaves it out; needs the thirty-fourth): THE FILES OF A SECOND DRIVE FORM
GO BEHIND THE FILES IN USE, AND A SECOND FORM IS REFUSED ONLY WHEN THE FILE POOL HAS NO ROOM (plan row 44, fault F6).
What was there (runs tfpm / fp1 of the eighth round, probe tools/own/filepool_probe.py): the loader keeps every
object file in one pool (list head 0x0034DCA0, limit word 0x0034DCB0 = the start of the object heap), laid out in
the order of the files' keep-numbers. A form's files are asked for with the numbers 5000 (the body), 5001 and 5002
(its weapons). With player 1 in Valor, player 2's Wisdom body (three files, 2.1 MB, number 5000) is put in FRONT of
Valor's weapon files (5001 / 5002): they move from 21,893,184 to 24,021,056 and are loaded again there, while
player 1's Keyblade still points at the old data. His body's next update calls into the destroyed data: the C++
runtime's "pure virtual method called", abort(), and the game leaves to the PS2 browser. The memory itself was
enough: 1.38 MB of the pool stayed free with both forms.
Now:
(1) fb_req (the form task's file request at 0x001B6700): while the OTHER hero is in a form, the changing hero's
    files are asked for with a number base 10 above the other hero's base (5010, 5020 ...), so they are laid out
    behind everything in use and nothing moves. Each hero's base is kept at 0x000E7C04 / 0x000E7C08. With no twin,
    or when the other hero is in no form: 5000, as the game.
(2) the thirty-fourth glue's judge of a form row (fm_ask_judge) now also asks, for a SECOND form only: is there
    room? Room = the pool's limit minus the end of the last file that may not be thrown out (keep-number below
    10000); it must be at least the form's need (table fa_need, measured in runs fp1 to fp5 + 64 KB). No room =
    the row is dim, exactly like a form whose helper is away.

FORTY-SECOND GLUE (option --no-helperback leaves it out): WHEN ONE OF TWO DRIVE FORMS ENDS, THE HELPERS THAT THE
OTHER HERO'S FORM USES STAY AWAY (plan row 44).
What was there (run tf5, candidate v47, picture p1_f006700): player 1 is in Valor (Goofy), player 2 in Wisdom
(Donald). Player 2 reverts, and BOTH helpers stand there again while player 1 is still in Valor. Read in the
program: the form record's cleanup (0x001B6450 / 0x001B6518) calls 0x001C9B90 for a revert, which brings back
EVERY helper on the "away" list (0x01D49980, count 0x00351F30).
Now both calls go through hb_back: the game's call, then, while there is a twin, the game's own "send this form's
helpers away" (0x001C9860(form)) once for each hero who is still in a form. (The hero who reverted has form 0 by
then: his number is cleared when the revert is asked for.)

FORTY-THIRD GLUE (option --no-heroscript leaves it out): THE SCRIPT THAT A PAIRED MOVE ATTACHES TO THE TWIN RUNS
WITH THE TWIN AS "THE PLAYER" (plan row 9, first step: the prompt in the right menu).
What was there (runs gp8 / gp9 and of270, the recorder at "offer a command"): in Shan-Yu's clash player 2's hero
is held, his Triangle presses count, but the prompt "Press" (command 270) sits in PLAYER 1'S menu. The first
offer's stack: the hero's own update (0x00178934 -> 0x00177510) runs the script attached to him for the move
(hero + 0xAEC) with 0x0016CD48, and that script calls the script routine 0x00174328, which offers the command to
the control object of the engine's player. That is player 1's hero, whoever the script is attached to.
Now the call at 0x00177510 goes through hs_tick: when the hero is the twin, the engine's player pointer holds the
twin for the length of that one call. Player 1's hero, or no twin: as the game.

FORTY-FOURTH GLUE (option --no-captureform leaves it out): A BOSS'S "CAPTURE FORM" (LUXORD'S CARD AND DIE) TAKES
THE HERO THE TRICK IS PLAYED ON (job 10 of the eighth round, fault F11).
What was there (runs luxc / lux2, in build 12 too): in Luxord's story fight player 2's hero is pulled into a
paired move at the start (FC, then FE) and stays in FE for the whole fight. Read in the program: the script calls
trap_player_capture_form (0x001741E0 -> 0x001B6BD8(hero, object)) and trap_player_capture_form_end (0x00174210 ->
0x001B6C20(hero)) take the hero from 0x001D14A0 = the last-built hero object (0x00352400), which is always player
1's hero; the paired moves of the same trick take "the player" of the script (the nearer hero, twelfth glue). So
the twin was held, PLAYER 1'S hero was turned into the card, and the twin's hold never ended. And 0x001B6C20
gives the body back in "the current form" of the save data, which is player 1's number.
Now:
(1) cf_who (the call at 0x001741EC): while there is a twin, the hero is the one who is HELD in a paired move when
    only one of the two is; otherwise the engine's player (the script's own "player"); no twin: as the game.
(2) cf_end_who (the call at 0x00174218): the hero who IS in a capture form (body form 12): the twin when only he
    is, the engine's player when both are; otherwise as the game.
(3) cf_form (the jump at 0x001B6C54): when the body that comes back is the twin's, the form number is his own
    (0x000F47E8).

FORTY-FIFTH GLUE (option --no-scriptplayer leaves it out; it uses the hold memory of glues 36 / 39): A SCRIPT THAT
ASKS FOR "THE PLAYER" GETS THE HERO ITS OBJECT HOLDS, WHEREVER THE SCRIPT RUNS (job 10: Xigbar's sniper part,
Luxord's card trick; faults F10 / F11).
What was there (runs xig, xig2, xigdc, luxc of the eighth round): a boss's trick in several steps starts on the
twin (paired moves FC, FD, FF) and then never lets him go; in build 12 the same fights stop or hold him too. The
steps of such a trick are not all run from the boss's thinking (0x0016A950) or from a callback (0x0016CCE8), where
the glues 12 / 36 / 39 put the right hero into the engine's player pointer: scripts also run as their own threads
(trap_magic_start_thread) and from other runners (0x0016CD48 has eleven callers), and there the script call
trap_sysobj_player (0x00171068 -> 0x0016B0D0) answers "the engine's player" = player 1's hero.
Now the call inside that script routine (0x00171074) goes through tp_player: the game's answer first; then, while
there is a twin and the running script (0x0034D8A4) belongs to an object that is neither a hero nor a helper: the
hero that this object holds in a paired move now, or held less than 90 steps ago (the hold memory 0x000E7C0C),
is the answer. Nobody held: the game's answer stays (inside thinking and callbacks that is already the nearer
hero).

FORTY-SIXTH GLUE (AN EXPERIMENT THAT DID NOT HELP; built only with the option --playernear; it needs the
forty-fifth and replaces its routine):
A SCRIPT'S "THE PLAYER" IS THE SAME HERO IN EVERY PLACE THE SCRIPT RUNS (job 10, faults F10 / F11).
What was there (runs x1, x2, x3 of chain 40, recorder at the paired-move call): with ONE hero Xigbar's sniper part
makes ONE capture (move 0xFC at counter 4988) and ends by itself. With two heroes there are TWO captures in the
same step, one for each hero, then 0xFD and an endless row of 0xFF every 84 steps on the twin, and the part never
ends, with the forty-fifth glue too. The first capture's stack shows where the script's own thread runs: object
update 0x00178C84 -> 0x0016BB28 -> 0x0016CB54 -> 0x0016CC9C -> the runner 0x0016CD48. In that path the engine's
player is player 1's hero, while in the object's thinking (0x0016A950, twelfth glue) it is the NEARER hero. So one
script saw two different "players" in one step and held both.
Now tp_player2 answers trap_sysobj_player for an object that is neither a hero nor a helper: the hero this
object holds in a paired move now; else the hero it held less than 90 steps ago; else THE NEARER HERO by the
twelfth glue's own rule (a hero who is down does not count; as near = player 1's hero). The same answer in the
thread path, in callbacks and in thinking.
And cf_who2 (the call at 0x001741EC, forty-fourth glue): Luxord's "turn the hero into a card / a die" asks the
same routine, so both halves of his trick take the same hero (run lux5: with the forty-fourth glue alone the
first trick still held player 2's hero while player 1's hero was the die).

FORTY-SEVENTH GLUE (option --no-sender leaves it out): THE HERO WHO PRESSES A REACTION COMMAND IS "THE PLAYER"
OF THE CALLBACK IT SENDS, AND AN OBJECT THAT HOLDS ONE HERO DOES NOT TAKE THE OTHER HERO'S COMMAND (job 10: Xigbar's
sniper part, Luxord's card trick, the stray calls of Shan-Yu's clash; faults F10 / F11).
What was there (chain 46, the recorder at the paired-move routine with the stack of calls 1 to 4): Xigbar's two
captures at counter 4988 both come from THE SAME PLACE: a hero's update runs his command (0x00178C7C: record at
hero + 0xB44, kind 0 = a Reaction Command) and calls function 11 of the SOURCE object's script through 0x0016BAE8
(source, hero, ...) -> the callback runner 0x0016CCE8. The script then pulls THE HERO IT WAS GIVEN into the move.
Both test players press Triangle in the same frame, so both heroes sent "Warp Snipe" and one boss held two
heroes; his script is written for one and never found its end. (With ONE hero the same press gives one capture
and the part ends: run x1.) And the thirty-sixth glue ran such a callback with "the player" = the held or the
NEARER hero, not the hero who sent it: one of the two captures ran with the twin as the player while player 1's
hero was the one pulled in. Luxord's trick is the same split (the grab takes the sender, the card / die took "the
player"). The forty-sixth glue (the nearer hero in every runner) did not change either fight (runs x9, lux9); it
is now built only with --playernear.
Now:
(1) rc_one (the call at 0x00178C7C): when the source is an object that is neither a hero nor a helper and it
    HOLDS THE OTHER HERO in a paired move at this moment, or held him less than 90 steps ago (the hold memory of
    the glues 36 / 39), this hero's command does nothing. Otherwise the callback
    is sent, and the sender is noted (0x000E7C18) while it runs.
(2) ns_pre (the jump at 0x0016CCE8 comes here first): while a sender is noted and the callback's script belongs
    to such an object, the callback runs with THE SENDER as "the player" (the twin: the engine's player is the
    twin for that call; player 1's hero: as the game). No sender: the thirty-sixth glue's nc_trig as before.

FORTY-EIGHTH GLUE (NOT in builds 13 / 14; built only with the option --ownrec): THE SECOND HERO'S UNIT SLOT READS A
CHARACTER RECORD OF HIS OWN (plan row 39 "own gear for each player", stage 1a; job 11 of the eighth round).
What is there (lane D, `tools/lane-d/make_ownhp2.py`): both heroes' unit slots point at the SAME character record
(Sora's, save + 0x24F0 = 0x0032E020, 0x114 bytes; slot + 0x244); only the current HP / MP bytes are the twin's own.
The game loads a slot's stats, abilities and equipment bonuses from that record in 0x001A11E0(slot, record or 0)
(experiments e1a / e1b / e1c: a second record in the twin's slot works; run or1: the first form of this glue).
The record has 8 armour places (+ 0x14 .. + 0x23) and 8 accessory places (+ 0x24 .. + 0x33); a hero's counts
(+ 0x10 / + 0x11) never pass 4. PLAYER 2'S FOUR ARMOUR PLACES ARE + 0x1C .. + 0x23 AND HIS FOUR ACCESSORY PLACES
+ 0x2C .. + 0x33 OF THAT SAME RECORD: saved, loaded and kept by Continue with the game's own save.
Now t_load (the jump at 0x001A1200, the stat loader's "which record" step): for the twin's slot (lane D's mark, bit
31 of slot + 0x250) the record is T (0x000E7D00, 0x114 bytes; 0x000E7E20 = the record it shows): every time T = a
full copy of the source record, with player 2's places where the hero's are and the hero's where player 2's
are. (While player 2's menu is open, forty-ninth glue, the source has them changed already: a plain copy.)
The slot's pointer (slot + 0x244) is set to T. Everything else is common: Keyblade, abilities, item places.
Only a HERO's slot (status id 1 = Sora, 14 = Roxas) gets player 2's places; any other body of the twin (King
Mickey) reads a plain copy. The hero's record is noted at 0x000E7E28 for the forty-ninth glue.

FORTY-NINTH GLUE (built only with --ownmenu; it needs --ownrec): PLAYER 2 CHOOSES HIS ARMOUR AND ACCESSORIES IN THE
PAUSE MENU WHEN HE OPENED IT.
The menu only knows "Sora's record". START is looked for at 0x00138538 (second glue: on both controllers) and the
main menu is opened by the call at 0x00138574 -> 0x00253180(0, -1).
 mo_open (that call): when there is a twin and START was pressed on controller 2 and not on controller 1, the
   hero's places 1 to 4 and player 2's places 5 to 8 change places in the source record (armour and accessories),
   a flag is set (0x000E7E24) and player 1's slot loads its stats again (lane D's D6 then loads the twin's), so
   the menu shows and edits PLAYER 2's places with his numbers.
 ms_tick (the call at 0x00138538, each step the field looks for START; it is not reached while a menu is open):
   when the flag is set the places change back, the flag is cleared and player 1's slot loads its stats again
   (and with it the twin's).
The bag is common: both players equip from the same stock.
The flag is also cleared when a save file is copied into the save data (0x00240B84) and when the save data are
made new (0x00105770), so it cannot stay set over a reset.

FIFTIETH GLUE (built only with the option --together; plan row 9, second half; the user's decision of 2026-11-10
"both heroes do a boss's scripted move together"): BOTH HEROES IN SHAN-YU'S CLASH.
Read in the program and in Shan-Yu's script (B_MU100):
 - the hero's side of a boss's move is a script that the boss's script HOOKS onto the hero (the script call
   trap_obj_hook = 0x00171FA8: a new context from 0x0016CF00(the boss's script, 0, function, [hero, extra], count),
   set on the hero with 0x00177460 = hero + 0xAEC, run once a step at 0x00177510). That hooked function makes
   the clash's captures on its hero (252, 253, 255, 254), offers "Press" / "Takedown" and counts the pushes;
 - a hooked context shares the boss's work memory (context + 16; + 52 is its handle); the boss's own numbers of
   the clash sit there (Shan-Yu: push count, push speed, time limit at work + 148, + 152, + 156) and the
   hero-side loop steps them.
The routines (0x000E9C00 ..; values 0x000E7E30 .. 0x000E7E48), all only in Shan-Yu's room (world 08, room 09):
 th_new (the call at 0x00171FE4): a PAIR is made when an enemy's script (not a hero's, not a helper's) hooks a
   script onto a hero and the hook is not the answer to a hero's own command: the other hero, when he is up,
   free (not held, no hooked script) and within 500 units, is put 55 units beside and 55 units behind the first
   (0x0016AF58 get direction, 0x0016ACE0 set position, 0x0016AEF0 set direction) and gets HIS OWN COPY of the
   hooked script. While the pair lives, every later hook on one of the two (the push, the takedown) is copied to
   the other as long as he is still in the move.
 th_tick (the call at 0x00177510): notes "a hero's hooked script runs" (0x000E7E48). When it is the script of the
   SECOND hero of the pair (the one who got the copy last), the boss's three numbers are kept before the run and
   put back after it: one script steps the boss's clock, and a press counts once (the hero who presses becomes
   the first hero at that moment).
 tg_cap (the jump at 0x00180378, the paired-move routine): a capture that the boss's OWN script makes on one hero
   of a living pair is copied to the other while he is still in the move (he is turned to the boss first).
   Without a pair nothing is copied: a grab or a lift (the falcon) stays that hero's alone.
 tg_tick (the call at 0x00138538): the pair is forgotten 10 steps after nobody is held and nobody has a hooked
   script. Safety rule: a hero of the pair who is held, has no hooked script and got no capture for 120 steps is
   freed ("no motion" 0x0017EFA0, then "go idle" 0x0016BD60(hero, 0)).
 tg_ro (0x00189E3C): a command offered by the boss's MOTION goes to both heroes of the pair.
 And the forty-seventh glue's rule "one object holds one hero" lets both heroes of a living pair press.
NOT together with the test recorders that sit on 0x00180378 (the kits -cap).

FIFTY-FIRST GLUE (built only with the option --ship2hit): PLAYER 2'S GUMMI SHIP CAN BE HIT AND HAS ITS OWN HULL.
What was there (lane S3, and the seventh round, part 7c): the second ship of the twenty-seventh glue is never
damaged; its hull stays at its first value while ship 1's goes down.
Read in the flight module (ovl_gumibattle.x at 0x01F18000): every kind of enemy shot asks for "the player ship"
with the getter 0x01F21CF8 (132 callers; the pointer 0x01F7DE44), makes a ball of its own place and size
(0x01F406E0) and asks the SHIP "does this ball touch you" (0x01F217C8(ship, ball)), then "can you be hit now"
(0x01F217A8(ship)), then calls the ship's "you are hit" (0x01F20320(ship, hit record); five callers) or its
"take damage" (0x01F203A8(ship, amount); two more callers). "Take damage" takes the amount off the hull in the
ship's own status record (ship + 0x4A8; 0x01F23320) and starts the end of the ship when the hull is 0. All of
these routines work on the ship they are handed. Only the question is asked about ship 1 alone.
gs_inst (the call at 0x00167E90, before the twenty-sixth glue's gm_pad): when a fresh flight module is in memory
  (its mark 0x636A and the four places still the game's own words), four jumps are written into it.
gs_test (0x01F217C8): the question about ship 1 is asked for ship 1 first; when ship 1 is not touched and ship 2
  is under control (state 2), it is asked for ship 2; when ship 2 is touched, "the hit is ship 2's" is noted
  (0x000E7E4C). Every new question clears the note.
gs_able (0x01F217A8), gs_hit (0x01F20320), gs_dmg (0x01F203A8): while the note stands, a call for ship 1 is a
  call for ship 2; "you are hit" and "take damage" use the note up.
NOT KNOWN before the runs: what the flight does when SHIP 2's hull is 0 (the game's own end of the mission is
started by "take damage" for whichever ship it is handed).

FIFTY-SECOND GLUE (built only with the option --carpet2): A CARPET UNDER PLAYER 2'S HERO.
What was there (seventh round, part 7e; disc v5 gives player 2 a carpet RIDER of his own): one carpet only; it
stays under the engine's player, and player 2's hero flies in the riding pose with nothing under him.
Read in the program:
 - the carpet is the object 0x0168 (N_AL010_BTL, kind BTLNPC, status 5008); the BTLNPC class (0x00351078) writes
   the last one built to 0x00351068 and puts it into the action state 19;
 - state 19's own routine 0x001B2DB8 (the word at 0x00350FF8 in that state's table 0x00350FE0) takes THE ENGINE'S
   PLAYER (0x0034E948) every step, turns the carpet as he looks (0x0016AFE0 / 0x0016AEB8) and puts it at his place
   (0x0016C028, 0x0016ACE0). That is all that binds the carpet to a hero; it is not a paired move (run carp1);
 - the hero's side starts the carpet's motions with the pointer 0x00351068 at four places (0x00178E1C, 0x00178E34
   in the hero's command routine, 0x00178E94 in its end call, 0x001B2A04 in the riding state 10);
 - the game makes an object with 0x0016F000(object number, place, turn): the same routine the script call "make
   an object" uses.
gc_tick (the call at 0x00138538, each step of the field): when BOTH heroes are carpet riders (object 0x04FF) and
  the game's carpet is alive, a SECOND carpet is made once at player 2's hero (0x000E7E54; made for the carpet
  0x000E7E58; at most four tries for one carpet, 0x000E7E5C). 0x00351068 stays the first carpet.
gc_upd (the word at 0x00350FF8): the second carpet's state routine runs with player 2's hero as "the player".
gc_c1, gc_c2, gc_c3 (the four places): a carpet motion started by player 2's hero goes to the second carpet.

FIFTY-THIRD GLUE (built only with the option --norec; an experiment): A HERO WITHOUT A CHARACTER RECORD HAS NO
ITEM PLACES. The command menu's count of the hero's item places (0x001BE9A0) reads record + 0x12 of the record
that 0x00177850 gives; a toy cannon (object 0x03C8) as player 2's "hero" has none (0): gn_cnt (the jump at
0x001BE9DC) takes the routine's own way out for a count of 0 then.

FIFTY-FOURTH GLUE (built only with the option --escape2; an experiment): A SECOND HERO IN THE CARPET ESCAPE.
Read in the program: the escape's manager puts THE ENGINE'S PLAYER into the action state 24 (0x002E0CCC) and the
escape's carpet (object 0x05EA, found by number) into state 25 (0x002E0CF0), and sets bit 0 of object + 0x108 on
both. State 24's routine 0x002E1998 works on the hero it is handed: it takes the manager's path matrix and keeps
that hero inside the moving path. State 25's routine 0x002E1D28 (the word at 0x00362E18) puts the carpet at the
engine's player (0x002E1D70). A second escape hero from the room data was left in the normal state with no
carpet (the seventh round's "confused pictures" and fault lines at 0x00177008).
ge_tick (the call at 0x00138538): when both heroes are escape heroes (object 0x05E9) and player 1's hero is in
  state 24, player 2's hero is put into state 24 too, and ONE second escape carpet is made at his place with the
  game's own routine and put into state 25 (0x000E7E60 the carpet, 0x000E7E64 its class word, 0x000E7E68 tries).
ge_upd (the word at 0x00362E18): the second carpet's state routine runs with player 2's hero as "the player".

FIFTY-FIFTH GLUE (built only with the option --sidecar2; an experiment): A SECOND HERO ON THE SIDECAR.
Read in the program: the sidecar's manager puts THE ENGINE'S PLAYER (the hero object 0x0840, Sora on the machine)
into the action state 53 (0x002E2074) and the object 0x0841 into state 54 (0x002E2098), and sets bit 0 of object
+ 0x108 on both. A second sidecar hero from the room data was left in the normal state (the seventh round's fault
lines at 0x00177008: a normal "Attack" on an object without an attack table).
gz_tick (the call at 0x00138538): when both heroes are sidecar heroes and player 1's hero is in state 53, player
  2's hero is put into state 53 too.

FIFTY-SIXTH GLUE (built only with the option --twinmake; an experiment): A SECOND HERO MADE AT RUN TIME in the
three one-hero small games. Read: the build's identity rule (lane E, hook at the player factory 0x00179FD0)
makes "any other player object" the twin, and the game's "make an object" 0x0016F000(object number, place, turn)
goes through that factory.
gw_tick (the call at 0x00138538): when there is no twin, and the engine's player is the escape hero (0x05E9), the
  toy cannon (0x03C8) or the sidecar hero (0x0840), ONE more object of the same number is made 60 units beside
  him (0x000E7E6C the hero it was made for, 0x000E7E70 the object, 0x000E7E74 its class word).

FIFTY-SEVENTH GLUE (built only with the option --hudowner): THE HUD'S OWNER IS PLAYER 1's HERO, OR NOBODY. The
game's attach 0x001D6938 makes a hero the HUD's owner (slot 0 of the party table 0x00348638: the hero the
game's own gauge shows) only if he has an HP record. A second toy cannon (glue 56) attaches itself that way
and, as the twin, has lane D's unit slot: it became the owner; and when it went away the base build's m_dtor
made the first cannon, which has NO HP record, the owner: fault lines in the gauge (0x001575C0, 0x001A2478).
gh_tick (the call at 0x00138538): the owner is the twin while player 1's hero is there: the owner becomes
  player 1's hero if he has an HP record, else the slot is emptied.
gh_set (the call at 0x000F0D8C, was jal 0x0013DDC0): m_dtor makes only a hero with an HP record the owner.

FIFTY-EIGHTH GLUE (built only with the option --ownabil, with --ownrec --ownmenu; an experiment): PLAYER 2
SWITCHES HIS OWN ABILITIES. The ability list (80 shorts at record + 0x54, 0x8000 = on) only grows (the adder
0x00188B68 takes the first empty place), so his switches are one bit per place: five shorts at P2A (King
Mickey's record, item places; a mark 0x5032 behind them). ab_init makes them from the hero's when the mark is
not there; ab_view puts them into the view T; ab_swap changes them with the hero's while player 2's pause menu
is open; ab_add gives him each new ability with the switch the game gives it.

FIFTY-NINTH GLUE (built only with the option --onevictim, with --together): A BOSS THAT HOLDS ONE HERO MAKES
ITS FURTHER CAPTURES ON THAT HERO. A boss's script is written for one hero and keeps "the capture I made" in its
own work memory; with two heroes one step of a sequence could land on the free hero, who was then never let go
(the Groundshaker, lk15: a hero in action FE for 11,250 frames). gk_cap (the jump at 0x00180378, in front of
tg_cap): the victim is a free hero and the other hero is held (action FC .. FF) by this same captor (hero +
0x240 = the captor's word): the capture is made on the held hero. Not in Shan-Yu's room (the fiftieth glue).

SIXTIETH GLUE (built only with the option --holdwatch): NO HERO IS HELD FOR EVER. A boss's script is written for
one hero; with two, a step of a hold can land on the free hero and nobody ends it (the Groundshaker: a hero in
the captured motion FE for 11,250 frames). gy_tick (the call at 0x00138538): a hero who is in ONE AND THE SAME
captured motion (action FC .. FF) for 1,800 steps is let go the game's own way (0x0017EFA0, 0x0016BD60). Who a
boss captures is not touched (the fifty-ninth glue tried that and made the Hydra worse; no build uses it).

SIXTY-FIRST GLUE (built only with the option --itemsync, with --ownrec --norec): PLAYER 2'S ITEM LIST SHOWS THE
ITEM PLACES AS THEY ARE. The item places are common (Sora's record); the game takes a used item out of Sora's
record also when player 2 used it, but his list is built from the view T, a copy that was not made anew: his
list kept items that were gone. gi_sync (the jump at 0x001BE9DC, in front of gn_cnt): when the list builder's
record is the view T, T's + 0x34 .. + 0x53 are copied from the record T shows, first.

SIXTY-SECOND GLUE (built only with the option --ownitems, with --ownrec --ownmenu --ownabil --norec --itemsync):
PLAYER 2'S OWN ITEM PLACES, HIS OWN STOCK OF THE SEVEN FIGHT ITEMS, HIS OWN SHORTCUTS; EVERY THING THE GAME GIVES
IS THERE FOR EACH PLAYER (plan row 39). His things live in King Mickey's record (0x0032E35C + 0x14 places, + 0x1C
refill entries, + 0x24 stock, + 0x2C shortcuts, + 0x44 the mark 0x5033). oi_init makes them from player 1's;
oi_view puts his places into the twin's view T; oi_use takes a used item out of HIS place (0x00176EA4); oi_refill
fills the other player's places from his own stock (0x00253BDC and, each step without a fight, 0x001918A8); oi_swap puts his things where the pause menu
reads them while HIS menu is open; oi_gain / oi_gain2 (0x001A31FC, 0x001A3298): a thing the game gives (not a
move of the menu, not a place given up, not a leaving guest's things) goes to both: a fight item to player 2's
places or stock as well, a Keyblade / armour / accessory twice into the common bag; oi_sc / sc_base: shortcuts.

SIXTY-THIRD GLUE (built only with the option --ownkey, with --ownitems): PLAYER 2'S OWN KEYBLADE (plan row 39).
His Keyblade is a short in King Mickey's record (0x0032E35C + 0x40; + 0x42 player 1's as last seen; + 0x46 the
mark 0x5034). kb_tick makes it and lets it follow a change the STORY makes; kb_swap puts it into the hero's
record while his pause menu is open; kb_tview gives the twin's view his Keyblade (his stats); kb_fact / kb_rec
(0x000F0344, 0x0016F680): while the twin is built his first hand gets HIS Keyblade when its files are there;
kb_req (0x0016ECDC): its files are asked for with the number 2303, in the hero's own block of the file pool;
kb_size (0x001A8B20): that block is 256 KB bigger; kc_menu / kc_load (0x002933D0, 0x0017607C): a Keyblade change
in player 1's menu rebuilds the twin's weapon with HIS Keyblade, a change in player 2's menu changes the twin's
weapon and files only; kb_fix (when a player object is built, kb_after at 0x000F03C0; and each step while no scene
plays): the twin's first hand gets HIS Keyblade as soon as its files are loaded
(a room's second hero can be built before lane E knows that he is the twin); kb_ctor (0x00176204): the twin's own Keyblade's weapon object gets the number 2303 of its
files.

SIXTY-FOURTH GLUE (built only with the option --bindname): AN OBJECT IS BOUND TO ITS FILES BY THEIR NAME WHEN THE
NUMBER DOES NOT FIT (register F8). An object binds to its model and effect file with 0x001A9218 ->
0x001708F8(name, number). Player 2's Drive Form body in a new room has the number of files that nobody asked for
again (29000), so the form's second Keyblade found nothing, its file pointers stayed 0 and its script start read
address 4 (one fault line). bn_find (the calls at 0x001A9238 and 0x001A9288): not found with the number: by name.

SIXTY-FIFTH GLUE (built only with the option --holdpair, with --together): BOTH HEROES INSIDE THE SAME HOLD OF A
BOSS, in every room but Shan-Yu's (plan row 9, the other fights), AND NO GAPS IN "THIS BOSS IS BUSY WITH A HERO"
(the Groundshaker's lost hold). hp_form makes a PAIR when an enemy's script captures a hero or attaches him to
itself (not as the answer to a hero's own command) and the other hero is up, free and within 500 units; hp_cap
(0x00180378) and the wrappers of ten script calls (attach, detach, idle, flags, place, direction, the motion
calls) make every call of the captor's script for one hero of the pair for the other hero too: the second hero
is a mirror of the first, one script drives the hold. hp_tick: the hold note of the glues 36 / 39 / 47 is
written each step while a hero is held or hooked; the pair is forgotten when the hold is over; a mirror left
behind is let go after 40 steps. In glue 47 both heroes of a pair may press the captor's command, once a step.

SIXTY-SEVENTH GLUE (built only with the option --trickguard): LUXORD DOES NOT FLINCH WHILE A HERO STANDS IN HIS
TRICK. A hero who loses Luxord's card or command trick is captured (move 254) and Luxord's act "rc_card_failure" /
"rc_card2_failure" must run to its end: only it turns the hero into the card or the die and so ends his captured
motion. The script's damage routine starts the damage act on every hit that "is a reaction" (script call (2,8),
0x0018F4C0), which replaces that act: with two heroes the other hero's hit left the first one held (up to the
one-minute rule). lt_dmg (table word 0x0034EF70): for Luxord (object 0x05F8) and Data Luxord (0x09C8), while a
hero stands in a captured motion of his, the call answers "no reaction".

SIXTY-EIGHTH GLUE (built only with the option --holdpads, with --holdpair): WHILE A BOSS HOLDS BOTH HEROES, BOTH
CONTROLLERS COUNT. In a hold's pair the boss's script reads one hero's controller (in the last Xemnas's hold the
player whose hero he named plays Riku; the other player was held with nothing to press). pm_pad (head of the
calls at 0x00167E90): while both heroes of the sixty-fifth glue's pair are held, the two logical controller
records are made one after the game's update (buttons of either, without START; a moving stick (record + 0x30) at
rest takes the other's; the camera sticks (+ 0x20) stay apart); each record gets its own held word back before
the next update.

SIXTY-NINTH GLUE (built only with the option --ownwallet, with --ownkey): PLAYER 2'S OWN WALLET. His munny is a word in
King Mickey's record (0x0032E35C + 0x48, the mark 0x5035 at + 0x4C). Munny the game gives (0x00242500: rewards, orbs) goes
to both wallets; a shop's sale is the seller's alone. A shop or the Moogle (the game mode at 0x0033CB80, start 0x00105C68)
is player 2's when the twin ran the last green command (0x00178AE8): then his menu things go in as for his pause menu
(glue 49's flag and ow_swap chain; the wallets change places at its end), so he pays from his own wallet.

SEVENTIETH GLUE (built only with the option --shoppad): PLAYER 2'S BUTTONS IN THE SHOP'S QUANTITY BOX. The shop module reads
"Buy how many?" from logical controller 0 only (its call at 0x01F1AA90), so player 2 could not finish a purchase. sp_inst
(head of the controller task's calls at 0x00167E90) points that call at the second glue's pad_both (both controllers)
whenever the shop module is in memory.

SEVENTY-FIRST GLUE (built only with the option --ownbag, with --ownwallet): PLAYER 2'S OWN BAG. His counts of the Keyblades,
armours, accessories and materials (158 things) live in King Mickey's ability places 16 .. 79 (0x4000 | 14 bits each: a
material's count in the low byte, two gear counts of 3 bits in the high byte; the mark 0x5036 at + 0x4E). ob_swap
(after ww_swap) puts them into the game's bag while his menu or his shop is open (player 1's wait in 0x000E7C40);
ob_gain gives a thing the game gives into both bags; ob_tick makes his bag = player 1's when there is no mark.

THE SIXTY-FIFTH GLUE'S FIFTH FORM (option --holdshared, with --holdpair): ONLY A SHARED MECHANIC TAKES BOTH HEROES. A pair is
made only for the last Xemnas's laser dome (captor 0x081F or 0x09CA, move 0x106: the game itself captures the player and
Riku with it). Every other boss capture takes the hero the script names, as the game; the stray capture of a free
bystander is still not made, and the nets stay.
Its second part: while that pair lives, a command the game offers to one hero of the pair (the script call 165, "command
override": the dome's "Reflect") is offered to the other hero's own menu too (co_two, in the sixty-eighth glue's room), so
each player's own press counts (once a step, the forty-seventh glue's hp_rc).
Its third part: the dome is never "a hero's own move": for that capture alone the own-move notes do not stop the pair
(hs_hf, the first routine of co_two's room; run xsK: the dome came 60 steps after player 1's own green command).
Its fifth part: ONLY AN ENEMY'S GRAB is single-target (the captor's kind, object entry + 4: BOSS 3, ZAKO 4, E_WEAPON 6,
L_BOSS 12, L_ZAKO 21, E_OBJ 23); any other captor (a board, a gimmick) pairs as in build 20, and co_two / hs_rc act only in
the dome (the regression of v128: Mail Delivery and the skate challenges ended with 49 fault lines without build 20's pair).
Its fourth part: the dome's pieces run on ONE hero, PLAYER 1'S, the one its lasers aim at, as in the game (runs xsN / xsQ:
with both heroes carrying a piece of the dome's script the end ran twice; xsS: a second end four steps late faulted at
0x001E2AC0; xsY: pieces on the named player 2 while the lasers hit player 1 failed the dome): hs_rc sends a press of
player 2's hero in player 1's hero's name (the mirror still gives both heroes the reflect; the count goes up once a
press). The script call "is the player" stays the game's (a first safety net there let the named player 2 go: run xs3).

SEVENTY-SECOND GLUE (built only with the option --drivesave): PLAYER 2'S OWN DRIVE GAUGE IN THE SAVE. dv_tick (head of
the controller task's calls at 0x00167E90) copies the twin's gauge and bars into King Mickey's record + 0x52 / + 0x53 with
the mark 0x5037 at + 0x50 (free bytes, STATE part 89), so a save holds them; dv_load (end of the twenty-second glue's
snap_none: a Load Game) and dv_ext (in the drive glue's dl_ext) give them back to the twin's own copy. Without the mark
(New Game, an older save) both heroes take the save's values as before.

SEVENTY-THIRD GLUE (built only with the option --itemtarget): A TARGET CHOICE FOR POTIONS, ETHERS AND ELIXIRS. The item target
window "PARTY" gets one more row for the second hero (ih_rows at 0x001BE3A4): on both screens the first "Sora" is player 1's
hero and the last "Sora" player 2's. ih_row (0x001BE2BC) gives the chosen hero as the target and notes the choice for the menu's
owner; ih_find (0x001BA53C) draws the effect on him; ih_pick (0x001BA624, in front of lane N's n_heal) gives the item to the
chosen hero. Shortcuts, helpers and party-wide items keep lane N's rule.

SEVENTY-FOURTH GLUE (built only with the option --boxpick): PLAYER 2'S HERO PICKS UP A DROPPED ITEM BOX TOO. The item box's
step routine 0x001BF4E8 asked only player 1's hero; bx_twin (at 0x001BF570) gives player 2's hero the same touch test when player
1's did not touch it, and lets him take the box with the game's own take 0x001BF378.

SEVENTY-FIFTH GLUE (built only with the option --formroom): IN A NEW ROOM PLAYER 2'S DRIVE FORM FILES ARE ASKED FOR AGAIN, AS
PLAYER 1'S. The room's request for the player placeholder (0x0016ED50) ends in fr_room (jump at 0x0016EEE4; the "no form" return
at 0x0016EED0 is a nop): player 1's form as before, then player 2's form with his own number base (forty-first glue), so his
files are not left as files "that may be thrown out".

SEVENTY-SIXTH GLUE (built only with the option --setposguard): trap_effect_set_pos (handler 0x0016E180) WRITES NOTHING FOR AN
ENDED EFFECT (its body pointer h + 0x1C is 0). Four words in place at 0x0016E19C .. 0x0016E1AC. Seen: the Fortuneteller's crystal
effect after "Clear Shot" (26 stores to address 0).

SEVENTY-SEVENTH GLUE (built only with the option --gummiall, needs --ship2score): THE GUMMI POINTS OF EVERY PLAYER WEAPON GO TO
THE SHIP THAT FIRED. gx_inst gives a fresh flight module five more jumps: around a weapon's fire (0x01F49B38, 0x01F4A6E8) the firing
ship is noted (its block's parent = ship + 0x3E0), each shot that starts up (0x01F3E1A0, 0x01F3FA20) takes that note into the
sixty-sixth glue's shots' table, and the hits of nine shot kinds (gx_hit, in front of gq_hit) and the "10 points" hit (0x01F26D00)
are credited by it.

SEVENTY-EIGHTH GLUE (built only with the option --gummitag, needs --ship2score, never with --gummiall): THE GUMMI POINTS OF
WEAPONS OTHER THAN CANNONS GO TO THE SHIP THAT FIRED (design "gt"). gt_inst gives a fresh flight module four jumps: a generic or a
special weapon's fire (0x01F49B38, 0x01F4A6E8) writes the firing ship as a tag 0xA501 / 0xA502 into the weapon's hit values + 30
(weapon + 110, padding), which every shot and so every hit record copies; the "10 points" (0x01F26D00) and "100 / 1000 points"
(0x01F27A40) hits take the tag for the credit. gq_hit's first word jumps to gt_hit: the cannon shots' call keeps glue 66's table
(as build 23), every other call takes the tag (none: player 1's, as before). Room 0x000EF000 .. 0x000EF400 (glue 77's).

  python -I tools/merge/merge_v7.py [outDir] [--no-eitherspawn] [--no-revenge] [--no-getup] [--no-keychange] [--no-twoforms] [--no-formfiles] [--no-nearcb] [--no-mickey | --mickey1] [--no-reactheld] [--no-thinkheld] [--no-helperform] [--no-formbase] [--no-helperback] [--no-heroscript] [--no-captureform] [--no-scriptplayer] [--playernear] [--no-sender] [--ownrec [--ownmenu]] [--together [--together-far]] [--ship2hit [--ship2first]] [--carpet2] [--norec] [--escape2] [--sidecar2] [--twinmake] [--hudowner] [--ownabil] [--onevictim] [--holdwatch] [--itemsync] [--ownitems] [--ownkey] [--bindname] [--holdpair] [--gummitag]
Writes <outDir>/SLPM-66675_F266B00B.pnach and <outDir>/listing.txt. Default outDir: patches/merged-v7.
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
BASE = ROOT / "patches" / "merged-v6"
BASE_SHA1 = "00e5112fd1f8ac2a8bb1ae2d3110141e4ea5d848"
if "--base-nn" in sys.argv:                         # the regression's one-hero control: build 12 without the twenty-eighth glue
    BASE = ROOT / "patches" / "test-v7-l-nn"
    BASE_SHA1 = "9575f0defb6026d6b909f42755845968d6311142"
LINE = re.compile(r"^patch=(\d),EE,([0-9A-Fa-f]{8}),(\w+),([0-9A-Fa-f]{8})\s*(?://.*)?$")

CAVE_LO, CAVE_HI = 0x000E8000, 0x000F0000          # this round's routines
V_TWIN = 0x000F05CC                                # lane E: the twin's object (0 = none)
V_PASS2 = 0x000F05D0                               # lane R: 1 during the second offer of a volume
V_P1 = 0x000F05D4                                  # lane R: player 1's hero DURING THE SECOND OFFER ONLY (not a general name for him)
POS_OF = 0x0016C028                                # game: pointer to an object's position

# ---- thirtieth glue ----------------------------------------------------------------------------------------
ESPAWN_AT = 0x000E8000
ESPAWN_END = 0x000E8080
RI_OUT = 0x000F3134                                # lane R's r_inside: its exit (ld ra / jr ra / addiu sp)
ESPAWN_SRC = """
sp_either:                        # from r_inside (0x000F3014): player 1's hero is not inside the volume (v0 = 0).
    lui t7,0x000F                 # s0 = the volume, s1 = the area event, 8(sp) = the volume's "is this point inside"
    lw t4,0x05D0(t7)
    bne t4,zero,sp_out            # only on the game's own offer (never on the twin's second offer)
    lw t3,8(s1)
    lbu t6,0(t3)                  # kind of area event
    addiu t5,t6,-2
    bne t5,zero,sp_out            # only kind 2 = make the zone's objects appear when a hero walks in
    lw a0,0x05CC(t7)              # the twin
    beq a0,zero,sp_out
    nop
    jal POS_OF
    nop
    move a1,v0
    ld t9,8(sp)
    jalr t9                       # is the twin inside the zone?
    move a0,s0
    j RI_OUT
    nop
sp_out:
    j RI_OUT
    move v0,zero
"""
ESPAWN_BASE_WORD = (0x000F3014, 0x10400047)        # lane R: beq v0,zero,ri_out (the nop after it stays)

# ---- thirty-first glue -------------------------------------------------------------------------------------
REVENGE_FACTOR_BITS = 0x3F40                       # the upper half of the float 0.75
RV_AT = 0x000E8080
RV_END = 0x000E8100
RV_SRC = """
rv_scale:                         # from 0x00185CE0 (jal; "cvt.s.w f1,f1" ran in the delay slot).
    lui t5,0x000F                 # f1 = this hit's revenge value, f0 = the target's counter, a1 = the hit record
    lw t6,0x05CC(t5)              # the twin
    beq t6,zero,rv_add            # one hero: as the game does it
    lw t7,0x10(a1)                # the attacker of this hit
    srl t6,t7,20
    beq t6,zero,rv_add            # not an object in the game's memory
    sltiu t6,t6,0x20
    beq t6,zero,rv_add
    nop
    lw t6,0x588(t7)
    andi t6,t6,0x80               # a player object = either hero (the game's own test, as at 0x00189E5C)
    beq t6,zero,rv_add            # a helper or anybody else: as the game does it
    nop
rv_do:
    lui t5,REVENGE_BITS
    mtc1 t5,f2
    mul.s f1,f1,f2
rv_add:
    jr ra
    add.s f0,f0,f1                # the instruction that sat at 0x00185CE4
"""
RV_HOOK = (0x00185CE0, 0x46800860, 0x46010000)     # cvt.s.w f1,f1 / add.s f0,f0,f1


# ---- thirty-second glue ------------------------------------------------------------------------------------
GU_AT = 0x000E8100
GU_END = 0x000E8180
GU_SRC = """
gu_fix:                           # from lane N's n_tick (0x000F2974): a0 = the hero whose timer ran out
    addiu sp,sp,-16
    sd ra,0(sp)
    sd a0,8(sp)
    jal 0x0017DE70                # the helper's own timed recovery (comes back through lane N's n_hp)
    nop
    ld a0,8(sp)
    lw t6,0x48C(a0)               # his unit slot
    beq t6,zero,gu_out
    nop
    lw t7,4(t6)                   # most HP
    sra t5,t7,2
    addiu t5,t5,1                 # the game's low-HP line is HP <= most HP >> 2: one step above it
    lw t4,0(t6)
    blez t4,gu_out                # still down (the recovery did not happen): leave it
    nop
    slt t3,t4,t5
    beq t3,zero,gu_out            # already above the line
    nop
    slt t3,t7,t5                  # never above his most HP
    movn t5,t7,t3
    sw t5,0(t6)
gu_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""
GU_BASE_WORD = (0x000F2974, 0x0C05F79C)            # lane N: jal 0x0017DE70


# ---- thirty-third glue -------------------------------------------------------------------------------------
WC_AT = 0x000E8180
WC_END = 0x000E8300
WC_SRC = """
wc_both:                          # from the menu (0x002933D0, was "j 0x00175F68"): a0 = the menu's record, a1 = the
    addiu sp,sp,-64               # character number, a2 = the hand (0 / 1), a3 = the new weapon item
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    sd s3,32(sp)
    sd s4,40(sp)
    move s1,a2
    move s2,a3
    move s3,a0
    move s4,a1
    sd zero,56(sp)
    lui t7,0x000F
    lw s0,0x05CC(t7)              # the twin
    beq s0,zero,wc_game           # none: the game's routine alone
    nop
    jal 0x0016A070                # the twin's character number
    move a0,s0
    bne v0,s4,wc_notwin           # another character's weapon: the twin keeps his
    nop
    sll t6,s1,2
    addu t6,t6,s0
    lw a0,0xAF8(t6)               # the twin's weapon of that hand
    beq a0,zero,wc_notwin
    nop
    sd a0,48(sp)
    jal 0x0019C5D0                # end it as the game ends the hero's, BEFORE the files go
    nop
    sd v0,56(sp)                  # (the game keeps this answer: 0 = the new weapon gets its method + 0x48 called)
    jal 0x00185A28
    ld a0,48(sp)
    sll t6,s1,2
    addu t6,t6,s0
    b wc_game
    sw zero,0xAF8(t6)
wc_notwin:
    move s0,zero
wc_game:
    move a0,s3
    move a1,s4
    move a2,s1
    jal 0x00175F68                # the game's routine (player 1's hero, or the other character)
    move a3,s2
    beq s0,zero,wc_out
    nop
    lw t6,8(s0)                   # the twin's object entry
    lhu a0,78(t6)                 # his body's weapon set
    addiu t7,zero,53
    beq a0,t7,wc_look
    nop
    lw t7,0x588(s0)
    lui t6,0x0100
    and t7,t7,t6
    beq t7,zero,wc_look
    nop
    bne s1,zero,wc_look
    nop
    jal 0x001D1438                # (the game's own detour for hand 0 of a hero: the base body's weapon set)
    move a0,zero
    jal 0x0016E920
    move a0,v0
    lhu a0,78(v0)
wc_look:
    jal 0x00185890                # the weapon object for this body and this item
    move a1,s2
    beq v0,zero,wc_out
    move a1,v0
    move a0,s0
    jal 0x00176168                # build it in that hand
    move a2,s1
    ld t7,56(sp)
    bne t7,zero,wc_out
    sll t6,s1,2
    addu t6,t6,s0
    lw a0,0xAF8(t6)
    beq a0,zero,wc_out
    nop
    lw t6,0(a0)
    lw t7,72(t6)
    jalr t7                       # (the game's last step for the new weapon)
    nop
wc_out:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    ld s3,32(sp)
    ld s4,40(sp)
    jr ra
    addiu sp,sp,64
"""
WC_HOOK = (0x002933D0, 0x0805D7DA)                 # the menu: j 0x00175F68 (its "addiu sp,sp,16" stays behind it)


# ---- thirty-fourth glue ------------------------------------------------------------------------------------
FM_AT = 0x000E8300
FM_END = 0x000E8600
FORM_NEED = {1: 2217984, 2: 2336768, 3: 3121152, 4: 2377728, 5: 2652160}   # Valor, Wisdom, Limit Form, Master, Final: runs fp1, fp3, fp4, fp5
FM_SRC = """
fm_ask_list:                      # from 0x001BEB68 (was jal 0x001C8DB8): s0 = the control object whose list is built
    move t8,zero                  # (no row: no question about room)
    b fm_ask
    lw t9,0x9E0(s0)               # its hero
fm_ask_judge:                     # from 0x001BC594 (was jal 0x001C8DB8): s0 = the hero whose row is judged,
    move t8,s1                    # s1 = the row's command
    move t9,s0
fm_ask:                           # a0 = the lock word, t9 = the asking hero -> v0 = 1 when Drive is shut for him
    lw t7,0(a0)
    addiu t6,zero,-2
    and t6,t7,t6
    bne t6,zero,fa_yes            # another reason than bit 0: as the game
    nop
    beq t9,zero,fa_bit0           # no hero known: the game's own answer
    nop
    lw t6,0xB50(t9)
    addiu t6,t6,-1
    sltiu t6,t6,6
    bne t6,zero,fa_yes            # he is in a form himself
    nop
    andi t6,t7,1
    beq t6,zero,fa_no             # nothing holds the lock
    nop
    lui t5,0x000F
    lw t4,0x05CC(t5)              # the twin
    beq t4,zero,fa_yes            # one hero: as the game
    nop
    lw t6,0xB50(t4)
    addiu t6,t6,-1
    sltiu t6,t6,6
    bne t6,zero,fa_mem            # the twin is in a form (the asker is not): bit 0 means forms -> free for him,
    nop                           # if there is room for a second form's files
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero (the game's "hero built last", kept right by the build)
    beq t4,zero,fa_yes
    nop
    lw t6,0xB50(t4)
    addiu t6,t6,-1
    sltiu t6,t6,6
    bne t6,zero,fa_mem            # player 1's hero is in a form (the asker is not)
    nop
fa_yes:                           # (bit 0 with no hero in a form: a Limit or a Summon holds it)
    jr ra
    addiu v0,zero,1
fa_no:
    jr ra
    move v0,zero
fa_bit0:
    jr ra
    sltu v0,zero,t7
fa_mem:                           # @FORMBASE@ a SECOND form: only when the object file pool has room for its files
    beq t8,zero,fa_no             # the list as a whole: yes
    nop
    lhu t6,2(t8)
    addiu t6,t6,-4
    bne t6,zero,fa_no             # not a form row
    nop
    lh t6,4(t8)                   # the form number
    sltiu t5,t6,7
    beq t5,zero,fa_no
    lui t5,0x0033
    lbu t5,-4012(t5)              # the same form as the other hero's: its files are there already
    beq t5,t6,fa_no
    lui t5,0x000F
    lbu t5,0x47E8(t5)
    beq t5,t6,fa_no
    sll t6,t6,2
    lui t5,%hi(fa_need)
    addiu t5,t5,%lo(fa_need)
    addu t5,t5,t6
    lw t3,0(t5)                   # what this form needs
    lui t5,0x0035
    lw t4,-9056(t5)               # the file list (0x0034DCA0)
    lw t2,-9040(t5)               # the pool's limit (0x0034DCB0)
    move t1,zero                  # the end of the last file that must stay
fa_walk:
    beq t4,zero,fa_sum
    nop
    lw t6,40(t4)                  # its keep-number
    slti t5,t6,10000
    beq t5,zero,fa_next           # it may be thrown out: not counted
    lw t6,48(t4)                  # its place
    lw t5,44(t4)                  # its size
    addu t6,t6,t5
    sltu t5,t1,t6
    movn t1,t6,t5
fa_next:
    b fa_walk
    lw t4,60(t4)
fa_sum:
    subu t2,t2,t1                 # room
    sltu t5,t2,t3
    jr ra
    move v0,t5                    # 1 = no room: the row is dim
fa_need:                          # bytes of the pool a form's files need (measured + 0x10000), forms 0 to 6
    .word 0x7FFFFFFF
    .word @NEED1@
    .word @NEED2@
    .word @NEED3@
    .word @NEED4@
    .word @NEED5@
    .word 0x7FFFFFFF

fm_lower:                         # from 0x001D0D40 (the destructor of a form body; was "ld s0,0(sp)", then ld ra and
    lui t5,0x000F                 # "j 0x001C8D98"): s0 = the body that ends, a0 = the lock word, a1 = 0, ra put back
    lw t4,0x05CC(t5)              # the twin
    beq t4,zero,fl_low            # one hero: lower it as the game does
    nop
    beq t4,s0,fl_p1               # the body that ends is the twin's: look at player 1's hero only
    nop
    lw t6,0xB50(t4)
    addiu t6,t6,-1
    sltiu t6,t6,6
    bne t6,zero,fl_keep           # the twin is still in a form
    nop
fl_p1:
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,fl_low
    nop
    beq t4,s0,fl_low
    nop
    lw t6,0xB50(t4)
    addiu t6,t6,-1
    sltiu t6,t6,6
    beq t6,zero,fl_low
    nop
fl_keep:
    ld s0,0(sp)
    jr ra
    addiu sp,sp,16
fl_low:
    ld s0,0(sp)
    j 0x001C8D98
    addiu sp,sp,16
"""
FM_HOOKS = (
    (0x001BEB68, 0x0C07236E, "jal", "fm_ask_list", "the Drive list of a control object: is Drive shut for THIS hero"),
    (0x001BC594, 0x0C07236E, "jal", "fm_ask_judge", "a form row: is Drive shut for THIS hero"),
    (0x001D0D40, 0xDFB00000, "j", "fm_lower", "a form body ends: the lock stays while the other hero is in a form"),
    (0x001D0D48, 0x08072366, "nop", None, "(the jump that sat here is inside fm_lower; ld ra,8(sp) runs in fm_lower's delay slot)"),
)


# ---- thirty-fifth glue -------------------------------------------------------------------------------------
FK_AT = 0x000E89E0
FK_END = 0x000E8A80
FK_SRC = """
fk_form:                          # from 0x001B66F8 (was jal 0x00170320; a0 = 5000 from the delay slot). s2 = the form
    lui t5,0x000F                 # record: its first word is the body that changes
    lw t4,0x05CC(t5)              # the twin
    beq t4,zero,fk_do             # one hero: as the game
    nop
    lw t6,0(s2)
    bne t6,t4,fk_twin             # player 1's hero changes: is the twin in a form?
    nop
    lui t7,0x0033
    b fk_ask
    lbu t6,-4012(t7)              # the twin changes: player 1's form (the save's byte 0x0032F054)
fk_twin:
    lbu t6,0x47E8(t5)             # the twin's own form (ninth glue)
fk_ask:
    addiu t6,t6,-1
    sltiu t6,t6,6
    beq t6,zero,fk_do             # the other hero is in no form: the game's call
    nop
    jr ra                         # he is: his files stay as they are
    nop
fk_mickey:                        # from 0x001D0080 (King Mickey's files are asked for)
    lui t5,0x000F
    lw t4,0x05CC(t5)
    beq t4,zero,fk_do
    nop
    lbu t6,0x47E8(t5)             # the twin's form
    addiu t6,t6,-1
    sltiu t6,t6,6
    bne t6,zero,fk_skip
    lui t7,0x0033
    lbu t6,-4012(t7)              # player 1's form
    addiu t6,t6,-1
    sltiu t6,t6,6
    beq t6,zero,fk_do
    nop
fk_skip:
    jr ra
    nop
fk_do:
    j 0x00170320                  # the game's call: the files kept for forms may now be thrown out
    nop
"""
FK_HOOKS = (
    (0x001B66F8, 0x0C05C0C8, "fk_form", "the form task lets the form files go: not while the other hero is in a form"),
    (0x001D0080, 0x0C05C0C8, "fk_mickey", "King Mickey's files are asked for: the form files stay while a hero is in a form"),
)


# ---- thirty-sixth glue -------------------------------------------------------------------------------------
NC_AT = 0x000E8E60
NC_END = 0x000E9040
NC_SRC = """
nc_trig:                          # jump at 0x0016CCE8 (its second word is now a nop). a0 = the script, its object at +56
    lw t8,56(a0)                  # the object
    srl t7,t8,22
    addiu t7,t7,-6
    bne t7,zero,nc_body           # not an object (0x0180xxxx-0x01BFxxxx): as it is
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,nc_body
    lui t5,0x0035
    lw t9,1156(t8)
    bne t9,a0,nc_body             # not this object's own script: as it is
    nop
    lw t4,-5816(t5)               # the engine's player = player 1's hero
    beq t4,zero,nc_body
    nop
    beq t8,t4,nc_body             # player 1's hero's own script: as it is
    nop
    beq t8,t6,nc_twin             # THE TWIN'S OWN SCRIPT: he is "the player" of his own callbacks (run of270: the
    lw t3,0(t8)                   # clash motion on HIS body offered "Press" to player 1's control object, trap 0x00174328)
    lui t2,0x0034
    ori t2,t2,0x5C08
    beq t3,t2,nc_body             # a helper: unchanged
    nop
    lw t9,0x140(t8)               # HELDFIX: the first word of this object's motion part (what a held hero's + 0x240 holds)
    beq t9,zero,nc_up
    nop
    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
    bne t3,t9,nc_p1
    lw t3,0x160(t6)
    andi t3,t3,0x4000
    bne t3,zero,nc_mtwin
    nop
nc_p1:
    lw t3,0x240(t4)               # is player 1's hero?
    bne t3,t9,nc_mem
    lw t3,0x160(t4)
    andi t3,t3,0x4000
    bne t3,zero,nc_mp1
    nop
nc_mem:                           # nobody is held at this moment: did THIS object hold a hero a moment ago?
    lui t7,0x000E
    lw t3,0x7C0C(t7)
    bne t3,t9,nc_up
    lw t2,-11076(t5)              # the game's counter 0x0034D4BC
    lw t3,0x7C14(t7)
    subu t2,t2,t3
    sltiu t2,t2,90
    beq t2,zero,nc_up
    lw t3,0x7C10(t7)
    addiu t3,t3,-1
    beq t3,zero,nc_twin           # the twin, less than 90 steps ago
    nop
    b nc_body                     # player 1's hero
    nop
nc_mtwin:                         # the twin is held now: note it
    lui t7,0x000E
    sw t9,0x7C0C(t7)
    addiu t3,zero,1
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    b nc_twin
    sw t3,0x7C14(t7)
nc_mp1:                           # player 1's hero is held now: note it
    lui t7,0x000E
    sw t9,0x7C0C(t7)
    addiu t3,zero,2
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    b nc_body
    sw t3,0x7C14(t7)
nc_up:
    lw t3,0x48C(t6)               # the twin's unit slot
    beq t3,zero,nc_body
    nop
    lw t3,0(t3)
    beq t3,zero,nc_body           # the twin is down: player 1's hero
    nop
    lw t2,0x48C(t4)
    beq t2,zero,nc_dist
    nop
    lw t2,0(t2)
    beq t2,zero,nc_twin           # player 1's hero is down: the twin
    nop
nc_dist:
    lwc1 f0,0x70(t8)
    lwc1 f1,0x78(t8)
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
    bc1f nc_body                  # player 1's hero is nearer (or as near): as it is
    nop
nc_twin:
    addiu sp,sp,-32
    sd ra,0(sp)
    sd t4,8(sp)
    jal nc_body                   # this callback runs with the twin as "the player"
    sw t6,-5816(t5)
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
nc_body:
    addiu sp,sp,-48               # the two instructions that sat at 0x0016CCE8
    j 0x0016CCF0
    sd s0,0(sp)
"""
NC_HOOK = (0x0016CCE8, 0x27BDFFD0, 0xFFB00000)     # addiu sp,sp,-48 / sd s0,0(sp)


# ---- thirty-seventh glue -----------------------------------------------------------------------------------
MK_AT = 0x000E8600
MK_END = 0x000E8880
V_PARK2 = 0x000E7C00                               # the twin's fallen hero while a second Mickey plays (0 = none)
MK_SRC = """
mk_both:                          # from 0x001AF628 (was jal 0x001D00A8): the Game Over sequence builds King Mickey
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    lui t7,0x000E
    jal 0x001D00A8                # the game's call: Mickey for the engine's player
    sw zero,0x7C00(t7)            # (no twin is parked yet)
@TWO@
mb_out:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    jr ra
    addiu sp,sp,48
mk_end253:                        # from 0x00172EBC (was j 0x001D0228). a0 = the Mickey that ends
    lui t9,0x001D
    b mk_end
    ori t9,t9,0x0228
mk_end254:                        # from 0x001BA5C8 (was jal 0x001D02C8)
    lui t9,0x001D
    ori t9,t9,0x02C8
mk_end:
    addiu sp,sp,-64
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    sd s3,32(sp)
    move s3,t9                    # the game's end routine
    move s0,a0
    lui t7,0x000E
    lw s1,0x7C00(t7)              # the parked twin (0 = there is no second Mickey)
    sw zero,0x7C00(t7)
    beq s1,zero,me_one
    lui t6,0x000F
    lw s2,0x05CC(t6)              # the second Mickey
    beq s2,zero,me_one
    lui t5,0x0035
    lw t4,0(s2)
    ori t3,t5,0x2360              # King Mickey's class table 0x00352360
    bne t4,t3,me_one              # "the twin" is no Mickey (a Continue or a new room came between): one Mickey
    nop
    lw a0,-5816(t5)               # player 1's Mickey = the engine's player
    jalr s3                       # the game's routine: he ends, player 1's hero is back
    nop
    lui t5,0x0035
    lw t4,-5816(t5)               # player 1's hero
    sd t4,40(sp)
    sw s2,-5816(t5)               # "the player" = the second Mickey
    sw s1,-5812(t5)               # the parked hero = the twin
    jalr s3                       # the same routine: he ends, the twin is back
    move a0,s2
    lui t6,0x000F
    sw s1,0x05CC(t6)              # the twin is the twin again
    ld a0,40(sp)
    lui t5,0x0035
    sw a0,-5816(t5)               # the engine's player = player 1's hero
    sw zero,-5812(t5)
    sw a0,0x2400(t5)              # 0x00352400: the last-built object of the main player class
    jal 0x001781A8                # the game's attach for player 1's hero (camera target, HUD owner, control object)
    nop
    b me_fill
    nop
me_one:
    lui t5,0x0035
    lw t4,-5812(t5)               # the game's parking place
    beq t4,zero,me_fill           # nobody is parked: this rescue was ended already (the other Mickey's own call)
    nop
    jalr s3                       # one Mickey: the game's routine as it is
    move a0,s0
me_fill:                          # a twin who is still down gets up; his HP is filled as the hero's is
    lui t6,0x000F
    lw s1,0x05CC(t6)
    beq s1,zero,me_out
    nop
    lw t3,0x48C(s1)               # his unit slot
    beq t3,zero,me_out
    nop
    lw t5,0x7F8(s1)
    andi t5,t5,4
    beq t5,zero,me_hp             # he is up
    nop
    li t4,1
    sw t4,0x2FCC(t6)              # lane N's word "the twin is down by my rule": a heal brings him back
    lw a1,4(t3)                   # most HP
    move a0,s1
    move a2,zero
    move a3,zero
    lw t7,0(s1)
    lw t7,0x78(t7)
    jalr t7                       # his class's HP change (lane N's n_hp)
    nop
me_hp:
    lw t3,0x48C(s1)
    beq t3,zero,me_out
    nop
    lw t4,4(t3)
    sw t4,0(t3)                   # full HP
me_out:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    ld s3,32(sp)
    jr ra
    addiu sp,sp,64
"""
MK_TWO = """
    lui t7,0x000F
    lw s0,0x05CC(t7)              # the twin
    beq s0,zero,mb_out
    nop
    lw t6,0x7F8(s0)
    andi t6,t6,4
    beq t6,zero,mb_out            # he is not down: nothing more
    lui t5,0x0035
    lw s1,-5816(t5)               # player 1's Mickey (the engine's player now)
    lw s2,-5812(t5)               # player 1's parked hero
    beq s1,zero,mb_out
    nop
    beq s2,zero,mb_out            # no Mickey was built
    nop
    sw s0,-5816(t5)               # "the player" = the twin
    sw zero,-5812(t5)
    jal 0x001D00A8                # the same routine: the twin is parked, a Mickey with his controller holds him
    nop
    lui t5,0x0035
    lw t4,-5816(t5)               # the second Mickey
    lw t3,-5812(t5)               # the parked twin
    lui t7,0x000E
    sw t3,0x7C00(t7)
    lui t7,0x000F
    sw t4,0x05CC(t7)              # the second Mickey is "the twin" for the length of the rescue
    sw s1,-5816(t5)               # the engine's player = player 1's Mickey
    sw s2,-5812(t5)               # the parking place = player 1's hero
    lui t7,0x0033                 # mb_count: the second Mickey counted the rescue once more (save + 0x3DB0 / + 0x3DB2)
    lhu t6,-1824(t7)              # 0x0032F8E0
    beq t6,zero,mb_c2
    addiu t6,t6,-1
    sh t6,-1824(t7)
mb_c2:
    lhu t6,-1822(t7)              # 0x0032F8E2
    beq t6,zero,mb_att
    addiu t6,t6,-1
    sh t6,-1822(t7)
mb_att:
    jal 0x001781A8                # the game's attach for player 1's Mickey
    move a0,s1
"""
MK_HOOKS = (
    (0x001AF628, 0x0C07402A, "jal", "mk_both", "the Game Over sequence builds King Mickey: one for each fallen hero"),
    (0x00172EBC, 0x0807408A, "j", "mk_end253", "the rescue ends (paired move 253): both Mickeys end, both heroes are back"),
    (0x001BA5C8, 0x0C0740B2, "jal", "mk_end254", "the rescue ends (Healing Light): both Mickeys end, both heroes are back"),
)


# ---- thirty-eighth glue ------------------------------------------------------------------------------------
RH_AT = 0x000E8880
RH_END = 0x000E88E0
RH_SRC = """
ro2:                              # hook 0x00189E3C (was the fifteenth glue's jal react_own). s1 = the object whose
    lui t7,0x0035                 # motion offers the command. Out: s0 = "the player" of this offer
    lw s0,-5816(t7)               # the engine's player (the instruction that sat at 0x00189E40)
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    beq t6,zero,r2_out
    nop
    beq s1,t6,r2_twin             # the twin's own motion offers it (fifteenth glue)
    nop
    lw t4,0x140(s1)               # the first word of the source's motion part
    beq t4,zero,r2_out
    nop
    lw t5,0x240(t6)               # is the twin held in a paired move by this object?
    bne t5,t4,r2_out
    lw t5,0x160(t6)
    andi t5,t5,0x4000
    beq t5,zero,r2_out
    nop
r2_twin:
    move s0,t6
r2_out:
    jr ra
    nop
"""
RH_BASE_WORD = (0x00189E3C, 0x0C03D6E0)            # the base patch: jal react_own (0x000F5B80)


# ---- thirty-ninth glue -------------------------------------------------------------------------------------
NT_AT = 0x000E9040
NT_END = 0x000E9180
NT_SRC = """
nt_held:                          # jump at 0x0016A950 (was the twelfth glue's j near_think). a0 = the object that thinks
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,nt_old
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player = player 1's hero
    beq t4,zero,nt_old
    nop
    beq a0,t4,nt_old              # the heroes and the helpers: the old rule
    nop
    beq a0,t6,nt_old
    lw t3,0(a0)
    lui t2,0x0034
    ori t2,t2,0x5C08
    beq t3,t2,nt_old
    nop
    lw t9,0x140(a0)               # the first word of this object's motion part
    beq t9,zero,nt_old
    nop
    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
    bne t3,t9,nt_p1
    lw t3,0x160(t6)
    andi t3,t3,0x4000
    beq t3,zero,nt_p1
    lui t7,0x000E
    sw t9,0x7C0C(t7)              # note the hold
    addiu t3,zero,1
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    sw t3,0x7C14(t7)
nt_tw:
    addiu sp,sp,-32
    sd ra,0(sp)
    sd t4,8(sp)
    jal nt_body                   # it thinks with the twin as "the player"
    sw t6,-5816(t5)
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
nt_p1:
    lw t3,0x240(t4)               # is player 1's hero?
    bne t3,t9,nt_mem
    lw t3,0x160(t4)
    andi t3,t3,0x4000
    beq t3,zero,nt_mem
    lui t7,0x000E
    sw t9,0x7C0C(t7)              # note the hold
    addiu t3,zero,2
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    b nt_body
    sw t3,0x7C14(t7)
nt_mem:                           # nobody is held at this moment: did THIS object hold a hero a moment ago?
    lui t7,0x000E
    lw t3,0x7C0C(t7)
    bne t3,t9,nt_old
    lw t2,-11076(t5)
    lw t3,0x7C14(t7)
    subu t2,t2,t3
    sltiu t2,t2,90
    beq t2,zero,nt_old
    lw t3,0x7C10(t7)
    addiu t3,t3,-1
    beq t3,zero,nt_tw
    nop
nt_body:
    addiu sp,sp,-16               # the two instructions that sat at 0x0016A950
    j 0x0016A958
    sd s0,0(sp)
nt_old:
    j 0x000F5000                  # the twelfth glue's near_think
    nop
"""
NT_BASE_WORD = (0x0016A950, 0x0803D400)            # the base patch: j near_think (0x000F5000)


# ---- fortieth glue -----------------------------------------------------------------------------------------
HF_AT = 0x000E89A0
HF_END = 0x000E89E0
HF_SRC = """
hf_either:                        # from 0x0017E488 (was jal 0x001C9958). a0 = player 1's form, a1 = the helper's kind
    addiu sp,sp,-16
    sd ra,0(sp)
    sd a1,8(sp)
    jal 0x001C9958                # does player 1's form use this helper?
    nop
    bne v0,zero,hf_out
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,hf_out
    nop
    lbu a0,0x47E8(t7)             # the twin's own form (ninth glue)
    jal 0x001C9958                # does the twin's?
    ld a1,8(sp)
hf_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""
HF_HOOK = (0x0017E488, 0x0C072656)                 # jal 0x001C9958


# ---- forty-first glue --------------------------------------------------------------------------------------
FB_AT = 0x000E8CC0
FB_END = 0x000E8D80
FB_SRC = """
fb_req:                           # from 0x001B6700 (was jal 0x0016EF28; a0 = the form, from the delay slot). s2 = the
    lui t5,0x000F                 # form record: its first word is the body that changes
    lw t4,0x05CC(t5)              # the twin
    beq t4,zero,fb_plain          # one hero: as the game
    nop
    lw t6,0(s2)
    lui t3,0x000E
    bne t6,t4,fb_p1
    nop
    lui t7,0x0033                 # the twin changes: the other hero is player 1's
    lbu t6,-4012(t7)              # his form (the save's byte 0x0032F054)
    lw t2,0x7C04(t3)              # the number base of his form's files
    b fb_have
    addiu t1,t3,0x7C08            # where the twin's base is kept
fb_p1:
    lbu t6,0x47E8(t5)             # player 1's hero changes: the twin's form
    lw t2,0x7C08(t3)
    addiu t1,t3,0x7C04
fb_have:
    addiu t6,t6,-1
    sltiu t6,t6,6
    beq t6,zero,fb_go             # the other hero is in no form: 5000, as the game
    addiu t0,zero,5000
    bne t2,zero,fb_add
    nop
    addiu t2,zero,5000            # (his form was built with a room: the game's numbers)
fb_add:
    addiu t0,t2,10                # behind his files
fb_go:
    sw t0,0(t1)
    addiu sp,sp,-16
    sd ra,0(sp)
    sd t0,8(sp)
    jal 0x001D1438                # the form's object id
    nop
    move a0,v0
    ld a1,8(sp)
    ld ra,0(sp)
    addiu a2,zero,4
    addiu a3,zero,7
    j 0x0016EB48                  # the game's request, with this number base
    addiu sp,sp,16
fb_plain:
    j 0x0016EF28
    nop
"""
FB_HOOK = (0x001B6700, 0x0C05BBCA)                 # jal 0x0016EF28


# ---- forty-second glue -------------------------------------------------------------------------------------
HB_AT = 0x000E8D80
HB_END = 0x000E8E00
HB_SRC = """
hb_back:                          # from 0x001B649C and 0x001B6564 (was jal 0x001C9B90): a revert's cleanup
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x001C9B90                # the game's call: every helper who was away comes back
    nop
    lui t5,0x000F
    lw t4,0x05CC(t5)              # the twin
    beq t4,zero,hb_out            # one hero: as the game
    nop
    lui t7,0x0033
    lbu a0,-4012(t7)              # player 1's form (the save's byte 0x0032F054)
    addiu t6,a0,-1
    sltiu t6,t6,6
    beq t6,zero,hb_two
    nop
    jal 0x001C9860                # he is still in a form: its helpers go away again
    nop
hb_two:
    lui t5,0x000F
    lbu a0,0x47E8(t5)             # the twin's form
    addiu t6,a0,-1
    sltiu t6,t6,6
    beq t6,zero,hb_out
    nop
    jal 0x001C9860
    nop
hb_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""
HB_HOOKS = (
    (0x001B649C, 0x0C0726E4, "a revert's cleanup brings the helpers back: not those the other hero's form uses"),
    (0x001B6564, 0x0C0726E4, "(the second cleanup routine, the same call)"),
)


# ---- forty-third glue --------------------------------------------------------------------------------------
HS_AT = 0x000E8E00
HS_END = 0x000E8E60
HS_SRC = """
hs_tick:                          # from 0x00177510 (was jal 0x0016CD48). s0 = the hero, a0 = the script attached to him
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    bne s0,t6,hs_plain            # player 1's hero (or no twin): as it is
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player
    beq t4,t6,hs_plain
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd t4,8(sp)
    jal 0x0016CD48                # the twin's attached script runs with the twin as "the player"
    sw t6,-5816(t5)
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
hs_plain:
    j 0x0016CD48
    nop
"""
HS_HOOK = (0x00177510, 0x0C05B352)                 # jal 0x0016CD48


# ---- forty-fourth glue -------------------------------------------------------------------------------------
CF_AT = 0x000E9180
CF_END = 0x000E92A0
CF_SRC = """
cf_who:                           # from 0x001741EC (was jal 0x001D14A0): which hero is turned into the card / the die
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    lui t5,0x0035
    beq t6,zero,cf_game           # one hero: as the game
    lw t4,0x2400(t5)              # player 1's hero (the last-built hero object)
    beq t4,zero,cf_game
    nop
    lw t3,0x160(t6)
    andi t3,t3,0x4000             # is the twin held in a paired move?
    lw t2,0x160(t4)
    andi t2,t2,0x4000             # is player 1's hero?
    beq t3,t2,cf_eng              # both or none: the script's own player
    nop
    bne t3,zero,cf_tw             # only the twin
    nop
    jr ra                         # only player 1's hero
    move v0,t4
cf_tw:
    jr ra
    move v0,t6
cf_eng:
    lw v0,-5816(t5)               # the engine's player
    bne v0,zero,cf_ret
    nop
cf_game:
    lui t5,0x0035
    lw v0,0x2400(t5)
cf_ret:
    jr ra
    nop
cf_end_who:                       # from 0x00174218 (was jal 0x001D14A0): which hero comes back from the card / the die
    lui t7,0x000F
    lw t6,0x05CC(t7)
    lui t5,0x0035
    beq t6,zero,cf_game
    lw t4,0x2400(t5)
    beq t4,zero,cf_game
    nop
    lw t3,0xB50(t6)
    addiu t3,t3,-12
    bne t3,zero,cf_game           # the twin is in no capture form: the game's hero
    nop
    lw t2,0xB50(t4)
    addiu t2,t2,-12
    bne t2,zero,cf_tw             # only the twin is
    nop
    b cf_eng                      # both are: the script's own player
    nop
cf_form:                          # from 0x001B6C54 (was j 0x001B6298; a1 = the body that comes back, a2 = the form
    lui t7,0x000F                 # number of the save data = player 1's)
    lw t6,0x05CC(t7)
    bne a1,t6,cf_go
    nop
    lbu a2,0x47E8(t7)             # the twin's own form number
cf_go:
    j 0x001B6298
    nop
"""
CF_HOOKS = (
    (0x001741EC, 0x0C074528, "jal", "cf_who", "trap_player_capture_form: the hero the trick is played on"),
    (0x00174218, 0x0C074528, "jal", "cf_end_who", "trap_player_capture_form_end: the hero who is in the capture form"),
    (0x001B6C54, 0x0806D8A6, "j", "cf_form", "a body comes back from a capture form: the twin in his own form number"),
)


# ---- forty-fifth glue --------------------------------------------------------------------------------------
TP_AT = 0x000E92A0
TP_END = 0x000E9400
TP_SRC = """
tp_player:                        # from 0x00171074 (was jal 0x0016B0D0): a script asks for "the player"
    lui t5,0x0035
    lw v0,-5816(t5)               # the engine's player: the game's answer
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,tp_out
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,tp_out
    lw t8,-10076(t5)              # the running script (0x0034D8A4)
    beq t8,zero,tp_out
    nop
    lw t8,56(t8)                  # its object
    srl t3,t8,22
    addiu t3,t3,-6
    bne t3,zero,tp_out            # not an object
    nop
    beq t8,t4,tp_out              # a hero's own script: as it is
    nop
    beq t8,t6,tp_out
    lw t3,0(t8)
    lui t2,0x0034
    ori t2,t2,0x5C08
    beq t3,t2,tp_out              # a helper
    nop
    lw t9,0x140(t8)               # the first word of its motion part
    beq t9,zero,tp_out
    nop
    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
    bne t3,t9,tp_p1
    lw t3,0x160(t6)
    andi t3,t3,0x4000
    bne t3,zero,tp_ntw
    nop
tp_p1:
    lw t3,0x240(t4)               # is player 1's hero?
    bne t3,t9,tp_mem
    lw t3,0x160(t4)
    andi t3,t3,0x4000
    bne t3,zero,tp_nh1
    nop
tp_mem:                           # nobody at this moment: whom did it hold a moment ago?
    lui t7,0x000E
    lw t3,0x7C0C(t7)
    bne t3,t9,tp_out
    lw t2,-11076(t5)              # the game's counter
    lw t3,0x7C14(t7)
    subu t2,t2,t3
    sltiu t2,t2,90
    beq t2,zero,tp_out
    lw t3,0x7C10(t7)
    addiu t3,t3,-1
    bne t3,zero,tp_h1
    nop
tp_tw:
    jr ra
    move v0,t6
tp_h1:
    jr ra
    move v0,t4
tp_ntw:                           # the twin is held now: note it, he is the answer
    lui t7,0x000E
    sw t9,0x7C0C(t7)
    addiu t3,zero,1
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    b tp_tw
    sw t3,0x7C14(t7)
tp_nh1:                           # player 1's hero is held now
    lui t7,0x000E
    sw t9,0x7C0C(t7)
    addiu t3,zero,2
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    b tp_h1
    sw t3,0x7C14(t7)
tp_out:
    jr ra
    nop
"""
TP_HOOK = (0x00171074, 0x0C05AC34)                 # jal 0x0016B0D0


# ---- forty-sixth glue --------------------------------------------------------------------------------------
TQ_AT = 0x000E9400
TQ_END = 0x000E9600
TQ_SRC = """
tp_player2:                       # from 0x00171074 (was jal 0x0016B0D0): a script asks for "the player"
    lui t5,0x0035
    lw v0,-5816(t5)               # the engine's player: the game's answer
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,tq_out
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,tq_out
    lw t8,-10076(t5)              # the running script (0x0034D8A4)
    beq t8,zero,tq_out
    nop
    lw t8,56(t8)                  # its object
    srl t3,t8,22
    addiu t3,t3,-6
    bne t3,zero,tq_out            # not an object
    nop
    beq t8,t4,tq_out              # a hero's own script: as it is
    nop
    beq t8,t6,tq_out
    lw t3,0(t8)
    lui t2,0x0034
    ori t2,t2,0x5C08
    beq t3,t2,tq_out              # a helper
    nop
    lw t9,0x140(t8)               # the first word of its motion part
    beq t9,zero,tq_out
    nop
    lw t3,0x240(t6)               # is the twin held in a paired move by this object?
    bne t3,t9,tq_p1
    lw t3,0x160(t6)
    andi t3,t3,0x4000
    bne t3,zero,tq_ntw
    nop
tq_p1:
    lw t3,0x240(t4)               # is player 1's hero?
    bne t3,t9,tq_mem
    lw t3,0x160(t4)
    andi t3,t3,0x4000
    bne t3,zero,tq_nh1
    nop
tq_mem:                           # nobody at this moment: whom did it hold a moment ago?
    lui t7,0x000E
    lw t3,0x7C0C(t7)
    bne t3,t9,tq_near
    lw t2,-11076(t5)              # the game's counter
    lw t3,0x7C14(t7)
    subu t2,t2,t3
    sltiu t2,t2,90
    beq t2,zero,tq_near
    lw t3,0x7C10(t7)
    addiu t3,t3,-1
    bne t3,zero,tq_h1
    nop
tq_tw:
    jr ra
    move v0,t6
tq_h1:
    jr ra
    move v0,t4
tq_ntw:                           # the twin is held now: note it, he is the answer
    lui t7,0x000E
    sw t9,0x7C0C(t7)
    addiu t3,zero,1
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    b tq_tw
    sw t3,0x7C14(t7)
tq_nh1:                           # player 1's hero is held now
    lui t7,0x000E
    sw t9,0x7C0C(t7)
    addiu t3,zero,2
    sw t3,0x7C10(t7)
    lw t3,-11076(t5)
    b tq_h1
    sw t3,0x7C14(t7)
tq_near:                          # nobody held, nobody remembered: THE NEARER HERO (the twelfth glue's rule)
    lw t3,0x48C(t6)               # the twin's unit slot
    beq t3,zero,tq_h1
    nop
    lw t3,0(t3)
    beq t3,zero,tq_h1             # the twin is down: player 1's hero
    nop
    lw t2,0x48C(t4)
    beq t2,zero,tq_dist
    nop
    lw t2,0(t2)
    beq t2,zero,tq_tw             # player 1's hero is down: the twin
    nop
tq_dist:
    lwc1 f0,0x70(t8)
    lwc1 f1,0x78(t8)
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
    bc1f tq_h1                    # player 1's hero is nearer (or as near)
    nop
    b tq_tw
    nop
tq_out:
    jr ra
    nop
cf_who2:                          # from 0x001741EC (was jal 0x001D14A0): which hero is turned into the card / the die
    addiu sp,sp,-16
    sd ra,0(sp)
    jal tp_player2                # the same answer as the script's "the player"
    nop
    ld ra,0(sp)
    bne v0,zero,cq_ret
    addiu sp,sp,16
    lui t5,0x0035
    lw v0,0x2400(t5)              # nobody: the game's own answer
cq_ret:
    jr ra
    nop
"""


# ---- forty-seventh glue ------------------------------------------------------------------------------------
RC_AT = 0x000E9600
RC_END = 0x000E9800
V_SENDER = 0x000E7C18                              # the hero whose command's callback is running (0 = none)
#                                                    0x000E7C1C = the game's counter when that note was written
RC_SRC = """
rc_one:                           # from 0x00178C7C (was jal 0x0016BAE8): a hero's command calls back its source object
    lui t7,0x000F                 # a0 = the source object, a1 = the hero
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,rc_go
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,rc_go
    nop
    beq a1,t6,rc_o                # the twin sends: the other hero is player 1's
    move t3,t4
    bne a1,t4,rc_go               # the sender is no hero: as the game
    move t3,t6
rc_o:
    beq a0,zero,rc_go
    srl t2,a0,22
    addiu t2,t2,-6
    bne t2,zero,rc_go             # the source is not an object
    nop
    beq a0,t4,rc_go               # the source is a hero or a helper (Limits, the heroes' own commands): as the game
    nop
    beq a0,t6,rc_go
    lw t2,0(a0)
    lui t1,0x0034
    ori t1,t1,0x5C08
    beq t2,t1,rc_go
    nop
    lw t9,0x140(a0)               # the first word of the source's motion part
    beq t9,zero,rc_send
    nop
    lw t2,0x240(t3)               # does the source hold the OTHER hero in a paired move?
    bne t2,t9,rc_mem
    lw t2,0x160(t3)
    andi t2,t2,0x4000
    beq t2,zero,rc_mem
    nop
rc_drop:
    jr ra                         # yes: one object holds one hero. This hero's command does nothing.
    nop
rc_mem:                           # not at this moment: did it hold the other hero less than 90 steps ago?
    lui t7,0x000E
    lw t2,0x7C0C(t7)
    bne t2,t9,rc_send             # the memory is about another object
    lw t2,-11076(t5)              # the game's counter
    lw t1,0x7C14(t7)
    subu t2,t2,t1
    sltiu t2,t2,90
    beq t2,zero,rc_send
    lw t2,0x7C10(t7)              # 1 = the twin was held, 2 = player 1's hero
    addiu t1,zero,1
    beq t3,t6,rc_who              # the other hero is the twin: the memory must say 1
    nop
    addiu t1,zero,2
rc_who:
    beq t2,t1,rc_drop
    nop
rc_send:
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000E
    lw t2,-11076(t5)              # the game's counter: the note holds for this step only
    sw t2,0x7C1C(t7)
    jal 0x0016BAE8
    sw a1,0x7C18(t7)              # the sender, for the callback's "the player"
    lui t7,0x000E
    sw zero,0x7C18(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
rc_go:
    j 0x0016BAE8
    nop
ns_pre:                           # the jump at 0x0016CCE8 comes here first. a0 = the script, its object at +56
    lui t7,0x000E
    lw t3,0x7C18(t7)              # did a hero send this callback?
    beq t3,zero,ns_old
    lw t2,0x7C1C(t7)              # ... in this very step?
    lui t1,0x0035
    lw t1,-11076(t1)
    bne t2,t1,ns_old
    lw t8,56(a0)                  # the object
    srl t2,t8,22
    addiu t2,t2,-6
    bne t2,zero,ns_old            # not an object
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,ns_old
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t8,t4,ns_old              # a hero's or a helper's own script: the thirty-sixth glue decides
    nop
    beq t8,t6,ns_old
    lw t2,0(t8)
    lui t1,0x0034
    ori t1,t1,0x5C08
    beq t2,t1,ns_old
    nop
    bne t3,t6,ns_body             # player 1's hero sent it: he is the engine's player already
    nop
    lw t4,-5816(t5)               # the twin sent it: this callback runs with the twin as "the player"
    addiu sp,sp,-32
    sd ra,0(sp)
    sd t4,8(sp)
    jal ns_body
    sw t6,-5816(t5)
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
ns_body:
    addiu sp,sp,-48               # the two instructions that sat at 0x0016CCE8
    j 0x0016CCF0
    sd s0,0(sp)
ns_old:
    j 0x%08X                      # the thirty-sixth glue's nc_trig
    nop
""" % NC_AT
RC_HOOK = (0x00178C7C, 0x0C05AEBA)                 # jal 0x0016BAE8


# ---- forty-eighth glue (only with --ownrec) ----------------------------------------------------------------
RT_AT = 0x000E9800
RT_END = 0x000E9900                                # (0x000E9900 .. 0x000E9A00: the seventy-first glue's ob_gain)
REC_T = 0x000E7D00                                 # the twin's own character record (0x114 bytes)
V_TSRC = 0x000E7E20                                # the record T was made from (0 = not made yet)
RT_SRC = """
t_load:                           # jump at 0x001A1200 (was: bne a1,zero,0x001A1214 / daddu s1,a1,zero). a0 = the slot
    lw t7,0x250(a0)
    bltz t7,tl_twin               # lane D's mark: the second hero's slot
    nop
tl_game:
    bne a1,zero,tl_have
    daddu s1,a1,zero
    j 0x001A1208
    nop
tl_have:
    j 0x001A1214
    nop
tl_twin:
    lui t6,0x000E
    ori t6,t6,0x7D00              # record T (a view)
    lui t5,0x000E
    bne a1,zero,tl_s1
    lw t4,0x7E20(t5)              # the record T shows
    lw a1,0x244(a0)               # no record given: the slot's own
    beq a1,zero,tl_game           # none: as the game
    nop
tl_s1:
    bne a1,t6,tl_s2
    nop
    move a1,t4                    # the slot's record is T: the source is the remembered one
    beq a1,zero,tl_use            # (cannot be) T without a source: use it as it is
    nop
tl_s2:
    sw a1,0x7E20(t5)              # the source of the view
    addiu t3,zero,0x114           # T = all of the source ...
    move t2,a1
    move t1,t6
tl_cp:
    lw t0,0(t2)
    sw t0,0(t1)
    addiu t3,t3,-4
    addiu t2,t2,4
    bgtz t3,tl_cp
    addiu t1,t1,4
    lw t3,0x254(a0)               # whose slot: only a hero (1 = Sora, 14 = Roxas) has places of player 2's
    addiu t2,zero,1
    beq t3,t2,tl_hero
    addiu t2,zero,14
    bne t3,t2,tl_use              # another body (King Mickey ...): the plain copy
    nop
tl_hero:
    sw a1,0x7E28(t5)              # the hero's record: the one the pause menu edits
    lw t3,0x7E24(t5)              # player 2's menu is open: the places have changed places in the source already
    bne t3,zero,tl_use
    nop
    lw t0,0x1C(a1)                # ... with PLAYER 2'S armour places (+ 0x1C .. + 0x23) where the hero's are
    lw t1,0x20(a1)
    lw t2,0x14(a1)
    lw t3,0x18(a1)
    sw t0,0x14(t6)
    sw t1,0x18(t6)
    sw t2,0x1C(t6)
    sw t3,0x20(t6)
    lw t0,0x2C(a1)                # and his accessory places (+ 0x2C .. + 0x33)
    lw t1,0x30(a1)
    lw t2,0x24(a1)
    lw t3,0x28(a1)
    sw t0,0x24(t6)
    sw t1,0x28(t6)
    sw t2,0x2C(t6)
    sw t3,0x30(t6)
tl_use:
    sw t6,0x244(a0)               # the twin's slot reads the view
    j 0x001A1214
    daddu s1,t6,zero
"""
RT_HOOK = (0x001A1200, 0x14A00004, 0x00A0882D)     # bne a1,zero,0x001A1214 / daddu s1,a1,zero


# ---- forty-ninth glue (only with --ownmenu) ----------------------------------------------------------------
RM_AT = 0x000E9A00
RM_END = 0x000E9C00
V_MENU2 = 0x000E7E24                               # 1 while player 2's pause menu is open (the places have changed places)
RM_SRC = """
ow_swap:                          # the hero's places 1-4 and player 2's places 5-8 change places in the source record
    lui t5,0x000E
    lw t4,0x7E28(t5)              # the hero's record (Sora's, Roxas's)
    beq t4,zero,os_out
    addiu t3,zero,2               # twice: the armour block (+ 0x14), the accessory block (+ 0x24)
    addiu t4,t4,0x14
os_blk:
    lw t0,0(t4)
    lw t1,4(t4)
    lw t2,8(t4)
    lw t9,12(t4)
    sw t2,0(t4)
    sw t9,4(t4)
    sw t0,8(t4)
    sw t1,12(t4)
    addiu t3,t3,-1
    bgtz t3,os_blk
    addiu t4,t4,0x10
os_out:
    jr ra
    nop
ow_load:                          # player 1's slot writes back and loads its stats again (lane D's D6: the twin's too)
    addiu sp,sp,-32
    sd ra,0(sp)
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,ol_out
    nop
    lw a0,0x48C(t4)               # his unit slot
    beq a0,zero,ol_out
    nop
    sd a0,8(sp)
    jal 0x001A1840
    nop
    ld a0,8(sp)
    jal 0x001A11E0
    move a1,zero
ol_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
mo_open:                          # from 0x00138574 (was jal 0x00253180): START opens the main menu. a0 = 0, a1 = -1
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,mo_go
    lui t5,0x0035
    addiu t5,t5,-10560            # 0x0034D6C0: logical controller 0; controller 1 is 0x60 further
    ld t4,8(t5)                   # pressed, player 1's
    andi t4,t4,0x2
    bne t4,zero,mo_go             # player 1 pressed START (or both did): his menu
    ld t4,0x68(t5)
    andi t4,t4,0x2
    beq t4,zero,mo_go             # (not player 2 either)
    lui t3,0x000E
    lw t2,0x7E24(t3)
    bne t2,zero,mo_go             # (never twice)
    lw t2,0x7E28(t3)
    beq t2,zero,mo_go             # no hero record noted yet
    addiu t1,zero,1
    sw t1,0x7E24(t3)              # player 2's menu is open
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    jal ow_swap
    nop
    jal ow_load
    nop
    ld a0,8(sp)
    ld a1,16(sp)
    ld ra,0(sp)
    addiu sp,sp,32
mo_go:
    j 0x00253180
    nop
ms_tick:                          # from 0x00138538 (the second glue's jal pad_both): each step the field looks for START
    lui t3,0x000E
    lw t2,0x7E24(t3)
    beq t2,zero,ms_go             # player 2's menu is not open
    nop
    addiu sp,sp,-16               # the field looks for START again, so the menu has gone (or never came):
    sd ra,0(sp)
    jal ow_swap                   # the places change back
    nop
    lui t3,0x000E
    jal ow_load
    sw zero,0x7E24(t3)
    ld ra,0(sp)
    addiu sp,sp,16
ms_go:
    j 0x000F4740                  # the second glue's pad_both
    move a0,zero
or_load:                          # from 0x00240B84 (was j 0x002FDD68): a save file is copied into the save data
    lui t7,0x000E
    j 0x002FDD68
    sw zero,0x7E24(t7)            # nobody's menu is open
or_new:                           # from 0x00105770 (was jal 0x002FD310): the save data are made new
    lui t7,0x000E
    j 0x002FD310
    sw zero,0x7E24(t7)
"""
RM_LOAD = (0x00240B84, 0x080BF75A)                 # j 0x002FDD68
RM_NEW = (0x00105770, 0x0C0BF4C4)                  # jal 0x002FD310
RM_OPEN = (0x00138574, 0x0C094C60)                 # jal 0x00253180
RM_TICK = (0x00138538, 0x0C03D1D0)                 # the base patch: jal pad_both (0x000F4740)


# ---- fiftieth glue, an experiment (only with --together) --------------------------------------------------
TG_AT = 0x000E9C00
TG_END = 0x000EB000
TG_SRC = """
tg_cap:                           # jump at 0x00180378 (its first two instructions are at tg_go). a0 = the captor's
    lui t7,0x000E                 # motion part, a1 = the victim, a2 = the motion number, f12 = the time
    lw t6,0x7E30(t7)
    bne t6,zero,tg_go             # this IS the second call
    lw t3,0x7E38(t7)              # the second hero of a living pair
    beq t3,zero,tg_go             # no pair: as the game (a grab is the grabbed hero's alone)
    lw t2,0x7E34(t7)              # the first hero
    beq a1,t3,tg_c0               # the victim is the second: the other one is the first
    move t3,t2
    lw t4,0x7E38(t7)
    bne a1,t2,tg_go               # the victim is neither of the two
    move t3,t4
tg_c0:
    lui t5,0x0035
    lw t2,-11076(t5)
    sw t2,0x7E40(t7)              # a capture of either: the clock is fresh
    lw t6,0x7E48(t7)
    bne t6,zero,tg_go             # a hero's own hooked script makes this capture: it is his alone
    lui t2,0x0033
    lhu t2,-17696(t2)             # 0x0032BAE0: the world and the room
    addiu t1,zero,0x0908
    bne t2,t1,tg_go               # (the experiment: only Shan-Yu's room, world 08 room 09)
    addiu t8,a0,-320              # the captor object
    srl t2,t8,22
    addiu t2,t2,-6
    bne t2,zero,tg_go             # not an object
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    lw t4,0x2400(t5)              # player 1's hero
    beq t3,t6,tg_o
    nop
    bne t3,t4,tg_go               # the other one is no hero of this room any more
    nop
tg_o:
    beq t8,t4,tg_go               # a hero or a helper holds (a Limit ...): as the game
    nop
    beq t8,t6,tg_go
    lw t2,0(t8)
    lui t1,0x0034
    ori t1,t1,0x5C08
    beq t2,t1,tg_go
    nop
    lw t2,0x48C(t3)               # the other hero's unit slot
    beq t2,zero,tg_go
    nop
    lw t2,0(t2)
    beq t2,zero,tg_go             # he is down
    nop
    lw t2,0x160(t3)
    andi t2,t2,0x4000
    bne t2,zero,tg_do             # he is held: still in the move
    lw t2,0xAEC(t3)
    beq t2,zero,tg_go             # not held and no hooked script: he has left the move
    nop
tg_do:
    lw t9,0(a0)
    sw t9,0x7E3C(t7)              # the captor's word
    addiu sp,sp,-112
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd a2,24(sp)
    swc1 f12,32(sp)
    swc1 f13,36(sp)
    sd a3,40(sp)
    sd t3,48(sp)
    swc1 f14,56(sp)
    sd t8,80(sp)
tg_dir:
    lwc1 f0,0x70(t8)
    lwc1 f1,0x78(t8)
    lwc1 f2,0x70(t3)
    lwc1 f3,0x78(t3)
    sub.s f0,f0,f2
    sub.s f1,f1,f3
    swc1 f0,64(sp)                # the way from him to the boss (x, 0, z, 0)
    sw zero,68(sp)
    swc1 f1,72(sp)
    sw zero,76(sp)
    move a0,t3
    jal 0x0016AEF0                # he looks at the boss
    addiu a1,sp,64
    lui t7,0x000E
    addiu t2,zero,1
    sw t2,0x7E30(t7)
    ld a0,8(sp)
    ld a1,48(sp)
    ld a2,24(sp)
    ld a3,40(sp)
    lwc1 f13,36(sp)
    lwc1 f14,56(sp)
    jal 0x00180378                # the same move on the other hero of the pair
    lwc1 f12,32(sp)
    lui t7,0x000E
    sw zero,0x7E30(t7)
    ld ra,0(sp)
    ld a0,8(sp)
    ld a1,16(sp)
    ld a2,24(sp)
    ld a3,40(sp)
    lwc1 f13,36(sp)
    lwc1 f14,56(sp)
    lwc1 f12,32(sp)
    addiu sp,sp,112
tg_go:
    addiu sp,sp,-48               # the two instructions that sat at 0x00180378
    j 0x00180380
    swc1 f20,32(sp)
th_new:                           # from 0x00171FE4 (was jal 0x0016CF00): a new context for a script that is hooked onto
    addiu sp,sp,-128              # an object. a0 = the script root, a1 = 0, a2 = the function, a3 = [object, extra], t0 = how many
    sd ra,0(sp)
    sd a0,8(sp)
    sd a2,16(sp)
    sd a3,24(sp)
    sd t0,32(sp)
    jal 0x0016CF00
    nop
    sd v0,40(sp)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,tn_out
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,tn_out
    lui t2,0x0033
    lhu t2,-17696(t2)
    addiu t1,zero,0x0908
    bne t2,t1,tn_out              # (the experiment: only Shan-Yu's room)
    ld t8,24(sp)
    lw t8,0(t8)                   # the object the script is hooked onto
    beq t8,t6,tn_o
    move t3,t4
    bne t8,t4,tn_out              # not a hero
    move t3,t6
tn_o:
    lui t7,0x000E
    lw t2,0x7E48(t7)
    bne t2,zero,tn_out            # a hero's own hooked script hooks: each hero's script does that for itself
    nop
    ld t2,8(sp)
    lw t9,56(t2)                  # the object whose script hooks
    srl t2,t9,22
    addiu t2,t2,-6
    bne t2,zero,tn_out            # not an object
    nop
    beq t9,t4,tn_out              # a hero's or a helper's own script (a Limit ...): as the game
    nop
    beq t9,t6,tn_out
    lw t2,0(t9)
    lui t1,0x0034
    ori t1,t1,0x5C08
    beq t2,t1,tn_out
    nop
    lw t2,0x48C(t3)               # the other hero's unit slot
    beq t2,zero,tn_out
    nop
    lw t2,0(t2)
    beq t2,zero,tn_out            # he is down
    nop
    sd t3,48(sp)
    sd t8,56(sp)
    lw t1,0x160(t3)
    andi t1,t1,0x4000             # is he held
    lw t0,0xAEC(t3)               # has he a hooked script
    lw t2,0x7E38(t7)
    beq t2,zero,tn_first
    nop
    or t1,t1,t0                   # a pair lives: he gets the copy while he is still in the move
    beq t1,zero,tn_out
    nop
    b tn_copy
    nop
tn_first:
    or t1,t1,t0
    bne t1,zero,tn_out            # no pair yet, and he is busy in something else
    nop
    lw t2,0x7C18(t7)              # the forty-seventh glue's note: is this the answer to a hero's command?
    beq t2,zero,tn_far
    lw t2,0x7C1C(t7)
    lw t1,-11076(t5)
    beq t2,t1,tn_out              # yes: a hero's own command never pulls the other hero in
    nop
tn_far:
    lwc1 f0,0x70(t8)
    lwc1 f1,0x78(t8)
    lwc1 f2,0x70(t3)
    lwc1 f3,0x78(t3)
    sub.s f2,f2,f0
    sub.s f3,f3,f1
    mul.s f2,f2,f2
    mul.s f3,f3,f3
    add.s f2,f2,f3                # the two heroes' distance, squared
    lui t2,0x4874
    ori t2,t2,0x2400              # 250000.0 = 500 units, squared
    mtc1 t2,f4
    c.lt.s f2,f4
    bc1f tn_out                   # too far: he stays free
    nop
tn_place:
    addiu a0,sp,64
    jal 0x0016AF58                # the first hero's direction (the script has turned him for the move)
    move a1,t8
    ld t8,56(sp)
    lwc1 f0,64(sp)
    lwc1 f1,72(sp)
    lui t2,0x425C                 # 55.0: 55 units to the side and 55 units behind the first hero
    mtc1 t2,f6
    sub.s f2,f1,f0
    add.s f3,f0,f1
    mul.s f2,f2,f6
    mul.s f3,f3,f6
    lwc1 f4,0x70(t8)
    lwc1 f5,0x78(t8)
    add.s f4,f4,f2                # x: the first hero's + 55 * (his direction's z - x)
    sub.s f5,f5,f3                # z: the first hero's - 55 * (his direction's x + z)
    swc1 f4,80(sp)
    lw t2,0x74(t8)
    sw t2,84(sp)
    swc1 f5,88(sp)
    lw t2,0x7C(t8)
    sw t2,92(sp)
    ld a0,48(sp)
    jal 0x0016ACE0                # the second hero is put beside the first
    addiu a1,sp,80
    ld a0,48(sp)
    jal 0x0016AEF0                # and looks the same way
    addiu a1,sp,64
    ld t3,48(sp)
    ld t8,56(sp)
    lui t7,0x000E
    lui t5,0x0035
tn_copy:
    sw t8,0x7E34(t7)              # the first hero
    sw t3,0x7E38(t7)              # the second hero
    lw t2,-11076(t5)
    sw t2,0x7E40(t7)
    ld t9,24(sp)
    lw t2,4(t9)
    sw t3,96(sp)                  # the second array: [the other hero, the same extra]
    sw t2,100(sp)
    ld a0,8(sp)
    move a1,zero
    ld a2,16(sp)
    addiu a3,sp,96
    jal 0x0016CF00                # his own context of the same function
    ld t0,32(sp)
    ld a0,48(sp)
    jal 0x00177460                # hooked onto him
    move a1,v0
tn_out:
    ld v0,40(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,128
th_tick:                          # from 0x00177510 (the forty-third glue's jal hs_tick, or the game's runner): a hero's
    addiu sp,sp,-48               # hooked script runs. s0 = the hero, a0 = the script context
    sd ra,0(sp)
    sd zero,8(sp)
    lui t7,0x000E
    addiu t2,zero,1
    sw t2,0x7E48(t7)              # noted, so that tg_cap and th_new leave what it does alone
    lw t3,0x7E38(t7)
    bne t3,s0,tk_run              # not the second hero of a pair: as the game
    lw t4,16(a0)                  # the work memory (the boss's own: the hooked script shares it; + 52 is only its handle)
    beq t4,zero,tk_run
    nop
tk_keep:
    sd t4,8(sp)                   # the boss's three numbers of the clash (Shan-Yu: push count, push speed, time limit)
    lw t2,148(t4)
    sw t2,16(sp)
    lw t2,152(t4)
    sw t2,20(sp)
    lw t2,156(t4)
    sw t2,24(sp)
tk_run:
    jal HOOK_NEXT
    nop
    ld t4,8(sp)
    beq t4,zero,tk_done
    lw t2,16(sp)
    sw t2,148(t4)                 # as they were before the second hero's copy ran: one script steps them
    lw t2,20(sp)
    sw t2,152(t4)
    lw t2,24(sp)
    sw t2,156(t4)
tk_done:
    lui t7,0x000E
    sw zero,0x7E48(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
tg_tick:                          # from 0x00138538 (the field's START look-out, each step)
    lui t7,0x000E
    lw t3,0x7E38(t7)              # the second hero of a pair
    beq t3,zero,tt_go
    lui t5,0x000F
    lw t6,0x05CC(t5)              # the twin
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    lw t2,0x7E34(t7)              # the first hero
    beq t3,t6,tt_v1
    nop
    bne t3,t4,tt_clear            # not the heroes of this room any more
    nop
    bne t2,t6,tt_clear
    nop
    b tt_ok
    nop
tt_v1:
    bne t2,t4,tt_clear
    nop
tt_ok:
    lw t1,-11076(t5)
    lw t0,0x7E40(t7)
    subu t1,t1,t0                 # steps since the last hook or capture of either
    lw t8,0x160(t2)
    andi t8,t8,0x4000             # the first: held
    lw t9,0xAEC(t2)               # the first: hooked script
    lw v0,0x160(t3)
    andi v0,v0,0x4000             # the second: held
    lw v1,0xAEC(t3)               # the second: hooked script
    or t0,t8,v0
    or t0,t0,t9
    or t0,t0,v1
    bne t0,zero,tt_live
    sltiu t0,t1,10
    bne t0,zero,tt_go             # all quiet for less than 10 steps
    nop
    b tt_clear                    # all quiet: the pair is forgotten
    nop
tt_live:
    sltiu t0,t1,120
    bne t0,zero,tt_go             # a capture came in the last 120 steps
    nop
    beq t8,zero,tt_l2             # the safety rule: held, no hooked script, no capture for 120 steps
    nop
    beq t9,zero,tt_free
    move a0,t2
tt_l2:
    beq v0,zero,tt_go
    nop
    bne v1,zero,tt_go
    move a0,t3
tt_free:
    addiu sp,sp,-16
    sd ra,0(sp)
    sd a0,8(sp)
    mtc1 zero,f12
    mtc1 zero,f13
    addiu a0,a0,320
    jal 0x0017EFA0                # "no motion": the paired move ends
    move a1,zero
    ld a0,8(sp)
    jal 0x0016BD60                # "go idle": his action is ended the game's own way
    move a1,zero
    ld ra,0(sp)
    addiu sp,sp,16
    lui t7,0x000E
    lui t5,0x0035
    lw t1,-11076(t5)
    b tt_go
    sw t1,0x7E40(t7)
tt_clear:
    sw zero,0x7E38(t7)
tt_go:
    j TICK_NEXT
    move a0,zero
tg_ro:                            # hook 0x00189E3C (was the thirty-eighth glue's jal ro2). s1 = the object whose
    lui t7,0x0035                 # motion offers the command, s3 = the command, s2 = its argument. Out: s0
    lw s0,-5816(t7)               # the engine's player
    lui t3,0x000E
    lw t2,0x7E44(t3)
    beq t2,zero,tr_1
    nop
    sw zero,0x7E44(t3)            # the second pass: this offer is for the second hero
    jr ra
    move s0,t2
tr_1:
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    beq t6,zero,tr_out
    nop
    beq s1,t6,tr_twin             # the twin's own motion offers it (fifteenth glue)
    nop
    lw t4,0x140(s1)               # the first word of the source's motion part
    beq t4,zero,tr_out
    nop
    lw t2,0x7E38(t3)              # a pair in a move of this source?
    beq t2,zero,tr_held
    lw t5,0x7E3C(t3)
    bne t5,t4,tr_held
    nop
    lw s0,0x7E34(t3)              # this pass: the first hero
    addiu sp,sp,-48
    sd ra,0(sp)
    sd s0,8(sp)
    sw t2,0x7E44(t3)
    move a0,s1
    move a1,s3
    jal 0x00189E18                # and once more for the second hero
    move a2,s2
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,48
tr_held:
    lw t5,0x240(t6)               # is the twin held in a paired move by this object?
    bne t5,t4,tr_out
    lw t5,0x160(t6)
    andi t5,t5,0x4000
    beq t5,zero,tr_out
    nop
tr_twin:
    move s0,t6
tr_out:
    jr ra
    nop
"""
TG_HOOK = (0x00180378, 0x27BDFFD0, 0xE7B40020)     # addiu sp,sp,-48 / swc1 f20,32(sp)


# ---- fifty-first glue, an experiment (only with --ship2hit) ------------------------------------------------
GS_AT = 0x000EB000
GS_END = 0x000EB300                                # (0x000EB300 .. 0x000EB400: the seventy-first glue's ob_tick)
GS_SRC = """
gs_inst:                          # from 0x00167E90 (was the base's jal gm_pad): a fresh flight module gets four jumps
    lui t7,0x01F2
    lhu t6,-32748(t7)             # 0x01F18014: which Gummi module is in memory (0x636A = the flight)
    ori t4,zero,0x636A
    bne t6,t4,gi_go
    lw t5,0x17C8(t7)              # 0x01F217C8 "does this ball touch you": still addiu sp,sp,-128?
    lui t4,0x27BD
    ori t4,t4,0xFF80
    bne t5,t4,gi_go
    lw t5,0x17A8(t7)              # 0x01F217A8 "can you be hit now": still addiu sp,sp,-16?
    lui t4,0x27BD
    ori t4,t4,0xFFF0
    bne t5,t4,gi_go
    lw t5,0x0320(t7)              # 0x01F20320 "you are hit": still addiu sp,sp,-32?
    lui t4,0x27BD
    ori t4,t4,0xFFE0
    bne t5,t4,gi_go
    lw t5,0x03A8(t7)              # 0x01F203A8 "take damage": the same word
    bne t5,t4,gi_go
    lw t5,0x00C8(t7)              # 0x01F200C8 "repair": still addiu sp,sp,-16?
    lui t4,0x27BD
    ori t4,t4,0xFFF0
    bne t5,t4,gi_go
    lui t4,@J_REP_HI@
    ori t4,t4,@J_REP_LO@
    sw t4,0x00C8(t7)              # j gs_rep
    sw zero,0x00CC(t7)
    lui t4,@J_TEST_HI@
    ori t4,t4,@J_TEST_LO@
    sw t4,0x17C8(t7)              # j gs_test
    sw zero,0x17CC(t7)
    lui t4,@J_ABLE_HI@
    ori t4,t4,@J_ABLE_LO@
    sw t4,0x17A8(t7)              # j gs_able
    sw zero,0x17AC(t7)
    lui t4,@J_HIT_HI@
    ori t4,t4,@J_HIT_LO@
    sw t4,0x0320(t7)              # j gs_hit
    sw zero,0x0324(t7)
    lui t4,@J_DMG_HI@
    ori t4,t4,@J_DMG_LO@
    sw t4,0x03A8(t7)              # j gs_dmg
    sw zero,0x03AC(t7)
    lui t4,0x000E
    sw zero,0x7E4C(t4)
    lui t3,0x01F7                 # the hull gauge (0x01F69790) asks for "the player ship" at 0x01F697C4 and 0x01F697D4
    lui t4,0x0C7C
    ori t4,t4,0x873E              # jal 0x01F21CF8
    lw t5,-26684(t3)
    bne t5,t4,gi_go
    lw t5,-26668(t3)
    bne t5,t4,gi_go
    lui t4,@JAL_LOW_HI@
    ori t4,t4,@JAL_LOW_LO@
    sw t4,-26684(t3)              # jal gs_low
    sw t4,-26668(t3)
gi_go:
    j GM_NEXT                     # the twenty-sixth glue's gm_pad
    nop
gs_rep:                           # 0x01F200C8(a0 = a ship, f12 = the amount): repair
    lui t7,0x000F
    lw t6,0x2604(t7)              # ship 2
    beq t6,zero,gr_go
    lw t5,0x2600(t7)
    bne a0,t5,gr_go               # not ship 1
    lw t4,0x1438(t6)
    andi t4,t4,0x10
    bne t4,zero,gr_go             # ship 2 has fallen
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    swc1 f12,16(sp)
    jal gr_go                     # ship 2 gets the same repair
    move a0,t6
    ld a0,8(sp)
    lwc1 f12,16(sp)
    ld ra,0(sp)
    addiu sp,sp,32
gr_go:
    addiu sp,sp,-16               # the two instructions that sat at 0x01F200C8
    j 0x01F200D0
    sd s0,0(sp)
gs_low:                           # the gauge's "player ship": the ship with the lower hull
    lui t7,0x01F8
    lw v0,-8636(t7)               # the game's (ship 1)
    lui t6,0x000F
    lw t5,0x2604(t6)              # ship 2
    beq t5,zero,gl_out
    lw t4,0x2600(t6)
    bne t4,v0,gl_out
    nop
    lwc1 f0,0x4AC(v0)
    lwc1 f1,0x4AC(t5)
    c.lt.s f1,f0
    bc1f gl_out
    nop
    move v0,t5
gl_out:
    jr ra
    nop
gs_test:                          # 0x01F217C8(a0 = a ship, a1 = a ball): does the ball touch the ship
    lui t7,0x000F
    lw t6,0x2604(t7)              # ship 2
    beq t6,zero,gt_orig
    lw t5,0x2600(t7)              # ship 1
    bne a0,t5,gt_orig             # asked about something else
    lui t4,0x000E
    sw zero,0x7E4C(t4)            # a new question: no hit of ship 2 is waiting
    lw t3,0x50C(t6)
    addiu t2,zero,2
    bne t3,t2,gt_orig             # ship 2 is not under control (flying in, done, destroyed)
    lw t3,0x1438(t6)
    andi t3,t3,0x10
    bne t3,zero,gt_orig           # ship 2 is at its end already
    nop
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a1,16(sp)
    sd t6,24(sp)
    jal gt_orig                   # ship 1 first
    nop
    bne v0,zero,gt_done           # ship 1 is touched: as the game
    ld a0,24(sp)
    jal gt_orig                   # the same ball and ship 2
    ld a1,16(sp)
    beq v0,zero,gt_done
    lui t4,0x000E
    ld t6,24(sp)
    sw t6,0x7E4C(t4)              # ship 2 is touched: the calls that follow are ship 2's
gt_done:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
gt_orig:
    addiu sp,sp,-128              # the two instructions that sat at 0x01F217C8
    j 0x01F217D0
    sd s1,88(sp)
gs_able:                          # 0x01F217A8(a0 = a ship): can it be hit now
    lui t7,0x000E
    lw t6,0x7E4C(t7)
    beq t6,zero,ga_go
    lui t5,0x000F
    lw t5,0x2600(t5)
    bne a0,t5,ga_go
    nop
    move a0,t6                    # the hit that is waiting is ship 2's
ga_go:
    addiu sp,sp,-16               # the two instructions that sat at 0x01F217A8
    j 0x01F217B0
    sd ra,0(sp)
gs_hit:                           # 0x01F20320(a0 = a ship, a1 = the hit record): you are hit
    lui t7,0x000E
    lw t6,0x7E4C(t7)
    beq t6,zero,gh_go
    lui t5,0x000F
    lw t5,0x2600(t5)
    bne a0,t5,gh_go
    nop
    move a0,t6
    sw zero,0x7E4C(t7)            # used up
gh_go:
    addiu sp,sp,-32               # the two instructions that sat at 0x01F20320
    j 0x01F20328
    sd s0,0(sp)
gs_dmg:                           # 0x01F203A8(a0 = a ship, a1 = the amount): take damage
    lui t7,0x000E
    lw t6,0x7E4C(t7)
    beq t6,zero,gd_chk
    lui t5,0x000F
    lw t4,0x2600(t5)
    bne a0,t4,gd_chk
    nop
    move a0,t6
    sw zero,0x7E4C(t7)            # used up
gd_chk:
    lui t5,0x000F
    lw t4,0x2604(t5)              # ship 2
    beq t4,zero,gd_go
    nop
    bne a0,t4,gd_go               # not ship 2: as the game
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    jal gd_go                     # ship 2 takes the damage
    nop
    ld t4,8(sp)
    lw t3,0x1438(t4)
    andi t3,t3,0x10
    beq t3,zero,gd_out            # ship 2 is still flying
    lui t5,0x000F
    lw t2,0x2600(t5)              # ship 2 has fallen: the mission is over when either ship falls, so ship 1 goes
    beq t2,zero,gd_out            # with it: hull 0 and the game's own "at its end" flag
    nop
    lw t3,0x1438(t2)
    andi t1,t3,0x10
    bne t1,zero,gd_out
    ori t3,t3,0x10
    sw t3,0x1438(t2)
    sw zero,0x4AC(t2)
gd_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
gd_go:
    addiu sp,sp,-32               # the two instructions that sat at 0x01F203A8
    j 0x01F203B0
    sd s0,0(sp)
"""


# ---- fifty-second glue, an experiment (only with --carpet2) ------------------------------------------------
GC_AT = 0x000EB400
GC_END = 0x000EB800
GC_SRC = """
gc_tick:                          # from 0x00138538 (the field's START look-out, each step)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,gk_go
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,gk_go
    nop
    lw t2,8(t6)
    lw t2,0(t2)                   # the twin's object number
    addiu t1,zero,0x04FF
    bne t2,t1,gk_go               # he is no carpet rider
    lw t2,8(t4)
    lw t2,0(t2)
    bne t2,t1,gk_go               # player 1's hero is none
    lw t3,4200(t5)                # 0x00351068: the game's carpet
    beq t3,zero,gk_go
    nop
    lw t2,0(t3)
    lui t1,0x0035
    ori t1,t1,0x1078
    bne t2,t1,gk_go               # not a living carpet
    lui t7,0x000E
    lw t0,0x7E58(t7)              # the carpet the second one was made for
    bne t0,t3,gk_new              # another one (a new room): count anew
    lw t9,0x7E54(t7)              # the second carpet
    beq t9,zero,gk_make
    nop
    lw t2,0(t9)
    beq t2,t1,gk_go               # it is there and alive
    nop
    b gk_make
    nop
gk_new:
    sw zero,0x7E5C(t7)
gk_make:
    lw t2,0x7E5C(t7)
    sltiu t0,t2,4
    beq t0,zero,gk_go             # never more than four tries for one carpet
    addiu t2,t2,1
    sw t2,0x7E5C(t7)
    sw t3,0x7E58(t7)
    sw zero,0x7E54(t7)
    addiu sp,sp,-48
    sd ra,0(sp)
    sd t3,8(sp)
    lw t2,0x70(t6)                # the twin's place
    sw t2,16(sp)
    lw t2,0x74(t6)
    sw t2,20(sp)
    lw t2,0x78(t6)
    sw t2,24(sp)
    lw t2,0x7C(t6)
    sw t2,28(sp)
    mtc1 zero,f12
    addiu a0,zero,0x0168          # the carpet's object number
    jal 0x0016F000                # the game's own "make an object"
    addiu a1,sp,16
    lui t7,0x000E
    sw v0,0x7E54(t7)
    ld t3,8(sp)
    lui t5,0x0035
    sw t3,4200(t5)                # the first carpet stays "the carpet" (the new one's constructor wrote itself there)
    ld ra,0(sp)
    addiu sp,sp,48
gk_go:
    j TICK_NEXT
    move a0,zero
gc_upd:                           # the word at 0x00350FF8 (was 0x001B2DB8): state 19's routine. a1 = the carpet
    lui t7,0x000E
    lw t6,0x7E54(t7)
    bne a1,t6,gu_go               # the game's own carpet: as the game
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    beq t6,zero,gu_go
    lui t5,0x0035
    addiu sp,sp,-32
    sd ra,0(sp)
    lw t4,-5816(t5)
    sd t4,8(sp)                   # the engine's player
    jal 0x001B2DB8
    sw t6,-5816(t5)               # for this one call "the player" is the twin
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
gu_go:
    j 0x001B2DB8
    nop
gc_c1:                            # from 0x00178E1C and 0x00178E34 (was lw a0,4200(s0)): s2 = the acting hero's motion part
    lw t6,8(s2)                   # its owner: the hero
gc_cx:
    lui t7,0x0035
    lw a0,4200(t7)                # the game's carpet
    lui t5,0x000F
    lw t5,0x05CC(t5)
    bne t6,t5,gx_out              # not the twin
    lui t7,0x000E
    lw t4,0x7E54(t7)
    beq t4,zero,gx_out
    nop
    lw t3,0(t4)
    lui t2,0x0035
    ori t2,t2,0x1078
    bne t3,t2,gx_out              # not a living carpet
    nop
    move a0,t4                    # the twin's own carpet
gx_out:
    jr ra
    nop
gc_c3:                            # from 0x001B2A04 (was lw a0,4200(t7)): s1 = the hero
    b gc_cx
    move t6,s1
gc_c2:                            # from 0x00178E8C (was lui t7,0x35; the next but one instruction is lw a0,4200(t7)):
    lui t7,0x0035                 # a0 = the hero whose motion has ended. Out: t7 + 4200 = where his carpet's pointer is
    lui t5,0x000F
    lw t5,0x05CC(t5)
    bne a0,t5,g2_out              # not the twin
    lui t6,0x000E
    lw t4,0x7E54(t6)
    beq t4,zero,g2_out
    nop
    lw t3,0(t4)
    lui t2,0x0035
    ori t2,t2,0x1078
    bne t3,t2,g2_out
    nop
    ori t7,t6,0x6DEC              # 0x000E7E54 - 4200
g2_out:
    jr ra
    nop
"""


# ---- fifty-third glue, an experiment (only with --norec) ---------------------------------------------------
GN_AT = 0x000EB800
GN_END = 0x000EB840
GN_SRC = """
gn_cnt:                           # jump at 0x001BE9DC (was lbu t6,18(v0) / andi t7,t6,0xFF). v0 = the hero's record
    beq v0,zero,gn_zero
    nop
    lbu t6,18(v0)
    j 0x001BE9E4
    andi t7,t6,0xFF
gn_zero:
    j 0x001BEAC0                  # no record: no item places (the way out of the routine for a count of 0)
    daddu s3,v0,zero              # (the instruction in the delay slot of the routine's own branch)
"""


# ---- fifty-fourth glue, an experiment (only with --escape2) ------------------------------------------------
GE_AT = 0x000EB840
GE_END = 0x000EBA00
GE_SRC = """
ge_tick:                          # from 0x00138538 (the field's START look-out, each step)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,ek_go
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,ek_go
    nop
    lw t2,8(t6)
    lw t2,0(t2)                   # the twin's object number
    addiu t1,zero,0x05E9
    bne t2,t1,ek_go               # he is no escape hero
    lw t2,8(t4)
    lw t2,0(t2)
    bne t2,t1,ek_go
    lui t3,0x01C6
    ori t3,t3,0x01B0              # the handler of state 24
    lw t2,0xC(t4)
    bne t2,t3,ek_go               # the escape has not begun for player 1's hero
    nop
    addiu sp,sp,-48
    sd ra,0(sp)
    sd t6,8(sp)
    lw t2,0xC(t6)
    beq t2,t3,ek_carp             # the twin is in state 24 already
    nop
    move a0,t6
    jal 0x0016BD60                # the twin goes into state 24, as the manager does it for the hero
    addiu a1,zero,24
    ld t6,8(sp)
    lw t2,0x108(t6)
    ori t2,t2,0x1
    sw t2,0x108(t6)
    lui t7,0x000E
    sw zero,0x7E60(t7)            # a new escape: the second carpet of an older one is forgotten
    sw zero,0x7E68(t7)
ek_carp:
    lui t7,0x000E
    lw t9,0x7E60(t7)              # the second carpet
    beq t9,zero,ek_make
    nop
    lw t2,0(t9)
    lw t1,0x7E64(t7)
    bne t2,t1,ek_make             # it is gone
    lui t3,0x01C6
    ori t3,t3,0x01C0              # the handler of state 25
    lw t2,0xC(t9)
    beq t2,t3,ek_out              # alive and in state 25
    nop
    beq t2,zero,ek_out            # (no action part yet: the next step)
    move a0,t9
    sd t9,32(sp)
    jal 0x0016BD60                # the carpet's state 25, as the manager does it for the game's carpet
    addiu a1,zero,25
    ld t9,32(sp)
    lw t2,0x108(t9)
    ori t2,t2,0x1
    b ek_out
    sw t2,0x108(t9)
ek_make:
    lw t2,0x7E68(t7)
    sltiu t0,t2,3
    beq t0,zero,ek_out            # never more than three tries
    addiu t2,t2,1
    sw t2,0x7E68(t7)
    sw zero,0x7E60(t7)
    ld t6,8(sp)
    lw t2,0x70(t6)                # the twin's place
    sw t2,16(sp)
    lw t2,0x74(t6)
    sw t2,20(sp)
    lw t2,0x78(t6)
    sw t2,24(sp)
    lw t2,0x7C(t6)
    sw t2,28(sp)
    mtc1 zero,f12
    addiu a0,zero,0x05EA          # the escape's carpet
    jal 0x0016F000                # the game's own "make an object"
    addiu a1,sp,16
    beq v0,zero,ek_out
    lui t7,0x000E
    sw v0,0x7E60(t7)
    lw t2,0(v0)
    sw t2,0x7E64(t7)              # its class word: the sign that it is alive (state 25 comes at the next step)
ek_out:
    ld ra,0(sp)
    addiu sp,sp,48
ek_go:
    j TICK_NEXT
    move a0,zero
ge_upd:                           # the word at 0x00362E18 (was 0x002E1D28): state 25's routine. a1 = the carpet
    lui t7,0x000E
    lw t6,0x7E60(t7)
    bne a1,t6,eu_go               # the game's own carpet: as the game
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    beq t6,zero,eu_go
    lui t5,0x0035
    addiu sp,sp,-32
    sd ra,0(sp)
    lw t4,-5816(t5)
    sd t4,8(sp)                   # the engine's player
    jal 0x002E1D28
    sw t6,-5816(t5)               # for this one call "the player" is the twin
    ld t4,8(sp)
    lui t5,0x0035
    sw t4,-5816(t5)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
eu_go:
    j 0x002E1D28
    nop
"""


# ---- fifty-fifth glue, an experiment (only with --sidecar2) ------------------------------------------------
GZ_AT = 0x000EBA00
GZ_END = 0x000EBB00
GZ_SRC = """
gz_tick:                          # from 0x00138538 (the field's START look-out, each step)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,zk_go
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,zk_go
    nop
    lw t2,8(t6)
    lw t2,0(t2)                   # the twin's object number
    addiu t1,zero,0x0840
    bne t2,t1,zk_go               # he is no sidecar hero
    lw t2,8(t4)
    lw t2,0(t2)
    bne t2,t1,zk_go
    lui t3,0x01C6
    ori t3,t3,0x0450              # the handler of state 53 (0x01C60450, the word at 0x0034E9F8 + 4 * 53)
    lw t2,0xC(t4)
    bne t2,t3,zk_go               # the ride has not begun for player 1's hero
    lw t2,0xC(t6)
    beq t2,t3,zk_go               # the twin is in state 53 already
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    sd t6,8(sp)
    move a0,t6
    jal 0x0016BD60                # the twin goes into state 53, as the manager does it for the hero
    addiu a1,zero,53
    ld t6,8(sp)
    lw t2,0x108(t6)
    ori t2,t2,0x1
    sw t2,0x108(t6)
    ld ra,0(sp)
    addiu sp,sp,16
zk_go:
    j TICK_NEXT
    move a0,zero
"""


# ---- fifty-sixth glue, an experiment (only with --twinmake) ------------------------------------------------
GW_AT = 0x000EBB00
GW_END = 0x000EBC00
GW_SRC = """
gw_tick:                          # from 0x00138538 (the field's START look-out, each step)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    bne t6,zero,wk_go             # there is one
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player (the toy cannon is no hero of the main class: 0x00352400 is not asked)
    beq t4,zero,wk_go
    nop
    lw t2,8(t4)
    lw t2,0(t2)                   # his object number
    addiu t1,zero,0x05E9
    beq t2,t1,wk_make             # the escape hero
    addiu t1,zero,0x03C8
    beq t2,t1,wk_make             # the toy cannon
    addiu t1,zero,0x0840
    bne t2,t1,wk_go               # not the sidecar hero either
    nop
wk_make:
    lui t7,0x000E
    lw t1,0x7E6C(t7)
    bne t1,t4,wk_do               # another hero object than at the last try
    lw t9,0x7E70(t7)              # the object made at the last try
    beq t9,zero,wk_go             # (the try gave nothing: no second try for this hero)
    nop
    lw t1,0(t9)
    lw t0,0x7E74(t7)
    beq t1,t0,wk_go               # it is still there (and is not the twin: leave it)
    nop
wk_do:
    sw t4,0x7E6C(t7)
    sw zero,0x7E70(t7)
    addiu sp,sp,-48
    sd ra,0(sp)
    lwc1 f0,0x70(t4)
    lui t1,0x4270                 # 60.0
    mtc1 t1,f1
    add.s f0,f0,f1
    swc1 f0,16(sp)                # the hero's place, 60 units to the side
    lw t1,0x74(t4)
    sw t1,20(sp)
    lw t1,0x78(t4)
    sw t1,24(sp)
    lw t1,0x7C(t4)
    sw t1,28(sp)
    mtc1 zero,f12
    move a0,t2                    # the same object number
    jal 0x0016F000                # the game's own "make an object"; the build's identity rule makes it the twin
    addiu a1,sp,16
    beq v0,zero,wk_out
    lui t7,0x000E
    sw v0,0x7E70(t7)
    lw t1,0(v0)
    sw t1,0x7E74(t7)
wk_out:
    ld ra,0(sp)
    addiu sp,sp,48
wk_go:
    j TICK_NEXT
    move a0,zero
"""


# ---- fifty-seventh glue (only with --hudowner) -------------------------------------------------------------
GH_AT = 0x000EBC00
GH_END = 0x000EBD00
GH_SRC = """
gh_tick:                          # from 0x00138538 (the field's START look-out, each step)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,gh_go
    lui t5,0x0035
    lw t4,-31176(t5)              # 0x00348638: the HUD's owner (the hero the game's own gauge shows)
    bne t4,t6,gh_go               # not the twin: nothing to put right
    lw t2,-5816(t5)               # the engine's player = player 1's hero
    beq t2,zero,gh_go             # he is not there (yet): his own attach comes
    nop
    beq t2,t6,gh_go
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    lw t3,0x48C(t2)               # his HP record
    beq t3,zero,gh_clr
    move a1,t2
    jal 0x0013DDC0                # the owner = player 1's hero (the "changed" mark is set: the gauge takes him)
    move a0,zero
    b gh_done
    nop
gh_clr:
    jal 0x0013DDE8                # no HP record (the toy cannon): the slot is emptied, as the game has it
    move a0,zero
gh_done:
    ld ra,0(sp)
    addiu sp,sp,16
gh_go:
    j TICK_NEXT
    move a0,zero

gh_set:                           # the call at 0x000F0D8C (m_dtor; was jal 0x0013DDC0). a0 = 0, a1 = the engine's player
    lw t7,0x48C(a1)
    beq t7,zero,gh_ret
    nop
    j 0x0013DDC0
    nop
gh_ret:
    jr ra                         # no HP record: the game's own attach does not make him the owner either
    nop
"""


# ---- fifty-eighth glue, an experiment (only with --ownabil) -------------------------------------------------
GA_AT = 0x000EBD00
GA_END = 0x000EBF40
P2A = 0x0032E390                                   # player 2's eighty ability switches (five shorts), the mark at + 10
P2A_LO = P2A - 0x00330000                          # (as an offset from lui 0x0033)
GA_SRC = """
ab_init:                          # in: t9 = the hero's record. No mark: player 2's switches are made = the hero's
    lui t8,0x0033
    lhu t0,@MARK@(t8)
    addiu t1,zero,0x5032
    beq t0,t1,ai_out
    addiu t2,t9,0x54              # the list
    addiu t8,t8,@BITS@
    addiu t3,zero,5
ai_w:
    move t0,zero
    addiu t1,zero,16
ai_b:
    lhu t4,0(t2)
    srl t0,t0,1
    andi t4,t4,0x8000
    or t0,t0,t4                   # the first place of the sixteen ends in bit 0
    addiu t1,t1,-1
    addiu t2,t2,2
    bgtz t1,ai_b
    nop
    sh t0,0(t8)
    addiu t3,t3,-1
    addiu t8,t8,2
    bgtz t3,ai_w
    nop
    addiu t1,zero,0x5032
    sh t1,0(t8)                   # the mark
ai_out:
    jr ra
    nop

ab_view:                          # jump in glue 48's hero path (was sw t3,0x30(t6); its delay slot: sw t6,0x244(a0)). t6 = T, a1 = the hero's record
    sw t3,0x30(t6)
    addiu sp,sp,-16
    sd ra,0(sp)
    jal ab_init
    move t9,a1
    lui t8,0x0033
    addiu t8,t8,@BITS@
    addiu t2,t6,0x54              # T's list
    addiu t3,zero,5
av_w:
    lhu t0,0(t8)                  # sixteen switches of player 2's, the first place in bit 0
    addiu t1,zero,16
av_b:
    lhu t4,0(t2)
    andi t4,t4,0x7FFF
    beq t4,zero,av_n              # an empty place stays empty
    andi t5,t0,1
    sll t5,t5,15
    or t4,t4,t5
av_n:
    sh t4,0(t2)
    srl t0,t0,1
    addiu t1,t1,-1
    addiu t2,t2,2
    bgtz t1,av_b
    nop
    addiu t3,t3,-1
    addiu t8,t8,2
    bgtz t3,av_w
    nop
    ld ra,0(sp)
    addiu sp,sp,16
    j 0x001A1214                  # the end of glue 48's tl_use
    daddu s1,t6,zero

ab_swap:                          # from the end of glue 49's ow_swap (was jr ra): the hero's switches and player 2's change places
    lui t5,0x000E
    lw t9,0x7E28(t5)              # the hero's record
    beq t9,zero,as_out
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    jal ab_init
    nop
    ld ra,0(sp)
    addiu sp,sp,16
    lui t8,0x0033
    addiu t8,t8,@BITS@
    addiu t2,t9,0x54
    addiu t3,zero,5
aw_w:
    lhu t0,0(t8)
    move t5,zero
    addiu t1,zero,16
aw_b:
    lhu t4,0(t2)
    srl t5,t5,1
    andi t6,t4,0x8000
    or t5,t5,t6                   # the hero's switch, collected
    andi t4,t4,0x7FFF
    beq t4,zero,aw_n              # an empty place has no switch
    andi t6,t0,1
    sll t6,t6,15
    or t4,t4,t6
aw_n:
    sh t4,0(t2)
    srl t0,t0,1
    addiu t1,t1,-1
    addiu t2,t2,2
    bgtz t1,aw_b
    nop
    sh t5,0(t8)
    addiu t3,t3,-1
    addiu t8,t8,2
    bgtz t3,aw_w
    nop
as_out:
    jr ra
    nop

ab_add:                           # jump at 0x00188B90 (was or t7,t5,a1 [now its delay slot] / jr ra / sh t7,4(a0)). t6 = the place, a1 = on << 15
    sh t7,4(a0)
    sll t0,t6,1
    subu t0,a0,t0
    addiu t0,t0,-0x50             # the record the ability went into
    lui t5,0x000E
    lw t1,0x7E28(t5)              # the hero's record
    bne t0,t1,aa_out
    lw t2,0x7E24(t5)              # (player 2's menu is open: the list holds his switches; nothing is given then)
    bne t2,zero,aa_out
    lw t1,0x7E20(t5)              # the record the twin's view T shows
    bne t1,t0,aa_nt
    ori t1,t5,0x7D00              # T
    sll t3,t6,1
    addu t1,t1,t3
    sh t7,0x54(t1)                # the view has the new ability at once, with the switch the game gave
aa_nt:
    lui t8,0x0033
    lhu t1,@MARK@(t8)
    addiu t2,zero,0x5032
    bne t1,t2,aa_out              # his switches are not made yet: they will be made from the hero's
    srl t3,t6,4                   # which of the five shorts
    sll t3,t3,1
    addu t8,t8,t3
    lhu t0,@BITS@(t8)
    andi t4,t6,15
    addiu t1,zero,1
aa_m:
    beq t4,zero,aa_m2
    nop
    sll t1,t1,1
    b aa_m
    addiu t4,t4,-1
aa_m2:
    nor t2,t1,zero
    and t0,t0,t2
    beq a1,zero,aa_st
    nop
    or t0,t0,t1
aa_st:
    sh t0,@BITS@(t8)
aa_out:
    jr ra
    nop
""".replace("@MARK@", str(P2A_LO + 10)).replace("@BITS@", str(P2A_LO))


# ---- fifty-ninth glue (only with --onevictim) ---------------------------------------------------------------
GK_AT = 0x000EBF40
GK_END = 0x000EC000
GK_SRC = """
gk_cap:                           # jump at 0x00180378, in front of tg_cap. a0 = the captor's motion part, a1 = the victim, a2 = the move
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,gk_go             # one hero: as before
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player = player 1's hero
    bne t4,t6,gk_h
    nop
    lw t4,0x2400(t5)              # (the pointer stands on the twin for a moment: the main class's last hero)
gk_h:
    beq t4,zero,gk_go
    nop
    beq a1,t6,gk_other            # the victim is the twin: the other hero is player 1's
    move t3,t4
    bne a1,t4,gk_go               # the victim is no hero
    move t3,t6
gk_other:                         # t3 = the other hero
    lui t2,0x0033
    lhu t2,-17696(t2)             # 0x0032BAE0: the world and the room
    addiu t1,zero,0x0908
    beq t2,t1,gk_go               # Shan-Yu's room: the fiftieth glue's pairs rule there
    lw t2,0x154(a1)               # the victim's action
    andi t2,t2,0xFFFC
    addiu t1,zero,0x00FC
    beq t2,t1,gk_go               # the victim is held already (FC .. FF): the capture is his
    lw t2,0x154(t3)               # the other hero's action
    andi t2,t2,0xFFFC
    bne t2,t1,gk_go               # the other hero is not held: the capture is the victim's
    lw t2,0x240(t3)               # the captor's word the other hero was held with
    lw t0,0(a0)
    bne t2,t0,gk_go               # another captor holds him
    nop
    move a1,t3                    # THE SAME CAPTOR HOLDS THE OTHER HERO: the capture goes on with him
gk_go:
    j CAP_NEXT
    nop
"""


# ---- sixtieth glue (only with --holdwatch) ------------------------------------------------------------------
GY_AT = 0x000EC000
GY_END = 0x000EC100
GY_LIMIT = 1800                                    # steps of one and the same captured motion before the hero is let go
GY_SRC = """
gy_tick:                          # from 0x00138538 (the field's START look-out, each step)
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    lui t5,0x0035
    lw a0,-5816(t5)               # the engine's player = player 1's hero
    lui s0,0x000E
    jal gy_one
    ori s0,s0,0x7E78              # his two words
    lui t7,0x000F
    lw a0,0x05CC(t7)              # the twin
    jal gy_one
    addiu s0,s0,8
    ld s0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,32
    j TICK_NEXT
    move a0,zero

gy_one:                           # a0 = a hero (or 0), s0 = his two words: the captured motion seen, the steps it has lasted
    beq a0,zero,gy_clr
    nop
    lw t2,0x154(a0)
    andi t2,t2,0xFFFF
    andi t1,t2,0xFFFC
    addiu t0,zero,0x00FC
    bne t1,t0,gy_clr              # he is in no captured motion
    lw t3,0(s0)
    bne t3,t2,gy_new              # another captured motion than at the step before
    lw t4,4(s0)
    addiu t4,t4,1
    slti t1,t4,@LIMIT@
    bne t1,zero,gy_keep
    sw t4,4(s0)
    sw zero,4(s0)                 # ONE AND THE SAME captured motion for all these steps: nobody ends it. He is let go
    addiu sp,sp,-16
    sd ra,0(sp)
    sd a0,8(sp)
    mtc1 zero,f12
    mtc1 zero,f13
    addiu a0,a0,320
    jal 0x0017EFA0                # "no motion": the captured motion ends
    move a1,zero
    ld a0,8(sp)
    jal 0x0016BD60                # "go idle": his action is ended the game's own way
    move a1,zero
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
gy_new:
    sw t2,0(s0)
    jr ra
    sw zero,4(s0)
gy_clr:
    sw zero,0(s0)
    jr ra
    sw zero,4(s0)
gy_keep:
    jr ra
    nop
""".replace("@LIMIT@", str(GY_LIMIT))


# ---- sixty-first glue (only with --itemsync) ----------------------------------------------------------------
GI_AT = 0x000EC100
GI_END = 0x000EC140
GI_SRC = """
gi_sync:                          # jump at 0x001BE9DC, in front of gn_cnt. v0 = the record the item list is built from
    lui t7,0x000E
    ori t6,t7,0x7D00              # the twin's view T
    bne v0,t6,gi_go
    lw t5,0x7E20(t7)              # the record T shows
    beq t5,zero,gi_go
    addiu t4,zero,8               # eight words: the item places and the eight words behind them (+ 0x34 .. + 0x53)
gi_l:
    lw t3,0x34(t5)
    sw t3,0x34(t6)
    addiu t4,t4,-1
    addiu t5,t5,4
    bgtz t4,gi_l
    addiu t6,t6,4
gi_go:
    j GN_CNT
    nop
"""


# ---- sixty-second glue (only with --ownitems) ---------------------------------------------------------------
GO_AT = 0x000EC140
GO_END = 0x000EC700
P2B = 0x0032E35C                                   # King Mickey's record: player 2's own things live in its places
P2PL = P2B + 0x14 - 0x00330000                     # his eight item places (bytes); + 8: his eight refill entries
P2ST = P2B + 0x24 - 0x00330000                     # his stock of the fight items 1 .. 7 (bytes)
P2SC = P2B + 0x2C - 0x00330000                     # his four shortcuts (shorts)
P2MARK = P2B + 0x44 - 0x00330000                   # 0x5033 = his item things are made
BAG_LO = 0x0032F0B0 - 0x00330000                   # the bag (save + 0x3580); its first seven bytes = the fight items
SC_LO = 0x0032F228 - 0x00330000                    # the four shortcuts (save + 0x36F8)
GO_SRC = """
oi_init:                          # no mark: player 2's item places, refill entries, stock and shortcuts are made = player 1's. Out: t7 = 1 when they are there
    lui t8,0x0033
    lhu t0,@MARK@(t8)
    addiu t1,zero,0x5033
    beq t0,t1,oi_ok
    lui t9,0x0033
    addiu t9,t9,-8160             # the hero's record (Sora's; Roxas has the same one)
    addiu t2,zero,8
    addiu t3,t8,@PL@
    addiu t4,t9,0x34
oi_c1:
    lhu t0,0(t4)                  # a place
    sb t0,0(t3)
    lhu t0,0x10(t4)               # its refill entry
    sb t0,8(t3)
    addiu t2,t2,-1
    addiu t3,t3,1
    bgtz t2,oi_c1
    addiu t4,t4,2
    addiu t2,zero,7               # the stock = the bag's seven fight items
    addiu t3,t8,@ST@
    addiu t4,t8,@BAG@
oi_c2:
    lbu t0,0(t4)
    sb t0,0(t3)
    addiu t2,t2,-1
    addiu t3,t3,1
    bgtz t2,oi_c2
    addiu t4,t4,1
    lw t0,@SC@(t8)                # the four shortcuts
    sw t0,@P2SC@(t8)
    lw t0,@SC4@(t8)
    sw t0,@P2SC4@(t8)
    sh t1,@MARK@(t8)
oi_ok:
    jr ra
    addiu t7,zero,1
oi_no:
    jr ra
    move t7,zero

oi_view:                          # the twin's view T gets player 2's item places and refill entries (not while his menu is open: T is the record then)
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t9,0x000E
    lw t0,0x7E24(t9)
    bne t0,zero,ov_out
    lw t0,0x7E20(t9)              # the record T shows
    lw t1,0x7E28(t9)              # the hero's record
    bne t0,t1,ov_out              # T is another body's (King Mickey): no places of player 2's
    nop
    jal oi_init
    nop
    beq t7,zero,ov_out
    lui t8,0x0033
    lui t9,0x000E
    ori t9,t9,0x7D00              # T
    addiu t3,t8,@PL@
    addiu t2,zero,8
ov_l:
    lbu t0,0(t3)
    sh t0,0x34(t9)
    lbu t0,8(t3)
    sh t0,0x44(t9)
    addiu t2,t2,-1
    addiu t3,t3,1
    bgtz t2,ov_l
    addiu t9,t9,2
ov_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16

oi_tview:                         # jump at the end of glue 58's ab_view (was j 0x001A1214; its delay slot: s1 = T). a0 = the twin's slot
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    jal oi_view
    nop
    ld a1,16(sp)
    ld a0,8(sp)
    ld ra,0(sp)
    j 0x001A1214
    addiu sp,sp,32

oi_list:                          # jump at 0x001BE9DC (in the place of glue 61's gi_sync). v0 = the record the item list is built from
    lui t7,0x000E
    ori t6,t7,0x7D00
    bne v0,t6,ol_go
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    sd v0,8(sp)
    jal oi_view
    nop
    ld v0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,16
ol_go:
    j GN_CNT
    nop

oi_use:                           # call at 0x00176EA4 (was jal 0x0016A070: the user's character number). a0 = the user, s0 = the item
    lui t7,0x000F
    lw t6,0x05CC(t7)
    bne a0,t6,ou_game             # not the twin: the game's way
    nop
    lw t5,0x48C(a0)               # his unit slot
    beq t5,zero,ou_game
    nop
    lw t4,0x254(t5)               # whose slot: only a hero (1 = Sora, 14 = Roxas) has places of player 2's
    addiu t3,zero,1
    beq t4,t3,ou_hero
    addiu t3,zero,14
    bne t4,t3,ou_game
    nop
ou_hero:
    lui t7,0x000E
    lw t3,0x7E24(t7)
    bne t3,zero,ou_game           # (his menu is open: cannot be in a fight)
    lui t8,0x0033
    lhu t3,@MARK@(t8)
    addiu t2,zero,0x5033
    bne t3,t2,ou_game
    ori t9,t7,0x7D00              # T
    lbu t2,0x12(t9)               # the count of item places
    addiu t2,t2,-1
    bltz t2,ou_none
    addiu t3,t8,@PL@
    addu t3,t3,t2                 # from the last place down, as the game does
    sll t4,t2,1
    addu t9,t9,t4
ou_l:
    lbu t5,0(t3)
    bne t5,s0,ou_n
    nop
    sb zero,0(t3)                 # it leaves HIS place
    sh zero,0x34(t9)              # and his view
    j 0x00176EB8                  # the routine's own way out
    addiu v0,zero,1               # taken
ou_n:
    addiu t2,t2,-1
    addiu t3,t3,-1
    bgez t2,ou_l
    addiu t9,t9,-2
ou_none:
    j 0x00176EB8
    move v0,zero                  # he has none: nothing happens (as the game answers)
ou_game:
    j 0x0016A070
    nop

oi_refill:                        # call at 0x00253BDC (was jal 0x001A3710: the game fills empty places from the bag)
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x001A3710                # the places that stand in the records now (player 1's, or player 2's while his menu is open)
    nop
    jal oi_init
    nop
    beq t7,zero,or_out
    lui t8,0x0033
    lui t9,0x0033
    addiu t9,t9,-8160             # the hero's record: the count of places
    lbu t2,0x12(t9)
    blez t2,or_out
    addiu t3,t8,@PL@              # the places in the store: the OTHER player's
or_l:
    lbu t0,8(t3)                  # the refill entry
    beq t0,zero,or_n
    lbu t1,0(t3)
    bne t1,zero,or_n              # the place is not empty
    sltiu t4,t0,8
    beq t4,zero,or_n
    addu t4,t8,t0
    lbu t5,@STM1@(t4)             # his stock of that item
    blez t5,or_n
    addiu t5,t5,-1
    sb t5,@STM1@(t4)
    sb t0,0(t3)
or_n:
    addiu t2,t2,-1
    bgtz t2,or_l
    addiu t3,t3,1
    jal oi_view
    nop
or_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16

oi_swap:                          # jump at the end of glue 58's ab_swap (was jr ra): player 2's menu opens or goes
    addiu sp,sp,-16
    sd ra,0(sp)
    jal oi_init
    nop
    beq t7,zero,ow_out
    lui t8,0x0033
    lui t9,0x000E
    lw t9,0x7E28(t9)              # the hero's record
    beq t9,zero,ow_out
    addiu t2,zero,8
    addiu t3,t8,@PL@
ow_a:
    lhu t0,0x34(t9)               # the item places
    lbu t1,0(t3)
    sh t1,0x34(t9)
    sb t0,0(t3)
    lhu t0,0x44(t9)               # the refill entries
    lbu t1,8(t3)
    sh t1,0x44(t9)
    sb t0,8(t3)
    addiu t2,t2,-1
    addiu t3,t3,1
    bgtz t2,ow_a
    addiu t9,t9,2
    addiu t2,zero,7               # the stock of the seven fight items
    addiu t3,t8,@ST@
    addiu t4,t8,@BAG@
ow_b:
    lbu t0,0(t4)
    lbu t1,0(t3)
    sb t1,0(t4)
    sb t0,0(t3)
    addiu t2,t2,-1
    addiu t3,t3,1
    bgtz t2,ow_b
    addiu t4,t4,1
    lw t0,@SC@(t8)                # the four shortcuts
    lw t1,@P2SC@(t8)
    sw t1,@SC@(t8)
    sw t0,@P2SC@(t8)
    lw t0,@SC4@(t8)
    lw t1,@P2SC4@(t8)
    sw t1,@SC4@(t8)
    sw t0,@P2SC4@(t8)
ow_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16

oi_p2get:                         # in: a1 = a fight item (1 .. 7). The other player gets one too: into an empty place of his, else into his stock
    lui t8,0x0033
    lhu t3,@MARK@(t8)
    addiu t4,zero,0x5033
    bne t3,t4,pg_out
    sltiu t3,a1,8
    beq t3,zero,pg_out
    lui t9,0x000E
    lw t7,0x7E24(t9)
    bne t7,zero,pg_stock          # (player 2's menu is open: the store holds player 1's things; his stock gets it)
    lui t9,0x0033
    addiu t9,t9,-8160             # the hero's record: the count of places
    lbu t2,0x12(t9)
    blez t2,pg_stock
    addiu t3,t8,@PL@
    move t6,zero
pg_l:
    lbu t0,0(t3)
    bne t0,zero,pg_n              # not empty
    lbu t1,8(t3)
    beq t1,a1,pg_put              # empty, and kept for this item
    nop
    beq t1,zero,pg_put            # empty, and kept for nothing
    nop
pg_n:
    addiu t6,t6,1
    slt t0,t6,t2
    bne t0,zero,pg_l
    addiu t3,t3,1
pg_stock:
    addu t5,t8,a1
    lbu t6,@STM1@(t5)
    sltiu t3,t6,99
    beq t3,zero,pg_out
    addiu t6,t6,1
    jr ra
    sb t6,@STM1@(t5)
pg_put:
    sb a1,0(t3)
    lui t9,0x000E                 # the twin's view shows it at once (when it is the hero's view)
    lw t0,0x7E20(t9)
    lw t1,0x7E28(t9)
    bne t0,t1,pg_out
    ori t9,t9,0x7D00
    sll t6,t6,1
    addu t9,t9,t6
    sh a1,0x34(t9)
pg_out:
    jr ra
    nop

oi_gain:                          # call at 0x001A31FC (was jal 0x001A32C8: add to the bag). a0 = the item, a1 = 1, s2 = its table entry, 40(sp) = who called "give"
    ld t0,40(sp)
    lui t1,0x0027
    addiu t1,t1,-21504            # 0x0026AC00
    sltu t2,t0,t1
    bne t2,zero,og_w1
    addiu t1,t1,0x400             # 0x0026B000
    sltu t2,t0,t1
    bne t2,zero,og_go             # the menu moves a thing from a place into the bag: as the game
    nop
og_w1:
    lui t1,0x0019
    addiu t1,t1,-30208            # 0x00188A00
    beq t0,t1,og_go               # a place given up when the count shrinks: as the game
    lui t1,0x001E
    addiu t1,t1,-27036            # 0x001D9664
    beq t0,t1,og_go               # a leaving guest's things: as the game
    lbu t2,2(s2)                  # THE GAME GIVES A THING. Its type:
    bne t2,zero,og_eq
    addiu t3,zero,2
    addiu sp,sp,-32               # a fight item: the other player gets one too
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    jal oi_p2get
    move a1,a0
    ld a1,16(sp)
    ld a0,8(sp)
    ld ra,0(sp)
    b og_go
    addiu sp,sp,32
og_eq:
    beq t2,t3,og_two              # a Keyblade
    addiu t3,zero,14
    beq t2,t3,og_two              # an armour
    addiu t3,zero,15
    bne t2,t3,og_go               # an accessory
    nop
og_two:
    lhu t3,0x12(s2)               # its place in the bag
    lui t8,0x0033
    addu t3,t3,t8
    lbu t4,@BAG@(t3)
    sltiu t4,t4,98
    beq t4,zero,og_go
    nop
    addiu a1,zero,2               # one for each player
og_go:
    j 0x001A32C8
    nop

oi_gain2:                         # call at 0x001A3298 (was jal 0x00188A28: put into a place). a0 = the record, a1 = the item, s0 = the character number
    addiu t3,zero,1
    beq s0,t3,o2_hero
    addiu t3,zero,14
    bne s0,t3,o2_go               # a helper's place: his things are common
    nop
o2_hero:
    addiu sp,sp,-32               # the game gives the hero a fight item: the other player gets one too
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    jal oi_p2get
    nop
    ld a1,16(sp)
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,32
o2_go:
    j 0x00188A28
    nop

oi_sc:                            # jump at 0x001A3430 (was b 0x001A3410; its delay slot writes player 1's shortcut: sh t7,8(t4)). t4 = save + 0x36F0 + 2 x the place
    lui t8,0x0033
    lhu t3,@MARK@(t8)
    addiu t5,zero,0x5033
    bne t3,t5,oc_out
    lui t9,0x000E
    lw t9,0x7E24(t9)
    bne t9,zero,oc_out
    addiu t5,t8,@SCM8@            # save + 0x36F0
    subu t5,t4,t5                 # 2 x the place
    addu t5,t5,t8
    lhu t3,@P2SC@(t5)
    bne t3,zero,oc_out            # player 2's shortcut there is taken
    nop
    sh t7,@P2SC@(t5)
oc_out:
    j 0x001A3410
    nop

sc_base:                          # call at 0x001BED98 (was addiu t7,t7,-17616: the save's base; the next line adds 0x36F8). s4 = the control object
    lui t7,0x0033
    addiu t7,t7,-17616
    lui t5,0x000F
    lw t5,0x05CC(t5)              # the twin
    beq t5,zero,sb_out
    lw t4,2528(s4)                # this menu's hero
    bne t4,t5,sb_out
    lui t5,0x0033
    lhu t4,@MARK@(t5)
    addiu t3,zero,0x5033
    bne t4,t3,sb_out
    lui t3,0x000E
    lw t3,0x7E24(t3)
    bne t3,zero,sb_out
    nop
    addiu t7,t5,@P2SCB@           # so that + 0x36F8 is player 2's four shortcuts
sb_out:
    jr ra
    nop

oi_tick:                          # from 0x00138538 (each step the field looks for START): his things are made as soon as the hero's record is known
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000E
    lw t6,0x7E24(t7)
    bne t6,zero,ot_go
    nop
    jal oi_init
    nop
ot_go:
    ld ra,0(sp)
    addiu sp,sp,16
    j TICK_NEXT
    move a0,zero
""".replace("@MARK@", str(P2MARK)).replace("@PL@", str(P2PL)).replace("@STM1@", str(P2ST - 1)).replace("@ST@", str(P2ST)) \
   .replace("@P2SC4@", str(P2SC + 4)).replace("@P2SCB@", str(P2SC - 0x36F8)).replace("@P2SC@", str(P2SC)) \
   .replace("@BAG@", str(BAG_LO)).replace("@SCM8@", str(SC_LO - 8)).replace("@SC4@", str(SC_LO + 4)).replace("@SC@", str(SC_LO))

if "--ownbag" in sys.argv:                         # (the seventy-first glue: what the game gives goes into both own bags)
    GO_SRC = GO_SRC.replace("""og_eq:
    beq t2,t3,og_two              # a Keyblade
""", """og_eq:
    j 0x000E9900                  # (--ownbag) a thing that is not a fight item: the seventy-first glue's ob_gain
""")


# ---- sixty-third glue (only with --ownkey) ------------------------------------------------------------------
KB_AT = 0x000EC700
KB_END = 0x000ECF00
P2KB = P2B + 0x40 - 0x00330000                     # player 2's Keyblade (a short)
P2LW = P2B + 0x42 - 0x00330000                     # player 1's Keyblade as last seen
P2KM = P2B + 0x46 - 0x00330000                     # 0x5034 = his Keyblade is made
KB_SRC = """
kb_tick:                          # from 0x00138538 (each step the field looks for START)
    lui t9,0x000E
    lw t0,0x7E24(t9)
    bne t0,zero,kt_go             # player 2's menu is open (cannot be: the field does not look then)
    lui t8,0x0033
    lhu t2,-8160(t8)              # player 1's Keyblade now (Sora's record + 0)
    lhu t0,@KM@(t8)
    addiu t1,zero,0x5034
    beq t0,t1,kt_have
    lhu t3,@LW@(t8)
    sh t2,@KB@(t8)                # no mark: player 2's Keyblade is made = player 1's
    sh t2,@LW@(t8)
    b kt_go
    sh t1,@KM@(t8)
kt_have:
    beq t2,t3,kt_go
    nop
    sh t2,@LW@(t8)                # the story gave player 1 another Keyblade: player 2 gets the same
    sh t2,@KB@(t8)
kt_go:
    lui t7,0x0035
    lw t6,0x037C(t7)              # a story event runs: the twin's weapon is not touched now
    bne t6,zero,kt_x
    lui t7,0x0034
    lw t6,-13256(t7)              # 0x0033CC38: an event holds the camera
    bne t6,zero,kt_x
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    jal kb_fix
    nop
    ld ra,0(sp)
    addiu sp,sp,16
kt_x:
    j TICK_NEXT
    move a0,zero

kb_after:                         # jump at the end of lane E's e_wrap (0x000F03C0, was jr ra): a player object is built, the two heroes are sorted out. v0 = the new object
    addiu sp,sp,-32
    sd ra,0(sp)
    sd v0,8(sp)
    jal kb_fix                    # the twin gets HIS Keyblade now, while the room is built
    nop
    ld v0,8(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32

kb_fix:                           # each step: the twin holds HIS Keyblade as soon as its files are there
    lui t9,0x000E
    lw t0,0x7E24(t9)
    bne t0,zero,kf_out            # (player 2's menu is open)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,kf_out
    lui t8,0x0033
    lhu t5,@KM@(t8)
    addiu t4,zero,0x5034
    bne t5,t4,kf_out
    lhu t5,@KB@(t8)               # his Keyblade
    beq t5,zero,kf_out
    lhu t4,-8160(t8)
    beq t5,t4,kf_out              # the same as player 1's
    lw t3,0xAF8(t6)               # the weapon in his first hand
    beq t3,zero,kf_out
    nop
    lw t2,2560(t3)
    addiu t1,zero,2303
    beq t2,t1,kf_out              # it is bound to his own files already
    lw t2,0x48C(t6)
    beq t2,zero,kf_out
    nop
    lw t2,0x254(t2)               # a hero's body only (1 = Sora, 14 = Roxas)
    addiu t1,zero,1
    beq t2,t1,kf_h
    addiu t1,zero,14
    bne t2,t1,kf_out
    nop
kf_h:
    lw t2,0x7E90(t9)              # tried for this twin object and this Keyblade already
    bne t2,t6,kf_try
    lw t1,0x7E94(t9)
    beq t1,t5,kf_out
    nop
kf_try:
    sw t6,0x7E90(t9)
    sw t5,0x7E94(t9)
    addiu sp,sp,-64
    sd ra,0(sp)
    sd s0,8(sp)
    sd s3,16(sp)
    sd s4,24(sp)
    sd s5,32(sp)
    move s0,t6
    jal kc_set                    # his body's weapon set
    move s3,t5
    move a0,v0
    jal 0x00185890                # the weapon object for it and his Keyblade
    move a1,s3
    beq v0,zero,kf_back
    move s5,v0
    jal 0x0016E920                # its entry
    move a0,v0
    beq v0,zero,kf_back
    move a0,v0
    jal 0x0016F470                # the name of its model file
    move a1,zero
    move a0,v0
    jal 0x00170240                # in the pool with the number 2303 ...
    addiu a1,zero,2303
    beq v0,zero,kf_back
    nop
    lbu t7,1(v0)
    addiu t6,zero,3
    bne t7,t6,kf_back             # ... and loaded
    nop
    lw a0,0xAF8(s0)
    sd a0,40(sp)
    jal 0x0019C5D0                # the weapon he holds is ended as the game ends one
    nop
    move s4,v0
    jal 0x00185A28
    ld a0,40(sp)
    sw zero,0xAF8(s0)
    move a0,s0
    move a1,s5
    jal 0x00176168                # and his own is built in his hand
    move a2,zero
    bne s4,zero,kf_back
    nop
    lw a0,0xAF8(s0)
    beq a0,zero,kf_back
    nop
    lw t6,0(a0)
    lw t7,72(t6)
    jalr t7                       # (the game's last step for a new weapon)
    nop
kf_back:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s3,16(sp)
    ld s4,24(sp)
    ld s5,32(sp)
    addiu sp,sp,64
kf_out:
    jr ra
    nop

kb_swap:                          # jump at the end of glue 62's oi_swap (was jr ra): player 2's menu opens or goes
    lui t9,0x000E
    lw t9,0x7E28(t9)              # the hero's record
    beq t9,zero,kw_out
    lui t8,0x0033
    lhu t0,@KM@(t8)
    addiu t1,zero,0x5034
    beq t0,t1,kw_do
    lhu t2,0(t9)
    sh t2,@KB@(t8)                # (no mark yet: his Keyblade is made = player 1's, first)
    sh t2,@LW@(t8)
    sh t1,@KM@(t8)
kw_do:
    lhu t3,@KB@(t8)
    sh t3,0(t9)
    sh t2,@KB@(t8)
kw_out:
    jr ra
    nop

kb_tview:                         # jump at the end of glue 62's oi_tview (was j 0x001A1214): the hero's view T is made
    lui t8,0x0033
    lhu t0,@KM@(t8)
    addiu t1,zero,0x5034
    bne t0,t1,kv_go
    lui t9,0x000E
    lhu t0,@KB@(t8)
    beq t0,zero,kv_go
    nop
    sh t0,0x7D00(t9)              # the view's Keyblade is player 2's: his strength, his magic, the Keyblade's ability
kv_go:
    j 0x001A1214
    nop

kb_fact:                          # call at 0x000F0344 (lane E's e_wrap; was jal 0x00179FD0, the player factory)
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000E
    addiu t6,zero,1
    sw zero,0x7E90(t7)            # a new body: kb_fix may try again
    jal 0x00179FD0
    sw t6,0x7E88(t7)              # a player object is being built
    lui t7,0x000E
    sw zero,0x7E88(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16

kb_rec:                           # call at 0x0016F680 (was jal 0x00188FE0: the record of a character). a1 = the character number, s0 = the hand
    lui t7,0x000E
    lw t6,0x7E88(t7)
    beq t6,zero,kr_game           # no player object is being built: the game's way (file requests too)
    lui t6,0x000F
    lw t6,0x05C4(t6)              # lane E: is it player 1's hero
    bne t6,zero,kr_game
    nop
    bne s0,zero,kr_game           # the second hand: common
    addiu t6,zero,1
    beq a1,t6,kr_hero
    addiu t6,zero,14
    bne a1,t6,kr_game
    nop
kr_hero:
    lw t6,0x7E24(t7)
    bne t6,zero,kr_game           # (player 2's menu is open: the record holds his Keyblade already)
    lui t8,0x0033
    lhu t6,@KM@(t8)
    addiu t5,zero,0x5034
    bne t6,t5,kr_game
    lhu t6,@KB@(t8)
    beq t6,zero,kr_game
    lhu t5,-8160(t8)
    beq t6,t5,kr_game             # the same Keyblade as player 1's: the same files
    lui t4,0x0035
    lw t4,-9056(t4)               # the file pool's list: is a file of his Keyblade (number 2303) loaded
kr_w:
    beq t4,zero,kr_game           # no: player 1's Keyblade, whose files are there
    nop
    lw t3,0x28(t4)
    addiu t2,zero,2303
    bne t3,t2,kr_n
    lbu t3,1(t4)
    addiu t2,zero,3
    beq t3,t2,kr_own
    nop
kr_n:
    b kr_w
    lw t4,0x3C(t4)
kr_own:
    jr ra
    addiu v0,t8,@KB@              # "his record": the routine reads the first hand's weapon at + 0
kr_game:
    j 0x00188FE0
    nop

kb_req:                           # call at 0x0016ECDC (was jal 0x0016EF58: ask for a weapon's files). a0 = the weapon set, a1 = the hand, a3 = the number, s5 = the body's entry, s6 = a flag bit
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd a3,24(sp)
    sd t0,32(sp)
    jal 0x0016EF58                # the game's request (player 1's Keyblade)
    nop
    ld a1,16(sp)
    bne a1,zero,kq_out            # the second hand
    ld a3,24(sp)
    addiu t6,zero,2301
    bne a3,t6,kq_out              # not the hero's normal body (a form finds the model by its name)
    lhu t6,76(s5)                 # whose body
    addiu t5,zero,1
    beq t6,t5,kq_hero
    addiu t5,zero,14
    bne t6,t5,kq_out
    nop
kq_hero:
    lui t7,0x000E
    lw t6,0x7E24(t7)
    bne t6,zero,kq_out
    lui t8,0x0033
    lhu t6,@KM@(t8)
    addiu t5,zero,0x5034
    bne t6,t5,kq_out
    lhu a1,@KB@(t8)
    beq a1,zero,kq_out
    lhu t5,-8160(t8)
    beq a1,t5,kq_out              # the same Keyblade as player 1's: one set of files
    nop
    jal 0x00185890                # the weapon object of this body's set for player 2's Keyblade
    ld a0,8(sp)
    beq v0,zero,kq_out
    or a2,v0,s6
    ld a0,8(sp)
    move a1,zero
    addiu a3,zero,2303
    jal 0x0016EF58
    ld t0,32(sp)
kq_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48

kb_size:                          # jump at 0x001A8B20 (was j 0x0016FAB0: the sizes of the hero's and the helpers' blocks). a0 = the hero's
    beq a0,zero,kz_go
    lui t7,0x0004
    addu a0,a0,t7                 # room for a second Keyblade's model and effect file (252 KB at most)
kz_go:
    j 0x0016FAB0
    nop

kc_set:                           # out: v0 = the weapon set of the twin's body for the first hand (s0 = the twin)
    lw t6,8(s0)
    lhu v0,78(t6)
    addiu t7,zero,53
    beq v0,t7,ks_out
    nop
    lw t7,0x588(s0)
    lui t6,0x0100
    and t7,t7,t6
    beq t7,zero,ks_out
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    jal 0x001D1438                # (the game's own detour for the first hand of a form body: the base body's weapon set)
    move a0,zero
    jal 0x0016E920
    move a0,v0
    lhu v0,78(v0)
    ld ra,0(sp)
    addiu sp,sp,16
ks_out:
    jr ra
    nop

kc_menu:                          # jump at 0x002933D0 (was j wc_both). a0 = the menu's record, a1 = the character number, a2 = the hand, a3 = the new weapon item
    bne a2,zero,kc_old            # the second hand: as before (glue 33)
    lui t8,0x0033
    lhu t5,@KM@(t8)
    addiu t4,zero,0x5034
    bne t5,t4,kc_old
    addiu t4,zero,1
    beq a1,t4,kc_h
    addiu t4,zero,14
    bne a1,t4,kc_old              # another character's weapon: as before
    nop
kc_h:
    lui t7,0x000E
    lw t6,0x7E24(t7)
    bne t6,zero,kc_h2
    nop
    sh a3,@LW@(t8)                # player 1's own change of his Keyblade (not the story's)
kc_h2:
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,kc_old
    nop
    addiu sp,sp,-96
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    sd s3,32(sp)
    sd s4,40(sp)
    sd s5,48(sp)
    move s0,t6
    move s1,a0
    move s2,a1
    move s3,a3
    jal 0x0016A070                # the twin's character number
    move a0,s0
    beq v0,s2,kc_mine
    nop
    move a0,s1                    # the twin is another character (King Mickey): as before
    move a1,s2
    move a2,zero
    move a3,s3
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    ld s3,32(sp)
    ld s4,40(sp)
    ld s5,48(sp)
    addiu sp,sp,96
kc_old:
    j WC_BOTH
    nop
kc_mine:
    lw a0,0xAF8(s0)               # the twin's weapon in the first hand
    move s4,zero                  # the answer of its end (0 = the new weapon gets its method + 0x48 called)
    beq a0,zero,kc_ended
    addiu s5,zero,-1
    lw t7,0x9B4(a0)
    beq t7,zero,kc_e1
    nop
    lh s5,0(t7)
kc_e1:
    sd a0,56(sp)
    jal 0x0019C5D0                # it is ended as the game ends the hero's, BEFORE any file moves
    nop
    move s4,v0
    jal 0x00185A28
    ld a0,56(sp)
    sw zero,0xAF8(s0)
kc_ended:
    lui t7,0x000E
    lw t6,0x7E24(t7)
    bne t6,zero,kc_p2
    nop
    sw s3,0x7E8C(t7)              # PLAYER 1's MENU. His new Keyblade, for kc_load inside the game's routine
    move a0,s1
    move a1,s2
    move a2,zero
    jal 0x00175F68                # the game's routine: his hero's weapon and its files
    move a3,s3
    lui t7,0x000E
    sw zero,0x7E8C(t7)
    lui t8,0x0033
    lhu s3,@KB@(t8)               # the twin's weapon is built again with HIS Keyblade
    b kc_build
    move s2,zero                  # (the game's routine has done its last step itself)
kc_p2:
    jal 0x001703A8                # PLAYER 2's MENU. Only the twin's weapon changes. His old own files go
    addiu a0,zero,2303
    lui t8,0x0033
    lhu t6,@KB@(t8)               # player 1's Keyblade (it waits in the store while player 2's menu is open)
    beq t6,s3,kc_ld               # the same Keyblade now: one set of files
    nop
    jal kc_set
    nop
    sd v0,64(sp)
    move a0,v0
    jal 0x00185890                # the weapon object of the twin's body for the new Keyblade
    move a1,s3
    beq v0,zero,kc_ld
    move a2,v0
    ld a0,64(sp)
    move a1,zero
    addiu a3,zero,2303
    jal 0x0016EF58                # its files: behind player 1's, in the hero's block
    move t0,s5
kc_ld:
    jal 0x00170888                # load now
    move a0,s1
    addiu s2,zero,1               # (the routine's last step is still to do)
kc_build:
    beq s3,zero,kc_last
    nop
    jal kc_set
    nop
    move a0,v0
    jal 0x00185890
    move a1,s3
    beq v0,zero,kc_last
    move a1,v0
    move a0,s0
    jal 0x00176168                # the twin's weapon is built in his hand
    move a2,zero
    bne s4,zero,kc_last
    nop
    lw a0,0xAF8(s0)
    beq a0,zero,kc_last
    nop
    lw t6,0(a0)
    lw t7,72(t6)
    jalr t7                       # (the game's last step for a new weapon)
    nop
kc_last:
    beq s2,zero,kc_out
    nop
    jal 0x00103B38                # (the end of the game's routine)
    nop
    beq v0,zero,kc_out
    nop
    jal 0x001617D8
    nop
kc_out:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    ld s3,32(sp)
    ld s4,40(sp)
    ld s5,48(sp)
    jr ra
    addiu sp,sp,96

kb_ctor:                          # call at 0x00176204 (was jal 0x00185468: the weapon object's constructor). a1 = the weapon's entry, a2 = the hero, t0 = the hand, t1 = the files' number
    bne t0,zero,kx_go             # the second hand
    addiu t6,zero,2301
    bne t1,t6,kx_go
    lui t7,0x000F
    lw t6,0x05CC(t7)
    beq a2,t6,kx_twin             # the twin (a change in the menu)
    lui t7,0x000E
    lw t6,0x7E88(t7)              # or the twin while he is built
    beq t6,zero,kx_go
    lui t6,0x000F
    lw t6,0x05C4(t6)
    bne t6,zero,kx_go
    nop
kx_twin:
    addiu sp,sp,-64
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd a2,24(sp)
    sd a3,32(sp)
    sd t0,40(sp)
    sd t1,48(sp)
    move a0,a1
    jal 0x0016F470                # the name of the weapon's model file
    move a1,zero
    move a0,v0
    jal 0x00170240                # is it in the pool with the number 2303 (player 2's own Keyblade)
    addiu a1,zero,2303
    ld t1,48(sp)
    beq v0,zero,kx_r
    nop
    addiu t1,zero,2303            # yes: the weapon binds to those files
kx_r:
    ld t0,40(sp)
    ld a3,32(sp)
    ld a2,24(sp)
    ld a1,16(sp)
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,64
kx_go:
    j 0x00185468
    nop

kc_load:                          # call at 0x0017607C (was jal 0x00170888: load now, inside the game's weapon change). a0 = the menu's record, s0 = the weapon set, s5 = a value of the old weapon
    lui t7,0x000E
    lw t6,0x7E8C(t7)              # player 1's new Keyblade (0 = not his menu's change of the first hand with a twin there)
    beq t6,zero,kl_go
    lui t8,0x0033
    lhu a1,@KB@(t8)               # player 2's Keyblade
    beq a1,zero,kl_go
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    bne a1,t6,kl_ask
    nop
    jal 0x001703A8                # both hold the same Keyblade now: player 2's own files go
    addiu a0,zero,2303
    b kl_r
    nop
kl_ask:
    jal 0x00185890                # another one: its files are asked for (again; they move when player 1's files change their size)
    move a0,s0
    beq v0,zero,kl_r
    move a2,v0
    move a0,s0
    move a1,zero
    addiu a3,zero,2303
    jal 0x0016EF58
    move t0,s5
kl_r:
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,32
kl_go:
    j 0x00170888
    nop
""".replace("@KB@", str(P2KB)).replace("@LW@", str(P2LW)).replace("@KM@", str(P2KM))


# ---- sixty-fourth glue (only with --bindname) ---------------------------------------------------------------
BN_AT = 0x000ECF00
BN_END = 0x000ECF40
BN_SRC = """
bn_find:                          # calls at 0x001A9238 / 0x001A9288 (were jal 0x001708F8). a0 = the file's name, a1 = the number
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    jal 0x001708F8
    nop
    bne v0,zero,bn_out
    nop
    ld a0,8(sp)
    jal 0x001708F8                # not there with this number: by its name alone
    addiu a1,zero,-1
bn_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
"""


# ---- sixty-fifth glue (only with --holdpair) ----------------------------------------------------------------
# ---- sixty-seventh glue (only with --trickguard) -------------------------------------------------------------
LT_AT = 0x000EE400
LT_END = 0x000EE4C0
LT_SRC = """
lt_dmg:                           # the script call (2,8) "is this damage a reaction": a0 = the call's slot (in: the damage, out: 0 / 1)
    lui t7,0x0035
    lw t0,-10076(t7)              # the running script (0x0034D8A4)
    beq t0,zero,lt_go
    nop
    lw t1,56(t0)                  # its object
    beq t1,zero,lt_go
    nop
    lw t2,8(t1)
    beq t2,zero,lt_go
    nop
    lw t2,0(t2)                   # its object number
    xori t3,t2,0x05F8             # Luxord
    beq t3,zero,lt_lux
    xori t3,t2,0x09C8             # Data Luxord
    bne t3,zero,lt_go
    nop
lt_lux:
    lw t4,0x140(t1)               # the word a hero in his hold carries
    beq t4,zero,lt_go
    nop
    lw t5,0x2400(t7)              # player 1's hero
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    addiu t8,zero,2
lt_hero:
    beq t5,zero,lt_next
    nop
    lw t2,0x160(t5)
    andi t2,t2,0x4000             # in a captured motion
    beq t2,zero,lt_next
    nop
    lw t2,0x240(t5)
    bne t2,t4,lt_next             # not this Luxord's
    nop
    jr ra                         # a hero stands in Luxord's trick: no reaction, Luxord's act goes on
    sw zero,0(a0)
lt_next:
    addiu t8,t8,-1
    bne t8,zero,lt_hero
    daddu t5,t6,zero
lt_go:
    j 0x0018F4C0                  # the game's routine
    nop
"""

# ---- sixty-eighth glue (only with --holdpads) ----------------------------------------------------------------
PM_AT = 0x000EE4C0
PM_END = 0x000EE6C0
PM_SRC = """
pm_pad:                           # the call at 0x00167E90 (the controller task's update of record 1; a0 = record 1)
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,0x000E
    lw t6,0x7F80(t7)              # were the two records one for a hold at the last frame?
    beq t6,zero,pm_go
    nop
    ld t5,0x7F88(t7)              # then record 1 gets controller 2's own "held" word back first
    sd t5,0(a0)
pm_go:
    jal PM_NEXT                   # the game's update of record 1 (behind the other glues of this call)
    nop
    lui t7,0x000E
    lw t0,0x7EA0(t7)              # the two heroes of a hold's pair (the sixty-fifth glue)
    lw t1,0x7EA4(t7)
    beq t0,zero,pm_off
    nop
    beq t1,zero,pm_off
    nop
    lw t2,0x160(t0)
    lw t3,0x160(t1)
    and t2,t2,t3
    andi t2,t2,0x4000
    beq t2,zero,pm_off            # not both held
    lui t5,0x000F
    lw t2,0x2638(t5)
    bne t2,zero,pm_off            # the twenty-sixth glue has made the records one itself at this frame
    lui t6,0x0035
    addiu t6,t6,-10560            # record 0 (0x0034D6C0); record 1 is 0x60 further
    addiu t9,zero,-3              # every button but START (0x2): each player's START stays his own
    ld t0,0(t6)                   # held, controller 1
    ld t1,0x60(t6)                # held, controller 2
    sd t0,0x2640(t5)              # (kept for gm_pre)
    sd t1,0x7F88(t7)              # (kept for pm_pad)
    or t2,t0,t1
    and t2,t2,t9                  # held by either
    lw t3,0x7F80(t7)
    bne t3,zero,pm_have
    ld t3,0x7F90(t7)              # (what either held at the last frame)
    ld t4,8(t6)                   # the first frame: pressed and released of both
    ld t8,0x68(t6)
    or t4,t4,t8
    and t4,t4,t9
    ld t8,0x10(t6)
    ld t3,0x70(t6)
    or t8,t8,t3
    b pm_store
    and t8,t8,t9
pm_have:
    nor t4,t3,zero
    and t4,t4,t2                  # pressed = held now and not before
    nor t8,t2,zero
    and t8,t8,t3                  # released = held before and not now
pm_store:
    sd t2,0x7F90(t7)
    sd t2,0x2648(t5)
    andi t0,t0,2
    or t0,t0,t2
    sd t0,0(t6)                   # held
    andi t1,t1,2
    or t1,t1,t2
    sd t1,0x60(t6)
    ld t0,8(t6)                   # pressed
    andi t0,t0,2
    or t0,t0,t4
    sd t0,8(t6)
    ld t0,0x68(t6)
    andi t0,t0,2
    or t0,t0,t4
    sd t0,0x68(t6)
    ld t0,0x10(t6)                # released
    andi t0,t0,2
    or t0,t0,t8
    sd t0,0x10(t6)
    ld t0,0x70(t6)
    andi t0,t0,2
    or t0,t0,t8
    sd t0,0x70(t6)
    ld t0,0x18(t6)                # repeat: of either
    ld t1,0x78(t6)
    or t4,t0,t1
    and t4,t4,t9
    andi t0,t0,2
    or t0,t0,t4
    sd t0,0x18(t6)
    andi t1,t1,2
    or t1,t1,t4
    sd t1,0x78(t6)
    addiu t3,zero,1
    sw t3,0x7F80(t7)
    sw t3,0x2638(t5)              # gm_pre gives record 0 its own held word back at the next frame
    lw t0,0x3C(t6)                # the sticks that move a hero (record + 0x30: x, y, 0, strength): their strengths
    lw t1,0x9C(t6)
    bne t0,zero,pm_l1
    nop
    ld t2,0x90(t6)                # controller 1's is at rest: it takes controller 2's
    ld t3,0x98(t6)
    sd t2,0x30(t6)
    b pm_ret
    sd t3,0x38(t6)
pm_l1:
    bne t1,zero,pm_ret
    nop
    ld t2,0x30(t6)                # controller 2's is at rest: it takes controller 1's
    ld t3,0x38(t6)
    sd t2,0x90(t6)
    b pm_ret
    sd t3,0x98(t6)
pm_off:
    sw zero,0x7F80(t7)
pm_ret:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""

# ---- sixty-ninth glue (only with --ownwallet) ----------------------------------------------------------------
WW_AT = 0x000ED920
WW_END = 0x000EDB00                                # (0x000EDB00 .. 0x000EDC00: the seventieth glue)
WW_P2 = 0x0032E3A4 - 0x00330000                    # player 2's wallet: King Mickey's record + 0x48
WW_MARK = 0x0032E3A8 - 0x00330000                  # its mark 0x5035: King Mickey's record + 0x4C
WW_SRC = """
ww_cmd:                           # the entry of 0x00178AE8 (a0 = a hero): he runs a green command
    lui t7,0x000E
    sw a0,0x7FA0(t7)              # the hero
    lui t6,0x0035
    lw t6,-11076(t6)              # the game's counter (0x0034D4BC)
    sw t6,0x7FA4(t7)
    addiu sp,sp,-16               # the two instructions that sat at 0x00178AE8
    j 0x00178AF0
    addiu t7,zero,32

ww_sstart:                        # the shop mode's start (the word at 0x0033CBA0; was 0x00105C68), a0 = the shop
    lui t7,0x000E
    addiu t0,zero,1               # player 1's shop, unless:
    lui t6,0x000F
    lw t6,0x05CC(t6)              # the twin
    beq t6,zero,wss_set
    lw t5,0x7FA0(t7)              # the twin ran the last green command,
    bne t5,t6,wss_set
    lui t4,0x0035
    lw t4,-11076(t4)
    lw t3,0x7FA4(t7)
    subu t4,t4,t3
    sltiu t4,t4,600               # less than 600 steps ago,
    beq t4,zero,wss_set
    lw t2,0x7E24(t7)              # his menu things are not in already,
    bne t2,zero,wss_set
    lw t2,0x7E28(t7)              # and the hero's record is noted
    beq t2,zero,wss_set
    nop
    addiu t0,zero,2
wss_set:
    sw t0,0x7FA8(t7)              # whose shop
    addiu t1,zero,2
    bne t0,t1,wss_go
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    sd a0,8(sp)
    addiu t1,zero,1
    sw t1,0x7E24(t7)              # his menu things go in (glue 49's ms_tick puts them back at the field's next step)
    jal OW_SWAP
    nop
    jal OW_LOAD
    nop
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,16
wss_go:
    j 0x00105C68
    nop

ww_swap:                          # the end of glue 63's kb_swap (was jr ra): player 2's menu things go in or out
    lui t6,0x0033
    lhu t5,@WM@(t6)
    addiu t4,zero,0x5035
    beq t5,t4,wsw_do
    lw t3,-8336(t6)               # player 1's wallet (0x0032DF70)
    sw t3,@WW@(t6)                # (no mark yet: his wallet = player 1's)
    sh t4,@WM@(t6)
wsw_do:
    lw t3,-8336(t6)
    lw t2,@WW@(t6)
    sw t2,-8336(t6)               # the two wallets change places
    jr ra
    sw t3,@WW@(t6)

ww_add:                           # the entry of 0x00242500 (a0 = munny): the game gives munny
    lui t7,0x000E
    lw t6,0x7FA8(t7)
    bne t6,zero,wa_go             # a shop is open: a sale is the seller's alone
    lw t6,0x7E24(t7)
    bne t6,zero,wa_go             # (his menu things are in: as the game)
    lui t6,0x0033
    lhu t5,@WM@(t6)
    addiu t4,zero,0x5035
    bne t5,t4,wa_go               # (no wallet yet: the tick makes it = player 1's, this munny included)
    lw t3,@WW@(t6)
    addu t3,t3,a0                 # MUNNY THE GAME GIVES GOES TO BOTH
    lui t2,0x000F
    ori t2,t2,0x423F              # 999,999
    sltu t1,t2,t3
    movn t3,t2,t1
    sw t3,@WW@(t6)
wa_go:
    addiu sp,sp,-16               # the two instructions that sat at 0x00242500
    j 0x00242508
    sd s0,0(sp)

ww_tick:                          # from 0x00138538 (each step of the field)
    lui t7,0x000E
    sw zero,0x7FA8(t7)            # the field runs: no shop is open
    lw t6,0x7E24(t7)
    bne t6,zero,wt_go             # (his menu things are in: not now)
    lui t6,0x0033
    lhu t5,@WM@(t6)
    addiu t4,zero,0x5035
    beq t5,t4,wt_go
    lw t3,-8336(t6)
    sw t3,@WW@(t6)                # no mark yet (a new game, an older save): his wallet = player 1's
    sh t4,@WM@(t6)
wt_go:
    j TICK_NEXT
    nop
"""

# ---- seventieth glue (only with --shoppad) ------------------------------------------------------------------
SPP_AT = 0x000EDB00
SPP_END = 0x000EDC00
SPP_SRC = """
sp_inst:                          # from 0x00167E90 (the controller task, every frame): first, the shop module's getter call
    lui t7,0x01F2
    lhu t6,-32748(t7)             # 0x01F18014: which module is in memory (0x606E = the shop)
    ori t5,zero,0x606E
    bne t6,t5,spi_go
    nop
    lw t4,-21872(t7)              # 0x01F1AA90: still the game's call (jal 0x00167F18: logical controller 0 only)?
    lui t3,0x0C05
    ori t3,t3,0x9FC6
    bne t4,t3,spi_go
    lui t3,0x0C03
    ori t3,t3,0xD1D0              # jal 0x000F4740: the second glue's pad_both (both controllers)
    sw t3,-21872(t7)
spi_go:
    j SPP_NEXT
    nop
"""

# ---- seventy-first glue (only with --ownbag) -----------------------------------------------------------------
OB_A_AT = 0x000EE260                               # ob_get, ob_put, ob_swap
OB_A_END = 0x000EE400
OB_T_AT = 0x000EE6C0                               # ob_tab: the 158 bag places (halfwords)
OB_T_END = 0x000EE800
OB_B_AT = 0x000EB300                               # ob_tick
OB_B_END = 0x000EB400
OB_C_AT = 0x000E9900                               # ob_gain (glue 62's og_eq jumps here)
OB_C_END = 0x000E9A00
OB_P2 = 0x0032E3D0 - 0x00330000                    # player 2's bag: King Mickey's ability places 16 .. 79
OB_MARK = 0x0032E3AA - 0x00330000                  # its mark 0x5036: King Mickey's record + 0x4E
OB_BAG = 0x0032F0B0 - 0x00330000                   # the game's bag (save + 0x3580)


def ob_table():
    """The 158 bag places: the 60 materials (type 16), then the Keyblades (2), armours (14), accessories (15), each by id."""
    d = (ROOT / "local" / "extract" / "kh2" / "03system.bin").read_bytes()
    cnt = struct.unpack_from("<I", d, 4)[0]
    for i in range(cnt):
        _typ, name, off, _size = struct.unpack_from("<I4sII", d, 16 + 16 * i)
        if name.rstrip(b"\0") == b"item":
            break
    else:
        raise SystemExit("03system.bin has no item table")
    _ver, n = struct.unpack_from("<II", d, off)
    by = {}
    for k in range(n):
        e = struct.unpack_from("<HBBBBHHHHHHHHBB", d, off + 8 + 24 * k)
        by.setdefault(e[1], []).append((e[0], e[11]))
    places = [pl for t in (16, 2, 14, 15) for _iid, pl in sorted(by[t])]
    assert len(places) == 158 and len(set(places)) == 158 and max(places) < 0x138, (len(places), len(set(places)))
    return places


OB_A_SRC = """
ob_get:                           # a0 = a number (0 .. 157): v0 = player 2's count of it
    sltiu t0,a0,60
    beq t0,zero,obg_g
    lui t1,0x0033
    sll t0,a0,1
    addu t0,t0,t1
    jr ra
    lbu v0,@P2@(t0)               # a material: the low byte of place a0
obg_g:
    addiu t0,a0,-60               # gear number g: place g / 2, its high byte
    srl v0,t0,1
    sll v0,v0,1
    addu v0,v0,t1
    lbu v0,@P2H@(v0)
    andi t0,t0,1
    bne t0,zero,obg_lo
    nop
    srl v0,v0,3
obg_lo:
    jr ra
    andi v0,v0,7

ob_put:                           # a0 = a number, a1 = player 2's count of it (made 0 .. 99 / 0 .. 7)
    sltiu t0,a0,60
    beq t0,zero,obp_g
    lui t1,0x0033
    sltiu t0,a1,100
    bne t0,zero,obp_m
    nop
    addiu a1,zero,99
obp_m:
    sll t0,a0,1
    addu t0,t0,t1
    jr ra
    sb a1,@P2@(t0)
obp_g:
    sltiu t0,a1,8
    bne t0,zero,obp_g1
    nop
    addiu a1,zero,7
obp_g1:
    addiu t0,a0,-60
    srl t2,t0,1
    sll t2,t2,1
    addu t2,t2,t1
    lbu t3,@P2H@(t2)              # 0x40 | A << 3 | B
    andi t0,t0,1
    bne t0,zero,obp_b
    nop
    andi t3,t3,0x47               # A is this one
    sll a1,a1,3
    b obp_w
    or t3,t3,a1
obp_b:
    andi t3,t3,0x78               # B is this one
    or t3,t3,a1
obp_w:
    ori t3,t3,0x40
    jr ra
    sb t3,@P2H@(t2)

ob_swap:                          # the end of the sixty-ninth glue's ww_swap (was jr ra): player 2's menu things go in or out
    lui t9,0x0033
    lhu t8,@MK@(t9)
    addiu t7,zero,0x5036
    bne t8,t7,obs_ret             # no own bag yet
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    move s0,zero                  # the number
obs_l:
    lui t6,%hi(OB_TAB)
    addiu t6,t6,%lo(OB_TAB)
    sll t5,s0,1
    addu t6,t6,t5
    lhu s1,0(t6)                  # its place in the bag
    lui t6,0x0033
    addu s1,s1,t6                 # (its count: @BAG@(s1))
    lui t5,0x000E
    lw t7,0x7FAC(t5)
    bne t7,zero,obs_o
    addu t4,t5,s0
    lbu t3,@BAG@(s1)              # IN: player 1's count waits in the buffer,
    sb t3,0x7C40(t4)
    jal ob_get
    move a0,s0
    b obs_n
    sb v0,@BAG@(s1)               # player 2's count is in the bag
obs_o:
    lbu a1,@BAG@(s1)              # OUT: the bag's count is player 2's,
    jal ob_put
    move a0,s0
    lui t5,0x000E
    addu t4,t5,s0
    lbu t3,0x7C40(t4)
    sb t3,@BAG@(s1)               # player 1's comes back
obs_n:
    addiu s0,s0,1
    sltiu t0,s0,158
    bne t0,zero,obs_l
    nop
    lui t5,0x000E
    lw t7,0x7FAC(t5)
    xori t7,t7,1
    sw t7,0x7FAC(t5)              # in <-> out
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    addiu sp,sp,32
obs_ret:
    jr ra
    nop
"""

OB_B_SRC = """
ob_tick:                          # from 0x00138538 (the field's step): no own bag yet: his bag = player 1's
    lui t9,0x0033
    lhu t8,@MK@(t9)
    addiu t7,zero,0x5036
    beq t8,t7,obt_go
    lui t6,0x000E
    lw t6,0x7E24(t6)              # (his menu things are in: not now)
    bne t6,zero,obt_go
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    addiu t0,zero,64              # the 64 places: 0x4000 = nothing
    addiu t1,t9,@P2@
    ori t2,zero,0x4000
obt_c:
    sh t2,0(t1)
    addiu t0,t0,-1
    bne t0,zero,obt_c
    addiu t1,t1,2
    move s0,zero
obt_l:
    lui t6,%hi(OB_TAB)
    addiu t6,t6,%lo(OB_TAB)
    sll t5,s0,1
    addu t6,t6,t5
    lhu s1,0(t6)
    lui t6,0x0033
    addu s1,s1,t6
    lbu a1,@BAG@(s1)
    jal OB_PUT
    move a0,s0
    addiu s0,s0,1
    sltiu t0,s0,158
    bne t0,zero,obt_l
    nop
    lui t9,0x0033
    addiu t7,zero,0x5036
    sh t7,@MK@(t9)
    lui t6,0x000E
    sw zero,0x7FAC(t6)
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    addiu sp,sp,32
obt_go:
    j TICK_NEXT
    nop
"""

OB_C_SRC = """
ob_gain:                          # from glue 62's og_eq (t2 = the type, a0 = the item, a1 = the count, s2 = its table entry): THE GAME GIVES IT
    addiu t3,zero,2
    beq t2,t3,obn_y               # a Keyblade
    addiu t3,zero,14
    beq t2,t3,obn_y               # an armour
    addiu t3,zero,15
    beq t2,t3,obn_y               # an accessory
    addiu t3,zero,16
    bne t2,t3,obn_go              # (not a material either: as the game)
    nop
obn_y:
    lui t9,0x0033
    lhu t8,@MK@(t9)
    addiu t7,zero,0x5036
    bne t8,t7,obn_go              # no own bag yet
    nop
    lhu t4,0x12(s2)               # its place in the bag
    lui t6,%hi(OB_TAB)
    addiu t6,t6,%lo(OB_TAB)
    move t5,zero
obn_f:
    lhu t7,0(t6)
    beq t7,t4,obn_s
    nop
    addiu t5,t5,1
    sltiu t7,t5,158
    bne t7,zero,obn_f
    addiu t6,t6,2
    b obn_go                      # (not in the list)
    nop
obn_s:
    lui t7,0x000E
    lw t7,0x7FAC(t7)
    beq t7,zero,obn_p2
    nop
    lui t7,0x000E                 # his bag is in: the game's add is his; player 1's count waits in the buffer
    addu t7,t7,t5
    lbu t6,0x7C40(t7)
    addu t6,t6,a1
    sltiu t8,t6,100
    bne t8,zero,obn_b
    nop
    addiu t6,zero,99
obn_b:
    b obn_go
    sb t6,0x7C40(t7)
obn_p2:
    addiu sp,sp,-32               # player 1's bag gets it from the game, player 2's the same here
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd t5,24(sp)
    jal OB_GET
    move a0,t5
    ld a1,16(sp)
    ld a0,24(sp)
    jal OB_PUT
    addu a1,a1,v0
    ld a1,16(sp)
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,32
obn_go:
    j 0x001A32C8                  # the game's add to the bag
    nop
"""


def ob_src(src):
    return (src.replace("@P2H@", str(OB_P2 + 1)).replace("@P2@", str(OB_P2)).replace("@MK@", str(OB_MARK))
            .replace("@BAG@", str(OB_BAG)))

# ---- seventy-second glue (only with --drivesave) -------------------------------------------------------------
DV_AT = 0x000EE800
DV_END = 0x000EEA00
DV_SRC = """
dv_tick:                          # from 0x00167E90 (the controller task, every frame): the twin's gauge and bars into the save data
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin's object (lane E; 0 = none)
    beq t6,zero,dvt_go
    nop
    lw t6,0x48C(t6)               # his slot
    beq t6,zero,dvt_go
    nop
    lw t5,0x250(t6)               # the second hero's mark (bit 31)
    bgez t5,dvt_go
    lui t4,0x0033
    lw t5,0x260(t6)               # his save block: Sora's record (0x0032E020), whose Drive bytes the game keeps
    addiu t4,t4,-8160
    bne t5,t4,dvt_go
    lui t7,0x0033
    lbu t5,0x1B0(t6)              # his gauge
    lbu t4,0x1B1(t6)              # his bars
    sb t5,-7250(t7)               # King Mickey's record + 0x52 (0x0032E3AE)
    sb t4,-7249(t7)               # + 0x53
    ori t5,zero,0x5037
    sh t5,-7252(t7)               # + 0x50: the mark
dvt_go:
    j DV_NEXT
    nop

dv_load:                          # from snap_none's end (0x001CD2D0 in "the load menu fills the snapshot" 0x001CD2B8, a Load
    lui t1,0x0033                 # Game). Only t1 .. t4 are free there: t5 / t6 / t7 must stay
    lhu t2,-7252(t1)              # King Mickey's record + 0x50: the mark
    ori t3,zero,0x5037
    bne t2,t3,dvl_out             # no values of player 2 in this save: as before
    lui t4,0x000F
    lw t2,-4008(t1)               # the save's 12 Drive bytes (0x0032F058 ..): "what player 1 wrote last" from now on,
    sw t2,0x47C4(t4)              # and the twin's copy starts from them
    sw t2,0x47D0(t4)
    lw t2,-4004(t1)
    sw t2,0x47C8(t4)
    sw t2,0x47D4(t4)
    lw t2,-4000(t1)
    sw t2,0x47CC(t4)
    sw t2,0x47D8(t4)
    lbu t2,-7250(t1)              # his gauge
    sb t2,0x47D0(t4)
    lbu t2,-7249(t1)              # his bars, never more than the most bars (common: the save's)
    lbu t3,-4006(t1)
    sltu t3,t3,t2
    beq t3,zero,dvl_bars
    nop
    lbu t2,-4006(t1)
dvl_bars:
    sb t2,0x47D1(t4)
    ori t2,zero,1
    sw t2,0x47C0(t4)              # valid: his next slot load takes his own values
dvl_out:
    jr ra
    nop

dv_ext:                           # from 0x000F4668 in the drive glue's dl_ext (the save data does not hold what player 1 wrote
    lw t3,0x1040(t5)              # last). t5 = Sora's record, t4 = 0x000F0000; only t2 / t3 are free. First the two steps
    sw t3,0x47CC(t4)              # that the jump took the place of
    lhu t3,0x038C(t5)             # King Mickey's record + 0x50 (= Sora's record + 0x38C): the mark
    ori t2,zero,0x5037
    bne t3,t2,dve_out             # no values of player 2: both take the save's (as before)
    nop
    lw t3,0x1038(t5)              # his copy := the save's 12 bytes ..
    sw t3,0x47D0(t4)
    lw t3,0x103C(t5)
    sw t3,0x47D4(t4)
    lw t3,0x1040(t5)
    sw t3,0x47D8(t4)
    lbu t3,0x038E(t5)             # .. with his gauge
    sb t3,0x47D0(t4)
    lbu t3,0x038F(t5)             # .. and his bars, never more than the most bars
    lbu t2,0x103A(t5)
    sltu t2,t2,t3
    beq t2,zero,dve_bars
    nop
    lbu t3,0x103A(t5)
dve_bars:
    sb t3,0x47D1(t4)
    ori t3,zero,1
    sw t3,0x47C0(t4)              # valid
    lui t5,0x000F                 # out: his own copy (base + 0x1038 = 0x000F47D0)
    jr ra
    addiu t5,t5,0x3798
dve_out:
    jr ra
    nop
"""

# ---- seventy-third glue (only with --itemtarget) ------------------------------------------------------------
II_AT = 0x000EEA00
II_END = 0x000EEE00
II_SRC = """
ih_rows:                          # from 0x001BE3A4 (was jal 0x001BEC68): a0 = s0 = the menu's control object S
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    jal 0x001BEC68                # the game's rows (party members 0 .. 2)
    move s0,a0
    lui t7,0x000F
    addiu t6,t7,0x1000            # S2 = player 2's control object
    lui t5,0x000E
    bne s0,t6,ir_v
    addiu t5,t5,0x7FB0            # player 1's menu: its twin row number
    addiu t5,t5,4                 # player 2's menu: 0x000E7FB4
ir_v:
    addiu t4,zero,-1
    sw t4,0(t5)                   # no twin row (yet)
    sd t5,16(sp)
    lw a0,0x05CC(t7)              # the twin (lane E; 0 = none)
    beq a0,zero,ir_out
    nop
    jal 0x0019BA60                # the builder's first test
    nop
    beq v0,zero,ir_out
    lui t7,0x000F
    lw t6,0x05CC(t7)
    lw t4,0x588(t6)               # the builder's second test: no flag 0x400000
    lui t3,0x0040
    and t4,t4,t3
    bne t4,zero,ir_out
    nop
    lw t4,0x48C(t6)               # the third: a unit slot
    beq t4,zero,ir_out
    nop
    lw t4,8(t6)                   # the same status id as player 1's hero (both Sora, both Roxas)
    lhu t4,0x4C(t4)
    lui t3,0x0035
    lw t3,-5816(t3)               # player 1's hero (0x0034E948)
    beq t3,zero,ir_out
    nop
    lw t3,8(t3)
    lhu t3,0x4C(t3)
    bne t4,t3,ir_out
    nop
    lw t4,0x1FC(s0)               # the list's count = the new row's number
    sltiu t3,t4,8
    beq t3,zero,ir_out            # (at most 8 rows)
    ld t5,16(sp)
    sw t4,0(t5)                   # remembered for this menu
    lw a0,8(t6)
    jal 0x001B77E8                # the row's command (the character's name)
    lhu a0,0x4C(a0)
    move a1,v0
    addiu a0,s0,0x1F4             # list 4, PARTY
    move a2,zero
    jal 0x001BC780
    addiu a3,zero,1
ir_out:
    ld ra,0(sp)
    ld s0,8(sp)
    jr ra
    addiu sp,sp,32

ih_row:                           # from 0x001BE2BC (was: sll t7,t7,2 / addu t7,t7,s1 / lw a1,0xA5C(t7)): t7 = the confirmed
    lui t6,0x000F                 # row, s1 = S; out: a1 = the target. a0 / a2 and the s registers must stay
    addiu t5,t6,0x1000
    lui t4,0x000E
    bne s1,t5,irw_1
    addiu t4,t4,0x7FB0
    addiu t4,t4,4
irw_1:
    lw t3,0(t4)
    bne t7,t3,irw_game
    nop
    lw a1,0x05CC(t6)              # the twin's row: the twin
    b irw_note
    nop
irw_game:
    sll t3,t7,2                   # the game's row: its member
    addu t3,t3,s1
    lw a1,0xA5C(t3)
irw_note:
    lw t3,0x9E0(s1)               # the menu's owner (the hero who uses the item)
    lw t5,0x05CC(t6)
    lui t4,0x000E
    bne t3,t5,irw_2
    addiu t4,t4,0x7FB8            # player 1's hero: 0x000E7FB8 (object), 0x000E7FBC (counter)
    addiu t4,t4,8                 # the twin: 0x000E7FC0, 0x000E7FC4
irw_2:
    sw a1,0(t4)
    lui t3,0x0035
    lw t3,-11076(t3)              # the game's counter (0x0034D4BC)
    jr ra
    sw t3,4(t4)

ih_find:                          # from 0x001BA53C in 0x001BA528 (the effect of a queued item is drawn on the member whose id is a0)
    lw t7,16(sp)                  # 0x001BA528's caller: 0x001BA48C = one queued entry, then s0 = the entry
    lui t6,0x001B
    ori t6,t6,0xA48C
    bne t7,t6,if_game
    lui t6,0x000F
    lw t5,0x05CC(t6)              # the twin
    beq t5,zero,if_game
    lw t4,8(s0)                   # the user
    lui t3,0x0035
    lw t3,-5816(t3)               # player 1's hero
    lui t2,0x000E
    beq t4,t3,if_v
    addiu t2,t2,0x7FB8
    bne t4,t5,if_game
    nop
    addiu t2,t2,8
if_v:
    lw t1,0(t2)                   # the chosen hero (not used up here)
    beq t1,t5,if_hero
    nop
    bne t1,t3,if_game
    nop
if_hero:
    lw t0,8(t5)
    lhu t0,0x4C(t0)
    bne a0,t0,if_game             # the target is the heroes' id
    lui t0,0x0035
    lw t0,-11076(t0)
    lw t7,4(t2)
    subu t0,t0,t7
    sltiu t0,t0,300
    beq t0,zero,if_game
    nop
    bne t1,t4,if_ok               # the partner was picked: drawn on him
    nop
    beq t4,t3,if_selfp1           # the user picked himself: if his partner is down, lane N's rule decides (the game's
    lw t0,0x7F8(t3)               # search)
    b if_selfchk
    nop
if_selfp1:
    lw t0,0x7F8(t5)
if_selfchk:
    andi t0,t0,4
    bne t0,zero,if_game
    nop
if_ok:
    jr ra
    move v0,t1
if_game:
    j 0x00176B58
    nop

ih_pick:                          # from 0x001BA624 (was lane N's jal n_heal): a0 effect, a1 target id, a2 user id, a3 boost,
    lui t6,0x000F                 # s1 = the queued entry (+ 8 = the user's object)
    lw t5,0x05CC(t6)              # the twin
    beq t5,zero,ip_old
    lw t4,8(s1)                   # the user
    lui t3,0x0035
    lw t3,-5816(t3)               # player 1's hero
    lui t2,0x000E
    beq t4,t3,ip_v
    addiu t2,t2,0x7FB8
    bne t4,t5,ip_old
    nop
    addiu t2,t2,8
ip_v:
    lw t1,0(t2)                   # the chosen object (0 = none)
    beq t1,zero,ip_old
    sw zero,0(t2)                 # used up
    lui t0,0x0035
    lw t0,-11076(t0)
    lw t7,4(t2)
    subu t0,t0,t7
    sltiu t0,t0,300
    beq t0,zero,ip_old            # too old: lane N's rule
    nop
    lw t0,8(t5)
    lhu t0,0x4C(t0)               # the heroes' status id
    bne a1,t0,ip_old              # a friend is the target: lane N's rule (the game's routine)
    nop
    bne t1,t4,ip_whom             # the user picked his partner: exactly that
    nop
    beq t4,t3,ip_selfp1           # the user picked himself:
    lw t0,0x7F8(t3)               # (the user is the twin: is player 1's hero down?)
    b ip_selfchk
    nop
ip_selfp1:
    lw t0,0x7F8(t5)               # (the user is player 1's hero: is the twin down?)
ip_selfchk:
    andi t0,t0,4
    bne t0,zero,ip_old            # his partner is down: lane N's rule (the down partner gets it, as in build 21)
    nop
ip_whom:
    beq t1,t3,ip_hero
    nop
    bne t1,t5,ip_old
    nop
    addiu sp,sp,-64               # the twin: lane N's own step for his slot, set up as n_heal does it
    sd ra,0(sp)
    sd s0,8(sp)
    sd s2,16(sp)
    sd s3,24(sp)
    sd s4,32(sp)
    sd s5,40(sp)
    move s0,a0
    move s2,a1
    move s3,a2
    move s4,a3
    jal 0x000F2BB4                # n_he_slot
    move s5,t5
    ld ra,0(sp)
    ld s0,8(sp)
    ld s2,16(sp)
    ld s3,24(sp)
    ld s4,32(sp)
    ld s5,40(sp)
    addiu sp,sp,64
    jr ra
    move v0,zero
ip_hero:
    j 0x001A2A50                  # player 1's hero: the game's own routine (the heroes' id = his slot)
    nop
ip_old:
    j 0x000F2A9C                  # lane N's n_heal
    nop
"""

# ---- seventy-fourth glue (only with --boxpick) ---------------------------------------------------------------
BX_AT = 0x000EEE00
BX_END = 0x000EEF00
BX_SRC = """
bx_twin:                          # from 0x001BF570 in the item box's step 0x001BF4E8 (was jal 0x001BFCA0): player 1's hero did not
    addiu sp,sp,-16               # touch the box (s1 = the box, s0 = player 1's hero, f20 = 0)
    sd ra,0(sp)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # player 2's hero (lane E's twin; 0 = none)
    beq t6,zero,bx_game
    nop
    sd t6,8(sp)
    jal 0x0019BA60                # the routine's first test, for him
    move a0,t6
    beq v0,zero,bx_game
    ld t6,8(sp)
    lw t7,0x588(t6)               # and its second (flag 0x02000000)
    lui t5,0x0200
    and t7,t7,t5
    bne t7,zero,bx_game
    nop
    jal 0x0016C028                # the box's place
    move a0,s1
    move a1,v0
    ld a0,8(sp)
    mtc1 zero,f12
    jal 0x001A4FF8                # does he touch it?
    mtc1 zero,f13
    beq v0,zero,bx_game
    nop
    ld s0,8(sp)                   # yes: the routine's own end, with him as the taker
    ld ra,0(sp)
    j 0x001BF5D4
    addiu sp,sp,16
bx_game:
    ld ra,0(sp)
    addiu sp,sp,16
    j 0x001BFCA0                  # as before
    move a0,s1
"""

# ---- seventy-fifth glue (only with --formroom) ---------------------------------------------------------------
FR_AT = 0x000EEF00
FR_END = 0x000EEF80
FR_SRC = """
fr_room:                          # from 0x0016EEE4 (was j 0x0016EF28) in 0x0016ED50: a0 = player 1's form (0 = none); the caller's
    addiu sp,sp,-16               # frame is already given back, ra = its caller's
    sd ra,0(sp)
    beq a0,zero,fr_twin
    sd a0,8(sp)
    jal 0x0016EF28                # player 1's form, as before (number 5000)
    nop
fr_twin:
    lui t5,0x000F
    lw t4,0x47EC(t5)              # two heroes built in one room once
    beq t4,zero,fr_out
    lbu a0,0x47E8(t5)             # player 2's form (0 = none)
    beq a0,zero,fr_out
    ld t6,8(sp)
    beq a0,t6,fr_out              # the same form as player 1's: asked for already
    lui t3,0x000E
    lw a1,0x7C08(t3)              # his number base (forty-first glue; 0 = 5000)
    bne a1,zero,fr_ask
    nop
    addiu a1,zero,5000
fr_ask:
    sd a1,8(sp)
    jal 0x001D1438                # the form's object number
    nop
    move a0,v0
    ld a1,8(sp)
    addiu a2,zero,4
    jal 0x0016EB48                # the game's own request
    addiu a3,zero,7
fr_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""

# ---- seventy-seventh glue (only with --gummiall) --------------------------------------------------------------
GX_AT = 0x000EF000
GX_END = 0x000EF400
GX_SITES = (                                       # (the place in the flight module, its first word, its second, the routine)
    (0x01F49B38, 0x27BDFFA0, 0x248F0050, "gx_spawn"),   # a generic weapon fires one shot (a0 = the weapon)
    (0x01F4A6E8, 0x27BDFFA0, 0xFFB20040, "gx_spec"),    # a special weapon fires (a0 = the weapon)
    (0x01F3E1A0, 0x27BDFFE0, 0xAC850040, "gx_base1"),   # a shot's start-up (base class 0x01F81280)
    (0x01F3FA20, 0x27BDFFE0, 0xAC850040, "gx_base2"),   # a shot's start-up (base class 0x01F812B8)
    (0x01F26D00, 0x27BDFFF0, 0xFFBF0000, "gx_h10"),     # "10 points": a hit without damage (a1 = the shot + 72)
)
GX_SRC = """
gx_inst:                          # from 0x00167E90 (the controller task, every frame): a fresh flight module gets the jumps
    lui t7,0x01F2
    lhu t6,-32748(t7)             # 0x01F18014: which Gummi module is in memory (0x636A = the flight)
    ori t4,zero,0x636A
    bne t6,t4,gxi_go
    nop
@CHECKS@
@WRITES@
gxi_go:
    j GX_NEXT
    nop

gx_spawn:                         # 0x01F49B38(a0 = a weapon, a1, a2): one shot of a generic weapon
    addiu sp,sp,-16
    sd ra,0(sp)
    jal gx_own
    nop
    lui t7,0x000E
    jal gxs_body
    sw t2,0x7EF4(t7)              # the ship that fires now
    lui t7,0x000E
    sw zero,0x7EF4(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
gxs_body:
    addiu sp,sp,-96               # the two instructions that sat at 0x01F49B38
    j 0x01F49B40
    addiu t7,a0,80

gx_spec:                          # 0x01F4A6E8(a0 = a special weapon): it fires
    addiu sp,sp,-16
    sd ra,0(sp)
    jal gx_own
    nop
    lui t7,0x000E
    jal gxp_body
    sw t2,0x7EF4(t7)
    lui t7,0x000E
    sw zero,0x7EF4(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
gxp_body:
    addiu sp,sp,-96               # the two instructions that sat at 0x01F4A6E8
    j 0x01F4A6F0
    sd s2,64(sp)

gx_own:                           # a0 = a weapon -> t2 = 1 / 2 (the ship whose block carries it), 0 = none. t2 .. t5 only
    lw t3,0x40(a0)                # its block (for some weapons this word is no pointer: run gw1)
    move t2,zero
    andi t4,t3,3
    bne t4,zero,gxo_out
    lui t4,0x0010
    sltu t4,t3,t4
    bne t4,zero,gxo_out
    lui t4,0x0200
    sltu t4,t3,t4
    beq t4,zero,gxo_out
    nop
    lw t3,0x4A4(t3)               # the block's parent (ship + 0x3E0 for a player's ship)
    lui t5,0x000F
    lw t4,0x2604(t5)              # ship 2
    beq t4,zero,gxo_s1
    addiu t4,t4,0x3E0
    beq t3,t4,gxo_out
    addiu t2,zero,2
gxo_s1:
    move t2,zero
    lw t4,0x2600(t5)              # ship 1
    beq t4,zero,gxo_out
    addiu t4,t4,0x3E0
    bne t3,t4,gxo_out
    nop
    addiu t2,zero,1
gxo_out:
    jr ra
    nop

gx_base1:                         # 0x01F3E1A0(a0 = a shot, a1 .. a3, t0, t1): a shot starts up
    lui t7,0x000E
    lui t6,0x01F5
    ori t6,t6,0x38C4              # the cannon's start-up calls from here: gq_init has marked that shot
    beq ra,t6,gxb1_go
    srl t4,a0,4
    andi t4,t4,0x0FFF
    addiu t3,t7,-4096              # the shots' table (as gq_init)
    addu t4,t4,t3
    lw t2,0x7EF4(t7)              # the ship that fires now (0 = no player's weapon)
    sb t2,0(t4)
gxb1_go:
    addiu sp,sp,-32               # the two instructions that sat at 0x01F3E1A0
    j 0x01F3E1A8
    sw a1,64(a0)

gx_base2:                         # 0x01F3FA20(a0 = a shot, ...): the other start-up
    lui t7,0x000E
    srl t4,a0,4
    andi t4,t4,0x0FFF
    addiu t3,t7,-4096
    addu t4,t4,t3
    lw t2,0x7EF4(t7)
    sb t2,0(t4)
    addiu sp,sp,-32               # the two instructions that sat at 0x01F3FA20
    j 0x01F3FA28
    sw a1,64(a0)

gx_hit:                           # from gq_hit's first word (0x01F26998(a0 = an enemy, a1 = the hit record)): whose shot hit it
    lui t7,0x000E
    lui t3,%hi(gx_wl)
    addiu t3,t3,%lo(gx_wl)        # the calls whose a1 is a shot + 72
gxh_l:
    lw t1,0(t3)
    beq t1,zero,gxh_last          # another caller: player 1's
    addiu t3,t3,4
    bne t1,ra,gxh_l
    addiu t4,a1,-72               # the shot
    srl t4,t4,4
    andi t4,t4,0x0FFF
    addiu t3,t7,-4096
    addu t4,t4,t3
    lbu t2,0(t4)                  # the ship that fired it
    bne t2,zero,gxh_k
    nop
gxh_last:
    addiu t2,zero,1               # not known: player 1's
gxh_k:
    sw t2,0x7EF8(t7)              # the credit
    srl t4,a0,6
    andi t4,t4,0x07FF
    ori t3,t7,0xF800              # the enemies' table
    addu t4,t4,t3
    sb t2,0(t4)
    addiu sp,sp,-48               # the two instructions that sat at 0x01F26998
    j 0x01F269A0
    sd s0,0(sp)
gx_wl:
    .word 0x01F54278
    .word 0x01F55BF0
    .word 0x01F55F2C
    .word 0x01F572AC
    .word 0x01F584E8
    .word 0x01F59BEC
    .word 0x01F5AF84
    .word 0x01F72E64
    .word 0x01F74544
    .word 0

gx_h10:                           # 0x01F26D00(a0 = a thing, a1 = a shot + 72): 10 points, no damage
    lui t7,0x000E
    addiu t4,a1,-72
    srl t4,t4,4
    andi t4,t4,0x0FFF
    addiu t3,t7,-4096
    addu t4,t4,t3
    lbu t2,0(t4)
    bne t2,zero,gx10_k
    nop
    addiu t2,zero,1
gx10_k:
    sw t2,0x7EF8(t7)
    addiu sp,sp,-16               # the two instructions that sat at 0x01F26D00
    j 0x01F26D08
    sd ra,0(sp)
"""


def gx_source(labels):
    """The seventy-seventh glue's source with its installer's checks and writes (labels = None: the first pass)."""
    checks, writes = "", ""
    for site, word0, _word1, name in GX_SITES:
        hi = (site + 0x8000) >> 16
        lo = site - (hi << 16)
        checks += ("    lui t7,0x%04X\n    lw t5,%d(t7)                 # 0x%08X: still its own first word?\n    lui t4,0x%04X\n"
                   "    ori t4,t4,0x%04X\n    bne t5,t4,gxi_go\n    nop\n") % (hi, lo, site, word0 >> 16, word0 & 0xFFFF)
        j = ((2 << 26) | ((labels[name] >> 2) & 0x3FFFFFF)) if labels else 0
        writes += ("    lui t7,0x%04X\n    lui t4,0x%04X\n    ori t4,t4,0x%04X\n    sw t4,%d(t7)                 # 0x%08X: j %s\n"
                   "    sw zero,%d(t7)\n") % (hi, j >> 16, j & 0xFFFF, lo, site, name, lo + 4)
    return GX_SRC.replace("@CHECKS@", checks.rstrip("\n")).replace("@WRITES@", writes.rstrip("\n"))


# ---- seventy-eighth glue (only with --gummitag) --------------------------------------------------------------
GT_AT = 0x000EF000                                 # (glue 77's room; the two are never built together)
GT_END = 0x000EF400
GT_SITES = (                                       # (the place in the flight module, its first word, the routine)
    (0x01F49B38, 0x27BDFFA0, "gt_gen"),            # a generic weapon fires one shot (a0 = the weapon, a1, a2)
    (0x01F4A6E8, 0x27BDFFA0, "gt_spc"),            # a special weapon fires (a0 = the weapon)
    (0x01F26D00, 0x27BDFFF0, "gt_h10"),            # "10 points": a hit without damage (a1 = the shot + 72)
    (0x01F27A40, 0x27BDFFF0, "gt_h100"),           # "100 / 1000 points" (its only call 0x01F5BAD4: a1 = the shot + 72)
)
GT_SRC = """
gt_inst:                          # from 0x00167E90 (the controller task, every frame): a fresh flight module gets the jumps
    lui t7,0x01F2
    lhu t6,-32748(t7)             # 0x01F18014: which Gummi module is in memory (0x636A = the flight)
    ori t4,zero,0x636A
    bne t6,t4,gti_go
    nop
@CHECKS@
@WRITES@
gti_go:
    j GT_NEXT
    nop

gt_gen:                           # 0x01F49B38(a0 = a generic weapon, a1, a2): it fires one shot
    daddu t9,ra,zero
    jal gt_tag
    nop
    daddu ra,t9,zero
    addiu sp,sp,-96               # the two instructions that sat at 0x01F49B38
    j 0x01F49B40
    addiu t7,a0,80

gt_spc:                           # 0x01F4A6E8(a0 = a special weapon): it fires
    daddu t9,ra,zero
    jal gt_tag
    nop
    daddu ra,t9,zero
    addiu sp,sp,-96               # the two instructions that sat at 0x01F4A6E8
    j 0x01F4A6F0
    sd s2,64(sp)

gt_tag:                           # a0 = a weapon -> weapon + 110 = 0xA501 / 0xA502 (its owner block hangs on ship 1 / 2), else 0
    lw t4,0x40(a0)                # the owner (a block for a player's weapon)
    andi t5,t4,3
    bne t5,zero,gtt_0             # no aligned pointer
    lui t5,0x0010
    sltu t6,t4,t5
    bne t6,zero,gtt_0             # below 0x00100000
    lui t5,0x0200
    addiu t5,t5,-4096
    sltu t6,t4,t5
    beq t6,zero,gtt_0             # at or above 0x01FFF000
    lui t5,0x000F
    lw t4,0x4A4(t4)               # the block's parent
    lw t6,0x2600(t5)              # ship 1
    ori t7,zero,0xA501
    beq t6,zero,gtt_s2
    addiu t6,t6,0x3E0
    beq t4,t6,gtt_w
    nop
gtt_s2:
    lw t6,0x2604(t5)              # ship 2
    ori t7,zero,0xA502
    beq t6,zero,gtt_0
    addiu t6,t6,0x3E0
    beq t4,t6,gtt_w
    nop
gtt_0:
    move t7,zero
gtt_w:
    jr ra
    sh t7,110(a0)                 # the hit values + 30: copied into every shot (shot + 72 + 30) and so into every hit record

gt_who:                           # a1 = a hit record -> t7 = 1 / 2 (the ship that fired), 0 = not known. t4 .. t7 only
    andi t4,a1,3
    bne t4,zero,gtw_0
    lui t5,0x0010
    sltu t4,a1,t5
    bne t4,zero,gtw_0
    lui t5,0x0200
    addiu t5,t5,-32
    sltu t4,a1,t5
    beq t4,zero,gtw_0             # at or above 0x01FFFFE0
    nop
    lhu t4,30(a1)                 # the tag
    srl t5,t4,8
    addiu t6,zero,0xA5
    bne t5,t6,gtw_0
    andi t7,t4,0xFF
    sltiu t5,t7,3                 # 0, 1, 2 only
    bne t5,zero,gtw_out
    nop
gtw_0:
    move t7,zero
gtw_out:
    jr ra
    nop

gt_hit:                           # from gq_hit's first word (its delay slot "lui t1,0x01F5" ran): 0x01F26998(a0 = an enemy, a1 = the hit record)
    lui t8,0x01F5
    ori t8,t8,0x4278              # the cannon shots' own call: glue 66's shots' table, as build 23
    bne ra,t8,gth_tag
    nop
    j GQH_NEXT                    # gq_hit + 4
    lui t7,0x000E                 # gq_hit's first word
gth_tag:
    daddu t9,ra,zero
    lui t8,0x01F3
    ori t8,t8,0x6D1C              # 0x01F36D14's call: a ram block's record on its own stack (no shot, no tag)
    beq ra,t8,gth_k
    addiu t7,zero,1
    jal gt_who
    nop
    daddu ra,t9,zero
    bne t7,zero,gth_k
    nop
    addiu t7,zero,1               # no tag: player 1's (as build 23)
gth_k:
    lui t6,0x000E
    sw t7,0x7EF8(t6)              # the credit (gq_add reads it)
    srl t4,a0,6
    andi t4,t4,0x07FF
    ori t5,t6,0xF800              # the enemies' table (gq_kill reads it)
    addu t4,t4,t5
    sb t7,0(t4)
    addiu sp,sp,-48               # the two instructions that sat at 0x01F26998
    j 0x01F269A0
    sd s0,0(sp)

gt_h10:                           # 0x01F26D00(a0 = a thing, a1 = the shot + 72): 10 points, no damage
    daddu t9,ra,zero
    jal gt_who
    nop
    daddu ra,t9,zero
    beq t7,zero,gt10_go           # no tag (a cannon shot): the credit stays as it is (build 23)
    lui t6,0x000E
    sw t7,0x7EF8(t6)
gt10_go:
    addiu sp,sp,-16               # the two instructions that sat at 0x01F26D00
    j 0x01F26D08
    sd ra,0(sp)

gt_h100:                          # 0x01F27A40(a0 = a thing, a1 = the shot + 72): 100 / 1000 points
    daddu t9,ra,zero
    jal gt_who
    nop
    daddu ra,t9,zero
    beq t7,zero,gt100_go
    lui t6,0x000E
    sw t7,0x7EF8(t6)
gt100_go:
    addiu sp,sp,-16               # the two instructions that sat at 0x01F27A40
    j 0x01F27A48
    sd ra,0(sp)
"""


def gt_source(labels):
    """The seventy-eighth glue's source with its installer's checks and writes (labels = None: the first pass)."""
    checks, writes = "", ""
    for site, word0, name in GT_SITES:
        hi = (site + 0x8000) >> 16
        lo = site - (hi << 16)
        checks += ("    lui t7,0x%04X\n    lw t5,%d(t7)                 # 0x%08X: still its own first word?\n    lui t4,0x%04X\n"
                   "    ori t4,t4,0x%04X\n    bne t5,t4,gti_go\n    nop\n") % (hi, lo, site, word0 >> 16, word0 & 0xFFFF)
        j = ((2 << 26) | ((labels[name] >> 2) & 0x3FFFFFF)) if labels else 0
        writes += ("    lui t7,0x%04X\n    lui t4,0x%04X\n    ori t4,t4,0x%04X\n    sw t4,%d(t7)                 # 0x%08X: j %s\n"
                   "    sw zero,%d(t7)\n") % (hi, j >> 16, j & 0xFFFF, lo, site, name, lo + 4)
    return GT_SRC.replace("@CHECKS@", checks.rstrip("\n")).replace("@WRITES@", writes.rstrip("\n"))


# ---- sixty-sixth glue (only with --ship2score) --------------------------------------------------------------
GQ_AT = 0x000EDC00
GQ_END = 0x000EE260                                # (0x000EE260 .. 0x000EE400: the seventy-first glue's swap)
GQ_SITES = (                                       # (the place in the flight module, its first word, the routine that takes it over)
    (0x01F536D0, 0x27BDFF30, "gq_init"),           # a shot's start-up (the cannons' class)
    (0x01F26998, 0x27BDFFD0, "gq_hit"),            # an enemy takes a hit
    (0x01F26520, 0x27BDFFF0, "gq_kill"),           # the enemy is destroyed
    (0x01F4DE90, 0x27BDFFF0, "gq_add"),            # points are added to the score
    (0x01F4DE70, 0x27BDFFF0, "gq_reset"),          # the score is set to 0
    (0x01F67D40, 0x27BDFFF0, "gq_sdstep"),         # the score row's step
    (0x01F67748, 0x240F0001, "gq_sdstart"),        # the score row starts
    (0x01F67758, 0x240F0003, "gq_sdend"),          # the score row ends
    (0x01F676A8, 0x27BDFFE0, "gq_sdfree"),         # the score row is freed
)
GQ_CALLS = (                                       # (a call in the flight module, its word, the routine that is called in its place)
    (0x01F679A8, 0x0C7D37B4, "gq_get"),            # the score row reads the score
    (0x01F47164, 0x0C7C6458, "gq_new"),            # a new picture asks the module's heap for its 388 bytes
)
GQ_TAB = 0x000DF000                                # the shots' table (ship 1 / 2 per shot, 4 KB; was 0x000EE800 .. build 22, where glues 72 .. 75 lie)
GQ_OWN_AT = 0x000EA210                             # nine own pictures (388 bytes each) for row 2 and the gauge's digit
GQ_OWN_LAST = 0x000EB5E8                           # the tenth
GQ_OWN_END = 0x000EB770                            # (an own picture lies in GQ_OWN_AT .. GQ_OWN_END)
GQ_ROW_DX = 210                                    # player 2's row stands this much to the right of the game's row
GQ_ROW_DY = 0
GQ_MARK_X = 388                                    # the gauge's digit: left of the hull gauge (places count 512 across, 448 down)
GQ_MARK_Y = 396
GQ_SRC = """
gq_inst:                          # from 0x00167E90, in front of the fifty-first glue's gs_inst: a fresh flight module gets the jumps
    lui t7,0x01F2
    lhu t6,-32748(t7)             # 0x01F18014: which Gummi module is in memory (0x636A = the flight)
    ori t4,zero,0x636A
    bne t6,t4,gqi_go
    nop
@CHECKS@
@WRITES@
    lui t7,0x000E                 # a fresh module: the old pictures are gone with the old module
    ori t6,t7,0x7F40
    addiu t5,zero,16
gqi_clr:
    sw zero,0(t6)                 # row 2 (0x7F40 .. 0x7F7F: its state, its pictures, the gauge's digit)
    addiu t5,t5,-1
    bne t5,zero,gqi_clr
    addiu t6,t6,4
    sw zero,0x7F98(t7)            # no own picture place is given out
gqi_go:
    j GQ_NEXT
    nop

gq_init:                          # 0x01F536D0(a0 = a shot, ..., t1 = the weapon that fires): a cannon shot starts up
    lui t7,0x000E
    srl t4,a0,4
    andi t4,t4,0x0FFF
    addiu t3,t7,-4096              # the shots' table
    addu t4,t4,t3
    lui t6,0x01F5
    ori t6,t6,0x5168              # the cannon's own call of this routine
    bne ra,t6,gqn_w               # another caller: no number
    move t2,zero
    lui t5,0x000F
    lw t5,0x2604(t5)              # ship 2
    addiu t2,zero,1
    beq t5,zero,gqn_w
    sltu t6,t1,t5                 # the weapon stands in front of ship 2: it is ship 1's
    bne t6,zero,gqn_w
    nop
    addiu t2,zero,2
gqn_w:
    sb t2,0(t4)
    addiu sp,sp,-208              # the two instructions that sat at 0x01F536D0
    j 0x01F536D8
    sd s3,152(sp)

gq_hit:                           # 0x01F26998(a0 = an enemy, a1 = the hit record = the shot + 72)
    lui t7,0x000E
    lui t1,0x01F5
    ori t1,t1,0x4278              # the cannon shots' own call of this routine
    bne ra,t1,gqh_last
    addiu t4,a1,-72               # the shot
    srl t4,t4,4
    andi t4,t4,0x0FFF
    addiu t3,t7,-4096
    addu t4,t4,t3
    lbu t2,0(t4)                  # the ship that fired it
    bne t2,zero,gqh_k
    nop
gqh_last:
    addiu t2,zero,1               # not known (another kind of shot): player 1's
gqh_k:
    sw t2,0x7EF8(t7)              # the credit
    srl t4,a0,6
    andi t4,t4,0x07FF
    ori t3,t7,0xF800              # the enemies' table
    addu t4,t4,t3
    sb t2,0(t4)
    addiu sp,sp,-48               # the two instructions that sat at 0x01F26998
    j 0x01F269A0
    sd s0,0(sp)

gq_kill:                          # 0x01F26520(a0 = the enemy): it is destroyed, its worth is added
    lui t7,0x000E
    srl t4,a0,6
    andi t4,t4,0x07FF
    ori t3,t7,0xF800
    addu t4,t4,t3
    lbu t2,0(t4)                  # the ship whose shot hit it last
    beq t2,zero,gqk_1
    nop
    sw t2,0x7EF8(t7)
    sb zero,0(t4)
gqk_1:
    addiu sp,sp,-16               # the two instructions that sat at 0x01F26520
    j 0x01F26528
    sd s0,0(sp)

gq_add:                           # 0x01F4DE90(a0 = points)
    lui t7,0x000E
    lw t2,0x7EF8(t7)
    addiu t1,zero,2
    bne t2,t1,gqa_1               # the credit is not ship 2
    lui t5,0x01F8
    lbu t4,0x03A0(t5)             # the game's score is locked
    bne t4,zero,gqa_1
    nop
    lw t3,0x7EFC(t7)
    addu t3,t3,a0
    sw t3,0x7EFC(t7)              # player 2's points
gqa_1:
    addiu sp,sp,-16               # the two instructions that sat at 0x01F4DE90
    j 0x01F4DE98
    daddu a1,a0,zero

gq_get:                           # the call at 0x01F679A8 (was 0x01F4DED0 "the score"): the row that is being shown asks
    lui t7,0x000E
    lw t6,0x7F7C(t7)              # row 2 is in work
    lw t5,0x7EFC(t7)              # player 2's points
    bne t6,zero,gqg_2
    lui t4,0x01F8
    lw v0,0x039C(t4)              # the game's score
    jr ra
    subu v0,v0,t5                 # the game's row: player 1's points
gqg_2:
    jr ra
    move v0,t5

gq_sdstart:                       # 0x01F67748(a0 = the score row): it starts (the whole routine)
    addiu t7,zero,1
    sb zero,48(a0)
    sw t7,40(a0)
    lui t6,0x000E
    sb zero,0x7F70(t6)            # row 2 too
    sw t7,0x7F68(t6)
    lui t5,0x3F80
    jr ra
    sw t5,0x7F6C(t6)              # (its start value 1.0, as the game's row has from its builder)

gq_sdend:                         # 0x01F67758(a0 = the score row): it ends (the whole routine)
    addiu t7,zero,3
    sw t7,40(a0)
    lui t6,0x000E
    jr ra
    sw t7,0x7F68(t6)

gq_sdfree:                        # 0x01F676A8(a0 = the score row): its pictures are freed
    lui t7,0x000E
    ori t6,t7,0x7F40
    beq a0,t6,gqd_body            # (a call for row 2 itself: not made any more)
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    jal gqd_body                  # the game's row
    nop
    lui s0,0x000E
    ori s0,s0,0x7F44              # row 2's pictures: its frame, seven digits, the eighth (row 2 + 4 .. + 36)
    addiu s1,zero,9
gqd_l:
    lw a0,0(s0)
    beq a0,zero,gqd_n
    nop
    jal gq_end
    nop
    sw zero,0(s0)
gqd_n:
    addiu s1,s1,-1
    bne s1,zero,gqd_l
    addiu s0,s0,4
    lui t7,0x000E
    lw a0,0x7F78(t7)              # the gauge's digit
    sw zero,0x7F68(t7)
    sw zero,0x7F78(t7)
    beq a0,zero,gqd_1
    sw zero,0x7F98(t7)            # no own place is given out any more
    jal gq_end
    nop
gqd_1:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    jr ra
    addiu sp,sp,32

gq_end:                           # a0 = a picture: it is ended; one in the own memory without the module's "delete"
    lw t6,0(a0)                   # its class
    lui t5,0x000E
    ori t5,t5,@OWN_LO@
    sltu t4,a0,t5
    bne t4,zero,gqe_heap
    lui t5,0x000E
    ori t5,t5,@OWN_HI@
    sltu t4,a0,t5
    beq t4,zero,gqe_heap
    nop
    lw t6,0(t6)                   # the first method: destroy only
    jr t6
    nop
gqe_heap:
    lw t6,4(t6)                   # the second: destroy and delete, as the game ends its own
    jr t6
    nop

gq_new:                           # the call at 0x01F47164 (was the module's "new", a0 = 388): a new picture's memory
    lui t7,0x000E
    lw t6,0x7F7C(t7)              # row 2 is in work, or the gauge's digit is being made
    beq t6,zero,gqw_heap
    lw t5,0x7F98(t7)              # how many own places are given out
    sltiu t4,t5,10
    beq t4,zero,gqw_heap          # none left: the module's heap
    addiu t4,t5,1
    sw t4,0x7F98(t7)
    addiu t4,zero,9
    beq t5,t4,gqw_last
    sll t3,t5,8
    sll t2,t5,7
    addu t3,t3,t2
    sll t2,t5,2
    addu t3,t3,t2                 # 388 x its number
    lui v0,0x000E
    ori v0,v0,@OWN_LO@
    jr ra
    addu v0,v0,t3
gqw_last:
    lui v0,0x000E
    jr ra
    ori v0,v0,@OWN_LAST@
gqw_heap:
    j 0x01F19160
    nop

gqd_body:
    addiu sp,sp,-32               # the two instructions that sat at 0x01F676A8
    j 0x01F676B0
    sd s2,16(sp)

gq_sdstep:                        # 0x01F67D40(a0 = the score row): its step
    lui t7,0x000E
    ori t6,t7,0x7F40
    beq a0,t6,gqs_body            # (the call for row 2 itself)
    nop
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a0,8(sp)
    jal gqs_body                  # the game's row
    nop
    lui t7,0x000E
    lw t5,0x7F68(t7)              # row 2's state before its step
    sd t5,32(sp)
    addiu t4,zero,1
    sw t4,0x7F7C(t7)              # row 2 is in work
    jal gqs_body
    ori a0,t7,0x7F40
    lui t7,0x000E
    sw zero,0x7F7C(t7)
    lw t5,0x7F68(t7)
    addiu t4,zero,2
    bne t5,t4,gqs_mark            # row 2 is not shown
    ori t6,t7,0x7F48              # its digit pictures (row 2 + 8 .. + 36)
    lw t2,0x7F44(t7)              # its frame picture would lie on the game's digits: out of the picture
    beq t2,zero,gqs_nf
    addiu t1,zero,3000
    sw t1,356(t2)
gqs_nf:
    addiu t3,zero,8
gqs_dig:
    lw t2,0(t6)
    beq t2,zero,gqs_dn
    addiu t3,t3,-1
    lw t1,356(t2)
    addiu t1,t1,@ROW_DX@
    sw t1,356(t2)                 # the digit stands in row 2's place
    lw t1,360(t2)
    addiu t1,t1,@ROW_DY@
    sw t1,360(t2)
gqs_dn:
    bne t3,zero,gqs_dig
    addiu t6,t6,4
gqs_mark:
    lui t7,0x000E
    lw t5,0x7F68(t7)
    addiu t4,zero,2
    bne t5,t4,gqs_out             # row 2 is not shown: no digit work
    lw t3,0x7F78(t7)
    bne t3,zero,gqs_have
    nop
    jal 0x01F48038                # the HUD's picture sheet
    nop
    lui t7,0x000E
    addiu t4,zero,1
    sw t4,0x7F7C(t7)              # (its memory: an own place)
    move a0,v0
    addiu a1,zero,8
    jal 0x01F46E80                # a new picture: a digit
    addiu a2,zero,72
    lui t7,0x000E
    sw zero,0x7F7C(t7)
    beq v0,zero,gqs_out
    sw v0,0x7F78(t7)
gqs_have:
    lui t6,0x000F
    lw t5,0x2600(t6)              # ship 1
    lw t4,0x2604(t6)              # ship 2
    addiu t3,zero,54              # the digit 1
    beq t5,zero,gqs_num
    nop
    beq t4,zero,gqs_num
    nop
    lwc1 f0,0x4AC(t5)             # the hulls
    lwc1 f1,0x4AC(t4)
    c.lt.s f1,f0
    bc1f gqs_num                  # ship 2's is not the lower one
    nop
    addiu t3,zero,56              # the digit 2
gqs_num:
    sd t3,24(sp)
    jal 0x01F47A58                # the digit's picture number now
    lw a0,0x7F78(t7)
    ld a1,24(sp)
    beq v0,a1,gqs_pos
    lui t7,0x000E
    jal 0x01F47A10                # another one
    lw a0,0x7F78(t7)
gqs_pos:
    lui t7,0x000E
    lw a0,0x7F78(t7)
    addiu a1,zero,@MARK_X@
    jal 0x01F477C0                # the digit's place
    addiu a2,zero,@MARK_Y@
gqs_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
gqs_body:
    addiu sp,sp,-16               # the two instructions that sat at 0x01F67D40
    j 0x01F67D48
    addiu t7,zero,1

gq_reset:                         # 0x01F4DE70: the score is set to 0 (a new flight)
    lui t7,0x000E
    sw zero,0x7EFC(t7)
    sw zero,0x7EF8(t7)
    sw zero,0x7EF4(t7)
    sw zero,0x7EF0(t7)
    addiu sp,sp,-16               # the two instructions that sat at 0x01F4DE70
    j 0x01F4DE78
    lui a0,0x01F8
"""


def gq_source(labels):
    """The sixty-sixth glue's source with the installer's checks and writes (labels = None: the first pass)."""
    checks, writes = "", ""
    sites, calls = GQ_SITES, GQ_CALLS
    if "--gq-nodisp" in sys.argv:                                          # TEST: the counting half only
        sites, calls = GQ_SITES[:5], ()
    if "--gq-nocount" in sys.argv:                                         # TEST: the score rows only
        sites = GQ_SITES[5:]
    for site, word0, name in sites:
        hi = (site + 0x8000) >> 16
        lo = site - (hi << 16)
        checks += ("    lui t7,0x%04X\n    lw t5,%d(t7)                 # 0x%08X: still its own first word?\n    lui t4,0x%04X\n"
                   "    ori t4,t4,0x%04X\n    bne t5,t4,gqi_go\n    nop\n") % (hi, lo, site, word0 >> 16, word0 & 0xFFFF)
        j = ((2 << 26) | ((labels[name] >> 2) & 0x3FFFFFF)) if labels else 0
        writes += ("    lui t7,0x%04X\n    lui t4,0x%04X\n    ori t4,t4,0x%04X\n    sw t4,%d(t7)                 # 0x%08X: j %s\n"
                   "    sw zero,%d(t7)\n") % (hi, j >> 16, j & 0xFFFF, lo, site, name, lo + 4)
    for site, word0, name in calls:
        hi = (site + 0x8000) >> 16
        lo = site - (hi << 16)
        checks += ("    lui t7,0x%04X\n    lw t5,%d(t7)                 # 0x%08X: still the game's call?\n    lui t4,0x%04X\n"
                   "    ori t4,t4,0x%04X\n    bne t5,t4,gqi_go\n    nop\n") % (hi, lo, site, word0 >> 16, word0 & 0xFFFF)
        j = ((3 << 26) | ((labels[name] >> 2) & 0x3FFFFFF)) if labels else 0
        writes += ("    lui t7,0x%04X\n    lui t4,0x%04X\n    ori t4,t4,0x%04X\n    sw t4,%d(t7)                 # 0x%08X: jal %s\n"
                   ) % (hi, j >> 16, j & 0xFFFF, lo, site, name)
    src = GQ_SRC.replace("@OWN_LO@", "0x%04X" % (GQ_OWN_AT & 0xFFFF)).replace("@OWN_HI@", "0x%04X" % (GQ_OWN_END & 0xFFFF)).replace("@OWN_LAST@", "0x%04X" % (GQ_OWN_LAST & 0xFFFF))
    src = src.replace("@ROW_DX@", str(GQ_ROW_DX)).replace("@ROW_DY@", str(GQ_ROW_DY)).replace("@MARK_X@", str(GQ_MARK_X)).replace("@MARK_Y@", str(GQ_MARK_Y))
    return src.replace("@CHECKS@", checks.rstrip("\n")).replace("@WRITES@", writes.rstrip("\n"))


HP_AT = 0x000ECF40
HP_END = 0x000ED920                                # (its code ends at 0x000ED8E0, with --holdshared at 0x000ED914; 0x000ED920 .. is the sixty-ninth glue's)
CO_AT = 0x000EE4C0                                 # (--holdshared) co_two, in the sixty-eighth glue's room (never with --holdpads)
CO_END = 0x000EE6C0
CO_SRC = """
co_e1:                            # (--holdshared) FIXED ENTRIES: CO_AT + 0 from hp_form's hf_h, CO_AT + 8 from hp_rc
    j hs_hf
    nop
co_e2:
    j hs_rc
    nop
co_e3:                            # CO_AT + 16 from hp_form, in place of the shared-mechanic test
    j hs_kind
    nop
hs_hf:                            # the laser dome is never a hero's own move
    addiu t1,zero,0x106           # the shared mechanic (the laser dome) is never a hero's own move
    bne a3,t1,hs_back
    srl t2,a1,22
    addiu t2,t2,-6
    bne t2,zero,hs_back           # the captor is not an object
    nop
    lw t2,8(a1)                   # its object entry
    beq t2,zero,hs_back
    nop
    lw t2,0(t2)                   # its object number
    addiu t1,zero,0x081F
    beq t2,t1,hs_sh
    addiu t1,zero,0x09CA
    bne t2,t1,hs_back
    nop
hs_sh:
    move t8,zero                  # the victim's own-move note does not count for it
    move t0,zero                  # nor the other hero's
hs_back:
    j HF_H2
    nop
co_two:                           # the script call (1,165) "command override" (was 0x00174328). a0 = its inputs
    addiu sp,sp,-32
    sd ra,0(sp)
    jal 0x00174328                # the game's offer: to the engine's player's menu
    sd a0,8(sp)
    lui t7,0x000E
    lw t0,0x7EA0(t7)              # a living pair of the sixty-fifth glue
    beq t0,zero,co_out
    lw t1,0x7EA4(t7)
    beq t1,zero,co_out
    lw t2,0x7EA8(t7)              # its captor: only the last Xemnas's laser dome (0x081F / 0x09CA)
    beq t2,zero,co_out
    nop
    lw t2,8(t2)
    beq t2,zero,co_out
    nop
    lw t2,0(t2)
    addiu t3,zero,0x081F
    beq t2,t3,co_dome
    addiu t3,zero,0x09CA
    bne t2,t3,co_out
    nop
co_dome:
    lui t5,0x0035
    lw t4,-5816(t5)               # the engine's player
    beq t4,t0,co_oth
    move t2,t1
    bne t4,t1,co_out
    move t2,t0
co_oth:
    sd t4,16(sp)
    sw t2,-5816(t5)               # the other hero of the pair is "the player" for one more offer: his own menu gets it too
    jal 0x00174328
    ld a0,8(sp)
    lui t5,0x0035
    ld t4,16(sp)
    sw t4,-5816(t5)
co_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
hs_kind:                          # a0 = the victim, a1 = the captor, a3 = the move; t1 / t2 free. -> HF_SH (a pair) or HF_NO
    lw t2,8(a1)                   # the captor's object entry
    beq t2,zero,hk_pair           # none: as build 20
    nop
    lbu t1,4(t2)                  # its kind (00objentry + 4)
    addiu t2,zero,3               # BOSS
    beq t1,t2,hk_enemy
    addiu t2,zero,4               # ZAKO
    beq t1,t2,hk_enemy
    addiu t2,zero,6               # E_WEAPON
    beq t1,t2,hk_enemy
    addiu t2,zero,12              # L_BOSS
    beq t1,t2,hk_enemy
    addiu t2,zero,21              # L_ZAKO
    beq t1,t2,hk_enemy
    addiu t2,zero,23              # E_OBJ
    bne t1,t2,hk_pair             # not an enemy (a board, a gimmick, ...): the pair of build 20
    nop
hk_enemy:                         # an enemy's grab: a pair only for the shared mechanic, the last Xemnas's laser dome
    addiu t1,zero,0x106
    bne a3,t1,hk_no
    lw t2,8(a1)
    lw t2,0(t2)                   # the captor's object number
    addiu t1,zero,0x081F
    beq t2,t1,hk_pair
    addiu t1,zero,0x09CA
    bne t2,t1,hk_no
    nop
hk_pair:
    j HF_SH
    nop
hk_no:
    j HF_NO
    nop
hs_rc:                            # from hp_rc: a command of PLAYER 2'S hero in the DOME's pair is sent in PLAYER 1'S hero's name (a1 = the hero)
    lui t7,0x000E
    lw t1,0x7EA8(t7)              # the pair's captor: only the laser dome's boss
    beq t1,zero,hs_rc2
    nop
    lw t1,8(t1)
    beq t1,zero,hs_rc2
    nop
    lw t1,0(t1)
    addiu t2,zero,0x081F
    beq t1,t2,hs_rc1
    addiu t2,zero,0x09CA
    bne t1,t2,hs_rc2
    nop
hs_rc1:
    lui t7,0x000F
    lw t1,0x05CC(t7)              # the twin
    bne a1,t1,hs_rc2
    lui t7,0x0035
    lw a1,0x2400(t7)              # hs_rc: player 2's press goes in player 1's hero's name (the lasers aim at him; the pieces run on him)
hs_rc2:
    j RC_SEND
    nop
"""
HP_TRAPS = (                                       # (the script call, its table word, the game's handler, its inputs, the kind of its first argument)
    (102, 0x0034E030, 0x00171CC0, "H"),            # detach
    (74, 0x0034DF50, 0x001723D0, "H"),             # go idle
    (70, 0x0034DF30, 0x00173AE8, "H"),             # set a flag
    (71, 0x0034DF38, 0x00173B20, "H"),             # reset a flag
    (148, 0x0034E1A0, 0x00171460, "H"),            # set the place
    (79, 0x0034DF78, 0x00173C18, "H"),             # set the direction
    (11, 0x0034DD58, 0x00171150, "D"),             # motion start
    (12, 0x0034DD60, 0x001711B0, "D"),             # motion change
    (13, 0x0034DD68, 0x001711E0, "D"),             # motion push
    (129, 0x0034E108, 0x001712F8, "H"),            # blow (the script throws the hero off)
)
HP_SRC = """
hp_other:                         # in: a0 = a hero, a1 = a captor object (0 = any). Out: v0 = his partner in the living pair, or 0
    lui t7,0x000E
    lw t0,0x7EA0(t7)
    beq t0,zero,ho_no
    lw t1,0x7EA4(t7)
    beq a1,zero,ho_any
    lw t2,0x7EA8(t7)
    bne a1,t2,ho_no               # another captor
    nop
ho_any:
    beq a0,t0,ho_yes
    move v0,t1
    bne a0,t1,ho_no
    move v0,t0
ho_yes:
    lui t3,0x000F                 # the partner must still be a hero of this room
    lw t3,0x05CC(t3)
    beq v0,t3,ho_ok
    lui t3,0x0035
    lw t3,0x2400(t3)
    bne v0,t3,ho_no
    nop
ho_ok:
    jr ra
    nop
ho_no:
    jr ra
    move v0,zero

hp_ownset:                        # in: a0 = an object, a1 = the object that takes it. A hero whose OWN command is being answered: noted
    lui t7,0x000E
    lw t1,0x7C18(t7)              # the forty-seventh glue's note: the hero whose command is being answered
    beq t1,zero,hz_out
    nop
    bne t1,a0,hz_out
    lui t6,0x000F
    lw t6,0x05CC(t6)
    bne a0,t6,hz_p1
    lui t5,0x0035
    jr ra
    sw a1,0x7EC8(t7)              # the twin is in a move of his own command
hz_p1:
    lw t4,0x2400(t5)
    bne a0,t4,hz_out
    nop
    sw a1,0x7EC4(t7)              # player 1's hero is
hz_out:
    jr ra
    nop

hp_form:                          # in: a0 = a hero (the victim), a1 = the object that takes him. Out: v0 = the other hero when a pair is made (the caller mirrors the call); 0 = no pair; -1 = a stray capture of a bystander (the caller does not make it)
    lui t7,0x000F
    lw t6,0x05CC(t7)              # the twin
    beq t6,zero,hf_no
    lui t5,0x0035
    lw t4,0x2400(t5)              # player 1's hero
    beq t4,zero,hf_no
    lui t7,0x000E
    beq a0,t4,hf_p1               # the victim is player 1's hero
    nop
    bne a0,t6,hf_no               # he is no hero
    nop
    move t3,t4                    # the victim is the twin: the other hero is player 1's
    addiu t9,zero,2               # (the other hero's number in the hold note)
    lw t8,0x7EC8(t7)              # the victim's "own move" note
    b hf_h
    lw t0,0x7EC4(t7)              # the other hero's
hf_p1:
    move t3,t6
    addiu t9,zero,1
    lw t8,0x7EC4(t7)
    lw t0,0x7EC8(t7)
hf_h:
    bne t8,zero,hf_no             # the victim is in a move he started with his own command: it is his alone
    lui t2,0x0033
    lhu t2,-17696(t2)             # 0x0032BAE0: the world and the room
    addiu t1,zero,0x0908
    beq t2,t1,hf_no               # Shan-Yu's room: the fiftieth glue's own pair
    srl t2,a1,22
    addiu t2,t2,-6
    bne t2,zero,hf_no             # the captor is not an object
    nop
    beq a1,t4,hf_no               # a hero or a helper holds him (a Limit ...): as the game
    nop
    beq a1,t6,hf_no
    lw t2,0(a1)
    lui t1,0x0034
    ori t1,t1,0x5C08
    beq t2,t1,hf_no
    lw t2,0x7C18(t7)
    bne t2,zero,hf_no             # a hero's own command is being answered: he does that move alone
    lw t2,0x48C(t3)               # the other hero's unit slot
    beq t2,zero,hf_no
    nop
    lw t2,0(t2)
    beq t2,zero,hf_no             # he is down
    lw t2,0x160(t3)
    andi t2,t2,0x4000
    bne t2,zero,hf_join           # he is held
    lw t2,0xAEC(t3)
    bne t2,zero,hf_join           # he has a hooked script
    lw t2,0x154(t3)
    andi t2,t2,0xFFFF
    addiu t2,t2,-252
    sltiu t2,t2,20
    bne t2,zero,hf_join           # he is in a captured motion (the moves 0xFC .. 0x10F)
    nop
    bne t0,zero,hf_no             # he is free at this moment, but inside a move of his own command
    nop
    sw a0,0x7EA0(t7)              # A PAIR: the hero the script names, the other hero, the captor
    sw a0,0x7EBC(t7)              # (the hero the script named last)
    sw t3,0x7EA4(t7)
    sw a1,0x7EA8(t7)
    lw t2,-11076(t5)
    sw t2,0x7EAC(t7)
    sw zero,0x7EB4(t7)
    sw zero,0x7EB8(t7)
    jr ra
    move v0,t3
hf_join:                          # the other hero is busy: is he in THIS captor's sequence?
    lw t1,0x140(a1)               # the captor's word
    beq t1,zero,hf_no
    lw t2,0x240(t3)
    bne t2,t1,hf_jn               # not held by it at this moment: does the hold note say so?
    lw t2,0x160(t3)
    andi t2,t2,0x4000
    bne t2,zero,hf_stray
    nop
hf_jn:
    lw t2,0x7C0C(t7)
    bne t2,t1,hf_no
    lw t2,0x7C10(t7)
    bne t2,t9,hf_no
    lw t2,-11076(t5)
    lw t1,0x7C14(t7)
    subu t2,t2,t1
    sltiu t2,t2,90
    beq t2,zero,hf_no
    nop
hf_stray:                         # yes. Is the victim a bystander (free)?
    lw t2,0x160(a0)
    andi t2,t2,0x4000
    bne t2,zero,hf_no             # he is held himself: as the game
    lw t2,0xAEC(a0)
    bne t2,zero,hf_no             # he has a hooked script
    lw t2,0x154(a0)
    andi t2,t2,0xFFFF
    addiu t2,t2,-252
    sltiu t2,t2,20
    bne t2,zero,hf_no             # he is in a captured motion
    nop
    jr ra
    addiu v0,zero,-1              # A STRAY CAPTURE (the Groundshaker's attack hits the hero beside its ride): it is not made
hf_no:
    jr ra
    move v0,zero

hp_cap:                           # jump at 0x00180378, in front of the glues there. a0 = the captor's motion part, a1 = the victim, a2 = the move
    lui t7,0x000E
    lw t0,0x7EB0(t7)
    bne t0,zero,hq_go             # (the mirror's own call)
    nop
    addiu sp,sp,-96
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    sd a2,24(sp)
    sd a3,32(sp)
    swc1 f12,40(sp)
    swc1 f13,44(sp)
    swc1 f14,48(sp)
    lw t0,0x7EA0(t7)
    addiu a1,a0,-320              # the captor object
    beq t0,zero,hq_new
    ld a0,16(sp)
    jal hp_other                  # a pair lives: is the victim one of the two, and is this its captor
    nop
    beq v0,zero,hq_back
    lui t7,0x000E
    ld t1,16(sp)
    b hq_mir
    sw t1,0x7EBC(t7)              # the hero the script named
hq_new:
    jal hp_ownset                 # no pair: a hero's own command? then the move is noted as his own
    nop
    ld a1,8(sp)
    addiu a1,a1,-320
    jal hp_form                   # is this the start of a hold that takes the other hero too
    ld a0,16(sp)
    slt t0,v0,zero
    bne t0,zero,hq_skip           # a stray capture of a bystander
    nop
    beq v0,zero,hq_back
    lui t7,0x000E
hq_mir:
    addiu t1,zero,1
    sw t1,0x7EB0(t7)
    lui t5,0x0035
    lw t1,-11076(t5)
    sw t1,0x7EAC(t7)
    move a1,v0
    ld a0,8(sp)
    ld a2,24(sp)
    ld a3,32(sp)
    lwc1 f13,44(sp)
    lwc1 f14,48(sp)
    jal 0x00180378                # the same move on the other hero
    lwc1 f12,40(sp)
    lui t7,0x000E
    sw zero,0x7EB0(t7)
hq_back:
    ld ra,0(sp)
    ld a0,8(sp)
    ld a1,16(sp)
    ld a2,24(sp)
    ld a3,32(sp)
    lwc1 f12,40(sp)
    lwc1 f13,44(sp)
    lwc1 f14,48(sp)
    addiu sp,sp,96
hq_go:
    j CAP_NEXT
    nop
hq_skip:
    ld ra,0(sp)
    addiu sp,sp,96
    jr ra                         # the capture is not made; its answer is 0
    move v0,zero

hp_scr:                           # in: a0 = an object. Out: v0 = his partner when he is a hero of the living pair AND the call comes from the captor's script or from his own hooked piece of it, else 0
    lui t5,0x0035
    lw t8,-10076(t5)              # the running script (0x0034D8A4)
    beq t8,zero,hs_no
    lui t7,0x000E
    lw t8,56(t8)                  # its object
    lw t2,0x7EA8(t7)
    beq t8,t2,hs_ok               # the captor's own script
    nop
    bne t8,a0,hs_no               # ... or the hooked piece of it that runs AS this hero
    lui t6,0x000F
    lw t1,0xAEC(a0)
    beq t1,zero,hs_no
    lw t6,0x05CC(t6)              # the twin
    lw t1,0x7EC4(t7)              # player 1's "own move" note
    bne a0,t6,hs_o2
    nop
    lw t1,0x7EC8(t7)              # the twin's
hs_o2:
    bne t1,zero,hs_no             # the piece belongs to a move he started with his own command
    nop
hs_ok:
    j hp_other
    move a1,t2
hs_no:
    jr ra
    move v0,zero

hp_att:                           # the script call "attach" (1,18; was 0x00171C60). a0 = its inputs: the child, the parent, the bone, a flag, a callback, its value
    addiu sp,sp,-64
    sd ra,0(sp)
    sd a0,8(sp)
    jal 0x00171C60                # the game's attach for the hero the script names
    nop
    sd v0,16(sp)
    lui t7,0x000E
    lw t0,0x7EB0(t7)
    bne t0,zero,ha_out
    ld a0,8(sp)
    lw t1,0(a0)
    beq t1,zero,ha_out
    lw t2,4(a0)
    beq t2,zero,ha_out
    lw t0,0x7EA0(t7)
    lw a1,4(t2)                   # the parent object
    beq t0,zero,ha_new
    lw a0,4(t1)                   # the child object
    jal hp_other
    nop
    b ha_have
    nop
ha_new:
    sd a0,40(sp)
    sd a1,48(sp)
    jal hp_ownset
    nop
    ld a0,40(sp)
    jal hp_form
    ld a1,48(sp)
ha_have:
    slti t0,v0,1
    bne t0,zero,ha_out            # no pair (or a stray: the attach is done, nothing more)
    ld a0,8(sp)
    lw t1,0(a0)
    lw t2,4(t1)
    sd t2,24(sp)                  # the child the script named
    sw v0,4(t1)                   # ... is the other hero for one more call
    lw t3,16(a0)
    sd t3,32(sp)
    sw zero,16(a0)                # (without the script's callback: one hero's attach carries it)
    lui t7,0x000E
    sw t2,0x7EBC(t7)              # the hero the script named
    addiu t3,zero,1
    sw t3,0x7EB0(t7)
    lui t5,0x0035
    lw t3,-11076(t5)
    jal 0x00171C60
    sw t3,0x7EAC(t7)
    lui t7,0x000E
    sw zero,0x7EB0(t7)
    ld a0,8(sp)
    lw t1,0(a0)
    ld t2,24(sp)
    sw t2,4(t1)
    ld t3,32(sp)
    sw t3,16(a0)
ha_out:
    ld v0,16(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,64

hp_mirH:                          # a script call whose first input is an object's handle. a0 = the inputs, t0 = the game's handler
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a0,8(sp)
    sd t0,16(sp)
    jalr t0                       # the game's call for the object the script names
    nop
    sd v0,24(sp)
    lui t7,0x000E
    lw t1,0x7EA0(t7)
    beq t1,zero,mh_out            # no pair
    lw t1,0x7EB0(t7)
    bne t1,zero,mh_out
    ld a0,8(sp)
    lw t2,0(a0)
    beq t2,zero,mh_out
    nop
    jal hp_scr
    lw a0,4(t2)                   # the object
    beq v0,zero,mh_out
    ld a0,8(sp)
    lw t2,0(a0)
    lw t3,4(t2)
    sd t3,32(sp)
    sw v0,4(t2)                   # the other hero of the pair, for one more call
    lui t7,0x000E
    sw t3,0x7EBC(t7)              # the hero the script named
    addiu t3,zero,1
    sw t3,0x7EB0(t7)
    lui t5,0x0035
    lw t3,-11076(t5)
    sw t3,0x7EAC(t7)
    ld t0,16(sp)
    jalr t0
    nop
    lui t7,0x000E
    sw zero,0x7EB0(t7)
    ld a0,8(sp)
    lw t2,0(a0)
    ld t3,32(sp)
    sw t3,4(t2)
mh_out:
    ld v0,24(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48

hp_mirD:                          # a script call whose first input is the object itself. a0 = the inputs, t0 = the game's handler
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a0,8(sp)
    sd t0,16(sp)
    jalr t0
    nop
    sd v0,24(sp)
    lui t7,0x000E
    lw t1,0x7EA0(t7)
    beq t1,zero,md_out
    lw t1,0x7EB0(t7)
    bne t1,zero,md_out
    ld a0,8(sp)
    jal hp_scr
    lw a0,0(a0)                   # the object
    beq v0,zero,md_out
    ld a0,8(sp)
    lw t3,0(a0)
    sd t3,32(sp)
    sw v0,0(a0)
    lui t7,0x000E
    sw t3,0x7EBC(t7)              # the hero the script named
    addiu t3,zero,1
    sw t3,0x7EB0(t7)
    lui t5,0x0035
    lw t3,-11076(t5)
    sw t3,0x7EAC(t7)
    ld t0,16(sp)
    jalr t0
    nop
    lui t7,0x000E
    sw zero,0x7EB0(t7)
    ld a0,8(sp)
    ld t3,32(sp)
    sw t3,0(a0)
md_out:
    ld v0,24(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
@STUBS@
hp_rc:                            # jump from the forty-seventh glue's rc_drop2 ("this hero's command does nothing"): a0 = the source, a1 = the hero, t5 = 0x00350000
    lui t7,0x000E
    lw t2,0x7EA0(t7)              # both heroes are in this captor's hold: either may press, once a step
    beq t2,zero,hr_drop
    lw t1,0x7EA8(t7)
    bne t1,a0,hr_drop
    lw t1,0x7EA4(t7)
    beq t2,a1,hr_pair
    nop
    bne t1,a1,hr_drop
    nop
hr_pair:
    lw t2,0x7C1C(t7)              # the step of the last command that was sent
    lw t1,-11076(t5)
    beq t2,t1,hr_drop
    nop
    j RC_SEND
    nop
hr_drop:
    jr ra                         # one object holds one hero. This hero's command does nothing.
    nop

hp_note:                          # in: a0 = a hero (or 0), a1 = 1 (the twin) / 2 (player 1's). The hold note of the glues 36 / 39 / 47, each step
    beq a0,zero,hn_out
    lui t7,0x000E
    lui t5,0x0035
    lw t1,-11076(t5)              # the game's counter
    lw t2,0x160(a0)
    andi t2,t2,0x4000
    beq t2,zero,hn_hook           # not held at this moment
    lw t3,0x240(a0)               # the captor's word
    beq t3,zero,hn_hook
    nop
    sw t3,0x7C0C(t7)              # held: the note is written
    sw a1,0x7C10(t7)
    jr ra
    sw t1,0x7C14(t7)
hn_hook:
    lw t2,0xAEC(a0)
    beq t2,zero,hn_out            # no hooked script either
    lw t3,0x7C10(t7)
    bne t3,a1,hn_out              # the note is about the other hero
    nop
    sw t1,0x7C14(t7)              # still in the sequence (a hooked script): the note stays fresh
hn_out:
    jr ra
    nop

hp_busy:                          # in: a0 = a hero. Out: v0 = 1 when he is held, has a hooked script or is in a captured motion (the moves 0xFC .. 0x10F)
    lw t2,0x160(a0)
    andi t2,t2,0x4000
    bne t2,zero,hb_yes
    lw t2,0xAEC(a0)
    bne t2,zero,hb_yes
    lw t2,0x154(a0)
    andi t2,t2,0xFFFF
    addiu t2,t2,-252
    sltiu t2,t2,20
    bne t2,zero,hb_yes
    nop
    jr ra
    move v0,zero
hb_yes:
    jr ra
    addiu v0,zero,1

hp_bare:                          # in: a0 = a hero. Out: v0 = 1 when he is held (the held bit, or a captured motion) and has NO hooked script
    lw t2,0xAEC(a0)
    bne t2,zero,hx_no
    lw t2,0x160(a0)
    andi t2,t2,0x4000
    bne t2,zero,hx_yes
    lw t2,0x154(a0)
    andi t2,t2,0xFFFF
    addiu t2,t2,-252
    sltiu t2,t2,20
    bne t2,zero,hx_yes
    nop
hx_no:
    jr ra
    move v0,zero
hx_yes:
    jr ra
    addiu v0,zero,1

hp_free:                          # in: a0 = a hero. HE IS LET GO the way a boss's script throws a held hero off: detach, "motion start 16", "blow" with no speed (the sixtieth glue jumps here too)
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a0,8(sp)
    jal 0x001C0CD8                # is he attached
    nop
    beq v0,zero,hfr_1
    nop
    jal 0x001C0E60                # detach
    ld a0,8(sp)
hfr_1:
    ld a0,8(sp)
    mtc1 zero,f12
    mtc1 zero,f13
    addiu a0,a0,320
    jal 0x0017F488                # "motion start" (the script call (1,11)): motion 16
    addiu a1,zero,16
    sd zero,16(sp)
    sd zero,24(sp)
    ld a0,8(sp)
    jal 0x00186888                # "blow" (the script call (1,129)), no speed
    addiu a1,sp,16
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48

hp_own:                           # in: a0 = a hero (or 0), a1 = the address of his "own move" note (+ 8: his idle steps). The note is forgotten 45 idle steps after the move
    lw t0,0(a1)
    beq t0,zero,hw_out
    nop
    beq a0,zero,hw_clr
    nop
    addiu sp,sp,-16
    sd ra,0(sp)
    sd a1,8(sp)
    jal hp_busy
    nop
    ld a1,8(sp)
    ld ra,0(sp)
    addiu sp,sp,16
    bne v0,zero,hw_busy
    lw t1,8(a1)
    addiu t1,t1,1
    slti t2,t1,45
    bne t2,zero,hw_out
    sw t1,8(a1)
hw_clr:
    sw zero,0(a1)
hw_busy:
    sw zero,8(a1)
hw_out:
    jr ra
    nop

hp_tick:                          # from 0x00138538 (each step the field looks for START)
    addiu sp,sp,-64
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    sd s2,24(sp)
    sd s3,40(sp)
    lui t7,0x000F
    lw a0,0x05CC(t7)              # the twin
    jal hp_note
    addiu a1,zero,1
    lui t5,0x0035
    lw a0,0x2400(t5)              # player 1's hero
    jal hp_note
    addiu a1,zero,2
    lui t7,0x000F
    lw a0,0x05CC(t7)
    lui t7,0x000E
    jal hp_own                    # the twin's "own move" note
    addiu a1,t7,0x7EC8
    lui t5,0x0035
    lw a0,0x2400(t5)
    lui t7,0x000E
    jal hp_own                    # player 1's
    addiu a1,t7,0x7EC4
    lui t7,0x000E
    lw s0,0x7EA0(t7)              # the pair
    beq s0,zero,hk_out
    lw s1,0x7EA4(t7)
    move a0,s0
    jal hp_other                  # are both still heroes of this room
    move a1,zero
    beq v0,zero,hk_clear
    move a0,s1
    jal hp_other
    move a1,zero
    beq v0,zero,hk_clear
    nop
    jal hp_busy
    move a0,s0
    move s2,v0
    jal hp_busy
    move a0,s1
    move s3,v0
    lui t7,0x000E
    or t0,s2,s3
    bne t0,zero,hk_some
    lw t1,0x7EB4(t7)
    addiu t1,t1,1                 # nobody is held or hooked
    slti t2,t1,10
    bne t2,zero,hk_out
    sw t1,0x7EB4(t7)
hk_clear:
    lui t7,0x000E
    sw zero,0x7EA0(t7)            # the hold is over: the pair is forgotten
    sw zero,0x7EA4(t7)
    b hk_out
    sw zero,0x7EA8(t7)
hk_some:
    sw zero,0x7EB4(t7)
    lw t2,0x7EBC(t7)
    move a0,s1                    # the mirror hero = the one the script did not name last
    bne t2,s1,hk_m
    move t9,s2                    # (is the named one busy)
    move a0,s0
    move t9,s3
hk_m:
    sd a0,32(sp)
    sd t9,48(sp)
    jal hp_bare
    nop
    ld a0,32(sp)
    ld t9,48(sp)
    beq v0,zero,hk_keep           # the mirror hero is free, or has a hooked script of his own
    lui t7,0x000E
    beq t9,zero,hk_count          # the named hero is free: the mirror hero is left behind
    nop
    lui t5,0x0035
    lw t1,-11076(t5)
    lw t2,0x7EAC(t7)
    subu t1,t1,t2
    sltiu t1,t1,1200
    bne t1,zero,hk_keep           # the script named the pair less than 600 steps ago: the hold is alive
    nop
    b hk_free                     # no call for the pair for 600 steps: the mirror hero is let go
    nop
hk_count:
    lw t1,0x7EB8(t7)
    addiu t1,t1,1
    slti t2,t1,40
    bne t2,zero,hk_out
    sw t1,0x7EB8(t7)
hk_free:
    jal hp_free                   # a0 = the mirror hero
    nop
    b hk_clear
    nop
hk_keep:
    lui t7,0x000E
    sw zero,0x7EB8(t7)
hk_out:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    ld s2,24(sp)
    ld s3,40(sp)
    addiu sp,sp,64
    j TICK_NEXT
    move a0,zero
"""

if "--holdshared" in sys.argv:                     # (the sixty-fifth glue's fifth form: only a shared mechanic takes both heroes)
    for _o, _n in (('    ld a1,8(sp)\n    addiu a1,a1,-320\n    jal hp_form                   # is this the start of a hold that takes the other hero too\n    ld a0,16(sp)\n', '    ld a1,8(sp)\n    addiu a1,a1,-320\n    ld a3,24(sp)                  # (--holdshared) the move\n    jal hp_form                   # is this the start of a hold that takes the other hero too\n    ld a0,16(sp)\n'), ('    ld a0,40(sp)\n    jal hp_form\n    ld a1,48(sp)\n', '    ld a0,40(sp)\n    addiu a3,zero,-1              # (--holdshared) an attach never starts a pair\n    jal hp_form\n    ld a1,48(sp)\n'), ('    bne t0,zero,hf_no             # he is free at this moment, but inside a move of his own command\n    nop\n    sw a0,0x7EA0(t7)              # A PAIR: the hero the script names, the other hero, the captor\n', "    bne t0,zero,hf_no             # he is free at this moment, but inside a move of his own command\n    nop\n    j 0x000EE4D0                  # (--holdshared) hs_kind: an enemy pairs only for the laser dome, another captor as build 20\n    nop\nhf_sh:\n    sw a0,0x7EA0(t7)              # A PAIR: the hero the script names, the other hero, the captor\n")):
        assert HP_SRC.count(_o) == 1
        HP_SRC = HP_SRC.replace(_o, _n)
    _o2 = "    j RC_SEND\n    nop\nhr_drop:\n"
    assert HP_SRC.count(_o2) == 1
    HP_SRC = HP_SRC.replace(_o2, "    j 0x000EE4C8                  # (--holdshared) hs_rc: the other hero's press in the named hero's name\n    nop\nhr_drop:\n")
    _o = "hf_h:\n    bne t8,zero,hf_no             # the victim is in a move he started with his own command: it is his alone\n"
    assert HP_SRC.count(_o) == 1
    HP_SRC = HP_SRC.replace(_o, "hf_h:\n    j 0x000EE4C0                  # (--holdshared) hs_hf: the laser dome is never a hero's own move\n    nop\nhf_h2:\n    bne t8,zero,hf_no             # the victim is in a move he started with his own command: it is his alone\n")


def hp_stubs():
    """The sixty-fifth glue's entry for each wrapped script call: the game's handler in t0, then the mirror routine."""
    stubs = ""
    for num, tab, fn, kind in HP_TRAPS:
        stubs += "hp_t%d:\n    lui t0,0x%04X\n    j hp_mir%s\n    ori t0,t0,0x%04X\n" % (num, fn >> 16, kind, fn & 0xFFFF)
    return stubs


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = ROOT / (args[0] if args else "patches/merged-v7")
    raw_base = (BASE / NAME).read_bytes()
    assert hashlib.sha1(raw_base).hexdigest() == BASE_SHA1, "the base patch is not the expected file"
    order, words = [], {}
    for raw in raw_base.decode("utf-8").splitlines():
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
    elf = mips.Elf(str(ROOT / "local" / "iso-files" / "SLPM_666.75"))
    va, off, _fs = elf.segs[0]
    n_base, n_glue = len(order), 0

    def game_word(a):
        return struct.unpack_from("<I", elf.data, off + a - va)[0]

    def add_code(at, end, src, syms, what):
        code, labels = assemble(at, src, syms)
        code = [w if isinstance(w, int) else w[1] for w in code]
        assert CAVE_LO <= at and at + 4 * len(code) <= end <= CAVE_HI, "%s: %d words do not fit" % (what, len(code))
        for i, w in enumerate(code):
            a = at + 4 * i
            assert a not in words, "glue address already used: %08X" % a
            words[a] = w
            order.append(a)
            origin[a] = "glue 8 (%s)" % what
        return labels, len(code)

    def hook_game(a, expect, new, what):
        assert a not in words, "hook address already used: %08X" % a
        assert game_word(a) == expect, "hook %08X: the program has %08X, not %08X" % (a, game_word(a), expect)
        words[a] = new
        order.append(a)
        origin[a] = "glue 8 hook: " + what

    def hook_base(a, expect, new, what):
        assert words.get(a) == expect, "base word %08X is %s, not %08X" % (a, words.get(a), expect)
        words[a] = new
        origin[a] = origin.get(a, "") + " | glue 8: " + what

    def jal(t):
        return (3 << 26) | ((t >> 2) & 0x3FFFFFF)

    if "--no-eitherspawn" not in sys.argv:                                 # thirtieth glue
        labels, n = add_code(ESPAWN_AT, ESPAWN_END, ESPAWN_SRC, {"POS_OF": POS_OF, "RI_OUT": RI_OUT},
                             "enemy spawn zones also react to the twin")
        a, w0 = ESPAWN_BASE_WORD
        rel = (labels["sp_either"] - (a + 4)) // 4
        assert -0x8000 <= rel < 0x8000
        hook_base(a, w0, 0x10400000 | (rel & 0xFFFF), "player 1's hero is not inside: ask sp_either")
        n_glue += n

    if "--no-revenge" not in sys.argv:                                     # thirty-first glue
        labels, n = add_code(RV_AT, RV_END, RV_SRC, {"REVENGE_BITS": REVENGE_FACTOR_BITS},
                             "a hero's hit adds 0.75 of its revenge value while there are two heroes")
        a, w0, w1 = RV_HOOK
        hook_game(a, w0, jal(labels["rv_scale"]), "the revenge add goes through rv_scale")
        hook_game(a + 4, w1, w0, "(cvt.s.w f1,f1, now in the delay slot)")
        n_glue += n + 2

    if "--no-getup" not in sys.argv:                                       # thirty-second glue
        labels, n = add_code(GU_AT, GU_END, GU_SRC, {}, "a hero gets up one step above the low-HP line")
        a, w0 = GU_BASE_WORD
        hook_base(a, w0, jal(labels["gu_fix"]), "the timed get-up goes through gu_fix")
        n_glue += n

    if "--no-keychange" not in sys.argv:                                   # thirty-third glue
        labels, n = add_code(WC_AT, WC_END, WC_SRC, {}, "a weapon change in the menu also rebuilds the twin's weapon")
        a, w0 = WC_HOOK
        hook_game(a, w0, (2 << 26) | ((labels["wc_both"] >> 2) & 0x3FFFFFF), "the menu's weapon change goes through wc_both")
        n_glue += n + 1

    if "--no-twoforms" not in sys.argv:                                    # thirty-fourth glue
        fm_src = FM_SRC
        for k in range(1, 6):
            fm_src = fm_src.replace("@NEED%d@" % k, "0x%08X" % (0 if "--no-formbase" in sys.argv else FORM_NEED[k] + 0x10000))
        labels, n = add_code(FM_AT, FM_END, fm_src, {}, "two Drive Forms at once: the form lock is judged for each hero")
        for a, w0, kind, label, what in FM_HOOKS:
            new = 0 if kind == "nop" else ((3 if kind == "jal" else 2) << 26) | ((labels[label] >> 2) & 0x3FFFFFF)
            hook_game(a, w0, new, what)
        n_glue += n + len(FM_HOOKS)

    if "--no-formfiles" not in sys.argv:                                   # thirty-fifth glue
        labels, n = add_code(FK_AT, FK_END, FK_SRC, {}, "a hero's form files stay while the other hero changes his form")
        for a, w0, label, what in FK_HOOKS:
            hook_game(a, w0, jal(labels[label]), what)
        n_glue += n + len(FK_HOOKS)

    if "--no-nearcb" not in sys.argv:                                      # thirty-sixth glue
        labels, n = add_code(NC_AT, NC_END, NC_SRC, {}, "a callback of an object's script: the hero in its move, or the nearer hero, is the player")
        a, w0, w1 = NC_HOOK
        hook_game(a, w0, (2 << 26) | ((labels["nc_trig"] >> 2) & 0x3FFFFFF), "a callback of an object's script goes through nc_trig")
        hook_game(a + 4, w1, 0, "(sd s0,0(sp) is done in nc_body)")
        n_glue += n + 2

    if "--no-mickey" not in sys.argv:                                      # thirty-seventh glue
        src = MK_SRC.replace("@TWO@", "" if "--mickey1" in sys.argv else MK_TWO)
        labels, n = add_code(MK_AT, MK_END, src, {}, "King Mickey's rescue for two")
        for a, w0, kind, label, what in MK_HOOKS:
            hook_game(a, w0, ((3 if kind == "jal" else 2) << 26) | ((labels[label] >> 2) & 0x3FFFFFF), what)
        n_glue += n + len(MK_HOOKS)

    if "--no-reactheld" not in sys.argv:                                   # thirty-eighth glue
        labels, n = add_code(RH_AT, RH_END, RH_SRC, {}, "the command of a paired move goes to the hero who is held in it")
        a, w0 = RH_BASE_WORD
        hook_base(a, w0, jal(labels["ro2"]), "a motion offers a command: the twin when he is the source or is held by the source")
        n_glue += n

    if "--no-thinkheld" not in sys.argv:                                   # thirty-ninth glue
        labels, n = add_code(NT_AT, NT_END, NT_SRC, {}, "an object that holds a hero in a paired move thinks with that hero as the player")
        a, w0 = NT_BASE_WORD
        hook_base(a, w0, (2 << 26) | ((labels["nt_held"] >> 2) & 0x3FFFFFF), "an object thinks: first the hero it holds, then the twelfth glue's rule")
        n_glue += n

    if "--no-helperform" not in sys.argv:                                  # fortieth glue
        labels, n = add_code(HF_AT, HF_END, HF_SRC, {}, "a helper whom the twin's Drive Form uses stays away when a room is built")
        a, w0 = HF_HOOK
        hook_game(a, w0, jal(labels["hf_either"]), "a helper enters a room: is he used by player 1's form or by the twin's")
        n_glue += n + 1

    if "--no-formbase" not in sys.argv and "--no-twoforms" not in sys.argv:     # forty-first glue
        labels, n = add_code(FB_AT, FB_END, FB_SRC, {}, "the files of a second Drive Form are asked for with a number base behind the files in use")
        a, w0 = FB_HOOK
        hook_game(a, w0, jal(labels["fb_req"]), "the form task asks for the form's files: behind the other hero's form files")
        n_glue += n + 1

    if "--no-helperback" not in sys.argv:                                  # forty-second glue
        labels, n = add_code(HB_AT, HB_END, HB_SRC, {}, "when one of two Drive Forms ends, the other form's helpers stay away")
        for a, w0, what in HB_HOOKS:
            hook_game(a, w0, jal(labels["hb_back"]), what)
        n_glue += n + len(HB_HOOKS)

    if "--no-heroscript" not in sys.argv:                                  # forty-third glue
        labels, n = add_code(HS_AT, HS_END, HS_SRC, {}, "the script a paired move attaches to the twin runs with the twin as the player")
        a, w0 = HS_HOOK
        hook_game(a, w0, jal(labels["hs_tick"]), "a hero's attached script runs: the twin's with the twin as the player")
        n_glue += n + 1

    if "--no-captureform" not in sys.argv:                                 # forty-fourth glue
        labels, n = add_code(CF_AT, CF_END, CF_SRC, {}, "a boss's capture form takes the hero the trick is played on")
        for a, w0, kind, label, what in CF_HOOKS:
            hook_game(a, w0, ((3 if kind == "jal" else 2) << 26) | ((labels[label] >> 2) & 0x3FFFFFF), what)
        n_glue += n + len(CF_HOOKS)

    if "--no-scriptplayer" not in sys.argv:                                # forty-fifth glue
        labels, n = add_code(TP_AT, TP_END, TP_SRC, {}, "a script that asks for the player gets the hero its object holds")
        a, w0 = TP_HOOK
        hook_game(a, w0, jal(labels["tp_player"]), "trap_sysobj_player: the hero the running script's object holds, else the game's answer")
        n_glue += n + 1

    if "--playernear" in sys.argv and "--no-scriptplayer" not in sys.argv:             # forty-sixth glue (experiment)
        labels, n = add_code(TQ_AT, TQ_END, TQ_SRC, {}, "a script's player: the held hero, else the nearer hero, in every runner")
        hook_base(TP_HOOK[0], jal(TP_AT), jal(labels["tp_player2"]), "trap_sysobj_player: held, held a moment ago, else the NEARER hero")
        if "--no-captureform" not in sys.argv:
            hook_base(0x001741EC, jal(CF_AT), jal(labels["cf_who2"]), "trap_player_capture_form: the same hero as the script's player")
        n_glue += n

    if "--no-sender" not in sys.argv and "--no-nearcb" not in sys.argv:    # forty-seventh glue (it sits on the thirty-sixth)
        rc_src = RC_SRC
        if "--together" in sys.argv:                                       # (the experiment of the fiftieth glue)
            x = """rc_drop:
    jr ra                         # yes: one object holds one hero. This hero's command does nothing.
    nop
"""
            assert rc_src.count(x) == 1
            rc_src = rc_src.replace(x, """rc_drop:
    lui t7,0x000E
    lw t2,0x7E38(t7)              # (--together) a pair in a move: each of the two presses for himself
    beq t2,zero,rc_drop2
    nop
    beq t2,a1,rc_send
    lw t2,0x7E34(t7)
    beq t2,a1,rc_send
    nop
rc_drop2:
    jr ra                         # one object holds one hero. This hero's command does nothing.
    nop
""")
            if "--holdpair" in sys.argv:                                   # (the sixty-fifth glue's pair: both heroes are in the captor's hold)
                x = """rc_drop2:
    jr ra                         # one object holds one hero. This hero's command does nothing.
    nop
"""
                assert rc_src.count(x) == 1
                rc_src = rc_src.replace(x, """rc_drop2:
    j HP_RC                       # (--holdpair) the sixty-fifth glue's hp_rc: both heroes of a hold's pair may press
    nop
""")
        rc_syms = {}
        if "--holdpair" in sys.argv:
            _c, hp_l = assemble(HP_AT, HP_SRC.replace("@STUBS@", hp_stubs()), {"TICK_NEXT": 0, "CAP_NEXT": 0, "RC_SEND": 0})
            rc_syms["HP_RC"] = hp_l["hp_rc"]
        labels, n = add_code(RC_AT, RC_END, rc_src, rc_syms, "a hero's Reaction Command: the sender is the player; one object holds one hero")
        rc_send_at = labels["rc_send"]
        a, w0 = RC_HOOK
        hook_game(a, w0, jal(labels["rc_one"]), "a hero's command calls back its source: not while the source holds the other hero; the sender is noted")
        hook_base(NC_HOOK[0], (2 << 26) | ((NC_AT >> 2) & 0x3FFFFFF), (2 << 26) | ((labels["ns_pre"] >> 2) & 0x3FFFFFF),
                  "a callback: first the sender rule (ns_pre), then the thirty-sixth glue")
        n_glue += n + 1

    if "--ownrec" in sys.argv:                                             # forty-eighth glue (plan row 39; not in builds 13 / 14)
        labels, n = add_code(RT_AT, RT_END, RT_SRC, {}, "the second hero's unit slot reads a character record of his own")
        a, w0, w1 = RT_HOOK
        hook_game(a, w0, (2 << 26) | ((labels["t_load"] >> 2) & 0x3FFFFFF), "load a slot's stats: which record (the twin's own record T)")
        hook_game(a + 4, w1, 0, "(daddu s1,a1,zero is done in t_load)")
        n_glue += n + 2

    if "--ownmenu" in sys.argv:                                            # forty-ninth glue (plan row 39; not in builds 13 / 14)
        assert "--ownrec" in sys.argv, "--ownmenu needs --ownrec"
        labels, n = add_code(RM_AT, RM_END, RM_SRC, {}, "player 2's pause menu shows and edits his own armour and accessory places")
        a, w0 = RM_OPEN
        hook_game(a, w0, jal(labels["mo_open"]), "START opens the main menu: when player 2 pressed it, the places change places first")
        a, w0 = RM_TICK
        hook_base(a, w0, jal(labels["ms_tick"]), "the field looks for START: first, has player 2's menu gone? (then the second glue's pad_both)")
        a, w0 = RM_LOAD
        hook_game(a, w0, (2 << 26) | ((labels["or_load"] >> 2) & 0x3FFFFFF), "a save file goes into the save data: the menu flag is cleared")
        a, w0 = RM_NEW
        hook_game(a, w0, jal(labels["or_new"]), "the save data are made new: the menu flag is cleared")
        n_glue += n + 3

    if "--together" in sys.argv:                                           # fiftieth glue, an experiment (plan row 9, second half)
        tg_src = TG_SRC
        if "--together-far" in sys.argv:                                   # (test of the test: no distance limit)
            x = "    bc1f tn_out                   # too far: he stays free"
            assert tg_src.count(x) == 1
            tg_src = tg_src.replace(x, "    nop                           # (--together-far: any distance)")
        tick_next = words[0x00138538]                                      # jal pad_both, or jal ms_tick with --ownmenu
        assert (tick_next >> 26) == 3
        hook_next = words.get(0x00177510, game_word(0x00177510))           # jal hs_tick (forty-third glue), or the game's jal 0x0016CD48
        assert (hook_next >> 26) == 3
        labels, n = add_code(TG_AT, TG_END, tg_src, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2, "HOOK_NEXT": (hook_next & 0x3FFFFFF) << 2},
                             "EXPERIMENT: both heroes in a boss's paired move (the second hero gets his own copy of the hooked script)")
        if 0x00177510 in words:
            hook_base(0x00177510, hook_next, jal(labels["th_tick"]), "a hero's hooked script runs: noted")
        else:
            hook_game(0x00177510, hook_next, jal(labels["th_tick"]), "a hero's hooked script runs: noted")
        hook_game(0x00171FE4, 0x0C05B3C0, jal(labels["th_new"]), "a script is hooked onto a hero: the other hero of the pair gets his own copy")
        a, w0, w1 = TG_HOOK
        hook_game(a, w0, (2 << 26) | ((labels["tg_cap"] >> 2) & 0x3FFFFFF), "the paired-move routine: first tg_cap")
        hook_game(a + 4, w1, 0, "(swc1 f20,32(sp) is done in tg_go)")
        hook_base(0x00138538, tick_next, jal(labels["tg_tick"]), "the field's START look-out: first the release rule of a move with two heroes")
        hook_base(0x00189E3C, jal(RH_AT), jal(labels["tg_ro"]), "a motion offers a command: to both heroes of a move with two")
        n_glue += n + 2

    if "--ship2hit" in sys.argv:                                           # fifty-first glue, an experiment (player 2's Gummi ship can be hit)
        gm_next = words[0x00167E90]                                        # the base's jal gm_pad (twenty-sixth glue)
        assert (gm_next >> 26) == 3
        syms = {"GM_NEXT": (gm_next & 0x3FFFFFF) << 2}
        src = GS_SRC
        if "--ship2first" in sys.argv:                                     # (test of the test: only ship 2 is asked)
            x = """    jal gt_orig                   # ship 1 first
    nop
    bne v0,zero,gt_done           # ship 1 is touched: as the game
"""
            assert GS_SRC.count(x) == 1
            gs_src = GS_SRC.replace(x, """    nop                           # (--ship2first: ship 1 is not asked)
    nop
    nop
""")
        else:
            gs_src = GS_SRC
        src = gs_src
        for k in ("TEST", "ABLE", "HIT", "DMG", "REP"):                    # first pass: where the routines stand
            src = src.replace("@J_%s_HI@" % k, "0").replace("@J_%s_LO@" % k, "0")
        src = src.replace("@JAL_LOW_HI@", "0").replace("@JAL_LOW_LO@", "0")
        code, labels = assemble(GS_AT, src, syms)
        src = gs_src
        w_low = jal(labels["gs_low"])
        src = src.replace("@JAL_LOW_HI@", "0x%04X" % (w_low >> 16)).replace("@JAL_LOW_LO@", "0x%04X" % (w_low & 0xFFFF))
        for k, lab in (("TEST", "gs_test"), ("ABLE", "gs_able"), ("HIT", "gs_hit"), ("DMG", "gs_dmg"), ("REP", "gs_rep")):
            j = (2 << 26) | ((labels[lab] >> 2) & 0x3FFFFFF)
            src = src.replace("@J_%s_HI@" % k, "0x%04X" % (j >> 16)).replace("@J_%s_LO@" % k, "0x%04X" % (j & 0xFFFF))
        labels2, n = add_code(GS_AT, GS_END, src, syms, "EXPERIMENT: player 2's Gummi ship can be hit and has its own hull")
        assert labels2 == labels
        hook_base(0x00167E90, gm_next, jal(labels["gs_inst"]), "the controller task: first the four jumps into a fresh flight module, then gm_pad")
        n_glue += n

    if "--ship2score" in sys.argv:                                         # sixty-sixth glue (the Gummi flight counts player 2's points)
        assert "--ship2hit" in sys.argv, "--ship2score needs --ship2hit"
        gq_next = words[0x00167E90]                                        # the fifty-first glue's jal gs_inst
        assert (gq_next >> 26) == 3
        syms = {"GQ_NEXT": (gq_next & 0x3FFFFFF) << 2}
        _code, gq_labels = assemble(GQ_AT, gq_source(None), syms)
        labels, n = add_code(GQ_AT, GQ_END, gq_source(gq_labels), syms, "the Gummi flight counts player 2's points")
        assert labels == gq_labels
        hook_base(0x00167E90, gq_next, jal(labels["gq_inst"]), "the controller task: first the sixty-sixth glue's jumps into a fresh flight module")
        n_glue += n
        gq_own = list(range(GQ_OWN_AT, GQ_OWN_AT + 9 * 388, 4)) + list(range(GQ_OWN_LAST, GQ_OWN_LAST + 388, 4))
        assert GQ_OWN_LAST + 388 <= GQ_OWN_END and (GQ_OWN_AT >> 16) == (GQ_OWN_END >> 16) == 0x000E
        gq_own_check = True                                                # (checked at the end: no routine may lie in the own pictures' memory)

    if "--carpet2" in sys.argv:                                            # fifty-second glue, an experiment (a carpet under player 2's hero)
        tick_next = words[0x00138538]                                      # jal pad_both, or the glue that sits there already
        assert (tick_next >> 26) == 3
        labels, n = add_code(GC_AT, GC_END, GC_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "EXPERIMENT: a second carpet, under player 2's hero")
        hook_base(0x00138538, tick_next, jal(labels["gc_tick"]), "the field's START look-out: first, is a second carpet wanted")
        hook_game(0x00350FF8, 0x001B2DB8, labels["gc_upd"], "the carpet's state routine: the second carpet follows player 2's hero")
        hook_game(0x00178E1C, 0x8E041068, jal(labels["gc_c1"]), "the hero's command starts a carpet motion: on his own carpet")
        hook_game(0x00178E34, 0x8E041068, jal(labels["gc_c1"]), "the same, second call")
        hook_game(0x00178E8C, 0x3C0F0035, jal(labels["gc_c2"]), "the end of that motion: his own carpet goes back to rest")
        hook_game(0x001B2A04, 0x8DE41068, jal(labels["gc_c3"]), "the riding state's motion: on his own carpet")
        n_glue += n + 5

    if "--norec" in sys.argv:                                              # fifty-third glue, an experiment (a hero without a record)
        labels, n = add_code(GN_AT, GN_END, GN_SRC, {}, "EXPERIMENT: a hero without a character record has no item places")
        hook_game(0x001BE9DC, 0x904E0012, (2 << 26) | ((labels["gn_cnt"] >> 2) & 0x3FFFFFF), "the command menu counts the hero's item places: first, is there a record")
        hook_game(0x001BE9E0, 0x31CF00FF, 0, "(andi t7,t6,0xFF is done in gn_cnt)")
        n_glue += n + 2

    if "--escape2" in sys.argv:                                            # fifty-fourth glue, an experiment (a second hero in the carpet escape)
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        labels, n = add_code(GE_AT, GE_END, GE_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "EXPERIMENT: a second hero in the carpet escape, with his own carpet")
        hook_base(0x00138538, tick_next, jal(labels["ge_tick"]), "the field's START look-out: first, the second escape hero and his carpet")
        hook_game(0x00362E18, 0x002E1D28, labels["ge_upd"], "the escape carpet's state routine: the second carpet follows player 2's hero")
        n_glue += n + 1

    if "--sidecar2" in sys.argv:                                           # fifty-fifth glue, an experiment (a second hero on the sidecar)
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        labels, n = add_code(GZ_AT, GZ_END, GZ_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "EXPERIMENT: a second hero on the sidecar gets the sidecar's state")
        hook_base(0x00138538, tick_next, jal(labels["gz_tick"]), "the field's START look-out: first, the second sidecar hero's state")
        n_glue += n

    if "--twinmake" in sys.argv:                                           # fifty-sixth glue, an experiment (a second hero made at run time)
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        labels, n = add_code(GW_AT, GW_END, GW_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "EXPERIMENT: a second hero made at run time in the three one-hero small games")
        hook_base(0x00138538, tick_next, jal(labels["gw_tick"]), "the field's START look-out: first, is a second special hero wanted")
        n_glue += n

    if "--hudowner" in sys.argv:                                           # fifty-seventh glue (the HUD's owner is player 1's hero or nobody)
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        labels, n = add_code(GH_AT, GH_END, GH_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                             "the HUD's owner is player 1's hero or nobody, never the twin, never a hero without an HP record")
        hook_base(0x00138538, tick_next, jal(labels["gh_tick"]), "the field's START look-out: first, is the HUD's owner right")
        hook_base(0x000F0D8C, jal(0x0013DDC0), jal(labels["gh_set"]), "the twin goes away: player 1's hero becomes the HUD's owner only with an HP record")
        n_glue += n

    if "--ownabil" in sys.argv:                                            # fifty-eighth glue, an experiment (player 2's own ability switches)
        assert "--ownrec" in sys.argv and "--ownmenu" in sys.argv, "--ownabil needs --ownrec --ownmenu"
        labels, n = add_code(GA_AT, GA_END, GA_SRC, {}, "EXPERIMENT: player 2 switches his own abilities")
        at = [x for x in range(RT_AT, RT_END, 4) if words.get(x) == 0xADCB0030]           # sw t3,0x30(t6): the last store of glue 48's hero path
        assert len(at) == 1, at
        hook_base(at[0], 0xADCB0030, (2 << 26) | ((labels["ab_view"] >> 2) & 0x3FFFFFF), "the view T is made: player 2's ability switches go in")
        at = [x for x in range(RM_AT, RM_END, 4) if words.get(x) == 0x03E00008]           # the first jr ra of glue 49: the end of ow_swap
        hook_base(min(at), 0x03E00008, (2 << 26) | ((labels["ab_swap"] >> 2) & 0x3FFFFFF), "player 2's menu opens or goes: the ability switches change places too")
        hook_game(0x00188B90, 0x01A57825, (2 << 26) | ((labels["ab_add"] >> 2) & 0x3FFFFFF), "a new ability goes into a record's list: player 2 gets its switch too")
        hook_game(0x00188B94, 0x03E00008, 0x01A57825, "(or t7,t5,a1 moved into the delay slot)")
        n_glue += n + 2

    if "--onevictim" in sys.argv:                                          # fifty-ninth glue (a boss that holds one hero captures that hero)
        cap_next = words.get(0x00180378)
        assert cap_next is not None and (cap_next >> 26) == 2, "--onevictim needs --together (the jump at 0x00180378)"
        labels, n = add_code(GK_AT, GK_END, GK_SRC, {"CAP_NEXT": (cap_next & 0x3FFFFFF) << 2},
                             "a boss that holds one hero makes its further captures on that hero")
        hook_base(0x00180378, cap_next, (2 << 26) | ((labels["gk_cap"] >> 2) & 0x3FFFFFF), "the paired-move routine: first, does this captor hold the other hero")
        n_glue += n

    if "--holdwatch" in sys.argv:                                          # sixtieth glue (no hero is held for ever)
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        gy_src = GY_SRC
        if "--holdwatch-test" in sys.argv:                                 # (test of the release itself: the limit is 100 steps)
            assert gy_src.count("slti t1,t4,%d" % GY_LIMIT) == 1
            gy_src = gy_src.replace("slti t1,t4,%d" % GY_LIMIT, "slti t1,t4,100")
        gy_syms = {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2}
        if "--holdpair" in sys.argv:                                       # (the sixty-fifth glue's fourth form)
            _c, hp_l = assemble(HP_AT, HP_SRC.replace("@STUBS@", hp_stubs()), {"TICK_NEXT": 0, "CAP_NEXT": 0, "RC_SEND": 0})
            gy_syms["HP_FREE"] = hp_l["hp_free"]
            x = """    andi t1,t2,0xFFFC
    addiu t0,zero,0x00FC
    bne t1,t0,gy_clr              # he is in no captured motion
"""
            assert gy_src.count(x) == 1
            gy_src = gy_src.replace(x, """    addiu t1,t2,-252
    sltiu t1,t1,20
    beq t1,zero,gy_clr            # he is in no captured motion (the moves 0xFC .. 0x10F)
""")
            x = gy_src[gy_src.index("    addiu sp,sp,-16\n    sd ra,0(sp)\n    sd a0,8(sp)\n    mtc1 zero,f12"):gy_src.index("gy_new:")]
            assert "0x0016BD60" in x and "0x0017EFA0" in x
            gy_src = gy_src.replace(x, """    j HP_FREE                     # (--holdpair) the sixty-fifth glue's "let him go": detach, "motion start 16", "blow"
    nop
""")
        labels, n = add_code(GY_AT, GY_END, gy_src, gy_syms,
                             "a hero in one and the same captured motion for 1,800 steps is let go")
        hook_base(0x00138538, tick_next, jal(labels["gy_tick"]), "the field's START look-out: first, is a hero held too long")
        n_glue += n

    if "--itemsync" in sys.argv:                                           # sixty-first glue (player 2's item list shows the places as they are)
        gn_next = words.get(0x001BE9DC)
        assert "--ownrec" in sys.argv and gn_next is not None and (gn_next >> 26) == 2, "--itemsync needs --ownrec and --norec (the jump at 0x001BE9DC)"
        labels, n = add_code(GI_AT, GI_END, GI_SRC, {"GN_CNT": (gn_next & 0x3FFFFFF) << 2},
                             "player 2's item list is built from the item places as they are")
        hook_base(0x001BE9DC, gn_next, (2 << 26) | ((labels["gi_sync"] >> 2) & 0x3FFFFFF), "the command menu counts the hero's item places: first, the view's places are made fresh")
        n_glue += n

    if "--ownitems" in sys.argv:                                           # sixty-second glue (player 2's own item places, stock and shortcuts; every gain for each)
        assert all(o in sys.argv for o in ("--ownrec", "--ownmenu", "--ownabil", "--norec", "--itemsync")), "--ownitems needs --ownrec --ownmenu --ownabil --norec --itemsync"
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        _c, ga_labels = assemble(GA_AT, GA_SRC, {})
        labels, n = add_code(GO_AT, GO_END, GO_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2, "GN_CNT": GN_AT},
                             "player 2's own item places, stock and shortcuts; every thing the game gives is there for each player")

        def jmp(t):
            return (2 << 26) | ((t >> 2) & 0x3FFFFFF)
        hook_base(0x00138538, tick_next, jal(labels["oi_tick"]), "the field's START look-out: first, are player 2's item things made")
        hook_base(ga_labels["as_out"], 0x03E00008, jmp(labels["oi_swap"]), "player 2's menu opens or goes: his item places, stock and shortcuts change places too")
        at = [x for x in range(GA_AT, GA_END, 4) if words.get(x) == jmp(0x001A1214)]
        assert len(at) == 1, at
        hook_base(at[0], jmp(0x001A1214), jmp(labels["oi_tview"]), "the view T is made: player 2's item places go in")
        hook_base(0x001BE9DC, jmp(GI_AT), jmp(labels["oi_list"]), "the command menu counts the hero's item places: first, the view gets player 2's places")
        hook_game(0x00176EA4, 0x0C05A81C, jal(labels["oi_use"]), "an item is used: the twin's leaves HIS place")
        hook_game(0x00253BDC, jal(0x001A3710), jal(labels["oi_refill"]), "the game fills empty places: the other player's too, from his own stock")
        hook_game(0x001918A8, jmp(0x001A3710), jmp(labels["oi_refill"]), "the same, each step while there is no fight (the fight watcher's jump)")
        hook_game(0x001A31FC, jal(0x001A32C8), jal(labels["oi_gain"]), "a thing goes into the bag: what the game gives is there for each player")
        hook_game(0x001A3298, jal(0x00188A28), jal(labels["oi_gain2"]), "a fight item goes into the hero's place: the other player gets one too")
        hook_game(0x001A3430, 0x1000FFF7, jmp(labels["oi_sc"]), "a new spell takes an empty shortcut: player 2's too")
        hook_game(0x001BED98, 0x25EFBB30, jal(labels["sc_base"]), "the shortcut list of a command menu: the twin's is built from HIS four shortcuts")
        n_glue += n + 7

    if "--ownkey" in sys.argv:                                             # sixty-third glue (player 2's own Keyblade)
        assert "--ownitems" in sys.argv and "--no-keychange" not in sys.argv, "--ownkey needs --ownitems and the thirty-third glue"
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        _c, go_labels = assemble(GO_AT, GO_SRC, {"TICK_NEXT": 0, "GN_CNT": GN_AT})
        labels, n = add_code(KB_AT, KB_END, KB_SRC, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2, "WC_BOTH": WC_AT},
                             "player 2's own Keyblade")

        def jmp2(t):
            return (2 << 26) | ((t >> 2) & 0x3FFFFFF)
        hook_base(0x00138538, tick_next, jal(labels["kb_tick"]), "the field's START look-out: first, player 2's Keyblade is made and follows the story")
        hook_base(go_labels["ow_out"] + 4, 0x03E00008, jmp2(labels["kb_swap"]), "player 2's menu opens or goes: his Keyblade and player 1's change places in the hero's record")
        at = [x for x in range(GO_AT, GO_END, 4) if words.get(x) == jmp2(0x001A1214)]
        assert len(at) == 1, at
        hook_base(at[0], jmp2(0x001A1214), jmp2(labels["kb_tview"]), "the view T is made: player 2's Keyblade goes in")
        hook_base(0x000F0344, jal(0x00179FD0), jal(labels["kb_fact"]), "lane E's call of the player factory: noted while it runs")
        hook_base(0x000F03C0, 0x03E00008, jmp2(labels["kb_after"]), "the end of lane E's e_wrap: the twin gets his Keyblade as soon as the heroes are sorted out")
        hook_game(0x0016F680, jal(0x00188FE0), jal(labels["kb_rec"]), "a body's weapon item: the twin's first hand gets player 2's Keyblade while he is built")
        hook_game(0x0016ECDC, jal(0x0016EF58), jal(labels["kb_req"]), "a body asks for its weapon's files: player 2's Keyblade's files too (number 2303)")
        hook_game(0x001A8B20, jmp2(0x0016FAB0), jmp2(labels["kb_size"]), "the hero's block of the file pool: 256 KB more, for a second Keyblade")
        hook_base(0x002933D0, jmp2(WC_AT), jmp2(labels["kc_menu"]), "the menu's weapon change: first kc_menu (each player's own Keyblade), then glue 33")
        hook_game(0x0017607C, jal(0x00170888), jal(labels["kc_load"]), "the weapon change's load: player 2's files are asked for again or let go")
        hook_game(0x00176204, jal(0x00185468), jal(labels["kb_ctor"]), "a weapon object is made: the twin's own Keyblade binds to its files (number 2303)")
        n_glue += n + 5

    if "--bindname" in sys.argv:                                           # sixty-fourth glue (an object is bound to its files by name when the number does not fit)
        labels, n = add_code(BN_AT, BN_END, BN_SRC, {}, "an object is bound to its files by their name when the number does not fit")
        hook_game(0x001A9238, jal(0x001708F8), jal(labels["bn_find"]), "an object binds to its model file: by name when the number finds nothing")
        hook_game(0x001A9288, jal(0x001708F8), jal(labels["bn_find"]), "an object binds to its effect file: by name when the number finds nothing")
        n_glue += n + 2

    if "--holdpair" in sys.argv:                                           # sixty-fifth glue (both heroes inside the same hold of a boss)
        assert "--together" in sys.argv, "--holdpair needs --together (the forty-seventh glue's pair exit)"
        assert "--holdpads" not in sys.argv or "--holdshared" not in sys.argv, "--holdshared leaves the sixty-eighth glue out: each hero keeps his own controller"
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        cap_next = words.get(0x00180378)
        assert cap_next is not None and (cap_next >> 26) == 2
        labels, n = add_code(HP_AT, HP_END, HP_SRC.replace("@STUBS@", hp_stubs()),
                             {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2, "CAP_NEXT": (cap_next & 0x3FFFFFF) << 2, "RC_SEND": rc_send_at},
                             "both heroes inside the same hold of a boss; the hold note is written each step")
        hook_base(0x00138538, tick_next, jal(labels["hp_tick"]), "the field's START look-out: first, the hold note and the pair of a hold")
        hook_base(0x00180378, cap_next, (2 << 26) | ((labels["hp_cap"] >> 2) & 0x3FFFFFF), "the paired-move routine: first, the other hero of a hold's pair")
        hook_game(0x0034DD90, 0x00171C60, labels["hp_att"], "the script call 'attach': the other hero of the pair too")
        for num, tab, fn, kind in HP_TRAPS:
            hook_game(tab, fn, labels["hp_t%d" % num], "the script call (1,%d): the other hero of the pair too" % num)
        n_glue += n + 1 + len(HP_TRAPS)
        if "--holdshared" in sys.argv:                                     # (the fifth form's second part: the shared mechanic's command in both menus)
            assert CO_AT == 0x000EE4C0                                     # (hp_form jumps there: hs_hf is CO_SRC's first routine)
            labels, n = add_code(CO_AT, CO_END, CO_SRC, {"HF_H2": labels["hf_h2"], "RC_SEND": rc_send_at, "HF_SH": labels["hf_sh"], "HF_NO": labels["hf_no"]},
                                 "the laser dome is never a hero's own move; a command offered to one hero of a hold's pair goes to the other hero's menu too")
            hook_game(0x0034E228, 0x00174328, labels["co_two"], "the script call (1,165) 'command override': both heroes of a hold's pair")
            assert labels["co_e2"] == CO_AT + 8 and labels["co_e3"] == CO_AT + 16 and labels["hs_hf"] > CO_AT + 16
            n_glue += n + 1

    if "--trickguard" in sys.argv:                                         # sixty-seventh glue (Luxord does not flinch while a hero stands in his trick)
        labels, n = add_code(LT_AT, LT_END, LT_SRC, {}, "Luxord takes no damage reaction while a hero stands in his trick")
        hook_game(0x0034EF70, 0x0018F4C0, labels["lt_dmg"], "the script call (2,8) 'is this damage a reaction': not for Luxord while he holds a hero")
        n_glue += n + 1

    if "--holdpads" in sys.argv:                                           # sixty-eighth glue (while a boss holds both heroes, both controllers count)
        assert "--holdpair" in sys.argv, "--holdpads needs --holdpair"
        pm_next = words[0x00167E90]                                        # the head of the glues at the update of record 1
        assert (pm_next >> 26) == 3
        labels, n = add_code(PM_AT, PM_END, PM_SRC, {"PM_NEXT": (pm_next & 0x3FFFFFF) << 2},
                             "while a boss holds both heroes, both controllers count")
        hook_base(0x00167E90, pm_next, jal(labels["pm_pad"]), "the controller task: first, the two records of a hold's pair are made one")
        n_glue += n

    if "--ship2score" in sys.argv:
        clash = [a for a in gq_own if a in words]
        assert not clash, "the sixty-sixth glue's own pictures lie on patch words: %08X .." % clash[0]

    if "--ownwallet" in sys.argv:                                          # sixty-ninth glue (player 2's own wallet)
        assert "--ownkey" in sys.argv and "--ownmenu" in sys.argv, "--ownwallet needs --ownkey (its swap chain) and --ownmenu"
        _c, rm_l = assemble(RM_AT, RM_SRC, {})
        _c, kb_l = assemble(KB_AT, KB_SRC, {"TICK_NEXT": 0, "WC_BOTH": WC_AT})
        kw = kb_l["kw_out"]
        assert words.get(kw) == 0x03E00008, "kb_swap's end is not jr ra: %s" % words.get(kw)
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        src = WW_SRC.replace("@WW@", str(WW_P2)).replace("@WM@", str(WW_MARK))
        labels, n = add_code(WW_AT, WW_END, src, {"TICK_NEXT": (tick_next & 0x3FFFFFF) << 2, "OW_SWAP": rm_l["ow_swap"],
                                                  "OW_LOAD": rm_l["ow_load"]}, "player 2's own wallet")

        def jw(t):
            return (2 << 26) | ((t >> 2) & 0x3FFFFFF)
        hook_base(0x00138538, tick_next, jal(labels["ww_tick"]), "the field's START look-out: first, player 2's wallet is made, no shop is open")
        hook_base(kw, 0x03E00008, jw(labels["ww_swap"]), "player 2's menu things go in or out: the wallets change places")
        hook_game(0x00178AE8, 0x27BDFFF0, jw(labels["ww_cmd"]), "a hero runs a green command: he is noted")
        hook_game(0x00178AEC, 0x240F0020, 0, "(its delay slot)")
        hook_game(0x00242500, 0x27BDFFF0, jw(labels["ww_add"]), "the game gives munny: to both wallets")
        hook_game(0x00242504, 0xFFB00000, 0, "(its delay slot)")
        assert 0x0033CBA0 not in words
        words[0x0033CBA0] = labels["ww_sstart"]                            # the shop mode's start (a data word the game writes at boot)
        order.append(0x0033CBA0)
        origin[0x0033CBA0] = "glue 8 hook: the shop mode's start: whose shop is it (was 0x00105C68)"
        n_glue += n + 5

    if "--ownbag" in sys.argv:                                             # seventy-first glue (player 2's own bag)
        assert "--ownwallet" in sys.argv, "--ownbag needs --ownwallet (its swap ends the chain)"
        places = ob_table()
        tab = [".word 0x%08X" % (places[i] | ((places[i + 1] if i + 1 < len(places) else 0) << 16)) for i in range(0, len(places), 2)]
        _t, n_t = add_code(OB_T_AT, OB_T_END, "ob_tab:\n" + "\n".join("    " + x for x in tab) + "\n", {}, "player 2's own bag: the 158 places")
        oa, n_a = add_code(OB_A_AT, OB_A_END, ob_src(OB_A_SRC), {"OB_TAB": OB_T_AT}, "player 2's own bag: his counts, the swap")
        tick_next = words[0x00138538]
        assert (tick_next >> 26) == 3
        _ob, n_b = add_code(OB_B_AT, OB_B_END, ob_src(OB_B_SRC), {"OB_TAB": OB_T_AT, "OB_PUT": oa["ob_put"], "TICK_NEXT": (tick_next & 0x3FFFFFF) << 2},
                            "player 2's own bag: made = player 1's when there is no mark")
        oc, n_c = add_code(OB_C_AT, OB_C_END, ob_src(OB_C_SRC), {"OB_TAB": OB_T_AT, "OB_GET": oa["ob_get"], "OB_PUT": oa["ob_put"]},
                           "player 2's own bag: what the game gives goes into both bags")
        assert oc["ob_gain"] == 0x000E9900, "glue 62's og_eq jumps to 0x000E9900"
        _c, ww_l = assemble(WW_AT, WW_SRC.replace("@WW@", str(WW_P2)).replace("@WM@", str(WW_MARK)),
                            {"TICK_NEXT": 0, "OW_SWAP": 0, "OW_LOAD": 0})
        wj = ww_l["ww_add"] - 8                                            # ww_swap's jr ra (its delay slot is the last store)
        assert words.get(wj) == 0x03E00008, "ww_swap's end is not jr ra"
        hook_base(wj, 0x03E00008, (2 << 26) | ((oa["ob_swap"] >> 2) & 0x3FFFFFF), "player 2's menu things go in or out: the bags too")
        hook_base(0x00138538, tick_next, jal(_ob["ob_tick"]), "the field's START look-out: first, player 2's own bag is made")
        n_glue += n_t + n_a + n_b + n_c

    if "--shoppad" in sys.argv:                                            # seventieth glue (player 2's buttons in the shop's quantity box)
        spp_next = words[0x00167E90]
        assert (spp_next >> 26) == 3
        assert words.get(0x000F4740) is not None, "--shoppad needs the second glue's pad_both at 0x000F4740"
        labels, n = add_code(SPP_AT, SPP_END, SPP_SRC, {"SPP_NEXT": (spp_next & 0x3FFFFFF) << 2},
                             "player 2's buttons in the shop's quantity box")
        hook_base(0x00167E90, spp_next, jal(labels["sp_inst"]), "the controller task: first, the shop module's quantity box listens to both controllers")
        n_glue += n

    if "--drivesave" in sys.argv:                                          # seventy-second glue (player 2's own Drive gauge in the save)
        assert words.get(0x000F4668) == 0x8DAB1040 and words.get(0x000F466C) == 0xAD8B47CC, "the drive glue's dl_ext is not there"
        assert words.get(0x000F4670) == 0x03E00008 and words.get(0x000F4654) == 0xAD8047C0, "the drive glue's dl_ext is not there"
        assert words.get(0x000F49E4) == 0x3C09000F and words.get(0x000F49E8) == 0xAD207F34, "the snapshot glue's snap_none is not there"
        assert words.get(0x000F49F0) == 0x35AD0FC0 and words.get(0x001CD2D0) == 0x0C03D279, "the snapshot glue's snap_none is not there"
        dv_next = words[0x00167E90]
        assert (dv_next >> 26) == 3
        labels, n = add_code(DV_AT, DV_END, DV_SRC, {"DV_NEXT": (dv_next & 0x3FFFFFF) << 2},
                             "player 2's own Drive gauge in the save")
        hook_base(0x00167E90, dv_next, jal(labels["dv_tick"]), "the controller task: first, the twin's gauge and bars into the save data")
        hook_base(0x000F49EC, 0x03E00008, (2 << 26) | ((labels["dv_load"] >> 2) & 0x3FFFFFF), "a Load Game: the twin's own Drive values from the save")
        hook_base(0x000F4668, 0x8DAB1040, (2 << 26) | ((labels["dv_ext"] >> 2) & 0x3FFFFFF), "dl_ext: the twin's own Drive values from the save data")
        n_glue += n

    if "--itemtarget" in sys.argv:                                         # seventy-third glue (a target choice for single items)
        assert words.get(0x001BA624) == 0x0C03CAA7, "lane N's n_heal call is not at 0x001BA624"
        assert words.get(0x000F2A9C) == 0x3C0F000F and words.get(0x000F2BB4) == 0x27BDFFF0, "lane N's n_heal / n_he_slot moved"
        labels, n = add_code(II_AT, II_END, II_SRC, {}, "a target choice for Potions, Ethers and Elixirs")
        hook_game(0x001BE3A4, 0x0C06FB1A, jal(labels["ih_rows"]), "the PARTY rows: one more for the second hero")
        hook_game(0x001BE2BC, 0x000F7880, jal(labels["ih_row"]), "a PARTY row is confirmed: the second hero's row gives him")
        hook_game(0x001BE2C0, 0x01F17821, 0x00000000, "(the rest of the game's read of the row's member, now in ih_row)")
        hook_game(0x001BE2C4, 0x8DE50A5C, 0x00000000, "(the rest of the game's read of the row's member, now in ih_row)")
        hook_game(0x001BA53C, 0x0C05DAD6, jal(labels["ih_find"]), "a queued item's effect: drawn on the chosen hero")
        hook_base(0x001BA624, 0x0C03CAA7, jal(labels["ih_pick"]), "a queued item takes effect: on the chosen hero, else lane N's rule")
        n_glue += n

    if "--boxpick" in sys.argv:                                            # seventy-fourth glue (player 2 picks up item boxes)
        labels, n = add_code(BX_AT, BX_END, BX_SRC, {}, "player 2's hero picks up a dropped item box")
        assert game_word(0x001BF5D4) == 0x0220202D and game_word(0x001BF5EC) == 0x0806FCDE, "the item box's end is not as read"
        hook_game(0x001BF570, 0x0C06FF28, jal(labels["bx_twin"]), "an item box that player 1's hero did not touch: player 2's hero may")
        n_glue += n

    if "--formroom" in sys.argv:                                           # seventy-fifth glue (player 2's form files in a new room)
        assert "--no-formbase" not in sys.argv, "--formroom needs the forty-first glue's number base (0x000E7C08)"
        labels, n = add_code(FR_AT, FR_END, FR_SRC, {}, "player 2's form files are asked for in a new room")
        hook_game(0x0016EED0, 0x1080FFD1, 0x00000000, "the room's form request: no early return when player 1 is in no form")
        hook_game(0x0016EEE4, 0x0805BBCA, (2 << 26) | ((labels["fr_room"] >> 2) & 0x3FFFFFF), "the room's form request: player 2's form too")
        n_glue += n

    if "--setposguard" in sys.argv:                                        # seventy-sixth glue (trap_effect_set_pos on an ended effect)
        assert game_word(0x0016E198) == 0x8E0F0004 and game_word(0x0016E1A0) == 0xDFB00000 and game_word(0x0016E1B0) == 0xDFBF0008
        for a, old, new, what in ((0x0016E19C, 0x104F0004, 0x10400004, "an ended effect (no body): nothing is written"),
                                  (0x0016E1A4, 0x79E80000, 0x104F0002, "the game's own test (the same vector)"),
                                  (0x0016E1A8, 0x7C480000, 0x79E80000, "the copy (read)"),
                                  (0x0016E1AC, 0xDFB00000, 0x7C480000, "the copy (write)")):
            hook_game(a, old, new, "trap_effect_set_pos: " + what)
        n_glue += 4

    if "--gummiall" in sys.argv:                                           # seventy-seventh glue (Gummi points of every player weapon)
        assert "--ship2score" in sys.argv, "--gummiall needs --ship2score (the sixty-sixth glue)"
        gx_next = words[0x00167E90]
        assert (gx_next >> 26) == 3
        syms = {"GX_NEXT": (gx_next & 0x3FFFFFF) << 2}
        _code, gx_labels = assemble(GX_AT, gx_source(None), syms)
        labels, n = add_code(GX_AT, GX_END, gx_source(gx_labels), syms, "the Gummi points of every player weapon")
        assert labels == gx_labels
        gqh = [a for a in range(GQ_AT, GQ_END, 4) if words.get(a) == 0x3C0F000E and words.get(a + 4) == 0x3C0901F5
               and words.get(a + 8) == 0x35294278]                         # gq_hit: lui t7,0x000E / lui t1,0x01F5 / ori t1,t1,0x4278
        assert len(gqh) == 1, gqh
        hook_base(gqh[0], 0x3C0F000E, (2 << 26) | ((labels["gx_hit"] >> 2) & 0x3FFFFFF), "gq_hit: first gx_hit (every player weapon's shot)")
        hook_base(0x00167E90, gx_next, jal(labels["gx_inst"]), "the controller task: first, the seventy-seventh glue's jumps into a fresh flight module")
        n_glue += n

    if "--gummitag" in sys.argv:                                           # seventy-eighth glue (Gummi points of other weapons)
        assert "--ship2score" in sys.argv, "--gummitag needs --ship2score (the sixty-sixth glue)"
        assert "--gummiall" not in sys.argv, "--gummitag and --gummiall share 0x000EF000"
        gt_next = words[0x00167E90]
        assert (gt_next >> 26) == 3
        gqh = [a for a in range(GQ_AT, GQ_END, 4) if words.get(a) == 0x3C0F000E and words.get(a + 4) == 0x3C0901F5
               and words.get(a + 8) == 0x35294278]                         # gq_hit: lui t7,0x000E / lui t1,0x01F5 / ori t1,t1,0x4278
        assert len(gqh) == 1, gqh
        syms = {"GT_NEXT": (gt_next & 0x3FFFFFF) << 2, "GQH_NEXT": gqh[0] + 4}
        _code, gt_labels = assemble(GT_AT, gt_source(None), syms)
        labels, n = add_code(GT_AT, GT_END, gt_source(gt_labels), syms, "the Gummi points of other weapons (tag)")
        assert labels == gt_labels
        hook_base(gqh[0], 0x3C0F000E, (2 << 26) | ((labels["gt_hit"] >> 2) & 0x3FFFFFF), "gq_hit: first gt_hit (a tagged shot's ship)")
        hook_base(0x00167E90, gt_next, jal(labels["gt_inst"]), "the controller task: first, the seventy-eighth glue's jumps into a fresh flight module")
        n_glue += n

    out.mkdir(parents=True, exist_ok=True)
    head = [
        "gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
        "comment=Two-player project, MERGED BUILD 7: merged build 6 (test build 12) + the eighth round's glues",
        "comment=(tools/merge/merge_v7.py; its header explains each).",
        "comment=Every PC in an online game must have this same file.",
    ]
    if "--ship2score" in sys.argv:                                         # checked at the END (later glues too)
        assert 0x000E0000 - 4096 == GQ_TAB
        tab = [a for a in words if GQ_TAB <= a < GQ_TAB + 0x1000]
        assert not tab, "the sixty-sixth glue's shots' table lies on patch words: %08X .." % min(tab)
        clash = [a for a in gq_own if a in words]
        assert not clash, "the sixty-sixth glue's own pictures lie on patch words: %08X .." % clash[0]
        etab = [a for a in words if 0x000EF800 <= a < 0x000F0000]
        assert not etab, "the sixty-sixth glue's enemies' table lies on patch words: %08X .." % min(etab)
    body = ["patch=1,EE,%08X,word,%08X" % (a, words[a]) for a in order]
    (out / NAME).write_text("\n".join(head + body) + "\n", encoding="utf-8")
    listing = ["%08X %08X  %s" % (a, words[a], origin.get(a, "merged-v6")) for a in sorted(words)]
    (out / "listing.txt").write_text("\n".join(listing) + "\n", encoding="utf-8")
    print("merged-v6 words:", n_base, "+ glue words:", n_glue, "=", len(order))
    print("written:", out / NAME)
    print("sha1:", hashlib.sha1((out / NAME).read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
