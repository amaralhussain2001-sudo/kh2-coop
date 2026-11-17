"""One-off: turn the kit texts of TEST build 2 into TEST build 3 (own screens). Run once."""
import pathlib

KIT = pathlib.Path(__file__).resolve().parent / "kit"

p = KIT / "1-READ-ME-FIRST (KH2 TEST).txt"
t = p.read_text(encoding="utf-8").replace("\r\n", "\n")


def rep(old, new):
    global t
    if t.count(old) != 1:
        raise SystemExit("expected one place for: %r (found %d)" % (old[:70], t.count(old)))
    t = t.replace(old, new)


rep("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 2\n===========================================================",
    "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 3 (OWN SCREENS)\n=========================================================================")
rep("""Sora later). Player 2 plays a second copy of the same hero with their own controller. Both PCs show the same
picture in this build (player 1's camera). The text is English. The buttons are the ones of the Japanese disc.
""", """Sora later). Player 2 plays a second copy of the same hero with their own controller.
NEW IN BUILD 3: EACH PC SHOWS ITS OWN PLAYER. Your PC shows your hero, your camera, your command menu and your
HP gauge, full size. The small round gauge is the other player. Both heroes are still in the same room.
The text is English. The buttons are the ones of the Japanese disc.

!! BOTH PLAYERS MUST CHOOSE THE SAME "PICTURE QUALITY" IN THE LAUNCHER. Use "4x High" (this folder starts with it).
   Do NOT use "Auto": two different graphics cards would pick different values, and with this game the screen
   then says "OUT OF SYNC" although nothing is wrong.
""")
rep("""2. Game: the "2 Players TEST v2" file. Controllers: "2 players, no multitap". Screen: "Normal 4:3" (as the game
   was made). "Widescreen 16:9" also stayed in sync in my test; it is a community change of the game's camera,
   so it is the host's choice.""",
    """2. Game: the "2 Players TEST v2" file (the disc file did not change since build 2). Controllers: "2 players, no
   multitap". Screen: "Normal 4:3" (as the game was made; widescreen was not tried with own screens).
   Picture quality: "4x High" on BOTH PCs (see the top of this file).""")

start = t.index("------------------------------------------------------------------\nWHAT WORKS IN THIS BUILD")
end = t.index("------------------------------------------------------------------\nWHAT TO SEND BACK")
mid = """------------------------------------------------------------------
WHAT WORKS IN THIS BUILD
------------------------------------------------------------------
- NEW: own screens. Each PC shows its own hero with its own camera (right stick), its own command menu and
  cursor, its own big HP / MP gauge and its own lock-on ring. The small round gauge shows the other player.
  When the game takes the camera (story scenes, the pause menu, the save menu, Game Over) both PCs show the
  same full picture, and own screens come back afterwards.
- A second hero stands beside player 1's hero in every room and in every form tried so far (Roxas, Sora, the lion,
  the costumes).
- Each hero is moved by its own controller: run, jump, attack and combos, guard, dodge, magic through the L1
  shortcuts, own lock-on target. Each hero walks by its own camera.
- Each hero has its own HP and MP. Level and skills are the same for both.
- Enemies and bosses attack BOTH heroes. They go for the nearer hero; when both are near they take turns.
- A hero whose HP reaches 0 goes DOWN and stays in the room, like Goofy. He gets up by himself after 45 seconds
  in a fight (a few seconds outside a fight) with a quarter of his HP. The other player can bring him back sooner
  with a Potion or with Cure (stand near him). It is Game Over only when BOTH heroes are down at the same time;
  Continue then brings both back.
- Room exits. Both heroes must be at the exit: one in the doorway, the other within a few steps. While one hero
  waits there the screen says "Waiting for the other player." No exit while a hero is down.
- Bosses have 75 % more HP than in the original game, because two heroes hit them (Pete in the Underworld cave:
  40 % more, because of his time limit). Normal enemies are as in the original.
- Saving works (one shared save).

------------------------------------------------------------------
KNOWN PROBLEMS (no need to report these)
------------------------------------------------------------------
- Own screens are new. If they give trouble (wrong picture, very slow, a crash), read the folder
  SHARED-SCREEN-FALLBACK: it holds the same game with one shared screen.
- Player 1's 3D picture is a little less sharp than player 2's. (Player 1's picture takes a detour inside the
  game. A sharper way exists but still loses the words in the command menu, so it is not in this build.)
- The game can drop below its normal pace for a moment in busy fights, because it draws the world twice.
- Text boxes, story text and the "Waiting for the other player." sign appear on both screens.
- Player 2's command menu is new: Attack and the L1 shortcuts were tried, the sub-menus (Magic, Items) were not.
  The menu's open and close movements can look too fast.
- Donald and Goofy follow and help player 1's hero only.
- HP orbs (the green balls): player 2's hero probably cannot pick them up. Not tested.
- A Potion heals the hero who is down; if nobody is down, the hero who used it. There is no choice on screen.
- While a hero is down there is no countdown, only the red face in the gauge.
- START, the main menu, the save menu and every text box listen to controller 1 only.
- Boss moves that grab or carry the hero take player 1's hero only (seen with the first big boss of the Roxas
  part). Player 2 keeps playing during them.
- The first hours (Roxas in Twilight Town) are full of special jobs. Known not right for two yet: Mail Delivery
  (only player 1 gets the skateboard), Grandstander (the job stalls if player 2 hits the ball), the bag job,
  and the counter of two "hit them N times" fights does not count player 2's hits. If a job cannot be finished,
  let player 1 do it alone and tell me which one it was.
- NOT tested yet with two heroes: Drive Forms, Limits, Summons, most bosses, most minigames, the Gummi Ship,
  shops and the journal with own screens.
- Everything was tested by scripts on one PC only. You are the first two humans to play it.

"""
t = t[:start] + mid + t[end:]
rep("""- Do not change emulator settings (graphics, speed hacks) in "Controller settings"; only the controls.""",
    """- Do not change emulator settings (graphics, speed hacks) in "Controller settings"; only the controls.
- The same Picture quality on both PCs ("4x High").""")
rep("""- Do not add or remove files in emulator\\patches. (The launcher writes one small file there itself,
  game-file-check.pnach. It is not a patch; it makes the join check compare the game file.)""",
    """- Do not add or remove files in emulator\\patches. (The launcher writes one small file there itself,
  game-file-check.pnach. It is not a patch; it makes the join check compare the game file. The file ending in
  .view tells the emulator which picture this PC shows; without it both PCs show player 1's picture.)""")
p.write_text(t, encoding="utf-8", newline="\n")

p = KIT / "HOW-TO-SET-UP (FRIEND).txt"
t = p.read_text(encoding="utf-8").replace("\r\n", "\n")
rep("""4. In the COPY, the folder emulator\\patches must hold exactly these two files (plus, later, one small file the
   launcher writes itself, game-file-check.pnach):
       SLPM-66675_F266B00B.pnach      SLUS-21067_568A5C78.pnach""",
    """4. In the COPY, the folder emulator\\patches must hold exactly these three files (plus, later, one small file
   the launcher writes itself, game-file-check.pnach):
       SLPM-66675_F266B00B.pnach      SLPM-66675_F266B00B.view      SLUS-21067_568A5C78.pnach""")
rep("""6. Open "1-READ-ME-FIRST (KH2 TEST).txt" in the copy and follow it: make the disc file (STEP 1), then start with
   START-KH2-TEST.bat (STEP 3).""",
    """6. Open "1-READ-ME-FIRST (KH2 TEST).txt" in the copy and follow it: make the disc file (STEP 1; if you made the
   "TEST v2" file for build 2 already, keep it, it is the same), then start with START-KH2-TEST.bat (STEP 3).
7. In the launcher choose Picture quality "4x High". Both players must use the same value.
If you had the test folder of build 1 or 2: unzip this zip into it in the same way (step 2). It replaces the
emulator program too.""")
p.write_text(t, encoding="utf-8", newline="\n")
print("kit texts updated")
