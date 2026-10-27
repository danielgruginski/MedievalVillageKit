using Godot;

namespace MedievalKit;

/// <summary>Level root: camera settings and links from VKI_Root (Props), and the world graph the level belongs to. Once
/// it stands, its pieces get their world bounds for the see-through's shader (<see cref="KitSeeThrough.Bound"/>: Unity
/// gives every renderer its bounds, Godot's shader has none).</summary>
[GlobalClass]
public partial class KitLevel : Node3D
{
    [Export] public string LevelName = "";
    [Export] public string BlenderScene = "";
    [Export] public string ExportVersion = "";
    [Export] public Godot.Collections.Dictionary<string, string> Props = new();
    [Export] public KitWorld World;

    public override void _Ready()
    {
        if (!Engine.IsEditorHint()) Callable.From(() => KitSeeThrough.Bound(this)).CallDeferred();
    }
}
