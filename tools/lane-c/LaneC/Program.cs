// Lane C data-mining helper (read-only on the game data).
//   types                                   list OpenKH types that can read a table
//   bar-list <barFile>                      list the entries of a BAR file
//   table <barFile> <entry> <Type> <out>    read one table with OpenKH's own reader and write it as YAML
//   raw <barFile> <entry> <out.bin>         write one entry's raw bytes
//   ard-full <ardDir> <outDir>              every room file: scripts + complete spawn data
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.Loader;
using System.Text;

static class Program
{
    static string Apps;

    static int Main(string[] args)
    {
        Apps = Environment.GetEnvironmentVariable("OPENKH_APPS") ?? @"C:\Users\PC FORCE\Desktop\openkh\Apps";
        AssemblyLoadContext.Default.Resolving += (ctx, name) =>
        {
            var p = Path.Combine(Apps, name.Name + ".dll");
            return File.Exists(p) ? ctx.LoadFromAssemblyPath(p) : null;
        };
        try
        {
            if (args.Length >= 1 && args[0] == "types") return Work.Types();
            if (args.Length >= 2 && args[0] == "bar-list") return Work.BarList(args[1]);
            if (args.Length >= 5 && args[0] == "table") return Work.Table(args[1], args[2], args[3], args[4]);
            if (args.Length >= 4 && args[0] == "raw") return Work.Raw(args[1], args[2], args[3]);
            if (args.Length >= 3 && args[0] == "ard-full") return Work.ArdFull(args[1], args[2]);
            if (args.Length >= 5 && args[0] == "msg-dump") return Work.MsgDump(args[1], args[2], args[3], args[4]);
            Console.Error.WriteLine("usage: types | bar-list <bar> | table <bar> <entry> <Type> <out> | raw <bar> <entry> <out> | ard-full <ardDir> <outDir>");
            return 2;
        }
        catch (Exception e)
        {
            Console.Error.WriteLine(e);
            return 1;
        }
    }
}

static class Work
{
    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int Types()
    {
        var asm = typeof(OpenKh.Kh2.Bar).Assembly;
        foreach (var t in asm.GetTypes().Where(x => x.IsPublic || x.IsNestedPublic).OrderBy(x => x.FullName))
        {
            var m = t.GetMethods(BindingFlags.Public | BindingFlags.Static)
                .FirstOrDefault(x => x.Name == "Read" && x.GetParameters().Length == 1 && x.GetParameters()[0].ParameterType == typeof(Stream));
            if (m != null) Console.WriteLine(t.FullName + "  ->  " + m.ReturnType.Name);
        }
        return 0;
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int BarList(string file)
    {
        OpenKh.Kh2.Bar bar;
        using (var s = File.OpenRead(file)) bar = OpenKh.Kh2.Bar.Read(s);
        foreach (var e in bar) Console.WriteLine(e.Name.PadRight(6) + " type " + e.Type.ToString().PadRight(16) + " index " + e.Index + " size " + e.Stream.Length);
        return 0;
    }

    static Stream Entry(string file, string name)
    {
        OpenKh.Kh2.Bar bar;
        using (var s = File.OpenRead(file)) bar = OpenKh.Kh2.Bar.Read(s);
        var e = bar.First(x => x.Name == name);
        e.Stream.Position = 0;
        return e.Stream;
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int Raw(string file, string name, string outFile)
    {
        var st = Entry(file, name);
        using (var o = File.Create(outFile)) st.CopyTo(o);
        Console.WriteLine(name + ": " + st.Length + " bytes");
        return 0;
    }

    static string Yaml(object o)
    {
        var ser = new YamlDotNet.Serialization.SerializerBuilder()
            .ConfigureDefaultValuesHandling(YamlDotNet.Serialization.DefaultValuesHandling.Preserve)
            .Build();
        return ser.Serialize(o);
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int Table(string file, string name, string typeName, string outFile)
    {
        var asm = typeof(OpenKh.Kh2.Bar).Assembly;
        var t = asm.GetType(typeName, true);
        var m = t.GetMethods(BindingFlags.Public | BindingFlags.Static)
            .First(x => x.Name == "Read" && x.GetParameters().Length == 1 && x.GetParameters()[0].ParameterType == typeof(Stream));
        var st = Entry(file, name);
        var res = m.Invoke(null, new object[] { st });
        if (res is IEnumerable en && !(res is string)) res = en.Cast<object>().ToList();
        File.WriteAllText(outFile, Yaml(res));
        Console.WriteLine(name + " (" + typeName + ") -> " + outFile);
        return 0;
    }

    // msg-dump <barFile> <entry> <jp|en> <out.tsv>: every message id with its decoded text (one line each)
    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int MsgDump(string file, string name, string lang, string outFile)
    {
        var st = Entry(file, name);
        var list = OpenKh.Kh2.Msg.Read(st);
        var enc = lang == "jp" ? OpenKh.Kh2.Messages.Encoders.JapaneseSystem : OpenKh.Kh2.Messages.Encoders.InternationalSystem;
        var sb = new StringBuilder();
        foreach (var m in list.OrderBy(x => x.Id))
        {
            string text;
            try { text = OpenKh.Kh2.Messages.MsgSerializer.SerializeText(enc.Decode(m.Data)); }
            catch (Exception ex) { text = "(cannot decode: " + ex.Message + ")"; }
            sb.Append(m.Id).Append('\t').Append(text.Replace("\r", "").Replace("\n", " / ").Replace("\t", " ")).Append('\n');
        }
        File.WriteAllText(outFile, sb.ToString(), new UTF8Encoding(false));
        Console.WriteLine(name + ": " + list.Count + " messages -> " + outFile);
        return 0;
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int ArdFull(string ardDir, string outDir)
    {
        Directory.CreateDirectory(outDir);
        int n = 0, bad = 0;
        foreach (var f in Directory.GetFiles(ardDir, "*.ard").OrderBy(x => x, StringComparer.Ordinal))
        {
            var sb = new StringBuilder();
            OpenKh.Kh2.Bar bar;
            using (var s = File.OpenRead(f)) bar = OpenKh.Kh2.Bar.Read(s);
            foreach (var e in bar)
            {
                sb.AppendLine("==== entry " + e.Name + " type " + e.Type + " index " + e.Index + " size " + e.Stream.Length);
                e.Stream.Position = 0;
                try
                {
                    if (e.Type == OpenKh.Kh2.Bar.EntryType.AreaDataScript)
                        sb.AppendLine(OpenKh.Kh2.Ard.AreaDataScript.Decompile(OpenKh.Kh2.Ard.AreaDataScript.Read(e.Stream)));
                    else if (e.Type == OpenKh.Kh2.Bar.EntryType.AreaDataSpawn && e.Stream.Length > 0)
                    {
                        var sps = OpenKh.Kh2.Ard.SpawnPoint.Read(e.Stream);
                        for (int i = 0; i < sps.Count; i++)
                        {
                            var sp = sps[i];
                            sb.AppendLine(string.Format(CultureInfo.InvariantCulture,
                                "  SP {0} type {1} flag {2} id {3} tele place {4} door {5} world {6} unk {7} ents {8} acts {9} walk {10} ret {11} sig {12}",
                                i, sp.Type, sp.Flag, sp.Id, sp.Teleport.Place, sp.Teleport.Door, sp.Teleport.World, sp.Teleport.Unknown,
                                sp.Entities.Count, sp.EventActivators.Count, sp.WalkPath.Count, sp.ReturnParameters.Count, sp.Signals.Count));
                            foreach (var en in sp.Entities)
                                sb.AppendLine(string.Format(CultureInfo.InvariantCulture,
                                    "    ENT obj 0x{0:X4} pos {1:F1} {2:F1} {3:F1} type {4} arg {5} serial {6} a1 {7} a2 {8} rc {9} delay {10} cmd {11} range {12} lvl {13} medal {14}",
                                    en.ObjectId, en.PositionX, en.PositionY, en.PositionZ, en.SpawnType, en.SpawnArgument, en.Serial,
                                    en.Argument1, en.Argument2, en.ReactionCommand, en.SpawnDelay, en.Command, en.SpawnRange, en.Level, en.Medal));
                            foreach (var a in sp.EventActivators)
                                sb.AppendLine(string.Format(CultureInfo.InvariantCulture,
                                    "    ACT shape {0} option {1} pos {2:F1} {3:F1} {4:F1} scale {5:F1} {6:F1} {7:F1} flags 0x{8:X} type {9} onbg {10} offbg {11}",
                                    a.Shape, a.Option, a.PositionX, a.PositionY, a.PositionZ, a.ScaleX, a.ScaleY, a.ScaleZ, a.Flags, a.Type, a.OnBgGroup, a.OffBgGroup));
                            foreach (var r in sp.ReturnParameters)
                                sb.AppendLine("    RET id " + r.Id + " type " + r.Type + " rate " + r.Rate + " entry " + r.EntryType + " a4 " + r.Argument04 + " a8 " + r.Argument08 + " ac " + r.Argument0c);
                            foreach (var g in sp.Signals)
                                sb.AppendLine("    SIG id " + g.SignalId + " arg " + g.Argument + " action " + g.Action);
                        }
                    }
                }
                catch (Exception ex)
                {
                    bad++;
                    sb.AppendLine("  (cannot decode: " + ex.GetType().Name + ": " + ex.Message + ")");
                }
            }
            File.WriteAllText(Path.Combine(outDir, Path.GetFileNameWithoutExtension(f) + ".txt"), sb.ToString());
            n++;
        }
        Console.WriteLine("rooms dumped: " + n + ", entries that could not be decoded: " + bad);
        return 0;
    }
}
