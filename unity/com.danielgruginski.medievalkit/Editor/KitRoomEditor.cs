using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;

namespace MedievalKit.Editor
{
    /// <summary>Room tooling: the interior rules asset from Data/interior_rules.json, the KitRoom inspector, and the
    /// golden test that rebuilds the kit's walled rooms and compares them with the levels Blender exported.</summary>
    [InitializeOnLoad]
    public static class KitRoomTools
    {
        public const string RulesAsset = KitPaths.Generated + "/KitInteriorRules.asset";

        static KitRoomTools()
        {
            KitRoom.Spawn = (prefab, parent) =>
                Application.isPlaying ? Object.Instantiate(prefab, parent) : (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
        }

        static string Abs(string p) => Path.GetFullPath(p);

        [MenuItem("Tools/Medieval Kit/Build Interior Rules")]
        public static void BuildRulesMenu()
        {
            var log = new StringBuilder();
            BuildRules(log);
            Debug.Log(log.ToString());
        }

        /// <summary>Data/interior_rules.json -> Generated/KitInteriorRules.asset: the JSON, every interior (VKI) and
        /// exterior (VK, reused props) piece prefab by name, every style material by name.</summary>
        public static KitInteriorRules BuildRules(StringBuilder log)
        {
            string jp = KitPaths.Data + "/interior_rules.json";
            if (!File.Exists(Abs(jp))) { log?.AppendLine("no interior_rules.json"); return null; }
            var r = AssetDatabase.LoadAssetAtPath<KitInteriorRules>(RulesAsset);
            bool isNew = r == null;
            if (isNew) r = ScriptableObject.CreateInstance<KitInteriorRules>();
            r.rulesJson = AssetDatabase.LoadAssetAtPath<TextAsset>(jp);
            r.pieces.Clear();
            var dirs = new[] { KitPaths.Prefabs + "/VKI", KitPaths.Prefabs + "/VK" }.Where(AssetDatabase.IsValidFolder).ToArray();
            foreach (var g in AssetDatabase.FindAssets("t:Prefab", dirs))
            {
                var path = AssetDatabase.GUIDToAssetPath(g);
                var go = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                if (go != null && go.GetComponent<KitPiece>() != null) r.pieces.Add(new KitInteriorRules.PieceRef { name = go.name, prefab = go });
            }
            r.pieces.Sort((a, b) => string.CompareOrdinal(a.name, b.name));
            var j = JObject.Parse(File.ReadAllText(Abs(jp)));
            var names = new SortedSet<string>();
            foreach (var key in (JObject)j["styles"])
                foreach (var v in (JObject)key.Value)
                    if (v.Value.Type == JTokenType.String) names.Add((string)v.Value);
            r.materials.Clear();
            int missing = 0;
            foreach (var mn in names)
            {
                var m = AssetDatabase.LoadAssetAtPath<Material>($"{KitPaths.Materials}/{mn}.mat");
                if (m == null) { missing++; log?.AppendLine($"  interior rules: no material {mn}"); continue; }
                r.materials.Add(new KitInteriorRules.MatRef { name = mn, material = m });
            }
            if (isNew) AssetDatabase.CreateAsset(r, RulesAsset);
            else EditorUtility.SetDirty(r);
            AssetDatabase.SaveAssets();
            log?.AppendLine($"interior rules: {r.pieces.Count} pieces, {r.materials.Count} style materials ({missing} missing), " +
                            $"{((JObject)j["rooms"]).Count} room presets -> {RulesAsset}");
            return r;
        }

        [MenuItem("GameObject/Medieval Kit/Room From Plan", false, 10)]
        static void CreateRoom(MenuCommand cmd)
        {
            var go = new GameObject("Room");
            GameObjectUtility.SetParentAndAlign(go, cmd.context as GameObject);
            var room = go.AddComponent<KitRoom>();
            room.rules = AssetDatabase.LoadAssetAtPath<KitInteriorRules>(RulesAsset);
            if (room.rules != null) room.LoadPreset(room.rules.RoomNames.FirstOrDefault(n => n.Contains("Cottage")) ?? room.rules.RoomNames.First());
            Undo.RegisterCreatedObjectUndo(go, "Room From Plan");
            Selection.activeObject = go;
        }

        public const string ShowcaseFolder = "Assets/MedievalKitRooms";

        /// <summary>a small room typed by hand: bed, chest, table (forms come with it), barrel, log basket</summary>
        public const string DemoPlan =
            "      0  1  2  3\n" +
            "     +##+WW+##+##+\n" +
            "   2 #BX BX .. CH#\n" +
            "     +           +\n" +
            "   1 #.. TB TB ..W\n" +
            "     +           +\n" +
            "   0 #ba .. .. WP#\n" +
            "     +==+ee+==+==+\n";

        [MenuItem("Tools/Medieval Kit/Rooms/Build Room Showcase")]
        public static void BuildShowcaseMenu() => BuildShowcase();

        /// <summary>Assets/MedievalKitRooms/RoomShowcase.unity: a KitRoom per walled kit room preset, generated,
        /// in rows, with the interior lighting (sun key / fill, AgX volume) of VKI_Hovel_F0; then four of them again
        /// furnished from their plan codes alone.</summary>
        public static string BuildShowcase()
        {
            var scene = UnityEditor.SceneManagement.EditorSceneManager.NewScene(UnityEditor.SceneManagement.NewSceneSetup.DefaultGameObjects,
                                                                                UnityEditor.SceneManagement.NewSceneMode.Single);
            var rules = AssetDatabase.LoadAssetAtPath<KitInteriorRules>(RulesAsset);     // after the scene switch
            if (rules == null) { Debug.LogError("[MedievalKit] no interior rules: run Build Interior Rules"); return null; }
            string lit = $"{KitPaths.Levels}/VKI_Hovel_F0.unity";
            if (File.Exists(Abs(lit))) KitHouseTools.CopyLighting(scene, lit, l => l.type == LightType.Directional);
            float x = 0f, z = 0f, rowDepth = 0f;
            const float rowWidth = 60f, gap = 4f;
            foreach (var name in rules.RoomNames)
            {
                var R = rules.Room(name);
                if ((bool?)R["cave"] == true) continue;
                var go = new GameObject(name);
                var room = go.AddComponent<KitRoom>();
                room.rules = rules;
                room.LoadPreset(name);
                room.Generate();
                float w = room.Layout.W, d = room.Layout.D;
                if (x > 0f && x + w > rowWidth) { x = 0f; z += rowDepth + gap; rowDepth = 0f; }
                // Blender room space runs to -x / -z in Unity: put the room's (0, 0) corner at the far side of its slot
                go.transform.position = new Vector3(-x, 0f, -z);
                x += w + gap;
                rowDepth = Mathf.Max(rowDepth, d);
            }
            // a last row furnished from the plans' cell codes alone (Furniture = Codes), to compare with the rooms above
            x = 0f; z += rowDepth + gap * 2; rowDepth = 0f;
            foreach (var name in new[] { "VKI_Cottage_F0", "VKI_Tavern_F0", "VKI_Smithy_F0", "VKI_Dungeon_B1" })
            {
                if (rules.Room(name) == null) continue;
                var go = new GameObject(name + " (from codes)");
                var room = go.AddComponent<KitRoom>();
                room.rules = rules;
                room.LoadPreset(name);
                room.furniture = KitRoom.Furniture.Codes;
                room.Generate();
                go.transform.position = new Vector3(-x, 0f, -z);
                x += room.Layout.W + gap;
                rowDepth = Mathf.Max(rowDepth, room.Layout.D);
            }
            // the cave levels (cave maps: rock tiles, chasm, channels, tunnels), then two caves from the generator
            x = 0f; z += rowDepth + gap * 2; rowDepth = 0f;
            void Place(KitRoom room)
            {
                if (x > 0f && x + room.Layout.W > rowWidth) { x = 0f; z += rowDepth + gap; rowDepth = 0f; }
                room.transform.position = new Vector3(-x, 0f, -z);
                x += room.Layout.W + gap;
                rowDepth = Mathf.Max(rowDepth, room.Layout.D);
            }
            foreach (var name in rules.RoomNames.Where(n => (bool?)rules.Room(n)["cave"] == true))
            {
                var room = new GameObject(name).AddComponent<KitRoom>();
                room.rules = rules;
                room.LoadPreset(name);
                room.Generate();
                Place(room);
            }
            foreach (var seed in new[] { 7, 31 })
            {
                var room = new GameObject($"Random cave (seed {seed})").AddComponent<KitRoom>();
                room.rules = rules;
                room.cave.seed = seed;
                room.cave.poi = seed == 31 ? "POI_WyrmBones" : null;
                room.RandomCave();
                Place(room);
            }
            // random house ground floors (KitInteriorGenerator)
            x = 0f; z += rowDepth + gap * 2; rowDepth = 0f;
            foreach (var (kind, seed) in new[] { ("Cottage", 3), ("Townhouse", 8), ("Tavern", 5), ("Workshop", 2), ("Cottage", 14), ("Townhouse", 21) })
            {
                var room = new GameObject($"Random {kind} (seed {seed})").AddComponent<KitRoom>();
                room.rules = rules;
                room.interior.kind = kind;
                room.interior.seed = seed;
                room.RandomInterior();
                Place(room);
            }
            x = 0f; z += rowDepth + gap; rowDepth = 0f;
            {
                // and a plan typed from scratch, no record: defaults for walls and floor, furniture from its codes
                var go = new GameObject("Typed plan (no record)");
                var room = go.AddComponent<KitRoom>();
                room.rules = rules;
                room.plan = DemoPlan;
                room.Generate();
                go.transform.position = new Vector3(-x, 0f, -z);
            }
            var cam = Camera.main;
            if (cam != null)
            {
                cam.transform.SetPositionAndRotation(new Vector3(-30f, 38f, 22f), Quaternion.Euler(50f, 180f, 0f));
                cam.farClipPlane = 200f;
            }
            Directory.CreateDirectory(ShowcaseFolder);
            string path = $"{ShowcaseFolder}/RoomShowcase.unity";
            UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene, path);
            return path;
        }

        [MenuItem("Tools/Medieval Kit/Rooms/Build Dungeon Showcase")]
        public static void BuildDungeonShowcaseMenu() => BuildDungeonShowcase();

        /// <summary>Assets/MedievalKitRooms/DungeonShowcase.unity: three generated dungeon levels (Dungeon, Crypt, Warren)
        /// side by side, lit like VKI_Dungeon_B1 (its suns and AgX volume; the torches are the rooms' own).</summary>
        public static string BuildDungeonShowcase()
        {
            var scene = UnityEditor.SceneManagement.EditorSceneManager.NewScene(UnityEditor.SceneManagement.NewSceneSetup.DefaultGameObjects,
                                                                                UnityEditor.SceneManagement.NewSceneMode.Single);
            var rules = AssetDatabase.LoadAssetAtPath<KitInteriorRules>(RulesAsset);
            if (rules == null) { Debug.LogError("[MedievalKit] no interior rules: run Build Interior Rules"); return null; }
            string lit = $"{KitPaths.Levels}/VKI_Dungeon_B1.unity";
            if (File.Exists(Abs(lit))) KitHouseTools.CopyLighting(scene, lit, l => l.type == LightType.Directional);
            float x = 0f;
            foreach (var (theme, seed) in new[] { ("Dungeon", 11), ("Crypt", 5), ("Warren", 9) })
            {
                var room = new GameObject($"Dungeon {theme} (seed {seed})").AddComponent<KitRoom>();
                room.rules = rules;
                room.dungeon.theme = theme;
                room.dungeon.seed = seed;
                room.RandomDungeon();
                room.transform.position = new Vector3(-x, 0f, 0f);
                x += room.Layout.W + 6f;
            }
            var cam = Camera.main;
            if (cam != null)
            {
                cam.transform.SetPositionAndRotation(new Vector3(-21f, 34f, 14f), Quaternion.Euler(55f, 180f, 0f));
                cam.farClipPlane = 250f;
            }
            Directory.CreateDirectory(ShowcaseFolder);
            string path = $"{ShowcaseFolder}/DungeonShowcase.unity";
            UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene, path);
            return path;
        }

        // ------------------------------------------------------------------ walk test (navmesh)
        [MenuItem("Tools/Medieval Kit/Rooms/Walk Test (NavMesh)")]
        public static void WalkTestMenu() => Debug.Log(WalkTest());

        /// <summary>Bakes a temporary navmesh for a small humanoid (radius 0.3, height 1.8, 0.05 m voxels; the kit's doors
        /// leave 0.84 m and the rope bridge 0.88 m, so agents must stay under ~0.35 m radius and the voxels fine) from the colliders of the open scene, with UnityEngine.AI.NavMeshBuilder,
        /// and, for every KitRoom in it, finds a path from its first spawn to every other spawn and to every encounter's
        /// spawn points. Returns the report; the navmesh is removed afterwards.</summary>
        public static string WalkTest(float radius = 0.3f, float voxel = 0.05f)
        {
            var settings = UnityEngine.AI.NavMesh.CreateSettings();          // registers an agent type; the bake uses this copy
            settings.agentRadius = radius; settings.agentHeight = 1.8f; settings.agentClimb = 0.35f; settings.agentSlope = 40f;
            // the rope bridge leaves 0.88 m between its rails: at the default voxel (radius / 3) the eroded strip vanishes
            if (voxel > 0f) { settings.overrideVoxelSize = true; settings.voxelSize = voxel; }
            var sb = new StringBuilder();
            UnityEngine.AI.NavMeshDataInstance inst = default;
            try
            {
                Physics.SyncTransforms();     // rooms moved after they were built: the physics scene must see where they are now
                var rooms = Object.FindObjectsByType<KitRoom>(FindObjectsSortMode.InstanceID);
                var bounds = new Bounds(Vector3.zero, Vector3.zero);
                bool any = false;
                foreach (var r in Object.FindObjectsByType<Collider>(FindObjectsSortMode.None))
                    if (!r.isTrigger) { if (!any) { bounds = r.bounds; any = true; } else bounds.Encapsulate(r.bounds); }
                if (!any) return "walk test: no colliders";
                bounds.Expand(2f);
                var sources = new List<UnityEngine.AI.NavMeshBuildSource>();
                UnityEngine.AI.NavMeshBuilder.CollectSources(bounds, ~0, UnityEngine.AI.NavMeshCollectGeometry.PhysicsColliders, 0,
                    new List<UnityEngine.AI.NavMeshBuildMarkup>(), sources);
                // leaves the game opens (vki_openable: portcullis, iron and secret doors, gates) do not block, as in Blender's
                // check; in a game they want a carving NavMeshObstacle toggled with the door
                int openable = sources.RemoveAll(src => src.component != null &&
                    src.component.GetComponentInParent<KitPiece>()?.Get("vki_openable") is string op && op != "0" && op != "False");
                var data = UnityEngine.AI.NavMeshBuilder.BuildNavMeshData(settings, sources, bounds, Vector3.zero, Quaternion.identity);
                inst = UnityEngine.AI.NavMesh.AddNavMeshData(data);
                var filter = new UnityEngine.AI.NavMeshQueryFilter { agentTypeID = settings.agentTypeID, areaMask = UnityEngine.AI.NavMesh.AllAreas };
                bool Snap(Vector3 p, out Vector3 q)
                {
                    bool ok = UnityEngine.AI.NavMesh.SamplePosition(p, out var h, 0.8f, filter);
                    q = h.position;
                    return ok;
                }
                // the KitRooms, or (an exported level scene) the scene roots that hold spawns
                var units = rooms.Select(r => r.transform).ToList();
                if (units.Count == 0)
                    units = UnityEngine.SceneManagement.SceneManager.GetActiveScene().GetRootGameObjects()
                        .Where(g => g.GetComponentInChildren<KitSpawn>() != null).Select(g => g.transform).ToList();
                foreach (var room in units)
                {
                    var spawns = room.GetComponentsInChildren<KitSpawn>();
                    if (spawns.Length == 0) { sb.AppendLine($"{room.name}: no spawn"); continue; }
                    if (!Snap(spawns[0].transform.position, out var from)) { sb.AppendLine($"{room.name}: spawn {spawns[0].spawnId} is off the navmesh"); continue; }
                    int ok = 0, total = 0;
                    var fails = new List<string>();
                    void Try(Vector3 p, string what)
                    {
                        total++;
                        var path = new UnityEngine.AI.NavMeshPath();
                        if (Snap(p, out var to) && UnityEngine.AI.NavMesh.CalculatePath(from, to, filter, path) && path.status == UnityEngine.AI.NavMeshPathStatus.PathComplete) ok++;
                        else fails.Add(what);
                    }
                    foreach (var sp in spawns.Skip(1)) Try(sp.transform.position, "spawn " + sp.spawnId);
                    foreach (var e in room.GetComponentsInChildren<KitEncounter>())
                        foreach (var p in e.Points) Try(p.position, $"{e.encounterId}/{p.name}");
                    // islands: floor-level navmesh at the plan's cell centres (KitRooms) that the first spawn cannot reach
                    var kr = room.GetComponent<KitRoom>();
                    var cellsAt = new List<Vector3>();
                    if (kr != null && !string.IsNullOrEmpty(kr.plan))
                    {
                        var pl = KitRoomPlan.Parse(kr.plan);
                        for (int c = 0; c < pl.nc; c++)
                            for (int r = 0; r < pl.nr; r++)
                                cellsAt.Add(room.TransformPoint(new Vector3(-(1.5f * c + 0.75f), 0f, -(1.5f * r + 0.75f))));
                    }
                    int floorPts = 0, islands = 0;
                    var islandAt = new List<string>();
                    foreach (var cp in cellsAt)
                        {
                            var q = new Vector3(cp.x, from.y, cp.z);
                            if (!UnityEngine.AI.NavMesh.SamplePosition(q, out var h, 0.35f, filter) || Mathf.Abs(h.position.y - from.y) > 0.3f) continue;
                            floorPts++;
                            var path = new UnityEngine.AI.NavMeshPath();
                            if (!(UnityEngine.AI.NavMesh.CalculatePath(from, h.position, filter, path) && path.status == UnityEngine.AI.NavMeshPathStatus.PathComplete))
                            { islands++; if (islandAt.Count < 6) islandAt.Add($"{h.position.x:0.#},{h.position.z:0.#}"); }
                        }
                    sb.AppendLine($"{room.name}: from spawn {spawns[0].spawnId}, {ok}/{total} reachable" + (fails.Count > 0 ? $" (not: {string.Join(", ", fails.Take(8))})" : "") +
                                  $"; floor {floorPts - islands}/{floorPts} reachable" + (islands > 0 ? $" (islands at {string.Join(" ", islandAt)})" : ""));
                }
                if (openable > 0) sb.AppendLine($"({openable} colliders of openable leaves left out)");
            }
            finally
            {
                if (inst.valid) UnityEngine.AI.NavMesh.RemoveNavMeshData(inst);
                UnityEngine.AI.NavMesh.RemoveSettings(settings.agentTypeID);
            }
            return sb.ToString();
        }

        // ------------------------------------------------------------------ golden test
        class Item
        {
            public string piece, what; public float x, y, z, rot, tol = 0.002f; public Dictionary<string, string> mat; public bool used, debris;
        }

        static float Yaw(JToken r) => new Quaternion((float)r[0], (float)r[1], (float)r[2], (float)r[3]).eulerAngles.y;
        static float AngDiff(float a, float b) { float d = Mathf.Repeat(a - b, 360f); return Mathf.Min(d, 360f - d); }

        /// <summary>Slot -> material name where the instance's renderer differs from its prefab (the export's "mat").</summary>
        static Dictionary<string, string> Overrides(KitRoom.Placed p)
        {
            var o = new Dictionary<string, string>();
            var src = PrefabUtility.GetCorrespondingObjectFromSource(p.go);
            var mr = p.go.GetComponent<MeshRenderer>();
            if (src == null || mr == null || p.kp == null) return o;
            var a = src.GetComponent<MeshRenderer>().sharedMaterials;
            var b = mr.sharedMaterials;
            for (int i = 0; i < b.Length && i < p.kp.blenderSlots.Length; i++)
                if (a[i] != b[i] && b[i] != null) o[p.kp.blenderSlots[i].ToString()] = b[i].name;
            return o;
        }

        static string MatStr(Dictionary<string, string> m) => m == null || m.Count == 0 ? "{}" : "{" + string.Join(", ", m.OrderBy(k => int.Parse(k.Key)).Select(k => $"{k.Key}:{k.Value}")) + "}";

        [MenuItem("Tools/Medieval Kit/Rooms/Golden Test (Blender Rooms)")]
        public static void GoldenTest()
        {
            var rules = AssetDatabase.LoadAssetAtPath<KitInteriorRules>(RulesAsset);
            if (rules == null) { Debug.LogError("no KitInteriorRules: run Tools > Medieval Kit > Build Interior Rules"); return; }
            var culture = System.Threading.Thread.CurrentThread.CurrentCulture;
            System.Threading.Thread.CurrentThread.CurrentCulture = System.Globalization.CultureInfo.InvariantCulture;
            try { RunGoldenTest(rules); }
            finally { System.Threading.Thread.CurrentThread.CurrentCulture = culture; }
        }

        static void RunGoldenTest(KitInteriorRules rules)
        {
            var log = new StringBuilder();
            var summary = new StringBuilder();
            int totalOk = 0, totalBad = 0;
            var codeTot = (coded: 0, found: 0, turned: 0, extra: 0);
            foreach (var name in rules.RoomNames)
            {
                string lp = $"{KitPaths.Data}/Levels/{name}.json";
                if (!File.Exists(Abs(lp))) { summary.AppendLine($"{name}: no exported level"); continue; }
                var lv = JObject.Parse(File.ReadAllText(Abs(lp)));
                var go = new GameObject("KitRoomTest_" + name);
                try
                {
                    var room = go.AddComponent<KitRoom>();
                    room.rules = rules;
                    room.LoadPreset(name);
                    room.Generate();
                    var mine = room.placed.Select(p => new Item { piece = p.piece, what = p.what, x = p.x, y = p.y, z = p.z, rot = p.rot, mat = Overrides(p) }).ToList();
                    var theirs = new List<Item>();
                    foreach (var p in lv["placements"])
                    {
                        string coll = (string)p["coll"] ?? "";
                        string pn = (string)p["piece"];
                        if (pn.StartsWith("U_") && p["props"]?["vki_piece"] != null) pn = (string)p["props"]["vki_piece"];   // a restyle exported as its own mesh
                        theirs.Add(new Item
                        {
                            piece = pn, x = -(float)p["p"][0], y = -(float)p["p"][2], z = (float)p["p"][1], rot = -Yaw(p["r"]),
                            tol = coll.EndsWith("_Shell") ? 0.002f : 0.05f,       // props: the general idea, not to the millimetre
                            debris = coll.EndsWith("_Props") && p["props"]?["vki_prop_index"] == null && !pn.Contains("RushMat") && !pn.Contains("WindowPool"),
                            mat = ((JObject)p["mat"])?.Properties().ToDictionary(q => q.Name, q => (string)q.Value) ?? new Dictionary<string, string>()
                        });
                    }
                    var missing = new List<Item>();
                    var matBad = new List<string>();
                    foreach (var t in theirs)
                    {
                        var m = mine.FirstOrDefault(u => !u.used && u.piece == t.piece && Mathf.Abs(u.x - t.x) < t.tol && Mathf.Abs(u.y - t.y) < t.tol &&
                                                         Mathf.Abs(u.z - t.z) < t.tol && AngDiff(u.rot, t.rot) < 1f);
                        if (m == null) { missing.Add(t); continue; }
                        m.used = true;
                        if (MatStr(m.mat) != MatStr(t.mat)) matBad.Add($"{t.piece} @ {t.x:0.###},{t.y:0.###}: unity {MatStr(m.mat)} blender {MatStr(t.mat)}");
                    }
                    var extra = mine.Where(u => !u.used).ToList();
                    var debris = missing.Where(i => i.debris).ToList();         // strewn by vki_rooms_debris: not ported
                    missing = missing.Where(i => !i.debris).ToList();
                    log.AppendLine($"==== {name}");
                    // furniture from the plan's codes alone, against the record's props that have a code
                    var codes = (JObject)rules.Json["codes"];
                    string CodeOf(string piece)
                    {
                        string sn = piece.StartsWith("SM_VKI_Prop_") ? piece.Substring(12) : piece.StartsWith("SM_VKI_") ? piece.Substring(7) : piece.StartsWith("SM_VK_") ? piece.Substring(6) : piece;
                        return (string)codes[sn] ?? (string)codes["Prop_" + sn];
                    }
                    var fromCodes = room.PropsFromCodes().Select(e => (code: (string)codes[(string)e[0]], x: (float)e[1], y: (float)e[2], rot: (float)e[3], used: false)).ToList();
                    int coded = 0, found = 0, turned = 0;
                    foreach (var pr in room.placed.Where(p => p.what == "prop"))
                    {
                        string c = CodeOf(pr.piece);
                        if (c == null) continue;
                        coded++;
                        int k = fromCodes.FindIndex(e => !e.used && e.code == c && Mathf.Abs(e.x - pr.atX) <= 0.76f && Mathf.Abs(e.y - pr.atY) <= 0.76f);
                        if (k < 0) { log.AppendLine($"  codes: no {c} for {pr.piece} @ {pr.atX:0.##},{pr.atY:0.##}"); continue; }
                        var e0 = fromCodes[k]; e0.used = true; fromCodes[k] = e0;
                        found++;
                        if (AngDiff(e0.rot, pr.rot) < 1f) turned++;
                        else log.AppendLine($"  codes: {c} for {pr.piece} @ {pr.atX:0.##},{pr.atY:0.##} turned {e0.rot:0} (record {pr.rot:0})");
                    }
                    int codeExtra = fromCodes.Count(e => !e.used);
                    foreach (var e in fromCodes.Where(e => !e.used)) log.AppendLine($"  codes: extra {e.code} @ {e.x:0.##},{e.y:0.##}");
                    codeTot.coded += coded; codeTot.found += found; codeTot.turned += turned; codeTot.extra += codeExtra;
                    // spawns
                    var spB = lv["markers"].Where(mk => mk["props"]?["vki_spawn_id"] != null)
                        .Select(mk => ((string)mk["props"]["vki_spawn_id"], new Vector3((float)mk["p"][0], (float)mk["p"][1], (float)mk["p"][2]), (float)mk["props"]["vki_facing_deg"])).ToList();
                    var spU = go.GetComponentsInChildren<KitSpawn>().Select(s => (s.spawnId, s.transform.position, s.facingDeg)).ToList();
                    var spBad = new List<string>();
                    foreach (var b in spB)
                    {
                        var u = spU.FirstOrDefault(s => s.spawnId == b.Item1);
                        if (u.spawnId == null) spBad.Add($"spawn {b.Item1}: missing");
                        else if ((u.position - b.Item2).magnitude > 0.002f || AngDiff(u.facingDeg, b.Item3) > 0.5f)
                            spBad.Add($"spawn {b.Item1}: unity {u.position} {u.facingDeg} vs blender {b.Item2} {b.Item3}");
                    }
                    if (spU.Count != spB.Count) spBad.Add($"spawns: unity {spU.Count} vs blender {spB.Count}");
                    // links
                    var lkB = lv["placements"].Where(p => p["props"]?["vki_link"] != null)
                        .Select(p => $"{(string)p["props"]["vki_link_id"]}:{(string)p["props"]["vki_link"]}->{(string)p["props"]["vki_target"]}").OrderBy(s => s).ToList();
                    var lkU = go.GetComponentsInChildren<KitLink>().Select(l => $"{l.linkId}:{l.kind}->{l.target}").OrderBy(s => s).ToList();
                    string lkRes = lkB.SequenceEqual(lkU) ? "ok" : $"unity [{string.Join(", ", lkU)}] vs blender [{string.Join(", ", lkB)}]";
                    // lights (the pieces' and the props' sockets)
                    var ltB = lv["lights"].Where(l => ((string)l["name"]).StartsWith("LIT_"))
                        .Select(l => (new Vector3((float)l["p"][0], (float)l["p"][1], (float)l["p"][2]), (float)l["energy"])).ToList();
                    var ltU = room.lightsBuilt.ToList();
                    int ltOk = ltB.Count(b => ltU.Any(u => (u.pos - b.Item1).magnitude < 0.06f && Mathf.Abs(u.w - b.Item2) < 0.01f));

                    int ok = theirs.Count - debris.Count - missing.Count;
                    bool good = missing.Count == 0 && extra.Count == 0 && matBad.Count == 0 && spBad.Count == 0 && lkRes == "ok" && ltOk == ltB.Count && ltU.Count == ltB.Count;
                    if (good) totalOk++; else totalBad++;
                    summary.AppendLine($"{name}: {(good ? "OK" : "DIFF")}  pieces {ok}/{theirs.Count - debris.Count} matched, {missing.Count} missing, {extra.Count} extra, " +
                                       $"{matBad.Count} material diffs, {debris.Count} debris not ported; spawns {spB.Count - spBad.Count(s => s.StartsWith("spawn "))}/{spB.Count}; links {lkRes}; " +
                                       $"lights {ltOk}/{ltB.Count} (unity {ltU.Count}); codes found {found}/{coded} props ({turned} turned alike, {codeExtra} extra)");
                    foreach (var t in missing) log.AppendLine($"  missing (blender only): {t.piece} @ {t.x:0.###},{t.y:0.###},{t.z:0.###} rot {t.rot:0.#}");
                    foreach (var u in extra) log.AppendLine($"  extra (unity only): {u.piece} @ {u.x:0.###},{u.y:0.###},{u.z:0.###} rot {u.rot:0.#} [{u.what}]");
                    foreach (var s in matBad) log.AppendLine($"  material: {s}");
                    foreach (var s in spBad) log.AppendLine($"  {s}");
                    if (lkRes != "ok") log.AppendLine($"  links: {lkRes}");
                    foreach (var b in ltB.Where(b => !ltU.Any(u => (u.pos - b.Item1).magnitude < 0.06f && Mathf.Abs(u.w - b.Item2) < 0.01f)))
                        log.AppendLine($"  light missing: {b.Item1} {b.Item2} W");
                    foreach (var n in room.notes) log.AppendLine($"  note: {n}");
                }
                finally { Object.DestroyImmediate(go); }
            }
            summary.AppendLine($"furniture from codes alone: {codeTot.found}/{codeTot.coded} coded props found, {codeTot.turned} turned alike, {codeTot.extra} extra");
            Directory.CreateDirectory("Logs/MedievalKit");
            File.WriteAllText("Logs/MedievalKit/room_test.txt", summary + "\n" + log);
            Debug.Log($"KitRoom golden test: {totalOk} rooms match, {totalBad} differ (Logs/MedievalKit/room_test.txt)\n{summary}");
        }

        /// <summary>the LGT_ marker of a LIT_ light names its host piece</summary>
        static string HostOf(JObject lv, string lit)
        {
            var mk = lv["markers"].FirstOrDefault(m => (string)m["name"] == "LGT_" + lit.Substring(4));
            var js = (string)mk?["props"]?["vki_light"];
            string h = js != null ? (string)JObject.Parse(js)["host"] : null;
            return h != null ? System.Text.RegularExpressions.Regex.Replace(h, @"\.\d{3}$", "") : null;
        }
    }

    [CustomEditor(typeof(KitRoom))]
    public class KitRoomEditor : UnityEditor.Editor
    {
        public override void OnInspectorGUI()
        {
            var room = (KitRoom)target;
            if (room.rules == null)
            {
                EditorGUILayout.HelpBox("Assign the interior rules (Generated/KitInteriorRules.asset; Tools > Medieval Kit > Build Interior Rules makes it).", MessageType.Info);
                if (GUILayout.Button("Use the kit's rules"))
                {
                    Undo.RecordObject(room, "Room rules");
                    room.rules = AssetDatabase.LoadAssetAtPath<KitInteriorRules>(KitRoomTools.RulesAsset);
                }
            }
            else
            {
                var names = room.rules.RoomNames.ToArray();
                int i = System.Array.IndexOf(names, room.preset);
                using (new EditorGUILayout.HorizontalScope())
                {
                    int j = EditorGUILayout.Popup("Preset", i, names);
                    if (GUILayout.Button("Load", GUILayout.Width(60)) || (j != i && j >= 0))
                    {
                        Undo.RecordObject(room, "Load room preset");
                        room.LoadPreset(names[Mathf.Max(0, j)]);
                    }
                }
            }
            DrawDefaultInspector();
            using (new EditorGUI.DisabledScope(room.rules == null))
            using (new EditorGUILayout.HorizontalScope())
            {
                if (GUILayout.Button("Generate"))
                {
                    Undo.RegisterFullObjectHierarchyUndo(room.gameObject, "Generate room");
                    room.Generate();
                }
                if (GUILayout.Button(new GUIContent("Codes -> Record", "Write the furniture of the plan's cell codes into the record's prop list, to edit by hand")))
                {
                    Undo.RegisterFullObjectHierarchyUndo(room.gameObject, "Codes to record");
                    room.CodesToRecord();
                    room.Generate();
                }
                if (GUILayout.Button(new GUIContent("Random Cave", "A cave level from the cellular automaton with the Cave settings")))
                {
                    Undo.RegisterFullObjectHierarchyUndo(room.gameObject, "Random cave");
                    room.RandomCave();
                }
                if (GUILayout.Button(new GUIContent("Random Interior", "A house ground floor (hall, side rooms, hearth, furniture) with the Interior settings")))
                {
                    Undo.RegisterFullObjectHierarchyUndo(room.gameObject, "Random interior");
                    room.RandomInterior();
                }
                if (GUILayout.Button(new GUIContent("Random Dungeon", "A dungeon level (rooms, corridors, stairs, encounters) with the Dungeon settings")))
                {
                    Undo.RegisterFullObjectHierarchyUndo(room.gameObject, "Random dungeon");
                    room.RandomDungeon();
                }
                if (GUILayout.Button(new GUIContent("New Seed", "Random Cave with a new seed")))
                {
                    Undo.RegisterFullObjectHierarchyUndo(room.gameObject, "Random cave");
                    room.cave.seed = UnityEngine.Random.Range(1, 99999);
                    room.RandomCave();
                }
                if (GUILayout.Button("Clear"))
                {
                    Undo.RegisterFullObjectHierarchyUndo(room.gameObject, "Clear room");
                    room.Clear();
                }
            }
            if (room.notes.Count > 0)
                EditorGUILayout.HelpBox(string.Join("\n", room.notes.Take(20)) + (room.notes.Count > 20 ? $"\n... {room.notes.Count - 20} more" : ""), MessageType.None);
        }
    }
}
