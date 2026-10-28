using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>A stand-in player for trying levels and links: WASD / arrows to walk, E to take a link whose prompt shows,
/// a camera at the kit's 50-degree pitch. Lives outside the levels (a child of the tree's root), so it survives them.
/// Add it with KitTestWalker.Spawn(); a real game brings its own player and calls KitTravel. Unity: KitTestWalker.</summary>
[GlobalClass]
public partial class KitTestWalker : CharacterBody3D
{
    [Export] public float Speed = 4f;
    [Export] public float CamDistance = 22f;
    [Export] public float CamPitch = 50f;
    /// <summary>off: it stands still and ignores the keys (the demo's other cameras use them); its camera still follows</summary>
    public bool Controls = true;

    public Camera3D Camera => cam;

    Camera3D cam;
    Label hud;
    KitLink near;
    static KitTestWalker instance;

    /// <summary>a walker at the current level's spawn `spawn` (or its first one)</summary>
    public static KitTestWalker Spawn(string spawn = null)
    {
        var tree = (SceneTree)Engine.GetMainLoop();
        var w = new KitTestWalker { Name = "KitTestWalker" };
        tree.Root.AddChild(w);
        var scene = tree.CurrentScene;
        var at = KitNodes.Below(scene, "").OfType<KitSpawn>()
            .FirstOrDefault(s => spawn == null || s.SpawnId == spawn);
        if (at != null) KitTravel.Place(w, at.GlobalTransform);
        return w;
    }

    public override void _Ready()
    {
        // another stand-in, or a game's own player registered with KitTravel: step aside
        if ((instance != null && IsInstanceValid(instance) && instance != this) || (KitTravel.HasWalker && KitTravel.Walker != this))
        {
            QueueFree();
            return;
        }
        instance = this;
        AddToGroup("player");
        CollisionMask = KitPiece.Solid | KitPiece.Passable;
        KitTravel.SetWalker(this);
        AddChild(new CollisionShape3D { Shape = new CapsuleShape3D { Radius = 0.3f, Height = 1.8f }, Position = new Vector3(0, 0.9f, 0) });
        AddChild(new MeshInstance3D { Mesh = new CapsuleMesh { Radius = 0.3f, Height = 1.8f }, Position = new Vector3(0, 0.9f, 0) });
        cam = new Camera3D { Name = "KitTestWalker Camera", Fov = 28f, Near = 0.3f, Far = 400f, TopLevel = true };
        AddChild(cam);
        var ui = new CanvasLayer();
        hud = new Label { Position = new Vector2(12, 10) };
        ui.AddChild(hud);
        AddChild(ui);
        KitTravel.Arrived += OnArrived;
        OnArrived(KitTravel.CurrentLevel, null);
    }

    public override void _ExitTree() => KitTravel.Arrived -= OnArrived;

    public override void _UnhandledInput(InputEvent e)
    {
        // the mouse wheel zooms the camera in and out
        if (!Controls || e is not InputEventMouseButton { Pressed: true } mb) return;
        if (mb.ButtonIndex == MouseButton.WheelUp) CamDistance = Mathf.Max(CamDistance * 0.9f, 4f);
        else if (mb.ButtonIndex == MouseButton.WheelDown) CamDistance = Mathf.Min(CamDistance * 1.1f, 80f);
    }

    void OnArrived(string level, KitSpawn spawn)
    {
        cam.MakeCurrent();
        if (GetTree().CurrentScene is KitLevel l) CamDistance = l.Props.GetFloat("vki_cam_dist", CamDistance);
    }

    public override void _PhysicsProcess(double delta)
    {
        Vector2 mv = Vector2.Zero;
        if (Controls)
        {
            if (Input.IsPhysicalKeyPressed(Key.W) || Input.IsPhysicalKeyPressed(Key.Up)) mv.Y += 1;
            if (Input.IsPhysicalKeyPressed(Key.S) || Input.IsPhysicalKeyPressed(Key.Down)) mv.Y -= 1;
            if (Input.IsPhysicalKeyPressed(Key.D) || Input.IsPhysicalKeyPressed(Key.Right)) mv.X += 1;
            if (Input.IsPhysicalKeyPressed(Key.A) || Input.IsPhysicalKeyPressed(Key.Left)) mv.X -= 1;
        }
        // the kit's camera looks along Godot -Z (Blender +Y): screen up = -Z, screen right = +X
        var dir = new Vector3(mv.X, 0f, -mv.Y);
        float dt = (float)delta;
        if (dir.LengthSquared() > 0.01f)
        {
            dir = dir.Normalized();
            var want = Basis.LookingAt(dir, Vector3.Up);
            Basis = Basis.Slerp(want, Mathf.Min(12f * dt, 1f)).Orthonormalized();
            Velocity = dir * Speed;
            MoveAndSlide();
        }
        // stick to the ground (kit floors and terrain have colliders; no gravity drift where there are none)
        var space = GetWorld3D().DirectSpaceState;
        var ex = new Godot.Collections.Array<Rid> { GetRid() };
        using (var exNative = (Godot.Collections.Array)ex)                  // (Godot arrays disposed: see KitClickToMove.Cast)
        using (var rq = new PhysicsRayQueryParameters3D { From = GlobalPosition + Vector3.Up * 1.5f, To = GlobalPosition + Vector3.Down * 2.5f, CollideWithAreas = false, Exclude = ex })
        using (var hit = space.IntersectRay(rq))
            if (hit.Count > 0) GlobalPosition = new Vector3(GlobalPosition.X, ((Vector3)hit["position"]).Y, GlobalPosition.Z);
        // links within reach
        near = null;
        var q = new PhysicsShapeQueryParameters3D
        {
            Shape = new SphereShape3D { Radius = 0.6f }, Transform = new Transform3D(Basis.Identity, GlobalPosition + Vector3.Up),
            CollideWithAreas = true, CollideWithBodies = false,
        };
        var found = space.IntersectShape(q, 8);
        using (var foundNative = (Godot.Collections.Array)found)
            foreach (var r in found)
                using (r)
                    if (near == null && r["collider"].AsGodotObject() is KitLink l && l.CanUse(this)) near = l;
        if (Controls && near != null && Input.IsPhysicalKeyPressed(Key.E) && !KitTravel.Travelling) near.Use();
        float p = Mathf.DegToRad(CamPitch);
        cam.GlobalPosition = GlobalPosition + new Vector3(0f, Mathf.Sin(p), Mathf.Cos(p)) * CamDistance;
        cam.LookAt(GlobalPosition + Vector3.Up, Vector3.Up);
        hud.Text = $"{KitTravel.CurrentLevel}   (WASD walk, E use)" + (near != null ? $"\n[E] {near.Prompt}  -> {near.Target}" : "");
    }
}
