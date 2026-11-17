// Lane F: "twin everywhere". Adds a second PLAYER placeholder (object 0x0236) beside every PLAYER placeholder in
// the room spawn data, so the game itself builds a second player character of whatever form is current.
// Works on copies only; the result is deterministic (same input files -> same output bytes).
//
//   stats    <ardDir>                                             facts about the placements (facing convention)
//   twin-all <baseArdDir> <overlayDirs|-> <mapDir|-> <outDir> <report.csv> [after|before] [onlyRoom,..|-] [alsoObjHex,..]
//            alsoObjHex: real player objects placed directly by room data that also get a twin (e.g. 54 = Sora).
//            overlayDirs: ';'-separated folders whose *.ard files replace the base ones (test "jump" recipes).
//            mapDir: folder with <room>.map files, used to check that the twin's spot has ground and no wall.
//            after|before: the twin's record goes right after (default) or right before the player's record.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Numerics;
using System.Runtime.CompilerServices;
using System.Runtime.Loader;
using System.Text;

static class Program
{
    static int Main(string[] args)
    {
        var apps = Environment.GetEnvironmentVariable("OPENKH_APPS") ?? @"C:\Users\PC FORCE\Desktop\openkh\Apps";
        AssemblyLoadContext.Default.Resolving += (ctx, name) =>
        {
            var p = Path.Combine(apps, name.Name + ".dll");
            return File.Exists(p) ? ctx.LoadFromAssemblyPath(p) : null;
        };
        try
        {
            if (args.Length >= 2 && args[0] == "stats") return Work.Stats(args[1]);
            if (args.Contains("ignore-switched")) { Work.IgnoreSwitched = true; args = args.Where(a => a != "ignore-switched").ToArray(); }
            if (args.Length >= 5 && args[0] == "study") return Work.Study(args[1], args[2], args[3], args[4]);
            if (args.Length >= 3 && args[0] == "rawspawn") return Work.RawSpawn(args[1], args[2]);
            if (args.Length >= 3 && args[0] == "meshgroups") return Work.MeshGroups(args[1], args[2]);
            if (args.Length >= 8 && args[0] == "spotmask") return Work.SpotMask(args[1], args[2], args[3], int.Parse(args[4]), byte.Parse(args[5]), byte.Parse(args[6]), args[7]);
            if (args.Length >= 7 && args[0] == "why") return Work.Why(args[1], args[2], args[3], int.Parse(args[4]), byte.Parse(args[5]), byte.Parse(args[6]));
            if (args.Length >= 6 && args[0] == "twin-all")
                return Work.TwinAll(args[1], args[2], args[3], args[4], args[5],
                    args.Length > 6 ? args[6] : "after", args.Length > 7 ? args[7] : "", args.Length > 8 ? args[8] : "",
                    args.Length > 9 ? args[9] : "-");
            Console.Error.WriteLine("usage: stats <ardDir> | twin-all <baseArdDir> <overlayDirs|-> <mapDir|-> <outDir> <report.csv> [after|before] [rooms]");
            return 2;
        }
        catch (Exception e)
        {
            Console.Error.WriteLine(e);
            return 1;
        }
    }
}

class Ent
{
    public int Off, Obj;
    public Vector3 Pos;
    public float RotY;
    public byte Type, Arg;
    public short Serial;
}

class Zone
{
    public int Shape;
    public Vector3 Pos, Scale;
    // conservative test in the ground plane: a circle that contains the whole trigger shape
    public bool Contains(Vector3 q, float margin)
    {
        float r = Shape == 0 ? (float)Math.Sqrt(Scale.X * Scale.X + Scale.Z * Scale.Z) : Math.Max(Scale.X, Scale.Z);
        float dx = q.X - Pos.X, dz = q.Z - Pos.Z;
        return dx * dx + dz * dz <= (r + margin) * (r + margin);
    }
}

class Sp
{
    public int HdrOff, EntStart;
    public List<Ent> Ents = new List<Ent>();
    public List<Zone> Zones = new List<Zone>();
}

struct Tri
{
    public Vector3 A, B, C;
    public float MinX, MaxX, MinZ, MaxZ;
    public byte Vis, Grp;   // the collision mesh's switch bytes (0, 0 = always there)
    public int Flags;       // the triangle's attribute flags
}

class Geo
{
    public List<Tri> Floors = new List<Tri>();
    public List<Tri> Walls = new List<Tri>();
    public int Skipped;
}

static class Work
{
    const int Player = 0x236, Friend1 = 0x237, Friend2 = 0x238;
    const int EntSize = 0x40, HdrSize = 0x2C;
    static readonly CultureInfo Inv = CultureInfo.InvariantCulture;

    // Walk the raw bytes of one spawn entry. Returns null when the bytes do not follow the known layout.
    public static List<Sp> Walk(byte[] b)
    {
        var res = new List<Sp>();
        if (b.Length == 0) return res;
        if (b.Length < 8 || BitConverter.ToInt32(b, 0) != 2) return null;
        int count = BitConverter.ToInt32(b, 4);
        if (count < 0 || count > 4096) return null;
        int pos = 8;
        for (int i = 0; i < count; i++)
        {
            if (pos + HdrSize > b.Length) return null;
            int e = BitConverter.ToInt16(b, pos + 4), a = BitConverter.ToInt16(b, pos + 6), w = BitConverter.ToInt16(b, pos + 8),
                r = BitConverter.ToInt16(b, pos + 10), s = BitConverter.ToInt16(b, pos + 12);
            if (e < 0 || a < 0 || w < 0 || r < 0 || s < 0) return null;
            var sp = new Sp { HdrOff = pos, EntStart = pos + HdrSize };
            int p = sp.EntStart;
            if (p + (long)e * EntSize > b.Length) return null;
            for (int k = 0; k < e; k++, p += EntSize)
                sp.Ents.Add(new Ent
                {
                    Off = p, Obj = BitConverter.ToInt32(b, p),
                    Pos = new Vector3(BitConverter.ToSingle(b, p + 4), BitConverter.ToSingle(b, p + 8), BitConverter.ToSingle(b, p + 12)),
                    RotY = BitConverter.ToSingle(b, p + 0x14), Type = b[p + 0x1C], Arg = b[p + 0x1D], Serial = BitConverter.ToInt16(b, p + 0x1E),
                });
            if (p + (long)a * 0x40 > b.Length) return null;
            for (int k = 0; k < a; k++, p += 0x40)
                sp.Zones.Add(new Zone
                {
                    Shape = BitConverter.ToInt16(b, p),
                    Pos = new Vector3(BitConverter.ToSingle(b, p + 4), BitConverter.ToSingle(b, p + 8), BitConverter.ToSingle(b, p + 12)),
                    Scale = new Vector3(Math.Abs(BitConverter.ToSingle(b, p + 16)), Math.Abs(BitConverter.ToSingle(b, p + 20)), Math.Abs(BitConverter.ToSingle(b, p + 24))),
                });
            for (int k = 0; k < w; k++)
            {
                if (p + 8 > b.Length) return null;
                int cnt = BitConverter.ToInt16(b, p + 2);
                if (cnt < 0) return null;
                p += 8 + cnt * 12;
            }
            p += r * 0x10 + s * 8;
            if (p > b.Length) return null;
            res.Add(sp);
            pos = p;
        }
        for (int i = pos; i < b.Length; i++) if (b[i] != 0) return null;
        return res;
    }

    static IEnumerable<(string Room, OpenKh.Kh2.Bar Bar)> Rooms(string dir)
    {
        foreach (var f in Directory.GetFiles(dir, "*.ard").OrderBy(x => Path.GetFileName(x), StringComparer.Ordinal))
        {
            OpenKh.Kh2.Bar bar;
            using (var s = File.OpenRead(f)) bar = OpenKh.Kh2.Bar.Read(s);
            yield return (Path.GetFileNameWithoutExtension(f), bar);
        }
    }

    static byte[] Bytes(Stream s)
    {
        var ms = new MemoryStream();
        s.Position = 0; s.CopyTo(ms); s.Position = 0;
        return ms.ToArray();
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int Stats(string ardDir)
    {
        // Which way does RotY point? Compare the direction to the friends' centre with the four possible conventions.
        var names = new[] { "(sin, cos)", "(-sin, -cos)", "(cos, -sin)", "(-cos, sin)", "(sin, -cos)", "(-sin, cos)", "(cos, sin)", "(-cos, -sin)" };
        var sum = new double[8]; int n = 0; int behind = 0;
        var dists = new List<float>();
        foreach (var (room, bar) in Rooms(ardDir))
            foreach (var e in bar.Where(x => x.Type == OpenKh.Kh2.Bar.EntryType.AreaDataSpawn))
            {
                var sps = Walk(Bytes(e.Stream));
                if (sps == null) continue;
                foreach (var sp in sps)
                    foreach (var p in sp.Ents.Where(x => x.Obj == Player))
                    {
                        var fr = sp.Ents.Where(x => (x.Obj == Friend1 || x.Obj == Friend2) && x.Type == p.Type && x.Arg == p.Arg).ToList();
                        if (fr.Count != 2) continue;
                        var c = (fr[0].Pos + fr[1].Pos) / 2 - p.Pos; c.Y = 0;
                        if (c.Length() < 1) continue;
                        dists.Add(c.Length());
                        c = Vector3.Normalize(c);
                        double sn = Math.Sin(p.RotY), cs = Math.Cos(p.RotY);
                        var dirs = new[] { new Vector3((float)sn, 0, (float)cs), new Vector3((float)-sn, 0, (float)-cs), new Vector3((float)cs, 0, (float)-sn), new Vector3((float)-cs, 0, (float)sn),
                            new Vector3((float)sn, 0, (float)-cs), new Vector3((float)-sn, 0, (float)cs), new Vector3((float)cs, 0, (float)sn), new Vector3((float)-cs, 0, (float)-sn) };
                        for (int i = 0; i < 8; i++) sum[i] += Vector3.Dot(dirs[i], c);
                        if (Vector3.Dot(dirs[5], c) > 0.5f) behind++;
                        n++;
                    }
            }
        Console.WriteLine("placements with two friends: " + n);
        Console.WriteLine("  friends' centre lies on the (-sin, cos) side (within 60 degrees) in " + behind + " of " + n + " placements");
        for (int i = 0; i < 8; i++) Console.WriteLine("  mean dot of friends' centre with " + names[i] + ": " + (sum[i] / Math.Max(1, n)).ToString("F3", Inv));
        dists.Sort();
        if (dists.Count > 0) Console.WriteLine("  distance player -> friends' centre: median " + dists[dists.Count / 2].ToString("F0", Inv) + ", min " + dists[0].ToString("F0", Inv) + ", max " + dists[dists.Count - 1].ToString("F0", Inv));
        return 0;
    }

    // ---------- room geometry (collision) ----------

    static Geo LoadGeo(string mapFile)
    {
        if (mapFile == null || !File.Exists(mapFile)) return null;
        try
        {
            OpenKh.Kh2.Bar bar;
            using (var s = File.OpenRead(mapFile)) bar = OpenKh.Kh2.Bar.Read(s);
            var e = bar.FirstOrDefault(x => x.Type == OpenKh.Kh2.Bar.EntryType.CollisionOctalTree);
            if (e == null) return null;
            e.Stream.Position = 0;
            var coct = OpenKh.Kh2.Coct.Read(e.Stream);
            var g = new Geo();
            var seen = new HashSet<object>();
            foreach (var node in coct.Nodes)
                foreach (var mesh in node.Meshes)
                {
                    if (!seen.Add(mesh)) continue;
                    foreach (var c in mesh.Collisions)
                    {
                        var idx = new[] { c.Vertex1, c.Vertex2, c.Vertex3, c.Vertex4 }.Where(i => i >= 0 && i < coct.VertexList.Count).ToArray();
                        if (idx.Length < 3) continue;
                        var v = idx.Select(i => new Vector3(coct.VertexList[i].X, coct.VertexList[i].Y, coct.VertexList[i].Z)).ToArray();
                        int fl = c.Attributes == null ? 0 : c.Attributes.Flags;
                        if (IgnoreSwitched && (mesh.Group != 0)) { g.Skipped++; continue; }
                        // HYPOTHESIS used by "spotmask": collision group g (1..63) is switched on by bit g of the map
                        // program's MapVisibility value; group 0 is always there
                        if (UseMask && mesh.Group != 0 && (mesh.Group > 63 || ((Mask >> mesh.Group) & 1) == 0)) { g.Skipped++; continue; }
                        AddTri(g, v[0], v[1], v[2], mesh.Visibility, mesh.Group, fl);
                        if (v.Length == 4) AddTri(g, v[0], v[2], v[3], mesh.Visibility, mesh.Group, fl);
                    }
                }
            return g;
        }
        catch (Exception)
        {
            return null;
        }
    }

    // lane J: when true, collision meshes with a non-zero group byte (walls the game switches on and off per story
    // state, "barriers") are left out
    public static bool IgnoreSwitched = false;
    public static bool UseMask = false;
    public static ulong Mask = 0;

    static void AddTri(Geo g, Vector3 a, Vector3 b, Vector3 c, byte vis = 0, byte grp = 0, int flags = 0)
    {
        var n = Vector3.Cross(b - a, c - a);
        if (n.Length() < 1e-3f) return;
        n = Vector3.Normalize(n);
        var t = new Tri
        {
            A = a, B = b, C = c,
            MinX = Math.Min(a.X, Math.Min(b.X, c.X)), MaxX = Math.Max(a.X, Math.Max(b.X, c.X)),
            MinZ = Math.Min(a.Z, Math.Min(b.Z, c.Z)), MaxZ = Math.Max(a.Z, Math.Max(b.Z, c.Z)),
            Vis = vis, Grp = grp, Flags = flags,
        };
        if (Math.Abs(n.Y) >= 0.5f) g.Floors.Add(t); else g.Walls.Add(t);
    }

    // Height (Y) of the floor under (x, z) that is nearest to refY; NaN when none within maxDiff.
    static float FloorAt(Geo g, float x, float z, float refY, float maxDiff)
    {
        float best = float.NaN, bestD = maxDiff;
        foreach (var t in g.Floors)
        {
            if (x < t.MinX || x > t.MaxX || z < t.MinZ || z > t.MaxZ) continue;
            float d = (t.B.Z - t.C.Z) * (t.A.X - t.C.X) + (t.C.X - t.B.X) * (t.A.Z - t.C.Z);
            if (Math.Abs(d) < 1e-6f) continue;
            float u = ((t.B.Z - t.C.Z) * (x - t.C.X) + (t.C.X - t.B.X) * (z - t.C.Z)) / d;
            float v = ((t.C.Z - t.A.Z) * (x - t.C.X) + (t.A.X - t.C.X) * (z - t.C.Z)) / d;
            float w = 1 - u - v;
            if (u < -0.001f || v < -0.001f || w < -0.001f) continue;
            float y = u * t.A.Y + v * t.B.Y + w * t.C.Y;
            float diff = Math.Abs(y - refY);
            if (diff <= bestD) { bestD = diff; best = y; }
        }
        return best;
    }

    static bool SegHitsTri(Vector3 p, Vector3 q, Tri t)
    {
        var dir = q - p;
        var e1 = t.B - t.A; var e2 = t.C - t.A;
        var h = Vector3.Cross(dir, e2);
        float a = Vector3.Dot(e1, h);
        if (Math.Abs(a) < 1e-6f) return false;
        float f = 1 / a;
        var s = p - t.A;
        float u = f * Vector3.Dot(s, h);
        if (u < 0 || u > 1) return false;
        var qv = Vector3.Cross(s, e1);
        float v = f * Vector3.Dot(dir, qv);
        if (v < 0 || u + v > 1) return false;
        float tt = f * Vector3.Dot(e2, qv);
        return tt >= 0 && tt <= 1;
    }

    static bool Blocked(Geo g, Vector3 p, Vector3 q)
    {
        float minX = Math.Min(p.X, q.X), maxX = Math.Max(p.X, q.X), minZ = Math.Min(p.Z, q.Z), maxZ = Math.Max(p.Z, q.Z);
        foreach (var t in g.Walls)
        {
            if (t.MaxX < minX || t.MinX > maxX || t.MaxZ < minZ || t.MinZ > maxZ) continue;
            if (SegHitsTri(p, q, t)) return true;
        }
        return false;
    }

    // Is "c" a place where a character can stand, reachable on foot from the player's spot "p"? (Y: up is negative.)
    static bool SpotOk(Geo g, Vector3 p, float floorP, Vector3 c, out float floorC)
    {
        floorC = float.NaN;
        float prev = floorP;
        const int steps = 6;
        for (int i = 1; i <= steps; i++)
        {
            float t = i / (float)steps;
            float f = FloorAt(g, p.X + (c.X - p.X) * t, p.Z + (c.Z - p.Z) * t, prev, 45);
            if (float.IsNaN(f)) return false;
            prev = f;
        }
        floorC = prev;
        if (Math.Abs(floorC - floorP) > 120) return false;
        foreach (var h in new[] { 30f, 80f })
            if (Blocked(g, new Vector3(p.X, floorP - h, p.Z), new Vector3(c.X, floorC - h, c.Z))) return false;
        for (int k = 0; k < 8; k++)
        {
            double ang = k * Math.PI / 4;
            var q = new Vector3(c.X + 40 * (float)Math.Sin(ang), floorC - 45, c.Z + 40 * (float)Math.Cos(ang));
            if (Blocked(g, new Vector3(c.X, floorC - 45, c.Z), q)) return false;
            if (float.IsNaN(FloorAt(g, q.X, q.Z, floorC, 60))) return false;
        }
        return true;
    }

    static float Dist2D(Vector3 a, Vector3 b) => (float)Math.Sqrt((a.X - b.X) * (a.X - b.X) + (a.Z - b.Z) * (a.Z - b.Z));

    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int TwinAll(string baseDir, string overlays, string mapDir, string outDir, string reportCsv, string order, string only, string also, string overrideFile = "-")
    {
        bool before = order == "before";
        // lane J: placement overrides. One line per placement, same key columns as the report:
        // room,group,spawnpoint,spawn_type,spawn_arg,player_x,player_y,player_z,twin_x,twin_y,twin_z,status,note
        var overrides = new Dictionary<string, (Vector3 Pos, string Status, string Note)>(StringComparer.Ordinal);
        int overridesUsed = 0;
        if (overrideFile != "-" && overrideFile.Length > 0)
            foreach (var line in File.ReadAllLines(overrideFile).Skip(1))
            {
                var c = line.Split(',');
                if (c.Length < 12 || c[0].StartsWith("#")) continue;
                string key = string.Join("|", c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7]);
                overrides[key] = (new Vector3(float.Parse(c[8], Inv), float.Parse(c[9], Inv), float.Parse(c[10], Inv)), c[11], c.Length > 12 ? string.Join(" ", c.Skip(12)).Trim('"') : "");
            }
        // objects that get a twin: the PLAYER placeholder, plus real character objects the data places directly
        var twinObjs = new HashSet<int> { Player };
        foreach (var h in also.Split(',').Where(x => x.Length > 0 && x != "-")) twinObjs.Add(Convert.ToInt32(h, 16));
        var onlyRooms = new HashSet<string>(only.Split(',').Where(x => x.Length > 0 && x != "-"), StringComparer.OrdinalIgnoreCase);
        var src = new SortedDictionary<string, string>(StringComparer.Ordinal);
        var fromOverlay = new HashSet<string>();
        foreach (var f in Directory.GetFiles(baseDir, "*.ard")) src[Path.GetFileName(f)] = f;
        if (overlays != "-")
            foreach (var d in overlays.Split(';').Where(x => x.Length > 0))
                foreach (var f in Directory.GetFiles(d, "*.ard")) { src[Path.GetFileName(f)] = f; fromOverlay.Add(Path.GetFileName(f)); }

        var rep = new StringBuilder();
        rep.AppendLine("room,group,spawnpoint,spawn_type,spawn_arg,player_x,player_y,player_z,friends,method,checked,twin_x,twin_y,twin_z,distance,new_serial");
        int placements = 0, written = 0, undecodable = 0, noMap = 0;
        var methodCount = new SortedDictionary<string, int>(StringComparer.Ordinal);
        var skipped = new List<string>();
        Directory.CreateDirectory(Path.Combine(outDir, "ard"));

        foreach (var kv in src)
        {
            string room = Path.GetFileNameWithoutExtension(kv.Key);
            OpenKh.Kh2.Bar bar;
            using (var s = File.OpenRead(kv.Value)) bar = OpenKh.Kh2.Bar.Read(s);
            bool doTwin = onlyRooms.Count == 0 || onlyRooms.Contains(room);
            Geo geo = null; bool geoLoaded = false;
            bool changed = false;

            // serial numbers already used anywhere in this room file
            int maxSerial = 0;
            var zones = new List<Zone>();
            var others = new List<Vector3>();   // every other placed thing in this room file (people, chests, enemies, props)
            var raws = new Dictionary<OpenKh.Kh2.Bar.Entry, byte[]>();
            var walks = new Dictionary<OpenKh.Kh2.Bar.Entry, List<Sp>>();
            foreach (var e in bar.Where(x => x.Type == OpenKh.Kh2.Bar.EntryType.AreaDataSpawn))
            {
                var b = Bytes(e.Stream);
                var w = Walk(b);
                raws[e] = b; walks[e] = w;
                if (w == null) { undecodable++; skipped.Add(room + " " + e.Name + ": spawn data not in the known layout (left untouched)"); continue; }
                foreach (var sp in w) foreach (var en in sp.Ents) maxSerial = Math.Max(maxSerial, en.Serial);
                foreach (var sp in w) zones.AddRange(sp.Zones);
                foreach (var sp in w) others.AddRange(sp.Ents.Where(x => x.Obj != Player && x.Obj != Friend1 && x.Obj != Friend2).Select(x => x.Pos));
            }

            if (doTwin)
                foreach (var e in bar.Where(x => x.Type == OpenKh.Kh2.Bar.EntryType.AreaDataSpawn))
                {
                    var sps = walks[e];
                    if (sps == null) continue;
                    var b = raws[e];
                    var inserts = new List<(int At, byte[] Rec, int Hdr)>();
                    for (int si = 0; si < sps.Count; si++)
                    {
                        var sp = sps[si];
                        foreach (var p in sp.Ents.Where(x => twinObjs.Contains(x.Obj)))
                        {
                            if (!geoLoaded)
                            {
                                geoLoaded = true;
                                geo = mapDir == "-" ? null : LoadGeo(Path.Combine(mapDir, room + ".map"));
                                if (geo == null) noMap++;
                            }
                            var fr = sp.Ents.Where(x => (x.Obj == Friend1 || x.Obj == Friend2) && x.Type == p.Type && x.Arg == p.Arg).ToList();
                            // forward and right of the player. Facing = (sin RotY, 0, -cos RotY): measured by "stats" (the friends'
                            // centre lies on the opposite side) and seen in tests f-all-tt07 / f-final-start (a twin placed on the
                            // "behind" side hides the player from the camera; one placed "right" stands beside him).
                            var fwd = new Vector3((float)Math.Sin(p.RotY), 0, (float)-Math.Cos(p.RotY));
                            var right = new Vector3(fwd.Z, 0, -fwd.X);
                            var cands = new List<(string Name, Vector3 Pos)>();
                            // side by side first (so neither hero hides the other from a camera behind them), then the
                            // designer-made ground between the friends, then ahead, and behind (toward the door) last
                            cands.Add(("right 110", p.Pos + right * 110));
                            cands.Add(("left 110", p.Pos - right * 110));
                            cands.Add(("ahead right 110", p.Pos + (fwd + right) * (110 * 0.7071f)));
                            cands.Add(("ahead left 110", p.Pos + (fwd - right) * (110 * 0.7071f)));
                            if (fr.Count == 2) cands.Add(("between the two friends", (fr[0].Pos + fr[1].Pos) / 2));
                            foreach (var f in fr) cands.Add(("between player and a friend", (p.Pos + f.Pos) / 2));
                            foreach (var r in new[] { 110f, 80f })
                            {
                                cands.Add(("right " + r, p.Pos + right * r));
                                cands.Add(("left " + r, p.Pos - right * r));
                                cands.Add(("ahead right " + r, p.Pos + (fwd + right) * (r * 0.7071f)));
                                cands.Add(("ahead left " + r, p.Pos + (fwd - right) * (r * 0.7071f)));
                                cands.Add(("ahead " + r, p.Pos + fwd * r));
                                cands.Add(("behind right " + r, p.Pos + (right - fwd) * (r * 0.7071f)));
                                cands.Add(("behind left " + r, p.Pos - (right + fwd) * (r * 0.7071f)));
                                cands.Add(("behind " + r, p.Pos - fwd * r));
                            }
                            // keep a body's width from the player and from the friends' spots
                            cands = cands.Where(c => Dist2D(c.Pos, p.Pos) >= 60 && fr.All(f => Dist2D(c.Pos, f.Pos) >= 60)).ToList();
                            // and never inside a trigger zone (exit, event) that the player's own spot is outside of
                            var open = zones.Where(z => !z.Contains(p.Pos, 0)).ToList();
                            var clear = cands.Where(c => !open.Any(z => z.Contains(c.Pos, 30))
                                && !others.Any(o => Dist2D(o, c.Pos) < 50 && Math.Abs(o.Y - p.Pos.Y) < 200)).ToList();
                            bool zoneForced = clear.Count == 0 && cands.Count > 0;
                            if (clear.Count > 0) cands = clear;

                            string method = null; bool chk = false; Vector3 twin = default;
                            float floorP = geo == null ? float.NaN : FloorAt(geo, p.Pos.X, p.Pos.Z, p.Pos.Y, 150);
                            if (geo != null && !float.IsNaN(floorP))
                                foreach (var c in cands)
                                    if (SpotOk(geo, p.Pos, floorP, c.Pos, out float floorC))
                                    {
                                        method = c.Name; chk = true;
                                        twin = new Vector3(c.Pos.X, floorC + (p.Pos.Y - floorP), c.Pos.Z);
                                        break;
                                    }
                            if (method == null)
                            {
                                // no ground information (or nothing passed): designer-made spot between the friends if there is one,
                                // otherwise a step ahead of the player; a little higher so the character settles onto the ground
                                var pref = cands.Where(x => x.Name.StartsWith("between the two")).Concat(cands.Where(x => x.Name.StartsWith("between player"))).Concat(cands).ToList();
                                var c = pref.Count > 0 ? pref[0] : ("ahead 80 (too close to others)", p.Pos + fwd * 80);
                                if (zoneForced) method = null;
                                method = c.Item1 + (zoneForced ? " [every spot is in a trigger zone or on another object]" : "") + (geo == null ? " [no map data]" : float.IsNaN(floorP) ? " [no ground found under the player]" : " [no spot passed the ground check]");
                                twin = new Vector3(c.Item2.X, Math.Min(p.Pos.Y, c.Item2.Y) - 10, c.Item2.Z);
                            }
                            string okey = string.Join("|", room, e.Name, si.ToString(Inv), p.Type.ToString(Inv), p.Arg.ToString(Inv),
                                p.Pos.X.ToString("F1", Inv), p.Pos.Y.ToString("F1", Inv), p.Pos.Z.ToString("F1", Inv));
                            bool overridden = overrides.TryGetValue(okey, out var ov);
                            if (overridden)
                            {
                                twin = ov.Pos; method = "override (" + ov.Status + "): " + ov.Note; chk = false; overridesUsed++;
                            }
                            var rec = new byte[EntSize];
                            Buffer.BlockCopy(b, p.Off, rec, 0, EntSize);
                            Buffer.BlockCopy(BitConverter.GetBytes(twin.X), 0, rec, 4, 4);
                            Buffer.BlockCopy(BitConverter.GetBytes(twin.Y), 0, rec, 8, 4);
                            Buffer.BlockCopy(BitConverter.GetBytes(twin.Z), 0, rec, 12, 4);
                            short serial = (short)(++maxSerial);
                            Buffer.BlockCopy(BitConverter.GetBytes(serial), 0, rec, 0x1E, 2);
                            inserts.Add((before ? p.Off : p.Off + EntSize, rec, sp.HdrOff));
                            placements++;
                            string key = overridden ? "OVERRIDE " + ov.Status : chk ? Strip(method) : "UNCHECKED";
                            methodCount[key] = methodCount.TryGetValue(key, out int mc) ? mc + 1 : 1;
                            rep.AppendLine(string.Join(",", room, e.Name, si.ToString(Inv), p.Type.ToString(Inv), p.Arg.ToString(Inv),
                                p.Pos.X.ToString("F1", Inv), p.Pos.Y.ToString("F1", Inv), p.Pos.Z.ToString("F1", Inv), fr.Count.ToString(Inv),
                                "\"" + method.Replace('"', ' ') + (p.Obj == Player ? "" : " (direct object 0x" + p.Obj.ToString("X") + ")") + "\"", overridden ? "override" : chk ? "yes" : "no", twin.X.ToString("F1", Inv), twin.Y.ToString("F1", Inv), twin.Z.ToString("F1", Inv),
                                Dist2D(twin, p.Pos).ToString("F0", Inv), serial.ToString(Inv)));
                        }
                    }
                    if (inserts.Count == 0) continue;
                    // header counts first (offsets still valid), then splice from the back
                    foreach (var grp in inserts.GroupBy(x => x.Hdr))
                    {
                        short cnt = (short)(BitConverter.ToInt16(b, grp.Key + 4) + grp.Count());
                        Buffer.BlockCopy(BitConverter.GetBytes(cnt), 0, b, grp.Key + 4, 2);
                    }
                    var list = b.ToList();
                    foreach (var ins in inserts.OrderByDescending(x => x.At)) list.InsertRange(ins.At, ins.Rec);
                    var nb = list.ToArray();
                    if (Walk(nb) == null) throw new Exception("internal error: result does not parse: " + room + " " + e.Name);
                    e.Stream = new MemoryStream(nb);
                    changed = true;
                }

            if (changed || fromOverlay.Contains(kv.Key))
            {
                var outFile = Path.Combine(outDir, "ard", kv.Key);
                if (changed) { using (var o = File.Create(outFile)) OpenKh.Kh2.Bar.Write(o, bar); }
                else File.Copy(kv.Value, outFile, true);
                written++;
            }
        }
        File.WriteAllText(reportCsv, rep.ToString(), new UTF8Encoding(false));
        Console.WriteLine("room files read: " + src.Count + ", written: " + written + ", twin placements: " + placements
            + ", spawn entries left untouched (unknown layout): " + undecodable + ", rooms without usable map data: " + noMap);
        foreach (var m in methodCount) Console.WriteLine("  " + m.Value.ToString(Inv).PadLeft(5) + "  " + m.Key);
        if (overrides.Count > 0) Console.WriteLine("  override lines read: " + overrides.Count + ", used: " + overridesUsed);
        foreach (var s in skipped) Console.WriteLine("  skipped: " + s);
        return 0;
    }

    // ---------- lane J: a closer look at the placements lane F could not prove ----------

    static List<float> FloorsAt(Geo g, float x, float z)
    {
        var res = new List<float>();
        foreach (var t in g.Floors)
        {
            if (x < t.MinX || x > t.MaxX || z < t.MinZ || z > t.MaxZ) continue;
            float d = (t.B.Z - t.C.Z) * (t.A.X - t.C.X) + (t.C.X - t.B.X) * (t.A.Z - t.C.Z);
            if (Math.Abs(d) < 1e-6f) continue;
            float u = ((t.B.Z - t.C.Z) * (x - t.C.X) + (t.C.X - t.B.X) * (z - t.C.Z)) / d;
            float v = ((t.C.Z - t.A.Z) * (x - t.C.X) + (t.A.X - t.C.X) * (z - t.C.Z)) / d;
            float w = 1 - u - v;
            if (u < -0.001f || v < -0.001f || w < -0.001f) continue;
            float y = u * t.A.Y + v * t.B.Y + w * t.C.Y;
            if (!res.Any(r => Math.Abs(r - y) < 1f)) res.Add(y);
        }
        res.Sort();
        return res;
    }

    // any collision triangle (wall or floor/ceiling) between two points
    static bool BlockedAny(Geo g, Vector3 p, Vector3 q)
    {
        float minX = Math.Min(p.X, q.X), maxX = Math.Max(p.X, q.X), minZ = Math.Min(p.Z, q.Z), maxZ = Math.Max(p.Z, q.Z);
        foreach (var t in g.Walls.Concat(g.Floors))
        {
            if (t.MaxX < minX || t.MinX > maxX || t.MaxZ < minZ || t.MinZ > maxZ) continue;
            if (SegHitsTri(p, q, t)) return true;
        }
        return false;
    }

    // free space around "c" at its own height, and a free straight line from "p" (for swimming rooms and for
    // spawn points high in the air)
    static bool FreeSpace(Geo g, Vector3 p, Vector3 c)
    {
        if (BlockedAny(g, p, c)) return false;
        for (int k = 0; k < 8; k++)
        {
            double ang = k * Math.PI / 4;
            if (BlockedAny(g, c, new Vector3(c.X + 45 * (float)Math.Sin(ang), c.Y, c.Z + 45 * (float)Math.Cos(ang)))) return false;
        }
        if (BlockedAny(g, c, new Vector3(c.X, c.Y - 90, c.Z))) return false;   // head room (up is negative)
        return true;
    }

    public class Found { public string Mode, Name; public Vector3 Pos; public string Note; }

    // The lane J rule for one placement. Returns null when nothing can be proven from the collision data.
    public static Found Better(Geo geo, Ent p, List<Ent> friends, List<Zone> zones, List<Vector3> others)
    {
        if (geo == null) return null;
        var fwd = new Vector3((float)Math.Sin(p.RotY), 0, (float)-Math.Cos(p.RotY));
        var right = new Vector3(fwd.Z, 0, -fwd.X);
        var cands = new List<(string Name, Vector3 Pos)>();
        // same order of preference as lane F: beside the player first (so neither hero hides the other from a camera
        // behind them), then the designer-made ground between the friends, then a finer ring of spots
        Func<int, float, (string, Vector3)> ring = (deg, r) =>
        {
            double a = deg * Math.PI / 180;
            var dir = fwd * (float)Math.Cos(a) + right * (float)Math.Sin(a);
            string nm = deg == 0 ? "ahead" : deg == 180 ? "behind" : (Math.Abs(deg) < 90 ? "ahead " : Math.Abs(deg) > 90 ? "behind " : "") + (deg > 0 ? "right" : "left") + " (" + Math.Abs(deg) + " deg)";
            return (nm + " " + r, p.Pos + dir * r);
        };
        foreach (var deg in new[] { 90, -90, 45, -45 }) cands.Add(ring(deg, 110f));
        if (friends.Count == 2) cands.Add(("between the two friends", (friends[0].Pos + friends[1].Pos) / 2));
        foreach (var f in friends) cands.Add(("between player and a friend", (p.Pos + f.Pos) / 2));
        foreach (var deg in new[] { 67, -67, 112, -112, 22, -22, 0, 135, -135, 157, -157, 180 }) cands.Add(ring(deg, 110f));
        foreach (var r in new[] { 95f, 80f, 70f, 60f })
            foreach (var deg in new[] { 90, -90, 45, -45, 67, -67, 112, -112, 22, -22, 0, 135, -135, 157, -157, 180 })
                cands.Add(ring(deg, r));
        cands = cands.Where(c => Dist2D(c.Pos, p.Pos) >= 59.5f && friends.All(f => Dist2D(c.Pos, f.Pos) >= 59.5f)).ToList();
        var open = zones.Where(z => !z.Contains(p.Pos, 0)).ToList();
        cands = cands.Where(c => !open.Any(z => z.Contains(c.Pos, 30)) && !others.Any(o => Dist2D(o, c.Pos) < 50 && Math.Abs(o.Y - p.Pos.Y) < 200)).ToList();

        var floors = FloorsAt(geo, p.Pos.X, p.Pos.Z);
        float near = FloorAt(geo, p.Pos.X, p.Pos.Z, p.Pos.Y, 150);
        if (!float.IsNaN(near))
        {
            // ground under the player: lane F's own ground test, on the wider ring of spots
            foreach (var c in cands)
                if (SpotOk(geo, p.Pos, near, c.Pos, out float fc))
                    return new Found { Mode = "ground", Name = c.Name, Pos = new Vector3(c.Pos.X, fc + (p.Pos.Y - near), c.Pos.Z), Note = "floor " + near.ToString("F0", Inv) };
            return null;
        }
        // no ground near the player's feet (the hero swims, flies, drops in, or stands on a platform that is an object and
        // not part of the room's collision data). The friends' spots are designer-made, so try the spots between them first:
        // they are on the same unseen platform if there is one.
        var below = floors.Where(y => y > p.Pos.Y + 150).ToList();
        foreach (var c in cands.Where(x => x.Name.StartsWith("between")))
        {
            var cs = new Vector3(c.Pos.X, c.Pos.Y, c.Pos.Z);
            if (Math.Abs(cs.Y - p.Pos.Y) <= 60 && FreeSpace(geo, p.Pos, cs))
                return new Found { Mode = "designer spot", Name = c.Name, Pos = cs, Note = "no ground data under the player; spot taken from the friends' own places; free line to the player" + (below.Count > 0 ? "; nearest floor below at " + below[0].ToString("F0", Inv) : "") };
        }
        if (below.Count > 0)
        {
            float drop = below[0];
            foreach (var c in cands)
            {
                var cs = new Vector3(c.Pos.X, p.Pos.Y, c.Pos.Z);
                if (!FreeSpace(geo, p.Pos, cs)) continue;
                if (SpotOk(geo, p.Pos, drop, c.Pos, out float fc) && !BlockedAny(geo, cs, new Vector3(cs.X, fc - 5, cs.Z)))
                    return new Found { Mode = "drop", Name = c.Name, Pos = cs, Note = "spawn " + (drop - p.Pos.Y).ToString("F0", Inv) + " above the floor at " + drop.ToString("F0", Inv) };
            }
        }
        // nothing to stand on at all (swimming, flying, or a platform that is an object): free space only
        foreach (var c in cands)
        {
            var cs = new Vector3(c.Pos.X, p.Pos.Y, c.Pos.Z);
            if (FreeSpace(geo, p.Pos, cs))
                return new Found { Mode = "free space", Name = c.Name, Pos = cs, Note = below.Count > 0 ? "floor far below at " + below[0].ToString("F0", Inv) + " did not pass" : "no floor below the spawn point" };
        }
        return null;
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int Study(string baseDir, string mapDir, string lanefReport, string outCsv)
    {
        var sb = new StringBuilder();
        sb.AppendLine("room,group,spawnpoint,spawn_type,spawn_arg,player_x,player_y,player_z,friends,lane_f_method,map,floors_under_player,mode,spot,twin_x,twin_y,twin_z,note");
        foreach (var line in File.ReadAllLines(lanefReport).Skip(1))
        {
            // the method column is quoted and holds no comma-free guarantee: split around the quotes
            int q1 = line.IndexOf('"'), q2 = line.LastIndexOf('"');
            var head = line.Substring(0, q1).TrimEnd(',').Split(',');
            var tail = line.Substring(q2 + 1).TrimStart(',').Split(',');
            if (tail[0] != "no") continue;
            string room = head[0], group = head[1]; int si = int.Parse(head[2], Inv); byte type = byte.Parse(head[3], Inv), arg = byte.Parse(head[4], Inv);
            var pp = new Vector3(float.Parse(head[5], Inv), float.Parse(head[6], Inv), float.Parse(head[7], Inv));
            OpenKh.Kh2.Bar bar;
            using (var s = File.OpenRead(Path.Combine(baseDir, room + ".ard"))) bar = OpenKh.Kh2.Bar.Read(s);
            var zones = new List<Zone>(); var others = new List<Vector3>();
            Ent pl = null; List<Ent> fr = null;
            foreach (var e in bar.Where(x => x.Type == OpenKh.Kh2.Bar.EntryType.AreaDataSpawn))
            {
                var w = Walk(Bytes(e.Stream));
                if (w == null) continue;
                foreach (var sp in w) zones.AddRange(sp.Zones);
                foreach (var sp in w) others.AddRange(sp.Ents.Where(x => x.Obj != Player && x.Obj != Friend1 && x.Obj != Friend2).Select(x => x.Pos));
                if (e.Name == group && si < w.Count && pl == null)
                {
                    pl = w[si].Ents.FirstOrDefault(x => x.Type == type && x.Arg == arg && (x.Pos - pp).Length() < 0.2f && x.Obj != Friend1 && x.Obj != Friend2);
                    if (pl != null) fr = w[si].Ents.Where(x => (x.Obj == Friend1 || x.Obj == Friend2) && x.Type == type && x.Arg == arg).ToList();
                }
            }
            string mapFile = Path.Combine(mapDir, room + ".map");
            var geo = LoadGeo(mapFile);
            string floors = geo == null ? "" : string.Join(" ", FloorsAt(geo, pp.X, pp.Z).Select(y => y.ToString("F0", Inv)));
            Found f = pl == null ? null : Better(geo, pl, fr, zones, others);
            sb.AppendLine(string.Join(",", room, group, si.ToString(Inv), type.ToString(Inv), arg.ToString(Inv), head[5], head[6], head[7], head[8],
                "\"" + line.Substring(q1 + 1, q2 - q1 - 1) + "\"", geo == null ? "no map file" : "tris " + (geo.Floors.Count + geo.Walls.Count),
                "\"" + floors + "\"", f == null ? "NOT PROVEN" : f.Mode, f == null ? "" : "\"" + f.Name + "\"",
                f == null ? "" : f.Pos.X.ToString("F1", Inv), f == null ? "" : f.Pos.Y.ToString("F1", Inv), f == null ? "" : f.Pos.Z.ToString("F1", Inv),
                "\"" + (pl == null ? "placement not found again" : f == null ? "" : f.Note) + "\""));
        }
        File.WriteAllText(outCsv, sb.ToString(), new UTF8Encoding(false));
        Console.Write(sb.ToString());
        return 0;
    }

    static string SpotWhy(Geo g, Vector3 p, float floorP, Vector3 c)
    {
        float prev = floorP;
        const int steps = 6;
        for (int i = 1; i <= steps; i++)
        {
            float t = i / (float)steps;
            float f = FloorAt(g, p.X + (c.X - p.X) * t, p.Z + (c.Z - p.Z) * t, prev, 45);
            if (float.IsNaN(f)) return "no floor at step " + i + " of 6";
            prev = f;
        }
        float floorC = prev;
        if (Math.Abs(floorC - floorP) > 120) return "height difference " + (floorC - floorP).ToString("F0", Inv);
        foreach (var h in new[] { 30f, 80f })
            if (Blocked(g, new Vector3(p.X, floorP - h, p.Z), new Vector3(c.X, floorC - h, c.Z))) return "wall between at height " + h + " " + WhichWall(g, new Vector3(p.X, floorP - h, p.Z), new Vector3(c.X, floorC - h, c.Z));
        for (int k = 0; k < 8; k++)
        {
            double ang = k * Math.PI / 4;
            var q = new Vector3(c.X + 40 * (float)Math.Sin(ang), floorC - 45, c.Z + 40 * (float)Math.Cos(ang));
            if (Blocked(g, new Vector3(c.X, floorC - 45, c.Z), q)) return "wall within 40 (direction " + (k * 45) + ") " + WhichWall(g, new Vector3(c.X, floorC - 45, c.Z), q);
            if (float.IsNaN(FloorAt(g, q.X, q.Z, floorC, 60))) return "no floor within 40 (direction " + (k * 45) + ")";
        }
        return "OK floor " + floorC.ToString("F0", Inv);
    }

    static string WhichWall(Geo g, Vector3 p, Vector3 q)
    {
        foreach (var t in g.Walls)
            if (SegHitsTri(p, q, t))
            {
                float top = Math.Min(t.A.Y, Math.Min(t.B.Y, t.C.Y)), bottom = Math.Max(t.A.Y, Math.Max(t.B.Y, t.C.Y));
                return "[mesh visibility " + t.Vis + " group " + t.Grp + " flags 0x" + t.Flags.ToString("X") + ", wall from y " + bottom.ToString("F0", Inv) + " up to " + top.ToString("F0", Inv) + "]";
            }
        return "";
    }

    // Why does every spot fail for one placement? Prints one line per candidate spot.
    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int Why(string ardFile, string mapFile, string group, int si, byte type, byte arg)
    {
        OpenKh.Kh2.Bar bar;
        using (var s = File.OpenRead(ardFile)) bar = OpenKh.Kh2.Bar.Read(s);
        var zones = new List<Zone>(); var others = new List<Vector3>(); Ent p = null; List<Ent> fr = null;
        foreach (var e in bar.Where(x => x.Type == OpenKh.Kh2.Bar.EntryType.AreaDataSpawn))
        {
            var w = Walk(Bytes(e.Stream));
            if (w == null) continue;
            foreach (var sp in w) zones.AddRange(sp.Zones);
            foreach (var sp in w) others.AddRange(sp.Ents.Where(x => x.Obj != Player && x.Obj != Friend1 && x.Obj != Friend2).Select(x => x.Pos));
            if (e.Name == group && si < w.Count && p == null)
            {
                p = w[si].Ents.FirstOrDefault(x => x.Obj == Player && x.Type == type && x.Arg == arg);
                if (p != null) fr = w[si].Ents.Where(x => (x.Obj == Friend1 || x.Obj == Friend2) && x.Type == type && x.Arg == arg).ToList();
            }
        }
        var geo = LoadGeo(mapFile);
        float near = FloorAt(geo, p.Pos.X, p.Pos.Z, p.Pos.Y, 150);
        Console.WriteLine("player " + p.Pos + " rotY " + p.RotY.ToString("F2", Inv) + " floor " + near + " zones " + zones.Count + " others " + others.Count);
        foreach (var z in zones.Where(z => Dist2D(z.Pos, p.Pos) < 600)) Console.WriteLine("  zone shape " + z.Shape + " at " + z.Pos + " scale " + z.Scale + " contains player: " + z.Contains(p.Pos, 0));
        foreach (var o in others.Where(o => Dist2D(o, p.Pos) < 250)) Console.WriteLine("  other object at " + o + " dist " + Dist2D(o, p.Pos).ToString("F0", Inv));
        var fwd = new Vector3((float)Math.Sin(p.RotY), 0, (float)-Math.Cos(p.RotY));
        var right = new Vector3(fwd.Z, 0, -fwd.X);
        var open = zones.Where(z => !z.Contains(p.Pos, 0)).ToList();
        foreach (var r in new[] { 110f, 80f, 60f })
            foreach (var deg in new[] { 90, -90, 45, -45, 0, 135, -135, 180 })
            {
                double a = deg * Math.PI / 180;
                var c = p.Pos + (fwd * (float)Math.Cos(a) + right * (float)Math.Sin(a)) * r;
                string why = open.Any(z => z.Contains(c, 30)) ? "inside a trigger zone" :
                    others.Any(o => Dist2D(o, c) < 50 && Math.Abs(o.Y - p.Pos.Y) < 200) ? "on another object" :
                    fr.Any(f => Dist2D(c, f.Pos) < 59.5f) ? "on a friend's spot" : SpotWhy(geo, p.Pos, near, c);
                Console.WriteLine("  r " + r + " deg " + deg.ToString(Inv).PadLeft(4) + " -> " + why);
            }
        if (fr.Count == 2)
        {
            var c = (fr[0].Pos + fr[1].Pos) / 2;
            Console.WriteLine("  between the friends " + c + " -> " + (open.Any(z => z.Contains(c, 30)) ? "inside a trigger zone" : SpotWhy(geo, p.Pos, near, c)));
        }
        return 0;
    }

    // One placement under one MapVisibility value (64-bit hex: high word first, then low word, e.g. 9000000000003F0F).
    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int SpotMask(string ardFile, string mapFile, string group, int si, byte type, byte arg, string maskHex)
    {
        UseMask = true; Mask = Convert.ToUInt64(maskHex, 16);
        OpenKh.Kh2.Bar bar;
        using (var s = File.OpenRead(ardFile)) bar = OpenKh.Kh2.Bar.Read(s);
        var zones = new List<Zone>(); var others = new List<Vector3>(); Ent p = null; List<Ent> fr = null;
        foreach (var e in bar.Where(x => x.Type == OpenKh.Kh2.Bar.EntryType.AreaDataSpawn))
        {
            var w = Walk(Bytes(e.Stream));
            if (w == null) continue;
            foreach (var sp in w) zones.AddRange(sp.Zones);
            foreach (var sp in w) others.AddRange(sp.Ents.Where(x => x.Obj != Player && x.Obj != Friend1 && x.Obj != Friend2).Select(x => x.Pos));
            if (e.Name == group && si < w.Count && p == null)
            {
                p = w[si].Ents.FirstOrDefault(x => x.Obj == Player && x.Type == type && x.Arg == arg);
                if (p != null) fr = w[si].Ents.Where(x => (x.Obj == Friend1 || x.Obj == Friend2) && x.Type == type && x.Arg == arg).ToList();
            }
        }
        var geo = LoadGeo(mapFile);
        var f = Better(geo, p, fr, zones, others);
        Console.WriteLine("mask " + maskHex + ": collisions left out " + geo.Skipped + "; " + (f == null ? "NOT PROVEN" : f.Mode + " | " + f.Name + " | " + f.Pos.X.ToString("F1", Inv) + "," + f.Pos.Y.ToString("F1", Inv) + "," + f.Pos.Z.ToString("F1", Inv) + " | " + f.Note));
        return 0;
    }

    // For every room map: which (group, visibility) switch bytes its collision meshes carry, with triangle counts.
    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int MeshGroups(string mapDir, string outCsv)
    {
        var sb = new StringBuilder();
        sb.AppendLine("room,group,visibility,collisions");
        foreach (var f in Directory.GetFiles(mapDir, "*.map").OrderBy(x => x, StringComparer.Ordinal))
        {
            try
            {
                OpenKh.Kh2.Bar bar;
                using (var s = File.OpenRead(f)) bar = OpenKh.Kh2.Bar.Read(s);
                var e = bar.FirstOrDefault(x => x.Type == OpenKh.Kh2.Bar.EntryType.CollisionOctalTree);
                if (e == null) continue;
                e.Stream.Position = 0;
                var coct = OpenKh.Kh2.Coct.Read(e.Stream);
                var seen = new HashSet<object>();
                var cnt = new SortedDictionary<(int, int), int>();
                foreach (var node in coct.Nodes)
                    foreach (var mesh in node.Meshes)
                    {
                        if (!seen.Add(mesh)) continue;
                        var k = ((int)mesh.Group, (int)mesh.Visibility);
                        cnt[k] = (cnt.TryGetValue(k, out int c) ? c : 0) + mesh.Collisions.Count;
                    }
                foreach (var kv in cnt) sb.AppendLine(Path.GetFileNameWithoutExtension(f) + "," + kv.Key.Item1 + "," + kv.Key.Item2 + "," + kv.Value);
            }
            catch (Exception) { }
        }
        File.WriteAllText(outCsv, sb.ToString());
        Console.WriteLine("written " + outCsv);
        return 0;
    }

    // Print the raw bytes of the spawn entries the known layout does not fit (goal 3).
    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int RawSpawn(string ardFile, string outDir)
    {
        Directory.CreateDirectory(outDir);
        OpenKh.Kh2.Bar bar;
        using (var s = File.OpenRead(ardFile)) bar = OpenKh.Kh2.Bar.Read(s);
        string room = Path.GetFileNameWithoutExtension(ardFile);
        foreach (var e in bar)
        {
            var b = Bytes(e.Stream);
            bool known = e.Type != OpenKh.Kh2.Bar.EntryType.AreaDataSpawn || Walk(b) != null;
            Console.WriteLine(room + " " + e.Name.PadRight(5) + " " + e.Type.ToString().PadRight(16) + " size " + b.Length.ToString(Inv).PadLeft(6) + (known ? "" : "   <-- not in the known layout; first word " + (b.Length >= 4 ? BitConverter.ToInt32(b, 0).ToString(Inv) : "-")));
            if (!known) File.WriteAllBytes(Path.Combine(outDir, room + "_" + e.Name + ".bin"), b);
        }
        return 0;
    }

    static string Strip(string m)
    {
        int i = m.LastIndexOf(' ');
        return i > 0 && float.TryParse(m.Substring(i + 1), NumberStyles.Float, Inv, out _) ? m.Substring(0, i) : m;
    }
}
