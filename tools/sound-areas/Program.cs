// Read-only (STATE part 149): which rooms have AREA SOUNDS. The game (0x00142BF8) starts an area sound for every collision face
// whose surface flags have bits 0x60000 (kind = (flags >> 17) & 3). This lists, per map file, the faces with those bits.
//   SoundAreas <mapDir>            (prints the Coct member names first, then one line per map with area-sound faces)
using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Collections;
using System.Collections.Generic;

static class P
{
    static object Get(object o, params string[] names)
    {
        foreach (var n in names)
        {
            var p = o.GetType().GetProperty(n, BindingFlags.Public | BindingFlags.Instance);
            if (p != null) return p.GetValue(o);
        }
        return null;
    }

    static void Main(string[] args)
    {
        var dir = args[0];
        bool shown = false, shownAtt = false;
        foreach (var file in Directory.GetFiles(dir, "*.map").OrderBy(x => x))
        {
            try
            {
                OpenKh.Kh2.Bar bar;
                using (var s = File.OpenRead(file)) bar = OpenKh.Kh2.Bar.Read(s);
                var e = bar.FirstOrDefault(x => x.Type == OpenKh.Kh2.Bar.EntryType.CollisionOctalTree);
                if (e == null) continue;
                e.Stream.Position = 0;
                var coct = OpenKh.Kh2.Coct.Read(e.Stream);
                if (!shown)
                {
                    shown = true;
                    Console.WriteLine("Coct: " + string.Join(", ", coct.GetType().GetProperties().Select(p => p.Name)));
                }
                IList flagsList = null;
                foreach (var p in coct.GetType().GetProperties())
                    if (p.Name.Contains("Flag") || p.Name.Contains("Attrib")) flagsList = p.GetValue(coct) as IList;
                var counts = new Dictionary<uint, int>();
                var seen = new HashSet<object>();
                int faces = 0;
                foreach (var node in coct.Nodes)
                    foreach (var mesh in node.Meshes)
                    {
                        if (!seen.Add(mesh)) continue;
                        foreach (var c in mesh.Collisions)
                        {
                            faces++;
                            var att = Get(c, "Attributes");
                            if (!shownAtt)
                            {
                                shownAtt = true;
                                Console.WriteLine("Collision: " + string.Join(", ", c.GetType().GetProperties().Select(p => p.Name)));
                                Console.WriteLine("Attributes: " + string.Join(", ", att.GetType().GetProperties().Select(p => p.Name + ":" + p.PropertyType.Name)));
                            }
                            var fv = Get(att, "Flags", "Value", "Raw");
                            uint flags = Convert.ToUInt32(fv);
                            if ((flags & 0x60000) != 0)
                            {
                                counts.TryGetValue(flags, out var k);
                                counts[flags] = k + 1;
                            }
                        }
                    }
                if (counts.Count > 0)
                    Console.WriteLine(Path.GetFileNameWithoutExtension(file) + "  faces " + faces + "  " +
                        string.Join("  ", counts.Select(kv => string.Format("flags {0:X8} kind {1} x{2}", kv.Key, (kv.Key >> 17) & 3, kv.Value))));
            }
            catch (Exception ex)
            {
                Console.WriteLine(Path.GetFileNameWithoutExtension(file) + "  ERROR " + ex.GetType().Name + " " + ex.Message);
            }
        }
    }
}
