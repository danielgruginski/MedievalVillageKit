#if TOOLS
using Godot;

namespace MedievalKit.Editor;

/// <summary>The kit's editor menu (Project > Tools), the counterpart of Unity's Tools > Medieval Kit.</summary>
[Tool]
public partial class MedievalKitPlugin : EditorPlugin
{
    const string Check = "Medieval Kit: Check Pieces", Build = "Medieval Kit: Build Layouts";

    public override void _EnterTree()
    {
        AddToolMenuItem(Check, Callable.From(() => new KitBuilder().CheckPieces(System.Array.Empty<string>())));
        AddToolMenuItem(Build, Callable.From(() => GD.Print(new KitBuilder().BuildAllLayouts())));
    }

    public override void _ExitTree()
    {
        RemoveToolMenuItem(Check);
        RemoveToolMenuItem(Build);
    }
}
#endif
