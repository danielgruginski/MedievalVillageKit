using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>The scene the editor's Play From Start Level / Walk This Level run (Walker/kit_play.tscn): loads the level
/// named in user://kit_play_level.txt (the world's start when empty) through KitTravel and walks it, so nothing is saved
/// into the level: with the kit's click-to-move walker (<see cref="KitWalker"/>) where the level has a navmesh, else the
/// WASD stand-in (<see cref="KitTestWalker"/>). Unity: KitPlay.</summary>
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
        // arrive on the level's first link's spawn (both ends of a link share its id); an outdoor map from a layout (a
        // scene path) on its arrival; else its first spawn
        string spawn = world?.Find(level)?.Links.FirstOrDefault()?.Id ?? (level.StartsWith("res://") ? "arrival" : null);
        KitTravel.Arrived += PlaceOnce;
        Callable.From(() => KitTravel.Reload(level, spawn ?? "")).CallDeferred();
    }

    /// <summary>the walker, on the first arrival (no walker yet: KitTravel placed nobody; this boot scene is gone, the
    /// level replaced it)</summary>
    static void PlaceOnce(string level, KitSpawn spawn)
    {
        KitTravel.Arrived -= PlaceOnce;
        var tree = (SceneTree)Engine.GetMainLoop();
        var scene = tree.CurrentScene;
        var at = spawn ?? KitNodes.Below(scene, "").OfType<KitSpawn>().FirstOrDefault();
        var t = at?.GlobalTransform ?? Transform3D.Identity;
        bool nav = scene != null && KitNodes.Below(scene, "").OfType<KitNavMesh>().Any();
        Callable.From(() =>
        {
            if (nav) { KitWalker.Spawn(t); return; }
            var w = new KitTestWalker { Name = "KitTestWalker" };
            tree.Root.AddChild(w);
            KitTravel.Place(w, t);
        }).CallDeferred();
    }
}
