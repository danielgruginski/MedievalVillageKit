using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>The scene the editor's Play From Start Level / Walk This Level run (Walker/kit_play.tscn): loads the level
/// named in user://kit_play_level.txt (the world's start when empty) through KitTravel and walks it with a
/// KitTestWalker, so nothing is saved into the level. Unity: KitPlay.</summary>
public partial class KitPlayBoot : Node
{
    public const string LevelFile = "user://kit_play_level.txt";
    public const string Scene = KitPaths.Addon + "Walker/kit_play.tscn";

    public override void _Ready()
    {
        string level = Godot.FileAccess.FileExists(LevelFile) ? Godot.FileAccess.GetFileAsString(LevelFile).StripEdges() : "";
        var world = ResourceLoader.Exists(KitPaths.World) ? GD.Load<KitWorld>(KitPaths.World) : null;
        if (level == "") level = world?.Start ?? "";
        if (!ResourceLoader.Exists(KitTravel.ScenePath(level))) { GD.PushError($"[KitPlay] no level '{level}' (build the layouts first)"); return; }
        // arrive on the level's first link's spawn (both ends of a link share its id), else its first spawn
        string spawn = world?.Find(level)?.Links.FirstOrDefault()?.Id;
        KitTravel.Arrived += PlaceOnce;
        CallDeferred(MethodName.Begin, level, spawn ?? "");
    }

    void Begin(string level, string spawn)
    {
        GetTree().Root.AddChild(new KitTestWalker { Name = "KitTestWalker" });
        KitTravel.Reload(level, spawn);
    }

    void PlaceOnce(string level, KitSpawn spawn)
    {
        KitTravel.Arrived -= PlaceOnce;
        if (spawn != null) return;
        var first = GetTree().CurrentScene?.FindChildren("*", "", true, false).OfType<KitSpawn>().FirstOrDefault();
        if (first != null && KitTravel.Walker != null) KitTravel.Place(KitTravel.Walker, first.GlobalTransform);
    }
}
