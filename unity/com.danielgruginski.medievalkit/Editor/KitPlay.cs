using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace MedievalKit.Editor
{
    /// <summary>Tools > Medieval Kit > Play From Start Level: opens the world's start level and walks it with
    /// KitTestWalker (created in play mode only, at the first spawn, so nothing is saved into the scene).</summary>
    [InitializeOnLoad]
    public static class KitPlay
    {
        const string Flag = "MedievalKit.PlayWithWalker";

        static KitPlay()
        {
            EditorApplication.playModeStateChanged += s =>
            {
                if (s != PlayModeStateChange.EnteredPlayMode || !SessionState.GetBool(Flag, false)) return;
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

        public static GameObject SpawnWalker()
        {
            var spawn = Object.FindAnyObjectByType<KitSpawn>();
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
