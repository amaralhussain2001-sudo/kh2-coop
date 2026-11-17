"""One-off: turn the kit read-me of TEST build 3 into TEST build 4 (own menu lists, own Drive gauge, text boxes for
either player). Run once."""
import pathlib

KIT = pathlib.Path(__file__).resolve().parent / "kit"
p = KIT / "1-READ-ME-FIRST (KH2 TEST).txt"
t = p.read_text(encoding="utf-8")
if "TEST BUILD 4" in t:
    raise SystemExit("already build 4")


def rep(old, new):
    global t
    if t.count(old) != 1:
        raise SystemExit("expected one place for %r (found %d)" % (old[:60], t.count(old)))
    t = t.replace(old, new)


rep("PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 3 (OWN SCREENS)",
    "PS2 ONLINE - KINGDOM HEARTS II, TWO PLAYERS - TEST BUILD 4 (OWN SCREENS)")
rep("""NEW IN BUILD 3: EACH PC SHOWS ITS OWN PLAYER. Your PC shows your hero, your camera, your command menu and your
HP gauge, full size. The small round gauge is the other player. Both heroes are still in the same room.""",
    """EACH PC SHOWS ITS OWN PLAYER (since build 3). Your PC shows your hero, your camera, your command menu and your
HP gauge, full size. The small round gauge is the other player. Both heroes are still in the same room.
NEW IN BUILD 4: the lists inside the command menu (Magic and the others) show only on the screen of the player
who opened them; each hero keeps his own Drive gauge from room to room; either player can close text boxes.
If you have build 3: replace the whole test folder with this one (both players). The disc file stays the same.""")
rep("""- Each hero has its own HP and MP. Level and skills are the same for both.""",
    """- Each hero has its own HP, MP and Drive gauge. Each player's hits fill only his own Drive gauge.
  Level, skills, equipment, items and munny are common: one wallet, one item stock, the same abilities.""")
rep("""- Saving works (one shared save).""",
    """- Tutorial boxes and talk text can be closed by either player (Circle).
- Saving works (one shared save). The save holds player 1's Drive gauge; after loading, both heroes start with it.""")
rep("""- Text boxes, story text and the "Waiting for the other player." sign appear on both screens.
- When one player opens Magic (or another list inside the command menu), the OTHER player's screen shows that
  list too, until it is closed. Each player's buttons still act on their own menu, and the L1 shortcut list is
  right on each screen. The menu's open and close movements can look too fast.
""", """- Text boxes, story text and the "Waiting for the other player." sign appear on both screens (both players
  should see them).
""")
rep("""- START, the main menu, the save menu and every text box listen to controller 1 only.""",
    """- START, the main menu and the save menu listen to controller 1 only. Other full screens (the rules and result
  screens of the small games) may also still need player 1's Circle.""")
p.write_text(t, encoding="utf-8")
print("read-me is build 4")
