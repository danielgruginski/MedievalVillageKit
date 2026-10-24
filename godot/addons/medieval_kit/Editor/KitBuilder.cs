#if TOOLS
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using Godot;

namespace MedievalKit.Editor;

/// <summary>Builds res://kit/layouts/&lt;name&gt;.tscn from res://kit/data/layouts/&lt;name&gt;.json (gdx_export_layout): the kit
/// pieces as instances of their .glb (restyles: surface_material_override/N on the instance), the roof jitter's
/// object_random per placement, Blender's lights, cameras, world and view transform. And checks the imported pieces
/// against res://kit/data/pieces.json (CheckPieces). Unity's KitBuilder does the same from the package's Data/.
///
/// Blender -> Godot: colours are linear in Blender and sRGB-encoded in Godot's Color properties; a sun's W/m2 / pi is
/// Godot's energy (both shade a white Lambert surface to energy x cos); a flat world colour L lights a surface as
/// albedo x L in both (Godot's ambient colour, energy 1). Blender's AgX look -> tonemap_agx_contrast (AgxLooks): only
/// the kit's look is calibrated (the pilot's chart of emissive patches: greys within 1/255 but the brightest at 1.5;
/// saturated primaries stay up to ~17/255 apart, Godot's AgX not being Blender's matrices); other looks get Godot's default.</summary>
public partial class KitBuilder : RefCounted
{
    static readonly Dictionary<string, float> AgxLooks = new() { ["AgX - Medium High Contrast"] = 1.5f };
    // Sun shadows (pilot sweep against Eevee): one orthogonal map over 60 m (the 50-degree camera is ~30-40 m out) with the
    // project's 8192 directional atlas, and Blender's sun angle x 0.6 -- Godot's soft shadows spread wider for the same angle
    // and lost the small stones' contact shadows at the default 4-split / 4096 / full-angle settings.
    const float SunSoftness = 0.6f, SunShadowDistance = 60f;
    const float CheckTolerance = 0.001f;

    static float Srgb(double c)
    {
        c = Math.Max(c, 0.0);
        return (float)(c <= 0.0031308 ? 12.92 * c : 1.055 * Math.Pow(c, 1.0 / 2.4) - 0.055);
    }

    static Color Col(JsonElement rgb, double k = 1.0) =>
        new(Srgb(rgb[0].GetDouble() * k), Srgb(rgb[1].GetDouble() * k), Srgb(rgb[2].GetDouble() * k));

    static Vector3 Vec(JsonElement a) => new(a[0].GetSingle(), a[1].GetSingle(), a[2].GetSingle());

    static Transform3D Xform(JsonElement d)
    {
        var b = d.GetProperty("basis");
        return new Transform3D(new Basis(Vec(b[0]), Vec(b[1]), Vec(b[2])), Vec(d.GetProperty("origin")));
    }

    static JsonElement LoadJson(string path) => JsonDocument.Parse(Godot.FileAccess.GetFileAsString(path)).RootElement;

    static MeshInstance3D MeshInstanceOf(Node n) =>
        n as MeshInstance3D ?? n.FindChildren("*", "MeshInstance3D", true, false).OfType<MeshInstance3D>().FirstOrDefault();

    static double Num(JsonElement e, string key, double fallback) =>
        e.TryGetProperty(key, out var v) && v.ValueKind == JsonValueKind.Number ? v.GetDouble() : fallback;

    static Godot.Environment MakeEnvironment(JsonElement lay)
    {
        var env = new Godot.Environment();
        var w = lay.GetProperty("world");
        double k = Num(w, "strength", 1.0);
        var lin = w.GetProperty("color");
        env.BackgroundMode = Godot.Environment.BGMode.Color;
        env.BackgroundColor = w.TryGetProperty("camera_color", out var cc) ? Col(cc) : Col(lin, k);
        env.AmbientLightSource = Godot.Environment.AmbientSource.Color;
        env.AmbientLightColor = Col(lin, k);
        env.AmbientLightEnergy = 1f;
        // Blender's world lights reflections too. With a colour background Godot's REFLECTION_SOURCE_BG reflects nothing
        // (glossy films came out too warm): a flat sky of the world's colour is the reflection source instead.
        var skyMat = new ShaderMaterial { Shader = new Shader { Code = "shader_type sky;\nuniform vec4 world : source_color;\nvoid sky() {\n\tCOLOR = world.rgb;\n}\n" } };
        skyMat.SetShaderParameter("world", env.AmbientLightColor);
        env.Sky = new Sky { SkyMaterial = skyMat };
        env.ReflectedLightSource = Godot.Environment.ReflectionSource.Sky;
        var v = lay.GetProperty("view");
        if (v.GetProperty("transform").GetString() == "AgX")
        {
            env.TonemapMode = Godot.Environment.ToneMapper.Agx;
            env.TonemapAgxContrast = AgxLooks.TryGetValue(v.GetProperty("look").GetString() ?? "", out var c) ? c : 1.25f;
        }
        else env.TonemapMode = Godot.Environment.ToneMapper.Linear;
        env.TonemapExposure = (float)Math.Pow(2.0, Num(v, "exposure", 0.0));
        env.SsaoEnabled = lay.TryGetProperty("ao", out var ao) && ao.GetBoolean();
        return env;
    }

    static void Add(Node root, Node n)
    {
        root.AddChild(n);
        n.Owner = root;
    }

    /// <summary>Every layout JSON in res://kit/data/layouts built to its scene.</summary>
    public string BuildAllLayouts()
    {
        var names = DirAccess.GetFilesAt(KitPaths.LayoutData).Where(f => f.EndsWith(".json")).Select(f => f[..^5]);
        return string.Join("\n", names.Select(BuildLayout));
    }

    /// <summary>res://kit/data/layouts/&lt;name&gt;.json -> res://kit/layouts/&lt;name&gt;.tscn; returns the BUILD report line.</summary>
    public string BuildLayout(string name)
    {
        var lay = LoadJson(KitPaths.LayoutData + name + ".json");
        var pieces = LoadJson(KitPaths.Pieces);
        bool sceneShadows = !lay.TryGetProperty("shadows", out var sh) || sh.GetBoolean();
        var root = new Node3D { Name = name };
        Add(root, new WorldEnvironment { Name = "WorldEnvironment", Environment = MakeEnvironment(lay) });
        foreach (var L in lay.GetProperty("lights").EnumerateArray())
        {
            Light3D l;
            double energy = L.GetProperty("energy").GetDouble();
            switch (L.GetProperty("type").GetString())
            {
                case "SUN":
                    l = new DirectionalLight3D
                    {
                        LightEnergy = (float)(energy / Math.PI),
                        LightAngularDistance = (float)Num(L, "angle_deg", 0.0) * SunSoftness,
                        DirectionalShadowMode = DirectionalLight3D.ShadowMode.Orthogonal,
                        DirectionalShadowMaxDistance = SunShadowDistance,
                    };
                    break;
                case "POINT":
                    l = new OmniLight3D { LightEnergy = (float)(energy / (4 * Math.PI * Math.PI)) };
                    break;
                case "SPOT":
                    l = new SpotLight3D
                    {
                        LightEnergy = (float)(energy / (4 * Math.PI * Math.PI)),
                        SpotAngle = (float)(L.GetProperty("spot_size").GetDouble() / 2.0),
                    };
                    break;
                default:
                    continue;
            }
            bool shadow = L.GetProperty("shadow").GetBoolean();
            l.Name = L.GetProperty("name").GetString();
            l.LightColor = Col(L.GetProperty("color"));
            l.ShadowEnabled = shadow && sceneShadows;
            l.SetMeta("blender_shadow", shadow);        // KitCapture turns these on for its shadow pass
            l.Transform = Xform(L);
            Add(root, l);
        }
        foreach (var C in lay.GetProperty("cameras").EnumerateArray())
        {
            var c = new Camera3D { Name = C.GetProperty("name").GetString(), Transform = Xform(C) };
            if (C.GetProperty("type").GetString() == "ORTHO")
            {
                c.Projection = Camera3D.ProjectionType.Orthogonal;
                c.Size = C.GetProperty("ortho_scale").GetSingle();
            }
            else c.Fov = C.GetProperty("fov_deg").GetSingle();
            c.KeepAspect = C.TryGetProperty("fit", out var fit) && fit.GetString() == "height" ? Camera3D.KeepAspectEnum.Height : Camera3D.KeepAspectEnum.Width;
            c.Near = C.GetProperty("clip")[0].GetSingle();
            c.Far = C.GetProperty("clip")[1].GetSingle();
            c.Current = C.TryGetProperty("active", out var act) && act.GetBoolean();
            Add(root, c);
        }
        var scenes = new Dictionary<string, PackedScene>();
        var missing = new List<string>();
        int placed = 0;
        foreach (var P in lay.GetProperty("placements").EnumerateArray())
        {
            string piece = P.GetProperty("piece").GetString();
            if (!pieces.TryGetProperty(piece, out var pc)) { missing.Add(piece); continue; }
            if (!scenes.TryGetValue(piece, out var ps)) scenes[piece] = ps = GD.Load<PackedScene>(pc.GetProperty("glb").GetString());
            var inst = ps.Instantiate<Node3D>();
            inst.Name = P.GetProperty("name").GetString();
            inst.Transform = Xform(P);
            Add(root, inst);
            placed++;
            var mi = MeshInstanceOf(inst);
            bool edited = false;
            foreach (var kv in P.GetProperty("mat").EnumerateObject())
            {
                mi.SetSurfaceOverrideMaterial(int.Parse(kv.Name), GD.Load<Material>(KitPaths.Materials + kv.Value.GetString() + ".tres"));
                edited = true;
            }
            for (int s = 0; s < mi.Mesh.GetSurfaceCount(); s++)
            {
                if (mi.GetActiveMaterial(s) is ShaderMaterial sm && sm.Shader.ResourcePath.StartsWith(KitPaths.KitLit))
                {
                    mi.SetInstanceShaderParameter("object_random", P.GetProperty("random").GetSingle());
                    edited = true;
                    break;
                }
            }
            if (edited) root.SetEditableInstance(inst, true);
        }
        int helpers = 0;
        foreach (var H in lay.GetProperty("helpers").EnumerateArray())
        {
            // flat helper quads: a grey floor (Lambert) and the chart's emissive patches (black, no specular: the view
            // transform alone)
            var props = H.GetProperty("props");
            var size = H.GetProperty("size");
            var mat = new StandardMaterial3D();
            if (H.GetProperty("kind").GetString() == "floor")
            {
                mat.AlbedoColor = Col(props.GetProperty("gdx_color"));
                mat.Roughness = props.GetProperty("gdx_roughness").GetSingle();
                mat.DiffuseMode = BaseMaterial3D.DiffuseModeEnum.Lambert;
            }
            else
            {
                var e = props.GetProperty("gdx_emission");
                double k = Math.Max(e[0].GetDouble(), Math.Max(e[1].GetDouble(), e[2].GetDouble()));
                mat.AlbedoColor = Colors.Black;
                mat.SpecularMode = BaseMaterial3D.SpecularModeEnum.Disabled;
                mat.EmissionEnabled = true;
                mat.Emission = Col(e, 1.0 / k);
                mat.EmissionEnergyMultiplier = (float)k;
            }
            var mi = new MeshInstance3D
            {
                Name = H.GetProperty("name").GetString(),
                Mesh = new PlaneMesh { Size = new Vector2(size[0].GetSingle(), size[1].GetSingle()), Material = mat },
                Position = Vec(H.GetProperty("center")),
            };
            Add(root, mi);
            helpers++;
        }
        var packed = new PackedScene();
        packed.Pack(root);
        DirAccess.MakeDirRecursiveAbsolute(KitPaths.LayoutScenes);
        var err = ResourceSaver.Save(packed, KitPaths.LayoutScenes + name + ".tscn");
        root.Free();
        return $"BUILD {name}: {placed} placements, {lay.GetProperty("lights").GetArrayLength()} lights, " +
               $"{lay.GetProperty("cameras").GetArrayLength()} cameras, {helpers} helpers, missing [{string.Join(", ", missing)}], save {err}";
    }

    /// <summary>Every imported piece (or only those named) against pieces.json: bounds against Blender's turned into
    /// Godot's axes ((x, y, z) -> (x, z, -y), 1 mm), one surface per exported material and each the library's .tres of
    /// that name, double-sided shadows (KitImport). Prints a CHECK line per problem; returns the number of pieces with problems.</summary>
    public int CheckPieces(string[] only)
    {
        var pieces = LoadJson(KitPaths.Pieces);
        int n = 0, bad = 0;
        foreach (var kv in pieces.EnumerateObject())
        {
            if (only.Length > 0 && !only.Contains(kv.Name)) continue;
            n++;
            var pc = kv.Value;
            var ps = GD.Load<PackedScene>(pc.GetProperty("glb").GetString());
            if (ps == null) { GD.Print($"CHECK {kv.Name}: does not load"); bad++; continue; }
            var inst = ps.Instantiate();
            var mis = inst.FindChildren("*", "MeshInstance3D", true, false).OfType<MeshInstance3D>().ToList();
            if (inst is MeshInstance3D self) mis.Insert(0, self);
            var probs = new List<string>();
            if (mis.Count != 1) probs.Add($"{mis.Count} mesh instances");
            if (mis.Count > 0)
            {
                var mi = mis[0];
                var box = mi.Transform * mi.Mesh.GetAabb();
                var want = pc.GetProperty("bounds_godot");
                Vector3 lo = Vec(want[0]), hi = Vec(want[1]);
                Vector3 d1 = (box.Position - lo).Abs(), d2 = (box.End - hi).Abs();
                if (Math.Max(d1.X, Math.Max(d1.Y, d1.Z)) > CheckTolerance || Math.Max(d2.X, Math.Max(d2.Y, d2.Z)) > CheckTolerance)
                    probs.Add($"bounds {box.Position}..{box.End}, want {lo}..{hi}");
                var surfs = pc.GetProperty("surfaces");
                int count = mi.Mesh.GetSurfaceCount();
                if (count != surfs.GetArrayLength()) probs.Add($"{count} surfaces, want {surfs.GetArrayLength()}");
                for (int s = 0; s < Math.Min(count, surfs.GetArrayLength()); s++)
                {
                    var m = mi.Mesh.SurfaceGetMaterial(s);
                    string wantPath = KitPaths.Materials + surfs[s].GetString() + ".tres";
                    if (m == null || m.ResourcePath != wantPath) probs.Add($"surface {s}: {(m == null ? "none" : m.ResourcePath)}, want {wantPath}");
                }
                if (mi.CastShadow != GeometryInstance3D.ShadowCastingSetting.DoubleSided) probs.Add($"cast_shadow {mi.CastShadow}");
            }
            inst.Free();
            if (probs.Count > 0)
            {
                bad++;
                GD.Print($"CHECK {kv.Name}: {string.Join("; ", probs)}");
            }
        }
        GD.Print($"CHECK DONE {n} pieces, {bad} with problems");
        return bad;
    }
}
#endif
