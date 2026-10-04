using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.SceneManagement;

namespace MedievalKit
{
    /// <summary>
    /// Moves the walker between levels: loads the link's target scene and puts the walker on the arrival spawn.
    /// "@return" goes back through the link the walker came in by (building doors). The walker is whatever was
    /// registered with <see cref="SetWalker"/> (or the object tagged Player); it should survive scene loads
    /// (DontDestroyOnLoad). Games can listen to <see cref="Arrived"/> instead of relying on the default placement.
    /// The arrival spawn: the link's `arrive`, else the kit world's rule (its one link back), else the spawn named like
    /// the link (both ends of a stair share its id). A spawn in a chain's piece (a play scene with a
    /// <see cref="KitChainStreamer"/>) is reached once the streamer has loaded that piece.
    /// <para>Preloading (<see cref="Preload"/>, off by default): the levels the current one's links lead to are loaded
    /// beside it in the background and held switched off (their root objects inactive: unseen, no colliders, lights or
    /// navmesh), so taking a link is an instant cut: the level left is switched off, the target switched on and made the
    /// active scene (its lighting), the walker placed; the level left stays held while it is one link away, else it is
    /// unloaded. A level not held yet, a chain's play scene (it streams its own pieces) and the way out of a chain load
    /// the plain way behind a short fade.</para>
    /// </summary>
    public static class KitTravel
    {
        public static event Action<string, KitSpawn> Arrived;       // level, spawn (null if none was found)
        public static event Action<KitLink> Leaving;

        /// <summary>hold the current level's link targets loaded and switched off, for instant cuts</summary>
        public static bool Preload
        {
            get => preload;
            set { preload = value; Hook(); if (value) Host.Refresh(); }
        }
        /// <summary>the fade of a plain load (seconds each way)</summary>
        public static float FadeSeconds = 0.18f;
        /// <summary>the levels held switched off, ready for an instant cut</summary>
        public static IEnumerable<string> Held => held.Keys;
        public static bool Travelling => host != null && host.Fading;
        /// <summary>a journey was asked for and waits on its level's preload (the cut happens when it is ready)</summary>
        public static bool Pending => waiting.HasValue;

        static bool preload;
        static Transform walker;
        static string pendingSpawn;
        static (string level, string link)? pendingReturn;              // the way back, kept if one arrives on a "@return" door
        static readonly Stack<(string level, string link)> returns = new Stack<(string, string)>();
        static readonly Dictionary<string, (Scene scene, List<GameObject> roots)> held = new Dictionary<string, (Scene, List<GameObject>)>();
        static readonly HashSet<string> preloading = new HashSet<string>();
        static readonly HashSet<string> noPreload = new HashSet<string>();    // chains' play scenes: they stream themselves
        static (string target, string arrive)? waiting;                         // a link taken while its level was still loading
        static bool hooked;
        static KitTravelHost host;

        public static void SetWalker(Transform t) => walker = t;
        public static Transform Walker => walker != null ? walker : GameObject.FindWithTag("Player")?.transform;
        /// <summary>a walker was registered (a game's player): stand-ins (KitTestWalker) step aside</summary>
        public static bool HasWalker => walker != null;
        public static string CurrentLevel => SceneManager.GetActiveScene().name;
        public static int ReturnDepth => returns.Count;
        /// <summary>the door the current building was entered by (level, link id; null: none): one interior shared by
        /// many houses is told apart by it</summary>
        public static (string level, string link)? Entered => returns.Count > 0 ? returns.Peek() : ((string, string)?)null;
        /// <summary>the doors to return through, innermost first (a game's save keeps them)</summary>
        public static (string level, string link)[] ReturnStack => returns.ToArray();
        /// <summary>a door to return through, outermost first (a game's load puts the saved ones back after its GoTo)</summary>
        public static void PushReturn(string level, string link) { if (!string.IsNullOrEmpty(level)) returns.Push((level, link)); }

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        static void Reset()
        {
            if (hooked) SceneManager.sceneLoaded -= OnLoaded;
            walker = null; pendingSpawn = null; pendingReturn = null; returns.Clear(); hooked = false;
            preload = false; held.Clear(); preloading.Clear(); noPreload.Clear(); waiting = null; host = null;
            Arrived = null; Leaving = null;
        }

        /// <summary>forget a journey still waiting on its level's preload (the walker died, a menu opened...)</summary>
        public static void CancelPending() => waiting = null;

        static void Hook()
        {
            if (!hooked) { SceneManager.sceneLoaded += OnLoaded; hooked = true; }
        }

        static KitTravelHost Host
        {
            get
            {
                if (host == null)
                {
                    var go = new GameObject("KitTravel");
                    UnityEngine.Object.DontDestroyOnLoad(go);
                    host = go.AddComponent<KitTravelHost>();
                }
                return host;
            }
        }

        public static bool Go(KitLink link)
        {
            string from = CurrentLevel, target = link.target, arrive = link.arrive;
            if (target == "@deep" || string.IsNullOrEmpty(target))
            {
                Debug.Log($"[KitTravel] {link.linkId}: no level beyond ({target})");
                return false;
            }
            if (target == "@return")
            {
                if (returns.Count == 0) { Debug.LogWarning($"[KitTravel] {from}: nowhere to return to"); return false; }
                (target, arrive) = returns.Pop();
                pendingReturn = null;
            }
            else
            {
                if (string.IsNullOrEmpty(arrive))
                {
                    var world = UnityEngine.Object.FindAnyObjectByType<KitLevel>()?.world;
                    arrive = world != null ? world.ArrivalFor(from, link.linkId, target) : null;
                }
                if (string.IsNullOrEmpty(arrive)) arrive = link.linkId;
                // arriving on a building's "@return" door, the way back is remembered (Arrive; not when coming down its
                // own stairs: those land on the stair, not the door)
                pendingReturn = (from, link.linkId);
            }
            if (!Application.CanStreamedLevelBeLoaded(target))
            {
                Debug.LogError($"[KitTravel] level '{target}' is not in the build settings");
                return false;
            }
            if (host != null && host.Fading) return false;          // one journey at a time
            Leaving?.Invoke(link);
            Hook();
            bool inChain = UnityEngine.Object.FindAnyObjectByType<KitChainStreamer>() != null;
            if (preload && !inChain && held.ContainsKey(target)) { Switch(target, arrive); return true; }
            if (preload && !inChain && preloading.Contains(target)) { waiting = (target, arrive); return true; }
            pendingSpawn = arrive;
            if (preload) Host.FadeLoad(target);
            else SceneManager.LoadScene(target);
            return true;
        }

        /// <summary>to a level's spawn without a link (a respawn, a teleport): the way back is forgotten; an instant cut
        /// when the level is held, else a load behind the fade; in the current level the walker is just placed</summary>
        public static bool GoTo(string target, string spawn)
        {
            if (string.IsNullOrEmpty(target) || !Application.CanStreamedLevelBeLoaded(target))
            {
                Debug.LogError($"[KitTravel] level '{target}' is not in the build settings");
                return false;
            }
            if (host != null && host.Fading) return false;
            returns.Clear(); pendingReturn = null; waiting = null;
            Hook();
            if (target == CurrentLevel) { Arrive(SceneManager.GetActiveScene(), spawn); return true; }
            bool inChain = UnityEngine.Object.FindAnyObjectByType<KitChainStreamer>() != null;
            if (preload && !inChain && held.ContainsKey(target)) { Switch(target, spawn); return true; }
            if (preload && !inChain && preloading.Contains(target)) { waiting = (target, spawn); return true; }   // not a second load of it
            pendingSpawn = spawn;
            if (preload) Host.FadeLoad(target);
            else SceneManager.LoadScene(target);
            return true;
        }

        /// <summary>to a level's spawn on a fresh load, whatever is held or current: every level as built, not as the last
        /// visit left it (a game's New Game or Load, which put back what they keep themselves); the way back is
        /// forgotten. Always the fade and a plain load (which drops every held level).</summary>
        public static bool Reload(string target, string spawn)
        {
            if (string.IsNullOrEmpty(target) || !Application.CanStreamedLevelBeLoaded(target))
            {
                Debug.LogError($"[KitTravel] level '{target}' is not in the build settings");
                return false;
            }
            if (host != null && host.Fading) return false;
            returns.Clear(); pendingReturn = null; waiting = null;
            Hook();
            pendingSpawn = spawn;
            Host.FadeLoad(target);
            return true;
        }

        /// <summary>the instant cut: the level here switched off (its surface and colliders out of the way first), the
        /// held target switched on, made active, the walker placed</summary>
        static void Switch(string target, string arrive)
        {
            var from = SceneManager.GetActiveScene();
            var (sc, roots) = held[target];
            held.Remove(target);
            Hold(from);
            foreach (var r in roots) if (r != null) r.SetActive(true);
            SceneManager.SetActiveScene(sc);
            Arrive(sc, arrive);
            Host.Refresh();
        }

        static void Hold(Scene s)
        {
            var roots = s.GetRootGameObjects().Where(g => g.activeSelf).ToList();
            foreach (var r in roots) r.SetActive(false);
            held[s.name] = (s, roots);
        }

        static void OnLoaded(Scene scene, LoadSceneMode mode)
        {
            if (mode == LoadSceneMode.Additive && preloading.Remove(scene.name))
            {
                if (scene.GetRootGameObjects().Any(g => g.GetComponentInChildren<KitChainStreamer>(true) != null))
                {
                    noPreload.Add(scene.name);
                    foreach (var r in scene.GetRootGameObjects()) r.SetActive(false);
                    SceneManager.UnloadSceneAsync(scene);
                }
                else Hold(scene);
                if (waiting.HasValue && waiting.Value.target == scene.name)
                {
                    var (t, a) = waiting.Value;
                    waiting = null;
                    if (held.ContainsKey(t)) Switch(t, a);
                    else { pendingSpawn = a; Host.FadeLoad(t); }
                }
                return;
            }
            if (pendingSpawn == null || mode != LoadSceneMode.Single) return;
            string id = pendingSpawn;
            pendingSpawn = null;
            held.Clear();                       // a plain load unloaded everything else
            Arrive(scene, id);
            if (preload) Host.Refresh();
        }

        static T Find<T>(Scene s, Func<T, bool> f) where T : Component =>
            s.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<T>()).FirstOrDefault(f);

        static void Arrive(Scene scene, string id)
        {
            var spawn = Find<KitSpawn>(scene, s => s.spawnId == id);
            if (spawn == null)      // a chain's play scene: its streamer loads the piece holding the spawn and places the walker
            {
                var st = Find<KitChainStreamer>(scene, _ => true);
                if (st != null && st.chain != null && st.chain.WithSpawn(id) != null) { st.Arrive(id); pendingReturn = null; return; }
            }
            Transform at = spawn != null ? spawn.transform : null;
            var back = Find<KitLink>(scene, l => l.linkId == id);
            if (at == null && back != null) at = back.transform;     // no spawn: stand at the link itself (a hand-made door without a KitSpawn)
            if (pendingReturn != null && back != null && back.target == "@return") returns.Push(pendingReturn.Value);
            pendingReturn = null;
            if (at == null) Debug.LogWarning($"[KitTravel] {scene.name}: no spawn or link '{id}'");
            else if (spawn == null) Debug.Log($"[KitTravel] {scene.name}: no spawn '{id}', placed at its link");
            var w = Walker;
            if (at != null && w != null) Place(w, at.position, at.rotation);
            Arrived?.Invoke(scene.name, spawn);
        }

        /// <summary>put a walker somewhere: a NavMeshAgent is warped (onto the surface there), a CharacterController
        /// switched off while it moves</summary>
        public static void Place(Transform w, Vector3 p, Quaternion r)
        {
            var cc = w.GetComponent<CharacterController>();
            var agent = w.GetComponent<NavMeshAgent>();
            if (cc) cc.enabled = false;
            if (agent != null && agent.enabled)
            {
                if (!agent.Warp(p)) { agent.enabled = false; w.position = p; agent.enabled = true; }
                if (agent.isOnNavMesh) agent.ResetPath();
                w.rotation = r;
            }
            else w.SetPositionAndRotation(p, r);
            if (cc) cc.enabled = true;
        }

        /// <summary>the levels the current one's links lead to (its "@return" door: the level it returns to)</summary>
        static HashSet<string> Neighbours(Scene s)
        {
            var set = new HashSet<string>();
            foreach (var l in s.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<KitLink>()))
            {
                string t = l.target == "@return" ? (returns.Count > 0 ? returns.Peek().level : null) : l.target;
                if (!string.IsNullOrEmpty(t) && t != "@deep" && t != s.name && Application.CanStreamedLevelBeLoaded(t)) set.Add(t);
            }
            return set;
        }

        /// <summary>held and loading round the current level: what it no longer links to unloaded, what it does loaded
        /// (one at a time, in the background)</summary>
        internal static IEnumerator Refresh()
        {
            yield return null;                                     // let a cut settle first
            var cur = SceneManager.GetActiveScene();
            if (UnityEngine.Object.FindAnyObjectByType<KitChainStreamer>() != null) yield break;   // a chain streams itself
            var want = Neighbours(cur);
            foreach (var name in held.Keys.ToList())
                if (!want.Contains(name))
                {
                    var s = held[name].scene;
                    held.Remove(name);
                    if (s.isLoaded) yield return SceneManager.UnloadSceneAsync(s);
                }
            foreach (var name in want)
            {
                if (held.ContainsKey(name) || preloading.Contains(name) || noPreload.Contains(name)) continue;
                if (SceneManager.GetSceneByName(name).isLoaded) continue;
                preloading.Add(name);
                var op = SceneManager.LoadSceneAsync(name, LoadSceneMode.Additive);
                if (op == null) { preloading.Remove(name); continue; }
                yield return op;
                if (SceneManager.GetActiveScene() != cur) yield break;   // moved on meanwhile: the next refresh takes over
            }
        }

        /// <summary>a walker placed by someone else (a chain's streamer): tells the listeners</summary>
        internal static void NotifyArrived(string level, KitSpawn spawn) => Arrived?.Invoke(level, spawn);
    }

    /// <summary>KitTravel's helper (made on demand, kept across loads): runs the background preloading and the fade
    /// over a plain load</summary>
    [AddComponentMenu("")]
    public class KitTravelHost : MonoBehaviour
    {
        float alpha;
        bool arrived, refreshAgain, refreshing;
        Texture2D black;
        public bool Fading { get; private set; }

        void Awake()
        {
            black = new Texture2D(1, 1); black.SetPixel(0, 0, Color.black); black.Apply();
            KitTravel.Arrived += OnArrived;
        }

        void OnDestroy() => KitTravel.Arrived -= OnArrived;
        void OnArrived(string level, KitSpawn spawn) => arrived = true;

        public void Refresh()
        {
            refreshAgain = true;
            if (!refreshing) StartCoroutine(RefreshLoop());
        }

        IEnumerator RefreshLoop()
        {
            refreshing = true;
            while (refreshAgain)
            {
                refreshAgain = false;
                yield return KitTravel.Refresh();
            }
            refreshing = false;
        }

        public void FadeLoad(string target) => StartCoroutine(Fade(target));

        IEnumerator Fade(string target)
        {
            Fading = true;
            float t = KitTravel.FadeSeconds;
            for (float s = 0; s < t; s += Time.unscaledDeltaTime) { alpha = s / t; yield return null; }
            alpha = 1f;
            arrived = false;
            yield return null;                                     // the black frame shows before the load stalls
            SceneManager.LoadScene(target);
            for (float w = 0; !arrived && w < 5f; w += Time.unscaledDeltaTime) yield return null;   // a chain places its walker later
            yield return null;
            for (float s = 0; s < t; s += Time.unscaledDeltaTime) { alpha = 1f - s / t; yield return null; }
            alpha = 0f;
            Fading = false;
        }

        void OnGUI()
        {
            if (alpha <= 0f) return;
            GUI.depth = -1000;
            var c = GUI.color; GUI.color = new Color(0, 0, 0, alpha);
            GUI.DrawTexture(new Rect(0, 0, Screen.width, Screen.height), black);
            GUI.color = c;
        }
    }
}
