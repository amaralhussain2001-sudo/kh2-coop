import pathlib
f = pathlib.Path(r"C:/Users/PC FORCE/Desktop/New folder (3)/tools/lane-s1/run_s1.py")
s = f.read_text()
a1 = '    ap.add_argument("--run-dir", default="run-s1")\n'
b1 = a1 + ('    ap.add_argument("--rc", default="", help="START:END frames for the dense Reaction Command timeline (s1rc.py)")\n'
           '    ap.add_argument("--rc-redirect", action="store_true", help="ONE-copy tests only: s1rc.py --redirect")\n')
a2 = "    h.wait()\n"
b2 = ("    rc = None\n"
      "    if a.rc:\n"
      "        r0, r1 = a.rc.split(':')\n"
      "        rcmd = [py, '-I', str(ROOT / 'tools' / 'lane-s1' / 's1rc.py'), str(out), a.pine, r0, r1, '--timeout', a.timeout]\n"
      "        if a.rc_redirect:\n"
      "            assert a.players == '1', 'the redirect write is for one-copy tests only'\n"
      "            rcmd.append('--redirect')\n"
      "        rlog = open(ROOT / 'local' / 'analysis' / 'lane-s1' / (a.test + '-rc-console.txt'), 'w')\n"
      "        rc = subprocess.Popen(rcmd, stdout=rlog, stderr=subprocess.STDOUT)\n"
      "    h.wait()\n"
      "    if rc is not None:\n"
      "        try:\n"
      "            rc.wait(timeout=20)\n"
      "        except subprocess.TimeoutExpired:\n"
      "            rc.kill()\n")
assert s.count(a1) == 1 and s.count(a2) == 1 and "--rc-redirect" not in s
f.write_text(s.replace(a1, b1).replace(a2, b2))
print("ok")
