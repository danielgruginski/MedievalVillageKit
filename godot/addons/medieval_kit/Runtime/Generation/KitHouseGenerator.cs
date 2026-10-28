using System;
using System.Collections.Generic;
using System.Linq;
using Godot;
using Mathf = MedievalKit.UnityMath.Mathf;
using Vector2 = MedievalKit.UnityMath.Vector2;

namespace MedievalKit;

/// <summary>
/// Builds a village house from kit pieces under this node: the rules of the Blender kit's vk_helpers.build_house_v /
/// _assemble / _dress / random_style, on a footprint of `cells` x 2 cells. Same rules, not the same random sequence: a
/// seed gives a stable house here, the Unity kit's house of that seed, not Blender's. In the editor: Generate / Reroll /
/// Clear in the inspector; kit_cli houses makes a set. Blender house space (x along the front, y back, z up) is this
/// node's (x, z, -y). The fields keep the Unity kit's names. Unity: KitHouseGenerator.
/// </summary>
[GlobalClass, Tool]
public partial class KitHouseGenerator : Node3D
{
    public enum Shape { Rectangle, L }

    /// <summary>the rules (null: the kit's own, <see cref="KitHouseRules.Default"/>)</summary>
    [Export] public KitHouseRules rules;
    /// <summary>Rectangle: cells x 2 (build_house_v). L: a 2 x 2 corner block with an arm along the front and a wing to
    /// the back (build_L_v; tile roofs only, thatch becomes red tiles).</summary>
    [Export] public Shape shape = Shape.Rectangle;
    [Export(PropertyHint.Range, "1,6")] public int cells = 3;
    /// <summary>L: cells the front arm runs past the corner block</summary>
    [Export(PropertyHint.Range, "1,4")] public int armCells = 1;
    /// <summary>L: cells the wing runs back from the corner block</summary>
    [Export(PropertyHint.Range, "1,4")] public int wingCells = 1;
    [Export(PropertyHint.Range, "1,3")] public int stories = 2;
    [Export] public int seed = 1;

    [ExportGroup("Style")]
    /// <summary>pick ground, plaster, shutters and roof from the rules' random-style table (by seed)</summary>
    [Export] public bool randomStyle = true;
    [Export] public string ground = "Stone";
    [Export] public string plaster = "Cream";
    [Export] public string shutter = "Teal";
    [Export] public string roof = "Red";

    [ExportGroup("Layout (empty = random)")]
    /// <summary>front wall bays, one per cell: D door, W window, . plain. A door is added if none is given.</summary>
    [Export] public string front = "";
    /// <summary>back wall bays, one per cell (left to right seen from the back)</summary>
    [Export] public string back = "";
    [Export] public bool chimney = true;
    [Export] public bool dormers = true;
    [Export] public bool dressing = true;

    [ExportToolButton("Generate")] public Callable GenerateButton => Callable.From(Generate);
    [ExportToolButton("Reroll")] public Callable RerollButton => Callable.From(() => { seed = (int)(GD.Randi() % 99999) + 1; Generate(); });
    [ExportToolButton("Clear")] public Callable ClearButton => Callable.From(Clear);

    /// <summary>how pieces are made (a game may pool them); the generator places and parents them</summary>
    public static Func<PackedScene, Node3D> Spawn = ps => ps.Instantiate<Node3D>();

    /// <summary>the style the last Generate used (after random picks)</summary>
    public Dictionary<string, string> LastStyle { get; private set; } = new();
    public int LastPieceCount { get; private set; }

    System.Random rng;
    Dictionary<string, string> style;
    KitHouseRules R => rules ?? KitHouseRules.Default;
    Node SceneOwner => Owner ?? this;

    public void Clear()
    {
        foreach (var c in KitNodes.Children(this).ToList())
        {
            RemoveChild(c);
            c.QueueFree();
        }
    }

    public void Generate()
    {
        R.Load();
        Clear();
        LastPieceCount = 0;
        style = PickStyle();
        if (shape == Shape.L && style["roof"] == "Thatch") style["roof"] = "Red";    // no thatch L-roof
        LastStyle = new Dictionary<string, string>(style);
        rng = new System.Random(seed);
        groundSet = R.Ground(style["ground"]);
        if (groundSet == null) { GD.PushError("[KitHouseGenerator] rules have no ground sets"); return; }
        if (shape == Shape.L) BuildL(); else BuildRect();
    }

    KitHouseRules.GroundSet groundSet;

    // build_house_v: a row of `cells` bays, two cells deep, centred on this node
    void BuildRect()
    {
        int n = Mathf.Clamp(cells, 1, 6);
        float C = R.cell, L = n * C, D = R.depth;
        string fr = Pattern(front, n, "WW.");
        if (fr.IndexOf('D') < 0) { int i = rng.Next(n); fr = fr.Substring(0, i) + "D" + fr.Substring(i + 1); }
        string bk = Pattern(back, n, "W..");
        char[] bkRev = bk.ToCharArray(); Array.Reverse(bkRev);

        // walls: Blender house space (x along the front, y back, z up), rotation about z in degrees
        var walls = new List<(float x, float y, float rot, char c)>();
        for (int i = 0; i < n; i++) walls.Add((-L / 2 + C / 2 + C * i, -D / 2, 0, fr[i]));
        for (int i = 0; i < n; i++) walls.Add((-L / 2 + C / 2 + C * i, D / 2, 180, bkRev[i]));
        walls.Add((-L / 2, -C / 2, -90, Pick("W.")));
        walls.Add((-L / 2, C / 2, -90, '.'));
        walls.Add((L / 2, C / 2, 90, Pick("W.")));
        walls.Add((L / 2, -C / 2, 90, '.'));
        var corners = new List<(float, float, float)> { (-L / 2, -D / 2, 0f), (L / 2, -D / 2, 90f), (L / 2, D / 2, 180f), (-L / 2, D / 2, -90f) };
        Assemble(walls, corners);

        // roof: gable or hip ends (hips likelier on thatch), mid pieces between
        float top = Top();
        bool thatch = style["roof"] == "Thatch";
        var rs = thatch ? R.thatchRoof : R.tileRoof;
        float hipP = thatch ? 0.55f : 0.3f;
        bool[] ends = { rng.NextDouble() < hipP, rng.NextDouble() < hipP };
        for (int i = 0; i < n; i++)
        {
            float x = -L / 2 + C / 2 + C * i;
            bool isEnd = i == 0 || i == n - 1;
            bool hip = isEnd && ends[i == 0 ? 0 : 1];
            var pc = isEnd ? (hip ? rs.hip : rs.gable) : rs.mid;
            Place(pc, x, 0, top, i == 0 ? 180 : 0, true);
        }
        int ci = rng.Next(n);
        float crot = rng.Next(2) == 0 ? 0 : 180;
        if (chimney) Place(Choose(R.chimney), -L / 2 + C / 2 + C * ci, 0, top, crot, true);
        if (dormers && !thatch && (stories == 1 || rng.NextDouble() < 0.6))
            for (int i = 0; i < n; i++)
            {
                if (i == ci && chimney) continue;
                if ((i == 0 && ends[0]) || (i == n - 1 && ends[1])) continue;
                if (rng.NextDouble() < (stories == 1 ? 0.55 : 0.35))
                    Place(Choose(R.dormer), -L / 2 + C / 2 + C * i, 0, top, 0, true);
            }
    }

    // build_L_v: a 2 x 2 corner block at this node, `armCells` more along the front (+x), a wing of `wingCells` to the
    // back (+y); the concave corner at (C, C)
    void BuildL()
    {
        int a = Mathf.Clamp(armCells, 1, 4), b = Mathf.Clamp(wingCells, 1, 4);
        float C = R.cell, XA = C + C * a, YB = C + C * b;
        string fa = Pattern(front, 2 + a, "WW.");
        if (string.IsNullOrEmpty(front)) fa = fa.Substring(0, 1) + "D" + fa.Substring(2);
        var walls = new List<(float x, float y, float rot, char c)>();
        for (int i = 0; i < 2 + a; i++) walls.Add((-C / 2 + C * i, -C, 0, fa[i]));
        for (int j = 0; j < 2 + b; j++) walls.Add((-C, -C / 2 + C * j, -90, Pick("W.")));
        walls.Add((XA, -C / 2, 90, Pick("W.")));
        walls.Add((XA, C / 2, 90, '.'));
        for (int i = 0; i < a; i++) walls.Add((1.5f * C + C * i, C, 180, Pick("W.")));
        walls.Add((-C / 2, YB, 180, '.'));
        walls.Add((C / 2, YB, 180, Pick("W.")));
        for (int j = 0; j < b; j++) walls.Add((C, 1.5f * C + C * j, 90, Pick("WD")));
        var corners = new List<(float, float, float)> { (-C, -C, 0f), (XA, -C, 90f), (XA, C, 180f), (C, YB, 180f), (-C, YB, -90f) };
        Assemble(walls, corners);
        Place(groundSet.innerCorner, C, C, 0, 0, true);
        for (int lvl = 1; lvl < stories; lvl++)
            Place(Choose(R.upperInnerCorner), C, C, R.h1 + R.h2 * (lvl - 1), 0, true);

        float top = Top();
        var rs = R.tileRoof;
        Place(rs.lcorner, 0, 0, top, 0, true);
        for (int i = 0; i < a; i++) Place(i == a - 1 ? rs.gable : rs.mid, 1.5f * C + C * i, 0, top, 0, true);
        for (int j = 0; j < b; j++) Place(j == b - 1 ? rs.gable : rs.mid, 0, 1.5f * C + C * j, top, 90, true);
        int ci = rng.Next(a);
        float crot = rng.Next(2) == 0 ? 0 : 180;
        if (chimney) Place(Choose(R.chimney), 1.5f * C + C * ci, 0, top, crot, true);
    }

    float Top() => R.h1 + R.h2 * (stories - 1);

    // _assemble: the ground storey and its dressing, then timber upper storeys (a window above every ground window or
    // door, else a 35 % chance)
    void Assemble(List<(float x, float y, float rot, char c)> walls, List<(float, float, float)> corners)
    {
        foreach (var w in walls)
        {
            var p = w.c == 'D' ? groundSet.wallDoor : w.c == 'W' ? groundSet.wallWindow : groundSet.wallPlain;
            Place(p, w.x, w.y, 0, w.rot, true);
            if (dressing) Dress(w.x, w.y, w.rot, w.c);
        }
        foreach (var c in corners) Place(groundSet.corner, c.Item1, c.Item2, 0, c.Item3, true);
        for (int lvl = 1; lvl < stories; lvl++)
        {
            float z = R.h1 + R.h2 * (lvl - 1);
            foreach (var w in walls)
            {
                bool win = "WDA".IndexOf(w.c) >= 0 || rng.NextDouble() < 0.35;
                Place(win ? Choose(R.upperWallWindow) : Choose(R.upperWallPlain), w.x, w.y, z, w.rot, true);
            }
            foreach (var c in corners) Place(Choose(R.upperCorner), c.Item1, c.Item2, z, c.Item3, true);
        }
    }

    // _dress: props in wall-local coordinates, turned with the wall
    void Dress(float x, float y, float rot, char c)
    {
        float a = rot * Mathf.Deg2Rad, ca = Mathf.Cos(a), sa = Mathf.Sin(a);
        Vector2 Loc(float lx, float ly) => new Vector2(x + lx * ca - ly * sa, y + lx * sa + ly * ca);
        bool stone = style["ground"] == "Stone";
        if (c == 'W' && rng.NextDouble() < 0.7)
        {
            var p = Loc(0, stone ? -0.55f : -0.5f);
            var fb = R.flowerBox.Count > 1 && rng.NextDouble() >= 0.6 ? R.flowerBox[1] : Choose0(R.flowerBox);
            Place(fb, p.x, p.y, stone ? 0.78f : 0.9f, rot, false);
        }
        if (rng.NextDouble() < 0.4) Place(Choose0(R.weeds), x, y, 0, rot, false);
        if (c == '.' && rng.NextDouble() < 0.22) Place(R.ivy.Count > 1 && rng.NextDouble() >= 0.5 ? R.ivy[1] : Choose0(R.ivy), x, y, 0, rot, false);
        if (c == 'D' && rng.NextDouble() < 0.5)
        {
            float[] sides = rng.NextDouble() < 0.5 ? new[] { -1.05f, 1.05f } : new[] { 1.05f };
            foreach (var sx in sides) { var p = Loc(sx, -0.75f); Place(Choose0(R.planter), p.x, p.y, 0, rot, false); }
        }
        if (c == 'D')
        {
            if (rng.NextDouble() < 0.45) Place(Choose0(R.porch), x, y, 0, rot, true);
            else { var p = Loc(1.0f, -0.3f); Place(Choose0(R.lantern), p.x, p.y, 2.55f, rot, false); }
        }
    }

    Dictionary<string, string> PickStyle()
    {
        var s = new Dictionary<string, string> { ["ground"] = ground, ["plaster"] = plaster, ["shutter"] = shutter, ["roof"] = roof };
        if (!randomStyle) return s;
        var r = new System.Random(seed * 7919 + 17);
        s["ground"] = r.NextDouble() < R.stoneGroundChance ? "Stone" : "Plaster";
        var roofs = new List<string>(R.roofChoices);
        for (int i = 0; i < (s["ground"] == "Plaster" ? R.thatchWeightPlaster : R.thatchWeightStone); i++) roofs.Add("Thatch");
        s["plaster"] = R.plasterChoices[r.Next(R.plasterChoices.Count)];
        string sh = R.shutterChoices[r.Next(R.shutterChoices.Count)];
        if (sh != "Natural" && r.NextDouble() < R.shutterWornChance) sh += "Worn";   // about 1 in 5 weathered
        s["shutter"] = sh;
        s["roof"] = roofs[r.Next(roofs.Count)];
        return s;
    }

    string Pattern(string given, int n, string choices)
    {
        if (!string.IsNullOrEmpty(given))
        {
            given = given.Length >= n ? given.Substring(0, n) : given.PadRight(n, '.');
            return given.ToUpperInvariant().Replace('w', 'W');
        }
        var a = new char[n];
        for (int i = 0; i < n; i++) a[i] = choices[rng.Next(choices.Length)];
        return new string(a);
    }

    char Pick(string choices) => choices[rng.Next(choices.Length)];
    PackedScene Choose(List<PackedScene> l) => l == null || l.Count == 0 ? null : l[rng.Next(l.Count)];
    static PackedScene Choose0(List<PackedScene> l) => l == null || l.Count == 0 ? null : l[0];

    /// <summary>Blender house space -> this node's local space: (x, y, z) -> (x, z, -y), a turn about z the same turn
    /// about y</summary>
    Node3D Place(PackedScene prefab, float x, float y, float z, float rotDeg, bool styled)
    {
        if (prefab == null) return null;
        var go = Spawn(prefab);
        AddChild(go, true);
        go.Owner = SceneOwner;
        go.Position = new Godot.Vector3(x, z, -y);
        go.Rotation = new Godot.Vector3(0f, rotDeg * Mathf.Deg2Rad, 0f);
        go.Scale = Godot.Vector3.One;
        if (styled) Restyle(go);
        LastPieceCount++;
        return go;
    }

    void Restyle(Node3D go)
    {
        var kp = go as KitPiece;
        var mr = kp?.MeshInstance;
        if (kp == null || mr?.Mesh == null || kp.BlenderSlots == null || kp.BlenderSlots.Length == 0) return;
        bool changed = false;
        foreach (var kv in style)
        {
            var kind = R.Kind(kv.Key);
            var opt = kind?.Find(kv.Value);
            if (opt == null || opt.material == null) continue;          // the piece's own material is that option
            for (int i = 0; i < mr.Mesh.GetSurfaceCount() && i < kp.BlenderSlots.Length; i++)
                if (kp.BlenderSlots[i] == kind.blenderSlot) { mr.SetSurfaceOverrideMaterial(i, opt.material); changed = true; }
        }
        if (changed && SceneOwner != go) SceneOwner.SetEditableInstance(go, true);
    }
}
