using System;
using System.Linq;
using Godot;

namespace MedievalKit;

/// <summary>The kit's demo menu (Walker/kit_demo.tscn; the Godot project's main scene, so Play or the project's
/// "Play Medieval Kit demo.bat" opens it): every built level of res://kit/layouts. A world level is walked with the test
/// walker (its doors and stairs taken with E, as KitTravel does in a game); every layout can be looked at through
/// Blender's own cameras or a free camera (KitDemoView). Nothing here is needed by a game.</summary>
public partial class KitDemo : Control
{
    public const string Scene = KitPaths.Addon + "Walker/kit_demo.tscn";

    public override void _Ready()
    {
        SetAnchorsPreset(LayoutPreset.FullRect);
        AddChild(new ColorRect { Color = new Color(0.09f, 0.08f, 0.07f), AnchorRight = 1, AnchorBottom = 1 });
        var margin = new MarginContainer { AnchorRight = 1, AnchorBottom = 1 };
        foreach (var side in new[] { "left", "right", "top", "bottom" }) margin.AddThemeConstantOverride("margin_" + side, 32);
        AddChild(margin);
        var col = new VBoxContainer();
        col.AddThemeConstantOverride("separation", 10);
        margin.AddChild(col);
        col.AddChild(Text("Medieval Village Kit in Godot", 30));
        col.AddChild(Text("Pick a level. Walk: WASD or arrows, E at a door or stair, mouse wheel to zoom. " +
                          "Tab: Blender's camera views. F: free camera (hold the right mouse button to look). Esc: back here.", 16, true));
        var scroll = new ScrollContainer { SizeFlagsVertical = SizeFlags.ExpandFill };
        col.AddChild(scroll);
        var list = new VBoxContainer { SizeFlagsHorizontal = SizeFlags.ExpandFill };
        list.AddThemeConstantOverride("separation", 6);
        scroll.AddChild(list);

        var world = ResourceLoader.Exists(KitPaths.World) ? GD.Load<KitWorld>(KitPaths.World) : null;
        var built = DirAccess.DirExistsAbsolute(KitPaths.LayoutScenes)
            ? DirAccess.GetFilesAt(KitPaths.LayoutScenes).Where(f => f.EndsWith(".tscn")).Select(f => f[..^5]).ToHashSet()
            : new System.Collections.Generic.HashSet<string>();
        var levels = world?.Levels.Where(l => built.Contains(l.Name))
                          .OrderBy(l => l.Name == world.Start ? 0 : 1).ThenBy(l => l.Name, StringComparer.Ordinal).ToList()
                     ?? new System.Collections.Generic.List<KitWorldLevel>();
        list.AddChild(Text("Walk a level", 20));
        list.AddChild(Grid(levels.Select(l => (Label(l), (Action)(() => KitDemoView.Open(l.Name, true))))));
        var others = built.Where(n => levels.All(l => l.Name != n)).OrderBy(n => n, StringComparer.Ordinal).ToList();
        if (others.Count > 0)
        {
            list.AddChild(Text("Look around (Blender's cameras, free camera)", 20));
            list.AddChild(Grid(others.Select(n => (n.Replace('_', ' '), (Action)(() => KitDemoView.Open(n, false))))));
        }
        if (built.Count == 0)
            list.AddChild(Text("No levels are built yet: run sh tools/gdx_levels.sh in the kit repo (docs/GODOT_EXPORT.md).", 16, true));
    }

    static string Label(KitWorldLevel l)
    {
        string n = l.Name.Replace("VKI_", "").Replace("VK_", "").Replace('_', ' ');
        return l.Kind == "exterior" ? n + "  (outdoors)" : n;
    }

    static Label Text(string s, int size, bool wrap = false)
    {
        var t = new Label { Text = s, AutowrapMode = wrap ? TextServer.AutowrapMode.WordSmart : TextServer.AutowrapMode.Off };
        t.AddThemeFontSizeOverride("font_size", size);
        return t;
    }

    static GridContainer Grid(System.Collections.Generic.IEnumerable<(string label, Action go)> items)
    {
        var g = new GridContainer { Columns = 3, SizeFlagsHorizontal = SizeFlags.ExpandFill };
        g.AddThemeConstantOverride("h_separation", 8);
        g.AddThemeConstantOverride("v_separation", 8);
        foreach (var (label, go) in items)
        {
            var b = new Button { Text = label, CustomMinimumSize = new Vector2(320, 40), SizeFlagsHorizontal = SizeFlags.ExpandFill };
            b.AddThemeFontSizeOverride("font_size", 17);
            b.Pressed += go;
            g.AddChild(b);
        }
        return g;
    }
}
