using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>Level root: camera settings and links from VKI_Root (Props), and the world graph the level belongs to. Once
/// it stands, its pieces get their world bounds for the see-through's shader (<see cref="KitSeeThrough.Bound"/>: Unity
/// gives every renderer its bounds, Godot's shader has none), and its structures open as buildings, cut with caps
/// (<see cref="KitSeeThrough.SetUpLevel"/>; a village's: <see cref="KitVillage.SetUpSeeThrough"/>); its fires burn (<see cref="KitFires.LightLevel"/>) and its walkway decks
/// get their navmesh (<see cref="KitWalkways.Ensure"/>).</summary>
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
    /// <summary>levels light the kit's fires when they stand (a game with its own campfires turns it off and calls
    /// KitFires.Light per piece)</summary>
    public static bool LightFires = true;

    bool setUp;

    public override void _Ready()
    {
        if (Engine.IsEditorHint() || !SetUpSeeThrough) return;
        Callable.From(SetUp).CallDeferred();
    }

    /// <summary>once, while it stands (a level KitTravel took out of the tree again before this ran waits to come back)</summary>
    void SetUp()
    {
        if (setUp) return;
        if (!IsInsideTree()) { Connect(Node.SignalName.TreeEntered, Callable.From(() => Callable.From(SetUp).CallDeferred()), (uint)ConnectFlags.OneShot); return; }
        setUp = true;
        KitSeeThrough.Bound(this);
        KitSeeThrough.SetUpLevel(this);
        foreach (var v in KitNodes.Below(this, "").OfType<KitVillage>()) v.SetUpSeeThrough();   // an outdoor map's own
        if (LightFires) KitFires.LightLevel(this);
        KitWalkways.Ensure(this);
    }
}
