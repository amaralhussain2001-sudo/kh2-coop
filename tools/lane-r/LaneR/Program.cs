// Lane R helper (read-only on the game data).
//   msg-encode <text>                 encode a message with the game's international text table; prints hex bytes
//   msg-get <barFile> <entry> <id>    print one message of a message file: raw hex and decoded text (to a UTF-8 file)
using System;
using System.IO;
using System.Linq;
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
            if (args.Length >= 2 && args[0] == "msg-encode") return Work.Encode(args[1]);
            if (args.Length >= 5 && args[0] == "msg-get") return Work.Get(args[1], args[2], int.Parse(args[3]), args[4]);
            Console.Error.WriteLine("usage: msg-encode <text> | msg-get <barFile> <entry> <id> <outFile>");
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
    public static int Encode(string text)
    {
        var cmds = OpenKh.Kh2.Messages.MsgSerializer.DeserializeText(text).ToList();
        var data = OpenKh.Kh2.Messages.Encoders.InternationalSystem.Encode(cmds);
        Console.WriteLine(string.Join("", data.Select(b => b.ToString("X2"))));
        return 0;
    }

    [MethodImpl(MethodImplOptions.NoInlining)]
    public static int Get(string file, string entry, int id, string outFile)
    {
        OpenKh.Kh2.Bar bar;
        using (var s = File.OpenRead(file)) bar = OpenKh.Kh2.Bar.Read(s);
        var e = bar.First(x => x.Name == entry);
        e.Stream.Position = 0;
        var list = OpenKh.Kh2.Msg.Read(e.Stream);
        var m = list.First(x => x.Id == id);
        var sb = new StringBuilder();
        sb.AppendLine(string.Join("", m.Data.Select(b => b.ToString("X2"))));
        sb.AppendLine(OpenKh.Kh2.Messages.MsgSerializer.SerializeText(OpenKh.Kh2.Messages.Encoders.InternationalSystem.Decode(m.Data)));
        File.WriteAllText(outFile, sb.ToString(), new UTF8Encoding(false));
        Console.WriteLine("message " + id + ": " + m.Data.Length + " bytes -> " + outFile);
        return 0;
    }
}
