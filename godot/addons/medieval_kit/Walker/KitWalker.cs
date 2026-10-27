using Godot;

namespace MedievalKit;

/// <summary>
/// The kit's walker: a stand-in body on the level's navmesh with the kit's click-to-move for legs
/// (<see cref="KitClickToMove"/>) and the kit's camera following it (<see cref="KitCamera"/>: the 50-degree view, the
/// wheel's zoom, the see-through). What Play From Start Level and Walk This Level use where the level has a navmesh
/// (KitNavMesh); the WASD stand-in (<see cref="KitTestWalker"/>) elsewhere. A game brings its own player (the same two
/// with its rules on top). Lives outside the levels (a child of the tree's root), so it survives them. Shows the level's
/// name and, at the cursor, the way out under it. Unity: KitWalker (FULL_PORT_PLAN phase 6).
/// </summary>
[GlobalClass]
public partial class KitWalker : Node3D
{
    KitClickToMove legs;
    KitCamera cam;
    Label hud, tip;

    public KitClickToMove Legs => legs;
    public KitCamera Camera => cam;

    /// <summary>a walker at a place (it steps onto the navmesh there once the level's has joined the map), with its
    /// camera; `legs`: a game's or a test's own (the kit's when null)</summary>
    public static KitWalker Spawn(Transform3D at, KitClickToMove legs = null)
    {
        var tree = (SceneTree)Engine.GetMainLoop();
        var w = new KitWalker { Name = "KitWalker", legs = legs, Transform = new Transform3D(at.Basis.Orthonormalized(), at.Origin) };
        tree.Root.AddChild(w);                                          // (placed before: its camera starts on it)
        return w;
    }

    public override void _Ready()
    {
        if (KitTravel.HasWalker && KitTravel.Walker != this) { QueueFree(); return; }   // a game's own player: step aside
        AddChild(new MeshInstance3D { Name = "Body", Mesh = new CapsuleMesh { Radius = 0.3f, Height = 1.8f }, Position = new Vector3(0, 0.9f, 0) });
        legs ??= new KitClickToMove();
        legs.Name = "Legs";
        AddChild(legs);
        cam = new KitCamera { Name = "KitCamera", Target = this };     // (top level: it does not move with the walker)
        AddChild(cam);
        legs.Cam = cam;
        var ui = new CanvasLayer();
        hud = new Label { Position = new Vector2(12, 10) };
        tip = new Label();
        ui.AddChild(hud);
        ui.AddChild(tip);
        AddChild(ui);
    }

    public override void _Process(double delta)
    {
        if (hud == null) return;
        hud.Text = $"{KitTravel.CurrentLevel}   (click or hold the left button to walk; click a door to go through; the wheel zooms)";
        var l = legs?.Hover;
        tip.Visible = l != null;
        if (l == null) return;
        tip.Position = GetViewport().GetMousePosition() + new Vector2(18, 4);
        tip.Text = $"{(string.IsNullOrEmpty(l.Prompt) ? "Go" : l.Prompt)}  -> {l.Target}";
    }
}
