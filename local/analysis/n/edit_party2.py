import pathlib
p = pathlib.Path("C:/Users/PC FORCE/Desktop/New folder (3)/tools/lane-n/make_down.py")
s = p.read_text(encoding="utf-8")
NL = chr(10)
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60])
    s = s.replace(old, new)
rep("""n_tk_orig:
    addiu sp,sp,-16
    sd ra,0(sp)
    lui t7,%hi(N_CUR)
    jal PLAYER_UPDATE             # the game's own update; while it runs N_CUR = this player object
    sw a0,%lo(N_CUR)(t7)
    lui t7,%hi(N_CUR)
    sw zero,%lo(N_CUR)(t7)
    ld ra,0(sp)
    jr ra
    addiu sp,sp,16
""", """n_tk_orig:
    j PLAYER_UPDATE
    nop
""")
i = s.index("    lw t0,0(a0)" + NL + "    bne t0,zero,n_pa_orig")
j = s.index("n_pa_orig:")
s = s[:i] + """    lw t0,0(a0)
    bne t0,zero,n_pa_orig         # the friends: unchanged
    lui t7,%hi(V_TWIN)
    lw t5,%lo(V_TWIN)(t7)
    beq t5,zero,n_pa_orig         # one hero only: unchanged
    lui t7,%hi(SCRIPT_THREAD)
    lw t6,%lo(SCRIPT_THREAD)(t7)  # the script thread that is running now
    beq t6,zero,n_pa_orig
    nop
    lw t6,0x38(t6)                # the object that script belongs to (a Cure's: its caster)
    bne t6,t5,n_pa_orig           # not the twin's script: the engine's player as before
    nop
    jr ra                         # the twin's own script (its Cure): "the player" is the twin
    sw t5,0(a0)
""" + s[j:]
rep('''    "N_CUR": 0x000F2FF0,          # the player object whose update is running (0 outside)''',
    '''    "SCRIPT_THREAD": 0x0034D8A4,  # the script thread being run (set by 0x0016CD48); +0x38 = the object it belongs to''')
p.write_text(s, encoding="utf-8")
print("ok")
