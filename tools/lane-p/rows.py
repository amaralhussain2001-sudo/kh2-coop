"""Lane P: the hand-written part of the parity checklist (one entry per sequence).

Facts read from the game data are added by build_checklist.py from mission_facts.json. Everything written here that
is not in those facts comes from memory of the game and is labelled so in the output (ev = "V+M" or "M").
ev: "V" = the row's wording only restates data; "V+M" = data facts plus description from memory; "M" = memory only.
judg: BASE = expected to work with the twin and the merged patches (to confirm); OBJECT = needs a second special
object / vehicle / character state; ADAPT = the sequence itself must be adapted for two; UNKNOWN = not known.
"""

KIT = "Full kit: move, jump, combos, guard, dodge, magic, items, Drive, Limits, Summons, lock-on, Reaction Commands."
P2KIT = "The same kit on controller 2, with own target and own HP/MP; enemies attack P2 too."
RKIT = "Roxas's kit: move, jump, combos, guard (Struggle bat, later Keyblade); no magic, no Drive."
P2R = "The same with the second Roxas on controller 2."
BASESEP = "Nothing special: twin (second PLAYER placeholder), own unit slot, own control object."
V_FIGHT = "P1 puts the controller down and P2 alone wins; then both fight, both get hit, the fight ends once and both get the reward."
A_NONE = "None beyond the base. Counters, timers and gauges are shared; the fight ends once for both."
A_RC = "Reaction Command prompts are drawn for P1 only today (lane G), and enemies attack only the engine's player today (lane D)."
T_FIGHT = "Jump disc to this fight with the merged patch and the twin: P2 alone wins it."
T_BOSS = "Jump disc to the boss with the merged patch: P2 alone answers the Reaction Command and takes a special attack."
A_SCORE = "Check that the mission's counter also counts what P2 does; one shared score for the team."
V_SCORE = "Only P2 plays while P1 stands still: the score still rises and the result screen is right; then both play."
T_SCORE = "Jump disc to the mission with the twin: only pad 2 acts; read the counter."
A_ATTACH = "The Reaction Command moves or attaches the hero to the boss in a scripted way. Not known: can both heroes do it at the same moment, and what happens to the hero left on the ground."
V_ATTACH = "Each player rides / uses the scripted command once, alone and then both at the same moment, without a freeze."
T_ATTACH = "Jump disc to the boss: both pads press Triangle in the same window; watch positions and the camera."

DEF = {
    "fight": dict(mech="Forced fight: defeat the enemies in a closed room.", p1=KIT, p2=P2KIT, sep=BASESEP, adapt=A_NONE,
                  verify=V_FIGHT, test=T_FIGHT, judg="BASE", phase="1-2", ev="V+M"),
    "rfight": dict(mech="Forced fight as Roxas.", p1=RKIT, p2=P2R + " Enemies attack him too.", sep=BASESEP, adapt=A_NONE,
                   verify=V_FIGHT, test=T_FIGHT, judg="BASE", phase="1-2", ev="V+M"),
    "boss": dict(mech="Boss fight.", p1=KIT + " Plus the boss's own Reaction Commands.",
                 p2=P2KIT + " P2 answers the boss's Reaction Commands and is hit by its special attacks.", sep=BASESEP,
                 adapt=A_RC, verify="P2 lands a Reaction Command and the last hit; a special attack hits P2; then the same for P1.",
                 test=T_BOSS, judg="BASE", phase="2", ev="V+M"),
    "score": dict(mech="Score or time challenge.", p1=KIT, p2=P2KIT, sep=BASESEP, adapt=A_SCORE, verify=V_SCORE, test=T_SCORE,
                  judg="BASE", phase="3", ev="V+M"),
    "attach": dict(mech="Boss fight with Reaction Commands that carry the hero.", p1=KIT + " Plus the ride / grab commands.",
                   p2=P2KIT + " P2 can use the same ride / grab commands.", sep="Own attach state per hero (not known if the boss allows two).",
                   adapt=A_ATTACH, verify=V_ATTACH, test=T_ATTACH, judg="UNKNOWN", phase="2", ev="V+M"),
    "free": dict(mech="", p1="", p2="", sep="", adapt="", verify="", test="", judg="UNKNOWN", phase="3", ev="V+M"),
}

ROWS = []


def R(rid, group, title, missions=(), kind="fight", **kw):
    d = dict(id=rid, group=group, title=title, missions=list(missions), kind=kind)
    d.update(kw)
    ROWS.append(d)


G1 = "1. Twilight Town: Roxas's prologue"
G2 = "2. Twilight Town: Sora's visits"
G3 = "3. Hollow Bastion / Radiant Garden"
G4 = "4. The Land of Dragons"
G5 = "5. Beast's Castle"
G6 = "6. Olympus Coliseum: story"
G7 = "7. Olympus Coliseum: Phil's training and the cups"
G8 = "8. Disney Castle and Timeless River"
G9 = "9. Port Royal"
G10 = "10. Agrabah"
G11 = "11. Halloween Town"
G12 = "12. Pride Lands"
G13 = "13. Space Paranoids"
G14 = "14. The World That Never Was"
G15 = "15. 100 Acre Wood"
G16 = "16. Atlantica"
G17 = "17. Gummi Ship and world map"
G18 = "18. Final Mix extras"
G19 = "19. Game-wide mechanics"
G20 = "20. Mission names and files the game does not seem to use"

# ------------------------------------------------------------------ 1. Roxas
R("TTR-01", G1, "First control and tutorials: run, talk, lock on, save, open a chest",
  ["TT07_MS101", "TT07_MS103", "TT07_MS105", "TT02_MS201", "TT32_MS303", "TT04_MS106"], "free",
  mech="Tutorial steps given by on-screen text: walk to a shop, talk with Triangle, lock on to a cat, open the save menu at a save point, open a chest.",
  p1="Run, jump, talk, lock on, open the save menu, open the chest.",
  p2="The same with the second Roxas; a step counts when either player does it.",
  sep="Twin Roxas: VERIFIED (two Roxas at this spot, tests t1 and lane F).",
  adapt="Decide: a step is done by either player, or by both. Talk / Examine / Open / Save prompts are drawn for P1 only (lane G).",
  verify="P2 alone completes every tutorial step while P1 stands still.",
  test="kh2-coop-v1 disc, New Game, merged patch: P2 walks to the shop, talks, locks on.", judg="BASE", phase="1-2", ev="V")
R("TTR-02", G1, "Seifer duels with the Struggle bat", ["TT03_MS400", "TT04_MS107", "TT04_MS108", "TT04_MS500"], "rfight",
  mech="One-on-one fights against Seifer; the first one teaches attack and combos.",
  adapt="Balance only (two against one). The weapon choice before the fight is one choice for both (shared stats, lane D).")
R("TTR-03", G1, "Job: Mail Delivery", ["TT06_LETTER_01", "TT06_LETTER_02", "TT06_WORK_LETTER"], "free",
  mech="Timed job on a skateboard: ride down Market Street and hand over letters; letter counter and timer.",
  p1="Ride the skateboard, jump, deliver letters with a Reaction Command.",
  p2="Own skateboard, delivers letters too.", sep="A second skateboard. The board object is not identified in the data yet.",
  adapt="Two boards on one street; one shared letter count and timer.",
  verify="Both ride at the same time; each delivers a letter; the counter shows the sum.",
  test="Free roam in tt07 with the twin: both press Hop On at the one board; then with a second board placed.", judg="OBJECT", phase="3")
R("TTR-04", G1, "Job: Cargo Climb", ["TT06_BAGGAGE_01", "TT06_BAGGAGE_02", "TT06_WORK_BAGGAGE"], "score",
  mech="Timed job: knock a cart up the hill by hitting it.", p1="Hit the cart.", p2="Hit the same cart.",
  sep="Nothing special (one cart, two hitters).", adapt="Check the cart reacts to P2's hits; one shared timer.")
R("TTR-05", G1, "Job: Grandstander", ["TT06_PERFORM_01", "TT06_PERFORM_02", "TT06_WORK_PERFORM"], "score",
  mech="Keep a ball in the air by hitting it in front of a crowd; combo counter.", p1="Hit the ball.", p2="Hit the same ball.",
  sep="Nothing special (one ball).", adapt="Check the combo counter counts P2's hits and does not reset when the other player hits.")
R("TTR-06", G1, "Job: Poster Duty", ["TT07_POSTER_01", "TT07_POSTER_02", "TT07_WORK_POSTER"], "score",
  mech="Timed job: put up posters on walls around Tram Common with a Reaction Command; counter and timer.",
  p1="Run, jump, post with Triangle.", p2="Posts too.", sep="Nothing special.",
  adapt="P2 needs the Post prompt; one shared count.")
R("TTR-07", G1, "Job: Bumble-Buster", ["TT07_WORM_01", "TT07_WORM_02", "TT07_WORK_WORM"], "score",
  mech="Timed fight: defeat all the bees.", adapt="None beyond the base; shared timer.")
R("TTR-08", G1, "Job: Junk Sweep", ["TT07_CLEAN_01", "TT07_CLEAN_02", "TT07_WORK_CLEAN"], "score",
  mech="Smash all the junk with as few swings as possible; swing counter.", p1="Swing at the junk.", p2="Swings too.",
  sep="Nothing special.", adapt="The swing counter must count both players' swings.")
R("TTR-09", G1, "Struggle tournament (Roxas)", ["TT05_MS401", "TT05_MS402", "TT05_MS405"], "free",
  mech="Struggle match against Hayner, Vivi and Setzer: hits knock orbs out of the opponent; the side with more orbs when the timer ends wins (two orb counters, timer).",
  p1="Attack, guard, collect orbs.", p2="Fights and collects orbs too.", sep="Twin Roxas; no special object.",
  adapt="The match is one against one with one orb count per side. A rule for two is needed: both heroes' orbs in one team count, and whose orbs the opponent's hits knock out.",
  verify="Both collect orbs; the team count rises for either; the win and lose screens are right.",
  test="Jump disc to tt05 (TT05_MS401) with the twin: only pad 2 collects orbs; read both counters.", judg="ADAPT", phase="3")
R("TTR-10", G1, "Nobody fights in town and at the mansion", ["TT03_MS601", "TT05_MS403", "TT04_MS301", "TT14_MS109", "TT14_MS110", "TT19_MS602"], "rfight",
  mech="Fights against Dusks and other Nobodies; in one of them the bat does nothing until the Keyblade appears.",
  adapt="When the Keyblade appears, both Roxas must get one (the weapon comes with the object: to confirm).")
R("TTR-11", G1, "Axel, twice", ["TT05_MS404", "TT20_MS603"], "boss",
  mech="Two fights against Axel; in the second the floor burns and Roxas fights with two Keyblades.",
  p1=RKIT + " Two Keyblades in the second fight.", p2=P2R + " Two Keyblades too.",
  sep="The second fight uses another player object (P_EX110_BTLF, party table row 4): the twin must take the same form (not tested).",
  adapt=A_RC + " The burning floor must hurt both.")
R("TTR-12", G1, "Seven Wonders: wall balls, Vivi copies, Shadow Roxas", ["TT10_WORK_TIMBER", "TT36_WORK_FIGURE", "TT10_WORK_MIRROR"], "rfight",
  mech="Three small challenges: reach a wall while balls fly at you, defeat many Vivi copies, defeat a mirror image of Roxas.")
R("TTR-13", G1, "Seven Wonders: the moving bag on Sunset Hill", ["TT12_WORK_BOX"], "free",
  mech="Jump on a moving bag and stay on it with Reaction Commands until its gauge is empty.",
  p1="Jump on the bag, ride it, dodge obstacles with Triangle.", p2="Rides the bag too.",
  sep="One bag: own riding state for each hero (not known if two can ride).", adapt=A_ATTACH,
  verify="Both jump on; the gauge falls; the challenge ends once.", test="Jump disc to tt12 with the twin: both jump on the bag.",
  judg="UNKNOWN", phase="3")
R("TTR-14", G1, "Station of Serenity: Nobody fight", ["TT32_MS302"], "rfight")
R("TTR-15", G1, "Twilight Thorn", ["TT34_MS304"], "attach",
  mech="Giant boss fought largely through Reaction Commands (Key Counter, Lunarsault, Break Raid); it grabs Roxas and throws him in scripted sequences.",
  p1=RKIT + " Plus the scripted Reaction Commands.", p2=P2R + " Answers the same commands.")

# ------------------------------------------------------------------ 2. Sora in Twilight Town
R("TTS-01", G2, "Station Plaza: first fight as Sora", ["TT08_MS701"], "fight")
R("TTS-02", G2, "The Tower: three fights", ["TT25_MS801", "TT29_MS802", "TT30_MS803"], "fight")
R("TTS-03", G2, "Sandlot: Nobodies (second visit)", ["TT04_MS901"], "fight")
R("TTS-04", G2, "Old Mansion: fight beside King Mickey", ["TT14_MS001"], "fight",
  mech="Fight many Nobodies with King Mickey as a helper (object P_EX230).")
R("TTS-05", G2, "Betwixt and Between: Nobodies, then beside Axel", ["TT40_MS002", "TT40_MS003"], "fight")
R("TTS-06", G2, "Struggle matches as Sora", ["TT04_MS00", "TT04_MS01", "TT04_MS02"], "free",
  mech="Struggle against Hayner, Setzer and Seifer (journal entries 'The Struggle: ...'): orb counters and timer; Drive, magic and experience are switched off by the mission flags.",
  p1="Attack, guard, collect orbs.", p2="Fights and collects orbs too.", sep="Twin; no special object.",
  adapt="Same rule question as the Roxas tournament (TTR-09).",
  verify="Both collect orbs; the team count rises for either; results are recorded in the journal.",
  test="Covered by the TTR-09 test.", judg="ADAPT", phase="3")
R("TTS-07", G2, "Skateboard in Twilight Town", ["TT07_SKATE_01"], "free",
  mech="Skateboard challenge with three counters (journal: SB Street Rave). Tricks are commands: Heelflip, Pop-Jump, 360 Spin, Method Grab, Air Walk, Handstand, Grind.",
  p1="Hop On, ride, jump, do tricks, Get Off.", p2="Own board, same tricks.",
  sep="A second skateboard for P2 (board object not identified yet).", adapt="Two riders; one shared score, or one per player.",
  verify="Both ride and trick at once; the score counts both.", test="Same as TTR-03.", judg="OBJECT", phase="3")

# ------------------------------------------------------------------ 3. Hollow Bastion
R("HB-01", G3, "Bailey: defend the gate with Leon", ["HB08_MS102"], "fight",
  mech="Defeat the Nobodies before they break the gate; the fight is lost when the gate gauge is empty. No Donald or Goofy here.")
R("HB-02", G3, "Borough fights", ["HB09_MS101", "HB09_MS501", "HB09_MS901"], "fight",
  mech="Three story fights in the Borough; in one the town's defence system helps and the fight ends in a story scene at low HP (VERIFIED lane B).")
R("HB-03", G3, "Merlin's House: unnamed mission", ["HB13_MS902"], "free",
  mech="Not known: the mission file has no objective text.", p1="Not known.", p2="The same as P1.", sep="Not known.", adapt="Not known.",
  verify="Play the scene with two players and write down what it is.", test="Reach it in a normal playthrough.", judg="UNKNOWN", phase="3", ev="V")
R("HB-04", G3, "Second visit: corridor and town fights", ["HB20_MS401", "HB07_MS402"], "fight")
R("HB-05", G3, "Demyx at the Castle Gate", ["HB04_MS403"], "boss",
  mech="Demyx sets trials (destroy a number of water forms within a time limit: counter and timer), then fights.",
  adapt=A_RC + " The water-form counter must count P2's kills.")
R("HB-06", G3, "Ravine Trail: four fights beside friends", ["HB16_MS404A", "HB16_MS404B", "HB16_MS404C", "HB16_MS404D"], "fight",
  mech="Four fights in a row, each with a helper character; no Donald or Goofy.")
R("HB-07", G3, "The Great Maw: battle of 1000 Heartless", ["HB17_MS405"], "fight",
  mech="Defeat a huge crowd of two enemy types; kill counter; their Reaction Commands (Rising Sun, Snag, Sparkle Ray) do most of the work.",
  adapt=A_RC + " The kill counter must count P2's kills.")
R("HB-08", G3, "Sephiroth", ["HB01_MS601"], "boss",
  mech="Optional solo boss (journal: 'Meet Sephiroth again'). Opens with a Reaction Command (Block); one attack drops HP to 1 and MP to 0.",
  adapt=A_RC + " His single-target attacks must be able to pick either hero.")
R("HB-09", G3, "Skateboard in the Borough", ["HB09_SKATE_01"], "free",
  mech="Skateboard challenge with a combo counter (journal: SB Freestyle).", p1="Hop On, ride, tricks.", p2="Own board, same tricks.",
  sep="A second skateboard.", adapt="Two riders; score rule.", verify="Both ride and trick at once; the score counts both.",
  test="Same as TTR-03.", judg="OBJECT", phase="3")

# ------------------------------------------------------------------ 4. Land of Dragons
R("MU-01", G4, "Encampment: first fight beside Ping", ["MU01_MS101"], "fight")
R("MU-02", G4, "Morale-gauge missions", ["MU01_MS102", "MU01_MS103C", "MU02_MS103A", "MU02_MS103B"], "fight",
  mech="Fights with a morale gauge that drops when Ping is hit or as time passes; the mission fails when it is empty.")
R("MU-03", G4, "Mountain Trail: climb to the summit", ["MU03_MS104"], "fight",
  mech="Run up the trail through ambushes while the morale gauge runs down.",
  adapt="None beyond the base; the 'both at the exit' rule applies along the trail.")
R("MU-04", G4, "Village Cave: with Ping only", ["MU05_MS105"], "fight")
R("MU-05", G4, "Summit: timed fight, Sora alone", ["MU07_MS106"], "fight",
  mech="Defeat a set number of fast enemies before the timer ends (counter and timer); no friends.",
  adapt="The counter must count P2's kills.")
R("MU-06", G4, "Imperial Square and Antechamber fights", ["MU08_MS107", "MU08_MS202", "MU10_MS203"], "fight")
R("MU-07", G4, "Shan-Yu at the Palace Gate", ["MU09_MS108"], "boss",
  mech="Defeat Shan-Yu while his troops attack the gate (gate gauge). Reaction Commands Press and Takedown.")
R("MU-08", G4, "Summit: the mysterious man", ["MU07_MS201"], "boss", mech="Duel against a hooded man; Sora alone.")
R("MU-09", G4, "Storm Rider", ["MU08_MS204"], "attach",
  mech="Flying dragon boss; Reaction Commands (Slide, Vertigo Toss) put Sora on its back; whirlwinds lift him.")

# ------------------------------------------------------------------ 5. Beast's Castle
R("BB-01", G5, "Parlor: first fight", ["BB01_MS101"], "fight")
R("BB-02", G5, "West Hall: move the wardrobe", ["BB08_GIMMICK"], "free",
  mech="Push a sleeping wardrobe aside with a Reaction Command without waking her.", p1="Push with Triangle.", p2="Can push too.",
  sep="Nothing special.", adapt="P2 needs the Push prompt.", verify="P2 alone pushes the wardrobe all the way.",
  test="Reach it in a playthrough with the merged patch.", judg="BASE", phase="2-3", ev="M")
R("BB-03", G5, "Secret Passage: light the lanterns", ["BB12_GIMMICK"], "free",
  mech="Light all the lanterns while a helper holds a lever (gauge = how long he can hold).", p1="Run, jump, light lanterns with Triangle.",
  p2="Lights lanterns too.", sep="Nothing special.", adapt="P2 needs the Light prompt; shared gauge.",
  verify="Each player lights at least one lantern; the room opens.", test="Reach it in a playthrough with the merged patch.",
  judg="BASE", phase="2-3")
R("BB-04", G5, "Thresholder and Possessor (the door)", ["BB11_MS102"], "boss",
  mech="A possessed door; a Reaction Command (Release) pulls the Possessor out so it can be hit.")
R("BB-05", G5, "The Beast", ["BB03_MS103"], "boss",
  mech="Fight the Beast until he comes to his senses; Reaction Commands with Cogsworth (Wake Up!, Charge).")
R("BB-06", G5, "Shadow Stalker", ["BB05_MS104A"], "boss", mech="Boss that hides in the room's pillars and chandelier; a Reaction Command drives it out.")
R("BB-07", G5, "Dark Thorn", ["BB05_MS104B"], "attach",
  mech="Invisible boss; Reaction Commands (Step Vault, Catch, Pendulum Round, Slingshot) swing Sora and the boss on the chandelier.")
R("BB-08", G5, "Second visit: Ballroom and Entrance Hall", ["BB04_MS201", "BB00_MS202"], "fight")
R("BB-09", G5, "Xaldin", ["BB15_MS203"], "boss",
  mech="Boss whose lances can be copied: the Learn command stores Jump commands that Sora then spends.",
  adapt=A_RC + " Each hero has an own command state (lane G), so each should have an own Learn stock; P2 cannot see it yet.")

# ------------------------------------------------------------------ 6. Olympus story
R("HE-01", G6, "Cerberus", ["HE07_MS103"], "attach",
  mech="Three-headed dog fought with Auron only; Reaction Commands (Evade, Jump!, Dog Paddle) put Sora on its heads.")
R("HE-02", G6, "Valley of the Dead: run from Hades", ["HE05_MS102"], "fight",
  mech="Fight through to the exit while Hades cannot be hurt.", adapt="None beyond the base; the 'both at the exit' rule decides when the run ends.",
  verify="Both reach the exit; the scene starts only when both are there.")
R("HE-03", G6, "Hades' Chamber: first fight", ["HE06_MS101"], "boss",
  mech="Timed fight beside Auron against a Hades who cannot be beaten yet (counter, gauge, timer).")
R("HE-04", G6, "Demyx in the Underworld", ["HE17_MS105"], "boss",
  mech="Destroy Demyx's water forms before the timer ends (counter and timer).", adapt="The counter must count P2's kills.")
R("HE-05", G6, "Well of Captivity: defend Megara, then Pete", ["HE08_MS106", "HE08_MS107"], "fight",
  mech="Protect Megara from enemies (gauge, timer), then beat Pete beside Hercules before the cave collapses (timer).")
R("HE-06", G6, "The Hydra", ["HE18_MS108"], "attach",
  mech="Many-headed boss; Reaction Commands (Vanquish, Urninator, Pegasus Run, Attack) include a ride on Pegasus.")
R("HE-07", G6, "Second visit: Underdrome and Hades' Chamber fights", ["HE09_MS201", "HE09_MS202", "HE06_MS203"], "fight")
R("HE-08", G6, "Hades", ["HE19_MS204", "HE19_MS205"], "boss",
  mech="Two-part boss: a timed phase, then a fight beside Hercules whose aura spheres must be knocked into Hades to make him vulnerable.")

# ------------------------------------------------------------------ 7. training and cups
R("HEC-00", G7, "Phil's Training (Practice and Maniac)", ["HE00_MS104A", "HE00_MS104B", "HE02_MS104C", "HE02_MS104D", "HE00_MS104"], "score",
  mech="Break pots and collect the orbs for points within a time limit (journal: Phil's Training, Practice Mode, Maniac Mode).",
  adapt="One shared point count for both players' orbs.")
R("HEC-01", G7, "Pain and Panic Cup", ["HE_COLOSSEUM", "HE_COL_1_8", "HE_COL_1_10"], "fight",
  mech="Ten rounds with the party. Rule (VERIFIED text): Drive cannot be used, Limits cost less MP; one round is 'survive until time runs out'.",
  adapt="Limits started by either hero (plan rule); cheaper Limit cost applies to both.", phase="3")
R("HEC-02", G7, "Cerberus Cup", ["HE_COLOSSEUM_2", "HE_COLOSSEUM_2_FOG", "HE_COL_2_10"], "fight",
  mech="Sora alone against waves with a timer. Rule (VERIFIED text): Forms can be used alone and the Drive gauge fills fast.",
  adapt="'Alone' becomes two heroes without Donald and Goofy. 'Forms alone' must work for each hero (Drive rule for two is still to design).",
  judg="ADAPT", phase="3")
R("HEC-03", G7, "Titan Cup", ["HE_COLOSSEUM_3"], "fight",
  mech="Sora alone. Rule (VERIFIED text): Forms forbidden, summons usable alone; points are lost when taking damage and it is over when the points are gone.",
  adapt="One point pool: damage to either hero must cost points, and the rule for losing must be the pool, not one hero's HP.",
  verify="Each player takes a hit and the pool drops both times; the cup ends only when the pool is empty.",
  test="Jump disc to the cup's first round with the twin: let each hero be hit once; read the point counter.", judg="ADAPT", phase="3")
R("HEC-04", G7, "Goddess of Fate Cup", ["HE_COL_4_1", "HE_COL_4_2", "HE_COL_4_3", "HE_COL_4_4", "HE_COL_4_5", "HE_COL_4_6", "HE_COL_4_7", "HE_COL_4_8", "HE_COL_4_9", "HE_COL_4_10"], "fight",
  mech="Ten rounds with the party and no special rule; some rounds are timed, some use the point pool, the last is a boss.",
  adapt="Point-pool rounds as in the Titan Cup.", phase="3")
R("HEC-05", G7, "Pain and Panic Paradox Cup", ["HE_COL_5", "HE_COL_5_8", "HE_COL_5_10"], "fight", mech="Harder version of the Pain and Panic Cup (same rule).",
  adapt="As HEC-01.", phase="3")
R("HEC-06", G7, "Cerberus Paradox Cup", ["HE_COLOSSEUM_6", "HE_COLOSSEUM_6_FOG", "HE_COL_6_10"], "fight", mech="Harder version of the Cerberus Cup (same rule).",
  adapt="As HEC-02.", judg="ADAPT", phase="3")
R("HEC-07", G7, "Titan Paradox Cup", ["HE_COLOSSEUM_7"], "fight", mech="Harder version of the Titan Cup (same rule).", adapt="As HEC-03.",
  verify="As HEC-03.", test="Covered by HEC-03.", judg="ADAPT", phase="3")
R("HEC-08", G7, "Hades Paradox Cup (50 rounds)",
  ["HE_COLOSSEUM_8", "HE_COLOSSEUM_8_CEL", "HE_COLOSSEUM_8_ONLY", "HE_COLOSSEUM_8_PP", "HE_COLOSSEUM_8_TIT", "HE_COL_8_5", "HE_COL_8_6", "HE_COL_8_10",
   "HE_COL_8_25", "HE_COL_8_30", "HE_COL_8_31", "HE_COL_8_35", "HE_COL_8_40", "HE_COL_8_45", "HE_COL_8_49", "HE_COL_8_50", "HE_COL_8TI_BOSS"], "fight",
  mech="Fifty rounds that switch between the other cups' rules (VERIFIED texts), including 'Sora's on his own!' rounds, point-pool rounds and boss rounds.",
  adapt="Everything from HEC-01 to HEC-03 at once; rule changes between rounds must reach both heroes.",
  verify="Two players clear all 50 rounds; each rule change is seen to apply to both.", test="Covered by the single-cup tests first.", judg="ADAPT", phase="3")

# ------------------------------------------------------------------ 8. Disney Castle / Timeless River
R("DC-01", G8, "Disney Castle: escort Queen Minnie", ["DC02_MS100", "DC02_MS101", "DC02_MS102", "DC00_MS101"], "free",
  mech="Lead Minnie through rooms full of Heartless (her gauge must not empty); Reaction Commands call her over and trigger her light.",
  p1=KIT + " Plus Call Over and Faith with Minnie.", p2=P2KIT + " Can call Minnie and use her light too.",
  sep="Nothing special; one Minnie.", adapt="Whom Minnie follows and who may call her; her gauge is shared. " + A_RC,
  verify="Each player calls Minnie once and uses her light once; both reach the throne.",
  test="Jump disc to dc02 with the merged patch: P2 presses Triangle next to Minnie.", judg="BASE", phase="2-3")
R("WI-01", G8, "Timeless River: Pete, first fight", ["WI01_MS101"], "boss", mech="Fight Pete; Sora wears the old-cartoon form of this world.",
  sep="Twin in the same form (object P_EX100_WI from the party table): VERIFIED by lane J (test j-wi52: two old-cartoon Soras with Keyblades; each pad its own hero with lane E's patch, j-sep-wi52).")
R("WI-02", G8, "Timeless River: the four windows", ["WI07_MS102A", "WI06_MS102B", "WI04_MS102C", "WI05_MS102D"], "fight",
  mech="Four small missions: protect furniture, a burning building, a toy town (with a cannon tower), a scaffolding; each has a gauge.",
  adapt="None beyond the base; the cannon in the toy town is a one-seat Reaction Command object.")
R("WI-03", G8, "Timeless River: the cage on the steamboat", ["WI02_MS103"], "fight",
  mech="Break the cage before Pete gets away (gauge); thrown objects can be hit back with Reaction Commands.")
R("WI-04", G8, "Timeless River: Pete, final fight", ["WI03_MS104"], "boss", mech="Fight Pete with the old Pete helping; the stage scenery changes during the fight.")

# ------------------------------------------------------------------ 9. Port Royal
R("CA-01", G9, "Harbor and Town: pirates", ["CA01_MS101", "CA01_MS102", "CA02_MS103"], "fight",
  mech="Fights against cursed pirates, who can only be hurt in moonlight or by magic.")
R("CA-02", G9, "The Interceptor: protect the medallion; burning barrels", ["CA07_MS105", "CA03_MS106"], "fight",
  mech="Defend a medallion on deck with a timer (cannons can be fired), then get rid of burning barrels before they explode (counter).",
  adapt="None beyond the base; the cannons and barrels are Reaction Command objects P2 must be able to use.")
R("CA-03", G9, "Isla de Muerta: hold out for one minute", ["CA09_MS104"], "fight")
R("CA-04", G9, "Barbossa", ["CA10_MS107"], "boss", mech="Fight Barbossa beside Jack; a Heartless makes darkness that must be beaten first.")
R("CA-05", G9, "Second visit: Harbor and Seadrift Keep", ["CA01_MS201", "CA14_MS203"], "fight")
R("CA-06", G9, "Medallion hunts", ["CA09_MEDAL", "CA10_MEDAL", "CA12_MEDAL", "CA13_MEDAL", "CA14_MEDAL", "CA15_MEDAL"], "score",
  mech="Six rooms: catch the Nobody carrying a medallion before it escapes (counter and timer).",
  adapt="Either player can catch it; shared counter and timer.")
R("CA-07", G9, "Grim Reaper, first fight", ["CA18_MS202"], "boss")
R("CA-08", G9, "Ship ambushes", ["SHIP_BATTLE"], "free",
  mech="Text in the file: 'It's an ambush! You'll have to defeat them all or escape within the ship!' Used by 15 programs in five ship rooms. More is not known from the data.",
  p1=KIT, p2=P2KIT, sep="Not known.", adapt="Not known: how 'escape within the ship' is triggered, and by whom.",
  verify="Two players fight an ambush to the end and also escape from one.", test="Jump disc to ca18 with the merged patch.", judg="UNKNOWN", phase="3", ev="V")
R("CA-09", G9, "Grim Reaper, second fight", ["CA01_MS204"], "boss",
  mech="The boss cannot be hurt until medallions knocked out of it are collected (with magic) and returned to the chest; three counters.",
  adapt=A_RC + " Medallions collected by either hero must count; the 'cursed' state of a hero is per hero.")
R("CA-10", G9, "Skateboard in the Town", ["CA02_SKATE_01"], "free",
  mech="Skateboard challenge with counter, timer and a stopwatch (journal: SB Time Attack).", p1="Hop On, ride, tricks.", p2="Own board.",
  sep="A second skateboard.", adapt="Two riders; time for the team or per player.", verify="Both ride the course at once; a time is recorded.",
  test="Same as TTR-03.", judg="OBJECT", phase="3")

# ------------------------------------------------------------------ 10. Agrabah
R("AL-01", G10, "Agrabah streets: first fight", ["AL00_MS101"], "fight")
R("AL-02", G10, "Cave of Wonders: Abu and the jewel", ["AL09_GIMMICK"], "free",
  mech="Abu carries a jewel to a pedestal while statues attack; Reaction Commands send him on and set the jewel.",
  p1=KIT + " Plus the commands for Abu.", p2=P2KIT + " Can command Abu too.", sep="Nothing special; one Abu.",
  adapt="Who may command Abu; " + A_RC, verify="Each player sends Abu once; the jewel is set.",
  test="Jump disc to al09 with the merged patch.", judg="BASE", phase="2-3")
R("AL-03", G10, "Cave of Wonders: Chasm of Challenges", ["AL13_TRAP", "AL13_TRAP_FREE", "AL13_TRAP_FREE2"], "score",
  mech="Timed fight on floors that disappear; if all floors are gone it starts over (journal replay: 'Redo the Cave of Wonders: Chasm of Challenges').",
  adapt="Two heroes can stand on different floors; the camera must show both, or own screens.")
R("AL-04", G10, "Cave of Wonders: Treasure Room ambush", ["AL10_MS102"], "fight")
R("AL-05", G10, "Volcanic Lord and Blizzard Lord", ["AL03_MS103"], "boss", mech="Two bosses at once, each weak to the other's element.")
R("AL-06", G10, "Sandswept Ruins on the Magic Carpet", ["AL14_MS_K", "AL14_MS_L", "AL14_MS_M", "AL14_MS_O", "AL14_MS_P", "AL14_MS201A", "AL14_MS201B"], "free",
  mech="In the ruins Sora is on Carpet the whole time: chase Jafar's shadow, trigger switches with magic, fight Heartless from the carpet, reach the tower before a door shuts (timer).",
  p1="Fly the carpet (move, speed up), attack, use magic, lock on.",
  p2="Own carpet with all of that, flown independently.",
  sep="A second carpet for P2. Object P_EX100_AL_CARPET is placed directly in room al14 (13 placements), not through the PLAYER placeholder. VERIFIED by lane J (j-sp-al86): a second copy gives a second Sora but only ONE carpet; the second Sora floats without a carpet and drifts off. So the carpet itself is something else (HYPOTHESIS: the helper object N_AL010_BTL placed in the same groups).",
  adapt="Find what makes the carpet and give P2 one at every placement; who triggers the chase steps; camera for two carpets.",
  verify="Both fly separately on own carpets; P2 alone triggers a switch and defeats a Heartless; both reach the tower.",
  test="Repeat lane J's test with the helper object duplicated too: does a second carpet appear under the second Sora? Then the merged patch: own controller, own HP.",
  judg="OBJECT", phase="3")
R("AL-07", G10, "Escape from the ruins (journal minigame: Magic Carpet)", ["AL14_MS202", "AL14_MS202_FREE"], "free",
  mech="A forward-flying escape run with enemies; own objects (AL14_PLAYER, AL14_CARPET) and an own script module (minigame/al_14.bar); the replay version scores with two counters.",
  p1="Steer the carpet, attack enemies on the way.", p2="Own carpet in the same run, steers and attacks.",
  sep="A second AL14_PLAYER and AL14_CARPET pair; the module's state for a second rider.",
  adapt="The run is scripted for one rider: path, camera, scoring and the finish must take two.",
  verify="Both steer and attack through the whole run; the score counts both.",
  test="NOT TESTED by lane J: on a jump disc this mission shows a black screen with or without a twin (j-sp-al106, j-ctl-al106). It needs a start played in from the story (a save), then the two objects duplicated in group b_70.", judg="ADAPT", phase="3")
R("AL-08", G10, "Jafar (genie form) above Agrabah", ["AL05_MS203"], "boss",
  mech="Boss fought in the air on the carpet; text: 'Avoid his attacks by using Carpet to speed up'.",
  p1="Fly the carpet, speed up, attack, Reaction Commands on Jafar.", p2="Own carpet with the same.",
  sep="A second carpet in group b_60 of room al05. VERIFIED by lane J (j-sp-al62): a second P_EX100_AL_CARPET gives a second Sora but only one carpet; he drifts away in the air (gone from the picture after about 13 seconds).",
  adapt="As AL-06, plus " + A_RC,
  verify="Each player on an own carpet lands a Reaction Command; Jafar's attacks reach both.",
  test="After AL-06's test: the same in al05.", judg="OBJECT", phase="3")
R("AL-09", G10, "Skateboard in Agrabah", ["AL00_SKATE_01"], "free",
  mech="Skateboard challenge with two counters and a timer (journal: SB Sand Slider).", p1="Hop On, ride, tricks.", p2="Own board.",
  sep="A second skateboard.", adapt="Two riders; score rule.", verify="Both ride at once; the score counts both.", test="Same as TTR-03.",
  judg="OBJECT", phase="3")

# ------------------------------------------------------------------ 11. Halloween Town
R("NM-01", G11, "Town Square and Candy Cane Lane fights", ["NM00_MS101", "NM06_MS102"], "fight",
  mech="Fights where town objects (traps, a merry-go-round) can be used against the enemies.",
  sep=BASESEP + " The twin wears the same costume (objects P_EX100_NM / P_EX100_XM from the party table): VERIFIED by lane J (Halloween j-nm51, Christmas j-nm53).")
R("NM-02", G11, "Prison Keeper", ["NM03_MS103"], "boss")
R("NM-03", G11, "Oogie Boogie", ["NM09_MS104"], "boss",
  mech="Sora stands on a conveyor belt and knocks presents at Oogie's platform until it drops; then Oogie can be hit.",
  adapt=A_RC + " Both heroes on the belt; presents hit by either must count.")
R("NM-04", G11, "Lock, Shock and Barrel", ["NM10_MS201"], "boss", mech="Trap the three imps in boxes with a Reaction Command (counter).",
  adapt=A_RC + " A capture by either hero must count.")
R("NM-05", G11, "Retrieve the presents", ["NM00_MS202"], "fight", mech="Defeat Heartless that carry stolen presents (counter).")
R("NM-06", G11, "The Experiment", ["NM07_MS204"], "boss",
  mech="Boss whose head and arms come off and fight alone.",
  sep="The room data places the real Sora object here instead of the placeholder; lane F tested it: it gets a twin.")
R("NM-07", G11, "Gift Wrapping (story and journal minigame)", ["NM10_MS203", "NM10_MS203_FREE"], "free",
  mech="Text: 'Wrap some presents by firing toys into the boxes while avoiding Lock, Shock, and Barrel!' Counters; the replay has a timer.",
  p1="Aim and fire toys into moving boxes.", p2="Fires toys too, with an own aim.",
  sep="A second toy cannon. Object F_NM180 (PLAYER type, no player stats; lane J calls it the toy cannon) is placed in group m_50. VERIFIED by lane J (j-sp-nm63): a second copy stands beside the first and the game runs; whether it fires was not checked.",
  adapt="The second cannon must aim and fire from controller 2; one shared count; Lock, Shock and Barrel must bother both.",
  verify="Both fire at the same time from own cannons; presents wrapped by either are counted.",
  test="Lane J's disc with the merged patch: does the second cannon aim and fire on pad 2, and does the counter count its presents?", judg="OBJECT", phase="3")
R("NM-08", G11, "Skateboard in the toy factory", ["NM09_SKATE_01"], "free",
  mech="Skateboard challenge with two counters and a timer (journal: SB Workshop Rave).", p1="Hop On, ride, tricks.", p2="Own board.",
  sep="A second skateboard.", adapt="Two riders; score rule.", verify="Both ride at once; the score counts both.", test="Same as TTR-03.",
  judg="OBJECT", phase="3")

# ------------------------------------------------------------------ 12. Pride Lands
R("LK-00", G12, "Lion form: moving and fighting in the Pride Lands", [], "free",
  mech="Sora is a lion in this world (object P_LK100): runs on four legs, dashes, own combos; the party table gives no Drive Forms here.",
  p1="Lion moves: run, dash, jump, lion combos, magic, items, Limits with Simba.", p2="Second lion with the same moves.",
  sep="Twin lion through the placeholder: VERIFIED (two lion Soras in a fight, lane F).", adapt="None seen so far.",
  verify="Both lions run, dash and fight separately.", test="Done once by lane F (pad 1 on both); repeat with the merged patch.",
  judg="BASE", phase="1-3", ev="V+M")
R("LK-01", G12, "Elephant Graveyard: first fight", ["LK05_MS101"], "fight", p1="Lion kit.", p2="Lion kit on controller 2.")
R("LK-02", G12, "King's Den: protect Timon and Pumbaa", ["LK02_MS102"], "fight",
  mech="Keep the hyenas away from Timon and Pumbaa (gauge); Pumbaa can be used to gather them.", p1="Lion kit.", p2="Lion kit on controller 2.")
R("LK-03", G12, "Scar", ["LK14_MS103"], "boss", p1="Lion kit plus the boss's Reaction Command.", p2="The same on controller 2.")
R("LK-04", G12, "The three hyenas", ["LK05_MS201"], "boss", mech="Chase and defeat Shenzi, Banzai and Ed (counter).",
  p1="Lion kit.", p2="Lion kit on controller 2.")
R("LK-05", G12, "Groundshaker", ["LK15_MS202"], "attach",
  mech="Giant boss fought with Simba only; Sora gets onto its back with Reaction Commands and attacks from there.",
  p1="Lion kit plus the climb and ride commands.", p2="The same on controller 2.")

# ------------------------------------------------------------------ 13. Space Paranoids
R("TR-01", G13, "Pit Cell: charge the terminal", ["A_SCT_GIMMICK"], "free",
  mech="Fill an energy gauge at a terminal to open the way (the file has a gauge and no text).", p1="Use the terminal with Triangle.",
  p2="Can use it too.", sep="Nothing special.", adapt="P2 needs the prompt; shared gauge.",
  verify="P2 alone fills the gauge.", test="Jump disc to tr00 with the merged patch.", judg="BASE", phase="2-3", ev="M",
  note="Twin form in this world is object P_EX100_TR (party table): VERIFIED by lane J (j-tr54: two Soras in the Tron suit with Keyblades).")
R("TR-02", G13, "Canyon: find the real parts", ["TR01_MS101"], "score",
  mech="Hit the right cubes among fakes to fill a gauge before the timer ends.", adapt="Hits by either hero must count.")
R("TR-03", G13, "Light Cycle (story, two parts, and journal minigame)", ["TR02_MS102A", "TR02_MS102B", "TR02_MS102_FREE"], "free",
  mech="Ride a light cycle on the Game Grid: Attack, Charge and Guard against Heartless cycles, walls on both sides; defeat five, then reach the goal; the replay scores with two counters.",
  p1="Steer the cycle, Attack, Charge, Guard.", p2="Own cycle, steers and fights independently.",
  sep="A second P_EX100_TR_LIGHTCYCLE (placed directly in room tr02, groups b_97 and b_99). VERIFIED by lane J (j-sp-tr61): a second copy gives two light cycles with riders side by side, no crash.",
  adapt="The course, its camera and its goal are built around one cycle: collisions between the two cycles, who must reach the goal, score for two. Own controller per cycle is not tested.",
  verify="Both ride at once; each defeats a Heartless cycle; the run ends when the rule for two is met.",
  test="Lane J's disc with the merged patch: does each cycle follow its own controller through Attack, Charge and Guard?", judg="OBJECT", phase="3")
R("TR-04", G13, "Dataspace: freeze the monitors", ["TR03_MS103"], "score",
  mech="Defeat enemies to fill a gauge, then use Freeze on the monitors before the timer ends.", adapt="Either hero fills the gauge and freezes; " + A_RC)
R("TR-05", G13, "Hostile Program", ["TR04_MS104"], "boss", mech="Boss beaten by filling a gauge with dropped clusters and using Freeze.")
R("TR-06", G13, "Second visit: Game Grid and I/O Tower fights", ["TR02_MS210", "TR04_MS202"], "fight")
R("TR-07", G13, "Solar Sailer", ["TR07_MS203"], "fight", mech="Defend the sailer while it flies (gauge).")
R("TR-08", G13, "Sark and the MCP", ["TR09_MS204", "TR09_MS205"], "boss",
  mech="Beat Sark, then break the MCP's walls and hold the Delete command to finish it.",
  adapt=A_RC + " Delete is a held Reaction Command at one spot: can both hold it?")

# ------------------------------------------------------------------ 14. World That Never Was
R("EH-01", G14, "The man in black (Roxas)", ["EH21_MS101"], "free",
  mech="Solo duel. Text: 'Keep an eye out for reaction commands when he attacks'. A Reaction Command takes his Keyblades; he can take Sora's.",
  p1=KIT + " Plus the duel commands.", p2=P2KIT + " Plus the duel commands.",
  sep="Own 'Keyblade taken' state for each hero (not known how the game stores it).",
  adapt="The duel command and the stolen-Keyblade state are built for one Sora.",
  verify="Each player wins the duel command once; a hero who loses the Keyblade gets it back; the other hero is unaffected.",
  test="Jump disc to eh21 with the merged patch: P2 answers the duel command.", judg="UNKNOWN", phase="2")
R("EH-02", G14, "Xigbar", ["EH10_MS102"], "boss", mech="Gunner boss; the room changes shape; summons are switched off by the mission.")
R("EH-03", G14, "Luxord", ["EH14_MS103"], "free",
  mech="Fight on time gauges instead of HP (two gauges in the mission file); Luxord turns Sora into a card or a die and plays card games through Reaction Commands (Begin Game, the O and X commands, Stop Dice).",
  p1="Attack to drain Luxord's time; win the card games; move as a card or die when transformed.",
  p2="The same: own attacks, own card games, own transformation.",
  sep="Player objects M_EX950_CARD and M_EX950_DICE exist for the transformed Sora: one per hero. A time gauge per hero, or one for the team.",
  adapt="Time gauge rule for two; a transformed hero while the other still fights; card games started by either.",
  verify="Each player is transformed once and wins a card game once; the time gauges behave by the agreed rule.",
  test="Jump disc to eh14 with the merged patch: watch the gauges when each hero is hit; let each be turned into a die.", judg="ADAPT", phase="3")
R("EH-04", G14, "Saix", ["EH15_MS104"], "boss",
  mech="Berserk gauge; text: 'Use his weapon to your advantage!': a dropped claymore is picked up with Reaction Commands (Berserk, Eclipse, Magna Storm).",
  adapt=A_RC + " One claymore drops: whoever takes it; the other keeps fighting.")
R("EH-05", G14, "Xemnas, first fight", ["EH19_MS105"], "attach",
  mech="Solo boss with scripted Reaction Command sequences on the side of the skyscraper (Facedown, Clash, Break Through, Finish).")
R("EH-06", G14, "The energy core, two fights", ["EH25_MS109", "EH26_MS108"], "fight",
  mech="Stop the core by attacking it, then knock enemies into it (three gauges and a timer); Reaction Commands save a falling hero.")
R("EH-07", G14, "Chase through the falling buildings", ["EH27_MS106", "EH28_MS107"], "attach",
  mech="Text: 'Go after Xemnas! Use reaction commands to open paths!': buildings are cut with Reaction Commands (Slicer, Sky Scraper) in a scripted run.")
R("EH-08", G14, "Armoured Xemnas, first fight", ["EH24_MS110"], "boss")
R("EH-09", G14, "The dragon: shooting from the flying bike", ["EH22_MS111", "TEST_EH22_MS111"], "free",
  mech="Shooter sequence: Sora and Riku on one flying bike (objects P_EX100_SIDECAR and P_EH000_SIDECAR) against the dragon; text: Laser to shoot, Drain to absorb fire; gauge; own script module (minigame/eh_22.bar).",
  p1="Fly, fire the Laser, use Drain.", p2="An own bike, or an own seat with own weapons, flown or aimed independently.",
  sep="A second vehicle, or a second weapon station on the one bike; the module's state for a second pilot. VERIFIED by lane J (j-sp-eh72): a second P_EX100_SIDECAR gives a second Sora with NO vehicle, and he is gone from the later pictures.",
  adapt="Built for one bike: the vehicle, flight path, camera, the dragon's targets and the gauge must take two.",
  verify="Both shoot and drain at the same time, each steering or aiming alone; the dragon's fire reaches both.",
  test="Find what makes the bike (the Riku part P_EH000_SIDECAR and the module); place a full second set and see what the module does.", judg="ADAPT", phase="3")
R("EH-10", G14, "Armoured Xemnas, second fight", ["EH23_MS112"], "boss", mech="Fight beside Riku; Drive is switched off; the text points at jumping and gliding.")
R("EH-11", G14, "Xemnas, final fight", ["EH20_MS113"], "free",
  mech="Last boss beside Riku. When Sora is caught the game hands the controller to Riku for a rescue; the last attack is survived by mashing two buttons together.",
  p1=KIT + " Plus the duel and rescue commands.", p2=P2KIT + " Plus the same commands.",
  sep="The 'caught' state per hero; who is rescued by whom.",
  adapt="The rescue is built as 'Sora is caught, the player plays Riku'. With two heroes: the free hero rescues the caught one, or Riku does. The two-button finale could be one button per player.",
  verify="Each player is caught once and rescued by the other; the finale is cleared by both mashing.",
  test="Jump disc to eh20 with the merged patch: let Xemnas catch each hero in turn.", judg="ADAPT", phase="3")

# ------------------------------------------------------------------ 15. 100 Acre Wood
R("PO-00", G15, "The book and walking in the wood", [], "free",
  mech="Enter and leave the storybook in Merlin's house; walk between Pooh's friends' houses. No Donald or Goofy in this world (45 player placements, none with a friend beside it).",
  p1="Run, jump, talk, enter and leave the book.", p2="The same.", sep="Twin on foot (placeholder method).",
  adapt="P2 needs the Talk / Enter The Book prompts; both at the exit.", verify="Both walk the wood; either starts a talk.",
  test="Jump disc to po00 with the merged patch.", judg="BASE", phase="3", ev="V+M")
R("PO-01", G15, "A Blustery Rescue", ["PO06_MS101", "PO06_MS101_FREE", "PO06_MS100"], "free",
  mech="Sora and Pooh are carried by the wind to rescue Piglet (special player object PO06_PLAYER, script module minigame/po_06.bar); timer; counters in the replay.",
  p1="Steer in the wind, dodge and hit obstacles.", p2="An own flyer, steering independently.",
  sep="A second PO06_PLAYER; the module's state for a second flyer. VERIFIED by lane J (j-sp-po54): a second copy gives two flying Soras side by side that fly on together (pad 1 on both), no crash.",
  adapt="Built for one flyer: own controller for the second, path, camera, timer and score for two.",
  verify="Both steer separately through the whole flight.", test="Lane J's disc with the merged patch: does the second flyer follow pad 2?", judg="ADAPT", phase="3")
R("PO-02", G15, "Hunny Slider", ["PO07_MS201", "PO07_MS201_FREE", "PO07_MS200"], "free",
  mech="Slide down a course with Pooh collecting hunny (3,243 pickup objects in the room data) and avoiding obstacles (object PO07_PLAYER, module minigame/po_07.bar); counter.",
  p1="Steer the slide, jump, collect.", p2="An own slider, steering independently.",
  sep="A second PO07_PLAYER; the module's state for a second slider.", adapt="Built for one slider: track position, camera and score for two.",
  verify="Both steer separately; hunny collected by either is counted.", test="Jump disc to po07 with a second PO07_PLAYER.", judg="ADAPT", phase="3")
R("PO-03", G15, "Balloon Bounce", ["PO08_MS301", "PO08_MS301_FREE", "PO08_MS300", "TEST_PO08_MS300"], "free",
  mech="Bounce upward on balloons with Pooh, popping them for points (object PO08_PLAYER, module minigame/po_08.bar); counter and timer.",
  p1="Steer the bounces.", p2="An own bouncer, steering independently.",
  sep="A second PO08_PLAYER; the module's state for a second bouncer.", adapt="Built for one bouncer: camera and score for two.",
  verify="Both bounce separately; points from either are counted.", test="Jump disc to po08 with a second PO08_PLAYER.", judg="ADAPT", phase="3")
R("PO-04", G15, "The Expotition", ["PO09_MS401", "PO09_MS401_FREE", "PO09_MS400"], "free",
  mech="In the Spooky Cave on foot: Pooh's friends follow (four helper objects), enemies appear, a gauge and a timer run.",
  p1="Run, jump, attack, lead the friends.", p2="The same on controller 2.", sep="Twin on foot; nothing special seen in the data.",
  adapt="Whom the friends follow; shared gauge and timer.", verify="P2 alone leads the friends through part of the cave.",
  test="Jump disc to po09 with the merged patch.", judg="BASE", phase="3")
R("PO-05", G15, "The Hunny Pot", ["PO01_MS501", "PO01_MS501_FREE", "PO01_MS500"], "free",
  mech="Minigame at Starry Hill with Pooh (helper object N_PO010_BTL), a counter and a gauge. How it plays is not clear from the data.",
  p1="Not known in detail.", p2="The same as P1, independently.", sep="Not known.", adapt="Not known.",
  verify="Two players play it and both take an active part.", test="Jump disc to po01 with the twin and watch.", judg="UNKNOWN", phase="3", ev="V+M")

# ------------------------------------------------------------------ 16. Atlantica
R("LM-00", G16, "Swimming in Atlantica", ["LM02_MS101"], "free",
  mech="Sora is a merman here (object P_LM100; the friends are N_LM010_PLY and N_LM020_PLY). Swim with both sticks, Dolphin Kick, talk. There are no fights in this world.",
  p1="Swim, dash, lock on, talk.", p2="Second merman with the same moves.",
  sep="Twin merman through the placeholder: VERIFIED by lane J (j-lm02: two merman Soras; each pad its own hero with lane E's patch, in sync, j-sep-lm02). 15 player placements, none with a friend beside it; the swimming spots are in lane J's override file.",
  adapt="P2 needs the Talk prompt.", verify="Both swim separately; either talks to Flounder.",
  test="Done by lane J for moving; repeat with the merged patch for talking.", judg="BASE", phase="3", ev="V+M")
R("LM-01", G16, "The musical: tutorial and five songs", ["LM02_MS102", "LM04_MS103", "LM01_MS201", "LM03_MS301", "LM09_MS401", "LM04_MS501"], "free",
  mech="Rhythm game: press the shown buttons in time with the song. Songs named in the text: Swim This Way, Part of Your World, Under the Sea, Ursula's Revenge, A New Day is Dawning, plus a Musical Tutorial. Which mission file is which song is not matched from the data.",
  p1="Press the prompted buttons in time.", p2="Has own prompts to press in the same song.",
  sep="No object: an own prompt stream (or an own share of the prompts) for P2.",
  adapt="The song is one stream of prompts for one controller. For two: prompts dealt to both players, or each prompt answered by both; one shared score.",
  verify="Both players have to press to pass a song; a miss by either lowers the score.",
  test="Jump disc to a song with the merged patch: press only on pad 2 and see whether the game accepts it.", judg="ADAPT", phase="3")
R("LM-02", G16, "The musical: replay versions (journal: 'Perform ... again', 'A Musical Challenge')",
  ["LM04_MS103_FREE", "LM01_MS201_FREE", "LM03_MS301_FREE", "LM09_MS401_FREE", "LM04_MS501_FREE"], "free",
  mech="The same five songs replayed for a score.", p1="As LM-01.", p2="As LM-01.", sep="As LM-01.", adapt="As LM-01.",
  verify="As LM-01, with the score recorded in the journal.", test="Covered by LM-01.", judg="ADAPT", phase="3")

# ------------------------------------------------------------------ 17. Gummi
R("GM-01", G17, "Flying a Gummi Route (nine routes)", [], "free",
  mech="A separate flying-shooter mode with its own data (gumibattle: 9 maps, 27 stage files). Routes named in the text: Asteroid Sweep, Stardust Sweep, Broken Highway, Ancient Highway, Phantom Storm, Sunlight Storm, Splash Island, Floating Island, Assault of the Dreadnought.",
  p1="Fly the ship, fire cannons and lasers, use the Slash attack, change the Teeny Ship formation.",
  p2="A meaningful simultaneous role (user requirement): an own ship, or own weapons flown or aimed independently.",
  sep="A second player ship. The mode already has up to two escort 'Teeny Ships' (file tinyset.bin; text 'Build Teeny Ships that will defend your Gummi Ship'): a candidate for P2's ship. Not examined.",
  adapt="Nothing is known yet about how this mode reads the controller, places the camera or scores. Needs its own study.",
  verify="Both players fly and shoot at the same time through a whole route; damage and medals work for both.",
  test="Find the Gummi mode's controller read (same method as lane A); try giving a Teeny Ship to pad 2.", judg="ADAPT", phase="3", ev="V")
R("GM-02", G17, "Gummi mission levels and EX missions", [], "free",
  mech="Each route has mission levels 1 to 3 and EX missions (text: 'Level 1 missions are Medal hunts', 'EX Mission'); some need a ship built to a rule.",
  p1="Fly to the mission's score, medal or build rule.", p2="As GM-01; P2's kills and medals must count.",
  sep="As GM-01.", adapt="Score, medal and rank rules for two ships; build rules ('fly without any Teeny Ships') clash with P2 flying a Teeny Ship.",
  verify="A level-1 medal hunt is cleared with medals collected by both.", test="After GM-01's test.", judg="ADAPT", phase="3", ev="V")
R("GM-03", G17, "Gummi Garage: building ships", [], "free",
  mech="Menu mode: build and upgrade Gummi Ships and Teeny Ships.", p1="Builds ships.", p2="Can build and choose an own ship.",
  sep="An own ship slot for P2 if P2 flies an own ship.", adapt="Menus are driven by controller 1 only today.",
  verify="P2 picks or builds the ship P2 flies.", test="None until GM-01 is answered.", judg="UNKNOWN", phase="4", ev="V")
R("GM-04", G17, "World map: flying between worlds", ["WORLDMAP"], "free",
  mech="The world map is its own room (wm00) where the 'player' is a cursor object (WM_CURSOR in the party table) that flies to world symbols.",
  p1="Flies the cursor, chooses a world or a route.", p2="Not a gameplay mode with two bodies: one cursor.",
  sep="None proposed; a twin cursor would have no meaning.", adapt="Decision for the user: either player may steer, or player 1 only. The twin tool must not add a second cursor here.",
  verify="The world map works with two players connected; the agreed player can steer.", test="Open the world map on the kh2-coop-v1 disc and see what a second placeholder does there.",
  judg="UNKNOWN", phase="3", ev="V")

# ------------------------------------------------------------------ 18. Final Mix extras
R("FM-01", G18, "Cavern of Remembrance: climbing and forced fights",
  ["HB22_FM_SWITCH", "HB24_CONFINE", "HB24_CONFINE_2", "HB24_CONFINE_3", "HB25_CONFINE_1", "HB25_CONFINE_2", "HB25_CONFINE_3", "HB25_CONFINE_4"], "fight",
  mech="A long climb that needs the growth abilities (High Jump, Aerial Dodge, Glide), a switch room, and locked-room fights against many Nobodies.",
  adapt="None beyond the base: the twin has the same abilities as P1 (lane D). The 'both at the exit' rule over long jumps needs a look.", phase="3")
R("FM-02", G18, "Absent Silhouette: Vexen", ["HB32_FM_VEX", "HB33_FM_VEX"], "free",
  mech="Text: 'Destroy his shield and attack him! Don't stand on the emblem, or he'll extract your data!' A gauge fills while Sora stands on the emblem; a copy of Sora then joins the fight.",
  p1=KIT, p2=P2KIT, sep="The data gauge and the copy: one per hero, or one for the team.",
  adapt="Built around one Sora: whose data fills the gauge and whom the copy imitates.",
  verify="Each player stands on the emblem in turn; the gauge and the copy follow the agreed rule.",
  test="Jump disc to hb32 with the merged patch: only P2 stands on the emblem; read the gauge.", judg="ADAPT", phase="3")
R("FM-03", G18, "Absent Silhouette: Lexaeus", ["HB33_FM_LEX"], "boss", mech="Text: 'His strength will keep increasing throughout the battle. Unleash counterattacks to seal the deal!' Two counters.", phase="3")
R("FM-04", G18, "Absent Silhouette: Zexion", ["HB34_FM_ZEX"], "free",
  mech="Text: 'His mystical book is the key to this fight!' He traps Sora inside books and another space.",
  p1=KIT, p2=P2KIT, sep="The 'trapped in the book' state per hero.", adapt="Not known: what happens to the free hero while the other is trapped.",
  verify="Each player is trapped once and gets out; the other keeps playing meanwhile.", test="Jump disc to hb34 with the merged patch.", judg="UNKNOWN", phase="3")
R("FM-05", G18, "Absent Silhouette: Larxene", ["HB33_FM_LAR"], "boss", mech="Text: she duplicates herself and all copies are real; hitting two gives double damage.", phase="3")
R("FM-06", G18, "Absent Silhouette: Marluxia", ["HB38_FM_MAR"], "free",
  mech="Text: 'Each attack with his scythe will decrease the count above your head, and it's game over when the count hits 0.'",
  p1=KIT, p2=P2KIT, sep="The count above the head: one per hero.",
  adapt="A count for each hero, and the rule when one hero's count reaches 0 (the user's rule: Game Over only when both are down).",
  verify="Each player is hit by the scythe and sees an own count fall.", test="Jump disc to hb38 with the merged patch: let him hit only P2; watch the count.", judg="ADAPT", phase="3")
R("FM-07", G18, "Data rematches of the Organization (journal: 'Fight ... again')", ["TT20_MS603_RE", "BB15_MS203_RE", "EH20_MS113_RE"], "free",
  mech="Level-99 versions of the Organization fights. Three have own mission files; for the others the level-99 boss object sits in the original mission's room data (Demyx, Xigbar, Luxord, Saix, Xemnas). The journal lists twelve names plus Xemnas.",
  p1="As in each original fight.", p2="As in each original fight.", sep="As in each original fight.",
  adapt="Whatever each original fight needs (rows TTR-11, BB-09, HB-05, EH-01 to EH-05, EH-11, FM-02 to FM-06).",
  verify="Each data fight is won by two players with both taking an active part.", test="After the originals.", judg="ADAPT", phase="3")
R("FM-08", G18, "The Lingering Will", ["DC07_FM_NAZO"], "free",
  mech="Text: 'Defeat the mystery man! He's stronger than any previous foe.' He can seal commands and capture Sora, who breaks free by mashing.",
  p1=KIT + " Plus breaking free.", p2=P2KIT + " Plus breaking free.", sep="Sealed commands and the 'captured' state per hero.",
  adapt="Not known: sealing and capture are built for one Sora.", verify="Each player is captured once and breaks free; a seal on one does not seal the other.",
  test="Jump disc to dc07 with the merged patch.", judg="UNKNOWN", phase="3")
MUSH = [("FM-M01", "No. 1", "EH03_KINOKO_XEM", "eh03", "score of 70 or more"), ("FM-M02", "No. 2", "NM07_KINOKO_XIG", "Christmas Tree Plaza", "score of 80 or more"),
        ("FM-M03", "No. 3", "BB13_KINOKO_XAL", "Bridge", "score of 450 or more"), ("FM-M04", "No. 4", "MU09_KINOKO_VEX", "Palace Gate", "score of 85 or more"),
        ("FM-M05", "No. 5", "AL10_KINOKO_LEX", "Treasure Room", "within 10 seconds"), ("FM-M06", "No. 6", "HE17_KINOKO_ZEX", "Underworld Caverns: Atrium", "within 45 seconds"),
        ("FM-M07", "No. 7", "TT36_KINOKO_SAI", "Tunnelway", "within 10 seconds"), ("FM-M08", "No. 8", "TT25_KINOKO_AXE", "The Tower", "score of 85 or more"),
        ("FM-M09", "No. 9", "HB04_KINOKO_DEM", "Castle Gate", "score of 75 or more"), ("FM-M10", "No. 10", "CA13_KINOKO_LUX", "Moonlight Nook", "within 55 seconds"),
        ("FM-M11", "No. 11", "WI02_KINOKO_MAR", "Timeless River", "within 19 seconds"), ("FM-M12", "No. 12", "TT14_KINOKO_LAR", "The Old Mansion", "score of 40 or more"),
        ("FM-M13", "No. 13", "HB02_KINOKO_ROX", "The Great Maw", "no target in the journal list")]
for rid, no, ms, room, goal in MUSH:
    R(rid, G18, f"Mushroom XIII: {no} ({room})", [ms], "score",
      mech=f"A mushroom in a coat sets a hit-count or speed challenge; journal target: {goal}. Matching the file to the number is read from the name suffix and the order of the journal list (HYPOTHESIS).",
      adapt="Hits and kills by either hero must count toward the one score or time.")
R("FM-09", G18, "Puzzle pieces", [], "free",
  mech="157 puzzle-piece objects (F_EX260) are placed in the rooms; the journal has a Puzzle Mode where the pieces are assembled.",
  p1="Picks up pieces; assembles puzzles in the journal.", p2="Picks up pieces too.", sep="Nothing special; pieces go to the shared collection.",
  adapt="P2 needs the pick-up prompt; the journal is a controller-1 menu today.", verify="P2 picks up a piece and it appears in the journal.",
  test="Free roam with the merged patch at a known piece.", judg="BASE", phase="2", ev="V")

# ------------------------------------------------------------------ 19. game-wide
R("GW-01", G19, "Reaction Commands of enemies and bosses", [], "free",
  mech="Triangle commands that appear at the right moment near an enemy (list of all command names: section 5).",
  p1="Sees the prompt, presses Triangle, the hero performs the move.", p2="The same for the enemy P2 faces.",
  sep="Own command state per hero: exists (lane G: P2 opened Save from an own Reaction Command).",
  adapt="No prompt is drawn for P2 yet; enemies offer commands to the hero they consider the player.",
  verify="For each enemy type with a command: P2 alone triggers it once.", test="Free-roam disc with the merged patch: P2 uses Cyclone on a Soldier.",
  judg="BASE", phase="2")
R("GW-02", G19, "Talk, Examine, Open: people, objects and chests", [], "free",
  mech="Field commands: 328 chests, 1,057 talk or examine objects and 764 field objects are placed in the rooms.",
  p1="Talks, examines, opens chests.", p2="The same; a chest opened by either is opened for both.", sep="Nothing special; one shared inventory.",
  adapt="Prompts for P2; talk windows are answered by controller 1 only today.", verify="P2 alone opens a chest and starts a talk.",
  test="Free-roam disc with the merged patch at a chest.", judg="BASE", phase="2", ev="V")
R("GW-03", G19, "Save points, world points, shops, synthesis", [], "free",
  mech="16 save points, 52 world-exit points, 23 shop points and the Moogle synthesis menu.",
  p1="Opens and uses the menus.", p2="Can open them; using them needs controller 2 to drive a menu.",
  sep="Nothing special.", adapt="Menus listen to controller 1 only (lane G: P2 can open Save but not operate it).",
  verify="P2 saves the game and buys an item alone.", test="Free-roam disc: P2 opens Save and tries to confirm.", judg="BASE", phase="4", ev="V")
R("GW-04", G19, "Drive Forms (Valor, Wisdom, Limit, Master, Final, Anti) and Revert", [], "free",
  mech="Sora changes into another player object for a while; forms use up friends. Every world row of the party table names an object for every form.",
  p1="Drives, fights in the form, reverts.", p2="Drives too, in an own form.",
  sep="An own form object and an own Drive gauge per hero. Which friends a form uses up is not in the data tables (lane C).",
  adapt="Two heroes and only two friends to fuse with (plan: one friend each; forms needing both for one hero at a time); Drive state is shared in the save block today (lane D); memory for two forms; a new player object built while another exists counts as a second hero today (lane D).",
  verify="Each player drives while the other stays normal; then both at once in different one-friend forms.",
  test="Free-roam disc with Donald and Goofy and forms unlocked by a test patch: each pad selects Valor in turn.", judg="ADAPT", phase="3")
R("GW-05", G19, "Limits with party members", [], "free",
  mech="Team attacks from the limit table (25 rows: Twin Howl, Bushido, Red Rocket, Whirli-Goof, Knocksmash, Comet, Duck Flare, Speedster, Bluff, Wildcat, Dance Call, Setup, Session, Trinity ...); each pairs 'Sora' with one partner and plays through Reaction Commands.",
  p1="Starts a Limit and plays its commands.", p2="Starts a Limit too (user rule: either player; first press wins the friend).",
  sep="Which hero is the limit's 'Sora' is not in the data: our rule.", adapt="The limit's scripted moves and camera are for one hero; what the other hero does meanwhile.",
  verify="Each player starts one Limit with Donald and one with Goofy and finishes it.", test="Free-roam disc with the merged patch: pad 2 selects a Limit through the shortcut.",
  judg="UNKNOWN", phase="3", ev="V+M")
R("GW-06", G19, "Summons (Chicken Little, Genie, Stitch, Peter Pan)", [], "free",
  mech="A summon joins and replaces the friends; each has an own team attack. Chicken Little's is called FPS Mode (a first-person view).",
  p1="Summons, fights with the summon, uses its team attack.", p2="Can summon too.",
  sep="Which friends a summon replaces is not in the data (lane C).", adapt="One summon at a time or one per hero; a first-person view belongs to one player on a shared screen.",
  verify="Each player summons once; the team attack works for the summoner.", test="After GW-04's test, the same with a summon.", judg="UNKNOWN", phase="3", ev="V+M")
R("GW-07", G19, "Magic and MP", [], "free",
  mech="19 magic commands in the command table; MP gauge with recharge.",
  p1="Casts from the menu or the L1 shortcuts.", p2="Casts from own shortcuts with own MP.",
  sep="Own MP: exists (lane D). Own shortcuts: Fire, Blizzard, Thunder verified through L1 (lane G).",
  adapt="MP separation with real casting is untested in the merged build; P2 has no magic menu on screen.",
  verify="P2 casts until MP runs out while P1's MP stays full.", test="Merged build test (j) of lane M.", judg="BASE", phase="1-2", ev="V")
R("GW-08", G19, "Items, equipment, abilities, level-ups", [], "free",
  mech="Item stock, Keyblade and armour, ability points, growth abilities, levels.",
  p1="Uses items; equips; sets abilities.", p2="Uses items from the shared stock; own Keyblade and abilities come in Phase 4.",
  sep="Today the twin reads P1's character record: same stats, abilities and level (lane D).", adapt="Items through P2's commands are untested (lane G); own equipment for P2 is Phase 4.",
  verify="P2 uses a Potion on each hero; later P2 equips an own Keyblade.", test="Merged build: pad 2 uses an item through the shortcut.", judg="BASE", phase="2 and 4", ev="V")
R("GW-09", G19, "START menu, journal, map, cutscene skip", [], "free",
  mech="Pause menu, Jiminy's Journal, area map, 'Skip Scene'.", p1="Opens and uses them.", p2="Can pause and skip too (plan: skip by vote, either may pause).",
  sep="Nothing special.", adapt="All of these listen to controller 1 only today (lane G).", verify="P2 pauses, opens the journal, and votes to skip a scene.",
  test="Any disc with the merged patch: press START on pad 2.", judg="BASE", phase="5", ev="V")
R("GW-10", G19, "Falling, the King Mickey rescue, Game Over, Continue", [], "free",
  mech="Sora at 0 HP means Game Over; 11 missions carry the flag that lets King Mickey step in (his objects are in the party table); 'retry' missions restart in place.",
  p1="Falls; plays Mickey when the rescue triggers; continues.", p2="Falls like Goofy and is brought back (user rule); Game Over only when both are down.",
  sep="An own 'down' state per hero.", adapt="Today either hero at 0 HP gives Game Over (lane D). The Mickey rescue with two heroes: who becomes Mickey. Continue crashes on test discs that start inside a mission (lane B).",
  verify="One hero falls and is healed back by the other; both fall and Game Over appears; Continue restores both.",
  test="Free-roam disc, merged patch: let only P2 fall.", judg="ADAPT", phase="2", ev="V")
R("GW-11", G19, "Changed-form worlds", [], "free",
  mech="The party table gives another player object per world: Roxas (three variants), Halloween and Christmas costumes, Tron suit, Timeless River, lion, merman.",
  p1="Plays in the world's form.", p2="Twin in the same form.",
  sep="The second PLAYER placeholder follows the form: VERIFIED for Roxas, Sora and the lion (lane F) and for the Halloween and Christmas costumes, the Tron suit, Timeless River, the merman and Sora with Donald and Goofy (lane J: j-nm51, j-nm53, j-tr54, j-wi52, j-lm02, j-hb58), each with its weapon.",
  adapt="None known. Drive Forms in these worlds and Roxas's two-Keyblade form are not tested.", verify="Both heroes have the right look and moves on first entering each world.",
  test="Done by lanes F and J on jump discs; repeat in a real playthrough.", judg="BASE", phase="3", ev="V")
R("GW-12", G19, "Enemies choosing a target; helpers following", [], "free",
  mech="Enemies pick whom to attack; Donald, Goofy and guests follow and help the player.",
  p1="Is attacked; is followed and healed.", p2="Is attacked the same way; gets a helper when the heroes split (user rule).",
  sep="Nothing special.", adapt="Enemies attack only the engine's player today (lane D); helpers follow that player.",
  verify="With the heroes far apart, enemies near each attack that one; one helper goes with each.", test="Fight disc with the merged patch: heroes on opposite sides.",
  judg="ADAPT", phase="2", ev="V")
R("GW-13", G19, "Camera, lock-on, mini-map", [], "free",
  mech="One camera, one lock-on mark, one mini-map (hidden in most missions by a flag).",
  p1="Turns the camera, locks on.", p2="Own lock-on exists (lane G); own camera only with own screens.",
  sep="An own view per player: VERIFIED by lane K's study that the engine can draw a view for each hero in every step with its own two-view render mode; the HUD is still drawn once, for player 1.",
  adapt="Shared screen: the camera follows P1 (lane E). Own screens are a user decision after lane K; a HUD and prompts for P2's view are not built.",
  verify="P2 locks on to an own target; with own screens each player sees an own camera.", test="Lane K's demo.", judg="ADAPT", phase="1C / 2B", ev="V")
R("GW-14", G19, "Room exits, story triggers, world changes", [], "free",
  mech="6,572 trigger volumes and 2,320 scripted jumps move the party between rooms and start scenes.",
  p1="Walks into an exit or trigger.", p2="The same; user rule: both must be in it.",
  sep="Nothing special.", adapt="Done for room exits on one door (lane E); story triggers share the code but are untested; ambush triggers follow P1 only.",
  verify="At every kind of trigger: one hero alone does nothing, both start it.", test="Lane M's exit test, then a boss-room door.", judg="BASE", phase="1-2", ev="V")

# ------------------------------------------------------------------ 20. unused
R("UN-01", G20, "Names in room scripts with no mission file; files no room script names; test entries",
  ["TEST_SKATEBOARD", "TEST_HE_COLOSSEUM", "TEST_HE_COLOSSEUM2", "TEST_HE_COLOSSEUM3", "TEST_MU07_MS999", "ZZ_HE09_MS201",
   "AL00_SKATE_02", "HB09_SKATE_02", "NM09_SKATE_02", "TT05_AXEL", "TT20_AXEL", "TT40_KINOKO_AXE", "AL14_MS_S", "HE_COL_8PP_BOSS"], "free",
  mech="Left-over or test entries (lane C: 14 names without a file, 8 files without a script).", p1="Probably never reached in play.",
  p2="Nothing unless a playthrough reaches one.", sep="None.", adapt="None.", verify="If a playthrough shows one of these on screen, add a row for it.",
  test="None.", judg="UNKNOWN", phase="-", ev="V")
