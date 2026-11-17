"""Merged patch generator for the KH2 two-player project (CRC F266B00B, KH2 Final Mix SLPM-66675).

  python -I tools/merge/make_all.py [outDir] [--v2] [--check] [--without NAME ...] [--keep-base]

Default outDir: patches/merged-v1 (with --v2: patches/merged-v2). Writes SLPM-66675_F266B00B.pnach and listing.txt
(every word with its meaning).
--v2        merged build 2 = build 1 + SECTION commands (lane G) - SECTION base (no longer needed with lane G;
            --keep-base keeps it) + two more glue routines (see GLUE).
--check     also compares the unchanged routines word-for-word with the source lanes' delivered patch files.
--without   leave a section out (names: base, identity, exits, ownhp, commands). 'glue' goes with identity + ownhp.

One section per source lane, so a later lane (G: player 2's own attacks and commands) can replace or add one:

  SECTION base      lane A (kept by lane E): before a player object runs the shared control object's update,
                    S->pad = that object's own controller.            cave 0x000F0020-0x000F002F
  SECTION identity  lane E: the hero made from the PLAYER placeholder is and stays the engine's player on
                    controller 1; any other player object is the twin on controller 2.   cave 0x000F0300-0x000F040B
  SECTION exits     lane E: room exits and event triggers need BOTH heroes in the same trigger volume.
                                                                       cave 0x000F0420-0x000F058B, vars 0x000F05C0-D7
  SECTION ownhp     lane D: the twin has its own unit slot (own current HP / MP), same stats as player 1.
                    Routines D2, R, RM, W1, W2, D6 unchanged at lane D's addresses 0x000F015C-0x000F02BB.
                    Lane D's routine D1 (0x000F0100) is NOT used: see glue.
  SECTION commands  (--v2) lane G: the hero on controller 2 gets its own control object S2 (command menu state,
                    cursor, shortcut mode, command request, lock-on). Routines unchanged at lane G's addresses
                    0x000F0800-0x000F0AD3; S2's data is 0x000F1000-0x000F1AFF (reserved, must be zero at boot).
  SECTION glue      this lane: makes lane D's "who gets the fresh slot" follow lane E's roles instead of the
                    build order; with --v2 it also moves a twin that was built first onto S2 and releases S2 when
                    a twin goes away.                                  cave 0x000F0C00-0x000F0DEF, var 0x000F0DF0

Why the glue is needed (the clash): lane D decided "second hero" by "a player object already exists". The
twin-everywhere disc builds the twin FIRST and the placeholder hero second, and lane E makes the LATER
placeholder-made object player 1's hero. Unmerged, the hero would have received the marked slot and the twin the
game's real one. The glue routine m_slot asks lane E's role variables instead (see GLUE below).
"""
import pathlib
import struct
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE))
from asm import assemble  # noqa: E402
import mips  # noqa: E402

ELF = ROOT / "local" / "iso-files" / "SLPM_666.75"

SYM = {
    # game routines
    "GET_PAD": 0x00167F18,        # GetLogicalController(index)
    "S_UPDATE": 0x001D6BA0,       # shared control object S: update wrapper
    "FACTORY": 0x00179FD0,        # player factory
    "ATTACH": 0x001781A8,         # attach a player object (camera target, trigger owner, party slot 0, S)
    "DETACH": 0x001781E8,         # detach (called from the base destructor)
    "PH_LOOKUP": 0x001D1438,      # player object id for a form (called on the placeholder path only)
    "POS_OF": 0x0016C028,         # pointer to an object's position
    "AREA_OFFER": 0x00182980,     # offer a position to one area event
    "FIND_OR_SHARE": 0x001A15D0,  # unit slot by status id: find or share, then load stats
    "FRESH_SLOT": 0x001A1728,     # unit slot: always a new one
    "LOAD_STATS": 0x001A11E0,     # load a slot's stats from its character record
    "WRITE_BACK": 0x001A1840,     # write a slot's current values back into its record
    "NEXT_USED": 0x0031F168,      # next slot in use
    "ABIL_END": 0x001C3060,       # original tail call of LOAD_STATS
    "CO_DETACH": 0x001D69D0,      # release a control object from its hero (also clears party slot 0)
    "PARTY_SET": 0x0013DDC0,      # party table: slot a0 = object a1 (slot 0 = HUD owner)
    # game data
    "G_PLAYER": 0x0034E948,       # engine's player object pointer
    "G_LASTPLAYER": 0x00352400,   # last built object of the main player class
    "PAD0": 0x0034D6C0,
    "PAD1": 0x0034D720,
    "POOL": 0x01C62FB8,           # unit slot pool
    "SAVE_HP": 0x0032D98E,        # save data + 0x1E5E: the twin's current HP between rooms
    "SAVE_MP": 0x0032D98F,        # save data + 0x1E5F: the twin's current MP + 1
    # lane E variables (not written by the patch file; that memory is zero at boot)
    "V_FLAG": 0x000F05C0,         # 1 while a placeholder-made player object is being created
    "V_ISP1": 0x000F05C4,         # role of the object being created (1 = player 1's hero, 0 = twin)
    "V_OLD": 0x000F05C8,          # engine's player before the creation
    "V_TWIN": 0x000F05CC,         # the twin object (0 if none): other lanes may read it
    "V_PASS2": 0x000F05D0,        # 1 during the second exit offer
    "V_P1": 0x000F05D4,           # player 1's hero during the second exit offer
    # lane D work flag
    "BUSY": 0x000F02F0,
    # glue variable
    "V_BUILD": 0x000F0DF0,        # 1 while the player factory is running
}

# ---------------------------------------------------------------------------------------------------------------
# SECTION base (lane A, as kept by lane E). Lane G owns this routine and its two hooks from now on.
# ---------------------------------------------------------------------------------------------------------------
BASE_AT = 0x000F0020
BASE_SRC = """
a_spad:                           # hook 0x001788A0. a0 = the player object that is updating, t7 = S
    lw t6,0xB38(a0)               # this player object's own controller pointer
    sw t6,0x9E4(t7)               # S->pad = it
    j S_UPDATE                    # continue into S's update, as the game did
    move a0,t7                    # a0 = S (the instruction that sat at 0x00178898)
"""

# ---------------------------------------------------------------------------------------------------------------
# SECTION identity (lane E, text unchanged)
# ---------------------------------------------------------------------------------------------------------------
IDENT_AT = 0x000F0300
IDENT_SRC = """
e_mark:                           # hook 0x0016F0B0 (placeholder path of the object creator)
    lui t7,%hi(V_FLAG)
    li t6,1
    j PH_LOOKUP                   # continue into the routine the game wanted
    sw t6,%lo(V_FLAG)(t7)         # remember: the next player object comes from the PLAYER placeholder

e_getpad:                         # reached from m_getpad (hook 0x0017A000: the factory asks for the controller)
    lui t7,%hi(V_FLAG)
    lw t6,%lo(V_FLAG)(t7)
    sw zero,%lo(V_FLAG)(t7)
    lui t5,%hi(G_PLAYER)
    lw t5,%lo(G_PLAYER)(t5)
    sw t5,%lo(V_OLD)(t7)          # the engine's player before this build
    sltiu t4,t5,1
    or t6,t6,t4                   # player 1's hero if placeholder-made or no player exists yet
    sw t6,%lo(V_ISP1)(t7)
    j GET_PAD
    xori a0,t6,1                  # controller index 0 for player 1's hero, 1 for the twin

e_wrap:                           # reached from m_wrap (hook 0x0016F0F4: the only call of the player factory)
    addiu sp,sp,-32
    sd ra,0(sp)
    jal FACTORY
    nop
    sd v0,8(sp)
    lui t7,%hi(V_FLAG)
    lw t6,%lo(V_ISP1)(t7)
    lw t5,%lo(V_OLD)(t7)
    bne t6,zero,e_p1
    nop
    sw v0,%lo(V_TWIN)(t7)         # a twin was built: hand the "player" role back to the hero
    lui t4,%hi(G_PLAYER)
    sw t5,%lo(G_PLAYER)(t4)
    lui t4,%hi(G_LASTPLAYER)
    sw t5,%lo(G_LASTPLAYER)(t4)
    lw t3,0x48C(t5)
    beq t3,zero,e_noslot
    nop
    sw t5,0x25C(t3)               # the hero's unit slot points back at the hero
e_noslot:
    jal ATTACH                    # game's own attach: camera target, trigger owner, party slot 0, S
    move a0,t5
    b e_done
    nop
e_p1:
    beq t5,zero,e_done
    nop
    beq t5,v0,e_done
    nop
    sw t5,%lo(V_TWIN)(t7)         # an earlier player object becomes the twin ...
    lui t4,%hi(PAD1)
    addiu t4,t4,%lo(PAD1)
    sw t4,0xB38(t5)               # ... and moves to controller 2
e_done:
    ld v0,8(sp)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32

e_dtor:                           # hook 0x00178294 (base destructor of player objects), a0 = dying object
    lui t7,%hi(G_PLAYER)
    lw t6,%lo(G_PLAYER)(t7)
    lui t5,%hi(V_FLAG)
    lw t4,%lo(V_TWIN)(t5)
    bne t4,a0,e_d1
    nop
    sw zero,%lo(V_TWIN)(t5)       # the twin dies: forget it
e_d1:
    beq t6,a0,e_dnormal
    nop
    beq t6,zero,e_dnormal
    nop
    lui t5,%hi(G_LASTPLAYER)      # another player object dies while the engine's player lives:
    sw t6,%lo(G_LASTPLAYER)(t5)   # keep the hero registered
    jr ra
    sw zero,0xB3C(a0)             # only the dying object's own S pointer is cleared
e_dnormal:
    j DETACH                      # the engine's player dies: what the game did
    sw zero,%lo(G_PLAYER)(t7)
"""

# ---------------------------------------------------------------------------------------------------------------
# SECTION exits (lane E, text unchanged)
# ---------------------------------------------------------------------------------------------------------------
EXITS_AT = 0x000F0420
EXITS_SRC = """
e_inside:                         # hook 0x0019A168 (was: jalr v0). a0 = volume, a1 = point, v0 = method, s1 = area event
    addiu sp,sp,-32
    sd ra,0(sp)
    sd v0,8(sp)
    jalr v0                       # is the walking hero inside?
    nop
    beq v0,zero,e_in_out
    nop
    lui t7,%hi(V_TWIN)
    lw t4,%lo(V_PASS2)(t7)        # 1 during the second offer (twin walking)
    lw t3,8(s1)
    lbu t6,0(t3)                  # kind of area event
    addiu t5,t6,-1
    beq t5,zero,e_in_both         # 1 = jump to another room
    addiu t5,t6,-3
    beq t5,zero,e_in_both         # 3 = start an event
    nop
    beq t4,zero,e_in_out          # other kinds: first offer as before ...
    nop
    b e_in_out                    # ... and never on the second offer
    move v0,zero
e_in_both:
    lw a0,%lo(V_TWIN)(t7)         # the other hero: the twin on the first offer ...
    beq t4,zero,e_in_other
    nop
    lw a0,%lo(V_P1)(t7)           # ... player 1's hero on the second
e_in_other:
    beq a0,zero,e_in_out          # no twin here: as before
    nop
    jal POS_OF                    # game: pointer to an object's position
    nop
    move a1,v0
    ld t9,8(sp)
    jalr t9                       # is the other hero inside the same volume?
    move a0,s0
e_in_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32

e_offer:                          # hook 0x00182D04 (was: jal 0x00182980). a0 = area event table entry, a1 = point
    addiu sp,sp,-48
    sd ra,0(sp)
    sd a0,8(sp)
    jal AREA_OFFER                # first offer: player 1's hero, as the game does
    nop
    lui t7,%hi(V_TWIN)
    lw t6,%lo(V_TWIN)(t7)
    beq t6,zero,e_of_done         # no twin
    nop
    ld a0,8(sp)
    lw t5,4(a0)
    andi t5,t5,1
    bne t5,zero,e_of_done         # this entry is switched off
    nop
    lw t0,8(a0)                   # the area event
    beq t0,zero,e_of_done
    nop
    lw t1,8(t0)
    lbu t2,0(t1)                  # its kind
    addiu t3,t2,-1
    beq t3,zero,e_of_go
    addiu t3,t2,-3
    bne t3,zero,e_of_done         # only exits (1) and event triggers (3) get the second offer
    nop
e_of_go:
    lui t5,%hi(G_PLAYER)
    lw t4,%lo(G_PLAYER)(t5)
    beq t4,zero,e_of_done
    nop
    beq t4,t6,e_of_done           # the twin is the engine's player (should not happen): leave it
    nop
    sw t4,%lo(V_P1)(t7)
    sw t6,%lo(G_PLAYER)(t5)       # the engine's player = the twin, only during the second offer
    li t3,1
    sw t3,%lo(V_PASS2)(t7)
    lw t3,4(t0)
    andi t3,t3,0x18               # what the first offer found (inside / door-approach flags)
    sd t3,16(sp)
    sd t0,24(sp)
    jal POS_OF
    move a0,t6
    move a1,v0
    jal AREA_OFFER                # second offer: the twin as the walking hero
    ld a0,8(sp)
    lui t7,%hi(V_TWIN)
    sw zero,%lo(V_PASS2)(t7)
    lw t4,%lo(V_P1)(t7)
    lui t5,%hi(G_PLAYER)
    sw t4,%lo(G_PLAYER)(t5)       # put the engine's player back
    ld t0,24(sp)
    ld t3,16(sp)
    lw t2,4(t0)
    or t2,t2,t3
    sw t2,4(t0)                   # keep the first offer's flags
e_of_done:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,48
"""

# ---------------------------------------------------------------------------------------------------------------
# SECTION ownhp (lane D). D2, R, RM, W1, W2, D6 are lane D's routines at lane D's addresses, unchanged.
# Lane D's D1 (0x000F0100-0x000F0158) is replaced by m_slot in the glue section.
# ---------------------------------------------------------------------------------------------------------------
OWNHP_AT = 0x000F015C
OWNHP_SRC = """
D2:                               # hook 0x001A1518 (find-slot-by-id loop). s0 = slot, s1 = wanted id, t7 = slot id
    bne t7,s1,D2_next
    lw t6,0x250(s0)
    bltz t6,D2_next               # a marked slot (the twin's) is never found by a search by id
    nop
    j 0x001A1520                  # found
    nop
D2_next:
    j 0x001A14C4                  # loop head
    nop

R:                                # hook 0x001A1238 (load stats). s0 = slot, s1 = record, t5 = max HP
    lbu t7,4(s1)                  # the record's current HP (the original instruction)
    lw t6,0x250(s0)
    bgez t6,R_done
    lui t6,%hi(SAVE_HP)
    lbu t6,%lo(SAVE_HP)(t6)       # marked slot: the twin's own saved HP (0 = none)
    movn t7,t6,t6
R_done:
    jr ra
    slt t6,t5,t7                  # redo the compare that sat in the delay slot

RM:                               # hook 0x001A1248 (load stats). s0 = slot, s1 = record
    lbu t6,6(s1)                  # the record's current MP (the original instruction)
    lw t7,0x250(s0)
    bgez t7,RM_done
    lui t7,%hi(SAVE_MP)
    lbu t7,%lo(SAVE_MP)(t7)       # marked slot: the twin's own saved MP + 1 (0 = none)
    beq t7,zero,RM_done
    nop
    addiu t6,t7,-1
RM_done:
    jr ra
    nop

W1:                               # hook 0x001A1854 (write back). a0 = slot, t6 = record, t7 = HP byte
    lw t5,0x250(a0)
    bltz t5,W1_second
    nop
    j 0x001A185C
    sb t7,4(t6)                   # normal slot: into its record (the original instruction)
W1_second:
    lui t5,%hi(SAVE_HP)
    j 0x001A185C
    sb t7,%lo(SAVE_HP)(t5)        # marked slot: into the twin's own save byte

W2:                               # hook 0x001A1870 (write back). a0 = slot, t5 = record, t7 = MP byte
    lw t4,0x250(a0)
    bltz t4,W2_second
    nop
    j 0x001A1878
    sb t7,6(t5)                   # normal slot (the original instruction)
W2_second:
    lui t4,%hi(SAVE_HP)
    lbu t3,%lo(SAVE_HP)(t4)       # the HP just stored
    addiu t7,t7,1
    movz t7,zero,t3               # HP 0: store "none", the hero restarts from player 1's values
    j 0x001A1878
    sb t7,%lo(SAVE_MP)(t4)

D6:                               # hook 0x001A1438 (end of LOAD_STATS). a0 = slot + 0x1CC, ra = caller
    addiu sp,sp,-32
    sd ra,0(sp)
    sd s0,8(sp)
    sd s1,16(sp)
    addiu s0,a0,-0x1CC
    jal ABIL_END                  # the original tail call
    nop
    lui t7,%hi(BUSY)
    lw t6,%lo(BUSY)(t7)
    bne t6,zero,D6_out            # already inside this routine
    lw t5,0x254(s0)
    addiu t6,zero,1
    beq t5,t6,D6_hero             # status id 1 = Sora
    addiu t6,zero,14
    bne t5,t6,D6_out              # status id 14 = Roxas
    nop
D6_hero:
    sw t6,%lo(BUSY)(t7)
    move s1,zero
D6_loop:
    lui a0,%hi(POOL)
    addiu a0,a0,%lo(POOL)
    jal NEXT_USED                 # next slot in use
    move a1,s1
    beq v0,zero,D6_end
    move s1,v0
    beq s1,s0,D6_loop
    lw t6,0x254(s1)
    lw t5,0x254(s0)
    bne t6,t5,D6_loop             # only the other hero's slot (same status id)
    nop
    jal WRITE_BACK                # save its current HP / MP ...
    move a0,s1
    move a0,s1
    jal LOAD_STATS                # ... and reload its stats from the shared record
    move a1,zero
    beq zero,zero,D6_loop
    nop
D6_end:
    lui t7,%hi(BUSY)
    sw zero,%lo(BUSY)(t7)
D6_out:
    ld ra,0(sp)
    ld s0,8(sp)
    ld s1,16(sp)
    jr ra
    addiu sp,sp,32
"""

# ---------------------------------------------------------------------------------------------------------------
# SECTION glue (this lane)
#   m_getpad / m_wrap: wrap lane E's two factory hooks so that V_BUILD = 1 exactly while the player factory runs.
#   m_slot: replaces lane D's D1 at the unit-slot request of the player base constructor (0x00177E74).
#     - not inside the factory (some other code builds a player object): the game's own behaviour;
#     - the object being built is a TWIN (lane E role 0): fresh slot, marked, stats loaded (lane D's D1 path);
#     - the object being built is PLAYER 1'S HERO and an earlier player object exists (it becomes the twin when the
#       factory returns): that earlier object's slot is marked and reloaded NOW, then the hero asks the game for
#       its slot in the normal way. Because marked slots are skipped by searches (D2), the game makes a new,
#       unmarked slot for the hero: "Sora's slot" is the hero's whatever the build order.
# ---------------------------------------------------------------------------------------------------------------
GLUE_AT = 0x000F0C00
GLUE_GETPAD = """
m_getpad:                         # hook 0x0017A000 (was: jal 0x00167F18; lanes A and E hooked the same word)
    lui t7,%hi(V_BUILD)
    li t6,1
    j e_getpad                    # lane E's rule decides the role and the controller
    sw t6,%lo(V_BUILD)(t7)        # the player factory is running
"""
GLUE_WRAP_V1 = """
m_wrap:                           # hook 0x0016F0F4 (was: jal 0x00179FD0; lane E hooked the same word)
    addiu sp,sp,-16
    sd ra,0(sp)
    jal e_wrap                    # lane E: call the factory, then apply the identity rule
    nop
    lui t7,%hi(V_BUILD)
    sw zero,%lo(V_BUILD)(t7)      # the factory is done
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""
GLUE_SLOT = """
m_slot:                           # hook 0x00177E74 (was: jal 0x001A15D0). a0 = status id, a1 = form argument
    lui t7,%hi(V_BUILD)
    lw t6,%lo(V_BUILD)(t7)
    beq t6,zero,m_plain           # not built by the factory: the game's behaviour
    lui t5,%hi(V_ISP1)
    lw t6,%lo(V_ISP1)(t5)
    beq t6,zero,m_twin            # role 0: a twin (built after the hero)
    lw t4,%lo(V_OLD)(t5)          # the engine's player before this build
    beq t4,zero,m_plain           # player 1's hero and nobody before it: the game's behaviour
    nop
    lw t3,0x48C(t4)               # the earlier object's unit slot
    beq t3,zero,m_plain
    nop
    lw t2,0x254(t3)
    bne t2,a0,m_plain             # not the same kind of character: leave it alone
    nop
    lw t2,0x250(t3)
    bltz t2,m_plain               # already marked
    lui t1,0x8000
    or t2,t2,t1
    sw t2,0x250(t3)               # the earlier object is the twin: its slot becomes the marked one
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    sd a1,16(sp)
    move a0,t3
    jal LOAD_STATS                # load it once more, now as a marked slot (own HP / MP bytes)
    move a1,zero
    ld a0,8(sp)
    ld a1,16(sp)
    ld ra,0(sp)
    addiu sp,sp,32
m_plain:
    j FIND_OR_SHARE               # the game's own request (a new unmarked slot if the only other one is marked)
    nop
m_twin:
    addiu sp,sp,-16
    sd ra,0(sp)
    jal FRESH_SLOT                # the twin: a slot of its own
    nop
    beq v0,zero,m_out
    lui t6,0x8000
    lw t7,0x250(v0)
    or t7,t7,t6
    sw t7,0x250(v0)               # mark it
    sd v0,8(sp)
    move a0,v0
    jal LOAD_STATS                # load once more, now as a marked slot
    move a1,zero
    ld v0,8(sp)
m_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
"""
# --v2 only. With lane G a hero's control object is chosen when it ATTACHES, by its controller at that moment. A
# twin that was built first attached as "controller 1" (to S) and only became the twin, on controller 2, when the
# hero arrived. So in that case m_wrap attaches the twin once more (lane G then gives it S2) and then the hero once
# more, so that camera target, trigger owner, HUD owner and S end on the hero.
# Lane E lets a twin die without the game's detach so that player 1's hero stays registered. With lane G the twin
# owns a control object (S2) that has to be released: m_dtor does it with the game's routine, which also clears
# party slot 0 (the HUD owner), so that is given back to the hero.
GLUE_WRAP_V2 = """
m_wrap:                           # hook 0x0016F0F4 (was: jal 0x00179FD0; lane E hooked the same word)
    addiu sp,sp,-32
    sd ra,0(sp)
    jal e_wrap                    # lane E: call the factory, then apply the identity rule
    nop
    lui t7,%hi(V_BUILD)
    sw zero,%lo(V_BUILD)(t7)      # the factory is done
    lui t5,%hi(V_ISP1)
    lw t6,%lo(V_ISP1)(t5)
    beq t6,zero,m_w_out           # a twin was built after the hero: lane E already attached the hero again
    lw t4,%lo(V_OLD)(t5)
    beq t4,zero,m_w_out           # the hero is the first player object of the room
    nop
    beq t4,v0,m_w_out
    nop
    sd v0,8(sp)                   # v0 = player 1's hero, t4 = the earlier object, now the twin on controller 2
    jal ATTACH                    # attach the twin again: lane G's attach gives it S2
    move a0,t4
    jal ATTACH                    # then the hero again: camera target, trigger owner, HUD owner and S are its
    ld a0,8(sp)
    ld v0,8(sp)
m_w_out:
    ld ra,0(sp)
    jr ra
    addiu sp,sp,32
"""
GLUE_DTOR = """
m_dtor:                           # hook 0x00178294 (was: jal 0x001781E8; lane E hooked the same word). a0 = dying object
    lui t5,%hi(V_TWIN)
    lw t4,%lo(V_TWIN)(t5)
    bne t4,a0,m_dt_go             # not the twin: lane E's routine decides
    lui t7,%hi(G_PLAYER)
    lw t6,%lo(G_PLAYER)(t7)
    beq t6,zero,m_dt_go           # no engine player left: lane E does the game's full detach (releases S2 too)
    nop
    beq t6,a0,m_dt_go
    nop
    lw t3,0xB3C(a0)               # the twin's control object
    beq t3,zero,m_dt_go
    lui t2,0x01C6
    addiu t2,t2,-2768             # S
    beq t3,t2,m_dt_go             # the twin still uses S: nothing of its own to release
    nop
    addiu sp,sp,-32
    sd ra,0(sp)
    sd a0,8(sp)
    sd t6,16(sp)
    jal CO_DETACH                 # release the twin's own control object, as the game does for S
    move a0,t3
    ld a1,16(sp)
    jal PARTY_SET                 # party slot 0 (HUD owner) back to player 1's hero
    move a0,zero
    ld a0,8(sp)
    ld ra,0(sp)
    addiu sp,sp,32
m_dt_go:
    j e_dtor                      # lane E's rule (keeps the hero registered, clears the twin's pointers)
    nop
"""


def jal(t):
    return (3 << 26) | ((t >> 2) & 0x3FFFFFF)


def jmp(t):
    return (2 << 26) | ((t >> 2) & 0x3FFFFFF)


def asm_lines(base, text, sym):
    """Assemble and keep, for the listing, the label and the source text of every word."""
    words, syms = assemble(base, text, sym)
    rows, pending, pc = [], [], base
    for raw in text.split("\n"):
        code, _, comment = raw.partition("#")
        code, comment = code.strip(), comment.strip()
        if not code:
            continue
        if code.endswith(":") and " " not in code:
            pending.append((code[:-1], comment))
            continue
        rows.append((pc, words[(pc - base) // 4], list(pending), code, comment))
        pending = []
        pc += 4
    assert len(rows) == len(words)
    return rows, syms


def load_elf_words():
    data = ELF.read_bytes()
    e_phoff = struct.unpack_from("<I", data, 0x1C)[0]
    e_phentsize, e_phnum = struct.unpack_from("<HH", data, 0x2A)
    segs = []
    for i in range(e_phnum):
        p_type, p_offset, p_vaddr, _, p_filesz = struct.unpack_from("<IIIII", data, e_phoff + i * e_phentsize)
        if p_type == 1:
            segs.append((p_vaddr, p_offset, p_filesz))

    def word(addr):
        for vaddr, off, size in segs:
            if vaddr <= addr < vaddr + size:
                return struct.unpack_from("<I", data, off + addr - vaddr)[0]
        return None
    return word


COMMANDS_S2 = 0x000F1000          # lane G: data of the second control object, 0xB00 bytes (reserved)


def commands_section():
    """Lane G's routines, assembled by lane G's own generator code (copy: tools/merge/g_cmd.py), unchanged."""
    import g_cmd
    a = g_cmd.build(hud_pin=True)
    code = a.build()
    lb = a.labels
    by_addr = {}
    for name, addr in lb.items():
        by_addr.setdefault(addr, []).append((name, ""))
    rows = [(addr, code[addr], by_addr.get(addr, []), "", a.notes.get(addr, "")) for addr in sorted(code)]
    j, jl = g_cmd.j_word, g_cmd.jal_word
    hooks = [
        (0x001781C4, j(lb["attach"]), 0x3C0401C6, "tail of the player's attach routine: a hero on controller 2 attaches to S2, any other to S"),
        (0x001781C8, 0x0200282D, 0xDFBF0008, "delay slot: a1 = player object (was ld ra,8(sp))"),
        (0x001D6A10, j(lb["detach_tail"]), None, "end of the control object's detach: 'current control object' = S if S still has a hero, else 0"),
        (0x00179BFC, j(lb["reset"]), jmp(0x001D68F8), "room reset wrapper: reset S, then S2 if it exists"),
        (0x00179BDC, j(lb["ginit"]), jmp(0x001D68E0), "start-up reset wrapper: the same for the start-up reset"),
        (0x00174400, j(lb["enable"]), None, "script command 'player commands on': applies to S and S2"),
        (0x00174404, 0, None, "delay slot (was lui t7,0x35)"),
        (0x001D6C58, j(lb["disable"]), None, "global 'commands off': applies to S and S2"),
        (0x001D6C5C, 0, None, "delay slot (was addiu sp,sp,-16)"),
        (0x001D6C88, j(lb["enable"]), None, "global 'commands on': applies to S and S2"),
        (0x001D6C8C, 0, None, "delay slot (was addiu sp,sp,-16)"),
        (0x0013B258, j(lb["setdisp"]), None, "on-screen menu 'use this control object': if S2 asks, S is shown"),
        (0x0013B25C, 0, None, "delay slot (the store moved into setdisp)"),
        (0x001BDC64, jl(lb["hudshow"]), jal(0x0013B2F8), "control object shows the menu: skipped for S2"),
        (0x001BDCA4, jl(lb["hudhide"]), jal(0x0013B320), "control object hides the menu: skipped for S2"),
        (0x001BDE30, jl(lb["hudfade"]), jal(0x0013B2B8), "control object sets the menu's fade value: skipped for S2"),
    ]
    return rows, hooks


def build(without=(), v2=False):
    sections = []   # (name, title, rows)
    hooks = []      # (addr, new word, expected original word or None, section, meaning)
    sym = dict(SYM)

    def add(name, title, base, src):
        rows, syms = asm_lines(base, src, sym)
        for k, v in syms.items():
            sym.setdefault(k, v)
        sections.append((name, title, rows))
        return syms

    use = lambda n: n not in without  # noqa: E731
    cmds = v2 and use("commands")
    if use("base"):
        s = add("base", "lane A base (kept by lane E; lane G owns it): S->pad follows the updating player object", BASE_AT, BASE_SRC)
        hooks.append((0x00178898, 0, 0x01E0202D, "base", "was 'a0 = S'; moved into a_spad"))
        hooks.append((0x001788A0, jmp(s["a_spad"]), jmp(0x001D6BA0), "base", "player update: go through a_spad before S's update"))
    if use("identity"):
        s = add("identity", "lane E identity: the placeholder hero is the engine's player on controller 1, the other is the twin", IDENT_AT, IDENT_SRC)
        hooks.append((0x0016F0B0, jal(s["e_mark"]), jal(0x001D1438), "identity", "object creator, placeholder path: mark 'made from the PLAYER placeholder'"))
        hooks.append((0x0017828C, 0, 0xADE0E948, "identity", "base destructor: 'engine player = 0' moved into e_dtor"))
        if not cmds:
            hooks.append((0x00178294, jal(s["e_dtor"]), jal(0x001781E8), "identity", "base destructor: a dying twin does not unregister player 1's hero"))
    if use("exits"):
        s = add("exits", "lane E exits: room exits and event triggers need both heroes in the same volume", EXITS_AT, EXITS_SRC)
        hooks.append((0x0019A168, jal(s["e_inside"]), 0x0040F809, "exits", "volume test: the other hero must be inside too (kinds 1 and 3)"))
        hooks.append((0x00182D04, jal(s["e_offer"]), jal(0x00182980), "exits", "area-event loop: second offer with the twin as the walking hero"))
    if use("ownhp"):
        s = add("ownhp", "lane D own HP / MP: marked slot for the twin (routines unchanged)", OWNHP_AT, OWNHP_SRC)
        hooks.append((0x001A1518, jmp(s["D2"]), None, "ownhp", "find-slot-by-id loop: skip marked slots"))
        hooks.append((0x001A1238, jal(s["R"]), None, "ownhp", "load stats: marked slot takes current HP from its own save byte"))
        hooks.append((0x001A1248, jal(s["RM"]), None, "ownhp", "load stats: marked slot takes current MP from its own save byte"))
        hooks.append((0x001A1438, jmp(s["D6"]), jmp(0x001C3060), "ownhp", "end of load stats: reload the other hero's slot too"))
        hooks.append((0x001A1854, jmp(s["W1"]), None, "ownhp", "write back: marked slot's HP goes to its own save byte"))
        hooks.append((0x001A1870, jmp(s["W2"]), None, "ownhp", "write back: marked slot's MP goes to its own save byte"))
    if cmds:
        rows, ghooks = commands_section()
        sections.append(("commands", "lane G commands: second control object S2 for the hero on controller 2 (routines unchanged)", rows))
        for addr, w, orig, meaning in ghooks:
            hooks.append((addr, w, orig, "commands", meaning))
    if use("identity") and use("ownhp"):
        src = GLUE_GETPAD + (GLUE_WRAP_V2 if cmds else GLUE_WRAP_V1) + GLUE_SLOT + (GLUE_DTOR if cmds else "")
        s = add("glue", "merge glue: the fresh marked slot goes to the TWIN by lane E's roles, not by build order"
                + ("; a twin built first is moved onto S2; S2 is released when a twin goes away" if cmds else ""), GLUE_AT, src)
        if cmds:
            hooks.append((0x00178294, jal(s["m_dtor"]), jal(0x001781E8), "glue", "base destructor: release a dying twin's control object S2, then lane E's e_dtor"))
        hooks.append((0x0017A000, jal(s["m_getpad"]), jal(0x00167F18), "glue", "player factory asks for the controller: note 'factory running', then lane E's e_getpad"))
        hooks.append((0x0016F0F4, jal(s["m_wrap"]), jal(0x00179FD0), "glue", "the only factory call: lane E's e_wrap, then 'factory done'"))
        hooks.append((0x00177E74, jal(s["m_slot"]), jal(0x001A15D0), "glue", "base constructor asks for its unit slot: role-based rule (replaces lane D's D1)"))
    elif use("identity"):
        hooks.append((0x0017A000, jal(sym["e_getpad"]), jal(0x00167F18), "identity", "player factory asks for the controller"))
        hooks.append((0x0016F0F4, jal(sym["e_wrap"]), jal(0x00179FD0), "identity", "the only factory call"))
    return sections, hooks


def main():
    args = sys.argv[1:]
    without = set()
    while "--without" in args:
        i = args.index("--without")
        without.add(args[i + 1])
        del args[i:i + 2]
    check = "--check" in args
    v2 = "--v2" in args
    if v2 and "--keep-base" not in args:
        without.add("base")
    args = [a for a in args if a not in ("--check", "--v2", "--keep-base")]
    out = pathlib.Path(args[0]) if args else ROOT / "patches" / ("merged-v2" if v2 else "merged-v1")
    sections, hooks = build(without, v2)
    word = load_elf_words()

    code = {}
    for name, _, rows in sections:
        for addr, w, _, _, _ in rows:
            if addr in code:
                sys.exit("CLASH: code address %08X used by two sections" % addr)
            code[addr] = w
    hook_words = {}
    problems = []
    for addr, w, orig, name, _ in hooks:
        if addr in hook_words or addr in code:
            sys.exit("CLASH: hook address %08X used twice" % addr)
        hook_words[addr] = w
        have = word(addr)
        if have is None:
            problems.append("hook %08X is outside the program file" % addr)
        elif orig is not None and have != orig:
            problems.append("hook %08X: program has %08X, expected %08X" % (addr, have, orig))
    cave = sorted(code)
    for a in cave:
        if word(a) is not None:
            problems.append("code address %08X is inside the program file" % a)
    if problems:
        sys.exit("PROBLEMS:\n  " + "\n  ".join(problems))

    out.mkdir(parents=True, exist_ok=True)
    names = [n for n, _, _ in sections]
    lines = ["gametitle=Kingdom Hearts II Final Mix (SLPM-66675, CRC F266B00B)",
             "comment=Two-player project, merged build %s: " % ("v2" if v2 else "v1") + " + ".join(names) + " (tools/merge/make_all.py).",
             "comment=Every PC in an online game must have this same file (it changes game code)."]
    for a in cave:
        lines.append("patch=1,EE,%08X,word,%08X" % (a, code[a]))
    for a in sorted(hook_words):
        lines.append("patch=1,EE,%08X,word,%08X" % (a, hook_words[a]))
    (out / "SLPM-66675_F266B00B.pnach").write_text("\n".join(lines) + "\n")

    lst = ["Merged patch %s for CRC F266B00B. Every word the patch file writes, with its meaning." % ("v2" if v2 else "v1"), ""]
    for name, title, rows in sections:
        lst.append("=" * 100)
        lst.append("SECTION %s: %s" % (name, title))
        lst.append("  cave 0x%08X-0x%08X (%d words)" % (rows[0][0], rows[-1][0] + 3, len(rows)))
        for addr, w, labels, src, comment in rows:
            for lab, lc in labels:
                lst.append("%s:%s" % (lab, ("    # " + lc) if lc else ""))
            lst.append("  %08X  %08X  %-34s%s" % (addr, w, mips.dis(w, addr), ("# " + comment) if comment else ""))
        lst.append("")
    lst.append("=" * 100)
    lst.append("HOOKS (words changed inside the game program)")
    for addr, w, orig, name, meaning in sorted(hooks):
        have = word(addr)
        lst.append("  %08X  %08X  %-26s was %08X %-28s [%s] %s" % (
            addr, w, mips.dis(w, addr), have, mips.dis(have, addr), name, meaning))
    lst.append("")
    lst.append("VARIABLES (not written by the patch file; they rely on that memory being zero at boot)")
    for k in ("V_FLAG", "V_ISP1", "V_OLD", "V_TWIN", "V_PASS2", "V_P1", "BUSY", "V_BUILD"):
        lst.append("  %08X  %s" % (SYM[k], k))
    lst.append("SAVE DATA BYTES used: %08X (twin HP), %08X (twin MP + 1)" % (SYM["SAVE_HP"], SYM["SAVE_MP"]))
    if any(n == "commands" for n, _, _ in sections):
        lst.append("RESERVED DATA: %08X-%08X = second control object S2 (built by the game's own constructor on first use)" % (
            COMMANDS_S2, COMMANDS_S2 + 0xAFF))
    (out / "listing.txt").write_text("\n".join(lst) + "\n")
    print("%d code words, %d hook words -> %s" % (len(code), len(hook_words), out / "SLPM-66675_F266B00B.pnach"))
    for name, title, rows in sections:
        print("   %-9s 0x%08X-0x%08X  %s" % (name, rows[0][0], rows[-1][0] + 3, title))

    if check:
        def lane_words(path):
            d = {}
            for line in pathlib.Path(path).read_text().splitlines():
                if line.startswith("patch=1,EE,"):
                    p = line.split(",")
                    d[int(p[2], 16)] = int(p[4], 16)
            return d
        e = lane_words(ROOT / "patches" / "lane-e-x2" / "SLPM-66675_F266B00B.pnach")
        d = lane_words(ROOT / "patches" / "lane-d-ownhp-v2" / "SLPM-66675_F266B00B.pnach")
        allw = dict(code)
        allw.update(hook_words)
        diff_e = sorted(a for a in e if allw.get(a) != e[a])
        diff_d = sorted(a for a in d if allw.get(a) != d[a])
        print("check against lane E (patches/lane-e-x2): %d of %d words equal; different: %s" % (
            len(e) - len(diff_e), len(e), ", ".join("%08X" % a for a in diff_e) or "none"))
        print("check against lane D (patches/lane-d-ownhp-v2): %d of %d words equal; different: %s" % (
            len(d) - len(diff_d), len(d), ", ".join("%08X" % a for a in diff_d) or "none"))
        if v2:
            g = lane_words(ROOT / "patches" / "lane-g-cmd-v3-no-pad-rule" / "SLPM-66675_F266B00B.pnach")
            diff_g = sorted(a for a in g if allw.get(a) != g[a])
            print("check against lane G (patches/lane-g-cmd-v3-no-pad-rule): %d of %d words equal; different: %s" % (
                len(g) - len(diff_g), len(g), ", ".join("%08X" % a for a in diff_g) or "none"))


if __name__ == "__main__":
    main()
