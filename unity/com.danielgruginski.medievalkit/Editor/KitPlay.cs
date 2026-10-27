using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace MedievalKit.Editor
{
    /// <summary>Tools > Medieval Kit > Play From Start Level: opens the world's start level and walks it with KitWalker
    /// (click-to-move, the kit's camera and see-through) where it has a navmesh, KitTestWalker (WASD) where not (created
    /// in play mode only, at the first spawn, so nothing is saved into the scene). Look Around This
    /// Level: play without a walker, stepping through the scene's cameras or flying a free one (KitLookAround; the
    /// catalogs, where the game's z-fight watch, F8, then follows every view).</summary>
    [InitializeOnLoad]
    public static class KitPlay
    {
        const string Flag = "MedievalKit.PlayWithWalker", LookFlag = "MedievalKit.PlayLookAround";

        static KitPlay()
        {
            EditorApplication.playModeStateChanged += s =>
            {
                if (s != PlayModeStateChange.EnteredPlayMode) return;
                if (SessionState.GetBool(LookFlag, false))
                {
                    SessionState.SetBool(LookFlag, false);
                    if (Object.FindAnyObjectByType<KitLookAround>() == null)       // a catalog starts its own
                        new GameObject("KitLookAround").AddComponent<KitLookAround>();
                }
                if (!SessionState.GetBool(Flag, false)) return;
                SessionState.SetBool(Flag, false);
                SpawnWalker();
            };
        }

        [MenuItem("Tools/Medieval Kit/Play From Start Level")]
        public static void PlayFromStart()
        {
            var w = AssetDatabase.LoadAssetAtPath<KitWorld>(KitPaths.Generated + "/KitWorld.asset");
            if (w == null) { Debug.LogError("[MedievalKit] no KitWorld: run Build All first"); return; }
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            EditorSceneManager.OpenScene($"{KitPaths.Levels}/{w.start}.unity", OpenSceneMode.Single);
            SessionState.SetBool(Flag, true);
            EditorApplication.EnterPlaymode();
        }

        [MenuItem("Tools/Medieval Kit/Walk This Level")]
        public static void WalkThis()
        {
            SessionState.SetBool(Flag, true);
            EditorApplication.EnterPlaymode();
        }

        [MenuItem("Tools/Medieval Kit/Look Around This Level")]
        public static void LookAround()
        {
            SessionState.SetBool(LookFlag, true);
            EditorApplication.EnterPlaymode();
        }

        /// <summary>the kit's walker (KitWalker: click-to-move and the kit's camera, the see-through on) where the level has a
        /// navmesh at its first spawn, else the WASD stand-in; none when a game's player is already registered</summary>
        public static GameObject SpawnWalker()
        {
            if (KitTravel.HasWalker) return null;                              // a game's own player
            var spawn = Object.FindAnyObjectByType<KitSpawn>();
            if (spawn != null && KitWalker.Spawn(spawn.transform.position, spawn.transform.rotation) is KitWalker walker) return walker.gameObject;
            var go = new GameObject("KitTestWalker");
            var cc = go.AddComponent<CharacterController>();
            cc.height = 1.7f; cc.radius = 0.3f; cc.center = new Vector3(0, 0.85f, 0);
            var body = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            Object.Destroy(body.GetComponent<Collider>());
            body.transform.SetParent(go.transform, false);
            body.transform.localPosition = new Vector3(0, 0.85f, 0);
            body.transform.localScale = new Vector3(0.6f, 0.85f, 0.6f);
            if (spawn != null) go.transform.SetPositionAndRotation(spawn.transform.position, spawn.transform.rotation);
            go.AddComponent<KitTestWalker>();
            return go;
        }
    }
}
