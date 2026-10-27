#if TOOLS
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit.Editor;

/// <summary>
/// The see-through in a built layout (res://kit/layouts/&lt;name&gt;.tscn), as a player meets it: its structures marked as
/// buildings (<see cref="KitSeeThrough.Building"/>: each KitStructure, or the showcase's VKX_ST_ group, opens as one), a stand-in walker put behind each of
/// the first <see cref="Count"/> buildings (north of it: Godot -Z, the camera's side is +Z), the kit's camera following
/// it with the hidden check on. Each stand is shot twice, see-through on and off, to &lt;out&gt;/st_&lt;layout&gt;_&lt;i&gt;[_off].png,
/// with the hidden check's answer and the buildings opened logged (st_&lt;layout&gt;.txt); the first stand's check view goes
/// to st_probe.png. Needs a window (not --headless); quits when done. kit_cli: seethrough &lt;layout&gt; &lt;out dir&gt;.
/// Unity: the itch staging KitWalkerCheck (FULL_PORT_PLAN phase 6).
/// </summary>
public partial class KitSeeThroughTest : Node
{
    public int Count = 6;
    string layout = "Structures_Showcase", outDir = "";
    readonly List<(string name, Aabb b)> stands = new();
    readonly System.Text.StringBuilder log = new();
    Node3D walker;
    KitCamera cam;
    int stand, frame, phase = -1;

    public void Setup(string layoutName, string outDirectory) { layout = layoutName; outDir = outDirectory; }

    public override void _Ready() => Callable.From(Start).CallDeferred();   // (the root is busy adding this node)

    void Start()
    {
        DisplayServer.WindowSetSize(new Vector2I(1600, 900));
        var level = GD.Load<PackedScene>($"{KitPaths.LayoutScenes}{layout}.tscn").Instantiate<Node3D>();
        GetTree().Root.AddChild(level);
        GetTree().CurrentScene = level;
        foreach (var s in level.FindChildren("*", "Node3D", true, false).OfType<Node3D>()
                     .Where(n => n is KitStructure || n.Name.ToString().StartsWith("VKX_ST_")))   // (the showcase's groups)
        {
            var b = new KitSeeThrough.Building(s);
            if (b.Pieces.Length > 0) stands.Add((s.Name, AllOf(b.Pieces)));
        }
        log.AppendLine($"{layout}: {stands.Count} buildings marked");
        var c = stands.Count > 0 ? stands.Aggregate(Vector3.Zero, (a, s) => a + s.b.GetCenter()) / stands.Count : Vector3.Zero;
        stands.Sort((a, b) => a.b.GetCenter().DistanceTo(c).CompareTo(b.b.GetCenter().DistanceTo(c)));
        walker = new Node3D { Name = "StandIn" };
        walker.AddChild(new MeshInstance3D { Mesh = new CapsuleMesh { Radius = 0.3f, Height = 1.8f }, Position = new Vector3(0, 0.9f, 0) });
        GetTree().Root.AddChild(walker);
        cam = new KitCamera { Name = "KitCamera", Target = walker };
        GetTree().Root.AddChild(cam);
        phase = 0;
    }

    static Aabb AllOf(GeometryInstance3D[] gs)
    {
        var all = KitSeeThrough.WorldAabb(gs[0]);
        foreach (var g in gs) all = all.Merge(KitSeeThrough.WorldAabb(g));
        return all;
    }

    public override void _Process(double delta)
    {
        if (phase < 0) return;
        frame++;
        if (phase == 0)                                              // stand behind the next building
        {
            if (stand >= stands.Count || stand >= Count) { Finish(); return; }
            var b = stands[stand].b;
            walker.GlobalPosition = new Vector3(b.GetCenter().X, b.Position.Y, b.Position.Z - 1.0f);
            cam.Snap();
            frame = 0; phase = 1;
            return;
        }
        if (phase == 1 && frame >= 45)                               // the check has read, the hole has opened
        {
            int open = KitSeeThrough.Buildings.Count(x => x.Open);
            log.AppendLine($"behind {stands[stand].name} {stands[stand].b.Size}: hidden {cam.SeeThroughCover:F2}, hole {cam.SeeThroughOpen:F2}, reads {cam.Probe?.Reads}, buildings open {open}");
            Shot($"st_{layout}_{stand}");
            if (stand == 0 && cam.Probe != null) cam.Probe.GetTexture().GetImage()?.SavePng($"{outDir}/st_probe.png");
            cam.SeeThroughRadius = 0f;
            frame = 0; phase = 2;
            return;
        }
        if (phase == 2 && frame >= 4)
        {
            Shot($"st_{layout}_{stand}_off");
            cam.SeeThroughRadius = 2.4f;
            stand++; phase = 0;
        }
    }

    void Shot(string name) => GetViewport().GetTexture().GetImage().SavePng($"{outDir}/{name}.png");

    void Finish()
    {
        using (var f = FileAccess.Open($"{outDir}/st_{layout}.txt", FileAccess.ModeFlags.Write)) f.StoreString(log.ToString());
        GD.Print(log.ToString());
        GetTree().Quit();
    }
}
#endif
