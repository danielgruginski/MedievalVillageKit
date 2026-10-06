using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using UnityEditor;
using UnityEngine;

namespace MedievalKit.Editor
{
    /// <summary>
    /// Chains of generated maps joined by connectors (<see cref="KitPortal"/>): pieces lined up on their portals (maps are
    /// never turned, so a north portal meets a south one), a sample chain, and a walk test across the seams (one navmesh
    /// over every piece: the floor must run on from one map into the next).
    /// </summary>
    public static class KitChainTools
    {
        public class Piece
        {
            public string name;
            public Action<KitRoom> make;       // sets the generator's options (portals included) and generates
            public string inPortal, outPortal; // its portal lined up on the piece it joins; the one a later piece joins by default
            public int attach = -1;            // the piece it joins (an earlier one; -1: the one before)
            public string attachPortal;        // that piece's portal it joins (null: that piece's outPortal)
            public int Parent(int index) => attach >= 0 ? attach : index - 1;
        }

        public static KitPortalMarker Marker(KitRoom room, string id) =>
            room.GetComponentsInChildren<KitPortalMarker>().FirstOrDefault(m => m.portalId == id);

        /// <summary>moves `next` so its portal `nextPortal` sits on `prev`'s portal `prevPortal`</summary>
        public static bool Align(KitRoom prev, string prevPortal, KitRoom next, string nextPortal)
        {
            var a = Marker(prev, prevPortal);
            var b = Marker(next, nextPortal);
            if (a == null || b == null) return false;
            next.transform.position += a.transform.position - b.transform.position;
            return true;
        }

        /// <summary>a piece's footprint on the ground (world x / z), its map without the rock ring</summary>
        public static Rect Footprint(KitRoom room)
        {
            var p = room.transform.position;
            float w = room.Layout.W, d = room.Layout.D;
            return new Rect(p.x - w, p.z - d, w, d);         // Blender (x, y) -> local (-x, -y)
        }

        /// <summary>builds the pieces under `parent`, each lined up on the piece it joins; notes what fails</summary>
        public static List<KitRoom> Build(KitInteriorRules rules, IList<Piece> pieces, Transform parent, Vector3 origin, List<string> notes)
        {
            var built = new List<KitRoom>();
            foreach (var pc in pieces)
            {
                int k = built.Count, t = pc.Parent(k);
                var room = new GameObject(pc.name).AddComponent<KitRoom>();
                if (parent != null) room.transform.SetParent(parent, false);
                room.rules = rules;
                pc.make(room);
                if (k == 0) room.transform.position = origin;
                else if (t < 0 || t >= k) notes.Add($"{pc.name}: joins piece {t}, not an earlier one");
                else
                {
                    string tp = pc.attachPortal ?? pieces[t].outPortal;
                    if (!Align(built[t], tp, room, pc.inPortal)) notes.Add($"{pc.name}: portal {pc.inPortal} or {pieces[t].name}'s {tp} missing");
                }
                // a missing portal or piece breaks the level (a stair without its prefab is a way out that is gone)
                notes.AddRange(room.notes.Where(n => n.Contains("portal") || n.StartsWith("no prefab")).Select(n => $"{pc.name}: {n}"));
                built.Add(room);
            }
            for (int i = 0; i < built.Count; i++)
                for (int j = i + 1; j < built.Count; j++)
                {
                    var a = Footprint(built[i]); var b = Footprint(built[j]);
                    var o = Rect.MinMaxRect(Mathf.Max(a.xMin, b.xMin), Mathf.Max(a.yMin, b.yMin), Mathf.Min(a.xMax, b.xMax), Mathf.Min(a.yMax, b.yMax));
                    if (o.width > 0.01f && o.height > 0.01f) notes.Add($"{built[i].name} and {built[j].name} overlap ({o.width:0.#} x {o.height:0.#} m)");
                }
            return built;
        }

        /// <summary>a sample chain: a maze cave out north -> a connector -> a dungeon in south, out east -> a connector
        /// turning north -> an open cave in south; and a branch off the first cave's east side: a connector -> a small
        /// open cave in west</summary>
        public static List<Piece> Sample(int seed) => new List<Piece>
        {
            new Piece { name = $"Chain {seed}: cave (maze)", outPortal = "north", make = r =>
                {
                    r.cave.seed = seed;
                    r.cave.portals = new List<KitPortal> { new KitPortal { id = "north", side = "N" }, new KitPortal { id = "east", side = "E", at = 4 } };
                    r.RandomCave();
                } },
            new Piece { name = $"Chain {seed}: connector S-N", inPortal = "from", outPortal = "to", make = r =>
                { r.connector.seed = seed; r.connector.from = "S"; r.connector.to = "N"; r.RandomConnector(); } },
            new Piece { name = $"Chain {seed}: dungeon", inPortal = "south", outPortal = "east", make = r =>
                {
                    r.dungeon.seed = seed;
                    r.dungeon.portals = new List<KitPortal> { new KitPortal { id = "south", side = "S" }, new KitPortal { id = "east", side = "E", at = 14 } };
                    r.RandomDungeon();
                } },
            new Piece { name = $"Chain {seed}: connector W-N", inPortal = "from", outPortal = "to", make = r =>
                { r.connector.seed = seed + 1; r.connector.from = "W"; r.connector.to = "N"; r.RandomConnector(); } },
            new Piece { name = $"Chain {seed}: cave (open)", inPortal = "south", make = r =>
                { r.cave.seed = seed + 2; r.cave.layout = "Open"; r.cave.portals = new List<KitPortal> { new KitPortal { id = "south", side = "S" } }; r.RandomCave(); } },
            new Piece { name = $"Chain {seed}: branch connector W-E", inPortal = "from", outPortal = "to", attach = 0, attachPortal = "east", make = r =>
                { r.connector.seed = seed + 3; r.connector.from = "W"; r.connector.to = "E"; r.RandomConnector(); } },
            new Piece { name = $"Chain {seed}: side cave", inPortal = "west", make = r =>
                {
                    r.cave.seed = seed + 4; r.cave.layout = "Open"; r.cave.nc = 18; r.cave.nr = 14; r.cave.chasm = false;
                    r.cave.portals = new List<KitPortal> { new KitPortal { id = "west", side = "W", at = 4 } };
                    r.RandomCave();
                } },
        };

        /// <summary>one navmesh over every piece (radius 0.3, 0.05 m voxels, openable leaves left out): from the first
        /// piece's first spawn, which spawns of every piece can be reached. -> (reached, total, the unreached)</summary>
        public static (int ok, int total, List<string> missed) WalkChain(IList<KitRoom> rooms, float radius = 0.3f, float voxel = 0.05f)
        {
            var settings = UnityEngine.AI.NavMesh.CreateSettings();
            settings.agentRadius = radius; settings.agentHeight = 1.8f; settings.agentClimb = 0.35f; settings.agentSlope = 40f;
            settings.overrideVoxelSize = true; settings.voxelSize = voxel;
            UnityEngine.AI.NavMeshDataInstance inst = default;
            var missed = new List<string>();
            try
            {
                Physics.SyncTransforms();
                var cols = rooms.SelectMany(r => r.GetComponentsInChildren<Collider>()).Where(c => !c.isTrigger && c.enabled).ToList();
                var bounds = cols[0].bounds;
                foreach (var c in cols) bounds.Encapsulate(c.bounds);
                bounds.Expand(2f);
                var sources = new List<UnityEngine.AI.NavMeshBuildSource>();
                UnityEngine.AI.NavMeshBuilder.CollectSources(bounds, ~0, UnityEngine.AI.NavMeshCollectGeometry.PhysicsColliders, 0, new List<UnityEngine.AI.NavMeshBuildMarkup>(), sources);
                sources.RemoveAll(src => src.component == null || !rooms.Any(r => src.component.transform.IsChildOf(r.transform)) ||
                                         src.component.GetComponentInParent<KitPiece>()?.Get("vki_openable") is string op && op != "0" && op != "False");
                inst = UnityEngine.AI.NavMesh.AddNavMeshData(UnityEngine.AI.NavMeshBuilder.BuildNavMeshData(settings, sources, bounds, Vector3.zero, Quaternion.identity));
                var filter = new UnityEngine.AI.NavMeshQueryFilter { agentTypeID = settings.agentTypeID, areaMask = UnityEngine.AI.NavMesh.AllAreas };
                var spawns = rooms.SelectMany(r => r.GetComponentsInChildren<KitSpawn>().Select(s => (room: r, s))).ToList();
                if (spawns.Count == 0) return (0, 0, missed);
                UnityEngine.AI.NavMeshHit h0 = default;
                bool has = UnityEngine.AI.NavMesh.SamplePosition(spawns[0].s.transform.position, out h0, 0.8f, filter);
                int ok = 0;
                foreach (var (room, s) in spawns)
                {
                    var path = new UnityEngine.AI.NavMeshPath();
                    bool reach = has && UnityEngine.AI.NavMesh.SamplePosition(s.transform.position, out var h, 0.8f, filter) &&
                                 UnityEngine.AI.NavMesh.CalculatePath(h0.position, h.position, filter, path) && path.status == UnityEngine.AI.NavMeshPathStatus.PathComplete;
                    if (reach) ok++; else missed.Add($"{room.name}/{s.spawnId}");
                }
                return (ok, spawns.Count, missed);
            }
            finally
            {
                if (inst.valid) UnityEngine.AI.NavMesh.RemoveNavMeshData(inst);
                UnityEngine.AI.NavMesh.RemoveSettings(settings.agentTypeID);
            }
        }

        // ------------------------------------------------------------------ baking a KitChain asset
        static KitPortal PortalOf(KitChain.Map m, string id) => m.Portals().FirstOrDefault(p => p.id == id);

        /// <summary>the asset's maps as pieces: each map after the first behind a connector from the earlier map's out
        /// portal (its edge facing it) to its own in portal</summary>
        public static List<Piece> PiecesOf(KitChain chain, List<string> notes)
        {
            var list = new List<Piece>();
            var pieceOf = new Dictionary<string, int>();                     // map id -> its piece's index
            var used = new HashSet<string>();                                // "map.portal" taken by a join
            for (int i = 0; i < chain.maps.Count; i++)
            {
                var m = chain.maps[i];
                if (pieceOf.ContainsKey(m.id)) { notes.Add($"two maps are called {m.id}"); continue; }
                if (i > 0)
                {
                    var prev = string.IsNullOrEmpty(m.attachTo) ? chain.maps[i - 1] : chain.maps.Take(i).FirstOrDefault(q => q.id == m.attachTo);
                    if (prev == null) { notes.Add($"{m.id}: joins {m.attachTo}, not a map listed before it"); continue; }
                    string prevPortal = string.IsNullOrEmpty(m.attachPortal) ? prev.outPortal : m.attachPortal;
                    var po = PortalOf(prev, prevPortal); var pi = PortalOf(m, m.inPortal);
                    if (po == null || pi == null) { notes.Add($"{m.id}: portal {prev.id}.{prevPortal} or {m.id}.{m.inPortal} not in the maps' portals"); continue; }
                    if (!used.Add($"{prev.id}.{po.id}")) notes.Add($"{prev.id}.{po.id} is joined twice");
                    used.Add($"{m.id}.{pi.id}");
                    int parentPiece = pieceOf[prev.id];
                    char from = KitPortal.Opposite(po.Side), to = KitPortal.Opposite(pi.Side);
                    if (from == to) notes.Add($"{prev.id} -> {m.id}: both portals face the same way; a connector cannot turn back");
                    if (po.width != pi.width) notes.Add($"{prev.id}.{prev.outPortal} and {m.id}.{m.inPortal} differ in width");
                    var co = m.connector;
                    list.Add(new Piece
                    {
                        name = $"{chain.name} {i:00}a {prev.id}-{m.id}", inPortal = "from", outPortal = "to",
                        attach = parentPiece, attachPortal = po.id,
                        make = r =>
                        {
                            r.connector = new KitConnectorGenerator.Options
                            {
                                from = from.ToString(), to = to.ToString(), length = co.length, width = po.width, seed = co.seed, style = co.style, debris = co.debris,
                            };
                            r.RandomConnector();
                        },
                    });
                }
                pieceOf[m.id] = list.Count;
                list.Add(new Piece
                {
                    name = $"{chain.name} {i:00} {m.id}", inPortal = i > 0 ? m.inPortal : null, outPortal = m.outPortal,
                    make = r =>
                    {
                        if (m.kind == KitChain.Kind.Cave) { r.cave = m.cave; r.RandomCave(); }
                        else if (m.kind == KitChain.Kind.Dungeon) { r.dungeon = m.dungeon; r.RandomDungeon(); }
                        else { r.preset = ""; r.plan = m.PlanText; r.record = m.RecordText; r.Generate(); }
                    },
                });
            }
            // every portal leads somewhere (an unjoined one would open the map's edge onto nothing)
            foreach (var m in chain.maps)
                foreach (var p in m.Portals())
                {
                    if (!used.Contains($"{m.id}.{p.id}")) notes.Add($"{m.id}.{p.id} leads nowhere: join a map to it or remove it");
                    if (m.kind == KitChain.Kind.Plan && p.at < 0) notes.Add($"{m.id}.{p.id}: a hand-made map's portal needs its `at`");
                }
            return list;
        }

        [MenuItem("Tools/Medieval Kit/Chains/Bake Selected Chain")]
        public static void BakeSelectedMenu()
        {
            var chain = Selection.activeObject as KitChain;
            if (chain == null) { EditorUtility.DisplayDialog("Bake Chain", "Select a KitChain asset (Assets > Create > Medieval Kit > Chain).", "OK"); return; }
            Debug.Log(Bake(chain));
        }

        /// <summary>builds every piece of the chain lined up in world space beside the open scenes, stops if pieces overlap
        /// or a portal is missing, else saves each piece as a scene in a folder named after the asset (next to it), fills
        /// the asset's pieces, adds the scenes to the build settings and writes a play scene (sun, streamer, test walker).
        /// The open scenes are left as they were.</summary>
        public static string Bake(KitChain chain)
        {
            var rules = AssetDatabase.LoadAssetAtPath<KitInteriorRules>(KitRoomTools.RulesAsset);
            if (rules == null) return "no interior rules: run Build Interior Rules";
            string assetPath = AssetDatabase.GetAssetPath(chain);
            string folder = $"{Path.GetDirectoryName(assetPath).Replace('\\', '/')}/{chain.name}";
            var notes = new List<string>();
            var pieces = PiecesOf(chain, notes);
            if (notes.Count > 0) return $"chain {chain.name} not baked:\n{string.Join("\n", notes)}";
            var active = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            var tmp = UnityEditor.SceneManagement.EditorSceneManager.NewScene(UnityEditor.SceneManagement.NewSceneSetup.EmptyScene,
                                                                              UnityEditor.SceneManagement.NewSceneMode.Additive);
            // saved under a scratch name at once: new scenes cannot be made beside an untitled one with changes
            Directory.CreateDirectory(folder);
            string scratch = $"{folder}/_bake.unity";
            UnityEditor.SceneManagement.EditorSceneManager.SaveScene(tmp, scratch);
            UnityEngine.SceneManagement.SceneManager.SetActiveScene(tmp);
            var sb = new StringBuilder();
            try
            {
                var rooms = Build(rules, pieces, null, Vector3.zero, notes);
                if (notes.Count > 0) return $"chain {chain.name} not baked:\n{string.Join("\n", notes)}";
                var (ok, total, missed) = WalkChain(rooms);
                if (ok < total) sb.AppendLine($"walk test: {ok}/{total} spawns reached (not {string.Join(", ", missed)})");
                Directory.CreateDirectory(folder);
                chain.pieces = new List<KitChain.Piece>();
                for (int i = 0; i < rooms.Count; i++)
                {
                    var room = rooms[i];
                    string id = room.name.Substring(chain.name.Length + 1);
                    string path = $"{folder}/{room.name}.unity";
                    var sc = UnityEditor.SceneManagement.EditorSceneManager.NewScene(UnityEditor.SceneManagement.NewSceneSetup.EmptyScene,
                                                                                     UnityEditor.SceneManagement.NewSceneMode.Additive);
                    UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(room.gameObject, sc);
                    UnityEngine.SceneManagement.SceneManager.SetActiveScene(sc);      // the kit's levels: no sky reflection
                    RenderSettings.defaultReflectionMode = UnityEngine.Rendering.DefaultReflectionMode.Custom;
                    RenderSettings.reflectionIntensity = 0f;
                    UnityEngine.SceneManagement.SceneManager.SetActiveScene(tmp);
                    UnityEditor.SceneManagement.EditorSceneManager.SaveScene(sc, path);
                    chain.pieces.Add(new KitChain.Piece
                    {
                        id = id, scene = path, position = room.transform.position, footprint = Footprint(room),
                        spawns = room.GetComponentsInChildren<KitSpawn>().Select(sp => sp.spawnId).ToList(),
                    });
                    UnityEditor.SceneManagement.EditorSceneManager.CloseScene(sc, true);
                }
                for (int i = 1; i < chain.pieces.Count; i++)              // each piece and the piece it joins
                {
                    int t = pieces[i].Parent(i);
                    chain.pieces[i].neighbours.Add(chain.pieces[t].id);
                    chain.pieces[t].neighbours.Add(chain.pieces[i].id);
                }
                var scenes = EditorBuildSettings.scenes.ToList();
                foreach (var p in chain.pieces)
                    if (!scenes.Any(s => s.path == p.scene)) scenes.Add(new EditorBuildSettingsScene(p.scene, true));
                string play = WritePlayScene(chain, folder);
                if (play != null && !scenes.Any(s => s.path == play)) scenes.Add(new EditorBuildSettingsScene(play, true));
                EditorBuildSettings.scenes = scenes.ToArray();
                EditorUtility.SetDirty(chain);
                AssetDatabase.SaveAssets();
                sb.AppendLine(KitNavBake.BakeChain(chain));
                sb.Insert(0, $"chain {chain.name}: {chain.pieces.Count} pieces baked to {folder} (play: {play})\n");
            }
            finally
            {
                UnityEngine.SceneManagement.SceneManager.SetActiveScene(active);
                UnityEditor.SceneManagement.EditorSceneManager.CloseScene(tmp, true);
                AssetDatabase.DeleteAsset(scratch);
            }
            return sb.ToString();
        }

        /// <summary>{chain}_Play.unity: the sun and volume of VKI_Dungeon_B4, a KitChainStreamer, a KitShroud (as the
        /// play scene's was tuned, on a re-bake) and a KitTestWalker</summary>
        static string WritePlayScene(KitChain chain, string folder)
        {
            string path = $"{folder}/{chain.name}_Play.unity";
            string shroudWas = TunedShroud(path);
            var sc = UnityEditor.SceneManagement.EditorSceneManager.NewScene(UnityEditor.SceneManagement.NewSceneSetup.EmptyScene,
                                                                             UnityEditor.SceneManagement.NewSceneMode.Additive);
            try
            {
                var prevActive = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
                UnityEngine.SceneManagement.SceneManager.SetActiveScene(sc);
                string lit = $"{KitPaths.Levels}/VKI_Dungeon_B4.unity";
                if (AssetDatabase.LoadAssetAtPath<SceneAsset>(lit) != null) KitHouseTools.CopyLighting(sc, lit, l => l.type == LightType.Directional);
                var st = new GameObject("KitChainStreamer").AddComponent<KitChainStreamer>();
                st.chain = chain;
                var shroud = new GameObject("KitShroud").AddComponent<KitShroud>();      // the rock away from the passages fades to black
                if (shroudWas != null) EditorJsonUtility.FromJsonOverwrite(shroudWas, shroud);
                var walkerType = Type.GetType("MedievalKit.KitTestWalker, MedievalKit.Walker");
                if (walkerType != null)
                {
                    var w = GameObject.CreatePrimitive(PrimitiveType.Capsule);
                    w.name = "KitTestWalker";
                    UnityEngine.Object.DestroyImmediate(w.GetComponent<Collider>());
                    var cc = w.AddComponent<CharacterController>();
                    cc.height = 1.8f; cc.radius = 0.3f; cc.center = new Vector3(0f, 0.9f, 0f);
                    w.AddComponent(walkerType);
                    st.walker = w.transform;
                }
                UnityEditor.SceneManagement.EditorSceneManager.SaveScene(sc, path);
                UnityEngine.SceneManagement.SceneManager.SetActiveScene(prevActive);
                return path;
            }
            finally { UnityEditor.SceneManagement.EditorSceneManager.CloseScene(sc, true); }
        }

        /// <summary>the KitShroud's settings in the play scene already at <paramref name="path"/> (null: none yet), so a
        /// re-bake keeps the shroud as it was tuned</summary>
        static string TunedShroud(string path)
        {
            if (AssetDatabase.LoadAssetAtPath<SceneAsset>(path) == null) return null;
            var open = UnityEngine.SceneManagement.SceneManager.GetSceneByPath(path);
            bool wasOpen = open.IsValid() && open.isLoaded;
            var sc = wasOpen ? open : UnityEditor.SceneManagement.EditorSceneManager.OpenScene(path, UnityEditor.SceneManagement.OpenSceneMode.Additive);
            try
            {
                foreach (var root in sc.GetRootGameObjects())
                {
                    var s = root.GetComponentInChildren<KitShroud>(true);
                    if (s != null) return EditorJsonUtility.ToJson(s);
                }
                return null;
            }
            finally { if (!wasOpen) UnityEditor.SceneManagement.EditorSceneManager.CloseScene(sc, true); }
        }

        [MenuItem("Tools/Medieval Kit/Chains/Create Sample Chain")]
        public static void CreateSampleMenu() => Debug.Log(CreateSample("Assets/MedievalKitChains/SampleChain.asset", 1));

        /// <summary>a KitChain asset like the sample chain (maze cave -> dungeon -> open cave, and a side cave branching off
        /// the first cave's east side), baked</summary>
        public static string CreateSample(string path, int seed)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            var chain = AssetDatabase.LoadAssetAtPath<KitChain>(path);
            if (chain == null) { chain = ScriptableObject.CreateInstance<KitChain>(); AssetDatabase.CreateAsset(chain, path); }
            chain.maps = new List<KitChain.Map>
            {
                new KitChain.Map { id = "cave", kind = KitChain.Kind.Cave, inPortal = "", outPortal = "north",
                    cave = new KitCaveGenerator.Options { seed = seed, portals = new List<KitPortal> { new KitPortal { id = "north", side = "N" }, new KitPortal { id = "east", side = "E", at = 4 } } } },
                new KitChain.Map { id = "dungeon", kind = KitChain.Kind.Dungeon, inPortal = "south", outPortal = "east",
                    dungeon = new KitDungeonGenerator.Options { seed = seed, portals = new List<KitPortal> { new KitPortal { id = "south", side = "S" }, new KitPortal { id = "east", side = "E", at = 14 } } },
                    connector = new KitConnectorGenerator.Options { seed = seed, length = 10 } },
                new KitChain.Map { id = "deep cave", kind = KitChain.Kind.Cave, inPortal = "south", outPortal = "",
                    cave = new KitCaveGenerator.Options { seed = seed + 2, layout = "Open", portals = new List<KitPortal> { new KitPortal { id = "south", side = "S" } } },
                    connector = new KitConnectorGenerator.Options { seed = seed + 1, length = 10 } },
                new KitChain.Map { id = "side cave", kind = KitChain.Kind.Cave, inPortal = "west", attachTo = "cave", attachPortal = "east", outPortal = "",
                    cave = new KitCaveGenerator.Options { seed = seed + 4, layout = "Open", nc = 18, nr = 14, chasm = false, portals = new List<KitPortal> { new KitPortal { id = "west", side = "W", at = 4 } } },
                    connector = new KitConnectorGenerator.Options { seed = seed + 3, length = 10 } },
            };
            EditorUtility.SetDirty(chain);
            return Bake(chain);
        }

        [MenuItem("Tools/Medieval Kit/Rooms/Validate Chains (10 seeds)")]
        public static void ValidateChainsMenu() => Debug.Log(ValidateChains(10));

        /// <summary>builds the sample chain for `count` seeds in a temporary scene beside the open ones and walks each from
        /// its first map to its last (Logs/MedievalKit/chain_validation.txt)</summary>
        public static string ValidateChains(int count, int firstSeed = 1)
        {
            var rules = AssetDatabase.LoadAssetAtPath<KitInteriorRules>(KitRoomTools.RulesAsset);
            if (rules == null) return "no interior rules: run Build Interior Rules";
            var active = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
            var tmp = UnityEditor.SceneManagement.EditorSceneManager.NewScene(UnityEditor.SceneManagement.NewSceneSetup.EmptyScene,
                                                                              UnityEditor.SceneManagement.NewSceneMode.Additive);
            UnityEngine.SceneManagement.SceneManager.SetActiveScene(tmp);
            var sb = new StringBuilder();
            int good = 0;
            try
            {
                for (int sd = firstSeed; sd < firstSeed + count; sd++)
                {
                    var root = new GameObject($"chain {sd}");
                    try
                    {
                        var notes = new List<string>();
                        var rooms = Build(rules, Sample(sd), root.transform, new Vector3(2000f, 0f, 2000f), notes);
                        var (ok, total, missed) = WalkChain(rooms);
                        bool pass = ok == total && total > 0 && notes.Count == 0;
                        if (pass) good++;
                        else sb.AppendLine($"seed {sd}: {ok}/{total} spawns reached" + (missed.Count > 0 ? $" (not {string.Join(", ", missed)})" : "") +
                                           (notes.Count > 0 ? $"; {string.Join("; ", notes)}" : ""));
                    }
                    catch (Exception e) { sb.AppendLine($"seed {sd}: error {e.GetBaseException().Message}"); }
                    finally { UnityEngine.Object.DestroyImmediate(root); }
                }
            }
            finally
            {
                UnityEngine.SceneManagement.SceneManager.SetActiveScene(active);
                UnityEditor.SceneManagement.EditorSceneManager.CloseScene(tmp, true);
            }
            string res = $"chains: {good}/{count} walkable end to end\n{sb}";
            Directory.CreateDirectory("Logs/MedievalKit");
            File.WriteAllText("Logs/MedievalKit/chain_validation.txt", res);
            return res;
        }
    }
}
