using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace MedievalKit
{
    /// <summary>
    /// Moves the walker between levels: loads the link's target scene and puts the walker on the arrival spawn.
    /// "@return" goes back through the link the walker came in by (building doors). The walker is whatever was
    /// registered with <see cref="SetWalker"/> (or the object tagged Player); it should survive scene loads
    /// (DontDestroyOnLoad). Games can listen to <see cref="Arrived"/> instead of relying on the default placement.
    /// </summary>
    public static class KitTravel
    {
        public static event Action<string, KitSpawn> Arrived;       // level, spawn (null if none was found)
        public static event Action<KitLink> Leaving;

        static Transform walker;
        static string pendingSpawn;
        static readonly Stack<(string level, string link)> returns = new Stack<(string, string)>();
        static bool hooked;

        public static void SetWalker(Transform t) => walker = t;
        public static Transform Walker => walker != null ? walker : GameObject.FindWithTag("Player")?.transform;
        public static string CurrentLevel => SceneManager.GetActiveScene().name;
        public static int ReturnDepth => returns.Count;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        static void Reset() { walker = null; pendingSpawn = null; returns.Clear(); hooked = false; }

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
            }
            else
            {
                if (string.IsNullOrEmpty(arrive))
                {
                    var world = UnityEngine.Object.FindAnyObjectByType<KitLevel>()?.world;
                    arrive = world != null ? world.ArrivalFor(from, link.linkId, target) : null;
                }
                // arriving on a building's "@return" door: remember where we came from for the way back
                // (not when coming down its own stairs: those land on the stair, not the door)
                var tw = UnityEngine.Object.FindAnyObjectByType<KitLevel>()?.world?.Find(target);
                if (tw != null && tw.links.Exists(l => l.id == arrive && l.target == "@return"))
                    returns.Push((from, link.linkId));
            }
            if (!Application.CanStreamedLevelBeLoaded(target))
            {
                Debug.LogError($"[KitTravel] level '{target}' is not in the build settings");
                return false;
            }
            Leaving?.Invoke(link);
            pendingSpawn = arrive;
            if (!hooked) { SceneManager.sceneLoaded += OnLoaded; hooked = true; }
            SceneManager.LoadScene(target);
            return true;
        }

        static void OnLoaded(Scene scene, LoadSceneMode mode)
        {
            if (pendingSpawn == null) return;
            string id = pendingSpawn;
            pendingSpawn = null;
            KitSpawn spawn = null;
            foreach (var s in UnityEngine.Object.FindObjectsByType<KitSpawn>(FindObjectsSortMode.None))
                if (s.spawnId == id) { spawn = s; break; }
            Transform at = spawn != null ? spawn.transform : null;
            if (at == null)      // no spawn: stand at the link itself (a hand-made door without a KitSpawn)
                foreach (var l in UnityEngine.Object.FindObjectsByType<KitLink>(FindObjectsSortMode.None))
                    if (l.linkId == id) { at = l.transform; break; }
            if (at == null) Debug.LogWarning($"[KitTravel] {scene.name}: no spawn or link '{id}'");
            else if (spawn == null) Debug.Log($"[KitTravel] {scene.name}: no spawn '{id}', placed at its link");
            var w = Walker;
            if (at != null && w != null)
            {
                var cc = w.GetComponent<CharacterController>();
                if (cc) cc.enabled = false;
                w.SetPositionAndRotation(at.position, at.rotation);
                if (cc) cc.enabled = true;
            }
            Arrived?.Invoke(scene.name, spawn);
        }
    }
}
