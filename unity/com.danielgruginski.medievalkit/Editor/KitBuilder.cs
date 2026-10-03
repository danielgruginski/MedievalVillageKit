using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;

namespace MedievalKit.Editor
{
    /// <summary>
    /// Builds Unity assets from the Blender export (Data/*.json + Art/): KitLit materials, one prefab per master
    /// piece, and one scene per exported level. Everything under Generated/ is rebuilt; nothing there is hand-edited.
    /// </summary>
    public static class KitBuilder
    {
        static readonly StringBuilder Log = new StringBuilder();

        [MenuItem("Tools/Medieval Kit/Build All (materials, prefabs, levels)")]
        public static void BuildAll()
        {
            Log.Clear();
            if (!CanLeaveOpenScenes()) return;
            var reopen = OpenScenePaths();
            AssetDatabase.Refresh();
            InstallAgxFeature();
            BuildMaterials();
            BuildPrefabs();
            KitHouseTools.BuildRules(Log);
            KitRoomTools.BuildRules(Log);
            BuildStructures();
            BuildWorld();
            foreach (var f in Directory.GetFiles(Abs(KitPaths.Data + "/Levels"), "*.json"))
                BuildLevel(Path.GetFileNameWithoutExtension(f));
            RegisterWorldScenes();
            CheckWorld();
            Reopen(reopen);
            WriteReport();
        }

        [MenuItem("Tools/Medieval Kit/Build Levels")]
        public static void BuildLevelsMenu()
        {
            Log.Clear();
            if (!CanLeaveOpenScenes()) return;
            var reopen = OpenScenePaths();
            BuildWorld();
            foreach (var f in Directory.GetFiles(Abs(KitPaths.Data + "/Levels"), "*.json"))
                BuildLevel(Path.GetFileNameWithoutExtension(f));
            RegisterWorldScenes();
            CheckWorld();
            Reopen(reopen);
            WriteReport();
        }

        [MenuItem("Tools/Medieval Kit/Check World Links")]
        public static void CheckWorldMenu() { Log.Clear(); CheckWorld(); WriteReport(); }

        // ------------------------------------------------------------------ world graph
        const string WorldAsset = KitPaths.Generated + "/KitWorld.asset";

        /// <summary>Data/world.json (docs/world_graph.json) -> Generated/KitWorld.asset.</summary>
        public static KitWorld BuildWorld()
        {
            string json = KitPaths.Data + "/world.json";
            if (!File.Exists(Abs(json))) { Log.AppendLine("no world.json"); return null; }
            var g = ReadJson(json);
            var w = AssetDatabase.LoadAssetAtPath<KitWorld>(WorldAsset);
            bool isNew = w == null;
            if (isNew) w = ScriptableObject.CreateInstance<KitWorld>();
            w.start = (string)g["start"];
            w.levels.Clear();
            foreach (var kv in (JObject)g["levels"])
            {
                var lv = new KitWorld.Level { name = kv.Key, kind = (string)kv.Value["kind"] };
                foreach (var l in kv.Value["links"])
                    lv.links.Add(new KitWorld.Link { id = (string)l["id"], kind = (string)l["kind"], target = (string)l["target"], arrive = (string)l["arrive"] });
                w.levels.Add(lv);
            }
            if (isNew) { EnsureFolder(KitPaths.Generated); AssetDatabase.CreateAsset(w, WorldAsset); }
            else EditorUtility.SetDirty(w);
            AssetDatabase.SaveAssets();
            Log.AppendLine($"world: {w.levels.Count} levels, start {w.start}");
            return w;
        }

        /// <summary>The world's level scenes go into the build settings (start level first); other entries are kept.</summary>
        static void RegisterWorldScenes()
        {
            var w = AssetDatabase.LoadAssetAtPath<KitWorld>(WorldAsset);
            if (w == null) return;
            var names = new List<string> { w.start };
            names.AddRange(w.levels.Select(l => l.name).Where(n => n != w.start));
            var kit = names.Select(n => $"{KitPaths.Levels}/{n}.unity").Where(p => File.Exists(Abs(p)))
                .Select(p => new EditorBuildSettingsScene(p, true)).ToList();
            var others = EditorBuildSettings.scenes.Where(sc => !sc.path.StartsWith(KitPaths.Levels + "/")).ToList();
            EditorBuildSettings.scenes = kit.Concat(others).ToArray();
            Log.AppendLine($"build settings: {kit.Count} kit levels + {others.Count} other scenes");
        }

        /// <summary>Every link resolves: target level built (or a hole), an arrival found, and its spawn exists there.</summary>
        static void CheckWorld()
        {
            var w = AssetDatabase.LoadAssetAtPath<KitWorld>(WorldAsset);
            if (w == null) { Log.AppendLine("check: no world"); return; }
            int ok = 0, bad = 0, holes = 0;
            var spawns = new Dictionary<string, HashSet<string>>();
            HashSet<string> SpawnsOf(string level)
            {
                if (spawns.TryGetValue(level, out var set)) return set;
                set = new HashSet<string>();
                string p = $"{KitPaths.Data}/Levels/{level}.json";
                if (File.Exists(Abs(p)))
                    foreach (var mk in ReadJson(p)["markers"])
                        if (mk["props"]?["vki_spawn_id"] != null) set.Add((string)mk["props"]["vki_spawn_id"]);
                return spawns[level] = set;
            }
            foreach (var lv in w.levels)
            {
                if (!File.Exists(Abs($"{KitPaths.Levels}/{lv.name}.unity"))) { Log.AppendLine($"  check: level {lv.name} not built"); bad++; continue; }
                foreach (var l in lv.links)
                {
                    if (!SpawnsOf(lv.name).Contains(l.id)) { Log.AppendLine($"  check: {lv.name}.{l.id} has no spawn of its own"); bad++; }
                    if (l.target.StartsWith("@")) { holes++; continue; }
                    string arrive = w.ArrivalFor(lv.name, l.id, l.target);
                    if (arrive == null) { Log.AppendLine($"  check: {lv.name}.{l.id} -> {l.target}: no arrival"); bad++; continue; }
                    if (!SpawnsOf(l.target).Contains(arrive)) { Log.AppendLine($"  check: {lv.name}.{l.id} -> {l.target}.{arrive}: no such spawn"); bad++; continue; }
                    ok++;
                }
            }
            Log.AppendLine($"world check: {ok} links resolve, {holes} holes (@return / @deep), {bad} problems");
        }

        // Level builds replace the open scene: never drop unsaved work, and put the user's scenes back afterwards.
        static bool CanLeaveOpenScenes()
        {
            for (int i = 0; i < SceneManager.sceneCount; i++)
                if (SceneManager.GetSceneAt(i).isDirty)
                {
                    Debug.LogError($"[MedievalKit] '{SceneManager.GetSceneAt(i).name}' has unsaved changes; save it before building levels.");
                    return false;
                }
            return true;
        }

        static List<string> OpenScenePaths()
        {
            var l = new List<string>();
            for (int i = 0; i < SceneManager.sceneCount; i++)
                if (!string.IsNullOrEmpty(SceneManager.GetSceneAt(i).path)) l.Add(SceneManager.GetSceneAt(i).path);
            return l;
        }

        static void Reopen(List<string> paths)
        {
            for (int i = 0; i < paths.Count; i++)
                EditorSceneManager.OpenScene(paths[i], i == 0 ? OpenSceneMode.Single : OpenSceneMode.Additive);
        }

        [MenuItem("Tools/Medieval Kit/Build Materials")]
        public static void BuildMaterialsMenu() { Log.Clear(); BuildMaterials(); WriteReport(); }

        [MenuItem("Tools/Medieval Kit/Build Prefabs")]
        public static void BuildPrefabsMenu() { Log.Clear(); BuildPrefabs(); WriteReport(); }

        // ------------------------------------------------------------------ paths and json
        static string Abs(string assetPath) => Path.GetFullPath(assetPath);

        static JObject ReadJson(string assetPath) => JObject.Parse(File.ReadAllText(Abs(assetPath)));

        static void EnsureFolder(string assetPath)
        {
            Directory.CreateDirectory(Abs(assetPath));
        }

        static Color Lin(JToken t, float alpha = 1f)
        {
            // Blender colours are linear; Unity material / light colours are authored in gamma space
            var a = t.Select(x => (float)x).ToArray();
            var c = new Color(a[0], a[1], a[2], a.Length > 3 ? a[3] : alpha);
            var g = c.gamma;
            g.a = c.a;
            return g;
        }

        static Vector3 V3(JToken t) => new Vector3((float)t[0], (float)t[1], (float)t[2]);
        static Quaternion Q(JToken t) => new Quaternion((float)t[0], (float)t[1], (float)t[2], (float)t[3]);

        // ------------------------------------------------------------------ materials
        public static void BuildMaterials()
        {
            EnsureFolder(KitPaths.Materials);
            AssetDatabase.Refresh();
            var shader = Shader.Find(KitPaths.Shader);
            if (shader == null) { Log.AppendLine("ERROR shader " + KitPaths.Shader + " not found"); return; }
            var terrainShader = Shader.Find(KitPaths.TerrainShader);
            if (terrainShader == null) { Log.AppendLine("ERROR shader " + KitPaths.TerrainShader + " not found"); return; }
            var mats = ReadJson(KitPaths.Data + "/materials.json");
            int n = 0;
            AssetDatabase.StartAssetEditing();
            var created = new List<(string path, Material mat)>();
            try
            {
                foreach (var kv in mats)
                {
                    if (kv.Value.Type != JTokenType.Object) continue;
                    var d = (JObject)kv.Value;
                    string path = $"{KitPaths.Materials}/{kv.Key}.mat";
                    var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
                    bool isNew = mat == null;
                    bool projected = (string)d["shader"] == "projected" && d["recipe"] != null && d["recipe"].Type == JTokenType.String;
                    var sh = projected ? terrainShader : shader;
                    if (isNew) mat = new Material(sh) { name = kv.Key };
                    mat.shader = sh;
                    if (projected) FillTerrain(mat, d); else Fill(mat, d);
                    if (isNew) created.Add((path, mat));
                    else EditorUtility.SetDirty(mat);
                    n++;
                }
            }
            finally { AssetDatabase.StopAssetEditing(); }
            foreach (var (path, mat) in created) AssetDatabase.CreateAsset(mat, path);
            AssetDatabase.SaveAssets();
            Log.AppendLine($"materials: {n} ({created.Count} new)");
        }

        static Texture2D Tex(JToken file)
        {
            if (file == null || file.Type == JTokenType.Null) return null;
            var t = AssetDatabase.LoadAssetAtPath<Texture2D>($"{KitPaths.Textures}/{(string)file}");
            if (t == null) Log.AppendLine("  missing texture " + file);
            return t;
        }

        static void Keyword(Material m, string kw, bool on)
        {
            if (on) m.EnableKeyword(kw); else m.DisableKeyword(kw);
        }

        static void Fill(Material m, JObject d)
        {
            m.SetColor("_BaseColor", Lin(d["base_color"]));
            m.SetTexture("_BaseMap", Tex(d["base_map"]));
            bool vc = (bool)d["vertex_color"];
            m.SetFloat("_UseVertexColor", vc ? 1 : 0); Keyword(m, "_VKX_VERTEX_COLOR", vc);
            var j = d["jitter"];
            m.SetVector("_Jitter", j != null && j.Type == JTokenType.Array ? new Vector4((float)j[0], (float)j[1]) : new Vector4(1, 1));

            var nrm = Tex(d["normal_map"]);
            m.SetTexture("_BumpMap", nrm); Keyword(m, "_NORMALMAP", nrm != null);
            m.SetFloat("_BumpScale", d["normal_strength"] != null ? (float)d["normal_strength"] : 1f);

            var rough = Tex(d["rough_map"]);
            m.SetTexture("_RoughMap", rough); Keyword(m, "_VKX_ROUGHMAP", rough != null);
            m.SetFloat("_RoughScale", (float)d["rough_scale"]);
            m.SetFloat("_Roughness", (float)d["roughness"]);
            m.SetFloat("_Metallic", (float)d["metallic"]);
            m.SetFloat("_Specular", Mathf.Clamp01((float)d["specular"]));

            var emap = Tex(d["emission_map"]);
            float es = (float)d["emission_strength"];
            var ec = d["emission"].Select(x => (float)x).ToArray();
            bool emit = es > 0f;
            m.SetTexture("_EmissionMap", emap);
            var lin = new Color(ec[0] * es, ec[1] * es, ec[2] * es);
            m.SetColor("_EmissionColor", emit ? lin.gamma : Color.black);
            Keyword(m, "_EMISSION", emit);
            m.globalIlluminationFlags = emit ? MaterialGlobalIlluminationFlags.RealtimeEmissive : MaterialGlobalIlluminationFlags.EmissiveIsBlack;

            var rim = d["rim"];
            bool hasRim = rim != null && rim.Type == JTokenType.Object;
            m.SetFloat("_UseRim", hasRim ? 1 : 0); Keyword(m, "_VKX_RIM", hasRim);
            if (hasRim)
            {
                var cols = rim["colors"];
                if (cols != null && cols.Type == JTokenType.Array)
                {
                    m.SetColor("_RimColorA", Lin(cols[0]));
                    m.SetColor("_RimColorB", Lin(cols[1]));
                }
                var k = rim["k"];
                if ((string)rim["op"] == "MULTIPLY_ADD") m.SetVector("_RimK", new Vector4((float)k[0], (float)k[1]));
                else if ((string)rim["op"] == "MULTIPLY") m.SetVector("_RimK", new Vector4((float)k[0], 0));
                else Log.AppendLine($"  {m.name}: rim op {(string)rim["op"]} not ported");
            }

            m.SetFloat("_Translucency", d["translucency"] != null ? (float)d["translucency"] : 0f);
            var moss = d["moss"] as JObject;
            m.SetFloat("_UseMoss", moss != null ? 1 : 0); Keyword(m, "_VKX_MOSS", moss != null);
            if (moss != null)
            {
                m.SetTexture("_MossMap", Tex(moss["moss_map"]));
                m.SetTexture("_MossBumpMap", Tex(moss["moss_normal"]));
                m.SetTexture("_MossRoughMap", Tex(moss["moss_rough"]));
                m.SetTexture("_MossHeightMap", Tex(moss["moss_height"]));
                m.SetFloat("_MossTile", (float)moss["tile"]);
                m.SetVector("_MossNoise", new Vector4((float)moss["noise"][0], (float)moss["noise"][1]));
                m.SetVector("_MossRange", new Vector4((float)moss["range"][0], (float)moss["range"][1]));
                if (!(bool)moss["gate_vertex_alpha"]) Log.AppendLine($"  {m.name}: moss without the vertex-alpha gate (shader always gates)");
            }
            if ((string)d["shader"] == "projected") Log.AppendLine($"  {m.name}: projected material without a KitTerrain recipe, placeholder colour");

            string alpha = (string)d["alpha"];
            m.SetFloat("_Cutoff", (float)d["cutoff"]);
            m.SetFloat("_AlphaClip", alpha == "clip" ? 1 : 0);
            Keyword(m, "_ALPHATEST_ON", alpha == "clip");
            bool transparent = alpha == "blend";
            Keyword(m, "_SURFACE_TYPE_TRANSPARENT", transparent);
            m.SetFloat("_Surface", transparent ? 1 : 0);
            m.SetFloat("_SrcBlend", transparent ? (float)BlendMode.SrcAlpha : (float)BlendMode.One);
            m.SetFloat("_DstBlend", transparent ? (float)BlendMode.OneMinusSrcAlpha : (float)BlendMode.Zero);
            m.SetFloat("_ZWrite", transparent ? 0 : 1);
            m.SetOverrideTag("RenderType", transparent ? "Transparent" : alpha == "clip" ? "TransparentCutout" : "Opaque");
            m.renderQueue = transparent ? (int)RenderQueue.Transparent : alpha == "clip" ? (int)RenderQueue.AlphaTest : -1;
            m.SetShaderPassEnabled("ShadowCaster", !(d["no_shadow"] != null && (bool)d["no_shadow"]) && !transparent);
            m.SetFloat("_Cull", (bool)d["double_sided"] ? (float)CullMode.Off : (float)CullMode.Back);
            m.enableInstancing = true;
        }

        /// <summary>KitTerrain: the vk_terrain recipes. Images bind by name: T_VK_Grass_BC -> _GrassMap, T_VK_Grass_H (or _R) -> _GrassH,
        /// T_VK_StoneBlock_* -> _Stone*, T_VK_TerrainMacro -> _MacroMap, *GroundCtl* -> _CtlMap.</summary>
        static void FillTerrain(Material m, JObject d)
        {
            string recipe = (string)d["recipe"];
            foreach (var kw in new[]{"_KT_TERRAIN", "_KT_STAIR", "_KT_PAVING", "_KT_WATER"}) m.DisableKeyword(kw);
            m.EnableKeyword("_KT_" + recipe.ToUpperInvariant());
            m.SetFloat("_KT", new[]{"terrain", "stair", "paving", "water"}.ToList().IndexOf(recipe));
            if (d["images"] is JObject imgs)
                foreach (var kv in imgs)
                {
                    string prop = TerrainProp(kv.Key);
                    if (prop == null) { Log.AppendLine($"  {m.name}: image {kv.Key} has no KitTerrain slot"); continue; }
                    m.SetTexture(prop, Tex(kv.Value));
                }
            if (d["ctl_scale"] is JArray cs) m.SetVector("_CtlScale", new Vector4((float)cs[0], (float)cs[1]));
            bool box = d["box"] != null && (bool)d["box"];
            m.SetFloat("_Box", box ? 1 : 0); Keyword(m, "_KT_BOX", box);
            if (d["proj_scale"] != null) m.SetFloat("_ProjScale", (float)d["proj_scale"]);
            m.SetFloat("_Rough", (float)d["roughness"]);
            if (d["bump_strength"] != null) m.SetFloat("_BumpStrength", (float)d["bump_strength"]);
            bool water = recipe == "water";
            m.SetFloat("_Alpha", water ? (float)d["base_color"][3] : 1f);
            m.SetFloat("_SrcBlend", water ? (float)BlendMode.SrcAlpha : (float)BlendMode.One);
            m.SetFloat("_DstBlend", water ? (float)BlendMode.OneMinusSrcAlpha : (float)BlendMode.Zero);
            m.SetFloat("_ZWrite", water ? 0 : 1);
            m.SetOverrideTag("RenderType", water ? "Transparent" : "Opaque");
            m.renderQueue = water ? (int)RenderQueue.Transparent : -1;
            m.SetShaderPassEnabled("ShadowCaster", !water);
            m.enableInstancing = true;
        }

        static string TerrainProp(string image)
        {
            if (image.Contains("GroundCtl")) return "_CtlMap";
            if (image.Contains("TerrainMacro")) return "_MacroMap";
            var mt = System.Text.RegularExpressions.Regex.Match(image, @"^T_VK_([A-Za-z]+)_(BC|H|R)$");
            if (!mt.Success) return null;
            string key = mt.Groups[1].Value == "StoneBlock" ? "Stone" : mt.Groups[1].Value;
            if (!new[]{"Grass", "Sand", "Dirt", "Cobble", "Cliff", "Moss", "Stone"}.Contains(key)) return null;
            return mt.Groups[2].Value == "BC" ? $"_{key}Map" : $"_{key}H";
        }

        // ------------------------------------------------------------------ prefabs
        /// <summary>where the Unity kit's pieces depart from Blender's materials: painted furniture is plain wood (the
        /// user's call, 2026-10-02: no teal chests); shutters, stalls and boats keep their paint. A style on the "shutter"
        /// slot still paints them.</summary>
        static readonly Dictionary<string, (string from, string to)> MaterialDefaults = new Dictionary<string, (string, string)>
        {
            ["SM_VKI_Prop_Chest"] = ("M_VK_Shutter_Teal", "M_VK_Shutter_Natural"),
            ["SM_VKI_Prop_Dresser"] = ("M_VK_Shutter_Teal", "M_VK_Shutter_Natural"),
        };

        public static void BuildPrefabs() => BuildPrefabs(null);

        /// <summary>`only`: rebuild just the pieces whose name it accepts (null: all)</summary>
        public static void BuildPrefabs(System.Func<string, bool> only)
        {
            matsJson = null;
            EnsureFolder(KitPaths.Prefabs);
            AssetDatabase.Refresh();
            var pieces = ReadJson(KitPaths.Data + "/pieces.json");
            int n = 0, bad = 0;
            foreach (var kv in pieces)
            {
                if (only != null && !only(kv.Key)) continue;
                var d = (JObject)kv.Value;
                string fbx = KitPaths.Package + "/" + (string)d["fbx"];
                var mesh = AssetDatabase.LoadAllAssetsAtPath(fbx).OfType<Mesh>().FirstOrDefault();
                if (mesh == null) { Log.AppendLine("ERROR no mesh in " + fbx); bad++; continue; }
                // Unity's submesh order -> FBX material name -> the export's slot list -> the kit material
                var fbxNames = d["fbx_names"].Select(x => (string)x).ToList();
                var real = d["materials"].Select(x => (string)x).ToList();
                var subs = SubmeshMaterialNames(fbx);
                var names = subs.Select(n => fbxNames.IndexOf(n) is int i && i >= 0 ? real[i] : null).ToArray();
                if (MaterialDefaults.TryGetValue(kv.Key, out var md))
                    names = names.Select(n => n == md.from ? md.to : n).ToArray();
                if (mesh.subMeshCount != fbxNames.Count || names.Any(n => n == null))
                    Log.AppendLine($"WARN {kv.Key}: submeshes [{string.Join(",", subs)}] vs export [{string.Join(",", fbxNames)}]");
                CheckBounds(kv.Key, mesh, d["bounds_blender"]);

                var go = new GameObject(kv.Key);
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                var mr = go.AddComponent<MeshRenderer>();
                mr.sharedMaterials = names.Select(LoadMat).ToArray();
                var kp = go.AddComponent<KitPiece>();
                kp.piece = kv.Key;
                // submesh -> Blender slot (styles swap slots): Unity order -> FBX name -> export index -> slot
                var sm = (JObject)d["slot_map"];
                kp.blenderSlots = subs.Select(n =>
                {
                    int idx = fbxNames.IndexOf(n);
                    var hit = sm.Properties().FirstOrDefault(pr => (int)pr.Value == idx);
                    return hit != null ? int.Parse(hit.Name) : -1;
                }).ToArray();
                kp.props = Props(d["props"]);
                // walk-over overlays (vki_nav "none": debris, rugs, gravel, puddles) block nothing, as in the kit's walk check
                if (!(kp.Get("vki_class") == "overlay" && kp.Get("vki_nav") == "none")) AddColliders(go, kp.Get("vki_collider"));
                AddGroundFloor(go, kv.Key);
                if (names.Any(IsGroundMaterial)) go.AddComponent<MeshCollider>().sharedMesh = mesh;   // walkable terrain / paving
                string dir = $"{KitPaths.Prefabs}/{PrefabSubdir((string)d["fbx"])}";
                EnsureFolder(dir);
                PrefabUtility.SaveAsPrefabAsset(go, $"{dir}/{kv.Key}.prefab");
                Object.DestroyImmediate(go);
                n++;
            }
            AssetDatabase.SaveAssets();
            Log.AppendLine($"prefabs: {n}, failed {bad}");
        }

        /// <summary>Prefabs mirror Art/Models: "Art/Models/VKI/Wall/x.fbx" -> "VKI/Wall".</summary>
        static string PrefabSubdir(string fbx)
        {
            string dir = Path.GetDirectoryName(fbx).Replace('\\', '/');
            const string root = "Art/Models";
            return dir.StartsWith(root) ? dir.Substring(root.Length).TrimStart('/') : dir;
        }

        /// <summary>The Blender material name of each submesh, in Unity's submesh order (from the FBX's embedded materials).</summary>
        static string[] SubmeshMaterialNames(string fbx)
        {
            var go = AssetDatabase.LoadAssetAtPath<GameObject>(fbx);
            var r = go != null ? go.GetComponentInChildren<MeshRenderer>() : null;
            return r == null ? new string[0] : r.sharedMaterials.Select(m => m != null ? m.name : null).ToArray();
        }

        static JObject matsJson;

        static bool IsGroundMaterial(string name)
        {
            if (name == null) return false;
            matsJson = matsJson ?? ReadJson(KitPaths.Data + "/materials.json");
            var r = matsJson[name]?["recipe"];
            return r != null && r.Type == JTokenType.String && (string)r != "water";
        }

        static readonly Dictionary<string, Material> MatCache = new Dictionary<string, Material>();

        static Material LoadMat(string name)
        {
            if (name == null) return null;
            if (MatCache.TryGetValue(name, out var m) && m != null) return m;
            m = AssetDatabase.LoadAssetAtPath<Material>($"{KitPaths.Materials}/{name}.mat");
            if (m == null) Log.AppendLine("  missing material " + name);
            MatCache[name] = m;
            return m;
        }

        static List<KitProp> Props(JToken t)
        {
            var list = new List<KitProp>();
            if (t is JObject o)
                foreach (var kv in o)
                    list.Add(new KitProp
                    {
                        key = kv.Key,
                        value = kv.Value.Type == JTokenType.String ? (string)kv.Value
                            : kv.Value.ToString(Newtonsoft.Json.Formatting.None)
                    });
            return list;
        }

        /// <summary>vki_collider: boxes [cx, cy, cz, sx, sy, sz] in Blender piece space -> Unity (-x, z, -y).</summary>
        static void AddColliders(GameObject go, string json)
        {
            if (string.IsNullOrEmpty(json)) return;
            JArray boxes;
            try { boxes = JArray.Parse(json); } catch { Log.AppendLine($"WARN {go.name}: bad vki_collider"); return; }
            foreach (var b in boxes)
            {
                var c = go.AddComponent<BoxCollider>();
                c.center = new Vector3(-(float)b[0], (float)b[2], -(float)b[1]);
                c.size = new Vector3(Mathf.Abs((float)b[3]), Mathf.Abs((float)b[5]), Mathf.Abs((float)b[4]));
            }
        }

        /// <summary>A chasm / stream ground tile (SM_VKI_Ground_Cave|Stream_SWSENENW...) owns the floor of its open quarters
        /// (the cave layout lays no Floor_075 there), but its vki_collider only blocks the chasm: the open quarters get a
        /// walkable slab (top at floor level), so walkers and navmeshes have floor right up to the chasm's edge.</summary>
        static void AddGroundFloor(GameObject go, string name)
        {
            var m = System.Text.RegularExpressions.Regex.Match(name, @"^SM_VKI_Ground_(Cave|Stream)_([OX]{4})(_|$)");
            if (!m.Success) return;
            string code = m.Groups[2].Value;
            var quarter = new[] { (-0.375f, -0.375f), (0.375f, -0.375f), (0.375f, 0.375f), (-0.375f, 0.375f) };   // SW SE NE NW, Blender x / y
            for (int i = 0; i < 4; i++)
            {
                if (code[i] != 'O') continue;
                var c = go.AddComponent<BoxCollider>();
                c.center = new Vector3(-quarter[i].Item1, -0.05f, -quarter[i].Item2);
                c.size = new Vector3(0.75f, 0.1f, 0.75f);
            }
        }

        static int boundsChecked, boundsBad;

        /// <summary>The exporter's axis contract: Unity vertex = (-x, z, -y) of the Blender vertex.</summary>
        static void CheckBounds(string name, Mesh mesh, JToken bb)
        {
            if (bb == null) return;
            var lo = V3(bb[0]); var hi = V3(bb[1]);
            var eMin = new Vector3(-hi.x, lo.z, -hi.y);
            var eMax = new Vector3(-lo.x, hi.z, -lo.y);
            boundsChecked++;
            if ((mesh.bounds.min - eMin).magnitude > 0.002f || (mesh.bounds.max - eMax).magnitude > 0.002f)
            {
                boundsBad++;
                if (boundsBad <= 5)
                    Log.AppendLine($"WARN bounds {name}: unity {mesh.bounds.min:F3}..{mesh.bounds.max:F3} expected {eMin:F3}..{eMax:F3}");
            }
        }

        // ------------------------------------------------------------------ levels
        public static string BuildLevel(string name)
        {
            var lv = ReadJson($"{KitPaths.Data}/Levels/{name}.json");
            var pieces = ReadJson(KitPaths.Data + "/pieces.json");
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("Level_" + name);
            var level = root.AddComponent<KitLevel>();
            level.levelName = name;
            level.blenderScene = (string)lv["scene"];
            level.exportVersion = (string)lv["version"];
            level.props = Props(lv["root"]);
            level.world = AssetDatabase.LoadAssetAtPath<KitWorld>(WorldAsset);
            var worldLevel = level.world != null ? level.world.Find(name) : null;

            var (placed, missing) = Populate(name, lv, pieces, root.transform, worldLevel, true);
            int cut = KitDecks.Apply(root.transform);      // bridges over chasms / channels: walkable decks
            if (cut > 0) Log.AppendLine($"  {name}: {cut} ground colliders cut round bridge decks");
            foreach (var c in lv["cameras"]) AddCamera(c, root.transform);
            SetupEnvironment(lv, root.transform);

            EnsureFolder(KitPaths.Levels);
            string path = $"{KitPaths.Levels}/{name}.unity";
            EditorSceneManager.SaveScene(scene, path);
            Log.AppendLine($"level {name}: {placed} pieces, {missing} missing, {lv["markers"].Count()} markers, {lv["lights"].Count()} lights -> {path}");
            return path;
        }

        /// <summary>The placements, markers and lights of an exported level or structure, under `root`
        /// (grouped by Blender collection when `grouped`).</summary>
        static (int placed, int missing) Populate(string name, JObject lv, JObject pieces, Transform root, KitWorld.Level worldLevel, bool grouped)
        {
            var groups = new Dictionary<string, Transform>();
            Transform Group(JToken coll)
            {
                if (!grouped) return root;
                string c = (string)coll ?? "Level";
                if (!groups.TryGetValue(c, out var t))
                {
                    t = new GameObject(c).transform;
                    t.SetParent(root, false);
                    groups[c] = t;
                }
                return t;
            }

            var prefabCache = new Dictionary<string, GameObject>();
            int placed = 0, missing = 0;
            foreach (var p in lv["placements"])
            {
                string pn = (string)p["piece"];
                if (!prefabCache.TryGetValue(pn, out var prefab))
                {
                    var pd = pieces[pn];
                    string dir = pd != null ? PrefabSubdir((string)pd["fbx"]) : "";
                    prefab = AssetDatabase.LoadAssetAtPath<GameObject>($"{KitPaths.Prefabs}/{dir}/{pn}.prefab");
                    prefabCache[pn] = prefab;
                }
                if (prefab == null) { missing++; Log.AppendLine($"  {name}: no prefab {pn}"); continue; }
                var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, Group(p["coll"]));
                go.name = (string)p["name"];
                go.transform.SetPositionAndRotation(V3(p["p"]), Q(p["r"]));
                go.transform.localScale = V3(p["s"]);
                var ov = p["mat"] as JObject;
                if (ov != null && ov.Count > 0)
                {
                    // Blender slot -> exported material index -> its name -> Unity submesh carrying that name
                    var pd = pieces[pn];
                    var exported = pd["fbx_names"].Select(x => (string)x).ToList();
                    var subNames = SubmeshMaterialNames(KitPaths.Package + "/" + (string)pd["fbx"]).ToList();
                    var slotMap = new JObject();
                    foreach (var sm in (JObject)pd["slot_map"])
                        slotMap[sm.Key] = subNames.IndexOf(exported[(int)sm.Value]);
                    var mr = go.GetComponent<MeshRenderer>();
                    var arr = mr.sharedMaterials;
                    var setBy = new Dictionary<int, string>();
                    foreach (var kv in ov)
                    {
                        var k = slotMap[kv.Key];
                        if (k == null || (int)k < 0) { Log.AppendLine($"  {go.name}: override on unused slot {kv.Key}"); continue; }
                        int sub = (int)k;
                        string mn = (string)kv.Value;
                        if (setBy.TryGetValue(sub, out var prev) && prev != mn)
                            Log.AppendLine($"  {go.name}: slots sharing submesh {sub} restyled differently ({prev} / {mn})");
                        setBy[sub] = mn;
                        if (sub < arr.Length) arr[sub] = LoadMat(mn);
                    }
                    mr.sharedMaterials = arr;
                }
                var ip = p["props"] as JObject;
                if (ip != null && ip.Count > 0) go.GetComponent<KitPiece>().props = Props(ip);
                if (ip != null && ip["vki_link"] != null) AddLink(go, ip, worldLevel);
                placed++;
            }

            foreach (var mk in lv["markers"])
            {
                var go = new GameObject((string)mk["name"]);
                go.transform.SetParent(Group(mk["coll"]), false);
                go.transform.SetPositionAndRotation(V3(mk["p"]), Q(mk["r"]));
                var m = go.AddComponent<KitMarker>();
                m.props = Props(mk["props"]);
                string n = go.name;
                if (mk["props"]?["vki_spawn_id"] != null)
                {
                    var sp = go.AddComponent<KitSpawn>();
                    sp.spawnId = (string)mk["props"]["vki_spawn_id"];
                    sp.facingDeg = mk["props"]["vki_facing_deg"] != null ? (float)mk["props"]["vki_facing_deg"] : 0f;
                    go.transform.rotation = KitSpawn.FromBearing(sp.facingDeg);
                }
                m.kind = n.StartsWith("SPN_") ? KitMarker.Kind.Spawn : n.StartsWith("LGT_") ? KitMarker.Kind.LightAnchor
                    : n.StartsWith("FXA_") ? KitMarker.Kind.FxAnchor : n.StartsWith("VKI_Root") ? KitMarker.Kind.Root
                    : KitMarker.Kind.Other;
            }

            foreach (var l in lv["lights"]) AddLight(l, Group(l["coll"]));
            return (placed, missing);
        }

        // ------------------------------------------------------------------ premade structures
        public const string StructuresFolder = KitPaths.Generated + "/Structures";

        [MenuItem("Tools/Medieval Kit/Build Structures")]
        public static void BuildStructuresMenu() { Log.Clear(); BuildStructures(); WriteReport(); }

        /// <summary>Data/Structures/*.json (vkx_export_structures) -> Generated/Structures/<name>.prefab: the kit
        /// pieces as nested prefab instances (restyled where Blender restyled them), lights included.</summary>
        public static void BuildStructures()
        {
            string dir = Abs(KitPaths.Data + "/Structures");
            if (!Directory.Exists(dir)) return;
            EnsureFolder(StructuresFolder);
            var pieces = ReadJson(KitPaths.Data + "/pieces.json");
            int n = 0;
            foreach (var f in Directory.GetFiles(dir, "*.json").OrderBy(x => x))
            {
                string name = Path.GetFileNameWithoutExtension(f);
                var sj = ReadJson($"{KitPaths.Data}/Structures/{name}.json");
                var root = new GameObject(name);
                var st = root.AddComponent<KitStructure>();
                st.structureName = name;
                st.builder = (string)sj["builder"];
                st.exportVersion = (string)sj["version"];
                var (placed, missing) = Populate(name, sj, pieces, root.transform, null, false);
                PrefabUtility.SaveAsPrefabAsset(root, $"{StructuresFolder}/{name}.prefab");
                Object.DestroyImmediate(root);
                if (missing > 0) Log.AppendLine($"  structure {name}: {missing} missing pieces");
                n++;
            }
            AssetDatabase.SaveAssets();
            Log.AppendLine($"structures: {n} prefabs -> {StructuresFolder}");
        }

        /// <summary>A link piece (vki_link) becomes a KitLink with its trigger box (vki_trigger, Blender piece space).</summary>
        static void AddLink(GameObject go, JObject ip, KitWorld.Level worldLevel)
        {
            var l = go.AddComponent<KitLink>();
            l.linkId = (string)ip["vki_link_id"];
            l.kind = (string)ip["vki_link"];
            l.target = (string)ip["vki_target"];
            l.prompt = (string)ip["vki_prompt"] ?? "Enter";
            l.facingMin = ip["vki_facing_min"] != null ? (float)ip["vki_facing_min"] : 60f;
            var wl = worldLevel?.links.Find(x => x.id == l.linkId);
            if (wl != null) { l.arrive = wl.arrive; if (wl.target != l.target) Log.AppendLine($"  {go.name}: target {l.target} vs world graph {wl.target}"); }
            var tj = ip["vki_trigger"];
            JArray b = tj == null ? null : tj.Type == JTokenType.String ? JArray.Parse((string)tj) : tj as JArray;
            if (b == null || b.Count < 6) { Log.AppendLine($"  {go.name}: link without vki_trigger"); return; }
            var c = go.AddComponent<BoxCollider>();
            c.isTrigger = true;
            c.center = new Vector3(-(float)b[0], (float)b[2], -(float)b[1]);
            c.size = new Vector3(Mathf.Abs((float)b[3]), Mathf.Abs((float)b[5]), Mathf.Abs((float)b[4]));
        }

        // Blender lights are radiometric (W, W/m2) and diffuse is albedo/pi; URP's diffuse is albedo x intensity.
        //   point / spot: I = P / (4 pi) W/sr  ->  intensity = P / (4 pi^2)
        //   sun:          E = S W/m2           ->  intensity = S / pi
        static void AddLight(JToken l, Transform parent)
        {
            var go = new GameObject((string)l["name"]);
            go.transform.SetParent(parent, false);
            var q = Q(l["r"]);
            go.transform.SetPositionAndRotation(V3(l["p"]), Quaternion.LookRotation(q * Vector3.down, q * Vector3.back));
            var L = go.AddComponent<Light>();
            string type = (string)l["type"];
            float e = (float)l["energy"];
            L.color = Lin(l["color"]);
            switch (type)
            {
                case "SUN":
                    L.type = LightType.Directional; L.intensity = e / Mathf.PI; break;
                case "SPOT":
                    L.type = LightType.Spot; L.intensity = e / (4 * Mathf.PI * Mathf.PI);
                    L.spotAngle = (float)l["spot_size"];
                    L.innerSpotAngle = L.spotAngle * (1 - (float)l["spot_blend"]);
                    break;
                default:
                    L.type = LightType.Point; L.intensity = e / (4 * Mathf.PI * Mathf.PI); break;
            }
            if (L.type != LightType.Directional)
                L.range = Mathf.Clamp(10f * Mathf.Sqrt(L.intensity), 1.5f, 60f);    // falls to ~1 % of 1 m intensity
            L.shadows = (bool)l["shadow"] ? LightShadows.Soft : LightShadows.None;
            L.lightmapBakeType = LightmapBakeType.Realtime;
        }

        static void AddCamera(JToken c, Transform parent)
        {
            var go = new GameObject((string)c["name"]);
            go.transform.SetParent(parent, false);
            var q = Q(c["r"]);
            go.transform.SetPositionAndRotation(V3(c["p"]), Quaternion.LookRotation(q * Vector3.down, q * Vector3.back));
            var cam = go.AddComponent<Camera>();
            float aspect = (float)c["aspect"];
            if ((string)c["type"] == "ORTHO")
            {
                cam.orthographic = true;
                cam.orthographicSize = (float)c["ortho_scale"] / 2f / Mathf.Max(1f, aspect);
            }
            else cam.fieldOfView = (float)c["fov_deg"];
            cam.nearClipPlane = (float)c["clip"][0];
            cam.farClipPlane = (float)c["clip"][1];
            cam.allowHDR = true;
            var data = go.AddComponent<UniversalAdditionalCameraData>();
            data.renderPostProcessing = true;
            data.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
            if ((bool)c["active"]) go.tag = "MainCamera";
            else go.SetActive(false);
        }

        static void SetupEnvironment(JObject lv, Transform parent)
        {
            var w = lv["world"] as JObject;
            Color amb = Color.black, back = Color.black;
            if (w != null)
            {
                var col = w["color"].Select(x => (float)x).ToArray();
                float s = (float)w["strength"];
                amb = new Color(col[0] * s, col[1] * s, col[2] * s).gamma;
                back = w["camera_color"] != null ? Lin(w["camera_color"]) : amb;
                if ((bool)w["linked"]) Log.AppendLine($"  {lv["name"]}: world background is a node network; ambient is approximate");
            }
            if (w != null && w["trilight"] is JObject tri)
            {
                // a sky network, probed in Blender: sky / horizon / ground averages of its lighting branch
                RenderSettings.ambientMode = AmbientMode.Trilight;
                RenderSettings.ambientSkyColor = Lin(tri["sky"]);
                RenderSettings.ambientEquatorColor = Lin(tri["equator"]);
                RenderSettings.ambientGroundColor = Lin(tri["ground"]);
            }
            else
            {
                RenderSettings.ambientMode = AmbientMode.Flat;
                RenderSettings.ambientLight = amb;
            }
            RenderSettings.skybox = null;
            RenderSettings.defaultReflectionMode = DefaultReflectionMode.Custom;
            RenderSettings.reflectionIntensity = 0f;
            foreach (var cam in Object.FindObjectsByType<Camera>(FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                cam.clearFlags = CameraClearFlags.SolidColor;
                cam.backgroundColor = back;
            }

            // post: Blender's view transform -- AgX through KitAgX (exposure + look contrast), else plain exposure
            var vgo = new GameObject("PostProcess");
            vgo.transform.SetParent(parent, false);
            var vol = vgo.AddComponent<Volume>();
            vol.isGlobal = true;
            var profile = ScriptableObject.CreateInstance<VolumeProfile>();
            profile.name = "Kit_" + lv["name"];
            string view = (string)lv["view_transform"];
            var tm = profile.Add<Tonemapping>(true);
            if (view == "AgX")
            {
                tm.mode.Override(TonemappingMode.None);         // KitAgX replaces URP's curve
                var agx = profile.Add<KitAgX>(true);
                agx.enabled.Override(true);
                agx.exposure.Override(lv["exposure"] != null ? (float)lv["exposure"] : 0f);
                agx.contrast.Override(AgxLookContrast((string)lv["look"]));
            }
            else
            {
                tm.mode.Override(TonemappingMode.None);
                var ca = profile.Add<ColorAdjustments>(true);
                ca.postExposure.Override(lv["exposure"] != null ? (float)lv["exposure"] : 0f);
                if (view != "Standard") Log.AppendLine($"  {lv["name"]}: view transform {view} not ported");
            }
            string ppath = $"{KitPaths.Levels}/{lv["name"]}_Profile.asset";
            AssetDatabase.DeleteAsset(ppath);
            EnsureFolder(KitPaths.Levels);
            AssetDatabase.CreateAsset(profile, ppath);
            foreach (var comp in profile.components) AssetDatabase.AddObjectToAsset(comp, profile);
            AssetDatabase.SaveAssets();
            vol.sharedProfile = profile;
        }

        static float AgxLookContrast(string look)
        {
            if (string.IsNullOrEmpty(look) || look == "None") return 1f;
            if (look.EndsWith("Very High Contrast")) return 1.57f;
            if (look.EndsWith("Medium High Contrast")) return 1.2f;
            if (look.EndsWith("High Contrast")) return 1.4f;
            if (look.EndsWith("Very Low Contrast")) return 0.6f;
            if (look.EndsWith("Medium Low Contrast")) return 0.9f;
            if (look.EndsWith("Low Contrast")) return 0.8f;
            return 1f;
        }

        /// <summary>Adds KitAgXFeature to every URP renderer in the project (it only runs where a volume enables KitAgX).</summary>
        [MenuItem("Tools/Medieval Kit/Install AgX Renderer Feature")]
        public static void InstallAgxFeature()
        {
            foreach (var guid in AssetDatabase.FindAssets("t:UniversalRendererData"))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (!path.StartsWith("Assets/")) continue;
                var data = AssetDatabase.LoadAssetAtPath<UniversalRendererData>(path);
                if (data.rendererFeatures.Any(f => f is KitAgXFeature)) continue;
                var feat = ScriptableObject.CreateInstance<KitAgXFeature>();
                feat.name = "KitAgX";
                feat.shader = Shader.Find("Hidden/MedievalKit/AgX");
                AssetDatabase.AddObjectToAsset(feat, data);
                data.rendererFeatures.Add(feat);
                data.SetDirty();
                EditorUtility.SetDirty(data);
                Log.AppendLine("AgX feature added to " + path);
            }
            AssetDatabase.SaveAssets();
        }

        static void WriteReport()
        {
            Log.AppendLine($"bounds check: {boundsChecked} pieces, {boundsBad} off");
            boundsChecked = boundsBad = 0;
            Directory.CreateDirectory("Logs/MedievalKit");
            File.WriteAllText("Logs/MedievalKit/build_report.txt", Log.ToString());
            Debug.Log("[MedievalKit] build report:\n" + Log);
        }
    }
}
