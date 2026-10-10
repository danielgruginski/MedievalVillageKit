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

        /// <summary>a point's height over the map's ground: the lowest of the map's own colliders under it (a platform under
        /// an archer is not the ground, another open scene's colliders are not this map's); NaN when there is none</summary>
        static float OverGround(Transform root, Vector3 p)
        {
            var ys = Physics.RaycastAll(p + Vector3.up * 30f, Vector3.down, 60f).Where(h => h.collider.transform.IsChildOf(root)).Select(h => h.point.y).ToList();
            return ys.Count == 0 ? float.NaN : p.y - ys.Min();
        }

        /// <summary>an encounter point lifted off the ground (more than 0.5 m: archers on a walkway or up a tower, a lookout):
        /// out of reach by design</summary>
        static bool Lifted(Transform root, Vector3 p) { float g = OverGround(root, p); return float.IsNaN(g) || g > 0.5f; }

        /// <summary>the bounds of the map's cages (pieces named like one): a prisoner's marker inside stands shut in until
        /// the game opens it</summary>
        static List<Bounds> Cages(Transform root) =>
            root.GetComponentsInChildren<KitPiece>().Where(k => k.name.Contains("Cage")).SelectMany(k => k.GetComponentsInChildren<Renderer>()).Select(r => r.bounds).ToList();

        static bool Caged(List<Bounds> cages, Vector3 p) =>
            cages.Any(b => p.x >= b.min.x && p.x <= b.max.x && p.z >= b.min.z && p.z <= b.max.z && p.y > b.min.y - 1f && p.y < b.max.y);

        /// <summary>a point in the map's plan metres (x east, y north)</summary>
        static Vector2 Plan(Transform root, Vector3 p) { var l = root.InverseTransformPoint(p); return new Vector2(-l.x, -l.z); }

        /// <summary>a navmesh over the map (radius 0.3, 0.1 m voxels) from its own colliders: from the start spawn, every
        /// spawn, marker and encounter point on the ground reachable, and no point in the forest just beyond the clearing's wall.
        /// A marker in a cage is a prisoner, shut in by design. `repair`: an encounter point not reached (cut off: beyond a
        /// wall, on an island -- a creature put there never comes) moves to the nearest spot within 3 m on the ground that
        /// is, half a metre clear of everything, with a warning naming it (move the layout's point too). Breakable pieces
        /// (vki_breakable: a goblin gate) count as broken, so what lies behind them must be reachable; then a
        /// second navmesh with them whole lists what they shut off (the camp behind its gate), so a gate that leaves a way
        /// round shows. -> a report; its first line "ok" when all is well; problems are logged as an error</summary>
        public static string WalkVillage(KitVillage v, string start = "arrival", bool repair = false)
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
                if (from == null) { bad++; lines.Add("no spawn to start from"); return lines[0]; }
                UnityEngine.AI.NavMesh.SamplePosition(from.transform.position, out var h0, 1f, filter);
                var checks = new List<(string id, Vector3 p)>();
                bool Path(Vector3 to)
                {
                    var path = new UnityEngine.AI.NavMeshPath();
                    return UnityEngine.AI.NavMesh.CalculatePath(h0.position, to, filter, path) && path.status == UnityEngine.AI.NavMeshPathStatus.PathComplete;
                }
                bool Reach(Vector3 p) => UnityEngine.AI.NavMesh.SamplePosition(p, out var h, 1.2f, filter) && Path(h.position);
                // the nearest spot within 3 m on the ground reached from the start, half a metre clear of everything (the
                // navmesh keeps the walker's 0.3 m off it already: its edge 0.2 m away); of a ring, the clearest
                bool Near(Vector3 p, out Vector3 to)
                {
                    to = p;
                    for (float r = 0.25f; r < 3.01f; r += 0.25f)
                    {
                        int n = Mathf.CeilToInt(2f * Mathf.PI * r / 0.25f);
                        float clear = 0f;
                        for (int k = 0; k < n; k++)
                        {
                            float a = 2f * Mathf.PI * k / n;
                            var q = p + new Vector3(Mathf.Cos(a), 0f, Mathf.Sin(a)) * r;
                            if (!UnityEngine.AI.NavMesh.SamplePosition(q, out var h, 1.2f, filter) || new Vector2(h.position.x - q.x, h.position.z - q.z).sqrMagnitude > 0.01f) continue;
                            if (!UnityEngine.AI.NavMesh.FindClosestEdge(h.position, out var e, filter) || e.distance < 0.2f || e.distance <= clear || !Path(h.position)) continue;
                            to = h.position; clear = e.distance;
                        }
                        if (clear > 0f) return true;
                    }
                    return false;
                }
                foreach (var s in spawns)
                {
                    checks.Add(($"spawn {s.spawnId}", s.transform.position));
                    if (!Reach(s.transform.position)) { bad++; lines.Add($"spawn {s.spawnId} not reached"); }
                }
                var cages = Cages(root);
                int markers = 0, caged = 0;
                foreach (var m in root.GetComponentsInChildren<KitMarker>())
                {
                    markers++;
                    if (Reach(m.transform.position)) { checks.Add((m.name, m.transform.position)); continue; }
                    if (Caged(cages, m.transform.position)) { caged++; continue; }           // a prisoner, shut in
                    bad++; lines.Add($"{m.name} not reached");
                }
                // encounters' spawn points on the ground (the ones lifted off it, archers on a walkway or up a tower, are out of
                // reach by design)
                int encPts = 0, moved = 0;
                foreach (var e in root.GetComponentsInChildren<KitEncounter>())
                    foreach (Transform sp in e.transform)
                    {
                        if (Lifted(root, sp.position)) continue;
                        encPts++;
                        string id = $"{e.encounterId}/{sp.name}";
                        if (!Reach(sp.position))
                        {
                            var was = Plan(root, sp.position);
                            if (repair && Near(sp.position, out var to))
                            {
                                sp.position = to;
                                UnityEditor.SceneManagement.EditorSceneManager.MarkSceneDirty(sp.gameObject.scene);
                                var now = Plan(root, to);
                                string say = $"{id} at ({was.x:0.#}, {was.y:0.#}) not reached: moved {(now - was).magnitude:0.0} m to ({now.x:0.#}, {now.y:0.#})";
                                moved++; lines.Add(say);
                                Debug.LogWarning($"{v.name} walk test: {say} -- move it in the layout too");
                            }
                            else { bad++; lines.Add($"{id} at ({was.x:0.#}, {was.y:0.#}) not reached"); }
                        }
                        checks.Add((id, sp.position));
                    }
                int probes = 0;
                foreach (var q in v.ForestProbes())
                {
                    var top = root.TransformPoint(KitVillage.Local(q.x, q.y, 20f));
                    if (!Physics.Raycast(top, Vector3.down, out var hit, 60f)) continue;
                    probes++;
                    if (Reach(hit.point)) { bad++; lines.Add($"the forest leaks at ({q.x:0.#}, {q.y:0.#})"); }
                }
                lines.Insert(0, (bad == 0 ? "ok" : $"{bad} problems") + $": {spawns.Count} spawns, {markers} markers{(caged > 0 ? $" ({caged} in a cage)" : "")}, " +
                                $"{encPts} encounter points{(moved > 0 ? $" ({moved} moved)" : "")}, {probes} forest probes" +
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
                if (bad > 0) Debug.LogError($"{v.name} walk test: {string.Join("\n", lines)}");
            }
            return string.Join("\n", lines);
        }

        /// <summary>the separate pieces of a map's baked navmesh: the main one (the start spawn's) and the islands -- inside a
        /// building or a cage, the siege tower, on top of a rock or a walkway, a pocket shut in by trunks. -> a report line
        /// (how many, their area, the largest on the ground). A spawn, marker or encounter point whose nearest navmesh within
        /// 1.5 m (where a creature is put down) is an island is a warning, unless it is meant to be there: an encounter point
        /// lifted off the ground (archers on a walkway or a watchtower, a lookout) or a marker in a cage (a prisoner).
        /// Breakables count as broken (their carving off while it runs), as in the walk test</summary>
        public static string Islands(KitVillage v, UnityEngine.AI.NavMeshData data)
        {
            if (v == null || data == null) return "islands: no navmesh";
            if (UnityEngine.AI.NavMesh.CalculateTriangulation().vertices.Length > 0) return "islands: not counted (another navmesh is loaded)";
            var root = v.transform;
            string start = (string)JObject.Parse(string.IsNullOrWhiteSpace(v.layout) ? "{}" : v.layout)["start"] ?? "arrival";
            // the breakables' carving obstacles carve it in the editor too (a goblin gate shut off the camp behind it): off
            // while it is read, the gate counted as broken like the walk test does
            var carving = v.GetComponentsInChildren<UnityEngine.AI.NavMeshObstacle>().Where(o => o.enabled).ToList();
            foreach (var o in carving) o.enabled = false;
            var inst = UnityEngine.AI.NavMesh.AddNavMeshData(data);
            var warn = new List<string>();
            try
            {
                Physics.SyncTransforms();
                var tri = UnityEngine.AI.NavMesh.CalculateTriangulation();
                var V = tri.vertices;
                var T = tri.indices;
                int nt = T.Length / 3;
                // the tiles' shared vertices welded (the same place, a hair apart), the triangles joined over them
                var parent = Enumerable.Range(0, V.Length).ToArray();
                int Find(int x) { while (parent[x] != x) x = parent[x] = parent[parent[x]]; return x; }
                void Join(int a, int b) { a = Find(a); b = Find(b); if (a != b) parent[a] = b; }
                var cell = new Dictionary<(int, int), List<int>>();
                for (int i = 0; i < V.Length; i++)
                {
                    int kx = Mathf.RoundToInt(V[i].x * 100f), kz = Mathf.RoundToInt(V[i].z * 100f);
                    for (int a = -1; a <= 1; a++)
                        for (int b = -1; b <= 1; b++)
                            if (cell.TryGetValue((kx + a, kz + b), out var l))
                                foreach (int j in l) if ((V[j] - V[i]).sqrMagnitude < 1e-4f) Join(i, j);
                    if (!cell.TryGetValue((kx, kz), out var own)) cell[(kx, kz)] = own = new List<int>();
                    own.Add(i);
                }
                for (int t = 0; t < nt; t++) { Join(T[3 * t], T[3 * t + 1]); Join(T[3 * t], T[3 * t + 2]); }
                var area = new Dictionary<int, float>();
                var mid = new Dictionary<int, Vector3>();
                var near = new Dictionary<(int, int), List<int>>();          // the triangles over each 2 m square
                for (int t = 0; t < nt; t++)
                {
                    Vector3 a = V[T[3 * t]], b = V[T[3 * t + 1]], c = V[T[3 * t + 2]];
                    float s = Mathf.Abs((b.x - a.x) * (c.z - a.z) - (c.x - a.x) * (b.z - a.z)) / 2f;
                    int k = Find(T[3 * t]);
                    area[k] = (area.TryGetValue(k, out var s0) ? s0 : 0f) + s;
                    mid[k] = (mid.TryGetValue(k, out var m0) ? m0 : Vector3.zero) + (a + b + c) / 3f * s;
                    for (int x = Mathf.FloorToInt(Mathf.Min(a.x, b.x, c.x) / 2f); x <= Mathf.FloorToInt(Mathf.Max(a.x, b.x, c.x) / 2f); x++)
                        for (int z = Mathf.FloorToInt(Mathf.Min(a.z, b.z, c.z) / 2f); z <= Mathf.FloorToInt(Mathf.Max(a.z, b.z, c.z) / 2f); z++)
                        {
                            if (!near.TryGetValue((x, z), out var l)) near[(x, z)] = l = new List<int>();
                            l.Add(t);
                        }
                }
                // the piece under a point on the navmesh: the triangle round it in plan, the nearest in height
                int PieceAt(Vector3 q)
                {
                    int best = -1;
                    float bd = float.MaxValue;
                    if (!near.TryGetValue((Mathf.FloorToInt(q.x / 2f), Mathf.FloorToInt(q.z / 2f)), out var l)) return -1;
                    foreach (int t in l)
                    {
                        Vector3 a = V[T[3 * t]], b = V[T[3 * t + 1]], c = V[T[3 * t + 2]];
                        float d = (b.z - c.z) * (a.x - c.x) + (c.x - b.x) * (a.z - c.z);
                        if (Mathf.Abs(d) < 1e-8f) continue;
                        float u = ((b.z - c.z) * (q.x - c.x) + (c.x - b.x) * (q.z - c.z)) / d, w = ((c.z - a.z) * (q.x - c.x) + (a.x - c.x) * (q.z - c.z)) / d;
                        if (u < -0.01f || w < -0.01f || 1f - u - w < -0.01f) continue;
                        float dy = Mathf.Abs(u * a.y + w * b.y + (1f - u - w) * c.y - q.y);
                        if (dy < bd) { bd = dy; best = Find(T[3 * t]); }
                    }
                    return best;
                }
                int OnMesh(Vector3 p) => UnityEngine.AI.NavMesh.SamplePosition(p, out var h, 1.5f, UnityEngine.AI.NavMesh.AllAreas) ? PieceAt(h.position) : -1;
                Vector3 Mid(int k) => mid[k] / Mathf.Max(1e-6f, area[k]);
                string At(Vector3 p) { var q = Plan(root, p); return $"({q.x:0.#}, {q.y:0.#})"; }
                var spawns = root.GetComponentsInChildren<KitSpawn>().ToList();
                var from = spawns.FirstOrDefault(s => s.spawnId == start) ?? spawns.FirstOrDefault();
                int main = from != null ? OnMesh(from.transform.position) : -1;
                if (main < 0) return "islands: no navmesh at the start spawn";
                var isl = area.Keys.Where(k => k != main).ToList();
                var up = isl.Where(k => OverGround(root, Mid(k)) > 0.3f).ToList();          // on top of something
                var low = isl.Where(k => !up.Contains(k)).ToList();
                string line = $"islands: {isl.Count} besides the {area[main]:0} m2 walked from {start}: {low.Count} on the ground ({low.Sum(k => area[k]):0.#} m2), " +
                              $"{up.Count} on top of things ({up.Sum(k => area[k]):0.#} m2)";
                if (low.Count > 0) line += "; the largest on the ground: " + string.Join(", ", low.OrderByDescending(k => area[k]).Take(3).Select(k => $"{area[k]:0.#} m2 at {At(Mid(k))}"));
                // the points: where one arrives, the game's markers, the encounters' spawn points
                var cages = Cages(root);
                var pts = spawns.Select(s => (id: $"spawn {s.spawnId}", p: s.transform.position, meant: false))
                    .Concat(root.GetComponentsInChildren<KitMarker>().Select(m => (id: m.name, p: m.transform.position, meant: Caged(cages, m.transform.position))))
                    .Concat(root.GetComponentsInChildren<KitEncounter>().SelectMany(e => e.transform.Cast<Transform>().Where(sp => sp.name != "Creatures")
                        .Select(sp => (id: $"{e.encounterId}/{sp.name}", p: sp.position, meant: Lifted(root, sp.position)))));
                int meantOn = 0;
                foreach (var (id, p, meant) in pts)
                {
                    int k = OnMesh(p);
                    if (k == main) continue;
                    if (meant) { meantOn++; continue; }
                    warn.Add(k < 0 ? $"{id} at {At(p)}: no navmesh within 1.5 m"
                                   : $"{id} at {At(p)} stands on an island ({area[k]:0.#} m2 at {At(Mid(k))}): cut off from the {start} spawn");
                }
                if (meantOn > 0) line += $"; {meantOn} points on one by design (lifted, caged)";
                foreach (var w in warn) Debug.LogWarning($"{v.name} navmesh: {w}");
                return string.Join("\n  ", new[] { line }.Concat(warn));
            }
            finally
            {
                UnityEngine.AI.NavMesh.RemoveNavMeshData(inst);
                foreach (var o in carving) if (o != null) o.enabled = true;
            }
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
                    // a kit material by name, or a map's own by its asset path ("Assets/.../M_X.mat", like the ground)
                    var m = AssetDatabase.LoadAssetAtPath<Material>(mn.EndsWith(".mat") ? mn : $"{KitPaths.Materials}/{mn}.mat");
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
                // the walk test first: an encounter point it finds cut off moves onto the ground before the bake (which
                // reports the navmesh's islands) and the save
                report.Add("walk test: " + WalkVillage(v, (string)L["start"] ?? "arrival", repair: true));
                report.Add(KitNavBake.BakeScene(scene, 0.1f));
                UnityEditor.SceneManagement.EditorSceneManager.SaveScene(scene, scenePath);
                report.Add($"{scenePath}: {go.GetComponentsInChildren<Renderer>().Length} renderers, {go.GetComponentsInChildren<Collider>().Length} colliders");
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
