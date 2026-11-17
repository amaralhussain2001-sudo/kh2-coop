// Room data (ARD) and object list helpers for the investigation phase.
//   ard-dump   <ardFile> <outTxt>
//   ard-add    <inArd> <outArd> <spawnEntryName> <spawnPointIndex> <cloneEntityIndex> <objectIdHex> <dx> <dy> <dz>
//   objentry   <00objentry.bin> <outTxt>
using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Text;
using OpenKh.Kh2;
using OpenKh.Kh2.Ard;

static class ArdCmds
{
    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int Dump(string ardFile, string outTxt)
    {
        var sb = new StringBuilder();
        Bar bar;
        using (var s = File.OpenRead(ardFile)) bar = Bar.Read(s);
        foreach (var e in bar)
        {
            sb.AppendLine("==== entry " + e.Name + "  type " + e.Type + "  index " + e.Index + "  size " + e.Stream.Length);
            e.Stream.Position = 0;
            try
            {
                if (e.Type == Bar.EntryType.AreaDataScript)
                    sb.AppendLine(AreaDataScript.Decompile(AreaDataScript.Read(e.Stream)));
                else if (e.Type == Bar.EntryType.AreaDataSpawn)
                {
                    var sps = SpawnPoint.Read(e.Stream);
                    for (int i = 0; i < sps.Count; i++)
                    {
                        var sp = sps[i];
                        sb.AppendLine("  spawnpoint " + i + ": entities " + sp.Entities.Count);
                        for (int j = 0; j < sp.Entities.Count; j++)
                        {
                            var en = sp.Entities[j];
                            sb.AppendLine(string.Format(CultureInfo.InvariantCulture,
                                "    [{0}] obj 0x{1:X4} pos ({2:F1}, {3:F1}, {4:F1}) rotY {5:F2} type {6} arg {7} serial {8} a1 {9} a2 {10} rc {11} delay {12} cmd {13} range {14} lvl {15} medal {16}",
                                j, en.ObjectId, en.PositionX, en.PositionY, en.PositionZ, en.RotationY, en.SpawnType, en.SpawnArgument,
                                en.Serial, en.Argument1, en.Argument2, en.ReactionCommand, en.SpawnDelay, en.Command, en.SpawnRange, en.Level, en.Medal));
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                sb.AppendLine("  (cannot decode: " + ex.Message + ")");
            }
        }
        File.WriteAllText(outTxt, sb.ToString());
        Console.WriteLine("entries: " + bar.Count + " -> " + outTxt);
        return 0;
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int Add(string inArd, string outArd, string spawnName, int spIndex, int cloneIndex, int objectId, float dx, float dy, float dz)
    {
        Bar bar;
        using (var s = File.OpenRead(inArd)) bar = Bar.Read(s);
        var entry = bar.First(x => x.Name == spawnName && x.Type == Bar.EntryType.AreaDataSpawn);
        entry.Stream.Position = 0;
        var sps = SpawnPoint.Read(entry.Stream);
        var sp = sps[spIndex];
        var src = sp.Entities[cloneIndex];
        var ne = new SpawnPoint.Entity
        {
            ObjectId = objectId,
            PositionX = src.PositionX + dx, PositionY = src.PositionY + dy, PositionZ = src.PositionZ + dz,
            RotationX = src.RotationX, RotationY = src.RotationY, RotationZ = src.RotationZ,
            SpawnType = src.SpawnType, SpawnArgument = src.SpawnArgument, Serial = (short)(sp.Entities.Max(x => x.Serial) + 1),
            Argument1 = src.Argument1, Argument2 = src.Argument2, ReactionCommand = 0, SpawnDelay = src.SpawnDelay,
            Command = src.Command, SpawnRange = src.SpawnRange, Level = src.Level, Medal = src.Medal,
        };
        sp.Entities.Add(ne);
        var ms = new MemoryStream();
        SpawnPoint.Write(ms, sps);
        ms.Position = 0;
        entry.Stream = ms;
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(outArd)));
        using (var o = File.Create(outArd)) Bar.Write(o, bar);
        Console.WriteLine(string.Format(CultureInfo.InvariantCulture, "added obj 0x{0:X} to {1}[{2}] at ({3:F1}, {4:F1}, {5:F1}), serial {6}; {7} -> {8} bytes",
            objectId, spawnName, spIndex, ne.PositionX, ne.PositionY, ne.PositionZ, ne.Serial, new FileInfo(inArd).Length, new FileInfo(outArd).Length));
        return 0;
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int ObjList(string file, string outTxt)
    {
        var sb = new StringBuilder();
        System.Collections.Generic.List<Objentry> list;
        using (var s = File.OpenRead(file)) list = Objentry.Read(s);
        foreach (var o in list)
            sb.AppendLine(string.Format(CultureInfo.InvariantCulture, "0x{0:X4} type {1,-10} model {2,-20} anim {3,-24} flags 0x{4:X4} status {5} moveset {6} form {7} spawns {8:X},{9:X},{10:X},{11:X}",
                o.ObjectId, o.ObjectType, o.ModelName, o.AnimationName, o.Flags, o.NeoStatus, o.NeoMoveset, o.ObjectForm,
                o.SpawnObject1, o.SpawnObject2, o.SpawnObject3, o.SpawnObject4));
        File.WriteAllText(outTxt, sb.ToString());
        Console.WriteLine("objects: " + list.Count + " -> " + outTxt);
        return 0;
    }
}
