#if TOOLS
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Godot;

namespace MedievalKit.Editor;

/// <summary>
/// The outdoor maps' rendering, shot in a window (FULL_PORT_PLAN phase 5): (a) a 40 x 40 m ground with the kit's terrain
/// material and a KitGrass written with KitGrass.Write (plain clumps, a tinted patch, the east half tall, the walker
/// parting it), from the game's camera and close up; (b) a sea plane with the sea material over a sloping bed, a quay
/// block and a fishing boat sitting low, shot with its water mask and without (the hull fills with water); (c)
/// VKI_Cave_Falls with and without a KitShroud. Logged to &lt;out&gt;/gfx.txt with shots. kit_cli: gfx &lt;out dir&gt;.
/// </summary>
public partial class KitGfxTest : Node
{
    string outDir = "";
    readonly System.Text.StringBuilder log = new();
    SubViewport vp;
    Camera3D cam;
    int fails;
    static readonly Vector2I Size = new(1600, 900);

    public void Setup(string outDirectory) => outDir = outDirectory;

    public override void _Ready() => Callable.From(() => { _ = Run(); }).CallDeferred();

    async Task Run()
    {
        try { await Steps(); }
        catch (Exception e) { Say($"FAIL exception {e}"); fails++; }
        KitSeeThrough.Set(Vector4.Zero, Vector4.Zero);
        Say(fails == 0 ? "ALL PASS" : $"{fails} FAILED");
        using (var f = FileAccess.Open($"{outDir}/gfx.txt", FileAccess.ModeFlags.Write)) f.StoreString(log.ToString());
        GetTree().Quit(fails == 0 ? 0 : 1);
    }

    void Say(string s) { log.AppendLine(s); GD.Print("[gfx] " + s); }
    void Check(bool ok, string what) { Say($"{(ok ? "ok  " : "FAIL")} {what}"); if (!ok) fails++; }
    async Task Wait(int n) { for (int i = 0; i < n; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame); }

    Image Shot(string name)
    {
        var img = vp.GetTexture().GetImage();
        img.SavePng($"{outDir}/gfx_{name}.png");
        Say($"shot gfx_{name}.png");
        return img;
    }

    /// <summary>the game's camera: `pitch` degrees down, looking north (-z; turned `yaw` degrees left), `dist` metres from
    /// `at`</summary>
    void Look(Vector3 at, float pitch, float dist, float fov = 30f, float yaw = 0f)
    {
        var basis = Basis.FromEuler(new Vector3(Mathf.DegToRad(-pitch), Mathf.DegToRad(yaw), 0));
        cam.Projection = Camera3D.ProjectionType.Perspective;
        cam.Fov = fov;
        cam.GlobalTransform = new Transform3D(basis, at + basis.Z * dist);
    }

    /// <summary>a sun, an ambient and a sky colour (the level scenes bring their own)</summary>
    static Node3D Daylight(Node3D root)
    {
        root.AddChild(new DirectionalLight3D { RotationDegrees = new Vector3(-50, 35, 0), LightEnergy = 1.3f, ShadowEnabled = true, DirectionalShadowMaxDistance = 80f });
        root.AddChild(new WorldEnvironment
        {
            Environment = new Godot.Environment
            {
                BackgroundMode = Godot.Environment.BGMode.Color, BackgroundColor = new Color(0.55f, 0.68f, 0.82f),
                AmbientLightSource = Godot.Environment.AmbientSource.Color, AmbientLightColor = new Color(0.55f, 0.6f, 0.68f),
                AmbientLightEnergy = 0.8f, TonemapMode = Godot.Environment.ToneMapper.Agx,
            },
        });
        return root;
    }

    /// <summary>a grid mesh (1 m cells) over x 0..w, z -d..0 with heights from `height`, vertex colour `color` (the
    /// terrain material reads AO, rock, rim and wet from it)</summary>
    static ArrayMesh Grid(float w, float d, Func<float, float, float> height, Color color)
    {
        var st = new SurfaceTool();
        st.Begin(Mesh.PrimitiveType.Triangles);
        int nx = Mathf.CeilToInt(w), nz = Mathf.CeilToInt(d);
        for (int j = 0; j < nz; j++)
            for (int i = 0; i < nx; i++)
            {
                Vector3 P(int a, int b) => new(a, height(a, -b), -b);
                var q = new[] { P(i, j), P(i + 1, j), P(i + 1, j + 1), P(i, j + 1) };
                foreach (int k in new[] { 0, 2, 1, 0, 3, 2 })      // clockwise from above (Godot's front)
                {
                    st.SetColor(color);
                    st.SetUV(new Vector2(q[k].X, q[k].Z));
                    st.AddVertex(q[k]);
                }
            }
        st.GenerateNormals();
        return st.Commit();
    }

    async Task Steps()
    {
        DisplayServer.WindowSetSize(Size);
        vp = new SubViewport { Size = Size, RenderTargetUpdateMode = SubViewport.UpdateMode.Always, OwnWorld3D = true, Msaa3D = Viewport.Msaa.Msaa2X };
        AddChild(vp);
        cam = new Camera3D { Far = 400f, Current = true };
        vp.AddChild(cam);
        await Grass();
        await Sea();
        await Shroud();
    }

    // ---- (a) the grass ----
    async Task Grass()
    {
        var root = Daylight(new Node3D { Name = "GrassTest" });
        vp.AddChild(root);
        var terrain = GD.Load<ShaderMaterial>("res://kit/materials/M_VK_Terrain.tres");
        var groundMat = (ShaderMaterial)terrain.Duplicate();
        var noCtl = Image.CreateEmpty(1, 1, false, Image.Format.Rgba8);   // all grass (no roads, no rock from the kit's control map)
        noCtl.Fill(new Color(0, 0, 0, 0));
        groundMat.SetShaderParameter("ctl_map", ImageTexture.CreateFromImage(noCtl));
        var ground = new MeshInstance3D { Name = "Ground", Mesh = Grid(40f, 40f, (x, z) => 0f, new Color(1f, 0f, 0f, 0f)), MaterialOverride = groundMat };
        root.AddChild(ground);

        // the clumps as the village writes them: a jittered 0.5 m grid, tall in the east half, a reddish patch, a strip bare
        var data = new List<byte>();
        var rnd = new Random(7);
        int n = 0;
        var walkerAt = new Vector3(12f, 0f, -12f);
        for (float z = -39.5f; z < -0.5f; z += 0.5f)
            for (float x = 0.5f; x < 39.5f; x += 0.5f)
            {
                var p = new Vector3(x + (float)rnd.NextDouble() * 0.5f, 0f, z + (float)rnd.NextDouble() * 0.5f);
                if (p.Z > -6f && p.Z < -4f) continue;                                         // a bare strip (a road)
                bool patch = new Vector2(p.X - 28f, p.Z + 26f).Length() < 5f;
                float shade = 0.94f + 0.12f * (float)rnd.NextDouble();
                var tint = patch ? new Color(1.35f, 0.8f, 0.45f) : new Color(shade, shade * 1.01f, shade * 0.97f);
                float tall = p.X > 20f ? 1f : 0.25f;
                KitGrass.Write(data, p, tint, tall);
                n++;
            }
        var grassMat = new ShaderMaterial { Shader = GD.Load<Shader>("res://addons/medieval_kit/Shaders/KitGrass.gdshader") };
        foreach (var t in new[] { "grass_map", "macro_map", "grass_sat" }) grassMat.SetShaderParameter(t, groundMat.GetShaderParameter(t));
        var grass = new KitGrass { Name = "Grass", material = grassMat, clumps = data.ToArray(), seed = 11, localBounds = new Aabb(new Vector3(0, 0, -40), new Vector3(40, 1, 40)) };
        root.AddChild(grass);
        int chunks = grass.GetChildCount(true) - grass.GetChildCount(false);
        Check(grass.Clumps == n && chunks >= 9, $"grass: {grass.Clumps} clumps ({data.Count / 1024} KB) in {chunks} chunks, up to {n * KitGrass.MaxBlades * 3} tris");

        // the walker (the see-through's position, the hole shut) parting the grass
        var walker = new MeshInstance3D { Mesh = new CapsuleMesh { Radius = 0.3f, Height = 1.8f }, Position = walkerAt + new Vector3(0, 0.9f, 0),
                                          MaterialOverride = new StandardMaterial3D { AlbedoColor = new Color(0.25f, 0.3f, 0.6f) } };
        root.AddChild(walker);
        KitSeeThrough.Set(new Vector4(walkerAt.X, 1f, walkerAt.Z, 0f), new Vector4(0f, 1.4f, 0.25f, 0.2f));

        await Wait(30);
        Look(new Vector3(20f, 0f, -20f), 50f, 40f, 40f);
        await Wait(10);
        var game = Shot("a1_grass_game");
        Look(walkerAt, 50f, 22f);
        await Wait(10);
        Shot("a2_grass_game_walker");
        Look(walkerAt + new Vector3(1.5f, 0.3f, 0f), 25f, 5f, 45f);
        await Wait(10);
        var pushed = Shot("a3_grass_close_walker");
        // the walker parts the grass: the same view with no walker (the wind held still for the two)
        grassMat.SetShaderParameter("wind_strength", 0f);
        await Wait(4);
        pushed = vp.GetTexture().GetImage();
        KitSeeThrough.Set(Vector4.Zero, Vector4.Zero);
        await Wait(4);
        var still = vp.GetTexture().GetImage();
        var foot = (Vector2I)cam.UnprojectPosition(walkerAt);
        int near = Changed(pushed, still, foot, 160), far = Changed(pushed, still, foot + new Vector2I(500, 200), 160);
        Check(near > 200 && far * 10 < near, $"the walker parts the grass: {near} pixels change round its feet when it goes, {far} away from it");
        KitSeeThrough.Set(new Vector4(walkerAt.X, 1f, walkerAt.Z, 0f), new Vector4(0f, 1.4f, 0.25f, 0.2f));
        grassMat.SetShaderParameter("wind_strength", 0.09f);
        Look(new Vector3(23f, 0.3f, -26f), 25f, 7f, 45f);
        await Wait(10);
        Shot("a4_grass_close_tall_tinted");

        // green and not the ground alone: the grass's pixels differ from the bare strip's
        float green = 0;
        for (int y = 0; y < game.GetHeight(); y += 8)
            for (int x = 0; x < game.GetWidth(); x += 8) { var c = game.GetPixel(x, y); green += c.G - Mathf.Max(c.R, c.B); }
        Check(green > 0, $"the grass reads green (mean g - max(r, b) {green / (game.GetHeight() / 8 * game.GetWidth() / 8):F3})");

        // shadows off: the chunks stop casting
        grass.castShadows = false;
        grass.Rebuild();
        Look(walkerAt + new Vector3(1.5f, 0.3f, 0f), 25f, 5f, 45f);
        await Wait(10);
        Shot("a5_grass_close_no_shadows");
        KitSeeThrough.Set(Vector4.Zero, Vector4.Zero);
        root.QueueFree();
        await Wait(3);
    }

    // ---- (b) the sea and a boat's water mask ----
    async Task Sea()
    {
        var root = Daylight(new Node3D { Name = "SeaTest" });
        vp.AddChild(root);
        // the bed: 1.5 m deep in the north, rising to a beach in the south (z > -8)
        float Bed(float x, float z) => Mathf.Lerp(-1.5f, 0.6f, Mathf.Clamp((z + 14f) / 12f, 0f, 1f)) + 0.08f * Mathf.Sin(x * 0.7f);
        var sand = new StandardMaterial3D { AlbedoColor = new Color(0.72f, 0.64f, 0.48f), Roughness = 0.95f };
        root.AddChild(new MeshInstance3D { Name = "Bed", Mesh = Grid(30f, 30f, Bed, Colors.White), MaterialOverride = sand });
        // a quay block standing in the water (foam round its foot)
        var stone = new StandardMaterial3D { AlbedoColor = new Color(0.5f, 0.5f, 0.52f), Roughness = 0.9f };
        root.AddChild(new MeshInstance3D { Name = "Quay", Mesh = new BoxMesh { Size = new Vector3(4f, 3f, 10f) }, Position = new Vector3(3f, -0.3f, -22f), MaterialOverride = stone });
        // the water at y 0
        var sea = new MeshInstance3D { Name = "Sea", Mesh = new PlaneMesh { Size = new Vector2(30f, 30f), CenterOffset = new Vector3(15f, 0f, -15f) },
                                       MaterialOverride = GD.Load<Material>("res://addons/medieval_kit/Materials/KitSea.tres"), CastShadow = GeometryInstance3D.ShadowCastingSetting.Off };
        root.AddChild(sea);

        // the boat, sitting low (the water 0.55 m over its keel)
        var piece = GD.Load<PackedScene>("res://kit/models/VK/Boat/SM_VK_Boat_Fishing.glb").Instantiate<Node3D>();
        piece.Name = "Boat";
        root.AddChild(piece);
        var boatAt = new Vector3(16f, 0f, -20f);
        piece.Position = boatAt;
        await Wait(2);
        var box = Bounds(piece);
        piece.Position = boatAt + new Vector3(0f, -(box.Position.Y - boatAt.Y) - 0.55f, 0f);
        await Wait(2);
        box = Bounds(piece);
        Say($"boat bounds {box}");
        var mask = WaterMask(piece, 0f);
        Check(mask != null, $"the boat crosses the water: a mask of {(mask?.GetSurfaceCount() > 0 ? mask.SurfaceGetArrayLen(0) : 0)} vertices");
        var maskNode = new MeshInstance3D { Name = "SeaMask", Mesh = mask, MaterialOverride = GD.Load<Material>("res://addons/medieval_kit/Materials/KitWaterMask.tres"),
                                            CastShadow = GeometryInstance3D.ShadowCastingSetting.Off };
        root.AddChild(maskNode);

        await Wait(30);
        Look(new Vector3(15f, 0f, -16f), 50f, 34f, 40f);
        await Wait(10);
        Shot("b1_sea_game");
        var at = box.GetCenter() with { Y = 0f };
        Look(at, 50f, 12f);
        await Wait(10);
        var with = Shot("b2_boat_mask");
        maskNode.Visible = false;
        await Wait(6);
        var without = Shot("b3_boat_no_mask");
        maskNode.Visible = true;
        Look(at + new Vector3(0f, 0f, 2f), 22f, 9f, 45f);
        await Wait(10);
        Shot("b4_boat_close");
        Look(new Vector3(15f, 0f, -18f), 40f, 14f, 50f, 180f + 35f);       // toward the sun: the glint
        await Wait(10);
        Shot("b5_sea_toward_sun");
        // the mask keeps the water out of the hull: the middle of the boat changes when it goes
        var mid = (Vector2I)cam.UnprojectPosition(at);
        Look(at, 50f, 12f);
        await Wait(4);
        mid = (Vector2I)cam.UnprojectPosition(at);
        float diff = 0; int count = 0;
        for (int y = mid.Y - 40; y <= mid.Y + 40; y += 4)
            for (int x = mid.X - 40; x <= mid.X + 40; x += 4)
            {
                if (x < 0 || y < 0 || x >= with.GetWidth() || y >= with.GetHeight()) continue;
                var a = with.GetPixel(x, y); var b = without.GetPixel(x, y);
                diff += Mathf.Abs(a.R - b.R) + Mathf.Abs(a.G - b.G) + Mathf.Abs(a.B - b.B); count++;
            }
        Check(count > 0 && diff / count > 0.05f, $"the water mask changes the hull's inside (mean colour difference {(count > 0 ? diff / count : 0):F3})");
        root.QueueFree();
        await Wait(3);
    }

    /// <summary>pixels that differ between two shots in a box round `at` (half-size r)</summary>
    static int Changed(Image a, Image b, Vector2I at, int r)
    {
        int n = 0;
        for (int y = Math.Max(0, at.Y - r); y < Math.Min(a.GetHeight(), at.Y + r); y += 2)
            for (int x = Math.Max(0, at.X - r); x < Math.Min(a.GetWidth(), at.X + r); x += 2)
            {
                Color p = a.GetPixel(x, y), q = b.GetPixel(x, y);
                if (Mathf.Abs(p.R - q.R) + Mathf.Abs(p.G - q.G) + Mathf.Abs(p.B - q.B) > 0.06f) n++;
            }
        return n;
    }

    static Aabb Bounds(Node3D root)
    {
        Aabb box = new(); bool first = true;
        foreach (var mi in KitNodes.Below(root, "MeshInstance3D").OfType<MeshInstance3D>())
        {
            var b = mi.GlobalTransform * mi.GetAabb();
            box = first ? b : box.Merge(b);
            first = false;
        }
        return box;
    }

    /// <summary>a hull's waterline footprint (the village's SeaMasks): where its meshes cross the water plane, the convex
    /// outline of those points fanned at the water's height (world space; null if it does not cross)</summary>
    static ArrayMesh WaterMask(Node3D hull, float wy)
    {
        var pts = new List<Vector2>();
        foreach (var mi in KitNodes.Below(hull, "MeshInstance3D").OfType<MeshInstance3D>())
        {
            if (mi.Mesh == null) continue;
            var t = mi.GlobalTransform;
            for (int s = 0; s < mi.Mesh.GetSurfaceCount(); s++)
            {
                using var arrays = mi.Mesh.SurfaceGetArrays(s);
                var v = arrays[(int)Mesh.ArrayType.Vertex].AsVector3Array().Select(p => t * p).ToArray();
                var idx = arrays[(int)Mesh.ArrayType.Index].AsInt32Array();
                if (idx == null || idx.Length == 0) idx = Enumerable.Range(0, v.Length).ToArray();
                for (int k = 0; k + 2 < idx.Length; k += 3)
                    for (int e = 0; e < 3; e++)
                    {
                        Vector3 a = v[idx[k + e]], b = v[idx[k + (e + 1) % 3]];
                        float da = a.Y - wy, db = b.Y - wy;
                        if ((da < 0f) == (db < 0f)) continue;
                        var p = a.Lerp(b, da / (da - db));
                        pts.Add(new Vector2(p.X, p.Z));
                    }
            }
        }
        var hullPts = Convex(pts);
        if (hullPts.Count < 3) return null;
        var c = hullPts.Aggregate(Vector2.Zero, (s, p) => s + p) / hullPts.Count;
        var verts = new List<Vector3>();
        for (int k = 0; k < hullPts.Count; k++)
        {
            var a = hullPts[k]; var b = hullPts[(k + 1) % hullPts.Count];
            verts.Add(new Vector3(c.X, wy, c.Y)); verts.Add(new Vector3(a.X, wy, a.Y)); verts.Add(new Vector3(b.X, wy, b.Y));
        }
        var arr = new Godot.Collections.Array();
        arr.Resize((int)Mesh.ArrayType.Max);
        arr[(int)Mesh.ArrayType.Vertex] = verts.ToArray();
        var m = new ArrayMesh();
        m.AddSurfaceFromArrays(Mesh.PrimitiveType.Triangles, arr);
        arr.Dispose();
        return m;
    }

    /// <summary>the convex hull of plan points (Andrew's monotone chain)</summary>
    static List<Vector2> Convex(List<Vector2> pts)
    {
        var p = pts.Distinct().OrderBy(q => q.X).ThenBy(q => q.Y).ToList();
        if (p.Count < 3) return p;
        static float Cross(Vector2 o, Vector2 a, Vector2 b) => (a.X - o.X) * (b.Y - o.Y) - (a.Y - o.Y) * (b.X - o.X);
        var h = new List<Vector2>();
        foreach (var q in p) { while (h.Count >= 2 && Cross(h[^2], h[^1], q) <= 0) h.RemoveAt(h.Count - 1); h.Add(q); }
        int lower = h.Count + 1;
        for (int i = p.Count - 2; i >= 0; i--) { var q = p[i]; while (h.Count >= lower && Cross(h[^2], h[^1], q) <= 0) h.RemoveAt(h.Count - 1); h.Add(q); }
        h.RemoveAt(h.Count - 1);
        return h;
    }

    // ---- (c) the shroud ----
    async Task Shroud()
    {
        var level = GD.Load<PackedScene>("res://kit/layouts/VKI_Cave_Falls.tscn").Instantiate<Node3D>();
        vp.AddChild(level);
        await Wait(10);
        cam.MakeCurrent();                                   // (the level brings its Blender camera)
        var box = Bounds(level);
        var c = box.GetCenter();
        Say($"cave bounds {box}");
        float aspect = Size.X / (float)Size.Y;
        cam.Projection = Camera3D.ProjectionType.Orthogonal;
        cam.Size = Mathf.Max(box.Size.Z, box.Size.X / aspect) * 1.05f;
        cam.GlobalTransform = new Transform3D(Basis.FromEuler(new Vector3(-Mathf.Pi / 2, 0, 0)), new Vector3(c.X, box.End.Y + 50f, c.Z));
        await Wait(20);
        var offTop = Shot("c1_cave_top_no_shroud");
        var spawn = KitNodes.Below(level, "").OfType<KitSpawn>().FirstOrDefault();
        var at = spawn?.GlobalPosition ?? c;
        Look(at, 50f, 22f);
        await Wait(10);
        Shot("c2_cave_game_no_shroud");

        var shroud = new KitShroud { Name = "Shroud" };
        level.AddChild(shroud);
        shroud.Build();
        Check(KitShroud.Active == shroud && shroud.Field != null, $"the shroud is on: a field of {shroud.Field?.GetWidth()} x {shroud.Field?.GetHeight()} cells from the cave's navmesh, floor at {shroud.FloorY:F2}");
        shroud.Field?.GetImage().SavePng($"{outDir}/gfx_c_shroud_field.png");
        await Wait(10);
        Shot("c3_cave_game_shroud");
        cam.Projection = Camera3D.ProjectionType.Orthogonal;
        cam.GlobalTransform = new Transform3D(Basis.FromEuler(new Vector3(-Mathf.Pi / 2, 0, 0)), new Vector3(c.X, box.End.Y + 50f, c.Z));
        await Wait(10);
        var onTop = Shot("c4_cave_top_shroud");
        float before = Mean(offTop), after = Mean(onTop);
        Check(after < before * 0.85f, $"the shroud darkens the cave from above (mean {before:F3} -> {after:F3})");

        level.RemoveChild(shroud);
        Check(KitShroud.Active == null, "off when it leaves the tree");
        await Wait(10);
        var offAgain = Shot("c5_cave_top_shroud_removed");
        Check(Mathf.Abs(Mean(offAgain) - before) < 0.02f, $"back as before (mean {Mean(offAgain):F3})");
        shroud.Free();
        level.QueueFree();
        await Wait(3);
    }

    static float Mean(Image img)
    {
        float s = 0; int n = 0;
        for (int y = 0; y < img.GetHeight(); y += 6)
            for (int x = 0; x < img.GetWidth(); x += 6) { var c = img.GetPixel(x, y); s += (c.R + c.G + c.B) / 3f; n++; }
        return s / n;
    }
}
#endif
