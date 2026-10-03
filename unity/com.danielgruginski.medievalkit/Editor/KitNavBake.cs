using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.SceneManagement;

namespace MedievalKit.Editor
{
    /// <summary>
    /// Navigation for the game's walkers (NavMeshAgents): a level's NavMeshData baked from its colliders the way the walk
    /// tests see them (doors that open and breakables passable; triggers ignored), saved beside the scene as
    /// &lt;scene&gt;_NavMesh.asset, and a KitNavMesh root that adds it at runtime. Breakables (vki_breakable) carve themselves
    /// out with NavMeshObstacles until the game breaks them. A chain gets one surface over all its pieces, in its play
    /// scene. Outdoor maps, rooms and chains bake when they are built; the menu bakes scenes made before.
    /// </summary>
    public static class KitNavBake
    {
        static bool Flag(KitPiece p, string key) => p != null && p.Get(key) is string v && v != "0" && v != "False";

        static bool Passable(Component c)
        {
            var p = c.GetComponentInParent<KitPiece>();
            return Flag(p, "vki_openable") || Flag(p, "vki_breakable");
        }

        /// <summary>the surface of everything under roots (null and a note when there is nothing to walk on)</summary>
        public static NavMeshData Build(IList<GameObject> roots, float voxel, out string note)
        {
            note = null;
            Physics.SyncTransforms();
            var cols = roots.SelectMany(r => r.GetComponentsInChildren<Collider>()).Where(c => !c.isTrigger && c.enabled).ToList();
            if (cols.Count == 0) { note = "no colliders"; return null; }
            var bounds = cols[0].bounds;
            foreach (var c in cols) bounds.Encapsulate(c.bounds);
            bounds.Expand(2f);
            var src = new List<NavMeshBuildSource>();
            NavMeshBuilder.CollectSources(bounds, ~0, NavMeshCollectGeometry.PhysicsColliders, 0, new List<NavMeshBuildMarkup>(), src);
            src.RemoveAll(s => s.component == null || !roots.Any(r => s.component.transform.IsChildOf(r.transform)) ||
                               (s.component is Collider c && c.isTrigger) || Passable(s.component));
            var data = NavMeshBuilder.BuildNavMeshData(KitNavMesh.Settings(voxel), src, bounds, Vector3.zero, Quaternion.identity);
            if (data == null) note = "the build failed";
            return data;
        }

        static NavMeshData Save(NavMeshData data, string path)
        {
            if (AssetDatabase.LoadAssetAtPath<Object>(path) != null) AssetDatabase.DeleteAsset(path);
            data.name = Path.GetFileNameWithoutExtension(path);
            AssetDatabase.CreateAsset(data, path);
            return AssetDatabase.LoadAssetAtPath<NavMeshData>(path);
        }

        static KitNavMesh Holder(Scene scene)
        {
            var nav = scene.GetRootGameObjects().Select(g => g.GetComponent<KitNavMesh>()).FirstOrDefault(n => n != null);
            if (nav != null) return nav;
            var go = new GameObject("KitNavMesh");
            SceneManager.MoveGameObjectToScene(go, scene);
            return go.AddComponent<KitNavMesh>();
        }

        /// <summary>a NavMeshObstacle (carving) over each of a breakable's box colliders, under it: the surface runs
        /// through the gate (the bake leaves it out), the obstacle shuts it until the game swaps the broken piece in</summary>
        static int CarveBreakables(IEnumerable<GameObject> roots)
        {
            int n = 0;
            foreach (var p in roots.SelectMany(r => r.GetComponentsInChildren<KitPiece>(true)).Where(p => Flag(p, "vki_breakable")))
            {
                foreach (var old in p.GetComponentsInChildren<NavMeshObstacle>(true).Where(o => o.name == "NavCarve").ToList())
                    Object.DestroyImmediate(old.gameObject);
                foreach (var bc in p.GetComponentsInChildren<BoxCollider>().Where(c => !c.isTrigger))
                {
                    var go = new GameObject("NavCarve");
                    go.transform.SetParent(bc.transform, false);
                    var ob = go.AddComponent<NavMeshObstacle>();
                    ob.shape = NavMeshObstacleShape.Box; ob.center = bc.center; ob.size = bc.size; ob.carving = true;
                    n++;
                }
            }
            return n;
        }

        /// <summary>bake a loaded scene (it is left dirty; the caller saves it). voxel 0: 0.1 m for an outdoor map, else 0.05</summary>
        public static string BakeScene(Scene scene, float voxel = 0f)
        {
            var roots = scene.GetRootGameObjects().Where(g => g.GetComponent<KitNavMesh>() == null).ToList();
            if (voxel <= 0f) voxel = roots.Any(g => g.GetComponentInChildren<KitVillage>() != null) ? 0.1f : 0.05f;
            var data = Build(roots, voxel, out var note);
            if (data == null) return $"{scene.name}: no navmesh ({note})";
            var saved = Save(data, Path.ChangeExtension(scene.path, null) + "_NavMesh.asset");
            Holder(scene).data = saved;
            int carved = CarveBreakables(roots);
            EditorSceneManager.MarkSceneDirty(scene);
            return $"{scene.name}: navmesh baked ({voxel} m voxels{(carved > 0 ? $", {carved} breakable box carved" : "")})";
        }

        static bool OpenByUser(string path, out Scene s)
        {
            s = SceneManager.GetSceneByPath(path);
            return s.IsValid() && s.isLoaded;
        }

        /// <summary>bake scenes on disk: each opened beside the open ones, baked, saved and closed. A scene that is open
        /// already is left alone (close it, or bake it with the menu's Bake Active Scene and save it yourself).</summary>
        public static string BakeScenes(IEnumerable<string> paths, float voxel = 0f)
        {
            var report = new List<string>();
            var active = SceneManager.GetActiveScene();
            foreach (var path in paths)
            {
                if (OpenByUser(path, out _)) { report.Add($"{path}: open in the editor -- not baked (close it first)"); continue; }
                var s = EditorSceneManager.OpenScene(path, OpenSceneMode.Additive);
                try { report.Add(BakeScene(s, voxel)); EditorSceneManager.SaveScene(s); }
                finally
                {
                    if (active.IsValid()) SceneManager.SetActiveScene(active);
                    EditorSceneManager.CloseScene(s, true);
                }
            }
            AssetDatabase.SaveAssets();
            return string.Join("\n", report);
        }

        /// <summary>one surface over all of a baked chain's pieces (they stand in place in the world), saved as
        /// &lt;chain&gt;_NavMesh.asset in the chain's folder and held by its play scene</summary>
        public static string BakeChain(KitChain chain)
        {
            if (chain == null || chain.pieces.Count == 0) return "chain not baked yet";
            string folder = $"{Path.GetDirectoryName(AssetDatabase.GetAssetPath(chain)).Replace('\\', '/')}/{chain.name}";
            string play = $"{folder}/{chain.name}_Play.unity";
            var paths = chain.pieces.Select(p => p.scene).Append(play).ToList();
            var busy = paths.Where(p => OpenByUser(p, out _)).ToList();
            if (busy.Count > 0) return $"chain {chain.name}: {string.Join(", ", busy)} open in the editor -- not baked (close them first)";
            var active = SceneManager.GetActiveScene();
            var opened = new List<Scene>();
            try
            {
                foreach (var p in paths) opened.Add(EditorSceneManager.OpenScene(p, OpenSceneMode.Additive));
                var roots = opened.Take(chain.pieces.Count).SelectMany(s => s.GetRootGameObjects()).ToList();
                var data = Build(roots, 0.05f, out var note);
                if (data == null) return $"chain {chain.name}: no navmesh ({note})";
                var saved = Save(data, $"{folder}/{chain.name}_NavMesh.asset");
                var ps = opened[opened.Count - 1];
                Holder(ps).data = saved;
                EditorSceneManager.MarkSceneDirty(ps);
                EditorSceneManager.SaveScene(ps);
                return $"chain {chain.name}: one navmesh over {chain.pieces.Count} pieces, in {Path.GetFileName(play)}";
            }
            finally
            {
                if (active.IsValid()) SceneManager.SetActiveScene(active);
                foreach (var s in opened) EditorSceneManager.CloseScene(s, true);
                AssetDatabase.SaveAssets();
            }
        }

        [MenuItem("Tools/Medieval Kit/Navigation/Bake Active Scene")]
        static void BakeActiveMenu() => Debug.Log(BakeScene(SceneManager.GetActiveScene()) + " -- save the scene to keep it");

        [MenuItem("Tools/Medieval Kit/Navigation/Bake Selected Chain")]
        static void BakeChainMenu()
        {
            foreach (var c in Selection.GetFiltered<KitChain>(SelectionMode.Assets)) Debug.Log(BakeChain(c));
        }

        [MenuItem("Tools/Medieval Kit/Navigation/Bake Selected Scenes")]
        static void BakeScenesMenu() =>
            Debug.Log(BakeScenes(Selection.GetFiltered<SceneAsset>(SelectionMode.Assets).Select(AssetDatabase.GetAssetPath)));
    }
}
