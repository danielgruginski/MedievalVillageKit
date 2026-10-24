#if TOOLS
using Godot;

namespace MedievalKit.Editor;

/// <summary>The kit's editor menu (Project > Tools), the counterpart of Unity's Tools > Medieval Kit.</summary>
[Tool]
public partial class MedievalKitPlugin : EditorPlugin
{
    const string Check = "Medieval Kit: Check Pieces", Build = "Medieval Kit: Build Layouts",
                 PlayStart = "Medieval Kit: Play From Start Level", WalkThis = "Medieval Kit: Walk This Level";

    public override void _EnterTree()
    {
        AddToolMenuItem(Check, Callable.From(() => new KitBuilder().CheckPieces(System.Array.Empty<string>())));
        AddToolMenuItem(Build, Callable.From(() => GD.Print(new KitBuilder().BuildAllLayouts())));
        AddToolMenuItem(PlayStart, Callable.From(() => Play("")));
        AddToolMenuItem(WalkThis, Callable.From(() =>
        {
            if (EditorInterface.Singleton.GetEditedSceneRoot() is KitLevel l) Play(l.LevelName);
            else GD.PushWarning("[MedievalKit] Walk This Level: the open scene is not a kit level (res://kit/layouts/)");
        }));
    }

    /// <summary>runs Walker/kit_play.tscn on `level` (empty: the world's start) with the test walker</summary>
    static void Play(string level)
    {
        using (var f = FileAccess.Open(KitPlayBoot.LevelFile, FileAccess.ModeFlags.Write)) f.StoreString(level);
        EditorInterface.Singleton.PlayCustomScene(KitPlayBoot.Scene);
    }

    public override void _ExitTree()
    {
        foreach (var m in new[] { Check, Build, PlayStart, WalkThis }) RemoveToolMenuItem(m);
    }
}
#endif
