#if TOOLS
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using Godot;

namespace MedievalKit.Editor;

/// <summary>Builds res://kit/layouts/&lt;name&gt;.tscn from res://kit/data/layouts/&lt;name&gt;.json (gdx_export_layout) and
/// the world graph (res://kit/world.tres from res://kit/data/world.json), and checks the imported pieces against
/// res://kit/data/pieces.json (CheckPieces). Unity's KitBuilder does the same from the package's Data/.
/// A level: a KitLevel root (VKI_Root's properties, the world graph), the placements grouped by Blender collection as
/// instances of their .glb (KitPiece roots: the instance's properties; restyles: surface_material_override/N; the roof
/// jitter's object_random), a KitLink on every link piece (its trigger box from vki_trigger), the empties as KitMarker /
/// KitSpawn, Blender's lights and cameras, world and view transform; bridge decks cut into the ground tiles' colliders
/// (KitDecks); a world level also its navmesh (KitNavMesh, saved beside the scene as &lt;name&gt;_nav.res) and the walk
/// test's line in the report (KitWalkTest).
///
/// Blender -> Godot: colours are linear in Blender and sRGB-encoded in Godot's Color properties; a sun's W/m2 / pi is
/// Godot's energy (both shade a white Lambert surface to energy x cos), a point or spot light's W / (4 pi^2) with
/// inverse-square falloff (omni_attenuation 2: Godot's default 1 falls as 1/d) and a range where it is down to ~1 % of
/// its 1 m value (as Unity's); every light's specular at 1 (Godot's default 0.5 halves Blender's highlights); a flat
/// world colour L lights a surface as albedo x L in both (Godot's ambient colour, energy 1), a probed sky (the valley's)
/// as a three-colour sky. Blender's AgX look -> tonemap_agx_contrast (AgxLooks): only the kit's look is calibrated (the
/// pilot's chart of emissive patches: greys within 1/255 but the brightest at 1.5; saturated primaries stay up to
/// ~17/255 apart, Godot's AgX not being Blender's matrices); other looks get Godot's default.</summary>
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

    // pieces.json (1,465 pieces) parsed once per change, not once per structure: 49 structures in one run parsed it 49
    // times and the run died at the 41st (2026-10-25)
    static JsonElement? piecesCache;
    static ulong piecesTime;

    static JsonElement Pieces()
    {
        ulong t = Godot.FileAccess.GetModifiedTime(KitPaths.Pieces);
        if (piecesCache == null || t != piecesTime) { piecesCache = LoadJson(KitPaths.Pieces); piecesTime = t; }
        return piecesCache.Value;
    }

    static MeshInstance3D MeshInstanceOf(Node n) =>
        n as MeshInstance3D ?? n.FindChildren("*", "MeshInstance3D", true, false).OfType<MeshInstance3D>().FirstOrDefault();

    static double Num(JsonElement e, string key, double fallback) =>
        e.TryGetProperty(key, out var v) && v.ValueKind == JsonValueKind.Number ? v.GetDouble() : fallback;

    static string Str(JsonElement e, string key, string fallback = "") =>
        e.TryGetProperty(key, out var v) && v.ValueKind == JsonValueKind.String ? v.GetString() : fallback;

    static Sky FlatSky(Color c)
    {
        var mat = new ShaderMaterial { Shader = new Shader { Code = "shader_type sky;\nuniform vec4 world : source_color;\nvoid sky() {\n\tCOLOR = world.rgb;\n}\n" } };
        mat.SetShaderParameter("world", c);
        return new Sky { SkyMaterial = mat };
    }

    /// <summary>a probed sky network (vkx world_probe: its lighting branch averaged into sky / horizon / ground) as a sky
    /// that blends them by height, the ambient and reflections then taken from it (Unity: Trilight ambient)</summary>
    static Sky TrilightSky(JsonElement tri)
    {
        var mat = new ShaderMaterial
        {
            Shader = new Shader
            {
                Code = "shader_type sky;\nuniform vec4 sky_color : source_color;\nuniform vec4 equator : source_color;\n" +
                       "uniform vec4 ground : source_color;\nvoid sky() {\n\tfloat y = EYEDIR.y;\n" +
                       "\tCOLOR = y > 0.0 ? mix(equator.rgb, sky_color.rgb, y) : mix(equator.rgb, ground.rgb, -y);\n}\n",
            },
        };
        mat.SetShaderParameter("sky_color", Col(tri.GetProperty("sky")));
        mat.SetShaderParameter("equator", Col(tri.GetProperty("equator")));
        mat.SetShaderParameter("ground", Col(tri.GetProperty("ground")));
        return new Sky { SkyMaterial = mat };
    }

    static Godot.Environment MakeEnvironment(JsonElement lay)
    {
        var env = new Godot.Environment();
        var w = lay.GetProperty("world");
        env.BackgroundMode = Godot.Environment.BGMode.Color;
        env.AmbientLightEnergy = 1f;
        if (w.ValueKind == JsonValueKind.Object && w.TryGetProperty("trilight", out var tri))
        {
            env.BackgroundColor = w.TryGetProperty("camera_color", out var cc0) ? Col(cc0) : Col(tri.GetProperty("equator"));
            env.Sky = TrilightSky(tri);
            env.AmbientLightSource = Godot.Environment.AmbientSource.Sky;
            env.ReflectedLightSource = Godot.Environment.ReflectionSource.Sky;
        }
        else
        {
            double k = w.ValueKind == JsonValueKind.Object ? Num(w, "strength", 1.0) : 0.0;
            var lin = w.ValueKind == JsonValueKind.Object ? w.GetProperty("color") : default;
            var amb = w.ValueKind == JsonValueKind.Object ? Col(lin, k) : Colors.Black;
            env.BackgroundColor = w.ValueKind == JsonValueKind.Object && w.TryGetProperty("camera_color", out var cc) ? Col(cc) : amb;
            env.AmbientLightSource = Godot.Environment.AmbientSource.Color;
            env.AmbientLightColor = amb;
            // Blender's world lights reflections too. With a colour background Godot's REFLECTION_SOURCE_BG reflects
            // nothing (glossy films came out too warm): a flat sky of the world's colour is the reflection source instead.
            env.Sky = FlatSky(amb);
            env.ReflectedLightSource = Godot.Environment.ReflectionSource.Sky;
        }
        var v = lay.GetProperty("view");
        if (Str(v, "transform") == "AgX")
        {
            env.TonemapMode = Godot.Environment.ToneMapper.Agx;
            env.TonemapAgxContrast = AgxLooks.TryGetValue(Str(v, "look"), out var c) ? c : 1.25f;
        }
        else env.TonemapMode = Godot.Environment.ToneMapper.Linear;      // Standard: no curve, then sRGB
        env.TonemapExposure = (float)Math.Pow(2.0, Num(v, "exposure", 0.0));
        env.SsaoEnabled = lay.TryGetProperty("ao", out var ao) && ao.GetBoolean();
        return env;
    }

    static void Add(Node parent, Node n, Node owner)
    {
        parent.AddChild(n);
        n.Owner = owner;
    }

    /// <summary>res://kit/data/world.json (the kit's docs/world_graph.json) -> res://kit/world.tres</summary>
    public string BuildWorld()
    {
        string src = KitPaths.Data + "world.json";
        if (!Godot.FileAccess.FileExists(src)) return "WORLD no world.json";
        var g = LoadJson(src);
        var world = new KitWorld { Start = Str(g, "start") };
        foreach (var kv in g.GetProperty("levels").EnumerateObject())
        {
            var lv = new KitWorldLevel { Name = kv.Name, Kind = Str(kv.Value, "kind") };
            foreach (var l in kv.Value.GetProperty("links").EnumerateArray())
                lv.Links.Add(new KitWorldLink { Id = Str(l, "id"), Kind = Str(l, "kind"), Target = Str(l, "target"), Arrive = Str(l, "arrive") });
            world.Levels.Add(lv);
        }
        var err = ResourceSaver.Save(world, KitPaths.World);
        return $"WORLD {world.Levels.Count} levels, start {world.Start}, save {err}";
    }

    /// <summary>Every layout JSON in res://kit/data/layouts built to its scene (the world graph first).</summary>
    public string BuildAllLayouts()
    {
        var names = DirAccess.GetFilesAt(KitPaths.LayoutData).Where(f => f.EndsWith(".json")).Select(f => f[..^5]);
        return BuildWorld() + "\n" + string.Join("\n", names.Select(BuildLayout)) + "\n" + BuildStructures();
    }

    /// <summary>res://kit/data/layouts/&lt;name&gt;.json -> res://kit/layouts/&lt;name&gt;.tscn; returns the BUILD report line.</summary>
    public string BuildLayout(string name)
    {
        var lay = LoadJson(KitPaths.LayoutData + name + ".json");
        var world = ResourceLoader.Exists(KitPaths.World) ? GD.Load<KitWorld>(KitPaths.World) : null;
        var worldLevel = world?.Find(name);
        var root = new KitLevel
        {
            Name = name, LevelName = name, BlenderScene = Str(lay, "scene"), ExportVersion = Str(lay, "version"),
            Props = lay.TryGetProperty("root", out var rp) ? KitProps.FromJson(rp) : new(), World = world,
        };
        Add(root, new WorldEnvironment { Name = "WorldEnvironment", Environment = MakeEnvironment(lay) }, root);
        var log = new List<string>();
        var (placed, links, markers, missing) = Populate(lay, root, worldLevel, true, log);
        foreach (var C in lay.GetProperty("cameras").EnumerateArray())
        {
            var c = new Camera3D { Name = Str(C, "name"), Transform = Xform(C) };
            if (Str(C, "type") == "ORTHO")
            {
                // Blender's ortho_scale spans the sensor-fit axis (the width of a landscape render)
                c.Projection = Camera3D.ProjectionType.Orthogonal;
                c.Size = C.GetProperty("ortho_scale").GetSingle();
                c.KeepAspect = Str(C, "fit") == "height" ? Camera3D.KeepAspectEnum.Height : Camera3D.KeepAspectEnum.Width;
            }
            else
            {
                // fov_deg is vertical (vkx _vfov), and Godot reads fov along the locked axis
                c.Fov = C.GetProperty("fov_deg").GetSingle();
                c.KeepAspect = Camera3D.KeepAspectEnum.Height;
            }
            c.Near = C.GetProperty("clip")[0].GetSingle();
            c.Far = C.GetProperty("clip")[1].GetSingle();
            c.Current = C.TryGetProperty("active", out var act) && act.GetBoolean();
            Add(root, c, root);
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
            Add(root, new MeshInstance3D
            {
                Name = H.GetProperty("name").GetString(),
                Mesh = new PlaneMesh { Size = new Vector2(size[0].GetSingle(), size[1].GetSingle()), Material = mat },
                Position = Vec(H.GetProperty("center")),
            }, root);
            helpers++;
        }
        int cut = KitDecks.Apply(root);         // bridges over chasms / channels: walkable decks
        if (cut > 0) log.Add($"{cut} ground colliders cut round bridge decks");
        string walk = "";
        if (worldLevel != null)
        {
            // the walkable surface (0.1 m cells outdoors, 0.05 in) and the walk test on it; the parser reads global
            // transforms, so the level goes in the tree for the bake
            var tree = (SceneTree)Engine.GetMainLoop();
            tree.Root.AddChild(root);
            var nm = KitNavMesh.Bake(root, worldLevel.Kind == "exterior" ? 0.1f : 0.05f);
            var wt = KitWalkTest.Run(nm, KitWalkTest.Points(root));
            tree.Root.RemoveChild(root);
            ResourceSaver.Save(nm, KitPaths.LayoutScenes + name + "_nav.res", ResourceSaver.SaverFlags.ChangePath | ResourceSaver.SaverFlags.Compress);
            Add(root, new KitNavMesh { Name = "KitNavMesh", NavigationMesh = nm }, root);
            walk = ", " + wt;
        }
        var err = Save(root, KitPaths.LayoutScenes + name + ".tscn");
        foreach (var w in log) GD.Print($"BUILD {name}: {w}");
        return $"BUILD {name}: {placed} placements, {links} links, {markers} markers, {lay.GetProperty("lights").GetArrayLength()} lights, " +
               $"{lay.GetProperty("cameras").GetArrayLength()} cameras, {helpers} helpers, missing [{string.Join(", ", missing)}], save {err}{walk}";
    }

    /// <summary>res://kit/data/structures/*.json (gdx_export_structures) -> res://kit/structures/&lt;name&gt;.tscn: a
    /// KitStructure root with the kit pieces as instances of their .glb (restyled where Blender restyled them), markers
    /// and lights, no camera or world. Unity: KitBuilder.BuildStructures.</summary>
    public string BuildStructures() => BuildStructuresOnly(null);

    /// <summary>BuildStructures for the named structures only (all when names is null or empty).</summary>
    public string BuildStructuresOnly(string[] names)
    {
        if (!DirAccess.DirExistsAbsolute(KitPaths.StructureData)) return "STRUCTURES none exported";
        int n = 0;
        var notes = new List<string>();
        var want = names is { Length: > 0 } ? new HashSet<string>(names) : null;
        foreach (var f in DirAccess.GetFilesAt(KitPaths.StructureData).Where(f => f.EndsWith(".json")).OrderBy(f => f, StringComparer.Ordinal))
        {
            string name = f[..^5];
            if (want != null && !want.Contains(name)) continue;
            var sj = LoadJson(KitPaths.StructureData + f);
            var root = new KitStructure { Name = name, StructureName = name, Builder = Str(sj, "builder"), ExportVersion = Str(sj, "version") };
            var log = new List<string>();
            var (_, _, _, missing) = Populate(sj, root, null, false, log);
            int cut = KitDecks.Apply(root);
            if (cut > 0) log.Add($"{cut} ground colliders cut round bridge decks");
            var err = Save(root, KitPaths.Structures + name + ".tscn");
            if (missing.Count > 0) log.Add($"missing [{string.Join(", ", missing)}]");
            if (err != Error.Ok) log.Add($"save {err}");
            notes.AddRange(log.Select(l => $"  {name}: {l}"));
            n++;
        }
        return $"STRUCTURES {n} -> {KitPaths.Structures}" + string.Concat(notes.Select(l => "\n" + l));
    }

    static Error Save(Node root, string path)
    {
        var packed = new PackedScene();
        packed.Pack(root);
        DirAccess.MakeDirRecursiveAbsolute(path.GetBaseDir());
        var err = ResourceSaver.Save(packed, path);
        root.Free();
        return err;
    }

    /// <summary>The placements, lights and markers of an exported level or structure under root (grouped by Blender
    /// collection when `grouped`), as Unity's KitBuilder.Populate.</summary>
    static (int placed, int links, int markers, List<string> missing) Populate(JsonElement lay, Node3D root, KitWorldLevel worldLevel, bool grouped, List<string> log)
    {
        var pieces = Pieces();
        bool sceneShadows = !lay.TryGetProperty("shadows", out var sh) || sh.GetBoolean();
        var groups = new Dictionary<string, Node3D>();
        Node3D Group(JsonElement e)
        {
            if (!grouped) return root;
            string c = Str(e, "coll", "Level");
            if (string.IsNullOrEmpty(c)) c = "Level";
            if (!groups.TryGetValue(c, out var t)) { t = new Node3D { Name = c }; Add(root, t, root); groups[c] = t; }
            return t;
        }
        foreach (var L in lay.GetProperty("lights").EnumerateArray())
        {
            Light3D l;
            double energy = L.GetProperty("energy").GetDouble();
            double radius = Num(L, "radius", 0.0);
            float pointEnergy = (float)(energy / (4 * Math.PI * Math.PI));
            float range = Mathf.Clamp(10f * Mathf.Sqrt(pointEnergy), 1.5f, 60f);
            switch (Str(L, "type"))
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
                    l = new OmniLight3D { LightEnergy = pointEnergy, OmniAttenuation = 2f, OmniRange = range, LightSize = (float)radius };
                    break;
                case "AREA":
                {
                    // Blender's area light is a one-sided Lambertian emitter: on its axis P / pi W/sr, four times a point
                    // light's P / (4 pi); Godot's normalized AreaLight3D of energy E shines on its axis as an omni of E
                    // (measured), falling with the cosine off it as Blender's. Unity's builder makes it a point light.
                    float areaEnergy = (float)(energy / (Math.PI * Math.PI));
                    var sz = L.TryGetProperty("size", out var se) ? new Vector2(se[0].GetSingle(), se[1].GetSingle()) : new Vector2(0.25f, 0.25f);
                    l = new AreaLight3D
                    {
                        LightEnergy = areaEnergy, AreaSize = sz, AreaNormalizeEnergy = true, AreaAttenuation = 2f,
                        AreaRange = Mathf.Clamp(10f * Mathf.Sqrt(areaEnergy), 1.5f, 60f),
                    };
                    break;
                }
                case "SPOT":
                    // Blender fades the cone's last `blend` share (in 1 - cos) with a smoothstep; Godot 4.7 by 1 - rim^(1/a)
                    // for spot_angle_attenuation a (rim = (1 - cos) / (1 - cos cutoff); measured: a above 1 softens the
                    // whole beam, below 1 sharpens its edge), so a puts Godot's half-way where Blender's is, rim = 1 - blend/2
                    double blend = Math.Clamp(Num(L, "spot_blend", 0.15), 0.01, 1.0);
                    l = new SpotLight3D
                    {
                        LightEnergy = pointEnergy, SpotAttenuation = 2f, SpotRange = range, LightSize = (float)radius,
                        SpotAngle = (float)(Num(L, "spot_size", 45.0) / 2.0),
                        SpotAngleAttenuation = (float)(Math.Log(1.0 - blend / 2.0) / Math.Log(0.5)),
                    };
                    break;
                default:
                    log.Add($"light {Str(L, "name")}: type {Str(L, "type")} not ported");
                    continue;
            }
            bool shadow = L.GetProperty("shadow").GetBoolean();
            l.Name = Str(L, "name");
            l.LightColor = Col(L.GetProperty("color"));
            l.LightSpecular = 1f;
            l.ShadowEnabled = shadow && sceneShadows;
            l.SetMeta("blender_shadow", shadow);        // KitCapture turns these on for its shadow pass
            l.Transform = Xform(L);
            Add(Group(L), l, root);
        }
        var scenes = new Dictionary<string, PackedScene>();
        var missing = new List<string>();
        int placed = 0, links = 0;
        foreach (var P in lay.GetProperty("placements").EnumerateArray())
        {
            string piece = P.GetProperty("piece").GetString();
            if (!pieces.TryGetProperty(piece, out var pc)) { missing.Add(piece); continue; }
            if (!scenes.TryGetValue(piece, out var ps)) scenes[piece] = ps = GD.Load<PackedScene>(pc.GetProperty("glb").GetString());
            var inst = ps.Instantiate<Node3D>();
            inst.Name = P.GetProperty("name").GetString();
            inst.Transform = Xform(P);
            Add(Group(P), inst, root);
            placed++;
            var ip = P.TryGetProperty("props", out var pp) ? KitProps.FromJson(pp) : new();
            if (inst is KitPiece kp && ip.Count > 0) kp.Props = ip;      // the instance's properties, as Unity's
            var mi = MeshInstanceOf(inst);
            bool edited = false;
            foreach (var kv in P.GetProperty("mat").EnumerateObject())
            {
                mi.SetSurfaceOverrideMaterial(int.Parse(kv.Name), GD.Load<Material>(KitPaths.Materials + kv.Value.GetString() + ".tres"));
                edited = true;
            }
            for (int s = 0; s < mi.Mesh.GetSurfaceCount(); s++)
            {
                // only a material with the roof jitter reads it (every kit material is KitLit)
                if (mi.GetActiveMaterial(s) is ShaderMaterial sm && sm.Shader.ResourcePath.StartsWith(KitPaths.KitLit)
                    && sm.GetShaderParameter("jitter") is { VariantType: Variant.Type.Vector2 } j && j.AsVector2() != Vector2.One)
                {
                    mi.SetInstanceShaderParameter("object_random", P.GetProperty("random").GetSingle());
                    edited = true;
                    break;
                }
            }
            if (edited) root.SetEditableInstance(inst, true);
            if (ip.Has("vki_link")) { AddLink(inst, ip, worldLevel, root, log); links++; }
        }
        int markers = 0;
        if (lay.TryGetProperty("markers", out var mks))
            foreach (var M in mks.EnumerateArray())
            {
                var props = M.TryGetProperty("props", out var mp) ? KitProps.FromJson(mp) : new();
                string mname = Str(M, "name");
                KitMarker m = props.Has("vki_spawn_id")
                    ? new KitSpawn { SpawnId = props.Get("vki_spawn_id"), FacingDeg = props.GetFloat("vki_facing_deg") }
                    : new KitMarker();
                m.Name = mname;
                m.Kind = KitMarker.KindOf(mname);
                m.Props = props;
                var t = Xform(M);
                m.Transform = m is KitSpawn sp ? new Transform3D(KitSpawn.FromBearing(sp.FacingDeg), t.Origin) : t;
                Add(Group(M), m, root);
                markers++;
            }
        return (placed, links, markers, missing);
    }

    /// <summary>A link piece (vki_link) gets a KitLink with its trigger box (vki_trigger, Blender piece space), its arrival
    /// from the world graph.</summary>
    static void AddLink(Node3D piece, Godot.Collections.Dictionary<string, string> ip, KitWorldLevel worldLevel, Node owner, List<string> log)
    {
        var l = new KitLink
        {
            Name = "KitLink", LinkId = ip.Get("vki_link_id", ""), Kind = ip.Get("vki_link", "exit"),
            Target = ip.Get("vki_target", ""), Prompt = ip.Get("vki_prompt", "Enter"), FacingMin = ip.GetFloat("vki_facing_min", 60f),
            Monitorable = false,
        };
        var wl = worldLevel?.Links.FirstOrDefault(x => x.Id == l.LinkId);
        if (wl != null)
        {
            l.Arrive = wl.Arrive;
            if (wl.Target != l.Target) log.Add($"{piece.Name}: target {l.Target} vs world graph {wl.Target}");
        }
        Add(piece, l, owner);
        string tj = ip.Get("vki_trigger");
        if (string.IsNullOrEmpty(tj)) { log.Add($"{piece.Name}: link without vki_trigger"); return; }
        var b = JsonDocument.Parse(tj).RootElement;
        if (b.GetArrayLength() < 6) { log.Add($"{piece.Name}: bad vki_trigger"); return; }
        Add(l, new CollisionShape3D
        {
            Shape = new BoxShape3D { Size = new Vector3(Mathf.Abs(b[3].GetSingle()), Mathf.Abs(b[5].GetSingle()), Mathf.Abs(b[4].GetSingle())) },
            Position = new Vector3(b[0].GetSingle(), b[2].GetSingle(), -b[1].GetSingle()),
        }, owner);
    }

    /// <summary>Every imported piece (or only those named) against pieces.json: bounds against Blender's turned into
    /// Godot's axes ((x, y, z) -> (x, z, -y), 1 mm), one surface per exported material and each the library's .tres of
    /// that name, double-sided shadows, a KitPiece root (KitImport), colliders on the passable layer for doors that open
    /// and breakables. Prints a CHECK line per problem; returns the number of pieces with problems.</summary>
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
            if (inst is not KitPiece kpc) probs.Add("root is not a KitPiece");
            else if (kpc.GetNodeOrNull<StaticBody3D>("Collision") is { } cb)
            {
                uint wantLayer = kpc.Flag("vki_openable") || kpc.Flag("vki_breakable") ? KitPiece.Passable : KitPiece.Solid;
                if (cb.CollisionLayer != wantLayer) probs.Add($"collision layer {cb.CollisionLayer}, want {wantLayer}");
            }
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
