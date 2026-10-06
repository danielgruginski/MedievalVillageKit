using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json.Linq;
using UnityEditor;
using UnityEngine;

namespace MedievalKit.Editor
{
    /// <summary>
    /// Outdoor maps from layouts (<see cref="KitVillage"/>): the pieces a layout names found in the package, the map
    /// built in a scene of its own beside the open ones, its ground (mesh, control map, material) saved as assets next
    /// to the scene, lit like VK_ValleyTown, a camera at the arrival spawn. The open scenes are left as they were.
    /// </summary>
    [InitializeOnLoad]
    public static class KitVillageTools
    {
        static KitVillageTools()
        {
            KitVillage.Spawn = (prefab, parent) =>
                Application.isPlaying ? Object.Instantiate(prefab, parent) : (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
        }

        static Dictionary<string, GameObject> index;

        /// <summary>a package prefab by file name: the kit's pieces (SM_VK_*, SM_VKI_*) and structures (Inn, Chapel...)</summary>
        public static GameObject FindPrefab(string name)
        {
            if (index == null)
            {
                index = new Dictionary<string, GameObject>();
                foreach (var guid in AssetDatabase.FindAssets("t:Prefab", new[] { KitPaths.Prefabs, KitPaths.Generated + "/Structures" }))
                {
                    var path = AssetDatabase.GUIDToAssetPath(guid);
                    string n = Path.GetFileNameWithoutExtension(path);
                    if (!index.ContainsKey(n)) index[n] = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                }
            }
            foreach (var n in new[] { name, "SM_VK_" + name, "SM_VKI_Prop_" + name, "SM_VKI_" + name })
                if (index.TryGetValue(n, out var go)) return go;
            return KitRoomTools.ProjectPrefab(name);           // the game's own pieces
        }

        /// <summary>every piece name a layout uses</summary>
        public static IEnumerable<string> Names(JObject L)
        {
            foreach (var b in L["buildings"] as JArray ?? new JArray()) if (b["structure"] != null) yield return (string)b["structure"];
            foreach (var p in L["props"] as JArray ?? new JArray())
            {
                yield return (string)p["piece"];
                foreach (var d in Dressing(p)) yield return d.piece;          // what finishes it (the gatehouse's storey and roofs)
            }
            foreach (var t in L["trees"] as JArray ?? new JArray()) yield return (string)t["piece"];
            foreach (var f in L["fences"] as JArray ?? new JArray())
            {
                yield return (string)f["piece"] ?? "Prop_Fence";
                if (f["gate"] != null) yield return (string)f["gate"];
                if (f["gateDoor"] != null) yield return (string)f["gateDoor"];
                foreach (var e in f["along"] as JArray ?? new JArray()) if (e["piece"] != null) yield return (string)e["piece"];
            }
            foreach (var key in new[] { "species", "undergrowth" })
                foreach (var e in L["forest"]?[key] as JArray ?? new JArray()) yield return (string)e[0];
            foreach (var s in L["scatter"] as JArray ?? new JArray())
                foreach (var e in s["pieces"] as JArray ?? new JArray()) yield return (string)e[0];
            foreach (var g in L["gardens"] as JArray ?? new JArray())
            {
                foreach (var c in g["crops"] as JArray ?? new JArray()) yield return (string)c;
                if (g["fence"] != null) yield return (string)g["fence"];
                if (g["gatePiece"] != null) yield return (string)g["gatePiece"];
            }
        }

        /// <summary>a layout prop's dressing (KitVillage.Dressings, unless "dress": false)</summary>
        static IEnumerable<(string piece, Vector3 at, float rot, string roof)> Dressing(JToken p)
        {
            string n = (string)p["piece"];
            if (n == null || !((bool?)p["dress"] ?? true)) yield break;
            foreach (var k in new[] { n, "SM_VK_" + n })
                if (KitVillage.Dressings.TryGetValue(k, out var parts))
                {
                    foreach (var d in parts) yield return d;
                    yield break;
                }
        }

        /// <summary>a navmesh over the map (radius 0.3, 0.1 m voxels) from its own colliders: from the start spawn, every
        /// spawn, marker and encounter point on the ground reachable, and no point in the forest just beyond the clearing's wall.
        /// Breakable pieces (vki_breakable: a goblin gate) count as broken, so what lies behind them must be reachable; then a
        /// second navmesh with them whole lists what they shut off (the camp behind its gate), so a gate that leaves a way
        /// round shows. -> a report; its first line "ok" when all is well</summary>
        public static string WalkVillage(KitVillage v, string start = "arrival")
        {
            var settings = UnityEngine.AI.NavMesh.CreateSettings();
            settings.agentRadius = 0.3f; settings.agentHeight = 1.8f; settings.agentClimb = 0.35f; settings.agentSlope = 40f;
            settings.overrideVoxelSize = true; settings.voxelSize = 0.1f;
            UnityEngine.AI.NavMeshDataInstance inst = default;
            var lines = new List<string>();
            int bad = 0;
            // the breakables' carving obstacles (KitNavBake) carve every navmesh, the test's too: off while it runs
            var carving = v.GetComponentsInChildren<UnityEngine.AI.NavMeshObstacle>().Where(o => o.enabled).ToList();
            foreach (var o in carving) o.enabled = false;
            try
            {
                Physics.SyncTransforms();
                var root = v.transform;
                var cols = root.GetComponentsInChildren<Collider>().Where(c => !c.isTrigger && c.enabled).ToList();
                var bounds = cols[0].bounds;
                foreach (var c in cols) bounds.Encapsulate(c.bounds);
                bounds.Expand(2f);
                var all = new List<UnityEngine.AI.NavMeshBuildSource>();
                UnityEngine.AI.NavMeshBuilder.CollectSources(bounds, ~0, UnityEngine.AI.NavMeshCollectGeometry.PhysicsColliders, 0, new List<UnityEngine.AI.NavMeshBuildMarkup>(), all);
                all.RemoveAll(s => s.component == null || !s.component.transform.IsChildOf(root));
                var breakables = root.GetComponentsInChildren<KitPiece>().Where(p => p.Has("vki_breakable") && p.Get("vki_breakable") != "0").ToList();
                bool Broken(UnityEngine.AI.NavMeshBuildSource s) => breakables.Any(b => s.component.transform.IsChildOf(b.transform));
                var sources = all.Where(s => !Broken(s)).ToList();
                inst = UnityEngine.AI.NavMesh.AddNavMeshData(UnityEngine.AI.NavMeshBuilder.BuildNavMeshData(settings, sources, bounds, Vector3.zero, Quaternion.identity));
                var filter = new UnityEngine.AI.NavMeshQueryFilter { agentTypeID = settings.agentTypeID, areaMask = UnityEngine.AI.NavMesh.AllAreas };
                var spawns = root.GetComponentsInChildren<KitSpawn>().ToList();
                var from = spawns.FirstOrDefault(s => s.spawnId == start) ?? spawns.FirstOrDefault();
                if (from == null) return "no spawn to start from";
                UnityEngine.AI.NavMesh.SamplePosition(from.transform.position, out var h0, 1f, filter);
                var checks = new List<(string id, Vector3 p)>();
                bool Reach(Vector3 p)
                {
                    if (!UnityEngine.AI.NavMesh.SamplePosition(p, out var h, 1.2f, filter)) return false;
                    var path = new UnityEngine.AI.NavMeshPath();
                    return UnityEngine.AI.NavMesh.CalculatePath(h0.position, h.position, filter, path) && path.status == UnityEngine.AI.NavMeshPathStatus.PathComplete;
                }
                foreach (var s in spawns)
                {
                    checks.Add(($"spawn {s.spawnId}", s.transform.position));
                    if (!Reach(s.transform.position)) { bad++; lines.Add($"spawn {s.spawnId} not reached"); }
                }
                foreach (var m in root.GetComponentsInChildren<KitMarker>())
                {
                    checks.Add((m.name, m.transform.position));
                    if (!Reach(m.transform.position)) { bad++; lines.Add($"{m.name} not reached"); }
                }
                // encounters' spawn points on the ground (the ones lifted off it, archers on a walkway or up a tower, are out of
                // reach by design): the height over the terrain, the lowest thing under the point (a platform under an archer
                // is not the ground)
                int encPts = 0;
                foreach (var e in root.GetComponentsInChildren<KitEncounter>())
                    foreach (Transform sp in e.transform)
                    {
                        var hits = Physics.RaycastAll(sp.position + Vector3.up * 30f, Vector3.down, 60f);
                        if (hits.Length == 0 || sp.position.y - hits.Min(gh => gh.point.y) > 0.5f) continue;
                        encPts++;
                        checks.Add(($"{e.encounterId}/{sp.name}", sp.position));
                        if (!Reach(sp.position)) { bad++; lines.Add($"{e.encounterId}/{sp.name} not reached"); }
                    }
                int probes = 0;
                foreach (var q in v.ForestProbes())
                {
                    var top = root.TransformPoint(KitVillage.Local(q.x, q.y, 20f));
                    if (!Physics.Raycast(top, Vector3.down, out var hit, 60f)) continue;
                    probes++;
                    if (Reach(hit.point)) { bad++; lines.Add($"the forest leaks at ({q.x:0.#}, {q.y:0.#})"); }
                }
                lines.Insert(0, (bad == 0 ? "ok" : $"{bad} problems") + $": {spawns.Count} spawns, {root.GetComponentsInChildren<KitMarker>().Length} markers, {encPts} encounter points, {probes} forest probes" +
                                (breakables.Count > 0 ? $", {breakables.Count} breakable" : ""));
                if (breakables.Count > 0)
                {
                    // the breakables whole: what they shut off from the start
                    var open = checks.Where(c => Reach(c.p)).ToList();
                    UnityEngine.AI.NavMesh.RemoveNavMeshData(inst);
                    inst = UnityEngine.AI.NavMesh.AddNavMeshData(UnityEngine.AI.NavMeshBuilder.BuildNavMeshData(settings, all, bounds, Vector3.zero, Quaternion.identity));
                    UnityEngine.AI.NavMesh.SamplePosition(from.transform.position, out h0, 1f, filter);
                    var shut = open.Where(c => !Reach(c.p)).Select(c => c.id).ToList();
                    lines.Add(shut.Count > 0 ? $"behind the breakables ({string.Join(", ", breakables.Select(b => b.name))}): {shut.Count} of {open.Count} -- {string.Join(", ", shut)}"
                                             : $"the breakables ({string.Join(", ", breakables.Select(b => b.name))}) shut nothing off: there is a way round");
                }
            }
            finally
            {
                if (inst.valid) UnityEngine.AI.NavMesh.RemoveNavMeshData(inst);
                UnityEngine.AI.NavMesh.RemoveSettings(settings.agentTypeID);
                foreach (var o in carving) if (o != null) o.enabled = true;
            }
            return string.Join("\n", lines);
        }

        [MenuItem("Tools/Medieval Kit/World/Build Village From Selected Layout")]
        public static void BuildSelectedMenu()
        {
            var ta = Selection.activeObject as TextAsset;
            if (ta == null) { EditorUtility.DisplayDialog("Build Village", "Select a layout (.json TextAsset).", "OK"); return; }
            string path = AssetDatabase.GetAssetPath(ta);
            Debug.Log(BuildVillage(path, Path.ChangeExtension(path, null).Replace("_layout", "") + ".unity"));
        }

        /// <summary>builds the layout at `layoutPath` into the scene `scenePath` (made or replaced; it must not be open)</summary>
        public static string BuildVillage(string layoutPath, string scenePath)
        {
            string text = File.ReadAllText(layoutPath);
            var L = JObject.Parse(text);
            string mapName = (string)L["name"] ?? Path.GetFileNameWithoutExtension(scenePath);
            for (int i = 0; i < UnityEngine.SceneManagement.SceneManager.sceneCount; i++)
                if (UnityEngine.SceneManagement.SceneManager.GetSceneAt(i).path == scenePath) return $"{scenePath} is open: close it first";
            index = null;
            var missing = new List<string>();
            var prefabs = new List<GameObject>();
            foreach (var n in Names(L).Where(n => n != null).Distinct())
            {
                var p = FindPrefab(n);
                if (p == null) missing.Add(n); else prefabs.Add(p);
            }
            string folder = Path.GetDirectoryName(scenePath).Replace('\\', '/') + "/" + mapName + "_Ground";
            Directory.CreateDirectory(folder);
            var active = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            var scene = UnityEditor.SceneManagement.EditorSceneManager.NewScene(UnityEditor.SceneManagement.NewSceneSetup.EmptyScene,
                                                                                UnityEditor.SceneManagement.NewSceneMode.Additive);
            UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene, scenePath);
            UnityEngine.SceneManagement.SceneManager.SetActiveScene(scene);
            var report = new List<string>();
            try
            {
                string lit = $"{KitPaths.Levels}/VK_ValleyTown.unity";
                if (AssetDatabase.LoadAssetAtPath<SceneAsset>(lit) != null) KitHouseTools.CopyLighting(scene, lit, l => l.type == LightType.Directional);
                var go = new GameObject(mapName);
                var v = go.AddComponent<KitVillage>();
                v.layout = text;
                // the terrain material: the layout's "ground" (a material asset path, or a kit material's name -- a
                // map of its own colours: a burnt land's scorched grass and ash), else the kit's
                string groundName = (string)L["ground"];
                Material groundMat = null;
                if (!string.IsNullOrEmpty(groundName))
                {
                    groundMat = AssetDatabase.LoadAssetAtPath<Material>(groundName.EndsWith(".mat") ? groundName : $"{KitPaths.Materials}/{groundName}.mat");
                    if (groundMat == null) report.Add($"no ground material {groundName}: the kit's terrain instead");
                }
                v.groundMaterial = groundMat != null ? groundMat : AssetDatabase.LoadAssetAtPath<Material>(KitPaths.Materials + "/M_VK_Terrain.mat");
                v.houseRules = AssetDatabase.LoadAssetAtPath<KitHouseRules>(KitPaths.Generated + "/KitHouseRules.asset");
                v.prefabs = prefabs;
                // the materials the swaps name (the layout's palette and the entries' own)
                var swaps = new[] { L["swap"] }.Concat(new[] { "buildings", "props" }.SelectMany(k => (L[k] as JArray ?? new JArray()).Select(e => e["swap"])))
                    .OfType<JObject>().SelectMany(o => o.Properties().Select(pr => (string)pr.Value))
                    .Concat((L["props"] as JArray ?? new JArray()).SelectMany(Dressing).Select(d => d.roof).Where(m => m != null)).Distinct();
                foreach (var mn in swaps)
                {
                    var m = AssetDatabase.LoadAssetAtPath<Material>($"{KitPaths.Materials}/{mn}.mat");
                    if (m != null) v.materials.Add(m); else report.Add($"no material {mn} (for a swap)");
                }
                v.Build();
                // the ground's mesh, control map and material as assets beside the scene
                void Save(Object o, string file)
                {
                    if (o == null) return;
                    string p = $"{folder}/{file}";
                    if (AssetDatabase.LoadAssetAtPath<Object>(p) != null) AssetDatabase.DeleteAsset(p);
                    AssetDatabase.CreateAsset(o, p);
                }
                Save(v.GroundMesh, $"{mapName}_Ground.asset");
                Save(v.ControlMap, $"{mapName}_GroundControl.asset");
                Save(v.GroundMaterialInstance, $"{mapName}_Ground.mat");
                Save(v.GrassMaterialInstance, $"{mapName}_Grass.mat");
                string oldGrass = $"{folder}/{mapName}_Grass.asset";      // (baked blade meshes, before KitGrass grew them)
                if (AssetDatabase.LoadAssetAtPath<Object>(oldGrass) != null) AssetDatabase.DeleteAsset(oldGrass);
                // a camera at the arrival, at the game's angle
                var arrival = go.GetComponentsInChildren<KitSpawn>().FirstOrDefault(s => s.spawnId == ((string)L["start"] ?? "arrival")) ?? go.GetComponentInChildren<KitSpawn>();
                var cam = new GameObject("Main Camera").AddComponent<Camera>();
                cam.tag = "MainCamera";
                cam.fieldOfView = 30f; cam.farClipPlane = 400f;
                var at = arrival != null ? arrival.transform.position : go.transform.position;
                cam.transform.SetPositionAndRotation(at + new Vector3(0f, 26f, 22f), Quaternion.Euler(50f, 180f, 0f));
                report.Add(KitNavBake.BakeScene(scene, 0.1f));
                UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene, scenePath);
                report.Add($"{scenePath}: {go.GetComponentsInChildren<Renderer>().Length} renderers, {go.GetComponentsInChildren<Collider>().Length} colliders");
                report.Add("walk test: " + WalkVillage(v, (string)L["start"] ?? "arrival"));
                report.AddRange(v.notes.Distinct());
                if (missing.Count > 0) report.Add("missing pieces: " + string.Join(", ", missing));
            }
            finally
            {
                UnityEngine.SceneManagement.SceneManager.SetActiveScene(active);
                UnityEditor.SceneManagement.EditorSceneManager.CloseScene(scene, true);
                AssetDatabase.SaveAssets();
            }
            return string.Join("\n", report);
        }
    }
}
