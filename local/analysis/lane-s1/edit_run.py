import pathlib
f = pathlib.Path(r"C:/Users/PC FORCE/Desktop/New folder (3)/tools/lane-s1/run_s1.py")
s = f.read_text()
old = "    hlog.close()\n"
new = ("    hlog.close()\n"
       "    # keep the emulator logs of this run (the next run overwrites them): crashes are only visible there\n"
       "    import shutil\n"
       "    for n in ('p1', 'p2'):\n"
       "        src = ROOT / 'local' / a.run_dir / n / 'logs' / 'emulog.txt'\n"
       "        if src.exists():\n"
       "            shutil.copyfile(src, out / ('emulog_%s.txt' % n))\n")
assert s.count(old) == 1 and "emulog_%s" not in s
f.write_text(s.replace(old, new))
print("ok")
