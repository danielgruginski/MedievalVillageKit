#if TOOLS
using System;
using System.Collections.Generic;
using System.Linq;
using Godot;

namespace MedievalKit.Editor;

/// <summary>Renders every camera of a built layout (res://kit/layouts/&lt;name&gt;.tscn) to &lt;out&gt;/godot_&lt;camera&gt;.png,
/// then again with the lights' Blender shadows on to &lt;out&gt;/godot_shadows_&lt;camera&gt;.png (or once as built), for side-by-side checks
/// with the Blender renders (gdx_export.gdx_render_cameras, tools/gdx_compare.py). Through a SubViewport of the given
/// size (MSAA 4x + TAA), so the window's size does not matter; needs a window (not --headless). Quits when done.
/// Unity: KitCapture.CaptureAll.</summary>
public partial class KitCapture : Node
{
    const int WarmFrames = 48;      // shader compiles, then TAA converging on a still image

    string layout = "Pilot", outDir = "";
    Vector2I size = new(1600, 900);
    SubViewport vp;
    List<Camera3D> cams;
    List<Light3D> lights;
    int i, frame;
    int drawnAtSwitch;
    bool shadowPass, asBuilt;

    /// <summary>Called before the node enters the tree. res: "WxH", or empty for the layout's own (its Blender scene's).
    /// asBuiltShadows: one pass with the shadows as the level was built (its Blender scene's: a world level's renders
    /// from gdx_export_world), saved as godot_&lt;camera&gt;.png.</summary>
    public void Setup(string layoutName, string outDirectory, string res, bool asBuiltShadows = false)
    {
        layout = layoutName;
        outDir = outDirectory;
        asBuilt = asBuiltShadows;
        if (string.IsNullOrEmpty(res))
        {
            var lay = System.Text.Json.JsonDocument.Parse(Godot.FileAccess.GetFileAsString(KitPaths.LayoutData + layout + ".json")).RootElement;
            var r = lay.GetProperty("resolution");
            size = new Vector2I(r[0].GetInt32(), r[1].GetInt32());
            return;
        }
        var p = res.Split('x');
        size = new Vector2I(int.Parse(p[0]), int.Parse(p[1]));
    }

    public override void _Ready()
    {
        if (outDir == "") outDir = ProjectSettings.GlobalizePath("res://pilot/shots");
        DirAccess.MakeDirRecursiveAbsolute(outDir);
        vp = new SubViewport
        {
            Size = size, OwnWorld3D = true, Msaa3D = Viewport.Msaa.Msaa4X, UseTaa = true,
            RenderTargetUpdateMode = SubViewport.UpdateMode.Always,
        };
        AddChild(vp);
        var scene = GD.Load<PackedScene>(KitPaths.LayoutScenes + layout + ".tscn").Instantiate();
        vp.AddChild(scene);
        cams = scene.FindChildren("*", "Camera3D", true, false).OfType<Camera3D>().OrderBy(c => (string)c.Name, StringComparer.Ordinal).ToList();
        lights = scene.FindChildren("*", "Light3D", true, false).OfType<Light3D>().ToList();
        if (!asBuilt) SetShadows(false);
        cams[0].Current = true;
    }

    void SetShadows(bool on)
    {
        shadowPass = on;
        foreach (var l in lights) l.ShadowEnabled = on && (bool)l.GetMeta("blender_shadow", false);
    }

    public override void _Process(double delta)
    {
        // count frames actually drawn: a minimized or hidden window keeps processing but stops drawing, and the
        // viewport then hands back its last image (a whole shadow pass came out as one camera's view)
        int drawn = Engine.GetFramesDrawn();
        if (++frame == 1) drawnAtSwitch = drawn;
        if (drawn - drawnAtSwitch < WarmFrames)
        {
            if (frame % 600 == 0) GD.PushWarning($"KitCapture: nothing drawn for {frame} frames (window minimized or hidden?)");
            return;
        }
        string tag = shadowPass ? "_shadows" : "";
        vp.GetTexture().GetImage().SavePng(System.IO.Path.Combine(outDir, $"godot{tag}_{cams[i].Name}.png"));
        frame = 0;
        if (++i >= cams.Count)
        {
            if (shadowPass || asBuilt)
            {
                GD.Print($"CAPTURE {cams.Count} cameras x {(asBuilt ? 1 : 2)} -> {outDir}");
                GetTree().Quit();
                return;
            }
            SetShadows(true);
            i = 0;
        }
        cams[i].Current = true;
    }
}
#endif
