# User requirement: full gameplay parity in every world and special sequence

Received from the user on 2026-11-10. Verbatim copy; this text is the authority when the plan and this differ.

---

**Important Requirement: Full Gameplay Parity in Every World and Special Sequence**

I want you to pay special attention to gameplay mechanics that are unique to specific worlds, missions, boss fights, and story sequences in Kingdom Hearts II Final Mix.

For example, in Agrabah, Sora rides the Magic Carpet. Since we have two playable Soras, **P2 must also have their own independently controllable Magic Carpet**.

This requirement applies to the entire game, not just Agrabah.

**Core rule:**

Whenever the original game gives P1 a special vehicle, mount, transformation, movement mechanic, weapon, ability, interaction, or temporary gameplay mode, P2 must receive equivalent functionality.

Examples to investigate:

- **Agrabah:** Both players must be able to ride and independently control their own Magic Carpets.
- **Space Paranoids:** Both players must actively participate in Light Cycle sequences, with independent controls where appropriate.
- **Gummi Ship:** Both players must have meaningful, simultaneous gameplay roles.
- **Pride Lands:** Both players transform into lions and retain equivalent movement and combat capabilities.
- **Twilight Town:** Both players must be able to participate in skateboarding, Struggle, and other special activities.
- **Atlantica:** Both players must participate in the musical gameplay.
- **Roxas's prologue:** Both players must receive the appropriate playable character, equipment, abilities, and special interactions.
- **Boss encounters:** Any special mechanic, temporary transformation, scripted movement, or Reaction Command available to P1 must also work for P2.

These are examples, not an exhaustive list. You must investigate every world and gameplay sequence to identify other cases.

**Implementation requirements:**

1. If P1 receives a personal vehicle or mount, P2 should receive an equivalent independent vehicle or mount.
2. Both players must have direct control. P2 must never become an AI-controlled passenger or spectator.
3. Both players must be able to attack, defend, interact, and use relevant special abilities whenever those actions are available in that gameplay mode.
4. Special mechanics must work simultaneously for both players, including collisions, damage, enemy targeting, animations, and transitions.
5. If a sequence originally supports only one character or vehicle, investigate how to adapt it for two active players.
6. Both players must participate in the same story events and progression without losing their gameplay functionality.
7. Never consider a world or mission complete just because P1 can finish it while P2 follows or waits.

**Before implementation:**

Audit every world, mission, minigame, special movement sequence, and boss encounter.

Create a checklist identifying:

- The original gameplay mechanic.
- What P1 can do.
- What P2 must be able to do.
- Whether each player requires a separate object, vehicle, character state, or interaction.
- Any special adaptations required.
- How the functionality will be verified with two human-controlled players.

Add this requirement to the existing project plan and ensure every relevant phase includes appropriate tests.

**The ultimate goal is simple: If Kingdom Hearts II gives Sora something special to play with, both players should be able to experience that mechanic as genuine, independently controlled players.**

Do not limit this requirement to the examples I provided. Apply it consistently throughout the entire game.

## The user's decisions on this requirement (added by the project, not his text above)

- THE USER'S OK OF 2026-11-15 (evening): a move that a hero starts with his OWN green command (a player-initiated Reaction
  Command: Xaldin's jumps, Demyx's water forms, Xigbar's sniper part, Luxord's games and the like) stays that hero's alone,
  and the other hero stays free and keeps fighting. His words: "B OK. Keep player-initiated green Reaction Commands exclusive to the player who activates them. The other player should remain free to continue fighting."
  This is an exception to point 5 above that he approved; it is the behaviour of builds 14 to 21.
- The same message asks for the bosses' AUTOMATIC grabs: "For single-target attacks, prefer capturing only the targeted player.
  For genuinely shared boss mechanics, both players should participate meaningfully." (docs\STATE.md, Ninth round, part 109
  and the parts after it.)
