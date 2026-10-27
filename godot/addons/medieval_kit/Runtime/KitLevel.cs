using Godot;

namespace MedievalKit;

/// <summary>Level root: camera settings and links from VKI_Root (Props), and the world graph the level belongs to. Once
/// it stands, its pieces get their world bounds for the see-through's shader (<see cref="KitSeeThrough.Bound"/>: Unity
/// gives every renderer its bounds, Godot's shader has none), and its structures open as buildings, cut with caps
/// (<see cref="KitSeeThrough.SetUpLevel"/>).</summary>
[GlobalClass]
public partial class KitLevel : Node3D
{
    [Export] public string LevelName = "";
    [Export] public string BlenderScene = "";
    [Export] public string ExportVersion = "";
    [Export] public Godot.Collections.Dictionary<string, string> Props = new();
    [Export] public KitWorld World;

    /// <summary>levels set their see-through up when they stand (the cap bake turns it off: it sets them up itself)</summary>
    public static bool SetUpSeeThrough = true;

    public override void _Ready()
    {
        if (Engine.IsEditorHint() || !SetUpSeeThrough) return;
        Callable.From(() =>
        {
            KitSeeThrough.Bound(this);
            KitSeeThrough.SetUpLevel(this);
        }).CallDeferred();
    }
}
