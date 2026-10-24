using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>The demo's viewer (KitDemo), beside the level as a child of the tree's root so it outlives level changes:
/// on a world level the test walker (KitTravel takes it through doors and stairs), Blender's own cameras of the level
/// (Tab: the views the exporter's check renders), a free camera (F: hold the right mouse button to look, WASD to move),
/// back to the walker (C), back to the menu (Esc), the help line hidden (H).</summary>
public partial class KitDemoView : Node
{
    enum Mode { Walker, Cameras, Free }

    string level;
    bool walk;
    Mode mode;
    KitTestWalker walker;
    Camera3D free;
    int camIndex = -1;
    Label help;
    float yaw, pitch, speed = 6f;

    /// <summary>leave the menu for a level: walked (a world level) or only looked at</summary>
    public static void Open(string level, bool walk)
    {
        var tree = (SceneTree)Engine.GetMainLoop();
        foreach (var old in tree.Root.GetChildren().OfType<KitDemoView>()) old.QueueFree();
        tree.Root.AddChild(new KitDemoView { level = level, walk = walk, Name = "KitDemoView" });
    }

    public override void _Ready()
    {
        free = new Camera3D { Name = "KitDemo FreeCamera", Fov = 50f, Near = 0.05f, Far = 2000f };
        AddChild(free);
        var ui = new CanvasLayer { Layer = 10 };
        AddChild(ui);
        help = new Label { AnchorTop = 1, AnchorBottom = 1, OffsetLeft = 12, OffsetTop = -64, OffsetRight = 1400, OffsetBottom = -8 };
        help.AddThemeFontSizeOverride("font_size", 16);
        help.AddThemeColorOverride("font_outline_color", Colors.Black);
        help.AddThemeConstantOverride("outline_size", 6);
        ui.AddChild(help);
        if (walk)
        {
            walker = new KitTestWalker { Name = "KitTestWalker" };
            GetTree().Root.AddChild(walker);
            var world = ResourceLoader.Exists(KitPaths.World) ? GD.Load<KitWorld>(KitPaths.World) : null;
            KitTravel.Reload(level, world?.Find(level)?.Links.FirstOrDefault()?.Id ?? "");
            mode = Mode.Walker;
        }
        else
        {
            GetTree().ChangeSceneToFile(KitTravel.ScenePath(level));
            mode = Mode.Cameras;                        // its first camera once the level is in (_Process)
        }
    }

    public override void _ExitTree()
    {
        if (Input.MouseMode == Input.MouseModeEnum.Captured) Input.MouseMode = Input.MouseModeEnum.Visible;
    }

    Camera3D[] LevelCameras() =>
        GetTree().CurrentScene?.FindChildren("*", "Camera3D", true, false).OfType<Camera3D>()
            .OrderBy(c => (string)c.Name, System.StringComparer.Ordinal).ToArray() ?? System.Array.Empty<Camera3D>();

    void NextCamera(int step)
    {
        var cams = LevelCameras();
        if (cams.Length == 0) return;
        camIndex = ((camIndex + step) % cams.Length + cams.Length) % cams.Length;
        cams[camIndex].MakeCurrent();
        SetMode(Mode.Cameras);
    }

    void SetMode(Mode m)
    {
        mode = m;
        if (walker != null && IsInstanceValid(walker))
        {
            walker.Controls = m == Mode.Walker;
            if (m == Mode.Walker) walker.Camera?.MakeCurrent();
        }
        if (m != Mode.Free && Input.MouseMode == Input.MouseModeEnum.Captured) Input.MouseMode = Input.MouseModeEnum.Visible;
    }

    void FreeCamera()
    {
        var from = GetViewport().GetCamera3D();
        if (from != null && from != free)
        {
            free.GlobalTransform = from.GlobalTransform;
            var e = from.GlobalBasis.GetEuler();
            pitch = e.X; yaw = e.Y;
        }
        free.MakeCurrent();
        SetMode(Mode.Free);
    }

    void Back()
    {
        if (walker != null && IsInstanceValid(walker)) walker.QueueFree();
        GetTree().ChangeSceneToFile(KitDemo.Scene);
        QueueFree();
    }

    public override void _UnhandledInput(InputEvent e)
    {
        if (e is InputEventKey { Pressed: true, Echo: false } k)
        {
            switch (k.PhysicalKeycode)
            {
                case Key.Escape: Back(); break;
                case Key.Tab: NextCamera(k.ShiftPressed ? -1 : 1); break;
                case Key.F: FreeCamera(); break;
                case Key.C: if (walker != null) SetMode(Mode.Walker); break;
                case Key.H: help.Visible = !help.Visible; break;
                default: return;
            }
            GetViewport().SetInputAsHandled();
        }
        else if (mode == Mode.Free && e is InputEventMouseButton mb)
        {
            if (mb.ButtonIndex == MouseButton.Right)
                Input.MouseMode = mb.Pressed ? Input.MouseModeEnum.Captured : Input.MouseModeEnum.Visible;
            else if (mb.Pressed && mb.ButtonIndex == MouseButton.WheelUp) speed = Mathf.Min(speed * 1.25f, 200f);
            else if (mb.Pressed && mb.ButtonIndex == MouseButton.WheelDown) speed = Mathf.Max(speed / 1.25f, 0.5f);
        }
        else if (mode == Mode.Free && e is InputEventMouseMotion mm && Input.MouseMode == Input.MouseModeEnum.Captured)
        {
            yaw -= mm.Relative.X * 0.003f;
            pitch = Mathf.Clamp(pitch - mm.Relative.Y * 0.003f, -1.55f, 1.55f);
        }
    }

    public override void _Process(double delta)
    {
        if (mode == Mode.Cameras && camIndex < 0 && GetTree().CurrentScene is KitLevel) NextCamera(1);
        if (mode == Mode.Free)
        {
            free.GlobalBasis = Basis.FromEuler(new Vector3(pitch, yaw, 0f));
            var v = Vector3.Zero;
            if (Input.IsPhysicalKeyPressed(Key.W)) v -= free.GlobalBasis.Z;
            if (Input.IsPhysicalKeyPressed(Key.S)) v += free.GlobalBasis.Z;
            if (Input.IsPhysicalKeyPressed(Key.D)) v += free.GlobalBasis.X;
            if (Input.IsPhysicalKeyPressed(Key.A)) v -= free.GlobalBasis.X;
            if (Input.IsPhysicalKeyPressed(Key.E)) v += Vector3.Up;
            if (Input.IsPhysicalKeyPressed(Key.Q)) v -= Vector3.Up;
            float k = Input.IsPhysicalKeyPressed(Key.Shift) ? 4f : 1f;
            if (v != Vector3.Zero) free.GlobalPosition += v.Normalized() * speed * k * (float)delta;
        }
        string name = KitTravel.CurrentLevel ?? level;
        var cams = mode == Mode.Cameras ? LevelCameras() : null;
        string back = walker != null ? "  ·  C back to the walker" : "";
        help.Text = mode switch
        {
            Mode.Walker => "WASD / arrows walk  ·  E at a door or stair  ·  mouse wheel zoom  ·  Tab Blender's cameras  ·  F free camera  ·  Esc menu  ·  H hide",
            Mode.Cameras => $"{name}: Blender camera {camIndex + 1} of {cams?.Length}  ({(cams != null && camIndex >= 0 && camIndex < cams.Length ? cams[camIndex].Name : "")})" +
                            $"\nTab next  ·  Shift+Tab previous  ·  F free camera{back}  ·  Esc menu  ·  H hide",
            _ => $"{name}: free camera, speed {speed:0.#} m/s\nhold the right mouse button to look  ·  WASD move  ·  Q / E down / up  ·  Shift faster  ·  " +
                 $"mouse wheel speed  ·  Tab Blender's cameras{back}  ·  Esc menu  ·  H hide",
        };
    }
}
