using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace MedievalKit
{
    /// <summary>
    /// Streams a baked <see cref="KitChain"/> round the walker: the piece it stands in and the pieces joined to it stay
    /// loaded (scenes loaded additively, one at a time, already in place in the world), the rest are unloaded. Walking
    /// into a connector loads the map beyond it while one crosses; leaving a map unloads the one behind. Put it in the
    /// scene that holds the walker, the camera and the sun (the pieces bring only their own lights). The walker is
    /// <see cref="walker"/>, else <see cref="KitTravel.Walker"/> (registered, or tagged Player). Arriving by a scene
    /// link (<see cref="KitTravel"/>), it starts at the piece holding the arrival spawn instead of the first map.
    /// </summary>
    public class KitChainStreamer : MonoBehaviour
    {
        public KitChain chain;
        public Transform walker;
        [Tooltip("Pieces kept loaded round the one the walker stands in, in joins (1: its neighbours).")]
        [Min(1)] public int reach = 1;
        [Tooltip("At start: load the first map and put the walker on its way-in spawn.")]
        public bool placeWalker = true;
        [Tooltip("At start: the spawn to put the walker on (its piece loaded first); empty: the first map's. Set by KitTravel.")]
        public string arrive;

        public string Current { get; private set; }
        public IEnumerable<string> Loaded => loaded.Keys;
        readonly Dictionary<string, Scene> loaded = new Dictionary<string, Scene>();
        readonly HashSet<string> busy = new HashSet<string>();
        bool working, started;

        Transform Walker => walker != null ? walker : KitTravel.Walker;

        /// <summary>start at this spawn (KitTravel calls it when a scene link arrives in the play scene, before Start)</summary>
        public void Arrive(string spawnId) { arrive = spawnId; placeWalker = true; }

        IEnumerator Start()
        {
            if (chain == null || chain.pieces.Count == 0) { Debug.LogWarning("[KitChainStreamer] no baked chain"); yield break; }
            var first = (string.IsNullOrEmpty(arrive) ? null : chain.WithSpawn(arrive)) ?? chain.pieces[0];
            yield return Load(first);
            var w = Walker;
            if (placeWalker && w != null && loaded.TryGetValue(first.id, out var sc))
            {
                var map = chain.maps.Count > 0 ? chain.maps[0] : null;
                var spawn = sc.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<KitSpawn>())
                              .OrderBy(s => !string.IsNullOrEmpty(arrive) ? (s.spawnId == arrive ? 0 : 1) : map != null && s.spawnId == map.outPortal ? 1 : 0)
                              .FirstOrDefault();
                if (spawn != null)
                {
                    KitTravel.Place(w, spawn.transform.position, spawn.transform.rotation);
                    Current = first.id;
                }
                if (!string.IsNullOrEmpty(arrive)) KitTravel.NotifyArrived(gameObject.scene.name, spawn);
            }
            started = true;                 // streaming waits for the walker's first place (it may still stand where it came from)
        }

        void Update()
        {
            var w = Walker;
            if (chain == null || w == null || working || !started) return;
            var at = chain.At(w.position);
            if (at != null) Current = at.id;
            if (Current == null) return;
            StartCoroutine(Stream(chain.Around(Current, reach)));
        }

        IEnumerator Stream(HashSet<string> want)
        {
            working = true;
            foreach (var id in want)
                if (!loaded.ContainsKey(id)) { yield return Load(chain.Find(id)); break; }        // one load per pass
            // unload what is two joins beyond the wanted ring (a step back does not reload at once)
            var keep = new HashSet<string>(want.SelectMany(id => chain.Around(id, 1)));
            foreach (var id in loaded.Keys.ToList())
                if (!keep.Contains(id))
                {
                    var op = SceneManager.UnloadSceneAsync(loaded[id]);
                    loaded.Remove(id);
                    if (op != null) yield return op;
                }
            working = false;
        }

        IEnumerator Load(KitChain.Piece p)
        {
            if (p == null || loaded.ContainsKey(p.id) || !busy.Add(p.id)) yield break;
            var op = SceneManager.LoadSceneAsync(p.scene, LoadSceneMode.Additive);
            if (op == null) { Debug.LogError($"[KitChainStreamer] cannot load {p.scene} (in the build settings?)"); busy.Remove(p.id); yield break; }
            yield return op;
            var sc = SceneManager.GetSceneByPath(p.scene);
            if (sc.IsValid()) loaded[p.id] = sc;
            busy.Remove(p.id);
        }
    }
}
