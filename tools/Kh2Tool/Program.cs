// Kh2Tool: builds an OpenKH mod for the PS2 disc and writes the built files into a COPY of the disc image.
// The original disc image is only ever opened for reading.
//   patch  <extractedGameDir> <modDir> <outDir>
//   inject <srcIso> <dstIso> <builtDir> <reportFile>
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Runtime.Loader;
using System.Security.Cryptography;
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
        AssemblyLoadContext.Default.ResolvingUnmanagedDll += (asm, name) =>
        {
            foreach (var cand in new[] { name, name + ".dll" })
            {
                var p = Path.Combine(apps, cand);
                if (File.Exists(p) && NativeLibrary.TryLoad(p, out var h)) return h;
            }
            return IntPtr.Zero;
        };
        try
        {
            if (args.Length >= 4 && args[0] == "patch") return Cmds.Patch(args[1], args[2], args[3]);
            if (args.Length >= 5 && args[0] == "inject") return Cmds.Inject(args[1], args[2], args[3], args[4]);
            if (args.Length >= 3 && args[0] == "ard-dump") return ArdCmds.Dump(args[1], args[2]);
            if (args.Length >= 3 && args[0] == "objentry") return ArdCmds.ObjList(args[1], args[2]);
            if (args.Length >= 10 && args[0] == "ard-add")
            {
                var inv = System.Globalization.CultureInfo.InvariantCulture;
                return ArdCmds.Add(args[1], args[2], args[3], int.Parse(args[4]), int.Parse(args[5]), Convert.ToInt32(args[6], 16),
                    float.Parse(args[7], inv), float.Parse(args[8], inv), float.Parse(args[9], inv));
            }
            Console.Error.WriteLine("usage: patch <extractedGameDir> <modDir> <outDir> | inject <srcIso> <dstIso> <builtDir> <reportFile>");
            return 2;
        }
        catch (Exception e)
        {
            Console.Error.WriteLine(e);
            return 1;
        }
    }
}

static class Cmds
{
    const int Sector = 2048;

    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int Patch(string original, string modDir, string outDir)
    {
        Directory.CreateDirectory(outDir);
        OpenKh.Patcher.Metadata metadata;
        using (var s = File.OpenRead(Path.Combine(modDir, "mod.yml")))
            metadata = OpenKh.Patcher.Metadata.Read(s);
        var map = new ConcurrentDictionary<string, string>();
        // platform 1 = PS2 (PCSX2), game "kh2", language "en"
        new OpenKh.Patcher.PatcherProcessor().Patch(original, outDir, metadata, modDir, 1, false, map, "kh2", "en", false, new Dictionary<string, bool>());
        Console.WriteLine("patched assets: " + metadata.Assets.Count);
        return 0;
    }

    class Target
    {
        public string IdxName;
        public List<OpenKh.Kh2.Idx.Entry> List;
        public OpenKh.Kh2.Idx.Entry Entry;
    }

    class DirRec { public long RecordPos; public uint Lba; public uint Size; }

    static Dictionary<string, DirRec> ReadRoot(Stream iso)
    {
        var pvd = new byte[Sector];
        iso.Position = 16L * Sector; iso.ReadExactly(pvd);
        if (Encoding.ASCII.GetString(pvd, 1, 5) != "CD001") throw new Exception("not an ISO9660 image");
        uint lba = BitConverter.ToUInt32(pvd, 156 + 2), size = BitConverter.ToUInt32(pvd, 156 + 10);
        var d = new byte[size];
        iso.Position = (long)lba * Sector; iso.ReadExactly(d);
        var res = new Dictionary<string, DirRec>();
        int i = 0;
        while (i < d.Length)
        {
            int ln = d[i];
            if (ln == 0) { i = (i / Sector + 1) * Sector; continue; }
            var name = Encoding.ASCII.GetString(d, i + 33, d[i + 32]).Split(new[] { (char)59 })[0].ToUpperInvariant();
            res[name] = new DirRec { RecordPos = (long)lba * Sector + i, Lba = BitConverter.ToUInt32(d, i + 2), Size = BitConverter.ToUInt32(d, i + 10) };
            i += ln;
        }
        return res;
    }

    static void WriteBoth(Stream s, long pos, uint value)
    {
        var le = BitConverter.GetBytes(value);
        var be = le.Reverse().ToArray();
        s.Position = pos; s.Write(le); s.Write(be);
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int Inject(string srcIso, string dstIso, string builtDir, string reportFile)
    {
        if (Path.GetFullPath(srcIso).Equals(Path.GetFullPath(dstIso), StringComparison.OrdinalIgnoreCase))
            throw new Exception("source and destination must be different files");
        var rep = new StringBuilder();
        void Log(string s) { rep.AppendLine(s); }

        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(dstIso)));
        File.Copy(srcIso, dstIso, true);
        File.SetAttributes(dstIso, FileAttributes.Normal);

        using (var iso = new FileStream(dstIso, FileMode.Open, FileAccess.ReadWrite, FileShare.None))
        {
            long origLen = iso.Length;
            var root = ReadRoot(iso);
            var idxRec = root["KH2.IDX"]; var imgRec = root["KH2.IMG"];
            long imgBase = (long)imgRec.Lba * Sector;
            uint appendPos = (uint)(((long)imgRec.Size + Sector - 1) / Sector);
            uint appendStart = appendPos;

            byte[] ReadAt(long pos, int len) { var b = new byte[len]; iso.Position = pos; iso.ReadExactly(b); return b; }
            byte[] ReadEntry(OpenKh.Kh2.Idx.Entry e)
            {
                var raw = ReadAt(imgBase + (long)e.Offset * Sector, (e.BlockLength + 1) * Sector);
                if (e.IsCompressed) raw = OpenKh.Kh2.Img.Decompress(raw);
                if (raw.Length < e.Length) throw new Exception("short read");
                return raw.Length == e.Length ? raw : raw.Take(e.Length).ToArray();
            }

            var mainList = OpenKh.Kh2.Idx.Read(new MemoryStream(ReadAt((long)idxRec.Lba * Sector, (int)idxRec.Size)));
            Log("main index: " + mainList.Count + " entries");
            var lookup = new Dictionary<(uint, ushort), List<Target>>();
            void Register(string idxName, List<OpenKh.Kh2.Idx.Entry> list)
            {
                foreach (var e in list)
                {
                    var k = (e.Hash32, e.Hash16);
                    if (!lookup.TryGetValue(k, out var l)) lookup[k] = l = new List<Target>();
                    l.Add(new Target { IdxName = idxName, List = list, Entry = e });
                }
            }
            Register("KH2.IDX", mainList);
            var subLists = new Dictionary<string, List<OpenKh.Kh2.Idx.Entry>>();
            foreach (var sub in OpenKh.Kh2.Img.InternalIdxs)
            {
                var k = (OpenKh.Kh2.Idx.GetHash32(sub), OpenKh.Kh2.Idx.GetHash16(sub));
                var e = mainList.FirstOrDefault(x => x.Hash32 == k.Item1 && x.Hash16 == k.Item2);
                if (e == null) continue;
                var list = OpenKh.Kh2.Idx.Read(new MemoryStream(ReadEntry(e)));
                subLists[sub] = list;
                Register(sub, list);
                Log("sub index " + sub + ": " + list.Count + " entries");
            }

            var dirty = new HashSet<List<OpenKh.Kh2.Idx.Entry>>();
            int inPlace = 0, appended = 0, unchanged = 0;
            var notOnDisc = new List<string>();

            void Place(string name, byte[] data, List<Target> targets)
            {
                bool streamed = targets.Any(t => t.Entry.IsStreamed);
                bool compress = !streamed && targets.All(t => t.Entry.IsCompressed);
                var payload = compress ? OpenKh.Kh2.Img.Compress(data) : data;
                if (compress)
                {
                    var check = OpenKh.Kh2.Img.Decompress(payload);
                    if (check.Length < data.Length || !check.AsSpan(0, data.Length).SequenceEqual(data))
                    { compress = false; payload = data; }
                }
                int sectors = Math.Max(1, (payload.Length + Sector - 1) / Sector);
                if (sectors - 1 > OpenKh.Kh2.Idx.Entry.MaxBlockLength) throw new Exception("file too big for the index: " + name);
                int oldSectors = targets.Min(t => t.Entry.BlockLength + 1);
                bool sameSpot = targets.Select(t => t.Entry.Offset).Distinct().Count() == 1;
                uint pos; string how;
                if (sameSpot && sectors <= oldSectors)
                {
                    pos = targets[0].Entry.Offset; how = "in place"; inPlace++;
                    iso.Position = imgBase + (long)pos * Sector;
                    iso.Write(new byte[oldSectors * Sector]);
                }
                else
                {
                    pos = appendPos; appendPos += (uint)sectors; how = "appended"; appended++;
                }
                var buf = new byte[sectors * Sector];
                Buffer.BlockCopy(payload, 0, buf, 0, payload.Length);
                long abs = imgBase + (long)pos * Sector;
                if (abs + buf.Length > iso.Length) iso.SetLength(abs + buf.Length);
                iso.Position = abs; iso.Write(buf);
                foreach (var t in targets)
                {
                    t.Entry.Offset = pos; t.Entry.Length = data.Length;
                    t.Entry.IsCompressed = compress; t.Entry.BlockLength = sectors - 1;
                    dirty.Add(t.List);
                }
                Log(how.PadRight(9) + " " + name + "  " + data.Length + " bytes" + (compress ? " (packed " + payload.Length + ")" : "") + "  [" + string.Join(",", targets.Select(t => t.IdxName)) + "]");
            }

            var files = Directory.GetFiles(builtDir, "*", SearchOption.AllDirectories)
                .Select(f => (Rel: Path.GetRelativePath(builtDir, f).Replace((char)92, (char)47), Full: f))
                .OrderBy(x => x.Rel, StringComparer.Ordinal).ToList();
            foreach (var f in files)
            {
                var k = (OpenKh.Kh2.Idx.GetHash32(f.Rel), OpenKh.Kh2.Idx.GetHash16(f.Rel));
                if (!lookup.TryGetValue(k, out var targets)) { notOnDisc.Add(f.Rel); continue; }
                var data = File.ReadAllBytes(f.Full);
                var old = ReadEntry(targets[0].Entry);
                if (old.AsSpan().SequenceEqual(data)) { unchanged++; Log("unchanged " + f.Rel); continue; }
                Place(f.Rel, data, targets);
            }

            foreach (var kv in subLists.OrderBy(x => x.Key, StringComparer.Ordinal))
            {
                if (!dirty.Contains(kv.Value)) continue;
                var ms = new MemoryStream(); OpenKh.Kh2.Idx.Write(ms, kv.Value);
                var k = (OpenKh.Kh2.Idx.GetHash32(kv.Key), OpenKh.Kh2.Idx.GetHash16(kv.Key));
                Place(kv.Key, ms.ToArray(), lookup[k].Where(t => t.IdxName == "KH2.IDX").ToList());
            }

            var mainMs = new MemoryStream(); OpenKh.Kh2.Idx.Write(mainMs, mainList);
            if (mainMs.Length != idxRec.Size) throw new Exception("main index size changed");
            iso.Position = (long)idxRec.Lba * Sector; iso.Write(mainMs.ToArray());

            if (appendPos != appendStart)
            {
                uint newImgSize = appendPos * (uint)Sector;
                WriteBoth(iso, imgRec.RecordPos + 10, newImgSize);
                long end = imgBase + newImgSize;
                if (end > origLen - Sector) Log("note: appended data reaches the last sector of the original image");
                if (iso.Length % Sector != 0) iso.SetLength((iso.Length / Sector + 1) * Sector);
                if (iso.Length > origLen) WriteBoth(iso, 16L * Sector + 80, (uint)(iso.Length / Sector));
                Log("archive grew by " + (appendPos - appendStart) + " sectors (" + ((appendPos - appendStart) * (long)Sector) + " bytes); image length " + origLen + " -> " + iso.Length);
            }
            Log("summary: in place " + inPlace + ", appended " + appended + ", unchanged " + unchanged + ", not on the disc " + notOnDisc.Count);
            foreach (var n in notOnDisc) Log("not on disc: " + n);
            iso.Flush();
        }

        using (var fs = File.OpenRead(dstIso))
        using (var sha = SHA1.Create())
        {
            var h = Convert.ToHexString(sha.ComputeHash(fs)).ToLowerInvariant();
            Log("output: " + new FileInfo(dstIso).Length + " bytes, sha1 " + h);
        }
        File.WriteAllText(reportFile, rep.ToString());
        foreach (var l in rep.ToString().Split((char)10))
            if (l.StartsWith("summary") || l.StartsWith("output") || l.StartsWith("archive") || l.StartsWith("note") || l.StartsWith("main index"))
                Console.WriteLine(l.TrimEnd());
        return 0;
    }
}
