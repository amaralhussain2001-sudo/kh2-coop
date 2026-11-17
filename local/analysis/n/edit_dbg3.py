import pathlib
p = pathlib.Path("C:/Users/PC FORCE/Desktop/New folder (3)/tools/lane-n/make_down.py")
s = p.read_text(encoding="utf-8")
NL = chr(10)
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60])
    s = s.replace(old, new)
rep('''"    lui t3,%hi(N_CUR)", "    lw t3,%lo(N_CUR)(t3)", "    sw t3,28(t7)", ""])''',
    '''"    lui t3,%hi(N_CUR)", "    lw t3,%lo(N_CUR)(t3)", "    sw t3,28(t7)",
                             "    sw ra,32(t7)", "    lw t3,4(a0)", "    sw t3,36(t7)", "    lw t3,0(t3)", "    sw t3,40(t7)", ""])
        # every call of the party-member script command: counter, index asked, caller, whose update was running
        dbg3 = chr(10).join(["    lui t7,%hi(N_RING)", "    addiu t7,t7,%lo(N_RING)", "    lw t3,44(t7)", "    addiu t3,t3,1",
                             "    sw t3,44(t7)", "    lw t3,0(a0)", "    sw t3,48(t7)", "    sw ra,52(t7)",
                             "    lui t3,%hi(N_CUR)", "    lw t3,%lo(N_CUR)(t3)", "    sw t3,56(t7)", ""])''')
rep('    dbg2 = ""' + NL, '    dbg2 = ""' + NL + '    dbg3 = ""' + NL)
rep('''.replace("@DEBUG2@" + chr(10), dbg2)''', '''.replace("@DEBUG2@" + chr(10), dbg2).replace("@DEBUG3@" + chr(10), dbg3)''')
rep('''n_party:                          # script command "party member number N" (0 = the player, 1 and 2 = the friends)
''', '''n_party:                          # script command "party member number N" (0 = the player, 1 and 2 = the friends)
@DEBUG3@
''')
p.write_text(s, encoding="utf-8")
print("ok")
