#if TOOLS
using System.Linq;
using System.Threading.Tasks;
using Godot;

namespace MedievalKit.Editor;

/// <summary>A look at any scene (a generated room, a chain's piece, the house showcase): rendered top-down (north up,
/// orthographic over its meshes) and from the game's camera (50 degrees, looking north), with the scene's own light
/// or, without one, a sun. A room generated in code: build it, save it as a scene, shoot it. Needs a window.
/// `near`: a node's name (a marker, a piece) or a plan point "x,y" and a radius in metres (default 15): both views close round that node.
/// kit_cli: shot &lt;scene.tscn&gt; &lt;out prefix&gt; [WxH] [node [radius]]. Unity: LEVEL_BUILDING 6.4's render.</summary>
public partial class KitShot : Node
{
    string scenePath = "", outPrefix = "";
    Vector2I size = new(1600, 1000);
    string near = "";
    float radius = 15f;

    public void Setup(string scene, string prefix, string res, string nearNode = "", string nearRadius = "")
    {
        scenePath = scene; outPrefix = prefix; near = nearNode ?? "";
        if (float.TryParse(nearRadius, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var r)) radius = r;
        if (!string.IsNullOrEmpty(res) && res.Contains('x')) size = new Vector2I(int.Parse(res.Split('x')[0]), int.Parse(res.Split('x')[1]));
    }

    public override void _Ready() => Callable.From(() => { _ = Run(); }).CallDeferred();

    async Task Frames(int n) { for (int i = 0; i < n; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame); }

    async Task Run()
    {
        var vp = new SubViewport { Size = size, RenderTargetUpdateMode = SubViewport.UpdateMode.Always, OwnWorld3D = true };
        AddChild(vp);
        var scene = GD.Load<PackedScene>(scenePath).Instantiate<Node3D>();
        vp.AddChild(scene);
        if (!KitNodes.Below(scene, "DirectionalLight3D").Any())
            vp.AddChild(new DirectionalLight3D { RotationDegrees = new Vector3(-55, 30, 0), LightEnergy = 1.2f, ShadowEnabled = true });
        if (!KitNodes.Below(scene, "WorldEnvironment").Any())
            vp.AddChild(new WorldEnvironment { Environment = new Godot.Environment { BackgroundMode = Godot.Environment.BGMode.Color, BackgroundColor = new Color(0.08f, 0.08f, 0.1f), AmbientLightSource = Godot.Environment.AmbientSource.Color, AmbientLightColor = new Color(0.45f, 0.45f, 0.5f), TonemapMode = Godot.Environment.ToneMapper.Agx } });
        await Frames(3);
        var box = new Aabb();
        bool first = true;
        foreach (var mi in KitNodes.Below(scene, "MeshInstance3D").OfType<MeshInstance3D>())
        {
            var b = mi.GlobalTransform * mi.GetAabb();
            box = first ? b : box.Merge(b);
            first = false;
        }
        if (near != "")
        {
            Vector3 p;
            var xy = near.Split(',');
            if (xy.Length == 2 && float.TryParse(xy[0], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float px)
                && float.TryParse(xy[1], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float py))
                p = scene.GlobalTransform * new Vector3(px, box.GetCenter().Y, -py);      // a plan point (x east, y north)
            else
            {
                var n = KitNodes.Below(scene, "").OfType<Node3D>().FirstOrDefault(x => x.Name == near);
                if (n == null) { GD.PushError($"shot: no node {near}"); GetTree().Quit(1); return; }
                p = n.GlobalPosition;
            }
            box = new Aabb(p - new Vector3(radius, 2f, radius), new Vector3(2 * radius, 4f, 2 * radius));
        }
        var c = box.GetCenter();
        float aspect = size.X / (float)size.Y;
        var cam = new Camera3D { Projection = Camera3D.ProjectionType.Orthogonal, Size = Mathf.Max(box.Size.Z, box.Size.X / aspect) * 1.05f, Far = 500 };
        vp.AddChild(cam);
        cam.GlobalTransform = new Transform3D(Basis.FromEuler(new Vector3(-Mathf.Pi / 2, 0, 0)), new Vector3(c.X, box.End.Y + 50, c.Z));
        cam.Current = true;
        await Frames(4);
        vp.GetTexture().GetImage().SavePng(outPrefix + "_top.png");
        // the game's camera: 50 degrees down, looking north (-z), backed off to see the whole thing
        float dist = Mathf.Max(box.Size.X / aspect, box.Size.Z) * 1.1f + 6f;
        cam.Projection = Camera3D.ProjectionType.Perspective;
        cam.Fov = 40;
        var basis = Basis.FromEuler(new Vector3(Mathf.DegToRad(-50), 0, 0));
        cam.GlobalTransform = new Transform3D(basis, c + basis.Z * dist);
        await Frames(4);
        vp.GetTexture().GetImage().SavePng(outPrefix + "_game.png");
        GD.Print($"SHOT {scenePath} -> {outPrefix}_top.png, {outPrefix}_game.png ({box.Size})");
        GetTree().Quit();
    }
}
#endif
