"""One-off: tools/own/make_own.py, the option --cannon2view (ninth round, job 5), second form.
Seen in run cnA (v103 + --cannon2view): each player's picture looks along HIS cannon, but player 2's camera sat
much closer to his cannon than player 1's. The two camera offsets (object + 0xB70 / + 0xB80) are set by the
cannon's own script (call (1,330)); the second cannon, made at run time, still had the builder's start values.
Now cn_cam copies player 1's cannon's two offsets (8 words) to the twin's cannon each time camera 2 is worked
out, so both pictures have the same framing. cn_cam moves into a block of its own (0x000F5E90 .. 0x000F5EFF,
behind step 8's variable 0x000F5E80), because step 8's block is full.
Without the option the builder writes what it wrote before, bit for bit.
The record of the edit; run once:
  python -I tools/own/edit_make_own_cannon3.py"""
import pathlib

NL = chr(10)
p = pathlib.Path(__file__).resolve().parent / "make_own.py"
s = p.read_text(encoding="utf-8")
if "CN_AT = " in s:
    raise SystemExit("already there")

# (1) cn_cam leaves step 8's source
a = s.index('b2_k9:' + NL + '""") + """' + NL + 'cn_cam:')
b = s.index('    j 0x001589D0' + NL + '    nop' + NL + '"""' + NL, a)
b += len('    j 0x001589D0' + NL + '    nop' + NL + '"""' + NL)
s = s[:a] + 'b2_k9:' + NL + '""")' + NL + s[b:]

# (2) the hook: cn_cam's own block
old = '''        result[a] = (3 << 26) | ((_labels["cn_cam"] >> 2) & 0x3FFFFFF)
'''
new = '''        cn_code, cn_labels = assemble(CN_AT, CN_SRC, {})
        cn_code = [w if isinstance(w, int) else w[1] for w in cn_code]
        assert CN_AT + 4 * len(cn_code) <= CN_END, "the toy cannon's camera: too long (%d words)" % len(cn_code)
        for i, w in enumerate(cn_code):
            assert CN_AT + 4 * i not in result, "the toy cannon's camera: address already used %08X" % (CN_AT + 4 * i)
            result[CN_AT + 4 * i] = w
            origin[CN_AT + 4 * i] = "own screens step 8 (the toy cannon's camera for each player)"
        result[a] = (3 << 26) | ((cn_labels["cn_cam"] >> 2) & 0x3FFFFFF)
'''
assert s.count(old) == 1, s.count(old)
s = s.replace(old, new)

# (3) the new block's place and source
old = "BOSSV_END = 0x000F5E80" + NL
assert s.count(old) == 1
new = old + '''CN_AT = 0x000F5E90                # (--cannon2view) the toy cannon's camera for each player: 0x000F5E90-0x000F5EFF
CN_END = 0x000F5F00
CN_SRC = """
cn_cam:                           # the call at 0x00140C9C (camera kind 10 = the toy cannon's): a0 = the camera
    lui t7,0x000F
    lw t0,0x6F0C(t7)              # not 0: player 2's camera is in the game's camera memory
    lui t1,0x0035
    lw t9,-5816(t1)               # the engine's player (player 1's cannon)
    beq t0,zero,cc_have
    lw t8,0x05CC(t7)              # the twin
    beq t8,zero,cc_have
    nop
    beq t9,zero,cc_tw
    addiu t2,zero,8               # the two camera offsets (object + 0xB70 .. + 0xB8F): the twin's cannon gets player 1's
    addiu t3,t9,0x0B70
    addiu t4,t8,0x0B70
cc_cp:
    lw t5,0(t3)
    addiu t3,t3,4
    sw t5,0(t4)
    addiu t2,t2,-1
    bne t2,zero,cc_cp
    addiu t4,t4,4
cc_tw:
    move t9,t8
cc_have:
    beq t9,zero,cc_go
    lui t1,0x004F
    sw t9,0x35A0(t1)              # 0x004F35A0: the cannon this camera looks along
cc_go:
    j 0x001589D0
    nop
"""
'''
s = s.replace(old, new)
with open(p, "w", encoding="utf-8", newline=chr(13) + chr(10)) as f:      # the file has CRLF line ends
    f.write(s)
print("ok")
