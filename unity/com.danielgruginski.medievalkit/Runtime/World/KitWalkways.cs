using System;
using System.Collections.Generic;
using System.Linq;
using MedievalKit;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.SceneManagement;

namespace MedievalKit
{
    /// <summary>
    /// Walkable tops the kit's navmesh leaves out (the warcamp's walkway: its deck pieces have no collider, so the bake
    /// skips them): a scene's pieces the rules name (<see cref="Names"/>: the game's rules set it) each get a box over their top (to
    /// click and stand on) and one navmesh over all of them, once per scene as it loads (the <see cref="LevelDirector"/>
    /// and the encounter spawners ask for it). The walkway's ladders lead onto it and its archers walk it.
    /// </summary>
    public static class KitWalkways
    {
        /// <summary>the deck pieces' names (a mesh whose name holds one gets a deck): the game sets it, e.g. from its
        /// rules; null or empty = no decks</summary>
        public static Func<IList<string>> Names;

        static readonly Dictionary<int, NavMeshDataInstance> built = new Dictionary<int, NavMeshDataInstance>();

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        static void Init()
        {
            built.Clear();
            SceneManager.sceneUnloaded -= Unloaded;
            SceneManager.sceneUnloaded += Unloaded;
        }

        static void Unloaded(Scene s)
        {
            if (!built.TryGetValue(s.handle, out var inst)) return;
            if (inst.valid) inst.Remove();
            built.Remove(s.handle);
        }

        public static void Ensure(Scene scene)
        {
            if (!scene.IsValid() || !scene.isLoaded || built.ContainsKey(scene.handle)) return;
            built[scene.handle] = default;
            var names = Names?.Invoke();
            if (names == null || names.Count == 0) return;
            var src = new List<NavMeshBuildSource>();
            var area = new Bounds();
            bool any = false;
            foreach (var root in scene.GetRootGameObjects())
                foreach (var mf in root.GetComponentsInChildren<MeshFilter>())
                {
                    if (mf.sharedMesh == null || !names.Any(n => !string.IsNullOrEmpty(n) && mf.name.IndexOf(n, StringComparison.Ordinal) >= 0)) continue;
                    var m = mf.sharedMesh.bounds;                                    // the deck: the piece's top, a thin box
                    var top = new Vector3(m.center.x, m.max.y - 0.05f, m.center.z);
                    var size = new Vector3(m.size.x, 0.1f, m.size.z);
                    src.Add(new NavMeshBuildSource
                    {
                        shape = NavMeshBuildSourceShape.Box, size = size,
                        transform = mf.transform.localToWorldMatrix * Matrix4x4.Translate(top), area = 0,
                    });
                    if (mf.GetComponent<Collider>() == null)
                    {
                        var bc = mf.gameObject.AddComponent<BoxCollider>();
                        bc.center = top; bc.size = size;
                    }
                    var r = mf.GetComponent<Renderer>();
                    var b = r != null ? r.bounds : new Bounds(mf.transform.position, Vector3.one * 3f);
                    if (!any) { area = b; any = true; } else area.Encapsulate(b);
                }
            if (src.Count == 0) return;
            area.Expand(2f);
            var data = NavMeshBuilder.BuildNavMeshData(KitNavMesh.Settings(0.1f), src, area, Vector3.zero, Quaternion.identity);
            if (data != null) built[scene.handle] = NavMesh.AddNavMeshData(data);
        }
    }
}
