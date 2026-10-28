#if TOOLS
using System;
using Godot;

namespace MedievalKit.Editor;

/// <summary>kit_cli's room commands (KitRoomTools), run once the node stands in the tree, then quit:
/// rooms golden [log] | rooms validate [which] [count] [first seed] | rooms dump &lt;which&gt; &lt;count&gt; &lt;first seed&gt; &lt;out.jsonl&gt; |
/// houses [count] [first seed] | housedump [count] [out.jsonl]</summary>
public partial class KitRoomsCli : Node
{
    string[] args = Array.Empty<string>();

    public void Setup(string[] a) => args = a;

    public override void _Ready() => Callable.From(Run).CallDeferred();

    string Arg(int i, string fallback) => i < args.Length && args[i] != "" ? args[i] : fallback;

    void Run()
    {
        int code = 0;
        try
        {
            switch (Arg(0, ""))
            {
                case "golden":
                    GD.Print(KitRoomTools.GoldenTest(this, Arg(1, null)));
                    break;
                case "validate":
                    GD.Print(KitRoomTools.ValidateGenerators(this, int.Parse(Arg(2, "5")), Arg(1, "all"), int.Parse(Arg(3, "1"))));
                    break;
                case "dump":
                    GD.Print(KitRoomTools.Dump(this, Arg(1, "all"), int.Parse(Arg(2, "5")), int.Parse(Arg(3, "1")), Arg(4, "user://rooms_dump.jsonl")));
                    break;
                case "houses":
                    GD.Print(KitHouseTools.GenerateHouseSet(this, int.Parse(Arg(1, "12")), int.Parse(Arg(2, "1000"))));
                    break;
                case "housedump":
                    GD.Print(KitHouseTools.Dump(this, int.Parse(Arg(1, "20")), Arg(2, "user://houses_dump.jsonl")));
                    break;
                default:
                    GD.PushError("kit_cli rooms: golden [log] | validate [which] [count] [first] | dump <which> <count> <first> <out>");
                    code = 1;
                    break;
            }
        }
        catch (Exception e) { GD.PushError(e.ToString()); code = 1; }
        GetTree().Quit(code);
    }
}
#endif
